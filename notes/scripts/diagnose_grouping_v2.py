"""Round-5 descriptive, UNREGISTERED check: Perseus's "preserve grouping in randomizations".

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_grouping_v2.py

The question. Attempt 2 fitted a halved null count (`joint_half`) to reproduce PXD026748's
published Perseus calls, and attempt 3 transferred it to PXD018299. Perseus's documentation
defines its q-value with no halving. An adversarial review proposed the alternative: Munnur's
Table 3 compares WT against ISG15-KO across twelve shotgun samples in which PLpro treatment is
nested (WT-PLpro and mutant-PLpro, three each per genotype). If that run preserved the treatment
grouping in its randomisations, permutations exchange labels only within a treatment, the null is
narrower, and the FDR falls — which would look exactly like a factor of two, and would NOT
transfer to the anchor's unnested 3-against-3 design.

What this does. It rebuilds the gate's shotgun matrix, then computes q three ways at the
published settings (s0 = 1, FDR 0.05): unrestricted `joint`, unrestricted `joint_half`, and
`joint` with permutations restricted to within-treatment relabellings. It scores each against
Table 3's calls on complete-case proteins, as gate G does.

It imports `_statistic` and `_q_values` from `bzk.stats.perseus_s0` — private helpers — so that the
restricted null is scored by the same arithmetic as the registered runs, rather than a second
implementation of it. Nothing here is registered, and no committed fixture is touched.
"""

import itertools

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
from bzk.sources.pxd026748_reconstruction import sample_axes
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _q_values, _statistic, perseus_s0

SEEDS = range(20)
RANDOMISATIONS = 250

curation, _, _ = _parse_arm(SHOTGUN_CURATION, HOME)
deposit = _deposit_for(curation, HOME)
values, wt, ko, complete, accessions, calls, _ = _gate_inputs(
    curation, deposit, _supplement_path(SUPP_TABLE_1, HOME)
)
target = np.array([a in calls for a in accessions])
print(f"proteins {values.shape[0]}, complete-case {int(complete.sum())}, Table 3 calls "
      f"{int(target.sum())} ({int((target & complete).sum())} complete-case)")

# Treatment stratum per column, from the curation record via `sample_axes` — the same accessor the
# gate uses, so the strata line up with `wt`/`ko` by construction rather than by a second lookup.
axes = sample_axes(curation)
order = list(wt) + list(ko)
treatments = sorted(set(axes.treatment))
stratum = np.array([treatments.index(axes.treatment[i]) for i in order])
genotype = np.array([0] * len(wt) + [1] * len(ko))
print("columns as ordered here (index, genotype, treatment):")
for position, i in enumerate(order):
    print(f"  {i:>3}  {axes.genotype[i]:>4}  stratum {stratum[position]}  {axes.treatment[i][:58]}")
print("  stratum sizes:", [int((stratum == s).sum()) for s in (0, 1)])


def within_treatment_relabellings(limit: int, seed: int) -> list[np.ndarray]:
    """Label swaps that keep each treatment's genotype split, excluding the identity."""
    per_stratum = []
    for s in (0, 1):
        members = np.where(stratum == s)[0]  # positions within `order`, not raw column indices
        n_wt = int((genotype[members] == 0).sum())
        per_stratum.append([np.array(c) for c in itertools.combinations(members, n_wt)])
    every = [(a, b) for a in per_stratum[0] for b in per_stratum[1]]
    identity = np.where(genotype == 0)[0]
    kept = []
    for a, b in every:
        assignment = np.concatenate([a, b])
        if len(assignment) == len(identity) and np.array_equal(np.sort(assignment), np.sort(identity)):
            continue
        kept.append(np.sort(assignment))
    rng = np.random.default_rng(seed)
    if len(kept) > limit:
        kept = [kept[i] for i in rng.choice(len(kept), size=limit, replace=False)]
    return kept


def restricted_q(matrix: np.ndarray, seed: int) -> np.ndarray:
    """Perseus's documented q-value, with the null drawn only from within-treatment relabellings."""
    ordered = matrix[:, order]
    observed = _statistic(ordered[:, genotype == 0], ordered[:, genotype == 1], GATE_S0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    null_total = np.zeros_like(magnitude)
    relabellings = within_treatment_relabellings(RANDOMISATIONS, seed)
    for assignment in relabellings:
        mask = np.zeros(len(order), dtype=bool)
        mask[assignment] = True
        null = np.abs(_statistic(ordered[:, mask], ordered[:, ~mask], GATE_S0))[finite]
        null = np.sort(null[np.isfinite(null)])
        null_total += (null.size - np.searchsorted(null, magnitude, side="left")).astype(float)
    q = np.full(observed.shape, np.inf)
    q[finite] = _q_values(magnitude, null_total, magnitude, upper=True, draws=len(relabellings))
    return q


print(f"\nwithin-treatment relabellings available: {len(within_treatment_relabellings(10**6, 0))}")
print("\nscored against Table 3 on complete-case proteins, 20 seeds, majority call")
for label in ("joint (unrestricted)", "joint_half (unrestricted)", "joint (within-treatment null)"):
    called = np.zeros(values.shape[0])
    for seed in SEEDS:
        filled = downshifted_normal(values, downshift_sd=1.8, width_sd=0.3, seed=seed, scope="per_sample").values
        if label.startswith("joint (within"):
            hit = restricted_q(filled, seed) <= GATE_ALPHA
        else:
            sidedness = "joint_half" if "half" in label else "joint"
            out = perseus_s0(filled[:, wt], filled[:, ko], s0=GATE_S0, alpha=GATE_ALPHA,
                             randomisations=RANDOMISATIONS, seed=seed, sidedness=sidedness,
                             scheme="random_excluding_trivial")
            hit = out.significant
        called += hit.astype(float)
    majority = called >= len(SEEDS) / 2
    hits = int((majority & complete & target).sum())
    precision = hits / max(int((majority & complete).sum()), 1)
    recall = hits / max(int((complete & target).sum()), 1)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    print(f"  {label:>30}: calls {int(majority.sum()):>5} (Table 3: {int(target.sum())})  "
          f"complete-case precision {precision:.3f}  recall {recall:.3f}  F1 {f1:.3f}")
print("\n  If the restricted null reproduces Table 3 without halving, the factor of two belongs to")
print("  Munnur's nested design, and `joint_half` should not have been transferred to the anchor.")
