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

import json
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
#: The result's contrast, anchored and armed (ADR-0038 D1, D4) so its kind derives — `condition`,
#: in a non-IP experiment with role-less samples. Added 2026-10-09: since D7's display the table
#: refuses a result whose kind cannot be derived, and until then this one sat in no contrast.
EXPERIMENT = "bzk:experiment1"
CONTRAST = "bzk:contrast1"


def _n(label: str, node_id: str, **props: object) -> dict[str, object]:
    return {NODE_TYPE_KEY: label, "id": node_id, **props}


def _e(rel: str, frm: str, to: str, **props: object) -> dict[str, object]:
    return {"type": rel, "from": frm, "to": to, **props}


def _core() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """The change-set `conn` writes: one of everything the queries read. Returned rather than
    written so a test can vary one part — the result's state, its contrast — and keep the rest."""
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
        _n("Experiment", EXPERIMENT, title="synthetic", modality="digly_proteomics"),
        _n("Sample", "bzk:sample-num", replicate=1),
        _n("Sample", "bzk:sample-den", replicate=1),
        _n("Contrast", CONTRAST, numerator="KO", denominator="WT"),
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
            # ADR-0036 D8: the denominator arm is wholly generated, so (b) flags it while (a) —
            # 3 of 6, not more than half — would not.
            n_values_numerator=3,
            n_values_denominator=3,
            n_imputed_numerator=0,
            n_imputed_denominator=3,
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
        _e("RESULT_IN_CONTRAST", RESULT, CONTRAST),
        _e("CONTRAST_IN_EXPERIMENT", CONTRAST, EXPERIMENT),
        _e("NUMERATOR_SAMPLE", CONTRAST, "bzk:sample-num"),
        _e("DENOMINATOR_SAMPLE", CONTRAST, "bzk:sample-den"),
        _e("PROTEIN_ASSIGNMENT_FOR", "bzk:pa1", OBS),
        _e("WAS_DERIVED_FROM", RESULT, OBS),
    ]
    return nodes, edges


def _write(
    tmp_path: Path, nodes: list[dict[str, object]], edges: list[dict[str, object]], name: str = "g"
) -> kuzu.Connection:
    c = kuzu.Connection(kuzu.Database(str(tmp_path / f"{name}.kuzu")))
    for ddl in schema.ddl_statements():
        c.execute(ddl)
    store.write_change_set(c, nodes, edges)
    return c


@pytest.fixture
def conn(tmp_path: Path) -> kuzu.Connection:
    """A graph written through the real write path, holding one of everything the queries read."""
    nodes, edges = _core()
    invariants.validate(nodes, edges, only="I2")
    return _write(tmp_path, nodes, edges)


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


def test_an_empty_gene_table_is_not_stored_rather_than_unattributable(tmp_path: Path) -> None:
    """The branch neither fixture could reach, and the reason it needed its own graph.

    `UNATTRIBUTABLE` claims the graph holds the fact; over an empty `Gene` table it holds nothing,
    and `NOT_STORED` is defined for exactly that. Both graphs this module and `test_query_real_graph`
    had were populated — one gene and 1,039 — so the wrong branch was unreachable from the suite and
    was found by driving the app over a graph built with no `raw/` (`ROADMAP.md` § *Measured
    findings*, the cold-clone rehearsal).

    **The fixture carries a `Protein` on purpose.** The condition is *this query's table is empty*,
    not *the graph is empty*, and a graph with proteins and no genes is a real state — the resolver
    finding no usable cross-reference for any accession. A check written the looser way would pass
    the DDL-only case and still be wrong here, so the census assertion below is what stops this
    fixture quietly degenerating into an empty database.
    """
    empty = kuzu.Connection(kuzu.Database(str(tmp_path / "nogene.kuzu")))
    for ddl in schema.ddl_statements():
        empty.execute(ddl)
    nodes = [_n("Protein", MX1, accession="P20591", gene_absence="unresolved")]
    invariants.validate(nodes, [])
    store.write_change_set(empty, nodes, [])

    answers = gq.gene_symbols(empty, ["MX1", "NOSUCHGENE"])
    assert len(answers) == 2
    for answer in answers:
        assert not answer.present
        assert answer.absence is gq.Absence.NOT_STORED
        assert answer.gene_id is None and answer.protein_ids == ()
    # The retired claim, asserted as absent rather than inferred from the one above: these are the
    # two values a reader would have to tell apart, and `NOT_STORED` being present does not by
    # itself establish that `UNATTRIBUTABLE` is gone.
    assert gq.Absence.UNATTRIBUTABLE not in {a.absence for a in answers}
    # Non-vacuity: the graph is not empty, so `NOT_STORED` came from the `Gene` table being empty
    # and not from there being nothing at all to read.
    census = gq.gene_absence_census(empty)
    assert census == {"encoded": 0, "unresolved": 1, "no_cross_reference": 0, "not_captured": 0}


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
    # I15's flag, computed from the result's own per-arm counts (ADR-0036 D8), which travel with it.
    assert (row.n_values_numerator, row.n_values_denominator) == (3, 3)
    assert (row.n_imputed_numerator, row.n_imputed_denominator) == (0, 3)
    assert row.substantially_imputed is True


@pytest.mark.parametrize(
    ("nv_num", "nv_den", "ni_num", "ni_den", "expected"),
    [
        (3, 3, 0, 0, False),  # nothing generated
        (3, 3, 0, 3, True),  # (b) only: 3 of 6 is not more than half
        (2, 2, 0, 2, True),  # (b) only: the 2-vs-2 case
        (3, 1, 0, 1, True),  # (b) only: the single imputed bead arm
        (3, 3, 2, 2, True),  # (a) only: 4 of 6, neither arm entire
        (3, 3, 1, 2, False),  # 3 of 6 and neither arm entire
        (3, 3, None, 2, None),  # undeterminable
        (None, None, None, None, None),  # external
    ],
)
def test_substantially_imputed_is_more_than_half_or_a_whole_arm(
    nv_num: int | None,
    nv_den: int | None,
    ni_num: int | None,
    ni_den: int | None,
    expected: bool | None,
) -> None:
    """ADR-0036 D8's rule, case by case; the expected values are literals, never recomputed."""
    assert gq.substantially_imputed(nv_num, nv_den, ni_num, ni_den) is expected


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


# ── ADR-0038 D7: I4's label per (grain, kind, state), no fallback ───────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The two IP kinds, which `ONTOLOGY.md`'s table writes as one row, *either IP kind*. Checked below
#: against the kinds the protein rows name, so the expansion cannot drift from the table it reads.
IP_KINDS = ("differential_association", "background_enrichment")


def _i4_table() -> dict[tuple[str, str, str], str | None]:
    """`ONTOLOGY.md` §8 I4's table, parsed: every cell, with its label or `None` where refused."""
    lines = (REPO_ROOT / "ONTOLOGY.md").read_text().splitlines()
    start = next(i for i, x in enumerate(lines) if x.startswith("- **I4 — Declared adjustment.**"))
    rows: list[list[str]] = []
    for line in lines[start + 1 :]:
        if not line.strip():
            if rows:
                break
            continue
        if not line.lstrip().startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    header, body = rows[0], rows[2:]
    assert header[:2] == ["Grain", "Kind"], header
    states = [h.strip("`") for h in header[2:]]
    cells: dict[tuple[str, str, str], str | None] = {}
    for grain, kind_cell, *values in body:
        kinds = IP_KINDS if kind_cell == "either IP kind" else (kind_cell.strip("`"),)
        for kind in kinds:
            for state, value in zip(states, values, strict=True):
                if value == "refused":
                    cells[(grain, kind, state)] = None
                else:
                    assert value.startswith("*") and value.endswith("*"), value
                    cells[(grain, kind, state)] = value.strip("*")
    return cells


def test_the_label_table_mirrors_ontology_section_8() -> None:
    """The house pattern for a mirror: the copy is checked against its home, parsed from the
    document. Eighteen cells — *either IP kind* is two — six labelled, twelve refused, and the map
    carries exactly the labelled six."""
    cells = _i4_table()
    assert len(cells) == 18
    labelled = {k: v for k, v in cells.items() if v is not None}
    assert labelled == gq.I4_LABELS
    assert sum(1 for v in cells.values() if v is None) == 12
    assert {k for g, k, _ in cells if g == "protein"} - {"condition"} == set(IP_KINDS)


def test_every_labelled_cell_maps_and_every_refused_cell_raises_naming_the_triple() -> None:
    """D2 and D3 over the whole table: no cell is quietly blank."""
    for (grain, kind, state), label in _i4_table().items():
        if label is not None:
            assert gq.adjustment_label("bzk:r", grain, kind, state) == label
            continue
        with pytest.raises(gq.UnlabelledCell) as exc:
            gq.adjustment_label("bzk:r", grain, kind, state)
        assert f"(grain {grain!r}, kind {kind!r}, protein_adjusted {state!r})" in str(exc.value)


def test_a_row_carries_its_grain_kind_and_label(conn: kuzu.Connection) -> None:
    (row,), _ = gq.differential_table(conn, ANALYSIS)
    assert (row.grain, row.contrast_id, row.kind) == ("site", CONTRAST, "condition")
    assert row.adjustment_label == "stoichiometry-native (ratiometric source)"


def _ip_contrast() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """`_core` with its contrast moved into an IP experiment: both arms `ip` against ISG15, so the
    kind derives `differential_association` — a kind no site-grain result may occupy."""
    nodes, edges = _core()
    for node in nodes:
        if node["id"] == EXPERIMENT:
            node["modality"] = "ip_ms"
        if node[NODE_TYPE_KEY] == "Sample":
            node.update(role="ip", bait="uniprot:P05161", antibody="synthetic")
    return nodes, edges


def test_D3_a_site_result_in_an_ip_kind_is_refused_by_the_display(tmp_path: Path) -> None:
    """Written by hand, past `site_change_set`'s producer refusal, which is the only route a result
    reaches this cell — and the display refuses it again, naming the triple."""
    nodes, edges = _ip_contrast()
    c = _write(tmp_path, nodes, edges, "ip")
    with pytest.raises(gq.UnlabelledCell, match="kind 'differential_association'"):
        gq.differential_table(c, ANALYSIS)


def test_a_result_in_no_contrast_is_refused(tmp_path: Path) -> None:
    nodes, edges = _core()
    edges = [x for x in edges if x["type"] != "RESULT_IN_CONTRAST"]
    c = _write(tmp_path, nodes, edges, "nocontrast")
    with pytest.raises(gq.UnlabelledCell, match="is in no Contrast"):
        gq.differential_table(c, ANALYSIS)


def _drop(c: kuzu.Connection, rel: str) -> None:
    """Delete every edge of `rel` in the graph — a state the write path refuses to produce."""
    c.execute(f"MATCH ()-[e:{rel}]->() DELETE e")


def test_a_contrast_with_no_anchor_is_refused_rather_than_read_as_non_ip(tmp_path: Path) -> None:
    """`contrast_kind` would accept `modality` NULL as a non-IP experiment; the read layer does not
    hand it one, because that is a default where the graph says nothing.

    **The write path cannot produce this graph** — write-time I22 refuses arm edges with no anchor
    — so it is made by deleting the anchor in the store. The read refuses it anyway, because a
    store is not only ever written through `write_change_set`.
    """
    c = _write(tmp_path, *_core(), "noanchor")
    _drop(c, "CONTRAST_IN_EXPERIMENT")
    with pytest.raises(gq.UnlabelledCell, match="no CONTRAST_IN_EXPERIMENT anchor"):
        gq.differential_table(c, ANALYSIS)


def test_contrast_kinds_i22_refusal_propagates_as_the_views(tmp_path: Path) -> None:
    """A contrast whose arms derive no kind gives its results no cell, and `contrast_kind`'s I22
    refusal reaches the caller uncaught — the no-fallback case.

    Write-time I22 refuses an anchored contrast with an empty arm, so this state too is made in the
    store, by deleting the numerator arm.
    """
    c = _write(tmp_path, *_core(), "noarms")
    _drop(c, "NUMERATOR_SAMPLE")
    with pytest.raises(invariants.InvariantError) as exc:
        gq.differential_table(c, ANALYSIS)
    assert exc.value.invariant == "I22"
    assert "empty numerator arm" in str(exc.value)


# ── ADR-0038 D6-revised (c): the untested-row display ───────────────────────────────────────────

PERSEUS_TABLE = REPO_ROOT / "tests" / "fixtures" / "perseus_synthetic_proteins.txt"
PERSEUS_SAMPLES = ("bzk:9924d6d24941af0f1b64171e0b550e76", "bzk:7b2ed3b2751c3364da982151935c9845")


def _perseus_graph(tmp_path: Path) -> tuple[kuzu.Connection, str, str]:
    """A Perseus export as it reaches the graph: the loader's half first — an anchored `Contrast`
    with its arm edges — then the adapter's change-set over `perseus_synthetic_proteins.txt`,
    whose IFIT1 row is the untested placeholder. Returns the connection, the external analysis's
    id and the contrast's."""
    from bzk.adapters.base import SampleMapping
    from bzk.adapters.perseus import DeclaredAnalysis, DeclaredContrast, PerseusAdapter
    from bzk.curation.loader import ContrastArms
    from bzk.ontology.keys import evidence_id

    experiment = "bzk:experiment-perseus"
    props = {"numerator": "USP18-/- + IFN", "denominator": "WT + IFN"}
    contrast_id = evidence_id("Contrast", props, {"Experiment": experiment})
    contrast: dict[str, object] = {NODE_TYPE_KEY: "Contrast", "id": contrast_id, **props}
    loader_nodes: list[dict[str, object]] = [
        _n("Experiment", experiment, title="synthetic", modality="proteomics"),
        *(_n("Sample", sid, replicate=i + 1) for i, sid in enumerate(PERSEUS_SAMPLES)),
        contrast,
    ]
    loader_edges = [
        _e("CONTRAST_IN_EXPERIMENT", contrast_id, experiment),
        _e("NUMERATOR_SAMPLE", contrast_id, PERSEUS_SAMPLES[1]),
        _e("DENOMINATOR_SAMPLE", contrast_id, PERSEUS_SAMPLES[0]),
    ]
    c = _write(tmp_path, loader_nodes, loader_edges, "perseus")
    mapping = SampleMapping(
        curation_analysis_id="bzk:curation",
        samples=[
            {
                NODE_TYPE_KEY: "Sample",
                "id": PERSEUS_SAMPLES[0],
                "mapping_key": "LFQ intensity WT_IFN_1",
            },
            {
                NODE_TYPE_KEY: "Sample",
                "id": PERSEUS_SAMPLES[1],
                "mapping_key": "LFQ intensity KO_IFN_1",
            },
        ],
    )
    arms = ContrastArms((PERSEUS_SAMPLES[1],), (PERSEUS_SAMPLES[0],), "condition")
    adapter = PerseusAdapter(
        DeclaredAnalysis(
            quantity="lfq",
            filters_applied=[],
            test="welch_t",
            fdr_method="BH",
            external_version="1.6.15.0",
        ),
        [DeclaredContrast("KO_IFN_WT_IFN", contrast, arms)],
    )
    parsed = adapter.parse(PERSEUS_TABLE, mapping)
    store.write_change_set(c, parsed.nodes, parsed.edges)
    (analysis_id,) = [str(n["id"]) for n in parsed.nodes if n[NODE_TYPE_KEY] == "Analysis"]
    return c, analysis_id, contrast_id


def _set_recorded(c: kuzu.Connection, analysis_id: str, value: str | None) -> None:
    """Rewrite one analysis's recorded count in place — the disagreement a test needs, made in the
    graph rather than by a producer that would not write it."""
    c.execute(
        "MATCH (a:Analysis) WHERE a.id = $id SET a.rows_untested_json = $v",
        {"id": analysis_id, "v": value},
    )


def test_a_protein_grain_row_is_labelled_for_what_it_is(tmp_path: Path) -> None:
    """D2's protein cell, reached through a real producer: four results, each `(protein,
    condition, not_applied)` — *abundance — no adjustment defined*, never *uncorrected*."""
    c, analysis_id, contrast_id = _perseus_graph(tmp_path)
    rows, _ = gq.differential_table(c, analysis_id)
    assert {(r.grain, r.contrast_id, r.kind, r.adjustment_label) for r in rows} == {
        ("protein", contrast_id, "condition", "abundance — no adjustment defined")
    }
    assert len(rows) == 4


def test_equal_counts_show_the_untested_observations(tmp_path: Path) -> None:
    c, analysis_id, contrast_id = _perseus_graph(tmp_path)
    answer = gq.untested_rows(c, analysis_id)
    assert (answer.applies, answer.absence) == (True, None)
    (found,) = answer.contrasts
    assert (found.contrast_id, found.recorded, found.derived) == (contrast_id, 1, 1)
    assert found.status is gq.UntestedStatus.UNTESTED
    (observation,) = found.observation_ids
    candidates = c.execute(
        "MATCH (o:ProteinObservation) WHERE o.id = $id RETURN o.candidate_proteins",
        {"id": observation},
    )
    assert not isinstance(candidates, list)
    assert candidates.get_next() == [["uniprot:P09914"]]


def test_D4_unequal_counts_show_a_mismatch_and_never_the_label(tmp_path: Path) -> None:
    """The view must not infer *untested* from absence alone: one observation has no result, the
    analysis records two, and the answer names both numbers and labels nothing."""
    c, analysis_id, contrast_id = _perseus_graph(tmp_path)
    _set_recorded(c, analysis_id, json.dumps({contrast_id: 2}))
    (found,) = gq.untested_rows(c, analysis_id).contrasts
    assert found.status is gq.UntestedStatus.MISMATCH
    assert (found.recorded, found.derived) == (2, 1)
    assert "has 1 observation(s) with no result" in found.detail
    assert "records 2 untested" in found.detail
    assert gq.NOT_TESTED_LABEL not in found.detail


def test_a_contrast_with_results_and_no_recorded_count_is_a_mismatch(tmp_path: Path) -> None:
    c, analysis_id, _ = _perseus_graph(tmp_path)
    _set_recorded(c, analysis_id, "{}")
    (found,) = gq.untested_rows(c, analysis_id).contrasts
    assert (found.status, found.recorded) == (gq.UntestedStatus.MISMATCH, None)
    assert "records no count untested" in found.detail


def test_an_external_analysis_with_no_recorded_count_is_not_retained(tmp_path: Path) -> None:
    """Written before the field existed, or by an adapter that does not recognise untested rows:
    the observations with no result cannot be told apart, so none is labelled."""
    c, analysis_id, _ = _perseus_graph(tmp_path)
    _set_recorded(c, analysis_id, None)
    answer = gq.untested_rows(c, analysis_id)
    assert (answer.applies, answer.contrasts, answer.absence) == (True, (), gq.Absence.NOT_RETAINED)


def test_an_internal_analysis_has_no_untested_display(conn: kuzu.Connection) -> None:
    """`processing`: the platform decides which rows reach its test, so nothing is derived."""
    answer = gq.untested_rows(conn, ANALYSIS)
    assert (answer.applies, answer.contrasts, answer.absence) == (False, (), None)
    assert "filters_applied" in answer.detail
