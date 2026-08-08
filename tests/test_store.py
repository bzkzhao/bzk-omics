"""`bzk/ontology/store.py` — the one place the change-set contract meets Kùzu.

The properties worth pinning here are the ones that make I9's replay safe rather than merely
working: that a re-staged referent converges instead of colliding, that nothing reaches the store
without passing `invariants.validate`, and that a column the DDL does not declare is an error
rather than a silently dropped field.
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from pathlib import Path

import kuzu
import pytest

from bzk.ontology import schema, store
from bzk.ontology.invariants import NODE_TYPE_KEY, InvariantError

MX1 = "uniprot:P20591"
USP18 = "uniprot:O43593"


@pytest.fixture
def conn() -> Iterator[kuzu.Connection]:
    with tempfile.TemporaryDirectory() as tmp:
        connection = kuzu.Connection(kuzu.Database(str(Path(tmp) / "g.kuzu")))
        schema.create_schema(connection)
        yield connection


def n(node_type: str, node_id: str, **props: object) -> dict[str, object]:
    return {NODE_TYPE_KEY: node_type, "id": node_id, **props}


def test_writes_nodes_and_edges(conn: kuzu.Connection) -> None:
    nodes = [n("Protein", MX1, accession="P20591"), n("Protein", USP18, accession="O43593")]
    report = store.write_change_set(conn, nodes, [])
    assert report.nodes_staged == 2
    assert store.count_nodes(conn) == {"Protein": 2}
    assert store.ids_by_label(conn) == {"Protein": sorted([MX1, USP18])}


def test_the_report_counts_statements_issued_not_nodes_and_edges_created(
    conn: kuzu.Connection,
) -> None:
    """The detector for the rename (2026-08-08): reported count against the graph's *change*.

    A comparison against a constant cannot see this. `test_writes_nodes_and_edges` above asserts
    `nodes_staged == 2` and passes whichever quantity the field holds, because on a first write into
    an empty graph the two agree. The divergence is only visible on a re-write, which `MERGE` makes
    a no-op while the count stays the same — and ADR-0019's self-contained change-sets make that
    re-write mandatory rather than hypothetical.

    So this pins the semantics rather than the name: it fails if the fields are ever re-meant to
    count what landed without the names following.
    """
    nodes = [n("Protein", MX1, accession="P20591")]
    edges: list[dict[str, object]] = []

    before = sum(store.count_nodes(conn).values())
    first = store.write_change_set(conn, nodes, edges)
    after_first = sum(store.count_nodes(conn).values())
    second = store.write_change_set(conn, nodes, edges)
    after_second = sum(store.count_nodes(conn).values())

    assert first.nodes_staged == second.nodes_staged == 1, "the count is len(staged), both times"
    assert after_first - before == 1, "the first write creates the node"
    assert after_second - after_first == 0, "the second creates nothing — MERGE"
    assert second.nodes_staged != after_second - after_first, (
        "reported count and graph delta diverge on a re-write; that divergence is what the name "
        "`nodes_staged` states and `nodes_written` denied"
    )


def test_the_edge_report_counts_statements_issued_too(conn: kuzu.Connection) -> None:
    """The two fields are one defect and are pinned together — `WriteReport` builds both from
    `len()` in one expression, so a fix reaching only one of them would be the same defect left
    half-closed."""
    nodes = [
        n("Analysis", "bzk:an1", kind="curation", parameters_observed=True),
        n("Dataset", "bzk:ds1", content_hash="sha256:" + "0" * 64),
    ]
    edges = [{"type": "USED", "from": "bzk:an1", "to": "bzk:ds1"}]

    first = store.write_change_set(conn, nodes, edges)
    after_first = sum(store.count_edges(conn).values())
    second = store.write_change_set(conn, nodes, edges)
    after_second = sum(store.count_edges(conn).values())

    assert first.edges_staged == second.edges_staged == 1
    assert after_first == 1 and after_second == 1, "the second write creates no edge"
    assert second.edges_staged != after_second - after_first


def test_rewriting_the_same_change_set_converges(conn: kuzu.Connection) -> None:
    """`MERGE`, not `CREATE`. This is what makes ADR-0019's re-staging rule safe.

    A change-set must carry every referent it names, so the same `Protein` legitimately arrives in
    many batches. `CREATE` would raise on the second; ids are content-derived (I7), so a node
    written twice under one id *is* one node and converging on it is correct rather than lenient.
    """
    nodes = [n("Protein", MX1, accession="P20591")]
    store.write_change_set(conn, nodes, [])
    store.write_change_set(conn, nodes, [])
    assert store.count_nodes(conn) == {"Protein": 1}


def test_rewriting_an_edge_converges(conn: kuzu.Connection) -> None:
    nodes = [
        n("Analysis", "bzk:an1", kind="curation", parameters_observed=True),
        n("Dataset", "bzk:ds1", content_hash="sha256:" + "0" * 64),
    ]
    edges = [{"type": "USED", "from": "bzk:an1", "to": "bzk:ds1"}]
    store.write_change_set(conn, nodes, edges)
    store.write_change_set(conn, nodes, edges)
    assert store.count_edges(conn) == {"USED": 1}


def test_a_later_write_updates_non_identifying_columns(conn: kuzu.Connection) -> None:
    """Same id, richer content: the node is one node and the columns are set, not duplicated.

    Only non-identifying columns can differ under one id — an identifying change mints a different
    id by construction (ADR-0020) — so this is a fill-in, never a silent overwrite of a fact that
    would have made it a different node.
    """
    store.write_change_set(conn, [n("Protein", MX1, accession="P20591")], [])
    store.write_change_set(
        conn,
        [n("Protein", MX1, accession="P20591", name="Interferon-induced GTP-binding protein Mx1")],
        [],
    )
    assert store.count_nodes(conn) == {"Protein": 1}
    result = conn.execute("MATCH (p:Protein) RETURN p.name")
    assert isinstance(result, kuzu.QueryResult)
    row = result.get_next()
    assert isinstance(row, list)  # kuzu types get_next() as list | dict; a RETURN gives the list
    assert str(row[0]).startswith("Interferon-induced")


def test_nothing_reaches_the_store_unvalidated(conn: kuzu.Connection) -> None:
    """An edge naming an absent referent is an ADR-0019 structural failure, not a partial write."""
    nodes = [n("Protein", MX1, accession="P20591")]
    edges = [{"type": "HAS_SEQUENCE", "from": MX1, "to": "uniprot:P20591#sv4"}]
    with pytest.raises(InvariantError):
        store.write_change_set(conn, nodes, edges)
    assert store.count_nodes(conn) == {}


def test_a_column_the_ddl_does_not_declare_is_an_error(conn: kuzu.Connection) -> None:
    """Dropping it silently would lose a field a producer believed it had written.

    Enforced here rather than in each producer, so every writer gets it — `bzk/adapters/perseus.py`
    has no check of its own and does not need one.
    """
    with pytest.raises(store.StoreError) as exc:
        store.write_change_set(conn, [n("Protein", MX1, accession="P20591", colour="blue")], [])
    assert "colour" in str(exc.value)


def test_an_unknown_label_is_an_error_even_with_validation_off(conn: kuzu.Connection) -> None:
    """`validate=False` is for a caller that has already validated the identical batch. It is not
    a way in for something the schema does not know — the label still reaches a Cypher string."""
    with pytest.raises(store.StoreError):
        store.write_change_set(conn, [n("Smaple", "bzk:x")], [], validate=False)


def test_iso_timestamps_are_coerced(conn: kuzu.Connection) -> None:
    """A change-set is JSON-serialisable by construction, so it carries ISO strings; Kùzu binds
    `datetime`. Converting here keeps the contract plain data instead of pushing the type into
    every producer."""
    store.write_change_set(
        conn,
        [n("Imputation", "bzk:imp1", method="none", retracted_at="2026-08-14T00:00:00")],
        [],
    )
    result = conn.execute("MATCH (i:Imputation) RETURN i.retracted_at")
    assert isinstance(result, kuzu.QueryResult)
    row = result.get_next()
    assert isinstance(row, list)
    assert str(row[0]) == "2026-08-14 00:00:00"


def test_edge_properties_are_written(conn: kuzu.Connection) -> None:
    """`ANNOTATED_IN` is the only relationship in the DDL with properties; they must survive."""
    nodes = [
        n("Protein", MX1, accession="P20591"),
        n("Pathway", "reactome:R-HSA-1169408", name="Interferon Signaling"),
    ]
    edges = [
        {
            "type": "ANNOTATED_IN",
            "from": MX1,
            "to": "reactome:R-HSA-1169408",
            "source": "reactome",
            "evidence_code": "IEA",
        }
    ]
    store.write_change_set(conn, nodes, edges)
    result = conn.execute("MATCH ()-[e:ANNOTATED_IN]->() RETURN e.source, e.evidence_code")
    assert isinstance(result, kuzu.QueryResult)
    assert result.get_next() == ["reactome", "IEA"]


def test_an_edge_property_the_ddl_does_not_declare_is_an_error(conn: kuzu.Connection) -> None:
    nodes = [
        n("Protein", MX1, accession="P20591"),
        n("Pathway", "reactome:R-HSA-1169408", name="Interferon Signaling"),
    ]
    edges = [
        {"type": "ANNOTATED_IN", "from": MX1, "to": "reactome:R-HSA-1169408", "curator": "someone"}
    ]
    with pytest.raises(store.StoreError) as exc:
        store.write_change_set(conn, nodes, edges)
    assert "curator" in str(exc.value)


def test_counts_omit_empty_tables(conn: kuzu.Connection) -> None:
    """The mapping reads as what the graph holds, not as the schema with 57 zeroes in it."""
    assert store.count_nodes(conn) == {}
    assert store.count_edges(conn) == {}
