"""The PXD018299 digest is one fact stored in four places; these tests keep them agreeing.

`CLAUDE.md` § Single source of truth: *"Duplicating a fact into a second document is a defect...
The copies diverge within weeks and there is then no way to tell which is authoritative."* The
`content_hash` for `HAP1_USP18KO_GlyGlyKSites.txt` is cited by three records in `data/curation/`
and held by `bzk.sources.pride.PXD018299_SITES`. Nothing checked they agreed, so a deposit
revision applied to two records out of three would have left the suite green — the exact
copies-diverge failure, in the one value that decides whether a rebuild is working against the
bytes the curation was written for.

`PXD018299_SITES` is treated as the home: records are checked against it, not against each other,
so a revision has one place to be applied and a stale record is a failure rather than a tie.

Offline — reads committed files only; no network, no `raw/`.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from bzk.sources.pride import PXD018299_SITES

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATION_DIR = REPO_ROOT / "data" / "curation"
NOTEBOOK = REPO_ROOT / "colab_reproducefigure.ipynb"

# The three records that cite the deposit. Named explicitly rather than globbed: a new record that
# cites this file should fail here until it is added, which is the point of the guard.
CITING_RECORDS = (
    "curation_PXD018299.json",
    "analysis_PXD018299_KOIFN_vs_WTIFN.json",
    "resolution_PXD018299.json",
)


def _record(name: str) -> dict:
    return json.loads((CURATION_DIR / name).read_text())


@pytest.mark.parametrize("name", CITING_RECORDS)
def test_record_cites_the_module_digest(name: str) -> None:
    """Each record's content_hash equals the value the fetch module holds."""
    assert _record(name)["content_hash"] == PXD018299_SITES.expected_content_hash


@pytest.mark.parametrize("name", CITING_RECORDS)
def test_record_cites_the_module_filename(name: str) -> None:
    """The filename and accession are duplicated alongside the digest and drift the same way.

    The two record types spell the accession differently — the curation record keys it
    `accession`, the derived analysis/resolution records key it `dataset`. Both hold `PXD018299`,
    so this reads whichever is present rather than forcing a format change; the divergence is
    noted in the commit, not silently normalised here.
    """
    record = _record(name)
    assert record["file"] == PXD018299_SITES.filename
    accession = record.get("accession", record.get("dataset"))
    assert accession == PXD018299_SITES.accession


def test_all_three_records_agree() -> None:
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
