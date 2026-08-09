"""The identity pin: what `OPERATIONS.md` §3.1 decided, asserted rather than described.

The decision is that `entry/{canonical}.json` may be overwritten by any re-fetch and that this is
**safe**, because nothing an id depends on is read from it. Every test here is one way that claim
could be false. They are written against a snapshot that *disagrees* with its pin, because agreement
proves nothing — a cache whose snapshot and pin match cannot tell you which one was read.

`reviewed` gets its own test and is the one to watch: unlike `sequence_version` it appears in no key,
and its effect on identity runs one step removed through I17's choice of which protein a site is
keyed against. It is the field a split done by eye would leave in the snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bzk.ontology.keys import KeyError_
from bzk.resolve import pins, uniprot

SEQ = "MSSVAVLTQESFAEHRSGLVPQQIKVATLNSEEESDPPTYK"


class _Session:
    """Returns one canned entry payload and records every call."""

    def __init__(
        self,
        *,
        sv: int,
        reviewed: bool,
        sequence: str = SEQ,
        hgnc: str | list[str] | None = None,
    ):
        self.sv = sv
        self.reviewed = reviewed
        self.sequence = sequence
        self.hgnc = hgnc
        self.calls: list[str] = []

    def get(self, url: str, *, timeout: int = 30) -> Any:
        self.calls.append(url)
        entry_type = (
            "UniProtKB reviewed (Swiss-Prot)" if self.reviewed else "UniProtKB unreviewed (TrEMBL)"
        )
        ids = [self.hgnc] if isinstance(self.hgnc, str) else (self.hgnc or [])
        xrefs = [{"database": "HGNC", "id": i} for i in ids]
        return _Response(
            {
                "entryType": entry_type,
                "sequence": {"value": self.sequence},
                "entryAudit": {"sequenceVersion": self.sv, "lastSequenceUpdateDate": "2019-12-11"},
                "genes": [{"geneName": {"value": "MX1"}}],
                "uniProtKBCrossReferences": xrefs,
            }
        )


class _Response:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload
        self.status_code = 200
        self.text = ""

    def json(self) -> Any:
        return self._payload


def _cache(tmp_path: Path, *, sv: int, reviewed: bool) -> Path:
    """A cache holding one resolved accession, snapshot and pin agreeing."""
    uniprot.resolve("P20591", cache_dir=tmp_path, session=_Session(sv=sv, reviewed=reviewed))
    return tmp_path


def test_a_pinned_version_survives_a_snapshot_that_says_otherwise(tmp_path: Path) -> None:
    cache = _cache(tmp_path, sv=3, reviewed=True)
    assert (cache / "seq" / "P20591#sv3.meta.json").exists()

    # UniProt has moved on, and the snapshot is overwritten to prove it can be.
    refreshed = uniprot.resolve(
        "P20591", cache_dir=cache, refresh=True, session=_Session(sv=4, reviewed=True)
    )
    assert refreshed.sequence_version == 4, "refresh=True must bypass the pin, or drift goes blind"

    # The ordinary path reads the pin, so the id-bearing value is the captured one.
    again = uniprot.resolve("P20591", cache_dir=cache, session=_Session(sv=4, reviewed=True))
    assert again.sequence_version == 3
    assert json.loads((cache / "entry" / "P20591.json").read_text())["sequence_version"] == 4


def test_a_pinned_reviewed_flag_survives_a_snapshot_that_says_otherwise(tmp_path: Path) -> None:
    """The field a split done by eye would miss: it is in no key and it decides I17's promotion."""
    cache = _cache(tmp_path, sv=3, reviewed=False)
    uniprot.resolve("P20591", cache_dir=cache, refresh=True, session=_Session(sv=3, reviewed=True))
    assert json.loads((cache / "entry" / "P20591.json").read_text())["reviewed"] is True

    again = uniprot.resolve("P20591", cache_dir=cache, session=_Session(sv=3, reviewed=True))
    assert again.reviewed is False
    assert again.entry_type == "UniProtKB unreviewed (TrEMBL)"


def test_the_pinned_sequence_wins_over_a_payload_amended_at_the_same_version(
    tmp_path: Path,
) -> None:
    """§11 Q6's mechanism, closed: an amendment at an unchanged `sv` is what refuses live sites."""
    cache = _cache(tmp_path, sv=3, reviewed=True)
    amended = SEQ.replace("K", "R")
    uniprot.resolve(
        "P20591",
        cache_dir=cache,
        refresh=True,
        session=_Session(sv=3, reviewed=True, sequence=amended),
    )
    assert json.loads((cache / "entry" / "P20591.json").read_text())["sequence"] == amended

    again = uniprot.resolve("P20591", cache_dir=cache, session=_Session(sv=3, reviewed=True))
    assert again.sequence == SEQ


def test_the_pin_is_written_once(tmp_path: Path) -> None:
    """`_pin_put` is called directly, because `resolve` cannot reach the case.

    This test asserted write-once through `resolve(refresh=True)` first, and **it passed with the
    guard deleted** — `refresh=True` skips `_pin_put` altogether, so the assertion never exercised
    the line it named. The non-refresh path cannot reach it either, for a different and more
    interesting reason: `resolve` merges the pin into the entry *before* writing, so by the time
    `_pin_put` runs it is writing back the pinned values and the write is idempotent whether or not
    the existence check is there.

    So the guard is defence in depth against a future caller that does not merge first, and the
    only honest way to assert it is at the function. Both facts are pinned below, the second one
    because it is the reason the first needs saying.
    """
    cache = _cache(tmp_path, sv=3, reviewed=True)
    pin = cache / "seq" / "P20591#sv3.meta.json"
    before = pin.read_text()

    uniprot._pin_put(
        cache, "P20591", 3, uniprot._Entry(status="ok", entry_type="X", reviewed=False)
    )
    assert pin.read_text() == before

    # ...and the reason `resolve` never puts it in that position: the merge makes its write a no-op.
    uniprot.resolve("P20591", cache_dir=cache, session=_Session(sv=4, reviewed=False))
    assert pin.read_text() == before
    assert not (cache / "seq" / "P20591#sv4.meta.json").exists()


def test_two_pinned_versions_are_refused_rather_than_chosen_between(tmp_path: Path) -> None:
    """The ≥2 branch of the one selection rule, unreachable from the archive so built by hand.

    The current corpus has exactly one version for every one of its 2,845 accessions, so this
    branch would be asserted and never run if it were left to the corpus to produce.
    """
    cache = _cache(tmp_path, sv=3, reviewed=True)
    (cache / "seq" / "P20591#sv4.meta.json").write_text(
        json.dumps({"entry_type": "UniProtKB reviewed (Swiss-Prot)", "reviewed": True})
    )
    with pytest.raises(KeyError_, match="2 pinned sequence versions"):
        uniprot.resolve("P20591", cache_dir=cache, session=_Session(sv=4, reviewed=True))


def test_an_uncaptured_hgnc_id_refetches_and_a_null_one_does_not(tmp_path: Path) -> None:
    """§11 Q12: key absent means *never captured*; explicit null means *captured, none reported*.

    Both reconstruct to `None` through the dataclass, which is why the sentinel is on disk and the
    loader compares against it rather than against `None`.
    """
    entry = tmp_path / "entry" / "P20591.json"
    entry.parent.mkdir(parents=True)
    pre = {
        "status": "ok",
        "entry_type": "UniProtKB reviewed (Swiss-Prot)",
        "reviewed": True,
        "sequence": SEQ,
        "sequence_version": 3,
        "last_seq_update": "2019-12-11",
        "gene": "MX1",
        "fetched_at": "2026-08-07T00:00:00+00:00",
    }
    entry.write_text(json.dumps(pre))
    session = _Session(sv=3, reviewed=True, hgnc="HGNC:7532")
    assert uniprot.resolve("P20591", cache_dir=tmp_path, session=session).sequence_version == 3
    assert session.calls, "a snapshot predating hgnc_id must refetch, not read as 'no HGNC id'"
    assert json.loads(entry.read_text())["hgnc_id"] == "HGNC:7532"

    entry.write_text(json.dumps({**pre, "hgnc_id": None}))
    quiet = _Session(sv=3, reviewed=True, hgnc="HGNC:7532")
    uniprot.resolve("P20591", cache_dir=tmp_path, session=quiet)
    assert quiet.calls == [], "an explicit null is a captured answer and must not refetch"


def test_the_two_hgnc_states_are_distinguishable_on_disk_and_not_through_the_dataclass() -> None:
    # The measurement the sentinel rests on, as an assertion: if a future `_Entry` were rewritten to
    # default `hgnc_id` to `None`, the loader's check would silently stop firing and every
    # pre-widening snapshot would read as *no HGNC id*. Nothing else in the suite would notice.
    assert uniprot._Entry(status="ok").hgnc_id == uniprot.NOT_CAPTURED
    assert uniprot.NOT_CAPTURED is not None


def test_the_backfill_pins_what_is_on_disk_and_never_fetches(tmp_path: Path) -> None:
    entry = tmp_path / "entry"
    entry.mkdir(parents=True)
    (entry / "P20591.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "entry_type": "UniProtKB reviewed (Swiss-Prot)",
                "reviewed": True,
                "sequence_version": 3,
            }
        )
    )
    (entry / "A0A024R4M0.json").write_text(
        json.dumps({"status": "ok", "entry_type": "Inactive", "reviewed": False})
    )
    (entry / "BROKEN.json").write_text("{not json")

    dry = pins.backfill(tmp_path, dry_run=True)
    assert (dry.written, dry.no_version, dry.unreadable, dry.considered) == (1, 1, 1, 3)
    assert not (tmp_path / "seq").exists(), "--dry-run must not write"

    wet = pins.backfill(tmp_path)
    assert (wet.written, wet.already_pinned) == (1, 0)
    assert json.loads((tmp_path / "seq" / "P20591#sv3.meta.json").read_text()) == {
        "entry_type": "UniProtKB reviewed (Swiss-Prot)",
        "reviewed": True,
    }
    assert pins.backfill(tmp_path).written == 0, "re-running must be a no-op"


def test_the_backfill_never_overwrites_a_pin_the_snapshot_now_disagrees_with(
    tmp_path: Path,
) -> None:
    # The whole point of the correctness window: once a snapshot has been re-fetched, the pin beside
    # it is the older and better record, and a backfill that "repaired" the disagreement would
    # destroy exactly what the pin was written to hold.
    cache = _cache(tmp_path, sv=3, reviewed=False)
    uniprot.resolve("P20591", cache_dir=cache, refresh=True, session=_Session(sv=3, reviewed=True))
    report = pins.backfill(cache)
    assert report.written == 0 and report.already_pinned == 1
    assert json.loads((cache / "seq" / "P20591#sv3.meta.json").read_text())["reviewed"] is False


def test_several_hgnc_cross_references_are_captured_as_ambiguous_not_as_the_first(
    tmp_path: Path,
) -> None:
    """The refusal at the parse, which `tests/test_resolve_nodes.py` cannot reach.

    Those tests construct a `Resolution` with `hgnc_id=AMBIGUOUS` already set, so they assert what
    the *builder* does with the sentinel and say nothing about whether anything produces it.
    Restoring `next(...)` — the pre-2026-08-09 first-match — left every one of them green, which is
    how this gap was found: a guard asserted one layer downstream of where it lives.
    """
    session = _Session(sv=3, reviewed=True, hgnc=["HGNC:7532", "HGNC:19102"])
    got = uniprot.resolve("P20591", cache_dir=tmp_path, session=session)
    assert got.hgnc_id == uniprot.AMBIGUOUS
    assert json.loads((tmp_path / "entry" / "P20591.json").read_text())["hgnc_id"] == (
        uniprot.AMBIGUOUS
    )

    one = uniprot.resolve(
        "Q00000", cache_dir=tmp_path, session=_Session(sv=1, reviewed=True, hgnc="HGNC:7532")
    )
    assert one.hgnc_id == "HGNC:7532"
    none = uniprot.resolve("Q00001", cache_dir=tmp_path, session=_Session(sv=1, reviewed=True))
    assert none.hgnc_id is None
