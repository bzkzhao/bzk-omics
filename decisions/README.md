# Architecture decision records

Numbered, immutable records of settled choices. Each captures one decision, its context, and what was rejected.

**An ADR lands as `Proposed`, is reviewed, and becomes `Accepted` only once that round-trip completes.** Correcting a record during review is an ordinary edit to a `Proposed` document — that is what the status is for.

**Once `Accepted`, a record is append-only.** It is never edited; a changed decision gets a new record that supersedes the old, and both remain readable — the same discipline the product applies to `ModifierAssignment` and `EnzymeAssociation`. A decision should die visibly.

The line is drawn by **status rather than by elapsed time**, because a status is checkable and "shortly after writing it" is not. ADR-0020 and ADR-0021 each carry a `Revised in place` row recording amendments made after they were marked `Accepted`, under the earlier reading of this rule. Those rows stay: they are the record of how the convention reached its current form, and reclassifying them retroactively would erase exactly the history this file exists to keep.

This exists because a project with one developer and a compressed timeline will otherwise relitigate settled questions every few months, and because an AI agent given the repository has no other way to know why a choice was made.

## Written

| # | Decision |
|---|---|
| [0001](0001-two-graph-model.md) | Reference and evidence graphs are disjoint |
| [0002](0002-python-backend.md) | Python for the backend |
| [0003](0003-kuzu-over-neo4j.md) | Kùzu for the graph store |
| [0005](0005-modificationsite-and-protein-keys.md) | Sequence version and isoform as part of the `ModificationSite` and `Protein` keys |
| [0015](0015-perseus-s0-default.md) | Perseus `s0` test as the default statistical entry — supersedes 0011 |
| [0016](0016-embargoed-datasets.md) | Embargoed dataset state for unpublished collaborator data |
| [0017](0017-downstream-positioning.md) | Downstream positioning, with both ingestion paths |
| [0019](0019-changeset-structural-validation.md) | Change-sets are self-contained; structural validation precedes invariants |
| [0020](0020-deterministic-evidence-ids.md) | Deterministic, content-derived ids for evidence nodes (not ULIDs) |
| [0021](0021-no-contingent-identifying-fields.md) | An identifying field may be absent only when its absence is determined — no fallback keys |
| [0022](0022-protein-group-ambiguity.md) | Multi-mapping is carried by the observation, at both grains |
| [0023](0023-one-relationship-per-fact.md) | One relationship per fact: `SITE_ON` narrows to `MANY_ONE`; two duplicate names dropped |
| [0024](0024-keying-is-not-assignment.md) | Keying a site is not assigning a protein; `reviewed_preferred` leaves the basis enum |

## Queued

Seeded in [`../ARCHITECTURE.md`](../ARCHITECTURE.md) § Seed ADRs, not yet written up. Listed here so the numbering is reserved.

| # | Decision |
|---|---|
| 0004 | Split storage: graph identity in Kùzu, quantitative matrices in DuckDB |
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
