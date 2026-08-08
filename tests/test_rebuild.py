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


def test_rebuild_creates_schema_and_leaves_the_archive_alone(tmp_path: Any) -> None:
    """Reconstruction only. The drift check moved to `bzk.drift` (2026-08-07) and rebuild does no
    network work of its own — so this asserts the archive is *untouched*, which is the property
    that makes it an I9 input rather than derived output."""
    fx = _fx()
    home = tmp_path / "home"
    _seed_cache(home, fx)
    report = rebuild(home=home, curation_dir=CURATION_DIR)
    assert report.tables_created == 57  # 24 node + 33 rel tables (ADR-0023 dropped two)
    assert report.curation_records == 1  # data/curation/curation_PXD018299.json
    # Statements issued, not the graph's size — the two agree here only because this replay finds
    # no deposit, so nothing is staged twice (`store.WriteReport`).
    assert (report.nodes_staged, report.edges_staged) == (16, 38)
    assert (home / "graph.kuzu").exists()
    assert (home / "cache" / "uniprot" / "seq" / "P09914-2#sv2.txt").exists()  # archive untouched
    assert not hasattr(report, "drifts"), "rebuild no longer performs the drift check"


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
    rebuild(home=home, curation_dir=CURATION_DIR)
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
    rebuild(home=home, curation_dir=CURATION_DIR)
    first = store.ids_by_label(open_graph(home))
    rebuild(home=home, curation_dir=CURATION_DIR)
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
    rebuild(home=home, curation_dir=CURATION_DIR)
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
        rebuild(home=home, curation_dir=curation)
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
    rebuild(home=home, curation_dir=CURATION_DIR)
    conn = open_graph(home)
    before = store.ids_by_label(conn)
    replay_ingestion(conn, CURATION_DIR, home=home)
    assert store.ids_by_label(conn) == before
    assert store.count_nodes(conn) == EXPECTED_NODES


# ── Search-output ingestion in the replay (Slice 4a) ─────────────────────────────────────────────


SYNTHETIC_RECORD = Path(__file__).parent / "fixtures" / "curation_synthetic_loadable.json"


def _fresh_graph(home: Path) -> Any:
    """An empty graph with the DDL applied, without `rebuild`'s drop / drift-check steps."""
    from bzk.rebuild import create_graph

    return create_graph(home)


_SYNTHETIC_SEQUENCE = "MAAKGGKLLKR"  # K at 4, 7, 10 — synthetic, and labelled as such


def _synthetic_site_table() -> bytes:
    """A two-row MaxQuant site table, CRLF as the deposit is. One row is a residue mismatch."""
    header = (
        "Proteins\tPositions within proteins\tLeading proteins\tProtein\tPosition\t"
        "Amino acid\tLocalization prob\tScore\tReverse\tPotential contaminant\tid"
    )
    rows = [
        "P20591\t4\tP20591\tP20591\t4\tK\t0.99\t80.5\t\t\t0",
        "P20591\t5\tP20591\tP20591\t5\tK\t0.99\t70.1\t\t\t1",  # position 5 is G — refused
    ]
    return ("\r\n".join([header, *rows]) + "\r\n").encode("utf-8")


def _resolver_for(accession: str) -> Any:
    from bzk.resolve.uniprot import Resolution

    def _resolve(requested: str) -> Resolution:
        assert requested == accession, requested
        return Resolution(
            status="ok",
            requested=requested,
            canonical=requested,
            isoform=None,
            is_isoform=False,
            reviewed=True,
            entry_type="UniProtKB reviewed (Swiss-Prot)",
            sequence=_SYNTHETIC_SEQUENCE,
            sequence_version=4,
            last_seq_update="2019-12-11",
            gene=None,
            sequence_source="canonical",
        )

    return _resolve


def _curation_dir_with_deposit(tmp_path: Path, home: Path) -> Path:
    """A curation export whose record names a synthetic deposit that is in the content store.

    Built rather than committed: the record's `content_hash` must equal the digest of the bytes,
    so writing the two independently would let them drift apart. `raw_store.store` computes it.
    """
    from bzk.provenance import raw_store

    stored = raw_store.store(_synthetic_site_table(), "SYNTHETIC_GlyGlyKSites.txt", home=home)
    record = json.loads(SYNTHETIC_RECORD.read_text())
    record["file"] = "SYNTHETIC_GlyGlyKSites.txt"
    record["content_hash"] = stored.content_hash
    curation_dir = tmp_path / "curation"
    curation_dir.mkdir()
    (curation_dir / "curation_SYNTHETIC.json").write_text(json.dumps(record), encoding="utf-8")
    return curation_dir


def test_replay_ingests_the_deposit_its_curation_names(tmp_path: Any) -> None:
    """Slice 4a: the sites reach the graph, not just the curation.

    Entirely offline — synthetic deposit, injected resolver — per `HANDOFF.md` §8: a path tested
    against the real 2.8 MB deposit would be slow, would depend on someone having run the fetch,
    and would stop testing the day the deposit changes.
    """
    from bzk.rebuild import replay_ingestion

    home = tmp_path / "home"
    curation_dir = _curation_dir_with_deposit(tmp_path, home)
    conn = _fresh_graph(home)

    report = replay_ingestion(conn, curation_dir, home=home, resolver=_resolver_for("P20591"))
    assert report.deposits_ingested == 1
    assert report.site_observations == 1  # of two rows; the other is a residue mismatch
    assert [r.reason for r in report.refusals] == ["residue_mismatch"]

    counts = store.count_nodes(conn)
    assert counts["SiteObservation"] == 1
    assert counts["ModifierAssignment"] == 1
    assert counts["Modifier"] == 3
    assert counts["ModificationSite"] == 1
    assert counts["ProteinSequence"] == 1


def test_the_adapter_and_the_curation_agree_on_one_dataset(tmp_path: Any) -> None:
    """The join that makes I5 traversable: both key `Dataset` on `content_hash` — the loader from
    the record, the adapter by hashing the bytes — so their ids converge (I7) and the sites hang off
    the dataset the curation describes rather than off a second, unprovenanced one.

    Asserted rather than assumed: a mismatch would produce a graph that looks complete, with two
    `Dataset` nodes and no path from any observation back to a `Sample`.
    """
    from bzk.rebuild import replay_ingestion

    home = tmp_path / "home"
    curation_dir = _curation_dir_with_deposit(tmp_path, home)
    conn = _fresh_graph(home)
    replay_ingestion(conn, curation_dir, home=home, resolver=_resolver_for("P20591"))

    assert store.count_nodes(conn)["Dataset"] == 1
    rows = conn.execute(
        "MATCH (s:Sample)-[:PRODUCED]->(d:Dataset)-[:REPORTS_SITE]->(o:SiteObservation) "
        "RETURN count(DISTINCT o)"
    )
    assert not isinstance(rows, list)
    assert rows.get_next()[0] == 1, "no SiteObservation is reachable from a Sample"


def test_a_deposit_absent_from_the_store_is_reported_not_invented(tmp_path: Any) -> None:
    """`raw/` is per-machine and gitignored, so a fresh container has curation and no deposit. That
    is a smaller graph, not a broken one — and the count says so rather than the total implying it.
    """
    from bzk.rebuild import replay_ingestion

    home = tmp_path / "home"
    curation_dir = tmp_path / "curation"
    curation_dir.mkdir()
    record = json.loads(SYNTHETIC_RECORD.read_text())
    (curation_dir / "curation_SYNTHETIC.json").write_text(json.dumps(record), encoding="utf-8")
    conn = _fresh_graph(home)

    report = replay_ingestion(conn, curation_dir, home=home, resolver=_resolver_for("P20591"))
    assert report.deposits_ingested == 0
    assert report.site_observations == 0
    assert report.curation_records == 1
    assert "SiteObservation" not in store.count_nodes(conn)


def test_an_altered_deposit_raises_rather_than_ingesting(tmp_path: Any) -> None:
    """The digest is what ties curation to bytes (`OPERATIONS.md` §2). A file that is present but
    altered is the case worth failing on — absent is tolerated, changed is not."""
    from bzk.rebuild import replay_ingestion

    home = tmp_path / "home"
    curation_dir = _curation_dir_with_deposit(tmp_path, home)
    deposit = next((home / "raw").rglob("SYNTHETIC_GlyGlyKSites.txt"))
    deposit.write_bytes(_synthetic_site_table() + b"tampered\r\n")
    conn = _fresh_graph(home)

    with pytest.raises(ValueError, match="hash|altered|differ"):
        replay_ingestion(conn, curation_dir, home=home, resolver=_resolver_for("P20591"))
