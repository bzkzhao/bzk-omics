"""Run `walk/PREREG-PXD026748-reconstruction.md`: the shotgun gate, then the GG imputation family.

`python -m bzk.sources.pxd026748_reconstruction`, after both deposits and the supplement are in the
content store. Writes `tests/fixtures/pxd026748_reconstruction.json`.

**The pre-registration is the specification and this module implements it, in its order.** The
shotgun positive controls first (`:60-107`), and the GG family only if they pass. Where the
pre-registration is silent this module chooses, and every such choice is named in a constant or a
docstring below and repeated in the turn's report. **No choice was made by looking at an outcome**:
this container has no raw store, so nothing here has been run against the real bytes at all.

**The registered expectations are not inputs.** R1-R5 and the reviewer's own guess at which H9s
outcome will fall out are never read: no constant here carries them, and no branch consults them.
The JUDGED thresholds of PC1-PC3 appear exactly once each, at the point where the gate's verdict is
formed, *after* every figure has been computed from the data — a figure that depended on the
threshold it is compared against would be the shape this whole exercise exists to avoid.

**The gate can only stop the run; it cannot change a number.** If a control misses, the control
block is written with `gg_run: false` and `main` exits non-zero, with the GG arm untouched. That is
`:104-106`: *"If one fails, the failure is reported and the GG arm does not run until it is
understood. No threshold is moved."*

**Nothing here re-derives a population someone else measured.** The GG population is the site
adapter's own `_filter` output, reached through `pxd026748_ingest_figures._parse_arm`, which is
`replay_ingestion`'s `_deposit_for` / `_adapter_for` pair; the claims are the rows the committed
cascade fixture placed at `reaches_test`, read through `bzk.published_cascade.outcome` rather than
by testing `lost_at` here; the sample groups come off the curation records. An adapter or a cascade
re-implemented here would be a second population wearing the same name.

**Two numbers in this module are read from the publication rather than computed**: PC0's 2,438, and
nothing else. `:92` records it as MEASURED — Table 3 lists 2,438 rows — and the gate is an exact
comparison against it, so it is a constant here by necessity. Table 2's 600 is **not** a constant:
`:65` records it, and this module reads Table 2's membership from the workbook at run time and
reports the count it actually read, because a membership test against a remembered number cannot
notice that the sheet it is joined to has moved.
"""

from __future__ import annotations

import collections
import json
import math
import platform
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from bzk import published_cascade as cascade
from bzk.adapters import maxquant, spreadsheet
from bzk.adapters.maxquant_protein_groups import _split
from bzk.curation.loader import LoadedCuration
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.provenance.raw_store import verify
from bzk.rebuild import _deposit_for
from bzk.sources.protein_groups import SupplementaryFile
from bzk.sources.pxd026748_ingest_figures import _parse_arm
from bzk.sources.pxd026748_published_cascade import SUPP_TABLE_1, _commit
from bzk.stats import downshifted_normal, student_t, student_t_s0, welch_t, welch_t_s0
from bzk.stats.anova import two_way
from bzk.stats.registry import TestResult

REPO_ROOT = Path(__file__).resolve().parents[2]
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HOME = Path.home() / ".bzk-omics"

DIGLY_CURATION = CURATION_DIR / "curation_PXD026748.json"
SHOTGUN_CURATION = CURATION_DIR / "curation_PXD026748_shotgun.json"
CASCADE_FIXTURE = FIXTURES_DIR / "pxd026748_published_cascade.json"
FIXTURE_NAME = "pxd026748_reconstruction.json"

GENERATED_BY = "python -m bzk.sources.pxd026748_reconstruction"

#: The two sheets of the supplement the gate reads. `SUPP_TABLE_1` — the workbook and its digest —
#: is imported from the cascade module rather than restated: one file has one home.
TABLE_2_SHEET = "Table 2"
TABLE_3_SHEET = "Table 3"

#: MaxQuant's flag for a group identified only by a modified peptide. `:77-79` removes these in the
#: shotgun arm; `bzk/adapters/maxquant_protein_groups.py` does not, which is why this filter is
#: applied here rather than taken off the adapter.
ONLY_BY_SITE_COLUMN = "Only identified by site"

#: The paper's valid-value rule: at least this many measured values in at least one of the four
#: (genotype, treatment) groups. `:83` for the shotgun arm, `:44` for the GG arm — one rule.
MIN_VALID_IN_A_GROUP = 3

#: `:146-148`. Primary is strict, secondary is inclusive, exactly as the pre-registration writes
#: them — `P < 0.01` from the methods, `P <= 0.001` from the supplement's caption.
PRIMARY_THRESHOLD = 0.01
SECONDARY_THRESHOLD = 0.001

#: `:92`, MEASURED from the publication. The one published figure the gate compares against
#: exactly — see the module docstring.
PC0_REGISTERED = 2438

#: The JUDGED shares of `:93-95`. **Read once each, in `gate_verdict`, and nowhere else.** No
#: figure in this module is computed with reference to them.
PC1_THRESHOLD = 0.99
PC2_THRESHOLD = 0.99
PC3_THRESHOLD = 0.98

#: `:93-94`'s tolerances, on the published quantity's own scale.
PC1_TOLERANCE = 0.01
PC2_TOLERANCE = 0.05

#: `:110-119`. 3 x 3 x 2 x 20 = 360 members, and the grid is fixed here because the
#: pre-registration fixes it: *"No value in this grid is changed after the run."*
WIDTH_SDS = (0.2, 0.3, 0.4)
DOWNSHIFT_SDS = (1.6, 1.8, 2.0)
SCOPES = ("per_sample", "whole_matrix")
SEEDS = tuple(range(20))

#: `:124`. The cell a reader assuming Perseus defaults would pick. Reported, and never evidence of
#: what the publication ran.
DEFAULT_WIDTH_SD = 0.3
DEFAULT_DOWNSHIFT_SD = 1.8
DEFAULT_SCOPE = "per_sample"

#: `:97-102`'s registered set, and the whole of it. Enumerated here rather than in `bzk.stats`'s
#: `TESTS` registry — see `bzk/stats/tests.py`'s docstring for why three of the four are not
#: registered: `ARCHITECTURE.md` §4's table is normative and lists neither Student nor either S0
#: variant.
T_VARIANTS: dict[str, Callable[[np.ndarray, np.ndarray], TestResult]] = {
    "student_t": student_t,
    "student_t_s0": student_t_s0,
    "welch_t": welch_t,
    "welch_t_s0": welch_t_s0,
}

#: How Table 3 and Table 2 are joined to the deposit's protein groups. **Chosen here because no
#: document states it**, and recorded in the fixture as a string so a reader sees the rule beside
#: the counts it produced.
JOIN_RULE = (
    "A published row joins to the protein group whose `Majority protein IDs`, split on ';' with "
    "blanks dropped by `maxquant_protein_groups._split`, has that row's Uniprot ID as its FIRST "
    "entry. First entry and not membership: MaxQuant orders that column by evidence and the "
    "leading accession is the group's representative, so membership would match a group by one of "
    "its also-rans and attribute a published number to a protein the publication did not name. "
    "Rows whose id is the first entry of more than one group are counted as ambiguous and used by "
    "nothing; rows matching no group are counted as unmatched."
)

#: What a missing value is, at the point where the analysis decides. `maxquant.cell_value` returns
#: `0.0` for a reported zero because I19 forbids the *adapter* reading that convention as absence —
#: it is the statistics layer's call, and this is the statistics layer making it, as `:81` requires
#: (*"zero or blank becomes missing"*). Recorded in the fixture for the same reason.
MISSING_RULE = (
    "A cell is missing where the deposit reports nothing (blank, unparseable, or MaxQuant's "
    "literal NaN) AND where it reports a value of zero or less, which log2 cannot take. "
    "`maxquant.cell_value` keeps a reported zero as a measurement (I19) because reading that "
    "convention as absence is the analysis layer's decision to make and record; this is that "
    "decision, and PREREG:81 is the statement of it."
)


class ReconstructionError(ValueError):
    """The inputs cannot be read as the pre-registration describes. Never a warning."""


# ── reading the supplement's other two sheets ───────────────────────────────────────────────────


def _normalise(name: object) -> str:
    """A header cell reduced to lowercase alphanumerics, for matching by content."""
    return "".join(c for c in str(name).lower() if c.isalnum())


def header_index(rows: Sequence[Sequence[object]], markers: Sequence[str]) -> int:
    """The 0-based index of the one row carrying every marker, matched on `_normalise`.

    The same shape as `pxd026748_published_cascade.header_row_index` and deliberately a second
    function rather than a generalisation of it: that one's markers are its own table's join key
    and are fixed on purpose, and widening it would let a caller point it at a sheet it was never
    checked against. Zero and two matches are different defects and the message says which.
    """
    wanted = {_normalise(m) for m in markers}
    matches = [i for i, row in enumerate(rows) if wanted <= {_normalise(c) for c in row if c}]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ReconstructionError(
            f"no row of this sheet carries all of {list(markers)}, so its header cannot be located "
            f"by content. Read {len(rows)} row(s)."
        )
    raise ReconstructionError(
        f"{len(matches)} rows carry all of {list(markers)} (0-based {matches}); the header must be "
        "unique, because choosing one of two would decide silently which block of rows is data."
    )


def sheet_rows(source: Path | bytes, *, sheet: str, markers: Sequence[str]) -> list[dict[str, Any]]:
    """Every data row of one sheet, keyed by its header, in file order."""
    cells = spreadsheet.rows(source, sheet=sheet)
    index = header_index(cells, markers)
    header = [str(c).strip() if c is not None else "" for c in cells[index]]
    return [
        {name: value for name, value in zip(header, row, strict=False) if name}
        for row in cells[index + 1 :]
        if any(c is not None and str(c).strip() for c in row)
    ]


def resolve_column(
    header: Sequence[str], *, required: Sequence[str], forbidden: Sequence[str], what: str
) -> str:
    """The one header whose normalised text holds every `required` and no `forbidden` fragment.

    **The published sheets' column names are not recorded anywhere in this repository**, and this
    module was written without the workbook in reach: `walk/walk_PXD026748.json` shapes sheet
    `Table 1` alone, and the pre-registration names the *quantities* on sheets 2 and 3 rather than
    their spellings. So the columns are located by content, and a miss is a named refusal that
    prints the header it actually read — never a guess, and never a silent fallback to a column
    position. `main` also takes each of these as an override, so a run against a header this cannot
    resolve is one argument away rather than an edit.
    """
    matches = [
        name
        for name in header
        if all(fragment in _normalise(name) for fragment in required)
        and not any(fragment in _normalise(name) for fragment in forbidden)
    ]
    if len(matches) == 1:
        return matches[0]
    raise ReconstructionError(
        f"{len(matches)} column(s) match {what} (normalised text containing all of "
        f"{list(required)} and none of {list(forbidden)}): {matches}. The header read was "
        f"{list(header)}. Pass the column name to `main` rather than letting this module guess."
    )


@dataclass(frozen=True)
class PublishedProtein:
    """One Table 3 row: the two published quantities the gate compares against."""

    log2_fold_change: float
    minus_log_p: float


def read_table_3(
    source: Path | bytes,
    *,
    sheet: str = TABLE_3_SHEET,
    id_column: str | None = None,
    fold_change_column: str | None = None,
    minus_log_p_column: str | None = None,
) -> dict[str, PublishedProtein]:
    """`Uniprot ID` -> the published log2 fold change and -log P, for every readable row.

    A duplicated id raises: `:67` describes one row per quantified protein, and silently keeping
    the last would compare the reconstruction against whichever row happened to sort late.
    """
    rows = sheet_rows(source, sheet=sheet, markers=[id_column or "Uniprot ID"])
    if not rows:
        raise ReconstructionError(f"sheet {sheet!r} has a header and no data rows")
    header = list(rows[0])
    ids = id_column or resolve_column(
        header, required=["uniprot"], forbidden=[], what="Table 3's protein identifier"
    )
    fold = fold_change_column or resolve_column(
        header,
        required=["log2"],
        forbidden=["pvalue", "pval"],
        what="Table 3's published log2 fold change",
    )
    minus_log = minus_log_p_column or resolve_column(
        header,
        required=["log", "p"],
        forbidden=["log2", "fold", "ratio", "difference"],
        what="Table 3's published -log P",
    )

    published: dict[str, PublishedProtein] = {}
    for row in rows:
        key = str(row.get(ids, "")).strip()
        if not key:
            continue
        if key in published:
            raise ReconstructionError(
                f"Table 3 lists {key!r} more than once; `:67` describes one row per quantified "
                "protein, and keeping one of two would decide silently which published number the "
                "controls are measured against."
            )
        try:
            published[key] = PublishedProtein(
                log2_fold_change=float(row[fold]), minus_log_p=float(row[minus_log])
            )
        except (TypeError, ValueError, KeyError):
            # A row whose numbers cannot be read is not a row the controls can use, and inventing
            # a value for it would put a fabricated number in a denominator. Counted by the caller
            # as the difference between the sheet's rows and this mapping's size.
            continue
    return published


def read_table_2_ids(
    source: Path | bytes, *, sheet: str = TABLE_2_SHEET, id_column: str | None = None
) -> list[str]:
    """Table 2's protein identifiers, in file order, **read at run time and never from a constant**.

    A list rather than a set, so the caller can report how many rows were read beside how many
    distinct ids they carry: `:65` records 600, and a figure that silently deduplicated would agree
    with it for the wrong reason.
    """
    rows = sheet_rows(source, sheet=sheet, markers=[id_column or "Uniprot ID"])
    if not rows:
        raise ReconstructionError(f"sheet {sheet!r} has a header and no data rows")
    ids = id_column or resolve_column(
        list(rows[0]), required=["uniprot"], forbidden=[], what="Table 2's protein identifier"
    )
    return [str(row[ids]).strip() for row in rows if str(row.get(ids, "")).strip()]


# ── the pipeline, pure ──────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SampleAxes:
    """The 12 quantitative columns and the design over them, off the curation record.

    Read from the record and never parsed back out of a filename: the record is what states which
    run is which condition, and re-deriving it here would be the `filename_inference` its own
    `basis` field already declares (I8).
    """

    labels: tuple[str, ...]
    genotype: tuple[str, ...]
    treatment: tuple[str, ...]

    @property
    def groups(self) -> dict[str, tuple[int, ...]]:
        """`"genotype | treatment"` -> the column indices in it, sorted by name."""
        found: dict[str, list[int]] = collections.defaultdict(list)
        for i, (g, t) in enumerate(zip(self.genotype, self.treatment, strict=True)):
            found[f"{g} | {t}"].append(i)
        return {k: tuple(v) for k, v in sorted(found.items())}

    def columns_where(self, genotype: str) -> tuple[int, ...]:
        return tuple(i for i, g in enumerate(self.genotype) if g == genotype)


def sample_axes(curation: LoadedCuration) -> SampleAxes:
    """The design, with the columns in the record's own mapping-key order sorted by name.

    Sorted rather than left in insertion order so two runs of this module over the same record
    build the same matrix; the ANOVA and the t-tests are both invariant to the order, so the sort
    decides nothing beyond reproducibility.
    """
    samples = sorted(curation.sample_mapping().samples, key=lambda s: str(s.get("mapping_key", "")))
    return SampleAxes(
        labels=tuple(str(s["mapping_key"]) for s in samples),
        genotype=tuple(str(s.get("genotype")) for s in samples),
        treatment=tuple(str(s.get("treatment")) for s in samples),
    )


def intensity_matrix(
    rows: Sequence[Sequence[str]], column: Mapping[str, int], labels: Sequence[str]
) -> np.ndarray:
    """Rows x the 12 labels, with every absence as NaN. Read through `maxquant.cell_value`."""
    missing = [label for label in labels if label not in column]
    if missing:
        raise ReconstructionError(
            f"the deposit has no column for {missing}; the curation record's mapping keys are the "
            "column names, so a missing one means the record and the file have parted company."
        )
    return np.array(
        [
            [
                np.nan if (v := maxquant.cell_value(row, column, label)) is None else v
                for label in labels
            ]
            for row in rows
        ],
        dtype=float,
    ).reshape(len(rows), len(labels))


def log2_zero_as_missing(matrix: np.ndarray) -> np.ndarray:
    """log2 of every positive value; everything else NaN. `:81`, and see `MISSING_RULE`."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(matrix > 0, np.log2(np.where(matrix > 0, matrix, 1.0)), np.nan)


def median_normalise(matrix: np.ndarray) -> np.ndarray:
    """Subtract each sample's median over its measured values. `:82`.

    Over the **whole** matrix as it stands, which is what makes the order in `pipeline` matter: a
    median taken after the valid-value filter is a median of a different population.
    """
    if matrix.size == 0:
        return matrix.copy()
    return np.asarray(matrix - np.nanmedian(matrix, axis=0), dtype=float)


def valid_value_mask(
    matrix: np.ndarray,
    groups: Mapping[str, Sequence[int]],
    *,
    min_valid: int = MIN_VALID_IN_A_GROUP,
) -> np.ndarray:
    """Rows with at least `min_valid` measured values in at least one group. `:83`."""
    if matrix.size == 0:
        return np.zeros(matrix.shape[0], dtype=bool)
    measured = ~np.isnan(matrix)
    return np.any(
        np.stack([measured[:, list(idx)].sum(axis=1) >= min_valid for idx in groups.values()]),
        axis=0,
    )


def pipeline(matrix: np.ndarray, axes: SampleAxes) -> tuple[np.ndarray, np.ndarray]:
    """`(normalised, keep)` — the registered order, in one place, for both arms.

    log2, then per-sample median subtraction, **then** the valid-value filter: `:80-83` for the
    shotgun arm and `:41-44` for the GG arm state the same three steps in the same order. The order
    is load-bearing and not a formality — normalising after filtering computes each sample's median
    over a different population, which moves every value in the matrix, so the two orders give
    different answers and only one of them is the paper's.

    Returns the normalised matrix over the **whole** population and the mask, rather than the
    filtered matrix alone: the population a row was normalised against is part of what the numbers
    mean, and a caller that wants to know a refused row still contributed to the medians can see
    that it did.
    """
    normalised = median_normalise(log2_zero_as_missing(matrix))
    return normalised, valid_value_mask(normalised, axes.groups)


# ── the shotgun gate ────────────────────────────────────────────────────────────────────────────


def shotgun_rows(table: maxquant.MaxQuantTable) -> tuple[list[list[str]], dict[str, int]]:
    """`:77-78`'s three removals: reverse, contaminant, and only identified by site.

    The first two are `maxquant.drop_decoys_and_contaminants`, the function both adapters call, so
    the rows removed here are the rows an ingestion removes. The third is this module's, because
    the protein adapter does not make it — `pxd026748_ingest_figures._only_identified_by_site`
    records exactly that difference, and the publication's pipeline states it.

    A file without the column keeps every row and says nothing about it, which is that function's
    rule one level up: absent is not zero.
    """
    column = {name: i for i, name in enumerate(table.header)}
    rows = maxquant.drop_decoys_and_contaminants(table)
    index = column.get(ONLY_BY_SITE_COLUMN)
    kept = rows if index is None else [row for row in rows if row[index].strip() != "+"]
    return kept, column


def first_accession(row: Sequence[str], column: Mapping[str, int]) -> str:
    """The protein group's representative accession — see `JOIN_RULE`."""
    index = column.get("Majority protein IDs")
    if index is None:
        raise ReconstructionError(
            "the protein-groups table has no `Majority protein IDs` column, so no published row "
            "can be joined to it"
        )
    entries = _split(row[index])
    return entries[0] if entries else ""


def minus_log10(p: np.ndarray) -> np.ndarray:
    """-log10 of a P value, with 0 going to +inf rather than raising."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return -np.log10(p)


def _fraction(numerator: int, denominator: int) -> dict[str, Any]:
    """A count and its denominator, never a float — `pxd026748_ingest_figures._share`'s rule.

    `share` is included here, unlike there, because the gate's own verdict is a comparison against
    a share and a reader checking that comparison should not have to divide. It is `null` at a zero
    denominator rather than 0.0: no proteins is not a share of zero.
    """
    return {
        "numerator": numerator,
        "denominator": denominator,
        "share": (numerator / denominator) if denominator else None,
    }


def positive_controls(
    *,
    rows: Sequence[Sequence[str]],
    column: Mapping[str, int],
    axes: SampleAxes,
    table_3: Mapping[str, PublishedProtein],
    table_2_ids: Sequence[str],
) -> dict[str, Any]:
    """PC0 to PC3 over the shotgun arm, with no imputation anywhere. Pure.

    **Every figure here is computed before any threshold is consulted.** The verdict is formed by
    `gate_verdict` from this block, which is what keeps the registered shares out of the
    arithmetic.

    **Complete-case proteins only, for PC1 to PC3** (`:72-75`): a protein with no missing value
    among the 12 cannot be touched by imputation, so its reconstructed numbers are comparable with
    published ones without choosing a seed. That is the whole reason the gate is run on the shotgun
    arm rather than on the GG arm.
    """
    matrix = intensity_matrix(rows, column, axes.labels)
    normalised, keep = pipeline(matrix, axes)

    passing = [row for row, k in zip(rows, keep, strict=True) if k]
    values = normalised[keep]
    complete = ~np.isnan(values).any(axis=1)

    accessions = [first_accession(row, column) for row in passing]
    by_accession = collections.Counter(accessions)

    # The three join populations, counted rather than inferred from each other.
    joined = [a in table_3 and by_accession[a] == 1 for a in accessions]
    ambiguous = sum(1 for a in accessions if by_accession[a] > 1)
    unmatched_groups = sum(1 for a in accessions if a not in table_3)
    matched_ids = {a for a, j in zip(accessions, joined, strict=True) if j}

    #: The PC1-PC2 population: complete-case, unambiguously joined to a Table 3 row.
    population = np.array(
        [c and j for c, j in zip(complete.tolist(), joined, strict=True)], dtype=bool
    )
    subject = values[population]
    published_fc = np.array(
        [table_3[a].log2_fold_change for a, p in zip(accessions, population, strict=True) if p]
    )
    published_mlp = np.array(
        [table_3[a].minus_log_p for a, p in zip(accessions, population, strict=True) if p]
    )

    genotypes = sorted(set(axes.genotype))
    if len(genotypes) != 2:
        raise ReconstructionError(
            f"the shotgun record names {len(genotypes)} genotype(s), {genotypes}; `:85`'s t-test "
            "is WT against ISG15-/- and needs exactly two"
        )
    #: WT over KO, and the direction is stated rather than assumed: `:85` writes the contrast as
    #: WT vs ISG15-/-, and `:93` as log2(WT/KO). "WT" is whichever label is not the knockout; the
    #: record spells the knockout with a slash (`ISG15-/-`) and the wild type as `WT`.
    knockout = next((g for g in genotypes if g != "WT"), genotypes[1])
    wild_type = next(g for g in genotypes if g != knockout)
    wt_columns = list(axes.columns_where(wild_type))
    ko_columns = list(axes.columns_where(knockout))

    n = int(population.sum())
    reconstructed_fc = (
        subject[:, wt_columns].mean(axis=1) - subject[:, ko_columns].mean(axis=1)
        if n
        else np.zeros(0)
    )
    pc1_hits = int(np.sum(np.abs(reconstructed_fc - published_fc) <= PC1_TOLERANCE)) if n else 0
    #: Reported, never used: a sign convention opposite to the one assumed above would show up
    #: here as a large number and in PC1 as a small one, which is a diagnosis rather than a
    #: correction. The gate reads `within_tolerance` and nothing else.
    pc1_flipped = int(np.sum(np.abs(-reconstructed_fc - published_fc) <= PC1_TOLERANCE)) if n else 0

    variants: dict[str, Any] = {}
    for name, variant in sorted(T_VARIANTS.items()):
        if not n:
            variants[name] = _fraction(0, 0)
            continue
        result = variant(subject[:, wt_columns], subject[:, ko_columns])
        hits = int(np.sum(np.abs(minus_log10(result.p_value) - published_mlp) <= PC2_TOLERANCE))
        variants[name] = _fraction(hits, n)

    # PC3's population is **all** complete-case proteins, not only the joined ones: `:95` says
    # "complete-case proteins" where `:93-94` say "complete-case proteins ... that are in Table 3",
    # and the difference is in the pre-registration rather than in this reading of it. The
    # restricted figure is reported beside it because the two populations differ and a reader
    # comparing PC3 with PC1 should see which is which.
    table_2 = set(table_2_ids)
    complete_accessions = [a for a, c in zip(accessions, complete.tolist(), strict=True) if c]
    complete_values = values[complete]
    membership = (
        two_way(complete_values, np.array(axes.genotype), np.array(axes.treatment)).min_p()
        < PRIMARY_THRESHOLD
        if complete_values.size
        else np.zeros(0, dtype=bool)
    )
    agree = [
        bool(m) == (a in table_2)
        for a, m in zip(complete_accessions, membership.tolist(), strict=True)
    ]
    agree_joined = [
        ok for ok, a in zip(agree, complete_accessions, strict=True) if a in matched_ids
    ]

    return {
        "pc0": {
            "proteins_passing": len(passing),
            "registered": PC0_REGISTERED,
            "holds": len(passing) == PC0_REGISTERED,
            "rows_after_filters": len(rows),
        },
        "join": {
            "rule": JOIN_RULE,
            "table_3_rows": len(table_3),
            "table_2_rows_read": len(table_2_ids),
            "table_2_distinct_ids": len(table_2),
            "groups_joined": sum(joined),
            "groups_unmatched": unmatched_groups,
            "groups_ambiguous": ambiguous,
            "table_3_ids_unmatched": len([k for k in table_3 if k not in matched_ids]),
        },
        "complete_case": {
            "proteins": int(complete.sum()),
            "in_table_3": n,
            "wild_type": wild_type,
            "knockout": knockout,
        },
        "pc1": {
            **_fraction(pc1_hits, n),
            "tolerance": PC1_TOLERANCE,
            "within_tolerance_under_a_flipped_sign": pc1_flipped,
        },
        "pc2": {"tolerance": PC2_TOLERANCE, "variants": variants},
        "pc3": {
            **_fraction(sum(agree), len(agree)),
            "threshold_used": PRIMARY_THRESHOLD,
            "reconstructed_members": int(membership.sum()),
            "restricted_to_table_3": _fraction(sum(agree_joined), len(agree_joined)),
        },
    }


def gate_verdict(controls: Mapping[str, Any]) -> dict[str, Any]:
    """Pass or fail, from the figures alone. **The only place a registered share is read.**

    PC2 passes if at least one variant passes, and the chosen variant is the one passing with the
    most proteins within tolerance — `:105` and the turn's instruction. Ties break on the variant's
    name, so a tie is resolved by something stable rather than by dictionary order; a tie is
    reported by `variants` carrying two equal numerators, which is visible in the fixture.
    """
    pc2 = controls["pc2"]["variants"]
    passing = {
        name: figures
        for name, figures in pc2.items()
        if figures["share"] is not None and figures["share"] >= PC2_THRESHOLD
    }
    chosen = min(passing, key=lambda name: (-passing[name]["numerator"], name)) if passing else None

    pc1_share = controls["pc1"]["share"]
    pc3_share = controls["pc3"]["share"]
    holds = {
        "pc0": bool(controls["pc0"]["holds"]),
        "pc1": pc1_share is not None and pc1_share >= PC1_THRESHOLD,
        "pc2": chosen is not None,
        "pc3": pc3_share is not None and pc3_share >= PC3_THRESHOLD,
    }
    return {
        "thresholds": {
            "pc0": PC0_REGISTERED,
            "pc1": PC1_THRESHOLD,
            "pc2": PC2_THRESHOLD,
            "pc3": PC3_THRESHOLD,
        },
        "holds": holds,
        "chosen_variant": chosen,
        "passed": all(holds.values()),
    }


# ── the GG family ───────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Member:
    """One of the 360: a grid cell and a seed."""

    width_sd: float
    downshift_sd: float
    scope: str
    seed: int

    @property
    def is_default_cell(self) -> bool:
        return (self.width_sd, self.downshift_sd, self.scope) == (
            DEFAULT_WIDTH_SD,
            DEFAULT_DOWNSHIFT_SD,
            DEFAULT_SCOPE,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "width_sd": self.width_sd,
            "downshift_sd": self.downshift_sd,
            "scope": self.scope,
            "seed": self.seed,
        }


def family_members() -> tuple[Member, ...]:
    """The 360, in a fixed order — width, then downshift, then scope, then seed.

    The order is the fixture's column order for every per-claim array, so it is generated once
    here rather than at each call site.
    """
    return tuple(
        Member(width_sd=w, downshift_sd=d, scope=s, seed=seed)
        for w in WIDTH_SDS
        for d in DOWNSHIFT_SDS
        for s in SCOPES
        for seed in SEEDS
    )


def run_member(values: np.ndarray, axes: SampleAxes, member: Member) -> np.ndarray:
    """Impute, run the two-way ANOVA, and return min(P) per row. `:84-86`."""
    filled = downshifted_normal(
        values,
        downshift_sd=member.downshift_sd,
        width_sd=member.width_sd,
        seed=member.seed,
        scope=member.scope,
    )
    result = two_way(filled.values, np.array(axes.genotype), np.array(axes.treatment))
    return result.min_p()


def claims(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The cascade fixture's rows that reached the test, keyed by `deposit_id`.

    Placement is read through `cascade.outcome`, never by testing `lost_at` here: that function
    refuses a record lost at two stages or at none, so a malformed fixture stops the run instead of
    quietly contributing a claim.
    """
    found = [
        {
            "deposit_id": str(row["deposit_id"]),
            "cluster": str(row["published"].get("Cluster")),
            "published_row": row["published"].get("#"),
            "uniprot_id": row["published"].get("Uniprot ID"),
            "lysine_position": row["published"].get("Lysine position"),
            "has_positive_multiplicity_column": bool(row.get("has_positive_multiplicity_column")),
        }
        for row in fixture["rows"]
        if cascade.outcome(dict(row)) == cascade.RECOVERED
    ]
    duplicates = [
        k for k, c in collections.Counter(r["deposit_id"] for r in found).items() if c > 1
    ]
    if duplicates:
        raise ReconstructionError(
            f"{len(duplicates)} deposit id(s) carry more than one claim ({duplicates[:5]}), so a "
            "claim cannot be keyed by deposit row as `:138` assumes"
        )
    return found


def verdict_thresholds(exposure: int) -> tuple[int, int]:
    """`(durable, underdetermined)` counts needed, computed from the exposure. `:156-160`.

    **From E, never from a constant.** At E = 288 they are 274 and 15, which is the registered
    instance and the only one written in the pre-registration; at any other exposure they move, and
    a hard-coded pair would report the registered instance's verdict over a different family.
    Rounded up, because *"≥ 95% of exposure"* is not met by 273.6 of 288.
    """
    return math.ceil(0.95 * exposure), math.ceil(0.05 * exposure)


def verdict(*, exposure: int, durable: int, underdetermined: int) -> dict[str, Any]:
    """H9s's rule, mechanically. `:156-162`.

    The fourth outcome is not the pre-registration's and cannot arise at its own exposure: `:162`
    observes that *"the first two outcomes cannot both hold, because 274 + 15 > 288"*, which is
    arithmetic about 288 rather than a property of the rule. At some other exposure both can hold —
    at E = 200, durable 190 and underdetermined 10 sum to exactly 200 — and reporting one of them
    would be choosing silently. `both` says so instead.
    """
    durable_needed, underdetermined_needed = verdict_thresholds(exposure)
    weakens = durable >= durable_needed
    extends = underdetermined >= underdetermined_needed
    if weakens and extends:
        outcome = "both"
    elif weakens:
        outcome = "weakens_d5"
    elif extends:
        outcome = "extends_d5_to_imputation_alone"
    else:
        outcome = "neither"
    return {
        "exposure": exposure,
        "durable": durable,
        "underdetermined": underdetermined,
        "durable_needed": durable_needed,
        "underdetermined_needed": underdetermined_needed,
        "outcome": outcome,
    }


def supported(min_p: np.ndarray, *, threshold: float, inclusive: bool) -> np.ndarray:
    """Which values clear a threshold. `:146-148` writes the two differently and means it.

    Primary is `P < 0.01` and secondary is `P <= 0.001`, so the comparison is a parameter rather
    than a `<` written twice. A NaN — a claim with no row in the filtered population — clears
    neither, which is what `unsupported` means for it.
    """
    return min_p <= threshold if inclusive else min_p < threshold


def _categories(support: np.ndarray, total: int) -> list[str]:
    """One category per claim from its support count over all `total` members. `:134-136`."""
    return [
        "durable" if int(c) == total else ("unsupported" if int(c) == 0 else "underdetermined")
        for c in support
    ]


def _counts(categories: Sequence[str]) -> dict[str, int]:
    tally = collections.Counter(categories)
    return {name: int(tally.get(name, 0)) for name in ("durable", "underdetermined", "unsupported")}


def family_block(
    *,
    claim_rows: Sequence[Mapping[str, Any]],
    min_p: np.ndarray,
    members: Sequence[Member],
    default_cell_medians: np.ndarray,
    whole_table_supported: int,
    population_rows: int,
    claims_without_a_row: Sequence[str],
) -> dict[str, Any]:
    """Every readout of `:130-152`, plus H9s's verdict. Pure.

    `min_p` is claims x members, in `members` order. A claim whose deposit row is not in the
    filtered population carries a row of NaN: it is supported by no member, which is what
    `unsupported` means, and it is *also* counted separately so that "supported in none" and "not
    in the population at all" are never the same number.
    """
    exposure = len(claim_rows)
    readouts: dict[str, Any] = {}
    for label, threshold, inclusive in (
        ("primary", PRIMARY_THRESHOLD, False),
        ("secondary", SECONDARY_THRESHOLD, True),
    ):
        support = supported(min_p, threshold=threshold, inclusive=inclusive).sum(axis=1)
        categories = _categories(support, len(members))
        by_cluster: dict[str, dict[str, int]] = {}
        for cluster in sorted({str(c["cluster"]) for c in claim_rows}):
            by_cluster[cluster] = _counts(
                [
                    k
                    for k, c in zip(categories, claim_rows, strict=True)
                    if str(c["cluster"]) == cluster
                ]
            )
        readouts[label] = {
            "threshold": threshold,
            "counts": _counts(categories),
            "by_cluster": by_cluster,
            # The default cell alone (`:139`), by the median over its twenty seeds rather than by
            # any one of them: a single seed is a member, and the cell is the twenty together.
            "default_cell_supported": int(
                supported(default_cell_medians, threshold=threshold, inclusive=inclusive).sum()
            ),
            "categories": categories,
            "support": [int(c) for c in support],
        }

    consistency = int(
        np.sum(
            (default_cell_medians > SECONDARY_THRESHOLD)
            & (default_cell_medians <= PRIMARY_THRESHOLD)
        )
    )
    flagged = [i for i, c in enumerate(claim_rows) if c["has_positive_multiplicity_column"]]
    primary = readouts["primary"]
    return {
        "members": [m.as_dict() for m in members],
        "default_cell": {
            "width_sd": DEFAULT_WIDTH_SD,
            "downshift_sd": DEFAULT_DOWNSHIFT_SD,
            "scope": DEFAULT_SCOPE,
            "seeds": list(SEEDS),
        },
        "exposure": exposure,
        "population_rows": population_rows,
        "claims_without_a_row_in_the_population": list(claims_without_a_row),
        "readouts": readouts,
        "threshold_consistency_count": consistency,
        "whole_table_supported_in_the_default_cell": whole_table_supported,
        "multiplicity_flagged_claims": [
            {
                **dict(c),
                "median_min_p_default_cell": float(default_cell_medians[i]),
                "support_primary": primary["support"][i],
                "category_primary": primary["categories"][i],
            }
            for i, c in enumerate(claim_rows)
            if i in flagged
        ],
        "verdict": verdict(
            exposure=exposure,
            durable=primary["counts"]["durable"],
            underdetermined=primary["counts"]["underdetermined"],
        ),
        "claims": [
            {
                **dict(c),
                "median_min_p_default_cell": float(default_cell_medians[i]),
                "min_p": [None if np.isnan(v) else float(v) for v in min_p[i]],
            }
            for i, c in enumerate(claim_rows)
        ],
    }


# ── the IO ──────────────────────────────────────────────────────────────────────────────────────


def _dataset(curation: LoadedCuration) -> Mapping[str, Any]:
    return next(n for n in curation.nodes if n[NODE_TYPE_KEY] == "Dataset")


def _header(
    *,
    digly: LoadedCuration,
    shotgun: LoadedCuration,
    supplement: SupplementaryFile,
    generated_at: str,
    gg_run: bool,
) -> dict[str, Any]:
    digly_dataset, shotgun_dataset = _dataset(digly), _dataset(shotgun)
    return {
        "dataset": str(digly_dataset["external_accession"]),
        "registration": "walk/PREREG-PXD026748-reconstruction.md",
        "gg_run": gg_run,
        "published_file": supplement.filename,
        "published_content_hash": supplement.expected_content_hash,
        "published_sheets": [TABLE_2_SHEET, TABLE_3_SHEET],
        "shotgun_file": str(shotgun_dataset["label"]),
        "shotgun_content_hash": str(shotgun_dataset["content_hash"]),
        "digly_file": str(digly_dataset["label"]),
        "digly_content_hash": str(digly_dataset["content_hash"]),
        "note": (
            "PXD026748's reconstruction, as registered. The shotgun arm's positive controls run "
            "first over imputation-free proteins; the GG imputation family runs only if they all "
            "hold, and `gg_run` says whether it did. Every per-claim min(P) is kept in full: "
            "`family.claims[].min_p` is one value per member, aligned with `family.members`, so "
            "any readout can be recomputed from the fixture without re-running the family. "
            "Generated from both deposits' and the supplement's bytes, with the populations taken "
            "from the adapters and the cascade fixture rather than re-derived. Regenerate with "
            f"`{GENERATED_BY}`."
        ),
        "generated_by": GENERATED_BY,
        "generated_under": {
            "generated_at": generated_at,
            **_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "missing_rule": MISSING_RULE,
            "valid_value_rule": (
                f"at least {MIN_VALID_IN_A_GROUP} measured values in at least one of the four "
                "(genotype, treatment) groups, applied after log2 and per-sample median subtraction"
            ),
        },
    }


def _write(fixtures_dir: Path, fixture: Mapping[str, Any]) -> Path:
    path = fixtures_dir / FIXTURE_NAME
    path.write_text(json.dumps(fixture, indent=2) + "\n")
    return path


def _supplement_path(supplement: SupplementaryFile, home: Path) -> Path:
    try:
        return verify(supplement.expected_content_hash, filename=supplement.filename, home=home)
    except FileNotFoundError as exc:
        raise SystemExit(
            f"{supplement.filename} is not in the content store under {home}; fetch it from "
            f"{supplement.url} and re-run. No fixture was written."
        ) from exc


def main(
    *,
    home: Path = HOME,
    fixtures_dir: Path = FIXTURES_DIR,
    digly_curation_path: Path = DIGLY_CURATION,
    shotgun_curation_path: Path = SHOTGUN_CURATION,
    cascade_fixture_path: Path = CASCADE_FIXTURE,
    supplement: SupplementaryFile = SUPP_TABLE_1,
    table_2_id_column: str | None = None,
    table_3_id_column: str | None = None,
    table_3_fold_change_column: str | None = None,
    table_3_minus_log_p_column: str | None = None,
) -> int:
    """The gate, then the family if it passes. Returns 0 only when the whole registration ran.

    **The IO is here and the arithmetic is above**, as turns 13 and 15 have it: every path is a
    parameter with a real default, so the tests drive `main` end to end over synthetic bytes. The
    four column overrides exist because the published sheets' header spellings are recorded nowhere
    in this repository — `resolve_column` locates them by content and refuses by name, and an
    override turns a refusal into an argument rather than an edit.
    """
    generated_at = datetime.now(UTC).isoformat()

    shotgun_curation, _, _ = _parse_arm(shotgun_curation_path, home)
    digly_curation, digly_adapter, _ = _parse_arm(digly_curation_path, home)
    shotgun_deposit = _deposit_for(shotgun_curation, home)
    digly_deposit = _deposit_for(digly_curation, home)
    assert shotgun_deposit is not None and digly_deposit is not None  # `_parse_arm` raised if not

    supplement_path = _supplement_path(supplement, home)
    table_3 = read_table_3(
        supplement_path,
        id_column=table_3_id_column,
        fold_change_column=table_3_fold_change_column,
        minus_log_p_column=table_3_minus_log_p_column,
    )
    table_2_ids = read_table_2_ids(supplement_path, id_column=table_2_id_column)

    shotgun_table = maxquant.read_table(shotgun_deposit)
    rows, shotgun_column = shotgun_rows(shotgun_table)
    shotgun_axes = sample_axes(shotgun_curation)
    controls = positive_controls(
        rows=rows,
        column=shotgun_column,
        axes=shotgun_axes,
        table_3=table_3,
        table_2_ids=table_2_ids,
    )
    gate = {**controls, "verdict": gate_verdict(controls)}

    print(f"[gate] PC0 {controls['pc0']['proteins_passing']:,} of {PC0_REGISTERED:,} registered")
    for name in ("pc1", "pc3"):
        share = controls[name]["share"]
        print(
            f"[gate] {name.upper()} {controls[name]['numerator']:,}/"
            f"{controls[name]['denominator']:,}" + (f" ({share:.4f})" if share else "")
        )
    for name, figures in sorted(controls["pc2"]["variants"].items()):
        print(f"[gate] PC2 {name:<14} {figures['numerator']:,}/{figures['denominator']:,}")

    header = _header(
        digly=digly_curation,
        shotgun=shotgun_curation,
        supplement=supplement,
        generated_at=generated_at,
        gg_run=gate["verdict"]["passed"],
    )
    if not gate["verdict"]["passed"]:
        # `:104-106`: the failure is reported and the GG arm does not run. No family block at all,
        # rather than an empty one — an empty block would read as a family that ran and found
        # nothing.
        path = _write(fixtures_dir, {**header, "gate": gate})
        failed = [k for k, ok in gate["verdict"]["holds"].items() if not ok]
        print(f"[gate] FAILED on {failed}; the GG arm did not run. Wrote {path}")
        return 1

    # The claims are read first, before the deposit is touched: they are the exposure H9s is
    # measured against, and a cascade fixture that cannot be read should stop the run before 360
    # ANOVAs rather than after them.
    claim_rows = claims(json.loads(cascade_fixture_path.read_text(encoding="utf-8")))

    digly_table = maxquant.read_table(digly_deposit)
    digly_column = {name: i for i, name in enumerate(digly_table.header)}
    # **`_filter`'s output, which is the paper's matrix and includes rows the platform refused at
    # ingestion.** Not the emitted observations and not the claims: a refused row still carries
    # measured intensities, and dropping it here would compute every per-sample median over a
    # different population and move every value in the matrix.
    population, _, _ = digly_adapter._filter(digly_table, digly_column)
    digly_axes = sample_axes(digly_curation)
    normalised, keep = pipeline(
        intensity_matrix(population, digly_column, digly_axes.labels), digly_axes
    )
    values = normalised[keep]
    kept_ids = [
        str(row[digly_column["id"]]).strip() for row, k in zip(population, keep, strict=True) if k
    ]
    row_of_id = {row_id: i for i, row_id in enumerate(kept_ids)}

    index_of_claim = [row_of_id.get(c["deposit_id"]) for c in claim_rows]
    missing_claims = [
        c["deposit_id"] for c, i in zip(claim_rows, index_of_claim, strict=True) if i is None
    ]

    members = family_members()
    min_p = np.full((len(claim_rows), len(members)), np.nan)
    default_columns: list[np.ndarray] = []
    for position, member in enumerate(members):
        row_min_p = run_member(values, digly_axes, member)
        for claim, index in enumerate(index_of_claim):
            if index is not None:
                min_p[claim, position] = row_min_p[index]
        if member.is_default_cell:
            default_columns.append(row_min_p)
        print(f"[family] {position + 1:>3}/{len(members)} {member.as_dict()}", end="\r")
    print()

    # The default cell's median over its seeds, once for the whole population and then read off for
    # the claims: `:150-152`'s whole-table count and `:145-148`'s per-claim median are the same
    # statistic over two populations, and computing it twice would let them drift apart.
    default_median = np.median(np.stack(default_columns, axis=1), axis=1)
    claim_medians = np.array(
        [np.nan if i is None else default_median[i] for i in index_of_claim], dtype=float
    )

    family = family_block(
        claim_rows=claim_rows,
        min_p=min_p,
        members=members,
        default_cell_medians=claim_medians,
        whole_table_supported=int(np.sum(default_median < PRIMARY_THRESHOLD)),
        population_rows=len(population),
        claims_without_a_row=missing_claims,
    )
    path = _write(fixtures_dir, {**header, "gate": gate, "family": family})

    counts = family["readouts"]["primary"]["counts"]
    print(f"[family] exposure {family['exposure']:,} claim(s) over {len(members)} member(s)")
    print(
        f"[family] primary durable {counts['durable']:,}, "
        f"underdetermined {counts['underdetermined']:,}, unsupported {counts['unsupported']:,}"
    )
    print(
        f"[family] verdict {family['verdict']['outcome']} "
        f"(needs {family['verdict']['durable_needed']} / "
        f"{family['verdict']['underdetermined_needed']} of {family['exposure']})"
    )
    print(f"[family] wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
