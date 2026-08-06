# ADR-0017 — Downstream positioning, with both ingestion paths

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | — |

## Context

Author correspondence confirmed that the collaborating group's workflow is Perseus, described as the field standard for over a decade and freely available.

This exposed an implicit assumption in the design: that bzk Omics performs the analysis. It does not, and should not. Perseus does that job well, the group trusts it, and a month of work will not produce a better modified *t*-test.

Three positions were considered.

**A — downstream only.** Ingest analysis outputs; never compute a statistic.
**B — both paths.** Ingest analysis outputs *and* search-engine output with the underlying matrix retained.
**C — full pipeline.** Perform the analysis; Perseus becomes optional.

## Decision

**B, positioned as A.**

The stated position is downstream: bzk Omics sits after the tools a researcher already uses, and their outputs are its inputs. Both ingestion paths are built. `Analysis.kind = 'external'` and `parameters_observed = false` distinguish results computed elsewhere from results the platform produced.

## Consequences

**Positive.** No tool has to be displaced, so no user is asked to abandon something they trust — which removes the largest adoption objection at a stroke. The Perseus adapter is the smallest possible first deliverable and the shortest path to holding a real user's real results. Retaining the quantitative matrix where available preserves recomputation, which is what keeps the platform from being a filing cabinet, and enables a capability no existing tool offers: showing where a recomputed result diverges from an externally computed one, as a finding about analytical sensitivity rather than a defect.

**Negative.** Two ingestion paths is more surface than one. Where only an analysis output is ingested, provenance begins where that output begins — a threshold changed upstream produces a result the platform cannot explain. This limitation is recorded in `VISION.md` rather than discovered later.

**Reframed rather than lost.** The statistics registry demotes from *the point* to *needed for recomputation and comparison*. `perseus_s0` remains default and required, because matching the collaborator's numbers is a precondition for being trusted with the comparison at all.

## Alternatives considered

**A, downstream only.** Rejected: without the raw matrix, invariant I11 loses its meaning, no alternative test can ever be run, and the resulting product is easy enough to build that it is easy for anyone else to build.

**C, full pipeline.** Rejected: competing with a mature tool on its own ground, with a month of work against a decade of theirs, asking a PI to abandon what he has just called the gold standard. Being 95% right about `s0` and permutation FDR is worse than useless.

## Open

At which point in his pipeline the collaborator would rather hand something over — search-engine output or Perseus results — is unresolved. If the answer is decisively the latter, A may prove sufficient and B over-engineered. To ask at the meeting; recorded in `ROADMAP.md` § Open questions.
