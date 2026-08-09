"""Measure protein-group ambiguity at protein grain — §6.3's 82% figure, one grain up.

`ONTOLOGY.md` §6.3 settled the *site* grain on a measurement: 1,896 of 2,298 filtered GlyGly sites
(82%) map to more than one protein, *"the common case rather than an edge case"*. The protein grain
had no such number, and at the time this was written `bzk/adapters/perseus.py` refused a
multi-accession row, so how often it refuses was an assumption. This module measures it, over three
real artefacts:

1. **BJC Supplementary Data 2** (`MOESM4`) — a Perseus protein-level export, 25 rows.
2. **BJC Supplementary Data 3** (`MOESM5`) — the same, 323 rows.
3. **`HAP1_USP18KO_proteinGroups.txt`** — MaxQuant, upstream of Perseus, 4,982 groups.

The first two are the exact artefact in question: Perseus exports, identifiable by the `C:` / `N:` /
`T:` column-type prefixes it writes into an Excel export. The third gives a larger *n* and shows
whether Perseus' selection changes the picture.

**Two corrections, 2026-08-09, from the turn that went to ingest the first two.** The premise above
— *"`perseus.py` refuses a multi-accession row"* — was true when written and **is not now**:
ADR-0022 made `candidate_proteins` identifying and the group *is* the identity, so nothing is
refused for being a group. The measurement stands; only its motivation is historical. And *Perseus
export* is accurate but says less than it seems to: these are exports of the **annotation matrix**,
carrying LFQ intensities, MaxQuant QC columns and identifiers, with **no `Student's T-test
Difference` and no p-value column in either file**. They cannot supply a `DifferentialResult`, which
this module never claimed and a reader could reasonably have assumed. `ROADMAP.md` § *Step 0 stopped
the BJC ingestion* carries the measurement.

**Two accession columns, and the difference is the whole question.** `Protein IDs` lists every
protein in the group; `Majority protein IDs` lists the subset carrying at least half the peptides,
and its first entry is MaxQuant's leading pick. Both are measured, because which one an adapter
reads decides how often it must refuse.

**Six lines of `HAP1_USP18KO_proteinGroups.txt` are not protein groups.** MaxQuant writes long
semicolon-separated numeric lists in its `*_IDs` columns, and six of them spill onto their own
physical lines — each carrying exactly 147 tabs, so the field count matches the header and every
structural check passes. `pandas` reads them as data, and their accession columns then hold numbers
like `6215;8153;8154`. Excluding them takes the largest apparent group from 5,090 members to 33 and
moves the headline percentage by 0.1, which is precisely why nothing would have caught it: the
`ran cleanly and was wrong` class of `HANDOFF.md` §6. The file states its own row count — `id` is a
contiguous 0-based sequence — so a row without one is not a row, and that is the test used here
rather than anything heuristic.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import openpyxl
import requests

from bzk.adapters.maxquant import drop_decoys_and_contaminants, read_table
from bzk.http import BytesSession
from bzk.provenance.raw_store import StoredFile, store, verify
from bzk.sources.pride import PXD018299_PROTEIN_GROUPS, fetch

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "pxd018299_protein_groups.json"

#: Br J Cancer 124:817-830 (2021), doi:10.1038/s41416-020-01167-y — the publication the whole
#: PXD018299 reproduction is anchored to. Springer serves supplementary files at a stable path.
SPRINGER_ESM = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41416-020-01167-y/MediaObjects/"
)


@dataclass(frozen=True)
class SupplementaryFile:
    """One journal supplementary file. Not a `DepositFile` — the path scheme is Springer's, not
    PRIDE's, and giving it its own type keeps `sources/pride.py` about PRIDE."""

    label: str
    filename: str
    expected_content_hash: str

    @property
    def url(self) -> str:
        return SPRINGER_ESM + self.filename


SUPP_DATA_2 = SupplementaryFile(
    label="BJC Supplementary Data 2 (proteins up in USP18-/- +IFN)",
    filename="41416_2020_1167_MOESM4_ESM.xlsx",
    expected_content_hash="sha256:da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509",
)
SUPP_DATA_3 = SupplementaryFile(
    label="BJC Supplementary Data 3 (proteins up in WT +IFN)",
    filename="41416_2020_1167_MOESM5_ESM.xlsx",
    expected_content_hash="sha256:9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca",
)


@dataclass(frozen=True)
class GroupStats:
    """One artefact, one accession column."""

    artefact: str
    column: str
    rows: int
    multi_accession: int
    multi_fraction: float
    median_size: float
    max_size: int
    isoform_only: int
    distinct_gene_multi: int


def _base(accession: str) -> str:
    """Accession with any isoform suffix removed: `P09914-2` -> `P09914`.

    An isoform-only group names one gene whose isoform is unresolved; a distinct-gene group names
    different proteins. The two are different problems and only the second is unanswerable, so the
    split is the measurement that matters, not the headline percentage.
    """
    return accession.split("-", 1)[0]


def _split(cell: str) -> list[str]:
    return [a.strip() for a in str(cell).split(";") if a.strip() and a.strip() != "None"]


def summarise(artefact: str, column: str, groups: Sequence[Sequence[str]]) -> GroupStats:
    multi = [g for g in groups if len(g) > 1]
    isoform_only = [g for g in multi if len({_base(a) for a in g}) == 1]
    sizes = [len(g) for g in groups]
    return GroupStats(
        artefact=artefact,
        column=column,
        rows=len(groups),
        multi_accession=len(multi),
        multi_fraction=round(len(multi) / len(groups), 4) if groups else 0.0,
        median_size=statistics.median(sizes) if sizes else 0.0,
        max_size=max(sizes) if sizes else 0,
        isoform_only=len(isoform_only),
        distinct_gene_multi=len(multi) - len(isoform_only),
    )


def measure_perseus_export(path: Path, artefact: str) -> list[GroupStats]:
    """A Perseus Excel export: title in row 1, `C:`/`N:`/`T:`-prefixed header in row 2, data after."""
    workbook = openpyxl.load_workbook(path, read_only=True)
    sheet = workbook.worksheets[0]
    rows = list(sheet.iter_rows(min_row=2, values_only=True))
    workbook.close()
    header = [str(v) for v in rows[0]]
    data = [r for r in rows[1:] if r[header.index("T: Protein IDs")]]
    return [
        summarise(artefact, column, [_split(str(r[header.index(column)])) for r in data])
        for column in ("T: Majority protein IDs", "T: Protein IDs")
    ]


def measure_max_quant(path: Path, artefact: str) -> list[GroupStats]:
    """MaxQuant `proteinGroups.txt`, through the shared reader.

    The spill-line guard lives in `bzk/adapters/maxquant.py`, not here: it was found by this
    measurement but any MaxQuant reader hits it, and a copy in each would be two homes for one rule.
    """
    table = read_table(path)
    kept = drop_decoys_and_contaminants(table)
    return [
        summarise(artefact, column, [_split(r[table.column(column)]) for r in kept])
        for column in ("Majority protein IDs", "Protein IDs")
    ]


def fetch_supplementary(
    supp: SupplementaryFile, *, session: BytesSession | None = None
) -> StoredFile:
    sess = session or requests.Session()
    response = sess.get(supp.url, timeout=600)
    response.raise_for_status()
    stored = store(response.content, supp.filename)
    print(f"[supp] {supp.filename}: {len(response.content):,} bytes, {stored.content_hash}")
    return stored


def measure_all() -> list[GroupStats]:
    """Every artefact, read from the content-addressed store. Raises if one is not fetched."""
    stats: list[GroupStats] = []
    for supp in (SUPP_DATA_2, SUPP_DATA_3):
        path = verify(supp.expected_content_hash, filename=supp.filename)
        stats += measure_perseus_export(path, supp.label)
    digest = PXD018299_PROTEIN_GROUPS.expected_content_hash
    assert digest is not None
    path = verify(digest, filename=PXD018299_PROTEIN_GROUPS.filename)
    stats += measure_max_quant(path, "PXD018299 HAP1_USP18KO_proteinGroups.txt (MaxQuant)")
    return stats


def main() -> int:  # pragma: no cover - convenience entry point
    for supp in (SUPP_DATA_2, SUPP_DATA_3):
        fetch_supplementary(supp)
    fetch(PXD018299_PROTEIN_GROUPS)
    stats = measure_all()
    for s in stats:
        print(
            f"\n{s.artefact}\n  {s.column}: {s.rows:,} rows | "
            f"{s.multi_accession:,} multi-accession ({100 * s.multi_fraction:.1f}%) | "
            f"median {s.median_size:g}, max {s.max_size} | "
            f"isoform-only {s.isoform_only:,}, distinct-gene {s.distinct_gene_multi:,}"
        )
    FIXTURE_PATH.write_text(
        json.dumps(
            {
                "note": (
                    "Measured protein-group ambiguity at protein grain — the counterpart to "
                    "ONTOLOGY.md §6.3's 82% for sites, recorded in ROADMAP.md § Measured findings. "
                    "Regenerate with `python -m bzk.sources.protein_groups`. A change here means "
                    "the measurement code moved or an artefact was revised; both need explaining, "
                    "neither is fixed by regenerating."
                ),
                "measurements": [asdict(s) for s in stats],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"\nwrote {FIXTURE_PATH}")
    return 0


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    sys.exit(main())
