"""``bzk rebuild`` — drop the derived stores and reconstruct them (I9).

Per OPERATIONS.md §5 and HANDOFF.md §3, written in week 1 so I9 is exercised rather than assumed.
Reconstruction has four steps:

1. Drop the derived stores — ``graph.kuzu`` and ``quant.duckdb`` under ``~/.bzk-omics/``. The
   sequence archive is *not* dropped: it is an I9 input (ONTOLOGY.md §8), not derived output.
2. Recreate the schema from `schema.py` (the executable mirror of ONTOLOGY.md §4-7).
3. Replay ingestion from the curation export in ``data/curation/``: every record through
   `bzk.curation.loader`, then the deposit it names through the adapter that recognises it,
   validated, and written to the graph by `bzk.ontology.store`.
4. Report how stale the sequence archive's validation is, from the receipt `bzk.drift` leaves.

**The drift check is no longer step 4; it is `bzk drift`, a separate command.** It was never a
rebuild step — it validates an *input* against the outside world, and the graph is byte-identical
whether or not it runs. Welding them cost 980 s of the 1,057 s a full rebuild took once Slice 4a
pinned 1,028 sequences, and a 17-minute command run "after every schema change" (OPERATIONS.md §5)
is one that stops being run. Rebuild **reports** staleness and never refuses: it is the
disaster-recovery path, and a network check standing in front of recovery is worse than a stale
check.

**Step 3 was a logged no-op from week 1 until 2026-08-07, and I9 was vacuous for exactly that
long.** "The graph rebuilds without loss" is trivially true of a graph with nothing in it, and
`HANDOFF.md` §8 has said so throughout rather than letting the passing test stand for the claim.
It stops being vacuous here: the PXD018299 curation record now produces content, a rebuild
reproduces it, and `tests/test_rebuild.py` compares a second rebuild against the first *and*
against the ids pinned in `tests/fixtures/pxd018299_curation_ids.json` — so reproducibility is
checked against something outside this module as well as against itself.

**Search-output ingestion joined the replay 2026-08-07.** Each curation record names a deposit by
`content_hash`; where those bytes are in the content-addressed store, the record's
`SampleMapping` and the file go through the adapter that recognises it, and the sites are written
alongside the curation. This is what I9's *"regenerable from `raw/` plus the curation export"*
actually means — before it, the clause was discharged against curation content only.

`perseus.py` still stays out: it has no real input (`HANDOFF.md` §8) and inventing one to make the
replay look fuller would put content in the graph that `raw/` cannot regenerate, which is the one
thing I9 forbids. The MaxQuant site table is the opposite case — it *is* in `raw/`, by digest.

**A rebuild reaches UniProt.** `resolve_to_nodes` needs a sequence version per razor pick, served
from `~/.bzk-omics/cache/uniprot` and fetched on a miss. That makes the cache an input to the
replay and not only to the drift check, which is `ONTOLOGY.md` §11 Q6 — recorded there, unresolved,
and now load-bearing rather than latent. Both the resolver and the HTTP session are injectable, so
the whole path is testable offline.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import kuzu

from bzk import drift
from bzk.adapters.base import Refusal
from bzk.adapters.maxquant_sites import DeclaredSiteAnalysis, MaxQuantSiteAdapter
from bzk.curation.loader import CurationError, LoadedCuration, load_path
from bzk.ontology import schema, store
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.provenance import raw_store
from bzk.quant import store as quant
from bzk.resolve.nodes import Resolver

DEFAULT_HOME = Path.home() / ".bzk-omics"
DEFAULT_CURATION_DIR = Path(__file__).resolve().parents[1] / "data" / "curation"


def log(message: str) -> None:
    print(f"[rebuild] {message}")


#: Re-exported so `Drift` has one definition (`bzk.drift`) and one import path for existing callers.
Drift = drift.Drift


@dataclass(frozen=True)
class ReplayReport:
    curation_records: int
    #: Statements *issued*, not nodes/edges created — see `store.WriteReport`. `MERGE` plus
    #: ADR-0019's self-contained change-sets means a node staged by two change-sets is counted
    #: twice here and exists once in the graph. Renamed from `nodes_written` 2026-08-08.
    nodes_staged: int
    edges_staged: int
    #: Per-sample cells written to `quant.duckdb` (I11). Staged, like the two above: the writer
    #: uses `INSERT OR REPLACE`, so a re-ingested deposit rewrites rather than accumulates.
    cells_staged: int = 0
    #: Deposits an adapter recognised and ingested. Zero on a machine where `raw/` is empty.
    deposits_ingested: int = 0
    #: `SiteObservation`s written — the ingested population, which is NOT the file's row count.
    site_observations: int = 0
    #: Rows an adapter refused, carried up so a rebuild states what it did not ingest rather than
    #: leaving it to be inferred from a smaller total (`CLAUDE.md` § Flag rather than hide).
    refusals: list[Refusal] = field(default_factory=list)


@dataclass(frozen=True)
class RebuildReport:
    tables_created: int
    curation_records: int
    #: Statements issued, as `ReplayReport` above — never the graph's size.
    nodes_staged: int
    edges_staged: int
    cells_staged: int = 0
    deposits_ingested: int = 0
    site_observations: int = 0
    refusals: list[Refusal] = field(default_factory=list)


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


def _deposit_for(loaded: LoadedCuration, home: Path) -> Path | None:
    """The raw file a curation record is about, or `None` if it is not in the content store.

    Located by **digest, not filename**: the record's `Dataset.content_hash` is what ties curation
    to bytes, and `raw_store.verify` re-hashes the file it finds, so a replay cannot silently run
    against a re-downloaded or revised deposit that happens to share a name (`OPERATIONS.md` §2).

    `None` rather than an error when it is absent: `raw/` is per-machine and gitignored
    (`ARCHITECTURE.md` §2), so a fresh container has curation but no deposit until
    `python -m bzk.sources.pride` runs. That is a smaller graph, not a broken one, and the count is
    reported. A file that is present but *altered* still raises, which is the case worth failing on.
    """
    dataset = next((n for n in loaded.nodes if n[NODE_TYPE_KEY] == "Dataset"), None)
    if dataset is None or not dataset.get("content_hash"):
        return None
    try:
        return raw_store.verify(
            str(dataset["content_hash"]), filename=str(dataset["label"]), home=home
        )
    except FileNotFoundError:
        return None


def _adapter_for(loaded: LoadedCuration, path: Path, resolver: Resolver | None) -> Any | None:
    """The adapter that recognises this file, configured from the curation record.

    Every declared parameter comes from the record — `search_engine`, its version — rather than
    from a constant here, so the graph records what the curator stated about the run rather than
    what this module assumed. Selection is by `sniff` on content, never by filename
    (`ARCHITECTURE.md` §3).
    """
    dataset = next(n for n in loaded.nodes if n[NODE_TYPE_KEY] == "Dataset")
    adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(
            search_engine=str(dataset.get("search_engine") or "unknown"),
            external_version=str(dataset.get("search_engine_version") or "unknown"),
            acquisition_mode=dataset.get("acquisition_mode"),
        ),
        resolver=resolver,
    )
    return adapter if adapter.sniff(path) else None


def replay_ingestion(
    conn: kuzu.Connection,
    curation_dir: Path,
    *,
    home: Path,
    resolver: Resolver | None = None,
) -> ReplayReport:
    """Load every curation record, then ingest the deposit it names. The substance of I9.

    Records are replayed in sorted filename order so a rebuild is deterministic in the one respect
    the loader is not: ids are content-derived and order-independent, but *log output* and any
    future failure-on-first-error are not, and a reproducibility claim that depends on filesystem
    iteration order is not a claim.

    A record that cannot be loaded **stops the rebuild**. Skipping it and carrying on would produce
    a graph that is silently a subset of the export — I9 says the graph is regenerable from `raw/`
    plus the curation export, and a partial replay makes that false while looking successful.

    **The curation record runs first, and that ordering is load-bearing.** The adapter needs the
    `SampleMapping` the loader produces, and the two agree on the `Dataset` because both key it on
    `content_hash` — the loader from the record, the adapter by hashing the bytes. Their ids
    converge (I7), so the sites attach to the dataset the curation describes rather than to a second
    one, and every `SiteObservation` is reachable from a `Sample` and its curation `Analysis` (I5).
    That convergence is asserted in `tests/test_rebuild.py` rather than assumed.

    **`home` has no default, deliberately.** It did for one revision, `DEFAULT_HOME`, and a test
    calling `replay_ingestion(conn, CURATION_DIR)` against a temporary graph then reached into the
    real `~/.bzk-omics/raw/` and ingested the actual 2.8 MB deposit — 78 seconds, and counts that
    depended on whether the developer had run the fetch. That is `HANDOFF.md` §8's live-data hazard
    arriving from the other direction: not a fixture that stops guarding when real data changes, but
    a *test* that silently starts using real data because a default pointed at it. Requiring the
    argument makes the omission a type error.
    """
    records = sorted(curation_dir.glob("curation_*.json")) if curation_dir.exists() else []
    nodes = edges = cells = 0
    # Opened unconditionally, so `quant.duckdb` exists with its tables even where no deposit is
    # ingested. An absent file and an empty one are different states, and only the second says
    # "the layer ran and there was nothing to retain" (`OPERATIONS.md` §1 calls it regenerable,
    # which presumes it is generated).
    quant_connection = quant.connect(home)
    observations = deposits = 0
    refusals: list[Refusal] = []
    for path in records:
        try:
            loaded = load_path(path)
        except CurationError as exc:
            raise CurationError(
                f"{path.name} cannot be replayed, so the rebuild would be a silent subset of the "
                f"curation export (I9). Fix the record or remove it from the export.\n{exc}"
            ) from exc
        written = store.write_change_set(conn, loaded.nodes, loaded.edges)
        nodes += written.nodes_staged
        edges += written.edges_staged
        log(
            f"replayed {path.name}: {written.nodes_staged} node statement(s), "
            f"{written.edges_staged} edge statement(s)"
        )

        source = _deposit_for(loaded, home)
        if source is None:
            log(f"  no deposit in the content store for {path.name}; sites not ingested")
            continue
        adapter = _adapter_for(loaded, source, resolver)
        if adapter is None:
            log(f"  no adapter recognises {source.name}; sites not ingested")
            continue
        parsed = adapter.parse(source, loaded.sample_mapping())
        written = store.write_change_set(conn, parsed.nodes, parsed.edges)
        nodes += written.nodes_staged
        edges += written.edges_staged
        # I11's columnar half (ADR-0004/0013). Written here rather than inside `write_change_set`
        # because a change-set is graph content by definition (`ONTOLOGY.md` §2) and these values
        # are one-per-entity-per-sample — the side of §2's rule that is not a graph property.
        for label, batch in parsed.cells:
            cells += quant.write_cells(quant_connection, label, batch).cells_staged
        deposits += 1
        refusals.extend(parsed.refusals)
        report = adapter.report
        emitted = report.sites_emitted if report is not None else 0
        observations += emitted
        log(
            f"  ingested {source.name} via {adapter.name}: {emitted} site(s), "
            f"{len(parsed.refusals)} refused, {written.nodes_staged} node statement(s), "
            f"{written.edges_staged} edge statement(s), "
            f"{sum(len(b) for _, b in parsed.cells):,} quantitative cell(s)"
        )
    log(
        f"ingestion replay: {len(records)} curation record(s), {deposits} deposit(s), "
        f"{observations} site observation(s), {len(refusals)} refusal(s), "
        f"{nodes} node statement(s), {edges} edge statement(s), {cells:,} quantitative cell(s)"
    )
    quant_connection.close()
    return ReplayReport(
        curation_records=len(records),
        nodes_staged=nodes,
        edges_staged=edges,
        cells_staged=cells,
        deposits_ingested=deposits,
        site_observations=observations,
        refusals=refusals,
    )


def rebuild(
    *,
    home: Path = DEFAULT_HOME,
    curation_dir: Path = DEFAULT_CURATION_DIR,
    resolver: Resolver | None = None,
) -> RebuildReport:
    """Drop and reconstruct the derived stores from the I9 inputs, and report archive staleness.

    No `session` parameter: rebuild's only network path is now the resolver, injected as `resolver`.
    A `session` argument survived here for one revision after the drift check moved out, doing
    nothing — a parameter that is accepted and ignored is a worse lie than one that is missing.
    """
    log("dropping derived stores (graph.kuzu, quant.duckdb)")
    drop_stores(home)

    log("recreating schema from ONTOLOGY.md §4-7")
    conn = create_graph(home)
    tables = len(schema.table_names())

    replay = replay_ingestion(conn, curation_dir, home=home, resolver=resolver)

    log(drift.staleness_line(home))

    log(
        f"done: {tables} tables, {replay.curation_records} curation record(s), "
        f"{replay.deposits_ingested} deposit(s), {replay.site_observations} site observation(s), "
        f"{len(replay.refusals)} refused, {replay.nodes_staged} node statement(s), "
        f"{replay.edges_staged} edge statement(s), {replay.cells_staged:,} quantitative cell(s)"
    )
    return RebuildReport(
        tables_created=tables,
        curation_records=replay.curation_records,
        nodes_staged=replay.nodes_staged,
        edges_staged=replay.edges_staged,
        cells_staged=replay.cells_staged,
        deposits_ingested=replay.deposits_ingested,
        site_observations=replay.site_observations,
        refusals=replay.refusals,
    )


def main() -> None:
    rebuild()


if __name__ == "__main__":
    main()
