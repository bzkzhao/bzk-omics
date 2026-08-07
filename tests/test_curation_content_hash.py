"""The PXD018299 digest is one fact stored in five places; these tests keep them agreeing.

`CLAUDE.md` § Single source of truth: *"Duplicating a fact into a second document is a defect...
The copies diverge within weeks and there is then no way to tell which is authoritative."* The
`content_hash` for `HAP1_USP18KO_GlyGlyKSites.txt` is cited by three records in `data/curation/`,
by the baseline fixture in `tests/fixtures/`, and held by `bzk.sources.pride.PXD018299_SITES`.
Nothing checked they agreed, so a deposit revision applied to two records out of three would have
left the suite green — the exact copies-diverge failure, in the one value that decides whether a
rebuild is working against the bytes the curation was written for.

Discovery spans `data/curation/` **and** `tests/fixtures/`. Scoping it to the curation directory
would have recreated the self-limiting gap `test_the_citing_records_are_exactly_these` exists to
close, one directory out: the baseline fixture cites the digest on its face and would have been
the fourth unguarded copy.

`PXD018299_SITES` is treated as the home: records are checked against it, not against each other,
so a revision has one place to be applied and a stale record is a failure rather than a tie.

Offline — reads committed files only; no network, no `raw/`.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.sources.pride import PXD018299_SITES

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
SEARCHED_DIRS = (CURATION_DIR, FIXTURE_DIR)
NOTEBOOK = REPO_ROOT / "colab_reproducefigure.ipynb"

# The four records that cite the deposit, as repo-relative paths, named explicitly so the
# parametrised checks below have a fixed list. A hardcoded list alone would leave a *fifth* record
# citing this file silently unguarded, so `test_the_citing_records_are_exactly_these` discovers
# citers from disk and asserts the two sets match — that is what makes adding a citer fail here
# until it is listed.
CITING_RECORDS = (
    "data/curation/curation_PXD018299.json",
    "data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json",
    "data/curation/resolution_PXD018299.json",
    "tests/fixtures/pxd018299_welch_baseline.json",
)


def _record(name: str) -> dict[str, Any]:
    loaded: Any = json.loads((REPO_ROOT / name).read_text())
    return cast("dict[str, Any]", loaded)


def _records_citing_the_deposit() -> set[str]:
    """Every committed record whose `file` is this deposit, discovered rather than listed."""
    found = set()
    for directory in SEARCHED_DIRS:
        for path in directory.glob("*.json"):
            if json.loads(path.read_text()).get("file") == PXD018299_SITES.filename:
                found.add(path.relative_to(REPO_ROOT).as_posix())
    return found


def test_the_citing_records_are_exactly_these() -> None:
    """A new record citing this deposit must be added to CITING_RECORDS, not silently unchecked.

    Without this the guard would be self-limiting: it protects the three files it already knows
    about and says nothing about a fourth, which is how a partial back-fill escapes in the first
    place.
    """
    assert _records_citing_the_deposit() == set(CITING_RECORDS)


@pytest.mark.parametrize("name", CITING_RECORDS)
def test_record_cites_the_module_digest(name: str) -> None:
    """Each record's content_hash equals the value the fetch module holds."""
    assert _record(name)["content_hash"] == PXD018299_SITES.expected_content_hash


@pytest.mark.parametrize("name", CITING_RECORDS)
def test_record_cites_the_module_filename(name: str) -> None:
    """The filename and accession are duplicated alongside the digest and drift the same way.

    The record types spell the accession differently — the curation record keys it `accession`,
    the derived analysis/resolution records and the baseline fixture key it `dataset`. All hold
    `PXD018299`, so this reads whichever is present rather than forcing a format change; the
    divergence is noted in the commit, not silently normalised here.
    """
    record = _record(name)
    assert record["file"] == PXD018299_SITES.filename
    accession = record.get("accession", record.get("dataset"))
    assert accession == PXD018299_SITES.accession


def test_all_records_agree() -> None:
    """Stated directly as well: a partial back-fill leaves two values, and this names that."""
    hashes = {name: _record(name)["content_hash"] for name in CITING_RECORDS}
    assert len(set(hashes.values())) == 1, f"records disagree on content_hash: {hashes}"


def test_module_digest_is_a_well_formed_sha256() -> None:
    """Guards against a truncated or prefix-less paste, which would compare equal nowhere."""
    expected = PXD018299_SITES.expected_content_hash
    assert expected is not None
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", expected), expected


def test_module_url_matches_the_notebook() -> None:
    """`colab_reproducefigure.ipynb` cell 2 hard-codes the same URL this module builds from parts.

    The notebook is the provenance of record for the 12-of-14 baseline, so if the two point at
    different deposits the module is fetching bytes the published figure was not derived from.
    The URL is written as an implicit string concatenation across two lines, so it is recovered
    with `ast.literal_eval` over the parenthesised expression rather than by matching one literal.
    """
    cells = json.loads(NOTEBOOK.read_text())["cells"]
    sources = ["".join(c["source"]) for c in cells if c["cell_type"] == "code"]
    urls = []
    for src in sources:
        match = re.search(r"^URL\s*=\s*(\(.*?\))", src, re.MULTILINE | re.DOTALL)
        if match:
            urls.append(ast.literal_eval(match.group(1)))
    assert urls, "no URL assignment found in the notebook — has cell 2 been rewritten?"
    assert PXD018299_SITES.url in urls, f"module builds {PXD018299_SITES.url}; notebook has {urls}"
