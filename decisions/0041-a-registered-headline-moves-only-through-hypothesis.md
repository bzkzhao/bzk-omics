# ADR-0041 — A registered headline moves only through a versioned HYPOTHESIS restatement; H10's stays at the registered denominator

| | |
|---|---|
| Status | Proposed |
| Date | 2026-11-13 |
| Supersedes | — |
| Superseded by | — |

**It supersedes nothing.** No record decides who may move a registered headline. This one does,
and applies the answer to H10's headline, which two CHECKS documents have moved:

- `walk/CHECKS-convention-resolved.md:5-7` moved its **level** ("this supersedes the *level*"), and
  HYPOTHESIS v10 took that up the same evening (`HYPOTHESIS.md:84-85`).
- `walk/CHECKS-collateral-and-pkm.md` moved its **denominator**, and no version took that up.

## Context

**H10's primary is registered at one denominator, by all three of its pre-registrations.**
- `walk/PREREG-PXD018299-H10.md:179-181` (attempt 1) registers the primary as the share over claims
  whose row carries at least one imputed value, the 751. It lists "the same share over all claims"
  under "Reported, never the headline" (`:186-187`).
- `walk/PREREG-PXD018299-H10-attempt2.md` states no denominator of its own. It carries attempt 1's §6
  readouts over unchanged (`:6-13`).
- `walk/PREREG-PXD018299-H10-attempt3.md` keeps attempts 1 and 2 governing except where it replaces
  them (`:6-8`). At `:81-82` it takes the shares over the same population. It reads
  the verdict "from the primary only" (`:76`), and lists the share over all claims as one of readout
  B's items (`:70`).

`HYPOTHESIS.md` v10 agrees. It states H10's level as 27.8%, "209 of 751 claims with an imputed
value" (`:43-44`). H10's own entry fixes the primary at the default cell's 20 draws, over claims with
an imputed value (`:904-907`). It lists "the same share over all claims reaching the test" as
"Reported, and never the headline" (`:908-909`). The 791 are the testable claims: 798 are published,
and 7 have no deposit value (`:1018`).

**HYPOTHESIS already holds the rules (a) generalises.** Amendments are recorded with their trigger
(`:22-23`), and the pre-registration fixes the population before measurement (`:918-919`).

**A CHECKS document moved the denominator, and no version took it up.**
`walk/CHECKS-collateral-and-pkm.md` argues the 751 leaves out exposed claims (`:13`, `:15-17`), and
concludes "**26.5% is the figure with the right denominator**; 27.8% is superseded as the headline
and kept as the conditional rate" (`:29-30`). Two documents follow it:
- `walk/FINDINGS.md` §5 leads with 210 of 791 (26.5%);
- `walk/CHECKS-census.md:119-122` calls 26.5% "the registered result and the answer to H10".

No HYPOTHESIS version records the move, and neither chain cites the other on it (reviewer map D1).

**The move has a reason, a direction, and a timing problem.**
- *Reason:* the shared-threshold mechanism. Round 12 found that a fully measured claim's q moves
  with other rows' draws, so the 40 fully measured claims are exposed too
  (`walk/CHECKS-collateral-and-pkm.md:15-17`).
- *Direction:* down, 27.8% to 26.5%, so it does not favour the verdict.
- *Timing:* it was chosen after the data were seen.

**The verdict does not depend on it.** Both figures are far above the 5% "recurs" threshold
(`walk/PREREG-PXD018299-H10.md:182-184`). What depends on it is whether a later document may change
what a registration fixed.

**The level move is the precedent (a) follows.** A CHECKS document stated a change, and a HYPOTHESIS
version restated it: v10 named its trigger (`HYPOTHESIS.md:39-41`) and kept the pre-specified 21.2%
visible as **superseded, not withdrawn** (`:43-46`). The denominator move took only the first step.

## Decision

**Decided by bzk on 2026-11-13** (called *A* below, against alternative *B*):

- **(a)** A CHECKS document may propose moving a registered headline. Only a versioned HYPOTHESIS
  restatement moves it.
- **(b)** H10's headline stays at the registered denominator: 27.8% (209 of 751). 26.5% (210 of 791)
  is reported over all claims, never the headline.

**This record's reading of (a), for review.** The round trip may amend this reading without amending
the decision.

- **A *registered headline*** is the readout fixed as a hypothesis's primary: its population,
  denominator and statistic, and the test, rule, cell and draw count it is computed under.
  - A `walk/PREREG-*` committed before the run it governs fixes these, under HYPOTHESIS's delegation
    (`HYPOTHESIS.md:918-919`). Fixing them there is registration, not a move.
  - Where a later HYPOTHESIS version restates any of them, the restatement governs. For H10, v10
    restated the rule (`:43-46`, `:84-85`), so H10's headline is under the documented rule, not
    attempt 3's pre-registered halved variant.
  - The headline's value is the one its dated home records for that readout.
- **Scope.** (a) governs which figure any document gives for a registered hypothesis's primary
  readout, whether or not that document names the hypothesis. It does not govern which finding
  `walk/FINDINGS.md` leads with. Execution records
  (Consequences item 8) are outside it.
- **A *proposal*** carries six things:
  - it names the registered headline it would move, citing the line that registers it;
  - it states its reason, citing the evidence it rests on;
  - it gives the proposed figure, as numerator over denominator where the statistic is a share;
  - it states the direction relative to the registered value;
  - it states whether it was made after seeing data;
  - it uses "proposed", and never calls the registered figure "superseded".
- **Until a HYPOTHESIS version takes a proposal up, the registered headline stands.** The proposed
  figure may be reported beside it, under its own label. HYPOTHESIS decides which readout is the
  headline. Each figure keeps its own dated home (`HYPOTHESIS.md:30-33`).
- **`walk/CHECKS-convention-resolved.md:5-7` predates (a)** and calls a move "supersedes". It is not
  corrected, because v10 took the move up.

**(b), as this record states it.** H10's headline is 27.8% (209 of 751 claims with an imputed
value), under the documented rule at the default cell's 20 draws (`HYPOTHESIS.md:43-46`, `:904-905`).
26.5% (210 of 791) is the share over all testable claims, and is never the headline, as
`walk/PREREG-PXD018299-H10.md:186-187` lists it.

The argument that 791 is the better denominator stands as an argument. This record declines it for
the current headline and does not ask a HYPOTHESIS version to take it up. Under (a), a later version
still may.

## Consequences

The edits below are for a follow-on prompt, which states their exact wording.
- **Items 1–4** follow from (a) and (b).
- **Item 7** follows from item 4. Once §5's row 1 changes, stage 6's note misnames the headline's
  population, and §5 carries a figure `RECEIPT_MAP` does not pair.
- **Items 5 and 6** are cleanup this record surfaced. The round trip may drop them without touching
  the decision.
- **Item 8** bounds the edits, and **item 9** records which reviewer defect closes.

1. **HYPOTHESIS does not change.** v10 states the 27.8% headline and the never-the-headline rule. It
   reports no 26.5% figure.
2. **`walk/CHECKS-collateral-and-pkm.md`.**
   - `:29-30`'s claim that the headline changed is **withdrawn**, in the sense of
     `walk/CHECKS-membership-and-corrections.md:9-10`: false as stated, because the reasoning took
     an analytic argument for a change of status that `walk/PREREG-PXD018299-H10.md:186-187`
     forbade and no HYPOTHESIS version made.
   - It is not **superseded**, which `walk/CHECKS-membership-and-corrections.md:12-13` reserves for a
     computation under a disfavoured choice. Whether later evidence disfavours the 751 is the
     argument's own question, which (b) declines without answering.
   - **Successor:** 27.8% (209 of 751).
   - **What survives:** the argument at `walk/CHECKS-collateral-and-pkm.md:15-17`, restated as a
     proposal under (a), and marked as declined for the current headline. The `:13` heading ("The
     denominator was wrong") makes `:29-30`'s status claim, and is restated with it.
3. **`walk/CHECKS-census.md:119-122`.** Its claim that 26.5% "remains the registered result and the
   answer to H10" is withdrawn: false as stated, because 26.5% was never registered. 27.8% (209 of
   751) succeeds it. Its point
   that the census should lead (`:121`) is not touched: which finding leads is outside (a)'s scope.
4. **`walk/FINDINGS.md` §5, row 1.** It leads with 27.8% (209 of 751), labelled as claims with an
   imputed value, and reports 26.5% (210 of 791) beside it, labelled as all testable claims. 26.5%
   sits in row 1 itself or below row 2, so that row 2's "the same" keeps referring to the 751.
5. **`walk/FINDINGS.md` §5, rows 2 and 3** (reviewer map D2; bears on reviewer defect W12).
   - Row 2 ("the same at 100 draws | 38.3%") is over the 751, so "the same" becomes true; it needs
     the 751 shown. Its home (`walk/CHECKS-draws-and-threshold.md:19`) gives no numerator, so none is
     computed.
   - Row 3 is 13.7%, 103 of 751 (`walk/CHECKS-ceiling-survives.md:70`), and needs its denominator
     shown.
6. **The 791 called "published claims" — a label error, separate from the headline.** 791 claims
   are testable, of 798 published. The instances are:
   - `walk/FINDINGS.md:109`;
   - `walk/CHECKS-collateral-and-pkm.md:25`;
   - `walk/CHECKS-census.md:62`, `:70`, `:119`;
   - `bzk/audit.py:103`, `:1096-1097`.

   The enumeration is complete at `aec062e` (prompt 43, V8). The class is **unguarded**: the
   follow-on prompt writes the guard, or records why it cannot be written. Execution records keep
   theirs (item 8).
7. **`bzk.audit` stage 6: its computation is unaffected, its note is not.**
   - The stage computes the variant its `registered_variant` key names: attempt 3's halved rule,
     whose level v10 superseded for the headline. `registered_primary` marks
     `conditional_on_imputation`, the headline's population. After row 1 changes, that population
     and the headline differ only in rule; `over_all_claims` differs in both.
   - Its hand-written item (`bzk/audit.py:1096-1102`) calls the all-claims population "the
     population of the section 5 headline", and its comment at `:1069` reads "The registered
     estimand, not a headline". Both need re-reading.
   - `RECEIPT_MAP` needs an entry for 27.8% (209 of 751), placed in §5's order (`bzk/audit.py:90`).
     Its home is `walk/CHECKS-collateral-and-pkm.md:24` and its log `notes/logs/round13.txt:6`.
     Several homes measure the figure: HYPOTHESIS names `walk/CHECKS-convention-resolved.md`
     (`:84-85`; `:45` there), and `walk/CHECKS-ceiling-survives.md:71` and
     `walk/CHECKS-draws-and-threshold.md:17` record it too. The map names round 13's only because
     round 13 has its only committed log, and the receipt checker's direction 6 refuses a log-less
     entry whose anchor occurs in a log.
   - The stage 6 item count pinned at `tests/test_audit.py:1560` moves from 9 to 10.
   - The receipt checker guards the new entry's anchors and instrument. These are **not guarded**,
     and are verified by reading:
     - the hand-written item's population wording (`tests/test_audit.py:1270`);
     - which of §5's rows the map covers, beyond the pinned count;
     - the map's order.
8. **Execution records are not edited.** `notes/logs/round13.txt` and the `notes/scripts/` files
   record what was run and printed, including "the right denominator" and "all published claims".
9. **Reviewer defect W3 closes** when items 2–4 and 7 land. The reviewer records the closing commit in
   `notes/REVIEWER-DEFECTS.md`.

## Alternatives considered

**B. Adopt 26.5% through HYPOTHESIS v11, recorded as a deviation.** This complied with (a). v11
would state the reason, the direction and the post-hoc timing. v10 stated its trigger and kept the
superseded figure visible; it stated neither direction nor timing.

**Not chosen:** bzk chose A on 2026-11-13 and recorded no reason. What each costs is noted for the
record, not as the ground of the choice:
- **B's cost:** a pre-registered estimand changed after the data were seen, legitimised by
  recording it.
- **A's cost:** the headline excludes the 40 fully measured claims the shared-threshold mechanism
  shows are exposed. The two numerators differ by one claim, 210 against 209.

**Let a CHECKS document move a headline directly.** Rejected, by (a). It is what happened to the
denominator, and it left two chains disagreeing, with neither citing the other.

**Report both figures and name neither the headline.** Not chosen. In this record's reading, the
pre-registrations name the primary, so declining to name one would depart from them without a
record.

## Landing verification

Landed `Proposed` by prompt 43 on 2026-11-14, from `notes/drafts/` at `b8b8cf2`. 0041 was free:
`decisions/` held 0001–0040 without 0018. The decision text above is unchanged from the draft.
Each entry gives the command, its output, and a verdict. **No entry is corrected:** all nine
hold. The measured state is the landing commit's parent (`b8b8cf2`). It cites the same lines as
`aec062e`, where the line references were measured (V1).

### V1 — every line reference in the record

```
git diff --stat aec062e -- HYPOTHESIS.md walk bzk tests/test_audit.py notes/logs
```

```text
(no output)
```

The C0–C13 quotes of prompt 43 §0(c) were taken again on the landed tree and on `b8b8cf2`. The two
captures, 158 lines each, are byte-identical (`cmp`), and §0 had found every row as cited.

**Coverage.** Every line reference in the record falls inside a C row's range, and none is left
uncovered:
- `HYPOTHESIS.md:43-44`, `:904-905`, `:904-907` and `:908-909` sit inside C5 or C6;
- `walk/CHECKS-membership-and-corrections.md:9-10` and `:12-13` sit inside C10's `:8-13`;
- `walk/CHECKS-census.md:121` and `:119` sit inside C9's `:119-122`.

**Holds.**

### V2 — "Both figures are far above the 5% 'recurs' threshold"

```
sed -n '182,184p' walk/PREREG-PXD018299-H10.md
```

```text
- **Recurs:** at least 5%.
- **Absent:** at most 1%.
- **Indeterminate:** between the two.
```

27.8% is about 5.6 times the threshold, and 26.5% about 5.3 times. **Holds.**

### V3 — "HYPOTHESIS does not change … It reports no 26.5% figure"

```
grep -cF "26.5" HYPOTHESIS.md
```

```text
0
```

C5 (`:43-46`) states 27.8% (209 of 751). C6 (`:908-909`) lists the share over all claims as
"Reported, and never the headline". **Holds.**

### V4 — row 2 is over the 751 with no numerator in its home; row 3 is 103 of 751

```
sed -n '15,19p' walk/CHECKS-draws-and-threshold.md
grep -cE "751|791" walk/CHECKS-draws-and-threshold.md
sed -n '119,120p' notes/scripts/diagnose_round11.py
sed -n '70p' walk/CHECKS-ceiling-survives.md
```

```text
| draws | unstable, of claims with an imputed value | structural misses | structural extras |
|---|---|---|---|
| 20 | 27.8% | 6 | 3 |
| 50 | 34.1% | 5 | 3 |
| 100 | **38.3%** | **2** | **2** |
0
    with_imputed = published & (imputed_count > 0)
    unstable = with_imputed & (counts > 0) & (counts < draws)
| floor across the rule family | **13.7%** (103 of 751) | unstable at every scaling from 0.25 to 2.0; no choice within the family removes it |
```

**Holds.**
- Row 2's home prints neither a numerator nor a denominator. Its population is the column header's
  "claims with an imputed value".
- The script's denominator (`with_imputed`) does not depend on the draw count. So row 2 is over the
  same population as the 20-draw row, which the record's other homes give as 209 of 751.

### V5 — "All three of its pre-registrations", attempt 2 by inheritance

```
sed -n '6,13p' walk/PREREG-PXD018299-H10-attempt2.md
grep -c -i -E "751|791|imputed value|denominator|over all claims|headline" walk/PREREG-PXD018299-H10-attempt2.md
```

```text
**What it supersedes.** It replaces only what it names in §1–§3 of
`walk/PREREG-PXD018299-H10.md` (attempt 1, `0e4dc6b`). Everything else there
still governs attempt 2 unchanged:
- the population and exposure (§2);
- the unstated steps (§3);
- the family (§5);
- readouts A to D (§6);
- expectations X1–X3 and X6–X8 (§7);
0
```

**Holds.**
- Attempt 2 states no denominator of its own and carries attempt 1's §6 over unchanged.
- C1 confirms attempt 3: `:6-8` keeps attempts 1 and 2 governing, `:81-82` takes the shares over
  claims with an imputed value, `:76` reads the verdict from the primary, and `:70` lists the share
  over all claims under readout B.
- C4 confirms attempt 1: `:186-187` lists the all-claims share under "Reported, never the headline".

### V6 — stage 6 computes attempt 3's halved variant; `registered_primary` marks `conditional_on_imputation`

The command runs on the committed fixtures only. It was run from the repository root, and
`audit-out/` and `audit.json` were deleted afterwards.

```
uv run python -m bzk.audit --out audit-out --json > audit.json
uv run python -c "import json; s = [x for x in json.load(open('audit.json'))['stages'] if x['stage'] == 6][0]['findings']; [print(k + ':', json.dumps(s[k])) for k in ('registered_variant', 'registered_primary', 'over_all_claims', 'conditional_on_imputation')]"
```

```text
registered_variant: "joint_half+random_excluding_trivial"
registered_primary: "conditional_on_imputation"
over_all_claims: {"numerator": 159, "denominator": 791, "share": 0.20101137800252844}
conditional_on_imputation: {"numerator": 159, "denominator": 751, "share": 0.21171770972037285}
```

**Holds.**
- `joint_half` + `random_excluding_trivial` is attempt 3's primary
  (`walk/PREREG-PXD018299-H10-attempt3.md:45`).
- 159 of 751 = 21.2% is the halved rule's figure, which v10 superseded as the level
  (`walk/CHECKS-convention-resolved.md:46`; `HYPOTHESIS.md:43-46`).

### V7 — stage 6's note and `RECEIPT_MAP` change with §5

```
grep -n "section 5 headline\|the headline's" bzk/audit.py
grep -c "209 of 751" bzk/audit.py
```

```text
1097:            "claims, the population of the section 5 headline, so only the rule separates them: "
1101:            "value, a different population from the headline's, and is computed under the same "
0
```

**Holds.** The note names the all-claims population as the headline's (`:1097`). No map entry
anchors 27.8% (209 of 751).

### V8 — every site *Consequences* must reach is named in it

```
git grep -n -F -e "26.5%" -e "210 of 791" -e "210/791" -e "right denominator" -e "denominator was wrong" -e "superseded as the headline" -- "*.md" "*.py" "*.txt"
git grep -n -i -F "all published claims" -- "*.md" "*.py" "*.txt"
git grep -n -F -e "of 791" -e "791 claims" -- "*.md" "*.py"
```

The output below excludes this record's own hits and gives file and line only. The first two
queries return:

```text
bzk/audit.py :102 :103 :108 :109
walk/CHECKS-census.md :70 :119
walk/CHECKS-collateral-and-pkm.md :13 :25 :29
walk/FINDINGS.md :109
notes/logs/round13.txt :1 :7
notes/scripts/diagnose_round13.py :119 :131
notes/scripts/diagnose_round14.py :19
notes/prompts/22-walk-two-route-independence.md :149
notes/prompts/42a-stages-6-and-7-name-their-rule.md :174
notes/prompts/42b-the-notes-name-their-instruments.md :142 :344 :377 :641
notes/prompts/43-land-adr-0041.md :56 :57 :58 :61 :138 :139 :144
notes/REVIEWER-DEFECTS.md :37
notes/REVIEWER-HANDOFF-2026-11-12.md :130 :150
notes/REVIEWER-MAP-findings-5-and-6.md :17 :74 :89 :155 :163 :180 :214
```

The third query returns 55 hits. Only those whose label calls the 791 "published claims" are kept.
- **Kept:**
  - `bzk/audit.py:102`, `:108`, `:109`, the entry described at `:103`;
  - `walk/CHECKS-census.md:64-66`, cells under the `:62` header "published claims inside it";
  - `walk/CHECKS-collateral-and-pkm.md:25`;
  - `walk/FINDINGS.md:109`;
  - reviewer and prompt hits, as listed above.
- **Dropped:** every other hit labels the 791 as testable claims, all claims, claims supported, or
  the registered population. "9 of 791" (`walk/FINDINGS.md:131`,
  `walk/CHECKS-ceiling-survives.md:55`, `:69`, `bzk/audit.py:164`, `:169`) is dropped too: there
  "published" qualifies the list, not the 791.

**Classified:**
- *Named in Consequences:*
  - `walk/CHECKS-collateral-and-pkm.md:13`, `:25`, `:29` (items 2, 6);
  - `walk/CHECKS-census.md:62` (with its cells `:64-66`), `:70`, `:119` (items 3, 6);
  - `walk/FINDINGS.md:109` (items 4, 6);
  - `bzk/audit.py:103` (item 6), whose entry's anchors are `:102`, `:108`, `:109`. Item 7 names
    the map, and the receipt checker guards those anchors.
  - `bzk/audit.py:1096-1097` (items 6, 7) is not hit by these queries, because "published" and
    "claims" fall on two lines. Item 6 names it.
- *Reports the figure without calling it H10's result, so it stays under (b):* no hit.
- *Execution record:* `notes/logs/round13.txt:1`, `:7`; `notes/scripts/diagnose_round13.py:119`,
  `:131`; `notes/scripts/diagnose_round14.py:19`.
- *Prompt:* `notes/prompts/22-*`, `42a-*`, `42b-*`, `43-*`.
- *Dated reviewer record:* `notes/REVIEWER-MAP-findings-5-and-6.md`,
  `notes/REVIEWER-HANDOFF-2026-11-12.md`, and `notes/REVIEWER-DEFECTS.md:37` (W3, whose closing
  item 9 names).

**No hit falls outside the five classes. Holds.**
- Nothing in `walk/`, `bzk/` or `HYPOTHESIS.md` changed between `aec062e` and the landing (V1). So
  item 6's "complete at `aec062e`" is this measurement.
- A rewording that avoids all three queries would escape this sweep. The class is unguarded, as
  item 6 states.

### V9 — "It supersedes nothing"

```
git grep -n -i -E "headline|pre-regist|PREREG" decisions/
```

The command returns 66 hits. This record holds 44. The rest, per file:

```text
      2 decisions/0028-the-anchor-curation-record-is-one-supersession.md
      2 decisions/0029-how-an-experiment-id-reaches-the-contrast-mints.md
      1 decisions/0032-what-the-perseus-adapter-reads-and-whether-the-platform-converts.md
      1 decisions/0033-frame-is-a-coverage-repair.md
      2 decisions/0036-ip-ms-as-role-tagged-observations.md
      2 decisions/0037-every-digest-id-encodes-its-anchors.md
     11 decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md
      1 decisions/README.md
```

**Holds.**
- `decisions/README.md`'s hit is this record's own Written row.
- In the other 21 hits:
  - 0028 `:16` and `:20` use "headline(s)" as a verb about that record's own counts;
  - 0032 `:408` concerns I9's "headline sentence";
  - the rest are those records' own pre-registered measurements.
- None cites a `walk/PREREG-*` or decides who may move a hypothesis's registered headline.

## Open questions

1. **Does (a) cover a withdrawal, not only a moved headline?** Reviewer defect P4 is the case.
   - `walk/CHECKS-membership-and-corrections.md` withdrew "validated on the deposit under test, with
     nothing fitted" (`:43`), and corrected the 781-against-798 comparison under it (`:57-59`).
   - HYPOTHESIS v10 still states "nothing fitted" (`:5`, `:48-49`, `:637-638`, `:1203`) and 781
     against 798 (`:48`).
   - If (a) extends to claims, a HYPOTHESIS version takes the withdrawal up. If it does not, the two
     chains disagree, with no rule saying which governs.

   Not decided here.
2. **May `walk/RESULT-*` or `walk/FINDINGS.md` propose?** (a) already denies them the move: FINDINGS
   §5 is the main place the move appeared. What is open is whether either may *propose* one, and in
   what form.
