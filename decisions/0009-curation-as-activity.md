# ADR-0009 — Sample-to-condition mapping is a curation activity, not configuration

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-09 |
| Supersedes | — |
| Superseded by | — |

## Context

To compute anything from a deposit the platform must know which raw files correspond to which
experimental conditions. Where SDRF-Proteomics accompanies a submission this is machine-readable;
most PRIDE submissions do not include it, so the mapping is inferred from filenames, submission
metadata, or the methods section of the paper.

That inference is an assertion about an experiment this laboratory did not perform, and it is
frequently wrong.

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed.** The substance is already normative
at `ONTOLOGY.md` §5.3 and invariant I8; this record carries the reasoning, not a new decision.

## Decision

The mapping is a **curation activity**, recorded in the graph. No new node type: an `Analysis`
carries `kind = 'curation'` with an author, a closed `basis` enum and a confidence, and gains PROV-O
provenance for free. I8 requires every `Sample` to reach one via `SAMPLE_GENERATED_BY`, and any
result derived from a curation with `confidence = 'inferred'` is labelled as such in every view and
export, naming the basis.

## Consequences

Correcting a mapping is a supersession with an author and a date rather than a file edit, so the
provenance chain from `DifferentialResult` through `Contrast` to `Sample` terminates in a recorded
event instead of in a config file that no longer exists in the form it had.

The cost is that no dataset can be ingested without a curation record, which is real friction and is
the intended friction: a design nobody has stated is a design nobody has checked.

**Configuration was not rejected so much as ruled out.** I5 requires every entity node to reach an
`Analysis` or be flagged `unprovenanced`, and a `Sample` conjured from a configuration file reaches
no activity — so it would be permanently and correctly flagged. Configuration is not an available
option under an invariant the schema already carries.

Structurally this is the same problem as modifier ambiguity (ADR-0006): an inference the primary
measurement does not support, which the field habitually reports as fact. Both get the same
treatment, and that symmetry is worth more than either instance.

## Alternatives considered

**A YAML or JSON mapping file per dataset, read at ingestion.** Rejected: an error in it is
invisible in the graph and its correction is destructive — nothing records that the design was ever
inferred or ever different.

**Require SDRF and refuse deposits without it.** Rejected: it would exclude most of PRIDE, including
PXD018299, which is the project's own validation dataset.

**A separate `Curation` node type.** Rejected as redundant: `Analysis` already carries author, time,
basis and PROV-O edges, and a second type would duplicate the provenance machinery to express one
discriminator that a `kind` field expresses.
