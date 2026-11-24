# ADR-0042 — A withdrawal of a claim HYPOTHESIS states takes a version; one of a claim it does not state does not oblige one

| | |
|---|---|
| Status | Proposed |
| Date | 2026-11-24 |
| Supersedes | — |
| Superseded by | — |

**It supersedes nothing.** It amends the **scope** of ADR-0041(a) and leaves both of ADR-0041's
decisions standing: (a), that only a versioned HYPOTHESIS restatement moves a registered headline,
and (b), that H10's headline stays at the registered denominator. ADR-0041 stays `Accepted` and is
not edited; the `Supersedes` row stays `—` because no decision of it is replaced. An amendment to a
decision's scope, like one to a mechanism, is not a supersession.

ADR-0041 is `Accepted`, so `decisions/README.md`'s append-only rule binds it. The rejection
`decisions/README.md` records for its three routes — an in-place edit, a superseding record, and a
note inside the ADR — binds here too. None of them is needed, because answering an open question
*decides something*, which is what the README says a correcting-only record does not.

## Context

ADR-0041's Open question 1 asks: *"Does (a) cover a withdrawal, not only a moved headline? Reviewer
defect P4 is the case."* It states both branches — *"If (a) extends to claims, a HYPOTHESIS version
takes the withdrawal up. If it does not, the two chains disagree, with no rule saying which
governs."* — and closes *"Not decided here."* The declining branch therefore costs a third rule,
one choosing between two chains that disagree.

P4's facts, as attested by `notes/REVIEWER-DEFECTS.md` row **P4** (at `:61` when this record was
written). That row is the source for all three hashes below; none resolves in the shallow clone this
record was written in, so each is carried with that provenance rather than asserted bare.

- `walk/CHECKS-membership-and-corrections.md`, under the heading `## 2. Withdrawn: "validated on the
  deposit under test, with nothing fitted"`, withdrew the claim at `783138a` (2026-09-22 22:23). It withdrew the
  781-against-798 comparison with it: the comparable figure is 689.
- `HYPOTHESIS.md` v10, at `1019744` sixteen minutes earlier, still states both and cites the
  withdrawal nowhere. One of its statements was re-added at `4c88e9a`, after the withdrawal.

The same register states this decision, in row **R38** (at `:135` when this record was written), as
not obliging a version *"for withdrawals confined to CHECKS documents"*. That is not this record's
wording. It is false of the instance under *Consequences* item 2, where the claim is restated in a
pre-registration, so a rule written over it would leave that case unaddressed while appearing to
cover it. The facts are taken from the register; the wording is not. R38 is left as it stands.

## Decision

**Decided by bzk on 2026-11-24.** ADR-0041(a) extends to a withdrawal, but only to a withdrawal of a
claim `HYPOTHESIS.md` itself states: such a withdrawal is taken up by a versioned HYPOTHESIS
restatement. A withdrawal of a claim `HYPOTHESIS.md` does not state does not oblige a HYPOTHESIS
version.

## Consequences

1. **P4's HYPOTHESIS half is fixed by a HYPOTHESIS version** — v11, prompt 47. This record licenses
   that version and does not make it.
2. **P4 does not close on that version; it narrows.** The withdrawn claim is live and unbannered in
   three places outside `HYPOTHESIS.md`, measured 2026-11-24. Each is cited with its text, because a
   later correction will add banners to these documents and move the lines:

   | site | text it carries | note |
   |---|---|---|
   | `walk/CHECKS-convention-resolved.md:11` | *"The documented rule reproduces the anchor's own published count"* | the claim as a **section heading**. The document's banner, "this supersedes the *level* it was computed at, and nothing else", does not reach it |
   | `walk/CHECKS-convention-resolved.md:24-26` | *"the documented rule lands within 2% of the published count, with nothing fitted. That is a validation on the deposit under test"* | the claim's **origin**. Register row P4 records that it *"carries no banner"* |
   | `walk/PREREG-PXD032267-gate.md:225` | *"The anchor's documented rule came within 2% of its count"* | inside a **pre-registration** document, which carries no withdrawal banner anywhere |

   **This enumeration is a floor: three instances, not an exhaustive measurement.** Two of the three
   documents are neither `HYPOTHESIS.md` nor the CHECKS document the withdrawal sits in, so the
   withdrawal spans documents.
3. What a withdrawal of a claim `HYPOTHESIS.md` does not state fails to oblige is **a HYPOTHESIS
   version**. This record says nothing about what else such a withdrawal may oblige; see *Not decided
   here*.

## Alternatives considered

**The wider reading: every withdrawal, wherever it sits, takes a HYPOTHESIS version.** Available,
and not taken.

**The declining reading: (a) does not extend to a withdrawal.** Available, and not taken.

**Not chosen:** bzk chose the narrow reading on 2026-11-24 and recorded no reason. What each costs is
noted for the record, not as the ground of the choice:
- **The wider reading's cost:** a HYPOTHESIS version for every withdrawal, including one of a claim
  `HYPOTHESIS.md` never made.
- **The declining reading's cost:** the one ADR-0041 names, quoted under *Context*.

## Not decided here

- **ADR-0041's Open question 2** — may `walk/RESULT-*` or `walk/FINDINGS.md` *propose* a move — is
  not answered by this record and stays open.
- **Whether a withdrawal obliges a spanning `walk/CORRECTION-*.md` record where the claim is
  restated in a third document.** This record decides what obliges a *version*, not that. The three
  sites under *Consequences* item 2 are the live case.
