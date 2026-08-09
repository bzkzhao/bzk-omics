"""The key builder must make two spellings of one fact produce one id (ADR-0020, HANDOFF §8).

Each test below is a defect the 2026-08-07 identity audit found unguarded across ~43 identifying
fields. They are written against the *three families* rather than field by field, because
patching field by field is what the audit named as the defect.
"""

from __future__ import annotations

from typing import Any

import pytest

from bzk.ontology import keys, schema
from bzk.ontology.keys import (
    KeyError_,
    canonical_parameters_json,
    canonical_value,
    check_curie_case,
    evidence_id,
    identity_tuple,
    modification_site_key,
    protein_key,
    protein_sequence_key,
)
from bzk.resolve import uniprot

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


def test_parameters_json_int_and_float_spellings_of_one_number_do_not_change_an_id() -> None:
    """§3 l.171 says *"normalized numeric forms"*; only key order and spacing were normalized.

    `json.loads` keeps the written form — `250` becomes an `int`, `250.0` a `float` — and
    `json.dumps` writes each back as it found it, so the int/float boundary survived into the hash.
    JSON has one number type, so these are one value and normalizing is right; there is nothing to
    refuse. Float *spelling* already converged through the parse, which is why the clause read as
    met (`test_...key_order_and_spacing...` above passes on both sides of this defect).
    """
    a = dict(
        SITE_ANALYSIS, test="perseus_s0", parameters_json='{"s0": 0.1, "n_randomisations": 250}'
    )
    b = dict(
        SITE_ANALYSIS, test="perseus_s0", parameters_json='{"s0": 0.1, "n_randomisations": 250.0}'
    )
    assert evidence_id("Analysis", a) == evidence_id("Analysis", b)


def test_parameters_json_number_normalization_reaches_nested_values() -> None:
    a = dict(SITE_ANALYSIS, parameters_json='{"grid": {"reps": [10, 20.0]}}')
    b = dict(SITE_ANALYSIS, parameters_json='{"grid": {"reps": [10.0, 20]}}')
    assert evidence_id("Analysis", a) == evidence_id("Analysis", b)


def test_parameters_json_normalization_keeps_true_distinct_from_one() -> None:
    # `isinstance(True, int)` is True in Python; JSON's `true` is not the number 1.
    assert canonical_parameters_json('{"x": true}') != canonical_parameters_json('{"x": 1}')


def test_parameters_json_normalization_does_not_merge_a_big_int_into_a_float() -> None:
    """Injectivity, which is what the removed `2**53` cutoff was wrongly said to protect.

    `2**53 + 1` is not representable as a float, so the float literal denotes `2**53` — a genuinely
    different number, and it must stay different. The collapse preserves that because `int()` on an
    integral float is exact at any magnitude, not because anything above the bound is skipped.
    """
    big = 2**53 + 1
    assert canonical_parameters_json(f'{{"n": {big}}}') != canonical_parameters_json(
        f'{{"n": {float(big)!r}}}'
    )


def test_parameters_json_normalization_reaches_above_two_to_the_fifty_third() -> None:
    """The fork the `2**53` cutoff left standing (corrected 2026-08-08).

    `1e16` and `10000000000000000` are one JSON number written two ways, and above the old bound
    they hashed differently — C1's defect, unfixed in a range, behind a reason that was false.
    """
    assert canonical_parameters_json('{"n": 1e16}') == canonical_parameters_json(
        '{"n": 10000000000000000}'
    )
    assert canonical_parameters_json('{"n": 1e22}') == canonical_parameters_json(
        '{"n": 10000000000000000000000}'
    )


def test_parameters_json_normalization_leaves_non_integral_floats_alone() -> None:
    # `0.1` reports `is_integer()` false, so the collapse never sees it.
    assert canonical_parameters_json('{"n": 0.1}') == '{"n":0.1}'


def test_a_non_finite_number_is_refused_at_the_same_door_as_malformed_json() -> None:
    """Decided 2026-08-08. This test replaces one that pinned the lax output as expected.

    The previous assertion was `"Infinity" in canonical_parameters_json('{"n": 1e400}')`, which
    recorded a choice nobody had made: the function refused input that was not JSON and emitted
    output that was not JSON. Both literals and overflow-to-`inf` are covered, which is why the
    check is `allow_nan=False` on the way out rather than `parse_constant` on the way in.

    Note what this does *not* establish. Nothing in the repository can put a value into
    `parameters_json` today, so no real path reaches either branch.
    """
    for raw in ('{"n": Infinity}', '{"n": -Infinity}', '{"n": NaN}', '{"n": 1e400}'):
        with pytest.raises(KeyError_, match="non-finite"):
            canonical_parameters_json(raw)
    # Nesting, since the check must not be a shallow scan of top-level values.
    with pytest.raises(KeyError_, match="non-finite"):
        canonical_parameters_json('{"grid": {"reps": [1, NaN]}}')
    # And a finite payload still canonicalizes, so the refusal is not a blanket one.
    assert canonical_parameters_json('{"s0": 0.1, "n": 250.0}') == '{"n":250,"s0":0.1}'


def test_malformed_parameters_json_is_an_error_not_a_passthrough() -> None:
    # Hashing it as raw text is exactly what §3 forbids; failing loudly is the point.
    with pytest.raises(KeyError_):
        canonical_parameters_json("{not json")


# ── Family 4: mis-cased identifiers — refused, not repaired ─────────────────────────────────────


def test_a_lowercase_accession_is_refused_rather_than_uppercased() -> None:
    """§4 l.265: *"`accession` keeps UniProt's own casing, uppercase"*.

    `protein_key` interpolated its argument verbatim, so `p20591` and `P20591` minted two `Protein`
    ids, two `ProteinSequence` ids and two `ModificationSite` ids for one lysine. Refused rather
    than uppercased: `resolve/nodes.py` writes `accession` into the node from the same raw string,
    so a repaired id would sit on a node whose own column contradicted it.
    """
    assert protein_key("P20591") == "uniprot:P20591"
    with pytest.raises(KeyError_, match="not uppercase"):
        protein_key("p20591")


def test_the_isoform_suffix_survives_the_accession_case_check() -> None:
    # `-2` is unaffected by `.upper()`, so the check must not reject a legitimate isoform.
    assert protein_key("P09914-2") == "uniprot:P09914-2"


def test_a_miscased_curie_prefix_in_an_identifying_list_is_refused() -> None:
    """§4 l.266: *"CURIE prefixes are lowercase and spelled exactly as in the §3 map"*.

    Nothing implemented this inside the digest path, so `uniprot:P05161` and `UniProt:P05161`
    hashed to two `ModifierAssignment` ids for one assignment.
    """
    ma = {"basis": "literature", "confidence": "probable"}
    good = dict(ma, candidate_modifiers=["uniprot:P05161"])
    assert evidence_id("ModifierAssignment", good, {"Modifier": "uniprot:P05161"})
    with pytest.raises(KeyError_, match="CURIE prefix"):
        canonical_value(["UniProt:P05161"], "STRING[]")
    with pytest.raises(KeyError_, match="CURIE prefix"):
        evidence_id(
            "ModifierAssignment",
            dict(ma, candidate_modifiers=["UniProt:P05161"]),
            {"Modifier": "uniprot:P05161"},
        )


def test_a_miscased_curie_prefix_in_an_anchor_id_is_refused() -> None:
    ma = {
        "basis": "literature",
        "confidence": "probable",
        "candidate_modifiers": ["uniprot:P05161"],
    }
    with pytest.raises(KeyError_, match="CURIE prefix"):
        evidence_id("ModifierAssignment", ma, {"Modifier": "UNIPROT:P05161"})
    with pytest.raises(KeyError_, match="CURIE prefix"):
        evidence_id("Experiment", {"title": "t"}, {"Project": "BZK:abc123"})


def test_the_curie_check_leaves_values_that_are_not_curies_alone() -> None:
    """The check's precision is what makes it safe to run over every list element.

    A `filters_applied` token has no colon. A prefix that case-folds to something the §3 map does
    not contain is not a CURIE the clause governs, so it passes — which also states the check's
    limit: it cannot catch an *unknown* prefix, which is a §3-map question, not a casing one.
    """
    assert canonical_value(["reverse", "potential_contaminant"], "STRING[]")
    assert canonical_value(["Note:2 of 3 replicates"], "STRING[]")
    assert canonical_value(["Sample:A"], "STRING[]")


def test_a_miscased_uniprot_local_part_is_refused_inside_the_digest_path() -> None:
    """§4 l.266's **second** clause: *"The local part keeps its authority's casing"*.

    Unenforced at 3ca5868 while the prefix half was called closed — `canonical_value` accepted
    `['uniprot:p05161']` and the two spellings minted two `ModifierAssignment` ids. The position
    matters: `candidate_proteins` is identifying on four node types, `protein_key` refuses there but
    sits outside the hashing path, and the argument for this whole class is that the builder must
    not rely on a producer emitting canonical values.
    """
    ma = {"basis": "literature", "confidence": "probable"}
    assert canonical_value(["uniprot:P05161"], "STRING[]") == "[uniprot:P05161]"
    with pytest.raises(KeyError_, match="not uppercase"):
        canonical_value(["uniprot:p05161"], "STRING[]")
    with pytest.raises(KeyError_, match="not uppercase"):
        evidence_id("ModifierAssignment", dict(ma, candidate_modifiers=["uniprot:p05161"]))
    with pytest.raises(KeyError_, match="not uppercase"):
        evidence_id("ModifierAssignment", ma, {"Modifier": "uniprot:p05161"})


def test_a_composed_reference_key_survives_the_local_part_check() -> None:
    """The over-broad failure mode: a §4 composed key continues past the accession in lowercase.

    `uniprot:P20591#sv4#K48#unimod:121` is canonical as written — `#sv4` and the trailing `unimod:`
    are lowercase by the same section — so the check is scoped to the segment before the first `#`.
    These ids reach the builder as anchors (`SiteObservation` anchors on `ModificationSite`), so an
    unscoped check would refuse every site in the graph.
    """
    site = "uniprot:P20591#sv4#K48#unimod:121"
    assert canonical_value([site, "uniprot:P09914-2#sv2"], "STRING[]")
    assert evidence_id(
        "SiteObservation",
        {"candidate_proteins": ["uniprot:P20591"]},
        {"Dataset": "bzk:abc123", "ModificationSite": site},
    )


def test_the_local_part_check_is_scoped_to_the_authorities_section_4_fixes() -> None:
    """Stated as a test because it is a decision, not an omission — see `HANDOFF.md` §8.

    §4 determines the local part for UniProt and for the four authorities that carry a prefix
    inside their own identifiers; it fixes nothing for the numeric and opaque ones, and enforcing
    a guessed rule there would be inventing a fact with no home. The clause stays open for those,
    with a trigger recorded in §8.

    `hgnc:4053` was in this list until 2026-08-09, cited as an authority with a *numeric* local
    part. HGNC's identifier is `HGNC:4053`, so the citation was wrong and the example it licensed
    was a second spelling of a `Gene` id.
    """
    assert canonical_value(["pmid:21139048", "unimod:121"], "STRING[]")
    assert canonical_value(["ensembl:ENSG00000187608", "reactome:R-HSA-1169408"], "STRING[]")
    assert canonical_value(["doi:10.1038/s41416-021-01444-4"], "STRING[]")

    # The open set is the complement of the enforced one, asserted rather than listed twice.
    assert set(keys._LOCAL_PART_PREFIX) | {"uniprot"} | {
        "unimod",
        "pmid",
        "ensembl",
        "reactome",
        "doi",
        "mod",
    } == set(schema.CURIE_PREFIXES)


def test_every_authority_that_prefixes_its_own_identifier_is_guarded() -> None:
    """`chebi`, `go` and `mondo` came with `hgnc` (2026-08-09), not after their node types exist.

    The argument for deferring them — no nodes, out of scope, nothing can fork — is the argument
    that left `hgnc` unguarded until `Gene` came into scope carrying three live spellings. §4's
    sharpened rule determines all four, so what was left was a check rather than a decision.

    Each §3 example is asserted to pass and its stripped form to be refused, which is the pairing
    that makes this a two-spellings-one-id guard rather than a smoke test.
    """
    for curie, stripped in (
        ("hgnc:HGNC:4053", "hgnc:4053"),
        ("chebi:CHEBI:15377", "chebi:15377"),
        ("go:GO:0032020", "go:0032020"),
        ("mondo:MONDO_0004992", "mondo:0004992"),
    ):
        assert check_curie_case(curie) == curie
        with pytest.raises(KeyError_):
            check_curie_case(stripped)
        with pytest.raises(KeyError_):
            canonical_value([stripped], "STRING[]")


def test_two_spellings_of_one_gene_do_not_reach_the_hash() -> None:
    """§4: an `hgnc:` local part renders HGNC's identifier verbatim, `HGNC:` and all.

    The two-spellings-one-id shape, at the position where it is worst: `Gene.id` *is* `Gene`'s
    whole identity, so a fork here is two nodes for one gene rather than two ids for one node's
    content. At 3ca5868 all three spellings below were accepted.
    """
    assert check_curie_case("hgnc:HGNC:7532") == "hgnc:HGNC:7532"
    for stripped in ("hgnc:7532", "hgnc:hgnc:7532", "hgnc:Hgnc:7532"):
        with pytest.raises(KeyError_) as ei:
            check_curie_case(stripped)
        assert "hgnc:HGNC:" in str(ei.value)  # the message names the form, not a repair


def test_the_gene_spelling_is_refused_inside_the_hashing_path_too() -> None:
    """The list path, which is the only hashing route an `hgnc:` value can reach today.

    **What this does not cover, asserted rather than assumed.** The other route into the check is
    `identity_tuple`'s anchor loop, and it iterates the *label's own* `spec.anchors` — a value
    handed in under a type the spec does not name is dropped, not checked. `Gene` anchors nothing,
    so an `evidence_id` assertion here would pass while testing nothing, which is the vacuity this
    file was widened to stop. The assertion below is on the fact that makes the gap real, so that
    adding `Gene` to any spec's anchors fails here and the coverage claim gets revisited.
    """
    assert canonical_value(["hgnc:HGNC:7532"], "STRING[]")
    with pytest.raises(KeyError_):
        canonical_value(["hgnc:7532"], "STRING[]")

    assert "Gene" not in {anchor for spec in schema.IDENTITY.values() for anchor, _ in spec.anchors}
    assert evidence_id("ModifierAssignment", {}, {"Gene": "hgnc:7532"})  # dropped, not checked


def test_a_null_list_element_still_renders_as_null_not_as_the_word() -> None:
    # Routing elements through the CURIE check must not route them through `str()` on the way:
    # `str(None)` is "None", which would collide with the literal string and lose §3's null/empty
    # distinction one level down inside a list.
    assert canonical_value([None], "STRING[]") != canonical_value(["None"], "STRING[]")


def test_the_accession_case_clause_covers_the_sequence_cache_path(tmp_path: Any) -> None:
    """C10's second consequence, and it does not depend on UniProt's behaviour at all.

    `resolve` builds **three** paths from the accession verbatim — `entry/{canonical}.json`,
    `seq/{accession}#sv{n}.txt` and, since 2026-08-09, the pin at `seq/{canonical}#sv{n}.meta.json`
    — where canonical means isoform-stripped, not case-folded. So a casing departure forks the
    archive and the drift receipt's digest as well as the graph, and forks them differently by
    platform: a case-insensitive volume hands both spellings one file while two ids are still
    minted. Lives beside `protein_key`'s guard rather than in `test_resolve.py` because it is the
    same §4 clause, and this file is organised by clause rather than by module.

    **The prose enumerates and the assertion does not, which is why the enumeration went stale
    without failing.** `rglob("*") == []` covers any path the function might build, including the
    pin it knew nothing about, so adding a tier left this test green and this docstring wrong. The
    breadth is deliberate — *no file is written* is the load-bearing claim, since a check that
    raised after building a path would leave the fork on disk and only refuse the id — so the
    remedy is to keep the list current, not to narrow the assertion to match it.
    """
    with pytest.raises(KeyError_, match="not uppercase"):
        uniprot.resolve("p20591", cache_dir=tmp_path)
    assert list(tmp_path.rglob("*")) == [], "a refused accession must not touch the cache"


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
