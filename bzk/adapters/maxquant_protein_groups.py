"""MaxQuant `proteinGroups.txt` → `ProteinObservation` plus its per-sample values (ADR-0004, I11).

The protein-grain twin of `maxquant_sites.py`, and shorter than it for a reason worth stating: at
site grain a razor pick is unavoidable because a `ModificationSite` key carries a protein-specific
position, and everything downstream of that — the pick, its refusal, the promotion, the residue
check — is machinery this grain does not need. **ADR-0022 made the group the identity**, so a
protein group is ingested as the set the search reported and nothing is chosen.

**What it inherits rather than re-derives.** `maxquant.read_table` drops the **six spill lines** in
`HAP1_USP18KO_proteinGroups.txt` — each carries 147 tabs, so the field count matches the header and
every structural check passes — using the file's own contiguous `id` column rather than a
heuristic; and it reads bytes and decodes explicitly against the CRLF hazard. Going through the
reader is the whole reason it was written before this module existed.

**`Protein IDs`, not `Majority protein IDs`.** §3 calls `candidate_proteins` *the protein group as
the search reported it*. `Majority protein IDs` is MaxQuant's narrowing to the subset carrying at
least half the peptides, which §6.3 calls its own razor-rule inference; reading it would put an
inference where the observation belongs. `perseus.PROTEIN_COLUMNS` prefers the same column, so the
two adapters agree without either of them deciding.

**The declared quantity chooses the column family**, so I16's record and the numbers cannot
disagree: `lfq` reads `LFQ intensity `, `intensity` reads `Intensity `, `ibaq` reads `iBAQ `. Bare
`intensity` is legal here and only here — §5's enum permits it where there is no multiplicity axis.

**One invariant fires at this grain, and the pre-registration said none did.** That claim came from
a probe that removed `quant_ref`, `REPORTS_PROTEIN` and `RESOLVES_TO_PROTEIN` *entirely* and watched
each batch validate — but I14's second half fires only on a **strict non-empty subset**: an
observation naming a group while resolving to *some* of it is a razor pick asserted through an edge,
and pointing at none of it is a node re-staged as a referent (ADR-0019), which is legal. So the
probe could not have fired the one guard there is; removing all three edges is the shape that hides
it. Re-probed here: three candidates with all three edges validates, with none validates, **with one
or two the batch is refused by name**. Everything else at this grain is still this module's and its
tests' — I3 forces a `ModifierAssignment` onto every `SiteObservation` and has no counterpart here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bzk.adapters import maxquant
from bzk.adapters.base import ParsedObservations, Refusal, SampleMapping, sample_nodes
from bzk.adapters.maxquant import drop_decoys_and_contaminants, read_table
from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.keys import evidence_id, protein_key
from bzk.provenance.raw_store import content_hash
from bzk.quant import store as quant_store
from bzk.resolve.nodes import ResolvedProteins

Node = dict[str, Any]
Edge = dict[str, Any]

#: Shared with `perseus.py` for the same reason it lives there: a `Protein` staged twice is
#: last-write-wins, so what an unresolved candidate carries is decided in one place.
_UNRESOLVED = ResolvedProteins(nodes=[], edges=[], protein_id={})

#: The declared quantity and the column family it names. Reading is driven by the declaration, so
#: an `Analysis` recording `lfq` over `Intensity ` columns is unrepresentable rather than a mistake
#: a reviewer has to catch (I16).
#:
#: **`ibaq` is in §5's enum and has no columns in this deposit.** Measured on
#: `HAP1_USP18KO_proteinGroups.txt`: 14 `Intensity `, 14 `LFQ intensity `, **0 `iBAQ`** — the
#: pre-registration's *fourteen columns per family, `Intensity `, `LFQ intensity `, `iBAQ `* is
#: wrong on the third and the file carries no iBAQ column of any spelling, bare or per-sample. The
#: row stays because iBAQ is a MaxQuant output option rather than a MaxQuant-version fact, and
#: because a declaration naming it against this file then raises by name in `_sample_columns`
#: instead of reading a family that is not there.
QUANTITY_COLUMNS: dict[str, str] = {
    "intensity": "Intensity ",
    "lfq": "LFQ intensity ",
    "ibaq": "iBAQ ",
}

#: Applied before anything else, and recorded on the ingestion `Analysis` (I16).
FILTERS_APPLIED = ("reverse", "potential_contaminant")

ACCESSION_COLUMN = "Protein IDs"
PEPTIDE_COUNT_COLUMNS = ("Peptides", "Razor + unique peptides")


class MaxQuantProteinGroupsError(ValueError):
    """A MaxQuant `proteinGroups.txt` cannot be ingested as given."""


@dataclass(frozen=True)
class DeclaredProteinAnalysis:
    """What the file does not state about the search that produced it (I13, I16)."""

    search_engine: str
    external_version: str
    #: From §5's closed enum, and it selects the column family read below.
    quantity: str = "lfq"
    acquisition_mode: str | None = None
    fasta_release: str | None = None


@dataclass(frozen=True)
class ProteinIngestReport:
    """What the file contained and what became of it. Every number here is a finding."""

    rows_read: int
    spill_lines: int
    dropped_decoy_or_contaminant: int
    groups_emitted: int
    refused_empty_group: int
    distinct_accessions: int
    cells: int
    #: MaxQuant row `id` → the `ProteinObservation` id it became, for the same reason the site
    #: adapter carries one: nothing on the observation records its source row, and re-deriving the
    #: key outside the adapter would be a second source of truth for identity.
    observation_of_row: dict[str, str] = field(default_factory=dict)


def _sample_columns(
    mapping: SampleMapping, column: Mapping[str, int], prefix: str
) -> list[tuple[str, str]]:
    """`(Sample.id, column name)` per mapped sample.

    The curation maps each sample to a **column name**, so the column is taken from the mapping
    rather than guessed from a run label. A key naming a column this file does not have raises: a
    mapping the adapter cannot place is a curation problem, and skipping the sample would drop it
    from the matrix while leaving its `Sample` node in the graph — I11 unmet in a shape nothing
    would notice, which is the failure `maxquant_sites.py` records for the same reason.
    """
    placed = []
    for sample in mapping.samples:
        key = str(sample.get("mapping_key", ""))
        if key not in column:
            raise MaxQuantProteinGroupsError(
                f"sample mapping key {key!r} names no column in this file. Expected a column of "
                f"the declared quantity's family ({prefix!r}); found "
                f"{sorted(c for c in column if c.startswith(prefix))}"
            )
        if not key.startswith(prefix):
            raise MaxQuantProteinGroupsError(
                f"sample mapping key {key!r} is not of the declared quantity's family {prefix!r}. "
                "The declared quantity chooses the columns, so a mapping naming another family "
                "would record one quantity on the Analysis and store another (I16)."
            )
        placed.append((str(sample["id"]), key))
    return placed


class MaxQuantProteinGroupsAdapter:
    """`ObservationAdapter` for a MaxQuant `proteinGroups.txt` (`ARCHITECTURE.md` §3)."""

    name = "maxquant_protein_groups"

    def __init__(self, declared: DeclaredProteinAnalysis) -> None:
        if declared.quantity not in QUANTITY_COLUMNS:
            raise MaxQuantProteinGroupsError(
                f"quantity {declared.quantity!r} names no column family here; "
                f"expected one of {sorted(QUANTITY_COLUMNS)}"
            )
        self.declared = declared
        self.report: ProteinIngestReport | None = None

    def sniff(self, path: Path) -> bool:
        """True for a MaxQuant protein-groups table.

        Content, not name (`ARCHITECTURE.md` §3). What distinguishes it from the site table in the
        same deposit is that it carries a protein-group accession column and **no** per-site
        residue or position — the site table's own `sniff` keys on exactly those, so the two are
        mutually exclusive rather than merely different.
        """
        try:
            header = read_table(path).header
        except (OSError, ValueError):
            return False
        return ACCESSION_COLUMN in header and not {
            "Amino acid",
            "Positions within proteins",
        } <= set(header)

    def parse(self, path: Path, mapping: SampleMapping) -> ParsedObservations:
        """One protein-groups table into a self-contained change-set (ADR-0019), plus its cells."""
        if not mapping.samples:
            raise MaxQuantProteinGroupsError(
                f"{path.name}: no sample mapping. A protein group with no sample has no values to "
                "retain, and ingesting it would set quant_ref over an empty matrix (I11)."
            )
        table = read_table(path)
        column = {name: i for i, name in enumerate(table.header)}
        if ACCESSION_COLUMN not in column:
            raise MaxQuantProteinGroupsError(
                f"{path.name} has no {ACCESSION_COLUMN!r} column; found {sorted(table.header)}"
            )
        prefix = QUANTITY_COLUMNS[self.declared.quantity]
        samples = _sample_columns(mapping, column, prefix)
        peptides = next((c for c in PEPTIDE_COUNT_COLUMNS if c in column), None)

        kept = drop_decoys_and_contaminants(table)
        raw = path.read_bytes()
        dataset: Node = {
            NODE_TYPE_KEY: "Dataset",
            "label": path.name,
            "content_hash": content_hash(raw),
            "source": "pride",
            # I13: pipeline metadata is recorded data and lives on the `Dataset`.
            "search_engine": self.declared.search_engine,
            "search_engine_version": self.declared.external_version,
            "acquisition_mode": self.declared.acquisition_mode,
            "fasta_release": self.declared.fasta_release,
        }
        dataset_id = evidence_id("Dataset", dataset)
        dataset["id"] = dataset_id
        # `sample_nodes`, not `mapping.samples`: the entries are descriptors and carry a
        # `mapping_key` that is not a DDL column (`base.py`). The first draft passed them through.
        nodes: list[Node] = [*sample_nodes(mapping), dataset]
        edges: list[Edge] = [
            {"type": "PRODUCED", "from": str(s["id"]), "to": dataset_id} for s in mapping.samples
        ]

        # The ingestion `Analysis`, for `maxquant_sites.py`'s reason: this adapter drops rows, and
        # a filter the platform applied and did not record is the invisible analytical choice
        # `ROADMAP.md` names. `kind = 'processing'` with `parameters_observed = True` — the platform
        # chose and executed this filtering; what it did not witness is the MaxQuant search, whose
        # parameters sit on the `Dataset` above where I13 puts them.
        analysis: Node = {
            "label": f"ingest {path.name}",
            "kind": "processing",
            "quantity": self.declared.quantity,
            "filters_applied": sorted(FILTERS_APPLIED),
            "parameters_observed": True,
            # Determined by `kind`: `basis` and `confidence` are curation's fields (§3, §5.3).
            "basis": None,
            "confidence": None,
            # This analysis filters; it runs no test, and a protein-level quantity has no residues
            # to localise. §3 classifies all three absences as determined.
            "test": None,
            "fdr_method": None,
            "localization_threshold": None,
            "external_tool": None,
            "external_version": None,
        }
        analysis_id = evidence_id("Analysis", analysis, {"Dataset": dataset_id})
        analysis["id"] = analysis_id
        analysis[NODE_TYPE_KEY] = "Analysis"
        nodes.append(analysis)
        edges.append({"type": "USED", "from": analysis_id, "to": dataset_id})

        refusals: list[Refusal] = []
        cells: list[quant_store.Cell] = []
        observation_of_row: dict[str, str] = {}
        row_of_observation: dict[str, str] = {}
        staged_proteins: set[str] = set()
        for row in kept:
            row_id = row[column["id"]]
            group = _split(row[column[ACCESSION_COLUMN]])
            if not group:
                # The one refusal this grain has, and it is a counted kind and nothing more —
                # refusals are settled as not-entities. `candidate_proteins` is identifying, so an
                # empty list would key every such row identically and silently merge them.
                refusals.append(
                    Refusal(
                        row=row_id,
                        reason="empty_protein_group",
                        detail=(
                            f"{ACCESSION_COLUMN!r} is empty, so the group has no identity: "
                            "candidate_proteins is identifying (§3, ADR-0022) and an empty list "
                            "would key every such row to one node."
                        ),
                    )
                )
                continue
            protein_ids = [protein_key(a) for a in group]
            # Candidate `Protein`s recur across the batch — 23,807 accessions over 4,797 groups on
            # PXD018299 — and ADR-0019 refuses a duplicate id, so each is staged at most once.
            # Filtered before minting rather than deduplicated after: a post-pass over every node
            # would also absorb a duplicate `ProteinObservation`, which is the one duplicate that
            # must be refused rather than folded (below).
            for candidate in _UNRESOLVED.candidate_nodes(group):
                if str(candidate["id"]) not in staged_proteins:
                    staged_proteins.add(str(candidate["id"]))
                    nodes.append(candidate)

            observation: Node = {
                # Identifying, and `keys.canonical_value` sorts `STRING[]` before hashing, so
                # MaxQuant's ordering — which is its own ranking, an inference — cannot fork an id.
                "candidate_proteins": protein_ids,
                # I11's witness at the node (ADR-0004). Names the columnar *table*, not a join key.
                # Set unconditionally because the cells below are always emitted, nulls included.
                "quant_ref": quant_store.quant_ref("ProteinObservation"),
            }
            if peptides is not None and row[column[peptides]].strip():
                observation["n_peptides"] = int(row[column[peptides]])
            observation_id = evidence_id("ProteinObservation", observation, {"Dataset": dataset_id})
            if observation_id in row_of_observation:
                # Two rows keying to one observation is the file contradicting the identity
                # ADR-0022 fixed: `candidate_proteins` is the whole group, and MaxQuant's groups
                # are disjoint, so two rows cannot name the same set. Measured 0 on PXD018299
                # (4,797 rows, 4,797 distinct sorted groups). Raised rather than refused because
                # neither row can be chosen and folding them would overwrite one row's cells with
                # the other's under `INSERT OR REPLACE` — a merge nothing downstream could see.
                raise MaxQuantProteinGroupsError(
                    f"{path.name}: rows {row_of_observation[observation_id]} and {row_id} name the "
                    f"same protein group, so both key to {observation_id}. Protein groups are "
                    "disjoint by construction; a file where two are identical cannot be ingested "
                    "without choosing between them (§3, ADR-0022)."
                )
            observation["id"] = observation_id
            observation[NODE_TYPE_KEY] = "ProteinObservation"
            nodes.append(observation)
            observation_of_row[row_id] = observation_id
            row_of_observation[observation_id] = row_id
            edges.append({"type": "REPORTS_PROTEIN", "from": dataset_id, "to": observation_id})
            for protein_id in protein_ids:
                edges.append(
                    {"type": "RESOLVES_TO_PROTEIN", "from": observation_id, "to": protein_id}
                )
            for sample_id, name in samples:
                cells.append(
                    quant_store.Cell(
                        observation_id=observation_id,
                        sample_id=sample_id,
                        quantity=self.declared.quantity,
                        # `maxquant.cell_value`, not a local one. The first draft here folded `0`
                        # to `None` — MaxQuant does write 0 for an unquantified protein — and that
                        # is a reading `maxquant_sites.py` had already refused to make (I19). Two
                        # adapters over one deposit cannot mean two things by a zero, so the
                        # convention has one home and this defers to it.
                        value=maxquant.cell_value(row, column, name),
                    )
                )

        # Same contract as every other producer of a change-set: a batch that cannot validate never
        # leaves this module half-written.
        invariants.validate(nodes, edges)
        self.report = ProteinIngestReport(
            rows_read=len(table.rows),
            spill_lines=table.spill_lines,
            dropped_decoy_or_contaminant=len(table.rows) - len(kept),
            groups_emitted=len(observation_of_row),
            refused_empty_group=len(refusals),
            distinct_accessions=len(staged_proteins),
            cells=len(cells),
            observation_of_row=observation_of_row,
        )
        return ParsedObservations(
            nodes=nodes,
            edges=edges,
            refusals=refusals,
            cells=[("ProteinObservation", cells)] if cells else [],
        )


def _split(cell: str) -> list[str]:
    return [a.strip() for a in cell.split(";") if a.strip()]
