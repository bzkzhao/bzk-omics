"""MaxQuant table reading — the guarded entry point every MaxQuant reader uses.

**The adapter itself is weeks 5–6 and is not written.** What is here is the *reader*, because one
of its guards was found before the adapter existed and a defect found early should not wait for the
module that would inherit it. `bzk/sources/protein_groups.py` already reads a MaxQuant table and
must go through this rather than keeping its own copy.

Two hazards, both of the class `HANDOFF.md` §6 catalogues — code that runs, prints cleanly and is
wrong.

**Spill lines.** MaxQuant writes long semicolon-separated numeric lists in its `*_IDs` columns
(`Peptide IDs`, `Evidence IDs`, `MS/MS IDs`), and some of them spill onto their own physical lines.
Measured on `HAP1_USP18KO_proteinGroups.txt`: **six** of them, each carrying exactly 147 tabs — so
the field count matches the header, every structural check passes, and `pandas` reads them as data
rows whose accession column then holds numbers like `6215;8153;8154`. Nothing raises. The effect on
that file was to inflate the largest apparent protein group from **33 members to 5,090** while
moving the headline multi-mapping percentage by 0.1, which is exactly why no summary statistic
would have caught it.

The test is the file's own bookkeeping, not a heuristic: MaxQuant's `id` column is a contiguous
0-based row number, so **a line without one is not a row**. On that file `id` runs 0..4,981 across
4,988 physical lines, and the six without one are the spill. A heuristic — "the accession column
looks numeric", "the row is mostly empty" — would be guessing at the same answer the file states.

**CRLF.** The deposit is CRLF throughout (`ARCHITECTURE.md` §3). The file is read as bytes and
decoded explicitly, then split with `splitlines()`, for the reason `bzk/adapters/perseus.py`
records: reading text and relying on universal-newline translation works, but makes the defence an
implicit default a later `newline=''` could switch off with no test noticing.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path


class MaxQuantError(ValueError):
    """A MaxQuant table cannot be read as given."""


@dataclass(frozen=True)
class MaxQuantTable:
    """One MaxQuant table: its header, its real rows, and what was discarded getting there."""

    header: list[str]
    rows: list[list[str]]
    #: Physical lines dropped because they carried no `id` — spill, not rows. Reported rather than
    #: silently absorbed: a file where this is large is a file to look at, not one to trust.
    spill_lines: int

    def column(self, *names: str) -> int:
        """Index of the first of `names` present, or an error naming what was looked for."""
        for name in names:
            if name in self.header:
                return self.header.index(name)
        raise MaxQuantError(f"none of {list(names)} in this table; found {sorted(self.header)}")


def read_table(path: Path) -> MaxQuantTable:
    """Read a MaxQuant tab-separated table, dropping spill lines. See the module docstring."""
    csv.field_size_limit(sys.maxsize)
    lines = path.read_bytes().decode("utf-8", errors="replace").splitlines()
    if not lines:
        raise MaxQuantError(f"{path} is empty")
    reader = list(csv.reader(lines, delimiter="\t"))
    header = reader[0]
    if "id" not in header:
        raise MaxQuantError(
            f"{path} has no `id` column, so spill lines cannot be told from rows. Every MaxQuant "
            "table carries one; a file without it is not one, or has been edited."
        )
    id_index = header.index("id")
    rows = [r for r in reader[1:] if len(r) > id_index and r[id_index].isdigit()]
    return MaxQuantTable(header=header, rows=rows, spill_lines=len(reader) - 1 - len(rows))


def drop_decoys_and_contaminants(table: MaxQuantTable) -> list[list[str]]:
    """`Reverse` and `Potential contaminant` removed — mandatory before anything else.

    `ARCHITECTURE.md` §3 lists this first among the adapter's responsibilities, and
    `ROADMAP.md` § Measured findings records the 2,341 → 2,298 it makes on the site table.
    """
    reverse = table.header.index("Reverse") if "Reverse" in table.header else None
    contaminant = (
        table.header.index("Potential contaminant")
        if "Potential contaminant" in table.header
        else None
    )
    return [
        row
        for row in table.rows
        if (reverse is None or row[reverse] != "+")
        and (contaminant is None or row[contaminant] != "+")
    ]
