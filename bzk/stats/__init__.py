"""The statistics layer — pluggable by construction (`ARCHITECTURE.md` §4).

**No statistical test is privileged by the schema.** `Analysis.test` is a recorded string that
nothing downstream branches on; tests register here against a common interface and are selected per
analysis. Imputation registers the same way, because §4 is explicit that it *is* part of this layer
and never the adapter's: "adapters emit measured values and nulls; what to do about the nulls is an
analysis decision that must be recorded."

**Written from the specification, not from `colab_reproducefigure.ipynb`.** The earlier
re-derivation (`bzk/sources/pxd018299_baseline.py`) is a deliberate transcription of that notebook's
cells and says so; it establishes that the transcription is faithful. It cannot establish that this
pipeline is correct, because copied arithmetic agreeing with itself is guaranteed — the third
instance of that shape this project has caught (`HANDOFF.md` §8). So this module is built from
`ONTOLOGY.md` §6.5 and `ARCHITECTURE.md` §4, in polars and numpy per §1, and the notebook is
something to *compare against* afterwards. Where the two disagree, that is a finding about the two
routes and not a defect to tune away.
"""

from bzk.stats.fdr import FDR_METHODS, benjamini_hochberg
from bzk.stats.imputation import IMPUTATION_METHODS, ImputationOutcome, downshifted_normal
from bzk.stats.registry import TESTS, TestResult, presence_filter
from bzk.stats.tests import welch_t

__all__ = [
    "FDR_METHODS",
    "IMPUTATION_METHODS",
    "TESTS",
    "ImputationOutcome",
    "TestResult",
    "benjamini_hochberg",
    "downshifted_normal",
    "presence_filter",
    "welch_t",
]
