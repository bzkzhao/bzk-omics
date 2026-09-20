# REVIEW — ADR-0035, a perturbation applied after the biological sample ends

**Reviewed 2026-09-19 at `ff54bf2`**, against the landed text. Six findings:

- one ruling (a): a defect in the thing decided;
- three rulings (b): narrowed;
- one ruling (c): stands;
- one set of factual edits with no bearing on any decision.

No decision is reversed outright. R2 loses the instance it was written for and
survives on a different one, which the deposit supplies and the record does not
yet know about.

The form follows ADR-0033's review. Each finding names its ruling, quotes the
sentence it turns on, and says what survives. Each figure is marked **measured**
(re-derived from the repository), **read** (quoted from a named source) or
**judged** (the reviewer's call).

The source this review leans on is already in the repository. It is
`data/frame/frame_raw.tsv`, the `PXD026748` row, field 14, the PRIDE
sample-processing protocol as captured on 2026-09-17 and committed at `3422d51`.
The record was landed at `3b7e969`, whose parent `0bd9653` is the tree its
Landing verification was re-derived against. It came after that capture, and it
did not read it for this point.

---

## A — The Context's premise is contradicted by the deposit. Ruling (a)

The record states: *"Two samples differing only in PLpro treatment come from one
culture, split after lysis."* Its R2 builds on this: *"the two aliquots are
different conditions on shared material."*

**The protocol says otherwise (read).** The count, and the absence of a split,
both rest on one clause. Five million cells of each genotype were *"seeded in
triplicate for each condition (WT or mutant PLpro)"*. The PLpro assignment is
therefore made at seeding, per dish. Two genotypes × two PLpro conditions ×
three gives twelve dishes, each already committed to one PLpro condition before
any lysate exists.

The following clause agrees: *"7.2 mg total protein of each replicate was
treated with recombinant WT or mutant PLpro"*, one treatment per replicate
lysate. The dish phrase *"12x150 mm2 culture dishes"* is consistent with twelve
dishes, but it also parses as a dish specification, so the count does not rest
on it.

The publication's methods say the same (Munnur et al., Nat Immunol
22:1416–1427, 2021, *Sample preparation for PLpro ISGylome*).
`curation_PXD026748.json`'s PAIRING item has recorded the contradiction since
turn 09.

**Ruling (a) — a defect in the thing decided.** R2 decides how to handle a
relation, and the relation it names does not exist in this deposit. That is more
than a flaw in how the record is presented: a builder following R2 would record
a split-lysate blocking structure that no source supports.

**What does not survive:**

- the Context's *"one culture, split after lysis"*;
- R2's *"the two aliquots are different conditions on shared material"*;
- `WALK-STANDARD` v2's *"three cultures split two ways"*, quoted in the Context
  as the reason being answered.

---

## B — R2 survives on a different instance: one digest split across two measurements. Ruling (b)

**The deposit does contain a split, one step later and across the arms (read).**
The same protocol field goes on, after on-column trypsin digestion of each
replicate: *"At this point, an aliquot of 30 µg total peptide was taken for
shotgun proteomics analysis. The remaining peptide solution was incubated with
antibody-bead slurry"*. So each shotgun run and one GG run measure two portions
of one digest.

**This is R2's shape, with the relation re-typed (judged).** `WALK-STANDARD`
§7(b) lists the lost relations it tests for as *"pairing, blocking, nesting,
shared source"*. The draft's relation was **blocking**, between conditions. The
one the deposit supplies is **shared source**: one unenriched and one enriched
measurement of the same material. R2's reasons all carry over unchanged:

- no `Sample` field names another `Sample`, and `bzk/ontology/schema.py`'s
  relationship tables name no Sample-to-Sample relation (measured);
- `replicate` cannot carry it, on the ground supplied at landing.

**That ground is now tested for the first time (measured).** The two records
give the same `replicate` values, 1 to 3, in both arms. Which shotgun `-N` came
from which GG `_repN` digest is stated nowhere in the deposit or the paper.
Reading equal `replicate` values as that pairing is exactly the reading the
record rejects. `curation_PXD026748_shotgun.json`'s REPLICATE LABELS item says
so.

**Ruling (b) — R2 is re-grounded and narrowed.** It stands as *"a shared-source
relation between Samples is not representable, and is not recoverable from
`replicate`"*. It no longer claims a blocking relation on the PLpro axis.

**Its consequence moves as well (read, then judged).** The publication analysed
the two arms separately: separate MaxQuant searches, and separate Perseus
analyses, each by condition. No published analysis depends on the cross-arm
relation. What depends on it is the platform's own protein adjustment of sites
at sample grain (I4 `'applied'`). Under R2 that adjustment can be keyed at
condition grain only. That is a limit on this platform, not a defeater of any
published claim.

---

## C — The defeater section loses its strong form. Ruling (b)

The record states: *"A reconstruction choosing an unpaired two-way ANOVA and one
choosing a paired one will not agree, and nothing in the publication says which
was run."*

The paired reading needs the split that finding A removes. **What survives is
narrower (judged).** Whether same-index dishes were seeded, stimulated or lysed
together, as **blocks**, is unstated. If they were, a model with a block term and
one without could disagree. The GG record's PAIRING item already puts it this
way. The surviving question is as invisible from the deposited matrix as the
original, so the record's *"invisible from the data structure"* stands for it.

**Ruling (b).**

- **What survives:** a defeater from an unstated design factor, the block,
  biting at the reconstruction alongside ADR-0034's unstated imputation.
- **What does not:** *"paired vs unpaired"*, and the claim that the PLpro axis
  is a split.

**Its standing in the defeater taxonomy weakens as well (judged).** The record
calls this *"a defeater arising from an unrepresentable design rather than an
omitted parameter"*. After A, the published analysis's surviving gap is an
**omitted design fact**, the block, not an unrepresentable one. The
unrepresentable relation in B bears on the platform's analysis, not the
publication's. So the claim-durability thesis loses this record as the
motivating instance of an *"unrepresentable design"* class. That is a finding
worth taking to the thesis rather than smoothing over.

---

## D — R1 stands, and one sentence of it is now false. Ruling (b) on the sentence, (c) on the decision

R1, *"`Sample` is the material measured"*, has now been applied in two committed
records:

- twelve GG Samples in `curation_PXD026748.json`;
- twelve shotgun Samples in `curation_PXD026748_shotgun.json`.

`tests/test_curation_pxd026748_arms.py` pins that the two sets are disjoint, and
that each shotgun Sample's identity fields equal one GG Sample's (measured). The
convention does work the record did not foresee. It makes 24 Samples over 12
dishes correct, because an enriched fraction and an unenriched aliquot are
different materials at the point of measurement.

**The sentence that no longer holds:** *"Twelve samples are twelve measured
materials. What would be false is reading them as twelve independent cultures."*
After A, the twelve GG Samples **are** twelve separately seeded dishes. The
caution belongs one level up. 24 Samples are 24 measured materials from 12
dishes, and what would be false is reading them as 24 independent cultures.

**Ruling (b) on the sentence; the decision stands (c).**

---

## E — R5 stands, and its instance count resets. Ruling (c)

R5 declines a `block` or `source_material_id` field: *"worth doing only when a
second deposit needs it. One instance is not a schema change; it is an
instance."*

After A and B, the PLpro instance is gone, and the one remaining instance, the
cross-arm split, is in the **same deposit**. So R5's trigger, a second deposit,
is not met, and R5 stands on its own terms. The review adds one thing: when a
second instance is counted, it must be counted as a **shared-source** instance,
so that the field eventually designed fits that relation and not the blocking
one.

**Ruling (c).**

---

## F — Factual edits with no bearing on any decision

These are **measured** unless marked.

1. *"the pattern is consistent across the 24 runs"*: **false**. The two arms use
   different naming schemes: `Gly-Gly-{WT|KO}[_mut]_repN` for GG, and
   `shotgun-{ctrl|ko}_{wt|mut}-N` for shotgun. This was read off both records'
   mapping keys. The correspondence between the schemes is itself a filename
   inference (shotgun record, rationale 1).
2. *"The one filename this repository records is `Gly-Gly-KO_mut_rep1`"*: **out
   of date**. Both records now hold all 24 run names. The *Not verifiable* list's
   entry for `Gly-Gly-WT_rep1` and `Gly-Gly-WT_mut_rep1` can be struck, because
   both are in `curation_PXD026748.json`'s keys.
3. *"catalytically dead SARS-CoV-2 PLpro"* (**read**): now sourced. The
   publication's methods make the mutant C111A and call it the catalytic dead
   mutant. The deposit still says only *"mutant"*. The GG record's PLPRO MUTANT
   item can cite the paper; that is a curation change, not this record's.

---

## What the review does not touch

- **R3 stands entirely.** An unrepresentable relation is not a §3 absence, and
  that is as true of the shared-source relation as of the blocking one.
- **R4 stands.** `unresolved` is the relation's home, and the shotgun record's
  DIGEST SPLIT item is its second use.
- **The ground supplied at landing stands**, and B is its first test. That ground
  is that `replicate` has never been given a meaning that includes shared
  material. It was the right ground to supply.
- **The Landing verification table stands** as a record of the landing.

---

## Edits required before acceptance

To be applied in one turn to the `Proposed` record, which `decisions/README.md`
allows during review:

1. **A:** rewrite the Context's split sentence to the deposit's design: twelve
   dishes, each assigned its PLpro condition at seeding. Quote the protocol's
   *"seeded in triplicate for each condition"* clause as the ground, not the dish
   phrase, citing `frame_raw.tsv`.
2. **B:** re-ground R2 as a shared-source relation, citing the aliquot sentence.
   State that no published analysis depends on it and that it limits I4
   `'applied'` to condition grain.
3. **C:** narrow the defeater section to the unstated block, and state that the
   *"unrepresentable design"* class loses this instance for the published
   analysis.
4. **D:** correct R1's caution sentence to 24 materials over 12 dishes.
5. **E:** add R5's note on counting the next instance by relation type.
6. **F:** the three factual edits.
7. Add a `Reviewed` header row citing this file, and set the status to
   `Accepted`.

**Consequences outside this record, each its own change:**

- `WALK-STANDARD` v2, §7's `PXD026748` row: **FAIL → UNRESOLVED**, because the
  block structure is unstated. The motivating-instance sentence (*"The
  `PXD026748` instance is why R5 exists"*) falls. This is the second time, after
  v1's `PXD074990`, and a dated correction is needed.
- `curation_PXD026748_shotgun.json`, rationale (2): it says the aliquot is read
  *"from the publication … not from the PRIDE record, which describes only the GG
  workflow"*. **That is the reviewer's error.** The short PRIDE project
  description omits it, but the PRIDE sample-processing protocol, committed in
  `frame_raw.tsv`, contains the same sentence. The primary source should be the
  committed one, with the paper as confirmation. A dated correction is needed.
- **For Adán, 21 September:** the two design questions this review cannot settle:
  - which shotgun `-N` came from which GG `_repN` digest;
  - whether same-index dishes were processed as blocks.
