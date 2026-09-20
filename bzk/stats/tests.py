"""Registered statistical tests, plus the four t variants the PXD026748 gate chooses among.

`ARCHITECTURE.md` §4's registry table lists three entries and their status:

  - `perseus_s0`         default and required — SAM-style, fold-change curvature `s0`,
                         permutation FDR. **Written 2026-09-21, in `bzk/stats/perseus_s0.py`**,
                         once `PXD018299`'s publication supplied the two values `ROADMAP.md`
                         l.73 deferred the entry for. It is registered; this module's four
                         variants below are still not.
  - `moderated_t_ebayes` v0.2, deferred by `ROADMAP.md`.
  - `welch_t`            *"Sanity check. Plain two-sample test; useful for detecting when the
                         choice of test is load-bearing."*

`welch_t` was the only registered entry until 2026-09-21 and is now one of two, and §4 is explicit
that it is not a substitute for the default:
*"`perseus_s0` is not the same test as `welch_t` with Benjamini-Hochberg. The `s0` parameter
introduces a fold-change dependence into the significance threshold... A reproduction that ignores
this will not match the group's numbers even when it recovers the same proteins."* `welch_t` is
written first because the 12-of-14 figure on record was measured under it (`ROADMAP.md` § In scope),
so it is the comparison that exists — not because it is the right default.

**The other three variants are written but not registered, and that is a decision.**
`walk/PREREG-PXD026748-reconstruction.md:97-102` leaves the shotgun arm's test unfixed and gives PC2
a set of four implementations to settle it from: *"{Student, Welch} × {S0 applied to P, S0 not
applied}"*. All four are written here. Registering them would put three names in `TESTS` that
`ARCHITECTURE.md` §4's table does not list, and §4 is normative — code that diverges from it is
wrong, or the document is wrong and must be amended first (`CLAUDE.md`). Worse, `student_t_s0` with
`S0 = 1` sits one permutation-FDR step away from `perseus_s0`, and a registry entry would have read
as that gap having been closed. So the pre-registration's "registered set" is enumerated by the
instrument that uses it, and `TESTS` holds exactly what §4's table names. Amending §4 to admit
these is a separate change with its own reason.

**That last sentence was written while `perseus_s0` was unwritten, and the gap is now closed by the
entry itself** (2026-09-21, `bzk/stats/perseus_s0.py`) rather than by one of these standing in for
it. The reasoning above is unchanged by that: these four are still not §4's entries, and the one
that is now exists.

**The S0 modification is Tusher et al.'s, in one line:** the statistic divides the difference in
means by `standard error + S0` rather than by the standard error, and the P value is read off the
*same* degrees of freedom as the unmodified variant. The effect is to damp the significance of rows
whose standard error is small for want of spread rather than for want of effect. `S0 = 1` is the
value `walk/PREREG-PXD026748-reconstruction.md:102` registers; it is a module constant rather than a
parameter, because a per-call `s0` would make the four variants a continuum and PC2's choice
unrecordable as one of four.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bzk.stats.registry import TestResult, register

#: Tusher et al.'s fold-change curvature constant, fixed at the pre-registration's value.
S0 = 1.0


@dataclass(frozen=True)
class _Moments:
    """What every two-sample t is made of, before the statistic is formed.

    Split out because the four variants differ in exactly two places — how the standard error and
    the degrees of freedom are formed (pooled or not), and whether `S0` enters the denominator. A
    second copy of Welch-Satterthwaite for the S0 variant would be a mirror between two sources
    with nothing guarding it, which is the defect class `CLAUDE.md` point 3 names.
    """

    difference: np.ndarray
    standard_error: np.ndarray
    df: np.ndarray


def _moments(numerator: np.ndarray, denominator: np.ndarray, *, pooled: bool) -> _Moments:
    """Row-wise difference of means, its standard error, and the degrees of freedom.

    `pooled=False` is Welch: each group's variance is weighted by its own n and the degrees of
    freedom come from Welch-Satterthwaite, so unequal variances do not borrow strength.
    `pooled=True` is Student: one variance estimate for both groups, on `n1 + n2 - 2` df, which is
    correct when the variances are equal and anti-conservative when they are not.
    """
    n1, n2 = numerator.shape[1], denominator.shape[1]
    if n1 < 2 or n2 < 2:
        raise ValueError(f"a two-sample t needs >=2 replicates per group; got {n1} and {n2}")

    mean1, mean2 = numerator.mean(axis=1), denominator.mean(axis=1)
    # ddof=1: the sample variance. ddof=0 would understate the spread at n=3 and inflate every t.
    var1, var2 = numerator.var(axis=1, ddof=1), denominator.var(axis=1, ddof=1)

    with np.errstate(divide="ignore", invalid="ignore"):
        if pooled:
            pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
            se_squared = pooled_var * (1.0 / n1 + 1.0 / n2)
            df = np.full(se_squared.shape, float(n1 + n2 - 2))
        else:
            se_squared = var1 / n1 + var2 / n2
            df = se_squared**2 / ((var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1))
        return _Moments(
            difference=mean1 - mean2,
            standard_error=np.sqrt(se_squared),
            df=np.asarray(df, dtype=float),
        )


def _t_test(
    numerator: np.ndarray, denominator: np.ndarray, *, pooled: bool, s0: float
) -> TestResult:
    """The statistic and its two-sided P, for one of the four variants.

    NaNs must already be resolved by imputation; a row containing one yields NaN rather than being
    silently dropped, so a caller that skipped imputation gets an obviously wrong answer instead of
    a plausible one over a shrunken population.

    A row with zero variance in both groups has `standard_error == 0`: at `s0 == 0` its t is +-inf
    or NaN and its P is NaN, left as it falls rather than coerced to 0 or 1 — it is undefined, and
    BH excludes NaN from its count rather than ranking a fabricated value. At `s0 > 0` the same row
    has a finite statistic, which is one of the things the modification does and is not a defect.
    """
    from scipy import stats  # local: only the p-value needs it, and it is the heaviest import

    moments = _moments(numerator, denominator, pooled=pooled)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = moments.difference / (moments.standard_error + s0)
    p = 2.0 * stats.t.sf(np.abs(t), moments.df)
    return TestResult(log2fc=moments.difference, p_value=np.asarray(p, dtype=float))


@register("welch_t")
def welch_t(numerator: np.ndarray, denominator: np.ndarray) -> TestResult:
    """Two-sample *t* with unequal variances (Welch), row-wise, two-sided.

    Written from the definition rather than called out to `scipy.stats.ttest_ind`, for one reason:
    the Welch-Satterthwaite degrees of freedom and the survival function are the whole of the test,
    and having them here means the arithmetic is inspectable next to the invariant that records it.
    `scipy` supplies only the *t* distribution's CDF, which is a special function and not arithmetic.
    """
    return _t_test(numerator, denominator, pooled=False, s0=0.0)


def student_t(numerator: np.ndarray, denominator: np.ndarray) -> TestResult:
    """Two-sample *t* with a pooled variance (Student), row-wise, two-sided.

    Not registered — see the module docstring. It exists because the PXD026748 methods do not say
    which of the two the shotgun arm ran, and PC2 settles it against published numbers rather than
    by assumption.
    """
    return _t_test(numerator, denominator, pooled=True, s0=0.0)


def welch_t_s0(numerator: np.ndarray, denominator: np.ndarray) -> TestResult:
    """Welch's *t* with the difference divided by `standard error + S0`, P on Welch's df."""
    return _t_test(numerator, denominator, pooled=False, s0=S0)


def student_t_s0(numerator: np.ndarray, denominator: np.ndarray) -> TestResult:
    """Student's *t* with the difference divided by `standard error + S0`, P on `n1 + n2 - 2` df."""
    return _t_test(numerator, denominator, pooled=True, s0=S0)
