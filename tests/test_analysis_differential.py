"""`bzk/analysis/` — the change-set for a run the platform performed.

Everything here goes through `store.write_change_set` rather than being asserted on the returned
dicts alone. A change-set proved correct against nothing that writes it is correct about nothing:
three wrong Cypher premises survived in `bzk/query/` until a fixture built through the real write
path refused them, and the self-containment rule this module is shaped around is enforced *there*
and nowhere else.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import kuzu
import pytest

from bzk.analysis import DeclaredRun, SiteResult, site_change_set
from bzk.ontology import invariants, schema, store
from bzk.ontology.invariants import NODE_TYPE_KEY

MX1 = "uniprot:P20591"
SEQ = f"{MX1}#sv4"
SITE = f"{MX1}#sv4#K48#unimod:121"
OBS = "bzk:obs1"
DATASET = "bzk:dataset1"

RUN = DeclaredRun(
    quantity="intensity_multiplicity_summed",
    test="welch_t",
    fdr_method="BH",
    localization_threshold=0.75,
    filters_applied=("reverse", "localization_prob>=0.75"),
    imputation={"method": "downshifted_normal", "seed": 0, "downshift_sd": 1.8},
    numerator="KO_IFN",
    denominator="WT_IFN",
    label="welch_t KO_IFN vs WT_IFN (BH)",
)


def _n(label: str, node_id: str, **props: object) -> dict[str, object]:
    return {NODE_TYPE_KEY: label, "id": node_id, **props}


def _attached() -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """The slice of an ingestion change-set a result attaches to, as an adapter would hand it over.

    The `ModifierAssignment` is here because I3 refuses the observation without one — the constraint
    that decided this module's signature, and it is asserted below rather than only obeyed.
    """
    dataset = _n("Dataset", DATASET, source="local", search_engine="maxquant")
    nodes = [
        _n(
            "SiteObservation",
            OBS,
            candidate_proteins=[MX1],
            is_decoy=False,
            quant_ref="site_values",
        ),
        _n(
            "ModifierAssignment",
            "bzk:ma1",
            candidate_modifiers=["uniprot:P05161"],
            basis="inferred_default",
            confidence="ambiguous",
            retracted_at=None,
        ),
    ]
    edges: list[dict[str, object]] = [{"type": "ASSIGNMENT_FOR", "from": "bzk:ma1", "to": OBS}]
    return dataset, nodes, edges


@pytest.fixture
def conn(tmp_path: Path) -> kuzu.Connection:
    c = kuzu.Connection(kuzu.Database(str(tmp_path / "g.kuzu")))
    for ddl in schema.ddl_statements():
        c.execute(ddl)
    return c


def _write(conn: kuzu.Connection, results: list[SiteResult]) -> None:
    dataset, nodes, edges = _attached()
    change_set = site_change_set(
        RUN, results, dataset=dataset, attached_nodes=nodes, attached_edges=edges
    )
    store.write_change_set(conn, change_set.nodes, change_set.edges)


def _one(conn: kuzu.Connection, cypher: str) -> Any:
    result = conn.execute(cypher)
    assert not isinstance(result, list)
    row = result.get_next()
    assert isinstance(row, list)
    return row[0]


def test_a_computed_run_lands_as_processing_with_parameters_observed(conn: kuzu.Connection) -> None:
    """I19's flag, and the `kind` §5's enum leaves for it.

    `true` is the standing a platform-produced result has, and `'processing'` is the only value in
    `'processing' | 'curation' | 'external'` that says the platform ran it — `'external'` is the one
    that says it did not, and there is no fourth.
    """
    _write(conn, [SiteResult(OBS, log2fc=1.5, p_value=0.001, adj_p_value=0.01)])
    assert _one(conn, "MATCH (a:Analysis) WHERE a.test = 'welch_t' RETURN a.kind") == "processing"
    assert _one(conn, "MATCH (a:Analysis) WHERE a.test = 'welch_t' RETURN a.parameters_observed")
    # Determined by `kind` — curation's fields, and an external tool is what did not run this.
    for field in ("basis", "confidence", "external_tool", "external_version"):
        assert _one(conn, f"MATCH (a:Analysis) WHERE a.test = 'welch_t' RETURN a.{field}") is None


def test_every_result_reaches_its_analysis_contrast_and_observation(conn: kuzu.Connection) -> None:
    _write(conn, [SiteResult(OBS, log2fc=1.5, p_value=0.001, adj_p_value=0.01)])
    assert _one(conn, "MATCH (r:DifferentialResult) RETURN count(r)") == 1
    for rel in ("WAS_GENERATED_BY", "RESULT_FOR_SITE", "RESULT_IN_CONTRAST"):
        assert _one(conn, f"MATCH ()-[e:{rel}]->() RETURN count(e)") == 1
    assert _one(conn, "MATCH ()-[e:IMPUTATION_FOR]->() RETURN count(e)") == 1
    assert _one(conn, "MATCH ()-[e:USED]->() RETURN count(e)") == 1
    # §11 Q11: `WAS_DERIVED_FROM` restates `RESULT_FOR_SITE` and is deliberately not stored, which
    # is the choice `perseus.py` already makes. A second home for one fact is what Q11 exists over.
    assert _one(conn, "MATCH ()-[e:WAS_DERIVED_FROM]->() RETURN count(e)") == 0


def test_two_results_over_one_observation_are_refused_rather_than_merged(
    conn: kuzu.Connection,
) -> None:
    """Found by writing the test, not by reading the code, and it is the stronger behaviour.

    A result's identity is (analysis, observation, contrast, correction state) — the numbers are
    excluded (§3) — so two results for one observation in one analysis have **one** id. The
    expectation written first was that they converge on one node; ADR-0019's structural validation
    refuses the batch instead, because a duplicate id inside one change-set means the producer
    contradicted itself rather than repeated itself. Silent convergence would have kept whichever
    the loop wrote last.
    """
    dataset, nodes, edges = _attached()
    change_set = site_change_set(
        RUN,
        [
            SiteResult(OBS, log2fc=1.5, p_value=0.001, adj_p_value=0.01),
            SiteResult(OBS, log2fc=-2.0, p_value=0.2, adj_p_value=0.3),
        ],
        dataset=dataset,
        attached_nodes=nodes,
        attached_edges=edges,
    )
    with pytest.raises(invariants.InvariantError, match="duplicate node id"):
        store.write_change_set(conn, change_set.nodes, change_set.edges)


def test_rewriting_a_result_with_different_numbers_updates_it_rather_than_forking(
    conn: kuzu.Connection,
) -> None:
    """ADR-0020's identity rule where it bites: a re-run must not double the table."""
    _write(conn, [SiteResult(OBS, log2fc=1.5, p_value=0.001, adj_p_value=0.01)])
    _write(conn, [SiteResult(OBS, log2fc=9.9, p_value=0.5, adj_p_value=0.6)])
    assert _one(conn, "MATCH (r:DifferentialResult) RETURN count(r)") == 1
    assert _one(conn, "MATCH (r:DifferentialResult) RETURN r.log2fc") == 9.9
    # An `r.id == first` line was written here and **withdrawn rather than pinned**: it cannot
    # fail. Including the numbers in identity would mint a second node, which the count above
    # catches first, and `MERGE` cannot replace a single row with a differently-keyed one — so
    # there is no state in which the count holds and the id has moved.


def test_a_result_whose_observation_is_not_in_the_batch_is_refused(conn: kuzu.Connection) -> None:
    """The premise this module's signature exists for, made to fail rather than described.

    **Which layer refuses it was got wrong before this test was run.** Reading `store.py` says the
    endpoint labels are resolved from the change-set's own nodes, so a missing endpoint cannot
    resolve — true, and it never gets that far: ADR-0019's structural validation runs first and
    names the edge. The stricter guard is the earlier one, and the pre-registration attributed the
    refusal to the wrong layer from reading rather than running.
    """
    dataset, nodes, edges = _attached()
    change_set = site_change_set(
        RUN,
        [SiteResult("bzk:not-in-the-batch", log2fc=1.0, p_value=0.1, adj_p_value=0.2)],
        dataset=dataset,
        attached_nodes=nodes,
        attached_edges=edges,
    )
    with pytest.raises(invariants.InvariantError, match="RESULT_FOR_SITE"):
        store.write_change_set(conn, change_set.nodes, change_set.edges)


def test_the_module_computes_nothing_and_writes_nothing(conn: kuzu.Connection) -> None:
    """The boundary `bzk/analysis/` claims about itself, asserted on the source.

    Its whole justification for being a fourth layer is that it neither does arithmetic nor touches
    the store — so the claim has to fail if either arrives, rather than resting on a docstring.
    """
    tree = ast.parse(Path(site_change_set.__globals__["__file__"]).read_text())
    imported = {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported <= {"__future__", "dataclasses", "typing", "bzk"}, sorted(imported)
    # On the AST rather than on the text, because the prose above names `store.write_change_set` to
    # say what this module leaves to it — a substring check reads that as the call it forbids.
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for forbidden in ("write_change_set", "execute", "open", "read_text", "connect"):
        assert forbidden not in called, f"bzk/analysis/ calls {forbidden!r}"
