"""`bzk/stats/perseus_s0.py` — §4's default and required entry, against independent arithmetic.

**Nothing here was copied from a Perseus run, and nothing here is a data run.** What is checked is
the definition: the SAM statistic, the permutation null, the FDR at a threshold, and the q-value as
the smallest FDR over the thresholds that would still call a row. The expected values come either
from closed-form arithmetic written out in a docstring, or from a second enumeration written in
this file that shares no line with the module — the shape `tests/test_anova.py` uses for the same
reason: an error in one route could not be reproduced by the other.

**The 3-against-3 case is enumerable, which is what makes P1 exact.** There are C(6,3) = 20
relabellings of six columns into two groups of three, so the whole null can be written down rather
than sampled, and every count below is an integer somebody can check by hand.
"""

from __future__ import annotations

import itertools
from typing import Any

import numpy as np
import pytest
from scipy import stats as scipy_stats

from bzk.stats import TESTS, welch_t
from bzk.stats.perseus_s0 import PerseusS0Error, perseus_s0

#: Six rows, three against three, chosen so every group mean and variance is exact in binary
#: floating point and the interesting cases are all present: a large separation, no difference at
#: all, a tiny difference on a tiny spread, and a row whose two group means are exactly equal.
NUMERATOR = np.array(
    [
        [4.0, 5.0, 6.0],  # mean 5, sample variance 1
        [1.0, 2.0, 3.0],  # identical to its denominator
        [2.0, 2.0, 2.0],  # no spread either side
        [1.0, 1.5, 2.0],  # a small difference on a small spread
        [8.0, 4.0, 0.0],  # wide spread, mean 4
        [9.0, 1.0, 5.0],  # mean 5, equal to its denominator's
    ]
)
DENOMINATOR = np.array(
    [
        [1.0, 2.0, 3.0],  # mean 2, sample variance 1
        [1.0, 2.0, 3.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.5, 1.75],
        [4.0, 4.0, 4.0],
        [1.0, 9.0, 5.0],
    ]
)


def _hand_statistic(a: np.ndarray, b: np.ndarray, s0: float) -> np.ndarray:
    """`d` from the definition, written here and sharing no line with the module.

    Pooled variance, pooled standard error, then `(mean_A − mean_B) / (s + s0)`. This is the
    independent route: it is the arithmetic a reader would do with a calculator, not a second call
    into `_moments`.
    """
    n_a, n_b = a.shape[1], b.shape[1]
    var_a = a.var(axis=1, ddof=1)
    var_b = b.var(axis=1, ddof=1)
    pooled = ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
    standard_error = np.sqrt(pooled * (1.0 / n_a + 1.0 / n_b))
    return np.asarray((a.mean(axis=1) - b.mean(axis=1)) / (standard_error + s0))


def _hand_null(a: np.ndarray, b: np.ndarray, s0: float) -> np.ndarray:
    """Every non-identity relabelling's `d`, as a `(19, rows)` array, by enumeration."""
    combined = np.hstack([a, b])
    total, n_a = combined.shape[1], a.shape[1]
    return np.array(
        [
            _hand_statistic(
                combined[:, list(group)],
                combined[:, [i for i in range(total) if i not in set(group)]],
                s0,
            )
            for group in itertools.combinations(range(total), n_a)
            if group != tuple(range(n_a))
        ]
    )


def _hand_q(d: np.ndarray, null: np.ndarray) -> np.ndarray:
    """The joint q-value per row, from the brief's definition, by enumeration.

    `FDR(t)` is the mean over permutations of the null count at or beyond `t`, over the observed
    count at or beyond `t`; a row's q is the smallest such FDR over the observed thresholds that
    would still call it. Written as a loop over thresholds, which is unusably slow at real sizes
    and exactly right here.
    """
    absolute = np.abs(d)
    draws = null.shape[0]
    return np.array(
        [
            min(
                ((np.abs(null) >= t).sum() / draws) / (absolute >= t).sum()
                for t in absolute
                if t <= value
            )
            for value in absolute
        ]
    )


# ── P1 · the hand-computed case ─────────────────────────────────────────────────────────────────


def test_p1_the_statistic_matches_closed_form_arithmetic() -> None:
    """Two rows written out by hand, to anchor the enumeration below on real arithmetic.

    Row 0: `A = [4, 5, 6]`, mean 5, sample variance 1; `B = [1, 2, 3]`, mean 2, variance 1. The
    pooled variance is `(2·1 + 2·1)/4 = 1`, so `s = sqrt(1 · (1/3 + 1/3)) = sqrt(2/3)` and, at
    `s0 = 0.1`, `d = 3 / (sqrt(2/3) + 0.1) = 3.27443…`.

    Row 2: `A = [2, 2, 2]`, `B = [1, 1, 1]`. Both variances are 0, so `s = 0` and the whole
    denominator is `s0`: `d = 1 / 0.1 = 10`. **This is what `s0` is for** — without it the row has
    infinite evidence from three identical readings.
    """
    result = perseus_s0(
        NUMERATOR,
        DENOMINATOR,
        s0=0.1,
        alpha=0.05,
        randomisations=20,
        seed=0,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )

    assert result.d[0] == pytest.approx(3.0 / (np.sqrt(2.0 / 3.0) + 0.1), rel=1e-12)
    assert result.d[2] == pytest.approx(10.0, rel=1e-12)
    assert result.d[1] == pytest.approx(0.0)
    assert result.d[5] == pytest.approx(0.0)


def test_p1_the_null_counts_fdr_and_q_match_an_independent_enumeration() -> None:
    """All 19 non-identity relabellings, the FDR at every observed threshold, and every q-value.

    The second route is `_hand_*` above: a loop over `itertools.combinations` and a loop over
    thresholds, with the statistic written from the definition. It shares no line with the module,
    so agreement to 1e-12 is a real check rather than one implementation agreeing with itself.
    """
    s0 = 0.1
    result = perseus_s0(
        NUMERATOR,
        DENOMINATOR,
        s0=s0,
        alpha=0.05,
        randomisations=20,
        seed=0,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )
    d = _hand_statistic(NUMERATOR, DENOMINATOR, s0)
    null = _hand_null(NUMERATOR, DENOMINATOR, s0)

    assert null.shape == (19, 6)
    np.testing.assert_allclose(result.d, d, rtol=1e-12)
    np.testing.assert_allclose(result.q_value, _hand_q(d, null), rtol=1e-12)

    # **1/19 here is the mirror's floor, not the draw count's.** Corrected 2026-09-22: this comment
    # read *"the smallest a 19-draw null can produce … the reason a 19-permutation null cannot
    # support an FDR of 0.01"*, and that generalisation is wrong. Under `joint` the mirror
    # relabelling — group A given exactly B's columns — reproduces every observed `|d|` exactly,
    # so the null count at every threshold is at least one and q is floored at one over the number
    # of relabellings whatever the data say. Drop the mirror and the same 19-ish null reaches q =
    # 0: `exhaustive_excluding_trivial` runs 18 draws here and is not floored. What cannot support
    # an FDR of 0.01 is `joint` **with the mirror**, at any draw count, and that is a property of
    # the scheme rather than of the enumeration's size.
    assert result.q_value[2] == pytest.approx(1.0 / 19.0, rel=1e-12)
    assert result.significant.tolist() == [False, False, False, False, False, False]


def test_p1b_the_standard_error_is_pooled_and_not_welchs() -> None:
    """Unequal group sizes, because at `n_A == n_B` the two standard errors are the same number.

    **Found by a mutation, not by reading.** Swapping `pooled=True` for `pooled=False` left P1
    green: at three against three, `pooled_var · (1/n + 1/n) = (v_A + v_B)/n`, which is Welch's
    `v_A/n + v_B/n` exactly, for any variances. So P1 cannot tell the two apart and this case
    exists to. At three against five with different spreads they differ, and §4's entry is the
    pooled one — SAM's `s` is the pooled standard error.

    By hand: `A = [1, 2, 3]`, mean 2, variance 1; `B = [2, 4, 6, 8, 10]`, mean 6, variance 10.
    Pooled variance `(2·1 + 4·10)/6 = 7`, so `s = sqrt(7 · (1/3 + 1/5)) = sqrt(56/15)`, and at
    `s0 = 0.1`, `d = −4 / (sqrt(56/15) + 0.1)`. Welch's `s` would be `sqrt(1/3 + 10/5)`.
    """
    numerator = np.array([[1.0, 2.0, 3.0]])
    denominator = np.array([[2.0, 4.0, 6.0, 8.0, 10.0]])

    result = perseus_s0(
        numerator,
        denominator,
        s0=0.1,
        alpha=0.05,
        randomisations=60,
        seed=0,
        sidedness="joint",
        scheme="random",
    )

    pooled = -4.0 / (np.sqrt(56.0 / 15.0) + 0.1)
    welch = -4.0 / (np.sqrt(7.0 / 3.0) + 0.1)
    assert result.d[0] == pytest.approx(pooled, rel=1e-12)
    assert result.d[0] != pytest.approx(welch, rel=1e-6)


# ── P2 · s0 bites ───────────────────────────────────────────────────────────────────────────────


def test_p2_s0_withdraws_significance_from_a_tiny_standard_error() -> None:
    """A row with a small difference and a tiny spread is significant at `s0 = 0` and not at 1.

    This is §4's whole point about the entry: *"the `s0` parameter introduces a fold-change
    dependence into the significance threshold"*. Without it, three near-identical readings each
    side give an arbitrarily large `t` for an arbitrarily small difference — the artefact SAM's
    denominator exists to damp.
    """
    numerator = np.array([[1.000, 1.001, 1.002], [5.0, 1.0, 9.0]])
    denominator = np.array([[1.010, 1.011, 1.012], [1.0, 9.0, 5.0]])
    settings: dict[str, Any] = {
        "alpha": 0.2,
        "randomisations": 20,
        "seed": 0,
        "sidedness": "joint",
        "scheme": "exhaustive_when_small",
    }

    without = perseus_s0(numerator, denominator, s0=0.0, **settings)
    with_s0 = perseus_s0(numerator, denominator, s0=1.0, **settings)

    assert abs(without.d[0]) > 10.0
    assert abs(with_s0.d[0]) < 0.02
    assert bool(without.significant[0]) is True
    assert bool(with_s0.significant[0]) is False


# ── P3 · q is monotone ──────────────────────────────────────────────────────────────────────────


def test_p3_q_is_monotone_in_the_absolute_statistic_under_joint() -> None:
    """A row with a larger `|d|` never has a larger q. That is what the "smallest FDR over the
    thresholds that would still call it" construction buys, and the raw `FDR(|d|)` does not have
    it: the ratio can rise again at an extreme threshold where the observed count falls to one."""
    rng = np.random.default_rng(11)
    numerator = rng.normal(6.0, 1.0, size=(60, 4))
    denominator = rng.normal(5.0, 1.0, size=(60, 4))

    result = perseus_s0(
        numerator,
        denominator,
        s0=0.1,
        alpha=0.05,
        randomisations=200,
        seed=1,
        sidedness="joint",
        scheme="random",
    )
    order = np.argsort(np.abs(result.d))
    ordered_q = result.q_value[order]

    assert np.all(np.diff(ordered_q) <= 1e-12)


# ── P4 · the seed ───────────────────────────────────────────────────────────────────────────────


def test_p4_the_seed_is_honoured_and_changes_the_null_under_random() -> None:
    """The same seed gives identical q-values; a different one gives a different null.

    `random` only — under `exhaustive_when_small` at this size the null is the whole set of
    relabellings and the seed cannot move it, which is asserted here too because it is the
    property that makes the exhaustive scheme worth having.
    """
    rng = np.random.default_rng(5)
    numerator = rng.normal(6.0, 1.0, size=(40, 4))
    denominator = rng.normal(5.0, 1.0, size=(40, 4))
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.05,
        "randomisations": 60,
        "sidedness": "joint",
        "scheme": "random",
    }

    first = perseus_s0(numerator, denominator, seed=0, **settings)
    again = perseus_s0(numerator, denominator, seed=0, **settings)
    other = perseus_s0(numerator, denominator, seed=1, **settings)

    np.testing.assert_array_equal(first.q_value, again.q_value)
    assert not np.array_equal(first.q_value, other.q_value)

    exhaustive = {**settings, "scheme": "exhaustive_when_small", "randomisations": 100}
    np.testing.assert_array_equal(
        perseus_s0(NUMERATOR, DENOMINATOR, seed=0, **exhaustive).q_value,
        perseus_s0(NUMERATOR, DENOMINATOR, seed=7, **exhaustive).q_value,
    )


# ── P5 · the permutation scheme ─────────────────────────────────────────────────────────────────


def test_p5_the_exhaustive_scheme_uses_nineteen_relabellings_and_falls_back_above_the_cut() -> None:
    """C(6,3) = 20, so 19 non-identity relabellings; C(12,6) = 924 > 250, so `random` at 250.

    The identity is excluded because under it the "null" is the observed data itself — including
    it would pull every FDR towards the observed counts by exactly one draw, which is a bias with
    no argument behind it. The fallback is reported rather than silent: `scheme_used` says which
    null ran, and `randomisations_used` says how large it was.
    """
    small = perseus_s0(
        NUMERATOR,
        DENOMINATOR,
        s0=0.1,
        alpha=0.05,
        randomisations=19,
        seed=0,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )

    assert small.scheme == "exhaustive_when_small"
    assert small.scheme_used == "exhaustive"
    assert small.randomisations_used == 19

    # **The cut bites at 19 and not at 20**, which is the one point where the brief states the
    # rule two ways — see `_relabellings`. Asserted on both sides so the resolution is visible
    # rather than implied by the case above.
    below = perseus_s0(
        NUMERATOR,
        DENOMINATOR,
        s0=0.1,
        alpha=0.05,
        randomisations=18,
        seed=0,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )
    assert below.scheme_used == "random"
    assert below.randomisations_used == 18

    rng = np.random.default_rng(2)
    large = perseus_s0(
        rng.normal(size=(5, 6)),
        rng.normal(size=(5, 6)),
        s0=0.1,
        alpha=0.05,
        randomisations=250,
        seed=0,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )

    assert large.scheme_used == "random"
    assert large.randomisations_used == 250


def test_p5b_the_identity_relabelling_is_not_in_the_exhaustive_null() -> None:
    """Asserted on the null itself rather than only on its size: a scheme that dropped some other
    relabelling and kept the identity would also have 19 draws."""
    from bzk.stats.perseus_s0 import _relabellings

    draws, used, count = _relabellings(
        3, 3, scheme="exhaustive_when_small", randomisations=20, seed=0
    )
    groups = {tuple(sorted(draw[:3].tolist())) for draw in draws}

    assert used == "exhaustive"
    assert count == 19
    assert (0, 1, 2) not in groups
    assert len(groups) == 19
    assert (3, 4, 5) in groups  # the mirror is a relabelling and is kept


# ── P6 · the two sidedness variants ─────────────────────────────────────────────────────────────


def test_p6_per_side_differs_from_joint_on_an_asymmetric_case() -> None:
    """Eight rows up and one row down, so the two directions have nothing like the same null.

    Under `joint` the single downward row is judged against a threshold set and a null that the
    eight upward rows dominate; under `per_side` it is judged against the downward tail alone. The
    two give different q-values, which is the whole reason the choice has to be made on published
    output rather than here.
    """
    rng = np.random.default_rng(13)
    numerator = np.vstack([rng.normal(9.0, 0.3, size=(8, 4)), rng.normal(5.0, 0.3, size=(1, 4))])
    denominator = np.vstack([rng.normal(5.0, 0.3, size=(8, 4)), rng.normal(9.0, 0.3, size=(1, 4))])
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.05,
        "randomisations": 200,
        "seed": 0,
        "sidedness": "joint",
        "scheme": "random",
    }

    joint = perseus_s0(numerator, denominator, **settings)
    per_side = perseus_s0(numerator, denominator, **{**settings, "sidedness": "per_side"})

    np.testing.assert_allclose(joint.d, per_side.d, rtol=1e-12)
    assert not np.allclose(joint.q_value, per_side.q_value)
    assert per_side.sidedness == "per_side"


# ── P7 · no silent defaults ─────────────────────────────────────────────────────────────────────


def test_p7_every_parameter_is_required_and_a_missing_one_fails_loudly() -> None:
    """`ROADMAP.md` l.73 deferred this entry because its values were unknown. A default would put
    a number in `Analysis.parameters_json` that no publication and no collaborator supplied, which
    is the failure ADR-0017 names: *being 95% right about `s0` and permutation FDR is worse than
    useless*."""
    with pytest.raises(TypeError, match="randomisations"):
        perseus_s0(
            NUMERATOR, DENOMINATOR, s0=0.1, alpha=0.05, seed=0, sidedness="joint", scheme="random"
        )  # type: ignore[call-arg]
    with pytest.raises(TypeError, match="seed"):
        perseus_s0(
            NUMERATOR,
            DENOMINATOR,
            s0=0.1,
            alpha=0.05,
            randomisations=20,
            sidedness="joint",
            scheme="random",
        )  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        TESTS["perseus_s0"].run(NUMERATOR, DENOMINATOR)

    with pytest.raises(PerseusS0Error, match="sidedness"):
        perseus_s0(
            NUMERATOR,
            DENOMINATOR,
            s0=0.1,
            alpha=0.05,
            randomisations=20,
            seed=0,
            sidedness="one_sided",
            scheme="random",
        )
    with pytest.raises(PerseusS0Error, match="scheme"):
        perseus_s0(
            NUMERATOR,
            DENOMINATOR,
            s0=0.1,
            alpha=0.05,
            randomisations=20,
            seed=0,
            sidedness="joint",
            scheme="all",
        )


# ── P8 · the registry entry ─────────────────────────────────────────────────────────────────────


def test_p8_the_registry_entry_declares_what_an_analysis_must_record() -> None:
    """`ONTOLOGY.md` l.155: `parameters_json` is determined by `test`, and `perseus_s0` *"requires
    `s0` and the randomisation count, which ARCHITECTURE §4 makes mandatory"*. §4's own sentence
    names three — `s0`, `fdr` and the number of randomisations — and the declaration is that
    superset, so neither document is under-recorded.

    **`welch_t` is unchanged**, which is asserted rather than assumed: the same callable is still
    registered under its name, it declares no parameters, and its numbers on a fixed matrix are
    what they were.
    """
    entry = TESTS["perseus_s0"]

    assert entry.name == "perseus_s0"
    assert entry.run is perseus_s0
    assert "s0" in entry.parameters
    assert "randomisations" in entry.parameters
    assert entry.parameters == ("s0", "fdr", "randomisations")

    assert TESTS["welch_t"].run is welch_t
    assert TESTS["welch_t"].parameters == ()
    # Row 0 by hand: both groups have variance 1 at n = 3, so Welch's standard error is
    # `sqrt(2/3)` and Welch-Satterthwaite gives exactly 4 degrees of freedom.
    unchanged = welch_t(NUMERATOR, DENOMINATOR)
    assert unchanged.log2fc[0] == pytest.approx(3.0)
    assert unchanged.p_value[0] == pytest.approx(
        2.0 * scipy_stats.t.sf(3.0 / np.sqrt(2.0 / 3.0), 4), rel=1e-12
    )


def test_the_outcome_carries_every_declared_parameter_value() -> None:
    """A declaration nothing can be filled from would be a second table of names. Each declared
    parameter has its value on the outcome, `fdr` under the `alpha` the brief names it by."""
    result = perseus_s0(
        NUMERATOR,
        DENOMINATOR,
        s0=0.1,
        alpha=0.01,
        randomisations=19,
        seed=3,
        sidedness="joint",
        scheme="exhaustive_when_small",
    )

    assert result.s0 == 0.1
    assert result.alpha == 0.01
    assert result.randomisations == 19
    assert result.randomisations_used == 19
    assert result.seed == 3
    assert result.direction.tolist() == [1.0, 0.0, 1.0, 1.0, 0.0, 0.0]


# ── the trivial-relabelling schemes ─────────────────────────────────────────────────────────────


def test_joint_reaches_a_q_of_one_percent_only_once_the_mirror_is_excluded() -> None:
    """The mirror floors every q at `1 / draws` under `joint`, and excluding it removes the floor.

    Both runs are the same matrix, the same statistic and the same 3-against-3 design; the only
    difference is whether the one relabelling that reproduces every observed `|d|` is in the null.
    With it, nothing can reach 0.01 however strong the effect. Without it, strong rows reach 0.

    **This is the finding that made the two `_excluding_trivial` schemes necessary**, and it is
    asserted rather than described: `walk/PREREG-PXD018299-H10.md` §4 makes a variant that cannot
    reach 0.01 at 3 against 3 refuted by the anchor's own publication, which reports 798 calls at
    that level from that design.
    """
    rng = np.random.default_rng(0)
    numerator = rng.normal(0.0, 1.0, size=(400, 3))
    denominator = rng.normal(0.0, 1.0, size=(400, 3))
    numerator[:60] += 4.0
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.01,
        "randomisations": 250,
        "seed": 0,
        "sidedness": "joint",
    }

    with_mirror = perseus_s0(numerator, denominator, scheme="exhaustive_when_small", **settings)
    without = perseus_s0(numerator, denominator, scheme="exhaustive_excluding_trivial", **settings)

    assert np.nanmin(with_mirror.q_value) == pytest.approx(1.0 / 19.0, rel=1e-12)
    assert not with_mirror.significant.any()
    assert np.nanmin(without.q_value) == pytest.approx(0.0)
    assert without.significant.any()


def test_the_exhaustive_excluding_trivial_scheme_runs_eighteen_at_three_against_three() -> None:
    """C(6,3) = 20, less the identity and the mirror. At unequal sizes there is no mirror, so the
    two exhaustive schemes coincide and the count says so."""
    from bzk.stats.perseus_s0 import _relabellings

    draws, used, count = _relabellings(
        3, 3, scheme="exhaustive_excluding_trivial", randomisations=250, seed=0
    )
    groups = {tuple(sorted(draw[:3].tolist())) for draw in draws}

    assert used == "exhaustive"
    assert count == 18
    assert len(groups) == 18
    assert (0, 1, 2) not in groups  # the identity
    assert (3, 4, 5) not in groups  # the mirror

    _, _, unequal = _relabellings(
        3, 5, scheme="exhaustive_excluding_trivial", randomisations=250, seed=0
    )
    _, _, kept = _relabellings(3, 5, scheme="exhaustive_when_small", randomisations=250, seed=0)
    assert unequal == kept == 55  # C(8,3) − 1, and no mirror to drop


def test_random_excluding_trivial_never_draws_a_trivial_relabelling() -> None:
    """And it returns the count asked for, having drawn past whatever it rejected.

    Asserted over every draw rather than over the count alone: a scheme that stopped early would
    also report a plausible number, and a scheme that filtered after drawing would report fewer.
    """
    from bzk.stats.perseus_s0 import _relabellings

    draws, used, count = _relabellings(
        3, 3, scheme="random_excluding_trivial", randomisations=400, seed=1
    )
    groups = [frozenset(draw[:3].tolist()) for draw in draws]

    assert used == "random_excluding_trivial"
    assert count == 400
    assert len(draws) == 400
    assert frozenset({0, 1, 2}) not in groups
    assert frozenset({3, 4, 5}) not in groups
    # The draws are still with replacement — what is excluded is the trivial pair, not repetition.
    assert len(set(groups)) == 18


# ── joint_half ──────────────────────────────────────────────────────────────────────────────────


def _fdr_at(result: Any, threshold: float, observed: np.ndarray, null: np.ndarray) -> float:
    """FDR(t) read back from a run's own inputs, by the definition rather than from the module."""
    draws = result.randomisations_used
    return float(
        ((np.abs(null) >= threshold).sum() / draws) / (np.abs(observed) >= threshold).sum()
    )


def test_joint_half_is_joint_with_the_null_count_halved_at_every_threshold() -> None:
    """`walk/PREREG-PXD018299-H10-attempt2.md` §1, and nothing else: the null count is multiplied
    by ½ and the observed count is untouched.

    Asserted as a ratio at every observed threshold rather than at one: halving the *observed*
    count would double each FDR instead of halving it, and on a symmetric case the two are
    distinguishable only by direction, not by size. The hand case is turn 18's P1 matrix, whose
    nineteen relabellings are enumerable.
    """
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.5,
        "randomisations": 250,
        "seed": 0,
        "scheme": "exhaustive_when_small",
    }
    whole = perseus_s0(NUMERATOR, DENOMINATOR, sidedness="joint", **settings)
    half = perseus_s0(NUMERATOR, DENOMINATOR, sidedness="joint_half", **settings)

    np.testing.assert_allclose(whole.d, half.d, rtol=1e-12)
    finite = np.isfinite(whole.q_value) & (whole.q_value > 0)
    assert finite.any()
    np.testing.assert_allclose(half.q_value[finite], whole.q_value[finite] / 2.0, rtol=1e-12)

    # And against the definition, at the most extreme threshold, computed here from the null.
    null = _hand_null(NUMERATOR, DENOMINATOR, 0.1)
    extreme = float(np.max(np.abs(whole.d)))
    assert _fdr_at(whole, extreme, whole.d, null) == pytest.approx(1.0 / 19.0, rel=1e-12)
    assert half.q_value[np.argmax(np.abs(half.d))] == pytest.approx(1.0 / 38.0, rel=1e-12)


def test_joint_half_halves_the_mirror_floor_at_three_against_three() -> None:
    """`joint`'s floor is 1/19 with the mirror kept; `joint_half`'s is 1/38.

    That is arithmetic and not a second claim about the convention — the mirror still reproduces
    every observed `|d|`, so the null count at every threshold is still at least one, and the only
    thing that moved is the ½. It is asserted because the pre-registration's own expectation about
    which schemes fail check A turns on this number.
    """
    rng = np.random.default_rng(0)
    numerator = rng.normal(0.0, 1.0, size=(400, 3))
    denominator = rng.normal(0.0, 1.0, size=(400, 3))
    numerator[:60] += 4.0
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.01,
        "randomisations": 250,
        "seed": 0,
        "scheme": "exhaustive_when_small",
    }

    whole = perseus_s0(numerator, denominator, sidedness="joint", **settings)
    half = perseus_s0(numerator, denominator, sidedness="joint_half", **settings)

    assert np.nanmin(whole.q_value) == pytest.approx(1.0 / 19.0, rel=1e-12)
    assert np.nanmin(half.q_value) == pytest.approx(1.0 / 38.0, rel=1e-12)
    # 1/38 is 0.0263, still above 0.01, so neither reaches the anchor's threshold with the mirror
    # in the null. Halving moves the floor; it does not remove it.
    assert not whole.significant.any()
    assert not half.significant.any()


def test_joint_and_per_side_are_unchanged_by_the_addition() -> None:
    """A fixed input through both older sidedness values, against values measured before
    `joint_half` existed.

    `walk/PREREG-PXD018299-H10.md`'s attempt 1 has already run and its result is committed; a
    change to what `joint` or `per_side` computes would make that result a description of
    something else. **The numbers below were read off the implementation at `0a6892d`** — the
    commit before this one — in a `git worktree` of that commit, and are asserted here rather than
    recomputed from this one. A first draft of this test carried invented values and failed on two
    of the six, which is the whole reason it is worth having: a regression pin whose numbers come
    from the code it is pinning would pass whatever that code did.
    """
    settings: dict[str, Any] = {
        "s0": 0.1,
        "alpha": 0.05,
        "randomisations": 250,
        "seed": 0,
        "scheme": "exhaustive_when_small",
    }
    joint = perseus_s0(NUMERATOR, DENOMINATOR, sidedness="joint", **settings)
    per_side = perseus_s0(NUMERATOR, DENOMINATOR, sidedness="per_side", **settings)

    assert joint.q_value.tolist() == pytest.approx(
        [0.05263157894736842, 1.0, 0.05263157894736842, 1.0, 1.0, 1.0]
    )
    assert per_side.q_value.tolist() == pytest.approx(
        [0.0, 0.5789473684210527, 0.0, 0.5789473684210527, 0.5789473684210527, 0.5789473684210527]
    )
    assert joint.sidedness == "joint"
    assert per_side.sidedness == "per_side"
