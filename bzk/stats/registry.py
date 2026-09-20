"""The common interface tests register against, and the presence rule that precedes them.

`ARCHITECTURE.md` §4: *"Tests register against a common interface and are selected per analysis —
the test and its `fdr_method` are properties of the `Analysis`."* So a test knows nothing of sites,
of the graph, or of which contrast it serves. That is what makes `Analysis.test` a recorded string
rather than a branch (I13).

**"A function of two matrices and nothing else" is what this docstring said until 2026-09-21, and
`perseus_s0` is why it no longer does.** §4 makes `s0`, `fdr` and the randomisation count mandatory
parameters of that entry, and `ONTOLOGY.md` l.155 makes them identifying on the `Analysis`. A test
with required parameters is still ignorant of everything above it, which is what the sentence was
protecting; what it cannot be is a two-argument callable. So the interface is now *a callable plus
the parameter names an `Analysis` must record to have run it* — `RegisteredTest` below — and the
older, narrower shape survives as `Test`, which `welch_t` still satisfies exactly.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

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

#: Anything registrable. **Wider than `Test` since 2026-09-21, and the width is the point.**
#: `perseus_s0` takes four required parameters beside the two matrices and returns more than a
#: `TestResult` — a q-value is not a p-value, and calling one the other would be the shape I15
#: forbids one level down. So the registry's value type admits any callable, and what a given entry
#: needs is declared beside it rather than encoded in one signature every entry must wear.
AnyTest = Callable[..., Any]


@dataclass(frozen=True)
class RegisteredTest:
    """One registry entry: what to call, and what an `Analysis` must record to have called it.

    **`parameters` exists because `ONTOLOGY.md` l.155 makes it identifying.** `Analysis`
    `parameters_json` is *determined* by `test`, and for `perseus_s0` it *"requires `s0` and the
    randomisation count, which ARCHITECTURE §4 makes mandatory"*. Declaring the names here, beside
    the callable, is what lets a caller build that payload without a second table of which test
    needs what — a second table being exactly the mirror this repository guards everywhere else.

    A one-field record rather than two parallel dicts, for the same reason: the entry and its
    required parameters are one fact, and two dicts keyed by name are two homes for it.
    """

    name: str
    run: AnyTest
    #: The parameter names an `Analysis` running this test must record. Empty where the test takes
    #: none beyond its two matrices.
    parameters: tuple[str, ...] = ()


TESTS: dict[str, RegisteredTest] = {}

F = TypeVar("F", bound=AnyTest)


def register(name: str, *, parameters: tuple[str, ...] = ()) -> Callable[[F], F]:
    """Register a test under `name`, declaring the parameters an `Analysis` must record for it."""

    def _register(fn: F) -> F:
        TESTS[name] = RegisteredTest(name=name, run=fn, parameters=parameters)
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
