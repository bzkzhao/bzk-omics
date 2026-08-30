# ADR-0028 — The anchor's curation record is one supersession, and two of its four defects are not defects

| | |
|---|---|
| Status | Proposed |
| Date | 2026-08-30 |
| Supersedes | — |
| Superseded by | — |

## Scope

Decides the four standing defects in `data/curation/curation_PXD018299.json` as one question.
**This record decides and does not execute:** no file under `data/curation/` is edited, no id moves,
no graph is written, no rebuild is run. Every figure below was measured by loading the record
through `bzk/curation/loader.py` and diffing in-memory copies.

**An un-populated container is sufficient for that measurement, and this is why.** The loader reads
`data/curation/curation_PXD018299.json` and mints nodes and edges from it alone; `raw/` supplies
site tables and `graph.kuzu/` supplies a store, and neither is consulted. Ids are content-derived
(ADR-0020), so the figures are a function of the record and the identity map, not of anything on
disk.

## The four defects, and what each costs

Measured per defect against the same baseline: the record loads to **16 nodes** — 1 `Project`,
1 `Experiment`, 1 `Dataset`, 1 `Analysis`, 12 `Sample` — and **38 edges**.

Both figures are set differences. *Ids moved* is the baseline `(label, id)` set minus the mutated
one; *edges re-keyed* is the baseline `(type, from, to)` set minus the mutated one. **A `Sample`
count is not a `Sample`-ids-moved count**: there are twelve `Sample` nodes throughout, and six of
their ids move under defect 3.

| Defect | ids moved / 16 | edges re-keyed / 38 | which nodes, which edges |
|---|---|---|---|
| **1 — `basis`** | **1** | **13** | the `Analysis`; 12 `SAMPLE_GENERATED_BY` (target) + 1 `USED` (source) |
| **2 — the twelve `mapping` keys** | **0** | **0** | none — the key becomes `Sample.label`, which §3 l.115 lists as excluded |
| **3 — `timepoint_h: 48`** | **6** | **18** | six `Sample`s; 6 `PERFORMED_ON` + 6 `PRODUCED` + 6 `SAMPLE_GENERATED_BY` |
| **4 — the mixed `rationale`** | **0** | **0** | none — §3 l.120 lists `rationale` as excluded on `Analysis` |
| **all four together** | **7** | **25** | the `Analysis` and six `Sample`s |

**The combined edge figure is not the sum of the parts and the ids are.** 1 + 0 + 6 + 0 = 7 ids,
and the two moving sets are disjoint. The edge parts sum to **31** against a union of **25**: the
six treated samples' `SAMPLE_GENERATED_BY` edges are re-keyed on their **target** by defect 1 and on
their **source** by defect 3, so six edges appear in both parts and once in the union.

## ADR-0026's costing is correct as scoped, and is not the four-item figure

ADR-0026 l.278 reads *"Exactly one node id moves, of sixteen"* and l.282 *"Thirteen edges of
thirty-eight are re-keyed"*. **Both are correct**, and re-measuring the `basis` substitution alone
reproduces them exactly: 1 of 16, and 13 of 38 as 12 `SAMPLE_GENERATED_BY` plus 1 `USED`.

**The scope is stated in the record itself**, at l.279–280: *"`Sample` is anchored on `("Experiment",
"PERFORMED_ON")`, not on the curation `Analysis`, so no sample id is a function of **the basis**."*
That sentence is true and it is about one substitution.

**So the figures are right about defect 1 and would be wrong if reused for the four**, where the
answer is 7 and 25. **Being right about one substitution and reused for four is a different fact
from being wrong**, and ADR-0026 is `Accepted` and append-only — nothing there needs correcting, and
nothing there is corrected. What is recorded is that its numbers do not generalise, which its own
scope sentence already implies and nobody had tested.

## The verdicts

### Defect 1 — `basis` is `publication_methods`. Verdict (a): the record is wrong

ADR-0026's R2 records the weakest link, and the methods walk at `88198e3` measured the composition
directly: the BJC methods section names no column, and `181212`, `.raw`, `raw file` and
`HAP1_USP18KO` all return zero hits in the paper. **The column-token reading is load-bearing and the
paper is not**, so under R2 the value is `filename_inference`.

**Decided: `basis` becomes `filename_inference`, `confidence` stays `inferred`.** Both values carry
`inferred` in §5.3, so the loader's basis/confidence pairing check is satisfied and I8's labelling
obligation is unchanged in strength — what changes is the string a reader is pointed at.

### Defect 2 — the twelve `mapping` keys. Verdict (b): the standing description is wrong

**The keys are read.** `bzk/adapters/maxquant_sites.py` l.122–125 registers both `"Intensity "` and
`"Ratio mod/base "` in `QUANTITY_COLUMNS`, and l.140–147 strips whichever prefix matches to recover
the run label. **Verified against the source rather than taken from the report that raised it.**

**What is true is narrower and is about a consumer, not the record.**
`bzk/sources/pxd018299_differential.py` l.133 builds `f"Intensity {arm}_{i}"` and never consults the
record's choice. So the record and the adapter agree; the differential diverges from both.

**Decided: the record needs no change.** The contradiction is real and lives in
`pxd018299_differential.py`, which is code and outside a curation ADR. **A fix aimed at the record's
keys would be aimed at nothing** — it moves no id, satisfies no consumer, and would leave the
divergence exactly where it is.

### Defect 3 — `timepoint_h: 48`. Verdict (c): the sources do not settle it

**Four dispositions, and every one is blocked.**

**(i) Drop it.** Forbidden, and not by cost. §3 l.146 classifies `timepoint_h`'s absence as
*determined* by `treatment` — *"NULL where `treatment = 'none'`"*. The six entries carrying 48 are
the **treated** arms (`treatment = 'IFN-alpha2b_1000U_per_mL'`), so a null there is **contingent**,
which ADR-0021 refuses. Dropping it would produce a record that says when it was written rather than
what the sample is.

**(ii) Move `basis` to a value that reaches a figure legend.** §5.3's enum is closed at five values
and **none of them reaches one**. `publication_methods` is the methods section *"including a
supplementary file the methods cite for the design"* — widened to exactly that by ADR-0026 and no
further. A figure legend is neither a methods section nor a cited supplementary file.

**(iii) Record that field's basis separately.** §5.3 gives one `basis` per curation `Analysis`.
There is no per-field basis, and adding one is a DDL change.

**(iv) Widen §5.3 to reach a paper's figure legends.** Available in principle and **not available
here**: ADR-0026 is `Accepted` and append-only, so its narrowing is changed only by a superseding
record, which this is not.

**So what §5.3 licenses is nothing that fits.** The value 48 is correct — Fig. 1f states it — and
there is no basis in the closed enum that reaches where it came from. **Decided: the value stays,
the gap is recorded, and this ADR does not invent a disposition to avoid saying so.** It moves no id
under this decision, and its 6-and-18 figure is what disposition (i) *would* have cost had it been
available.

**Not chosen for cheapness.** (c) is the disposition that moves fewest ids, and that is not its
ground — (i) is blocked by §3, (ii) and (iii) by a closed enum and a DDL boundary, and (iv) by an
append-only record. **Cheapness of supersession is not a ground, and if (i) had been available its
six moved ids would not have counted against it.**

### Defect 4 — the mixed `rationale`. Verdict (a): the record is wrong

The field opens *"Design taken from the methods section of Pinto-Fernandez et al."* and closes with
*"the raw 'Intensity' columns … should not be used for this contrast"* — an analytical instruction
with **no source in that methods section**, measured at `88198e3`. Nothing marks the change of
footing.

**Decided: a curation `rationale` marks which of its claims come from the record's `basis` and which
are the curator's own judgement.** The rewrite attributes per clause. It moves no id, `rationale`
being excluded on `Analysis` at §3 l.120.

## The shape: one supersession, and the measurement is what makes it one

**The four are one question, and the reason is I6 rather than convenience.**

Only defect 1 mints a new `Analysis` id. Defect 4 corrects a **non-identifying** field on **the same
node**, so it changes nothing about that node's identity — and §5.3 states *"Curation nodes are
immutable under I6"*, so a correction is a supersession and never an edit. **A `rationale` fix
landing alone would therefore have to mutate an immutable node in place without minting a new one,
which I6 forbids and no mechanism in this repository supports.** It is not expressible on its own.

**So defect 4 can only travel on the node defect 1 mints.** That is what makes them one supersession
rather than four items filed together.

**Defects 2 and 3 ride nothing**, and this follows from their verdicts rather than being asserted:
(b) changes no record, and (c) changes no record. Neither is separable because neither is separate —
they are decided and not executed.

**What breaks if split:** defect 4 alone is inexpressible, as above. Defect 1 alone is expressible
and would land a new node still carrying the mixed `rationale`, which is a worse state than either
end — the basis would then be honest while the prose beneath it still attributed itself to a paper.

## The literals, enumerated over the whole repository

Every moved id was grepped for across the tree, excluding `.git`, `.venv` and `__pycache__` —
**not the three that were expected**.

| File | Carries | Verdict |
|---|---|---|
| `tests/fixtures/pxd018299_curation_ids.json` | the `analysis` id **and all twelve `samples` ids** | **a pin; moves** — the analysis under defect 1, six samples had defect 3 been executed |
| `HANDOFF.md` | the `Analysis` id row | **a pin; moves.** The `Sample` (WT_1) and (WT_2) rows beside it **do not** — both are untreated arms |
| `tests/test_perseus.py` | `curation_analysis_id` hard-coded | **a pin; moves** |
| `decisions/0026-basis-classifies-warrants.md` | both the old and the new `Analysis` id | **a record of the move, not a pin on it** — it states the pair as a costing, and it is `Accepted` and append-only |

**Four files, and there is no fifth.** The six `Sample` ids appear in the fixture and nowhere else.

## Implied changes, described and not made

1. **The supersession itself** — a new curation `Analysis` carrying `basis = 'filename_inference'`
   and the re-attributed `rationale`, with the old node retracted under I6 and the retraction
   propagating to every derived result.
2. **The three pins move in the same commit as that supersession**, and
   `tests/fixtures/pxd018299_curation_ids.json`'s own note requires the move be explained rather
   than regenerated to make a red test green.
3. **`bzk/sources/pxd018299_differential.py` reads the record's quantity choice** instead of building
   `Intensity` names itself — defect 2's real content, and a code change outside this record.
4. **A superseding ADR if §5.3 is ever to reach a figure legend** — defect 3's disposition (iv),
   named so the gap has a route rather than only a description.
5. **ADR-0026's R2 guard**, whose trigger is item 1 above: a curation record whose `rationale` names
   a column-token reading carries no basis stronger than `filename_inference`. It is red against the
   tree until the supersession lands, which is why ADR-0026 deferred it and why it is still deferred.

## The class

**The class this record closes is: a curation record whose stated `basis` does not reach every claim
the record makes.** All three of its live instances are here — the basis naming a paper where column
tokens did the work, the timepoint sourced from a figure legend, and the `rationale` attributing its
whole contents to one source.

**It is partly machine-checkable, the checkable half is already specified, and it is not closed.**
ADR-0026 wrote the assertion — a record whose `rationale` names a column-token reading carries no
basis stronger than `filename_inference` — and recorded that it would be red from birth against an
un-superseded record. **This decision is that guard's trigger, and executing it is what makes the
guard writable.** The half that is not machine-checkable is defect 3's: no assertion can tell that a
value came from a figure legend, because the record does not record where its fields came from —
which is disposition (iii), and a DDL change.

**So: the class is named, one instance is decided, one is ruled unsettleable, and the guard stays
open with its trigger stated rather than as a note a reader must remember.**
