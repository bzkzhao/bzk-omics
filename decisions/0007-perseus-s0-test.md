# ADR-0007 — Perseus-compatible modified *t*-test with `s0`, implemented locally

| | |
|---|---|
| Status | Superseded |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | ADR-0011 |

## Context

**Two accounts of this record existed before it was written, and they disagree.** ADR-0015's
Context says *"ADR-0007 proposed implementing a Perseus-compatible modified t-test with the `s0`
parameter, to reproduce the cutoffs used in the collaborating group's published work."*
`ARCHITECTURE.md` §5's seed line says *"Local moderated t-test over an R dependency."*
`decisions/README.md`'s Queued table said the same, and declares itself derived from that seed — so
there were two statements, not three, one of them copied.

The disagreement is settled in favour of ADR-0015, on evidence rather than preference:

* **The supersession relation only works one way round.** Both documents agree ADR-0011 supersedes
  this record. Under the seed's reading — *implement the moderated test locally rather than depend
  on R* — ADR-0011, which makes `moderated_t_ebayes` the registry default, **agrees** with it;
  there is nothing to supersede. Under ADR-0015's reading the supersession is real: `s0` was the
  default and 0011 demoted it.
* **ADR-0015 describes 0011 as demoting `permutation_s0` to a legacy option.** A demotion requires
  the entry to have been there first, which only this record can have put there.
* **ADR-0002 places the R rejection elsewhere.** Its Alternatives section rejects R and says the
  question was *"revisited and rejected again in ADR-0011"* — not here.
* Git cannot arbitrate: `ARCHITECTURE.md` and ADR-0015 arrive in the same bulk commit, so neither is
  evidence about the other's provenance.

`ARCHITECTURE.md` §5 is corrected in the same change as this record.

## Decision

Implement a Perseus-compatible modified *t*-test with the fold-change curvature parameter `s0`, in
Python, as the platform's statistical entry point — so that the significance boundary matches the
one the collaborating group's published work was drawn against.

## Consequences

The platform can reproduce the group's cutoffs rather than approximate them. The cost is that a
non-standard test must be implemented and validated rather than called from a library.

## Why it was superseded

ADR-0011 read the group's 2025 preprint — which reports GraphPad Prism for functional assays and
states nothing about proteomic statistics — as evidence that the workflow had moved on, made
`moderated_t_ebayes` the default, and demoted `s0` to a legacy option. ADR-0015 then reversed that
on author correspondence and restored `s0` as default and required. **The reversal is recorded in
ADR-0015 and is not restated here**; this record ends where it was replaced.

## Alternatives considered

**Depend on R and call `limma`.** Rejected in ADR-0002 on install-cost grounds and again in
ADR-0011; the seed line that survived into `ARCHITECTURE.md` §5 appears to be that alternative
mistaken for this decision.

**Plain Welch's *t* with Benjamini–Hochberg.** Rejected as the entry point: `s0` introduces a
fold-change dependence into the threshold, so a reproduction ignoring it will not match the group's
numbers even where it recovers the same proteins.
