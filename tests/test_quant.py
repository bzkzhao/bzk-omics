"""`bzk/quant/` — I11's columnar half (ADR-0004, ADR-0013).

The properties worth pinning are the ones that make I11 *true* rather than merely implemented: that
a value written is the value read back, that a cell the search did not report stays distinguishable
from a cell nobody ingested, and that a re-ingested deposit converges instead of accumulating.

Reading a value back is the whole point. I11 exists so an alternative test is *recomputable from
stored values without re-ingestion*, and a layer that writes without a demonstrated read is a claim
rather than a capability.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bzk.adapters.base import SampleMapping
from bzk.adapters.maxquant_sites import MaxQuantSiteError, _sample_columns
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.quant import store as quant

CELLS = [
    quant.Cell("bzk:obs1", "bzk:s1", "intensity_multiplicity_summed", 150520.0),
    quant.Cell("bzk:obs1", "bzk:s2", "intensity_multiplicity_summed", 0.0),
    quant.Cell("bzk:obs1", "bzk:s1", "ratio_mod_base", None),
    quant.Cell("bzk:obs2", "bzk:s1", "intensity_multiplicity_summed", 42.5),
]


def test_connect_creates_both_tables_even_with_nothing_to_write(tmp_path: Path) -> None:
    """An absent file and an empty one are different states, and `OPERATIONS.md` §1 calls this
    store regenerable, which presumes it is generated. A rebuild that ingests no deposit must still
    leave a store that says "nothing was retained" rather than one that says nothing at all."""
    connection = quant.connect(tmp_path)
    assert quant.path_for(tmp_path).exists()
    assert quant.count_cells(connection) == {}, "empty tables report as absent, not as zero"
    for table in quant.TABLES.values():
        connection.execute(f"SELECT * FROM {table}")  # raises if the table is missing
    connection.close()


def test_a_value_written_is_the_value_read_back(tmp_path: Path) -> None:
    """I11's actual obligation. Everything else here guards the edges of this one sentence."""
    connection = quant.connect(tmp_path)
    quant.write_cells(connection, "SiteObservation", CELLS)
    back = quant.read_cells(connection, "SiteObservation", "bzk:obs1")
    assert back == [
        quant.Cell("bzk:obs1", "bzk:s1", "intensity_multiplicity_summed", 150520.0),
        quant.Cell("bzk:obs1", "bzk:s2", "intensity_multiplicity_summed", 0.0),
        quant.Cell("bzk:obs1", "bzk:s1", "ratio_mod_base", None),
    ]
    connection.close()


def test_an_unreported_cell_stays_distinguishable_from_an_uningested_one(tmp_path: Path) -> None:
    """`value IS NULL` and *no row* are different claims, which is why nulls are stored.

    A layer that skipped nulls would make "the search reported nothing here" indistinguishable from
    "this observation was never ingested", and I11 exists so that distinction survives to whatever
    test is run later.
    """
    connection = quant.connect(tmp_path)
    quant.write_cells(connection, "SiteObservation", CELLS)
    reported_nothing = quant.read_cells(connection, "SiteObservation", "bzk:obs1")
    never_ingested = quant.read_cells(connection, "SiteObservation", "bzk:obs99")
    assert [c for c in reported_nothing if c.value is None], "a null cell is a row"
    assert never_ingested == [], "an uningested observation has no rows at all"
    connection.close()


def test_a_zero_is_kept_as_a_zero(tmp_path: Path) -> None:
    """MaxQuant writes 0 for an undetected intensity. Reading that as absence is an interpretation
    the adapter has no licence to make (I19); it is the statistics layer's, and must be recorded."""
    connection = quant.connect(tmp_path)
    quant.write_cells(connection, "SiteObservation", CELLS)
    zero = [c for c in quant.read_cells(connection, "SiteObservation", "bzk:obs1") if c.value == 0]
    assert len(zero) == 1 and zero[0].value == 0.0
    connection.close()


def test_re_ingesting_the_same_cells_converges(tmp_path: Path) -> None:
    """I9 at the columnar grain. `INSERT OR REPLACE` on `(observation, sample, quantity)`."""
    connection = quant.connect(tmp_path)
    quant.write_cells(connection, "SiteObservation", CELLS)
    first = quant.count_cells(connection)
    quant.write_cells(connection, "SiteObservation", CELLS)
    assert quant.count_cells(connection) == first == {"site_values": 4}
    connection.close()


def test_the_quantity_is_part_of_the_key_not_a_label(tmp_path: Path) -> None:
    """ADR-0004 decision 4, exercised by the case that justified it: one observation, one sample,
    two quantities. Without `quantity` in the key the second would overwrite the first."""
    connection = quant.connect(tmp_path)
    quant.write_cells(
        connection,
        "SiteObservation",
        [
            quant.Cell("bzk:o", "bzk:s", "intensity_multiplicity_summed", 1.0),
            quant.Cell("bzk:o", "bzk:s", "ratio_mod_base", 2.0),
        ],
    )
    assert [c.value for c in quant.read_cells(connection, "SiteObservation", "bzk:o")] == [1.0, 2.0]
    connection.close()


def test_the_two_grains_are_separate_tables(tmp_path: Path) -> None:
    connection = quant.connect(tmp_path)
    quant.write_cells(connection, "SiteObservation", CELLS[:1])
    quant.write_cells(
        connection,
        "ProteinObservation",
        [quant.Cell("bzk:p1", "bzk:s1", "intensity_multiplicity_summed", 9.0)],
    )
    assert quant.count_cells(connection) == {"site_values": 1, "protein_values": 1}
    assert quant.read_cells(connection, "ProteinObservation", "bzk:obs1") == []
    connection.close()


def test_quant_ref_refuses_a_label_with_no_table() -> None:
    """A guessed table name is a dangling reference, and `None` already means the violation state,
    so neither is available as a fallback (ADR-0004)."""
    assert quant.quant_ref("SiteObservation") == "site_values"
    assert quant.quant_ref("ProteinObservation") == "protein_values"
    with pytest.raises(KeyError, match="no columnar table"):
        quant.quant_ref("PeptideObservation")


def test_the_row_digest_is_over_content_not_the_file(tmp_path: Path) -> None:
    """What `OPERATIONS.md` §1's regenerability claim needs. Measured on the real deposit: two
    rebuilds are **value-for-value** identical and **not** byte-for-byte, because a DuckDB file
    carries metadata and free-space layout that byte equality would compare as well."""
    a, b = tmp_path / "a", tmp_path / "b"
    for home in (a, b):
        connection = quant.connect(home)
        quant.write_cells(connection, "SiteObservation", CELLS)
        connection.close()
    first, second = quant.connect(a), quant.connect(b)
    assert quant.digest_rows(first) == quant.digest_rows(second)
    quant.write_cells(second, "SiteObservation", [quant.Cell("bzk:x", "bzk:s", "lfq", 1.0)])
    assert quant.digest_rows(first) != quant.digest_rows(second), "a changed cell changes it"
    first.close()
    second.close()


# ── The adapter side: what reaches the store, and what it refuses ───────────────────────────────


def _descriptor(mapping_key: str) -> SampleMapping:
    return SampleMapping(
        curation_analysis_id="bzk:curation1",
        samples=[{NODE_TYPE_KEY: "Sample", "id": "bzk:s1", "mapping_key": mapping_key}],
    )


def test_a_mapping_key_naming_no_recognised_column_is_refused() -> None:
    """Silently skipping the sample would drop it from the matrix while leaving its `Sample` node
    in the graph — I11 unmet in a shape nothing would notice."""
    columns = {"Intensity WT_1": 0, "Ratio mod/base WT_1": 1}
    assert _sample_columns(_descriptor("Intensity WT_1"), columns) == [("bzk:s1", "WT_1")]
    with pytest.raises(MaxQuantSiteError, match="names no column this adapter recognises"):
        _sample_columns(_descriptor("LFQ intensity WT_1"), columns)
    with pytest.raises(MaxQuantSiteError, match="matches no quantitative column"):
        _sample_columns(_descriptor("Intensity WT_9"), columns)
