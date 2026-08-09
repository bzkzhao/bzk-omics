"""Run the differential analysis over the population the graph actually holds (Slice 4b).

`python -m bzk.sources.pxd018299_differential`. Reports the population at every step, because the
whole output of this slice is a number compared against 12-of-14 and **the two routes do not see
the same sites**. The notebook tested 1,375; ingestion admits 1,967 after refusing 89 for reasons
the notebook could not detect (residue drift, deleted UniProt entries, a withheld razor pick), and
the presence rule cuts both again to different thirds. A recovery figure that matched would need
explaining as much as one that differs.

**The arithmetic comes from `bzk/stats/`, which was written from `ARCHITECTURE.md` §4 and
`ONTOLOGY.md` §6.5 — not from `colab_reproducefigure.ipynb`.** That distinction is the point of the
slice. `bzk/sources/pxd018299_baseline.py` is the notebook transcription and says so; it can only
establish that the transcription is faithful. Copied arithmetic agreeing with itself is guaranteed,
which is the shape `HANDOFF.md` §8 catalogues three times over.

**Two things this cannot yet do from the graph alone, both real gaps rather than shortcuts:**

1. **Gene symbols never enter the graph.** `Gene` has no nodes and `Protein.name` is null on all
   **4,561** (corrected 2026-08-08 from 4,441), so "which of the 14 published targets" is
   unanswerable from stored content and the symbol is read from the file's `Gene names` column
   here. `ROADMAP.md`'s v0.1 exit criterion is *"12-of-14 through the real pipeline"*; the pipeline
   is real, the *identification* is not yet.

   **Decided 2026-08-08 (ONTOLOGY.md §4, §11 Q12): the symbol's home is `Gene.symbol`, not
   `Protein.name`.** So this module's `Gene names` read at the identification step below is not a
   shortcut awaiting a one-line swap — it stays until `Gene` exists, and swapping it for
   `Protein.name` would be reading a protein description where a symbol is meant, which is the
   `Protein names` / `Gene names` error `HANDOFF.md` §6 records costing fourteen silent misses.

   **`Gene` landed 2026-08-09 and this read is now a choice rather than a necessity.** The graph
   holds 1,044 `Gene` nodes and 1,059 `ENCODES` edges, and 12 of the 14 published symbols are
   answerable from stored content — 13 counting `DDX58`, which HGNC renamed and the graph carries
   as `RIGI` (`hgnc:HGNC:19102`). So this module *could* stop reading `Gene names`. It has not
   been switched over, because doing so changes what the differential identifies against and
   therefore what its recovery figure means, and that is a change to make deliberately with the
   figure in view rather than as a side effect of minting a table. The rename is the reason it is
   not a one-line swap: matching the deposit's 2020 symbols against today's approved ones misses
   `DDX58` while the gene is present, so the match has to run on `hgnc:` ids.
2. **The quantitative matrix is now stored (I11) — corrected 2026-08-08.** This said
   `quant_ref` was null and `quant.duckdb` never created. Both are false since `bzk/quant/`
   (ADR-0004, ADR-0013): `quant_ref` is `site_values` on every observation and the store holds
   48,696 measured-or-null cells. **This module still re-reads the deposit**, which is now a
   property of this module rather than of the platform — reading from the columnar store instead is
   what the retention was built to allow.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bzk.adapters import maxquant
from bzk.curation.loader import load_path
from bzk.provenance.raw_store import verify
from bzk.rebuild import _adapter_for, _deposit_for
from bzk.sources.pride import PXD018299_SITES
from bzk.stats import benjamini_hochberg, downshifted_normal, presence_filter, welch_t

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"

# Declared in `data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json`, which is a curation record —
# a human statement of what was done — and therefore a legitimate input. Transcribed here rather
# than read from it for the reason `pxd018299_baseline.py` gives: that record is what this run is
# checked *against*, so consuming its parameters would make the comparison partly circular.
CONTRAST = ("KO_IFN", "WT_IFN")
PRESENCE_MIN = 2
PRESENCE_EITHER = True  # ">=2 replicates in either group"
IMPUTE: dict[str, object] = {
    "downshift_sd": 1.8,
    "width_sd": 0.3,
    "seed": 0,
    "scope": "whole_matrix",
}

# The significance criterion, from `ROADMAP.md` § Measured findings — which records ADAR and PSMB9
# as falling "just outside thresholds (adj p 0.24; log2FC +0.89)". Those are the thresholds.
SIG_ADJ_P = 0.05
SIG_LOG2FC = 1.0

# The 14 ISGylation substrates reported in Pinto-Fernandez et al., Br J Cancer 124:817-830 (2021).
# Real gene symbols; matched exactly after splitting on ';' — substring matching lets OAS1 hit OASL.
EXPECTED_TARGETS = (
    "ADAR", "EIF2AK2", "DDX58", "DDX60", "DHX58", "OAS1", "OAS2",
    "IFIH1", "STAT1", "PSMB9", "PSMB10", "PSMA7", "PSME2", "TAP1",
)  # fmt: skip


@dataclass(frozen=True)
class Populations:
    """Every step's count. The slice's real output — the recovery figure is one line of it."""

    rows_in_file: int
    after_decoys: int
    after_localization: int
    ingested: int
    refused: int
    after_presence_rule: int
    tested: int
    significant_up: int
    targets_present: int
    targets_recovered: int


def _intensity_columns(header: list[str], arm: str) -> list[int]:
    """The three replicate columns for one arm, in replicate order.

    Matched against the *exact* prefixed names rather than by substring: `Intensity KO_1` and
    `Intensity KO_IFN_1` share a prefix, and one replicate carries a run id
    (`KO_1_181212063719`) that a loose match would also catch (`ROADMAP.md` § Measured findings).
    """
    wanted = [f"Intensity {arm}_{i}" for i in (1, 2, 3)]
    missing = [w for w in wanted if w not in header]
    if missing:
        raise SystemExit(f"missing intensity column(s) {missing}; found {sorted(header)}")
    return [header.index(w) for w in wanted]


def main() -> int:
    assert PXD018299_SITES.expected_content_hash is not None
    path = verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename)
    curation = load_path(CURATION)

    # The ingested population, taken from the adapter rather than re-derived: whichever rows it
    # accepted are the graph's `SiteObservation`s, and re-implementing its refusal logic here would
    # be a second source of truth for the population this whole report is about.
    deposit = _deposit_for(curation, Path.home() / ".bzk-omics")
    if deposit is None:
        raise SystemExit("deposit not in the content store; run `python -m bzk.sources.pride`")
    adapter = _adapter_for(curation, deposit, None)
    assert adapter is not None
    parsed = adapter.parse(deposit, curation.sample_mapping())
    report = adapter.report
    assert report is not None
    refused_rows = {r.row for r in parsed.refusals}

    table = maxquant.read_table(path)
    column = {name: i for i, name in enumerate(table.header)}
    kept = [
        row
        for row in maxquant.drop_decoys_and_contaminants(table)
        if row[column["Localization prob"]].strip()
        and float(row[column["Localization prob"]]) >= adapter.declared.localization_threshold
    ]
    ingested_rows = [r for r in kept if r[column["id"]] not in refused_rows]

    numerator_cols = _intensity_columns(table.header, CONTRAST[0])
    denominator_cols = _intensity_columns(table.header, CONTRAST[1])

    def matrix(indices: list[int]) -> np.ndarray:
        raw = np.array(
            [[float(row[i] or 0.0) for i in indices] for row in ingested_rows], dtype=float
        )
        # MaxQuant writes 0 for "not detected", which is not a measurement of zero abundance. Left
        # as 0 it would survive log2 as -inf and be treated as an extremely low *observation*
        # rather than as a hole for the imputation to fill — the generated/measured line (§6.5).
        raw[raw == 0.0] = np.nan
        return np.log2(raw)

    numerator, denominator = matrix(numerator_cols), matrix(denominator_cols)

    keep = presence_filter(
        numerator, denominator, min_per_group=PRESENCE_MIN, either=PRESENCE_EITHER
    )
    numerator, denominator = numerator[keep], denominator[keep]
    tested_rows = [row for row, k in zip(ingested_rows, keep, strict=True) if k]

    # Imputed as one matrix, because `scope='whole_matrix'` means one observed mean and SD across
    # both arms; imputing the arms separately would centre each on its own distribution and erase
    # exactly the difference the test is about.
    both = np.hstack([numerator, denominator])
    imputed = downshifted_normal(both, **IMPUTE)
    filled_num = imputed.values[:, : numerator.shape[1]]
    filled_den = imputed.values[:, numerator.shape[1] :]

    result = welch_t(filled_num, filled_den)
    adjusted = benjamini_hochberg(result.p_value)

    up = (adjusted < SIG_ADJ_P) & (result.log2fc > SIG_LOG2FC)
    genes = [
        {g.strip() for g in row[column["Gene names"]].split(";") if g.strip()}
        for row in tested_rows
    ]
    recovered = {
        target
        for target in EXPECTED_TARGETS
        for i, symbols in enumerate(genes)
        if target in symbols and up[i]
    }
    present = {t for t in EXPECTED_TARGETS for symbols in genes if t in symbols}

    pops = Populations(
        rows_in_file=len(table.rows),
        after_decoys=len(maxquant.drop_decoys_and_contaminants(table)),
        after_localization=len(kept),
        ingested=len(ingested_rows),
        refused=len(refused_rows),
        after_presence_rule=int(keep.sum()),
        tested=int(np.sum(~np.isnan(result.p_value))),
        significant_up=int(up.sum()),
        targets_present=len(present),
        targets_recovered=len(recovered),
    )

    print(f"[4b] contrast {CONTRAST[0]} vs {CONTRAST[1]}, test welch_t, fdr BH")
    print(f"[4b] rows in file                    {pops.rows_in_file:>6,}")
    print(f"[4b]   after decoys/contaminants     {pops.after_decoys:>6,}")
    print(
        f"[4b]   after localization >= {adapter.declared.localization_threshold}     {pops.after_localization:>6,}"
    )
    print(f"[4b]   ingested (graph population)   {pops.ingested:>6,}   [{pops.refused} refused]")
    print(
        f"[4b]   after presence rule           {pops.after_presence_rule:>6,}   [>={PRESENCE_MIN} in {'either' if PRESENCE_EITHER else 'both'}]"
    )
    print(f"[4b]   tested (non-NaN p)            {pops.tested:>6,}")
    print(
        f"[4b] imputed {imputed.n_values_imputed:,} of {imputed.n_values_total:,} values "
        f"({100 * imputed.n_values_imputed / imputed.n_values_total:.1f}%)"
    )
    print(
        f"[4b] significant up                  {pops.significant_up:>6,}   "
        f"[adj p < {SIG_ADJ_P}, log2FC > {SIG_LOG2FC}]"
    )
    print(
        f"[4b] published targets present       {pops.targets_present:>6,} of {len(EXPECTED_TARGETS)}"
    )
    print(
        f"[4b] published targets RECOVERED     {pops.targets_recovered:>6,} of {len(EXPECTED_TARGETS)}"
    )
    print(f"[4b]   recovered: {sorted(recovered)}")
    print(f"[4b]   not recovered: {sorted(set(EXPECTED_TARGETS) - recovered)}")
    print(
        f"[4b]   of those, absent from the tested population: {sorted(set(EXPECTED_TARGETS) - present)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
