"""`python -m bzk.pxd055843_depletion_ranking` — PXD055843's one contrast, ranked by difference.

**What this answers, and why it had to become code.** `Supplementary_Data_S1_TP.xlsx` carries
exactly one set of statistics columns, for the contrast `data/curation/curation_PXD055843.json`
records as `siUSP24_IFN_vs_siC_IFN`. A ranking of its proteins by that contrast's difference was
computed off-repository and read off a terminal, and a figure produced that way cannot be
re-derived. The artefact is digest-pinned, so the ranking becomes reproducible the moment the
computation is committed beside the pin — which is all this module is.

**It lives in `bzk/` beside `drift.py`, `fetch_progress.py` and `target_recovery_rules.py`, which
is the stated precedent.** `bzk/target_recovery_rules.py` sets it out for a module of exactly this
kind: *"`bzk/sources/` is 'retrieval of public deposits' (its `__init__`), and this retrieves
nothing; `bzk/analysis/` is change-sets for the graph, and this writes no node."* Both clauses hold
here — the bytes are located in a store this module does not fill, and nothing it computes reaches
the graph. Nothing in the installed package imports it.

**This module writes nothing and decides nothing.** No fixture, no file, stdout only. It reports an
*ordering*; which protein sits where in it, and whether that protein clears any threshold, is a
finding for whoever reads the output. Committing a slice of the ranking would need a cutoff, and a
cutoff is a selection rule — the thing this project has twice had to unpick. So the whole ordering
is computed on demand from the pinned bytes and none of it is pinned here.

**It does not touch the arm order and cannot settle it.** `curation_PXD055843.json` records under
`unresolved` that which arm is the numerator *"rests on Perseus' numerator-first convention rather
than on any statement"*. A ranking by difference inherits that sign convention whole: it says which
proteins sit at which end of the file's own column, not which direction that end means. Nothing
here resolves it, and the contrast is printed as the **file** spells it — the suffix Perseus wrote
into the column name — rather than as the curation record's id, so an output read later cannot be
mistaken for a statement about the arms.

**The digest is not spelled a second time.** The bytes are located through
`bzk/sources/pxd055843_perseus.py`'s `locate`, which reads the digest and filename off
`data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` and hands them to
`bzk/provenance/raw_store.py`'s `verify`, re-hashing what it finds. A second spelling of either
value here could disagree with the record that ingestion runs against, and the refusal message that
names what was looked for is worth inheriting rather than re-writing. The cost is stated: importing
that module pulls the ingestion path in at import time. It is paid for one home for *which bytes*.

**Columns are discovered by name and never by position.** The file's real header is the row Perseus
stamped, and the rows above it are merged group labels — so a column index read off one file would
be a coincidence, not a rule. The named row is located by `bzk/adapters/perseus.py`'s own rule (the
first row within `HEADER_SCAN_ROWS` carrying a type-stamped cell) rather than by the index that
rule happens to return for this file, so a file of another shape fails instead of reading a label
row as a header. `TYPE_PREFIXES` is imported from that module rather than restated.

**A needed column that is absent, or that matches twice, is an error.** Taking the first of several
matches is how a lookup silently reads the wrong column, and this file carries a `p-value` column
whose name is a substring of its `-Log ... p-value` column's — the exact shape that goes wrong. So
each mark below is matched against every header name and the count is asserted, with the header
printed either way.

**No gene column of *this file* is on record in this repository, and it may carry none.** Its
protein columns are — `Protein.Group` and `Protein.Ids`, recorded as reviewer-supplied in
`ROADMAP.md`'s four-findings block — and the only gene spelling the tree holds is MaxQuant's
`Gene names`, off the other deposit entirely. So `GENE_MARK` is a substring and not a name, and a
file carrying no such column, or two, is refused with its header named rather than ranked without
the identifier every reported row needs. **That refusal is the honest outcome and not a gap**: the
run this module replaces reported genes, so a gene column was there to be read; if the header this
raises with says otherwise, that is a fact about the file worth learning at the point of reading.

**A null difference is an exclusion, not a loser.** Perseus writes `NaN` where the arithmetic
produced one, and a NaN comparison is silently false, so an unexcluded null would sort somewhere
and read as a protein that was measured — the ground `bzk/target_recovery_rules.py` already states
for the same reason. Rows with no difference are counted, excluded, and the count is printed. A
cell that is neither empty nor a number is neither: it is refused, because a value nobody can parse
is not a value that is absent.

**The sort is stable, so ties keep the file's row order.** Stated because it is a property of
`list.sort` that this module depends on and does not enforce: two proteins with the same difference
are reported in the order the file carries them, which is the only order the file states.
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from bzk.adapters import spreadsheet
from bzk.adapters.perseus import HEADER_SCAN_ROWS, TYPE_PREFIXES
from bzk.sources.pxd055843_perseus import locate

#: Substrings of the header text, not column names. Each must match exactly one column — see the
#: module docstring on why the first match is never taken. `MINUS_LOG_P_MARK` carries its `-Log`
#: because without it the mark would also match the plain p-value column, which is the collision
#: this rule exists to catch rather than to tolerate.
DIFFERENCE_MARK = "Student's T-test Difference"
Q_VALUE_MARK = "Student's T-test q-value"
MINUS_LOG_P_MARK = "-Log Student's T-test p-value"

#: The identifier every reported row carries. A substring because no gene column of this file is
#: recorded anywhere in this repository — see the module docstring.
GENE_MARK = "Gene"

#: How many rows are printed at each end. Fixed rather than a flag: a caller choosing the number
#: chooses a cutoff, and this module reports an ordering rather than a selection from one.
HEAD_TAIL = 15

#: What separates the members of an identifier cell. `ROADMAP.md`'s four-findings block normalises
#: this file's protein cells *"by splitting on `;` and stripping"*, and the gene column is read the
#: same way so a lookup finds a name that shares its cell with another.
MEMBER_SEPARATOR = ";"


class RankingError(ValueError):
    """The file cannot be ranked. Never downgraded to a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class Row:
    """One protein's place in the ordering, with the statistics the file carries beside it."""

    rank: int  # 1-based, ascending by difference — rank 1 is the most negative
    gene: str  # the identifier cell verbatim, members unsplit
    difference: float
    q_value: float | None
    minus_log_p: float | None


@dataclass(frozen=True)
class Ranked:
    """The whole ordering, with the counts that say what it was computed from."""

    contrast: str  # as the file's own column name spells it, not as the curation record ids it
    columns: dict[str, str]  # mark -> the header name it matched, so the discovery is readable
    rows: list[Row]
    data_rows: int
    without_difference: int


def _named(cell: str) -> str:
    """A header cell's name: Perseus' type stamp removed where there is one, whitespace stripped.

    The prefix *set* has one home — `bzk/adapters/perseus.py` — and only its two-line application
    is here, because that module's own stripper is private to it.
    """
    for prefix in TYPE_PREFIXES:
        if cell.startswith(prefix):
            return cell[len(prefix) :].strip()
    return cell.strip()


def header_row(cells: list[list[str]]) -> int:
    """The index of the row that names the columns: the first stamped one. See the docstring."""
    for index, row in enumerate(cells[:HEADER_SCAN_ROWS]):
        if any(cell.startswith(TYPE_PREFIXES) for cell in row):
            return index
    raise RankingError(
        f"no column-type stamp in the first {HEADER_SCAN_ROWS} rows, so no row names the columns. "
        f"Expected one of {list(TYPE_PREFIXES)} to start a header cell."
    )


def column(header: list[str], mark: str) -> int:
    """The one column whose name contains `mark`, or an error naming what was found instead."""
    hits = [i for i, name in enumerate(header) if mark in name]
    if not hits:
        raise RankingError(
            f"no column's name contains {mark!r}. The header names {header}. Refused rather than "
            "read without it — every reported row carries this column."
        )
    if len(hits) > 1:
        raise RankingError(
            f"{len(hits)} columns' names contain {mark!r}: {[header[i] for i in hits]}. Refused "
            "rather than taking the first, which is how a lookup silently reads the wrong column."
        )
    return hits[0]


def contrast_of(header: list[str], difference: int) -> str:
    """The contrast as the file records it: what the difference column's name carries after the mark.

    Read from the header rather than restated from `bzk/sources/pxd055843_perseus.py`'s
    `COLUMN_SUFFIX` or from the curation record's contrast id. A restated value would agree with
    the file only for as long as nobody hands this module a different export.
    """
    name = header[difference]
    suffix = name[name.find(DIFFERENCE_MARK) + len(DIFFERENCE_MARK) :].strip()
    if not suffix:
        raise RankingError(
            f"the difference column is named {name!r} and carries nothing after "
            f"{DIFFERENCE_MARK!r}, so the file names no contrast for it."
        )
    return suffix


def _value(cell: str, *, row_no: int, column_name: str) -> float | None:
    """The cell as a number, or `None` where the file carries no value. See the docstring on NaN."""
    text = cell.strip()
    if not text:
        return None
    try:
        value = float(text)
    except ValueError as exc:
        raise RankingError(
            f"row {row_no}, column {column_name!r}: {text!r} is not a number. Refused rather than "
            "read as absent — a cell nobody can parse is not a cell with nothing in it."
        ) from exc
    return None if math.isnan(value) else value


def members(cell: str) -> list[str]:
    """An identifier cell's members, split and stripped. See `MEMBER_SEPARATOR`."""
    return [part.strip() for part in cell.split(MEMBER_SEPARATOR) if part.strip()]


def rank(source: Path) -> Ranked:
    """The whole ordering for one export, ascending by difference."""
    cells = spreadsheet.text_rows(source)
    named = header_row(cells)
    header = [_named(cell) for cell in cells[named]]
    at = {
        mark: column(header, mark)
        for mark in (GENE_MARK, DIFFERENCE_MARK, Q_VALUE_MARK, MINUS_LOG_P_MARK)
    }
    found: list[tuple[str, float, float | None, float | None]] = []
    data_rows = 0
    without_difference = 0
    for row_no, row in enumerate(cells[named + 1 :], start=named + 2):
        if not any(cell.strip() for cell in row):
            continue
        data_rows += 1
        read = {
            mark: _value(
                row[index] if index < len(row) else "", row_no=row_no, column_name=header[index]
            )
            for mark, index in at.items()
            if mark != GENE_MARK
        }
        difference = read[DIFFERENCE_MARK]
        if difference is None:
            without_difference += 1
            continue
        gene_at = at[GENE_MARK]
        gene = row[gene_at].strip() if gene_at < len(row) else ""
        found.append((gene, difference, read[Q_VALUE_MARK], read[MINUS_LOG_P_MARK]))
    found.sort(key=lambda entry: entry[1])  # stable: ties keep the file's row order
    return Ranked(
        contrast=contrast_of(header, at[DIFFERENCE_MARK]),
        columns={mark: header[index] for mark, index in at.items()},
        rows=[Row(i, *entry) for i, entry in enumerate(found, start=1)],
        data_rows=data_rows,
        without_difference=without_difference,
    )


def lookup(ranked: Ranked, gene: str) -> list[Row]:
    """Every row whose identifier cell has `gene` among its members. Exact, and case-sensitive.

    A list rather than a row: a name can sit in more than one cell, and reporting the first would
    be a selection. Callers get every place the ordering holds it, or nothing.
    """
    return [row for row in ranked.rows if gene in members(row.gene)]


def _show(value: float | None, spec: str) -> str:
    """A number, or the third state. `absent` and not a zero — see the module docstring."""
    return "absent" if value is None else format(value, spec)


def _row_line(row: Row) -> str:
    cells = (
        f"{row.rank:>7}",
        f"{row.gene[:28]:<28}",
        f"{_show(row.difference, '+.4f'):>12}",
        f"{_show(row.q_value, '.4g'):>12}",
        f"{_show(row.minus_log_p, '.4g'):>12}",
    )
    return "  " + "  ".join(cells)


def _heading() -> str:
    cells = (f"{'rank':>7}", f"{'gene':<28}", f"{'difference':>12}", f"{'q-value':>12}")
    return "  " + "  ".join((*cells, f"{'-log p':>12}"))


def report(ranked: Ranked, genes: Sequence[str] = ()) -> list[str]:
    """The printed form. Returned rather than printed so a caller can test it without capturing."""
    total = len(ranked.rows)
    lines = [
        f"[PXD055843] contrast, as the file's own column names spell it: {ranked.contrast}",
        "[PXD055843] columns matched, mark by mark:",
    ]
    lines.extend(f"    {mark!r} -> {name!r}" for mark, name in sorted(ranked.columns.items()))
    lines.append(
        f"[PXD055843] {ranked.data_rows:,} data row(s): {total:,} with a value in the difference "
        f"column, {ranked.without_difference:,} excluded for having none"
    )
    if total <= 2 * HEAD_TAIL:
        lines.append(
            f"[PXD055843] {total:,} ranked row(s) is at most two blocks of {HEAD_TAIL}, so the "
            "two below overlap and are the same ordering read twice"
        )
    lines.append(f"[PXD055843] most negative {HEAD_TAIL} by difference, in rank order:")
    lines.append(_heading())
    lines.extend(_row_line(row) for row in ranked.rows[:HEAD_TAIL])
    lines.append(f"[PXD055843] most positive {HEAD_TAIL} by difference, in rank order:")
    lines.append(_heading())
    lines.extend(_row_line(row) for row in ranked.rows[-HEAD_TAIL:])
    for gene in genes:
        hits = lookup(ranked, gene)
        if not hits:
            lines.append(
                f"[PXD055843] {gene}: absent — no ranked row's identifier cell carries it as a "
                f"{MEMBER_SEPARATOR!r}-separated member (compared exactly, case-sensitively)"
            )
            continue
        for hit in hits:
            lines.append(f"[PXD055843] {gene}: rank {hit.rank:,} of {total:,}")
            lines.append(_heading())
            lines.append(_row_line(hit))
    return lines


def main(argv: list[str] | None = None) -> int:
    """Print the ordering. Writes no file — see the module docstring."""
    parser = argparse.ArgumentParser(
        prog="python -m bzk.pxd055843_depletion_ranking",
        description=(
            "Rank PXD055843's Perseus total-proteome export by its one contrast's difference. "
            "Reports an ordering; it settles neither the arm order nor any threshold."
        ),
    )
    parser.add_argument(
        "genes",
        nargs="*",
        help="gene names to locate in the full ordering, so a caller need not re-sort it",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=None,
        help="the tree whose raw/ holds the artefact (default: ~/.bzk-omics)",
    )
    args = parser.parse_args(argv)
    for line in report(rank(locate(home=args.home)), args.genes):
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    raise SystemExit(main())
