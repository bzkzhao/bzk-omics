"""`bzk/audit.py` — the nine-stage report is derived from fixtures, and `--live` says what it did.

**Offline throughout.** The live paths are driven with a stubbed `pxd018299_h10.main` (the module's
own tests drive the real one over synthetic bytes) and, for the graph read, with a small Kùzu graph
written through `store.write_change_set` — the same builder `tests/test_query.py` uses, so the
Cypher is exercised against a shape a producer could emit rather than against hand-written rows.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
