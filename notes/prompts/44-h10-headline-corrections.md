# Prompt 44 — ADR-0041's Consequences: H10's headline restored in `walk/`, FINDINGS §5 and `bzk.audit` stage 6

**Repository:** `main` at the commit adding this prompt. Line references were measured at `248dd6d`.

**What this is.** ADR-0041 (`decisions/0041-a-registered-headline-moves-only-through-hypothesis.md`,
`Accepted` at `248dd6d`) decided that H10's headline stays at the registered denominator: 27.8% (209
of 751). 26.5% (210 of 791) is reported over all testable claims and is never the headline. Its
*Consequences* list the edits that follow. This prompt makes items 2–7. The other three need nothing
from the build:
- item 1: HYPOTHESIS does not change;
- item 8: execution records are not edited;
- item 9: the reviewer records W3's closure.

ADR-0041 is `Accepted` and therefore append-only (`decisions/README.md`). **Do not edit it.** If the
build finds it wrong, raise it.

**The house form for a correction** is the one `b960c9a` set for reviewer defect W1:
- the dated CHECKS document is **not rewritten**, and carries a dated banner at the top;
- a `walk/CORRECTION-*.md` document is the record;
- `walk/FINDINGS.md` is edited directly.

Follow `walk/CHECKS-two-route-recovery.md:1-14` (the banner) and
`walk/CORRECTION-PXD018299-two-route-independence.md` (the record, including its closing table of
every home and how each was handled).

**Dates.** The record, both banners and the floor comment carry the build day.

---

## 0. Receipt check — answer, then stop and wait

Quote from the file or from git, never from this prompt. **Stop on any mismatch.**

**(a) State.**
- `git log --oneline -2` shows this prompt's commit with `248dd6d` beneath it, and
  `git status --short` is empty.
- After `uv sync --frozen`, `pytest -q` reads 1292 passed / 15 skipped.
- `sweep()` (`tests/test_tautology_sweep.py`) reads 60 modules / 2721 asserts, `PINNED` 353,
  new 0 / gone 0. The floor at `:2405` reads 2721.
- ADR-0041's header reads `| Status | Accepted |`.

**(b) The lines this prompt changes or cites.** Quote each:

| # | where | expected |
|---|---|---|
| R1 | `walk/FINDINGS.md:102-111` | §5's heading, its lead sentence (`:104-105`), and the three rows: `210 of 791 (26.5%)`, `38.3%`, `13.7%` |
| R2 | `walk/FINDINGS.md:124-125` | "about a quarter of its threshold-region membership" |
| R3 | `walk/CHECKS-collateral-and-pkm.md:1-6`, `:13`, `:15-17`, `:24-25`, `:29-30` | the title and run line; "The denominator was wrong, and the collateral channel is narrow"; round 12's mechanism; 209 of 751 and "all published claims … 210 of 791"; "26.5% is the figure with the right denominator; 27.8% is superseded as the headline" |
| R4 | `walk/CHECKS-census.md:1-5`, `:62-66`, `:70`, `:112`, `:119-122` | the title and run line; "published claims inside it" over `of 791` cells; "0.6% of all published claims"; the section heading over `:119`; "26.5% of published claims"; "remains the registered result and the answer to H10" |
| R5 | `walk/CHECKS-ceiling-survives.md:70`; `walk/CHECKS-draws-and-threshold.md:15`, `:19` | 13.7% (103 of 751); the header "unstable, of claims with an imputed value"; 38.3% at 100 draws |
| R6 | `walk/PREREG-PXD018299-H10.md:179-181`, `:186-187`; `HYPOTHESIS.md:43-46`, `:904-907`, `:1018` | the registered primary; "Reported, never the headline"; 27.8% (209 of 751) under v10; the primary readout; 751 of 791 testable, 798 published |
| R7 | `bzk/audit.py:90-98`, `:99-110` | `RECEIPT_MAP`'s comment ("in the order those sections print them"), and its first entry: `210 of 791`, describes "share of all published claims whose support changes across draws, documented rule, 20 draws" |
| R8 | `bzk/audit.py:1069-1072` | "The registered estimand, not a headline: …" |
| R9 | `bzk/audit.py:1089-1106` | stage 6's hand-written item, including "'over_all_claims' is over all published claims, the population of the section 5 headline" |
| R10 | `tests/test_audit.py:1200-1201`, `:1552-1561` | the real-repository receipt test; the note test with `len(six.not_automated) == 9` |
| R11 | `notes/logs/round13.txt:6-7` | 209 of 751 (27.8%); 210 of 791 (26.5%) |
| R12 | `walk/CHECKS-two-route-recovery.md:1-14`; `walk/CORRECTION-PXD018299-two-route-independence.md:1-12` | the banner form and the CORRECTION form |
| R13 | `tests/test_maxquant_sites_composition.py:223-272`; `tests/test_tautology_sweep.py:2410-2417` | the `CAUGHT` / `UNCAUGHT` pattern; the sweep's rule for an unclassified match |

**(c) Absences.**
- `grep -c "209 of 751" walk/FINDINGS.md` and `grep -c "209 of 751" bzk/audit.py` both return 0.
- `git grep -n -i "all published claims" -- walk bzk` returns exactly `bzk/audit.py:103`,
  `walk/CHECKS-census.md:70` and `walk/CHECKS-collateral-and-pkm.md:25`.
- `walk/CORRECTION-PXD018299-H10-headline.md` does not exist.

**Do not start §1 until bzk replies.**

---

## 1. Build

### 1.1 The CORRECTION record

Create `walk/CORRECTION-PXD018299-H10-headline.md` in R12's form. It records ADR-0041's
*Consequences* items 2, 3 and 6, and cites ADR-0041 for the decision rather than restating it.

**Line numbers.** This section's references into the two CHECKS documents were measured at
`248dd6d`, before the banners. In the record, give each at its post-banner line, and state each
document's shift once, so that ADR-0041's and the reviewer records' pre-banner references can be
mapped. References into `walk/FINDINGS.md` and `bzk/audit.py` are edited by this build too: give
those by name (the row, the entry, the item), or state them as at `248dd6d`.

The record holds these parts.

**What is withdrawn**, in the vocabulary of `walk/CHECKS-membership-and-corrections.md:8-13`:
- **`walk/CHECKS-collateral-and-pkm.md:29-30`'s claim that the headline changed** ("27.8% is
  superseded as the headline").
  - **Withdrawn: false as stated, and the reasoning was defective.** The reasoning took an analytic
    argument for a change of status. `walk/PREREG-PXD018299-H10.md:186-187` lists the all-claims
    share as "Reported, never the headline", and no HYPOTHESIS version made the change.
  - v10 restated the rule, and with it the level; not the denominator (`HYPOTHESIS.md:43-46`). No
    version has been cut since (ADR-0041's review, finding D). Under ADR-0041 (a), only such a
    version moves a registered headline.
- **`walk/CHECKS-census.md:121-122`'s "remains the registered result and the answer to H10"**
  (the sentence starts at `:121`; the phrase is on `:122`), said of 26.5%.
  - **Withdrawn: false as stated, and the reasoning was defective:** it carried the collateral
    check's status claim forward as a registration (ADR-0041 *Context*: "Two documents follow
    it"). 26.5% was never registered as H10's result.
  - The all-claims share is registered only as a reported readout, never the headline
    (`walk/PREREG-PXD018299-H10.md:186-187`).

**Why not "superseded".** That word classifies a computation under a disfavoured choice. Whether
later evidence disfavours the 751 is the argument's own question, which ADR-0041 (b) declines without
answering.

**Successor**, to both withdrawals: 27.8% (209 of 751), H10's level as `HYPOTHESIS.md:43-46`
states it.

**What survives.**
- **The argument at `walk/CHECKS-collateral-and-pkm.md:15-17`**: the 40 fully measured claims are
  exposed through the shared threshold. The argument is that document's, run 2026-09-22; this record
  does not make it. It **restates** the argument as a proposal in the form of ADR-0041's reading of
  (a), carrying all six elements:
  1. it names the registered headline it would move, citing the lines that register it
     (`walk/PREREG-PXD018299-H10.md:179-181`, `HYPOTHESIS.md:904-907`, and the level at
     `HYPOTHESIS.md:43-46`);
  2. it states its reason, citing the evidence: `walk/CHECKS-collateral-and-pkm.md:15-17` and
     `notes/logs/round13.txt:6-7`;
  3. it gives the proposed figure, 210 of 791;
  4. it states the direction, down from the registered 27.8%;
  5. it states that it was made after the data were seen;
  6. it is worded as "proposed", and never calls 27.8% "superseded".

  **It is declined for the current headline by ADR-0041 (b).** A later HYPOTHESIS version may
  still take it up.
- **The `:13` heading's first clause** ("The denominator was wrong"). ADR-0041 item 2 says the
  heading "makes `:29-30`'s status claim, and is restated with it" (give `:29-30`'s post-banner
  lines beside the quote); quote that phrase in the record rather than paraphrasing it, and state
  that ADR-0041 lists the heading under *What survives*, so this record reads it as restated with
  the argument, not withdrawn. The first clause is the argument's conclusion. It is **restated with
  the argument**, not withdrawn: as part of the proposal above, the denominator is argued to be
  wrong. Its second clause ("the collateral channel is narrow") is unaffected.
- **`:29`'s first clause** ("26.5% is the figure with the right denominator") is the same
  conclusion, handled the same way: restated with the proposal, not withdrawn. Its second clause,
  "27.8% is superseded as the headline", is the withdrawn status claim; "kept as the conditional
  rate" is unaffected.
- **Every figure in both documents.** No figure moves. 26.5% (210 of 791) stands as the
  all-testable-claims figure.
- **`walk/CHECKS-census.md:121`'s point that the census should lead.** Which finding leads is
  outside ADR-0041's scope.

**The label error, a separate class.** The 791 are the testable claims; 798 are published
(`HYPOTHESIS.md:1018`).
- **The membership rule** (required by ADR-0041's review, finding I): an instance is a label that
  calls the 791 "published claims": it says "all published claims", or it names "published claims"
  as the population of a figure over the 791, shown by `of 791` in its row or in the cells under its
  column header, by a printed count of the 791 itself, or by a share its home computes over the 791
  (`26.5%`). Outside the rule: a label whose qualifier makes the 791 correct ("published claims in
  the matrix"), and a label on a subset that gives no figure over the 791 ("fully measured published
  claims | 40", "39 published claims with all three wild-type cells", "the 118 published claims the
  documented rule does not call").
- **The seven instances** ADR-0041 item 6 names, each with where it is corrected:
  - `walk/FINDINGS.md:109`: edited here (§1.3);
  - `bzk/audit.py:103` and `:1096-1097`: edited here (§1.4);
  - `walk/CHECKS-collateral-and-pkm.md:25` and `walk/CHECKS-census.md:62`, `:70`, `:119`: named in
    the banners (§1.2). The dated text is not rewritten.
- **Two more, missed by ADR-0041**, in RESULT documents, which this prompt does not edit (§2):
  `walk/RESULT-PXD018299-H10-attempt3.md:126-127` ("About 92% of published claims are recovered …:
  725 of 791") and `walk/RESULT-PXD018299-H10-attempt2.md:91` ("about 92% of the published claims
  are recovered", a share of the "supported of 791" column at `:84`). Both are listed, not edited.
  ADR-0041 item 6's "The enumeration is complete at `aec062e`" is therefore false for `walk/`. The
  record says so; the ADR is append-only and is not edited (raise it, §3).

**A closing table, in R12's form,** with the homes of the withdrawn claims, of the restated
argument, and of the label class, and how each was handled. Each row's handled cell names which of
the three kinds the home is, or each kind where a line or range is more than one (for example
collateral `:29-30`, FINDINGS §5 row 1, and stage 6's item); one row, not overlapping rows. For
`HYPOTHESIS.md`, the PREREG documents, ADR-0041, and the `notes/prompts/` and `notes/REVIEWER-*`
row, which hold the registered figure, the decision, or
quotations of all three rather than a home, the cell says so instead, and a sentence before the
table says that those rows are context. One row per home line or contiguous range, with its
wording, as R12's table does; `notes/prompts/` and `notes/REVIEWER-*` take one row together, and
ADR-0041 and `HYPOTHESIS.md` take one row each, and the PREREG documents one row together.

**Its heading** reads "Every home of the withdrawn claims and the restated argument, the label
class's homes in `walk/` and `bzk/`, and its execution-record homes as far as searched, and how each
was handled". Do not head it "Every home … of the label class": the Completeness paragraph below
does not claim every execution-record instance.

Its rows cover:
- the two CHECKS documents: banner only (§1.2);
- `walk/FINDINGS.md` §5: rows replaced (§1.3);
- `bzk/audit.py`'s `RECEIPT_MAP` and stage 6's item: edited (§1.4);
- the comment above `registered_primary`: a home of the withdrawn status claim ("The registered
  estimand, not a headline", reversed by ADR-0041 (b)); edited (§1.4);
- ADR-0041: unchanged, append-only;
- `HYPOTHESIS.md` and the PREREG documents: unchanged, correct as they stand;
- the two RESULT lines above: listed, not edited (label class);
- these execution records, listed and not edited:
  - `notes/logs/round13.txt:1` (restated argument), `:7` (label class);
  - `notes/logs/round14.txt:13-15` (label class);
  - `notes/scripts/diagnose_round13.py:10-12` and `:119` (restated argument), `:131-132` (label
    class);
  - `notes/scripts/diagnose_round14.py:19`, `:156-157` (label class);
  - `notes/scripts/diagnose_round10.py:73` (label class; no committed log);
- `notes/prompts/` and `notes/REVIEWER-*`: dated records, not edited (ADR-0041 V8's classes).

  `notes/scripts/diagnose_round9.py:69`'s "published claims in the matrix" is outside the rule: the
  qualifier names the 791 correctly. `notes/reports/REVIEW-seed-lability.md:92` ("The denominator is
  wrong by one level") argues for the 751, so it is not a home of the withdrawn claim.
  `walk/CHECKS-ceiling-and-floor.md:44` ("the 118 published claims the documented rule does not
  call"), `walk/CHECKS-membership-and-corrections.md:52-53` and `notes/scripts/diagnose_round9.py:14`
  ("misses 119 published claims") are outside the rule: each counts a subset and gives no figure
  over the 791.

  `notes/logs/round14.txt:13-15`, `diagnose_round14.py:156-157`, `diagnose_round10.py:73` and
  `diagnose_round13.py:10-12` were missed by ADR-0041's V8. Its `of 791` query did not cover `*.txt`
  and cannot see a 791 that an f-string computes. Its `all published claims` query needs "all". Its
  `denominator was wrong` query differs from "THE DENOMINATOR IS WRONG" in tense as well as case,
  so it misses even with `-i`. The two RESULT lines were missed too: attempt 3's `of 791` is on the
  line after its label, and attempt 2's line gives a percentage with no 791.

  **Completeness.** The list is exhaustive for the withdrawn claims and the restated argument. For
  the label class it is exhaustive for `walk/` and `bzk/`. The record names the two searches this
  build ran there, both case-insensitive and both run before any edit (on the prompt's commit,
  identical to `248dd6d` in `walk/` and `bzk/`), and says so: run after the edits, they also hit the
  banners' and the record's own quotations. They are: every line matching `published claims?`, and
  every line whose last word, ignoring trailing quotes, punctuation and spaces, is "published" and
  whose next line's first word, ignoring indentation, quotes and markup, is "claim" or "claims".
  Every hit is classified under the rule (the record lists only the instances and the exclusions
  named above; the rest are classified in the build report). At `248dd6d` the first search finds the
  two RESULT lines ADR-0041 missed, and the second finds stage 6's item in `bzk/audit.py`
  (`:1096-1097` as at `248dd6d`). For execution records, the label class is listed as far as the
  same two searches, and `-i` searches for "denominator" and "26.5%", find over `notes/logs/` and
  `notes/scripts/`, and the record says so rather than claiming every instance. Execution records
  are not edited either way (ADR-0041 item 8), so a later find adds a row and changes nothing else.

**Prompt pointers.** The "(§1.2)"-style references in this section point into this prompt. Do not
copy them into the record; name the document or edit instead.

**What does not change.** HYPOTHESIS, every registered rule, threshold and verdict, and every
execution record.

### 1.2 Two banners

Add a dated banner at the top of each of `walk/CHECKS-collateral-and-pkm.md` and
`walk/CHECKS-census.md`, in R12's banner form: a `> **Correction (<date>).**` blockquote after the
title. It names:
- what is withdrawn;
- what is unaffected;
- the document's instances of the label error under §1.1's rule (collateral: one; census:
  three), **by their wording, not by line**, as R12's banner
  names its claims;
- for the collateral check, that the §1 heading's first clause ("The denominator was wrong") and
  "26.5% is the figure with the right denominator" are restated in the record as a proposal declined
  for the current headline, not withdrawn; the heading's second clause and "kept as the conditional
  rate" are unaffected;
- for the census, that the "selection instability" row of the table under "What this changes about
  the headline" gives the all-claims share, which is not H10's result;
- a pointer to `walk/CORRECTION-PXD018299-H10-headline.md`.

**Each banner names no `diagnose_round*.py` script.** Both documents are `RECEIPT_MAP` homes. The
receipt checker's direction 3 compares the scripts an entry names with **every** script name in its
home (`tests/test_audit.py`, `check_receipts`), so a banner naming another round breaks every entry
homed in that document: four in the collateral check once §1.4's entry lands (three at `248dd6d`),
one in the census.
Do not edit either document below its banner.

**Anchors.** Neither banner contains, quoted or not, a `RECEIPT_MAP` home anchor of its document,
and gives those figures by percentage alone (27.8%, 26.5%). The anchors in the collateral check are
"210 of 791", "of those, q range spans the 0.01 cut", "median 0.0015", and, once §1.4 lands,
"209 of 751". In the census it is "0.1% to 13%". The home check is a raw substring test
(`tests/test_audit.py`, `check_receipts`), so a banner alone would satisfy it.

**Order.** Write both banners before the record, so that the record's post-banner line numbers are
read off the files rather than computed.

### 1.3 `walk/FINDINGS.md` §5

Replace the three rows at `:109-111` with these four, in this order:

```
| claims with an imputed value whose support changes across draws | **209 of 751 (27.8%)** |
| the same at 100 draws | 38.3% of 751 |
| floor across the whole FDR rule family, at 20 draws | 13.7% (103 of 751) |
| of all 791 testable claims, those whose support changes across draws (reported beside row 1, never in its place) | 210 of 791 (26.5%) |
```

- Row 1 is H10's headline (ADR-0041 (b)).
- Row 2's "the same" now refers to row 1's population, and "of 751" shows it
  (`walk/CHECKS-draws-and-threshold.md:15`). Its home gives no numerator, so none is computed.
- Row 3's denominator comes from `walk/CHECKS-ceiling-survives.md:70`.
- Row 4 is the all-claims share. It reads "beside row 1" but sits below row 3, so that row 2's
  "the same" keeps referring to the 751.

The lead sentence (`:104-105`) does not change. Make no other edit to FINDINGS. The "about a
quarter" at `:124-125` (as at `248dd6d`) is out of this prompt's scope. Report it unchanged.

### 1.4 `bzk/audit.py`

**`RECEIPT_MAP`.** Its §5 entries must follow §5's new print order (R7's comment).

1. **A new first entry**, for row 1:
   - section 5, findings anchor `209 of 751`;
   - describes `share of claims with an imputed value whose support changes across draws,
     documented rule, 20 draws`;
   - scripts `("notes/scripts/diagnose_round13.py",)`, `script_anchor` `None`;
   - home `walk/CHECKS-collateral-and-pkm.md`, home anchor `209 of 751`;
   - log `("notes/logs/round13.txt", "209 of 751")`.

   ADR-0041 item 7 and its review (finding E) give the home and log. Round 13's log is the only
   committed log carrying the figure, and the receipt checker refuses a log-less entry whose anchor
   occurs in a log.
2. **The existing `210 of 791` entry moves** to after the `13.7%` entry. Its describes becomes
   `share of all testable claims whose support changes across draws, documented rule, 20 draws`.
   Nothing else in it changes.

**`:1069-1072`** (the comment above `"registered_primary"`). Replace the whole four-line comment with
these five lines:

```
        # The registered estimand and H10's headline population (HYPOTHESIS.md:904-907).
        # walk/PREREG-PXD018299-H10-attempt3.md:81-82 takes the shares over claims whose row
        # carries an imputed value, and walk/PREREG-PXD018299-H10.md:186-187 puts the all-claims
        # share under "Reported, never the headline". The fixture marks no primary;
        # `tests/test_audit.py` guards both PREREG lines.
```

The old first line, "not a headline", is the claim ADR-0041 (b) reverses. The attempt-3 citation
stays: it is the subject of the sentence that follows.

**Stage 6's hand-written item (R9).**
- Keep its first sentence unchanged. That sentence is the marker
  `Withdrawn and replaced 2026-11-13: ` followed by the withdrawn clause.
- The date stays: it records the withdrawal of the round 11/12 attribution. The correction this
  prompt makes is recorded in §1.1's document and in the commit.
- Replace everything after the withdrawn clause with this text, written as concatenated string
  literals in the existing item's style:

```
Neither population this stage reports is a section 5 figure, and none of section 5's figures is
reproduced by this fixture. 'conditional_on_imputation', the population the 'registered_primary'
key marks, is over claims with an imputed value: the population of the section 5 headline, so only
the rule separates them. The headline was computed under Perseus's documented FDR rule, and this
stage computes the variant the 'registered_variant' key names. 'over_all_claims' is over all
testable claims, the population of the share section 5 reports alongside the headline and never as
it, and is computed under the same variant. Do not quote either as the headline. The items below
name the instrument behind each section 5 figure.
```

**`check_note`'s docstring** (`tests/test_audit.py`, "What it does not establish"). Its last sentence,
"The `describes` strings' rule and population claims are checked by nothing", becomes false for one
label. Replace it with: "The `describes` strings' rule and population claims are checked by nothing,
except that neither they nor any item of either note may match `PUBLISHED_CLAIMS` ("published
claim" or "published claims" as words, so "unpublished claims" passes; the label guard below)."

### 1.5 Tests

**The pin.** `tests/test_audit.py:1560`: `len(six.not_automated) == 9` becomes `== 10`.

**The label guard.** Add to `tests/test_audit.py`, in R13's `CAUGHT` / `UNCAUGHT` pattern:
- a pattern `PUBLISHED_CLAIMS = re.compile(r"\bpublished claims?\b")`;
- a function `mislabels_791(text: str) -> list[str]`, returning every line of `text` that either:
  - contains `all published claims` (case-sensitive, as `PUBLISHED_CLAIMS` is); or
  - matches `PUBLISHED_CLAIMS` and also matches `\b791\b`.

The `\b` matters: "called-but-unpublished claims" contains "published claims" as a substring, and
must not match.

Place the guard after `test_no_anchor_reaches_the_report`.

**Name the sets `CAUGHT_791` and `UNCAUGHT_791`.** `tests/test_audit.py` already defines `CAUGHT` and
`UNCAUGHT` at `:670` and `:706`, and the handler-rule tests at `:736-745` look them up by name at run
time. Reusing the names fails 11 existing tests.

**`CAUGHT_791`**, one line each, asserted `len(mislabels_791(text)) == 1`:
- `| published claims whose support changes | 210 of 791 |`
- `share of published claims, 5/791`
- `the 791 published claims`
- `and the band holds about 0.6% of all published claims.`
- `798 published claims; 751 of 791 testable`. This is a correct line, the shape of
  `HYPOTHESIS.md:1018`, and the guard's **known false positive**. It is why the guard reads only the
  places below and never HYPOTHESIS.

**`UNCAUGHT_791`**, asserted `mislabels_791(text) == []`. Write each assert on the call itself, never
on a bound name (`found = mislabels_791(text); assert found == []` registers under Pass D). The first
two are correct negatives. The rest are the guard's **measured limits**, mislabels it does not catch:
- `| of all 791 testable claims, those whose support changes across draws (reported beside row 1, never in its place) | 210 of 791 (26.5%) |`
  — the new FINDINGS row 4, verbatim;
- `| called-but-unpublished claims supported in every draw | 9 of 791 |`
- `| band | published claims inside it |` followed on the next line by `| ±0.0015 | 5 of 791 |`. The
  header and the cells are on separate lines.
- `26.5% of published claims change support`. A percentage, with no 791 on the line.
- `'over_all_claims' is over all published` followed on the next line by `claims, the population`.
  The phrase is wrapped across lines.

**Real-repository assertions**, each written `assert not …` and **each in its own test function**,
so a mutation that reddens one cannot hide another (M4 and M6 each redden two of them):
- `mislabels_791` over `walk/FINDINGS.md` returns nothing;
- no `describes` in `audit.RECEIPT_MAP` matches `PUBLISHED_CLAIMS`;
- no item of stage 6's or stage 7's `not_automated`, run on the committed fixture, matches
  `PUBLISHED_CLAIMS`. These are single rendered strings, so the wrapped-line limit does not apply.

**Scope.** The guard covers FINDINGS, `RECEIPT_MAP` and the two notes. The dated CHECKS documents
keep their text under a banner. `HYPOTHESIS.md` uses "published claims" correctly beside 791
figures.

### 1.6 Registration and mutations

**Forecast.**
- `PINNED` stays at 353. The guard's asserts are the R13 forms: `len(…) == 1`, `… == []`, and
  `assert not …`. None of them registers. A bound or parametrised right-hand side such as
  `mislabels_791(text) == [text]` would register. Do not write it.
- The assert count rises. Read the new floor off `sweep()`, bump it, and add the dated comment in the
  existing form.
- If anything registers anyway, classify it by the rule at R13 (`:2410-2417`). Never reshape an
  assertion to escape the sweep.

**Mutations.** For each one:
- read the file back to confirm it applied;
- defeat the bytecode cache as `CLAUDE.md:97` specifies: delete every `__pycache__`, then run with
  `PYTHONDONTWRITEBYTECODE=1`;
- report the failure message;
- revert it.

| # | mutation | must fail |
|---|---|---|
| M1 | delete the new `209 of 751` entry | the note test's count (`assert 9 == 10`) |
| M2 | set the new entry's log to `None` | the receipt test, with `absence_false` on `209 of 751` |
| M3 | restore FINDINGS §5 row 1 to its `248dd6d` text, `\| published claims whose support changes across draws \| **210 of 791 (26.5%)** \|`, and delete row 4 | the label guard on FINDINGS, and the receipt test (`findings_not_unique` on `209 of 751`) |
| M4 | restore the moved entry's old describes ("share of all published claims …") | the label guard on `RECEIPT_MAP`, and the notes guard (stage 6 renders the describes) |
| M5 | add `diagnose_round14.py` to the collateral banner | the receipt test, with `attribution` on at least the four entries homed in that document |
| M6 | remove the leading `\b` from `PUBLISHED_CLAIMS` | at least the "unpublished" `UNCAUGHT_791` case, and the real `RECEIPT_MAP` and notes guards (the real "called-but-unpublished claims" describes) |
| M7 | restore stage 6's item to its `248dd6d` text after the withdrawn clause | the label guard on the notes |

## 2. Out of scope. Do not touch.

- `decisions/0041-*.md`: `Accepted` and append-only.
- These documents and parts of documents:
  - `HYPOTHESIS.md`;
  - every PREREG and RESULT document;
  - every CHECKS document other than the two banners, and those two below their banners;
  - `walk/FINDINGS.md` outside §5's table rows;
  - `notes/logs/` and `notes/scripts/`.
- Every `notes/` reviewer record. The reviewer records W3's closure (ADR-0041 item 9). If you find a
  reviewer record contradicting the repository, raise it.
- ADR-0041's Open questions, including reviewer defect P4.
- `notes/REVIEWER-DEFECTS.md` items other than W3. In particular W12, which §1.3's rows bear on but
  do not close.

## 3. Report

Give the four-point close (`CLAUDE.md:95`). Name each check at the version it ran, with its target,
including `pytest tests/test_schema.py` run separately. Then report the following.

1. §0 as a table, with every row quoted.
2. Quoted in full: the CORRECTION record, both banners, the new FINDINGS rows, the five-line comment
   replacing `:1069-1072`, the new stage 6 item, and the amended `check_note` docstring sentence.
3. **The three things ADR-0041 item 7 says are unguarded, each verified by reading:**
   - `RECEIPT_MAP`'s §5 entries in order, against §5's printed order;
   - which §5 rows the map covers (rows 1–4 each have an entry);
   - the stage 6 item's population wording, against §5 rows 1 and 4.
4. `sweep()` before and after, the floor comment, and each mutation with its failure message.
5. **Raise:** ADR-0041 item 6's "The enumeration is complete at `aec062e`" is false (the two RESULT
   lines). Do not edit the ADR; the reviewer records it.
6. Point 3 of the close states the label class's status in five groups:
   - **guarded:** FINDINGS, the `RECEIPT_MAP` describes, and the two notes;
   - **corrected by banner only:** the dated CHECKS documents;
   - **listed only:** the two RESULT lines and the execution records;
   - **measured limits:** the `UNCAUGHT_791` shapes;
   - **the known false positive**, and why HYPOTHESIS is outside the guard.
