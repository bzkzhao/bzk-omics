"""Round-9 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round9.py

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

I — THE F1 CEILING. The documented and halved rules are one family: the halved rule is the
    documented one with the null count scaled, so its calls are a superset and it must win recall
    and lose precision. Citing precision as support for the documented rule argues from the chosen
    threshold. Scored continuously over the scaling factor, the MAXIMUM achievable F1 against the
    published list says whether any thresholding of this statistic could reproduce it. If the
    ceiling is low, the mismatch is upstream of the FDR rule.

J — WHAT THE MISSES ARE. The documented rule misses 119 published claims. If those cluster among
    claims supported in some draws but not a majority, the shortfall is draw dependence — the
    phenomenon under study. If they cluster by intensity or missingness, it is misspecification.

K — IS THE GRADIENT MONOTONE? The claim that "more imputed, more fragile" survives both rules is
    tested here, with Wilson intervals, because the 2-imputed class appears to exceed the
    3-imputed class under the documented rule and the ordering flips between rules.

L — THRESHOLD-FREE MEASURES. The spread of log10 q across draws, and the rule-invariant
    intersection (claims unstable under BOTH rules), which no convention choice can remove.
"""

import json
import math

import numpy as np

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import HOME, PXD018299_SITES, anchor_population
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic

SEEDS = range(20)
R = 250
S0, ALPHA = 0.1, 0.01
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]

rows, column = anchor_population(
    maxquant.read_table(verify(PXD018299_SITES.expected_content_hash,
                               filename=PXD018299_SITES.filename, home=HOME))
)


def cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return math.nan
    return math.log2(value) if value > 0 else math.nan


matrix = np.array([[cell(r, n) for n in KO + WT] for r in rows])
ids = [str(r[column["id"]]).strip() for r in rows]
measured = ~np.isnan(matrix)
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept, kept_measured = matrix[keep], measured[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    claim_ids = {str(c["deposit_id"]) for c in json.load(handle)["rows"]}
published = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - kept_measured.sum(1)
print(f"rows {kept.shape[0]}, published claims in the matrix {int(published.sum())}")


def q_and_direction(block: np.ndarray, seed: int, scale: float) -> tuple[np.ndarray, np.ndarray]:
    """Perseus's documented q with the null count scaled; scale 1.0 is documented, 0.5 the halved rule."""
    observed = _statistic(block[:, :3], block[:, 3:], S0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    thresholds = np.sort(magnitude)
    counts = []
    for assignment in _relabellings(3, 3, scheme="random_excluding_trivial",
                                    randomisations=R, seed=seed)[0]:
        mask = np.zeros(6, dtype=bool)
        mask[np.asarray(assignment[:3])] = True
        null = np.abs(_statistic(block[:, mask], block[:, ~mask], S0))[finite]
        null = np.sort(null[np.isfinite(null)])
        counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
    null_count = np.array(counts, dtype=float).mean(axis=0)
    observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
    fdr = scale * null_count / np.maximum(observed_count, 1)
    by_threshold = np.minimum.accumulate(fdr)
    q = np.full(observed.shape, np.inf)
    q[finite] = by_threshold[np.searchsorted(thresholds, magnitude, side="right") - 1]
    return q, observed


blocks = [downshifted_normal(kept, seed=seed, **DEFAULT).values for seed in SEEDS]
base = [q_and_direction(block, seed, 1.0) for block, seed in zip(blocks, SEEDS, strict=True)]
q_stack = np.array([q for q, _ in base])
direction = np.array([d for _, d in base])

print("\nI — F1 against the published list, across the scaling factor")
print(f"  {'scale':>7} {'calls':>7} {'precision':>10} {'recall':>8} {'F1':>7}")
best = None
for scale in (0.25, 0.4, 0.5, 0.6, 0.75, 1.0, 1.5, 2.0):
    called = ((q_stack * scale <= ALPHA) & (direction > 0)).sum(0) >= len(SEEDS) / 2
    hits = int((called & published).sum())
    precision = hits / max(int(called.sum()), 1)
    recall = hits / int(published.sum())
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    label = " (documented)" if scale == 1.0 else (" (halved)" if scale == 0.5 else "")
    print(f"  {scale:>7} {int(called.sum()):>7} {precision:>10.3f} {recall:>8.3f} {f1:>7.3f}{label}")
    if best is None or f1 > best[1]:
        best = (scale, f1)
print(f"  ceiling over this family: F1 {best[1]:.3f} at scale {best[0]}")

print("\nJ — the published claims the documented rule misses")
support = ((q_stack <= ALPHA) & (direction > 0))
counts = support.sum(0)
called = counts >= len(SEEDS) / 2
missed = published & ~called
print(f"  missed {int(missed.sum())} of {int(published.sum())}")
print(f"    supported in 0 draws:        {int((missed & (counts == 0)).sum())}")
print(f"    supported in 1-9 draws:      {int((missed & (counts >= 1) & (counts < 10)).sum())}")
for n in range(7):
    mask = missed & (imputed_count == n)
    if mask.any():
        print(f"    imputed {n}: {int(mask.sum()):>4} missed of {int((published & (imputed_count == n)).sum()):>4}")
measured_ko = np.nanmean(np.where(kept_measured[:, :3], kept[:, :3], np.nan), axis=1)
for label, mask in (("missed", missed), ("recovered", published & called)):
    values = measured_ko[mask]
    values = values[np.isfinite(values)]
    print(f"    {label:>9}: measured KO mean {values.mean():.2f} over {values.size} claims with any measured KO value")


def wilson(hits: int, total: int) -> tuple[float, float]:
    if total == 0:
        return (float("nan"), float("nan"))
    p, z = hits / total, 1.96
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return (max(0.0, centre - half), min(1.0, centre + half))


print("\nK — unstable share by imputed class, with 95% Wilson intervals")
halved_support = ((q_stack * 0.5 <= ALPHA) & (direction > 0))
halved_counts = halved_support.sum(0)
print(f"  {'imputed':>8} {'claims':>7} {'documented':>22} {'halved':>22}")
for n in range(7):
    mask = published & (imputed_count == n)
    if not mask.any():
        continue
    line = f"  {n:>8} {int(mask.sum()):>7}"
    for c in (counts, halved_counts):
        unstable = int((mask & (c > 0) & (c < len(SEEDS))).sum())
        low, high = wilson(unstable, int(mask.sum()))
        line += f"  {unstable / mask.sum():>6.1%} [{low:.0%}-{high:.0%}]".rjust(22)
    print(line)

print("\nL — threshold-free, and the rule-invariant floor")
with_imputed = published & (imputed_count > 0)
log_q = np.log10(np.clip(q_stack, 1e-12, None))
spread = log_q.max(0) - log_q.min(0)
print(f"  log10 q spread across draws, claims with an imputed value: median {np.median(spread[with_imputed]):.2f}, "
      f"90th {np.percentile(spread[with_imputed], 90):.2f}")
straddles = with_imputed & (q_stack.min(0) <= ALPHA) & (q_stack.max(0) > ALPHA)
print(f"  q range straddles 0.01 (documented): {int(straddles.sum())} of {int(with_imputed.sum())} "
      f"({straddles.sum() / with_imputed.sum():.1%})")
unstable_doc = with_imputed & (counts > 0) & (counts < len(SEEDS))
unstable_half = with_imputed & (halved_counts > 0) & (halved_counts < len(SEEDS))
both = unstable_doc & unstable_half
print(f"  unstable under the documented rule: {int(unstable_doc.sum())} "
      f"({unstable_doc.sum() / with_imputed.sum():.1%})")
print(f"  unstable under the halved rule:     {int(unstable_half.sum())} "
      f"({unstable_half.sum() / with_imputed.sum():.1%})")
print(f"  unstable under BOTH (the floor no convention removes): {int(both.sum())} "
      f"({both.sum() / with_imputed.sum():.1%})")
