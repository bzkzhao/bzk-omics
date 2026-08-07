"""Invariant enforcement tests.

One case per write-time invariant (I2, I3, I4, I10, I14, I15, I16, I19), each asserting the
specific message so an untested second branch cannot hide (F2); the branch tests that F2 found
missing; a shared valid change-set every check accepts, proving none rejects unconditionally (F3);
the missing-referent cases that used to pass vacuously (F1); and change-set structural validation
(ADR-0019) across its four holes. Identifiers are real (ONTOLOGY.md §9).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bzk.ontology.invariants import InvariantError, validate

VALID_CHANGESET = Path(__file__).parent / "fixtures" / "valid_changeset.json"

# Real external identifiers (ONTOLOGY.md §9; USP18 = O43593).
UBIQUITIN = "uniprot:P0CG48"
MX1 = "uniprot:P20591"
IFIT1_2 = "uniprot:P09914-2"
USP18 = "uniprot:O43593"
GG = "unimod:121"


def n(label: str, **props: object) -> dict[str, object]:
    return {"label": label, **props}


def e(rel: str, frm: str, to: str) -> dict[str, str]:
    return {"type": rel, "from": frm, "to": to}


# ── F3: the valid change-set every check accepts ──────────────────────────────────────────────


def test_valid_changeset_passes_every_check() -> None:
    cs = json.loads(VALID_CHANGESET.read_text())
    validate(cs["nodes"], cs["edges"])  # structural + all checks: must not raise
    for inv in ["I2", "I3", "I4", "I10", "I14", "I15", "I16", "I19"]:
        validate(cs["nodes"], cs["edges"], only=inv)  # each check accepts valid input


# ── One violation per invariant, asserting the branch via its message ─────────────────────────


def test_I2_site_parent_protein_needs_sequence_version() -> None:
    site = f"{MX1}#sv?#K48#{GG}"
    nodes = [
        n("Protein", id=MX1, sequence_version=None),
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [e("SITE_ON", site, MX1)], only="I2")
    assert ei.value.invariant == "I2"
    assert "sequence_version" in str(ei.value)


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
    assert "not 'SiteObservation'" in str(ei.value)


def test_structure_label_mismatch_on_owned_relation_attributes_to_invariant() -> None:
    # A SITE_ON whose 'to' is not a Protein is I2's error — the guard that makes _check_I2 sound
    # in reading sequence_version off edge["to"].
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
    assert "not 'Protein'" in str(ei.value)


def test_structure_node_without_id_raises() -> None:
    with pytest.raises(InvariantError) as ei:
        validate([n("Protein", sequence_version=1)], [])  # no id
    assert ei.value.invariant == "STRUCTURE"
    assert "has no id" in str(ei.value)


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
