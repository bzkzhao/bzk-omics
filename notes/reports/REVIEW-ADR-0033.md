# REVIEW — ADR-0033, the frame as a query-set repair

**Reviewed 2026-09-18 at `d46a3ab`**, against the landed text rather than the
draft. Four findings. **Two rulings (b) — narrow — one (c) — stands — and one
new objection the record does not answer.** No decision is reversed.

Form follows ADR-0031's own review: each finding names its ruling, quotes the
sentence it turns on, and says what survives and what does not.

---

## A — R1's name asserts a mechanism the record says it cannot establish. Narrowed

**The record already sees the problem and stops one step short of acting on it.**
It writes: *"R1's name is left standing and is flagged for review … whether the
instrument is better named a **coverage** repair is a reviewer's call."* This is
that call.

**Ruling (b) — the name is narrowed to *coverage repair*, and the title moves with
it.**

The ground is not that *coverage* is more likely than *reach*. It is that
**coverage is true under both mechanisms and reach is true under only one.** If
the query set failed to reach the deposit, the survey's coverage of its own
domain was incomplete. If the classification cap stopped at 60 of 450, the
survey's coverage was incomplete. **Coverage is the superset**, so a record that
cannot distinguish the two should take the name that holds either way.

**What survives untouched**: R1's content — that the frame licenses nothing,
admits nobody, excludes nobody and amends no criterion. The record is right that
this holds under either mechanism.

**What does not**: the phrase *query-set repair* in the title, in R1, and in every
self-reference. A record's name is not a label on its content; it is the
characterisation a future reader indexes it by, and this one names a finding the
record explicitly declines to make.

---

## B — R2's ground is weaker than the record thinks under one mechanism and
## stronger under the other, and the record gives neither. Narrowed

**Ruling (b).** R2's stated ground is that offering candidates to C0 is *"the
existing instrument applied to candidates it was never offered."*

**Under the coverage mechanism that ground is much stronger than stated, and the
record does not say so.** Full classification covers *"60 of 450 = 13.3%"*, so
**390 pool members are inside the pool and unscreened**. Those deposits are not
outside the survey's route at all — they are on it, and the cap interrupted the
walk down it. Offering eleven of them to C0 is not a new route; it is continuing a
classification that stopped early. That ground needs no appeal to ADR-0031's gap
and is not exposed to (ii)'s objection at any point.

**Under the reach mechanism the stated ground is right as written**, since a
deposit the query set never returned was never a pool member.

**What survives**: R2's conclusion, under either mechanism.
**What does not**: the claim that one ground covers both. The record should give
the stronger ground for the coverage case and keep the present one for the reach
case, rather than a single ground that fits one and understates the other.

---

## C — Selective continuation. The objection is real and is ruled on here

**This is the finding the record most needs and does not contain, and a review
that only raised it would not complete the round-trip.** Finding C objects to
**R2**, which is this record's operative ruling. ADR-0031's own review faced the
same situation at its finding A — a gap in the operative ruling — and did not
defer it: *"A reading is supplied to this record by the reviewer and is written in
as decided, not as read."* That is the precedent, and it is followed here.

### The objection

If the coverage mechanism holds, **390 pool members are inside the pool and
unscreened, and this record proposes screening eleven of them.** The eleven were
selected by `FRAME v1`, an instrument built for the thesis's §5 countable. So
ADR-0031's warning returns by a different door. That record's *"a rule that admits
exactly one deposit is a selection wearing a rule's clothes"* is answered by this
record in its eleven-versus-one form. **The form that bites is eleven versus three
hundred and ninety.** And the easy answer — *because the frame produced them* — is
foreclosed by this record's own R3, which insists the two instruments have
different objects.

### The reading, decided here and not read from the source

**Origin: the reviewer. Written in as decided.** The eleven are not an arbitrary
eleven of the remainder. **They are pre-filtered for the property that decides
the gate.**

Measured, not assumed. ADR-0031 records that C0 *"is decided entirely by (c) and
(d)"*, and its own instrument returns the distribution over the sixty: `abcde` ×10,
`abce` ×2, `abde` ×3, **`abe` ×45**. So **45 of 60 failed at (c) or (d)** — a
site-grain processed table, and MaxQuant. C0(c) is the dominant cause of exclusion
in the classification as actually run.

**Frame B's membership criterion and C0(c) test nearly the same property.** Frame
B is defined as site-directed enrichment — GlyGly or di-Gly peptidomics,
diglycine-remnant enrichment, anti-K-ε-GG immunoaffinity, PTMScan IAP. C0(c) asks
whether the deposit carries a site-grain processed table. These are not identical:
enrichment is a wet-lab fact and a processed table is a deposited artefact, and a
deposit can have the first without the second. **But the first is close to
necessary for the second**, which is why the frame's eleven are enriched for C0
passes by construction rather than by luck.

**So continuing the classification here is prioritisation, not selection.** A
budget that must stop somewhere spends where the yield is highest, and the
remainder is not foreclosed — it is unscreened, exactly as it was before this
record.

### What would falsify it, and it is cheap to check

**The claim is empirical and carries a number.** The baseline pass rate over the
classified sixty is **15 of 60 = 25%** — the cells carrying a `c` or a `d`. If the
eleven pass C0 at a rate no better than that, **the enrichment claim is empty** and
R2 needs a different ground, because screening them would then be indistinguishable
from screening eleven arbitrary pool members.

**Register that prediction before the screening runs.** The reviewer's expectation
is a pass rate materially above 25%, driven by (c); the mouse members are expected
to fail at (f) and the non-MaxQuant members at (d), so the binding constraint
should move from (c) to (d) and (f). **If it does not move, the reading above is
wrong.**

### What this does to R2

**Ruling (b) — R2's reach is narrowed, and its ground is now stated.** R2 stands:
the eleven are offered to C0 unamended. What is added is *why these eleven*, which
the record did not say — and the answer commits it to a measurable claim it can be
held to.

**What does not survive**: any reading of R2 under which the frame's output is a
sufficient ground on its own. It is not. The ground is the pre-filtering, and the
pre-filtering is a claim about C0's own failure distribution rather than about the
thesis.

---

## D — R5's distinction may not survive the coverage mechanism. Narrowed

**Ruling (b).** R5 holds that *"screening a candidate is not drawing one."* True
in general, and true under the reach mechanism.

**Under the coverage mechanism it is doing more work than it can bear.** C3 is
survey size, and the 60 exist *because* of the cap. Screening eleven further pool
members is moving the cap for eleven specific deposits — which is a C3 amendment
in effect, made per-deposit and without a record, which is precisely the shape
ADR-0031's (ii) rejects.

**What survives**: R5's referral of the draw question to its own record.
**What does not**: the confidence of the closing sentence. It should read that the
distinction holds under the reach mechanism and is contested under coverage, which
is the same honesty the Context already shows.

---

## E — Gate (b) is still unchecked, and it is load-bearing for the worked
## consequence. Stands as a defect

**Ruling (c) on the substance, recorded as an outstanding item.** The expectation
table marks C0(b) — reuse terms establishable from the deposit's own metadata —
`unchecked` for both candidates, and predicts a pass on the strength of CC0 being
universal across the sixty. **That is a claim about different deposits.** The
prediction is labelled a prediction, so the record is not wrong; but its worked
consequence — that `PXD026748` would be the first deposit evaluated against all
six gates — rests on a gate nobody has looked at. One lookup closes it.

---

## What the review does not touch

**R3 stands entirely.** The record's cleanest passage, and the distinction it
draws — C0 governs admissibility, the walk governs comparability, a deposit can be
one and not the other — is the thing most worth keeping in it.

**R4 stands.** The record selects no deposit and says so.

**The Context's correction stands and is the best work in the record.** It caught
a quotation that stopped one clause early, named both mechanisms, and refused to
pick between them on evidence the repository does not hold. Findings A, B and D
above are all consequences of that correction being right — they are the parts of
the record that had not yet been brought into line with it.
