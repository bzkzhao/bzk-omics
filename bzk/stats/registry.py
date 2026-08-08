"""The common interface tests register against, and the presence rule that precedes them.

`ARCHITECTURE.md` §4: *"Tests register against a common interface and are selected per analysis —
the test and its `fdr_method` are properties of the `Analysis`."* So a test is a function of two
matrices and nothing else: no knowledge of sites, of the graph, or of which contrast it serves. That
is what makes `Analysis.test` a recorded string rather than a branch (I13).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TestResult:
    """One test's output over an aligned pair of matrices, row-wise.

    `log2fc` is the difference of the group means **in the units given** — which for this layer is
    always log2 space, because `presence_filter` and the imputation both operate there. Naming it
    `log2fc` rather than `difference` is therefore a claim about the caller's contract, and
    `ARCHITECTURE.md` §4 flags the same ambiguity as unresolved with the collaborator: whether
    "difference in intensities" means log2 or untransformed. This layer means log2.
    """

    log2fc: np.ndarray
    p_value: np.ndarray


#: A test takes (numerator, denominator) matrices — rows are features, columns are replicates —
#: and returns one `TestResult`. Missing values must already be resolved; a test never imputes.
Test = Callable[[np.ndarray, np.ndarray], TestResult]

TESTS: dict[str, Test] = {}


def register(name: str) -> Callable[[Test], Test]:
    def _register(fn: Test) -> Test:
        TESTS[name] = fn
        return fn

    return _register


def presence_filter(
    numerator: np.ndarray, denominator: np.ndarray, *, min_per_group: int, either: bool
) -> np.ndarray:
    """Rows with enough measured values to be worth testing. Returns a boolean mask.

    This runs **before** imputation and is the reason the tested population is smaller than the
    ingested one. Two readings of "enough" are possible and they are not equivalent:

    - `either=True` — at least `min_per_group` measured in *one* group. Keeps a site seen only in
      the KO arm, which for an induced modification is the interesting case, and is what
      PXD018299's curation record declares (`presence_rule: ">=2 replicates in either group"`).
    - `either=False` — at least `min_per_group` in *both*. Stricter, and what `ONTOLOGY.md` §6.5's
      table means by "testable sites (>=2 replicates both groups)" when it counts 23 for
      `Ratio mod/base`.

    The two appear in different documents describing the same dataset, so the parameter is explicit
    rather than defaulted: a rule that silently picked one would make the tested population depend
    on which sentence the implementer had read last.
    """
    have_num = np.sum(~np.isnan(numerator), axis=1) >= min_per_group
    have_den = np.sum(~np.isnan(denominator), axis=1) >= min_per_group
    return (have_num | have_den) if either else (have_num & have_den)
