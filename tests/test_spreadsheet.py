"""`bzk/adapters/spreadsheet.py` — the one home for reading an `.xlsx` sheet.

Every workbook here is built in `tmp_path` by `openpyxl` and thrown away. No deposit file is in the
tree and none is fetched; the shape being modelled — three header rows, a type stamp on the third —
is **reviewer-supplied and not re-derivable in this container**, and is labelled so at each site.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

from bzk.adapters.spreadsheet import (
    SpreadsheetError,
    looks_like_a_workbook,
    rows,
    text_rows,
)


def _workbook(path: Path, sheet_rows: list[list[object]]) -> Path:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in sheet_rows:
        sheet.append(row)
    workbook.save(path)
    return path


def test_a_workbook_is_recognised_by_its_container_and_a_text_file_is_not(tmp_path: Path) -> None:
    """`ARCHITECTURE.md` §3's *content, not name*: the suffix is not evidence, the bytes are."""
    book = _workbook(tmp_path / "book.xlsx", [["a", "b"], [1, 2]])
    assert looks_like_a_workbook(book.read_bytes())
    text = tmp_path / "table.txt"
    text.write_text("a\tb\n1\t2\n", encoding="utf-8")
    assert not looks_like_a_workbook(text.read_bytes())


def test_rows_yields_cells_as_openpyxl_does_including_the_empty_cell(tmp_path: Path) -> None:
    """The raw reading, which `bzk/sources/protein_groups.py` depends on: a missing cell arrives as
    `None` there and its own splitter discards the `'None'` that `str` makes of it."""
    book = _workbook(tmp_path / "raw.xlsx", [["T: Protein IDs", None], ["P20591", 3]])
    read = rows(book)
    assert read[0] == ("T: Protein IDs", None)
    assert read[1] == ("P20591", 3)


def test_text_rows_makes_a_missing_cell_the_empty_string(tmp_path: Path) -> None:
    """*Absent* has to stay distinguishable from a cell whose text is the word `None`."""
    book = _workbook(tmp_path / "text.xlsx", [["Set 1", None], ["P20591", "None"]])
    read = text_rows(book)
    assert read[0][1] == ""
    assert read[1][1] == "None"


def test_min_row_skips_a_title_row(tmp_path: Path) -> None:
    """`bzk/sources/protein_groups.py` reads a Perseus Excel export whose row 1 is a title."""
    book = _workbook(tmp_path / "titled.xlsx", [["A title"], ["T: Protein IDs"], ["P20591"]])
    assert text_rows(book, min_row=2)[0][0] == "T: Protein IDs"


def test_bytes_and_a_path_are_the_same_read(tmp_path: Path) -> None:
    """The adapter hashes bytes and must parse those same bytes, so the reader takes both.

    Both readings are compared to what the workbook was written with, rather than to each other:
    two calls of one function agreeing says nothing if the function returns the same wrong thing
    twice, which is the shape `tests/test_tautology_sweep.py` exists to catch.
    """
    book = _workbook(tmp_path / "both.xlsx", [["T: Protein IDs"], ["P20591"]])
    assert text_rows(book.read_bytes()) == [["T: Protein IDs"], ["P20591"]]
    assert text_rows(book) == [["T: Protein IDs"], ["P20591"]]


def test_a_truncated_workbook_is_refused_and_the_refusal_names_what_it_found(
    tmp_path: Path,
) -> None:
    """Refuse rather than guess, and name what was found — `HANDOFF.md` §8 for this adapter class.

    The container test says *try the workbook reader*; only the reader can say the bytes are not a
    workbook, and it says so loudly rather than returning an empty sheet.
    """
    broken = tmp_path / "broken.xlsx"
    broken.write_bytes(b"PK\x03\x04truncated")
    assert looks_like_a_workbook(broken.read_bytes())
    with pytest.raises(SpreadsheetError) as exc:
        rows(broken)
    assert "not a readable workbook" in str(exc.value)
