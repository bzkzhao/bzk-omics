"""Write a validated change-set into the graph — the one place the contract meets Kùzu.

`invariants.py` is deliberately storage-free: a change-set is *"plain data, independent of Kùzu
storage"*, which is what lets every invariant be a pure function and be unit-tested without a
graph (ADR-0019's rejected alternative (b)). Something still has to put it in the store, and this
is that something — the single module that knows both the change-set shape and the DDL, keeping
that knowledge out of the validator and out of every producer.

**`MERGE`, never `CREATE`.** Ids are content-derived (I7, ADR-0020), so a node written twice with
the same id *is* the same node — and ADR-0019 requires every producer to re-stage the referents it
names, so the same `Protein` legitimately arrives in many change-sets. `CREATE` would raise on the
second; `MERGE` converges, which is what makes replay idempotent under I9. This is the write-path
half of the guarantee ADR-0020's digest scheme makes on the read side.

**Nothing is interpolated into Cypher that the schema does not declare.** Labels, relationship
names and column names all come from `schema.py` and are checked against it before they reach a
query string; values are always bound parameters. A producer emitting a column the DDL lacks is an
error here rather than a silently dropped field — the same reason `bzk/curation/loader.py` checks
its own props, now enforced once for every producer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import kuzu

from bzk.ontology import invariants, schema
from bzk.ontology.invariants import NODE_TYPE_KEY

_NODE_COLUMNS: dict[str, dict[str, str]] = {t.name: dict(t.columns) for t in schema.NODE_TABLES}
_NODE_PRIMARY_KEY: dict[str, str] = {t.name: t.primary_key for t in schema.NODE_TABLES}
_REL_ENDPOINTS: dict[str, tuple[tuple[str, str], ...]] = {
    t.name: t.pairs for t in schema.REL_TABLES
}
_REL_PROPERTIES: dict[str, dict[str, str]] = {t.name: dict(t.properties) for t in schema.REL_TABLES}


class StoreError(RuntimeError):
    """A change-set cannot be written as given. Not downgraded to a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class WriteReport:
    """What a write *issued*, not what it landed. **Renamed from `nodes_written` 2026-08-08.**

    Both fields are the length of the staged collection, and both write paths are `MERGE`, so
    anything staged a second time issues a statement and creates nothing. ADR-0019 requires a
    change-set to be self-contained, which makes re-staging **mandatory rather than incidental** —
    on PXD018299 the adapter re-stages the `Dataset` and all 12 `Sample`s the curation record
    already wrote, so the divergence is systematic, not an edge case.

    The old names asserted a property the code does not have, and it was read as true: `HANDOFF.md`
    §8 recorded "11,743 nodes and 9,229 edges" for a graph holding 11,730 and 9,217.

    Renamed rather than re-meant, for two reasons beyond cost. **What the graph holds already has a
    home** — `count_nodes` below, which is where §3's composition list comes from — so re-meaning
    these would put one fact in two places, which `CLAUDE.md` calls a defect rather than
    redundancy. And **statements issued has no other home and is load-bearing**: §8's performance
    row is denominated in it ("20,294 statements … 225 statements/second").

    **Corrected 2026-08-08:** this paragraph used to add *"and that row already used the correct
    word one line below the sentence that did not"*. It did not. The row's total said *statements*
    and its own parenthetical decomposed that total as "11,386 nodes + 8,908 edges" — the two words
    the rename removes, on the same line as the word that replaces them. The row was cited as the
    reason to rename and was itself carrying the defect; §8 is fixed and the claim of cleanliness is
    withdrawn rather than moved.

    `tests/test_store.py` excludes, by name and by separate value, every quantity these fields could
    otherwise hold: the graph delta, the total `count_nodes` reports, that total one statement
    earlier, the transposed field, and any constant. **Widened 2026-08-08** — the first version
    excluded only the graph delta, which is the alternative it was built around, so re-meaning both
    fields to `sum(count_nodes(conn).values())` passed the entire suite. Two candidates stay
    unexcluded and are named there rather than left implicit: distinct staged `(label, id)`, which
    no validated write can separate from `len(staged)` because ADR-0019 refuses duplicates inside a
    change-set, and rows-actually-changed, which Kùzu does not expose.
    """

    nodes_staged: int
    edges_staged: int


def _coerce(value: Any, column_type: str) -> Any:
    """Render one change-set value into what Kùzu binds for that column type.

    Only `TIMESTAMP` needs work: the change-set carries ISO-8601 strings, because a change-set is
    JSON-serialisable by construction, and Kùzu binds `datetime`. Doing it here rather than in each
    producer keeps the change-set a plain-data contract — the point of the split.
    """
    if value is None:
        return None
    if column_type == "TIMESTAMP" and isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def _query(conn: kuzu.Connection, statement: str, parameters: dict[str, Any]) -> kuzu.QueryResult:
    result = conn.execute(statement, parameters=parameters)
    if isinstance(result, list):  # kuzu returns a list only for a multi-statement query
        raise StoreError(f"expected one result from a single statement, got {len(result)}")
    return result


def write_change_set(
    conn: kuzu.Connection,
    nodes: list[invariants.Node],
    edges: list[invariants.Edge],
    *,
    validate: bool = True,
) -> WriteReport:
    """Validate a change-set and write it. Nothing reaches the store unvalidated by default.

    `validate=False` exists for a caller that has already validated the identical batch and is
    writing it in a hot loop; it is not a way to write something that would not pass.
    """
    if validate:
        invariants.validate(nodes, edges)

    for node in nodes:
        label = node[NODE_TYPE_KEY]
        columns = _NODE_COLUMNS.get(label)
        if columns is None:
            raise StoreError(f"{label!r} is not a node table in the schema")
        primary_key = _NODE_PRIMARY_KEY[label]
        props = {k: v for k, v in node.items() if k not in (NODE_TYPE_KEY, primary_key)}
        unknown = set(props) - set(columns)
        if unknown:
            raise StoreError(f"{label} has no column(s) {sorted(unknown)} in the DDL")
        parameters: dict[str, Any] = {"pk": node[primary_key]}
        assignments = []
        for name, value in props.items():
            parameters[name] = _coerce(value, columns[name])
            assignments.append(f"n.{name} = ${name}")
        statement = f"MERGE (n:{label} {{{primary_key}: $pk}})"
        if assignments:
            statement += " SET " + ", ".join(assignments)
        _query(conn, statement, parameters)

    # id -> every label carrying it. Not `{id: node}`: two node tables may share an id (§3 keys
    # both `Protein` and `Modifier` on `uniprot:`, so ISG15 is `uniprot:P05161` under both), and
    # keying on id alone lets the later node win. That would pick the wrong label below, MATCH the
    # wrong table, and write nothing — the exact silent failure the next comment warns about.
    labels_by_id: dict[Any, set[str]] = defaultdict(set)
    for node in nodes:
        labels_by_id[node["id"]].add(str(node[NODE_TYPE_KEY]))
    for edge in edges:
        rel = edge["type"]
        endpoints = _REL_ENDPOINTS.get(rel)
        if endpoints is None:
            raise StoreError(f"{rel!r} is not a relationship in the schema")
        # Which declared pair this edge uses is read off the change-set's own nodes, not assumed
        # to be the first: a multi-pair relationship (ADR-0022) would otherwise MATCH the wrong
        # label and silently write nothing, since MATCH on no rows is not an error. Where an id
        # carries two labels the relationship's declared endpoints are what disambiguate it.
        pair = next(
            (
                (s, d)
                for s, d in endpoints
                if s in labels_by_id[edge["from"]] and d in labels_by_id[edge["to"]]
            ),
            None,
        )
        if pair is None:
            raise StoreError(
                f"{rel} runs {sorted(labels_by_id[edge['from']])} → "
                f"{sorted(labels_by_id[edge['to']])}, which the schema does not declare"
            )
        src_label, dst_label = pair
        declared = _REL_PROPERTIES[rel]
        props = {k: v for k, v in edge.items() if k not in ("type", "from", "to")}
        unknown = set(props) - set(declared)
        if unknown:
            raise StoreError(f"{rel} has no propert(ies) {sorted(unknown)} in the DDL")
        parameters = {"src": edge["from"], "dst": edge["to"]}
        statement = (
            f"MATCH (a:{src_label} {{{_NODE_PRIMARY_KEY[src_label]}: $src}}), "
            f"(b:{dst_label} {{{_NODE_PRIMARY_KEY[dst_label]}: $dst}}) "
            f"MERGE (a)-[e:{rel}]->(b)"
        )
        if props:
            assignments = []
            for name, value in props.items():
                parameters[name] = _coerce(value, declared[name])
                assignments.append(f"e.{name} = ${name}")
            statement += " SET " + ", ".join(assignments)
        _query(conn, statement, parameters)

    return WriteReport(nodes_staged=len(nodes), edges_staged=len(edges))


# ── Reading back, for the rebuild report and for I9's reproducibility check ──────────────────────


def count_nodes(conn: kuzu.Connection) -> dict[str, int]:
    """Non-empty node tables and their row counts. Empty tables are omitted, so the mapping reads
    as what the graph holds rather than as the schema with zeroes in it."""
    counts = {}
    for table in schema.NODE_TABLES:
        row = _query(conn, f"MATCH (n:{table.name}) RETURN count(n)", {}).get_next()
        assert isinstance(row, list)
        if row[0]:
            counts[table.name] = int(row[0])
    return counts


def count_edges(conn: kuzu.Connection) -> dict[str, int]:
    counts = {}
    for table in schema.REL_TABLES:
        row = _query(conn, f"MATCH ()-[e:{table.name}]->() RETURN count(e)", {}).get_next()
        assert isinstance(row, list)
        if row[0]:
            counts[table.name] = int(row[0])
    return counts


def ids_by_label(conn: kuzu.Connection) -> dict[str, list[str]]:
    """Every stored id, per label, sorted — what an I9 rebuild is compared on."""
    stored = {}
    for table in schema.NODE_TABLES:
        primary_key = table.primary_key
        result = _query(conn, f"MATCH (n:{table.name}) RETURN n.{primary_key}", {})
        values = []
        while result.has_next():
            row = result.get_next()
            assert isinstance(row, list)
            values.append(str(row[0]))
        if values:
            stored[table.name] = sorted(values)
    return stored
