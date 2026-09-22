"""Round-6 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_round6.py

Not an independent path: the same instruments the registered runs use, re-aggregated here. No
registered verdict, pre-registration or committed fixture is touched.

The review refuted my account of why the within-treatment null called fewer proteins, and proposed
four cheaper routes to the factor of two. This measures all of them.

A — THE NULL TAILS, MEASURED.  I inferred the restricted null's behaviour from call counts. Wrong
    way round: compare the null |d| distributions directly, and report the per-seed spread of the
    call counts rather than a single majority number.
B — IS THERE A TREATMENT EFFECT AT ALL?  PLpro was applied to lysates for 30 minutes, so on the
    shotgun matrix the treatment may shift nothing. If it does not, restricted and unrestricted
    nulls are near enough the same object and there is no direction to explain.
C — THE IMPUTATION GRID UNDER THE DOCUMENTED RULE.  If any of the 18 registered settings reproduces
    Table 3's 282 calls under unrestricted `joint`, the halving was never an FDR convention: it was
    Munnur's imputation differing from our default cell, and the transfer problem dissolves.
D — MEDIAN RATHER THAN MEAN over randomisations. SAM estimates the false-positive count as the
    median across permutations; Perseus's wording reads as a mean. Where tail counts are small and
    skewed the median can be half the mean, which would loosen Munnur and leave the anchor alone.
E — A π0 FACTOR.  SAM-family implementations scale the null count by the estimated null proportion.
    π0 near 0.5 is a factor of two. Estimated on both matrices, Storey-style.
"""

import numpy as np
from bzk.sources.pxd018299_h10 import (
    GATE_ALPHA,
    GATE_S0,
    HOME,
    SHOTGUN_CURATION,
    SUPP_TABLE_1,
    _deposit_for,
    _gate_inputs,
    _parse_arm,
    _supplement_path,
)
from bzk.sources.pxd026748_reconstruction import family_members, sample_axes
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic, perseus_s0
from scipy import stats

SEEDS = range(20)
R = 250
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}

curation, _, _ = _parse_arm(SHOTGUN_CURATION, HOME)
values, wt, ko, complete, accessions, calls, _ = _gate_inputs(
    curation, _deposit_for(curation, HOME), _supplement_path(SUPP_TABLE_1, HOME)
)
target = np.array([a in calls for a in accessions])
axes = sample_axes(curation)
order = list(wt) + list(ko)
treatments = sorted(set(axes.treatment))
stratum = np.array([treatments.index(axes.treatment[i]) for i in order])
genotype = np.array([0] * len(wt) + [1] * len(ko))
print(f"proteins {values.shape[0]}, complete-case {int(complete.sum())}, Table 3 calls {int(target.sum())}")


def filled_at(setting: dict, seed: int) -> np.ndarray:
    return downshifted_normal(values, seed=seed, **setting).values


def score(hit: np.ndarray) -> tuple[int, float, float]:
    """Calls, and precision/recall against Table 3 among complete-case proteins."""
    hits = int((hit & complete & target).sum())
    precision = hits / max(int((hit & complete).sum()), 1)
    recall = hits / max(int((complete & target).sum()), 1)
    return int(hit.sum()), precision, recall


print("\nB — is there a treatment effect on the shotgun matrix at all?")
filled = filled_at(DEFAULT, 0)
ordered = filled[:, order]
by_treatment = _statistic(ordered[:, stratum == 0], ordered[:, stratum == 1], GATE_S0)
by_genotype = _statistic(ordered[:, genotype == 0], ordered[:, genotype == 1], GATE_S0)
for name, d in (("treatment (PLpro WT vs mutant)", by_treatment), ("genotype (WT vs KO)", by_genotype)):
    finite = np.isfinite(d)
    print(f"  {name:>34}: |d| median {np.median(np.abs(d[finite])):.3f}, "
          f"95th {np.percentile(np.abs(d[finite]), 95):.3f}, 99th {np.percentile(np.abs(d[finite]), 99):.3f}")

print("\nA — the two nulls, measured directly (seed 0, default cell)")


def null_tail(restricted: bool) -> np.ndarray:
    observed = _statistic(ordered[:, genotype == 0], ordered[:, genotype == 1], GATE_S0)
    finite = np.isfinite(observed)
    tails = []
    if restricted:
        import itertools
        per = []
        for s in (0, 1):
            members = np.where(stratum == s)[0]
            n_wt = int((genotype[members] == 0).sum())
            per.append([np.array(c) for c in itertools.combinations(members, n_wt)])
        every = [np.sort(np.concatenate([a, b])) for a in per[0] for b in per[1]]
        identity = np.sort(np.where(genotype == 0)[0])
        pool = [a for a in every if not np.array_equal(a, identity)]
        rng = np.random.default_rng(0)
        chosen = [pool[i] for i in rng.choice(len(pool), size=min(R, len(pool)), replace=False)]
    else:
        chosen = _relabellings(len(wt), len(ko), scheme="random_excluding_trivial",
                               randomisations=R, seed=0)[0]
        chosen = [a[: len(wt)] for a in chosen]
    for assignment in chosen:
        mask = np.zeros(len(order), dtype=bool)
        mask[np.asarray(assignment)] = True
        tails.append(np.abs(_statistic(ordered[:, mask], ordered[:, ~mask], GATE_S0))[finite])
    return np.concatenate(tails)


for label, restricted in (("unrestricted", False), ("within-treatment", True)):
    tail = null_tail(restricted)
    tail = tail[np.isfinite(tail)]
    print(f"  {label:>16} null |d|: median {np.median(tail):.3f}, 95th {np.percentile(tail, 95):.3f}, "
          f"99th {np.percentile(tail, 99):.3f}, 99.9th {np.percentile(tail, 99.9):.3f}")

print("\n  per-seed call counts (not a majority summary)")
for sidedness in ("joint", "joint_half"):
    counts = []
    for seed in SEEDS:
        out = perseus_s0(filled_at(DEFAULT, seed)[:, wt], filled_at(DEFAULT, seed)[:, ko],
                         s0=GATE_S0, alpha=GATE_ALPHA, randomisations=R, seed=seed,
                         sidedness=sidedness, scheme="random_excluding_trivial")
        counts.append(int(out.significant.sum()))
    print(f"  {sidedness:>16}: median {int(np.median(counts))}, range {min(counts)}-{max(counts)}")

print("\nC — the 18 registered imputation settings under the DOCUMENTED rule (unrestricted joint)")
print(f"{'width':>6} {'downshift':>10} {'scope':>13} {'calls':>7} {'precision':>10} {'recall':>8}")
seen = set()
best = None
for member in family_members():
    setting = {"width_sd": member.width_sd, "downshift_sd": member.downshift_sd, "scope": member.scope}
    key = tuple(setting.values())
    if key in seen:
        continue
    seen.add(key)
    called = np.zeros(values.shape[0])
    for seed in SEEDS:
        block = filled_at(setting, seed)
        out = perseus_s0(block[:, wt], block[:, ko], s0=GATE_S0, alpha=GATE_ALPHA,
                         randomisations=R, seed=seed, sidedness="joint",
                         scheme="random_excluding_trivial")
        called += out.significant.astype(float)
    calls_n, precision, recall = score(called >= len(SEEDS) / 2)
    print(f"{setting['width_sd']:>6} {setting['downshift_sd']:>10} {setting['scope']:>13} "
          f"{calls_n:>7} {precision:>10.3f} {recall:>8.3f}")
    if best is None or abs(calls_n - int(target.sum())) < abs(best[0] - int(target.sum())):
        best = (calls_n, setting, precision, recall)
print(f"  closest to Table 3's {int(target.sum())}: {best[1]} with {best[0]} calls "
      f"(precision {best[2]:.3f}, recall {best[3]:.3f})")

print("\nD — median rather than mean over randomisations (default cell, unrestricted joint)")
for use_median in (False, True):
    counts = []
    for seed in SEEDS:
        block = filled_at(DEFAULT, seed)
        ordered_block = block[:, order]
        observed = _statistic(ordered_block[:, genotype == 0], ordered_block[:, genotype == 1], GATE_S0)
        finite = np.isfinite(observed)
        magnitude = np.abs(observed[finite])
        thresholds = np.sort(magnitude)
        per_permutation = []
        for assignment in _relabellings(len(wt), len(ko), scheme="random_excluding_trivial",
                                        randomisations=R, seed=seed)[0]:
            mask = np.zeros(len(order), dtype=bool)
            mask[np.asarray(assignment[: len(wt)])] = True
            null = np.abs(_statistic(ordered_block[:, mask], ordered_block[:, ~mask], GATE_S0))[finite]
            null = np.sort(null[np.isfinite(null)])
            per_permutation.append(null.size - np.searchsorted(null, thresholds, side="left"))
        stack = np.array(per_permutation, dtype=float)
        null_count = np.median(stack, axis=0) if use_median else stack.mean(axis=0)
        observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
        fdr = np.divide(null_count, np.maximum(observed_count, 1))
        # q is the smallest FDR over the thresholds that would still call the row, and the
        # eligible thresholds are those at or below its statistic — a PREFIX minimum over
        # `thresholds` sorted ascending. Taking it the other way round calls everything.
        q_by_threshold = np.minimum.accumulate(fdr)
        q = np.full(observed.shape, np.inf)
        q[finite] = q_by_threshold[np.searchsorted(thresholds, magnitude, side="right") - 1]
        counts.append(int((q <= GATE_ALPHA).sum()))
    print(f"  {'median' if use_median else 'mean':>6} over randomisations: calls median "
          f"{int(np.median(counts))}, range {min(counts)}-{max(counts)}  (Table 3: {int(target.sum())})")

print("\nE — π0, the estimated null proportion (Storey, 2 * mean(p > 0.5))")
block = filled_at(DEFAULT, 0)
p_shotgun = stats.ttest_ind(block[:, wt], block[:, ko], axis=1, equal_var=True).pvalue
print(f"  PXD026748 shotgun: π0 ≈ {min(1.0, 2 * np.mean(p_shotgun > 0.5)):.3f} over {p_shotgun.size} proteins")
print("  A low π0 here, with π0 near 1 on the anchor, would explain both directions at once.")
