"""Invariant enforcement tests.

One case per write-time invariant (I2, I3, I4, I10, I14, I15, I16, I19), each asserting the
specific message so an untested second branch cannot hide (F2); the branch tests that F2 found
missing; a shared valid change-set every check accepts, proving none rejects unconditionally (F3);
the missing-referent cases that used to pass vacuously (F1); and change-set structural validation
(ADR-0019) across its four holes. Identifiers are real (ONTOLOGY.md §9).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from bzk.ontology import schema
from bzk.ontology.invariants import (
    COLUMN_BACKED_NODE_KEYS,
    NODE_TYPE_KEY,
    RESERVED_EDGE_KEYS,
    RESERVED_NODE_KEYS,
    InvariantError,
    validate,
)

VALID_CHANGESET = Path(__file__).parent / "fixtures" / "valid_changeset.json"

# Real external identifiers (ONTOLOGY.md §9; USP18 = O43593).
UBIQUITIN = "uniprot:P0CG48"
MX1 = "uniprot:P20591"
IFIT1_2 = "uniprot:P09914-2"
USP18 = "uniprot:O43593"
GG = "unimod:121"


def n(node_type: str, **props: object) -> dict[str, object]:
    """Build a change-set node. The parameter is `node_type`, not `label`, for the same reason the
    discriminator is `__label__`: `label` is a real column and a test that sets one must be able
    to. This helper hit the collision itself the moment such a test was written."""
    return {NODE_TYPE_KEY: node_type, **props}


def e(rel: str, frm: str, to: str) -> dict[str, str]:
    return {"type": rel, "from": frm, "to": to}


# ── F3: the valid change-set every check accepts ──────────────────────────────────────────────


def test_valid_changeset_passes_every_check() -> None:
    cs = json.loads(VALID_CHANGESET.read_text())
    validate(cs["nodes"], cs["edges"])  # structural + all checks: must not raise
    for inv in ["I2", "I3", "I4", "I10", "I14", "I15", "I16", "I19"]:
        validate(cs["nodes"], cs["edges"], only=inv)  # each check accepts valid input


# ── One violation per invariant, asserting the branch via its message ─────────────────────────


def test_I2_site_parent_sequence_needs_sequence_version() -> None:
    # The SITE_ON target is a ProteinSequence, not a Protein (ADR-0005).
    site = f"{MX1}#sv?#K48#{GG}"
    nodes = [
        n("ProteinSequence", id=f"{MX1}#sv?", sequence_version=None),
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", site, f"{MX1}#sv?")], only="I2")
    assert ei.value.invariant == "I2"
    assert "sequence_version" in str(ei.value)


def test_I2_site_key_version_must_match_its_target() -> None:
    """Clause 2. The key says sv3, the target declares 4 — the position asserts against one
    sequence while attaching to another, which is the whole failure I2 exists to prevent.

    The sequence deliberately **has K at 48**, so clause 3 is satisfied and only clause 2 can fire.
    Written flat first, with `M`*50, and mutation-testing caught it: clause 3 raised instead, and
    the assertion passed anyway because the site's own id contains `sv3` and appears in *that*
    message too. A red test that goes red for the wrong reason is the same defect as a green one
    that passes vacuously — assert on text only one branch can produce.
    """
    site = f"{MX1}#sv3#K48#{GG}"
    nodes = [
        n(
            "ProteinSequence",
            id=f"{MX1}#sv4",
            sequence_version=4,
            sequence="M" * 47 + "K" + "M" * 2,
        ),
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", site, f"{MX1}#sv4")], only="I2")
    assert ei.value.invariant == "I2"
    assert "attaching to another" in str(ei.value)


def test_I2_site_residue_must_match_the_sequence_it_sits_on() -> None:
    """Clause 3, the write-time mirror of the adapter's own check. `MAAKG…` has A at 2, not K."""
    site = f"{MX1}#sv4#K2#{GG}"
    nodes = [
        n("ProteinSequence", id=f"{MX1}#sv4", sequence_version=4, sequence="MAAKGGKLLKR"),
        n("ModificationSite", id=site, residue="K", position=2, modification_type=GG),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", site, f"{MX1}#sv4")], only="I2")
    assert ei.value.invariant == "I2"
    assert "'A'" in str(ei.value)


def test_I2_a_change_set_without_the_sequence_skips_the_residue_check() -> None:
    """Clause 3 is a backstop, not the first line: re-staging a site against a `ProteinSequence`
    already in the graph is legal, and the change-set then carries no sequence to check against.
    Asserted so a future tightening is a deliberate change rather than an accident."""
    site = f"{MX1}#sv4#K2#{GG}"
    nodes = [
        n("ProteinSequence", id=f"{MX1}#sv4", sequence_version=4),
        n("ModificationSite", id=site, residue="K", position=2, modification_type=GG),
    ]
    validate(nodes, [e("SITE_ON", site, f"{MX1}#sv4")], only="I2")  # must not raise


def test_I2_protein_sequence_id_must_match_its_own_version() -> None:
    """Clause 4, first half. A key and a column are two homes for one fact."""
    nodes = [
        n("Protein", id=MX1, accession="P20591"),
        n("ProteinSequence", id=f"{MX1}#sv4", sequence_version=7),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("HAS_SEQUENCE", MX1, f"{MX1}#sv4")], only="I2")
    assert ei.value.invariant == "I2"
    assert "sv4" in str(ei.value)


def test_I2_protein_sequence_id_must_match_the_protein_it_hangs_from() -> None:
    """Clause 4, second half — the isoform substitution ADR-0005 forbids, at write time. The
    canonical `Protein` carrying the isoform's `ProteinSequence` is exactly how a K-GG position
    resolves to the wrong residue while validating as a lysine (`HANDOFF.md` §6)."""
    nodes = [
        n("Protein", id="uniprot:P09914", accession="P09914"),
        n("ProteinSequence", id=f"{IFIT1_2}#sv2", sequence_version=2),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("HAS_SEQUENCE", "uniprot:P09914", f"{IFIT1_2}#sv2")], only="I2")
    assert ei.value.invariant == "I2"
    assert "different protein" in str(ei.value)


def test_I3_ambiguous_assignment_may_not_name_a_modifier() -> None:
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("Modifier", id=UBIQUITIN, name="ubiquitin", leaves_gg_remnant=True),
        n(
            "ModifierAssignment",
            id="bzk:ma1",
            candidate_modifiers=[UBIQUITIN],
            basis="inferred_default",
            confidence="ambiguous",
            retracted_at=None,
        ),
    ]
    edges = [e("ASSIGNMENT_FOR", "bzk:ma1", "bzk:obs1"), e("ASSIGNS", "bzk:ma1", UBIQUITIN)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I3")
    assert ei.value.invariant == "I3"
    assert "ambiguous" in str(ei.value)


def test_I4_applied_adjustment_requires_adjusted_by_edge() -> None:
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("DifferentialResult", id="bzk:dr1", log2fc=3.4, protein_adjusted="applied"),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("RESULT_FOR_SITE", "bzk:dr1", "bzk:obs1")], only="I4")
    assert ei.value.invariant == "I4"
    assert "ADJUSTED_BY" in str(ei.value)


def test_I4_protein_adjusted_must_be_in_the_enum() -> None:
    # F2: the enum branch of I4, previously untested.
    nodes = [n("DifferentialResult", id="bzk:dr1", log2fc=3.4, protein_adjusted="sort_of")]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I4")
    assert ei.value.invariant == "I4"
    assert "must be one of" in str(ei.value)


def test_I10_enzyme_attribution_requires_a_live_association() -> None:
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("Protein", id=USP18, sequence_version=1),
        n(
            "EnzymeAssociation",
            id="bzk:ea1",
            direction="deconjugates",
            basis="knockout",
            confidence="confirmed",
            retracted_at="2026-08-14T00:00:00",
        ),
    ]
    edges = [e("ASSOCIATION_FOR", "bzk:ea1", "bzk:obs1"), e("ASSOCIATION_ENZYME", "bzk:ea1", USP18)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I10")
    assert ei.value.invariant == "I10"
    assert "retracted" in str(ei.value)


def test_I14_multimapping_site_needs_confirmed_protein_assignment() -> None:
    nodes = [
        n("Protein", id=MX1, sequence_version=3),
        n("Protein", id=IFIT1_2, sequence_version=2),
        n("SiteObservation", id="bzk:obs1", peptide_sequence="SHVISADK"),
        n(
            "ProteinAssignment",
            id="bzk:pa1",
            candidate_proteins=[MX1, IFIT1_2],
            basis="razor",
            confidence="ambiguous",
            retracted_at=None,
        ),
    ]
    edges = [
        e("PROTEIN_ASSIGNMENT_FOR", "bzk:pa1", "bzk:obs1"),
        e("ASSIGNS_PROTEIN", "bzk:pa1", MX1),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I14")
    assert ei.value.invariant == "I14"
    assert "confirmed" in str(ei.value)


def test_I14_a_group_observation_may_not_resolve_to_one_member() -> None:
    """The protein-grain half, added with ADR-0022 — the door the original I14 left open.

    An observation naming two candidates while resolving to one asserts a razor pick through
    `RESOLVES_TO_PROTEIN`, which the assignment half of I14 forbids through `ASSIGNS_PROTEIN`. Same
    claim, different edge; nothing caught it because I14 was phrased about peptides and a
    `ProteinObservation` has none.
    """
    nodes = [
        n("Protein", id=MX1, accession="P20591"),
        n("Protein", id=IFIT1_2, accession="P09914-2"),
        n("Dataset", id="bzk:ds1", content_hash="sha256:" + "0" * 64),
        n("ProteinObservation", id="bzk:pobs1", candidate_proteins=[MX1, IFIT1_2]),
    ]
    edges = [
        e("REPORTS_PROTEIN", "bzk:ds1", "bzk:pobs1"),
        e("RESOLVES_TO_PROTEIN", "bzk:pobs1", MX1),  # names two, points at one
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I14")
    assert ei.value.invariant == "I14"
    assert "razor pick" in str(ei.value)


def test_I14_a_group_observation_resolving_to_every_member_is_accepted() -> None:
    """The other side of the same branch, so the check cannot pass by rejecting everything."""
    nodes = [
        n("Protein", id=MX1, accession="P20591"),
        n("Protein", id=IFIT1_2, accession="P09914-2"),
        n("Dataset", id="bzk:ds1", content_hash="sha256:" + "0" * 64),
        n("ProteinObservation", id="bzk:pobs1", candidate_proteins=[MX1, IFIT1_2]),
    ]
    edges = [
        e("REPORTS_PROTEIN", "bzk:ds1", "bzk:pobs1"),
        e("RESOLVES_TO_PROTEIN", "bzk:pobs1", MX1),
        e("RESOLVES_TO_PROTEIN", "bzk:pobs1", IFIT1_2),
    ]
    validate(nodes, edges, only="I14")


def test_I15_analysis_with_results_must_declare_imputation() -> None:
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR", n_imputed=4),
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity="intensity",
            localization_threshold=0.75,
            filters_applied=["reverse"],
            parameters_observed=True,
        ),
        n("DifferentialResult", id="bzk:dr1", log2fc=3.4, protein_adjusted="not_applied"),
    ]
    edges = [
        e("WAS_GENERATED_BY", "bzk:dr1", "bzk:an1"),
        e("RESULT_FOR_SITE", "bzk:dr1", "bzk:obs1"),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I15")
    assert ei.value.invariant == "I15"
    assert "declares no Imputation" in str(ei.value)


def test_I15_stochastic_imputation_requires_a_seed() -> None:
    # F2: the seed branch of I15, previously untested.
    nodes = [n("Imputation", id="bzk:imp1", method="downshifted_normal", seed=None)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I15")
    assert ei.value.invariant == "I15"
    assert "without a seed" in str(ei.value)


def test_I16_quantity_must_be_in_the_closed_enum() -> None:
    # Membership, not merely presence. Before this was wired, validate() accepted any string and
    # the only guard was a test over committed JSON that never sees an ingested change-set —
    # the arrangement ADR-0019's rejected alternative (c) argues against.
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity="Intensity",  # right family, wrong spelling: two ids for one fact
            filters_applied=["reverse"],
            parameters_observed=True,
        )
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I16")
    assert ei.value.invariant == "I16"
    assert "closed enum" in str(ei.value)


def test_I3_confidence_must_be_in_the_closed_enum() -> None:
    # schema.CONFIDENCE existed but was imported nowhere, so confidence looked guarded and was not.
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("Modifier", id=UBIQUITIN, name="ubiquitin", leaves_gg_remnant=True),
        n(
            "ModifierAssignment",
            id="bzk:ma1",
            candidate_modifiers=[UBIQUITIN],
            basis="uba7_knockout",
            confidence="likely",  # not in {ambiguous, probable, confirmed}
            retracted_at=None,
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("ASSIGNS", "bzk:ma1", UBIQUITIN)], only="I3")
    assert ei.value.invariant == "I3"
    assert "closed enum" in str(ei.value)


def test_I16_analysis_must_declare_quantity() -> None:
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity=None,
            localization_threshold=0.75,
            filters_applied=["reverse"],
            parameters_observed=True,
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I16")
    assert ei.value.invariant == "I16"
    assert "quantity" in str(ei.value)


def test_I16_analysis_must_declare_filters() -> None:
    # F2: the filters_applied branch of I16, previously untested.
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity="intensity",
            localization_threshold=0.75,
            filters_applied=None,
            parameters_observed=True,
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I16")
    assert ei.value.invariant == "I16"
    assert "filters" in str(ei.value)


def test_I19_analysis_must_set_parameters_observed() -> None:
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="external",
            external_tool="perseus",
            quantity="intensity",
            localization_threshold=0.75,
            filters_applied=["reverse"],
            parameters_observed=None,
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I19")
    assert ei.value.invariant == "I19"
    assert "parameters_observed" in str(ei.value)


# ── F1 / ADR-0019 hole (i): a missing referent is the owning invariant's error, not a pass ─────


def test_I2_missing_protein_referent_raises() -> None:
    site = f"{MX1}#sv3#K48#{GG}"
    nodes = [n("ModificationSite", id=site, residue="K", position=48, modification_type=GG)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", site, MX1)], only="I2")  # no Protein node
    assert ei.value.invariant == "I2"
    assert "absent from the change-set" in str(ei.value)


def test_I3_missing_assignment_referent_raises() -> None:
    nodes = [n("Modifier", id=UBIQUITIN, name="ubiquitin", leaves_gg_remnant=True)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("ASSIGNS", "bzk:ma1", UBIQUITIN)], only="I3")  # no ModifierAssignment
    assert ei.value.invariant == "I3"
    assert "absent from the change-set" in str(ei.value)


def test_I10_missing_association_referent_raises() -> None:
    nodes = [n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR")]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("ASSOCIATION_FOR", "bzk:ea1", "bzk:obs1")], only="I10")  # no assoc
    assert ei.value.invariant == "I10"
    assert "absent from the change-set" in str(ei.value)


def test_I14_missing_assignment_referent_raises() -> None:
    nodes = [n("Protein", id=MX1, sequence_version=3)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("ASSIGNS_PROTEIN", "bzk:pa1", MX1)], only="I14")  # no ProteinAssignment
    assert ei.value.invariant == "I14"
    assert "absent from the change-set" in str(ei.value)


# ── ADR-0019 holes (ii) label mismatch, (iii) unknown edge type, (iv) node id integrity ───────


def test_structure_unknown_edge_type_raises() -> None:
    site = f"{MX1}#sv3#K48#{GG}"
    nodes = [
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
        n("Protein", id=MX1, sequence_version=3),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITS_ON", site, MX1)])  # typo'd relationship
    assert ei.value.invariant == "STRUCTURE"
    assert "not a relationship in the schema" in str(ei.value)


def test_structure_label_mismatch_on_unowned_relation_is_structural() -> None:
    site = f"{MX1}#sv3#K48#{GG}"
    nodes = [
        n("Protein", id=MX1, sequence_version=3),
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    # MEASURED_AT is SiteObservation -> ModificationSite; a Protein 'from' is wrong.
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("MEASURED_AT", MX1, site)])
    assert ei.value.invariant == "STRUCTURE"
    # The message names the pair the edge actually runs between and the pair(s) the schema
    # declares. It changed shape with ADR-0022, because a relationship may now declare more than
    # one pair and "not X" no longer describes the failure.
    assert "runs 'Protein' → 'ModificationSite'" in str(ei.value)
    assert "declares SiteObservation → ModificationSite" in str(ei.value)


def test_structure_label_mismatch_on_owned_relation_attributes_to_invariant() -> None:
    # A SITE_ON whose 'to' is not a ProteinSequence is I2's error — the guard that makes _check_I2
    # sound in reading sequence_version off edge["to"].
    nodes = [
        n(
            "ModificationSite",
            id=f"{MX1}#sv3#K48#{GG}",
            residue="K",
            position=48,
            modification_type=GG,
        ),
        n("Modifier", id=UBIQUITIN, name="ubiquitin", leaves_gg_remnant=True),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", f"{MX1}#sv3#K48#{GG}", UBIQUITIN)])  # to is a Modifier
    assert ei.value.invariant == "I2"
    assert "declares ModificationSite → ProteinSequence" in str(ei.value)


def test_structure_node_without_id_raises() -> None:
    with pytest.raises(InvariantError) as ei:
        validate([n("Protein", sequence_version=1)], [])  # no id
    assert ei.value.invariant == "STRUCTURE"
    assert "has no id" in str(ei.value)


# ── ADR-0019's reserved namespace: the change-set format against the DDL ──────────────────────


def test_reserved_node_keys_are_not_columns_on_any_node_table() -> None:
    """No structural node key may name a column. This is the guard the `label` collision needed.

    `label` was the node-type discriminator *and* a `STRING` column on six node tables, so those
    six columns were unwritable through the ingestion contract — `{**columns}` overwrote the node
    type. It went unnoticed through the whole of ADR-0019 and its first two addenda because
    nothing compared the format's key names against the DDL's column names; it took a writer that
    actually wanted the column to surface it.

    Instance fixes do not generalise. This does: it fails the day anyone adds a column called
    `__label__`, or renames the discriminator onto a name a table already uses, and it names the
    table and column rather than leaving the next session to diagnose a mangled node.
    """
    offenders = {
        (t.name, column)
        for t in schema.NODE_TABLES
        for column, _type in t.columns
        if column in RESERVED_NODE_KEYS
    }
    assert not offenders, (
        f"reserved change-set key(s) collide with DDL columns: {sorted(offenders)}. A node dict is "
        f"{{**reserved, **columns}}, so the column can never be written. Rename the column, or the "
        "key (ADR-0019 § reserved namespace)."
    )


def test_reserved_edge_keys_are_not_properties_on_any_rel_table() -> None:
    """The same rule for edges, where it currently has nothing to catch — which is the point.

    An edge dict is `{"type", "from", "to", **properties}`. The DDL declares two rel properties in
    total (`source`, `evidence_code`) and neither collides, so this passes today and was left
    un-renamed deliberately. It fires the moment a relationship gains a property called `type`,
    `from` or `to` — the trigger `HANDOFF.md` §8 records, made automatic instead of remembered.
    """
    offenders = {
        (t.name, prop)
        for t in schema.REL_TABLES
        for prop, _type in t.properties
        if prop in RESERVED_EDGE_KEYS
    }
    assert not offenders, (
        f"reserved edge key(s) collide with DDL rel properties: {sorted(offenders)}. Rename the "
        "property, or move the structural keys into a dunder namespace as the node ones were "
        "(ADR-0019 § reserved namespace)."
    )


def test_column_backed_keys_are_columns_on_every_node_table() -> None:
    """The converse direction, which the same rule implies and a one-sided guard would miss.

    `id` is not reserved: it names a real column and means exactly it, which is why the rename left
    it alone. That only holds while every node table actually has the column — otherwise structural
    validation reads a field the store does not have. Checked as the primary key too, since that is
    what makes `id` unique in the graph and not merely within a change-set.
    """
    for table in schema.NODE_TABLES:
        columns = {column for column, _type in table.columns}
        missing = COLUMN_BACKED_NODE_KEYS - columns
        assert not missing, f"{table.name} has no {sorted(missing)} column, but the format reads it"
        assert table.primary_key in COLUMN_BACKED_NODE_KEYS, (
            f"{table.name} keys on {table.primary_key!r}, which the change-set format does not read"
        )


def test_the_node_type_key_is_outside_the_column_name_space() -> None:
    """A structural key must be *unable* to become a column, not merely happen not to be one.

    Every column in ONTOLOGY.md §4-§7 matches `[a-z][a-z0-9_]*`, so a key outside that shape cannot
    collide with a future one. This is what makes `__label__` a fix and `node_type` only a
    postponement — and it is what fails if someone later "tidies" the dunder away.
    """
    for key in RESERVED_NODE_KEYS:
        assert not re.fullmatch(r"[a-z][a-z0-9_]*", key), (
            f"reserved key {key!r} is shaped like a DDL column name, so a future column could take "
            "it. Reserved keys live outside the column-name space (ADR-0019 § reserved namespace)."
        )


def test_structure_node_with_no_type_raises() -> None:
    """A node no edge references was previously unchecked, so it could carry no node type at all.

    Node types were only ever verified where an edge pointed at one, which left this hole: a
    change-set of nothing but untyped nodes validated clean. Found 2026-08-07 while checking the
    discriminator rename had no silent-failure mode — it has exactly this one.
    """
    with pytest.raises(InvariantError) as ei:
        validate([{"id": "bzk:x1"}], [])
    assert ei.value.invariant == "STRUCTURE"
    assert NODE_TYPE_KEY in str(ei.value)


def test_structure_old_style_node_is_rejected_not_silently_accepted() -> None:
    """The regression the rename could have caused: a producer still emitting `label`.

    Before the node-type check, `{"label": "Sample", "id": ...}` passed — the old key was ignored,
    the node had no type, and nothing complained. A stale adapter would have written type-less
    nodes into the graph. The error names the right key so the fix is obvious from the message.
    """
    with pytest.raises(InvariantError) as ei:
        validate([{"label": "Sample", "id": "bzk:s1"}], [])
    assert ei.value.invariant == "STRUCTURE"
    assert "'label'" in str(ei.value)


def test_structure_unknown_node_type_raises() -> None:
    """A typo'd node type is not a node table, and mints an id under a label the DDL lacks."""
    with pytest.raises(InvariantError) as ei:
        validate([n("Smaple", id="bzk:s1")], [])
    assert ei.value.invariant == "STRUCTURE"
    assert "Smaple" in str(ei.value)


def test_structure_a_node_may_carry_both_the_type_key_and_a_label_column() -> None:
    """The point of the rename: `Sample.label` is a real column and must be writable."""
    validate([n("Sample", id="bzk:s1", label="WT_IFN_1", replicate=1)], [])


def test_structure_duplicate_node_id_raises() -> None:
    nodes = [n("Protein", id="dup", sequence_version=1), n("Modifier", id="dup", name="x")]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [])
    assert ei.value.invariant == "STRUCTURE"
    assert "duplicate node id" in str(ei.value)


# ── ADR-0019 hole (v): multiplicity, from schema.RelTable.multiplicity ─────────────────────────


def test_structure_many_one_source_appears_at_most_once() -> None:
    # MEASURED_AT is SiteObservation -> ModificationSite, MANY_ONE: one observation, one site.
    site_a = f"{MX1}#sv3#K48#{GG}"
    site_b = f"{MX1}#sv3#K63#{GG}"
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("ModificationSite", id=site_a, residue="K", position=48, modification_type=GG),
        n("ModificationSite", id=site_b, residue="K", position=63, modification_type=GG),
    ]
    edges = [e("MEASURED_AT", "bzk:obs1", site_a), e("MEASURED_AT", "bzk:obs1", site_b)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges)
    assert ei.value.invariant == "STRUCTURE"
    assert "MANY_ONE" in str(ei.value)


def test_structure_a_site_may_not_have_two_parent_sequences() -> None:
    """What ADR-0023's narrowing actually buys: a second `SITE_ON` is now a **write-time error**.

    While `SITE_ON` was `MANY_MANY` this change-set validated. The site's id names `P20591#sv4`, so
    attaching it to `P09914-2#sv2` as well asserted a position against a sequence the key does not
    mention — and position 48 is `K` in the first and `E` in the second, which is the whole reason
    one `ModificationSite` cannot span parents. Unrepresentable in the id before; rejected now.
    """
    site = f"{MX1}#sv4#K48#{GG}"
    nodes = [
        n("ProteinSequence", id=f"{MX1}#sv4", sequence_version=4),
        n("ProteinSequence", id=f"{IFIT1_2}#sv2", sequence_version=2),
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    edges = [e("SITE_ON", site, f"{MX1}#sv4"), e("SITE_ON", site, f"{IFIT1_2}#sv2")]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges)
    assert ei.value.invariant == "STRUCTURE"
    assert "MANY_ONE" in str(ei.value)


def test_structure_one_many_destination_appears_at_most_once() -> None:
    # ENCODES is Gene -> Protein, ONE_MANY: a protein is encoded by at most one gene.
    nodes = [
        n("Gene", id="hgnc:1", symbol="A"),
        n("Gene", id="hgnc:2", symbol="B"),
        n("Protein", id=MX1, sequence_version=3),
    ]
    edges = [e("ENCODES", "hgnc:1", MX1), e("ENCODES", "hgnc:2", MX1)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges)
    assert ei.value.invariant == "STRUCTURE"
    assert "ONE_MANY" in str(ei.value)
