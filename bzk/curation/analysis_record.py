"""The `data/curation/analysis_*.json` format — what a record may carry, and what refuses one.

**A second format in the curation directory, not a second dialect of the first.** `loader.py` turns
a `curation_*.json` into a change-set; nothing turns an `analysis_*.json` into anything.
`bzk/rebuild.py`'s replay globs `curation_*.json`, so no analysis record passes through the loader
or its `KNOWN_KEYS` check. Each is opened by literal path with `json.loads` by the one module or
test that wants it, and until this module existed nothing asked what else the file held: a key no
reader reads was dropped in silence — the defect `_check_known_keys` closed for the other format in
the same directory, one commit earlier.

**Why the two formats do not share a guard.** `loader.py`'s vocabulary is composed from the three
places that module reads keys, so a key outside it is *provably* dropped: one loader, one read
surface, one set. This format has no loader and five readers — one shipped module and four test
modules — and the two committed records overlap on only twelve of their sixteen keys. A vocabulary
built here is therefore the union of two dialects and, being a union, **guards less than either
half**: it recognises `n_sites_tested` in a record whose readers would never look for it. That is a
real gap and not a hypothetical one — four keys (`contrast`, `test`, `fdr_method`,
`filters_applied`) are read from one committed record and from nothing that opens the other.

So the refusal below is deliberately the weaker of the two available checks, and the stronger one
is a test rather than a runtime rule: `tests/test_analysis_record.py` derives, per record, which
keys its own readers read, and holds the remainder to a declared list with a reason for each. The
split is the point — a misspelling is caught the moment a record is opened, and a key that reaches
no reader is caught by the suite, which is where a new record and its new reader actually meet.

**Recognising a key is not reading it.** Seven keys of each committed record are recognised here and
read by nothing; they are carried because a human reads them. They are named, with their ground, in
that test module rather than deleted.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class AnalysisRecordInvalid(ValueError):
    """A record this format cannot accept. Separate from `CurationError` — a different format."""


#: The twelve keys both committed records carry: the analysis itself, in the vocabulary
#: `ONTOLOGY.md` §5 gives `Analysis` and `DifferentialResult`. `presence_rule` and
#: `localization_threshold` sit here rather than with the prose keys because both records state
#: them, including as an explicit null.
CORE_KEYS: frozenset[str] = frozenset(
    {
        "dataset",
        "file",
        "content_hash",
        "contrast",
        "quantity",
        "localization_threshold",
        "filters_applied",
        "presence_rule",
        "imputation",
        "test",
        "fdr_method",
        "protein_adjusted",
    }
)

#: Counts of the run, present when the analysis was re-derived in this container and the record is
#: what the rederivation is checked against (`tests/test_pxd018299_baseline.py`). A record for an
#: analysis nobody here has repeated carries none of them, and stating that absence is what
#: `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`'s `unresolved` does.
DERIVED_COUNT_KEYS: frozenset[str] = frozenset(
    {
        "n_sites_tested",
        "n_significant_up",
        "n_expected_recovered",
        "n_expected_total",
    }
)

#: The tool that performed the analysis, when it was not this repository. §5.4's external-analysis
#: columns; `external_version` lands on `Analysis` and is read, `external_tool` is not — the adapter
#: writes its own name.
EXTERNAL_TOOL_KEYS: frozenset[str] = frozenset({"external_tool", "external_version"})

#: Curator prose. The curation format's `rationale` reaches `Analysis.rationale` through the loader;
#: this format has no loader, so neither of these reaches anything.
CURATOR_KEYS: frozenset[str] = frozenset({"rationale", "unresolved"})

#: Every top-level key a record may carry — the union of the four groups above, never restated.
KNOWN_KEYS: frozenset[str] = CORE_KEYS | DERIVED_COUNT_KEYS | EXTERNAL_TOOL_KEYS | CURATOR_KEYS


def check_keys(record: Mapping[str, Any], *, source: str) -> None:
    """Refuse a record carrying a top-level key this format does not define.

    `source` names the file in the message: unlike the curation loader, this check is called from
    several places over several records, so *which* record carries the key is not obvious from the
    traceback.
    """
    unknown = sorted(set(record) - KNOWN_KEYS)
    if unknown:
        raise AnalysisRecordInvalid(
            f"{source} carries top-level key(s) {unknown} that the analysis-record format does not "
            f"define, so nothing would read them. The format is {sorted(KNOWN_KEYS)}. Note that "
            "recognition is not a read: this format has no single loader, and which reader reads "
            "which key — and which keys are read by none — is held in "
            "tests/test_analysis_record.py."
        )


def read_record(path: Path) -> dict[str, Any]:
    """One `analysis_*.json` off disk, refused rather than half-read.

    Every reader in `bzk/` goes through here, so the refusal is a live check rather than a
    function nothing calls.
    """
    loaded: Any = json.loads(path.read_text())
    if not isinstance(loaded, dict):
        raise AnalysisRecordInvalid(f"{path.name} holds a {type(loaded).__name__}, not an object")
    check_keys(loaded, source=path.name)
    return dict(loaded)
