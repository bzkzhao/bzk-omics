"""Round-7 descriptive, UNREGISTERED checks: does a single rule explain both deposits?

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round7.py

Round 6 left two candidates for the factor of two that attempt 2 fitted as `joint_half`:
  * the MEDIAN rather than the mean false-positive count over randomisations (SAM's own estimator):
    241 calls against Table 3's 282, where the mean gives 158;
  * a π0 SCALING of the null count. π0 on Munnur's shotgun matrix is 0.490 — a factor of two.

Both are properties of a rule, not of a deposit, and π0 is a property of the data, so one rule can
loosen a matrix where most proteins move and leave one where few do. This measures π0 on BOTH
deposits and scores four estimators on each: the documented mean rule, the median rule, the
π0-scaled mean rule, and the fitted halving.

The anchor's own published count is 798; Munnur's Table 3 calls 282. A rule that lands near both,
without being fitted to either, is the rule. Nothing here is registered.
"""

import numpy as np
from scipy import stats

from bzk.adapters import maxquant
from bzk.provenance.raw_store import verify
from bzk.sources.pxd018299_h10 import (
    GATE_ALPHA,
    GATE_S0,
    HOME,
    PXD018299_SITES,
    SHOTGUN_CURATION,
    SUPP_TABLE_1,
    _deposit_for,
    _gate_inputs,
    _parse_arm,
    _supplement_path,
    anchor_population,
)
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic

SEEDS = range(20)
R = 250
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
ANCHOR_KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
ANCHOR_WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]


def q_values(matrix: np.ndarray, left: list[int], right: list[int], s0: float, seed: int,
             *, estimator: str, pi0: float) -> np.ndarray:
    """Perseus's q, with the null count taken as the mean or the median over randomisations.

    `pi0` scales the null count; 1.0 leaves the documented rule unchanged. Validated in round 6:
    with estimator="mean" and pi0=1.0 this reproduces `perseus_s0(..., sidedness="joint")` exactly.
    """
    order = list(left) + list(right)
    ordered = matrix[:, order]
    split = len(left)
    observed = _statistic(ordered[:, :split], ordered[:, split:], s0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    thresholds = np.sort(magnitude)
    counts = []
    for assignment in _relabellings(len(left), len(right), scheme="random_excluding_trivial",
                                    randomisations=R, seed=seed)[0]:
        mask = np.zeros(len(order), dtype=bool)
        mask[np.asarray(assignment[:split])] = True
        null = np.abs(_statistic(ordered[:, mask], ordered[:, ~mask], s0))[finite]
        null = np.sort(null[np.isfinite(null)])
        counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
    stack = np.array(counts, dtype=float)
    null_count = np.median(stack, axis=0) if estimator == "median" else stack.mean(axis=0)
    observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
    fdr = pi0 * null_count / np.maximum(observed_count, 1)
    by_threshold = np.minimum.accumulate(fdr)
    q = np.full(observed.shape, np.inf)
    q[finite] = by_threshold[np.searchsorted(thresholds, magnitude, side="right") - 1]
    return q


def pi0_of(matrix: np.ndarray, left: list[int], right: list[int]) -> float:
    p = stats.ttest_ind(matrix[:, left], matrix[:, right], axis=1, equal_var=True).pvalue
    p = p[np.isfinite(p)]
    return float(min(1.0, 2 * np.mean(p > 0.5)))


# ---- the two matrices ---------------------------------------------------------------------------
curation, _, _ = _parse_arm(SHOTGUN_CURATION, HOME)
shotgun, wt, ko, complete, accessions, calls, _ = _gate_inputs(
    curation, _deposit_for(curation, HOME), _supplement_path(SUPP_TABLE_1, HOME)
)
target = np.array([a in calls for a in accessions])

rows, column = anchor_population(
    maxquant.read_table(verify(PXD018299_SITES.expected_content_hash,
                               filename=PXD018299_SITES.filename, home=HOME))
)


def anchor_cell(row: list[str], name: str) -> float:
    raw = row[column[name]].strip() if name in column else ""
    try:
        value = float(raw)
    except ValueError:
        return np.nan
    return np.log2(value) if value > 0 else np.nan


anchor = np.array([[anchor_cell(r, n) for n in ANCHOR_KO + ANCHOR_WT] for r in rows])
keep = ((~np.isnan(anchor[:, :3])).sum(1) >= 1) | ((~np.isnan(anchor[:, 3:])).sum(1) >= 1)
anchor = anchor[keep]
print(f"shotgun proteins {shotgun.shape[0]} (Table 3 calls {int(target.sum())}); "
      f"anchor rows {anchor.shape[0]} (the paper called 798)")

print("\nπ0, the estimated null proportion (Storey, 2 * mean(p > 0.5)), at the default cell")
pi0 = {}
for name, matrix, left, right in (("PXD026748 shotgun", shotgun, list(wt), list(ko)),
                                  ("PXD018299 anchor", anchor, [0, 1, 2], [3, 4, 5])):
    estimates = [pi0_of(downshifted_normal(matrix, seed=seed, **DEFAULT).values, left, right)
                 for seed in SEEDS]
    pi0[name] = float(np.median(estimates))
    print(f"  {name:>20}: median {pi0[name]:.3f} (range {min(estimates):.3f}-{max(estimates):.3f})")

print("\ncalls under four estimators, median over 20 seeds")
print(f"{'deposit':>20} {'estimator':>22} {'calls':>7} {'target':>8}")
for name, matrix, left, right, s0, alpha, published in (
    ("PXD026748 shotgun", shotgun, list(wt), list(ko), GATE_S0, GATE_ALPHA, int(target.sum())),
    ("PXD018299 anchor", anchor, [0, 1, 2], [3, 4, 5], 0.1, 0.01, 798),
):
    for label, estimator, scale in (("mean (documented)", "mean", 1.0),
                                    ("median (SAM)", "median", 1.0),
                                    (f"mean x pi0={pi0[name]:.2f}", "mean", pi0[name]),
                                    ("mean x 0.5 (the fitted halving)", "mean", 0.5)):
        counts = []
        for seed in SEEDS:
            filled = downshifted_normal(matrix, seed=seed, **DEFAULT).values
            q = q_values(filled, left, right, s0, seed, estimator=estimator, pi0=scale)
            if published == 798:  # the anchor's claims are one-directional, as the paper's are
                d = _statistic(filled[:, left], filled[:, right], s0)
                counts.append(int(((q <= alpha) & (d > 0)).sum()))
            else:
                counts.append(int((q <= alpha).sum()))
        print(f"{name:>20} {label:>22} {int(np.median(counts)):>7} {published:>8}")

print("\n  A rule that lands near both targets without being fitted to either is the rule.")
print("  If the pi0-scaled mean does that, the halving was a data property of one deposit,")
print("  not a convention, and the anchor's documented figure needs no transfer at all.")
