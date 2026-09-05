"""Ingest PXD055843's Perseus total-proteome export into the graph.

`python -m bzk.sources.pxd055843_perseus`. Same shape as
`bzk/sources/pxd018299_differential.py`: locate the deposit in the content store, refuse with a
usable message if it is absent, build a change-set, write it with `store.write_change_set`, and
report what was written. Nothing in the installed package imports this module.

**It constructs the Perseus adapter directly, and it must.** `bzk/rebuild.py`'s `_adapter_for`
builds a `MaxQuantSiteAdapter` and returns it only if it sniffs; `MaxQuantSiteAdapter.sniff` wants
three MaxQuant column names in the first tab-split line, and this export is a workbook, so that
function would return `None` for this file. It is not changed here — this module reaches past it.

**It reads its parameters from `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`, and
that is the opposite of what the anchor module does.** `pxd018299_differential.py` transcribes its
parameters and says why, citing `pxd018299_baseline.py`: *"These are transcribed from the notebook
rather than read from the curation record: the record is the artefact this run is checked
**against**, so taking its parameters as input would make the comparison circular."* That reason is
about a run whose whole output is a figure compared with a recorded baseline. **This module compares
nothing.** It ingests a file someone else's analysis produced; there is no baseline here and
therefore no circle, so the precedent is not followed — a precedent is followed for its reason or
not at all.

**`column_suffix` is the one declared value that stays in this module**, and its own docstring is
the ground: *"the suffix is not [identifying] — it never reaches the graph and exists only to find
the columns."* Every other field of `DeclaredAnalysis` lands on the `Analysis` node, so the record —
a statement about the analysis — is where they belong. The suffix lands nowhere; it is a fact about
how Perseus spelled this file's column headings, and it belongs beside the code that reads the file.

**This module cannot succeed today, and the reason is a missing seed rather than a missing file.**
The paper's methods state that missing values were imputed and state no seed; I15 refuses a
stochastic imputation without one, because the analysis is then irreproducible from its own inputs.
The check is **not** re-implemented here — one home for one rule — so the refusal arrives from
`invariants.validate` inside the parse, before anything reaches the graph. Running this for real
needs the seed as much as it needs the bytes, and both are recorded in the analysis record's
`unresolved`.

**What the graph will not hold.** `ParsedObservations.cells` is left empty by
`bzk/adapters/perseus.py` — a carried finding, not repaired here — so the export's eighteen
quantitative columns reach no columnar store through this path. The graph gets the
`ProteinObservation`s and their `DifferentialResult`s and none of the per-sample values they were
computed from, which is the half of I11 this route does not satisfy.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from bzk.adapters.base import ParsedObservations
from bzk.adapters.perseus import DeclaredAnalysis, DeclaredContrast, PerseusAdapter
from bzk.curation import analysis_record
from bzk.curation.loader import LoadedCuration, load_path
from bzk.ontology import store
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.provenance.raw_store import verify
from bzk.rebuild import open_graph

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD055843.json"
ANALYSIS = REPO_ROOT / "data" / "curation" / "analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json"

#: The suffix Perseus wrote into this export's statistics column names, read off the file's own
#: header. It is here and not in the analysis record because it reaches no node: `DeclaredContrast`
#: records that it *"never reaches the graph and exists only to find the columns"*, so it is a
#: property of this file's spelling rather than of the analysis the record describes. The deposit's
#: other export spells its suffix differently, which is why it is a constant of this module and not
#: of the adapter.
COLUMN_SUFFIX = "siUSP24_IFN_siCTRL_IFN"


def _analysis_record() -> dict[str, Any]:
    """Through `analysis_record.read_record`, so a key this format does not define is refused here.

    The record is opened by literal path — nothing globs it and `bzk/rebuild.py` does not replay it
    — so this call site is where the format's vocabulary is enforced for this deposit.
    """
    return analysis_record.read_record(ANALYSIS)


def declared() -> tuple[DeclaredAnalysis, DeclaredContrast]:
    """The declaration, read from the two records rather than transcribed.

    The analysis record supplies every field that lands on `Analysis`; the curation record supplies
    the contrast's two arms, which are identifying on `Contrast` and already have a home there. The
    arms are looked up by the id the analysis record names, so a record naming a contrast the
    curation does not carry is refused rather than silently paired with the first entry.
    """
    record = _analysis_record()
    contrast_id = record["contrast"]
    entries = json.loads(CURATION.read_text()).get("contrasts_of_interest") or []
    entry = next((c for c in entries if c.get("id") == contrast_id), None)
    if entry is None:
        raise SystemExit(
            f"{ANALYSIS.name} names contrast {contrast_id!r}, which {CURATION.name} does not "
            f"carry — it lists {[c.get('id') for c in entries]}. The arms are identifying on "
            "Contrast (ONTOLOGY.md §3), so they are read from the curation record and not guessed."
        )
    declaration = DeclaredAnalysis(
        quantity=record["quantity"],
        filters_applied=list(record["filters_applied"]),
        test=record["test"],
        fdr_method=record["fdr_method"],
        external_version=record["external_version"],
        imputation=dict(record["imputation"]),
    )
    contrast = DeclaredContrast(
        column_suffix=COLUMN_SUFFIX,
        numerator=entry["numerator"],
        denominator=entry["denominator"],
    )
    return declaration, contrast


def locate(*, home: Path | None = None) -> Path:
    """The deposit's bytes in the content store, or a refusal naming what was looked for.

    By digest, never by filename — `raw_store.verify` re-hashes what it finds, so a replay cannot
    run against a revised file that happens to share a name (`OPERATIONS.md` §2).
    """
    record = _analysis_record()
    digest, filename = record["content_hash"], record["file"]
    try:
        return verify(digest, filename=filename, home=home or Path.home() / ".bzk-omics")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"{filename} is not in the content store: looked for {digest} under "
            f"{(home or Path.home() / '.bzk-omics') / 'raw'}. It is a supplementary file of the "
            "deposit's paper rather than a PRIDE archive member, so `python -m bzk.sources.pride` "
            "does not fetch it; it has to be put into the store by hand."
        ) from exc


def build(
    deposit: Path,
    curation: LoadedCuration,
    declaration: DeclaredAnalysis,
    contrast: DeclaredContrast,
) -> ParsedObservations:
    """One export into a change-set, refusing rather than half-reading.

    `sniff` is called before `parse` even though `parse` calls it too: a file that is not a Perseus
    export at all is a different failure from one that is and cannot be parsed, and an operator who
    put the wrong bytes in the store should be told which.
    """
    adapter = PerseusAdapter(declaration, [contrast])
    if not adapter.sniff(deposit):
        raise SystemExit(
            f"{deposit} does not sniff as a Perseus export. A workbook is recognised by Perseus' "
            "column-type stamp and a tab-separated file by its `#!{` annotation rows; this file "
            "carries neither."
        )
    return adapter.parse(deposit, curation.sample_mapping())


def main() -> int:  # pragma: no cover - convenience entry point
    home = Path.home() / ".bzk-omics"
    curation = load_path(CURATION)
    declaration, contrast = declared()
    deposit = locate(home=home)
    parsed = build(deposit, curation, declaration, contrast)

    nodes = Counter(str(node[NODE_TYPE_KEY]) for node in parsed.nodes)
    conn = open_graph(home)
    written = store.write_change_set(conn, parsed.nodes, parsed.edges)
    print(f"[PXD055843] {deposit.name} via {PerseusAdapter.name}")
    print(f"[PXD055843]   nodes by label: {dict(sorted(nodes.items()))}")
    print(
        f"[PXD055843]   wrote {written.nodes_staged:,} node statement(s), "
        f"{written.edges_staged:,} edge statement(s)"
    )
    print(
        f"[PXD055843]   per-sample values retained: {len(parsed.cells)} (see the module docstring)"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    sys.exit(main())
