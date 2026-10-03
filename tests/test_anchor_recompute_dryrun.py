"""The ADR-0037 dry-run instrument can see each failure it reports.

A measurement that returns zero refusals over real ingestion is evidence only if the instrument
can return a non-zero count. So each outcome is planted once here on a real curation change-set and
counted. `walk/` is not a package, so the module is loaded by path.
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from bzk.curation.loader import load_path
from bzk.ontology import keys
from bzk.ontology.invariants import Edge, Node

ROOT = Path(__file__).resolve().parents[1]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "anchor_recompute_dryrun", ROOT / "walk" / "anchor_recompute_dryrun.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dry = _load()

LABEL = dry.NODE_TYPE_KEY


@pytest.fixture(autouse=True)
def _fresh() -> None:
    dry.STATS.clear()
    dry.EXAMPLES.clear()
    dry.PARTIAL.clear()
    vars(dry)["CHANGE_SETS"] = 0


def _record() -> tuple[list[Node], list[Edge]]:
    loaded = load_path(ROOT / "data" / "curation" / "curation_PXD018299.json")
    return copy.deepcopy(loaded.nodes), copy.deepcopy(loaded.edges)


def test_clean_record_recomputes() -> None:
    nodes, edges = _record()
    dry.classify(nodes, edges)
    assert dry.STATS["Sample"]["triggered"] == 12
    assert dry.STATS["Sample"]["recompute_ok"] == 12
    assert dry.STATS["Experiment"]["recompute_ok"] == 1
    assert dry.STATS["Analysis"]["recompute_ok"] == 1


def test_null_door_is_seen() -> None:
    nodes, edges = _record()
    sample = next(n for n in nodes if n[LABEL] == "Sample")
    old = sample["id"]
    new = keys.evidence_id("Sample", sample)  # minted with the Experiment anchor omitted
    sample["id"] = new
    for e in edges:
        for end in ("from", "to"):
            if e[end] == old:
                e[end] = new
    dry.classify(nodes, edges)
    assert dry.STATS["Sample"]["null_door"] == 1
    assert dry.STATS["Sample"]["recompute_ok"] == 11


def test_multi_valued_anchor_is_seen() -> None:
    nodes, edges = _record()
    analysis = next(n for n in nodes if n[LABEL] == "Analysis")
    edges.append({"type": "USED", "from": analysis["id"], "to": "bzk:" + "0" * 32})
    dry.classify(nodes, edges)
    assert dry.STATS["Analysis"]["multi_valued_anchor"] == 1
    assert dry.STATS["Analysis"]["recompute_ok"] == 0


def test_referent_without_anchor_edge_is_exempt() -> None:
    nodes, edges = _record()
    edges = [e for e in edges if e["type"] != "PERFORMED_ON"]
    dry.classify(nodes, edges)
    assert dry.STATS["Sample"]["staged_digest"] == 12
    assert dry.STATS["Sample"]["triggered"] == 0
