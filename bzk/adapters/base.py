"""The ingestion adapter contract (ARCHITECTURE.md §3).

An adapter turns one search-engine or analysis-tool output file into a *self-contained change-set*
that `invariants.validate` accepts and the graph can write — batched by a complete fact (ADR-0019),
never a partial one. The signature is `(file, SampleMapping)`, never a directory convention, so
local and PRIDE-downloaded datasets are ingested identically.

Two adapter classes (ARCHITECTURE.md §3):
  - **analysis-output** (Perseus): ingest results computed elsewhere — `Analysis.kind = 'external'`,
    `parameters_observed = false` (ADR-0017, I19);
  - **search-output** (MaxQuant, DIA-NN): ingest raw quantification, retaining the matrix (I11).
Both emit the same contract defined here. The adapter module is the *one* place pipeline-specific
handling lives; downstream code sees only recorded fields, never branches on them (I13).
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from bzk.quant import store as quant_store

# A change-set node is `{invariants.NODE_TYPE_KEY: <node type>, "id", **columns}` and an edge is
# `{"type", "from", "to", **properties}` — the format ADR-0019 governs and `invariants.py` enforces.
# The node-type key is `__label__`, not `label`, because `label` is a real DDL column on six node
# tables; see that module. Note the distinction from `SampleMapping.samples` below, whose entries
# are descriptors rather than change-set nodes.
Node = dict[str, Any]
Edge = dict[str, Any]


@dataclass(frozen=True)
class SampleMapping:
    """The sample-to-condition mapping, already written to the graph as a curation `Analysis`
    (ONTOLOGY.md §5.3).

    The adapter consumes this — never a configuration file — and links the `Sample` nodes it emits
    to that curation `Analysis` by `SAMPLE_GENERATED_BY`. The `basis` and `confidence` recorded on
    that `Analysis` propagate to every derived result, which is what I8 enforces at export.
    """

    curation_analysis_id: str
    samples: list[dict[str, Any]]  # per-sample descriptors: label, genotype, treatment, replicate…


@dataclass(frozen=True)
class Refusal:
    """One input row that did not become a node, and why.

    An adapter that filters is normal; an adapter that filters *silently* is the defect `CLAUDE.md`
    § Flag rather than hide names. A change-set is a claim about what a file contained, and a file
    of 2,056 rows that yields 1,900 sites has said something about the other 156 — sometimes the
    most interesting thing in the run, as with sequence drift in `maxquant_sites.py`.

    `reason` is a short stable slug so refusals can be counted by kind; `detail` is for the human
    reading the report and may name values. Deliberately not an exception: one unusable row must not
    sink a batch of thousands, and a per-row raise would make the count unobtainable.

    **The model is unchanged as of 2026-08-09; what that day added is the boundary around it.**
    Enumerating every population that loses rows found **three kinds and not one**, and this type is
    only the second:

    * **Declared-filter drops** — decoys and contaminants (43), localisation (242), the presence
      rule (667). The criterion is stated in advance and recorded in `Analysis.filters_applied`;
      nothing about an individual row is interesting, because the row failed a threshold. These are
      **not** `Refusal`s and must not become them: a count against a declared filter is a different
      fact from a row the platform could not key.
    * **Keying failures** — this type. 27 on PXD018299: `residue_mismatch` 15, `unresolved_protein`
      11, `no_razor_pick` 1, behind which sit 7 accessions the resolver could not key. The
      platform's own machinery failed against a specific row, and the row is worth naming
      individually — residue drift is a finding about UniProt rather than about data quality.
    * **Unreadable input** — `perseus.py` raises `PerseusError` for a missing column or an
      undeclared contrast and produces **no `Refusal` at all**. That is not a second adapter
      disagreeing with the sentence above: *deliberately not an exception* is about **rows**, and a
      file with no usable column has no rows to refuse.

    **A refusal is not an entity**, decided the same day and recorded in `ROADMAP.md`
    § *Measured findings*: it has no id by construction, `evidence_id` refuses a label §3 does not
    carry, and `unprovenanced` iterates §7's `prov:Entity` list — so a node type here would sit
    outside the one invariant the read layer enforces. Nothing is stored; `query.refusals` answers
    `NOT_RETAINED` and that remains true.
    """

    row: str
    reason: str
    detail: str


@dataclass(frozen=True)
class ParsedObservations:
    """One adapter's output as a self-contained change-set (ADR-0019).

    `nodes` and `edges` together must pass `invariants.validate(nodes, edges)` as a complete fact —
    every referent present, correctly labelled, multiplicity respected. Satisfies the `Observation`
    contract (ONTOLOGY.md §5.1) and makes no tryptic assumptions (I12): peptides need not end in
    K or R, may carry several modifications, and may map to more than one protein.

    `refusals` defaults to empty, so an adapter that cannot refuse anything says nothing about it.
    """

    nodes: list[Node]
    edges: list[Edge]
    refusals: list[Refusal] = dc_field(default_factory=list)
    #: The per-sample values I11 requires retained, as `(observation label, cells)` — the columnar
    #: half of `ONTOLOGY.md` §2's boundary, which the change-set cannot carry because a change-set
    #: is graph content and these are one-per-entity-per-sample (ADR-0004).
    #:
    #: **The adapter is the writer, and that is what settles pre- versus post-imputation.**
    #: `ARCHITECTURE.md` § *Imputation is part of the statistics layer, not the adapter* says
    #: adapters emit measured values and nulls; since the values leave through here, that sentence
    #: governs directly rather than being re-decided (ADR-0013). Empty for an adapter that reports
    #: no per-sample values, which is a different state from reporting nulls.
    cells: list[tuple[str, list[quant_store.Cell]]] = dc_field(default_factory=list)


@runtime_checkable
class ObservationAdapter(Protocol):
    """One module per search engine or analysis tool (ARCHITECTURE.md §3)."""

    name: str  # 'perseus' | 'maxquant' | 'diann' | 'fragpipe' | 'spectronaut'

    def sniff(self, path: Path) -> bool:
        """True if this adapter recognises the file. Sniff the file's content, never a folder
        shape — search engines differ in output layout more than in output content."""
        ...

    def parse(self, path: Path, mapping: SampleMapping) -> ParsedObservations:
        """Parse one file into a change-set the invariant layer accepts. Recording — not
        branching downstream on — `search_engine`, `acquisition_mode` and `library_type` is the
        adapter's job (I13); this module is where pipeline-specific handling is allowed to live."""
        ...
