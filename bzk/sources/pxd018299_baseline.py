"""Re-derive the 12-of-14 welch_t baseline from the PXD018299 deposit, and regenerate its fixture.

Run as `python -m bzk.sources.pxd018299_baseline` after `python -m bzk.sources.pride`. Reads the
deposit out of the content-addressed store by the digest `bzk.sources.pride.PXD018299_SITES`
holds, so it cannot silently run against different bytes; writes
`tests/fixtures/pxd018299_welch_baseline.json`.

**This is a transcription of `colab_reproducefigure.ipynb` cells 2-12, not a reimplementation.**
The notebook is the provenance of record for the baseline (`HANDOFF.md` §5), so the arithmetic
here is deliberately the notebook's arithmetic — including its hand-written BH, its whole-matrix
imputation scope, and its best-site-by-log2FC rule for each target gene. Improving any of that
would make the output a different number that happens to be near 12.

**It therefore imports pandas, which is a `dev` dependency and not a runtime one.** That is
deliberate and it is the point: `ARCHITECTURE.md` §4 puts the platform's own quantitative layer on
polars and DuckDB, and whether this pipeline gives the same answer there is exactly the untested
thing the fixture exists to catch. Reproducing the notebook means using the notebook's library.
Nothing in the installed package imports this module — it is a regeneration entry point, kept
beside `pride.py` because it is the fetch path for the input it reads, so a session that re-fetches
the deposit finds the script that consumes it in the same place.

The counts (`n_sites_tested`, `n_significant_up`, `n_expected_recovered`) are **not** written to the
fixture. They already have a home in `data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json`, and
`CLAUDE.md` § Single source of truth makes a second copy a defect. The fixture carries only the
per-site rows, which have no home — `colab_reproducefigure.ipynb`'s `res` is 1,375 rows built in
memory and never persisted (`ROADMAP.md` § Deposit and supplementary survey).
"""

from __future__ import annotations

import json
import math
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy
from scipy import stats

from bzk.provenance.raw_store import verify
from bzk.sources.pride import PXD018299_SITES

# Every analysis choice the baseline depends on (HANDOFF.md §5). These are transcribed from the
# notebook rather than read from the curation record: the record is the artefact this run is
# checked *against*, so taking its parameters as input would make the comparison circular.
LOC_THRESHOLD = 0.75
QUANTITY = "Intensity"
IMPUTE_DOWNSHIFT = 1.8
IMPUTE_WIDTH = 0.3
IMPUTE_SEED = 0

KO_IFN = [f"{QUANTITY} KO_IFN_{i}" for i in (1, 2, 3)]
WT_IFN = [f"{QUANTITY} WT_IFN_{i}" for i in (1, 2, 3)]

# The 14 ISGylation substrates reported in Pinto-Fernandez et al., Br J Cancer 124:817-830 (2021),
# in the notebook's order (cell 12). Real gene symbols; matched exactly after splitting on ';' —
# substring matching would let OAS1 match OASL.
EXPECTED_TARGETS = (
    "ADAR", "EIF2AK2", "DDX58", "DDX60", "DHX58", "OAS1", "OAS2",
    "IFIH1", "STAT1", "PSMB9", "PSMB10", "PSMA7", "PSME2", "TAP1",
)  # fmt: skip

SIG_ADJ_P = 0.05
SIG_LOG2FC = 1.0

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "pxd018299_welch_baseline.json"


@dataclass(frozen=True)
class CandidateSite:
    """One row the target's selection was made from, as the fixture records it.

    Six fields, read off the tested frame and none recomputed. Recording them is what makes the
    selection checkable: a `TargetRow` alone says which site won and nothing about what it won
    against, so the two paths cannot be compared site by site from committed data.

    `protein` is the accession that row's own search reported — `res["protein"]`, the razor pick
    for that row, not the target's. `hits` is selected by gene symbol, so a target's candidates
    need not share one accession, and without this a `position` would be a number with no frame to
    read it against. `TargetRow.protein` names the accession for the **selected** row; this names
    it for every row, the selected one included.

    `position` is the deposit's own `Position` for that row, in the coordinate frame of the
    `protein` beside it — not resolved, not promoted, not converted to canonical coordinates. The
    platform path keys sites against the sequence the row *resolved to*, and the difference between
    the two keyings is a finding; a record that harmonised them would erase it.

    `log2fc`, `p` and `adj_p` are `null` where the arithmetic produced NaN: `json` writes a bare
    `NaN`, which is not JSON and which no reader outside Python accepts. The row is in the tested
    population either way — it cleared the presence rule — and is never significant, since every
    comparison against NaN is false. That is the pipeline's own behaviour, recorded, not changed.
    `protein` and `position` are `null` on the same principle where the deposit has no value: the
    unguarded `str()` that builds `TargetRow.protein` would write the string `"nan"`, which reads
    as an accession and is not one.

    **Nothing marks which of these the selection picked.** `TargetRow`'s own fields identify it
    among them, and a second marker would be a derived claim that could disagree with the first.
    """

    protein: str | None
    position: int | None
    loc_prob: float | None
    log2fc: float | None
    p: float | None
    adj_p: float | None


@dataclass(frozen=True)
class TargetRow:
    """One published target, at its best site by log2 fold change.

    `recovered` is the claim; the floats are the diagnostics behind it. A target the deposit does
    not contain at all keeps `n_sites = 0` and leaves the rest null rather than being dropped —
    a missing row and a row that failed the thresholds are different findings.

    `sites` is every candidate that survived to the tested population for this target — every row
    the selection chose among, in the order the rows were tested — and `n_sites` is its length. The
    scalar fields above are the selected row's; they are not removed or recomputed, and the
    selection rule is untouched.
    """

    gene: str
    n_sites: int
    recovered: bool
    protein: str | None = None
    position: int | None = None
    loc_prob: float | None = None
    log2fc: float | None = None
    p: float | None = None
    adj_p: float | None = None
    n_candidate_proteins: int | None = None
    sites: tuple[CandidateSite, ...] = ()


@dataclass(frozen=True)
class Baseline:
    n_sites_tested: int
    n_significant_up: int
    n_values_imputed: int
    n_values_total: int
    targets: tuple[TargetRow, ...]

    @property
    def n_expected_recovered(self) -> int:
        return sum(row.recovered for row in self.targets)


def benjamini_hochberg(p: Any) -> Any:
    """The notebook's own BH (cell 10), transcribed. NaN in, NaN out; ties keep input order."""
    p = np.asarray(p, dtype=float)
    ok = ~np.isnan(p)
    out = np.full_like(p, np.nan)
    q = p[ok]
    order = np.argsort(q)
    ranked = q[order]
    n = len(ranked)
    adj = ranked * n / (np.arange(n) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    res_ = np.empty(n)
    res_[order] = np.clip(adj, 0, 1)
    out[ok] = res_
    return out


def _json_float(value: Any) -> float | None:
    """NaN as JSON `null`. See `CandidateSite` for why the fixture may not carry a bare `NaN`."""
    number = float(value)
    return None if math.isnan(number) else number


def _candidate_sites(hits: Any) -> tuple[CandidateSite, ...]:
    """Every row the selection is made from, in the order the rows were tested.

    Read off `hits` — the same frame `idxmax` indexes into, one line later — so the two records
    cannot come from different populations. No filter, no re-ordering, nothing recomputed: this
    records rows that already exist, which is the whole of what it does.
    """
    return tuple(
        CandidateSite(
            protein=None if pd.isna(row.protein) else str(row.protein),
            position=None if pd.isna(row.position) else int(row.position),
            loc_prob=_json_float(row.loc_prob),
            log2fc=_json_float(row.log2fc),
            p=_json_float(row.p),
            adj_p=_json_float(row.adj_p),
        )
        for row in hits.itertuples()
    )


def derive(path: Path) -> Baseline:
    """Run the notebook pipeline over the deposit at `path` and return its counts and target rows.

    Deterministic: the imputation draws come from `default_rng(IMPUTE_SEED)` over a matrix whose
    row order is the deposit's, so two runs on the same bytes agree exactly (I15 requires the seed
    to be recorded for precisely this reason).
    """
    df = pd.read_csv(path, sep="\t", low_memory=False)

    # cell 4 — decoys and contaminants, then the localisation threshold
    clean = df[(df["Reverse"] != "+") & (df["Potential contaminant"] != "+")].copy()
    clean = clean[clean["Localization prob"] >= LOC_THRESHOLD].copy()

    missing = [c for c in KO_IFN + WT_IFN if c not in clean.columns]
    if missing:
        raise KeyError(f"deposit is missing the quantity columns {missing}")

    # cell 8 — log2, presence rule, downshifted-normal imputation over the whole matrix
    vals = clean[KO_IFN + WT_IFN].apply(pd.to_numeric, errors="coerce").replace(0, np.nan)
    log2 = np.log2(vals)
    usable = (log2[KO_IFN].notna().sum(axis=1) >= 2) | (log2[WT_IFN].notna().sum(axis=1) >= 2)

    obs = log2[usable]
    mu, sd = np.nanmean(obs.values), np.nanstd(obs.values)
    rng = np.random.default_rng(IMPUTE_SEED)
    draws = rng.normal(mu - IMPUTE_DOWNSHIFT * sd, IMPUTE_WIDTH * sd, size=obs.shape)
    sub = obs.where(obs.notna(), pd.DataFrame(draws, index=obs.index, columns=obs.columns))
    meta = clean[usable]

    # cell 10 — Welch, then BH. `.values` throughout: filtering kept the deposit's row numbering
    # and a fresh frame does not, which is the index-misalignment failure in HANDOFF.md §6.
    lfc = sub[KO_IFN].mean(axis=1) - sub[WT_IFN].mean(axis=1)
    _, p_raw = stats.ttest_ind(sub[KO_IFN], sub[WT_IFN], axis=1, equal_var=False, nan_policy="omit")
    res = pd.DataFrame(
        {
            "protein": meta["Protein"].values,
            "proteins_all": meta["Proteins"].values,
            "gene": meta["Gene names"].values,
            "position": meta["Position"].values,
            "loc_prob": meta["Localization prob"].values,
            "log2fc": lfc.values,
            "p": np.asarray(p_raw, dtype=float),
        }
    )
    res["adj_p"] = benjamini_hochberg(res["p"])
    res["n_candidate_proteins"] = res["proteins_all"].astype(str).str.count(";") + 1
    sig = (res["adj_p"] < SIG_ADJ_P) & (res["log2fc"] > SIG_LOG2FC)

    # cell 12 — exact gene-symbol match, best site per target by log2FC. `Gene names` holds
    # symbols; `Protein names` holds descriptions and matched nothing fourteen times (HANDOFF §6).
    genes = res["gene"].astype(str).str.upper()
    targets = []
    for gene in EXPECTED_TARGETS:
        hits = res[genes.str.split(";").apply(lambda lst, g=gene: g in [x.strip() for x in lst])]
        if len(hits) == 0:
            targets.append(TargetRow(gene=gene, n_sites=0, recovered=False))
            continue
        best = hits.loc[hits["log2fc"].idxmax()]
        targets.append(
            TargetRow(
                gene=gene,
                n_sites=len(hits),
                recovered=bool(best["adj_p"] < SIG_ADJ_P and best["log2fc"] > SIG_LOG2FC),
                protein=str(best["protein"]),
                position=int(best["position"]),
                loc_prob=float(best["loc_prob"]),
                log2fc=float(best["log2fc"]),
                p=float(best["p"]),
                adj_p=float(best["adj_p"]),
                n_candidate_proteins=int(best["n_candidate_proteins"]),
                sites=_candidate_sites(hits),
            )
        )

    return Baseline(
        n_sites_tested=len(res),
        n_significant_up=int(sig.sum()),
        n_values_imputed=int(obs.isna().values.sum()),
        n_values_total=int(obs.size),
        targets=tuple(targets),
    )


def deposit_path() -> Path:
    """The deposit in the content-addressed store, bytes checked. Raises if it is not fetched."""
    digest = PXD018299_SITES.expected_content_hash
    assert digest is not None  # the module holds it; a None here is a code change, not a state
    return verify(digest, filename=PXD018299_SITES.filename)


def as_fixture(baseline: Baseline) -> dict[str, Any]:
    """The committed fixture: provenance, then the fourteen rows. No counts — see the docstring.

    `asdict` carries `TargetRow.sites` through as a list of objects; nothing is flattened, dropped
    or re-ordered here, and no field is added that `derive` did not produce.
    """
    return {
        "dataset": PXD018299_SITES.accession,
        "file": PXD018299_SITES.filename,
        "content_hash": PXD018299_SITES.expected_content_hash,
        "note": (
            "Per-site rows for the fourteen published ISGylation targets, at each target's best "
            "site by log2 fold change, under the welch_t + BH baseline (HANDOFF.md §5). Rows only: "
            "n_sites_tested, n_significant_up and n_expected_recovered live in "
            "data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json and are read from there, not "
            "restated here. ADAR and PSMB9 are pinned as recovered=false on purpose — a change "
            "that raises the count to 13 or 14 must fail and be explained, not quietly pass. "
            "Each target's `sites` carries every candidate that survived to the tested population "
            "for that target — every row the selection chose among, in the order the rows were "
            "tested — and no site is marked as the selection: the entry's own position, log2fc, p "
            "and adj_p identify it among them, and a second marker could disagree with the first. "
            "The pinned row remains the `hits.loc[hits['log2fc'].idxmax()]` selection, unchanged. "
            "Each site carries the accession its own row reported — the razor pick for that row, "
            "which need not be the target's, since candidates are selected by gene symbol — and "
            "the entry's own `protein` names the selected row's. Positions are recorded exactly as "
            "the baseline reports them, in the coordinate frame of the accession beside them, and "
            "are not resolved or converted to canonical coordinates — the platform path keys sites "
            "against the sequence the row resolved to, and the difference between the two keyings "
            "is the finding. A site's statistics are null where the arithmetic produced NaN, "
            "because a bare NaN is not JSON. "
            "Regenerate with `python -m bzk.sources.pride && python -m bzk.sources.pxd018299_"
            "baseline`."
        ),
        "generated_by": "python -m bzk.sources.pxd018299_baseline",
        "generated_under": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "reproduction_caveat": (
            "These rows were generated with pandas, transcribing colab_reproducefigure.ipynb. "
            "pandas is pinned in the dev dependency group for that reason and is not a runtime "
            "dependency. The platform's own quantitative layer is polars and DuckDB "
            "(ARCHITECTURE.md §4); whether this pipeline yields these same rows there is "
            "UNTESTED, and catching that difference is what this fixture is for."
        ),
        "targets": [asdict(row) for row in baseline.targets],
    }


def main() -> int:  # pragma: no cover - convenience entry point
    path = deposit_path()
    print(f"[baseline] input {path}")
    baseline = derive(path)
    print(f"[baseline] n_sites_tested        {baseline.n_sites_tested:,}")
    print(f"[baseline] n_significant_up      {baseline.n_significant_up:,}")
    print(
        f"[baseline] n_expected_recovered  {baseline.n_expected_recovered} of "
        f"{len(baseline.targets)}"
    )
    print(
        f"[baseline] values imputed        {baseline.n_values_imputed:,} of "
        f"{baseline.n_values_total:,}"
    )
    for row in baseline.targets:
        mark = "OK  " if row.recovered else "    "
        detail = (
            "not detected"
            if row.n_sites == 0
            else (
                f"n_sites={row.n_sites:3d}  log2FC={row.log2fc:+6.2f}  "
                f"adj p={row.adj_p:.2e}  candidates={row.n_candidate_proteins}"
            )
        )
        print(f"[baseline] {mark}{row.gene:9s} {detail}")
    FIXTURE_PATH.write_text(json.dumps(as_fixture(baseline), indent=2) + "\n")
    print(f"[baseline] wrote {FIXTURE_PATH}")
    return 0


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    sys.exit(main())
