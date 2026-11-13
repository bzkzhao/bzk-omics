# Prompt 43 — Land ADR-0041 (Proposed) and verify its claims against the repository

**Repository:** `main` at the commit adding this prompt and the draft
`notes/drafts/0041-a-registered-headline-moves-only-through-hypothesis.md`. Line references were
measured at `aec062e`.

**What this is.** bzk decided on 2026-11-13 that a registered headline moves only through a versioned
HYPOTHESIS restatement, and that H10's stays at the registered 751 denominator. ADR-0041 records
that decision.

This prompt **lands the record as `Proposed` and measures its claims**. The record's
*Consequences*, the `walk/` and `bzk/audit.py` edits, are described in it and not made here. They
are the next prompt, after the record's review round trip (`decisions/README.md`).

**Files this prompt touches:**
- the record: the draft moves into `decisions/`;
- `decisions/README.md`: the Written table, one row;
- `tests/test_decision_index.py`: the pins.

---

## 0. Receipt check — answer, then stop and wait

Quote from the file or from git, never from this prompt. **Stop on any mismatch.**

**(a) State.**
- `git log --oneline -2` shows this prompt's commit with `aec062e` beneath it.
- `git status --short` is empty.
- After `uv sync --frozen`, `pytest -q` reads 1292 passed / 15 skipped.

**(b) The decision index.** `tests/test_decision_index.py` holds these pins:

| pin | value | line |
|---|---|---|
| `EXPECTED_FILES` | 39 | `:52` |
| `EXPECTED_WRITTEN_ROWS` | 39 | `:53` |
| `EXPECTED_QUEUED_ROWS` | 1 | `:54` |
| `EXPECTED_SEED_LINES` | 18 | `:55` |
| `EXPECTED_SEED_STRUCK` | 17 | `:56` |
| `EXPECTED_STATUSES` | `{"Accepted": 27, "Proposed": 9, "Superseded": 3}` | `:79` |

The dated history comment above `EXPECTED_STATUSES` is at `:58-78`. `decisions/` holds 39 records,
0001–0040 except 0018, and no 0041. The Written table's last row is 0040 (`decisions/README.md:93`).

**(c) The draft's citations.** Quote each at the line given, or say where it is now.

| # | where | expected |
|---|---|---|
| C0 | `walk/CHECKS-convention-resolved.md:5-7`, `:45`; `HYPOTHESIS.md:84-85` | "this supersedes the *level*"; 209 of 751 = 27.8%; v10 citing that file as the restatement's home |
| C1 | `walk/PREREG-PXD018299-H10-attempt3.md:6-8`, `:81-82`, `:76`, `:70`; `walk/PREREG-PXD018299-H10-attempt2.md:6-13` | attempts 1 and 2 still governing attempt 3 except where it replaces them; the shares over claims with an imputed value; the verdict "from the primary only"; "the share over all claims" among readout B's items; attempt 2 keeping attempt 1's §6 readouts unchanged |
| C2 | `walk/PREREG-PXD018299-H10.md:179-181` | H10's primary over claims whose row carries at least one imputed value |
| C3 | `walk/PREREG-PXD018299-H10.md:182-184` | the 5% / 1% thresholds |
| C4 | `walk/PREREG-PXD018299-H10.md:186-187` | "Reported, never the headline", then "the same share over all claims" |
| C5 | `HYPOTHESIS.md:39-41`, `:43-46` | v10's trigger; H10's level at 27.8% (209 of 751); 21.2% "superseded, not withdrawn" |
| C6 | `HYPOTHESIS.md:22-23`, `:30-33`, `:904-909`, `:918-919`, `:1018` | amendments recorded with their trigger; "What this document is not:** a home for measured numbers"; the primary over claims with an imputed value; "Reported, and never the headline …"; the pre-registration fixing the population; 751 of 791 testable, 7 of 798 untested |
| C7 | `walk/CHECKS-collateral-and-pkm.md:13`, `:15-17`, `:24`, `:25`, `:29-30`; `notes/logs/round13.txt:6` | "The denominator was wrong"; round 12's mechanism; 209 of 751; "all published claims" for 210 of 791; "26.5% is the figure with the right denominator; 27.8% is superseded as the headline"; "instability over claims with an imputed value: 209 of 751 (27.8%)" |
| C8 | `walk/FINDINGS.md:109-111` | §5's three rows: 210 of 791 (26.5%), 38.3%, 13.7% |
| C9 | `walk/CHECKS-census.md:62`, `:70`, `:119-122` | "published claims inside it" over `of 791` cells; "of all published claims"; 26.5% "of published claims"; "the registered result and the answer to H10" |
| C10 | `walk/CHECKS-membership-and-corrections.md:8-13`, `:39-41`, `:43`, `:57-59` | the two-word vocabulary; "What survives"; the withdrawn "nothing fitted" claim and the correction under it |
| C11 | `HYPOTHESIS.md:5`, `:48-49`, `:637-638`, `:1203` | "nothing fitted" still stated; 781 against 798 at `:48` |
| C12 | `bzk/audit.py:90`, `:99`, `:103`, `:1069`, `:1096-1102`; `tests/test_audit.py:1270`, `:1560` | `RECEIPT_MAP`'s order comment and start; its "share of all published claims" describes; "The registered estimand, not a headline"; stage 6's item naming the all-claims population "the population of the section 5 headline"; `check_note`'s "What it does not establish"; `len(six.not_automated) == 9` |
| C13 | `walk/CHECKS-draws-and-threshold.md:15`, `:17`, `:19`; `walk/CHECKS-ceiling-survives.md:70`, `:71` | the header "unstable, of claims with an imputed value", 27.8% at 20 draws and 38.3% at 100 draws; 13.7% (103 of 751); 27.8% (209 of 751) "H10's level as reported" |

**(d) No other record decides this.** Run
`git grep -n -i -E "headline|pre-regist|PREREG" decisions/`. Report what it returns, and whether any
record decides who may move a registered headline.

**Do not start §1 until bzk replies.**

---

## 1. Land the record

1. `git mv` the draft to `decisions/0041-a-registered-headline-moves-only-through-hypothesis.md`.
   If 0041 is taken, use the next free number, and change only the number, everywhere it appears:
   the filename, the record's text, the README row and the history line. Record the change under *Landing verification*.
2. Status stays `Proposed`. Make no other edit to the decision text. If §0 forces a correction,
   leave the body unchanged: the *Landing verification* entry quotes the wrong text struck, with its
   correction beside it and the check that forced it.
3. Add this Written row after 0040's in `decisions/README.md`:

   ```
   | [0041](0041-a-registered-headline-moves-only-through-hypothesis.md) | A registered headline moves only through a versioned HYPOTHESIS restatement; H10's stays at the registered denominator |
   ```

   Do not touch README's dated round-trip count ("against the 39 records"): it is a 2026-11-11
   measurement.
4. **Make the index guard fail first.** Before each run below, delete every `__pycache__`
   (`find . -name __pycache__ -prune -exec rm -rf {} +`) and run with `PYTHONDONTWRITEBYTECODE=1`
   (`CLAUDE.md:97`). Read each changed pin back from the file before re-running. With the record and
   row in place and the pins unchanged, run `pytest -q tests/test_decision_index.py`. Expect **exactly two** failing tests, and report both
   messages verbatim:
   - `test_every_parser_finds_its_table` at `:164`, `assert 40 == 39` (`EXPECTED_FILES`).
     `EXPECTED_WRITTEN_ROWS` is the next assert in the same test, so this failure masks it.
   - `test_every_status_is_one_of_the_three_named_values` at `:233`,
     `{'Proposed': 10} != {'Proposed': 9}`.

   Then move `EXPECTED_FILES` alone to 40 and re-run. Expect exactly two failures again:
   `test_every_parser_finds_its_table` at `:165`, `assert 40 == 39` (`EXPECTED_WRITTEN_ROWS`), and the
   status test at `:233` exactly as before. If anything else fails at either run, stop.
5. Move the remaining pins:
   - `EXPECTED_WRITTEN_ROWS`: 39 → 40;
   - `EXPECTED_STATUSES`: `{"Accepted": 27, "Proposed": 10, "Superseded": 3}`.

   The queued and seed counts do not move, because 0041 is not in `ARCHITECTURE.md` §5's seed list.
   Confirm that from §5 rather than from this sentence.

   Add the history lines after `:78`, wrapped at 100 columns and with backticks as in `:73-75`:

   ```
   #: 27/9/3 -> 27/10/3 on <landing date>: ADR-0041 landed `Proposed` (prompt 43). `EXPECTED_FILES` and
   #: `EXPECTED_WRITTEN_ROWS` moved 39 -> 40 with it; the queued and seed counts did not, since 0041
   #: is not in `ARCHITECTURE.md` §5's seed list.
   ```
6. Re-run the index tests. Do not commit yet: §2 adds to the record first, and §2's last step
   commits.

## 2. Landing verification

Insert `## Landing verification` immediately before `## Open questions`, so that Open questions stays
at the end of the file (`CLAUDE.md:92`). It is a new section, not an edit to the decision text, with
one entry per item. Each entry gives
three things:
- the command;
- its output, verbatim or the tail where long;
- a verdict: **holds**, **corrected** (with the correction, struck rather than deleted) or **not
  measurable here** (with the reason).

**Last step of §2:** re-run the index tests, `tests/test_command_blocks.py` and the full suite. Then
commit once, to `main`: the rename and the two edited files.

`tests/test_command_blocks.py` scans `decisions/*.md`. In a fenced shell block, set every variable it
uses, or present the output as plain text.

| # | claim in the record | measure |
|---|---|---|
| V1 | Every line reference in the record | C0–C13 of §0(c), re-run on the landed file. List any reference in the record that no C row covers |
| V2 | "Both figures are far above the 5% 'recurs' threshold" | 27.8% and 26.5% against C3 |
| V3 | "HYPOTHESIS does not change … It reports no 26.5% figure" | C5 and C6. Also `grep -cF "26.5" HYPOTHESIS.md`, expected 0 |
| V4 | Row 2 is over the 751 with no numerator in its home; row 3 is 103 of 751 | C13 |
| V5 | "All three of its pre-registrations", attempt 2 by inheritance | Quote `walk/PREREG-PXD018299-H10-attempt2.md:6-13`, and C1, C4 |
| V6 | Stage 6 computes attempt 3's halved variant; `registered_primary` marks `conditional_on_imputation` | `python -m bzk.audit --out <tmp dir> --json` (fixtures only). From the entry of `stages` with `stage == 6`, print `findings`' `registered_variant`, `registered_primary`, `over_all_claims` and `conditional_on_imputation` |
| V7 | Stage 6's note and `RECEIPT_MAP` change with §5 | `grep -n "section 5 headline\|the headline's" bzk/audit.py`, expected `:1097` and `:1101`; `grep -c "209 of 751" bzk/audit.py`, expected 0 |
| V8 | Every site *Consequences* must reach is named in it | `git grep -n -F -e "26.5%" -e "210 of 791" -e "210/791" -e "right denominator" -e "denominator was wrong" -e "superseded as the headline" -- "*.md" "*.py" "*.txt"`, then `git grep -n -i -F "all published claims" -- "*.md" "*.py" "*.txt"`, then `git grep -n -F -e "of 791" -e "791 claims" -- "*.md" "*.py"`, keeping only hits whose label calls the 791 "published claims" and dropping the rest. Exclude ADR-0041's own hits. Classify each remaining hit: named in *Consequences*; reports the figure without calling it H10's result (stays under (b)); an execution record (`notes/logs`, `notes/scripts`); a prompt (`notes/prompts`); or a dated reviewer record (`notes/`). List any hit outside all five |
| V9 | "It supersedes nothing" | §0(d), with ADR-0041's own hits excluded |

## 3. Out of scope. Do not touch.

- **The record's *Consequences*:**
  - the corrections to `walk/CHECKS-collateral-and-pkm.md:29-30` and `walk/CHECKS-census.md:119-122`;
  - FINDINGS §5's three rows;
  - stage 6's note and `RECEIPT_MAP`.

  They are the next prompt, after the review round trip.
- **The record's Open questions**, including reviewer defect P4. Do not answer them.
- `HYPOTHESIS.md`, every `walk/` file, `bzk/`, and every test except `tests/test_decision_index.py`.
- `notes/REVIEWER-DEFECTS.md`, `notes/REVIEWER-MAP-findings-5-and-6.md` and every handoff. If you
  find one contradicting the repository, **raise it; do not edit it**.

## 4. Report

Give the four-point close (`CLAUDE.md:95`). Name each check at the version it actually ran, with its
target stated, including `pytest tests/test_schema.py` run separately. Then report:

1. The landed path and its commit.
2. §0 and V1–V9 as a table: claim, verdict, one line of evidence.
3. The failure messages from §1 step 4, verbatim, both runs.
4. Every correction made under *Landing verification*.
5. Anything the record asserts that §2 did not reach.
