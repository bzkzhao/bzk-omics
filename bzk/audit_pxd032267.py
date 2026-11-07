"""`python -m bzk.audit_pxd032267` — the PXD032267 audit, ten stages, reading only the record.

**An operational instrument, not part of the platform**, like `bzk/audit.py`: nothing in `bzk/`
imports it, and it writes nothing into the graph or the content store.

**It reads; it does not compute.** This is the one deliberate inversion of `bzk/audit.py`, which
derives its numbers at run time. PXD032267's attempt 2 was final
(`walk/PREREG-PXD032267-gate-attempt2.md` §5), so every figure here is read from the committed
record: the three PXD032267 fixtures under `tests/fixtures/`, `walk/walk_PXD032267.json` and
`walk/PXD032267-published-tables.json`. What it keeps from `bzk/audit.py` is the rule against
restating prose figures: a figure that lives only in prose is `NOT_AUTOMATED`, with its source named
and not quoted. The one operation over figures is stage 8's presentation filter, a threshold that
is the audit's and says so.

**Structurally a reader.** Its imports are a whitelist (`tests/test_audit_pxd032267.py`): it does
not import `bzk.audit` or `bzk.sources.pxd032267_gate`, either of which loads numpy, scipy and
`bzk.stats`, and it never reads the attempt-2 fixture's exploratory keys.

**Modes, always labelled.** `FIXTURE`: read from the committed record. `LIVE` / `FIXTURE+LIVE`: the
pinned bytes under `~/.bzk-omics/raw` were found and their hashes verified (`--live`); a stage is
never reported as LIVE unless they were. `NOT_AUTOMATED`: the figure lives only in prose.
`NOT_AVAILABLE`: nothing committed answers the stage. `NOT_APPLICABLE`: the question does not
arise for this design.

    .venv/bin/python -m bzk.audit_pxd032267              # writes ./audit-out-pxd032267/
    .venv/bin/python -m bzk.audit_pxd032267 --live       # also verify the two pinned deposit files
    .venv/bin/python -m bzk.audit_pxd032267 --reasons    # also stage 10, one CSV row per claim
"""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from bzk.provenance.raw_store import verify
from bzk.sources.pride import PXD032267_PARAMETERS, PXD032267_SITES

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
WALK = REPO_ROOT / "walk"

ATTEMPT1 = "pxd032267_gate.json"
ATTEMPT2 = "pxd032267_gate_attempt2.json"
MARKER = "pxd032267_gate_attempt2.started.json"
WALK_RECORD = "walk_PXD032267.json"
PUBLISHED_TABLES = "PXD032267-published-tables.json"

#: Named, never read: the comparison with other k lives only there and in prose.
EXPLORATORY_SCRIPT = "notes/scripts/explore_pxd032267_gate_only.py"
ATTEMPT1_RESULT = "walk/RESULT-PXD032267-gate-attempt1.md"
REGISTRATION_ATTEMPT2 = "walk/PREREG-PXD032267-gate-attempt2.md"

#: Stage 8's presentation filter. The audit's threshold, not a registered one.
DISCREPANCY_AT_OR_BELOW = 10
DRAWS = 20

FIXTURE = "FIXTURE"
LIVE = "LIVE"
FIXTURE_LIVE = "FIXTURE+LIVE"
NOT_AUTOMATED = "NOT_AUTOMATED"
NOT_AVAILABLE = "NOT_AVAILABLE"
NOT_APPLICABLE = "NOT_APPLICABLE"
MODES = (FIXTURE, LIVE, FIXTURE_LIVE, NOT_AUTOMATED, NOT_AVAILABLE, NOT_APPLICABLE)

#: The 13 places the attempt-2 fixture carries `label` (prompt 36 §1.1). The marker's own `label`
#: is a fourteenth, checked under the same rule.
LABEL_PATHS: tuple[tuple[str, ...], ...] = (
    (),
    ("consistency",),
    ("readouts", "T1"),
    ("readouts", "T1", "readout_a"),
    ("readouts", "T1", "readout_a", "default_cell"),
    ("readouts", "T1", "readout_b"),
    ("readouts", "T1", "readout_b", "secondary"),
    ("readouts", "T1", "readout_c"),
    ("readout_d",),
    ("readout_d", "readout_a"),
    ("readout_d", "readout_a", "default_cell"),
    ("readout_d", "readout_b"),
    ("readout_d", "readout_b", "secondary"),
)


class AuditError(Exception):
    """The record contradicts itself, or a pin. Raised, never downgraded to a note."""


@dataclass
class Stage:
    number: int
    name: str
    mode: str
    reason: str
    figures: dict[str, Any] = field(default_factory=dict)
    not_automated: list[str] = field(default_factory=list)
    not_available: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise AuditError(f"stage {self.number}: unknown mode {self.mode!r}")
        if not self.reason.strip():
            raise AuditError(f"stage {self.number}: a mode carries a one-line reason")


@dataclass
class Record:
    """Everything the audit reads, with the sha256 of every file opened."""

    attempt1: dict[str, Any]
    attempt2: dict[str, Any]
    marker: dict[str, Any]
    walk: dict[str, Any]
    published: dict[str, Any]
    label: str
    files_read: dict[str, str]
    digests: dict[str, str]


# --------------------------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------------------------


def bare(digest: str) -> str:
    """A digest without its `sha256:` prefix — the form digests are compared in."""
    return digest.removeprefix("sha256:")


def prefixed(digest: str) -> str:
    """A digest with its `sha256:` prefix — the form digests are recorded in."""
    return "sha256:" + bare(digest)


def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path, files_read: dict[str, str], digests: dict[str, str]) -> dict[str, Any]:
    raw = path.read_bytes()
    digest = prefixed(hashlib.sha256(raw).hexdigest())
    files_read[_display(path)] = digest
    digests[path.name] = digest
    data: dict[str, Any] = json.loads(raw.decode("utf-8"))
    return data


def _at(block: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any]:
    node = block
    for key in path:
        node = node[key]
    return node


def _where(path: tuple[str, ...]) -> str:
    return ".".join(path) or "<top level>"


def labelled(block: dict[str, Any], where: str, expected: str) -> str:
    """The block's `label`, which must be present and equal the fixture's top-level label."""
    if "label" not in block:
        raise AuditError(f"no label at {where}; every attempt-2 readout carries one")
    if block["label"] != expected:
        raise AuditError(
            f"label at {where} is {block['label']!r}, not the fixture's top-level {expected!r}"
        )
    return expected


def load_record(fixtures: Path = FIXTURES, walk: Path = WALK) -> Record:
    files_read: dict[str, str] = {}
    digests: dict[str, str] = {}
    attempt1 = _read_json(fixtures / ATTEMPT1, files_read, digests)
    attempt2 = _read_json(fixtures / ATTEMPT2, files_read, digests)
    marker = _read_json(fixtures / MARKER, files_read, digests)
    walk_record = _read_json(walk / WALK_RECORD, files_read, digests)
    published = _read_json(walk / PUBLISHED_TABLES, files_read, digests)
    if "label" not in attempt2:
        raise AuditError("no label at <top level> of the attempt-2 fixture")
    label: str = attempt2["label"]
    for path in LABEL_PATHS:
        labelled(_at(attempt2, path), _where(path), label)
    labelled(marker, f"the marker {MARKER}", label)
    return Record(attempt1, attempt2, marker, walk_record, published, label, files_read, digests)


def _claims(record: Record) -> list[dict[str, Any]]:
    join: list[dict[str, Any]] = record.attempt2["join"]
    return join


# --------------------------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------------------------


def _store_status(digest: str, filename: str, home: Path | None) -> str:
    try:
        verify(prefixed(digest), filename=filename, home=home)
    except FileNotFoundError:
        return "ABSENT"
    except ValueError:
        return "CORRUPT"
    return "OK"


def stage1_sources(record: Record, *, live: bool, home: Path | None) -> Stage:
    pins = {
        "sites_content_hash": PXD032267_SITES,
        "parameters_content_hash": PXD032267_PARAMETERS,
    }
    files: dict[str, Any] = {}
    for key, deposit in pins.items():
        pinned = deposit.expected_content_hash or ""
        holders = {
            ATTEMPT1: record.attempt1[key],
            ATTEMPT2: record.attempt2[key],
            MARKER: record.marker[key],
        }
        for holder, digest in holders.items():
            if bare(digest) != bare(pinned):
                raise AuditError(
                    f"{holder} {key} {prefixed(digest)} is not the pin {prefixed(pinned)} "
                    "in bzk/sources/pride.py"
                )
        entry: dict[str, Any] = {
            "filename": deposit.filename,
            "pinned_sha256": prefixed(pinned),
            "equal_in": sorted(holders),
        }
        entry["store"] = (
            _store_status(pinned, deposit.filename, home) if live else "not checked (no --live)"
        )
        files[deposit.filename] = entry

    actual = record.digests[ATTEMPT2]
    claimed = record.marker["fixture_sha256"]
    if record.marker["fixture"] != ATTEMPT2:
        raise AuditError(f"the marker names {record.marker['fixture']!r}, not {ATTEMPT2}")
    if bare(claimed) != bare(actual):
        raise AuditError(
            f"the marker's fixture_sha256 {prefixed(claimed)} is not {ATTEMPT2}'s {actual}"
        )
    reference = record.attempt2["reference_fixture_sha256"]
    attempt1_actual = record.digests[ATTEMPT1]
    if bare(reference) != bare(attempt1_actual):
        raise AuditError(
            f"attempt 2's reference_fixture_sha256 {prefixed(reference)} is not "
            f"{ATTEMPT1}'s {attempt1_actual}"
        )

    source_sha = record.published["source"]["sha256"]
    for holder, block in ((ATTEMPT1, record.attempt1), (ATTEMPT2, record.attempt2)):
        if bare(block["published_tables_source_sha256"]) != bare(source_sha):
            raise AuditError(
                f"{holder} published_tables_source_sha256 is not {PUBLISHED_TABLES}'s "
                f"source.sha256 {prefixed(source_sha)}"
            )

    if live:
        statuses = [e["store"] for e in files.values()]
        verified = statuses.count("OK")
        mode = FIXTURE_LIVE if verified == len(statuses) else FIXTURE
        reason = (
            f"--live: {verified} of {len(statuses)} pinned files verified in the store "
            f"({', '.join(statuses)})"
            + ("" if mode == FIXTURE_LIVE else "; not LIVE, since a file was not verified")
        )
    else:
        mode = FIXTURE
        reason = "pins and record digests compared; the deposit bytes were not re-hashed"
    return Stage(
        1,
        "Sources",
        mode,
        reason,
        figures={
            "label": record.label,
            "pinned_files": files,
            "marker": {
                "fixture": record.marker["fixture"],
                "fixture_sha256": prefixed(claimed),
                "actual_sha256": actual,
                "equal": True,
                "state": record.marker["state"],
            },
            "reference_fixture": {
                "fixture": record.attempt2["reference_fixture"],
                "reference_fixture_sha256": prefixed(reference),
                "actual_sha256": attempt1_actual,
                "equal": True,
            },
            "published_tables_source": {
                "artefact": record.published["source"]["artefact"],
                "sha256": prefixed(source_sha),
                "equal_in": [ATTEMPT1, ATTEMPT2, PUBLISHED_TABLES],
            },
        },
        sources=["bzk/sources/pride.py", ATTEMPT1, ATTEMPT2, MARKER, PUBLISHED_TABLES],
    )


def stage2_graph() -> Stage:
    return Stage(
        2,
        "Graph",
        NOT_AVAILABLE,
        "PXD032267 is not ingested, and no handoff orders it",
        not_available=[
            (
                "Ingestion would need a curation record, the adapter run and the first Mus "
                "musculus resolution. The platform line (notes/REVIEWER-HANDOFF-2026-11-07.md §5 "
                "item 6, carrying notes/REVIEWER-HANDOFF-2026-10-10.md §6 (B)) names PXD018299's "
                "IP ingestion as the next platform item."
            )
        ],
        sources=["notes/REVIEWER-HANDOFF-2026-11-07.md", "notes/REVIEWER-HANDOFF-2026-10-10.md"],
    )


def stage3_census(record: Record) -> Stage:
    a2 = record.attempt2
    rule = a2["valid_value_rule"]
    check_1 = a2["consistency"]["checks"]["1"]
    return Stage(
        3,
        "Census",
        FIXTURE,
        "population, join and valid-value rule read from the attempt-2 fixture",
        figures={
            "label": record.label,
            "population": a2["population"],
            "join": [
                {
                    "claim": j["claim"],
                    "key_p_ids": j["key_p_ids"],
                    "key_n_ids": j["key_n_ids"],
                    "joined_id": j["joined_id"],
                    "decided_by": j["decided_by"],
                }
                for j in _claims(record)
            ],
            "valid_value_rule": {
                "candidates": rule["candidates"],
                "taken": rule["taken"],
                "retains_every_claim": rule["retains_every_claim"],
                "claims_lost": rule["claims_lost"],
                "rows_reaching_imputation": rule["rows_reaching_imputation"],
            },
            "check_1": {
                "label": labelled(a2["consistency"], "consistency", record.label),
                "check": check_1["check"],
                "inputs": check_1["inputs"],
                "passed": check_1["passed"],
                "reason": check_1["reason"],
            },
        },
        sources=[ATTEMPT2],
    )


def stage4_imputation(record: Record) -> Stage:
    a1_gate = record.attempt1["gate_g"]
    a2 = record.attempt2
    check_2 = a2["consistency"]["checks"]["2"]
    return Stage(
        4,
        "Imputation and input fidelity",
        FIXTURE,
        "attempt 1's input check and attempt 2's rounding and check 2, read from the fixtures",
        figures={
            "attempt_1": {
                "source": f"{ATTEMPT1} (attempt 1 carries no label; it ended at the input check)",
                "status": a1_gate["status"],
                "result": a1_gate["result"],
                "tolerance": a1_gate["input_check"]["tolerance"],
                "input_deltas": [
                    {"claim": r["claim"], "abs_delta": r["abs_delta"], "passes": r["passes"]}
                    for r in a1_gate["input_check"]["rows"]
                ],
            },
            "attempt_2": {
                "label": record.label,
                "rounding_decimals": a2["rounding_decimals"],
                "input_tolerance": a2["input_tolerance"],
                "check_2": {
                    "label": labelled(a2["consistency"], "consistency", record.label),
                    "check": check_2["check"],
                    "tolerance": check_2["inputs"]["tolerance"],
                    "rows": check_2["inputs"]["rows"],
                    "conditions": check_2["conditions"],
                    "passed": check_2["passed"],
                },
            },
        },
        not_automated=[
            (
                f"The comparison with other k (3 and 5): produced by {EXPLORATORY_SCRIPT} and "
                f"reported in {ATTEMPT1_RESULT}'s exploratory block. Not quoted here."
            )
        ],
        not_available=[
            (
                "The published-draw estimate: no post-imputation matrix is published, so there "
                "is nothing to compare a draw against."
            )
        ],
        sources=[ATTEMPT1, ATTEMPT2],
    )


def _cells(default_cell: dict[str, Any], *, with_verdict: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for comparison, directions in default_cell["cells"].items():
        for direction, cell in directions.items():
            entry: dict[str, Any] = {
                "published": cell["published"],
                "median": cell["median"],
                "range": [cell["minimum"], cell["maximum"]],
            }
            if with_verdict:
                entry["verdict"] = cell["verdict"]
            out[f"{comparison}, {direction}"] = entry
    return out


def stage5_differential(record: Record) -> Stage:
    gate = record.attempt2["gate_g"]
    t1 = record.attempt2["readouts"]["T1"]
    readout_a = t1["readout_a"]
    default_cell = readout_a["default_cell"]
    where = "readouts.T1.readout_a"
    return Stage(
        5,
        "Differential",
        FIXTURE,
        "gate G and readout A read from the attempt-2 fixture",
        figures={
            "gate": {
                "label": record.label,
                "status": gate["status"],
                "primary": gate["primary"],
                "passing": gate["passing"],
                "variants": {
                    name: {"max_abs_delta_p": v["max_abs_delta_p"], "passes": v["passes"]}
                    for name, v in gate["variants"].items()
                },
            },
            "readout_a": {
                "label": labelled(readout_a, where, record.label),
                "default_cell_label": labelled(default_cell, where + ".default_cell", record.label),
                "variant": t1["variant"],
                "headline": default_cell["headline"],
                "cells": _cells(default_cell, with_verdict=True),
            },
        },
        sources=[ATTEMPT2],
    )


def _readout_b(block: dict[str, Any], where: str, label: str, *, verdict: bool) -> dict[str, Any]:
    secondary = block["secondary"]
    out: dict[str, Any] = {"label": labelled(block, where, label)}
    if verdict:
        out |= {
            "verdict": block["verdict"],
            "share": block["share"],
            "exposure": block["exposure"],
            "exposure_size": block["exposure_size"],
            "claims_whose_support_differs": block["claims_whose_support_differs"],
            "power_flag": block["power_flag"],
        }
    out["secondary"] = {
        "label": labelled(secondary, where + ".secondary", label),
        "support_out_of_20_at_default_cell": secondary["support_out_of_20_at_default_cell"],
        "family_categories": secondary["family_categories"],
    }
    if verdict:
        out["secondary"] |= {
            "whole_population_per_cell": secondary["whole_population_per_cell"],
            "whole_population_any_cell": secondary["whole_population_any_cell"],
        }
    return out


def stage6_sensitivity(record: Record) -> Stage:
    t1 = record.attempt2["readouts"]["T1"]
    d = record.attempt2["readout_d"]
    label = record.label
    return Stage(
        6,
        "Sensitivity",
        FIXTURE,
        "readout B, and readout D as a sensitivity analysis, read from the attempt-2 fixture",
        figures={
            "readout_b": _readout_b(t1["readout_b"], "readouts.T1.readout_b", label, verdict=True),
            "readout_d": {
                "label": labelled(d, "readout_d", label),
                "presented_as": (
                    "a sensitivity analysis, registered 'reported, not predicted' (Y8, "
                    f"{REGISTRATION_ATTEMPT2} §4); never as a verdict"
                ),
                "variant": d["variant"],
                "cells_masked": d["cells_masked"],
                "valid_value_rule_taken": d["valid_value_rule"]["taken"],
                "valid_value_rule_changed": d["valid_value_rule_changed"],
                "rows_reaching_imputation": d["valid_value_rule"]["rows_reaching_imputation"],
                "counts": {
                    "label": labelled(d["readout_a"], "readout_d.readout_a", label),
                    "default_cell_label": labelled(
                        d["readout_a"]["default_cell"], "readout_d.readout_a.default_cell", label
                    ),
                    "cells": _cells(d["readout_a"]["default_cell"], with_verdict=False),
                },
                "per_claim": _readout_b(
                    d["readout_b"], "readout_d.readout_b", label, verdict=False
                ),
            },
        },
        sources=[ATTEMPT2],
    )


def stage7_propagation() -> Stage:
    return Stage(
        7,
        "Propagation",
        NOT_APPLICABLE,
        "T1's Tukey adjustment is within a site, not across sites: no cross-site q to propagate",
        sources=[REGISTRATION_ATTEMPT2],
    )


def discrepancies(record: Record) -> list[dict[str, Any]]:
    """Stage 8's selection: (a) readout C always; (b) default support ≤ 10 of 20; (c) support ≤ 10
    under the MBR mask while > 10 by default. A filter over committed figures, nothing more."""
    label = record.label
    t1 = record.attempt2["readouts"]["T1"]
    readout_c = t1["readout_c"]
    default = t1["readout_b"]["secondary"]["support_out_of_20_at_default_cell"]
    masked = record.attempt2["readout_d"]["readout_b"]["secondary"][
        "support_out_of_20_at_default_cell"
    ]
    selected: list[dict[str, Any]] = [
        {
            "rule": "a",
            "path": "readouts.T1.readout_c",
            "claim": readout_c["target"],
            "comparison": readout_c["comparison"],
            "direction": readout_c["direction"],
            "supported_draws": readout_c["supported_draws"],
            "of": readout_c["of"],
            "label": labelled(readout_c, "readouts.T1.readout_c", label),
            "described_as": "the paper's stated downregulation of its headline target",
        }
    ]
    for j in _claims(record):
        claim = j["claim"]
        if default[claim] <= DISCREPANCY_AT_OR_BELOW:
            selected.append(
                {
                    "rule": "b",
                    "path": "readouts.T1.readout_b.secondary.support_out_of_20_at_default_cell",
                    "claim": claim,
                    "support_default": default[claim],
                    "of": DRAWS,
                    "label": label,
                }
            )
        elif masked[claim] <= DISCREPANCY_AT_OR_BELOW:
            selected.append(
                {
                    "rule": "c",
                    "path": "readout_d.readout_b.secondary.support_out_of_20_at_default_cell",
                    "claim": claim,
                    "support_default": default[claim],
                    "support_mbr_masked": masked[claim],
                    "of": DRAWS,
                    "label": label,
                    "described_as": "support collapses under the MBR sensitivity",
                }
            )
    return selected


def stage8_discrepancy(record: Record) -> Stage:
    selected = discrepancies(record)
    return Stage(
        8,
        "Discrepancy",
        FIXTURE,
        "a presentation filter over figures already in the record (prompt 36 §2.1)",
        figures={
            "label": record.label,
            "threshold": f"support at or below {DISCREPANCY_AT_OR_BELOW} of {DRAWS}",
            "threshold_is": "this audit's presentation filter, not a registered threshold",
            "rules": {
                "a": "fixed inclusion: readouts.T1.readout_c",
                "b": "readouts.T1.readout_b.secondary.support_out_of_20_at_default_cell <= 10",
                "c": (
                    "readout_d.readout_b.secondary.support_out_of_20_at_default_cell <= 10 and "
                    "(b)'s field > 10"
                ),
            },
            "selected": selected,
        },
        sources=[ATTEMPT2],
    )


def stage10_reasons(record: Record, out: Path) -> Stage:
    rows_by_id = {
        r["id"]: r for r in record.walk["deposit_read"]["join_to_published_claims"]["rows"]
    }
    table_8 = {f"{r['protein_name']} K{r['position']}" for r in record.published["table_8"]["rows"]}
    claims = _claims(record)
    if {j["claim"] for j in claims} != table_8 or len(claims) != len(table_8):
        raise AuditError("the attempt-2 join's claims are not Table 8's claims")
    t1 = record.attempt2["readouts"]["T1"]
    secondary = t1["readout_b"]["secondary"]
    masked = record.attempt2["readout_d"]["readout_b"]["secondary"]
    readout_c = t1["readout_c"]
    path = out / "reasons_PXD032267.csv"
    columns = [
        "claim",
        "deposit_id",
        "wt_control_pattern",
        "wt_tac_pattern",
        "support_default",
        "family",
        "support_mbr_masked",
        "family_mbr_masked",
        "readout_c",
        "label",
    ]
    out.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for j in claims:
            claim, deposit_id = j["claim"], j["joined_id"]
            if deposit_id not in rows_by_id:
                raise AuditError(f"deposit id {deposit_id} ({claim}) is not in {WALK_RECORD}")
            walk_row = rows_by_id[deposit_id]
            c = ""
            if claim == readout_c["target"]:
                c = (
                    f"{readout_c['direction']} in {readout_c['comparison']}: "
                    f"{readout_c['supported_draws']} of {readout_c['of']} draws"
                )
            writer.writerow(
                {
                    "claim": claim,
                    "deposit_id": deposit_id,
                    "wt_control_pattern": walk_row["ctrl"],
                    "wt_tac_pattern": walk_row["tac"],
                    "support_default": secondary["support_out_of_20_at_default_cell"][claim],
                    "family": secondary["family_categories"]["by_claim"][claim],
                    "support_mbr_masked": masked["support_out_of_20_at_default_cell"][claim],
                    "family_mbr_masked": masked["family_categories"]["by_claim"][claim],
                    "readout_c": c,
                    "label": record.label,
                }
            )
    return Stage(
        10,
        "Reasons",
        FIXTURE,
        "one row per Table 8 claim, joined on deposit id",
        figures={
            "label": record.label,
            "written": str(path),
            "rows": len(claims),
            "join": f"{WALK_RECORD} rows' id = the attempt-2 join's joined_id",
            "patterns": record.walk["deposit_read"]["join_to_published_claims"]["ctrl_tac_legend"],
        },
        sources=[ATTEMPT2, WALK_RECORD, PUBLISHED_TABLES],
    )


# --------------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------------


def _git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


def _version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "not installed"


def write_report(stages: list[Stage], record: Record, out: Path) -> dict[str, Any]:
    stages = sorted(stages, key=lambda s: s.number)
    report: dict[str, Any] = {
        "report_version": 1,
        "accession": "PXD032267",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "code_version": {
            "commit": _git("rev-parse", "HEAD"),
            "working_tree_clean": _git("status", "--porcelain") == "",
            "bzk-omics": _version("bzk-omics"),
        },
        "record_generated_under": record.attempt2["generated_under"],
        "label": record.label,
        "files_read": dict(sorted(record.files_read.items())),
        "stages": [
            {
                "stage": s.number,
                "name": s.name,
                "mode": s.mode,
                "reason": s.reason,
                "figures": s.figures,
                "not_automated": s.not_automated,
                "not_available": s.not_available,
                "sources": s.sources,
            }
            for s in stages
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit_PXD032267.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    (out / "audit_PXD032267.md").write_text(render(report), "utf-8")
    return report


def render(report: dict[str, Any]) -> str:
    cv = report["code_version"]
    lines = [
        f"# PXD032267 audit (report v{report['report_version']})",
        "",
        (
            f"Generated {report['generated_at']} at commit `{cv['commit'][:12]}` "
            f"({'clean' if cv['working_tree_clean'] else 'DIRTY working tree'}), "
            f"bzk-omics {cv['bzk-omics']}. Read from the record; nothing here is computed."
        ),
        "",
        f"Every attempt-2 figure carries the label *{report['label']}*.",
        "",
        "| Stage | Name | Mode | Reason |",
        "|---|---|---|---|",
        *(
            f"| {s['stage']} | {s['name']} | `{s['mode']}` | {s['reason']} |"
            for s in report["stages"]
        ),
        "",
    ]
    for s in report["stages"]:
        lines += [f"## {s['stage']}. {s['name']}  [{s['mode']}]", "", f"_{s['reason']}_", ""]
        for key, value in s["figures"].items():
            if isinstance(value, dict | list):
                lines += [f"- **{key}**:", "  ```json"]
                lines += ["  " + ln for ln in json.dumps(value, indent=2).splitlines()]
                lines.append("  ```")
            else:
                lines.append(f"- **{key}**: {value}")
        lines += [f"- _NOT_AUTOMATED_: {note}" for note in s["not_automated"]]
        lines += [f"- _NOT_AVAILABLE_: {note}" for note in s["not_available"]]
        lines += ["", f"Sources: {', '.join(s['sources'])}", ""]
    lines += ["## Files read (sha256)", ""]
    lines += [f"- `{name}`: `{digest}`" for name, digest in report["files_read"].items()]
    return "\n".join(lines) + "\n"


def run(
    out: Path,
    *,
    live: bool = False,
    home: Path | None = None,
    reasons: bool = False,
    fixtures: Path = FIXTURES,
    walk: Path = WALK,
) -> dict[str, Any]:
    record = load_record(fixtures, walk)
    stages = [
        stage1_sources(record, live=live, home=home),
        stage2_graph(),
        stage3_census(record),
        stage4_imputation(record),
        stage5_differential(record),
        stage6_sensitivity(record),
        stage7_propagation(),
        stage8_discrepancy(record),
    ]
    if reasons:
        stages.append(stage10_reasons(record, out))
    stages.append(
        Stage(
            9,
            "Report",
            FIXTURE,
            "this report, with the sha256 of every file read",
            figures={
                "written": [str(out / "audit_PXD032267.json"), str(out / "audit_PXD032267.md")]
            },
            sources=["this module"],
        )
    )
    return write_report(stages, record, out)


def main() -> None:
    parser = argparse.ArgumentParser(prog="bzk.audit_pxd032267", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=Path("audit-out-pxd032267"))
    parser.add_argument("--home", type=Path, default=None, help="raw-store home (--live only)")
    parser.add_argument("--live", action="store_true", help="verify the two pinned deposit files")
    parser.add_argument("--reasons", action="store_true", help="add stage 10: one row per claim")
    parser.add_argument("--json", action="store_true", help="print the JSON report to stdout")
    args = parser.parse_args(sys.argv[1:])
    try:
        report = run(args.out, live=args.live, home=args.home, reasons=args.reasons)
    except AuditError as exc:
        print(f"audit refused: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(report, indent=2) if args.json else render(report))


if __name__ == "__main__":
    main()
