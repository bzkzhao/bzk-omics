"""`bzk/audit_pxd032267.py`: the PXD032267 audit reads the record and computes nothing (prompt 36).

Run on the committed fixtures, and on synthetic twins (copies under `tmp_path`, edited) for the
failure paths. This module may import `bzk.sources.pxd032267_gate` to cross-check the label; the
audit module may not, and two guards below hold it to that: an import whitelist over its AST, and a
fresh interpreter that imports it and inspects `sys.modules`.
"""

import ast
import csv
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from bzk import audit_pxd032267 as audit
from bzk.sources import pxd032267_gate as gate
from bzk.sources.pride import PXD032267_SITES

REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "bzk" / "audit_pxd032267.py"

EXPECTED_MODES = {
    1: "FIXTURE",
    2: "NOT_AVAILABLE",
    3: "FIXTURE",
    4: "FIXTURE",
    5: "FIXTURE",
    6: "FIXTURE",
    7: "NOT_APPLICABLE",
    8: "FIXTURE",
    9: "FIXTURE",
    10: "FIXTURE",
}

#: The attempt-1 result's exploratory block, l.75–85, verbatim (prompt 36 §1.4), plus T1's
#: exploratory third p (bzk's reply to the §0 receipt, point 2). T1's other two exploratory p values
#: equal the published ones and stay allowed. `3.3e-07` is check 2's committed k = 4 figure and is
#: not forbidden.
FORBIDDEN = (
    "6.48e-06",
    "1.40e-02",
    "3.73e-02",
    "4.82e-02",
    "4.80e-02",
    "0.024973",
    "0.012209",
    "0.038545",
    "0.009637",
    "0.004869",
    "0.012531",
    "0.022283",
    "0.018225",
    "0.001693",
    "0.063524",
    "0.019006",
    "0.001872",
    "1.7e-04",
    "2.0e-04",
    "1.0e-04",
    "9.7e-06",
    "3.3e-05",
    "0.049864",
)


def whole_tokens(token: str, text: str) -> list[str]:
    """Occurrences of `token` bounded on both sides by a character outside `[0-9.eE+-]`, or by an
    end of the string."""
    return re.findall(r"(?<![0-9.eE+\-])" + re.escape(token) + r"(?![0-9.eE+\-])", text)


def _twin(tmp_path: Path) -> tuple[Path, Path]:
    fixtures, walk = tmp_path / "fixtures", tmp_path / "walk"
    fixtures.mkdir(parents=True)
    walk.mkdir(parents=True)
    for name in (audit.ATTEMPT1, audit.ATTEMPT2, audit.MARKER):
        shutil.copy(audit.FIXTURES / name, fixtures / name)
    for name in (audit.WALK_RECORD, audit.PUBLISHED_TABLES):
        shutil.copy(audit.WALK / name, walk / name)
    return fixtures, walk


def _edit(path: Path, change: Callable[[dict[str, Any]], None]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")


@pytest.fixture(scope="module")
def report(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Any], Path]:
    out = tmp_path_factory.mktemp("audit-out-pxd032267")
    return audit.run(out, reasons=True), out


def _stage(report: dict[str, Any], number: int) -> dict[str, Any]:
    (stage,) = [s for s in report["stages"] if s["stage"] == number]
    found: dict[str, Any] = stage
    return found


# --------------------------------------------------------------------------------------------
# Modes and the record
# --------------------------------------------------------------------------------------------


def test_every_stage_has_the_mode_prompt_36_gives_it(report: tuple[dict[str, Any], Path]) -> None:
    rep, _ = report
    assert {s["stage"]: s["mode"] for s in rep["stages"]} == EXPECTED_MODES
    assert all(s["reason"].strip() for s in rep["stages"])


def test_every_file_read_is_hashed_walk_files_included(
    report: tuple[dict[str, Any], Path],
) -> None:
    rep, _ = report
    assert sorted(rep["files_read"]) == [
        "tests/fixtures/pxd032267_gate.json",
        "tests/fixtures/pxd032267_gate_attempt2.json",
        "tests/fixtures/pxd032267_gate_attempt2.started.json",
        "walk/PXD032267-published-tables.json",
        "walk/walk_PXD032267.json",
    ]
    assert all(d.startswith("sha256:") for d in rep["files_read"].values())
    # Against digests the record itself commits, not a recomputation of the module's expression.
    marker = json.loads((audit.FIXTURES / audit.MARKER).read_text(encoding="utf-8"))
    attempt2 = json.loads((audit.FIXTURES / audit.ATTEMPT2).read_text(encoding="utf-8"))
    assert (
        rep["files_read"]["tests/fixtures/pxd032267_gate_attempt2.json"] == marker["fixture_sha256"]
    )
    assert (
        rep["files_read"]["tests/fixtures/pxd032267_gate.json"]
        == attempt2["reference_fixture_sha256"]
    )


def test_each_recorded_digest_follows_its_files_bytes(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path / "same")
    before = sorted(audit.load_record(fixtures, walk).digests.items())
    for path in (walk / audit.WALK_RECORD, walk / audit.PUBLISHED_TABLES):
        path.write_bytes(path.read_bytes() + b"\n")
    after = dict(audit.load_record(fixtures, walk).digests)
    changed = sorted(name for name, digest in before if after[name] != digest)
    assert changed == ["PXD032267-published-tables.json", "walk_PXD032267.json"]


def test_the_label_is_the_registrations(report: tuple[dict[str, Any], Path]) -> None:
    rep, _ = report
    assert rep["label"] == gate.attempt2_label()


def test_stage4_reports_rounding_and_check_2_at_full_precision(
    report: tuple[dict[str, Any], Path],
) -> None:
    rep, out = report
    fixture = json.loads((audit.FIXTURES / audit.ATTEMPT2).read_text(encoding="utf-8"))
    committed = [r["abs_delta"] for r in fixture["consistency"]["checks"]["2"]["inputs"]["rows"]]
    figures = _stage(rep, 4)["figures"]["attempt_2"]
    assert figures["rounding_decimals"] == fixture["rounding_decimals"]
    assert [r["abs_delta"] for r in figures["check_2"]["rows"]] == committed
    text = (out / "audit_PXD032267.md").read_text(encoding="utf-8")
    for delta in committed:
        assert repr(delta) in text


def test_stage4_names_the_exploratory_script_without_quoting_it(
    report: tuple[dict[str, Any], Path],
) -> None:
    rep, _ = report
    stage = _stage(rep, 4)
    (note,) = stage["not_automated"]
    assert audit.EXPLORATORY_SCRIPT in note
    assert (REPO / audit.EXPLORATORY_SCRIPT).is_file()
    assert (REPO / audit.ATTEMPT1_RESULT).is_file()
    assert len(stage["not_available"]) == 1


def test_readout_d_is_presented_without_a_verdict(report: tuple[dict[str, Any], Path]) -> None:
    rep, _ = report
    d = _stage(rep, 6)["figures"]["readout_d"]
    keys: list[str] = []

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            keys.extend(node)
            for value in node.values():
                collect(value)

    collect(d)
    assert "verdict" not in keys
    assert "cells" in d["counts"]
    assert "Y8" in d["presented_as"]
    registration = (REPO / audit.REGISTRATION_ATTEMPT2).read_text(encoding="utf-8")
    assert "| Y8 | readout D: reported, not predicted | reported |" in registration


def test_stage5_reads_variant_deltas_from_gate_g(report: tuple[dict[str, Any], Path]) -> None:
    rep, _ = report
    fixture = json.loads((audit.FIXTURES / audit.ATTEMPT2).read_text(encoding="utf-8"))
    variants = _stage(rep, 5)["figures"]["gate"]["variants"]
    for name, v in fixture["gate_g"]["variants"].items():
        assert variants[name]["max_abs_delta_p"] == v["max_abs_delta_p"]


# --------------------------------------------------------------------------------------------
# Stage 1
# --------------------------------------------------------------------------------------------


def test_stage1_raises_when_the_marker_hash_differs(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def wrong(m: dict[str, Any]) -> None:
        m["fixture_sha256"] = "sha256:" + "0" * 64

    _edit(fixtures / audit.MARKER, wrong)
    record = audit.load_record(fixtures, walk)
    with pytest.raises(audit.AuditError, match="marker's fixture_sha256"):
        audit.stage1_sources(record, live=False, home=None)


def test_stage1_compares_digests_without_their_prefix(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def unprefixed(m: dict[str, Any]) -> None:
        m["fixture_sha256"] = m["fixture_sha256"].removeprefix("sha256:")

    _edit(fixtures / audit.MARKER, unprefixed)
    stage = audit.stage1_sources(audit.load_record(fixtures, walk), live=False, home=None)
    assert stage.figures["marker"]["fixture_sha256"].startswith("sha256:")


def test_stage1_raises_on_a_pin_mismatch(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def wrong(f: dict[str, Any]) -> None:
        f["sites_content_hash"] = "sha256:" + "1" * 64

    _edit(fixtures / audit.ATTEMPT1, wrong)
    with pytest.raises(audit.AuditError, match="is not the pin"):
        audit.stage1_sources(audit.load_record(fixtures, walk), live=False, home=None)


def test_stage1_raises_when_the_published_source_digest_differs(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def wrong(p: dict[str, Any]) -> None:
        p["source"]["sha256"] = "2" * 64

    _edit(walk / audit.PUBLISHED_TABLES, wrong)
    with pytest.raises(audit.AuditError, match="published_tables_source_sha256"):
        audit.stage1_sources(audit.load_record(fixtures, walk), live=False, home=None)


def test_stage1_raises_when_attempt_2s_reference_digest_differs(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)
    (fixtures / audit.ATTEMPT1).write_bytes((fixtures / audit.ATTEMPT1).read_bytes() + b"\n")
    with pytest.raises(audit.AuditError, match="reference_fixture_sha256"):
        audit.stage1_sources(audit.load_record(fixtures, walk), live=False, home=None)


def test_stage10_raises_when_the_join_is_not_table_8(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def drop_row(p: dict[str, Any]) -> None:
        p["table_8"]["rows"].pop()

    _edit(walk / audit.PUBLISHED_TABLES, drop_row)
    with pytest.raises(audit.AuditError, match="Table 8"):
        audit.stage10_reasons(audit.load_record(fixtures, walk), tmp_path / "out")


def test_stage10_raises_when_a_deposit_id_is_not_in_the_walk(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)

    def drop_row(w: dict[str, Any]) -> None:
        w["deposit_read"]["join_to_published_claims"]["rows"].pop()

    _edit(walk / audit.WALK_RECORD, drop_row)
    with pytest.raises(audit.AuditError, match="is not in walk_PXD032267.json"):
        audit.stage10_reasons(audit.load_record(fixtures, walk), tmp_path / "out")


def test_a_stage_needs_a_known_mode_and_a_reason() -> None:
    with pytest.raises(audit.AuditError, match="unknown mode"):
        audit.Stage(1, "x", "LIVE-ish", "a reason")
    with pytest.raises(audit.AuditError, match="one-line reason"):
        audit.Stage(1, "x", "NOT_AVAILABLE", " ")


def test_live_records_absent_with_no_store_and_is_not_live(tmp_path: Path) -> None:
    stage = audit.stage1_sources(audit.load_record(), live=True, home=tmp_path)
    assert [f["store"] for f in stage.figures["pinned_files"].values()] == ["ABSENT", "ABSENT"]
    assert stage.mode == "FIXTURE"


def test_live_records_corrupt_and_continues(tmp_path: Path) -> None:
    deposit = PXD032267_SITES
    digest = (deposit.expected_content_hash or "").removeprefix("sha256:")
    planted = tmp_path / "raw" / digest / deposit.filename
    planted.parent.mkdir(parents=True)
    planted.write_bytes(b"not the deposit")
    stage = audit.stage1_sources(audit.load_record(), live=True, home=tmp_path)
    assert stage.figures["pinned_files"][deposit.filename]["store"] == "CORRUPT"
    assert stage.mode == "FIXTURE"


def test_live_is_claimed_only_when_every_file_verifies(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(audit, "verify", lambda digest, *, filename, home: tmp_path)
    stage = audit.stage1_sources(audit.load_record(), live=True, home=tmp_path)
    assert stage.mode == "FIXTURE+LIVE"


# --------------------------------------------------------------------------------------------
# Labels
# --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("path", audit.LABEL_PATHS, ids=lambda p: ".".join(p) or "top")
def test_a_missing_label_at_any_location_raises(tmp_path: Path, path: tuple[str, ...]) -> None:
    fixtures, walk = _twin(tmp_path)

    def drop(f: dict[str, Any]) -> None:
        node = f
        for key in path:
            node = node[key]
        del node["label"]

    _edit(fixtures / audit.ATTEMPT2, drop)
    with pytest.raises(audit.AuditError, match="no label at"):
        audit.load_record(fixtures, walk)


@pytest.mark.parametrize("path", audit.LABEL_PATHS[1:], ids=lambda p: ".".join(p))
def test_a_differing_label_at_any_location_raises(tmp_path: Path, path: tuple[str, ...]) -> None:
    fixtures, walk = _twin(tmp_path)

    def change(f: dict[str, Any]) -> None:
        node = f
        for key in path:
            node = node[key]
        node["label"] = "first attempt"

    _edit(fixtures / audit.ATTEMPT2, change)
    with pytest.raises(audit.AuditError, match="not the fixture's top-level"):
        audit.load_record(fixtures, walk)


def test_the_markers_label_is_a_fourteenth_location(tmp_path: Path) -> None:
    for change in ("drop", "differ"):
        fixtures, walk = _twin(tmp_path / change)

        def edit(m: dict[str, Any], change: str = change) -> None:
            if change == "drop":
                del m["label"]
            else:
                m["label"] = "first attempt"

        _edit(fixtures / audit.MARKER, edit)
        with pytest.raises(audit.AuditError, match="marker"):
            audit.load_record(fixtures, walk)


def test_the_label_paths_are_exactly_the_fixtures(tmp_path: Path) -> None:
    fixture = json.loads((audit.FIXTURES / audit.ATTEMPT2).read_text(encoding="utf-8"))
    found: list[tuple[str, ...]] = []

    def walk(node: Any, path: tuple[str, ...]) -> None:
        if isinstance(node, dict):
            if "label" in node:
                found.append(path)
            for key, value in node.items():
                walk(value, (*path, key))
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(fixture, ())
    assert sorted(found) == sorted(audit.LABEL_PATHS)
    assert len(found) == 13


# --------------------------------------------------------------------------------------------
# Stage 8
# --------------------------------------------------------------------------------------------


def _plant_support(fixtures: Path, default: dict[str, int], masked: dict[str, int]) -> None:
    def plant(f: dict[str, Any]) -> None:
        f["readouts"]["T1"]["readout_b"]["secondary"]["support_out_of_20_at_default_cell"] = default
        f["readout_d"]["readout_b"]["secondary"]["support_out_of_20_at_default_cell"] = masked

    _edit(fixtures / audit.ATTEMPT2, plant)


def test_stage8_selects_exactly_the_planted_claims(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)
    claims = [j["claim"] for j in audit.load_record(fixtures, walk).attempt2["join"]]
    default = dict.fromkeys(claims, 20)
    masked = dict.fromkeys(claims, 20)
    default[claims[0]], masked[claims[0]] = 10, 20  # (b) at the boundary
    default[claims[1]], masked[claims[1]] = 0, 0  # (b), not also (c)
    default[claims[2]], masked[claims[2]] = 11, 10  # (c) at both boundaries
    default[claims[3]], masked[claims[3]] = 11, 11  # neither
    _plant_support(fixtures, default, masked)
    selected = audit.discrepancies(audit.load_record(fixtures, walk))
    assert [(s["rule"], s["claim"]) for s in selected] == [
        ("a", "Filamin-C K2590"),
        ("b", claims[0]),
        ("b", claims[1]),
        ("c", claims[2]),
    ]


def test_stage8_always_includes_readout_c(tmp_path: Path) -> None:
    fixtures, walk = _twin(tmp_path)
    claims = [j["claim"] for j in audit.load_record(fixtures, walk).attempt2["join"]]
    _plant_support(fixtures, dict.fromkeys(claims, 20), dict.fromkeys(claims, 20))
    selected = audit.discrepancies(audit.load_record(fixtures, walk))
    assert [s["rule"] for s in selected] == ["a"]
    assert selected[0]["path"] == "readouts.T1.readout_c"


def test_stage8_says_the_threshold_is_the_audits(report: tuple[dict[str, Any], Path]) -> None:
    rep, _ = report
    figures = _stage(rep, 8)["figures"]
    assert "not a registered threshold" in figures["threshold_is"]


# --------------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------------


def test_the_whole_token_rule() -> None:
    assert whole_tokens("0.024973", "p 0.024973, next") == ["0.024973"]
    assert whole_tokens("0.024973", "0.024973571628308266") == []
    assert whole_tokens("0.024973", "10.024973") == []
    assert whole_tokens("3.3e-07", "3.3e-07") == ["3.3e-07"]
    assert len(FORBIDDEN) == len(set(FORBIDDEN)) == 23
    assert "3.3e-07" not in FORBIDDEN


def test_no_forbidden_token_appears_in_any_output(report: tuple[dict[str, Any], Path]) -> None:
    _, out = report
    written = sorted(out.iterdir())
    assert [p.name for p in written] == [
        "audit_PXD032267.json",
        "audit_PXD032267.md",
        "reasons_PXD032267.csv",
    ]
    hits = {
        p.name: [t for t in FORBIDDEN if whole_tokens(t, p.read_text(encoding="utf-8"))]
        for p in written
    }
    assert {name: found for name, found in hits.items() if found} == {}


def test_the_forbidden_tokens_are_the_exploratory_blocks() -> None:
    block = (REPO / audit.ATTEMPT1_RESULT).read_text(encoding="utf-8").splitlines()[74:85]
    text = "\n".join(block)
    assert all(whole_tokens(t, text) for t in FORBIDDEN)


def test_exploratory_keys_are_never_read(tmp_path: Path) -> None:
    assert "exploratory_" not in MODULE.read_text(encoding="utf-8")
    fixtures, walk = _twin(tmp_path)

    def poison(f: dict[str, Any]) -> None:
        inputs = f["consistency"]["checks"]["3"]["inputs"]
        inputs["exploratory_values"] = "POISON"
        for v in inputs["variants"].values():
            v["exploratory_max_abs_delta_p"] = "POISON"

    _edit(fixtures / audit.ATTEMPT2, poison)
    record = audit.load_record(fixtures, walk)
    stages = [
        audit.stage3_census(record),
        audit.stage4_imputation(record),
        audit.stage5_differential(record),
        audit.stage6_sensitivity(record),
        audit.stage8_discrepancy(record),
    ]
    assert not any("POISON" in json.dumps(s.figures) for s in stages)


def test_reasons_writes_ten_rows_joined_on_id(report: tuple[dict[str, Any], Path]) -> None:
    _, out = report
    with (out / "reasons_PXD032267.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    fixture = json.loads((audit.FIXTURES / audit.ATTEMPT2).read_text(encoding="utf-8"))
    walk = json.loads((audit.WALK / audit.WALK_RECORD).read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in walk["deposit_read"]["join_to_published_claims"]["rows"]}
    assert len(rows) == 10
    assert [r["claim"] for r in rows] == [j["claim"] for j in fixture["join"]]
    assert [int(r["deposit_id"]) for r in rows] == [j["joined_id"] for j in fixture["join"]]
    for row in rows:
        walk_row = by_id[int(row["deposit_id"])]
        assert (row["wt_control_pattern"], row["wt_tac_pattern"]) == (
            walk_row["ctrl"],
            walk_row["tac"],
        )
        assert row["label"] == gate.attempt2_label()
    assert [r["claim"] for r in rows if r["readout_c"]] == ["Filamin-C K2590"]


# --------------------------------------------------------------------------------------------
# Structurally a reader
# --------------------------------------------------------------------------------------------

STDLIB = frozenset(
    {
        "argparse",
        "csv",
        "dataclasses",
        "hashlib",
        "importlib.metadata",
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "typing",
        "datetime",
    }
)
FROM_BZK = {
    "bzk.sources.pride": {"PXD032267_SITES", "PXD032267_PARAMETERS"},
    "bzk.provenance.raw_store": {"verify"},
}
BANNED_NAMES = frozenset({"getattr", "eval", "exec", "__import__", "compile"})
SYS_ATTRIBUTES = frozenset({"argv", "exit", "stderr"})
SUBPROCESS_ATTRIBUTES = frozenset({"CalledProcessError"})


def violations(source: str) -> list[str]:
    """Every import outside the whitelist, every non-`git` subprocess call, every `sys` attribute
    beyond argv/exit/stderr, and every banned builtin, in `source`. Imports and calls are checked;
    string constants never are."""
    tree = ast.parse(source)
    found: list[str] = []
    allowed_values: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in STDLIB or alias.asname is not None:
                    found.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = {a.name for a in node.names}
            aliased = any(a.asname for a in node.names)
            if node.level or aliased:
                found.append(f"from {'.' * node.level}{module} import {sorted(names)}")
            elif module in FROM_BZK:
                if names != FROM_BZK[module]:
                    found.append(f"from {module} import {sorted(names)}")
            elif module not in STDLIB:
                found.append(f"from {module} import {sorted(names)}")
        elif isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "subprocess"
            ):
                allowed_values.add(id(func.value))
                first = node.args[0] if node.args else None
                if not (
                    isinstance(first, ast.List)
                    and first.elts
                    and isinstance(first.elts[0], ast.Constant)
                    and first.elts[0].value == "git"
                ):
                    found.append(f"subprocess.{func.attr} without a ['git', ...] literal")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "sys":
                allowed_values.add(id(node.value))
                if node.attr not in SYS_ATTRIBUTES:
                    found.append(f"sys.{node.attr}")
            elif node.value.id == "subprocess" and node.attr in SUBPROCESS_ATTRIBUTES:
                allowed_values.add(id(node.value))
        if isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES:
            found.append(f"attribute {node.attr}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id in BANNED_NAMES:
                found.append(f"name {node.id}")
            elif node.id in {"subprocess", "sys"} and id(node) not in allowed_values:
                found.append(f"bare {node.id} at line {node.lineno}")
    return found


def test_the_audit_module_passes_the_whitelist() -> None:
    assert violations(MODULE.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(
    ("planted", "expected"),
    [
        ("import numpy", ["import numpy"]),
        ("import importlib", ["import importlib"]),
        ("import json as j", ["import json"]),
        ("from bzk.sources import pxd032267_gate", ["from bzk.sources import ['pxd032267_gate']"]),
        ("from bzk import audit", ["from bzk import ['audit']"]),
        (
            "from bzk.sources.pride import PXD032267_SITES, PXD032267_PARAMETERS, fetch_bytes",
            [
                (
                    "from bzk.sources.pride import ['PXD032267_PARAMETERS', 'PXD032267_SITES', "
                    "'fetch_bytes']"
                )
            ],
        ),
        (
            "from bzk.provenance.raw_store import verify, store",
            ["from bzk.provenance.raw_store import ['store', 'verify']"],
        ),
        ("from importlib import import_module", ["from importlib import ['import_module']"]),
        ("from . import x", ["from . import ['x']"]),
        (
            "import subprocess\nsubprocess.run(['sh', '-c', 'x'])",
            ["subprocess.run without a ['git', ...] literal"],
        ),
        (
            "import subprocess\ncmd = ['git']\nsubprocess.run(cmd)",
            ["subprocess.run without a ['git', ...] literal"],
        ),
        ("import subprocess\nrun = subprocess.run", ["bare subprocess at line 2"]),
        ("import sys\nsys.modules", ["sys.modules"]),
        ("import sys\nsys.path.append('x')", ["sys.path"]),
        ("getattr(x, 'y')", ["name getattr"]),
        ("f = eval", ["name eval"]),
        ("exec('1')", ["name exec"]),
        ("__import__('numpy')", ["name __import__"]),
        ("compile('1', 'f', 'exec')", ["name compile"]),
        ("x = 'readout_d'\ny = 'getattr'", []),
        (
            (
                "import subprocess, sys\nsubprocess.run(['git', 'status'])\nsys.exit(sys.argv)\n"
                "try:\n    pass\nexcept subprocess.CalledProcessError:\n    print(file=sys.stderr)"
            ),
            [],
        ),
    ],
)
def test_the_whitelist_catches_each_planted_shape(planted: str, expected: list[str]) -> None:
    assert violations(planted) == expected


def test_importing_the_audit_loads_no_statistics() -> None:
    probe = (
        "import sys, bzk.audit_pxd032267\n"
        "heavy = sorted(m for m in sys.modules if m.split('.')[0] in "
        "('numpy', 'scipy', 'statistics') or m == 'bzk.stats' or m.startswith('bzk.stats.'))\n"
        "print(heavy)"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True, cwd=REPO
    )
    assert result.stdout.strip() == "[]", result.stdout
