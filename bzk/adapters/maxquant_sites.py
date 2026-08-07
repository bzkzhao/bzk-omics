"""The MaxQuant GlyGly-site adapter — the first *search-output* adapter (`ARCHITECTURE.md` §3).

Where `perseus.py` ingests numbers someone else computed, this ingests what the search engine
reported: one row of `GlyGly (K)Sites.txt` becomes a `SiteObservation` on a `ModificationSite`,
keyed against a specific `ProteinSequence`. That last clause is the whole difficulty. A protein
grain needs no sequence at all; a *position* is meaningless without one, so this adapter cannot
emit anything until it knows what UniProt currently calls sequence version *n* of the protein — and
what UniProt currently says is not what the search saw in 2019.

**The residue check is the point of this module, not a safety net.** Every site names a residue
(`Amino acid`) and a position, and the resolved sequence either has that residue there or it does
not. Where it does not, the site is **refused** — not silently kept, not silently dropped — and
counted, because the count is a measurement of how far this deposit has drifted from today's
UniProt and nothing else in the project measures it. `ROADMAP.md` § Measured findings carries the
number. A run that quietly accepted the mismatches would key sites at positions that mean something
different now than they did then, which is the isoform-stripping defect of `HANDOFF.md` §6 in its
third form: arithmetic that runs, prints cleanly and is wrong.

**Refusals are returned, never logged and dropped.** `ParsedObservations.refusals` carries one
entry per refused row with the reason, so the caller sees what did not make it into the graph.
`CLAUDE.md`: flag rather than hide.

Three things this adapter decides, each measured on the real file first (2,341 rows → 2,298 after
decoys and contaminants → 2,056 at `Localization prob >= 0.75`):

1. **Which protein keys the site.** MaxQuant's `Protein` column — its razor pick. `Positions within
   proteins` is index-aligned with `Proteins` (0 of 2,056 rows mismatched in length), and the
   `Position` column agrees with the aligned entry on 2,055 of 2,055 rows where the pick is in the
   list, so the pick's position is read directly rather than inferred. Choosing a pick is *permitted
   here and nowhere else*: I14 says so explicitly at site grain, because a `ModificationSite` key
   carries a protein-specific position and pointing at every candidate is not available. The
   multi-mapping is not lost — it is carried by `candidate_proteins`, which names all of them and is
   identifying (ADR-0022). 1,693 of 2,056 rows (82.3%) name a group, matching the 82% on record.

2. **A row with no razor pick is refused.** One row (`id` 1319, YWHAB/SFN) carries seven proteins,
   two leading proteins and an *empty* `Protein` column: MaxQuant declined to pick. Falling back to
   the first leading protein would be inventing the pick it withheld, and the choice is not even
   cosmetic — the group splits `11;13;13;13;13;11;11`, so which member is picked changes the
   position the site is keyed at. Refused and counted.

3. **Candidates that key nothing are not resolved.** Only the 1,054 distinct razor picks need a
   sequence; the 4,631 accessions named across `Proteins` need only a `Protein` node, which
   `protein_key` mints from the accession alone. Resolving all of them would be ~4,600 network
   calls to populate a field that is a list of ids. The `Protein` node is identical either way —
   `resolve_to_nodes` also emits accession-only `Protein`s — so this is a cost decision, not a
   modelling one.

I13 holds: `search_engine` and the rest are recorded on the `Dataset`, never branched on. Reading
`Amino acid` and `Localization prob` is branching on *file content*, which is what an adapter is for.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from bzk.adapters import maxquant
from bzk.adapters.base import Edge, Node, ParsedObservations, Refusal, SampleMapping
from bzk.ontology import invariants, schema
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.keys import evidence_id, modification_site_key, protein_key
from bzk.provenance.raw_store import content_hash
from bzk.resolve.nodes import ResolvedProteins, Resolver, residue_at, resolve_to_nodes

#: The Unimod accession for the GlyGly remnant. §4 pins Unimod as the sole key authority — a
#: PSI-MOD spelling of the same modification would fragment the site into a second node (I7).
GLYGLY = "unimod:121"

#: Columns this adapter cannot proceed without, and what each is for. Checked up front so a missing
#: one is a property of the file rather than a crash on row 4,000.
REQUIRED_COLUMNS = (
    "Proteins",  # the observed candidate set (§6.3: the widest column, not `Leading proteins`)
    "Protein",  # MaxQuant's razor pick — what the site is keyed against
    "Position",  # the pick's 1-based position
    "Amino acid",  # the residue the search reported, checked against the resolved sequence
    "Localization prob",  # I16's localisation threshold applies to this column
    "id",  # MaxQuant's row number, used to name a refusal
)


class MaxQuantSiteError(ValueError):
    """A MaxQuant site table cannot be ingested. Never downgraded to a warning (`CLAUDE.md`)."""


#: `Sample` columns, so a descriptor can be narrowed to the node inside it. `SampleMapping.samples`
#: holds *descriptors* (`base.py`), and the curation loader's carry a `mapping_key` — the column
#: header the curation was written against — which is not a DDL column and must not reach the graph.
_SAMPLE_COLUMNS = frozenset(
    c for t in schema.NODE_TABLES if t.name == "Sample" for c, _ in t.columns
)


def _sample_nodes(mapping: SampleMapping) -> list[Node]:
    """The `Sample` nodes inside the mapping's descriptors, with non-column keys dropped."""
    return [
        {NODE_TYPE_KEY: "Sample", **{k: v for k, v in s.items() if k in _SAMPLE_COLUMNS}}
        for s in mapping.samples
    ]


@dataclass(frozen=True)
class DeclaredSiteAnalysis:
    """What the file does not state about the search that produced it.

    Smaller than `perseus.DeclaredAnalysis` because a search output states far more about itself
    than an analysis output does — but `search_engine`, its version and the FASTA release are still
    the caller's to declare, and I16's `localization_threshold` is a filter this adapter *applies*,
    so it must be recorded as one.
    """

    search_engine: str
    external_version: str
    localization_threshold: float = 0.75
    #: The quantity the search reported, from §5's closed enum. Named specifically: a MaxQuant site
    #: table's bare `Intensity` hides the multiplicity axis, which I16 forbids at this grain.
    quantity: str = "intensity_multiplicity_summed"
    acquisition_mode: str | None = None
    fasta_release: str | None = None


@dataclass(frozen=True)
class SiteIngestReport:
    """What the file contained and what became of it. Every number here is a finding.

    Kept as counts *plus* the refusal list rather than counts alone: a bare number cannot be
    checked, and the residue-drift measurement is the kind of number someone will want to audit.
    """

    rows_read: int
    dropped_decoy_or_contaminant: int
    dropped_below_localization: int
    sites_emitted: int
    refused_no_razor_pick: int
    refused_unresolved_protein: int
    refused_residue_mismatch: int
    #: accession → why no `ProteinSequence` could be keyed, straight from `resolve_to_nodes`.
    unresolved: dict[str, str] = field(default_factory=dict)


class MaxQuantSiteAdapter:
    """`ObservationAdapter` for a MaxQuant `GlyGly (K)Sites.txt` (`ARCHITECTURE.md` §3).

    The resolver is injected on the constructor, not threaded through `parse`, so `parse(file,
    mapping)` keeps the signature the contract fixes. Tests pass a stub and never touch the network.
    """

    name = "maxquant"

    def __init__(self, declared: DeclaredSiteAnalysis, *, resolver: Resolver | None = None) -> None:
        if declared.quantity not in schema.QUANTITY_VALUES:
            raise MaxQuantSiteError(
                f"declared quantity {declared.quantity!r} is not in the closed enum "
                f"{sorted(schema.QUANTITY_VALUES)} (ONTOLOGY.md §5, I16). It is identifying on "
                "Analysis (§3), so a misspelling forks an id rather than failing."
            )
        if not 0.0 <= declared.localization_threshold <= 1.0:
            raise MaxQuantSiteError(
                f"localization_threshold {declared.localization_threshold!r} is not a probability"
            )
        self.declared = declared
        self.resolver = resolver
        self.report: SiteIngestReport | None = None

    # ── sniff ───────────────────────────────────────────────────────────────────────────────────

    def sniff(self, path: Path) -> bool:
        """True for a MaxQuant modification-site table.

        Content, not name (`ARCHITECTURE.md` §3): `proteinGroups.txt` and the Perseus export in this
        same deposit are also tab-separated `.txt`. What distinguishes a *site* table is that it
        carries a per-site residue and a position within the protein, which neither of those has.
        """
        try:
            header = path.read_bytes().decode("utf-8", errors="replace").splitlines()[0].split("\t")
        except (OSError, IndexError):
            return False
        return {"Amino acid", "Positions within proteins", "Localization prob"} <= set(header)

    # ── parse ───────────────────────────────────────────────────────────────────────────────────

    def parse(self, path: Path, mapping: SampleMapping) -> ParsedObservations:
        """One site table into a self-contained change-set (ADR-0019), plus its refusals."""
        if not mapping.samples:
            raise MaxQuantSiteError(
                "the SampleMapping carries no samples, so nothing links these sites to a curation "
                "activity; every one would be permanently `unprovenanced` (I5, ONTOLOGY.md §5.3)"
            )
        if not self.sniff(path):
            raise MaxQuantSiteError(
                f"{path} does not look like a MaxQuant site table — it carries no 'Amino acid' / "
                "'Positions within proteins' / 'Localization prob' columns. Refused rather than "
                "half-read."
            )

        raw = path.read_bytes()
        table = maxquant.read_table(path)
        missing = [c for c in REQUIRED_COLUMNS if c not in table.header]
        if missing:
            raise MaxQuantSiteError(
                f"{path} is missing {missing}; found {sorted(table.header)}. Refused rather than "
                "emitting a partial table, which would read as a smaller experiment."
            )
        column = {name: i for i, name in enumerate(table.header)}

        kept, dropped_decoy, dropped_loc = self._filter(table, column)
        resolved = resolve_to_nodes(
            {row[column["Protein"]] for row in kept if row[column["Protein"]]},
            resolver=self.resolver,
        )

        nodes: list[Node] = _sample_nodes(mapping) + list(resolved.nodes)
        edges: list[Edge] = list(resolved.edges)

        dataset = {
            "label": path.name,
            "content_hash": content_hash(raw),
            "source": "local",
            "search_engine": self.declared.search_engine,
            "acquisition_mode": self.declared.acquisition_mode,
            "fasta_release": self.declared.fasta_release,
        }
        dataset_id = evidence_id("Dataset", dataset)
        nodes.append(self._node("Dataset", dataset_id, dataset))
        for sample in mapping.samples:
            edges.append({"type": "PRODUCED", "from": sample["id"], "to": dataset_id})

        refusals: list[Refusal] = []
        emitted = 0
        for row in kept:
            outcome = self._site(row, column, resolved, dataset_id)
            if isinstance(outcome, Refusal):
                refusals.append(outcome)
                continue
            site_nodes, site_edges = outcome
            nodes.extend(site_nodes)
            edges.extend(site_edges)
            emitted += 1

        nodes = self._deduplicate(nodes)
        # Same contract as every other producer of a change-set: a batch that cannot validate never
        # leaves this module half-written.
        invariants.validate(nodes, edges)
        self.report = SiteIngestReport(
            rows_read=len(table.rows),
            dropped_decoy_or_contaminant=dropped_decoy,
            dropped_below_localization=dropped_loc,
            sites_emitted=emitted,
            refused_no_razor_pick=sum(r.reason == "no_razor_pick" for r in refusals),
            refused_unresolved_protein=sum(r.reason == "unresolved_protein" for r in refusals),
            refused_residue_mismatch=sum(r.reason == "residue_mismatch" for r in refusals),
            unresolved=dict(resolved.unresolved),
        )
        return ParsedObservations(nodes=nodes, edges=edges, refusals=refusals)

    # ── internals ───────────────────────────────────────────────────────────────────────────────

    def _filter(
        self, table: maxquant.MaxQuantTable, column: dict[str, int]
    ) -> tuple[list[list[str]], int, int]:
        """Decoys, contaminants and poorly localised sites, in that order, each counted.

        Counted rather than merely applied: `ROADMAP.md` § Measured findings records 2,341 → 2,298
        for the first and the threshold is I16's, so both belong in the report. The order matters
        only for the counts — a decoy below threshold is attributed to being a decoy.
        """
        after_decoys = maxquant.drop_decoys_and_contaminants(table)
        threshold = self.declared.localization_threshold
        index = column["Localization prob"]
        kept = [r for r in after_decoys if r[index].strip() and float(r[index]) >= threshold]
        return kept, len(table.rows) - len(after_decoys), len(after_decoys) - len(kept)

    def _site(
        self,
        row: list[str],
        column: dict[str, int],
        resolved: ResolvedProteins,
        dataset_id: str,
    ) -> tuple[list[Node], list[Edge]] | Refusal:
        """One row into its nodes and edges, or the reason it cannot become any.

        Three refusals, deliberately distinguished rather than merged into one "bad row" count:
        they are three different findings about the data and only one of them is a measurement of
        sequence drift.
        """
        row_id = row[column["id"]]
        pick = row[column["Protein"]].strip()
        if not pick:
            return Refusal(
                row=row_id,
                reason="no_razor_pick",
                detail=(
                    f"`Protein` is empty (candidates {row[column['Proteins']]!r}). MaxQuant declined "
                    "to pick, and a ModificationSite key composes exactly one ProteinSequence (§4); "
                    "choosing for it would invent the inference it withheld."
                ),
            )

        sequence_id = resolved.sequence_id.get(pick)
        if sequence_id is None:
            return Refusal(
                row=row_id,
                reason="unresolved_protein",
                detail=(
                    f"{pick} has no usable sequence: "
                    f"{resolved.unresolved.get(pick, 'not resolved')}. Without a sequence version "
                    "the site's position has no meaning (I2)."
                ),
            )

        position = int(row[column["Position"]])
        reported = row[column["Amino acid"]].strip().upper()
        actual = residue_at(resolved, pick, position)
        if actual != reported:
            return Refusal(
                row=row_id,
                reason="residue_mismatch",
                detail=(
                    f"{pick} position {position}: the search reported {reported!r}, "
                    f"{sequence_id} has {actual or 'nothing (past the end)'!r}. The sequence has "
                    "been amended since the search, so this position no longer means what the "
                    "search meant by it."
                ),
            )

        site_id = modification_site_key(sequence_id, reported, position, GLYGLY)
        nodes: list[Node] = [
            self._node(
                "ModificationSite",
                site_id,
                {"residue": reported, "position": position, "modification_type": GLYGLY},
            )
        ]
        edges: list[Edge] = [{"type": "SITE_ON", "from": site_id, "to": sequence_id}]

        candidates = [a.strip() for a in row[column["Proteins"]].split(";") if a.strip()]
        candidate_ids = [protein_key(a) for a in candidates]
        for accession, protein_id in zip(candidates, candidate_ids, strict=True):
            nodes.append(self._node("Protein", protein_id, {"accession": accession}))

        # `candidate_proteins` is identifying and `keys.canonical_value` sorts `STRING[]` before
        # hashing, so MaxQuant's ranking — an inference — cannot fork an id (I7, ADR-0022).
        observation: dict[str, object] = {
            "candidate_proteins": candidate_ids,
            "localization_prob": float(row[column["Localization prob"]]),
            "is_decoy": False,
        }
        if "Score" in column and row[column["Score"]].strip():
            observation["score"] = float(row[column["Score"]])
        observation_id = evidence_id(
            "SiteObservation",
            observation,
            {"Dataset": dataset_id, "ModificationSite": site_id},
        )
        nodes.append(self._node("SiteObservation", observation_id, observation))
        # **Only the two §3 anchors, not their duplicates.** The DDL declares four relationships
        # over these two pairs: `REPORTED_BY` (SiteObservation→Dataset, MANY_ONE) alongside
        # `REPORTS_SITE` (Dataset→SiteObservation, ONE_MANY), and `RESOLVES_TO_SITE` alongside
        # `MEASURED_AT` — which are the *same* endpoints and the *same* multiplicity as each other.
        # Emitting all four would write each fact twice and leave a reader unable to tell which is
        # authoritative, which is what `CLAUDE.md` § Single source of truth calls a defect rather
        # than redundancy. The two kept are the ones §3 anchors identity on, so they are the pair a
        # `SiteObservation` id is already a function of. Which duplicate survives in the DDL is an
        # ONTOLOGY question and is recorded in `HANDOFF.md` §8 rather than decided here.
        edges.append({"type": "REPORTED_BY", "from": observation_id, "to": dataset_id})
        edges.append({"type": "RESOLVES_TO_SITE", "from": observation_id, "to": site_id})
        return nodes, edges

    @staticmethod
    def _node(label: str, node_id: str, props: Mapping[str, object]) -> Node:
        return {NODE_TYPE_KEY: label, "id": node_id, **props}

    @staticmethod
    def _deduplicate(nodes: list[Node]) -> list[Node]:
        """Content-derived ids converge, so one `Protein` named by 400 rows is one node (I7)."""
        seen: dict[str, Node] = {}
        for node in nodes:
            seen.setdefault(node["id"], node)
        return list(seen.values())
