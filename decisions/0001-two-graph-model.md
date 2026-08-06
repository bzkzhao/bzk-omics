# ADR-0001 — Reference and evidence graphs are disjoint

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | — |

## Context

A biological knowledge graph holds two kinds of claim. Some describe entities that exist independently of any measurement: a lysine at position 42 of a given protein sequence, a pathway membership curated by Reactome, a disease term from MONDO. Others describe what this laboratory did and found: a peptide observed at a given intensity in a stated experiment.

The intuitive design puts both in one graph. `Analysis identifies Protein participates_in Pathway associated_with Disease` reads naturally and is how most public biological graphs are built.

## Decision

The graph is partitioned into two disjoint node sets, joined only through observation nodes.

**Reference nodes** are imported from external authorities and never authored locally: `Gene`, `Protein`, `ModificationSite`, `Modifier`, `Pathway`, `Disease`, `Drug`, `Publication`.

**Evidence nodes** are authored locally and carry provenance: `Project`, `Experiment`, `Sample`, `Dataset`, `Analysis`, and the observation subtypes.

Reference-to-reference edges carry a `source` field naming the external authority. No edge may connect two reference nodes with locally-authored semantics (invariant I1).

## Consequences

**Positive.** The system can answer "what did we measure" and "what does the literature claim" separately, and can distinguish them in any combined answer. Reference nodes are deterministically keyed, so identical entities from different sources converge without a merge step. The reference layer can be dropped and re-imported without touching evidence.

**Negative.** Queries spanning both sets are longer to write. Some entities are awkward to place — `Contrast` encodes a local design decision but is reused across datasets, and remains an open question in `ONTOLOGY.md`.

**Accepted cost.** Once `we measured this` and `someone published this` share an edge type, no later query can separate them, and the system cannot be trusted with either. The separation is not recoverable after the fact, so it is made at the outset.

## Alternatives considered

**Single graph with an edge property distinguishing provenance.** Rejected: properties are easy to omit and easy to ignore in a query. A structural constraint cannot be forgotten.

**Reference data held outside the graph entirely, joined at query time.** Rejected: loses the ability to traverse from an observation to pathway context in one query, which is the main analytical value.
