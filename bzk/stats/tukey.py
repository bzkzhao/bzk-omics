"""Tukey HSD and its four neighbours over a balanced 2 × 2 design, vectorised over rows.

`walk/PREREG-PXD032267-gate.md` §4 names five ways a p-value could have been formed for one pair
of the four cells, and the gate asks which of them reproduces the publication's `p_value`. This
module computes all five, from the definition, for every pair:

| id | p for the pair (first − second) |
|---|---|
| T1 | studentised range over the four cell means, interaction-model MSE, df = N − 4 |
| T2 | the same, with the additive model's MSE, df = N − 3 |
| T3 | two-sided t on the interaction-model MSE (Fisher's LSD), df = N − 4 |
| T4 | Student's t on the two cells alone, df = 2(n − 1) |
| T5 | Welch's t on the two cells alone |

The registration states those df at the gate's own n = 3 per cell (8, 9, 8 and 4). They are the
same formulas there; nothing here is fixed to n = 3, and the oracle exercises n = 10 as well.

**Written from the definition, following `bzk/stats/anova.py`'s convention.** The sums of squares
come from `anova.two_way`, which is already validated against R's `aov`, so the two MSEs cannot
disagree with the ANOVA the publication names. **The additive MSE is (residual SS + interaction
SS) / (residual df + 1)**: dropping the interaction term from a 2 × 2 frees its single df into the
residual. `scipy` supplies two special functions and no arithmetic: `studentized_range.sf`, which
the registration names, and `t.sf`, which it does not but which T3 to T5 need — reported as an
addition in the build turn.

**What `two_way` refuses, this refuses**, by calling it: a missing value, an unbalanced design, and
fewer than two observations per cell. It adds one refusal of its own — a design that is not
exactly 2 × 2 — because the studentised range below is taken over four means and would be the
wrong distribution for any other number.

**Validated before any real data passed through it**: `tests/test_tukey.py` reproduces every
value of `tests/fixtures/r_tukey_reference.csv` — generated on bzk's Mac by
`notes/scripts/tukey_reference.R`, outside the session that wrote this — to |Δ| ≤ 1e-6.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from bzk.stats.anova import AnovaError, _levels, two_way

#: Registration §4's table, in its order. Table order breaks exact ties in the gate's primary, so
#: the order is part of the contract rather than a presentation choice.
VARIANTS = ("T1", "T2", "T3", "T4", "T5")

#: The number of cell means the studentised range is taken over. Fixed by the 2 × 2 design.
N_MEANS = 4


class TukeyError(AnovaError):
    """The design is not one this module computes. A subclass, so a caller catching `two_way`'s
    refusals catches these too — they are the same kind of fault."""


@dataclass(frozen=True)
class PairResult:
    """One pair of cells: `diff` is mean(`first`) − mean(`second`), one value per row."""

    first: str
    second: str
    diff: np.ndarray
    p: dict[str, np.ndarray]

    def reversed(self) -> PairResult:
        """The same pair named the other way round: `diff` negates, every p is unchanged."""
        return PairResult(first=self.second, second=self.first, diff=-self.diff, p=dict(self.p))


@dataclass(frozen=True)
class TukeyResult:
    """Every pair of the four cells, with the two MSEs and the df every variant used."""

    cells: tuple[str, ...]
    n_per_cell: int
    mse_interaction: np.ndarray
    df_interaction: int
    mse_additive: np.ndarray
    df_additive: int
    df_student: int
    pairs: tuple[PairResult, ...]

    def pair(self, first: str, second: str) -> PairResult:
        """The pair `first` − `second`, whichever way round it was computed."""
        for result in self.pairs:
            if (result.first, result.second) == (first, second):
                return result
            if (result.first, result.second) == (second, first):
                return result.reversed()
        raise TukeyError(
            f"no pair {first!r} - {second!r}; cells are {list(self.cells)} and the pairs computed "
            f"were {[(r.first, r.second) for r in self.pairs]}"
        )


def cell_name(level_a: object, level_b: object) -> str:
    """`a:b`, the name R's `interaction(a, b, sep = ":")` gives the same cell."""
    return f"{level_a}:{level_b}"


def tukey(
    values: np.ndarray,
    factor_a: np.ndarray,
    factor_b: np.ndarray,
    *,
    pairs: Sequence[tuple[str, str]] | None = None,
    variants: Sequence[str] = VARIANTS,
) -> TukeyResult:
    """Every pair of the four cells under every variant in `variants`, for every row.

    `pairs` names the pairs to compute as `(first, second)`; omitted, it is all six, each named
    later-level minus earlier-level as R's `TukeyHSD` names them. Restricting it, or `variants`,
    changes nothing about the pairs that are computed — each row and each pair is independent — and
    exists because `studentized_range.sf` costs milliseconds per value.
    """
    from scipy import stats  # local, as in `anova.two_way`: only the p-values need it

    unknown = [v for v in variants if v not in VARIANTS]
    if unknown:
        raise TukeyError(f"unknown variant(s) {unknown}; registration §4 names {list(VARIANTS)}")
    values = np.asarray(values, dtype=float)
    factor_a = np.asarray(factor_a)
    factor_b = np.asarray(factor_b)
    # `two_way` validates shape, missing values, balance and n >= 2 per cell, and raises
    # `AnovaError` naming the fault. Called first so this module never computes on a design it
    # would refuse.
    anova = two_way(values, factor_a, factor_b)
    levels_a, levels_b = _levels(factor_a), _levels(factor_b)
    if (len(levels_a), len(levels_b)) != (2, 2):
        raise TukeyError(
            f"the design is {len(levels_a)}x{len(levels_b)}, not 2x2. The studentised range here is "
            f"taken over {N_MEANS} means, which is the wrong distribution for any other design."
        )

    columns: dict[str, np.ndarray] = {
        cell_name(la, lb): np.flatnonzero((factor_a == la) & (factor_b == lb))
        for lb in levels_b
        for la in levels_a
    }
    cells = tuple(columns)
    n = int(next(iter(columns.values())).size)

    df_interaction = anova.residual_df
    df_additive = df_interaction + anova.interaction.df
    mse_interaction = anova.residual_sum_squares / df_interaction
    mse_additive = (anova.residual_sum_squares + anova.interaction.sum_squares) / df_additive
    df_student = 2 * (n - 1)

    means = {c: values[:, idx].mean(axis=1) for c, idx in columns.items()}
    variances = {c: values[:, idx].var(axis=1, ddof=1) for c, idx in columns.items()}

    if pairs is None:
        pairs = [(cells[j], cells[i]) for i in range(len(cells)) for j in range(i + 1, len(cells))]
    for first, second in pairs:
        if first not in columns or second not in columns or first == second:
            raise TukeyError(f"pair {first!r} - {second!r} is not two distinct cells of {cells}")

    computed: list[PairResult] = []
    with np.errstate(divide="ignore", invalid="ignore"):
        for first, second in pairs:
            diff = means[first] - means[second]
            p: dict[str, np.ndarray] = {}
            if "T1" in variants:
                q = np.abs(diff) / np.sqrt(mse_interaction / n)
                p["T1"] = np.asarray(stats.studentized_range.sf(q, N_MEANS, df_interaction))
            if "T2" in variants:
                q = np.abs(diff) / np.sqrt(mse_additive / n)
                p["T2"] = np.asarray(stats.studentized_range.sf(q, N_MEANS, df_additive))
            if "T3" in variants:
                t = np.abs(diff) / np.sqrt(2.0 * mse_interaction / n)
                p["T3"] = np.asarray(2.0 * stats.t.sf(t, df_interaction))
            if "T4" in variants:
                pooled = (variances[first] + variances[second]) / 2.0
                t = np.abs(diff) / np.sqrt(2.0 * pooled / n)
                p["T4"] = np.asarray(2.0 * stats.t.sf(t, df_student))
            if "T5" in variants:
                a, b = variances[first] / n, variances[second] / n
                t = np.abs(diff) / np.sqrt(a + b)
                df_welch = (a + b) ** 2 / (a**2 / (n - 1) + b**2 / (n - 1))
                p["T5"] = np.asarray(2.0 * stats.t.sf(t, df_welch))
            computed.append(PairResult(first=first, second=second, diff=diff, p=p))

    return TukeyResult(
        cells=cells,
        n_per_cell=n,
        mse_interaction=np.asarray(mse_interaction),
        df_interaction=df_interaction,
        mse_additive=np.asarray(mse_additive),
        df_additive=df_additive,
        df_student=df_student,
        pairs=tuple(computed),
    )
