"""A balanced two-way ANOVA with interaction, vectorised over rows.

`walk/PREREG-PXD026748-reconstruction.md` step 7: *"A two-way ANOVA of genotype × PLpro treatment,
with interaction. After imputation every cell holds 3 values, so the design is balanced and the
Type I, II and III sums of squares coincide."* That sentence is the whole licence for what is
written here — **the sums of squares below are the balanced-design ones, and they are correct only
because the design is balanced.** So the balance is checked rather than assumed, and an unbalanced
call raises.

**Written from the definition, following `bzk/stats/tests.py`'s convention.** That module says why:
the arithmetic is the whole of the test, and having it here means it is inspectable next to the
record that uses it. `scipy` supplies only `f.sf`, which is a special function and not arithmetic.

**Missing values are refused, not dropped.** The pre-registration puts imputation at step 6 and this
at step 7, so by the time a matrix reaches here every cell of the design is full. A NaN here is a
bug upstream — a skipped imputation, or a filter that let a row through — and dropping it silently
would compute a different design from the one the caller asked for, over a shrunken population that
nothing downstream could see. `welch_t` makes the same refusal one level weaker (it yields NaN);
this one raises, because a shrunken *design* is not recoverable from the output the way a NaN row is.

**Validated before any real data passed through it** (`walk/PREREG-PXD026748-reconstruction.md`
:54-58), against R's `aov` on `ToothGrowth` and against an independent least-squares F test. Both
live in `tests/test_anova.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class AnovaError(ValueError):
    """The design is not one this function computes. Never downgraded to a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class Term:
    """One term of the table: its sum of squares, df, F and P, one value per row."""

    sum_squares: np.ndarray
    df: int
    f: np.ndarray
    p_value: np.ndarray


@dataclass(frozen=True)
class TwoWayResult:
    """The full table for every row of the input matrix.

    The residual carries no F or P of its own, so it is a pair of fields rather than a `Term`:
    giving it an `f` of NaN would invite a caller to read one.
    """

    factor_a: Term
    factor_b: Term
    interaction: Term
    residual_sum_squares: np.ndarray
    residual_df: int

    def min_p(self) -> np.ndarray:
        """The smallest of the three P values per row — the pre-registration's support statistic.

        Step 8: *"A row is supported if its smallest P value is below the threshold."* Computed
        here rather than at each call site so *smallest of which three* has one answer.
        """
        return np.nanmin(
            np.vstack([self.factor_a.p_value, self.factor_b.p_value, self.interaction.p_value]),
            axis=0,
        )


def _levels(labels: np.ndarray) -> list[object]:
    """The distinct labels, in first-appearance order.

    First appearance rather than sorted: the order decides nothing here — the sums of squares are
    symmetric in it — but a stable order makes a level's index reproducible for a caller that wants
    to name a group, and sorting would fail on labels of mixed type.
    """
    seen: list[object] = []
    for label in labels.tolist():
        if label not in seen:
            seen.append(label)
    return seen


def two_way(values: np.ndarray, factor_a: np.ndarray, factor_b: np.ndarray) -> TwoWayResult:
    """A two-way ANOVA with interaction for every row of `values`.

    `values` is rows × samples; `factor_a` and `factor_b` are one label per sample. Every
    combination of levels must appear the same number of times, at least twice — the balanced
    design the sums of squares below assume.
    """
    from scipy import stats  # local: only the P value needs it, and it is the heaviest import

    values = np.asarray(values, dtype=float)
    if values.ndim != 2:
        raise AnovaError(f"values must be rows x samples; got shape {values.shape}")
    factor_a = np.asarray(factor_a)
    factor_b = np.asarray(factor_b)
    n_samples = values.shape[1]
    if factor_a.shape != (n_samples,) or factor_b.shape != (n_samples,):
        raise AnovaError(
            f"one label per sample is required; got {factor_a.shape} and {factor_b.shape} "
            f"for {n_samples} sample(s)"
        )
    if np.isnan(values).any():
        bad = int(np.isnan(values).any(axis=1).sum())
        raise AnovaError(
            f"{bad} row(s) carry a missing value. This ANOVA runs after imputation "
            "(PREREG step 6 before step 7), so every cell of the design is full by then; dropping "
            "the missing ones here would compute a different design over a smaller population and "
            "say nothing about it."
        )

    levels_a, levels_b = _levels(factor_a), _levels(factor_b)
    a, b = len(levels_a), len(levels_b)
    if a < 2 or b < 2:
        raise AnovaError(f"both factors need >=2 levels; got {a} and {b}")

    # `cells[i][j]` is the column indices of one design cell. Balance is a property of these.
    cells = [
        [np.flatnonzero((factor_a == la) & (factor_b == lb)) for lb in levels_b] for la in levels_a
    ]
    sizes = {int(idx.size) for row in cells for idx in row}
    if len(sizes) != 1:
        raise AnovaError(
            f"the design is unbalanced: cell sizes {sorted(sizes)} across {a}x{b} cells. "
            "The sums of squares computed here are the balanced ones and would be wrong."
        )
    n = sizes.pop()
    if n < 2:
        raise AnovaError(f"each cell needs >=2 observations to leave residual df; got {n}")
    if a * b * n != n_samples:
        raise AnovaError(
            f"{a}x{b} cells of {n} account for {a * b * n} samples, but the matrix has {n_samples}; "
            "some sample belongs to no cell, which a label of a third kind would cause"
        )

    # Cell means, rows x a x b. Every sum of squares below is a weighted spread of these.
    cell_means = np.stack(
        [
            np.stack([values[:, cells[i][j]].mean(axis=1) for j in range(b)], axis=1)
            for i in range(a)
        ],
        axis=1,
    )
    grand = values.mean(axis=1)
    mean_a = cell_means.mean(axis=2)  # rows x a, marginal over B
    mean_b = cell_means.mean(axis=1)  # rows x b, marginal over A

    ss_a = n * b * ((mean_a - grand[:, None]) ** 2).sum(axis=1)
    ss_b = n * a * ((mean_b - grand[:, None]) ** 2).sum(axis=1)
    # The interaction is what the cell means hold beyond both marginals — the residual of an
    # additive model fitted to them, which is why the two marginals are subtracted and the grand
    # mean added back once.
    ss_ab = n * (
        (cell_means - mean_a[:, :, None] - mean_b[:, None, :] + grand[:, None, None]) ** 2
    ).sum(axis=(1, 2))
    # Within-cell spread, from the definition rather than by subtraction from the total: computing
    # it as `total - a - b - ab` would make the table sum to the total by construction and hide any
    # error in the three terms above.
    ss_residual = sum(
        ((values[:, cells[i][j]] - cell_means[:, i, j][:, None]) ** 2).sum(axis=1)
        for i in range(a)
        for j in range(b)
    )

    df_a, df_b, df_ab = a - 1, b - 1, (a - 1) * (b - 1)
    df_residual = a * b * (n - 1)
    ms_residual = ss_residual / df_residual

    def term(ss: np.ndarray, df: int) -> Term:
        with np.errstate(divide="ignore", invalid="ignore"):
            f = (ss / df) / ms_residual
        # A row with no within-cell spread has ms_residual == 0: F is inf or NaN and so is P. Left
        # as it falls rather than coerced, for `welch_t`'s reason — it is undefined, and a
        # fabricated 0 or 1 would rank in a comparison that should exclude it.
        return Term(sum_squares=ss, df=df, f=f, p_value=np.asarray(stats.f.sf(f, df, df_residual)))

    return TwoWayResult(
        factor_a=term(ss_a, df_a),
        factor_b=term(ss_b, df_b),
        interaction=term(ss_ab, df_ab),
        residual_sum_squares=np.asarray(ss_residual),
        residual_df=df_residual,
    )
