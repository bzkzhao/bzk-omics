# ADR-0031 — Whether a deposit outside the survey's route may be selected, and what C0's gates ranged over

| | |
|---|---|
| Status | Proposed |
| Date | 2026-09-04 |
| Supersedes | — |
| Superseded by | — |

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

**R3 — Selection outside the route remains available for a deposit C0 never screened.** That is
what the *"anchor laboratory's own next dataset"* is, and it is not the same act: there is no
verdict to work around, no instrument to leave unread, and nothing recorded that the selection
contradicts. **The two cases are separated by whether a C0 verdict exists, not by the strength of
the ground offered.**

**R4 — The right answer to the underlying problem is to amend C0's scope so a gate is evaluated per
artefact, and this record does not make that amendment.** It is a criteria change and out of this
turn's scope. **Naming it and deferring the act is not rejecting it**, and the amendment's price is
already known from the one this project has made: *"a criteria change that binds every future draw;
it excludes seven of twelve retroactively; and it leaves C3's cap of twelve holding five, so the
survey is under-drawn until a re-draw, which is a separate turn."* **So the precedent is that a
retroactive criteria change is affordable here, having been paid once.**

### What the rule excludes

**A rule that admits exactly one deposit is a selection wearing a rule's clothes**, so the
exclusions are named rather than left to be inferred.

- **`PXD055843` is excluded today**, by R2. It was screened, it failed (c) and (d), and the
  amendment R4 names is unmade. **The rule's first consequence is to exclude the deposit that
  prompted it**, which is the strongest available evidence that it is a rule.
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
