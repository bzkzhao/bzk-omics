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
from bzk.sources import pxd018299_h10 as h10
from bzk.sources import pxd026748_reconstruction as reconstruction

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
