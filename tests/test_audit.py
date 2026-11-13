"""`bzk/audit.py` — the nine-stage report is derived from fixtures, and `--live` says what it did.

**Offline throughout.** The live paths are driven with a stubbed `pxd018299_h10.main` (the module's
own tests drive the real one over synthetic bytes) and, for the graph read, with a small Kùzu graph
written through `store.write_change_set` — the same builder `tests/test_query.py` uses, so the
Cypher is exercised against a shape a producer could emit rather than against hand-written rows.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import kuzu
import pytest

from bzk import audit
from bzk.provenance import raw_store
from bzk.sources import pxd018299_h10 as h10
from bzk.sources import pxd026748_reconstruction as reconstruction
from bzk.sources.pride import PXD018299_SITES
from bzk.sources.protein_groups import SUPP_DATA_1

FIXTURES = Path(__file__).parent / "fixtures"
H10_FILE = "pxd018299_h10_attempt3.json"


def _committed() -> dict[str, Any]:
    return json.loads((FIXTURES / H10_FILE).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


# ── The registered default cell is a mirror, so it has a guard ──────────────────────────────────


def test_the_default_cell_mirrors_the_registered_constants() -> None:
    assert audit.DEFAULT_CELL == (
        reconstruction.DEFAULT_WIDTH_SD,
        reconstruction.DEFAULT_DOWNSHIFT_SD,
        reconstruction.DEFAULT_SCOPE,
    )


# ── The comparison `--live` reports ──────────────────────────────────────────────────────────────


def test_identical_documents_do_not_differ() -> None:
    doc = {"a": [1, 2.5, {"b": "x"}], "c": None}
    assert audit._diff(doc, json.loads(json.dumps(doc))) == []


def test_a_float_within_the_tolerance_is_the_same_and_one_outside_it_is_not() -> None:
    assert audit._diff({"x": 1.0}, {"x": 1.0 + 1e-12}) == []
    assert audit._diff({"x": 1.0}, {"x": 1.001}) == ["x: 1.0 -> 1.001"]


def test_every_kind_of_difference_names_its_path() -> None:
    assert audit._diff({"a": 1}, {"a": 2}) == ["a: 1 -> 2"]
    assert audit._diff({"a": 1}, {}) == ["a: present -> absent"]
    assert audit._diff({}, {"a": 1}) == ["a: absent -> present"]
    assert audit._diff({"a": [1, 2]}, {"a": [1]}) == ["a: length 2 -> 1"]
    assert audit._diff({"a": [1, {"b": 1}]}, {"a": [1, {"b": 2}]}) == ["a[1].b: 1 -> 2"]


def test_a_bool_is_not_an_int_and_a_float_is_not_an_int() -> None:
    """`True == 1` and `1 == 1.0` in Python; a regenerated fixture that changed type has changed."""
    assert audit._diff({"a": True}, {"a": 1}) == ["a: True -> 1"]
    assert audit._diff({"a": 1}, {"a": 1.0}) == ["a: 1 -> 1.0"]


# ── Regenerating attempt 3 ───────────────────────────────────────────────────────────────────────


class _StubMain:
    """Stands in for `h10.main`: records what it was given and writes a chosen fixture."""

    def __init__(self, document: dict[str, Any] | None, *, code: int = 0) -> None:
        self.document = document
        self.code = code
        self.kwargs: dict[str, Any] = {}
        self.had_attempt_2 = False

    def __call__(self, **kwargs: Any) -> int:
        self.kwargs = kwargs
        scratch: Path = kwargs["fixtures_dir"]
        self.had_attempt_2 = (scratch / h10.fixture_name_for(2)).exists()
        if self.document is not None:
            (scratch / h10.fixture_name_for(3)).write_text(json.dumps(self.document))
        return self.code


def test_the_committed_fixture_is_what_a_faithful_regeneration_reproduces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    document = _committed()
    document["generated_under"] = {"generated_at": "later", "commit": "other"}
    document["runtime_seconds"] = 999.0
    stub = _StubMain(document)
    monkeypatch.setattr(h10, "main", stub)
    before = sorted(p.name for p in FIXTURES.iterdir())
    _, report = audit._regenerate_attempt3(tmp_path / "home", tmp_path / "work")
    assert report["reproduced"] is True
    assert report["differences"] == 0
    assert stub.had_attempt_2 is True
    assert stub.kwargs["attempt"] == 3
    assert sorted(p.name for p in FIXTURES.iterdir()) == before


def test_a_regeneration_that_differs_is_reported_with_its_path_and_not_adjusted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    document = _committed()
    document["readouts"]["primary"]["readout_a"]["default_cell"]["supported"] += 1
    monkeypatch.setattr(h10, "main", _StubMain(document))
    regenerated, report = audit._regenerate_attempt3(tmp_path / "home", tmp_path / "work")
    assert report["reproduced"] is False
    assert report["differences"] == 1
    assert report["first_differences"][0].startswith("readouts.primary.readout_a.default_cell")
    assert (
        regenerated["readouts"]["primary"]["readout_a"]["default_cell"]["supported"]
        == (document["readouts"]["primary"]["readout_a"]["default_cell"]["supported"])
    )


# ── What `run(live=True)` does with the outcome ──────────────────────────────────────────────────


def _modes(report: dict[str, Any]) -> dict[int, str]:
    return {s["stage"]: s["mode"] for s in report["stages"]}


def test_a_fixture_run_labels_every_stage_fixture(tmp_path: Path) -> None:
    report = audit.run(tmp_path, live=False, home=tmp_path / "none")
    assert [s["stage"] for s in report["stages"]] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert set(_modes(report).values()) == {"FIXTURE"}
    assert report["stages"][8]["findings"]["attempt3_reproduction"]["ran"] is False


def test_a_regenerated_run_labels_the_stages_it_recomputed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(h10, "main", _StubMain(_committed()))
    report = audit.run(tmp_path, live=True, home=tmp_path / "none")
    modes = _modes(report)
    assert modes[4] == "LIVE" and modes[6] == "LIVE" and modes[7] == "LIVE"
    assert modes[3] == "FIXTURE+LIVE" and modes[8] == "FIXTURE+LIVE"
    assert modes[2] == "FIXTURE"  # no --rebuild, so the derived stores were not touched
    assert report["stages"][8]["findings"]["attempt3_reproduction"]["reproduced"] is True


def test_a_stopped_regeneration_leaves_the_committed_fixture_in_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(h10, "main", _StubMain(_committed(), code=1))
    report = audit.run(tmp_path, live=True, home=tmp_path / "none")
    assert _modes(report)[4] == "FIXTURE"
    assert report["stages"][8]["findings"]["attempt3_reproduction"]["return_code"] == 1


def test_a_missing_store_does_not_sink_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(**_: Any) -> int:
        raise FileNotFoundError("sha256:x is not in the store — re-fetch the input")

    monkeypatch.setattr(h10, "main", refuse)
    report = audit.run(tmp_path, live=True, home=tmp_path / "none")
    reproduction = report["stages"][8]["findings"]["attempt3_reproduction"]
    assert reproduction["ran"] is False
    assert "FileNotFoundError" in reproduction["error"]
    assert _modes(report)[4] == "FIXTURE"


# ── The graph read ───────────────────────────────────────────────────────────────────────────────


def _graph(tmp_path: Path, *, adj_p: float) -> kuzu.Connection:
    import test_query

    nodes, edges = test_query._core()
    for node in nodes:
        if node.get("id") == test_query.RESULT:
            node["adj_p_value"] = adj_p
    return test_query._write(tmp_path, nodes, edges)


def test_the_graph_read_classifies_a_target_by_the_modules_own_rule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conn = _graph(tmp_path, adj_p=0.001)
    monkeypatch.setattr("bzk.query.graph.connect", lambda *_a, **_k: conn)
    read = audit._read_graph(tmp_path / "g.kuzu", [{"gene": "MX1"}, {"gene": "NOT_A_GENE"}])
    assert read["results_at_site_grain"] == 1
    assert read["significant_up"] == 1
    assert read["target_status"] == {"MX1": "recovered", "NOT_A_GENE": "absent_from_tested"}


def test_a_tested_target_that_is_not_significant_is_not_called_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conn = _graph(tmp_path, adj_p=0.5)
    monkeypatch.setattr("bzk.query.graph.connect", lambda *_a, **_k: conn)
    read = audit._read_graph(tmp_path / "g.kuzu", [{"gene": "MX1"}])
    assert read["significant_up"] == 0
    assert read["target_status"] == {"MX1": "tested_not_recovered"}


def test_an_unreadable_graph_is_reported_and_the_stage_survives(tmp_path: Path) -> None:
    stage = audit.stage5_differential(tmp_path / "absent.kuzu")
    assert str(stage.findings["live_graph"]).startswith("NOT READ")
    assert stage.mode == "FIXTURE"


def test_the_fixture_run_counts_what_the_fixture_holds(tmp_path: Path) -> None:
    """Expected values come from reading the fixture directly, not through the audit's helpers."""
    rows = _committed()["readouts"]["primary"]["per_claim_support"]["rows"]
    imputed = sum(1 for r in rows if r["row_carries_an_imputed_cell"])
    census = audit.stage3_census(_committed()).findings
    assert census["claims_in_tested_population"] == len(rows)
    assert census["tested_claims_with_an_imputed_cell"] == imputed


def test_a_renamed_gene_is_found_by_its_sites_and_reported_as_renamed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The DDX58 case: the fixture names a target by the 2019 symbol, the graph's `Gene` carries the
    current one. A symbol-only match called a target with tested sites absent."""
    import test_query

    conn = _graph(tmp_path, adj_p=0.001)
    monkeypatch.setattr("bzk.query.graph.connect", lambda *_a, **_k: conn)
    renamed = {"gene": "OLD_NAME", "sites": [{"site": test_query.SITE}]}
    read = audit._read_graph(tmp_path / "g.kuzu", [renamed])
    assert read["target_status"] == {"OLD_NAME": "recovered"}
    assert read["symbol_differs"] == {"OLD_NAME": ["MX1"]}
    # Without its sites the same name is, correctly, not found.
    bare = audit._read_graph(tmp_path / "g.kuzu", [{"gene": "OLD_NAME"}])
    assert bare["target_status"] == {"OLD_NAME": "absent_from_tested"}


# ── Stage 4 reads the drawn cells against two references ────────────────────────────────────────


def _two_column_log2() -> Any:
    import numpy as np

    nan = float("nan")
    return np.array([[10, nan], [12, nan], [14, 8], [nan, 9], [nan, 10]], dtype=float)


def test_whole_column_reference_reads_drawn_cells_against_the_whole_retained_column() -> None:
    drawn = {
        "a": {"n": 5, "mean": 9.0, "sd": 1.0},
        "b": {"n": 5, "mean": 7.0, "sd": 0.5},
    }
    got = audit.whole_column_reference(
        _two_column_log2(), {"valid_value_rule": {"taken": 1}}, drawn
    )
    assert got["a"] == {"n_reference": 3, "downshift_sd": 1.5, "width_sd": 0.5}
    assert got["b"] == {"n_reference": 3, "downshift_sd": 2.0, "width_sd": 0.5}


def test_whole_column_reference_honours_the_valid_value_rule() -> None:
    drawn = {"a": {"n": 5, "mean": 9.0, "sd": 1.0}, "b": {"n": 5, "mean": 7.0, "sd": 0.5}}
    got = audit.whole_column_reference(
        _two_column_log2(), {"valid_value_rule": {"taken": 2}}, drawn
    )
    assert got["a"] == {"n_reference": 0, "downshift_sd": None, "width_sd": None}


def test_stage4_without_live_says_the_whole_column_reference_was_not_computed() -> None:
    stage = audit.stage4_imputation(_committed())
    assert stage.findings["against_whole_deposit_column"].startswith("NOT COMPUTED")
    assert "reference_distribution" in stage.findings


def test_stage4_live_with_no_store_reports_the_failure_instead_of_raising(tmp_path: Path) -> None:
    stage = audit.stage4_imputation(_committed(), tmp_path)
    assert "NOT COMPUTED" in stage.findings["against_whole_deposit_column"]


# ── Stage 3's drawn-cell census: classes, gap, and the drawn rule ───────────────────────────────


def test_drawn_cell_census_partitions_the_claims_and_measures_the_comparable_gap() -> None:
    """One claim per class. Only the one-KO-cell claim is comparable: published KO mean 3, measured
    KO mean (4 + 5) / 2 = 4.5, WT mean 1 in both, so the signed gap is 2 - 3.5 = -1.5."""
    values = [0.0, 4.0, 5.0, 1.0, 1.0, 1.0]
    claims = [
        (values, [False] * 6),
        (values, [True, False, False, False, False, False]),
        (values, [True, True, True, False, False, False]),
        (values, [False, False, False, True, True, True]),
        (values, [True] * 6),
    ]
    got = audit.drawn_cell_census(claims)
    assert got["published_claims"] == 5
    assert got["no_drawn_cell"] == 1
    assert got["some_drawn_both_arms_measured"] == 1
    assert got["whole_arm_drawn"] == 3
    assert got["no_drawn_cell"] + got["some_drawn_both_arms_measured"] + got["whole_arm_drawn"] == 5
    assert got["containing_a_drawn_cell"] == {"count": 4, "of": 5, "fraction": 0.8}
    assert got["comparable_gap_published_minus_measured_only_log2"] == {
        "n": 1,
        "signed_quartiles": [-1.5, -1.5, -1.5],
        "absolute_median": 1.5,
        "published_exceeds_measured_only": 0,
    }


def test_stage3_without_live_says_the_drawn_cell_census_was_not_computed() -> None:
    stage = audit.stage3_census(_committed())
    assert stage.findings["drawn_cell_census"].startswith("NOT COMPUTED")


def test_stage3_live_with_no_store_reports_the_failure_instead_of_raising(tmp_path: Path) -> None:
    stage = audit.stage3_census(_committed(), tmp_path)
    assert "NOT COMPUTED" in stage.findings["drawn_cell_census"]


_INTENSITY = [f"Intensity {arm}_{i}" for arm in ("KO_IFN", "WT_IFN") for i in (1, 2, 3)]


def _sites_table(tmp_path: Path, cells: dict[str, str]) -> Path:
    """A one-row MaxQuant sites table, id 7: every intensity measured unless `cells` says otherwise."""
    header = ["id", "Reverse", *_INTENSITY, "Intensity KO_IFN_1___1"]
    values = {"id": "7", "Reverse": "", **dict.fromkeys(_INTENSITY, "100"), **cells}
    path = tmp_path / "sites.txt"
    path.write_text("\t".join(header) + "\n" + "\t".join(values.get(h, "0") for h in header) + "\n")
    return path


def _live_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cells: dict[str, str], *, s1: bool = True
) -> None:
    """Stub the store: the sites table is the synthetic one, S1 is present or absent by `s1`."""
    sites = _sites_table(tmp_path, cells)
    s1_path = tmp_path / "s1.xlsx"
    s1_path.write_bytes(b"stand-in; _s1_rows is stubbed")

    def verify(_digest: str, *, filename: str, home: Path) -> Path:
        if filename == SUPP_DATA_1.filename:
            if not s1:
                raise FileNotFoundError(f"{filename} is not in {home}")
            return s1_path
        return sites

    columns = [f"S1 {name}" for name in _INTENSITY]
    monkeypatch.setattr(audit, "verify", verify)
    monkeypatch.setattr(h10, "_s1_rows", lambda _p: (columns, {3: dict.fromkeys(columns, "1.0")}))
    monkeypatch.setattr(h10, "s1_columns", lambda header: list(header))
    real_load = audit._load
    monkeypatch.setattr(
        audit,
        "_load",
        lambda name: (
            {"rows": [{"deposit_id": "7", "row": 3, "lost_at": None}]}
            if name == audit.CASCADE
            else real_load(name)
        ),
    )


def test_stage3_live_with_s1_absent_reports_it_and_raises_no_system_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reported as S1's own `FileNotFoundError`, not as an exit. `_supplement_path` would turn this
    into `SystemExit`; the wrapper reads S1 through `verify` so the finding names the missing file
    rather than relying on the handler's width to catch an exit."""
    _live_inputs(tmp_path, monkeypatch, {}, s1=False)
    census = audit.stage3_census(_committed(), tmp_path).findings["drawn_cell_census"]
    assert census == {
        "NOT COMPUTED": f"FileNotFoundError: {SUPP_DATA_1.filename} is not in {tmp_path}"
    }


def test_a_cell_reported_only_at_a_multiplicity_is_provided_not_drawn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _live_inputs(tmp_path, monkeypatch, {"Intensity KO_IFN_1": "0", "Intensity KO_IFN_1___1": "5"})
    census = audit.stage3_census(_committed(), tmp_path).findings["drawn_cell_census"]
    assert census["no_drawn_cell"] == 1
    assert census["some_drawn_both_arms_measured"] == 0


def test_a_cell_reported_at_no_multiplicity_either_is_drawn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control for the test above: the same stubs do see a drawn cell when there is one."""
    _live_inputs(tmp_path, monkeypatch, {"Intensity KO_IFN_1": "0"})
    census = audit.stage3_census(_committed(), tmp_path).findings["drawn_cell_census"]
    assert census["no_drawn_cell"] == 0
    assert census["some_drawn_both_arms_measured"] == 1


# ── Stage 4's route 2: the downshift band from published fold changes ───────────────────────────

ROUND16 = Path(__file__).parent.parent / "notes" / "scripts" / "diagnose_round16.py"
ROUND16_LOG = Path(__file__).parent.parent / "notes" / "logs" / "round16.txt"

#: Two comparable claims, each with one drawn cell, both in the KO arm: claims whose drawn cells
#: sit in opposite arms give a pooled gap that barely responds to the downshift. Column statistics
#: are given (mean 20, SD 1 everywhere), so the observed gaps are hand-computable:
#: A = (18.2 + 21 + 21)/3 - 21 = -0.9333 and B = (21 + 18.3 + 21)/3 - 21 = -0.9, median -0.9167.
_BAND_CLAIMS: list[tuple[list[float], list[bool], float]] = [
    ([18.2, 21.0, 21.0, 20.0, 20.0, 20.0], [True, False, False, False, False, False], 1.0),
    ([21.0, 18.3, 21.0, 20.0, 20.0, 20.0], [False, True, False, False, False, False], 1.0),
]
#: 1.8 is scanned FIRST and 1.7 second, deliberately. With a fresh generator per value the first
#: value's draws are the shared run's, so only the second value's verdict can show whether the
#: generator is shared. Seed 17 puts 1.8 11.6% inside `2 * spread` and 1.7 13.4% outside it;
#: a fresh generator per value moves 1.7 to 49% inside, and `4 * spread` moves it to 43% inside.
_BAND_SCAN = (1.8, 1.7)
_BAND_SEED = 17


def _band(seed: int = _BAND_SEED) -> dict[str, Any]:
    return audit.downshift_band(_BAND_CLAIMS, [20.0] * 6, [1.0] * 6, _BAND_SCAN, 0.29, seed)


def test_downshift_band_keeps_the_consistent_value_and_drops_the_other() -> None:
    """The band is a strict subset of the scan, and each value reports its own spread.

    Sits about 12% from the consistency boundary on purpose (see `_BAND_SCAN`): that is what lets
    this case tell a shared generator from a fresh one, at the price of a verdict a change in
    numpy's generator stream could move.
    """
    got = _band()
    assert got["comparable_claims"] == 2
    assert got["observed_median_gap"] == -0.917
    assert got["consistent_band"] == [1.8]
    assert set(got["consistent_band"]) < set(_BAND_SCAN)
    assert list(got["scan"]) == ["1.8", "1.7"]
    assert [v["consistent"] for v in got["scan"].values()] == [True, False]
    for value in got["scan"].values():
        assert set(value) == {"predicted_median_gap", "bootstrap_standard_error", "consistent"}
        assert value["bootstrap_standard_error"] > 0
    assert got["width_sd_given"] == 0.29


def test_downshift_band_is_deterministic_in_its_seed() -> None:
    assert _band() == _band()


def test_the_ported_scan_matches_the_script_it_was_ported_from() -> None:
    """`LL_*` mirror `diagnose_round16.py` section LL; read the constants back out of it."""
    import ast

    tree = ast.parse(ROUND16.read_text(encoding="utf-8"))
    width = next(
        ast.literal_eval(n.value)
        for n in ast.walk(tree)
        if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "WIDTH" for t in n.targets)
    )
    loop = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.For) and getattr(n.target, "id", None) == "downshift"
    )
    seeds = [
        ast.literal_eval(n.args[0])
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "default_rng"
    ]
    ranges = [
        ast.literal_eval(n.args[0])
        for n in ast.walk(loop)
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "range"
    ]
    assert width == audit.LL_WIDTH
    assert ast.literal_eval(loop.iter) == audit.LL_DOWNSHIFTS
    assert seeds == [audit.LL_SEED]
    assert sorted(ranges) == sorted([audit.LL_DRAWS, audit.LL_RESAMPLES])


def test_stage4_without_live_says_neither_route_was_computed() -> None:
    findings = audit.stage4_imputation(_committed()).findings
    assert findings["downshift_band_from_fold_changes"] == (
        "NOT COMPUTED: needs the deposit bytes; run with --live"
    )
    assert findings["against_whole_deposit_column"] == (
        "NOT COMPUTED: needs the deposit bytes; run with --live"
    )


def test_stage4_live_with_no_store_reports_both_failures_instead_of_raising(
    tmp_path: Path,
) -> None:
    findings = audit.stage4_imputation(_committed(), tmp_path).findings
    for key in ("downshift_band_from_fold_changes", "against_whole_deposit_column"):
        assert set(findings[key]) == {"NOT COMPUTED"}
        assert findings[key]["NOT COMPUTED"].startswith("FileNotFoundError: ")


def test_stage4_live_with_s1_absent_names_the_missing_file_not_an_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The exact finding, exception name included. The handler catches `SystemExit` too, so a
    wrapper reading S1 through `_supplement_path` would still return `NOT COMPUTED` and let nothing
    escape; only the name inside the finding tells the two apart."""
    _live_inputs(tmp_path, monkeypatch, {"Intensity KO_IFN_1": "0"}, s1=False)
    band = audit.stage4_imputation(_committed(), tmp_path).findings[
        "downshift_band_from_fold_changes"
    ]
    assert band == {
        "NOT COMPUTED": f"FileNotFoundError: {SUPP_DATA_1.filename} is not in {tmp_path}"
    }


@pytest.mark.parametrize(
    ("cells", "comparable"),
    [
        ({"Intensity KO_IFN_1": "0", "Intensity KO_IFN_1___1": "5"}, 0),
        ({"Intensity KO_IFN_1": "0"}, 1),
    ],
    ids=["multiplicity-only-is-provided", "control-drawn"],
)
def test_route_2_uses_the_multiplicity_aware_drawn_rule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cells: dict[str, str], comparable: int
) -> None:
    """Route 2's drawn rule is `provided()`, not route 1's summed-column-only `cell()`.

    The two rules disagree on no cell of the PXD018299 deposit, so the real-data test above cannot
    see which one the wrapper uses; only this synthetic case can. Two fully measured rows join the
    claim's row so every column has a finite mean and SD.
    """
    _live_inputs(tmp_path, monkeypatch, cells)
    sites = tmp_path / "sites.txt"
    width = len(sites.read_text().splitlines()[0].split("\t"))
    measured = ["100"] * (width - 3)
    sites.write_text(
        sites.read_text() + "".join("\t".join([i, "", *measured, "0"]) + "\n" for i in ("8", "9"))
    )
    seen: list[Any] = []

    def record(claims: Any, *_a: Any, **_k: Any) -> dict[str, Any]:
        seen.append(claims)
        return {}

    monkeypatch.setattr(audit, "downshift_band", record)
    band = audit.stage4_imputation(_committed(), tmp_path).findings[
        "downshift_band_from_fold_changes"
    ]
    assert "NOT COMPUTED" not in band
    (claims,) = seen
    assert len(claims) == comparable
    if comparable:
        assert claims[0][1] == [True, False, False, False, False, False]


def _logged_band() -> dict[str, Any]:
    """Section LL of the committed log, `notes/logs/round16.txt`, parsed into the band's shape."""
    import re

    lines = ROUND16_LOG.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("LL —"))
    end = next(i for i in range(start, len(lines)) if "downshifts consistent" in lines[i])
    block = lines[start : end + 1]
    observed = next(
        re.search(r"over (\d+) claims: ([+-][\d.]+)", x) for x in block if "observed" in x
    )
    assert observed is not None
    scan = {
        m[1]: (float(m[2]), m[3] == "yes")
        for x in block
        if (m := re.fullmatch(r"\s+([\d.]+)\s+([+-][\d.]+)\s+(yes|no)", x))
    }
    se = next(float(x.rsplit(":", 1)[1]) for x in block if "bootstrap standard error" in x)
    band = json.loads(block[-1].rsplit(":", 1)[1])
    return {
        "claims": int(observed[1]),
        "observed": float(observed[2]),
        "scan": scan,
        "se": se,
        "band": band,
    }


def test_route_2_on_the_deposit_reproduces_the_committed_log() -> None:
    """Against the real bytes, the port reproduces every figure LL printed. The log prints one
    standard error, the LAST downshift's, so it is compared against 2.5's alone."""
    try:
        for digest, filename in (
            (PXD018299_SITES.expected_content_hash or "", PXD018299_SITES.filename),
            (SUPP_DATA_1.expected_content_hash, SUPP_DATA_1.filename),
        ):
            raw_store.verify(digest, filename=filename, home=raw_store.DEFAULT_HOME)
    except FileNotFoundError as exc:
        pytest.skip(f"deposit or S1 not in raw/ — run `python -m bzk.sources.pride` first ({exc})")
    got = audit._live_downshift_band(raw_store.DEFAULT_HOME)
    log = _logged_band()
    assert got["comparable_claims"] == log["claims"]
    assert got["observed_median_gap"] == log["observed"]
    assert {k: (v["predicted_median_gap"], v["consistent"]) for k, v in got["scan"].items()} == (
        log["scan"]
    )
    assert got["scan"][str(audit.LL_DOWNSHIFTS[-1])]["bootstrap_standard_error"] == log["se"]
    assert got["consistent_band"] == log["band"]


# ── A helper's exit must not end the report ──────────────────────────────────────────────────────


def _caught(handler: Any) -> set[str]:
    """The names an `except` clause catches; a bare `except:` catches everything."""
    import ast

    if handler.type is None:
        return {"BaseException"}
    types = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
    return {ast.unparse(t).rsplit(".", 1)[-1] for t in types}


def exception_handlers(source: str) -> list[int]:
    """The line of every `except` clause in `source` that catches `Exception`, in source order.

    Sorted because `ast.walk` is breadth-first: a nested handler comes back after a later one at
    module depth.
    """
    import ast

    return sorted(
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ExceptHandler) and "Exception" in _caught(node)
    )


def handlers_missing_system_exit(source: str) -> list[int]:
    """Of `exception_handlers(source)`, the lines that catch neither `SystemExit` nor
    `BaseException`, in source order."""
    import ast

    return sorted(
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ExceptHandler)
        and "Exception" in _caught(node)
        and not _caught(node) & {"SystemExit", "BaseException"}
    )


def test_every_handler_that_catches_exception_also_catches_system_exit() -> None:
    """`except Exception` does not catch `SystemExit`, and several input helpers turn a missing file
    into one. A handler that exists to keep the report alive must catch it too, or a helper that
    exits ends the process instead of being reported. Read by shape, not by line or comment."""
    source = Path(audit.__file__).read_text(encoding="utf-8")
    assert exception_handlers(source), (
        "no handler catches Exception: the guard is reading the wrong source"
    )
    offending = handlers_missing_system_exit(source)
    assert not offending, (
        f"bzk/audit.py line(s) {offending} catch Exception but not SystemExit. `except Exception` "
        "does not catch SystemExit, so a helper that exits on a missing input would end the "
        "process instead of being reported. Catch (Exception, SystemExit)."
    )


def _one(clause: str) -> str:
    """A module whose only handler, on line 3, is `clause`."""
    return f"try:\n    pass\n{clause}\n    pass\n"


#: Sources `handlers_missing_system_exit` must flag, each with the exact lines it must return. The
#: guard above passes on a clean module whether or not the rule works; these are what show it fires.
CAUGHT: dict[str, tuple[str, list[int]]] = {
    "except Exception": (_one("except Exception:"), [3]),
    "except Exception as exc": (_one("except Exception as exc:"), [3]),
    "with ValueError": (_one("except (Exception, ValueError):"), [3]),
    "with a BaseException sibling that is not SystemExit": (
        _one("except (Exception, KeyboardInterrupt):"),
        [3],
    ),
    "nested in a method": (
        (
            "class C:\n"
            "    def f(self):\n"
            "        try:\n"
            "            pass\n"
            "        except Exception:\n"
            "            pass\n"
        ),
        [5],
    ),
    "only the second of two": (
        (
            "try:\n"
            "    pass\n"
            "except (Exception, SystemExit):\n"
            "    pass\n"
            "try:\n"
            "    pass\n"
            "except Exception:\n"
            "    pass\n"
        ),
        [7],
    ),
}

#: Sources `handlers_missing_system_exit` must pass: the order inside a tuple carries no meaning,
#: and a handler that does not catch `Exception` is outside the rule.
UNCAUGHT: dict[str, str] = {
    "Exception with SystemExit": _one("except (Exception, SystemExit):"),
    "SystemExit with Exception": _one("except (SystemExit, Exception):"),
    "BaseException": _one("except BaseException:"),
    "ValueError": _one("except ValueError:"),
    "bare except": _one("except:"),
}

#: Sources for `exception_handlers`, the guard's non-empty question, with the exact lines it must
#: return. The two-handler case puts the first handler one level deeper than the second, so a
#: breadth-first walk returns them out of source order.
EXCEPTION_HANDLERS: dict[str, tuple[str, list[int]]] = {
    "no handler": ("x = 1\n", []),
    "only ValueError": (_one("except ValueError:"), []),
    "two Exception handlers at different depths": (
        (
            "def f():\n"
            "    try:\n"
            "        pass\n"
            "    except Exception:\n"
            "        pass\n"
            "try:\n"
            "    pass\n"
            "except (Exception, SystemExit):\n"
            "    pass\n"
        ),
        [4, 8],
    ),
}


@pytest.mark.parametrize("name", list(CAUGHT))
def test_the_handler_rule_flags_each_caught_shape(name: str) -> None:
    source, expected = CAUGHT[name]
    assert handlers_missing_system_exit(source) == expected


@pytest.mark.parametrize("name", list(UNCAUGHT))
def test_the_handler_rule_passes_each_uncaught_shape(name: str) -> None:
    assert handlers_missing_system_exit(UNCAUGHT[name]) == []


@pytest.mark.parametrize("name", list(EXCEPTION_HANDLERS))
def test_exception_handlers_finds_exactly_the_exception_clauses(name: str) -> None:
    source, expected = EXCEPTION_HANDLERS[name]
    assert exception_handlers(source) == expected


def test_the_handler_rule_reads_names_not_bindings() -> None:
    """The guard's limits, asserted as they stand so that widening either is deliberate.

    `_caught` reads the spelled name and keeps its last dotted part, so `except builtins.Exception`
    reads as `Exception` and is flagged. It does not resolve bindings, so an aliased import read as
    `except E:` is not seen as catching `Exception` at all, and is missed.
    """
    dotted = "import builtins\n" + _one("except builtins.Exception:")
    aliased = "from builtins import Exception as E\n" + _one("except E:")
    assert exception_handlers(dotted) == [4]
    assert handlers_missing_system_exit(dotted) == [4]
    assert exception_handlers(aliased) == []
    assert handlers_missing_system_exit(aliased) == []


def _exits(code: object) -> Any:
    def stub(**_: Any) -> int:
        raise SystemExit(code)

    return stub


def test_a_helper_that_exits_does_not_sink_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `--live` regeneration reaches `raise SystemExit` when a PXD026748 input is missing."""
    monkeypatch.setattr(h10, "main", _exits("sites.txt is not in the content store"))
    report = audit.run(tmp_path, live=True, home=tmp_path / "none")
    reproduction = report["stages"][8]["findings"]["attempt3_reproduction"]
    assert reproduction["ran"] is False
    assert reproduction["error"].startswith("SystemExit")
    assert len(report["stages"]) == 9
    assert _modes(report)[4] == "FIXTURE"


def test_an_interrupt_still_ends_the_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The handler is widened to `SystemExit` only, never to `BaseException`."""

    def interrupt(**_: Any) -> int:
        raise KeyboardInterrupt

    monkeypatch.setattr(h10, "main", interrupt)
    with pytest.raises(KeyboardInterrupt):
        audit.run(tmp_path, live=True, home=tmp_path / "none")


# ── Stages 6 and 7 say which variant, and stage 6 which population, they computed ────────────────


def test_stages_6_and_7_read_the_variant_from_the_fixture(tmp_path: Path) -> None:
    """Read from `readouts.primary.variant`, never written: only that home is mutated below, so a
    stage reading `primary_variant` or the top-level key — or a hand-written label — stays red."""
    fx = _committed()
    six = audit.stage6_sensitivity(fx, tmp_path)
    seven = audit.stage7_propagation(fx)
    assert six.findings["registered_variant"] == fx["readouts"]["primary"]["variant"]
    assert seven.findings["registered_variant"] == fx["readouts"]["primary"]["variant"]
    # The three homes coincide at this fixture; recorded, not assumed. `primary_variant` names its
    # block's primary, and takes another value in the secondary block.
    assert (
        fx["readouts"]["primary"]["variant"]
        == fx["readouts"]["primary"]["primary_variant"]
        == fx["primary_variant"]
        == "joint_half+random_excluding_trivial"
    )
    assert (
        fx["readouts"]["secondary"]["primary_variant"] == "joint_half+exhaustive_excluding_trivial"
    )
    mutant = copy.deepcopy(fx)
    mutant["readouts"]["primary"]["variant"] = "MUTANT"
    six_m = audit.stage6_sensitivity(mutant, tmp_path)
    seven_m = audit.stage7_propagation(mutant)
    assert six_m.findings["registered_variant"] == "MUTANT"
    assert seven_m.findings["registered_variant"] == "MUTANT"
    assert mutant["readouts"]["primary"]["primary_variant"] == "joint_half+random_excluding_trivial"
    assert mutant["primary_variant"] == "joint_half+random_excluding_trivial"


def test_stage_6_recomputes_both_populations_of_the_registered_readout(tmp_path: Path) -> None:
    """Exact equality, shares included: each is the int/int division the fixture stored."""
    fx = _committed()
    six = audit.stage6_sensitivity(fx, tmp_path)
    readout_b = fx["readouts"]["primary"]["readout_b"]
    assert six.findings["over_all_claims"] == readout_b["over_all_claims"]
    assert six.findings["conditional_on_imputation"] == readout_b["conditional_on_imputation"]
    assert (
        six.findings["changing_somewhere_in_family"]
        == readout_b["family_categories"]["underdetermined"]
    )
    # The marked primary is the population the fixture's own verdict reads.
    assert six.findings["registered_primary"] == "conditional_on_imputation"
    assert (
        six.findings[six.findings["registered_primary"]]["share"] == readout_b["verdict"]["share"]
    )


def test_a_measured_claim_changing_in_the_default_cell_separates_the_two_populations(
    tmp_path: Path,
) -> None:
    """The case the committed fixture cannot make: no fully measured claim changes support in its
    default cell, so both numerators are 159 and a build counting the all-claims numerator over the
    imputed rows passes the mirror above. One cell flipped: row 274 (deposit 859, ALDOA, fully
    measured, already changing elsewhere in the family) at column 160, the first default-cell
    column. One column only — flipping all twenty gives min == max == 0 and nothing changes."""
    fx = _committed()
    assert audit._default_columns(audit._members(fx))[0] == 160
    assert audit._default_columns(audit._members(fx))[-1] == 179
    six = audit.stage6_sensitivity(fx, tmp_path)
    seven = audit.stage7_propagation(fx)
    assert six.findings["over_all_claims"]["numerator"] == 159
    assert six.findings["conditional_on_imputation"]["numerator"] == 159
    assert six.findings["changing_somewhere_in_family"] == 479
    assert six.findings["supported_in_every_default_draw"] == 631
    assert six.findings["supported_in_no_default_draw"] == 1
    assert seven.findings["support_changes_in_family"] == 3
    assert seven.findings["support_changes_in_default_cell"] == 0
    assert seven.findings["fully_measured_claims"] == 40

    flipped = copy.deepcopy(fx)
    row = flipped["readouts"]["primary"]["per_claim_support"]["rows"][274]
    assert row["deposit_id"] == "859"
    assert row["gene_names"] == "ALDOA"
    assert row["row_carries_an_imputed_cell"] is False
    assert row["support"][160] == 1  # a cell already 0 would void the test
    row["support"][160] = 0
    six_f = audit.stage6_sensitivity(flipped, tmp_path)
    seven_f = audit.stage7_propagation(flipped)
    assert six_f.findings["over_all_claims"]["numerator"] == 160
    assert six_f.findings["over_all_claims"]["denominator"] == 791
    assert six_f.findings["conditional_on_imputation"]["numerator"] == 159
    assert six_f.findings["conditional_on_imputation"]["denominator"] == 751
    assert six_f.findings["changing_somewhere_in_family"] == 479
    assert (
        six_f.findings["changing_somewhere_in_family"]
        == flipped["readouts"]["primary"]["readout_b"]["family_categories"]["underdetermined"]
    )
    assert six_f.findings["supported_in_every_default_draw"] == 630
    assert six_f.findings["supported_in_no_default_draw"] == 1
    assert seven_f.findings["support_changes_in_family"] == 3
    # The first nonzero this counter has produced in any test or run.
    assert seven_f.findings["support_changes_in_default_cell"] == 1
    # Read from `row_carries_an_imputed_cell`, so no support flip can move it: a regression guard.
    assert seven_f.findings["fully_measured_claims"] == 40


def test_registered_variant_is_the_first_finding_of_stages_6_and_7(tmp_path: Path) -> None:
    fx = _committed()
    six = audit.stage6_sensitivity(fx, tmp_path)
    seven = audit.stage7_propagation(fx)
    assert next(iter(six.findings)) == "registered_variant"
    assert next(iter(seven.findings)) == "registered_variant"


def test_the_marked_primary_is_the_estimand_both_pre_registrations_name() -> None:
    """`registered_primary` in stage 6 is written, because the fixture marks no primary; these two
    sentences are its source, so the label is a mirror and carries a guard."""
    walk = Path(__file__).parent.parent / "walk"
    attempt3 = " ".join(
        (walk / "PREREG-PXD018299-H10-attempt3.md").read_text(encoding="utf-8").split()
    )
    base = " ".join((walk / "PREREG-PXD018299-H10.md").read_text(encoding="utf-8").split())
    assert (
        "These shares are taken over claims whose row carries at least one imputed value."
        in attempt3
    )
    assert "**Reported, never the headline:** - the same share over all claims;" in base


# ── The receipt map: every figure stages 6 and 7 disclaim, held against its sources ──────────────


class Violation(NamedTuple):
    kind: str
    subject: str


_SCRIPT = re.compile(r"diagnose_round\d+[a-z]?\.py")


def _round(name: str) -> str:
    """The text between `round` and the extension: `diagnose_round15b.py` and `round15b.txt`
    both give `15b`."""
    return name[name.rindex("round") + len("round") : name.rindex(".")]


def _once_in_its_section(text: str, anchor: str, section: int) -> bool:
    if text.count(anchor) != 1:
        return False
    heading = re.search(rf"^## {section}\. ", text, re.MULTILINE)
    if heading is None:
        return False
    after = re.search(r"^## ", text[heading.end() :], re.MULTILINE)
    end = heading.end() + after.start() if after is not None else len(text)
    at = text.index(anchor)
    return heading.start() <= at and at + len(anchor) <= end


def _misattributed(entry: audit.ReceiptEntry, home_text: str, root: Path) -> bool:
    named = {Path(s).name for s in entry.scripts}
    home_set = set(_SCRIPT.findall(home_text))
    if not named:  # 3a
        return True
    if not named <= home_set:  # 3b
        return True
    if len(home_set) > 1 and entry.script_anchor is None:  # 3c
        return True
    if len(home_set) > 1 and entry.script_anchor is not None:
        anchor = entry.script_anchor
        own = [root / s for s in entry.scripts if (root / s).is_file()]
        if any(anchor not in p.read_text(encoding="utf-8") for p in own):  # 3d
            return True
        others = [root / "notes" / "scripts" / n for n in sorted(home_set - named)]
        if any(p.is_file() and anchor in p.read_text(encoding="utf-8") for p in others):  # 3e
            return True
    return len(home_set) == 1 and entry.script_anchor is not None  # 3f


def check_receipts(entries: tuple[audit.ReceiptEntry, ...], root: Path) -> list[Violation]:
    """Each entry's anchors still occur in their sources, and its instrument agrees with its home.

    Six directions, each kind reported at most once per entry, in direction order; `subject` is the
    entry's `findings_anchor`. Anchors match as raw substrings, so a reflowed line fails loudly.

    1. `findings_not_unique` — the anchor occurs other than exactly once in `walk/FINDINGS.md`, or
       its one occurrence is outside the entry's section.
    2. `home_drift` — the home is missing or lacks `home_anchor`. A missing home skips direction 3.
    3. `attribution` — the scripts are empty or not all named by the home; or, where the home names
       several, `script_anchor` is absent, missing from one of the entry's own scripts, or present
       in a home script the entry does not name; or the home names one and `script_anchor` is set.
    4. `missing_script` — a named script does not exist.
    5. `log_drift` — the log is missing, lacks its anchor, or comes from a round no named script
       is from.
    6. `absence_false` — an entry without a log, whose `walk/FINDINGS.md` anchor a top-level file
       in `notes/logs/` contains.

    **What it does not establish.** Direction 3 checks the instrument against the home document,
    not whether the home is right. A coherent re-attribution passes: `home_anchor` is chosen by the
    map, not tied to `findings_anchor`, so moving a log-less row's `scripts`, `home` and
    `home_anchor` together to another home where the new anchor occurs satisfies every direction.
    Direction 6 establishes absence only in `walk/FINDINGS.md`'s own words, so removing row 11's
    log goes undetected (its wording occurs in no log); direction 3 still guards its attribution.
    """
    findings = (root / "walk" / "FINDINGS.md").read_text(encoding="utf-8")
    logs_dir = root / "notes" / "logs"
    logs = sorted(p for p in logs_dir.iterdir() if p.is_file()) if logs_dir.is_dir() else []
    out: list[Violation] = []
    for entry in entries:
        kinds: list[str] = []
        if not _once_in_its_section(findings, entry.findings_anchor, entry.section):
            kinds.append("findings_not_unique")
        home = root / entry.home
        home_text = home.read_text(encoding="utf-8") if home.is_file() else None
        if home_text is None or entry.home_anchor not in home_text:
            kinds.append("home_drift")
        if home_text is not None and _misattributed(entry, home_text, root):
            kinds.append("attribution")
        if any(not (root / s).is_file() for s in entry.scripts):
            kinds.append("missing_script")
        if entry.log is not None:
            log_path, log_anchor = entry.log
            log = root / log_path
            rounds = {_round(Path(s).name) for s in entry.scripts}
            if (
                not log.is_file()
                or log_anchor not in log.read_text(encoding="utf-8")
                or _round(log.name) not in rounds
            ):
                kinds.append("log_drift")
        elif any(entry.findings_anchor in p.read_text(encoding="utf-8") for p in logs):
            kinds.append("absence_false")
        out += [Violation(kind, entry.findings_anchor) for kind in kinds]
    return out


_R13 = "notes/scripts/diagnose_round13.py"
_R11 = "notes/scripts/diagnose_round11.py"
_R12 = "notes/scripts/diagnose_round12.py"
_TWO_SCRIPT_HOME = (
    "Scripts: `notes/scripts/diagnose_round11.py` and `diagnose_round12.py`.\n\nhome anchor\n"
)
_BASE_ENTRY = audit.ReceiptEntry(
    5,
    "alpha anchor",
    "the synthetic figure, 20 draws",
    (_R13,),
    None,
    "walk/CHECKS-base.md",
    "home anchor",
    ("notes/logs/round13.txt", "log anchor"),
)


def _write(root: Path, rel: str, text: str) -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _receipt_root(root: Path) -> None:
    """Consistent with `_BASE_ENTRY`: the anchor once, in section 5; a home naming only round 13;
    rounds 11 to 14's scripts present; a log carrying its anchor and not the findings anchor."""
    _write(root, "walk/FINDINGS.md", "# F\n\n## 5. Five\n\nalpha anchor here.\n\n## 6. Six\n\nx\n")
    _write(
        root, "walk/CHECKS-base.md", "Script: `notes/scripts/diagnose_round13.py`.\n\nhome anchor\n"
    )
    for n in (11, 12, 13, 14):
        _write(root, f"notes/scripts/diagnose_round{n}.py", "print('synthetic')\n")
    _write(root, "notes/logs/round13.txt", "log anchor\n")


def _one_of_two(
    root: Path, entry: audit.ReceiptEntry, in11: bool, in12: bool
) -> audit.ReceiptEntry:
    _write(root, "walk/CHECKS-base.md", _TWO_SCRIPT_HOME)
    _write(root, _R11, "print('S anchor')\n" if in11 else "print('other')\n")
    _write(root, _R12, "print('S anchor')\n" if in12 else "print('other')\n")
    return entry._replace(scripts=(_R11,), script_anchor="S anchor", log=None)


Case = Callable[[Path, audit.ReceiptEntry], audit.ReceiptEntry]


def _unchanged(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return e


def _no_log(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return e._replace(log=None)


def _no_logs_directory(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    shutil.rmtree(r / "notes" / "logs")
    return e._replace(log=None)


def _anchor_twice(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "walk/FINDINGS.md", "## 5. Five\n\nalpha anchor, alpha anchor\n\n## 6. Six\n")
    return e


def _anchor_absent(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "walk/FINDINGS.md", "## 5. Five\n\nnothing\n\n## 6. Six\n")
    return e


def _anchor_in_the_other_section(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "walk/FINDINGS.md", "## 5. Five\n\nx\n\n## 6. Six\n\nalpha anchor\n")
    return e


def _home_drift(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "walk/CHECKS-base.md", "Script: `notes/scripts/diagnose_round13.py`.\n")
    return e


def _home_absent(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    (r / "walk" / "CHECKS-base.md").unlink()
    return e


def _wrong_instrument(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return e._replace(scripts=(_R11, _R12), log=None)


def _no_scripts(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return e._replace(scripts=(), log=None)


def _right_of_two(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return _one_of_two(r, e, True, False)


def _anchor_in_neither(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return _one_of_two(r, e, False, False)


def _anchor_in_both(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return _one_of_two(r, e, True, True)


def _two_without_anchor(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    return _one_of_two(r, e, True, False)._replace(script_anchor=None)


def _stray_anchor(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, _R13, "print('S anchor')\n")
    return e._replace(script_anchor="S anchor")


def _missing_script(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    (r / _R13).unlink()
    return e


def _log_content_drift(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "notes/logs/round13.txt", "something else\n")
    return e


def _wrong_log(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "notes/logs/round14.txt", "log anchor\n")
    return e._replace(log=("notes/logs/round14.txt", "log anchor"))


def _log_absent(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    (r / "notes" / "logs" / "round13.txt").unlink()
    return e


def _absence_false(r: Path, e: audit.ReceiptEntry) -> audit.ReceiptEntry:
    _write(r, "notes/logs/round13.txt", "alpha anchor\n")
    return e._replace(log=None)


#: Each fixture is consistent except in the one property its case names, so each expects one kind.
RECEIPT_CASES: dict[str, tuple[Case, list[str]]] = {
    "true, with log": (_unchanged, []),
    "true, without log": (_no_log, []),
    "no logs directory": (_no_logs_directory, []),
    "anchor not unique": (_anchor_twice, ["findings_not_unique"]),
    "anchor absent": (_anchor_absent, ["findings_not_unique"]),
    "home drift": (_home_drift, ["home_drift"]),
    "home absent": (_home_absent, ["home_drift"]),
    "wrong instrument": (_wrong_instrument, ["attribution"]),
    "no scripts": (_no_scripts, ["attribution"]),
    "one of two, right": (_right_of_two, []),
    "one of two, anchor in neither": (_anchor_in_neither, ["attribution"]),
    "one of two, anchor in both": (_anchor_in_both, ["attribution"]),
    "one of two, no anchor": (_two_without_anchor, ["attribution"]),
    "one script, stray anchor": (_stray_anchor, ["attribution"]),
    "wrong section": (_anchor_in_the_other_section, ["findings_not_unique"]),
    "missing script": (_missing_script, ["missing_script"]),
    "content drift": (_log_content_drift, ["log_drift"]),
    "wrong log": (_wrong_log, ["log_drift"]),
    "log absent": (_log_absent, ["log_drift"]),
    "absence false": (_absence_false, ["absence_false"]),
}


@pytest.mark.parametrize("name", list(RECEIPT_CASES))
def test_the_receipt_checker_returns_exactly_each_cases_kinds(name: str, tmp_path: Path) -> None:
    mutate, expected = RECEIPT_CASES[name]
    _receipt_root(tmp_path)
    entry = mutate(tmp_path, _BASE_ENTRY)
    assert [v.kind for v in check_receipts((entry,), tmp_path)] == expected


def test_every_receipt_in_the_map_holds_against_the_repository() -> None:
    assert check_receipts(audit.RECEIPT_MAP, audit.REPO_ROOT) == []
    # Direction 6 passes vacuously over nothing, so the logs it scans are pinned: a new committed
    # log is a deliberate edit here.
    assert sorted(p.name for p in (audit.REPO_ROOT / "notes" / "logs").iterdir()) == [
        "round13.txt",
        "round14.txt",
        "round15.txt",
        "round15b.txt",
        "round15c.txt",
        "round16.txt",
    ]


# ── The notes: stages 6 and 7 name the instrument behind each figure, and quote none ─────────────

_PATH = r"(?:walk|notes|bzk|tests)/[\w./-]*\w\.(?:md|py|txt|json)(?!:\d)"
_ALLOWED_DIGITS = (
    _PATH,
    r"diagnose_round\d+[a-z]?\.py",
    r"(?:20|100) draws",
    r"[Ss]ections? [56](?: and [56])?",
    r"ATP1A1 K605",
)
_MARKER_DATE = r"\d{4}-\d{2}-\d{2}"
_NOTE_KINDS = (
    "count",
    "order",
    "scripts",
    "section",
    "home",
    "log",
    "figure",
    "reviewer_pointer",
    "marker",
    "rule",
    "hand_instruments",
    "keys",
)


def _checks_docs(text: str) -> set[str]:
    return {f"walk/{m}" for m in re.findall(r"CHECKS-[\w-]+\.md", text)}


def _log_paths(text: str) -> set[str]:
    return {p for p in re.findall(_PATH, text) if p.startswith("notes/logs/")}


def _script_names(text: str) -> set[str]:
    paths = {Path(p).name for p in re.findall(_PATH, text) if p.startswith("notes/scripts/")}
    return set(_SCRIPT.findall(text)) | paths


def _instruments(text: str) -> tuple[set[str], set[str], set[str]]:
    return _script_names(text), _checks_docs(text), _log_paths(text)


def check_note(
    items: list[str],
    entries: tuple[audit.ReceiptEntry, ...],
    stage: int,
    anchors: tuple[str, ...],
) -> list[Violation]:
    """A stage's `not_automated` list: one hand-written item, then one item per entry, in order.

    Each kind is reported at most once per list, `subject` being the first offending item's index
    (or the stage, for `count`). A `count` violation is returned alone; an item failing `order` is
    not checked for `scripts`, `section`, `home` or `log`.

    **What it does not establish.** The claims in item 0 — its attributions and rule statements —
    are unchecked beyond digit and anchor absence, the reviewer pointer, the marker's form, stage
    7's rule words, the key pointers and item 0's instrument allowance. Digits pass unchecked in
    path-shaped tokens, a date in stage 6's item 0, draw counts, section numbers and `ATP1A1 K605`,
    so a wrong draw count is not caught; nor is a figure spelled out in words. The `describes`
    strings' rule and population claims are checked by nothing.
    """
    if len(items) != 1 + len(entries):
        return [Violation("count", str(stage))]
    found: dict[str, str] = {}

    def flag(kind: str, index: int) -> None:
        found.setdefault(kind, str(index))

    for k, entry in enumerate(entries):
        i = 1 + k
        item = items[i]
        if entry.describes not in item:
            flag("order", i)
            continue
        if set(_SCRIPT.findall(item)) != {Path(s).name for s in entry.scripts}:
            flag("scripts", i)
        cited = re.findall(r"[Ss]ections? ([56])(?: and ([56]))?", item)
        if {n for pair in cited for n in pair if n} != {str(entry.section)}:
            flag("section", i)
        if _checks_docs(item) != {entry.home}:
            flag("home", i)
        logs = _log_paths(item)
        if entry.log is not None:
            if logs != {entry.log[0]} or "no committed log" in item:
                flag("log", i)
        elif logs or "no committed log" not in item:
            flag("log", i)
    for i, item in enumerate(items):
        if any(a in item for a in anchors):
            flag("figure", i)
        stripped = item
        for pattern in _ALLOWED_DIGITS + ((_MARKER_DATE,) if (stage, i) == (6, 0) else ()):
            stripped = re.sub(pattern, "", stripped)
        if re.search(r"\d", stripped):
            flag("figure", i)
        if "REVIEWER-MAP" in item:
            flag("reviewer_pointer", i)
        if stage == 7 and "withdrawn" in item.lower():
            flag("marker", i)
        if stage == 7 and re.search(r"documented|halved", item, re.IGNORECASE):
            flag("rule", i)
    head = items[0]
    if stage == 6 and not re.match(r"Withdrawn and replaced \d{4}-\d{2}-\d{2}: ", head):
        flag("marker", 0)
    if stage == 6:
        end = head.find(". ")
        clause, rest = (head, "") if end < 0 else (head[:end], head[end:])
        scripts, docs, logs = _instruments(clause)
        allowed = scripts <= {"diagnose_round11.py", "diagnose_round12.py"} and docs <= {
            "walk/CHECKS-draws-and-threshold.md"
        }
        if not allowed or logs or any(_instruments(rest)):
            flag("hand_instruments", 0)
    elif any(_instruments(head)):
        flag("hand_instruments", 0)
    keys = ("registered_variant", "registered_primary") if stage == 6 else ("registered_variant",)
    if not all(key in head for key in keys):
        flag("keys", 0)
    return [Violation(kind, found[kind]) for kind in _NOTE_KINDS if kind in found]


# Synthetic entries, written here rather than taken from `RECEIPT_MAP`, so no mutation of the map
# or of the generator can redden the checker's own cases.
_E5 = (
    audit.ReceiptEntry(
        5,
        "alpha figure",
        "share alpha, 20 draws",
        (_R13,),
        None,
        "walk/CHECKS-collateral-and-pkm.md",
        "alpha home",
        ("notes/logs/round13.txt", "alpha log"),
    ),
    audit.ReceiptEntry(
        5,
        "beta figure",
        "count beta, 100 draws",
        ("notes/scripts/diagnose_round10.py",),
        None,
        "walk/CHECKS-ceiling-survives.md",
        "beta home",
        None,
    ),
    audit.ReceiptEntry(
        5,
        "gamma figure",
        "count gamma, 20 draws",
        ("notes/scripts/diagnose_round9.py",),
        None,
        "walk/CHECKS-ceiling-and-floor.md",
        "gamma home",
        None,
    ),
)
_E6 = (
    audit.ReceiptEntry(
        6,
        "delta figure",
        "ATP1A1 K605's delta, 20 draws",
        (_R12,),
        "delta script",
        "walk/CHECKS-draws-and-threshold.md",
        "delta home",
        None,
    ),
    audit.ReceiptEntry(
        6,
        "epsilon figure",
        "share epsilon, 20 draws",
        ("notes/scripts/diagnose_round14.py",),
        None,
        "walk/CHECKS-census.md",
        "epsilon home",
        ("notes/logs/round14.txt", "epsilon log"),
    ),
)
_ANCHORS = ("alpha figure", "a quiet anchor phrase", "delta script", "epsilon log")

_HEAD6 = (
    "Withdrawn and replaced 2026-11-13: the note this replaces named "
    "notes/scripts/diagnose_round11.py and diagnose_round12.py, recorded in "
    "walk/CHECKS-draws-and-threshold.md. Neither of this stage's populations is a section 5 "
    "figure; see 'registered_variant' and 'registered_primary'."
)
_HEAD7 = (
    "The fixture keeps support as binary and stores no q-values, so the figures are not reproduced; "
    "see 'registered_variant'."
)
_ITEMS6 = [
    _HEAD6,
    (
        "walk/FINDINGS.md section 5, share alpha, 20 draws: script notes/scripts/diagnose_round13.py; "
        "home walk/CHECKS-collateral-and-pkm.md; log notes/logs/round13.txt."
    ),
    (
        "walk/FINDINGS.md section 5, count beta, 100 draws: script notes/scripts/diagnose_round10.py; "
        "home walk/CHECKS-ceiling-survives.md; no committed log."
    ),
    (
        "walk/FINDINGS.md section 5, count gamma, 20 draws: script notes/scripts/diagnose_round9.py; "
        "home walk/CHECKS-ceiling-and-floor.md; no committed log."
    ),
]
_ITEMS7 = [
    _HEAD7,
    (
        "walk/FINDINGS.md section 6, ATP1A1 K605's delta, 20 draws: script "
        "notes/scripts/diagnose_round12.py; home walk/CHECKS-draws-and-threshold.md; no committed log."
    ),
    (
        "walk/FINDINGS.md section 6, share epsilon, 20 draws: script "
        "notes/scripts/diagnose_round14.py; home walk/CHECKS-census.md; log notes/logs/round14.txt."
    ),
]


def _with(items: list[str], index: int, old: str, new: str) -> list[str]:
    assert old in items[index], (index, old)
    return [x.replace(old, new) if i == index else x for i, x in enumerate(items)]


NOTE_CASES: dict[str, tuple[int, list[str], list[str]]] = {
    "stage 6, correct": (6, _ITEMS6, []),
    "stage 7, correct": (7, _ITEMS7, []),
    "count, one appended": (6, [*_ITEMS6, _ITEMS6[3]], ["count"]),
    "order, two swapped": (6, [_ITEMS6[0], _ITEMS6[2], _ITEMS6[1], _ITEMS6[3]], ["order"]),
    "scripts, another script": (6, _with(_ITEMS6, 2, "round10.py", "round11.py"), ["scripts"]),
    "section, the other section": (6, _with(_ITEMS6, 2, "section 5", "section 6"), ["section"]),
    "section, both sections": (6, _with(_ITEMS6, 2, "section 5", "sections 5 and 6"), ["section"]),
    "home, another home": (
        6,
        _with(_ITEMS6, 2, "CHECKS-ceiling-survives", "CHECKS-census"),
        ["home"],
    ),
    "log, another log": (6, _with(_ITEMS6, 1, "round13.txt", "round14.txt"), ["log"]),
    "log, also no committed log": (
        6,
        _with(_ITEMS6, 1, "round13.txt.", "round13.txt; no committed log."),
        ["log"],
    ),
    "figure, a digit-free anchor": (
        6,
        _with(_ITEMS6, 0, "see 'registered", "a quiet anchor phrase; see 'registered"),
        ["figure"],
    ),
    "figure, a population size": (
        6,
        _with(_ITEMS6, 0, "Neither of", "Of 791 claims, neither of"),
        ["figure"],
    ),
    "figure, binary as digits": (7, _with(_ITEMS7, 0, "as binary", "as 0/1"), ["figure"]),
    "figure, a line reference": (
        6,
        _with(_ITEMS6, 0, "a section 5 figure", "a walk/FINDINGS.md:109 figure"),
        ["figure"],
    ),
    "reviewer_pointer, the path": (
        7,
        _with(
            _ITEMS7,
            0,
            "are not reproduced",
            "are not reproduced (notes/REVIEWER-MAP-findings-5-and-6.md)",
        ),
        ["reviewer_pointer"],
    ),
    "reviewer_pointer, the token": (
        7,
        _with(_ITEMS7, 0, "are not reproduced", "are not reproduced (REVIEWER-MAP)"),
        ["reviewer_pointer"],
    ),
    "marker, an em dash for the colon": (
        6,
        _with(_ITEMS6, 0, "2026-11-13: ", "2026-11-13 — "),
        ["marker"],
    ),
    "marker, Withdrawn in stage 7": (
        7,
        _with(_ITEMS7, 0, "The fixture", "Withdrawn: the fixture"),
        ["marker"],
    ),
    "marker, withdrawn in stage 7": (
        7,
        _with(_ITEMS7, 0, "are not reproduced", "are withdrawn and not reproduced"),
        ["marker"],
    ),
    "rule, documented": (
        7,
        _with(_ITEMS7, 0, "stores no", "under the documented rule stores no"),
        ["rule"],
    ),
    "rule, Documented": (
        7,
        _with(_ITEMS7, 0, "stores no", "under the Documented rule stores no"),
        ["rule"],
    ),
    "hand_instruments, round13 in the withdrawn clause": (
        6,
        _with(_ITEMS6, 0, "and diagnose_round12.py", "and diagnose_round13.py"),
        ["hand_instruments"],
    ),
    "hand_instruments, round11 after the withdrawn clause": (
        6,
        _with(_ITEMS6, 0, "is a section 5", "is a diagnose_round11.py section 5"),
        ["hand_instruments"],
    ),
    "hand_instruments, a CHECKS document in stage 7": (
        7,
        _with(_ITEMS7, 0, "are not reproduced", "are not reproduced (CHECKS-census.md)"),
        ["hand_instruments"],
    ),
    "keys, stage 6 without registered_primary": (
        6,
        _with(_ITEMS6, 0, " and 'registered_primary'", ""),
        ["keys"],
    ),
}


@pytest.mark.parametrize("name", list(NOTE_CASES))
def test_the_note_checker_returns_exactly_each_cases_kinds(name: str) -> None:
    stage, items, expected = NOTE_CASES[name]
    entries = _E5 if stage == 6 else _E6
    assert [v.kind for v in check_note(items, entries, stage, _ANCHORS)] == expected


def _every_anchor() -> tuple[str, ...]:
    out: list[str] = []
    for e in audit.RECEIPT_MAP:
        out += [e.findings_anchor, e.home_anchor]
        out += [e.script_anchor] if e.script_anchor is not None else []
        out += [e.log[1]] if e.log is not None else []
    return tuple(out)


def test_both_notes_name_their_instruments_and_quote_no_figure(tmp_path: Path) -> None:
    fx = _committed()
    six = audit.stage6_sensitivity(fx, tmp_path)
    seven = audit.stage7_propagation(fx)
    fives = tuple(e for e in audit.RECEIPT_MAP if e.section == 5)
    sixes = tuple(e for e in audit.RECEIPT_MAP if e.section == 6)
    assert check_note(six.not_automated, fives, 6, _every_anchor()) == []
    assert check_note(seven.not_automated, sixes, 7, _every_anchor()) == []
    assert len(six.not_automated) == 9
    assert len(seven.not_automated) == 6


def test_no_anchor_reaches_the_report(tmp_path: Path) -> None:
    """The writer escapes non-ASCII, and round 11's script anchor carries an em dash, so the JSON
    is re-serialised unescaped before it is searched."""
    audit.run(tmp_path, live=False, home=tmp_path / "none")
    markdown = (tmp_path / "audit_PXD018299.md").read_text(encoding="utf-8")
    report = json.loads((tmp_path / "audit_PXD018299.json").read_text(encoding="utf-8"))
    serialised = json.dumps(report, ensure_ascii=False)
    assert not any(a in markdown or a in serialised for a in _every_anchor())
