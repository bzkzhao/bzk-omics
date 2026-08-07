"""bzk rebuild — offline: schema recreated, sequence-cache drift caught, cache preserved.

The drift check refetches through an injected fixture session, so "current UniProt" is the recorded
PXD018299 responses. A cached sequence that matches shows no drift; a tampered one is caught by
content, which is ONTOLOGY.md §11 Q5's mitigation exercised end to end.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from bzk.rebuild import drop_stores, rebuild

FIXTURE = Path(__file__).parent / "fixtures" / "pxd018299_resolution.json"
CURATION_DIR = Path(__file__).resolve().parents[1] / "data" / "curation"


class _Resp:
    def __init__(self, status_code: int, *, json_data: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> Any:
        return self._json


class _FixtureSession:
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


def _fx() -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(FIXTURE.read_text()))


def _session(fx: dict[str, Any]) -> _FixtureSession:
    return _FixtureSession(fx["entries"], fx["isoform_fasta"])


def _seed_cache(home: Path, fx: dict[str, Any]) -> Path:
    """Write two tier-2 sequence-cache files matching the fixture, as a prior resolve would have."""
    seq = home / "cache" / "uniprot" / "seq"
    seq.mkdir(parents=True)
    iso = "".join(fx["isoform_fasta"]["P09914-2"].split("\n")[1:]).strip()
    (seq / "P09914-2#sv2.txt").write_text(iso)
    sv = fx["entries"]["P49720"]["entryAudit"]["sequenceVersion"]
    (seq / f"P49720#sv{sv}.txt").write_text(fx["entries"]["P49720"]["sequence"]["value"])
    return seq


def test_rebuild_creates_schema_and_finds_no_drift(tmp_path: Any) -> None:
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    report = rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    assert report.tables_created == 59  # 24 node + 35 rel tables
    assert report.curation_records == 1  # data/curation/curation_PXD018299.json
    assert report.drifts == []
    assert (home / "graph.kuzu").exists()
    assert (home / "cache" / "uniprot" / "seq" / "P09914-2#sv2.txt").exists()  # cache untouched


def test_rebuild_detects_content_drift(tmp_path: Any) -> None:
    fx = _fx()
    home = tmp_path / "home"
    seq = _seed_cache(home, fx)
    sv = fx["entries"]["P49720"]["entryAudit"]["sequenceVersion"]
    (seq / f"P49720#sv{sv}.txt").write_text("MUTATEDSEQUENCE")  # no longer matches UniProt
    report = rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    drifted = {d.accession: d for d in report.drifts}
    assert "P49720" in drifted
    assert drifted["P49720"].content_changed is True


def test_drop_stores_removes_derived_but_keeps_cache(tmp_path: Any) -> None:
    home = tmp_path / "home"
    (home / "graph.kuzu").mkdir(parents=True)
    (home / "graph.kuzu" / "data").write_text("x")
    (home / "quant.duckdb").write_text("x")
    cache = home / "cache" / "uniprot" / "seq"
    cache.mkdir(parents=True)
    (cache / "P49720#sv1.txt").write_text("SEQ")
    drop_stores(home)
    assert not (home / "graph.kuzu").exists()
    assert not (home / "quant.duckdb").exists()
    assert (cache / "P49720#sv1.txt").exists()  # inputs to drift check are never dropped
