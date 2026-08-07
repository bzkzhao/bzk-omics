"""bzk rebuild — schema recreated, curation replayed into the graph, sequence-cache drift caught.

The drift check refetches through an injected fixture session, so "current UniProt" is the recorded
PXD018299 responses. A cached sequence that matches shows no drift; a tampered one is caught by
content, which is ONTOLOGY.md §11 Q5's mitigation exercised end to end.

**I9 was vacuous from week 1 until 2026-08-07** — "the graph rebuilds without loss" is trivially
true of a graph with nothing in it, and `replay_ingestion` was a logged no-op for that whole time.
The tests below are the first that could fail for the reason I9 exists. Two directions, and the
second is the one that matters: a rebuild is compared against *itself* (run twice, same ids), and
against `tests/fixtures/pxd018299_curation_ids.json`, which was committed before this module wrote
anything. Self-comparison alone would be `test_rebuild` asserting a count against its own source,
the failure `CLAUDE.md` point 2 names.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.curation.loader import CurationError
from bzk.ontology import store
from bzk.rebuild import drop_stores, open_graph, rebuild

FIXTURE = Path(__file__).parent / "fixtures" / "pxd018299_resolution.json"
CURATION_DIR = Path(__file__).resolve().parents[1] / "data" / "curation"
MINTED_IDS = Path(__file__).parent / "fixtures" / "pxd018299_curation_ids.json"
PENDING_RECORD = Path(__file__).parent / "fixtures" / "curation_synthetic_pending.json"

# What data/curation/curation_PXD018299.json produces. Stated once here so a change shows up as one
# edit rather than as three tests disagreeing.
EXPECTED_NODES = {"Project": 1, "Experiment": 1, "Sample": 12, "Dataset": 1, "Analysis": 1}
EXPECTED_EDGES = {
    "CONTAINS": 1,
    "PERFORMED_ON": 12,
    "PRODUCED": 12,
    "SAMPLE_GENERATED_BY": 12,
    "USED": 1,
}


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
    assert (report.nodes_written, report.edges_written) == (16, 38)
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


# ── I9, no longer vacuous ───────────────────────────────────────────────────────────────────────


def test_rebuild_puts_the_curation_record_in_the_graph(tmp_path: Any) -> None:
    """The first content this project has ever stored, counted by label and by relationship.

    Asserted against the graph rather than against the return value: `RebuildReport` is what the
    replay *believes* it wrote, and the two agreeing is the point.
    """
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    conn = open_graph(home)
    assert store.count_nodes(conn) == EXPECTED_NODES
    assert store.count_edges(conn) == EXPECTED_EDGES


def test_rebuild_is_reproducible(tmp_path: Any) -> None:
    """I9 itself: drop everything, rebuild, and get the same graph back.

    Ids, not counts. Two rebuilds could agree on 16 nodes while disagreeing on which sixteen, and
    "regenerable from raw/ plus the curation export" is a claim about identity — under ADR-0020 a
    moved id is a node the graph has forgotten, not a node it has renamed.
    """
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    first = store.ids_by_label(open_graph(home))
    rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    second = store.ids_by_label(open_graph(home))
    assert first == second
    assert sum(len(v) for v in second.values()) == 16


def test_rebuilt_ids_match_the_committed_pin(tmp_path: Any) -> None:
    """The half that is not self-referential: the pin predates this module writing anything.

    `tests/fixtures/pxd018299_curation_ids.json` was generated from the loader before `rebuild.py`
    could store a node, so agreement here says the graph holds what the loader produced — not
    merely that two runs of the same code agree with each other.
    """
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    pinned = json.loads(MINTED_IDS.read_text())
    assert store.ids_by_label(open_graph(home)) == {
        "Project": [pinned["project"]],
        "Experiment": [pinned["experiment"]],
        "Dataset": [pinned["dataset"]],
        "Analysis": [pinned["analysis"]],
        "Sample": sorted(pinned["samples"].values()),
    }


def test_replay_stops_on_a_record_it_cannot_load(tmp_path: Any) -> None:
    """A skipped record would leave a graph that is silently a subset of the curation export.

    I9 says the graph is regenerable from `raw/` plus that export. A partial replay makes the claim
    false while the rebuild reports success, so it raises instead. The unloadable record here is the
    synthetic incomplete twin — not a real record broken for the occasion (`HANDOFF.md` §8).
    """
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    curation = tmp_path / "curation"
    curation.mkdir()
    shutil.copy(PENDING_RECORD, curation / "curation_broken.json")
    with pytest.raises(CurationError) as exc:
        rebuild(home=home, curation_dir=curation, session=_session(fx))
    assert "curation_broken.json" in str(exc.value)
    assert "project.title" in str(exc.value)


def test_replay_is_idempotent_within_one_graph(tmp_path: Any) -> None:
    """Replaying the same export into a graph that already holds it changes nothing.

    Distinct from `test_rebuild_is_reproducible`, which drops the store first. This is the `MERGE`
    path: ADR-0019 makes every producer re-stage its referents, so the same nodes arrive repeatedly
    and must converge rather than collide.
    """
    from bzk.rebuild import replay_ingestion

    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    rebuild(home=home, curation_dir=CURATION_DIR, session=_session(fx))
    conn = open_graph(home)
    before = store.ids_by_label(conn)
    replay_ingestion(conn, CURATION_DIR)
    assert store.ids_by_label(conn) == before
    assert store.count_nodes(conn) == EXPECTED_NODES
