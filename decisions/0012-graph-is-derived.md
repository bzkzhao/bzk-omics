# ADR-0012 — The graph is derived, not authoritative; rebuild over migration

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-09 |
| Supersedes | — |
| Superseded by | — |

## Context

A schema on a pre-1.0 store, in a domain whose modelling questions are still open, will change
often. The usual answer is a migration framework: each schema change ships a script that transforms
the data in place, and the store is the authority.

That answer is expensive here for a reason specific to this project — most of what the graph holds
is derived from files that are still on disk.

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed.** The decision is already normative
as invariant I9 at `ONTOLOGY.md` §8, which now carries two amendments this record does not restate;
where the two differ, `CLAUDE.md` § Conventions makes `ONTOLOGY.md` right.

## Decision

The graph is a **derived artefact and never authoritative**. Given four inputs — `raw/`
(content-addressed), the curation export, the UniProt cache, and the DDL — it must be regenerable
from scratch. Curation records and manual inferences are the only non-derivable content, and they
serialise to plain JSON alongside the graph and are versioned independently.

Schema change is therefore a **compute cost**, not a migration: change the DDL, drop the stores,
replay.

## Consequences

Nothing may exist only inside `graph.kuzu/`. That is a live constraint rather than a slogan — it is
why manual assertions need a nightly export (`OPERATIONS.md` §2), and why a retraction needs its own
record, since `retracted_at` is outside identity and no input supplies it.

It is also the mitigation for choosing a young store: a broken Kùzu means re-ingesting, not losing
data — but only while the rebuild path is exercised often enough to be trusted, which is why
`OPERATIONS.md` §5 makes it weekly.

The cost is the rebuild itself, and it is not small: **83.9–149.7 s** with the cache on disk and
**37 m 14 s – 39 m 34 s** from nothing, essentially all of the latter network. A claim that schema
change is cheap is true at the first figure and not at the second.

**I9 was executed from the state it describes for the first time on 2026-08-09**, twice. What those
runs established, and what they did not, is recorded in `ONTOLOGY.md` §8 I9 and in `ROADMAP.md`
§ *Measured findings*; the part that belongs here is only that the claim stopped being an assumption
that day, having been made on week one.

## Alternatives considered

**Migration scripts per schema change.** Rejected: every script is code that must be written,
tested and kept correct against a schema that is still moving, and a failed migration on an
authoritative store loses data that a failed rebuild does not.

**Treat the graph as authoritative and back it up.** Rejected: it makes the store the only copy of
things that were derived, so a modelling change becomes irreversible and the backup inherits every
error rather than dropping it at the next replay.

**Dual-write to the graph and to a durable event log.** Rejected as the same cost twice: `raw/` plus
the curation export already **is** the log, and a second one would need its own consistency
guarantee against the first.
