"""Invariant enforcement tests — written before the schema, and failing by design.

Per HANDOFF.md §3 and ARCHITECTURE.md §4a, the invariant suite is authored first and
fails first: "an adapter that ingests data while violating I3 or I14 is worse than no
adapter." These tests import ``bzk.ontology.invariants``, which does not exist yet, so
collection fails with ImportError — that is the correct initial state. Once
``bzk/ontology/invariants.py`` and ``bzk/ontology/schema.py`` exist, each test must go
green by *rejecting* the violating change.

Scope: one case per invariant checkable at write time (HANDOFF.md §3) —
I2, I3, I4, I10, I14, I15, I16, I19. Invariants that can only be enforced at the export
boundary (I18) or over the whole rebuilt graph (I5, I9) are not write-time cases and are
covered elsewhere.

Contract asserted here (provisional, to be realised by invariants.py):
``validate(nodes, edges, only="I?") -> None`` runs a single invariant's rule over a
staged change-set and raises ``InvariantError`` (carrying ``.invariant``) on violation.
The change-set is plain data — node = ``{"label", **props}``, edge =
``{"type", "from", "to"}`` — mirroring ONTOLOGY.md §4-6, so invariant logic stays a pure
function independent of Kùzu storage. Identifiers are real (ONTOLOGY.md §9).
"""

from __future__ import annotations

import pytest

from bzk.ontology.invariants import InvariantError, validate


def n(label: str, **props: object) -> dict[str, object]:
    return {"label": label, **props}


def e(rel: str, frm: str, to: str) -> dict[str, str]:
    return {"type": rel, "from": frm, "to": to}


# Real external identifiers (ONTOLOGY.md §9 worked example; USP18 = O43593).
UBIQUITIN = "uniprot:P0CG48"
MX1 = "uniprot:P20591"
IFIT1_2 = "uniprot:P09914-2"
USP18 = "uniprot:O43593"
GG = "unimod:121"


def test_I2_site_parent_protein_needs_sequence_version() -> None:
    """I2 — a ModificationSite whose parent Protein lacks a sequence_version cannot exist.

    Residue numbering is meaningless without a fully specified sequence (ONTOLOGY.md §8 I2).
    """
    site = f"{MX1}#sv?#K48#{GG}"
    nodes = [
        n("Protein", id=MX1, sequence_version=None, sequence="MVVSEVDIAKADK"),  # unpinned
        n("ModificationSite", id=site, residue="K", position=48, modification_type=GG),
    ]
    edges = [e("SITE_ON", site, MX1)]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I2")
    assert ei.value.invariant == "I2"


def test_I3_ambiguous_assignment_may_not_name_a_modifier() -> None:
    """I3 — no bare modifier claims: a definite modifier (ASSIGNS edge) may not ride on an
    assignment whose confidence is still 'ambiguous' (ONTOLOGY.md §6.1, §8 I3)."""
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR", localization_prob=0.98),
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
    edges = [
        e("ASSIGNMENT_FOR", "bzk:ma1", "bzk:obs1"),
        e("ASSIGNS", "bzk:ma1", UBIQUITIN),  # asserting ubiquitin while ambiguous
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I3")
    assert ei.value.invariant == "I3"


def test_I4_applied_adjustment_requires_adjusted_by_edge() -> None:
    """I4 — protein_adjusted='applied' requires an ADJUSTED_BY edge to the protein-level
    result used for correction (ONTOLOGY.md §8 I4)."""
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n(
            "DifferentialResult",
            id="bzk:dr1",
            log2fc=3.4,
            p_value=1.2e-5,
            protein_adjusted="applied",
            adjustment_method="residual_vs_protein_lfc",
        ),
    ]
    edges = [e("RESULT_FOR_SITE", "bzk:dr1", "bzk:obs1")]  # 'applied' but no ADJUSTED_BY
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I4")
    assert ei.value.invariant == "I4"


def test_I10_enzyme_attribution_requires_a_live_association() -> None:
    """I10 — a site may not be presented as an enzyme's product except through a *live*
    EnzymeAssociation; a retracted one is not live (ONTOLOGY.md §6.2, §8 I10)."""
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR"),
        n("Protein", id=USP18, sequence_version=1, sequence="MSKAFGLLR"),
        n(
            "EnzymeAssociation",
            id="bzk:ea1",
            direction="deconjugates",
            basis="knockout",
            confidence="confirmed",
            retracted_at="2026-08-14T00:00:00",  # retracted → not live
        ),
    ]
    edges = [
        e("ASSOCIATION_FOR", "bzk:ea1", "bzk:obs1"),
        e("ASSOCIATION_ENZYME", "bzk:ea1", USP18),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I10")
    assert ei.value.invariant == "I10"


def test_I14_multimapping_site_needs_confirmed_protein_assignment() -> None:
    """I14 — a peptide mapping to >1 protein is never rendered against one protein without
    a ProteinAssignment of confidence='confirmed' (ONTOLOGY.md §6.3, §8 I14; 82% prevalence)."""
    nodes = [
        n("Protein", id=MX1, sequence_version=3, sequence="MVVSEVDIAKADK"),
        n("Protein", id=IFIT1_2, sequence_version=2, sequence="MSTNGDDHQVK"),
        n("SiteObservation", id="bzk:obs1", peptide_sequence="SHVISADK"),
        n(
            "ProteinAssignment",
            id="bzk:pa1",
            candidate_proteins=[MX1, IFIT1_2],  # shared peptide, >1 candidate
            basis="razor",
            confidence="ambiguous",  # not 'confirmed'
            retracted_at=None,
        ),
    ]
    edges = [
        e("PROTEIN_ASSIGNMENT_FOR", "bzk:pa1", "bzk:obs1"),
        e("ASSIGNS_PROTEIN", "bzk:pa1", MX1),  # rendered against one, but not confirmed
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I14")
    assert ei.value.invariant == "I14"


def test_I15_analysis_with_results_must_declare_imputation() -> None:
    """I15 — every Analysis producing differential results links to an Imputation, including
    method='none' (ONTOLOGY.md §6.5, §8 I15)."""
    nodes = [
        n("SiteObservation", id="bzk:obs1", peptide_sequence="LLQFIDKELVR", n_imputed=4),
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity="intensity",
            localization_threshold=0.75,
            filters_applied=["reverse", "potential_contaminant"],
            parameters_observed=True,
        ),
        n("DifferentialResult", id="bzk:dr1", log2fc=3.4, protein_adjusted="not_applied"),
    ]
    edges = [
        e("WAS_GENERATED_BY", "bzk:dr1", "bzk:an1"),  # Analysis yields a result...
        e("RESULT_FOR_SITE", "bzk:dr1", "bzk:obs1"),
        # ...but no IMPUTATION_FOR edge to any Imputation
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, edges, only="I15")
    assert ei.value.invariant == "I15"


def test_I16_analysis_must_declare_quantity() -> None:
    """I16 — every Analysis records the quantity it consumed and the filters applied,
    including the localisation threshold (ONTOLOGY.md §8 I16)."""
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="processing",
            quantity=None,  # undeclared
            localization_threshold=0.75,
            filters_applied=["reverse"],
            parameters_observed=True,
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I16")
    assert ei.value.invariant == "I16"


def test_I19_analysis_must_set_parameters_observed() -> None:
    """I19 — every Analysis sets parameters_observed; externally computed results carry
    reported, not observed, provenance (ONTOLOGY.md §5.4, §8 I19)."""
    nodes = [
        n(
            "Analysis",
            id="bzk:an1",
            kind="external",
            external_tool="perseus",
            quantity="intensity",
            localization_threshold=0.75,
            filters_applied=["reverse"],
            parameters_observed=None,  # unset
        ),
    ]
    with pytest.raises(InvariantError) as ei:
        validate(nodes, [], only="I19")
    assert ei.value.invariant == "I19"
