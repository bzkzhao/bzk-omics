"""False-discovery-rate control, pluggable and recorded in `Analysis.fdr_method` (I16).

`ARCHITECTURE.md` §4: *"FDR control (BH, permutation) is a separate pluggable step recorded in
`fdr_method`. Perseus uses permutation-based FDR, not BH."* Only BH is written; permutation FDR
belongs with `perseus_s0` and neither exists yet.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

FDRMethod = Callable[[np.ndarray], np.ndarray]
FDR_METHODS: dict[str, FDRMethod] = {}


def register(name: str) -> Callable[[FDRMethod], FDRMethod]:
    def _register(fn: FDRMethod) -> FDRMethod:
        FDR_METHODS[name] = fn
        return fn

    return _register


@register("BH")
def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg step-up adjusted p-values, NaN-preserving.

    Written from the definition: sort ascending, scale each by m/rank, then enforce monotonicity by
    taking the running minimum from the largest p downwards, and clip at 1.

    **NaNs are excluded from m rather than ranked.** A site whose test was undefined (zero variance
    in both groups) has no p-value to adjust, and counting it in the denominator would deflate every
    other site's adjusted value — a quiet increase in significance caused by rows that were never
    tested. It comes back as NaN.
    """
    p = np.asarray(p_values, dtype=float)
    out = np.full(p.shape, np.nan)
    finite = ~np.isnan(p)
    m = int(finite.sum())
    if m == 0:
        return out

    values = p[finite]
    order = np.argsort(values, kind="stable")
    ranked = values[order]
    scaled = ranked * m / np.arange(1, m + 1)
    # Step-up: an adjusted value may never exceed one from a larger raw p, so sweep from the top.
    monotone = np.minimum.accumulate(scaled[::-1])[::-1]

    adjusted = np.empty(m)
    adjusted[order] = np.clip(monotone, 0.0, 1.0)
    out[finite] = adjusted
    return out
