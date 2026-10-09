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

from bzk.adapters.perseus import PerseusAdapter
from bzk.curation.loader import load_path
from bzk.ontology.invariants import NODE_TYPE_KEY, InvariantError

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATION = REPO_ROOT / "data" / "curation" / "curation_PXD055843.json"
ANALYSIS = REPO_ROOT / "data" / "curation" / "analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json"


def _synthetic_export(path: Path, suffix: str) -> Path:
    """A workbook of the deposit's shape. Reviewer-supplied shape; the values are this file's own.

    Row 1 carries a merged `Set` qualifier over each set's columns, row 2 their condition strings,
    row 3 an acquisition path for each and the Perseus type-stamped names for the rest.

    **The quantitative columns are the record's own arm columns since 2026-10-09** (ADR-0038
    D6-revised (b)): the adapter now proves its binding by recomputing each tested row's Difference
    from the arm samples' columns, so the workbook carries exactly the six headers the curation
    record's `numerator_samples` / `denominator_samples` name — split on the composition's own
    separator and rebuilt across the three header rows, never retyped. Each row's numerator values
    are its denominator values plus its Difference. The last row is Perseus' untested placeholder
    (ADR-0038 E2–E4) and carries arm values that rule (b) would refuse, so it parses only because
    rule (a) excuses it first.
    """
    import openpyxl

    entry = json.loads(CURATION.read_text())["contrasts_of_interest"][0]
    numerator = [key.split(" | ") for key in entry["numerator_samples"]]
    denominator = [key.split(" | ") for key in entry["denominator_samples"]]
    columns = [col for pair in zip(numerator, denominator, strict=True) for col in pair]
    stamped = [
        "T: Protein.Group",
        "T: Protein.Ids",
        f"N: Student's T-test Difference {suffix}",
        f"N: -Log Student's T-test p-value {suffix}",
        f"N: Student's T-test q-value {suffix}",
        f"N: Student's T-test Test statistic {suffix}",
    ]
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append([c[0] for c in columns] + [None] * len(stamped))
    sheet.append([c[1] for c in columns] + [None] * len(stamped))
    sheet.append([c[2] for c in columns] + stamped)

    def arms(denominator_values: list[float], difference: float) -> list[float]:
        return [v for d in denominator_values for v in (d + difference, d)]

    for values, identity, statistics in (
        (arms([20.0, 21.0, 22.0], 3.42), ["P20591", "P20591"], [3.42, 4.51, 0.0012, 6.1]),
        (arms([23.0, 24.0, 25.0], 4.95), ["P19525", "P19525;Q9NRZ9"], [4.95, 5.02, 0.0009, 7.0]),
        (arms([26.0, 27.0, 28.0], -1.87), ["O43593", "O43593"], [-1.87, 2.30, 0.0210, -3.1]),
        ([30.0, 20.0, 30.0, 20.0, 30.0, 20.0], ["P05161", "P05161"], [0, 0, 1, 0]),
    ):
        sheet.append([*values, *identity, *statistics])
    for first in range(0, len(columns), 2):
        sheet.merge_cells(start_row=1, start_column=first + 1, end_row=1, end_column=first + 2)
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
    # The loader's node since ADR-0029 item 3 (2026-10-03): the arms arrive inside it, anchored.
    assert contrast.contrast["numerator"] == "siUSP24 (+ IFN-B)"
    assert contrast.contrast["denominator"] == "siC (+IFN-B)"
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


def test_the_proof_is_readable_when_I15_refuses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """ADR-0038 D6-revised on the record as it stands, which I15 refuses by design.

    The proof is set before anything is emitted, so it survives the refusal that follows — which is
    what lets `main` print the binding's outcome for the one file it exists for, and what §5 of
    prompt 31 reads off S1 without a graph write. Asserted on the synthetic workbook: three tested
    rows, one untested.
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    adapter = PerseusAdapter(declaration, [contrast])
    with pytest.raises(InvariantError, match="I15"):
        pxd055843_perseus.build(book, load_path(CURATION), declaration, contrast, adapter=adapter)
    assert adapter.report is None, "a refused parse must not leave a report of what it emitted"
    assert adapter.proof is not None
    found = adapter.proof[str(contrast.contrast["id"])]
    assert (found.rows_tested, found.rows_untested) == (3, 1)
    pxd055843_perseus._print_proof(adapter)
    printed = capsys.readouterr().out
    assert "binding accepted — 3 tested row(s)" in printed
    assert "1 untested row(s), no result minted for them" in printed


def test_the_untested_row_mints_no_result_on_the_change_set_path(tmp_path: Path) -> None:
    """Rule (c) through the source module, with the seed this test supplies: four observations,
    three results, and the count the `Analysis` carries."""
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    seeded = replace(
        declaration,
        imputation=dict(declaration.imputation)
        | {"seed": 0, "downshift_sd": 1.8, "width_sd": 0.3, "scope": "whole_matrix"},
    )
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    parsed = pxd055843_perseus.build(book, load_path(CURATION), seeded, contrast)
    count = {
        label: sum(1 for n in parsed.nodes if n[NODE_TYPE_KEY] == label)
        for label in ("ProteinObservation", "DifferentialResult")
    }
    assert count == {"ProteinObservation": 4, "DifferentialResult": 3}
    analysis_node = next(n for n in parsed.nodes if n[NODE_TYPE_KEY] == "Analysis")
    assert json.loads(str(analysis_node["rows_untested_json"])) == {str(contrast.contrast["id"]): 1}


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

    **The assertion is unchanged and its reason is not** (2026-09-09). It held because
    `bzk/adapters/perseus.py` retained no per-sample values from any file; that adapter now retains
    them where the declared imputation method is `none`, and this run still gets none because *this
    record* declares `downshifted_normal`. The seed supplied below is what I15 wants and it does not
    change the answer — an export is the far side of the draw, so there is no pre-imputation matrix
    for the mask to be reconstructed against.

    So the reason is asserted alongside the emptiness. Without it this test would keep passing on
    the day the withholding started coming from a placement failure instead, which is a different
    fact about a different defect.
    """
    from bzk.sources import pxd055843_perseus

    declaration, contrast = pxd055843_perseus.declared()
    seeded = replace(declaration, imputation=dict(declaration.imputation) | {"seed": 0})
    book = _synthetic_export(tmp_path / "export.xlsx", contrast.column_suffix)
    adapter = PerseusAdapter(seeded, [contrast])
    parsed = pxd055843_perseus.build(book, load_path(CURATION), seeded, contrast, adapter=adapter)
    assert not parsed.cells
    report = adapter.report
    assert report is not None
    because = report.withheld_because
    assert because is not None
    assert "downshifted_normal" in because
    assert "A seed does not lift this" in because


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
