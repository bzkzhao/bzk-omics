"""`bzk/adapters/maxquant.py` — the guarded reader, ahead of the adapter that will use it.

The spill-line guard is the reason this module exists before the adapter does. It was found while
measuring protein groups (`ROADMAP.md` § Protein-group ambiguity), and the failure mode is the one
this project keeps designing against: the line passes every structural check, `pandas` reads it as
data, nothing raises, and a summary statistic moves by a tenth of a point while the maximum moves
by two orders of magnitude.

Fixtures are synthetic and minimal, per the rule in `HANDOFF.md` §8 — an error path tested against
whichever real file happens to be malformed today stops testing the day that file is replaced. The
real file is exercised separately, by `tests/test_protein_groups.py`, where it is the subject rather
than the guard.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bzk.adapters.maxquant import (
    MaxQuantError,
    drop_decoys_and_contaminants,
    read_table,
)

HEADER = "Protein IDs\tMajority protein IDs\tReverse\tPotential contaminant\tPeptide IDs\tid"


def _write(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "proteinGroups.txt"
    path.write_bytes(("\r\n".join((HEADER, *lines)) + "\r\n").encode())  # CRLF, as the deposit is
    return path


def test_reads_a_clean_table(tmp_path: Path) -> None:
    path = _write(tmp_path, "P20591\tP20591\t\t\t1;2;3\t0", "P19525\tP19525\t\t\t4;5\t1")
    table = read_table(path)
    assert table.header[0] == "Protein IDs"
    assert len(table.rows) == 2
    assert table.spill_lines == 0


def test_crlf_leaves_no_carriage_return_on_the_last_column(tmp_path: Path) -> None:
    """`ARCHITECTURE.md` §3: a manual split leaves `\\r` on the last field of every row, so a
    lookup on the last column silently returns nothing. `id` IS the last column here, and the whole
    spill guard depends on reading it."""
    path = _write(tmp_path, "P20591\tP20591\t\t\t1;2\t0")
    table = read_table(path)
    assert table.rows[0][table.column("id")] == "0"


def test_a_spill_line_is_not_a_row(tmp_path: Path) -> None:
    """The defect, reproduced: a line with the right field count and no `id`.

    MaxQuant's numeric id lists spill onto their own physical lines. Six do in
    `HAP1_USP18KO_proteinGroups.txt`, each carrying exactly the header's field count — so nothing
    structural rejects them, and their accession column holds numbers.
    """
    path = _write(
        tmp_path,
        "P20591\tP20591\t\t\t1;2;3\t0",
        "6215;8153;8154\t6215;8153\t\t\t99;100\t",  # spill: full field count, no id
        "P19525\tP19525\t\t\t4;5\t1",
    )
    table = read_table(path)
    assert table.spill_lines == 1
    assert len(table.rows) == 2
    accessions = [r[table.column("Protein IDs")] for r in table.rows]
    assert accessions == ["P20591", "P19525"], "a spill line reached the rows"


def test_spill_lines_are_reported_not_absorbed(tmp_path: Path) -> None:
    """A file with many is a file to look at. Dropping them silently would hide that."""
    path = _write(tmp_path, "P20591\tP20591\t\t\t1\t0", "1;2\t1;2\t\t\t9\t", "3;4\t3;4\t\t\t9\t")
    assert read_table(path).spill_lines == 2


def test_a_table_without_an_id_column_is_refused(tmp_path: Path) -> None:
    """Without `id` there is no way to tell a spill line from a row, so the guard cannot run.

    Refused rather than silently skipped: a reader that quietly stops guarding is worse than one
    that stops.
    """
    path = tmp_path / "no_id.txt"
    path.write_text("Protein IDs\tReverse\nP20591\t\n")
    with pytest.raises(MaxQuantError) as exc:
        read_table(path)
    assert "`id` column" in str(exc.value)


def test_decoys_and_contaminants_are_dropped(tmp_path: Path) -> None:
    """`ARCHITECTURE.md` §3 lists this first among the adapter's responsibilities."""
    path = _write(
        tmp_path,
        "P20591\tP20591\t\t\t1\t0",
        "REV__X\tREV__X\t+\t\t2\t1",
        "CON__Y\tCON__Y\t\t+\t3\t2",
    )
    table = read_table(path)
    kept = drop_decoys_and_contaminants(table)
    assert len(table.rows) == 3
    assert [r[table.column("Protein IDs")] for r in kept] == ["P20591"]


def test_column_lookup_names_what_it_looked_for(tmp_path: Path) -> None:
    """A renamed column must fail loudly with the alternatives, not return the wrong index."""
    table = read_table(_write(tmp_path, "P20591\tP20591\t\t\t1\t0"))
    assert table.column("Majority protein IDs", "Protein IDs") == 1  # first present wins
    with pytest.raises(MaxQuantError) as exc:
        table.column("Leading proteins")
    assert "Leading proteins" in str(exc.value)
