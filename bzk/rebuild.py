"""``bzk rebuild`` — drop the derived stores and reconstruct them (I9).

Per OPERATIONS.md §5 and HANDOFF.md §3, written in week 1 so I9 is exercised rather than
assumed. Reconstruction has four steps; at v0.1 week 1 only three do work, because no ingestion
adapter exists yet (weeks 3-6):

1. Drop the derived stores — ``graph.kuzu`` and ``quant.duckdb`` under ``~/.bzk-omics/``. The
   UniProt cache is *not* dropped: it is an input to the drift check, not derived output.
2. Recreate the schema from `schema.py` (the executable mirror of ONTOLOGY.md §4-7).
3. Replay ingestion from ``raw/`` plus the curation export in ``data/curation/`` — an explicit,
   logged **no-op** until the first adapter lands. It reads the curation records so the path is
   real, and reports how many it found.
4. Drift-check the UniProt sequence cache (ONTOLOGY.md §11 Q5): for each immutable tier-2 entry
   (``accession#sv``), refetch the current sequence and compare by content, catching a sequence
   UniProt has amended even when the version number did not move. This is pointed at the cache, not
   at stored ``Protein`` nodes, because there are none yet — the cache gives the check something to
   exercise from week 1.

Network access is injectable (``session``) so the drift check is testable offline.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import kuzu

from bzk.http import RestSession
from bzk.ontology import schema
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
class RebuildReport:
    tables_created: int
    curation_records: int
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


def replay_ingestion(curation_dir: Path) -> int:
    """No-op until the first adapter exists (weeks 3-6). Reads the curation export so the path is
    real and returns how many records were found. See HANDOFF.md §3."""
    records = sorted(curation_dir.glob("curation_*.json")) if curation_dir.exists() else []
    # TODO(first-adapter): replay raw/ + these curation records into the graph. Until an adapter
    # exists there is nothing to ingest, so this stays a logged no-op rather than fabricating state.
    log(
        f"ingestion replay: no-op (no adapter yet); {len(records)} curation record(s) in {curation_dir}"
    )
    return len(records)


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
    create_graph(home)
    tables = len(schema.table_names())

    curation_records = replay_ingestion(curation_dir)

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

    log(f"done: {tables} tables, {curation_records} curation record(s), {len(drifts)} drift(s)")
    return RebuildReport(tables_created=tables, curation_records=curation_records, drifts=drifts)


def main() -> None:
    rebuild()


if __name__ == "__main__":
    main()
