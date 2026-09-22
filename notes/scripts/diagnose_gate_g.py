"""Descriptive, UNREGISTERED diagnosis of gate G's failure (walk/PREREG-PXD018299-H10.md §4).

Usage, from the repository root:  .venv/bin/python notes/scripts/diagnose_gate_g.py

Gate G failed with precision 1.0 and recall 0.50 (joint) or 0.66 (per_side) on all eight
variants: every complete-case protein we call, Perseus also called, but Perseus called more. This
script asks WHY. It changes nothing registered and cannot re-admit a variant. It separates two
explanations:

  (a) The statistic ranks proteins the same way Perseus does, and only the FDR threshold is more
      conservative. Then the published calls should be the top of our |d| ranking.
  (b) The statistic itself differs, for example standard error against standard deviation in the
      s0 denominator. Then the published calls are not a prefix of our ranking.

It uses seed 0 at the registered default cell only.
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
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import perseus_s0

curation, _, _ = _parse_arm(SHOTGUN_CURATION, HOME)
deposit = _deposit_for(curation, HOME)
values, wt, ko, complete, accessions, calls, _ = _gate_inputs(
    curation, deposit, _supplement_path(SUPP_TABLE_1, HOME)
)
target = np.array([a in calls for a in accessions])
filled = downshifted_normal(values, downshift_sd=1.8, width_sd=0.3, seed=0, scope="per_sample").values
A, B = filled[:, wt], filled[:, ko]
print(f"rows {len(accessions)}, complete-case {int(complete.sum())}, published calls {int(target.sum())}"
      f" (complete-case {int(target[complete].sum())})")

# The two candidate statistics, computed directly.
nA, nB = A.shape[1], B.shape[1]
diff = A.mean(1) - B.mean(1)
pooled_var = ((nA - 1) * A.var(1, ddof=1) + (nB - 1) * B.var(1, ddof=1)) / (nA + nB - 2)
se = np.sqrt(pooled_var * (1 / nA + 1 / nB))
sd = np.sqrt(pooled_var)
for name, denom in (("SE + s0 (as implemented)", se), ("SD + s0 (alternative)", sd)):
    d = np.abs(diff / (denom + GATE_S0))
    cc = np.where(complete)[0]
    order = cc[np.argsort(-d[cc])]
    k = int(target[complete].sum())
    top = set(order[:k])
    hit = sum(target[i] for i in top)
    min_pub = d[cc][target[cc]].min()
    above = int(((d[cc] > min_pub) & ~target[cc]).sum())
    print(f"[{name}] top-{k} of complete cases by |d| contains {hit} of the {k} published calls;"
          f" unpublished complete cases ranked above the weakest published call: {above}")

# Where the implemented variants put the threshold, against Perseus's 282 calls.
d_all = np.abs(diff / (se + GATE_S0))
rank = np.argsort(-d_all)
t282 = d_all[rank[281]]
for side in ("joint", "per_side"):
    out = perseus_s0(A, B, s0=GATE_S0, alpha=GATE_ALPHA, randomisations=250, seed=0,
                     sidedness=side, scheme="random_excluding_trivial")
    n_called = int(out.significant.sum())
    q_at_282 = float(np.sort(out.q_value)[281])
    up = int((out.significant & (out.direction > 0)).sum())
    print(f"[{side}] called {n_called} of {len(accessions)} (Perseus: 282; 72 up, 210 down in WT/KO);"
          f" ours up {up}, down {n_called - up}; the 282nd-smallest q = {q_at_282:.4f}"
          f" (Perseus's 282nd call sits at <= {GATE_ALPHA})")
print(f"|d| at Perseus's 282nd rank under our statistic: {t282:.3f}")
pub_all = target
print(f"published calls among our top-282 by |d| (all rows): {int(pub_all[rank[:282]].sum())} of 282")
