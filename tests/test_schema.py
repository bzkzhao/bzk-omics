"""schema.py is the executable mirror of ONTOLOGY.md §4-7 — these tests keep it honest.

Two guarantees: the emitted DDL actually builds on the pinned Kùzu (so the mirror is valid),
and it matches the normative document field-for-field (so the mirror has not drifted). Drift
fails here loudly rather than surfacing as a wrong residue or a silently dropped column later.
"""

from __future__ import annotations

import json
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


def _walk_nodes(obj: object):
    """Yield every dict carrying an 'id' and a 'label' — the node shape, wherever it is nested."""
    if isinstance(obj, dict):
        if "id" in obj and "label" in obj:
            yield obj
        for value in obj.values():
            yield from _walk_nodes(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_nodes(item)


def _identity_rows() -> list[tuple[str, str, str, str]]:
    text = ONTOLOGY.read_text()
    region = text[
        text.index("**Node identity, per label.**") : text.index("> **To verify, no longer blocking:**")
    ]
    rows = re.findall(r"^\| `(\w+)` \| (.+?) \| (.+?) \| (.+?) \|\s*$", region, re.M)
    assert rows, "identity table not found in §3"
    return rows


def _curie_prefixes() -> set[str]:
    """The §3 prefix map's first column. Handles multi-prefix rows such as `doi` / `pmid`."""
    text = ONTOLOGY.read_text()
    start = text.index("| Prefix | Authority")
    block = text[start : text.index("\n\n", start)]
    return {
        p
        for line in block.splitlines()[2:]  # skip header and separator
        for p in re.findall(r"`(\w+)`", line.split("|")[1])
    }


def _reference_node_tables() -> set[str]:
    """Node tables declared in §4 — the reference half of the graph (§1)."""
    text = ONTOLOGY.read_text()
    section = text[text.index("## 4. Reference nodes") : text.index("## 5. Evidence nodes")]
    return set(re.findall(r"CREATE NODE TABLE (\w+)\(", section))


def test_identity_table_matches_ddl() -> None:
    """§3's identity table must partition every node's columns and cite anchors correctly.

    Four directions. Coverage: every node table in the DDL has exactly one row — reference nodes
    included, whose absence is why the Protein key went unexamined through two audits.
    Completeness: every column is listed identifying or excluded; a column that is neither is a
    silent default to non-identifying (caught `Analysis` omitting `basis`/`confidence`).
    Soundness: identifying and excluded names are real columns (caught `test`/`fdr_method`
    mislisted on `Analysis`). Direction: an anchor's relationship must be declared between *this*
    node and *that* anchor — not merely exist (caught `ProteinObservation` citing `REPORTED_BY`,
    which is `SiteObservation` → `Dataset`, through two passes of a name-only check).
    """
    nodes, rels = _parse_ontology()
    rows = _identity_rows()

    listed = [label for label, *_ in rows]
    assert len(listed) == len(set(listed)), f"§3 lists a node twice: {listed}"
    assert set(listed) == set(nodes), (
        f"§3 coverage — missing rows {set(nodes) - set(listed)}, unknown rows {set(listed) - set(nodes)}"
    )

    for label, ident_col, anchors_col, excl_col in rows:
        identifying = set(re.findall(r"`([a-z][a-z0-9_]*)`", ident_col))
        excluded = set(re.findall(r"`([a-z][a-z0-9_]*)`", excl_col))
        columns = nodes[label] - {"id"}
        assert identifying.isdisjoint(excluded), (
            f"§3 {label}: both identifying and excluded: {identifying & excluded}"
        )
        assert identifying | excluded == columns, (
            f"§3 {label}: columns not partitioned — unaccounted {columns - identifying - excluded}, "
            f"phantom {(identifying | excluded) - columns}"
        )

        pairs = re.findall(r"`([A-Z]\w*)`\s*\(`([A-Z][A-Z0-9_]+)`\)", anchors_col)
        for anchor, edge in pairs:
            assert edge in rels, f"§3 anchor {edge!r} (row {label}) is not a rel table"
            src, dst, _ = rels[edge]
            assert {src, dst} == {label, anchor}, (
                f"§3 {label}: anchor cites {edge} as {label}↔{anchor}, "
                f"but the DDL declares it {src} → {dst}"
            )
        # Every relationship named in the anchors cell must belong to a type-paired citation,
        # so a bare edge name cannot slip past the direction check above.
        named = set(re.findall(r"`([A-Z][A-Z0-9_]+)`", anchors_col))
        assert named == {e for _, e in pairs}, (
            f"§3 {label}: relationship(s) {named - {e for _, e in pairs}} cited without a node type"
        )


def test_key_templates_cover_reference_nodes_and_name_real_fields() -> None:
    """§4's key templates were prose no test read — the surface the Protein defect hid on.

    Checks: every reference node has exactly one template (authority-assigned or composed); every
    authority prefix is in the §3 map; in a composed template every bare {field} is a column of
    that node and every {Type.id} is an anchor of that node per §3.

    What it CANNOT check, stated plainly: that any id on disk actually conforms to its template
    (see the canonicalization test below for the data-level half, and I2's deferred clauses for
    id↔column agreement); that the literal punctuation (`#sv`, `#`) is what a key builder will
    emit, since no builder exists; that an authority really mints ids in the shape shown; that the
    examples are real identifiers rather than plausible ones; and — the same blind spot as the
    partition check — that a template is not *missing* a component it ought to compose.
    """
    text = ONTOLOGY.read_text()
    nodes, _ = _parse_ontology()
    section = text[text.index("**Key templates.**") : text.index("**Key canonicalization.**")]
    prefixes = _curie_prefixes()

    authority = dict(re.findall(r"^\| `(\w+)` \| `(\w+):` \|", section, re.M))
    composed = dict(
        re.findall(r"^(\w+)\s+((?:uniprot:|\{)\S+)$", section, re.M)
    )

    assert set(authority) & set(composed) == set(), "a node appears in both template groups"
    assert set(authority) | set(composed) == _reference_node_tables(), (
        f"§4 template coverage — missing "
        f"{_reference_node_tables() - set(authority) - set(composed)}, unknown "
        f"{(set(authority) | set(composed)) - _reference_node_tables()}"
    )

    for node, prefix in authority.items():
        assert prefix in prefixes, f"§4 {node}: prefix {prefix!r} is not in the §3 prefix map"

    anchors_of = {
        label: {a for a, _ in re.findall(r"`([A-Z]\w*)`\s*\(`([A-Z][A-Z0-9_]+)`\)", anchors)}
        for label, _, anchors, _ in _identity_rows()
    }
    for node, template in composed.items():
        for ref in re.findall(r"\{(\w+)\.id\}", template):
            assert ref in anchors_of[node], (
                f"§4 {node}: template composes {ref}.id, which §3 does not list as its anchor"
            )
        for field in re.findall(r"\{(\w+)\}", template):
            assert field in nodes[node], f"§4 {node}: template names {{{field}}}, not a column"


def test_reference_ids_on_disk_are_canonical() -> None:
    """§4's key canonicalization, checked against committed data.

    Two spellings of one key are two nodes for one fact — ADR-0020's fragmentation mirrored into
    the reference half, sitting under every observation. Unimod is the sole modification authority
    in a key; PSI-MOD is a cross-reference only.
    """
    prefixes = _curie_prefixes()
    root = Path(__file__).resolve().parents[1]
    seen = 0
    for folder in ("tests/fixtures", "data/curation"):
        for path in (root / folder).rglob("*.json"):
            for node in _walk_nodes(json.loads(path.read_text())):
                label, node_id = node.get("label"), node.get("id", "")
                if label not in {"Protein", "ProteinSequence", "ModificationSite", "Modifier"}:
                    continue
                seen += 1
                prefix = node_id.split(":", 1)[0]
                assert prefix in prefixes, f"{node_id}: prefix {prefix!r} not in the §3 map"
                assert prefix == prefix.lower(), f"{node_id}: CURIE prefix must be lowercase"
                if label == "ProteinSequence":
                    sv = re.search(r"#sv(\d+)$", node_id)
                    assert sv, f"{node_id}: ProteinSequence id must end in #sv<n>"
                    assert not sv.group(1).startswith("0"), f"{node_id}: #sv must be unpadded"
                if label == "ModificationSite":
                    m = re.search(r"#([A-Za-z])(\d+)#(\w+):", node_id)
                    assert m, f"{node_id}: ModificationSite id does not match the §4 template"
                    assert m.group(1).isupper(), f"{node_id}: residue must be uppercase"
                    assert m.group(3) == "unimod", (
                        f"{node_id}: modification must be keyed on unimod (§4); "
                        f"{m.group(3)!r} is a cross-reference only"
                    )
    assert seen, "no reference ids found — guard would be vacuous"


def test_quantity_values_are_in_enum() -> None:
    """Every Analysis.quantity on disk must be in the closed enum (ONTOLOGY §5, schema.QUANTITY_VALUES).

    quantity is an identifying field (§3, ADR-0020); two spellings of one quantity mint two Analysis
    ids for one fact. This checks fixtures and curation records honour the closed vocabulary.
    """
    def quantities(obj: object):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "quantity" and isinstance(v, str):
                    yield v
                else:
                    yield from quantities(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from quantities(item)

    root = Path(__file__).resolve().parents[1]
    seen = 0
    for folder in ("tests/fixtures", "data/curation"):
        for path in (root / folder).rglob("*.json"):
            for q in quantities(json.loads(path.read_text())):
                seen += 1
                assert q in schema.QUANTITY_VALUES, (
                    f"{path.name}: quantity {q!r} not in closed enum {sorted(schema.QUANTITY_VALUES)}"
                )
    assert seen, "no quantity values found — guard would be vacuous"


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
