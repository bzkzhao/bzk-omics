# ADR-0035 — A perturbation applied after the biological sample ends

| | |
|---|---|
| Status | Accepted |
| Date | 2026-09-18 |
| Reviewed | 2026-09-19 — six findings; one defect in the decision, three grounds narrowed, one stands; `notes/reports/REVIEW-ADR-0035.md` |
| Supersedes | — |
| Superseded by | — |

Landed `Proposed` at `3b7e969` and reviewed at `ff54bf2`; `Accepted` on
2026-09-20 once that round-trip completed, per `decisions/README.md`. The
reviewer drafted it against `d46a3ab`, and it was numbered 0035 on landing,
following ADR-0033 and ADR-0034 in landing order.

**The review found a defect in the thing decided, and no decision is reversed.**
R2 was written for a split that this deposit does not contain; the deposit
supplies a different split, one step later, and R2 survives on that. Every
change the review forced is carried through the text below and listed under
*Review* at the end, each against the finding that forced it. Where a sentence
did not survive it is struck rather than deleted, so the correction is visible.

**Every claim this record makes about the repository was re-derived at
`0bd9653` (2026-09-19) before landing, and six were corrected.** The
corrections are listed, each with the check that forced it, under *Landing
verification* at the end. **One of them changes the ground of R2:** the draft
killed the reading that `replicate` carries the pairing by pointing at a fact
about the anchor that this repository does not hold. R2's decision stands, on a
ground supplied at landing and marked as such.

---

## Context

`PXD026748`'s design has two treatments in sequence, **in different
compartments**. HeLa WT and *Isg15*-/- cells are stimulated with IFN-α at
500 U/mL for 72 h — a treatment of living cells. The **lysates** are then
incubated with recombinant wild-type or catalytically dead SARS-CoV-2 PLpro at
1:50 w/w for 30 min.

**Sourced on review, 2026-09-19: *"catalytically dead"* is the publication's, not
the deposit's.** The protocol field says only *"mutant PLpro"*; the reviewer
reports that the publication's methods make the mutant C111A and call it the
catalytic dead mutant. **That is a read this repository cannot check — the paper
is not on disk** — so it is attributed rather than asserted, and
`curation_PXD026748.json`'s PLPRO MUTANT item continues to record that the
deposit does not say it. Citing the paper there is a curation change and not this
record's.

**The contrast that defines the paper's claim is the second one**, and it happens
after the biological sample has ceased to exist.

~~Two samples differing only in PLpro treatment come from **one culture, split
after lysis**.~~ **Struck on review, 2026-09-19: the deposit's own protocol says
the opposite.** `data/frame/frame_raw.tsv`, the `PXD026748` row, field
`sampleProcessing` — the PRIDE sample-processing protocol captured 2026-09-17
and committed at `3422d51` — reads: *"five millions cells of each genotype were
seeded in triplicate for each condition (WT or mutant PLpro)"*. **The PLpro
assignment is made at seeding, per dish.** Two genotypes × two PLpro conditions ×
three replicates is twelve dishes, each already committed to one PLpro condition
before any lysate exists. The next clause agrees — *"7.2 mg total protein of each
replicate was treated with recombinant WT or mutant PLpro"* — one treatment per
replicate lysate, not two aliquots of one.

**The ground is the seeding clause, not the dish phrase.** *"12x150 mm2 culture
dishes"* in the same sentence is consistent with twelve dishes and also parses as
a dish specification, so the count does not rest on it.

The record was landed after that capture and did not read it for this point.
`curation_PXD026748.json`'s PAIRING item has recorded the contradiction since
turn 09, and the protocol still places the PLpro incubation after lysis — so the
*compartment* claim above is untouched. What is struck is the *split*.

`WALK-STANDARD` v2 records this as the deposit's R5 FAIL and names it as the
instance that motivated R5. Its stated reason is: *"Expressing it as
`Sample.treatment` multiplies samples falsely; not expressing it breaks I11's
`Cell` key; and the pairing — three cultures split two ways, not six
independent replicates — is unrecordable either way. **To clear:** an ADR on
post-preparation perturbation."* **This is that ADR, and R1 below disagrees
with the first clause of that reason.** The quotation stands verbatim because it
is what v2 says; its third clause — *"three cultures split two ways"* — does not
survive the finding above, and `WALK-STANDARD` carries its own dated correction. The rest of the walk record
(`walk/walk_PXD026748.json`, judged against v1) reads:

- **R1** passes at G4 — in the draft's words, *"the cleanest claim table of the
  four candidates"*.
- **R2** passes at grade B, from the deposit itself.
- **R4** passes.
- **R3** passes only **provisionally**, at G1: the design is derived from
  filenames, with confidence `inferred` under I8, and there is no SDRF and no
  design spreadsheet.

### What the schema provides

`ONTOLOGY.md:384-398`. `Sample` carries `source_type`, `cell_line`,
`organism_taxid`, `model_system`, `genotype`, `treatment`, `timepoint_h`,
`replicate` and `replicate_type` — and **every one of them is identifying**
(`ONTOLOGY.md:115`). `treatment`'s comment exemplifies
*'IFN-alpha2b 10 U/mL'*; `timepoint_h` is *"hours SINCE TREATMENT, not hours in
culture"*. A grep of `ONTOLOGY.md` for *aliquot*, *lysate*, *post-lysis* or
*ex vivo* returns nothing.

---

## The reading that looks right and is not

**`replicate` appears to carry the pairing for free.** The deposit's own
filenames put the same index on both aliquots of one culture. ~~The one filename
this repository records is `Gly-Gly-KO_mut_rep1`, in the walk record's R3 note,
and the pattern is consistent across the 24 runs.~~ **Both clauses corrected on
review, 2026-09-19.** The repository now records **all 24 run names**, as the two
curation records' mapping keys. And the pattern is *not* consistent across them:
the two arms use different schemes — `Gly-Gly-{WT|KO}[_mut]_repN` for the GG arm,
`shotgun-{ctrl|ko}_{wt|mut}-N` for the shotgun arm — so the correspondence
between the two is itself a filename inference, which
`curation_PXD026748_shotgun.json`'s rationale (1) records as such. So
`(genotype, replicate)` would identify the culture, and the pairing would be
recoverable without any schema change.

**It fails — but not for the reason the draft gave.** The draft said the anchor
kills the reading: *"In `PXD018299`, WT_IFN replicate 1 and WT_mock replicate 1
are separate wells seeded separately."* **This repository does not hold that
fact.** The anchor's curation record gives `WT_1` and `WT_IFN_1` the same index,
`replicate: 1`, and says nothing about wells or seeding. Its `unresolved` list
states the opposite of certainty: *"Replicate type (biological vs technical) is
not explicitly stated in the methods for the GlyGly peptidome. Recorded as
'unspecified' pending author correspondence."*

**The ground that does hold — supplied at landing, not read from the draft.**
Whether or not the anchor's replicates share material, `replicate` has never
been given a meaning that includes shared material. The field carries no DDL
comment, and the anchor's own record declares its replicate structure unknown.
Reading the field as a source identifier therefore fails either way:

- **Applied uniformly**, the reading would make the anchor's existing twelve
  `Sample`s assert something new. `WT_1` and `WT_IFN_1` share genotype and index,
  so under it they would share material, and nobody has established that.
  Writing it into the graph asserts what the data cannot support.
- **Applied only to `PXD026748`**, it makes one field mean two things in one
  graph, which is the overloading this project refuses everywhere else.

The draft's argument needed the anchor *not* to pair. This one works whether it
pairs or not, which is why it replaces the draft's rather than sitting beside it.

**`replicate INT64` carries no DDL comment.** Of `Sample`'s nine descriptive
fields it is the only one without one. `id` and `label` carry none either, but
they are the identity pair, and the opening `id` line is uncommented on most node
tables in the DDL.
The reading is available only because the field never said what it meant, which
is a reason to fix the comment, not a licence to exploit it.

---

## Decision

**R1 — `Sample` is the material measured, not the organism it came from.** The
twelve GG runs map to twelve `Sample` nodes. `treatment` names the full sequence
and `timepoint_h` measures from the contrast-defining treatment, 0.5 h.

This is not a false assertion. A lysate aliquot incubated with a protease **is**
distinct material at the point of measurement, and `source_type`, `cell_line` and
`genotype` describe its provenance rather than its identity. The convention is
stated here because the DDL does not state it. **This answers `WALK-STANDARD`
v2's *"multiplies samples falsely"* directly.**

~~Twelve samples are twelve measured materials. What would be false is reading
them as twelve independent cultures, and that reading is exactly what R2 declines
to encode.~~ **Corrected on review, 2026-09-19.** After the Context's correction
the twelve GG `Sample`s *are* twelve separately seeded dishes, so that caution
was aimed one level too low. **24 `Sample`s are 24 measured materials from 12
dishes**, and what would be false is reading them as 24 independent cultures.

R1 has since been applied in two committed records — twelve GG `Sample`s in
`curation_PXD026748.json` and twelve shotgun `Sample`s in
`curation_PXD026748_shotgun.json` — and does work this record did not foresee.
`tests/test_curation_pxd026748_arms.py` pins that the two sets are **disjoint**
and that each shotgun `Sample`'s identity fields equal one GG `Sample`'s. That is
R1 being right about a case it never named: an enriched fraction and an
unenriched aliquot of one digest are different materials at the point of
measurement, so 24 over 12 is correct rather than a doubling.

**R2 — ~~the pairing is a blocking relation~~ the relation is a *shared source*,
and this schema cannot express it.**

~~It is not a replicate: the two aliquots are different *conditions* on shared
material, not repeated measurements of one condition.~~ **Re-grounded on review,
2026-09-19.** The instance R2 was written for does not exist: the PLpro axis is
assigned at seeding, so there are no two aliquots of one lysate. **The deposit
supplies a different split, one step later and across the two arms.** The same
protocol field, after on-column trypsin digestion of each replicate, reads: *"At
this point, an aliquot of 30 µg total peptide was taken for shotgun proteomics
analysis. The remaining peptide solution was incubated with antibody-bead
slurry"*. Each shotgun run and one GG run therefore measure two portions of one
digest.

`WALK-STANDARD` §7(b) lists the lost relations it tests for as *"pairing,
blocking, nesting, shared source"*. The relation here is the fourth, not the
second: one unenriched and one enriched measurement of the same material. **R2's
two reasons carry over unchanged.** It is not a `Sample` field: no field names
another `Sample`, and `bzk/ontology/schema.py`'s relationship tables name no
Sample-to-Sample relation — `PERFORMED_ON`, `PRODUCED` and `SAMPLE_GENERATED_BY`
are the only three that touch `Sample`, and none of them is one. And it is not
recoverable from `replicate`, on the ground above — **which this instance tests
for the first time.** Both records give `replicate` the values 1 to 3; which
shotgun `-N` came from which GG `_repN` digest is stated nowhere in the deposit
or the publication, so reading equal indices as that pairing is exactly the
reading the ground rejects. `curation_PXD026748_shotgun.json`'s REPLICATE LABELS
item says so, and its DIGEST SPLIT item is R4's home for the relation itself.

**So R2 stands as: a shared-source relation between `Sample`s is not
representable, and is not recoverable from `replicate`.** It no longer claims a
blocking relation on the PLpro axis.

**Its consequence moves with it.** The publication analysed the two arms
separately — separate searches, separate Perseus analyses, each by condition —
so **no published analysis depends on the cross-arm relation**. What depends on
it is this platform's own protein adjustment of sites at sample grain (I4
`'applied'`): under R2 that adjustment can be keyed at **condition grain only**.
That is a limit on this platform, not a defeater of any published claim.

**R3 — it is NOT recorded as a §3 absence, and the reason is the finding.**
§3's classification governs **absent values on identifying fields that exist**.
In its own words: *"An identifying field may be null — but only when something
outside the moment of ingest fixes that null."* There is no field here to be
null. **An unrepresentable relation is not an absent value, and §3 has no cell
for it.** Declaring one would file this under a taxonomy that does not cover
it — the same error as recording a contingent null as a determined one, which
ADR-0021 refuses.

**R4 — the gap is declared in the curation record's `unresolved`, naming the
specific relation and its consequence.** That is where an unrepresentable fact
about a deposit currently has a home. It is a weaker home than a typed field, and
the record should say so.

**R5 — no field is added to `Sample` in this record.** A `block` or
`source_material_id` field would be identifying under ADR-0021's reasoning, as
every descriptive `Sample` field is (`ONTOLOGY.md:115`). It would therefore
change every existing `Sample` id, and it is worth doing only when a second
deposit needs it. One instance is not a schema change; it is an instance.

**The instance count reset on review, 2026-09-19, and R5's trigger is further
off than it looked.** The PLpro instance is gone with the Context's correction,
and the one that replaces it — the cross-arm digest split — is in the *same*
deposit. So R5's trigger, a *second deposit*, is still not met, and R5 stands on
its own terms rather than on the count it was written against. **When a second
instance is counted, it must be counted as a shared-source instance**, so that
the field eventually designed fits that relation and not the blocking one R2 no
longer claims. A `block` field designed for the struck instance would be the
wrong field, shipped for a reason that had already been withdrawn.

---

## What this unblocks, and it is more than expected

**The lysate question does not block the ingest. It blocks the reconstruction.**

The site-table ingest needs samples and cells. Under R1 it has twelve of each,
and every cell is a measured value from a named run. **Nothing in the ingest path
consults the pairing.**

The pairing binds at the reconstruction, where the choice between a paired and an
unpaired two-way ANOVA is made — and the publication **does not state which it
ran**.

**The stage matches ADR-0034's, and the scope does not.** ADR-0034 is about
`PXD065158`. There, *"the `Analysis`, the `DifferentialResult`s and the
published claim set ingest fine. What is withheld is the columnar half of I11"*
— the `Cell`s, because none of `Cell`'s four columns separates a measured
number from a generated one. The pairing here withholds less: every cell is
measured, so nothing at ingest is withheld and only the reconstruction waits.
Imputation is also unstated in `PXD026748` (the walk's R2 records it so). That
makes two unstated analytical choices in this one deposit, both biting at the
reconstruction.

**So the lysate question is not what stands between `PXD026748` and ingest.**
It is not the only item, either. The walk record's *multiplicity finding* says
the publication consumed the **expanded** site table, which is per-multiplicity
intensities. `Analysis.quantity`'s closed enum defers per-multiplicity
consumption until *"a per-multiplicity analysis is actually run"*
(`ONTOLOGY.md:474-483`), and `quantity` is identifying. The walk softens the
practical consequence — every one of the 296 published claims is a
multiplicity-1 row — but it leaves the enum question standing. **That is a
separate question, and this record does not settle it.**

---

## The defeater this produces

~~A reconstruction choosing an unpaired two-way ANOVA and one choosing a paired
one will not agree, and **nothing in the publication says which was run**.~~
**Narrowed on review, 2026-09-19.** The paired reading needed the split the
Context's correction removes, so *"paired vs unpaired"* is no longer the
question.

**What survives is narrower and still bites.** Whether same-index dishes were
seeded, stimulated or lysed together — as **blocks** — is unstated. If they were,
a model carrying a block term and one without it could disagree, and nothing says
which the publication ran. `curation_PXD026748.json`'s PAIRING item already puts
it this way. The surviving question is as invisible from the deposited matrix as
the original was, so the record's *"invisible from the data structure"* stands
for it: a reader of that matrix cannot tell whether the replicate index carries a
block.

~~That is a defeater arising from an **unrepresentable design** rather than an
omitted parameter, and the taxonomy has no class for it. It is the second such
instance found this week, after the walk's own R5 gap — and the first where the
unrepresentability sits in the schema rather than in the standard.~~ **Struck on
the same review, and this is the finding worth carrying rather than smoothing
over.** After the correction, the published analysis's surviving gap is an
**omitted design fact** — the block — not an unrepresentable one. The
unrepresentable relation that does remain, R2's shared source, bears on *this
platform's* analysis and not on the publication's. **So the claim-durability
thesis loses this record as the motivating instance of an "unrepresentable
design" class.** The class may still exist; this deposit is no longer the case
that establishes it, and finding that out cost one reading of a protocol field
this repository already held.

**What replaces it at the reconstruction:** an unstated design factor, the block,
biting alongside ADR-0034's unstated imputation. Two unstated analytical choices
in one deposit, as before — one of them now a different kind.

---

## What this record does not settle

- **Whether `replicate` should get a DDL comment.** It should — it is the only
  descriptive `Sample` field without one — but fixing it is an `ONTOLOGY.md`
  edit with its own review. This record only shows why it matters.
- **What the anchor's replicate index means.** The anchor's curation record
  leaves its replicate type `unspecified` pending author correspondence. A
  comment on `replicate` cannot be written truthfully until that closes, or
  until the comment is phrased to cover not knowing.
- **Whether a `block` field is eventually right.** R5 defers it to a second
  instance, not forever.
- **Which ANOVA the publication ran.** That needs correspondence, or a
  peer-review file under `WALK-STANDARD` §4 source 5a.
- **Whether per-multiplicity consumption enters `Analysis.quantity`.** The walk
  record names it, and it is not this record's question.
- **Whether `PXD026748` is selected.** ADR-0033 routes it to C0; C1 and C2 decide.

---

## Landing verification

Re-derived at `0bd9653`. Where a check disagreed with the draft, the check
governs and the draft was edited. Each correction below names its check.

| # | the draft said | the check | what it showed | edit |
|---|---|---|---|---|
| 1 | WT_IFN rep 1 and WT_mock rep 1 in `PXD018299` *"are separate wells seeded separately"* | `data/curation/curation_PXD018299.json` `mapping` and `unresolved`; a repository-wide search for *seeded*, *separate well*, *same culture*, *paired* | Both samples carry `replicate: 1`. Nothing in the repository says anything about wells or seeding, and the record states the replicate type is *"not explicitly stated in the methods"* | The claim is removed. R2's *"not recoverable from `replicate`"* now rests on a ground supplied at landing, which holds whether or not the anchor pairs |
| 2 | `replicate` is *"the only field of `Sample`"* without a DDL comment | `ONTOLOGY.md:384-398` | `id STRING, label STRING` carry none either. They are the identity pair, and the opening `id` line is uncommented on most node tables in the DDL | *"the only one of `Sample`'s nine descriptive fields"* |
| 3 | §3 classifies *"absent values on fields that exist"* | `ONTOLOGY.md:134` | *"An **identifying** field may be null — but only when…"* | Sharpened to *identifying* fields, with the sentence quoted. This strengthens R3 |
| 4 | *"R3 and R4 both passing"* | `walk/walk_PXD026748.json` `requirements` | R3 is `PASS-provisional` at G1, grade B, with the design derived from filenames | Stated as provisional |
| 5 | ADR-0034's imputation *"blocks the Perseus-side analysis and not the search-output ingest"* | `decisions/0034-…md:42-45` | ADR-0034 withholds *"the columnar half of I11"* — the `Cell`s — for `PXD065158`, while the `Analysis`, results and claim set ingest | Quoted in ADR-0034's own terms. The stage matches and the scope differs |
| 6 | *"`PXD026748` can be ingested now"* | the walk record's `the_multiplicity_finding`; `ONTOLOGY.md:474-483` | The publication consumed per-multiplicity intensities, which the closed `quantity` enum defers | Narrowed to: the lysate question does not block ingest. The enum item is named as separate and not settled |

**Two additions that are not corrections.** The Context now quotes
`WALK-STANDARD` v2's R5 reason in full, because R1 disagrees with its first
clause and a reviewer should see what is being answered. The *filenames* claim
now cites the one filename the repository actually records.

**Held without edit:**

- the DDL span `384-398`;
- `treatment`'s and `timepoint_h`'s comments, verbatim;
- the grep for *aliquot*, *lysate*, *post-lysis* and *ex vivo*, which returns
  nothing (exit 1);
- R5's premise that a new `Sample` field would be identifying, which holds
  because every descriptive field is (`ONTOLOGY.md:115`);
- the curation record's `unresolved` key as R4's home;
- 2 × 2 × 3 = 12 GG runs.

**Not verifiable from the repository, and left as the reviewer wrote them:**

- *"the cleanest claim table of the four candidates"*, kept in the Context and
  attributed to the draft;
- ~~the specific filenames `Gly-Gly-WT_rep1` and `Gly-Gly-WT_mut_rep1`, since
  only `Gly-Gly-KO_mut_rep1` is recorded;~~ **struck 2026-09-19: both are in
  `curation_PXD026748.json`'s mapping keys and were verified there;**
- ~~*"the second such instance found this week"*;~~ **struck 2026-09-19 with the
  sentence that carried it;**
- ~~*"the taxonomy has no class for it"*.~~ **struck 2026-09-19 with the same
  sentence — the class may exist, and this deposit no longer establishes it.**

---

## Review

Reviewed 2026-09-19 at `ff54bf2`, against the landed text.
`notes/reports/REVIEW-ADR-0035.md` carries the review in full. **Six findings:
one ruling (a) — a defect in the thing decided — three (b) — narrowed — one (c)
— stands — and one set of factual edits bearing on no decision.** Every change
is carried into the text above and struck where a sentence did not survive.

| # | ruling | what it turned on | what it changed here |
|---|---|---|---|
| A | **(a)** | `frame_raw.tsv`'s `sampleProcessing` field: *"seeded in triplicate for each condition (WT or mutant PLpro)"* | The Context's *"one culture, split after lysis"* is struck. The PLpro axis is assigned at seeding, twelve dishes, and R2's instance goes with it |
| B | (b) | the same field, after digestion: *"an aliquot of 30 µg total peptide was taken for shotgun proteomics"* | R2 is re-grounded on a **shared-source** relation across the two arms. Its two reasons carry over; the `replicate` ground is tested for the first time. Its consequence narrows to I4 `'applied'` at condition grain |
| C | (b) | *"A reconstruction choosing an unpaired two-way ANOVA…"* | The defeater narrows to an **unstated block**. The *"unrepresentable design"* class loses this record as its motivating instance for the published analysis |
| D | (b) sentence, **(c)** decision | *"Twelve samples are twelve measured materials…"* | Corrected to 24 materials over 12 dishes. R1 itself stands, and is now applied in two committed records |
| E | **(c)** | *"One instance is not a schema change; it is an instance."* | R5 stands; the instance count resets, and the next one must be counted as shared-source |
| F | — | three factual claims | The 24-run pattern, the one-filename claim and the *"catalytically dead"* attribution |

**What the review did not touch:** R3 entirely — an unrepresentable relation is
not a §3 absence, and that holds for the shared-source relation as it did for the
blocking one; R4 — `unresolved` is still the relation's home, and the shotgun
record's DIGEST SPLIT item is its second use; the ground supplied at landing,
which B is the first test of; and the Landing verification table, which stands as
a record of the landing rather than of the review.

**Two consequences outside this record**, each landed as its own change:
`WALK-STANDARD` v2's §7 `PXD026748` row (FAIL → UNRESOLVED, and the
motivating-instance sentence withdrawn), and `curation_PXD026748_shotgun.json`'s
rationale (2), whose primary source for the aliquot sentence was the publication
where the committed PRIDE protocol says the same thing.

**Two design questions this review could not settle**, carried to author
correspondence: which shotgun `-N` came from which GG `_repN` digest, and whether
same-index dishes were processed as blocks.
