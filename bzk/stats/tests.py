"""Registered statistical tests. `welch_t` only in v0.1.

`ARCHITECTURE.md` §4's registry table lists three entries and their status:

  - `perseus_s0`         default and required — SAM-style, fold-change curvature `s0`,
                         permutation FDR. **Not implemented here.**
  - `moderated_t_ebayes` v0.2, deferred by `ROADMAP.md`.
  - `welch_t`            *"Sanity check. Plain two-sample test; useful for detecting when the
                         choice of test is load-bearing."*

Only `welch_t` is written, and §4 is explicit that this is **not** a substitute for the default:
*"`perseus_s0` is not the same test as `welch_t` with Benjamini-Hochberg. The `s0` parameter
introduces a fold-change dependence into the significance threshold... A reproduction that ignores
this will not match the group's numbers even when it recovers the same proteins."* `welch_t` is
written first because the 12-of-14 figure on record was measured under it (`ROADMAP.md` § In scope),
so it is the comparison that exists — not because it is the right default.
"""

from __future__ import annotations

import numpy as np

from bzk.stats.registry import TestResult, register


@register("welch_t")
def welch_t(numerator: np.ndarray, denominator: np.ndarray) -> TestResult:
    """Two-sample *t* with unequal variances (Welch), row-wise, two-sided.

    Written from the definition rather than called out to `scipy.stats.ttest_ind`, for one reason:
    the Welch-Satterthwaite degrees of freedom and the survival function are the whole of the test,
    and having them here means the arithmetic is inspectable next to the invariant that records it.
    `scipy` supplies only the *t* distribution's CDF, which is a special function and not arithmetic.

    NaNs must already be resolved by imputation; a row containing one yields NaN rather than being
    silently dropped, so a caller that skipped imputation gets an obviously wrong answer instead of
    a plausible one over a shrunken population.
    """
    from scipy import stats  # local: only the p-value needs it, and it is the heaviest import

    n1 = numerator.shape[1]
    n2 = denominator.shape[1]
    if n1 < 2 or n2 < 2:
        raise ValueError(f"Welch's t needs >=2 replicates per group; got {n1} and {n2}")

    mean1, mean2 = numerator.mean(axis=1), denominator.mean(axis=1)
    # ddof=1: the sample variance. ddof=0 would understate the spread at n=3 and inflate every t.
    var1, var2 = numerator.var(axis=1, ddof=1), denominator.var(axis=1, ddof=1)

    se_squared = var1 / n1 + var2 / n2
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (mean1 - mean2) / np.sqrt(se_squared)
        # Welch-Satterthwaite. This is what makes it Welch rather than Student: the denominator
        # weights each group's variance by its own n, so unequal variances do not borrow strength.
        df = se_squared**2 / ((var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1))
    p = 2.0 * stats.t.sf(np.abs(t), df)
    # A row with zero variance in both groups has se == 0: t is +-inf or NaN and p is NaN. Left as
    # NaN rather than coerced to 0 or 1 — it is undefined, and BH below excludes it from the count
    # rather than ranking a fabricated value.
    return TestResult(log2fc=mean1 - mean2, p_value=np.asarray(p, dtype=float))
