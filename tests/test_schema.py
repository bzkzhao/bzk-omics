"""schema.py is the executable mirror of ONTOLOGY.md §4-7 — these tests keep it honest.

Two guarantees: the emitted DDL actually builds on the pinned Kùzu (so the mirror is valid),
and it matches the normative document field-for-field (so the mirror has not drifted). Drift
fails here loudly rather than surfacing as a wrong residue or a silently dropped column later.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

import kuzu

from bzk.ontology import schema

ONTOLOGY = Path(__file__).resolve().parents[1] / "ONTOLOGY.md"
MULTIPLICITIES = {"ONE_ONE", "ONE_MANY", "MANY_ONE", "MANY_MANY"}


def _ontology_ddl() -> str:
    blocks = re.findall(r"```cypher\n(.*?)```", ONTOLOGY.read_text(), re.DOTALL)
    return re.sub(r"--[^\n]*", "", "\n".join(blocks))  # drop inline comments


def _parse_ontology() -> tuple[dict[str, set[str]], dict[str, tuple[str, str, str | None]]]:
    """Extract {node table -> columns} and {rel table -> (src, dst, multiplicity)} from the DDL.

    The document guarantees every column is declared in its table's CREATE (§ preamble), so
    there is no ALTER TABLE to account for; a re-introduced ALTER would surface here as a
    column the emitter appears to add on its own, which is the divergence we want to catch.
    """
    nodes: dict[str, set[str]] = {}
    rels: dict[str, tuple[str, str, str | None]] = {}
    for stmt in (s.strip() for s in _ontology_ddl().split(";") if s.strip()):
        node = re.match(r"CREATE NODE TABLE (\w+)\((.*)\)", stmt, re.DOTALL)
        if node:
            body = re.sub(r"PRIMARY KEY\s*\([^)]*\)", "", node.group(2))
            nodes[node.group(1)] = {p.split()[0] for p in body.split(",") if p.split()}
            continue
        rel = re.match(r"CREATE REL TABLE (\w+)\((.*)\)", stmt, re.DOTALL)
        if rel:
            src_dst = re.search(r"FROM (\w+) TO (\w+)", rel.group(2))
            assert src_dst is not None, f"unparsable rel: {stmt}"
            tokens = rel.group(2).replace(",", " ").split()
            mult = next((t for t in tokens if t in MULTIPLICITIES), None)
            rels[rel.group(1)] = (src_dst.group(1), src_dst.group(2), mult)
    return nodes, rels


def test_schema_node_tables_match_ontology() -> None:
    ontology_nodes, _ = _parse_ontology()
    schema_nodes = {t.name: {c for c, _ in t.columns} for t in schema.NODE_TABLES}
    assert schema_nodes == ontology_nodes


def test_schema_rel_tables_match_ontology() -> None:
    _, ontology_rels = _parse_ontology()
    schema_rels = {t.name: (t.src, t.dst, t.multiplicity) for t in schema.REL_TABLES}
    assert schema_rels == ontology_rels


def test_identity_table_matches_ddl() -> None:
    """§3's per-label identity table must name only real columns and rel tables (ADR-0020).

    Identity is normative in §3, and the key builder mirrors it. This keeps the table honest against
    the DDL: it caught `test`/`fdr_method` listed for `Analysis` while they sat on `DifferentialResult`.
    """
    nodes, rels = _parse_ontology()
    text = ONTOLOGY.read_text()
    region = text[text.index("Evidence-node identity, per label") : text.index("Provenance agents key")]
    rows = re.findall(r"^\| `(\w+)` \| (.+?) \| (.+?) \|\s*$", region, re.M)
    assert rows, "identity table not found in §3"
    for label, fields_col, anchors_col in rows:
        assert label in nodes, f"§3 identity table lists unknown node {label!r}"
        for fld in re.findall(r"`([a-z][a-z0-9_]*)`", fields_col):
            assert fld in nodes[label], f"§3: {label}.{fld} is not a column of {label}"
        for edge in re.findall(r"`([A-Z][A-Z0-9_]+)`", anchors_col):
            assert edge in rels, f"§3: anchor {edge!r} (row {label}) is not a rel table"


def test_schema_builds_on_kuzu() -> None:
    tmp = tempfile.mkdtemp(prefix="schema_test_")
    try:
        conn = kuzu.Connection(kuzu.Database(str(Path(tmp) / "g.kuzu")))
        schema.create_schema(conn)
        result = conn.execute("CALL SHOW_TABLES() RETURN name")
        built = set()
        while result.has_next():
            built.add(result.get_next()[0])
        assert built == schema.table_names()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
