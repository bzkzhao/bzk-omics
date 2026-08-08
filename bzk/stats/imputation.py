"""Imputation, registered like a test — never done in the adapter (`ARCHITECTURE.md` §4).

§4 is unambiguous about where this belongs: *"Imputation never happens in the adapter. Adapters emit
measured values and nulls; what to do about the nulls is an analysis decision that must be
recorded."* And `ONTOLOGY.md` §6.5 is unambiguous about what it produces: *"a **generated number,
not a measurement**, and it materially determines the result."* Everything here exists to keep those
two facts attached to the numbers it makes — the count of generated values comes back with them
(I15's `n_values_imputed`), and `SiteObservation.n_imputed` records it per site.

Default entry per §4: `downshifted_normal`, 1.8 SD downshift, 0.3 SD width, matching Perseus.
A seed is mandatory for a stochastic method — I15, and without one I9 fails too.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ImputationOutcome:
    """The filled matrix and what it cost, kept together so the count cannot be dropped.

    `n_values_imputed` / `n_values_total` are I15's fields verbatim, and `imputed_mask` is what
    `SiteObservation.n_imputed` is computed from (§6.5). Returning the matrix alone would make the
    generated-versus-measured distinction unrecoverable one function call later, which is exactly
    what I15 exists to prevent.
    """

    values: np.ndarray
    imputed_mask: np.ndarray
    n_values_imputed: int
    n_values_total: int


Imputer = Callable[..., ImputationOutcome]
IMPUTATION_METHODS: dict[str, Imputer] = {}


def register(name: str) -> Callable[[Imputer], Imputer]:
    def _register(fn: Imputer) -> Imputer:
        IMPUTATION_METHODS[name] = fn
        return fn

    return _register


@register("none")
def none(values: np.ndarray, **_: object) -> ImputationOutcome:
    """No imputation. Declared explicitly because I15 requires an `Imputation` either way."""
    return ImputationOutcome(
        values=values.copy(),
        imputed_mask=np.zeros(values.shape, dtype=bool),
        n_values_imputed=0,
        n_values_total=int(values.size),
    )


@register("downshifted_normal")
def downshifted_normal(
    values: np.ndarray,
    *,
    downshift_sd: float = 1.8,
    width_sd: float = 0.3,
    seed: int | None = None,
    scope: str = "whole_matrix",
) -> ImputationOutcome:
    """Replace missing values with draws from a normal below the observed distribution.

    The definition, from `ONTOLOGY.md` §6.5 and `ARCHITECTURE.md` §4: draws come from a normal
    centred `downshift_sd` standard deviations below the observed mean, with standard deviation
    `width_sd` times the observed one. Values are assumed already log2-transformed — the downshift
    is in SD units of the observed *log* distribution, which is what makes 1.8/0.3 meaningful.

    `scope` decides what "observed" ranges over. `whole_matrix` computes one mean and SD across
    every measured value; `per_sample` does it per column, which is Perseus' own default and models
    per-run detection limits. They give materially different answers on a matrix with uneven depth,
    so the scope is recorded on the `Imputation` node (§6.5) rather than assumed.

    A seed is **required**, not defaulted: I15, and `ARCHITECTURE.md` §4 — *"without it the same
    inputs give different answers and I9 fails."* Raising is the point; a default seed would make an
    irreproducible analysis look reproducible.
    """
    if seed is None:
        raise ValueError(
            "downshifted_normal is stochastic and requires a seed (I15); without one the same "
            "inputs give different answers and the analysis is irreproducible from itself"
        )
    if scope not in ("whole_matrix", "per_sample"):
        raise ValueError(f"scope {scope!r} is not in ONTOLOGY.md §6.5's enum")

    filled = values.copy()
    missing = np.isnan(values)
    rng = np.random.default_rng(seed)

    if scope == "whole_matrix":
        observed = values[~missing]
        if observed.size == 0:
            raise ValueError("no measured values to impute from")
        mean, sd = float(observed.mean()), float(observed.std(ddof=1))
        draws = rng.normal(mean - downshift_sd * sd, width_sd * sd, size=int(missing.sum()))
        filled[missing] = draws
    else:
        for column in range(values.shape[1]):
            column_missing = missing[:, column]
            if not column_missing.any():
                continue
            observed = values[~column_missing, column]
            if observed.size == 0:
                raise ValueError(f"column {column} has no measured values to impute from")
            mean, sd = float(observed.mean()), float(observed.std(ddof=1))
            filled[column_missing, column] = rng.normal(
                mean - downshift_sd * sd, width_sd * sd, size=int(column_missing.sum())
            )

    return ImputationOutcome(
        values=filled,
        imputed_mask=missing,
        n_values_imputed=int(missing.sum()),
        n_values_total=int(values.size),
    )
