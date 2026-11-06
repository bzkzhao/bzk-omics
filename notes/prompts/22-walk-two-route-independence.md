# Prompt 22 (reissued, rev 3): walk/ item 1. Withdraw "two routes sharing no inputs"

Repo: bzkzhao/bzk-omics. Review commit: 3a165a4. Linear history, no merges.

## 0. Opening state, then receipt check. Both before any edit.

### Opening state. CLAUDE.md:102, both halves.

1. Run `git fetch --all`. State HEAD's hash, `git rev-list --count HEAD`, `git rev-list --merges HEAD | wc -l`, and `git status --porcelain --untracked-files=all`.
   If HEAD ≠ 3a165a4, re-derive every line number below before using it.

2. Confirm this prompt has not already landed. Check that:
   - walk/CORRECTION-PXD018299-two-route-independence.md does not exist;
   - walk/CHECKS-two-route-recovery.md carries no banner;
   - no commit after 3a165a4 touches either file.
   If any of these is false, stop and report.

3. Run the full suite with PYTHONDONTWRITEBYTECODE=1. Report:
   - passed/failed/skipped counts;
   - every failing test by node id;
   - the numpy, scipy, polars and duckdb versions actually imported;
   - whether ~/.bzk-omics/ exists, and its top-level entries.
   Record only. Do not diagnose.

   The failing set may be exactly empty, or exactly these two:
   - tests/test_pxd018299_h10.py::test_attempts_1_and_2_are_unchanged_by_attempt_3
   - tests/test_tautology_sweep.py::test_every_classified_instance_re_runs_its_recorded_evidence
   These fail in some environments at 3a165a4 and pass on a fresh pinned install (`uv sync --frozen`: 860 passed, 14 skipped). They are carried as D30 below. This prompt suspends CLAUDE.md:102's green-at-open requirement for these two only. If any other test fails, stop and report.

4. Items outstanding from the previous turn in this window. That turn was a stopped ADR-0029 prompt pinned to 387da83; it changed nothing. State each item and its disposition:
   (a) The ADR-0029 prompt: retired by bzk. Its work landed at f345243. Not to be re-run.
   (b) Its proposed "defect 30" (the attempt-1 digest): carried as D30, not acted on in this turn.
   (c) Its line-drift observation (ROADMAP.md l.8387–8391 at 387da83 against HEAD): already covered by the repo's line-drift defect class. Not acted on.
   If you find any other outstanding item in that turn's report or the repo, list it. Do not act on it.

### Receipt check. Answer all four, quoting from files at HEAD.

R1. Quote verbatim:
    - walk/CHECKS-two-route-recovery.md lines 1, 12, 33–34 and 36–39;
    - walk/FINDINGS.md lines 47, 51–52, 56–57 and 110;
    - notes/logs/round16.txt lines 18–19.
    For each, say whether the sentence is compound, and quote every half.
    For :36–39, name the claim each half makes.

R2. Route 2 is block LL of notes/scripts/diagnose_round16.py. Give line numbers for:
    (a) the object `values` is read from, and whether drawn cells, measured cells, or both enter `observed_gaps`;
    (b) the test that classifies a cell as drawn (`provided()` and its callers);
    (c) the variables setting the simulated draws' mean and SD, including where WIDTH is defined.

    Route 1 is the "against the deposit's column" readout in Check 2 of walk/CHECKS-PXD018299-imputation-effects.md: the wild-type downshift and width figures, computed in notes/scripts/diagnose_imputation_effects.py. Give line numbers for:
    (d) which S1 cells enter it, and the test that classifies a cell as drawn (`cell()`);
    (e) the reference column set (the `keep`/`kept` path).

    Then state, each argued from the code:
    - whether "drawn" under (b) implies "drawn" under (d), whether the converse holds, and hence whether route 2's drawn cells are a subset of route 1's drawn inputs;
    - whether route 2's measured S1 cells are members of route 1's reference set, using walk/CORRECTION-PXD018299-S1-provenance.md:25–27 (quote it);
    - whether the two reference populations are the same set of cells;
    - whether WIDTH equals a figure route 1 reports, and at which line of the CHECKS file that figure lives.

R3. Readout C is defined in walk/RESULT-PXD018299-H10-attempt2.md §5.
    - Quote its definition.
    - Quote CHECKS-PXD018299-imputation-effects.md:57–59 and :75, which state its status.
    - Say whether the route labelled "readout C" at CHECKS-two-route-recovery.md:33 is readout C or Check 2's deposit-reference readout.

R4. Quote:
    - the definitions of "withdrawn" and "superseded" from walk/CHECKS-membership-and-corrections.md (lines 8–13);
    - line 33 there, on withdrawing a claim together with "the stronger claim built on it";
    - the full banner that commit 49225b3 added to walk/RESULT-PXD018299-H10-attempt2.md;
    - CLAUDE.md:40.

STOP CONDITION. Make no edits if R2 shows either of the following:
- route 2's `observed_gaps` do not use S1 values at cells route 1 also classes as drawn;
- the two reference populations are different sets of cells.
In that case, report the opening state and R1–R4, and stop.

## 1. The defect and the restated finding

**The claim.** CHECKS-two-route-recovery.md:12 and :36–39, and FINDINGS.md:56–57, say that the two downshift recoveries "share no inputs" and are "independent routes". That is false as stated. R2 establishes four dependences:

1. **Drawn cells: a subset.** Route 2's drawn S1 cells are among route 1's drawn inputs. The two scripts use different drawn tests, and route 2's implies route 1's.
2. **Measured cells: taken from the reference.** Route 2's measured S1 cells, which set `measured_fc`, are by the provenance correction rounded copies of deposit cells in the reference set both routes use.
3. **A shared reference population.** Both routes reference the same deposit column statistics.
4. **A consumed output.** Route 2 fixes its draw width at a figure route 1 recovered.

**The dependent claim.** CHECKS-two-route-recovery.md:37–39 says this "supersedes round 15's framing", on the ground that the finding is "not that an observation matched a simulation". That rests on the independence claim. Route 2 is itself an observation matched against a simulation. By the rule quoted in R4, it is withdrawn with the claim it is built on. Round 15's framing is left standing.

**The restated finding.** Two statistics agree near Perseus's default of 1.8. The second's drawn cells are a subset of the first's. Its measured cells come from the reference both use. It takes the first's recovered width as fixed. State this. Do NOT argue in the text either that the agreement still corroborates the setting or that it does not.

## 2. Count the homes yourself

Enumerate candidates across the whole repo (excluding .git). Read every hit in context.

- `grep -rniE "share[sd]? no inputs|sharing no inputs|independent(ly)? (route|recover)|two independent|second,? independent"`
- `grep -rniE "twice|two routes|recovered twice"` over walk/, HYPOTHESIS.md, and notes/scripts/diagnose_round16.py
- `grep -rniE "recover"` over notes/logs/round16.txt
- `grep -rn "two-route-recovery\|round16"`: every file citing the check may restate its claim
- `grep -rni "supersedes round 15"`

Classify each hit:
- **(A)** asserts input-independence of the two downshift recoveries, or rests on it. This includes an unqualified "twice", a "second recovery" framed as separate evidence, and the supersession claim.
- **(B)** another sense or another finding. Examples: "Not an independent path: the same instruments"; imputation-effects.md:73's "independently confirms what a lab postdoc…"; a line citing one route only.

Report every hit with its class and a one-line reason. Do not inherit a count from this prompt.

## 3. What to do with each (A) home

The rules below come from the reviewer; verify them where the repo can.

- **Dated records** (RESULT-, CHECKS-, PREREG-) are not rewritten. Precedent: walk/CORRECTION-PXD018299-S1-provenance.md:5–6 and commit 49225b3.
- **Committed fixtures** are not edited.
- **walk/FINDINGS.md is edited directly by bzk's decision.** The repo does not state this. Its only commit is 0ad257d. Do not describe it as a repo convention in any file.

**walk/CHECKS-two-route-recovery.md.** Do NOT edit its body. Add a banner at the top, in 49225b3's form, that:
- **withdraws** (false as stated) the claim that the two routes share no inputs and are independent (headings :1 and :12, sentence :36, and :39);
- **withdraws** the claim at :37–38 that this supersedes round 15's framing;
- states that the band scan's figures and sensitivity table are unaffected;
- points to the new correction document.

**walk/FINDINGS.md** (direct edits):
- :47 heading: remove wording implying independent recovery. "Twice" may stay only if the §2 body says what the two statistics are and how they overlap.
- :51–52 table: replace "supplement + deposit" in both rows with each route's inputs, described in words. Say which cells, which reference, and that route 2's width is fixed at route 1's, so that the overlap is visible in the table. Do not introduce any number that is not already in FINDINGS; point to CHECKS-two-route-recovery.md and CHECKS-PXD018299-imputation-effects.md instead.
- :56–57: replace the "share no inputs" half and keep the "overlap on Perseus's default of 1.8" half. Add one sentence naming the four dependences in §1.
- :110: change only "twice", to wording consistent with §2 or a pointer to §2. Leave "**yes**" and the rest of the row untouched (item 2).
- Change no figure (1.76–1.78, 1.70–1.90, +1.055, 0.077). Add no knockout-column figures.

**notes/scripts/diagnose_round16.py** (the docstring at :14–15, the print at :127–128, and any other (A) home in it): do NOT edit. It is the instrument of a dated run. List each line in the correction document.

**notes/logs/\*** (including round16.txt:18–19): never edit. List each (A) home in the correction document.

**(A) homes outside walk/ and notes/:** list them in the report and do not edit them.

**New file:** walk/CORRECTION-PXD018299-two-route-independence.md, dated 2026-09-27. It contains:
- **The findings withdrawn.** The independence claim and the supersession claim, each quoted with source lines.
- **Why they were wrong.** The four dependences, each cited by script and line from R2, and dependence 2 also by CORRECTION-PXD018299-S1-provenance.md:25–27.
- **The restated finding.**
- **An erratum on the route-1 label.** The route labelled "readout C" at CHECKS-two-route-recovery.md:33 (also diagnose_round16.py:127 and notes/logs/round16.txt:18) is Check 2's deposit-reference readout in CHECKS-PXD018299-imputation-effects.md. Readout C proper is superseded there (:75). Cite R3.
- **What does NOT change.** Both bands, the band scan's sensitivity table, the bootstrap SE, and attempt 3's registered verdict. Name each by its home and line; do not restate the figure.
- **Every (A) home**, with how each was handled.

Single-source rule (CLAUDE.md:40, quoted in R4): the correction document restates no measured figure, the width included.
- Cite the WIDTH constant as `diagnose_round16.py:49`.
- Cite the figure it equals by its line in CHECKS-PXD018299-imputation-effects.md.
- Point to CHECKS-two-route-recovery.md and CHECKS-PXD018299-imputation-effects.md for every number.

## 4. Out of scope. Do not touch.

Reviewer's walk/ defect list (not in the repo; each item carries its content):
2  Check 2's knockout columns (down 1.39–1.51) and the "noisy" reading at imputation-effects.md:78–80. Do not add knockout figures, conditionality or reference-population caveats to FINDINGS §2 or :110. Do not change :110's "yes".
3  The headline estimand: 27.8% (registered, PREREG-PXD018299-H10.md §6B) against 26.5% (CHECKS-collateral-and-pkm.md §1).
4  FINDINGS §3 "seven claims": the missing base rate and the unreconciled "stable and comfortably significant" prediction.
5  The census's implicit "deposit = analysed table" assumption (CHECKS-census.md:107–108).
6  "Selection adds almost nothing" conditions on a fold-change floor, not on q (CHECKS-gap-and-protein-grain.md:34).
7  MOESM5 "log2 ratios" against "unknown" (CHECKS-gap-and-protein-grain.md:73/:76; CHECKS-draws-and-threshold.md:119).
8  The join-mapping defeater class (CHECKS-two-route-recovery.md §4; FINDINGS §9).
9  Check E's direction: 918 against 798 (CHECKS-PXD018299-population-and-convention.md:54, :68; CHECK-PXD026748-grouping.md:56).
10 MATCH_TOLERANCE = 1e-6 at bzk/sources/pxd018299_h10.py:164.
11 The rows-against-peptides unit slip (CHECKS-census.md:107–108).
12 The instability estimand grows with draw count (CHECKS-draws-and-threshold.md:17–19; FINDINGS:102).

Platform review:
P1 The seed-0 whole_matrix + Welch baseline (bzk/sources/pxd018299_differential.py:108–113).
P2 bzk/stats/imputation.py: defaults, docstring, and row-order dependence of draws.
P3 bzk/rebuild.py _adapter_for: hard-coded quantity and localization_threshold, and the literal "unknown" search_engine.
P4 The "nothing fitted" population claim (HYPOTHESIS v10; CHECKS-convention-resolved.md).
P5 Invariant enforcement gaps I1/I6/I18; missing I12/I13 lints.
P6 PXD055843 unreachable by rebuild.
P7 Research code inside bzk/.
P8 The "12 of 14" propagation.
P9 Repo exposure and licence; HANDOFF.md staleness; "Last reviewed" headers; ROADMAP size; the Kùzu risk line.

Environment:
D30 ATTEMPT_1_DIGEST at tests/test_pxd018299_h10.py:804 fails in some environments at 3a165a4, with the tautology-sweep failure as its knock-on. It passes on a fresh pinned install at the same commit.
    - Do not diagnose it.
    - Do not re-pin it.
    - Do not add it to HANDOFF.md or any other file.

Also out of scope:
- CHECKS-two-route-recovery.md §2–§4;
- every other CHECKS/RESULT/PREREG body;
- HYPOTHESIS.md;
- all code and tests.

## 5. Commit

One commit on top of HEAD, linear. Message:
`walk: withdraw 'two routes sharing no inputs' and the supersession built on it; route 2's cells overlap route 1's inputs and reference, and its width is route 1's — correction + banner, FINDINGS §2 and :110 restated`

Re-run the full suite. The failing set must be identical to the opening state's, by node id, and the passed and skipped counts unchanged. If any Markdown-reading test newly fails, report it and do not commit.

## 6. Report, then stop

1. The opening state (all four points) and R1–R4 answers.
2. The grep hit table: path:line | class A/B | reason.
3. For every edited or created file, the diff, verbatim.
4. For each (A) home, the old wording and the new (or "listed, not edited"), quoted in full.
5. Commit hash, `git rev-list --count HEAD`, and confirmation of no merges.
6. The closing suite result, with the failing set compared by node id against the opening's.
7. Anything found that bears on items 2–12, P1–P9 or D30: listed, not acted on.

End here. Do not begin item 2.
