# Architecture decision records

Numbered, immutable records of settled choices. Each captures one decision, its context, and what was rejected.

**Append-only.** An ADR is never edited after acceptance. A changed decision gets a new record that supersedes the old, and both remain readable — the same discipline the product applies to `ModifierAssignment` and `EnzymeAssociation`. A decision should die visibly.

This exists because a project with one developer and a compressed timeline will otherwise relitigate settled questions every few months, and because an AI agent given the repository has no other way to know why a choice was made.

## Written

| # | Decision |
|---|---|
| [0001](0001-two-graph-model.md) | Reference and evidence graphs are disjoint |
| [0002](0002-python-backend.md) | Python for the backend |
| [0003](0003-kuzu-over-neo4j.md) | Kùzu for the graph store |
| [0015](0015-perseus-s0-default.md) | Perseus `s0` test as the default statistical entry — supersedes 0011 |
| [0016](0016-embargoed-datasets.md) | Embargoed dataset state for unpublished collaborator data |
| [0017](0017-downstream-positioning.md) | Downstream positioning, with both ingestion paths |
| [0019](0019-changeset-structural-validation.md) | Change-sets are self-contained; structural validation precedes invariants |
| [0020](0020-deterministic-evidence-ids.md) | Deterministic, content-derived ids for evidence nodes (not ULIDs) |

## Queued

Seeded in [`../ARCHITECTURE.md`](../ARCHITECTURE.md) § Seed ADRs, not yet written up. Listed here so the numbering is reserved.

| # | Decision |
|---|---|
| 0004 | Split storage: graph identity in Kùzu, quantitative matrices in DuckDB |
| 0005 | Sequence version and isoform as part of the `ModificationSite` primary key |
| 0006 | Modifier identity as a defeasible assignment, not a site property |
| 0007 | Local moderated *t*-test over an R dependency — superseded by 0011 |
| 0008 | Append-only assertions with explicit retraction |
| 0009 | Sample-to-condition mapping as a curation activity, not configuration |
| 0010 | `Observation` and `EvidencedInference` as contracts, not tables |
| 0011 | Statistical tests pluggable; supersedes 0007 — **superseded by 0015** |
| 0012 | Graph is derived, not authoritative; rebuild over migration |
| 0013 | Quantitative matrices retained permanently, never only derived statistics |
| 0014 | Adapter order under pipeline uncertainty: DIA-NN, MaxQuant, FragPipe |

Numbers 0015 and 0016 were written ahead of 0004–0014 because they arose from author correspondence rather than from design. Writing them out of sequence is correct — the numbering reserves identity, not chronology.

## Format

Keep them short — context, decision, consequences, alternatives rejected. The value is in recording what was considered and discarded, not in length.

```markdown
# ADR-NNNN — Title

| | |
|---|---|
| Status | Proposed / Accepted / Superseded |
| Date | YYYY-MM-DD |
| Supersedes | — |
| Superseded by | — |

## Context
## Decision
## Consequences
## Alternatives considered
```
