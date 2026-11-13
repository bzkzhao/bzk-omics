"""`python -m bzk.audit` — the PXD018299 research audit, nine stages, one command.

**An operational instrument, not part of the platform.** It sits beside `drift.py`,
`fetch_progress.py` and `published_cascade.py` for the reason those do: nothing in `bzk/` imports it,
so no lint or type target widens. It writes nothing into the graph or the content store.

**It computes; it does not restate.** Every number in the report is derived at run time from a
committed fixture or from the pinned deposit bytes. The prose figures in `walk/FINDINGS.md` are not
inputs, and where a stage's headline figure cannot be derived from what is committed the stage says
`NOT_AUTOMATED` and names the script that produced it — it does not quote the figure (single-source
rule, `CLAUDE.md`).
`RECEIPT_MAP` holds phrases from `walk/FINDINGS.md`, its CHECKS homes, the committed logs and the
scripts as guard data for stages 6 and 7's notes, and the note checker in `tests/test_audit.py`
asserts that no such phrase reaches either note; the draw counts and section numbers those notes
carry, the correction marker's date and the round numbers inside paths are stated conditions, not
derived figures.

**Two modes per stage, always labelled.** `FIXTURE`: derived from `tests/fixtures/*.json`, which
needs no network and no raw store. `LIVE`: re-derived from the pinned bytes under `~/.bzk-omics/raw`
(`--live`). A stage is never reported as LIVE unless its inputs were found and their hashes verified.

    .venv/bin/python -m bzk.audit                     # fixtures only; writes ./audit-out/
    .venv/bin/python -m bzk.audit --live              # verify the store, regenerate attempt 3, read the graph
    .venv/bin/python -m bzk.audit --live --rebuild    # also drop and rebuild the derived stores
    .venv/bin/python -m bzk.audit --out DIR --json    # JSON to stdout as well
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np

from bzk import drift, published_cascade
from bzk.provenance.raw_store import DEFAULT_HOME, verify
from bzk.sources.pride import PXD018299_PROTEIN_GROUPS, PXD018299_SITES
from bzk.sources.protein_groups import SUPP_DATA_1, SUPP_DATA_2, SUPP_DATA_3

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"

H10_FIXTURE = "pxd018299_h10_attempt3.json"
PLATFORM_TARGETS = "pxd018299_platform_targets.json"
WELCH_BASELINE = "pxd018299_welch_baseline.json"
REFUSALS = "pxd018299_refusals.json"
PROTEIN_GROUPS = "pxd018299_protein_groups.json"
CASCADE = "pxd018299_published_cascade.json"

# The registered default cell of the imputation family (bzk/sources/pxd026748_reconstruction.py
# :121-123). Duplicated as three literals only because importing that module pulls the whole
# reconstruction stack; `tests/test_audit.py` asserts the three still agree with the source.
DEFAULT_CELL = (0.3, 1.8, "per_sample")


class ReceiptEntry(NamedTuple):
    """One figure of `walk/FINDINGS.md` sections 5 and 6, and the instrument that produced it.

    `describes` renders into stages 6 and 7's notes. Every other string field is guard data and
    never renders: `findings_anchor`, `home_anchor`, `script_anchor` and the log's anchor are
    phrases the receipt checker finds in their sources. `log` is the log's path and its anchor, so
    "no committed log" is one `None` and cannot be half-filled. `script_anchor` is required exactly
    where the home names more than one script, and picks which of them produced the figure.
    """

    section: int
    findings_anchor: str
    describes: str
    scripts: tuple[str, ...]
    script_anchor: str | None
    home: str
    home_anchor: str
    log: tuple[str, str] | None


# Which instrument produced each figure of walk/FINDINGS.md sections 5 and 6, in the order those
# sections print them. Kept here because a note must identify the figures it disclaims, and the
# figures live in prose that cannot be imported. The anchor fields are guard data and never render:
# only `describes`, the paths and the section reach the report. The receipt checker in
# `tests/test_audit.py` asserts every anchor still occurs in its source and every instrument agrees
# with its home; the note checker there asserts no anchor reaches either note. Derived from
# `notes/REVIEWER-MAP-findings-5-and-6.md` §1, a dated measurement record, and from then on held
# against the primary sources rather than against that record. It is the only maintained copy of
# the figure -> home -> log pairing.
RECEIPT_MAP: tuple[ReceiptEntry, ...] = (
    ReceiptEntry(
        5,
        "210 of 791",
        "share of all published claims whose support changes across draws, documented rule, "
        "20 draws",
        ("notes/scripts/diagnose_round13.py",),
        None,
        "walk/CHECKS-collateral-and-pkm.md",
        "210 of 791",
        ("notes/logs/round13.txt", "210 of 791"),
    ),
    ReceiptEntry(
        5,
        "38.3%",
        "share of claims with an imputed value whose support changes, documented rule, 100 draws",
        ("notes/scripts/diagnose_round11.py",),
        "S and T — both headlines as functions of the draw count",
        "walk/CHECKS-draws-and-threshold.md",
        "38.3%",
        None,
    ),
    ReceiptEntry(
        5,
        "13.7%",
        "floor of support-change instability across the FDR rule family, over claims with an "
        "imputed value, 20 draws",
        ("notes/scripts/diagnose_round10.py",),
        None,
        "walk/CHECKS-ceiling-survives.md",
        "**13.7%** (103 of 751)",
        None,
    ),
    ReceiptEntry(
        5,
        "133 calls",
        "difference in calls between the halved and documented rules, 20 draws",
        ("notes/scripts/diagnose_round9.py",),
        None,
        "walk/CHECKS-ceiling-and-floor.md",
        "133 calls",
        None,
    ),
    ReceiptEntry(
        5,
        "3 are supported in every draw",
        "called-but-unpublished claims supported in every draw, 20 draws",
        ("notes/scripts/diagnose_round10.py",),
        None,
        "walk/CHECKS-ceiling-survives.md",
        "**3** (supported in all 20 draws)",
        None,
    ),
    ReceiptEntry(
        5,
        "6 are supported in none",
        "published-but-uncalled claims supported in no draw, 20 draws",
        ("notes/scripts/diagnose_round10.py",),
        None,
        "walk/CHECKS-ceiling-survives.md",
        "**6** (supported in no draw)",
        None,
    ),
    ReceiptEntry(
        5,
        "9 claims of 791",
        "structural disagreement with the published list, 20 draws",
        ("notes/scripts/diagnose_round10.py",),
        None,
        "walk/CHECKS-ceiling-survives.md",
        "9 of 791 claims",
        None,
    ),
    # The home states no "4" by itself: the figure is this row's last two cells summed, 2
    # structural misses plus 2 structural extras, so the anchor is the whole 100-draw row of the
    # home's §1 table, which occurs there once.
    ReceiptEntry(
        5,
        "4 at 100 draws",
        "structural disagreement with the published list, 100 draws",
        ("notes/scripts/diagnose_round11.py",),
        "S and T — both headlines as functions of the draw count",
        "walk/CHECKS-draws-and-threshold.md",
        "| 100 | **38.3%** | **2** | **2** |",
        None,
    ),
    ReceiptEntry(
        6,
        "+2.664",
        "ATP1A1 K605's statistic, frozen across 20 draws",
        ("notes/scripts/diagnose_round12.py",),
        "id 889: measured in all six columns",
        "walk/CHECKS-draws-and-threshold.md",
        "+2.664 to +2.664",
        None,
    ),
    ReceiptEntry(
        6,
        "0.0144 and 0.0177",
        "ATP1A1 K605's q range, 20 draws",
        ("notes/scripts/diagnose_round12.py",),
        "id 889: measured in all six columns",
        "walk/CHECKS-draws-and-threshold.md",
        "0.0144 to 0.0177",
        None,
    ),
    ReceiptEntry(
        6,
        "one is moved across the cut",
        "fully measured claims whose q range spans the cut, 20 draws",
        ("notes/scripts/diagnose_round13.py",),
        None,
        "walk/CHECKS-collateral-and-pkm.md",
        "of those, q range spans the 0.01 cut",
        ("notes/logs/round13.txt", "their q ranges span the 0.01 cut: 1"),
    ),
    ReceiptEntry(
        6,
        "median 0.0015",
        "median q range of the fully measured claims, 20 draws",
        ("notes/scripts/diagnose_round13.py",),
        None,
        "walk/CHECKS-collateral-and-pkm.md",
        "median 0.0015",
        ("notes/logs/round13.txt", "median 0.0015"),
    ),
    ReceiptEntry(
        6,
        "0.1% to 13%",
        "interval on the rate at which fully measured claims cross the cut, 20 draws",
        ("notes/scripts/diagnose_round14.py",),
        None,
        "walk/CHECKS-census.md",
        "0.1% to 13%",
        ("notes/logs/round14.txt", "0.1% to 13%"),
    ),
)


def _receipt_item(entry: ReceiptEntry) -> str:
    """One `not_automated` item: the figure's description and where it was produced. No anchor."""
    noun = "script" if len(entry.scripts) == 1 else "scripts"
    log = f"log {entry.log[0]}" if entry.log is not None else "no committed log"
    return (
        f"walk/FINDINGS.md section {entry.section}, {entry.describes}: {noun} "
        f"{', '.join(entry.scripts)}; home {entry.home}; {log}."
    )


def _receipt_items(section: int) -> list[str]:
    entries = [e for e in RECEIPT_MAP if e.section == section]
    return [_receipt_item(e) for e in entries]


@dataclass
class Stage:
    number: int
    title: str
    mode: str  # FIXTURE | LIVE | FIXTURE+LIVE | NOT_AUTOMATED
    findings: dict[str, Any] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    not_automated: list[str] = field(default_factory=list)


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip()


def _per_claim_matrix(
    fixture: dict[str, Any],
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    block = fixture["readouts"]["primary"]["per_claim_support"]
    rows: list[dict[str, Any]] = block["rows"]
    support = np.array([r["support"] for r in rows], dtype=int)
    imputed = np.array([bool(r["row_carries_an_imputed_cell"]) for r in rows])
    return rows, support, imputed


def _members(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = fixture["readouts"]["primary"]["per_claim_support"]["members"]
    return members


def _default_columns(members: list[dict[str, Any]]) -> list[int]:
    return [
        i
        for i, m in enumerate(members)
        if (m["width_sd"], m["downshift_sd"], m["scope"]) == DEFAULT_CELL
    ]


# --------------------------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------------------------


#: What `--live` regenerates for stages 3, 4, 6, 7 and 8 (`bzk/sources/pxd018299_h10.py`), and the
#: top-level keys that are expected to differ between two runs of it. Registered before the first
#: run: the regenerated fixture is identical to the committed one in every other key, floats to a
#: relative 1e-9, and any other difference is reported as a difference, never adjusted.
H10_ATTEMPT = 3
IGNORED_TOP_LEVEL = frozenset({"generated_under", "runtime_seconds"})
FLOAT_RTOL = 1e-9


def _diff(a: Any, b: Any, path: str = "") -> list[str]:
    """Where two parsed JSON documents differ, as `path: committed -> regenerated` lines."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: list[str] = []
        for key in sorted(set(a) | set(b)):
            sub = f"{path}.{key}" if path else str(key)
            if key not in a:
                out.append(f"{sub}: absent -> present")
            elif key not in b:
                out.append(f"{sub}: present -> absent")
            else:
                out += _diff(a[key], b[key], sub)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} -> {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            out += _diff(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, float) and isinstance(b, float):
        close = math.isclose(a, b, rel_tol=FLOAT_RTOL, abs_tol=0.0) or (a == b)
        return [] if close else [f"{path}: {a!r} -> {b!r}"]
    return [] if a == b and type(a) is type(b) else [f"{path}: {a!r} -> {b!r}"]


def _regenerate_attempt3(home: Path, work: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the registered attempt 3 into `work` and compare it with the committed fixture.

    Writes nothing under the repository: `main` is given a scratch `fixtures_dir`, into which the
    committed attempt-2 fixture is copied first because attempt 3's rerun-consistency check reads
    it from there. Imported here so the fixture-only path never pays for scipy.
    """
    from bzk.sources import pxd018299_h10 as h10

    scratch = work / "h10"
    scratch.mkdir(parents=True, exist_ok=True)
    attempt_2 = h10.fixture_name_for(2)
    shutil.copy(FIXTURES / attempt_2, scratch / attempt_2)
    started = time.monotonic()
    code = h10.main(home=home, fixtures_dir=scratch, attempt=H10_ATTEMPT, progress=False)
    seconds = round(time.monotonic() - started, 1)
    produced = scratch / h10.fixture_name_for(H10_ATTEMPT)
    regenerated: dict[str, Any] = json.loads(produced.read_text(encoding="utf-8"))
    committed = _load(H10_FIXTURE)
    differences = _diff(
        {k: v for k, v in committed.items() if k not in IGNORED_TOP_LEVEL},
        {k: v for k, v in regenerated.items() if k not in IGNORED_TOP_LEVEL},
    )
    report = {
        "ran": True,
        "return_code": code,
        "seconds": seconds,
        "ignored_keys": sorted(IGNORED_TOP_LEVEL),
        "float_rtol": FLOAT_RTOL,
        "reproduced": code == 0 and not differences,
        "differences": len(differences),
        "first_differences": differences[:20],
    }
    return regenerated, report


def _read_graph(graph: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    """Count and classify the stored `DifferentialResult`s, read-only, by the module's own rule.

    A target is matched to graph proteins two ways, and the union is used: by the symbol on the
    graph's `Gene` nodes, and by the accessions of the sites the committed fixture lists for it.
    The second exists because a symbol is a label that moves: the fixture's `DDX58` is `RIGI` on
    the graph's `Gene` (the HGNC symbol changed after the 2019 search), so a symbol-only match
    called a target with four tested sites absent. The graph keys `Gene` by HGNC id, so identity is
    stable; only the name moved. `symbol_differs` lists every target where the two disagree.
    """
    from bzk.query.graph import connect
    from bzk.sources import pxd018299_differential as differential

    conn = connect(graph)

    def rows(cypher: str, **params: Any) -> list[list[Any]]:
        result: Any = conn.execute(cypher, params) if params else conn.execute(cypher)
        out: list[list[Any]] = []
        while result.has_next():
            out.append(list(result.get_next()))
        return out

    def fixture_proteins(target: dict[str, Any]) -> set[str]:
        ids: set[str] = set()
        for site in target.get("sites", []):
            accession = str(site["site"]).split("#", 1)[0].removeprefix("uniprot:")
            ids |= {f"uniprot:{accession}", f"uniprot:{accession.split('-', 1)[0]}"}
        return ids

    results = rows(
        "MATCH (r:DifferentialResult)-[:RESULT_FOR_SITE]->(o:SiteObservation) "
        "RETURN r.id, r.log2fc, r.adj_p_value, o.candidate_proteins"
    )
    wanted = {str(p) for r in results for p in (r[3] or [])}
    for target in targets:
        wanted |= fixture_proteins(target)
    symbols: dict[str, set[str]] = {}
    if wanted:
        for pid, symbol in rows(
            "MATCH (g:Gene)-[:ENCODES]->(p:Protein) WHERE p.id IN $ids RETURN p.id, g.symbol",
            ids=sorted(wanted),
        ):
            symbols.setdefault(str(pid), set()).add(str(symbol))

    def significant(row: list[Any]) -> bool:
        return bool(
            row[2] is not None
            and row[2] < differential.SIG_ADJ_P
            and row[1] is not None
            and row[1] > differential.SIG_LOG2FC
        )

    status: dict[str, str] = {}
    symbol_differs: dict[str, list[str]] = {}
    for target in targets:
        gene = str(target["gene"])
        by_symbol = {pid for pid, names in symbols.items() if gene in names}
        by_accession = fixture_proteins(target)
        matched = by_symbol | by_accession
        graph_names = sorted({n for pid in by_accession for n in symbols.get(pid, set())})
        if graph_names and gene not in graph_names:
            symbol_differs[gene] = graph_names
        mine = [r for r in results if any(str(p) in matched for p in (r[3] or []))]
        if not mine:
            status[gene] = "absent_from_tested"
        else:
            status[gene] = (
                "recovered" if any(significant(r) for r in mine) else "tested_not_recovered"
            )
    return {
        "results_at_site_grain": len(results),
        "significant_up": sum(1 for r in results if significant(r)),
        "rule": f"adj_p < {differential.SIG_ADJ_P} and log2FC > {differential.SIG_LOG2FC}",
        "target_status": status,
        "symbol_differs": symbol_differs,
    }


def stage1_sources(home: Path, live: bool) -> Stage:
    pinned = {
        "GlyGly site table": (PXD018299_SITES.filename, PXD018299_SITES.expected_content_hash),
        "proteinGroups table": (
            PXD018299_PROTEIN_GROUPS.filename,
            PXD018299_PROTEIN_GROUPS.expected_content_hash,
        ),
        "BJC Supplementary Data 1": (SUPP_DATA_1.filename, SUPP_DATA_1.expected_content_hash),
        "BJC Supplementary Data 2": (SUPP_DATA_2.filename, SUPP_DATA_2.expected_content_hash),
        "BJC Supplementary Data 3": (SUPP_DATA_3.filename, SUPP_DATA_3.expected_content_hash),
    }
    files: dict[str, Any] = {}
    for label, (filename, digest) in pinned.items():
        entry: dict[str, Any] = {
            "filename": filename,
            "pinned_sha256": digest,
            "accession": "PXD018299",
        }
        if live:
            try:
                path = verify(digest or "", filename=filename, home=home)
                entry["store_status"] = "present, hash verified"
                entry["bytes"] = path.stat().st_size
            except FileNotFoundError:
                entry["store_status"] = "ABSENT from store"
            except ValueError as exc:
                entry["store_status"] = f"CORRUPT: {exc}"
        else:
            entry["store_status"] = "not checked (no --live)"
        files[label] = entry
    present = sum(1 for e in files.values() if e["store_status"].startswith("present"))
    stage = Stage(1, "Source verification and ingestion", "LIVE" if live else "FIXTURE")
    stage.findings = {
        "pinned_files": files,
        "verified_in_store": present if live else None,
        "of": len(files),
        "sequence_archive": drift.staleness_line(home) if live else "not checked (no --live)",
    }
    stage.sources = ["bzk/sources/pride.py", "bzk/sources/protein_groups.py", "bzk/drift.py"]
    if not live:
        stage.limitations.append(
            "Pinned hashes are reported but the bytes were not re-hashed. Run with --live on a "
            "machine that holds ~/.bzk-omics/raw."
        )
    return stage


def stage2_graph(rebuild: bool, home: Path) -> Stage:
    refusals = _load(REFUSALS)
    targets = _load(PLATFORM_TARGETS)
    groups = _load(PROTEIN_GROUPS)
    stage = Stage(2, "Evidence graph reconstruction", "FIXTURE")
    pop = targets["population"]
    stage.findings = {
        "site_table_rows": pop["rows_in_file"],
        "after_decoys": pop["after_decoys"],
        "after_localisation": pop["after_localization"],
        "ingested": pop["ingested"],
        "refused": pop["refused"],
        "refusals_by_reason": refusals["counts"],
        "refusal_records": len(refusals["refusals"]),
        "protein_group_ambiguity": [
            {
                "artefact": m["artefact"],
                "column": m["column"],
                "rows": m["rows"],
                "multi_accession_fraction": m["multi_fraction"],
                "max_group_size": m["max_size"],
                "distinct_gene_multi": m["distinct_gene_multi"],
            }
            for m in groups["measurements"]
            if "multi_fraction" in m
        ],
    }
    stage.sources = [f"tests/fixtures/{n}" for n in (REFUSALS, PLATFORM_TARGETS, PROTEIN_GROUPS)]
    stage.limitations.append(
        "Refusals and ambiguity are the committed fixtures' record of the last generating run, "
        "not a rebuild performed now."
    )
    if rebuild:
        started = datetime.now(UTC)
        proc = subprocess.run(
            [sys.executable, "-m", "bzk.rebuild"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        stage.mode = "FIXTURE+LIVE"
        stage.findings["live_rebuild"] = {
            "exit_code": proc.returncode,
            "seconds": round((datetime.now(UTC) - started).total_seconds(), 1),
            "stdout_tail": proc.stdout.strip().splitlines()[-12:],
            "stderr_tail": proc.stderr.strip().splitlines()[-6:],
            "home": str(home),
        }
    return stage


def stage3_census(fixture: dict[str, Any], home: Path | None = None) -> Stage:
    rows, _, imputed = _per_claim_matrix(fixture)
    cascade = _load(CASCADE)["rows"]
    lost: dict[str, int] = {}
    for r in cascade:
        lost[str(r["lost_at"])] = lost.get(str(r["lost_at"]), 0) + 1
    stage = Stage(3, "Published-claim alignment and measurement census", "FIXTURE")
    stage.findings = {
        "published_claims": len(cascade),
        "claims_in_tested_population": len(rows),
        "tested_claims_with_an_imputed_cell": int(imputed.sum()),
        "tested_claims_fully_measured": int((~imputed).sum()),
        "claims_lost_before_test_by_stage": {k: v for k, v in lost.items() if k != "None"},
        "reading": (
            "Counts cover the claims that reach the test. Claims lost earlier never enter the "
            "matrix, and the fixture does not record how many of them are wholly drawn."
        ),
        "drawn_cell_census": (
            _live_drawn_cell_census(home)
            if home is not None
            else "NOT COMPUTED: needs the deposit bytes; run with --live"
        ),
    }
    stage.sources = [f"tests/fixtures/{H10_FIXTURE}", f"tests/fixtures/{CASCADE}"]
    return stage


def whole_column_reference(
    log2: np.ndarray, anchor: dict[str, Any], per_sample: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Each column's drawn cells read against the deposit's WHOLE retained column.

    `readout_c` references the measured deposit values inside the 798 claim rows only (n 56-63 in
    the WT columns). The 2026-09-22 review named the whole retained column as the right reference,
    and it is the one `walk/FINDINGS.md` section 2 quotes (1.76-1.78). `log2` is the deposit's
    six intensity columns in the fixture's order, already log2; the drawn mean and SD are the
    fixture's own, so both references describe the same drawn cells.
    """
    measured = ~np.isnan(log2)
    half = log2.shape[1] // 2
    taken = int(anchor["valid_value_rule"]["taken"])
    keep = np.maximum(measured[:, :half].sum(axis=1), measured[:, half:].sum(axis=1)) >= taken
    out: dict[str, Any] = {}
    for j, (name, drawn) in enumerate(per_sample.items()):
        column = log2[keep, j]
        column = column[~np.isnan(column)]
        if column.size < 2 or not drawn.get("n") or drawn.get("sd") is None:
            out[name] = {"n_reference": int(column.size), "downshift_sd": None, "width_sd": None}
            continue
        sd = float(column.std(ddof=1))
        out[name] = {
            "n_reference": int(column.size),
            "downshift_sd": round((float(column.mean()) - drawn["mean"]) / sd, 3),
            "width_sd": round(drawn["sd"] / sd, 3),
        }
    return out


#: The scan of `notes/scripts/diagnose_round16.py` section LL, as written there: the downshift
#: values (l.107), the fixed width (l.49), the generator's seed (l.104), the simulated draws per
#: value (l.109) and the bootstrap resamples (l.120). `tests/test_audit.py` reads these back out
#: of the script, so the port cannot drift from the run whose log is the committed baseline.
LL_DOWNSHIFTS = (1.0, 1.2, 1.4, 1.6, 1.7, 1.77, 1.8, 1.9, 2.0, 2.2, 2.5)
LL_WIDTH = 0.29
LL_SEED = 0
LL_DRAWS = 200
LL_RESAMPLES = 400


def downshift_band(
    claims: list[tuple[list[float], list[bool], float]],
    column_mean: list[float],
    column_sd: list[float],
    downshifts: tuple[float, ...],
    width: float,
    seed: int,
    *,
    draws: int = LL_DRAWS,
    resamples: int = LL_RESAMPLES,
) -> dict[str, Any]:
    """The downshifts whose simulated fold-change gap is consistent with the published one.

    Each claim is its six published values (KO 1-3, WT 1-3), six `drawn` flags in the same order,
    and its measured-only fold change. Only comparable claims belong here (some cell drawn, both
    arms partly measured); the caller selects them. `column_mean` and `column_sd` are per column,
    in the same order. Ported from `notes/scripts/diagnose_round16.py` section LL, l.101-124, as
    written: one generator for the whole scan, the draw order unchanged, and the bootstrap spread
    drawn from that same generator once per downshift value, after that value's simulation.

    `width` is taken as given and never re-derived: it is the wild-type width route 1 recovered,
    which is one of the reasons the two routes are not independent
    (`walk/CORRECTION-PXD018299-two-route-independence.md`). Reads no file and prints nothing.
    """
    # l.100: the observed gap, published fold change minus measured-only, per claim.
    observed_gaps = [
        (np.mean(values[:3]) - np.mean(values[3:])) - measured_fc
        for values, _, measured_fc in claims
    ]
    observed = float(np.median(observed_gaps))
    rng = np.random.default_rng(seed)
    scan: dict[str, dict[str, Any]] = {}
    band: list[float] = []
    for downshift in downshifts:
        gaps = []
        for _ in range(draws):
            for values, drawn, measured_fc in claims:
                simulated = list(values)
                for position, (mean, sd) in enumerate(zip(column_mean, column_sd, strict=True)):
                    if drawn[position]:
                        simulated[position] = rng.normal(mean - downshift * sd, width * sd)
                gaps.append((np.mean(simulated[:3]) - np.mean(simulated[3:])) - measured_fc)
        predicted = float(np.median(gaps))
        # The sampling spread of the observed median, from the same generator, at THIS value.
        spread = float(
            np.std(
                [
                    np.median(rng.choice(observed_gaps, size=len(observed_gaps)))
                    for _ in range(resamples)
                ]
            )
        )
        consistent = abs(predicted - observed) <= 2 * spread
        if consistent:
            band.append(downshift)
        scan[str(downshift)] = {
            "predicted_median_gap": round(predicted, 3),
            "bootstrap_standard_error": round(spread, 3),
            "consistent": consistent,
        }
    return {
        "comparable_claims": len(claims),
        "observed_median_gap": round(observed, 3),
        "width_sd_given": width,
        "seed": seed,
        "scan": scan,
        "consistent_band": band,
        "consistency_rule": "|predicted - observed| <= 2 x that downshift's bootstrap SE",
    }


def _live_whole_column_reference(fixture: dict[str, Any], home: Path) -> dict[str, Any]:
    """Read the hash-verified deposit and apply `whole_column_reference`; never raises."""
    try:
        from bzk.adapters import maxquant
        from bzk.sources import pxd018299_h10 as h10
        from bzk.sources import pxd026748_reconstruction as reconstruction

        path = verify(
            PXD018299_SITES.expected_content_hash or "",
            filename=PXD018299_SITES.filename,
            home=home,
        )
        rows, column = h10.anchor_population(maxquant.read_table(path))
        anchor = fixture["anchor_matrix"]
        indices, _ = h10.anchor_columns(column, anchor["column_family"])
        raw = np.array([[h10._float_cell(r[i]) for i in indices] for r in rows], dtype=float)
        log2 = reconstruction.log2_zero_as_missing(raw)
        if anchor.get("normalisation") == "median_subtracted":
            log2 = log2 - np.nanmedian(log2, axis=0)
        per = fixture["readouts"]["primary"]["readout_c"]["per_sample"]
        return whole_column_reference(log2, anchor, per)
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - a missing store, or a helper that exits on one, must not sink the report
        return {"NOT COMPUTED": f"{type(exc).__name__}: {exc}"}


def drawn_cell_census(claims: list[tuple[list[float], list[bool]]]) -> dict[str, Any]:
    """Partition the published claims by their drawn cells, and compare the comparable class.

    Each claim is its six published values (KO 1-3, WT 1-3) and six `drawn` flags in the same
    order. Ported from `notes/scripts/diagnose_round14.py` section EE (the classes) and
    `notes/scripts/diagnose_round15.py` section II (the signed gap) as written. Reads no file: the
    drawn rule belongs to the caller (`_live_drawn_cell_census`).
    """
    none_drawn = comparable = arm_drawn = 0
    signed: list[float] = []
    for values, drawn in claims:
        if not any(drawn):
            none_drawn += 1
        elif all(drawn[:3]) or all(drawn[3:]):
            arm_drawn += 1
        else:
            comparable += 1
            ko_measured = [v for v, d in zip(values[:3], drawn[:3], strict=True) if not d]
            wt_measured = [v for v, d in zip(values[3:], drawn[3:], strict=True) if not d]
            published_fc = np.mean(values[:3]) - np.mean(values[3:])
            measured_fc = np.mean(ko_measured) - np.mean(wt_measured)
            signed.append(float(published_fc - measured_fc))
    total = len(claims)
    containing = comparable + arm_drawn
    gap: dict[str, Any] = {"n": len(signed)}
    if signed:
        s = np.array(signed)
        gap |= {
            "signed_quartiles": [
                round(float(np.percentile(s, 25)), 3),
                round(float(np.median(s)), 3),
                round(float(np.percentile(s, 75)), 3),
            ],
            "absolute_median": round(float(np.median(np.abs(s))), 3),
            "published_exceeds_measured_only": int((s > 0).sum()),
        }
    return {
        "published_claims": total,
        "no_drawn_cell": none_drawn,
        "some_drawn_both_arms_measured": comparable,
        "whole_arm_drawn": arm_drawn,
        "containing_a_drawn_cell": {
            "count": containing,
            "of": total,
            "fraction": round(containing / total, 3) if total else None,
        },
        "comparable_gap_published_minus_measured_only_log2": gap,
    }


def _raw_value(row: list[str], column: dict[str, int], name: str) -> float:
    text = row[column[name]].strip() if name in column else ""
    try:
        return float(text)
    except ValueError:
        return 0.0


def _cell_provided(row: list[str], column: dict[str, int], name: str) -> bool:
    """The deposit provides this cell, in the summed column OR at any multiplicity.

    `provided()` of `diagnose_round14.py` section EE and `diagnose_round15.py` section II. A cell
    not provided is drawn.
    """
    if _raw_value(row, column, name) > 0:
        return True
    return any(
        _raw_value(row, column, f"{name}{suffix}") > 0 for suffix in ("___1", "___2", "___3")
    )


def _live_drawn_cell_census(home: Path) -> dict[str, Any]:
    """Read the hash-verified deposit and S1, apply `drawn_cell_census`; never raises.

    S1 is read through `verify`, not `pxd018299_h10._supplement_path`: that one turns a missing
    file into `SystemExit`. The handler below catches `SystemExit` too, but `verify` raises
    `FileNotFoundError`, an ordinary `Exception`, so a missing input becomes this finding's value
    without the wrapper depending on the handler's width to stay alive.
    """
    try:
        from bzk.adapters import maxquant
        from bzk.sources import pxd018299_h10 as h10

        sites_path = verify(
            PXD018299_SITES.expected_content_hash or "",
            filename=PXD018299_SITES.filename,
            home=home,
        )
        rows, column = h10.anchor_population(maxquant.read_table(sites_path))
        index_of = {str(r[column["id"]]).strip(): i for i, r in enumerate(rows)}
        s1_path = verify(
            SUPP_DATA_1.expected_content_hash, filename=SUPP_DATA_1.filename, home=home
        )
        header, s1 = h10._s1_rows(s1_path)
        published_columns = h10.s1_columns(header)
        names = [f"Intensity {arm}_{i}" for arm in (h10.KO_ARM, h10.WT_ARM) for i in h10.REPLICATES]
        claims: list[tuple[list[float], list[bool]]] = []
        for claim in _load(CASCADE)["rows"]:
            row = rows[index_of[str(claim["deposit_id"])]]
            values = [h10._float_cell(s1[int(claim["row"])].get(n)) for n in published_columns]
            drawn = [not _cell_provided(row, column, name) for name in names]
            claims.append((values, drawn))
        return drawn_cell_census(claims) | {
            "read": {
                PXD018299_SITES.filename: f"sha256:{_sha256_path(sites_path)}",
                SUPP_DATA_1.filename: f"sha256:{_sha256_path(s1_path)}",
            },
            "drawn_rule": (
                "a cell is drawn unless the summed intensity column or any of its ___1/___2/___3 "
                "multiplicity columns is > 0"
            ),
        }
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - a missing store, or a helper that exits on one, must not sink the report
        return {"NOT COMPUTED": f"{type(exc).__name__}: {exc}"}


def _live_downshift_band(home: Path) -> dict[str, Any]:
    """Read the hash-verified deposit and S1, apply `downshift_band`; never raises.

    The column statistics (`diagnose_round16.py` l.78-85) and the claim extraction (l.89-100) are
    this wrapper's; the scan is the pure function's. S1 is read through `verify`, not
    `pxd018299_h10._supplement_path`, for the reason `_live_drawn_cell_census` gives.
    """
    try:
        from bzk.adapters import maxquant
        from bzk.sources import pxd018299_h10 as h10

        sites_path = verify(
            PXD018299_SITES.expected_content_hash or "",
            filename=PXD018299_SITES.filename,
            home=home,
        )
        rows, column = h10.anchor_population(maxquant.read_table(sites_path))
        index_of = {str(r[column["id"]]).strip(): i for i, r in enumerate(rows)}
        s1_path = verify(
            SUPP_DATA_1.expected_content_hash, filename=SUPP_DATA_1.filename, home=home
        )
        header, s1 = h10._s1_rows(s1_path)
        published_columns = h10.s1_columns(header)
        names = [f"Intensity {arm}_{i}" for arm in (h10.KO_ARM, h10.WT_ARM) for i in h10.REPLICATES]
        # l.78-85: each column's log2 mean and SD over the anchor population, summed column only.
        column_mean: list[float] = []
        column_sd: list[float] = []
        for name in names:
            values = [math.log2(x) for r in rows if (x := _raw_value(r, column, name)) > 0]
            column_mean.append(float(np.mean(values)))
            column_sd.append(float(np.std(values, ddof=1)))
        # l.89-100. The drawn rule is `_cell_provided`, the multiplicity-aware one: it is route 2's
        # `provided()` (diagnose_round16.py l.67-70). It is NOT route 1's rule, which reads the
        # summed column alone (`cell()` in diagnose_imputation_effects.py), so route 2's drawn
        # cells are a subset of route 1's - the correction's first dependence. Do not reuse this
        # helper for route 1.
        claims: list[tuple[list[float], list[bool], float]] = []
        for claim in _load(CASCADE)["rows"]:
            row = rows[index_of[str(claim["deposit_id"])]]
            cells = [h10._float_cell(s1[int(claim["row"])].get(n)) for n in published_columns]
            drawn = [not _cell_provided(row, column, name) for name in names]
            # The complement of `drawn_cell_census`'s comparable class, as at l.94.
            if not any(drawn) or all(drawn[:3]) or all(drawn[3:]):
                continue
            ko_measured = [v for v, d in zip(cells[:3], drawn[:3], strict=True) if not d]
            wt_measured = [v for v, d in zip(cells[3:], drawn[3:], strict=True) if not d]
            claims.append((cells, drawn, float(np.mean(ko_measured) - np.mean(wt_measured))))
        return downshift_band(claims, column_mean, column_sd, LL_DOWNSHIFTS, LL_WIDTH, LL_SEED) | {
            "column_sd": [round(s, 2) for s in column_sd],
            "read": {
                PXD018299_SITES.filename: f"sha256:{_sha256_path(sites_path)}",
                SUPP_DATA_1.filename: f"sha256:{_sha256_path(s1_path)}",
            },
            "drawn_rule": (
                "a cell is drawn unless the summed intensity column or any of its ___1/___2/___3 "
                "multiplicity columns is > 0"
            ),
        }
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - a missing store, or a helper that exits on one, must not sink the report
        return {"NOT COMPUTED": f"{type(exc).__name__}: {exc}"}


def stage4_imputation(fixture: dict[str, Any], home: Path | None = None) -> Stage:
    block = fixture["readouts"]["primary"]["readout_c"]
    per = block["per_sample"]
    shifts = {k: v["downshift"] for k, v in per.items()}
    stage = Stage(4, "Perseus imputation reconstruction", "FIXTURE")
    stage.findings = {
        "matrix": fixture["readouts"]["primary"]["matrix"],
        "rule": block["rule"],
        "per_sample": {
            k: {
                "n_imputed": v["n"],
                "downshift_sd": round(v["downshift"], 3),
                "width_sd": round(v["width"], 3),
            }
            for k, v in per.items()
        },
        "per_sample_downshift_range": [
            round(min(shifts.values()), 3),
            round(max(shifts.values()), 3),
        ],
        "whole_matrix": {
            "n_imputed": block["whole_matrix"]["n"],
            "downshift_sd": round(block["whole_matrix"]["downshift"], 3),
            "width_sd": round(block["whole_matrix"]["width"], 3),
        },
        "reference_distribution": (
            "per_sample and whole_matrix above are this fixture's readout C: the drawn cells read "
            "against the measured deposit values inside the claim rows only. That is a different "
            "statistic from either route below and should not be read as walk/FINDINGS.md section "
            "2's figure; readout C is superseded (walk/CHECKS-PXD018299-imputation-effects.md:75-77)."
        ),
        "against_whole_deposit_column": (
            _live_whole_column_reference(fixture, home)
            if home is not None
            else "NOT COMPUTED: needs the deposit bytes; run with --live"
        ),
        "downshift_band_from_fold_changes": (
            _live_downshift_band(home)
            if home is not None
            else "NOT COMPUTED: needs the deposit bytes; run with --live"
        ),
        "two_routes": (
            "walk/FINDINGS.md section 2 quotes two recoveries of the downshift. Route 1 is "
            "'against_whole_deposit_column': the SAME drawn cells as readout C, read against each "
            "column's whole retained deposit values; its column-by-column table is "
            "walk/CHECKS-PXD018299-imputation-effects.md:59-66. Route 2 is "
            "'downshift_band_from_fold_changes': the downshifts whose simulated gap between "
            "published and measured-only fold changes is consistent with the observed one; its "
            "figures are in walk/CHECKS-two-route-recovery.md. The two routes are NOT independent "
            "of each other - walk/CORRECTION-PXD018299-two-route-independence.md gives the account."
        ),
    }
    stage.limitations.append(
        "Per-sample downshift differs sharply between arms (the WT columns carry most of the "
        "drawn cells), so a single downshift number hides that structure."
    )
    stage.sources = [f"tests/fixtures/{H10_FIXTURE}"]
    return stage


def stage5_differential(graph: Path | None = None) -> Stage:
    targets = _load(PLATFORM_TARGETS)
    welch = _load(WELCH_BASELINE)
    pop = targets["population"]
    statuses: dict[str, int] = {}
    for t in targets["targets"]:
        statuses[t["status"]] = statuses.get(t["status"], 0) + 1
    stage = Stage(5, "Differential analysis and target recovery", "FIXTURE")
    stage.findings = {
        "tested_sites": pop["tested"],
        "significant_up": pop["significant_up"],
        "values_imputed": pop["n_values_imputed"],
        "values_total": pop["n_values_total"],
        "imputed_fraction": round(pop["n_values_imputed"] / pop["n_values_total"], 4),
        "targets_present": pop["targets_present"],
        "targets_recovered": pop["targets_recovered"],
        "targets_total": len(targets["targets"]),
        "target_status_counts": statuses,
        "welch_baseline_targets": len(welch["targets"]),
        "recovery_rule_note": (
            "platform rule: recovered if any tested site for the target is significant; the "
            "notebook baseline selects best site by log2FC. Different rules - see "
            "python -m bzk.target_recovery_rules."
        ),
    }
    stage.sources = [f"tests/fixtures/{PLATFORM_TARGETS}", f"tests/fixtures/{WELCH_BASELINE}"]
    if graph is not None:
        try:
            read = _read_graph(graph, targets["targets"])
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - a locked or absent graph, or a helper that exits on one, must not sink the report
            stage.findings["live_graph"] = f"NOT READ: {type(exc).__name__}: {exc}"
        else:
            fixture_status = {t["gene"]: t["status"] for t in targets["targets"]}
            read["results_match_fixture_tested"] = read["results_at_site_grain"] == pop["tested"]
            read["significant_up_matches_fixture"] = read["significant_up"] == pop["significant_up"]
            read["targets_differing_from_fixture"] = {
                g: {"graph": st, "fixture": fixture_status[g]}
                for g, st in read["target_status"].items()
                if st != fixture_status[g]
            }
            stage.findings["live_graph"] = read
            stage.mode = "FIXTURE+LIVE"
            stage.limitations.append(
                "The graph read matches a target to proteins by gene symbol and by the accessions "
                "of the fixture's own sites for it, so a target's status here is not independent "
                "of the fixture on which proteins it covers; significance and counts are "
                "recomputed from the graph. symbol_differs lists targets whose name on the graph "
                "is not the fixture's (a renamed gene)."
            )
    return stage


def stage6_sensitivity(fixture: dict[str, Any], out: Path) -> Stage:
    rows, support, imputed = _per_claim_matrix(fixture)
    members = _members(fixture)
    default = _default_columns(members)
    sub = support[:, default]
    freq = sub.mean(axis=1)
    changed = sub.min(axis=1) != sub.max(axis=1)
    every = support.min(axis=1) != support.max(axis=1)
    path = out / "per_claim_selection_frequency.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "published_row",
                "deposit_id",
                "gene_names",
                "carries_imputed_cell",
                "default_cell_frequency",
                "changes_in_default_cell",
                "frequency_all_members",
                "changes_in_family",
            ]
        )
        for i, r in enumerate(rows):
            writer.writerow(
                [
                    r["published_row"],
                    r["deposit_id"],
                    r["gene_names"] or "",
                    int(imputed[i]),
                    round(float(freq[i]), 4),
                    int(changed[i]),
                    round(float(support[i].mean()), 4),
                    int(every[i]),
                ]
            )
    n_changed = int(changed.sum())
    n_claims = int(support.shape[0])
    n_imputed = int(imputed.sum())
    n_changed_imputed = int((changed & imputed).sum())
    stage = Stage(6, "Stochastic imputation sensitivity", "FIXTURE")
    stage.findings = {
        "registered_variant": fixture["readouts"]["primary"]["variant"],
        # The two populations of `readouts.primary.readout_b`, recomputed and named as it names
        # them. Shares unrounded: each is the same int/int division the fixture stored.
        "over_all_claims": {
            "numerator": n_changed,
            "denominator": n_claims,
            "share": n_changed / n_claims,
        },
        "conditional_on_imputation": {
            "numerator": n_changed_imputed,
            "denominator": n_imputed,
            "share": n_changed_imputed / n_imputed,
        },
        # The registered estimand, not a headline: walk/PREREG-PXD018299-H10-attempt3.md:81-82
        # takes the shares over claims whose row carries an imputed value, and
        # walk/PREREG-PXD018299-H10.md:186-187 puts the all-claims share under "Reported, never
        # the headline". The fixture marks no primary; `tests/test_audit.py` guards both lines.
        "registered_primary": "conditional_on_imputation",
        "claims": len(rows),
        "default_cell": {
            "width_sd": DEFAULT_CELL[0],
            "downshift_sd": DEFAULT_CELL[1],
            "scope": DEFAULT_CELL[2],
            "draws": len(default),
        },
        "changing_in_default_cell": int(changed.sum()),
        "changing_in_default_cell_share": round(float(changed.mean()), 4),
        "family_members": len(members),
        "changing_somewhere_in_family": int(every.sum()),
        "supported_in_every_default_draw": int((sub.min(axis=1) == 1).sum()),
        "supported_in_no_default_draw": int((sub.max(axis=1) == 0).sum()),
        "per_claim_csv": str(path),
    }
    stage.not_automated = [
        (
            "Withdrawn and replaced 2026-11-13: the note this replaces attributed the "
            "changing-support count quoted in walk/FINDINGS.md section 5 to "
            "notes/scripts/diagnose_round11.py and diagnose_round12.py, recorded in "
            "walk/CHECKS-draws-and-threshold.md, which is not the instrument that produced it. "
            "Neither population this stage reports is a section 5 figure, and none of section "
            "5's figures is reproduced by this fixture. 'over_all_claims' is over all published "
            "claims, the population of the section 5 headline, so only the rule separates them: "
            "the headline was computed under Perseus's documented FDR rule, and this stage "
            "computes the variant the 'registered_variant' key names. 'conditional_on_imputation', "
            "the population the 'registered_primary' key marks, is over claims with an imputed "
            "value, a different population from the headline's, and is computed under the same "
            "registered variant. Do not quote either as the headline. The items below name the "
            "instrument behind each section 5 figure."
        ),
        *_receipt_items(5),
    ]
    stage.sources = [f"tests/fixtures/{H10_FIXTURE}"]
    return stage


def stage7_propagation(fixture: dict[str, Any]) -> Stage:
    rows, support, imputed = _per_claim_matrix(fixture)
    members = _members(fixture)
    default = _default_columns(members)
    measured = np.where(~imputed)[0]
    moved = []
    for i in measured:
        s = support[i]
        if s.min() != s.max():
            sd = support[i, default]
            moved.append(
                {
                    "published_row": rows[i]["published_row"],
                    "deposit_id": rows[i]["deposit_id"],
                    "gene_names": rows[i]["gene_names"],
                    "supported_in_family": f"{int(s.sum())}/{len(s)}",
                    "supported_in_default_cell": f"{int(sd.sum())}/{len(sd)}",
                }
            )
    stage = Stage(7, "Multiple-testing propagation", "FIXTURE")
    stage.findings = {
        "registered_variant": fixture["readouts"]["primary"]["variant"],
        "fully_measured_claims": len(measured),
        # Support changes, not cut crossings: the fixture keeps support as 0/1 and stores no
        # q-values (the note below), so no q-range reading is possible here.
        "support_changes_in_family": len(moved),
        "support_changes_in_default_cell": sum(
            1
            for m in moved
            if m["supported_in_default_cell"].split("/")[0]
            not in ("0", m["supported_in_default_cell"].split("/")[1])
        ),
        "claims": moved,
        "mechanism": (
            "A fully measured claim has a frozen statistic; any change in its support comes from "
            "draws made for other rows moving the shared FDR threshold."
        ),
    }
    stage.not_automated = [
        (
            "walk/FINDINGS.md section 6's figures are read from per-claim statistics and q-values "
            "across draws, and this fixture cannot produce them: it keeps each claim's support as "
            "binary and stores no q-values. What this stage computes instead is support changes "
            "under the variant the 'registered_variant' key names. No FDR rule is named for section 6's "
            "figures, because none of the documents behind section 6 states the rule they were "
            "computed under. The items below name the instrument behind each section 6 figure."
        ),
        *_receipt_items(6),
    ]
    stage.sources = [f"tests/fixtures/{H10_FIXTURE}"]
    return stage


def stage8_discrepancy(fixture: dict[str, Any]) -> Stage:
    """Per target, both instruments' verdicts side by side, each named.

    The platform path (Welch on the ingested, presence-filtered population) and the attempt-3
    reconstruction (Perseus-shaped test, population chosen to retain the published claim set) are
    different instruments over different populations. A disagreement between them is reported as
    a finding about the instruments, never resolved into one verdict.
    """
    targets = _load(PLATFORM_TARGETS)["targets"]
    groups = _load(PROTEIN_GROUPS)["measurements"]
    recon = fixture["readouts"]["primary"]["readout_d"]
    detail = []
    for t in targets:
        sites = t.get("sites", [])
        best = min(sites, key=lambda s: s["adj_p"]) if sites else None
        r = recon.get(t["gene"])
        recon_text = None if r is None else f"{r['supported']}/{r['claims']} S1 peptides supported"
        platform_ok = t["status"] == "recovered"
        recon_ok = None if r is None else (r["claims"] > 0 and r["supported"] > 0)
        detail.append(
            {
                "gene": t["gene"],
                "platform_path": {
                    "status": t["status"],
                    "tested_sites": len(sites),
                    "best_adj_p": None if best is None else round(best["adj_p"], 4),
                    "best_log2fc": None if best is None else round(best["log2fc"], 3),
                },
                "reconstruction_default_cell": recon_text,
                "instruments_disagree": None if recon_ok is None else platform_ok != recon_ok,
            }
        )
    seen: set[tuple[str, str]] = set()
    ambiguity: list[str] = []
    for m in groups:
        key = (m["artefact"], m.get("column", ""))
        if "multi_fraction" in m and key not in seen:
            seen.add(key)
            ambiguity.append(f"{m['artefact']} [{key[1]}]")
    stage = Stage(8, "Biological discrepancy inspection", "FIXTURE")
    stage.findings = {
        "instruments": {
            "platform_path": "Welch, BH-FDR, ingested + presence-filtered population (stage 5)",
            "reconstruction_default_cell": (
                "attempt-3 Perseus-shaped test, median support over the default cell's draws, "
                "population retains the published claim set (stages 6-7)"
            ),
        },
        "targets": detail,
        "not_recovered_on_platform_path": [
            d["gene"] for d in detail if d["platform_path"]["status"] != "recovered"
        ],
        "instruments_disagree_on": [d["gene"] for d in detail if d["instruments_disagree"]],
        "protein_group_ambiguity_artefacts": ambiguity,
    }
    stage.limitations.append(
        "The two instruments use different populations, so a target can be absent or "
        "non-significant on one and supported on the other. This stage does not adjudicate."
    )
    stage.sources = [f"tests/fixtures/{PLATFORM_TARGETS}", f"tests/fixtures/{H10_FIXTURE}"]
    return stage


def _write_csv(path: Path, header: list[str], records: list[list[Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(records)


def stage10_reasons(out: Path, home: Path, drift_live: bool) -> Stage:
    """Why each published claim, ingested site and target was lost, and what drifted.

    Reasons are the committed fixtures' own codes and sentences, joined; none is composed here.
    """
    cascade = _load(CASCADE)["rows"]
    refusals = _load(REFUSALS)["refusals"]
    targets = _load(PLATFORM_TARGETS)["targets"]
    detail_by_row = {str(r["row"]): r for r in refusals}

    lost = [r for r in cascade if r["lost_at"]]
    matched = 0
    claim_records: list[list[Any]] = []
    for r in lost:
        refusal = detail_by_row.get(str(r["deposit_id"])) if r["lost_at"] == "ingestion" else None
        matched += refusal is not None
        claim_records.append(
            [
                r["row"], r["gene_names"] or "", r["protein"], r["position"], r["deposit_id"],
                r["lost_at"], r["loss_reason"], r["localization_prob"], r["wt_cells_below_21"],
                r["published_log2fc"], r["platform_log2fc"], r["platform_p"],
                r["platform_adj_p"], refusal["detail"] if refusal else "",
            ]
        )  # fmt: skip
    claims_path = out / "rejected_published_claims.csv"
    _write_csv(
        claims_path,
        ["published_row", "gene_names", "protein", "position", "deposit_id", "lost_at",
         "reason_code", "localisation_prob", "wt_cells_below_21", "published_log2fc",
         "platform_log2fc", "platform_p", "platform_adj_p", "refusal_detail"],
        claim_records,
    )  # fmt: skip

    refusal_path = out / "ingestion_refusals.csv"
    _write_csv(
        refusal_path,
        ["site_table_row", "reason", "detail"],
        [[r["row"], r["reason"], r["detail"]] for r in refusals],
    )

    target_records: list[dict[str, Any]] = []
    for t in targets:
        if t["status"] == "recovered":
            continue
        sites = t.get("sites", [])
        target_records.append(
            {
                "gene": t["gene"],
                "status": t["status"],
                "explanation": (
                    "no site of this gene reached the tested population"
                    if not sites
                    else "tested, no site passed the significance rule"
                ),
                "tested_sites": [
                    {"site": x["site"], "log2fc": x["log2fc"], "p": x["p"], "adj_p": x["adj_p"]}
                    for x in sites
                ],
            }
        )

    by_reason: dict[str, int] = {}
    for r in lost:
        key = f"{r['lost_at']}/{r['loss_reason']}"
        by_reason[key] = by_reason.get(key, 0) + 1

    stage = Stage(10, "Reasons for every rejection and non-recovery, and drift", "FIXTURE")
    stage.findings = {
        "published_claims_lost": len(lost),
        "by_stage_and_reason": by_reason,
        "ingestion_losses_joined_to_refusal_detail": matched,
        "ingestion_losses_total": sum(1 for r in lost if r["lost_at"] == "ingestion"),
        "platform_refusals_total": len(refusals),
        "unrecovered_targets": target_records,
        "written": [str(claims_path), str(refusal_path)],
    }
    stage.limitations.append(
        "Reason codes on lost published claims are labels, not sentences; only ingestion "
        "refusals carry prose, and the join is on site-table row."
    )
    stage.sources = [f"tests/fixtures/{n}" for n in (CASCADE, REFUSALS, PLATFORM_TARGETS)]

    if drift_live:
        try:
            report = drift.check(home)

            def kind(d: drift.Drift) -> str:
                if d.entry_type.lower() == "inactive":
                    return "retired"
                return "content_changed" if d.content_changed else "version_only"

            drifts = report.drifts
            kinds = [kind(d) for d in drifts]
            drift_path = out / "sequence_drift.csv"
            _write_csv(
                drift_path,
                ["accession", "archived_sv", "current_sv", "content_changed", "archived_len",
                 "current_len", "entry_type", "kind"],
                [[d.accession, d.cached_sv, d.current_sv if d.current_sv is not None else "",
                  int(d.content_changed), d.stored_len, d.current_len, d.entry_type, k]
                 for d, k in zip(drifts, kinds, strict=True)],
            )  # fmt: skip
            unresolved_path = out / "sequence_drift_unchecked.csv"
            _write_csv(
                unresolved_path,
                ["accession", "archived_sv", "status"],
                [[u.accession, u.cached_sv, u.status] for u in report.unchecked],
            )
            stage.mode = "FIXTURE+LIVE"
            stage.findings["drift"] = {
                "sequences_in_archive": len(drift.archived_sequences(home)),
                "drifted": len(drifts),
                "by_kind": {k: kinds.count(k) for k in sorted(set(kinds))},
                "unchecked": len(report.unchecked),
                "unchecked_by_status": {
                    st: sum(1 for u in report.unchecked if u.status == st)
                    for st in sorted({u.status for u in report.unchecked})
                },
                "meaning": (
                    "A lookup that gave no usable answer is unchecked, not drifted and not clean "
                    f"(bzk.drift retries {drift.RETRIES} times with back-off first). 'retired' is "
                    "UniProt answering Inactive."
                ),
                "written": [str(drift_path), str(unresolved_path)],
                "receipt": "not updated; run python -m bzk.drift to refresh it",
            }
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - network or archive failure, or a helper that exits on one, must not sink the report
            stage.mode = "FIXTURE"
            stage.findings["drift"] = f"NOT RUN: {type(exc).__name__}: {exc}"
    else:
        stage.findings["drift"] = "not run (needs --drift: refetches every archived sequence)"
    return stage


def stage9_report(stages: list[Stage], out: Path, fixtures_read: list[str]) -> dict[str, Any]:
    stages = sorted(stages, key=lambda st: st.number)
    status = _git("status", "--porcelain")
    report: dict[str, Any] = {
        "report_version": 1,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "code_version": {
            "commit": _git("rev-parse", "HEAD"),
            "working_tree_clean": status == "",
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "accession": "PXD018299",
        "fixture_hashes": {n: _sha256_path(FIXTURES / n) for n in sorted(set(fixtures_read))},
        "stages": [
            {
                "stage": s.number,
                "title": s.title,
                "mode": s.mode,
                "findings": s.findings,
                "sources": s.sources,
                "limitations": s.limitations,
                "not_automated": s.not_automated,
            }
            for s in stages
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit_PXD018299.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (out / "audit_PXD018299.md").write_text(render(report), encoding="utf-8")
    return report


def render(report: dict[str, Any]) -> str:
    cv = report["code_version"]
    lines = [
        f"# PXD018299 research audit (report v{report['report_version']})",
        "",
        (
            f"Generated {report['generated_at']} at commit `{cv['commit'][:12]}` "
            f"({'clean' if cv['working_tree_clean'] else 'DIRTY working tree'}), "
            f"Python {cv['python']}, numpy {cv['numpy']}."
        ),
        "",
    ]
    for s in report["stages"]:
        lines += [f"## {s['stage']}. {s['title']}  [{s['mode']}]", ""]
        for k, v in s["findings"].items():
            if isinstance(v, (dict, list)):
                lines.append(f"- **{k}**:")
                lines += [
                    "  ```json",
                    *("  " + ln for ln in json.dumps(v, indent=2).splitlines()),
                    "  ```",
                ]
            else:
                lines.append(f"- **{k}**: {v}")
        for note in s["limitations"]:
            lines.append(f"- _Limitation_: {note}")
        for note in s["not_automated"]:
            lines.append(f"- _NOT_AUTOMATED_: {note}")
        lines += ["", f"Sources: {', '.join(s['sources'])}", ""]
    lines += ["## Fixture hashes (sha256)", ""]
    lines += [f"- `{n}`: `{h}`" for n, h in report["fixture_hashes"].items()]
    return "\n".join(lines) + "\n"


def _mark_regenerated(stage: Stage, *, mixed: bool) -> None:
    stage.mode = "FIXTURE+LIVE" if mixed else "LIVE"
    stage.sources.append(f"regenerated: bzk.sources.pxd018299_h10 attempt {H10_ATTEMPT}")


def run(
    out: Path,
    *,
    live: bool,
    home: Path,
    reasons: bool = False,
    drift_live: bool = False,
    rebuild: bool = False,
) -> dict[str, Any]:
    fixture = _load(H10_FIXTURE)
    reproduction: dict[str, Any] = {"ran": False, "reason": "not --live"}
    regenerated = False
    if live:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                fresh, reproduction = _regenerate_attempt3(home, Path(tmp))
            if reproduction["return_code"] == 0:
                fixture, regenerated = fresh, True
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - a missing store, or a helper that exits on one, must not sink the report
            reproduction = {"ran": False, "error": f"{type(exc).__name__}: {exc}"}
    out.mkdir(parents=True, exist_ok=True)
    builders: list[Callable[[], Stage]] = [
        lambda: stage1_sources(home, live),
        lambda: stage2_graph(rebuild, home),
        lambda: stage3_census(fixture, home if live else None),
        lambda: stage4_imputation(fixture, home if live else None),
        lambda: stage5_differential(home / "graph.kuzu" if live else None),
        lambda: stage6_sensitivity(fixture, out),
        lambda: stage7_propagation(fixture),
        lambda: stage8_discrepancy(fixture),
    ]
    if reasons or drift_live:
        builders.append(lambda: stage10_reasons(out, home, drift_live))
    stages = [b() for b in builders]
    if regenerated:
        for stage in stages:
            if stage.number in (4, 6, 7):
                _mark_regenerated(stage, mixed=False)
            elif stage.number in (3, 8):
                _mark_regenerated(stage, mixed=True)
    read = [
        n for s in stages for src in s.sources for n in [Path(src).name] if (FIXTURES / n).exists()
    ]
    stages.append(
        Stage(
            9,
            "Evidence report and export",
            "LIVE" if reproduction.get("ran") else "FIXTURE",
            findings={
                "written": [str(out / "audit_PXD018299.json"), str(out / "audit_PXD018299.md")],
                "published_claim_cascade_report": "python -m bzk.published_cascade",
                "attempt3_reproduction": reproduction,
            },
            sources=["this module"],
        )
    )
    return stage9_report(stages, out, read)


def main() -> None:
    parser = argparse.ArgumentParser(prog="bzk.audit", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=Path("audit-out"))
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME)
    parser.add_argument(
        "--live",
        action="store_true",
        help="verify the raw store, regenerate attempt 3 into a scratch directory, read the graph",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="with --live, also drop and rebuild the derived stores (this removes the "
        "differential results until bzk.sources.pxd018299_differential is run again)",
    )
    parser.add_argument(
        "--reasons", action="store_true", help="add stage 10: per-item rejection reasons (CSV)"
    )
    parser.add_argument(
        "--drift",
        action="store_true",
        help="add per-accession sequence drift to stage 10 (network; refetches the archive)",
    )
    parser.add_argument("--json", action="store_true", help="print the JSON report to stdout")
    args = parser.parse_args()
    report = run(
        args.out,
        live=args.live,
        home=args.home,
        reasons=args.reasons,
        drift_live=args.drift,
        rebuild=args.rebuild,
    )
    # `published_cascade` is imported for its report; stage 9 points at it rather than copying it.
    _ = published_cascade
    print(json.dumps(report, indent=2, default=str) if args.json else render(report))


if __name__ == "__main__":
    main()
