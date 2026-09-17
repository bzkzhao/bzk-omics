# ADR-0034 — The frame is a query-set repair, and C0 is the instrument that screens it

| | |
|---|---|
| Status | **Proposed** |
| Date | 2026-09-18 |
| Supersedes | — |
| Superseded by | — |

Lands `Proposed` per `decisions/README.md`. It becomes `Accepted` only once the
round-trip completes.

Cites ADR-0031 (selection outside the survey's route) as the record it extends
and does not supersede.

**Every quotation from `ROADMAP.md`, `ONTOLOGY.md` and `decisions/` in this record
was read at `019c711` (2026-09-17 21:17:46 +0100, *"Refresh the README's status
table and changelog"*), from a clone taken that evening.** Quotations are cited by
content rather than by line, because line numbers in `ROADMAP.md` move.

**Two statements in this record are reviewer-supplied and were not re-derived
here**, and are marked again at their sites: `PXD026748`'s submitter and lab head,
read from the PRIDE project page; and the C0 expectation table below, which is a
prediction and not a screening.

---

## Context

Two candidates for the second deposit arrived this week by a route ADR-0031 does
not name.

**Neither was screened by C0.** `PXD026748` appears nowhere in the repository —
zero hits across `*.md`, `*.json` and `*.py`. `PXD065158` is row 10 of the
sixty-row table and carries an `abe` cell, so it *was* screened.

**Neither is an anchor-laboratory deposit.** `PXD026748`'s PRIDE record names
**Denzel Eggermont as submitter and Francis Impens as lab head**, both VIB-UGent;
Pinto-Fernández is an author and neither — and ADR-0031's own applied test for
`PXD055843` was the Contact List carrying the name under **both** `lab head` and
`dataset submitter`. `PXD065158` is the same submitter and the same laboratory.
*(Reviewer-supplied from the PRIDE record; not re-derivable in this container.)*

So ADR-0031's two routes are closed: R2 governs deposits C0 screened and failed,
and R3 governs anchor-laboratory deposits. That record names the gap itself:
*"says nothing about a selection offered on some other ground that C0 also never
spoke to. Whether R2 generalises to those is not decided."*

### What the frame established, and it is not a new criterion

`FRAME-SPEC v1` and `FRAME v1` were built to give the thesis's §5 countable a
denominator. They produced a finding about the survey instead.

**C0 never screened `PXD026748` because the draw's query set could not reach it,
not because a gate excluded it.** The 450-deposit pool was built from *"what a
diGly deposit is actually **titled** — the remnant by its chemistry"*.
`PXD026748` is titled *Proteome-wide identification of ISG15 sites targeted by
SARS-CoV-2 PLpro* and carries no chemistry term anywhere in its title.
`ROADMAP.md` says the same thing of an earlier round in its own words: *"what
limited that draw was its **query set**, not its gate."*

`PXD065158` is in the pool by luck rather than construction — it too is titled by
its biology, and it was reachable only because the pool was wider than the title
route alone.

**That makes the frame a repair to the query set, not an admissibility
criterion.** It does not gate, rank, score or admit. It enlarges the set of
deposits C0 can be applied to.

---

## Decision

**R1 — `FRAME v1` is recorded as a query-set repair and licenses nothing on its
own.** It admits no deposit, excludes none, and amends no criterion. Its output
is a list of candidates that the survey's own route could not reach.

**R2 — The eleven Frame B members are offered to C0 unamended, and C0's verdicts
are recorded per deposit.** This is the existing instrument applied to candidates
it was never offered, which is neither a criteria change nor a selection outside
the criteria. (ii)'s objection — *"the restriction would live in prose that the
next ranking does not read"* — does not attach, because nothing is being put in
prose: the next screening reads C0, and C0 is what runs.

**R3 — `WALK-STANDARD`'s R1 to R5 is a thesis-side assessment and is not an
admissibility criterion.** The two instruments have different objects. C0 asks
whether a deposit can be ingested by this platform in this release. The walk asks
whether a deposit's published claim set can carry a claim-grain comparison.
**Where they disagree, C0 governs admissibility and the walk governs
comparability, and neither substitutes for the other.** A deposit can be
admissible and not comparable, or comparable and not admissible, and both states
are informative.

**R4 — This record selects no deposit.** It decides a route, as ADR-0031 decided
a rule.

**R5 — C3 is touched and this record does not amend it.** Offering eleven
candidates to C0 enlarges the pool C3's cap and draw range over. C3 already
*"holds five"* after the 2026-08-18 organism amendment and is recorded as
under-drawn. Whether these eleven join the draw, form a supplementary draw, or
sit outside the survey as individually screened candidates is **a C3 question
with its own record**. R2 stands without it: screening a candidate is not
drawing one.

---

## What applying C0 is expected to produce

**Stated as expectation before the screening runs**, per the project's
pre-registration convention. These are predictions, not verdicts.

| deposit | a | b | c | d | e | f | expected |
|---|---|---|---|---|---|---|---|
| `PXD026748` | public | unchecked | `GlyGly (K)Sites.txt` present | MaxQuant 1.6.17.0 | human | human | **likely passes all six** |
| `PXD065158` | public | unchecked | site table present | **FragPipe** | human | human | **fails (d)** |

**Two things follow if those hold, and both are dispositions rather than
selections.**

`PXD026748` would be **the first deposit evaluated against all six gates**,
including the f added 2026-08-18 that no row of the sixty ever met or failed.
That is worth recording in its own right.

`PXD065158` is **not excluded by a judgement — it is deferred by a scope decision
already taken.** C0(d)'s own text excludes a non-MaxQuant deposit *"for this
survey only"*, and FragPipe sits in § *Explicitly deferred* at v0.2. So the
FragPipe adapter question is not a selection question and never was: it is the
v0.2 adapter row, reached early.

**That is the strongest available evidence that R2 is a route and not a
selection.** ADR-0031 warns that *"a rule that admits exactly one deposit is a
selection wearing a rule's clothes."* This route offers eleven, and its first
consequence is to send the candidate that looked strongest yesterday morning away
from selection entirely.

---

## Relationship to ADR-0031's implied ordering

ADR-0031's R4 names three implied changes — amending C0 to per-artefact
evaluation, widening the `C0 gates met` notation to six letters, applying gate f
retroactively — and fixes that **none comes before the first**.

**This record makes none of them.** C0 is applied unamended, to deposits it has
not previously ranged over, and the notation question does not arise because
these verdicts are new rather than re-scored. **No ordering conflict.**

What this record does do is make R4's amendment *more* worth making, not less:
`PXD026748` carries both a site-grain and a protein-grain artefact in one
deposit, which is precisely the case per-artefact evaluation would handle
naturally.

---

## What this record does not settle

**Whether `PXD026748` should be selected.** That is C1 scoring and C2 ranking,
and neither runs here.

**Whether `PXD026748` can be represented.** It fails `WALK-STANDARD` R5: its
PLpro axis is applied to lysate, after the biological sample ends, and the
pairing is unrecordable. That needs its own ADR and is upstream of any curation
record.

**Whether the frame's eleven join the draw.** R5 above; a C3 question.

**Whether R2 generalises to a route that is not a query-set repair.** It does not
decide that, and stating so is cheaper than discovering it later — which is the
sentence ADR-0031 closed with, and it applies to this record for the same reason.

---

## What the route excludes

Named rather than left to be inferred, following ADR-0031's own discipline.

- **`PXD065158` is routed away from selection** by C0(d) and the v0.2 deferral,
  not by this record.
- **The fifty-three term-confirmed deposits outside Frame B** are not offered:
  Frame B is the site-directed subset, and a deposit with no site-grain
  enrichment fails C0(c) on the artefact C0 ranges over.
- **Any deposit C0 already screened and failed** remains governed by ADR-0031 R2.
  `PXD065158` carries an `abe` cell, so its exclusion needs no new ground.
- **A selection offered on a ground that is not a query-set repair** is outside
  this record.

---

## Alternatives considered

**Select `PXD026748` by hand on a stated ground.** This is ADR-0031's already
rejected (ii), and the objection bites unchanged: the restriction would live in
prose the next screening does not read.

**Treat `FRAME` plus `WALK-STANDARD` as the per-artefact instrument R4 named.**
Tempting and wrong. The walk assesses comparability for the thesis, not
admissibility for the platform; conflating them would make every future walk
verdict double as an admissibility claim it was not written to bear, and would
make R4's amendment look discharged when it is not.

**Defer until R4's amendment is made.** Rejected: nothing about these deposits
changes while the decision waits, and the amendment has an unpaid retroactive
cost already recorded. Screening new candidates against C0 as it stands incurs
none of it.
