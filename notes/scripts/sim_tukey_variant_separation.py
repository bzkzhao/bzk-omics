"""Basis for PREREG-PXD032267-gate.md §4's tolerance: how far apart the candidate tests' p-values fall.

Simulates a balanced 2 x 2 design, n = 3 per cell, unit variance, with an effect of 0.5-2.5 in the
tested cell. Keeps designs whose T1 p lies in 0.01-0.06, which is the range of Table 8's p-values. For
each design it reports the smallest gap between any two variants' p-values, and which pairs fall
within the registered tolerance. Seeded, deterministic, no data from any deposit.

    .venv/bin/python notes/scripts/sim_tukey_variant_separation.py
"""

from __future__ import annotations

import collections
import itertools

import numpy as np
from scipy import stats
from scipy.stats import studentized_range

TOLERANCE = 1e-4
NAMES = ("T1", "T2", "T3", "T4", "T5")


def variant_pvalues(x: np.ndarray) -> list[float]:
    """Cells in row order KO control, KO TAC, WT control, WT TAC; the pair is WT TAC vs WT control."""
    m = x.mean(axis=1)
    ss_within = float(((x - m[:, None]) ** 2).sum())
    mse8 = ss_within / 8
    g = m.reshape(2, 2)
    interaction = g - g.mean(axis=1, keepdims=True) - g.mean(axis=0, keepdims=True) + g.mean()
    mse9 = (ss_within + 3 * float((interaction**2).sum())) / 9
    d = abs(m[3] - m[2])
    return [
        float(studentized_range.sf(d / np.sqrt(mse8 / 3), 4, 8)),
        float(studentized_range.sf(d / np.sqrt(mse9 / 3), 4, 9)),
        float(2 * stats.t.sf(d / np.sqrt(2 * mse8 / 3), 8)),
        float(stats.ttest_ind(x[3], x[2]).pvalue),
        float(stats.ttest_ind(x[3], x[2], equal_var=False).pvalue),
    ]


def main() -> None:
    rng = np.random.default_rng(0)
    gaps: list[float] = []
    close: collections.Counter[str] = collections.Counter()
    for _ in range(2000):
        x = rng.normal(0.0, 1.0, (4, 3))
        x[3] += rng.uniform(0.5, 2.5)
        p = variant_pvalues(x)
        if not 0.01 < p[0] < 0.06:
            continue
        pairs = list(itertools.combinations(range(5), 2))
        gaps.append(min(abs(p[i] - p[j]) for i, j in pairs))
        for i, j in pairs:
            if abs(p[i] - p[j]) <= TOLERANCE:
                close[f"{NAMES[i]}~{NAMES[j]}"] += 1
    arr = np.array(gaps)
    print(f"designs kept: {arr.size}")
    print(
        f"smallest inter-variant gap, quantiles 0/1/5/50%: {np.quantile(arr, [0, 0.01, 0.05, 0.5])}"
    )
    print(f"share of designs with some pair within {TOLERANCE}: {(arr <= TOLERANCE).mean():.3f}")
    print(f"pairs within tolerance: {dict(close)}")


if __name__ == "__main__":
    main()
