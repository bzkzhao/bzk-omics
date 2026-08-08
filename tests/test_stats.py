"""`bzk/stats/` — written from `ARCHITECTURE.md` §4 and `ONTOLOGY.md` §6.5, tested the same way.

**No expected value here was copied from `colab_reproducefigure.ipynb`**, and that is the point of
the module. Each assertion is either an analytic identity (a case where the answer is known in
closed form), a property that must hold for any correct implementation, or a comparison against
`scipy`, which is an independent implementation rather than the thing being reproduced.

Checking against the notebook's outputs would make these tests the fourth instance of the shape
`HANDOFF.md` §8 catalogues: a measurement guaranteed by its own setup.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats as scipy_stats

from bzk.stats import (
    FDR_METHODS,
    IMPUTATION_METHODS,
    TESTS,
    benjamini_hochberg,
    downshifted_normal,
    presence_filter,
    welch_t,
)

# ── The registry contract ────────────────────────────────────────────────────────────────────────


def test_the_registry_holds_what_architecture_4_says_v0_1_holds() -> None:
    """§4's table: `welch_t` is the sanity check and the only test in v0.1. `perseus_s0` is default
    and required but unwritten; `moderated_t_ebayes` is deferred to v0.2 by ROADMAP.

    Asserted so the gap is visible rather than discovered later by someone selecting a default that
    does not exist — §4 is explicit that `welch_t` with BH is *not* `perseus_s0`.
    """
    assert set(TESTS) == {"welch_t"}
    assert set(FDR_METHODS) == {"BH"}
    assert set(IMPUTATION_METHODS) == {"none", "downshifted_normal"}


# ── welch_t, against an independent implementation and against identities ────────────────────────


def test_welch_matches_scipy_on_random_matrices() -> None:
    """`scipy.stats.ttest_ind(equal_var=False)` is an independent implementation of the same test.

    Agreement is meaningful precisely because scipy is not the thing being reproduced — unlike the
    notebook, whose arithmetic this module deliberately did not read.
    """
    rng = np.random.default_rng(20260807)
    a = rng.normal(12.0, 1.5, size=(200, 3))
    b = rng.normal(11.0, 2.5, size=(200, 3))
    got = welch_t(a, b)
    expected = scipy_stats.ttest_ind(a, b, axis=1, equal_var=False)
    np.testing.assert_allclose(got.p_value, expected.pvalue, rtol=1e-10)
    np.testing.assert_allclose(got.log2fc, a.mean(axis=1) - b.mean(axis=1), rtol=1e-12)


def test_identical_groups_give_no_difference_and_p_of_one() -> None:
    """An identity: same values in both arms, so the difference is zero and t is zero."""
    a = np.array([[10.0, 11.0, 12.0]])
    got = welch_t(a, a.copy())
    assert got.log2fc[0] == pytest.approx(0.0)
    assert got.p_value[0] == pytest.approx(1.0)


def test_log2fc_is_the_difference_of_means_in_the_units_given() -> None:
    """`TestResult.log2fc` names a claim about units — this layer works in log2 throughout, so the
    difference of log2 means *is* the log2 fold change. Asserted against a case with a known answer:
    a group at 2^13 against one at 2^11 is a 4-fold change, log2 4 = 2."""
    a = np.log2(np.array([[8192.0, 8192.0, 8192.0]]))
    b = np.log2(np.array([[2048.0, 2048.0, 2048.0]]))
    assert welch_t(a, b).log2fc[0] == pytest.approx(2.0)


def test_a_row_with_no_variance_anywhere_is_nan_not_significant() -> None:
    """Zero variance in both groups leaves the standard error at zero: t is undefined. Returning
    NaN rather than 0 or 1 keeps it out of BH's denominator instead of ranking a fabrication."""
    a = np.array([[5.0, 5.0, 5.0]])
    b = np.array([[9.0, 9.0, 9.0]])
    assert np.isnan(welch_t(a, b).p_value[0])


def test_fewer_than_two_replicates_is_refused() -> None:
    """Welch needs a within-group variance. One replica has none, and n=1 would silently produce
    a division by zero rather than an error."""
    with pytest.raises(ValueError, match=">=2 replicates"):
        welch_t(np.array([[1.0]]), np.array([[2.0, 3.0]]))


# ── Benjamini-Hochberg, from the definition ──────────────────────────────────────────────────────


def test_bh_matches_an_independent_implementation() -> None:
    rng = np.random.default_rng(11)
    p = rng.uniform(size=500)
    expected = scipy_stats.false_discovery_control(p, method="bh")
    np.testing.assert_allclose(benjamini_hochberg(p), expected, rtol=1e-12)


def test_bh_is_monotone_and_never_below_the_raw_p() -> None:
    """Two properties any correct step-up procedure has, checked rather than assumed."""
    rng = np.random.default_rng(12)
    p = rng.uniform(size=1000)
    adjusted = benjamini_hochberg(p)
    assert np.all(adjusted >= p - 1e-12)
    order = np.argsort(p)
    assert np.all(np.diff(adjusted[order]) >= -1e-12)


def test_bh_excludes_nan_from_the_denominator() -> None:
    """A site whose test was undefined has no p-value to adjust, and counting it in m would deflate
    every other site's adjusted value — a quiet gain in significance from rows never tested."""
    p = np.array([0.01, 0.02, 0.03, 0.04])
    with_nans = np.array([0.01, 0.02, 0.03, 0.04, np.nan, np.nan])
    np.testing.assert_allclose(benjamini_hochberg(p), benjamini_hochberg(with_nans)[:4])
    assert np.all(np.isnan(benjamini_hochberg(with_nans)[4:]))


def test_bh_of_a_single_p_value_is_itself() -> None:
    assert benjamini_hochberg(np.array([0.031]))[0] == pytest.approx(0.031)


# ── Imputation ───────────────────────────────────────────────────────────────────────────────────


def test_a_stochastic_method_without_a_seed_is_refused() -> None:
    """I15, and `ARCHITECTURE.md` §4: without a seed the same inputs give different answers. A
    default seed would make an irreproducible analysis look reproducible, which is worse."""
    with pytest.raises(ValueError, match="requires a seed"):
        downshifted_normal(np.array([[1.0, np.nan]]))


def test_the_same_seed_gives_the_same_matrix() -> None:
    """What the seed is *for* — I9 fails otherwise, and a different seed must actually differ."""
    values = np.array([[10.0, np.nan, 12.0], [np.nan, np.nan, 9.0]])
    a = downshifted_normal(values, seed=0)
    b = downshifted_normal(values, seed=0)
    c = downshifted_normal(values, seed=1)
    np.testing.assert_array_equal(a.values, b.values)
    assert not np.array_equal(a.values, c.values)


def test_measured_values_are_never_touched() -> None:
    """The generated/measured line, at its sharpest: imputation fills holes and nothing else."""
    values = np.array([[10.0, np.nan, 12.0], [7.0, 8.0, np.nan]])
    out = downshifted_normal(values, seed=0)
    measured = ~np.isnan(values)
    np.testing.assert_array_equal(out.values[measured], values[measured])
    np.testing.assert_array_equal(out.imputed_mask, np.isnan(values))
    assert (out.n_values_imputed, out.n_values_total) == (2, 6)


def test_draws_land_below_the_observed_distribution() -> None:
    """The property that makes it *downshifted*: the generated values must sit below the measured
    ones, at roughly `downshift_sd` SDs. Checked as a distributional property over many draws
    rather than against specific numbers, which would be checking the RNG."""
    rng = np.random.default_rng(3)
    values = rng.normal(20.0, 2.0, size=(4000, 6))
    values[rng.uniform(size=values.shape) < 0.3] = np.nan
    observed = values[~np.isnan(values)]
    out = downshifted_normal(values, downshift_sd=1.8, width_sd=0.3, seed=0)
    drawn = out.values[out.imputed_mask]
    assert drawn.mean() == pytest.approx(observed.mean() - 1.8 * observed.std(ddof=1), rel=0.02)
    assert drawn.std(ddof=1) == pytest.approx(0.3 * observed.std(ddof=1), rel=0.05)


def test_per_sample_scope_differs_from_whole_matrix() -> None:
    """§6.5 records both, and they are not interchangeable: on a matrix with uneven depth per
    column they give materially different answers, which is why `scope` is stored on the node."""
    rng = np.random.default_rng(4)
    values = np.vstack([rng.normal(20.0, 1.0, 200), rng.normal(10.0, 1.0, 200)]).T
    values[rng.uniform(size=values.shape) < 0.3] = np.nan
    whole = downshifted_normal(values, seed=0, scope="whole_matrix")
    per = downshifted_normal(values, seed=0, scope="per_sample")
    assert not np.allclose(whole.values[whole.imputed_mask], per.values[per.imputed_mask])


def test_an_unknown_scope_is_refused() -> None:
    with pytest.raises(ValueError, match="§6.5"):
        downshifted_normal(np.array([[1.0, np.nan]]), seed=0, scope="per_plate")


# ── The presence rule, which decides the tested population ───────────────────────────────────────


def test_either_and_both_are_different_rules() -> None:
    """The curation record declares ">=2 replicates in either group"; §6.5's table counts "both".
    Two documents, one dataset, different populations — so the caller states which, and a row
    measured in only one arm is exactly where they disagree."""
    numerator = np.array([[1.0, 2.0, np.nan], [np.nan, np.nan, np.nan]])
    denominator = np.array([[np.nan, np.nan, np.nan], [1.0, 2.0, 3.0]])
    either = presence_filter(numerator, denominator, min_per_group=2, either=True)
    both = presence_filter(numerator, denominator, min_per_group=2, either=False)
    np.testing.assert_array_equal(either, [True, True])
    np.testing.assert_array_equal(both, [False, False])
