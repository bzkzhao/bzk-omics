"""`bzk/sources/pxd055843_perseus.py` — the ingestion entry point for PXD055843's Perseus export.

**The module cannot be run against the real deposit here and neither can these tests.** Those bytes
are in no content store in this container, and no `.xlsx` is in the tree. So the change-set path is
driven over a **synthetic** workbook built in `tmp_path` with the deposit's shape — three header
rows, a merged qualifier spanning the quantitative columns, and stamped statistics and identifier
columns — and the deposit-absent path is exercised as itself.

The shape being modelled is **reviewer-supplied and not re-derivable in this container**; it is
labelled so wherever it is stated. The real record's values, by contrast, are read from
`data/curation/`, which is in the tree.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from bzk.curation.loader import load_path
from bzk.ontology.invariants import NODE_TYPE_KEY, InvariantError

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD055843.json"
ANALYSIS = REPO_ROOT / "data" / "curation" / "analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json"


def _synthetic_export(path: Path, suffix: str) -> Path:
    """A workbook of the deposit's shape. Reviewer-supplied shape; the values are this file's own.

    Row 1 carries one merged qualifier over the four quantitative columns, row 2 their condition
    strings, row 3 an acquisition path for each and the Perseus type-stamped names for the rest.
    """
    import openpyxl

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    stamped = [
        "T: Protein.Group",
        "T: Protein.Ids",
        f"N: Student's T-test Difference {suffix}",
        f"N: -Log Student's T-test p-value {suffix}",
        f"N: Student's T-test q-value {suffix}",
    ]
    for row in (
        ["Set 1", None, None, None, None, None, None, None, None],
        [
            "siC (+IFN-B)",
            "siUSP24 (+ IFN-B)",
            "siC (-IFN-B)",
            "siUSP24 (-IFN-B)",
            None,
            None,
            None,
            None,
            None,
        ],
        ["/raw/A.d", "/raw/B.d", "/raw/C.d", "/raw/D.d", *stamped],
        [100.0, 200.0, 110.0, 210.0, "P20591", "P20591", 3.42, 4.51, 0.0012],
        [120.0, 220.0, 130.0, 230.0, "P19525", "P19525;Q9NRZ9", 4.95, 5.02, 0.0009],
        [140.0, 240.0, 150.0, 250.0, "O43593", "O43593", -1.87, 2.30, 0.0210],
    ):
        sheet.append(row)
    sheet.merge_cells("A1:D1")
    workbook.save(path)
    return path


def test_the_two_records_name_the_same_bytes() -> None:
    """The analysis record and the curation record are about one file, and both say which.

    A digest that disagreed would mean the analysis was performed on something other than the file
    the curation describes, and every id downstream anchors on `Dataset.content_hash`.
    """
    from bzk.sources import pxd055843_perseus

    analysis: dict[str, Any] = json.loads(ANALYSIS.read_text())
    curation: dict[str, Any] = json.loads(CURATION.read_text())
    assert analysis["content_hash"] == curation["content_hash"]
    assert analysis["file"] == curation["file"]
    assert pxd055843_perseus.ANALYSIS.name == ANALYSIS.name


def test_the_records_values_reach_the_declaration() -> None:
    """What the module declares comes from the two records, not from constants beside the code.

    The anchor module transcribes its parameters and gives a reason — the record is what its run is
    checked *against*, so consuming it would make the comparison circular. This module compares
    nothing; it ingests. So the reason does not reach it and the record is read.
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    assert declaration.quantity == "lfq"
    assert declaration.test == "perseus_s0"
    assert declaration.fdr_method == "permutation"
    assert declaration.external_version == "1.6.2.3"
    assert declaration.parameters_json is None
    assert declaration.imputation["method"] == "downshifted_normal"
    assert declaration.imputation["seed"] is None
    assert contrast.numerator == "siUSP24 (+ IFN-B)"
    assert contrast.denominator == "siC (+IFN-B)"
    assert contrast.column_suffix == pxd055843_perseus.COLUMN_SUFFIX


def test_the_record_as_it_stands_is_refused_by_I15(tmp_path: Path) -> None:
    """The one decision this turn makes, guarded rather than described.

    The methods state that missing values were imputed, and state no seed. I15 refuses a stochastic
    imputation without one. The module does not re-implement that check — a second home for one rule
    — so the refusal arrives from `invariants.validate` inside the parse, before anything is
    written. **Running this module for real needs a seed as much as it needs the bytes.**
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    with pytest.raises(InvariantError) as exc:
        pxd055843_perseus.build(book, load_path(CURATION), declaration, contrast)
    assert "I15" in str(exc.value)
    assert "seed" in str(exc.value)


def test_the_change_set_carries_what_the_adapter_mints(tmp_path: Path) -> None:
    """The change-set path, driven over a synthetic workbook with a seed supplied by this test.

    The seed is **supplied here and nowhere else** — it is not in the record and this test does not
    put it there. Everything else in the declaration comes from `data/curation/`.
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    seeded = replace(
        declaration,
        imputation=dict(declaration.imputation)
        | {"seed": 0, "downshift_sd": 1.8, "width_sd": 0.3, "scope": "whole_matrix"},
    )
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    parsed = pxd055843_perseus.build(book, load_path(CURATION), seeded, contrast)

    labels = {str(node[NODE_TYPE_KEY]) for node in parsed.nodes}
    for label in ("Analysis", "Contrast", "Dataset", "DifferentialResult", "Imputation", "Sample"):
        assert label in labels
    types = {str(edge["type"]) for edge in parsed.edges}
    for edge_type in ("IMPUTATION_FOR", "PRODUCED", "REPORTS_PROTEIN", "WAS_GENERATED_BY"):
        assert edge_type in types

    # `analysis_node`, not `analysis`: the name is bound to the *record* higher up this module, and
    # `tests/test_analysis_record.py` derives what each reader reads off a record by that binding.
    # Spelling both the same made four node fields read as four record reads (2026-09-05).
    analysis_node = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Analysis")
    assert analysis_node["external_version"] == "1.6.2.3"
    assert analysis_node["test"] == "perseus_s0"
    assert analysis_node["fdr_method"] == "permutation"
    assert analysis_node["quantity"] == "lfq"
    assert analysis_node["parameters_observed"] is False


def test_the_change_set_carries_no_per_sample_values(tmp_path: Path) -> None:
    """`ParsedObservations.cells` is empty, so the columnar half of I11 gets nothing from here.

    A carried finding, not this turn's to repair — recorded as a test so what the graph will *not*
    hold is checkable rather than only stated. The eighteen quantitative columns of the real export
    reach no store through this path.
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    seeded = replace(declaration, imputation=dict(declaration.imputation) | {"seed": 0})
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    parsed = pxd055843_perseus.build(book, load_path(CURATION), seeded, contrast)
    assert not parsed.cells


def test_an_absent_deposit_refuses_and_names_what_it_looked_for(tmp_path: Path) -> None:
    """The path this turn can exercise for real: the bytes are in no content store here.

    Named rather than merely refused — an operator meeting this needs the digest to look for and the
    command that would fetch it, not the word *missing*.
    """
    from bzk.sources import pxd055843_perseus

    with pytest.raises(SystemExit) as exc:
        pxd055843_perseus.locate(home=tmp_path / "empty-home")
    message = str(exc.value)
    assert "a6e12e555709612590d1a1d2f499bcd416d2ee69d6e28cb2e167a162fe5c95c2" in message
    assert "Supplementary_Data_S1_TP.xlsx" in message
