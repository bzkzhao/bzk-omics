# Report — verify and land the lysate ADR

**Run at:** 2026-09-19 · **Opened at:** `0bd9653` · **Landed as:** `decisions/0035-a-perturbation-applied-after-the-sample-ends.md` · **Commit:** `3b7e969`, pushed

---

## R0: state at the open

```
0bd9653 2026-09-18 17:51:18 +0100 notes: report turn 07, and track its prompt
?? data/frame/200            ?? data/frame/probe.py
?? data/frame/probe_v2.json  ?? data/frame/probe_v3.json
?? notes/ADR-lysate-draft.md
?? notes/prompts/08-land-the-lysate-adr.md
?? notes/prompts/09-curate-and-ingest-PXD026748.md
?? notes/reports/last.md     ?? notes/reports/run.md

git log --oneline origin/main..HEAD   →   (empty)
```

**HEAD was pushed**, and `main` was level with `origin/main`.

---

## Receipt checks

### R1: the `Sample` DDL, `ONTOLOGY.md:384-398`, in full

```
CREATE NODE TABLE Sample(
  id STRING, label STRING,
  source_type STRING,           -- 'cell_line' | 'tumour_tissue' | 'primary_cell'
  cell_line STRING,             -- NULL for tissue
  organism_taxid INT64,         -- REQUIRED. Mouse and human coexist in one graph.
  model_system STRING,          -- e.g. '4T1 BALB/c subcutaneous'; NULL in vitro
  genotype STRING,              -- e.g. 'USP18-/-', 'USP18 C64R/C65R'
  treatment STRING,             -- e.g. 'IFN-alpha2b 10 U/mL'; 'none' for an untreated arm
  timepoint_h DOUBLE,           -- hours SINCE TREATMENT, not hours in culture.
                                -- NULL where treatment = 'none': an untreated arm has no
                                -- elapsed-since-treatment, so the value does not exist rather
                                -- than being unknown (§3 absence table).
  replicate INT64,
  replicate_type STRING,        -- 'biological' | 'technical'
  PRIMARY KEY (id));
```

**`replicate` carries no comment. It is not the only field without one:** `id STRING, label STRING` carry none either. **Of the nine descriptive fields, `replicate` is the only one uncommented.** The `id` opening line is uncommented on most node tables in the DDL.

### R2: the anchor's replicate indices across treatment

From `data/curation/curation_PXD018299.json` `mapping`, two entries that differ only in `treatment`:

```
Ratio mod/base WT_1      {"genotype": "WT", "treatment": "none", "timepoint_h": null, "replicate": 1, "replicate_type": "unspecified", ...}
Ratio mod/base WT_IFN_1  {"genotype": "WT", "treatment": "IFN-alpha2b_1000U_per_mL", "timepoint_h": 48, "replicate": 1, "replicate_type": "unspecified", ...}
```

**They share the index**: `replicate: 1` on both. The same holds for every genotype × replicate pair, because indices run 1–3 inside each of the four condition groups.

**The record does not say whether a shared index means shared material.** Its `unresolved` list:

> Replicate type (biological vs technical) is not explicitly stated in the methods for the GlyGly peptidome. Recorded as 'unspecified' pending author correspondence. This affects how the variance estimate in any differential test should be interpreted.

### R3: the scope of §3's absence classification

`ONTOLOGY.md:134`:

> **Absence must be determined or curated, never contingent.** An identifying field may be null — but only when something outside the moment of ingest fixes that null.

The table at l.142–162 classifies `(node, field)` pairs, each a real identifying column, by the kind of its null.

### R4: the next free number

`decisions/` ran `0001`–`0017` and `0019`–`0034`, with `0018` reserved-and-unwritten in the Queued table. **N = 0035.**

### R5: grep for *aliquot*, *lysate*, *post-lysis*, *ex vivo*

```
grep -rn "aliquot\|lysate\|post-lysis\|ex vivo" ONTOLOGY.md   →   no output, exit 1
```

The draft's claim is **confirmed**: the grep returns nothing.

---

## Expectations

| # | expectation | result |
|---|---|---|
| **E1** | `replicate` has no DDL comment and is the only `Sample` field without one | **Half held.** It has no comment. It is **not** the only uncommented field, because `id` and `label` have none. It is the only uncommented *descriptive* field |
| **E2** | In PXD018299 the replicate index does **not** identify shared source material across treatments: separate wells, separate seeding | **Not established. The repository cannot settle it either way** |
| **E3** | §3's table classifies absent values on fields that exist, not absent relations | **Held, and sharper than stated.** §3 governs absent values on **identifying** fields |

### E2, the load-bearing one, in full

The prompt's stop condition was: *if the anchor DOES pair by replicate index, STOP.* **That condition was not met.** Nothing shows the anchor pairs. **But E2's positive claim was not met either.** Nothing in the repository says the anchor's replicates were separate wells or were seeded separately:

- The curation record shares the index across treatments, is silent on material, and declares the replicate structure unknown pending correspondence.
- A repository-wide search for *seeded*, *separate well*, *separately seeded*, *same culture* and *paired* found nothing bearing on it. The only near hit is `ARCHITECTURE.md:328`, where the proteome is split from the digest. That concerns the proteome–GlyGly pairing, not cross-treatment replicates.

**What I did, and why I did not stop.** The draft's R2 has two parts: a *decision* (the pairing cannot be recovered from `replicate`) and a *ground* (the anchor proves `replicate` is an ordinal). The check disagrees with the ground, so the ground was edited, under *where a check disagrees, the check is right*. The decision survives on a ground that does not need E2. `replicate` has never been given a meaning that includes shared material, and the anchor's own record declares its structure unknown. So reading it as a source identifier fails in both directions:

- **uniformly**, it would make the anchor's `WT_1`/`WT_IFN_1` assert shared material nobody has established;
- **for PXD026748 only**, it overloads one field with two meanings.

That ground is marked in the record as **supplied at landing, not read from the draft**.

**This is the judgement a reviewer should test first.** If the replacement ground is rejected, R2 has no ground at all until the anchor's replicate structure is known.

---

## Corrections made, each with its check

| # | the draft said | the check | the edit |
|---|---|---|---|
| 1 | WT_IFN rep 1 and WT_mock rep 1 *"are separate wells seeded separately"* | E2: the curation record's `mapping` and `unresolved`, plus the repository search | Claim removed, and R2's ground replaced as above, marked as supplied at landing |
| 2 | `replicate` is *"the only field of `Sample`"* without a comment | R1 | Changed to *"the only one of `Sample`'s nine descriptive fields"*, in both the body and *does not settle* |
| 3 | §3 classifies *"absent values on fields that exist"* | R3 | Sharpened to **identifying** fields, and `:134` quoted. This strengthens R3 of the record |
| 4 | *"R3 and R4 both passing"* | `walk/walk_PXD026748.json` `requirements` | R3 is `PASS-provisional`, G1, grade B, with the design from filenames and confidence `inferred` |
| 5 | ADR-0034 *"blocks the Perseus-side analysis and not the search-output ingest"* | `decisions/0034-…md:42-45` | Quoted in ADR-0034's own terms: it withholds *"the columnar half of I11"*, the `Cell`s, for PXD065158. The stage matches and the scope does not |
| 6 | *"`PXD026748` can be ingested now"* | `walk_PXD026748.json` `the_multiplicity_finding`; `ONTOLOGY.md:474-483` | Narrowed to *the lysate question does not block ingest*. The per-multiplicity `quantity` enum item is named as separate and unsettled |

**Two additions that are not corrections:**

- The Context now quotes `WALK-STANDARD` v2's R5 reason in full, because R1 disagrees with its first clause (*"multiplies samples falsely"*) and should say so where a reviewer can see it.
- The filenames claim now cites the one filename the repository records, `Gly-Gly-KO_mut_rep1`, instead of the draft's two, which are not recorded here.

**Held without edit:**

- the DDL span;
- `treatment`'s and `timepoint_h`'s comments, verbatim;
- the R5 grep;
- R5's premise that a new field would be identifying, because every descriptive `Sample` field is (`ONTOLOGY.md:115`);
- `unresolved` as R4's home;
- 2 × 2 × 3 = 12 GG runs.

**One slip of my own, caught before commit.** A first draft of the correction said `id`/`label` were *"the uncommented opening pair on five of six node tables"*. That count came from a grep that saw only six `id STRING, label STRING` lines out of roughly twenty node tables. It was replaced with the measured statement: the `id` line is uncommented on most node tables, 14 of the 20 an `awk` pass read. The same restructuring had also dropped the draft's *"cleanest claim table"* phrase. It was reinstated and attributed to the draft, so the record's "left as written" list is true.

---

## Landing

- **File:** `decisions/0035-a-perturbation-applied-after-the-sample-ends.md`
- **Status row:** `| Status | Proposed |`, plain. The draft's `**Proposed**` was unbolded, since `tests/test_decision_index.py` parses the literal.
- **`notes/ADR-lysate-draft.md` deleted.** It was never tracked, so git records a plain add rather than the rename ADR-0034 got.
- **`decisions/README.md`** has a Written row for 0035.
- **Pins:** `EXPECTED_FILES` 33→34, `EXPECTED_WRITTEN_ROWS` 33→34, `Proposed` 10→11. Accepted (20) and Superseded (3) are unchanged.
- **`pytest tests/test_decision_index.py` → 9 passed.** The suite was not run. `ruff` and `mypy` were not run; the only code-adjacent change is three integer pins in a test module.
- **Commit `3b7e969`**, pushed: `0bd9653..3b7e969`.

**Nothing out of scope was touched:**

- no field added to `Sample`;
- `ONTOLOGY.md` not edited, including `replicate`'s missing comment;
- nothing ingested;
- no curation record written;
- ADR-0033 and ADR-0034 cited, not edited.

---

## Bearing on prompt 09, noted and not acted on

Prompt 09 is *curate and ingest PXD026748*. Two items from this turn sit in its path:

1. **The multiplicity finding (correction 6).** The walk record says the publication consumed the expanded site table. The platform's adapter reads `intensity_multiplicity_summed` by default, so an ingest is mechanically possible. What does not exist is a `quantity` value for the publication's own per-multiplicity analysis, and `quantity` is identifying. How the curation record declares that analysis is 09's question.
2. **R4 of this record assigns the pairing to the curation record's `unresolved`.** That is the first place 09 must write it.

---

## Could not verify either way

- **The anchor's actual replicate structure**, whether wells, seeding or shared culture. It is not in the repository, and the curation record defers it to author correspondence. This is the fact the draft's original ground needed.
- **The deposit's WT filenames** `Gly-Gly-WT_rep1` and `Gly-Gly-WT_mut_rep1`. Only `Gly-Gly-KO_mut_rep1` is recorded here.
- **The draft's judgements**: *"the cleanest claim table of the four candidates"*, *"the second such instance found this week"*, and *"the taxonomy has no class for it"*. They are left as the reviewer wrote them and listed in the record as unverified.
