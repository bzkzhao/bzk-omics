"""The key builder must make two spellings of one fact produce one id (ADR-0020, HANDOFF §8).

Each test below is a defect the 2026-08-07 identity audit found unguarded across ~43 identifying
fields. They are written against the *three families* rather than field by field, because
patching field by field is what the audit named as the defect.
"""

from __future__ import annotations

import pytest

from bzk.ontology import schema
from bzk.ontology.keys import (
    KeyError_,
    canonical_parameters_json,
    canonical_value,
    evidence_id,
    identity_tuple,
    modification_site_key,
    protein_key,
    protein_sequence_key,
)

SITE_ANALYSIS = {
    "kind": "processing",
    "quantity": "intensity_multiplicity_summed",
    "localization_threshold": 0.75,
    "filters_applied": ["reverse", "potential_contaminant"],
    "test": "welch_t",
    "fdr_method": "BH",
    "parameters_observed": True,
}


# ── Family 1: order-sensitive lists ─────────────────────────────────────────────────────────────


def test_list_element_order_does_not_change_an_id() -> None:
    # A search engine's candidate ordering is not canonical, and at I14's measured 82%
    # multi-mapping this is the common path, not an edge case.
    a = dict(SITE_ANALYSIS, filters_applied=["reverse", "potential_contaminant"])
    b = dict(SITE_ANALYSIS, filters_applied=["potential_contaminant", "reverse"])
    assert evidence_id("Analysis", a) == evidence_id("Analysis", b)


def test_a_different_list_membership_does_change_an_id() -> None:
    a = dict(SITE_ANALYSIS, filters_applied=["reverse"])
    b = dict(SITE_ANALYSIS, filters_applied=["reverse", "potential_contaminant"])
    assert evidence_id("Analysis", a) != evidence_id("Analysis", b)


# ── Family 2: unformatted floats ────────────────────────────────────────────────────────────────


def test_float_spelling_does_not_change_an_id() -> None:
    assert evidence_id("Analysis", dict(SITE_ANALYSIS, localization_threshold=0.75)) == evidence_id(
        "Analysis", dict(SITE_ANALYSIS, localization_threshold=0.7500)
    )


def test_integer_and_float_spellings_of_one_value_agree() -> None:
    # 8 vs 8.0 for a DOUBLE column — the Sample.timepoint_h case.
    assert canonical_value(8, "DOUBLE") == canonical_value(8.0, "DOUBLE") == "8.0"


def test_a_different_float_does_change_an_id() -> None:
    assert evidence_id("Analysis", dict(SITE_ANALYSIS, localization_threshold=0.75)) != evidence_id(
        "Analysis", dict(SITE_ANALYSIS, localization_threshold=0.9)
    )


# ── Family 3: structured strings ────────────────────────────────────────────────────────────────


def test_parameters_json_key_order_and_spacing_do_not_change_an_id() -> None:
    a = dict(
        SITE_ANALYSIS, test="perseus_s0", parameters_json='{"s0": 0.1, "n_randomisations": 250}'
    )
    b = dict(SITE_ANALYSIS, test="perseus_s0", parameters_json='{"n_randomisations":250,"s0":0.1}')
    assert evidence_id("Analysis", a) == evidence_id("Analysis", b)


def test_malformed_parameters_json_is_an_error_not_a_passthrough() -> None:
    # Hashing it as raw text is exactly what §3 forbids; failing loudly is the point.
    with pytest.raises(KeyError_):
        canonical_parameters_json("{not json")


# ── Absence, and the null/empty distinction ─────────────────────────────────────────────────────


def test_absent_and_empty_are_not_the_same_id() -> None:
    assert canonical_value(None, "STRING") != canonical_value("", "STRING")
    assert evidence_id("Analysis", dict(SITE_ANALYSIS, test=None)) != evidence_id(
        "Analysis", dict(SITE_ANALYSIS, test="")
    )


def test_a_determined_absence_is_stable_across_calls() -> None:
    # A protein-grain analysis has no localization_threshold (§3, determined by quantity).
    protein = {k: v for k, v in SITE_ANALYSIS.items() if k != "localization_threshold"}
    assert evidence_id("Analysis", protein) == evidence_id("Analysis", dict(protein))


# ── The qualifying-child fold (§3) ──────────────────────────────────────────────────────────────


def test_imputation_seed_changes_the_analysis_id() -> None:
    # The collision the fold exists to prevent: two analyses identical but for the seed.
    seeded = {
        "Imputation": [
            {
                "method": "downshifted_normal",
                "downshift_sd": 1.8,
                "width_sd": 0.3,
                "seed": 42,
                "scope": "whole_matrix",
            }
        ]
    }
    other = {
        "Imputation": [
            {
                "method": "downshifted_normal",
                "downshift_sd": 1.8,
                "width_sd": 0.3,
                "seed": 99,
                "scope": "whole_matrix",
            }
        ]
    }
    assert evidence_id("Analysis", SITE_ANALYSIS, child_values=seeded) != evidence_id(
        "Analysis", SITE_ANALYSIS, child_values=other
    )


def test_child_enumeration_order_does_not_change_the_analysis_id() -> None:
    one = {"method": "none"}
    two = {"method": "downshifted_normal", "downshift_sd": 1.8, "width_sd": 0.3, "seed": 0}
    assert evidence_id("Analysis", SITE_ANALYSIS, child_values={"Imputation": [one, two]}) == (
        evidence_id("Analysis", SITE_ANALYSIS, child_values={"Imputation": [two, one]})
    )


def test_the_fold_reads_child_column_types_not_the_parents() -> None:
    # seed is INT64 on Imputation; a float 0.0 and an int 0 must agree.
    a = {"Imputation": [{"method": "downshifted_normal", "seed": 0}]}
    b = {"Imputation": [{"method": "downshifted_normal", "seed": 0.0}]}
    assert evidence_id("Analysis", SITE_ANALYSIS, child_values=a) == evidence_id(
        "Analysis", SITE_ANALYSIS, child_values=b
    )


# ── Anchors ─────────────────────────────────────────────────────────────────────────────────────


def test_anchor_id_changes_the_evidence_id() -> None:
    ma = {
        "basis": "literature",
        "candidate_modifiers": ["uniprot:P05161"],
        "confidence": "probable",
    }
    ub = evidence_id("ModifierAssignment", ma, anchor_ids={"Modifier": "uniprot:P0CG48"})
    isg = evidence_id("ModifierAssignment", ma, anchor_ids={"Modifier": "uniprot:P05161"})
    assert ub != isg, "ASSIGNS is an anchor — the Ub-vs-ISG15 pair must not collapse"


def test_identity_tuple_is_stable_and_readable() -> None:
    tup = identity_tuple("Software", {"name": "MaxQuant", "version": "1.5.5.1"})
    assert "label=Software" in tup and "name=MaxQuant" in tup and "version=1.5.5.1" in tup
    assert "container_digest" not in tup, "ADR-0021 removed it from identity"


def test_unknown_label_is_refused() -> None:
    with pytest.raises(KeyError_):
        evidence_id("Nonexistent", {})


# ── Reference key templates (§4) ────────────────────────────────────────────────────────────────


def test_reference_templates_compose_the_worked_example() -> None:
    protein = protein_key("P20591")
    sequence = protein_sequence_key(protein, 4)
    site = modification_site_key(sequence, "K", 48, "unimod:121")
    assert protein == "uniprot:P20591"
    assert sequence == "uniprot:P20591#sv4"
    assert site == "uniprot:P20591#sv4#K48#unimod:121"


def test_isoform_suffix_survives_the_template() -> None:
    assert protein_sequence_key(protein_key("P09914-2"), 2) == "uniprot:P09914-2#sv2"


def test_sequence_version_is_unpadded_and_residue_uppercased() -> None:
    assert protein_sequence_key("uniprot:P20591", "04") == "uniprot:P20591#sv4"
    assert modification_site_key("x", "k", 48, "unimod:121") == "x#K48#unimod:121"


def test_psi_mod_may_not_key_a_site() -> None:
    # unimod:121 and mod:00492 name one modification; keying on both fragments the site (I7).
    with pytest.raises(KeyError_):
        modification_site_key("uniprot:P20591#sv4", "K", 48, "mod:00492")


def test_protein_sequence_without_a_version_is_refused() -> None:
    # No `type: ignore` here any more. One used to be needed, and it was the tell: a test asserting
    # the I2 guard had to suppress the checker to reach it, because the signature claimed a state
    # the guard exists to reject could not arrive (HANDOFF.md §8).
    with pytest.raises(KeyError_):
        protein_sequence_key("uniprot:P20591", None)


# ── The builder covers every label the schema declares ──────────────────────────────────────────


def test_every_node_table_can_be_keyed() -> None:
    for table in schema.NODE_TABLES:
        assert table.name in schema.IDENTITY, f"{table.name} has no identity spec"
        identity_tuple(table.name, {})  # must not raise
