"""The DuckDB columnar layer — where I11's per-sample values are retained (ADR-0004, ADR-0013).

`ONTOLOGY.md` §2 draws the boundary: the graph holds identity, relationships and provenance, and
*"if a value is one-per-entity, it is a graph property. If it is one-per-entity-per-sample, it is
columnar."* This module is the columnar side of that line, and nothing else writes it.

**The row is `(observation_id, sample_id, quantity, value)` and the join key is the observation
id**, per ADR-0004. Not `quant_ref`: that column names the *table*, so an observation can be located
without the reader knowing the label→table map, and `NULL` there means no values were retained,
which is I11's violation state readable from the graph alone.

**Two tables, because `ARCHITECTURE.md` §2 names two matrices** — site × sample and protein × sample.
A single table would need a grain discriminator whose only content is the label already fixed by the
observation id's identity tuple.

**`quantity` is in the primary key** because one observation legitimately has more than one
per-sample vector: PXD018299 carries `Intensity <sample>` and `Ratio mod/base <sample>` over the same
12 samples, and `ROADMAP.md` § Measured findings records both as usable at this grain.

**Values are measured values and nulls, never imputed** (ADR-0013). `ARCHITECTURE.md` § *Imputation
is part of the statistics layer, not the adapter* settles that for this writer, which is the adapter.
A null cell here is a cell the search engine did not report; what to do about it is an analysis
decision that must be recorded, and the mask stays reconstructible because I15 makes the
`Imputation` seed mandatory.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import duckdb
import polars as pl

#: The two tables, keyed by the observation label whose values they hold. This map is what
#: `quant_ref` is drawn from, so a label gaining a table is a change in one place.
TABLES: dict[str, str] = {
    "SiteObservation": "site_values",
    "ProteinObservation": "protein_values",
}

#: Kept identical across the two tables deliberately: the row shape is ADR-0004's contract, and a
#: third grain is a third table rather than a redesign. `value` is nullable — a null cell is a
#: measurement the search did not report, which is the whole point of storing pre-imputation.
_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
  observation_id VARCHAR NOT NULL,
  sample_id      VARCHAR NOT NULL,
  quantity       VARCHAR NOT NULL,
  value          DOUBLE,
  PRIMARY KEY (observation_id, sample_id, quantity)
);
"""


@dataclass(frozen=True)
class Cell:
    """One per-observation-per-sample measurement, or the absence of one.

    `value=None` is a cell the search engine reported nothing for. It is stored rather than skipped,
    because "not measured" and "not ingested" are different states and I11 is about being able to
    tell them apart later — a row that is absent cannot say which it was.
    """

    observation_id: str
    sample_id: str
    quantity: str
    value: float | None


@dataclass(frozen=True)
class WriteReport:
    """What a matrix write issued, named for what it counts (the `store.py` lesson, 2026-08-08).

    `cells_staged` is the length of the staged sequence, not the number of rows the store gained —
    the writer uses `INSERT OR REPLACE`, so re-ingesting a deposit rewrites rather than accumulates.
    """

    table: str
    cells_staged: int


def path_for(home: Path) -> Path:
    return home / "quant.duckdb"


def connect(home: Path) -> duckdb.DuckDBPyConnection:
    """Open (creating if absent) the store and ensure both tables exist."""
    path = path_for(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(path))
    for table in TABLES.values():
        connection.execute(_DDL.format(table=table))
    return connection


def quant_ref(label: str) -> str:
    """The value `quant_ref` takes on a node of this label (ADR-0004).

    Raises rather than returning `None` for an unknown label: a silent `None` would be
    indistinguishable from "no values retained", which is the one thing that column has to mean.
    """
    try:
        return TABLES[label]
    except KeyError:
        raise KeyError(
            f"{label!r} has no columnar table. `quant_ref` must not be guessed — a wrong table name "
            "is a dangling reference, and `None` already means the I11 violation state"
        ) from None


def write_cells(
    connection: duckdb.DuckDBPyConnection, label: str, cells: Sequence[Cell]
) -> WriteReport:
    """Write one grain's cells. `INSERT OR REPLACE`, so a re-ingested deposit converges (I9).

    **One set-at-a-time statement over a registered frame, not `executemany`.** The first version
    used `executemany` and cited §8's per-statement graph write as the reason to batch — then cost
    the same thing: **165.2 s for 48,696 cells, 3.4 ms each**, taking a 69.0 s rebuild to 235.2 s.
    `executemany` is still one round trip per row against the primary key's index. Registering the
    batch as a relation and inserting from it in a single statement is the actual bulk path, and it
    keeps `INSERT OR REPLACE`'s semantics exactly rather than trading them for speed.
    """
    table = quant_ref(label)
    if cells:
        incoming = pl.DataFrame(  # noqa: F841 — referenced by name in the SQL below
            {
                "observation_id": [c.observation_id for c in cells],
                "sample_id": [c.sample_id for c in cells],
                "quantity": [c.quantity for c in cells],
                "value": [c.value for c in cells],
            },
            schema={
                "observation_id": pl.Utf8,
                "sample_id": pl.Utf8,
                "quantity": pl.Utf8,
                "value": pl.Float64,
            },
        )
        connection.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM incoming")
    return WriteReport(table=table, cells_staged=len(cells))


def read_cells(
    connection: duckdb.DuckDBPyConnection, label: str, observation_id: str
) -> list[Cell]:
    """Every retained cell for one observation, sample-ordered. The read half I11 exists for."""
    table = quant_ref(label)
    rows = connection.execute(
        f"SELECT observation_id, sample_id, quantity, value FROM {table} "
        "WHERE observation_id = ? ORDER BY quantity, sample_id",
        [observation_id],
    ).fetchall()
    return [Cell(*row) for row in rows]


def count_cells(connection: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Rows per table. Only non-empty tables appear, matching `store.count_nodes`' convention."""
    counts = {}
    for table in TABLES.values():
        row = connection.execute(f"SELECT count(*) FROM {table}").fetchone()
        # `fetchone` is Optional by signature; a scalar aggregate always returns a row, and
        # asserting that is better than a cast, which would hide it if it ever did not.
        assert row is not None
        n = int(row[0])
        if n:
            counts[table] = n
    return counts


def digest_rows(connection: duckdb.DuckDBPyConnection) -> str:
    """A stable digest over every stored cell, for the regenerability check (`OPERATIONS.md` §1).

    Over *content*, in a fixed order, rather than over the file: a DuckDB file carries its own
    metadata and free-space layout, so byte equality is the wrong question to ask of it. What
    `OPERATIONS.md` §1's "regenerable" claim needs is that a rebuild reproduces the same values.
    """
    import hashlib

    digest = hashlib.sha256()
    for table in sorted(TABLES.values()):
        rows: Iterable[tuple[object, ...]] = connection.execute(
            f"SELECT observation_id, sample_id, quantity, value FROM {table} "
            "ORDER BY observation_id, sample_id, quantity"
        ).fetchall()
        digest.update(table.encode("utf-8"))
        for row in rows:
            digest.update(repr(row).encode("utf-8"))
    return "sha256:" + digest.hexdigest()
