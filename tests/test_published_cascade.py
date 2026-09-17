"""The published-claim cascade (`bzk/published_cascade.py`, `tests/fixtures/pxd018299_published_cascade.json`).

**Structure and the load-bearing figures, not every number.** The fixture records what one run
computed; these tests assert that every published row sits at exactly one stage, that the stages
account for all 798 with nothing left over, and the handful of figures a write-up would quote —
recall, the significance split, the control partition sizes and the measured-WT partition's
closeness to zero. The partition *means* are not pinned: they are differences of values the
publication rounded to four decimals, so any assertion finer than the bound below would be
asserting rounding.

**All offline.** The module reads the fixture and nothing else, and one test holds it to that by
reading its imports — a cascade that quietly started opening the deposit would still pass every
figure here while no longer being re-derivable from a clone.
"""

from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from bzk import published_cascade
from bzk.published_cascade import (
    RECOVERED,
    STAGES,
    CascadeFixtureError,
    cascade,
    control_partitions,
    load,
    outcome,
    recovered,
    significance_split,
)


def _rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = load()["rows"]
    return rows


def test_the_stages_account_for_every_published_row_with_no_residual() -> None:
    rows = _rows()
    assert len(rows) == 798
    steps = cascade(rows)
    lost = sum(step.lost for step in steps)
    assert lost + recovered(rows) == 798, f"residual {798 - lost - recovered(rows)}"
    # The cascade's own running count must land where the recovered count does.
    assert steps[-1].surviving == 512


def test_recall_is_512_of_798() -> None:
    assert recovered(_rows()) == 512


def test_the_significance_split_is_179_14_44() -> None:
    assert significance_split(_rows()) == {"p_value": 179, "fold_change": 14, "both": 44}


def test_every_row_ends_at_exactly_one_stage() -> None:
    """One outcome per row, from a closed set, and each S1 row appears once."""
    rows = _rows()
    ends = [outcome(row) for row in rows]
    assert set(ends) <= {*STAGES, RECOVERED}
    numbers = [row["row"] for row in rows]
    assert len(set(numbers)) == 798, "an S1 row appears twice"
    assert min(numbers) == 3 and max(numbers) == 800, "S1 data rows are Excel rows 3-800"
    for row, end in zip(rows, ends, strict=True):
        # A row reaching the test carries the platform's statistics; one lost earlier carries none.
        reached = end in (RECOVERED, "significance")
        assert (row["platform_log2fc"] is not None) is reached, row["row"]


@pytest.mark.parametrize(
    "row",
    [
        {"row": 1, "lost_at": None, "loss_reason": "p_value"},
        {"row": 2, "lost_at": "nowhere", "loss_reason": None},
        {"row": 3, "lost_at": "significance", "loss_reason": "presence_rule"},
    ],
)
def test_a_contradictory_row_is_refused(row: dict[str, Any]) -> None:
    """The guard behind "exactly one stage": a row that could be read two ways is not read."""
    with pytest.raises(CascadeFixtureError):
        outcome(row)


def test_the_control_partitions_have_sizes_39_16_72_622() -> None:
    assert {k: d.n for k, d in control_partitions(_rows()).items()} == {0: 39, 1: 16, 2: 72, 3: 622}


def test_the_measured_wt_partition_differs_from_the_platform_by_almost_nothing() -> None:
    """Rows with no published WT cell below 21: the mean absolute difference is below 0.01.

    The bound, not the value. The fixture's differences are of four-decimal published cells, and
    one row in this partition (PKM K270) differs by about 0.29 on its own.
    """
    assert control_partitions(_rows())[0].mean_abs < 0.01


def test_the_summary_block_is_what_the_rows_say() -> None:
    """The summary a reader quotes and the rows the module reads are two stored surfaces.

    Either can be hand-edited without the other, and the module's stage definitions can move
    without the fixture being regenerated; any of the three makes this fail.
    """
    fixture = load()
    rows = fixture["rows"]
    derived = {
        "published_rows": len(rows),
        "lost": {step.stage: step.lost for step in cascade(rows)},
        "significance_split": significance_split(rows),
        "recovered": recovered(rows),
        "recall": recovered(rows) / len(rows),
    }
    assert fixture["summary"] == derived


def test_generated_under_records_when_where_and_under_which_network() -> None:
    """The fields `pxd018299_refusals.json` lacks, which is what made its run incomparable."""
    under = load()["generated_under"]
    stamp = datetime.fromisoformat(under["generated_at"])
    offset = stamp.utcoffset()
    assert offset is not None and offset.total_seconds() == 0, "generated_at must be UTC"
    assert len(under["commit"]) == 40
    assert isinstance(under["working_tree_clean"], bool)
    assert under["published_side_keying"]["online"] is True
    assert isinstance(under["published_side_keying"]["live_uniprot_requests"], int)
    assert under["deposit_side_run"]["online"] is False


def test_the_module_reads_nothing_but_the_fixture() -> None:
    """No reader for the deposit, the store, the graph or the network may be imported."""
    tree = ast.parse(Path(published_cascade.__file__).read_text())
    imported = {
        alias.name.split(".")[0] if isinstance(node, ast.Import) else str(node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    assert imported <= {
        "__future__",
        "json",
        "math",
        "statistics",
        "dataclasses",
        "pathlib",
        "typing",
    }


def test_the_report_states_the_cascade_and_its_bound() -> None:
    lines = published_cascade._report(load())
    assert any("recovered 512 of 798" in line for line in lines)
    assert any("Recall only" in line for line in lines)
