# ADR-0033 — The frame is a coverage repair, and C0 is the instrument that screens it

| | |
|---|---|
| Status | Accepted |
| Date | 2026-09-18 |
| Supersedes | — |
| Superseded by | — |

Landed `Proposed` at `d09bdae` and reviewed at `d46a3ab`; `Accepted` on
2026-09-18 once that round-trip completed, per `decisions/README.md`. The Review
is below, and the rename it forced — *query-set repair* to *coverage repair* — is
carried through the title, R1, the filename and every self-reference.

Cites ADR-0031 (selection outside the survey's route) as the record it extends
and does not supersede.

**Every quotation from `ROADMAP.md`, `ONTOLOGY.md` and `decisions/` in this record
was re-derived at `fda3cb9` (2026-09-18 00:05:25 +0100, *"notes: add two ADR
drafts for verification"*).** The draft was written against `019c711`; nothing in
`ROADMAP.md`, `ONTOLOGY.md` or `decisions/` moved between the two, so every
quotation held, and the pin is updated to the commit they were checked at.
Quotations are cited by content rather than by line, because line numbers in
`ROADMAP.md` move.

**Two statements in this record are reviewer-supplied and were not re-derived
here**, and are marked again at their sites: `PXD026748`'s submitter and lab head,
read from the PRIDE project page; and the C0 expectation table below, which is a
prediction and not a screening.

---

## Review

Landed `Proposed` at `d09bdae` and reviewed at `d46a3ab`. **Five findings: four
narrow a ground and one records an outstanding item; none reverses a decision.
The record's name changes and its operative rulings keep their content.** R1's
content stands and its *name* is struck and replaced; R2's ground is doubled, one
per mechanism, and its missing operative ground is supplied here; R3 stands
entirely; R4 stands; R5's referral stands and the confidence of its closing
sentence is struck.

**A reading is supplied to this record by the reviewer and is written in as
decided, not as read.** It is marked as such at its site, and its origin is named
there — Finding C.

**What the review does not touch, stated so the silence is not read as doubt.**
R3 stands entirely: C0 governs admissibility, the walk governs comparability, and
neither substitutes for the other. R4 stands: this record selects no deposit.
**The Context's correction is the best work in the record** — that the draft's
*"the query set could not reach it"* stops one clause short of the anchor-domain
terms, and that reach and coverage are both consistent with what the repository
holds. Findings A, B and D are all consequences of that correction being right
and not yet carried through the rest of the document.

### A — R1's name asserts a mechanism the record says it cannot establish. Renamed

**The record flags this itself and leaves the call to review; this is that call.**
Its own R1 note read *"whether the instrument is better named a **coverage**
repair is a reviewer's call, and this record is `Proposed` precisely so that call
can be made against it."*

**Ruling (b) — the name is struck and replaced; R1's content is untouched.**
*Coverage* is true under **both** mechanisms and *reach* under only one: if the
query set missed the deposit the survey's coverage was incomplete, and if the cap
stopped at 60 of 450 it was incomplete. Coverage is the superset, so the name
claims exactly what Context establishes and no more.

**What survives, and what does not.** R1's decision — the frame licenses nothing,
admits nobody, amends no criterion — **survives untouched**, as the record
correctly says it does under either mechanism. The word *query-set* in the title,
in R1, in the filename and in every self-reference **does not**, and is carried
through to *coverage* in this commit.

### B — R2's stated ground fits one mechanism and understates the other. Both given

**Ruling (b) — R2's reach is widened by one ground, not struck.** As written, R2
rests on *"the existing instrument applied to candidates it was never offered"*,
which is exactly right under **reach** and understates the position under
**coverage**.

**Under coverage the ground is much stronger and the record does not say so.**
The pool is 450 and full classification covered **60**, so **390 pool members sit
inside the pool, unscreened**. Offering eleven of them to C0 is then not a new
route at all: it is the continuation of a classification the cap interrupted, and
it needs no appeal to ADR-0031's gap — the gap is about routes C0 never spoke to,
and C0 has not yet spoken to 390 of its own pool.

**What survives, and what does not.** R2's decision survives on both grounds, and
both are now written into it. What does not survive is the implication that the
coverage case needs ADR-0031's gap: it does not.

### C — R2's operative ground was missing. A reading is supplied and decided here

**The objection the record does not answer.** If coverage holds, 390 are
unscreened and this record screens **eleven**, chosen by `FRAME v1` — a
thesis-side instrument. ADR-0031's warning that *"a rule that admits exactly one
deposit is a selection wearing a rule's clothes"* is answered by this record in
its eleven-versus-one form; the form that bites is **eleven versus three hundred
and ninety**. The record's own R3 forecloses the easy answer, since it insists the
two instruments have different objects — so the frame's own output cannot be the
ground.

**The reading — ORIGIN: THE REVIEWER. Written in as decided and marked as such.**
The eleven are not an arbitrary eleven of the remainder: they are **pre-filtered
for the property that decides the gate**.

- C0 *"is decided entirely by (c) and (d)"* (ADR-0031), every one of the sixty
  being CC0 with a resolvable organism so that (a), (b) and (e) never bind.
- **45 of the 60 failed at exactly those two gates** — the distinct `C0 gates met`
  values are `abcde` ×10, `abce` ×2, `abde` ×3, **`abe` ×45**.
- Frame B's membership criterion — site-directed enrichment — and C0(c) — a
  site-grain processed table — test **nearly the same property**. Not
  identically: enrichment is a wet-lab fact and a processed table is a deposited
  artefact, and a deposit can have the first without the second. But the first is
  close to necessary for the second.

So the eleven are enriched for C0 passes **by construction rather than by luck**,
and continuing the classification there is **prioritisation, not selection**. The
remainder is not foreclosed; it is unscreened, exactly as it was before this
record.

**The falsifier, registered as a prediction before any screening runs.** The
baseline over the classified sixty is **15 of 60 = 25%** passing (c) or (d)
(`abcde` + `abce` + `abde`). **If the eleven pass C0 at no better than that, the
enrichment claim is empty and R2 needs a different ground.** The reviewer's
registered expectation is a pass rate **materially above 25%**, driven by (c),
with the binding constraint **moving** from (c) to (d) and (f) — the three mouse
members failing at (f), the non-MaxQuant members at (d). **If the constraint does
not move, the reading is wrong.**

**One arithmetic caveat on the baseline, so the screening turn compares like with
like.** 15 of 60 is the rate of passing *(c) or (d)*, which is the quantity the
enrichment claim is about. It is **not** the rate of passing C0 outright: that is
`abcde` alone, **10 of 60 = 16.7%**, and no row of the sixty was evaluated against
(f) at all. A screening that reports whole-C0 verdicts for the eleven must say
which of the two baselines it is beating.

**What survives, and what does not.** R2's decision survives, now on a stated
operative ground. What does not survive is **any reading of R2 under which the
frame's output is a sufficient ground on its own** — the ground is the
pre-filtering, which is a claim about C0's own failure distribution and not about
the thesis.

### D — R5's closing sentence is more confident than the Context supports

**Ruling (b) — the confidence is struck; the referral stands.** *"Screening a
candidate is not drawing one"* holds under **reach**. Under **coverage** the sixty
exist *because* of the cap, so screening eleven further pool members is moving the
cap for eleven specific deposits — **a C3 amendment in effect, made per-deposit
and without a record**, which is the shape (ii) rejects.

**What survives, and what does not.** R5's referral of the draw question to its
own record **survives**: whether the eleven join the draw, form a supplementary
draw, or sit outside the survey is a C3 question this record does not answer. The
closing sentence's generality **does not**, and is qualified in place.

### E — C0(b) is unchecked for both candidates. Stands, recorded as outstanding

**Ruling (c) — the record is not wrong.** C0(b) reads `unchecked` for both
candidates in the expectation table, so nothing is asserted about it.

**But one worked consequence rests on a gate nobody has looked at.** The record
says `PXD026748` *"would be the first deposit evaluated against all six gates"*,
and that claim needs (b) — reuse terms establishable from the deposit's own
metadata — to have been read. **One project-record lookup closes it.** Recorded
here as an outstanding item against the screening turn, not as a defect in this
record.

---

## Context

Two candidates for the second deposit arrived this week by a route ADR-0031 does
not name.

**Neither was screened by C0.** `PXD026748` appears nowhere in the repository
outside this record — zero hits across `*.md`, `*.json` and `*.py`, measured at
`fda3cb9` — and no row of the sixty-row table names it. `PXD065158` is row 10 of
that table and carries an `abe` cell, so it *was* screened.

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

**C0 never screened `PXD026748`, and the repository does not establish why — the
draft's reason is corrected here against the current tree.** It said the draw's
query set could not reach the deposit, because the pool was built from *"what a
diGly deposit is actually *titled* — the remnant by its chemistry"* and this
deposit's title carries no chemistry term. **That quotation stops one clause
early.** The same sentence continues through the sub-proteome, the enrichment,
the measurement *"and the anchor domain (`ISG15`, `ISGylome`)"* — thirteen terms,
not three — and `PXD026748` is titled *Proteome-wide identification of ISG15 sites
targeted by SARS-CoV-2 PLpro*.

**Two mechanisms are consistent with what the repository records, and it does not
distinguish them.**

- **Reach.** The pool is *"450 of 450 distinct accessions the thirteen terms reach
  on page 0"*, at `size` 100 and no pagination, and the three truncated terms are
  `diGly`, `GlyGly` and `ubiquitin remnant`. **`ISG15` is not among them**: it
  returns 45 records and all 45 are on page 0. So a deposit whose title names
  ISG15 is within the reach of the query set as it now stands, and the earlier
  round's *"what limited that draw was its **query set**, not its gate"* is about
  the four-term draw whose terms *"never named the remnant chemistry"* — not this
  one.
- **Coverage.** Full classification covers *"60 of 450 = 13.3%"*. A pool member
  outside the sixty was never screened because the cap stopped short of it, not
  because C0 refused it.

**Which of the two applies to `PXD026748` cannot be settled from this
repository**, because the 450-accession pool is nowhere enumerated in it — only
the sixty classified rows are — and re-running the draw is a PRIDE query, not a
read. It is recorded here as open rather than asserted in either direction.

`PXD065158` is in the pool by the query set's own construction rather than by
luck: its title, *Proteome-wide identification of ISG15 sites in HeLa cells*,
names the same anchor-domain term.

**That makes the frame a repair to the survey's coverage, not an admissibility
criterion** (renamed from *query-set repair* by Review finding A; the Review
records why coverage is the claim both mechanisms support). It does not gate, rank, score or admit. It enlarges the set of
deposits C0 can be applied to.

---

## Decision

**R1 — `FRAME v1` is recorded as a coverage repair and licenses nothing on its
own.** It admits no deposit, excludes none, and amends no criterion. Its output
is a list of candidates the survey's own classification did not reach.

**Renamed by Review finding A, 2026-09-18** — ~~query-set repair~~ **coverage
repair**. Context below records that the repository cannot say whether
`PXD026748` was missed by the query set's *reach* or by the classification *cap*,
and *query-set repair* asserted the first. **Coverage is true under both**: if the
query set missed the deposit the survey's coverage was incomplete, and if the cap
stopped at 60 of 450 it was incomplete. Coverage is the superset, so the name now
claims only what is established. What R1 decides is unchanged and was never at
issue — the frame licenses nothing, admits nobody and amends no criterion, under
either mechanism.

**R2 — The eleven Frame B members are offered to C0 unamended, and C0's verdicts
are recorded per deposit.** This is the existing instrument applied to candidates
it was never offered, which is neither a criteria change nor a selection outside
the criteria. (ii)'s objection — *"the restriction would live in prose that the
next ranking does not read"* — does not attach, because nothing is being put in
prose: the next screening reads C0, and C0 is what runs.

**Two grounds, one per mechanism — Review finding B, 2026-09-18.** The sentence
above states the ground that fits *reach* and understates the one that fits
*coverage*.

- **Under reach**, it is right as written: the eleven are candidates the draw's
  query set could not see, so offering them to C0 is the existing instrument
  applied to candidates it was never offered.
- **Under coverage**, it is stronger than stated. The pool is 450 and full
  classification covered 60, so **390 pool members are inside the pool and
  unscreened**. Offering eleven of them to C0 is not a new route at all — it is
  the continuation of a classification the cap interrupted, and it needs no
  appeal to ADR-0031's gap. Which of the eleven are among the 390 and which were
  unreachable is not established here (Context), and the ground holds either way.

Why those eleven rather than eleven others is Finding C's question, answered
below.

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

**That closing sentence is softened by Review finding D, 2026-09-18, to what the
Context supports.** *Screening a candidate is not drawing one* holds under
**reach**. Under **coverage** the sixty exist *because* of the cap, so screening
eleven further pool members moves the cap for eleven specific deposits — a C3
amendment in effect, made per-deposit and without a record, which is the shape
(ii) rejects. So the sentence is not a general licence: **R2 stands without R5
under reach, and under coverage the C3 question in R5 is the one that decides
whether these eleven may be screened ahead of the other 379.** What survives
untouched is R5's referral — whether the eleven join the draw, form a
supplementary draw, or sit outside the survey is a C3 question with its own
record, and this record still does not answer it.

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

### Registered expectation — the eleven's pass rate, and what falsifies Finding C

**Added by Review finding C, 2026-09-18, before any screening runs. A prediction,
not a result, and the screening turn is to be held to it.**

| | |
|---|---|
| **Baseline** | **15 of 60 = 25%** of the classified sixty pass (c) or (d) — `abcde` ×10 + `abce` ×2 + `abde` ×3, against `abe` ×45 |
| **Prediction** | The eleven pass **materially above 25%**, driven by (c) |
| **Mechanism predicted** | The binding constraint **moves** off (c) — to (d) for the non-MaxQuant members, and to (f) for the three mouse members |
| **Falsified if** | The eleven pass at no better than 25%, or the constraint stays on (c) |
| **If falsified** | The pre-filtering reading in Finding C is empty, and R2 needs a different operative ground |

**Which baseline a verdict must be compared against.** 25% is the rate of passing
*(c) or (d)*, the property the enrichment claim is about. The rate of passing C0
outright is `abcde` alone — **10 of 60 = 16.7%** — and **no row of the sixty was
evaluated against (f)**, so a whole-C0 verdict over the eleven is not comparable
to either figure without saying which it beats.

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

**Whether R2 generalises to a route that is not a coverage repair.** It does not
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
- **A selection offered on a ground that is not a coverage repair** is outside
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
