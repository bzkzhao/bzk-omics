# ADR-0014 — Adapter order under pipeline uncertainty: DIA-NN, then MaxQuant, then FragPipe

| | |
|---|---|
| Status | Superseded |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | ADR-0017 |

## Context

v0.1 can afford one search-output adapter, and which one to build first was a bet on a pipeline
nobody had confirmed. The evidence available was the collaborating group's publication record: it
moved to DIA in 2022 (ABPP-HT\*), and its 2025 work uses DIA-NN 2.0 with FASTA-predicted libraries
on an Orbitrap Fusion Lumos. The archival deposits, including PXD018299, are MaxQuant.

**Written 2026-08-09 from `ARCHITECTURE.md` §5's one-line seed, after the decision had already been
reversed.** No record of the original deliberation survives; the reasoning below is recovered from
`ARCHITECTURE.md` §3, which states both the old order and why it changed.

## Decision

Build the **DIA-NN** adapter first, then **MaxQuant**, then **FragPipe** — ordering by where the
group's incoming data would arrive rather than by where its published data came from.

## Consequences

The first adapter would have been the one with no validation fixture. PXD018299 — the only dataset
with a published result to reproduce — is MaxQuant, so a DIA-NN-first order buys currency at the
cost of having nothing to check the ingestion against.

## Why it was superseded

ADR-0017 repositioned the platform **downstream** of existing analysis tools, and that changes which
adapter is shortest to a real user's real results: an analysis-output adapter, not a search-output
one. The collaborator then confirmed Perseus as his workflow. `ARCHITECTURE.md` §3 carries the
current order — **Perseus first, then MaxQuant; DIA-NN deferred to v0.2** — with the priority table.

The reversal is recorded in ADR-0017 and in `ARCHITECTURE.md` §3 and is not restated here.

## Alternatives considered

**MaxQuant first, for the fixture.** Rejected at the time on currency grounds — the reasoning being
that archival data proves the pipeline works on data nobody will send again. It is close to the
order that in fact holds today, arrived at by a different route.

**Build two adapters at once to hedge.** Rejected: v0.1's scope is one ingestion path, and two
half-validated adapters would establish less about the `Observation` contract than one validated
against a published result.
