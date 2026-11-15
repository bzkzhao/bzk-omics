# CORRECTION — H10's headline stays at the registered denominator (2026-11-15)

**This corrects two claims published in `walk/CHECKS-collateral-and-pkm.md` §1 and
`walk/CHECKS-census.md` §5, and carried into `walk/FINDINGS.md` §5 and `bzk/audit.py`
stage 6. It also records a label error separate from them.** The decision is
`decisions/0041-a-registered-headline-moves-only-through-hypothesis.md` (ADR-0041),
*Decision* (a) and (b); it is cited here, not restated. This record carries out its
*Consequences* items 2, 3 and 6. No figure moves, and no registered rule, threshold or
verdict changes. The dated checks are not rewritten; each carries a banner, and this
document is the record. `walk/FINDINGS.md` is edited directly.

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md:8-13`: **withdrawn**
= false as stated, because the instrument or the reasoning was defective; **superseded**
= a correct computation under a stated choice that later evidence disfavours. Both
claims below are **withdrawn**.

**Line numbers.** References into the two CHECKS documents are as their banners leave
them. The banner moved every line of `walk/CHECKS-collateral-and-pkm.md` from `:3` on
down by **16**, and every line of `walk/CHECKS-census.md` from `:3` on down by **14**:
subtract those to map ADR-0041's and the reviewer records' references, which were
measured before the banners. References into `walk/FINDINGS.md` and `bzk/audit.py`,
which this correction also edits, are given by name or as at `248dd6d`.

---

## The claims withdrawn

**1. That the headline changed.** `walk/CHECKS-collateral-and-pkm.md:45-46`:

> **26.5% is the figure with the right denominator**; 27.8% is superseded
> as the headline and kept as the conditional rate.

The withdrawn claim is the second clause, *"27.8% is superseded as the headline"*.

- **Withdrawn: false as stated, and the reasoning was defective.** The reasoning took
  an analytic argument for a change of status. `walk/PREREG-PXD018299-H10.md:186-187`
  lists the share over all claims as "Reported, never the headline", and no HYPOTHESIS
  version made the change.
- HYPOTHESIS v10 restated the rule, and with it the level; it did not restate the
  denominator (`HYPOTHESIS.md:43-46`). No version has been cut since (ADR-0041,
  *Review*, finding D). Under ADR-0041 (a), only such a version moves a registered
  headline.

**2. That 26.5% is H10's registered result.** `walk/CHECKS-census.md:135-136`. The
sentence starts at `:135`; the withdrawn phrase is on `:136`:

> The instability figure
> remains the registered result and the answer to H10

said of 26.5%.

- **Withdrawn: false as stated, and the reasoning was defective.** It carried the
  collateral check's status claim forward as a registration (ADR-0041, *Context*:
  "Two documents follow it"). 26.5% was never registered as H10's result.
- The share over all claims is registered only as a reported readout, never the
  headline (`walk/PREREG-PXD018299-H10.md:186-187`).

**Why not "superseded".** That word classifies a computation under a disfavoured
choice. Whether later evidence disfavours the 751 is the argument's own question, which
ADR-0041 (b) declines without answering.

**Successor**, to both withdrawals: **27.8% (209 of 751)**, H10's level as
`HYPOTHESIS.md:43-46` states it.

## What survives

**1. The argument at `walk/CHECKS-collateral-and-pkm.md:31-33`**: the 40 fully
measured claims are exposed through the shared threshold. The argument is that
document's, run 2026-09-22; this record does not make it. It restates the argument as
a proposal, in the form ADR-0041's reading of (a) sets out:

1. **The registered headline it would move:** H10's primary, the share of claims whose
   support differs across the default cell's 20 draws, over claims whose row carries at
   least one imputed value. It is registered at `walk/PREREG-PXD018299-H10.md:179-181`
   and `HYPOTHESIS.md:904-907`, and its level is at `HYPOTHESIS.md:43-46`.
2. **Its reason:** a fully measured claim's q moves with other rows' draws, so the 40
   fully measured claims are exposed too. Evidence: `walk/CHECKS-collateral-and-pkm.md:31-33`
   and `notes/logs/round13.txt:6-7`.
3. **The proposed figure:** 210 of 791.
4. **The direction:** down, from the registered 27.8%.
5. **Timing:** it was made after the data were seen.
6. It is **proposed**. The registered 27.8% is not superseded.

**It is declined for the current headline by ADR-0041 (b).** A later HYPOTHESIS
version may still take it up.

**2. The first clause of the §1 heading at `walk/CHECKS-collateral-and-pkm.md:29`**,
*"The denominator was wrong"*. ADR-0041 item 2 says the heading "makes `:29-30`'s
status claim, and is restated with it" (`:29-30` there is `:45-46` here). ADR-0041
lists the heading under *What survives*, so this record reads it as restated with the
argument, not withdrawn. The clause is the argument's conclusion. It is **restated with
the argument above**: as part of the proposal, the denominator is argued to be wrong.
The heading's second clause, *"the collateral channel is narrow"*, is unaffected.

**3. The first clause of `walk/CHECKS-collateral-and-pkm.md:45`**, *"26.5% is the
figure with the right denominator"*. It is the same conclusion, handled the same way:
restated with the proposal, not withdrawn. Its second clause is the withdrawn claim
above. *"kept as the conditional rate"* is unaffected.

**4. Every figure in both documents.** No figure moves. 26.5% (210 of 791) stands as
the share over all testable claims.

**5. `walk/CHECKS-census.md:135`'s point that the census should lead.** Which finding
leads is outside ADR-0041's scope.

## The label error, a separate class

The 791 are the testable claims. 798 claims are published, and 7 of them have no
deposit value (`HYPOTHESIS.md:1018`).

**The membership rule.** ADR-0041's review (finding I) requires one. A label is an
instance if it calls the 791 "published claims". It does that by:
- saying "all published claims"; or
- naming "published claims" as the population of a figure over the 791. That is shown
  by `of 791` in its row, or in the cells under its column header; by a printed count
  of the 791 itself; or by a share its home computes over the 791 (`26.5%`).

Two kinds of label are outside the rule:
- a label whose qualifier makes the 791 correct ("published claims in the matrix");
- a label on a subset that gives no figure over the 791 ("fully measured published
  claims | 40", "39 published claims with all three wild-type cells", "the 118
  published claims the documented rule does not call").

**The seven instances ADR-0041 item 6 names**, and where each is corrected:
- `walk/FINDINGS.md` §5 row 1 (`:109` as at `248dd6d`): edited. The row is replaced.
- `bzk/audit.py`, the `RECEIPT_MAP` entry for 210 of 791 (`:103` as at `248dd6d`), and
  stage 6's hand-written item (`:1096-1097` as at `248dd6d`): edited.
- `walk/CHECKS-collateral-and-pkm.md:41`, and `walk/CHECKS-census.md:76` (with its cells
  at `:78-80`), `:84` and `:133`: named in each document's banner. The dated text is not
  rewritten.

**Two more, missed by ADR-0041**, in RESULT documents, which this correction does not
edit:
- `walk/RESULT-PXD018299-H10-attempt3.md:126-127`: "About 92% of published claims are
  recovered … : 725 of 791".
- `walk/RESULT-PXD018299-H10-attempt2.md:91`: "about 92% of the published claims are
  recovered". It is a share of the "supported of 791" column at `:84`.

Both are listed, not edited. **ADR-0041 item 6's "The enumeration is complete at
`aec062e`" is therefore false for `walk/`.** ADR-0041 is `Accepted` and append-only, so
it is not edited here; the finding is raised for the reviewer.

**The guard.** `tests/test_audit.py` now carries a label guard (`PUBLISHED_CLAIMS`,
`mislabels_791`) over `walk/FINDINGS.md`, the `RECEIPT_MAP` describes and stage 6's
and 7's notes. Its caught and uncaught cases (`CAUGHT_791`, `UNCAUGHT_791`) state its
known false positive and its measured limits. It does not read the dated CHECKS
documents, the RESULT documents or `HYPOTHESIS.md`.

## What does not change

- HYPOTHESIS, and every registered rule, threshold and verdict.
- Every execution record (ADR-0041 item 8).
- Every figure in `walk/CHECKS-collateral-and-pkm.md` and `walk/CHECKS-census.md`.
- ADR-0041, which is append-only.

## Every home of the withdrawn claims and the restated argument, the label class's homes in `walk/` and `bzk/`, and its execution-record homes as far as searched, and how each was handled

Each handled cell names which kind of home the row is: **withdrawn claim**, **restated
argument** or **label class**. Where a row is more than one kind, it names each. The
last four rows are **context**, not homes. `HYPOTHESIS.md` and the PREREG documents
hold the registered figure. ADR-0041 holds the decision. `notes/prompts/` and
`notes/REVIEWER-*` quote all three kinds.

| home | wording | handled |
|---|---|---|
| `walk/CHECKS-collateral-and-pkm.md:29` | §1 heading, *"The denominator was wrong, and the collateral channel is narrow"* | restated argument (first clause): banner; body not edited. Second clause unaffected |
| `walk/CHECKS-collateral-and-pkm.md:31-33` | *"…the 40 fully measured claims are exposed too and should not have been excluded from the denominator"* | restated argument: restated above as a proposal, declined for the current headline; banner; body not edited |
| `walk/CHECKS-collateral-and-pkm.md:41` | *"instability over all published claims"* over 210 of 791 | label class: named in the banner; body not edited |
| `walk/CHECKS-collateral-and-pkm.md:45-46` | *"26.5% is the figure with the right denominator; 27.8% is superseded as the headline and kept as the conditional rate"* | restated argument (first clause) and withdrawn claim (*"superseded as the headline"*): banner; body not edited. *"kept as the conditional rate"* unaffected |
| `walk/CHECKS-census.md:76-80` | header *"published claims inside it"* over three `of 791` cells | label class: named in the banner; body not edited |
| `walk/CHECKS-census.md:84` | *"about 0.6% of all published claims"* | label class: named in the banner; body not edited |
| `walk/CHECKS-census.md:133` | *"selection instability \| 26.5% of published claims change support across re-draws"* | label class: named in the banner, which also says the row gives the all-claims share, not H10's result; body not edited |
| `walk/CHECKS-census.md:135-136` | *"remains the registered result and the answer to H10"* | withdrawn claim: banner; body not edited. The point that the census should lead is unaffected |
| `walk/FINDINGS.md` §5 row 1 | *"published claims whose support changes across draws \| 210 of 791 (26.5%)"*, leading the table | withdrawn claim (26.5% as the headline) and label class: edited. Row 1 now reads 209 of 751 (27.8%) over claims with an imputed value; rows 2 and 3 show their 751; a fourth row gives 210 of 791 (26.5%) over all 791 testable claims, reported beside row 1, never in its place |
| `bzk/audit.py`, `RECEIPT_MAP`'s 210-of-791 entry | describes *"share of all published claims whose support changes across draws"* | label class: edited to *"all testable claims"*, and moved after the 13.7% entry to follow §5's new order. A new first entry pairs 209 of 751 with round 13 |
| `bzk/audit.py`, the comment above `"registered_primary"` | *"The registered estimand, not a headline"* | withdrawn claim (reversed by ADR-0041 (b)): edited. It now names the registered estimand as H10's headline population |
| `bzk/audit.py`, stage 6's hand-written item | *"'over_all_claims' is over all published claims, the population of the section 5 headline"* | withdrawn claim and label class: edited after the withdrawn clause. The headline's population is now `conditional_on_imputation`'s, and `over_all_claims` is over all testable claims, never the headline |
| `walk/RESULT-PXD018299-H10-attempt3.md:126-127` | *"About 92% of published claims are recovered … 725 of 791"* | label class: listed, not edited (missed by ADR-0041) |
| `walk/RESULT-PXD018299-H10-attempt2.md:91` | *"about 92% of the published claims are recovered"*, a share of the *"supported of 791"* column at `:84` | label class: listed, not edited (missed by ADR-0041) |
| `notes/logs/round13.txt:1` | *"the right denominator"* | restated argument: listed, not edited; logs are never edited |
| `notes/logs/round13.txt:7` | *"instability over ALL published claims: 210 of 791 (26.5%)"* | label class: listed, not edited |
| `notes/logs/round14.txt:13-15` | *"published claims with median q within … of the cut: … of 791"* | label class: listed, not edited |
| `notes/scripts/diagnose_round13.py:10-12` | *"THE DENOMINATOR IS WRONG"* | restated argument: listed, not edited; the instrument of a dated run |
| `notes/scripts/diagnose_round13.py:119` | *"the right denominator"* | restated argument: listed, not edited |
| `notes/scripts/diagnose_round13.py:131-132` | *"instability over ALL published claims"*, printed over the 791 | label class: listed, not edited |
| `notes/scripts/diagnose_round14.py:19` | *"how many of ALL published claims sit inside that band"* | label class: listed, not edited |
| `notes/scripts/diagnose_round14.py:156-157` | *"published claims with median q within …"*, printed over the 791 | label class: listed, not edited |
| `notes/scripts/diagnose_round10.py:73` | *"published claims {…}"*, a printed count of the 791 | label class: listed, not edited; no committed log |
| `HYPOTHESIS.md` | `:43-46`, `:904-909`, `:1018` | context, not a home: the registered figure and the never-the-headline rule; unchanged, correct as they stand |
| `walk/PREREG-PXD018299-H10.md`, `-attempt2.md`, `-attempt3.md` | `walk/PREREG-PXD018299-H10.md:179-181`, `:186-187`; `walk/PREREG-PXD018299-H10-attempt3.md:81-82` | context, not a home: the registration; unchanged, correct as they stand |
| `decisions/0041-a-registered-headline-moves-only-through-hypothesis.md` | *Decision* (a) and (b), *Consequences* | context, not a home: the decision; unchanged, append-only |
| `notes/prompts/` and `notes/REVIEWER-*` | quotations of the withdrawn claims, the argument and the labels | context, not a home: dated records, not edited (ADR-0041's V8 classes) |

**Outside the rule, or not a home.**
- `notes/scripts/diagnose_round9.py:69`'s "published claims in the matrix" is outside
  the rule: its qualifier names the 791 correctly.
- `notes/reports/REVIEW-seed-lability.md:92` ("The denominator is wrong by one level")
  argues for the 751, so it is not a home of the withdrawn claim.
- Three labels count a subset and give no figure over the 791, so they are outside the
  rule:
  - `walk/CHECKS-ceiling-and-floor.md:44` ("the 118 published claims the documented
    rule does not call");
  - `walk/CHECKS-membership-and-corrections.md:52-53`;
  - `notes/scripts/diagnose_round9.py:14` ("misses 119 published claims").

**Missed by ADR-0041's V8:** `notes/logs/round14.txt:13-15`,
`notes/scripts/diagnose_round14.py:156-157`, `notes/scripts/diagnose_round10.py:73` and
`notes/scripts/diagnose_round13.py:10-12`. Each query missed them for its own reason:
- the `of 791` query did not cover `*.txt`, and cannot see a 791 that an f-string
  computes;
- the `all published claims` query needs "all";
- the `denominator was wrong` query differs from "THE DENOMINATOR IS WRONG" in tense as
  well as case, so it misses even with `-i`.

The two RESULT lines were missed too. Attempt 3's `of 791` is on the line after its
label, and attempt 2's line gives a percentage with no 791.

**Completeness.**
- **The withdrawn claims and the restated argument:** the list is exhaustive.
- **The label class, in `walk/` and `bzk/`:** the list is exhaustive. It rests on two
  searches, both case-insensitive. Both were run before any edit, on `15baed0`, which
  is identical to `248dd6d` in `walk/` and `bzk/`. Run after the edits, they would
  also hit the banners' and this record's own quotations.
  1. Every line matching `published claims?`.
  2. Every line whose last word is "published", and whose next line's first word is
     "claim" or "claims". Trailing quotes, punctuation and spaces are ignored on the
     first line, and indentation, quotes and markup on the second.

  Every hit was classified under the rule. This record lists only the instances and
  the exclusions named above. At `248dd6d`, the first search finds the two RESULT
  lines ADR-0041 missed, and the second finds stage 6's item in `bzk/audit.py`
  (`:1096-1097` as at `248dd6d`).
- **The label class, in execution records:** the list goes only as far as four
  searches over `notes/logs/` and `notes/scripts/` find. They are the same two
  searches, plus `-i` searches for "denominator" and "26.5%". It does not claim every
  instance. Execution records are not edited either way (ADR-0041 item 8), so a later
  find adds a row and changes nothing else.
