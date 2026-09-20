"""`bzk/stats/anova.py` — validated against a published table and an independent computation.

`walk/PREREG-PXD026748-reconstruction.md:54-58`: *"The ANOVA must be validated before any real data
passes through it, against a worked example with published answers. That is a requirement on the
build turn, and without it this pre-registration is not run."* This module is that validation.

**Two validations, because they fail differently.** A1 checks the whole table against numbers
someone else published, which catches a misread of the design or of what a term means — the errors
a second implementation of mine would reproduce. A2 checks against an independent computation over
random data, which catches arithmetic that happens to be right on one worked example — the errors a
single published case would miss. Neither subsumes the other.

**`tests/fixtures/toothgrowth.csv` is R's `ToothGrowth` dataset**, fetched 2026-09-20 from
`https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/datasets/ToothGrowth.csv`
and committed with its digest asserted below. It is R's own distributed copy of Bliss (1952), which
is what makes R's `aov` output a *published* answer for it rather than one this repository
computed.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np
import pytest

from bzk.stats.anova import AnovaError, two_way

FIXTURE = Path(__file__).parent / "fixtures" / "toothgrowth.csv"

#: The digest of the file as fetched. Asserted rather than trusted: a fixture whose bytes moved
#: would make the table below a comparison against a different dataset with the same name.
TOOTHGROWTH_SHA256 = "b35e084a98731429169eb9b216c9b904e8b9ea127707b741bb8fc146354c26fe"


def _toothgrowth() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """`(values as one row, supp labels, dose labels)`, in file order."""
    rows = list(csv.DictReader(FIXTURE.read_text(encoding="utf-8").splitlines()))
    length = np.array([[float(r["len"]) for r in rows]])
    supp = np.array([r["supp"] for r in rows])
    dose = np.array([r["dose"] for r in rows])
    return length, supp, dose


def test_the_fixture_is_the_file_that_was_fetched() -> None:
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == TOOTHGROWTH_SHA256


# ── A1 · R's published `aov` table ──────────────────────────────────────────────────────────────


def test_a1_matches_rs_published_aov_table() -> None:
    """`len ~ supp * factor(dose)`, 2 x 3 with n = 10.

    R's printed table, which is what is asserted here to its own precision:

        Df Sum Sq Mean Sq F value   Pr(>F)
        supp         1  205.4   205.4  15.572 0.000231 ***
        dose         2 2426.4  1213.2  92.000  < 2e-16 ***
        supp:dose    2  108.3    54.2   4.107 0.021860 *
        Residuals   54  712.1    13.2

    The SS are given to two decimals from R's full-precision `summary.aov`; the F values and the
    `supp:dose` P are R's printed digits. `dose`'s P prints as `< 2e-16`, which is a bound rather
    than a value, so it is asserted as one.
    """
    values, supp, dose = _toothgrowth()
    result = two_way(values, supp, dose)

    assert result.factor_a.df == 1
    assert result.factor_b.df == 2
    assert result.interaction.df == 2
    assert result.residual_df == 54

    assert result.factor_a.sum_squares[0] == pytest.approx(205.35, abs=5e-3)
    assert result.factor_b.sum_squares[0] == pytest.approx(2426.43434, abs=5e-3)
    assert result.interaction.sum_squares[0] == pytest.approx(108.319, abs=5e-3)
    assert result.residual_sum_squares[0] == pytest.approx(712.106, abs=5e-3)

    assert result.factor_a.f[0] == pytest.approx(15.572, abs=5e-4)
    assert result.factor_b.f[0] == pytest.approx(92.000, abs=5e-4)
    assert result.interaction.f[0] == pytest.approx(4.107, abs=5e-4)

    assert result.factor_a.p_value[0] == pytest.approx(0.000231, abs=5e-7)
    assert result.factor_b.p_value[0] < 2e-16
    assert result.interaction.p_value[0] == pytest.approx(0.0219, abs=5e-5)


def test_a1_is_symmetric_in_the_order_of_the_factors() -> None:
    """Swapping the factors swaps the two main effects and leaves the interaction alone.

    True of a balanced design and of nothing else — it is the property that makes *"Type I, II and
    III coincide"* the licence the pre-registration relies on, so it is asserted rather than
    assumed from the sentence.
    """
    values, supp, dose = _toothgrowth()
    forward = two_way(values, supp, dose)
    reversed_ = two_way(values, dose, supp)

    assert reversed_.factor_a.sum_squares[0] == pytest.approx(forward.factor_b.sum_squares[0])
    assert reversed_.factor_b.sum_squares[0] == pytest.approx(forward.factor_a.sum_squares[0])
    assert reversed_.interaction.sum_squares[0] == pytest.approx(forward.interaction.sum_squares[0])
    assert reversed_.residual_sum_squares[0] == pytest.approx(forward.residual_sum_squares[0])


# ── A2 · an independent computation ─────────────────────────────────────────────────────────────


def _lstsq_f(values: np.ndarray, full: np.ndarray, reduced: np.ndarray) -> np.ndarray:
    """F for `full` against `reduced`, per row, from residual sums of squares.

    Nested least squares, which is the textbook definition of an F test for a set of terms and
    shares no line with `anova.py`'s cell-mean arithmetic. That independence is the point: an error
    in one could not be reproduced by the other.
    """

    def rss(design: np.ndarray) -> np.ndarray:
        fitted = design @ np.linalg.lstsq(design, values.T, rcond=None)[0]
        return np.asarray(((values.T - fitted) ** 2).sum(axis=0), dtype=float)

    df_full = values.shape[1] - np.linalg.matrix_rank(full)
    df_terms = np.linalg.matrix_rank(full) - np.linalg.matrix_rank(reduced)
    return np.asarray(((rss(reduced) - rss(full)) / df_terms) / (rss(full) / df_full))


def _dummies(labels: np.ndarray) -> np.ndarray:
    """Sum-coded columns for one factor: each level but the last, minus the last.

    Sum coding rather than treatment coding, and the choice is load-bearing rather than cosmetic.
    Under treatment coding the interaction columns are products of indicators and still carry main
    -effect information, so dropping a factor's own columns while keeping the interaction block does
    not remove that factor from the model — the nested comparison then measures a Type I effect and
    disagrees with the balanced sums of squares by construction. Under sum coding the three blocks
    are mutually orthogonal on a balanced design, so each nested comparison isolates exactly its own
    term. This was found the hard way: with treatment coding both main effects disagreed by a factor
    of two or more while the interaction agreed exactly, which is the signature of the coding and not
    of the arithmetic under test.
    """
    levels = sorted(set(labels.tolist()))
    last = levels[-1]
    return np.column_stack(
        [(labels == level).astype(float) - (labels == last).astype(float) for level in levels[:-1]]
    )


def test_a2_agrees_with_nested_least_squares_on_random_balanced_data() -> None:
    """A 2 x 3 design with n = 2 over 40 random rows, to 1e-9.

    Random rather than contrived: a worked example can be passed by arithmetic that is wrong
    somewhere the example does not reach, and forty rows of noise reach further than one.
    """
    rng = np.random.default_rng(20260920)
    a = np.array(["x", "y"] * 6)
    b = np.array(["p", "p", "q", "q", "r", "r"] * 2)
    values = rng.normal(size=(40, 12))

    result = two_way(values, a, b)

    intercept = np.ones((12, 1))
    da, db = _dummies(a), _dummies(b)
    dab = np.column_stack(
        [da[:, i] * db[:, j] for i in range(da.shape[1]) for j in range(db.shape[1])]
    )
    full = np.column_stack([intercept, da, db, dab])

    assert result.factor_a.f == pytest.approx(
        _lstsq_f(values, full, np.column_stack([intercept, db, dab])), rel=1e-9
    )
    assert result.factor_b.f == pytest.approx(
        _lstsq_f(values, full, np.column_stack([intercept, da, dab])), rel=1e-9
    )
    assert result.interaction.f == pytest.approx(
        _lstsq_f(values, full, np.column_stack([intercept, da, db])), rel=1e-9
    )


def test_the_sums_of_squares_partition_the_total() -> None:
    """A + B + AB + residual is the total sum of squares, to 1e-9.

    The residual is computed from within-cell spread rather than by subtraction, so this is a real
    check and not an identity: an error in any of the three terms breaks it.
    """
    rng = np.random.default_rng(1)
    values = rng.normal(size=(25, 12))
    a = np.array(["x", "y"] * 6)
    b = np.array(["p", "p", "q", "q", "r", "r"] * 2)

    result = two_way(values, a, b)
    total = ((values - values.mean(axis=1)[:, None]) ** 2).sum(axis=1)

    assert (
        result.factor_a.sum_squares
        + result.factor_b.sum_squares
        + result.interaction.sum_squares
        + result.residual_sum_squares
    ) == pytest.approx(total, rel=1e-9)


def test_min_p_is_the_smallest_of_the_three() -> None:
    rng = np.random.default_rng(7)
    values = rng.normal(size=(30, 12))
    a = np.array(["x", "y"] * 6)
    b = np.array(["p", "p", "q", "q", "r", "r"] * 2)

    result = two_way(values, a, b)

    assert result.min_p() == pytest.approx(
        np.minimum(
            np.minimum(result.factor_a.p_value, result.factor_b.p_value),
            result.interaction.p_value,
        )
    )


# ── the refusals ────────────────────────────────────────────────────────────────────────────────


def test_a_missing_value_is_refused_not_dropped() -> None:
    """After imputation every cell is full, so a NaN here is a bug upstream. Dropping it would
    compute a different design over a smaller population and say nothing about it."""
    values = np.ones((2, 8))
    values[1, 3] = np.nan
    a = np.array(["x", "x", "y", "y"] * 2)
    b = np.array(["p", "q"] * 4)

    with pytest.raises(AnovaError, match="1 row\\(s\\) carry a missing value"):
        two_way(values, a, b)


def test_an_unbalanced_design_is_refused() -> None:
    """The sums of squares here are the balanced ones. On an unbalanced design they are wrong, and
    wrong in a way that still produces a plausible table."""
    values = np.ones((1, 7))
    a = np.array(["x", "x", "x", "x", "y", "y", "y"])
    b = np.array(["p", "p", "q", "q", "p", "p", "q"])

    with pytest.raises(AnovaError, match="unbalanced"):
        two_way(values, a, b)


def test_a_single_observation_per_cell_is_refused() -> None:
    """No residual df, so no F and no P. Raising beats returning a table of NaN."""
    values = np.ones((1, 6))
    a = np.array(["x", "x", "x", "y", "y", "y"])
    b = np.array(["p", "q", "r"] * 2)

    with pytest.raises(AnovaError, match=">=2 observations"):
        two_way(values, a, b)
