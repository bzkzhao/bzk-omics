# ADR-0031 — Whether a deposit outside the survey's route may be selected, and what C0's gates ranged over

| | |
|---|---|
| Status | Accepted |
| Date | 2026-09-04 |
| Reviewed | 2026-09-04 — five findings, three grounds struck or narrowed, the worked example withdrawn; ~~held `Proposed`~~ **Accepted 2026-09-04, the round-trip complete** |
| Supersedes | — |
| Superseded by | — |

## Review

Landed `Proposed` at `365eab5` and reviewed ~~in the following turn, at `c95a52b`~~ —
**corrected 2026-09-04: the Review was written at `b9abe32`, which is the only commit that changed
this file; `c95a52b` is its parent and changed `ROADMAP.md` alone. The wrong SHA was the commit the
review turn was *working at*, which a record cannot name as its own — its own SHA does not exist
until it lands.** **Three of the five
findings struck or narrowed a ground and none reversed a decision. The decision is narrowed and its
worked example is withdrawn.** R1 stands untouched; R2's artefact-scope argument stands and its
reach narrows; R3's identification of its class is struck and replaced by a reading supplied here;
R4's conclusion stands and its affordability ground is struck.

**A reading is supplied to this record by the reviewer and is written in as decided, not as read.**
It is marked as such at its site, and its origin is named there.

### A — R3 substitutes a screening status for a laboratory. Ground struck

**What the source conditions the clause on: nothing about screening.** The sentence reads *"A deposit
could still be selected by hand or by the anchor laboratory's own next dataset; what (d) forecloses
is the *survey's* route to a selection, not selection itself."* It names **two routes** — by hand,
and the anchor laboratory's own next dataset — and **conditions neither on whether C0 screened the
deposit**. The only condition in the sentence governs what (d) forecloses.

**R3 says *"That is what the 'anchor laboratory's own next dataset' is"* of a deposit C0 never
screened. That identification is not in the source**: the source names a laboratory and a dataset,
and R3 substitutes a screening status for both. **Ruling (b) — the ground is struck.**

**What survives, and what does not.** R3's first half — that selection outside the route remains
available — **survives**, and on the source's own words rather than on the substitution. R3's second
half — that the class it is available for is *a deposit C0 never screened* — **does not**. And R3's
closing sentence, *"The two cases are separated by whether a C0 verdict exists, not by the strength
of the ground offered"*, is where the substitution is carried and is the sentence that decides where
any particular deposit falls.

#### The reading, decided here and not read from the source

**Origin: the reviewer. This is a decision about project intent and the tree does not settle it.**
The anchor-laboratory clause means **any deposit of that laboratory not yet used**, on the ground
that the project's interest is centralisation around that laboratory's work rather than around any
one study. **It is written here as decided; nothing in the source says it**, and a reader must not
take it for a reading of the sentence quoted above.

**What would falsify it**: any source in the tree conditioning the clause on something else — a
screening status, a date, or *"next"* read strictly as *not yet existing* — or a statement of
project intent that centralisation is not the ground. **None was found**, which is why the question
needed deciding rather than reading.

#### The consequence, measured

**`ROADMAP.md`'s two blocks on this deposit record, reviewer-supplied and not re-derivable in this
container, that `PXD055843` is the anchor laboratory's own deposit** — PrimarySubmitter Adan
Pinto-Fernandez, with the Contact List carrying that name under both `lab head` and
`dataset submitter`. **So under the reading decided above, `PXD055843` falls under R3's clause, and
under R3 as written it falls under R2**, since it carries a C0 verdict. **The sentence that decides
between them is R3's last one**, quoted above. **Establishing that R3 reaches a deposit is not
admitting it**, and nothing here selects, admits or scores anything.

### B — a named route is not selection outside the criteria. R2's reach narrowed

**Ruled separately from A and not inferred from it.** The source distinguishes *"the survey's route
to a selection"* from *"selection itself"*, so the survey's route is **a** route and the
anchor-laboratory clause names another. **(ii) was rejected for *"leave the criteria untouched,
select outside them"*** — going around the instrument — and its objection is that *"the restriction
would live in prose that the next ranking does not read."* **Using a route the document itself names
is not going around the instrument, so that objection does not attach to it.**

**Ruling (b) — R2's reach is narrowed, not struck.** **What survives**: R2's argument against hand
selection **on the artefact-scope ground**, which is (ii)'s objection applied to a scope gap and is
not disputed here. **What does not**: R2's reach over a deposit arriving by the anchor-laboratory
clause, which is a named route and not an act outside the criteria.

### C — the amendment was charged once, not paid once. Ground struck

R4 concludes that a retroactive criteria change is *"affordable here, having been paid once."*

**Measured: the re-draw the cost names was never run.** Instrument — `grep -n "re-draw\|redraw"` over
`ROADMAP.md` returns 13 lines carrying *re-draw*, of which the only one recording a re-draw that
happened is dated **2026-08-12**, which **predates the organism amendment of 2026-08-18** and is
therefore not the re-draw that amendment's cost names; the others are the cost sentence itself, its
consequence, and a statement that re-drawing is out of scope. ~~**And the survey table still carries
12 `yes` in its `In widened 12` column, counted over all sixty rows — not the five the amendment
left.**~~ — **second ground struck 2026-09-04: the two are different quantities.** `In widened 12`
records membership in the draw — the document's nearest statement is that *"exactly 12 rows are
`site=present` — the same twelve marked In widened 12"*, and no definition block defines the column
— while *holds five* counts survivors of those twelve under the gate added afterwards. **A
membership column does not move when a gate later excludes some of its members**, and consequence 1
of that same amendment closes *"Not amended, not re-scored."* — **so the column could not have moved
at all, and a column that was never re-scored is not evidence that a re-score did not happen.
Finding C's ruling survives on the date ground alone, which is untouched.** The consequence recorded from that amendment reads *"**C3's cap of twelve now holds five.**
The survey is under-drawn against its own size criterion and a re-draw is a separate turn."*

**Ruling (b) — the affordability ground is struck.** The cost was **charged and is outstanding**, so
a second retroactive amendment would add a second unpaid debt to a first still unpaid. **The
conclusion survives**: that amending C0 to evaluate per artefact is the right answer, and that this
record does not make the amendment, does not depend on the price. What must go is the claim that the
price has been paid.

### D — the carried defect is not minted twice, and it is not the defect the review expected

**Ruling (c) on the substance, with the identification corrected.** The passage carrying *"whether
(f) would pass or fail for any given row is unrecorded"* and calling it *"a defect in the record and
is carried, not repaired here"* is **the no-row-was-evaluated claim**, which the defect register
already carried before this record landed. **The defect minted at `365eab5` alongside this record is
a different claim** — that gate f's *temporal reach* is unstated, whether it applies retroactively
to the sixty-row draw or only prospectively — **and this record carries that one separately**, as
its implied change *"Gate f applied to the sixty, or a recorded statement that it is not applied
retroactively."* **Two neighbouring claims, both carried, neither minted twice, and the record is
right to carry them as carried.**

### E — every scope figure reproduces. No defect

**Measured independently of the record; instrument stated with each.**

| Figure | Instrument | Result |
|---|---|---|
| C0 gate rows | `awk` over the C0 table block matching `^\| [a-f] \|` | **6**, and gate f's row carries **Added 2026-08-18** |
| `grep -c "C0(f)"` over `ROADMAP.md` | that command | **0** |
| distinct `C0 gates met` values over the sixty rows | `awk` on the tenth pipe-delimited field of l.4573–4632 | `abcde` ×10, `abce` ×2, `abde` ×3, **`abe` ×45** — 60 rows, **zero cells containing an `f`** |
| C0(c) and C0(d) wording | their own table rows, quoted to the cell terminator | *"Carries a site-grain processed table"* and *"MaxQuant"* |

**Ruling (c) on all four.** **One figure the record did not give is worth recording**: `abe` is not a
rare cell but **45 of 60**, so the reading of what an `abe` cell can mean governs three quarters of
the table rather than one row.

## Scope

Decides whether a deposit that failed C0 may be selected outside the survey's route, and on what.
**It decides a rule and not an instance.** It selects no deposit, admits nothing, scores nothing,
amends no criterion, and fetches nothing. Every line reference was verified at `7b0cbff`.

**Two acts are distinguished throughout, because at several points either would fit.**
*Establishing a gate's scope* is reading what a gate ranged over. *Overturning a verdict* is saying
a gate was applied wrongly to what it did range over. **This record does the first everywhere and
the second nowhere**, and says which at each point.

## What C0's gates range over, read rather than inferred

**C0 has six gates, not five.** The table carries rows a through f, and f — *"The recorded organism
set includes the anchor's organism"* — is marked **Added 2026-08-18**.

**C0(c) is *"Carries a site-grain processed table"***, and its stated reason is *"The v0.1 path is
the MaxQuant site adapter; a protein-only deposit tests nothing at the grain the anchor domain lives
at"*. **So C0(c) ranges over a site-grain table.** Read from the gate's own row, not inferred from
C0(d)'s reading rule.

**C0(d) is *"MaxQuant"***, and its reading rule states: *"C0(d) asks whether a written adapter can
read the deposit's site-grain table, and an adapter consumes a file. A project-level `softwares`
list does not say which tool produced which file, so it cannot answer that question and must not
admit on its own."* **So C0(d) ranges over a file, and specifically over the site-grain table.**

**Both gates therefore range over the same artefact.** That is the finding, and it is a statement
about scope: neither gate was applied wrongly, and neither verdict is disturbed.

### A deposit can hold an artefact no C0 gate was applied to

**It can, and the case is not hypothetical.** C0's six gates range over: the deposit's embargo
status (a), its reuse terms (b), its site-grain table (c and d), its proteome's resolvability (e),
and its recorded organism set (f). **No gate ranges over a protein-grain artefact.** A deposit
carrying a protein-grain processed table and no site-grain one fails (c) and (d) on the artefact
they do range over, and the protein-grain table is never examined by any gate.

**And that artefact is not idle.** The Weeks 3–4 exit names a Perseus table, and
`bzk/adapters/perseus.py`'s own module docstring settles what that is: *"the grain is **protein**,
so a row becomes a `ProteinObservation` anchored on a `Protein`, and there is no
`ModificationSite`, no `ProteinSequence`, no sequence version to resolve and therefore no network
call in the ingestion path."* **So the artefact C0 never gates is the artefact one of the two exits
is written around.**

### What an `abe` cell can and cannot mean

The column is defined as listing *"which of (a)–(e) pass"* — **five letters against six gates** —
and `grep -c "C0(f)"` over `ROADMAP.md` returns **0**, so gate f is never referred to in the
notation the verdicts are recorded in and was applied to no row. The table-wide statement is that
*"Every one of the sixty is CC0 with a resolvable organism, so C0(a), (b) and (e) never bind in this
draw"* and that the gate *"is decided entirely by (c) and (d)"*.

**So an `abe` cell means exactly this: (c) and (d) failed; (a), (b) and (e) passed and could not
have done otherwise in this draw; and (f) was not evaluated.** It cannot mean *this deposit was
screened against C0 as C0 now stands*, because a sixth gate exists that no row met or failed.

**Two things follow, and only the first bears on this decision.** First, an `abe` cell is a verdict
on two gates, not five and not six — which is why the scope of those two gates is the whole
question. Second, whether (f) would pass or fail for any given row is unrecorded; *"a resolvable
organism"* is gate (e) and is a different claim from *"includes the anchor's organism"*, so the
table-wide sentence does not cover (f) even by implication. **The second is a defect in the record
and is carried, not repaired here.**

## The question, and what already answers half of it

*"What (d) forecloses is the *survey's* route to a selection, not selection itself"*, and *"A
deposit could still be selected by hand or by the anchor laboratory's own next dataset"*. And
whether a second deposit should be ingested on the weakest basis *"is a decision nobody has made"*.

**So selection outside the route is available and unmade. The question is on what.**

### The option that looks right has already been rejected here, on a ground that still bites

**Selecting outside untouched criteria is not an open option in this repository.** It was considered
and rejected: *"**(ii) — rejected. Leave the criteria untouched, select outside them.** **Cost:**
nothing today, and the same failure tomorrow. C2 would still rank a plant first on the next
application, and the restriction would live in prose that the next ranking does not read. It is
honest about *this* selection and dishonest about the instrument."*

**The option this record was asked to weigh is that same option**, and saying so is the first thing
it owes. *Hand selection on a stated ground, with the C0 record carried rather than set aside* is
*leave the criteria untouched, select outside them* with the ground named. Naming the ground does
not answer the objection, because the objection is not that the ground would be unstated — it is
that **the instrument would go on not reading it**.

**Can the present case be distinguished? The candidate distinction is real and it does not survive
the last sentence.** The distinction is that (ii) was rejected where the criteria *selected wrongly*
— C2 ranking a plant first — whereas here the criteria *never ranged over* the artefact a selection
would be for. That is a genuine difference in kind. **But it makes the objection worse, not
better.** If C0 never ranges over protein-grain artefacts, then selecting one deposit outside C0 on
that ground leaves the next draw's C0 still not ranging over them, and the restriction lives in
prose the next screening does not read — which is (ii)'s sentence applied verbatim to a wider
failure. **A scope gap is more durable than a ranking error, so the argument against selecting
around it is stronger.**

## Decision

**R1 — The scope finding stands and licenses nothing on its own.** C0(c) and C0(d) range over the
site-grain table; a protein-grain artefact in any of the sixty was never gated. **This is
established and no verdict is overturned by it.** An `abe` cell remains a correct record of what it
records.

**R2 — A deposit that C0 screened and failed may not be selected outside the survey's route on the
ground that a gate never ranged over some artefact it holds, while the criteria stand as they are.**
Rejected on the repository's own recorded ground, quoted above and answered directly rather than
distinguished away.

**Reach narrowed by Review finding B, 2026-09-04.** The artefact-scope argument above survives
untouched. What does not is this rule's reach over a deposit arriving by the anchor-laboratory
clause: the source distinguishes *"the survey's route to a selection"* from *"selection itself"*, so
that clause is a route the document names, and (ii)'s objection — that the restriction would live in
prose the next ranking does not read — does not attach to a named route.

**R3 — Selection outside the route remains available for** ~~a deposit C0 never screened~~ —
**the class re-decided by Review finding A, 2026-09-04: any deposit of the anchor laboratory not yet
used. That reading is decided by the reviewer and not read from the source, which conditions the
clause on no screening status at all.** ~~That is what the *"anchor laboratory's own next dataset"*
is~~ — **identification struck by the same finding: the source names a laboratory and a dataset, and
this substituted a screening status for both.** The rest of the sentence stands: it is not the same
act — there is no verdict to work around, no instrument to leave unread, and nothing recorded that
the selection contradicts. ~~**The two cases are separated by whether a C0 verdict exists, not by the strength of
the ground offered.**~~ — **struck by Review finding A, 2026-09-04: this is the sentence that
carried the substitution, and it is the sentence that decides where any particular deposit falls.
Under the re-decided reading `PXD055843` falls under this clause; under the sentence as written it
falls under R2.**

**R4 — The right answer to the underlying problem is to amend C0's scope so a gate is evaluated per
artefact, and this record does not make that amendment.** It is a criteria change and out of this
turn's scope. **Naming it and deferring the act is not rejecting it**, and the amendment's price is
already known from the one this project has made: *"a criteria change that binds every future draw;
it excludes seven of twelve retroactively; and it leaves C3's cap of twelve holding five, so the
survey is under-drawn until a re-draw, which is a separate turn."* **So the precedent is that a
retroactive criteria change is affordable here, ~~having been paid once~~ — **struck by Review
finding C, 2026-09-04: it was charged once and the charge is outstanding. The re-draw that cost
names was never run — the only recorded re-draw is dated 2026-08-12 and predates the 2026-08-18
amendment, ~~and the survey table still carries 12 `yes` in `In widened 12`, not the five the
amendment left~~ — **that second ground struck 2026-09-04: a membership column and a survivor count
are different quantities, and consequence 1 records *"Not amended, not re-scored."*, so the column
could not have moved. This correction stands on the date ground alone.** A second retroactive
amendment would add a second unpaid debt to a first still
unpaid. The conclusion above survives; the price claim does not.**

### What the rule excludes

**A rule that admits exactly one deposit is a selection wearing a rule's clothes**, so the
exclusions are named rather than left to be inferred.

- ~~**`PXD055843` is excluded today**, by R2. It was screened, it failed (c) and (d), and the
  amendment R4 names is unmade. **The rule's first consequence is to exclude the deposit that
  prompted it**, which is the strongest available evidence that it is a rule.~~ — **withdrawn by
  Review finding A, 2026-09-04: under the re-decided reading of the anchor-laboratory clause this
  deposit falls under R3 rather than R2, so this worked example does not hold. The three exclusions
  below stand, so the rule still excludes — but not on this instance, and the record's strongest
  evidence that it is a rule rather than a selection is withdrawn with it.**
- **`PXD078284` is excluded under R2 and would remain excluded under R4's amendment.** Its recorded
  ground is *"C0(c), C0(d) — Arabidopsis XL-MS; no processed output"* — a deposit with no processed
  output holds no artefact of any grain for a per-artefact gate to range over.
- **`PXD074126` is excluded on the same two counts**, its recorded ground being *"C0(c), C0(d) —
  Arabidopsis"*, and gate f would bear on it were f ever applied.
- **All sixty rows of the survey table are excluded from the artefact-scope ground**, since every
  one carries a C0 verdict. R3's route is not open to any of them.

### What the rule permits

**A deposit C0 never screened**, on a ground stated at selection. The anchor laboratory's next
dataset is the case the document already names, and it needs no amendment because it needs no
exception.

## Options, each with its cost

| Option | Cost | Disposition |
|---|---|---|
| **(1) no hand selection at all** | v0.1's second-deposit half waits indefinitely | **rejected**: the document already records that (d) forecloses the survey's route and not selection itself, so this is stricter than the tree |
| **(2) hand selection on a stated ground, criteria untouched** | *"nothing today, and the same failure tomorrow"* | **rejected — it is the already-rejected (ii)**, and the artefact-scope distinction strengthens rather than weakens its objection |
| **(3) amend C0 to evaluate per artefact** | a criteria change binding every future draw, retroactive re-screening, the survey under-drawn until a re-draw | **named as the right answer and not made** — out of this turn's scope, and R4 says so rather than rejecting it |
| **(4) admissibility becomes exit-relative** | a second admissibility notion, and every recorded verdict becomes ambiguous as to which exit it ranged over | **rejected as new**: nothing in the tree makes admissibility exit-relative today — C0's rows name no exit, and the survey records one verdict per deposit |
| **(5) defer the question** | nothing about a deposit changes while the decision waits | **rejected on the asymmetry below** |

**On (4), measured rather than assumed**: C0's six gate rows name no exit and the sixty-row table
carries one `C0 gates met` cell per deposit, not one per exit. So exit-relative admissibility would
be new, and it would make every existing `abe` cell ambiguous as to which exit it was a verdict
for. That cost is not worth paying to reach a conclusion R4 reaches without it.

**On (5): deferring costs nothing about the deposit and something about the instrument.** A
deposit's files do not change while a decision waits, so nothing degrades on that side. What
degrades is that the scope gap R1 establishes stays unrecorded in C0 itself, and the next draw
screens on the same five-of-six letters. **What would make it urgent** is a second draw being run,
or a protein-grain deposit being offered from outside the survey — the second being R3's case,
which needs no decision here.

## What this record does not settle

**Whether R4's amendment should be made, and in what form.** This record establishes that the scope
gap is real and that closing it is the way through; it does not decide whether a per-artefact gate
replaces (c) and (d), supplements them, or is a sixth-and-seventh pair. **That is a criteria change
and needs its own record.**

**Whether `PXD055843` would pass an amended C0.** Nothing here bears on it. The tree records that
deposit's failures without establishing they are sound — no per-deposit ground, an undefined
`Skipped` column on which it is the table's extreme outlier, and the archive-read reassurance
scoped to a twelve it is not in — and that finding stands whatever this record decides.

## Implied changes, described and not made

1. **A criteria change amending C0's scope to per-artefact evaluation**, with the retroactive
   re-screening and the re-draw its precedent priced. Its own record.
2. **The `C0 gates met` column's notation widened to six letters**, or a stated reason it stays at
   five. Today it cannot express a verdict on the gate added 2026-08-18.
3. **Gate f applied to the sixty**, or a recorded statement that it is not applied retroactively.
4. **None of these before the amendment in 1**, which is the only ordering this record fixes.

## Consequences

**No deposit is selected and no verdict moves.** R2's immediate effect is to exclude the deposit
whose case prompted the question, and R3's route is open to no row of the survey table.

**The scope finding is recorded where a future screening can read it**, which is what (ii)'s
rejection asked for and what a selection outside untouched criteria would not have achieved.

**A distinction is drawn here that the repository did not previously carry, and it is labelled as
invented rather than presented as read**: the split between *a deposit C0 screened and failed* and
*a deposit C0 never screened*. The document's hand-selection sentence does not distinguish them —
it says selection is not foreclosed, without saying whether that covers a screened-and-failed
deposit. **R2 and R3 together are that distinction, and it is this record's, not the document's.**

**What this record does not establish** is that the rule is complete. It governs the ground it was
asked about — a gate's scope — and says nothing about a selection offered on some other ground that
C0 also never spoke to. Whether R2 generalises to those is not decided, and stating that is
cheaper than discovering it later.
