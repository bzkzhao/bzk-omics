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
