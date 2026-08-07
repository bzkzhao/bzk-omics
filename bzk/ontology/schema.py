"""Kùzu DDL, encoded as data and emitted as Cypher.

`ONTOLOGY.md` §4–§7 is the normative source; this module is its executable mirror, so a
field rename is a regeneration here rather than a search across the codebase (HANDOFF.md
§3). `tests/test_schema.py` asserts this module and ONTOLOGY.md agree — that check is what
keeps the mirror honest, per CLAUDE.md ("code that diverges from the DDL is wrong").

Every column is declared in its table's `CREATE`, matching ONTOLOGY.md §5 — the §5.2 embargo
and §5.4 external-analysis columns are defined directly on `Dataset` / `Analysis` there, not
in separate `ALTER`s. Validated against Kùzu 0.11.3 (ONTOLOGY.md § preamble).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import kuzu

# ── Closed enumerations (STRING columns; Kùzu does not enforce them, invariants do) ──
CONFIDENCE = frozenset({"ambiguous", "probable", "confirmed"})  # EvidencedInference (§6)
PROTEIN_ADJUSTED = frozenset({"applied", "not_applied", "native"})  # DifferentialResult (§8 I4)
STOCHASTIC_IMPUTATION = frozenset({"downshifted_normal"})  # methods requiring a seed (§6.5, I15)


@dataclass(frozen=True)
class NodeTable:
    name: str
    columns: list[tuple[str, str]]  # (column, Kùzu type)
    primary_key: str = "id"
    note: str = ""


@dataclass(frozen=True)
class RelTable:
    name: str
    src: str
    dst: str
    properties: list[tuple[str, str]] = field(default_factory=list)
    multiplicity: str | None = None  # ONE_MANY | MANY_ONE | MANY_MANY | ONE_ONE | None


# Closed vocabulary for the identifying Analysis.quantity field (ONTOLOGY.md §5, I16, ADR-0020).
# Mirror of the §5 enum; guarded against on-disk data by tests/test_schema.py. 'intensity' is a
# plain intensity with NO multiplicity axis (protein- or precursor-level) and is invalid for a
# MaxQuant modification-site source, which uses 'intensity_multiplicity_summed'.
QUANTITY_VALUES: frozenset[str] = frozenset(
    {"intensity", "intensity_multiplicity_summed", "ratio_mod_base", "lfq", "ibaq"}
)


# ── Reference nodes (ONTOLOGY.md §4) ──
NODE_TABLES: list[NodeTable] = [
    NodeTable(
        "Gene",
        [("id", "STRING"), ("symbol", "STRING"), ("ensembl_id", "STRING"), ("name", "STRING")],
    ),
    NodeTable(
        "Protein",
        [
            ("id", "STRING"),
            ("accession", "STRING"),
            ("name", "STRING"),
            ("organism_taxid", "INT64"),
        ],
        note="stable identity; the sequence lives on ProteinSequence (ADR-0005)",
    ),
    NodeTable(
        "ProteinSequence",
        [("id", "STRING"), ("sequence_version", "INT64"), ("sequence", "STRING")],
    ),
    NodeTable(
        "ModificationSite",
        [
            ("id", "STRING"),
            ("residue", "STRING"),
            ("position", "INT64"),
            ("modification_type", "STRING"),
        ],
    ),
    NodeTable(
        "Modifier",
        [
            ("id", "STRING"),
            ("name", "STRING"),
            ("c_terminal_motif", "STRING"),
            ("leaves_gg_remnant", "BOOLEAN"),
        ],
    ),
    NodeTable("Pathway", [("id", "STRING"), ("name", "STRING"), ("source", "STRING")]),
    NodeTable("Disease", [("id", "STRING"), ("label", "STRING")]),
    NodeTable("Drug", [("id", "STRING"), ("label", "STRING")]),
    NodeTable("Publication", [("id", "STRING"), ("title", "STRING"), ("year", "INT64")]),
    # ── Evidence nodes (ONTOLOGY.md §5) ──
    NodeTable("Project", [("id", "STRING"), ("title", "STRING"), ("created_at", "TIMESTAMP")]),
    NodeTable(
        "Experiment",
        [
            ("id", "STRING"),
            ("title", "STRING"),
            ("modality", "STRING"),
            ("organism_taxid", "INT64"),
        ],
    ),
    NodeTable(
        "Sample",
        [
            ("id", "STRING"),
            ("label", "STRING"),
            ("source_type", "STRING"),
            ("cell_line", "STRING"),
            ("organism_taxid", "INT64"),
            ("model_system", "STRING"),
            ("genotype", "STRING"),
            ("treatment", "STRING"),
            ("timepoint_h", "DOUBLE"),
            ("replicate", "INT64"),
            ("replicate_type", "STRING"),
        ],
    ),
    NodeTable(
        "Dataset",
        [
            ("id", "STRING"),
            ("label", "STRING"),
            ("source", "STRING"),
            ("external_accession", "STRING"),
            ("acquisition_mode", "STRING"),
            ("instrument", "STRING"),
            ("search_engine", "STRING"),
            ("search_engine_version", "STRING"),
            ("library_type", "STRING"),
            ("library_prediction_model", "STRING"),
            ("fasta_release", "STRING"),
            ("content_hash", "STRING"),
            # §5.2 embargo columns
            ("embargo_holder", "STRING"),
            ("embargo_reference", "STRING"),
            ("embargo_released_at", "TIMESTAMP"),
        ],
        note="embargo_* columns (§5.2)",
    ),
    NodeTable(
        "SiteObservation",
        [
            ("id", "STRING"),
            ("peptide_sequence", "STRING"),
            ("localization_prob", "DOUBLE"),
            ("score", "DOUBLE"),
            ("is_decoy", "BOOLEAN"),
            ("n_imputed", "INT64"),
            ("quant_ref", "STRING"),
        ],
    ),
    NodeTable(
        "ProteinObservation", [("id", "STRING"), ("quant_ref", "STRING"), ("n_peptides", "INT64")]
    ),
    NodeTable(
        "Contrast",
        [("id", "STRING"), ("label", "STRING"), ("numerator", "STRING"), ("denominator", "STRING")],
    ),
    NodeTable(
        "DifferentialResult",
        [
            ("id", "STRING"),
            ("log2fc", "DOUBLE"),
            ("p_value", "DOUBLE"),
            ("adj_p_value", "DOUBLE"),
            ("protein_adjusted", "STRING"),
            ("adjustment_method", "STRING"),
        ],
    ),
    NodeTable(
        "Analysis",
        [
            ("id", "STRING"),
            ("label", "STRING"),
            ("kind", "STRING"),
            ("basis", "STRING"),
            ("confidence", "STRING"),
            ("rationale", "STRING"),
            ("quantity", "STRING"),
            ("localization_threshold", "DOUBLE"),
            ("filters_applied", "STRING[]"),
            ("test", "STRING"),
            ("fdr_method", "STRING"),
            ("workflow_id", "STRING"),
            ("workflow_revision", "STRING"),
            ("parameters_json", "STRING"),
            ("started_at", "TIMESTAMP"),
            ("ended_at", "TIMESTAMP"),
            # §5.4 external-analysis columns
            ("external_tool", "STRING"),
            ("external_version", "STRING"),
            ("parameters_observed", "BOOLEAN"),
        ],
        note="external_* / parameters_observed columns (§5.4)",
    ),
    NodeTable("Person", [("id", "STRING"), ("name", "STRING"), ("orcid", "STRING")]),
    NodeTable(
        "Software",
        [
            ("id", "STRING"),
            ("name", "STRING"),
            ("version", "STRING"),
            ("container_digest", "STRING"),
        ],
    ),
    # ── Evidenced inference nodes (ONTOLOGY.md §6) ──
    NodeTable(
        "ModifierAssignment",
        [
            ("id", "STRING"),
            ("candidate_modifiers", "STRING[]"),
            ("basis", "STRING"),
            ("confidence", "STRING"),
            ("rationale", "STRING"),
            ("asserted_at", "TIMESTAMP"),
            ("retracted_at", "TIMESTAMP"),
        ],
    ),
    NodeTable(
        "EnzymeAssociation",
        [
            ("id", "STRING"),
            ("direction", "STRING"),
            ("basis", "STRING"),
            ("effect_size", "DOUBLE"),
            ("adj_p_value", "DOUBLE"),
            ("confidence", "STRING"),
            ("rationale", "STRING"),
            ("asserted_at", "TIMESTAMP"),
            ("retracted_at", "TIMESTAMP"),
        ],
    ),
    NodeTable(
        "ProteinAssignment",
        [
            ("id", "STRING"),
            ("candidate_proteins", "STRING[]"),
            ("basis", "STRING"),
            ("confidence", "STRING"),
            ("rationale", "STRING"),
            ("asserted_at", "TIMESTAMP"),
            ("retracted_at", "TIMESTAMP"),
        ],
    ),
    NodeTable(
        "Imputation",
        [
            ("id", "STRING"),
            ("method", "STRING"),
            ("downshift_sd", "DOUBLE"),
            ("width_sd", "DOUBLE"),
            ("seed", "INT64"),
            ("scope", "STRING"),
            ("n_values_imputed", "INT64"),
            ("n_values_total", "INT64"),
            ("asserted_at", "TIMESTAMP"),
            ("retracted_at", "TIMESTAMP"),
        ],
    ),
]

REL_TABLES: list[RelTable] = [
    # §4
    RelTable("ENCODES", "Gene", "Protein", multiplicity="ONE_MANY"),
    RelTable("HAS_SEQUENCE", "Protein", "ProteinSequence", multiplicity="ONE_MANY"),
    RelTable("SITE_ON", "ModificationSite", "ProteinSequence", multiplicity="MANY_MANY"),
    RelTable(
        "ANNOTATED_IN",
        "Protein",
        "Pathway",
        properties=[("source", "STRING"), ("evidence_code", "STRING")],
    ),
    # §5
    RelTable("CONTAINS", "Project", "Experiment", multiplicity="ONE_MANY"),
    RelTable("PERFORMED_ON", "Experiment", "Sample", multiplicity="ONE_MANY"),
    RelTable("PRODUCED", "Sample", "Dataset"),
    RelTable("REPORTS_SITE", "Dataset", "SiteObservation", multiplicity="ONE_MANY"),
    RelTable("REPORTS_PROTEIN", "Dataset", "ProteinObservation", multiplicity="ONE_MANY"),
    RelTable("RESULT_FOR_SITE", "DifferentialResult", "SiteObservation", multiplicity="MANY_ONE"),
    RelTable("RESULT_FOR_PROTEIN", "DifferentialResult", "ProteinObservation", multiplicity="MANY_ONE"),
    RelTable("RESULT_IN_CONTRAST", "DifferentialResult", "Contrast", multiplicity="MANY_ONE"),
    RelTable("ADJUSTED_BY", "DifferentialResult", "DifferentialResult", multiplicity="MANY_ONE"),
    RelTable("SAMPLE_GENERATED_BY", "Sample", "Analysis", multiplicity="MANY_ONE"),
    RelTable("CURATION_CITES", "Analysis", "Publication"),
    # §5.1 Observation contract
    RelTable("REPORTED_BY", "SiteObservation", "Dataset", multiplicity="MANY_ONE"),
    RelTable("RESOLVES_TO_SITE", "SiteObservation", "ModificationSite", multiplicity="MANY_ONE"),
    RelTable("RESOLVES_TO_PROTEIN", "ProteinObservation", "Protein", multiplicity="MANY_ONE"),
    # §6.1 modifier assignment
    RelTable("MEASURED_AT", "SiteObservation", "ModificationSite", multiplicity="MANY_ONE"),
    RelTable("ASSIGNMENT_FOR", "ModifierAssignment", "SiteObservation", multiplicity="MANY_ONE"),
    RelTable("ASSIGNS", "ModifierAssignment", "Modifier", multiplicity="MANY_ONE"),
    RelTable("ASSIGNMENT_SUPPORTED_BY", "ModifierAssignment", "Analysis"),
    RelTable("ASSIGNMENT_CITES", "ModifierAssignment", "Publication"),
    # §6.2 enzyme association
    RelTable("ASSOCIATION_FOR", "EnzymeAssociation", "SiteObservation", multiplicity="MANY_ONE"),
    RelTable("ASSOCIATION_ENZYME", "EnzymeAssociation", "Protein", multiplicity="MANY_ONE"),
    RelTable("ASSOCIATION_SUPPORTED_BY", "EnzymeAssociation", "Analysis"),
    RelTable("ASSOCIATION_CITES", "EnzymeAssociation", "Publication"),
    # §6.3 protein assignment
    RelTable(
        "PROTEIN_ASSIGNMENT_FOR", "ProteinAssignment", "SiteObservation", multiplicity="MANY_ONE"
    ),
    RelTable("ASSIGNS_PROTEIN", "ProteinAssignment", "Protein", multiplicity="MANY_ONE"),
    # §6.5 imputation
    RelTable("IMPUTATION_FOR", "Imputation", "Analysis", multiplicity="MANY_ONE"),
    # §7 provenance (PROV-O)
    RelTable("WAS_GENERATED_BY", "DifferentialResult", "Analysis", multiplicity="MANY_ONE"),
    RelTable("USED", "Analysis", "Dataset"),
    RelTable("WAS_ASSOCIATED_WITH", "Analysis", "Person", multiplicity="MANY_ONE"),
    RelTable("WAS_EXECUTED_BY", "Analysis", "Software", multiplicity="MANY_ONE"),
    RelTable("WAS_DERIVED_FROM", "DifferentialResult", "SiteObservation"),
]


def _node_ddl(t: NodeTable) -> str:
    cols = ", ".join(f"{name} {ktype}" for name, ktype in t.columns)
    return f"CREATE NODE TABLE {t.name}({cols}, PRIMARY KEY ({t.primary_key}))"


def _rel_ddl(t: RelTable) -> str:
    parts = [f"FROM {t.src} TO {t.dst}"]
    parts += [f"{name} {ktype}" for name, ktype in t.properties]
    if t.multiplicity is not None:
        parts.append(t.multiplicity)
    return f"CREATE REL TABLE {t.name}({', '.join(parts)})"


def ddl_statements() -> list[str]:
    """The full schema as ordered Cypher — every node table, then every rel table."""
    return [_node_ddl(t) for t in NODE_TABLES] + [_rel_ddl(t) for t in REL_TABLES]


def table_names() -> set[str]:
    return {t.name for t in NODE_TABLES} | {t.name for t in REL_TABLES}


def create_schema(conn: kuzu.Connection) -> None:
    """Apply the full DDL to an open Kùzu connection."""
    for statement in ddl_statements():
        conn.execute(statement)
