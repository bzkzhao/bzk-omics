"""Dry run of ADR-0037's generalised I21 over real change-sets.

This is **measurement only. It enforces nothing and writes nothing of its own.**

It wraps `bzk.ontology.invariants.validate`, the call every `store.write_change_set` makes, so
each change-set the real ingestion validates is also classified under the rule ADR-0037 proposes.
The wrap is report-only: `invariants.validate` still runs unchanged and still refuses what it
refused before.

The rule being measured is this. When a change-set carries an anchor edge incident to a
digest-shaped node of an anchored label, the node's id must equal `evidence_id` recomputed from
three things:
- its identifying fields;
- every anchor edge of its label present in that change-set;
- its children, for `Analysis`.

Edge-triggered, as I21 is. A node re-staged as a referent with no anchor edge is not examined.

Usage:

    uv run python walk/anchor_recompute_dryrun.py curation   # in-memory, the four curation records
    uv run python walk/anchor_recompute_dryrun.py rebuild    # python -m bzk.rebuild, wrapped
    uv run python walk/anchor_recompute_dryrun.py differential   # pxd018299_differential, wrapped

`rebuild` and `differential` touch `~/.bzk-omics/` exactly as the unwrapped commands do. Run them
where those commands are normally run, in that order.

Blind: the output is counts per label and per outcome. No accession, gene name or value is printed.
At most three example ids per outcome are printed, and they are digests.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from bzk.ontology import invariants, keys, schema

NODE_TYPE_KEY = invariants.NODE_TYPE_KEY
REL = {r.name: r for r in schema.REL_TABLES}

#: (anchored label) -> list of (anchor label, rel name, anchored-is-source)
ORIENT: dict[str, list[tuple[str, str, bool]]] = defaultdict(list)
for _label, _spec in schema.IDENTITY.items():
    for _alabel, _rel in _spec.anchors:
        _pairs = REL[_rel].pairs
        if (_label, _alabel) in _pairs:
            ORIENT[_label].append((_alabel, _rel, True))
        elif (_alabel, _label) in _pairs:
            ORIENT[_label].append((_alabel, _rel, False))
        else:  # pragma: no cover - schema guard
            raise SystemExit(f"anchor {_label}->{_alabel} via {_rel} matches no declared pair")

OUTCOMES = (
    "staged_digest",
    "triggered",
    "recompute_ok",
    "null_door",
    "mismatch",
    "multi_valued_anchor",
    "unresolved_counterpart",
)
STATS: dict[str, Counter[str]] = defaultdict(Counter)
EXAMPLES: dict[tuple[str, str], list[str]] = defaultdict(list)
PARTIAL: Counter[tuple[str, frozenset[str]]] = Counter()
CHANGE_SETS = 0


def _note(label: str, outcome: str, node_id: str) -> None:
    STATS[label][outcome] += 1
    quiet = outcome in ("staged_digest", "triggered", "recompute_ok")
    if not quiet and len(EXAMPLES[(label, outcome)]) < 3:
        EXAMPLES[(label, outcome)].append(node_id)


def classify(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
    global CHANGE_SETS
    CHANGE_SETS += 1
    by_id = {n["id"]: n for n in nodes}
    by_rel: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in edges:
        by_rel[e["type"]].append(e)

    for node in nodes:
        label = node.get(NODE_TYPE_KEY)
        if label not in ORIENT or not keys.is_digest_id(node.get("id")):
            continue
        nid = node["id"]
        _note(label, "staged_digest", nid)

        found: dict[str, set[str]] = defaultdict(set)
        unresolved = False
        for alabel, rel, anchored_is_src in ORIENT[label]:
            for e in by_rel.get(rel, ()):
                mine, other = (e["from"], e["to"]) if anchored_is_src else (e["to"], e["from"])
                if mine != nid:
                    continue
                if len(REL[rel].pairs) > 1:  # e.g. PROTEIN_ASSIGNMENT_FOR: label the counterpart
                    other_node = by_id.get(other)
                    if other_node is None:
                        unresolved = True
                        continue
                    if other_node.get(NODE_TYPE_KEY) != alabel:
                        continue
                found[alabel].add(other)
        if not found and not unresolved:
            continue  # re-staged referent: I21's own exemption, kept
        _note(label, "triggered", nid)
        if unresolved:
            _note(label, "unresolved_counterpart", nid)
            continue
        if any(len(v) > 1 for v in found.values()):
            _note(label, "multi_valued_anchor", nid)
            continue

        declared = {a for a, _, _ in ORIENT[label]}
        if set(found) != declared:
            PARTIAL[(label, frozenset(declared - set(found)))] += 1

        anchors = {a: next(iter(v)) for a, v in found.items()}
        children: dict[str, list[dict[str, Any]]] = {}
        for child_label, child_rel, _fields in schema.IDENTITY[label].child_fields:
            kids = [
                by_id[e["from"]]
                for e in by_rel.get(child_rel, ())
                if e["to"] == nid and e["from"] in by_id
            ]
            children[child_label] = kids
        expected = keys.evidence_id(label, node, anchors, children or None)
        if expected == nid:
            _note(label, "recompute_ok", nid)
        elif keys.evidence_id(label, node, {}, children or None) == nid:
            _note(label, "null_door", nid)
        else:
            _note(label, "mismatch", nid)


def _wrap() -> None:
    original = invariants.validate

    def wrapped(nodes, edges, only=None):  # type: ignore[no-untyped-def]
        classify(nodes, edges)
        return original(nodes, edges, only)

    invariants.validate = wrapped  # store.write_change_set resolves it through the module


def report() -> None:
    print(f"change-sets classified: {CHANGE_SETS}")
    print("| label | " + " | ".join(OUTCOMES) + " |")
    print("|---|" + "---|" * len(OUTCOMES))
    for label in sorted(STATS):
        print(f"| {label} | " + " | ".join(str(STATS[label][o]) for o in OUTCOMES) + " |")
    if PARTIAL:
        print("\ntriggered with some declared anchors absent (informational, not a refusal):")
        for (label, missing), n in sorted(PARTIAL.items(), key=lambda kv: kv[0][0]):
            print(f"- {label}: {n} lacking {sorted(missing)}")
    for (label, outcome), ids in sorted(EXAMPLES.items()):
        print(f"- example {label} {outcome}: {ids}")


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "curation"
    if mode == "curation":
        from bzk.curation.loader import load_path

        for p in sorted(Path("data/curation").glob("curation_*.json")):
            loaded = load_path(p)
            classify(loaded.nodes, loaded.edges)
    elif mode == "rebuild":
        _wrap()
        from bzk import rebuild

        rebuild.rebuild()
    elif mode == "differential":
        _wrap()
        from bzk.sources import pxd018299_differential

        pxd018299_differential.main()
    else:
        raise SystemExit(f"unknown mode {mode!r}: curation | rebuild | differential")
    report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
