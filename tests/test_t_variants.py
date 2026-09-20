"""The four t variants of `bzk/stats/tests.py` — the set PC2 chooses among.

`walk/PREREG-PXD026748-reconstruction.md:97-102` leaves the shotgun arm's test unfixed and names the
set that may settle it: *"{Student, Welch} × {S0 applied to P, S0 not applied}"*, with `S0 = 1`. A
choice made among four implementations is only as good as the four, so each is checked here against
arithmetic done by hand, and Student's additionally against `scipy`.

**The hand case, used by all four.** Two groups with unequal n, chosen so every quantity is exact:

    numerator   = [1, 2, 3]           n1 = 3, mean 2, sample variance 1
    denominator = [2, 4, 6, 8, 10]    n2 = 5, mean 6, sample variance 10

Equal group sizes would not do: at n1 == n2 the pooled and Welch standard errors coincide, so
Student and Welch would agree and a test that confused them would pass.

    Welch     se^2 = 1/3 + 10/5 = 7/3          df = (7/3)^2 / ((1/3)^2/2 + 2^2/4) = 98/19
    Student   sp^2 = (2*1 + 4*10)/6 = 7        se^2 = 7*(1/3 + 1/5) = 56/15,  df = 6

and the statistic is `-4 / (se + S0)` with `S0` either 0 or 1. The P values are read off
`scipy.stats.t.sf` at those hand-computed statistics and degrees of freedom — `scipy` supplies the
*t* distribution's survival function, which is a special function and not arithmetic, and which the
module under test does not compute either.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats as scipy_stats

from bzk.stats import S0, student_t, student_t_s0, welch_t, welch_t_s0

#: The hand case above, as a one-row pair.
NUMERATOR = np.array([[1.0, 2.0, 3.0]])
DENOMINATOR = np.array([[2.0, 4.0, 6.0, 8.0, 10.0]])

DIFFERENCE = -4.0
WELCH_SE = math.sqrt(7 / 3)
WELCH_DF = 98 / 19
STUDENT_SE = math.sqrt(56 / 15)
STUDENT_DF = 6.0


def _p(t: float, df: float) -> float:
    return float(2.0 * scipy_stats.t.sf(abs(t), df))


def test_s0_is_the_registered_value() -> None:
    """`:102` fixes it at 1. A different value would make PC2's choice a different four."""
    assert S0 == 1.0


def test_welch_matches_the_hand_computation() -> None:
    result = welch_t(NUMERATOR, DENOMINATOR)
    assert result.log2fc[0] == pytest.approx(DIFFERENCE)
    assert result.p_value[0] == pytest.approx(_p(DIFFERENCE / WELCH_SE, WELCH_DF), rel=1e-12)


def test_student_matches_the_hand_computation() -> None:
    result = student_t(NUMERATOR, DENOMINATOR)
    assert result.log2fc[0] == pytest.approx(DIFFERENCE)
    assert result.p_value[0] == pytest.approx(_p(DIFFERENCE / STUDENT_SE, STUDENT_DF), rel=1e-12)


def test_welch_s0_divides_by_the_standard_error_plus_s0_on_welchs_df() -> None:
    """Tusher et al.'s modification: `S0` enters the denominator, and nothing else moves."""
    result = welch_t_s0(NUMERATOR, DENOMINATOR)
    assert result.log2fc[0] == pytest.approx(DIFFERENCE)
    assert result.p_value[0] == pytest.approx(_p(DIFFERENCE / (WELCH_SE + S0), WELCH_DF), rel=1e-12)


def test_student_s0_divides_by_the_standard_error_plus_s0_on_students_df() -> None:
    result = student_t_s0(NUMERATOR, DENOMINATOR)
    assert result.log2fc[0] == pytest.approx(DIFFERENCE)
    assert result.p_value[0] == pytest.approx(
        _p(DIFFERENCE / (STUDENT_SE + S0), STUDENT_DF), rel=1e-12
    )


def test_the_four_variants_are_four_and_not_two() -> None:
    """All four P values differ on the hand case, which is what makes PC2 a choice.

    Pooling changes the standard error only because the group sizes differ; `S0` changes it for any
    design. A variant that had been wired to the wrong helper would collide with another here.
    """
    p = [
        welch_t(NUMERATOR, DENOMINATOR).p_value[0],
        student_t(NUMERATOR, DENOMINATOR).p_value[0],
        welch_t_s0(NUMERATOR, DENOMINATOR).p_value[0],
        student_t_s0(NUMERATOR, DENOMINATOR).p_value[0],
    ]
    assert len({round(value, 12) for value in p}) == 4


def test_s0_never_makes_a_row_more_significant() -> None:
    """The modification damps; it cannot sharpen. True row-wise for any data, since `S0 > 0` only
    ever enlarges the denominator, so it is asserted over random matrices rather than one case."""
    rng = np.random.default_rng(20260920)
    a = rng.normal(12.0, 1.5, size=(200, 4))
    b = rng.normal(11.0, 2.5, size=(200, 6))

    assert np.all(welch_t_s0(a, b).p_value >= welch_t(a, b).p_value)
    assert np.all(student_t_s0(a, b).p_value >= student_t(a, b).p_value)


def test_student_matches_scipy_on_random_matrices() -> None:
    """`scipy.stats.ttest_ind(equal_var=True)` is an independent implementation of the same test —
    the check `welch_t` already carries, for the variant added beside it."""
    rng = np.random.default_rng(20260807)
    a = rng.normal(12.0, 1.5, size=(200, 4))
    b = rng.normal(11.0, 2.5, size=(200, 6))
    got = student_t(a, b)
    expected = scipy_stats.ttest_ind(a, b, axis=1, equal_var=True)

    np.testing.assert_allclose(got.p_value, expected.pvalue, rtol=1e-10)
    np.testing.assert_allclose(got.log2fc, a.mean(axis=1) - b.mean(axis=1), rtol=1e-12)


def test_every_variant_refuses_a_single_replicate() -> None:
    """One replicate gives no variance, so there is no test. Raising beats a column of NaN."""
    one = np.array([[1.0]])
    for variant in (welch_t, student_t, welch_t_s0, student_t_s0):
        with pytest.raises(ValueError, match=">=2 replicates per group"):
            variant(one, DENOMINATOR)
