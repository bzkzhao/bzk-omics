"""`bzk drift` — the sequence-archive check, and the receipt that makes its absence visible.

Split out of `tests/test_rebuild.py` with the module (2026-08-07). The check itself is unchanged
and its content-drift case moved here wholesale; what is new is the receipt, and the reason the
receipt exists: a check nobody is forced to run is a check nobody runs, and 980 s welded to a 75 s
replay is how that happens.

Offline throughout — the "current UniProt" is an injected fixture session of recorded PXD018299
responses, and staleness is tested by passing `now` rather than by waiting or by patching a clock.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from bzk import drift

FIXTURE = Path(__file__).parent / "fixtures" / "pxd018299_resolution.json"


class _Resp:
    def __init__(self, status_code: int, *, json_data: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> Any:
        return self._json


class _FixtureSession:
    """Recorded UniProt responses. The same shape `tests/test_rebuild.py` uses."""

    def __init__(self, entries: dict[str, Any], isoform_fasta: dict[str, str]) -> None:
        self.entries = entries
        self.isoform_fasta = isoform_fasta

    def get(self, url: str, **_: Any) -> _Resp:
        if url.endswith(".json"):
            accession = url.rsplit("/", 1)[-1][: -len(".json")]
            entry = self.entries.get(accession)
            return _Resp(200, json_data=entry) if entry else _Resp(404)
        accession = url.rsplit("/", 1)[-1][: -len(".fasta")]
        fasta = self.isoform_fasta.get(accession)
        return _Resp(200, text=fasta) if fasta else _Resp(404)


def _fx() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text())  # type: ignore[no-any-return]


def _session(fx: dict[str, Any]) -> Any:
    return _FixtureSession(fx["entries"], fx.get("isoform_fasta", {}))


def _seed_archive(home: Path, fx: dict[str, Any]) -> Path:
    """Write the fixture's sequences into the archive, as an ingestion would have."""
    seq = home / "cache" / "uniprot" / "seq"
    seq.mkdir(parents=True)
    for accession, entry in fx["entries"].items():
        sv = entry["entryAudit"]["sequenceVersion"]
        (seq / f"{accession}#sv{sv}.txt").write_text(entry["sequence"]["value"])
    for accession, fasta in fx.get("isoform_fasta", {}).items():
        base = accession.split("-")[0]
        sv = fx["entries"][base]["entryAudit"]["sequenceVersion"]
        sequence = "".join(fasta.splitlines()[1:])
        (seq / f"{accession}#sv{sv}.txt").write_text(sequence)
    return seq


# ── The check, unchanged by the split ────────────────────────────────────────────────────────────


def test_a_matching_archive_reports_no_drift(tmp_path: Any) -> None:
    fx = _fx()
    home = tmp_path / "home"
    _seed_archive(home, fx)
    assert drift.drift_check(home, session=_session(fx)) == []


def test_content_drift_is_caught_even_when_the_version_did_not_move(tmp_path: Any) -> None:
    """`ONTOLOGY.md` §11 Q5's mitigation. The archived sequence is altered while its `sv` stays put,
    which is exactly the case a version-number comparison cannot see. Moved here from
    `test_rebuild.py` with the module; the assertion is unchanged."""
    fx = _fx()
    home = tmp_path / "home"
    seq = _seed_archive(home, fx)
    sv = fx["entries"]["P49720"]["entryAudit"]["sequenceVersion"]
    (seq / f"P49720#sv{sv}.txt").write_text("MUTATEDSEQUENCE")
    drifted = {d.accession: d for d in drift.drift_check(home, session=_session(fx))}
    assert "P49720" in drifted
    assert drifted["P49720"].content_changed is True
    assert drifted["P49720"].cached_sv == sv  # the version never moved; the content did


# ── The receipt ──────────────────────────────────────────────────────────────────────────────────


def test_run_writes_a_receipt_covering_what_it_checked(tmp_path: Any) -> None:
    fx = _fx()
    home = tmp_path / "home"
    _seed_archive(home, fx)
    receipt = drift.run(home, session=_session(fx))
    assert receipt.sequences_checked == len(drift.archived_sequences(home))
    assert receipt.drifts == 0
    assert receipt.archive_digest == drift.archive_digest(drift.archived_sequences(home))
    assert drift.read_receipt(home) == receipt


def test_a_never_checked_archive_says_so(tmp_path: Any) -> None:
    """The state every machine starts in, and the one a silent default would hide."""
    fx = _fx()
    home = tmp_path / "home"
    _seed_archive(home, fx)
    assert "NEVER been drift-checked" in drift.staleness_line(home)


def test_staleness_is_reported_in_days(tmp_path: Any) -> None:
    fx = _fx()
    home = tmp_path / "home"
    _seed_archive(home, fx)
    drift.run(home, session=_session(fx))
    fresh = drift.staleness_line(home, now=datetime.now(UTC) + timedelta(days=1))
    assert "STALE" not in fresh
    stale = drift.staleness_line(home, now=datetime.now(UTC) + timedelta(days=200))
    assert "STALE" in stale and "200 day(s) ago" in stale


def test_a_receipt_over_a_different_archive_does_not_count_as_fresh(tmp_path: Any) -> None:
    """The reason the receipt carries a digest of the *set*, not just a count.

    A check that covered 20 sequences yesterday says nothing about the 1,028 ingested this morning,
    and "checked 1 day ago" would be true and misleading — the average hiding the newest, which is
    the same shape as the sampling option deferred in `HANDOFF.md` §8.
    """
    fx = _fx()
    home = tmp_path / "home"
    seq = _seed_archive(home, fx)
    drift.run(home, session=_session(fx))
    assert "STALE" not in drift.staleness_line(home)

    (seq / "P0CG48#sv1.txt").write_text("MQIFVKTLTGK")  # a newly ingested sequence
    line = drift.staleness_line(home)
    assert "DIFFERENT set" in line
    assert "run `python -m bzk.drift`" in line


def test_an_unreadable_receipt_is_treated_as_absent(tmp_path: Any) -> None:
    """A corrupt receipt must not stop a rebuild, for the same reason a stale one must not."""
    fx = _fx()
    home = tmp_path / "home"
    _seed_archive(home, fx)
    (home / "cache" / "uniprot" / drift.RECEIPT_NAME).write_text("{not json")
    assert drift.read_receipt(home) is None
    assert "NEVER been drift-checked" in drift.staleness_line(home)


def test_an_empty_archive_says_there_is_nothing_to_check(tmp_path: Any) -> None:
    home = tmp_path / "home"
    (home / "cache" / "uniprot").mkdir(parents=True)
    assert "nothing to drift-check" in drift.staleness_line(home)


def test_the_staleness_threshold_mirrors_operations() -> None:
    """`OPERATIONS.md` §5 owns cadence, so it owns this number; `drift.py` mirrors it.

    The same mirror-plus-guard idiom as `schema.py` against `ONTOLOGY.md` §4–§7, `CURATION_BASIS`
    against §5.3 and `GG_REMNANT_MODIFIERS` against §6.1. Before this the constant merely *cited*
    §5 as its owner in a comment, which is not an arrangement — the value lived in one place and
    the authority in another, and either could move without the other noticing.
    """
    text = (Path(__file__).resolve().parents[1] / "OPERATIONS.md").read_text()
    stated = re.search(r"\*\*Staleness threshold: (\d+) days\.\*\*", text)
    assert stated, "OPERATIONS.md §5 no longer states a staleness threshold"
    assert drift.STALE_AFTER_DAYS == int(stated.group(1)), (
        f"drift.STALE_AFTER_DAYS is {drift.STALE_AFTER_DAYS} but OPERATIONS.md §5 says "
        f"{stated.group(1)}; §5 owns the number"
    )
