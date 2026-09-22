"""Round-13 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:
    .venv/bin/python notes/scripts/diagnose_round13.py | tee notes/logs/round13.txt

Not an independent path: the same instruments the registered runs use. Nothing registered changes.
From this round the stdout is committed alongside the script, so the figures quoted in the
write-ups have a home outside the prose.

AA — THE DENOMINATOR IS WRONG. Instability has been reported over the 751 claims carrying an
     imputed value. Round 12 showed a fully measured claim's q moves with OTHER rows' draws, so the
     40 fully measured claims are exposed too. Reported here over both denominators, with the
     collateral channel quantified: the q range across draws for every fully measured claim, and
     how many span the 0.01 cut. That also tests whether id 889 is singular or typical.

BB — THE PKM ROW. Of the 39 published claims with all three wild-type cells measured, 38 agree with
     the platform's fold change to within 0.001; id 1107 (PKM K270) differs by 0.29. If S1 is log2
     of the deposited site table, a fully measured row cannot differ by more than rounding. The
     summed and per-multiplicity columns are printed against the published values. Round 11
     eliminated the unit axis on AGGREGATE agreement; that does not imply row-level identity.

CC — THE PAPER'S OWN 2,341. The publication states 2,341 GlyGly peptides identified and 798
     enriched. 2,341 is an unused constraint on the population: our candidates are 2,653 raw, 2,318
     after the population rule and 2,101 reaching the test. This searches readings of the site
     table for one that gives 2,341 exactly, as the same kind of constraint did on the other
     deposit (where expanded rows carrying intensity reproduced its stated 2,143).

DD — DENOMINATORS FOR THE RESTRICTED POPULATION. "Recall 1.000 on dense rows" was quoted without
     saying how many published claims that population contains, or how many extra calls it makes.
"""

import json
import math

import numpy as np

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import (
    HOME,
    PXD018299_SITES,
    SUPP_DATA_1,
    _float_cell,
    _s1_rows,
    _supplement_path,
    anchor_population,
    s1_columns,
)
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic

ALPHA, S0, R_PERM, DRAWS = 0.01, 0.1, 250, 20
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]

table = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(table)
ids = [str(r[column["id"]]).strip() for r in rows]


def raw(row: list[str], name: str) -> float:
    text = row[column[name]].strip() if name in column else ""
    try:
        return float(text)
    except ValueError:
        return 0.0


def cell(row: list[str], name: str) -> float:
    value = raw(row, name)
    return math.log2(value) if value > 0 else math.nan


matrix = np.array([[cell(r, n) for n in KO + WT] for r in rows])
measured = ~np.isnan(matrix)
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept, kept_measured = matrix[keep], measured[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)["rows"]
claim_of = {str(c["deposit_id"]): c for c in cascade}
published = np.array([i in claim_of for i in kept_ids])
imputed_count = 6 - kept_measured.sum(1)


def draw_qs(block: np.ndarray, draws: int = DRAWS) -> tuple[np.ndarray, np.ndarray]:
    q_all, support = [], []
    for seed in range(draws):
        filled = downshifted_normal(block, seed=seed, **DEFAULT).values
        observed = _statistic(filled[:, :3], filled[:, 3:], S0)
        finite = np.isfinite(observed)
        magnitude = np.abs(observed[finite])
        thresholds = np.sort(magnitude)
        counts = []
        for assignment in _relabellings(3, 3, scheme="random_excluding_trivial",
                                        randomisations=R_PERM, seed=seed)[0]:
            mask = np.zeros(6, dtype=bool)
            mask[np.asarray(assignment[:3])] = True
            null = np.abs(_statistic(filled[:, mask], filled[:, ~mask], S0))[finite]
            null = np.sort(null[np.isfinite(null)])
            counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
        null_count = np.array(counts, dtype=float).mean(axis=0)
        observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
        q = np.full(observed.shape, np.inf)
        q[finite] = np.minimum.accumulate(null_count / np.maximum(observed_count, 1))[
            np.searchsorted(thresholds, magnitude, side="right") - 1
        ]
        q_all.append(q)
        support.append((q <= ALPHA) & (observed > 0))
    return np.array(q_all), np.array(support)


q_all, support = draw_qs(kept)
counts = support.sum(0)

print("AA — the collateral channel, and the right denominator")
fully = published & (imputed_count == 0)
spans = (q_all.min(0) <= ALPHA) & (q_all.max(0) > ALPHA)
unstable = (counts > 0) & (counts < DRAWS)
print(f"  fully measured published claims: {int(fully.sum())}")
print(f"    their q ranges span the 0.01 cut: {int((fully & spans).sum())}")
print(f"    unstable across draws:           {int((fully & unstable).sum())}")
ranges = q_all[:, fully].max(0) - q_all[:, fully].min(0)
print(f"    q range across draws: median {np.median(ranges):.4f}, max {ranges.max():.4f}")
with_imputed = published & (imputed_count > 0)
print(f"  instability over claims with an imputed value: {int((with_imputed & unstable).sum())} of "
      f"{int(with_imputed.sum())} ({(with_imputed & unstable).sum() / with_imputed.sum():.1%})")
print(f"  instability over ALL published claims:         {int((published & unstable).sum())} of "
      f"{int(published.sum())} ({(published & unstable).sum() / published.sum():.1%})")

print("\nBB — id 1107 (PKM K270): published against deposit, summed and per-multiplicity")
header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
published_columns = s1_columns(header)
row = rows[ids.index("1107")]
claim = claim_of["1107"]
s1_values = [_float_cell(s1[int(claim["row"])].get(n)) for n in published_columns]
summed = [cell(row, n) for n in KO + WT]
expanded = {}
for name in KO + WT:
    for suffix in ("___1", "___2", "___3"):
        full = f"{name}{suffix}"
        if full in column and raw(row, full) > 0:
            expanded.setdefault(name, []).append(round(math.log2(raw(row, full)), 3))
print(f"  S1:     {[round(v, 3) for v in s1_values]}")
print(f"  summed: {[round(v, 3) for v in summed]}")
for name in KO + WT:
    print(f"    {name:>24} ___n: {expanded.get(name, [])}")
print(f"  S1 fold change  {np.mean(s1_values[:3]) - np.mean(s1_values[3:]):+.3f};  "
      f"summed {np.nanmean(summed[:3]) - np.nanmean(summed[3:]):+.3f}")
for name in ("Multiplicity", "Localization prob", "Proteins", "Gene names", "Position"):
    if name in column:
        print(f"  deposit {name}: {row[column[name]]!r}")

print("\nCC — readings of the site table, against the paper's stated 2,341 GlyGly peptides")
reverse = [r for r in rows if "Reverse" in column and r[column["Reverse"]].strip() == "+"]
contaminant = [r for r in rows if "Potential contaminant" in column
               and r[column["Potential contaminant"]].strip() == "+"]
ifn_columns = KO + WT
all_columns = [n for n in table.header if n.startswith("Intensity ") and "___" not in n and n != "Intensity"]
readings = {
    "rows in the table": len(rows),
    "minus reverse and contaminants": len(rows) - len(reverse) - len(contaminant),
    "localisation >= 0.75": sum(1 for r in rows if raw(r, "Localization prob") >= 0.75),
    "any IFN intensity": sum(1 for r in rows if any(raw(r, n) > 0 for n in ifn_columns)),
    "any intensity in any of the twelve": sum(1 for r in rows if any(raw(r, n) > 0 for n in all_columns)),
    "population rule (>=1 in an IFN group)": int(keep.sum()),
}
expanded_rows = 0
for r in rows:
    present = {suffix for name in all_columns for suffix in ("___1", "___2", "___3")
               if f"{name}{suffix}" in column and raw(r, f"{name}{suffix}") > 0}
    expanded_rows += len(present)
readings["expanded rows carrying intensity (all twelve samples)"] = expanded_rows
expanded_ifn = 0
for r in rows:
    present = {suffix for name in ifn_columns for suffix in ("___1", "___2", "___3")
               if f"{name}{suffix}" in column and raw(r, f"{name}{suffix}") > 0}
    expanded_ifn += len(present)
readings["expanded rows carrying intensity (IFN samples only)"] = expanded_ifn
for label, value in readings.items():
    mark = "   <- matches the paper's 2,341" if value == 2341 else ""
    print(f"  {label:>52}: {value:>6}{mark}")

print("\nDD — the restricted population, with its denominators")
dense = (measured[:, :3].sum(1) >= 3) | (measured[:, 3:].sum(1) >= 3)
dense_ids = [i for i, k in zip(ids, dense, strict=True) if k]
dense_published = np.array([i in claim_of for i in dense_ids])
_, dense_support = draw_qs(matrix[dense])
dense_called = dense_support.sum(0) >= DRAWS / 2
hits = int((dense_called & dense_published).sum())
print(f"  rows {int(dense.sum())}; published claims inside it {int(dense_published.sum())} of "
      f"{len(claim_of)} ({dense_published.sum() / len(claim_of):.0%})")
print(f"  calls {int(dense_called.sum())}; hits {hits}; extra calls {int(dense_called.sum()) - hits}")
print(f"  recall within this population {hits / max(int(dense_published.sum()), 1):.3f}; "
      f"precision {hits / max(int(dense_called.sum()), 1):.3f}")
print("  The published claims excluded by this filter are the sparse ones that were being missed,")
print("  so recall inside it cannot be read as agreement on the full set.")
