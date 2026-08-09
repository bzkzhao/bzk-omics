"""`bzk/query/` — the read path, and the three rules its package docstring commits to.

**The fixture is built by handing change-sets to `ontology.store.write_change_set`**, which runs
`invariants.validate` first. That is deliberate and it closes a named risk: a query tested against
hand-written rows can be correct about a shape no producer makes, which is the same defect as the
projection that counted a population the builder never sees. Anything this fixture contains, an
adapter could have emitted.

**It is not a convenience.** The real graph has **0** `DifferentialResult` and **0** `Imputation`,
so two of the five questions cannot be exercised against it at all. What a fixture cannot do is
catch a query that is wrong about the *real* population — that is `test_query_real_graph.py`, which
skips without `raw/`.
"""

from __future__ import annotations

from pathlib import Path

import kuzu
import pytest

from bzk.ontology import invariants, schema, store
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.query import graph as gq

MX1 = "uniprot:P20591"
IFIT1_2 = "uniprot:P09914-2"
SEQ = f"{MX1}#sv4"
SITE = f"{MX1}#sv4#K48#unimod:121"
GENE = "hgnc:HGNC:7532"
ANALYSIS = "bzk:analysis1"
DATASET = "bzk:dataset1"
OBS = "bzk:obs1"
RESULT = "bzk:result1"


def _n(label: str, node_id: str, **props: object) -> dict[str, object]:
    return {NODE_TYPE_KEY: label, "id": node_id, **props}


def _e(rel: str, frm: str, to: str, **props: object) -> dict[str, object]:
    return {"type": rel, "from": frm, "to": to, **props}


@pytest.fixture
def conn(tmp_path: Path) -> kuzu.Connection:
    """A graph written through the real write path, holding one of everything the queries read."""
    c = kuzu.Connection(kuzu.Database(str(tmp_path / "g.kuzu")))
    for ddl in schema.ddl_statements():
        c.execute(ddl)
    nodes: list[dict[str, object]] = [
        _n("Gene", GENE, symbol="MX1"),
        _n("Protein", MX1, accession="P20591", gene_absence=None),
        _n("Protein", IFIT1_2, accession="P09914-2", gene_absence="unresolved"),
        _n("ProteinSequence", SEQ, sequence_version=4, sequence="M" * 47 + "K" + "MM"),
        _n("ModificationSite", SITE, residue="K", position=48, modification_type="unimod:121"),
        _n(
            "SiteObservation",
            OBS,
            peptide_sequence="LLQFIDKELVR",
            candidate_proteins=[MX1, IFIT1_2],
            keying_basis="reviewed_preferred",
            displaced_protein=IFIT1_2,
            is_decoy=False,
            n_imputed=1,
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
        _n("Dataset", DATASET, source="local", search_engine="maxquant"),
        _n(
            "Analysis",
            ANALYSIS,
            kind="processing",
            quantity="intensity_multiplicity_summed",
            localization_threshold=0.75,
            filters_applied=["localization_prob>=0.75"],
            test="welch_t",
            fdr_method="benjamini_hochberg",
            parameters_observed=True,
        ),
        _n("Imputation", "bzk:imp1", method="downshifted_normal", seed=0),
        _n("Imputation", "bzk:imp2", method="none", seed=None),
        _n(
            "DifferentialResult",
            RESULT,
            log2fc=2.5,
            p_value=0.0002,
            adj_p_value=0.001,
            protein_adjusted="native",
            adjustment_method="ratio_mod_base",
        ),
        _n(
            "ProteinAssignment",
            "bzk:pa1",
            candidate_proteins=[MX1, IFIT1_2],
            basis="razor",
            confidence="ambiguous",
            retracted_at=None,
        ),
    ]
    edges: list[dict[str, object]] = [
        _e("ENCODES", GENE, MX1),
        _e("HAS_SEQUENCE", MX1, SEQ),
        _e("SITE_ON", SITE, SEQ),
        _e("MEASURED_AT", OBS, SITE),
        _e("REPORTS_SITE", DATASET, OBS),
        _e("USED", ANALYSIS, DATASET),
        _e("ASSIGNMENT_FOR", "bzk:ma1", OBS),
        _e("IMPUTATION_FOR", "bzk:imp1", ANALYSIS),
        _e("IMPUTATION_FOR", "bzk:imp2", ANALYSIS),
        _e("WAS_GENERATED_BY", RESULT, ANALYSIS),
        _e("RESULT_FOR_SITE", RESULT, OBS),
        _e("PROTEIN_ASSIGNMENT_FOR", "bzk:pa1", OBS),
        _e("WAS_DERIVED_FROM", RESULT, OBS),
    ]
    invariants.validate(nodes, edges, only="I2")
    store.write_change_set(c, nodes, edges)
    return c


# ── Rule 3: an absent answer is a value, never an empty container ───────────────────────────────


def test_an_empty_differential_table_says_which_kind_of_empty_it_is(tmp_path: Path) -> None:
    """The case the whole layer is shaped around, and the one the real graph is actually in.

    *No results are stored* and *no site was significant* are opposite claims, and a bare `[]` is
    the same object for both. Both are constructed here, because asserting only one would leave the
    distinction untested in the direction that matters.
    """
    empty = kuzu.Connection(kuzu.Database(str(tmp_path / "empty.kuzu")))
    for ddl in schema.ddl_statements():
        empty.execute(ddl)
    rows, absence = gq.differential_table(empty, ANALYSIS)
    assert rows == [] and absence is gq.Absence.NOT_STORED


def test_a_populated_store_with_no_results_for_this_analysis_is_a_different_absence(
    conn: kuzu.Connection,
) -> None:
    rows, absence = gq.differential_table(conn, "bzk:some-other-analysis")
    assert rows == [] and absence is gq.Absence.NONE_FOUND


def test_refusals_report_not_retained_rather_than_nothing_refused(conn: kuzu.Connection) -> None:
    """Established 2026-08-09: no refusal node table exists and `Refusal` never leaves the adapter.

    PXD018299's ingestion refuses 27 rows, so `[]` here would assert something false about a real
    ingestion rather than merely being uninformative.
    """
    answer = gq.refusals(conn, dataset_id=DATASET)
    assert answer.reasons == ()
    assert answer.absence is gq.Absence.NOT_RETAINED
    assert "not reconstructible from stored content" in answer.detail
    assert not [t for t in schema.NODE_TABLES if "refus" in t.name.lower()], (
        "a refusal table now exists; `refusals` must read it instead of reporting NOT_RETAINED"
    )


def test_an_absent_symbol_is_unattributable_and_says_why(conn: kuzu.Connection) -> None:
    """The limit registered as falsifiable before the code was written.

    §4's three states are per-`Protein`, and a bare symbol does not reach one — the route runs
    through the `Gene` that is absent by hypothesis. If a route existed, this would come back
    attributed, so the assertion is on the claim and not on the phrasing.
    """
    [present] = gq.gene_symbols(conn, ["MX1"])
    assert present.present and present.gene_id == GENE and present.protein_ids == (MX1,)
    [absent] = gq.gene_symbols(conn, ["NOSUCHGENE"])
    assert absent.absence is gq.Absence.UNATTRIBUTABLE
    assert absent.gene_id is None and absent.protein_ids == ()
    # The two vocabularies are disjoint on purpose: §4's states describe a *protein*, and this one
    # describes what a *query* could not determine. Asserting the disjointness rather than
    # comparing members, because a symbol answer carrying `unresolved` would be the guess this
    # whole return shape exists to refuse.
    assert {a.value for a in gq.Absence}.isdisjoint(schema.GENE_ABSENCE)


def test_the_attributed_form_is_available_where_a_protein_is_in_hand(conn: kuzu.Connection) -> None:
    # What `gene_symbols` cannot give from a symbol, the census gives from the proteins themselves,
    # and every state is keyed even at zero — an omitted key and a zero read differently.
    census = gq.gene_absence_census(conn)
    assert census == {"encoded": 1, "unresolved": 1, "no_cross_reference": 0, "not_captured": 0}
    assert set(census) == set(schema.GENE_ABSENCE) | {"encoded"}


# ── Rule 1: no bare number leaves the layer ─────────────────────────────────────────────────────


def test_a_differential_row_carries_its_quantity_test_and_candidate_set(
    conn: kuzu.Connection,
) -> None:
    """I14's display half and I16, on the row rather than deferred to a renderer.

    The candidate set is the load-bearing one: this observation names two proteins, so a log2FC
    rendered against `MX1` alone is what I14 forbids, and the set has to arrive with the number.
    """
    rows, absence = gq.differential_table(conn, ANALYSIS)
    assert absence is None and len(rows) == 1
    row = rows[0]
    assert row.log2fc == 2.5 and row.p_value == 0.0002 and row.adj_p_value == 0.001
    assert row.quantity == "intensity_multiplicity_summed" and row.test == "welch_t"
    assert row.fdr_method == "benjamini_hochberg"
    assert row.candidate_proteins == (MX1, IFIT1_2)
    assert row.site_id == SITE and row.observation_id == OBS
    assert row.gene_symbols == ("MX1",)
    assert row.protein_adjusted == "native" and row.adjustment_method == "ratio_mod_base"
    assert row.assignment_confidence == "ambiguous"
    # I15's flag is not derivable from the graph: no column holds it and the denominator lives in
    # `quant.duckdb`. The numerator travels instead, and a `False` here would assert the clause met.
    assert row.substantially_imputed is None and row.n_imputed == 1


def test_a_site_keying_row_carries_the_basis_and_the_displaced_accession(
    conn: kuzu.Connection,
) -> None:
    keying = gq.site_keying(conn, SITE)
    assert keying is not None
    assert keying.sequence_id == SEQ and keying.sequence_version == 4
    assert keying.protein_id == MX1 and keying.accession == "P20591"
    assert keying.keying_basis == ("reviewed_preferred",)
    assert keying.displaced_protein == (IFIT1_2,)
    assert keying.candidate_proteins == (MX1, IFIT1_2)
    assert keying.modifier_basis == ("inferred_default",)
    assert keying.modifier_confidence == ("ambiguous",)


def test_a_site_that_is_not_there_is_none_rather_than_an_empty_record(
    conn: kuzu.Connection,
) -> None:
    # A record with every field null would be indistinguishable from a site with nothing recorded.
    assert gq.site_keying(conn, "uniprot:P00000#sv1#K1#unimod:121") is None


# ── Rule 2: this layer is I5's enforcement point ────────────────────────────────────────────────


def test_every_returned_entity_carries_its_provenance_status(conn: kuzu.Connection) -> None:
    rows, _ = gq.differential_table(conn, ANALYSIS)
    assert rows[0].provenance.provenanced
    assert rows[0].provenance.analysis_ids == (ANALYSIS,)
    keying = gq.site_keying(conn, SITE)
    assert keying is not None and keying.provenance.provenanced


def test_an_entity_with_no_path_to_an_analysis_is_flagged(tmp_path: Path) -> None:
    """I5's actual subject. A `SiteObservation` whose `Dataset` no `Analysis` `USED`.

    Constructed rather than found, because the real graph has none — which is the result, not a
    reason to skip the case: an invariant tested only on data that satisfies it is untested.
    """
    c = kuzu.Connection(kuzu.Database(str(tmp_path / "orphan.kuzu")))
    for ddl in schema.ddl_statements():
        c.execute(ddl)
    store.write_change_set(
        c,
        # The assignment is here because I3 refuses an observation without one (§6.1) — the write
        # path would not accept this change-set otherwise, which is the fixture-through-the-real-
        # -writer rule doing its job on the very case built to be malformed in a *different* way.
        [
            _n("Dataset", DATASET, source="local"),
            _n("SiteObservation", OBS, peptide_sequence="LLQFIDKELVR", is_decoy=False),
            _n(
                "ModifierAssignment",
                "bzk:ma1",
                candidate_modifiers=["uniprot:P05161"],
                basis="inferred_default",
                confidence="ambiguous",
                retracted_at=None,
            ),
        ],
        [_e("REPORTS_SITE", DATASET, OBS), _e("ASSIGNMENT_FOR", "bzk:ma1", OBS)],
    )
    assert gq.unprovenanced(c) == {
        "Dataset": (1, 1),
        "SiteObservation": (1, 1),
        "DifferentialResult": (0, 0),
    }


def test_an_entity_with_no_declared_provenance_path_fails_safe_to_unprovenanced(
    conn: kuzu.Connection,
) -> None:
    """`_provenance` is called directly, because **no production path reaches this branch**.

    `Figure` is in §7's `prov:Entity` list, has no table, and `unprovenanced` skips labels absent
    from the DDL — so the fall-through is unreachable from every current caller, and flipping it to
    `provenanced=True` left the whole module green. Established rather than assumed: the callers
    were enumerated, not guessed.

    It is kept rather than deleted because it is the direction I5 has to fail in — *flagged* is the
    state the invariant asks for when no path exists, and a default of `True` would silently
    certify every entity type added after this one. Asserted here so the branch is exercised the
    day it becomes reachable and not the day someone notices it was not.
    """
    unknown = gq._provenance(conn, "Figure", "bzk:whatever")
    assert not unknown.provenanced and unknown.unprovenanced
    assert unknown.analysis_ids == () and unknown.path == ""
    assert gq._provenance(conn, "Protein", MX1).provenanced is False, (
        "a reference node is not a §7 entity; claiming provenance for one is a wider assertion "
        "than I5 makes"
    )


def test_the_provenance_report_carries_the_total_beside_the_count(conn: kuzu.Connection) -> None:
    # `DifferentialResult: 0` is true of an empty table and of a fully provenanced one. The total
    # is what separates them, and the fixture has one result so the pair is not (0, 0) here.
    assert gq.unprovenanced(conn) == {
        "Dataset": (0, 1),
        "SiteObservation": (0, 1),
        "DifferentialResult": (0, 1),
    }


def test_figure_is_skipped_rather_than_reported_as_clean(conn: kuzu.Connection) -> None:
    # `Figure` is in §7's prov:Entity list and has no table. Reporting `Figure: (0, 0)` would read
    # as checked; omitting it says the check does not cover it.
    assert "Figure" in gq.PROV_ENTITIES
    assert "Figure" not in {t.name for t in schema.NODE_TABLES}
    assert "Figure" not in gq.unprovenanced(conn)


# ── Q3: the imputation state is a set, per the DDL rather than the scope table ──────────────────


def test_the_imputation_state_is_a_set_because_imputation_for_is_many_one(
    conn: kuzu.Connection,
) -> None:
    """`ROADMAP.md`'s scope table said *"One per `Analysis`"* and the DDL says otherwise.

    The fixture attaches two, which a shape following the scope table could not represent — so
    this fails against that reading rather than merely documenting the correction.
    """
    imputation_for = next(t for t in schema.REL_TABLES if t.name == "IMPUTATION_FOR")
    assert imputation_for.multiplicity == "MANY_ONE"
    state = gq.imputation_state(conn, ANALYSIS)
    assert state.methods == ("downshifted_normal", "none")
    assert state.seeds == (0, None)
    assert state.absence is None and state.satisfies_i15


def test_an_analysis_with_no_imputation_is_an_i15_violation_reported_not_raised(
    conn: kuzu.Connection,
) -> None:
    state = gq.imputation_state(conn, "bzk:some-other-analysis")
    assert state.methods == () and not state.satisfies_i15
    assert state.absence is gq.Absence.NONE_FOUND


def test_no_imputation_stored_at_all_is_a_different_absence(tmp_path: Path) -> None:
    empty = kuzu.Connection(kuzu.Database(str(tmp_path / "e.kuzu")))
    for ddl in schema.ddl_statements():
        empty.execute(ddl)
    assert gq.imputation_state(empty, ANALYSIS).absence is gq.Absence.NOT_STORED


# ── The layer's own boundary ────────────────────────────────────────────────────────────────────


def test_the_read_path_writes_nothing_and_renders_nothing() -> None:
    """`HANDOFF.md` §8's EX class puts I18 at the first path that can write a file. Not this one.

    Asserted on the source rather than trusted: the claim is what keeps I18 out of scope here, so
    it has to fail if the module ever grows the capability.
    """
    source = Path(gq.__file__).read_text()
    for forbidden in ("write_text(", "open(", "MERGE ", "CREATE ", "DELETE ", "SET "):
        assert forbidden not in source, f"the read path contains {forbidden!r}"
    assert "read_only" in source, "connect() must default to a read-only connection"
