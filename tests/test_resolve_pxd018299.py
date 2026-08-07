"""The 20/20 PXD018299 resolution regression — offline and deterministic.

This closes the week 1-2 exit criterion ("twenty accessions resolve and validate") without a
live network call: `tests/fixtures/pxd018299_resolution.json` holds the recorded UniProt responses
(real accessions, sequences as UniProt returned them) that drive a fixture-backed fake session. The
subset deliberately includes the hard cases — both isoforms (`P09914-2`, `P62195-2`), the sequence
amended since the search (`H7BZW7`), and a TrEMBL razor pick with a reviewed Swiss-Prot alternative
(`A0A087WXQ8` / `P49720`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from bzk.resolve.uniprot import resolve, validate_position

FIXTURE = Path(__file__).parent / "fixtures" / "pxd018299_resolution.json"


class _Resp:
    def __init__(self, status_code: int, *, json_data: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> Any:
        return self._json


class _FixtureSession:
    """Serves recorded UniProt responses: {acc}.json from `entries`, {iso}.fasta from `isoform_fasta`."""

    def __init__(self, entries: dict[str, Any], isoform_fasta: dict[str, str]) -> None:
        self.entries = entries
        self.isoform_fasta = isoform_fasta

    def get(self, url: str, *, timeout: int | None = None) -> _Resp:
        tail = url.rsplit("/", 1)[-1]
        if tail.endswith(".json") and tail[:-5] in self.entries:
            return _Resp(200, json_data=self.entries[tail[:-5]])
        if tail.endswith(".fasta") and tail[:-6] in self.isoform_fasta:
            return _Resp(200, text=self.isoform_fasta[tail[:-6]])
        return _Resp(404)


def _load() -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(FIXTURE.read_text()))


def _session(fx: dict[str, Any]) -> _FixtureSession:
    return _FixtureSession(fx["entries"], fx["isoform_fasta"])


def test_pxd018299_twenty_of_twenty(tmp_path: Any) -> None:
    fx = _load()
    sess = _session(fx)
    outcomes = {
        site["accession"]: validate_position(
            resolve(site["accession"], cache_dir=tmp_path, session=sess), site["position"]
        )
        for site in fx["sites"]
    }
    assert len(outcomes) == 20
    assert all(o == "ok" for o in outcomes.values()), outcomes


def test_amended_sequence_still_validates(tmp_path: Any) -> None:
    # H7BZW7 was amended since the ~2019 search (I2's silent-drift risk) and still holds K.
    fx = _load()
    res = resolve("H7BZW7", cache_dir=tmp_path, session=_session(fx))
    assert res.last_seq_update is not None and res.last_seq_update > "2019-01-01"
    assert validate_position(res, 37) == "ok"


def test_trembl_razor_pick_has_reviewed_alternative(tmp_path: Any) -> None:
    # A0A087WXQ8 (razor pick) is TrEMBL; P49720 in its candidate set is reviewed — I17 raw material.
    fx = _load()
    sess = _session(fx)
    picked = resolve("A0A087WXQ8", cache_dir=tmp_path, session=sess)
    alt = resolve(fx["reviewed_alternatives"]["A0A087WXQ8"], cache_dir=tmp_path, session=sess)
    assert picked.reviewed is False
    assert alt.reviewed is True


def test_both_isoform_cases_resolve_via_isoform(tmp_path: Any) -> None:
    fx = _load()
    sess = _session(fx)
    for acc, pos in [("P09914-2", 376), ("P62195-2", 47)]:
        res = resolve(acc, cache_dir=tmp_path, session=sess)
        assert res.sequence_source == "isoform"
        assert validate_position(res, pos) == "ok"
