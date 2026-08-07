"""``bzk rebuild`` — drop the derived stores and reconstruct them (I9).

Per OPERATIONS.md §5 and HANDOFF.md §3, written in week 1 so I9 is exercised rather than assumed.
Reconstruction has four steps:

1. Drop the derived stores — ``graph.kuzu`` and ``quant.duckdb`` under ``~/.bzk-omics/``. The
   UniProt cache is *not* dropped: it is an input to the drift check, not derived output.
2. Recreate the schema from `schema.py` (the executable mirror of ONTOLOGY.md §4-7).
3. Replay ingestion from the curation export in ``data/curation/``: every record through
   `bzk.curation.loader`, validated, and written to the graph by `bzk.ontology.store`.
4. Drift-check the UniProt sequence cache (ONTOLOGY.md §11 Q5): for each immutable tier-2 entry
   (``accession#sv``), refetch the current sequence and compare by content, catching a sequence
   UniProt has amended even when the version number did not move.

**Step 3 was a logged no-op from week 1 until 2026-08-07, and I9 was vacuous for exactly that
long.** "The graph rebuilds without loss" is trivially true of a graph with nothing in it, and
`HANDOFF.md` §8 has said so throughout rather than letting the passing test stand for the claim.
It stops being vacuous here: the PXD018299 curation record now produces content, a rebuild
reproduces it, and `tests/test_rebuild.py` compares a second rebuild against the first *and*
against the ids pinned in `tests/fixtures/pxd018299_curation_ids.json` — so reproducibility is
checked against something outside this module as well as against itself.

The adapters stay out of the replay. `perseus.py` has no real input (`HANDOFF.md` §8) and inventing
one to make the replay look fuller would put content in the graph that `raw/` cannot regenerate,
which is the one thing I9 forbids.

Network access is injectable (``session``) so the drift check is testable offline.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import kuzu

from bzk.curation.loader import CurationError, load_path
from bzk.http import RestSession
from bzk.ontology import schema, store
from bzk.resolve.uniprot import resolve

DEFAULT_HOME = Path.home() / ".bzk-omics"
DEFAULT_CURATION_DIR = Path(__file__).resolve().parents[1] / "data" / "curation"


def log(message: str) -> None:
    print(f"[rebuild] {message}")


@dataclass(frozen=True)
class Drift:
    accession: str
    cached_sv: int
    current_sv: int | None
    content_changed: bool
    stored_len: int
    current_len: int


@dataclass(frozen=True)
class ReplayReport:
    curation_records: int
    nodes_written: int
    edges_written: int


@dataclass(frozen=True)
class RebuildReport:
    tables_created: int
    curation_records: int
    nodes_written: int
    edges_written: int
    drifts: list[Drift]


def _remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def drop_stores(home: Path) -> None:
    """Remove the derived graph and quantitative stores. Never touches the cache or curation."""
    _remove(home / "graph.kuzu")
    _remove(home / "quant.duckdb")


def create_graph(home: Path) -> kuzu.Connection:
    """Create an empty graph with the full DDL applied."""
    home.mkdir(parents=True, exist_ok=True)
    conn = kuzu.Connection(kuzu.Database(str(home / "graph.kuzu")))
    schema.create_schema(conn)
    return conn


def open_graph(home: Path) -> kuzu.Connection:
    """Open an existing graph without touching its schema — for reading a rebuild back.

    Distinct from `create_graph`, which applies the DDL and therefore only works on a fresh store:
    running it against a populated one raises `Gene already exists in catalog`. Two functions
    rather than one with a flag, so a caller cannot accidentally re-apply the schema.
    """
    return kuzu.Connection(kuzu.Database(str(home / "graph.kuzu")))


def replay_ingestion(conn: kuzu.Connection, curation_dir: Path) -> ReplayReport:
    """Load every curation record and write it to the graph. The substance of I9.

    Records are replayed in sorted filename order so a rebuild is deterministic in the one respect
    the loader is not: ids are content-derived and order-independent, but *log output* and any
    future failure-on-first-error are not, and a reproducibility claim that depends on filesystem
    iteration order is not a claim.

    A record that cannot be loaded **stops the rebuild**. Skipping it and carrying on would produce
    a graph that is silently a subset of the export — I9 says the graph is regenerable from `raw/`
    plus the curation export, and a partial replay makes that false while looking successful.
    """
    records = sorted(curation_dir.glob("curation_*.json")) if curation_dir.exists() else []
    nodes = edges = 0
    for path in records:
        try:
            loaded = load_path(path)
        except CurationError as exc:
            raise CurationError(
                f"{path.name} cannot be replayed, so the rebuild would be a silent subset of the "
                f"curation export (I9). Fix the record or remove it from the export.\n{exc}"
            ) from exc
        written = store.write_change_set(conn, loaded.nodes, loaded.edges)
        nodes += written.nodes_written
        edges += written.edges_written
        log(f"replayed {path.name}: {written.nodes_written} nodes, {written.edges_written} edges")
    log(f"ingestion replay: {len(records)} curation record(s), {nodes} nodes, {edges} edges")
    return ReplayReport(curation_records=len(records), nodes_written=nodes, edges_written=edges)


def drift_check(cache_dir: Path, *, session: RestSession | None = None) -> list[Drift]:
    """Compare each cached tier-2 sequence against a fresh UniProt fetch (ONTOLOGY.md §11 Q5).

    Fetching into a throwaway cache with ``refresh=True`` bypasses both cache tiers, so an isoform
    sequence UniProt amended without bumping the parent version is caught by content, not just by a
    changed version number.
    """
    seq_dir = cache_dir / "seq"
    if not seq_dir.exists():
        return []
    drifts: list[Drift] = []
    for path in sorted(seq_dir.glob("*#sv*.txt")):
        accession, _, sv_text = path.stem.rpartition("#sv")
        if not sv_text.isdigit():
            continue
        stored = path.read_text()
        with tempfile.TemporaryDirectory() as tmp:
            fresh = resolve(accession, cache_dir=Path(tmp), refresh=True, session=session)
        current = fresh.sequence
        content_changed = current is not None and current != stored
        version_changed = fresh.sequence_version != int(sv_text)
        if content_changed or version_changed:
            drifts.append(
                Drift(
                    accession=accession,
                    cached_sv=int(sv_text),
                    current_sv=fresh.sequence_version,
                    content_changed=content_changed,
                    stored_len=len(stored),
                    current_len=len(current or ""),
                )
            )
    return drifts


def rebuild(
    *,
    home: Path = DEFAULT_HOME,
    curation_dir: Path = DEFAULT_CURATION_DIR,
    session: RestSession | None = None,
) -> RebuildReport:
    """Drop and reconstruct the derived stores, then drift-check the sequence cache."""
    log("dropping derived stores (graph.kuzu, quant.duckdb)")
    drop_stores(home)

    log("recreating schema from ONTOLOGY.md §4-7")
    conn = create_graph(home)
    tables = len(schema.table_names())

    replay = replay_ingestion(conn, curation_dir)

    log("drift-checking the UniProt sequence cache")
    drifts = drift_check(home / "cache" / "uniprot", session=session)
    if drifts:
        for d in drifts:
            log(
                f"DRIFT: {d.accession} cached sv{d.cached_sv} ({d.stored_len} aa) vs "
                f"current sv{d.current_sv} ({d.current_len} aa); content_changed={d.content_changed}"
            )
    else:
        log("no sequence drift detected")

    log(
        f"done: {tables} tables, {replay.curation_records} curation record(s), "
        f"{replay.nodes_written} nodes, {replay.edges_written} edges, {len(drifts)} drift(s)"
    )
    return RebuildReport(
        tables_created=tables,
        curation_records=replay.curation_records,
        nodes_written=replay.nodes_written,
        edges_written=replay.edges_written,
        drifts=drifts,
    )


def main() -> None:
    rebuild()


if __name__ == "__main__":
    main()
