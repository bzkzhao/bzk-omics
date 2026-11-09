# Prompt 41 — `bzk.audit` stage 4: FINDINGS §2's second route computed, and a note that contradicts a settled erratum (revision 5)

**Repository:** `main` at the commit adding this prompt. Every line reference below was measured at
`d44da28` and is wrong by however far later commits moved the file; §0 re-measures them.

**Why revision 5.** A third audit found **no blocker**, judged the prompt executable, and named
three fixes to apply first. All three are below. One is revision 4's own: its claim that mutation
2's two shifts drive the band *together* is wrong on direction — measured over twenty seeds they
are independent in sign and **opposed on twelve**. That is the fourth consecutive revision in which
a correction carried its own defect. **These three changes have not themselves been audited.**

**Why revision 4.** A second audit of the rewrite found **no blocker** and three defects. One was a
real contradiction between two of my own instructions — §1.1 said to port section LL *as written*
while §1.3 forbade repeating the mislabel that LL's last two statements contain. §1.1 now gives the
boundary. The other two: a vocabulary definition cited one line past the clause that fixes it, and
mutation 2's guidance naming one of its two detection mechanisms.

**Why revision 3.** An independent audit of the rewrite found **one blocker** and twelve smaller
defects. The blocker is instructive: prompt 38 widened the live wrappers' handler to
`except (Exception, SystemExit)` (l.566), so a wrapper reading S1 through `_supplement_path` now
returns `NOT COMPUTED` like any other failure — which made revision 2's mutation 3
**unfalsifiable** against the test it named. A guard built two prompts ago quietly removed the
signal a later mutation relied on; §1.5 now pins the exception type instead. Eight of the twelve
others were spans of mine long or short by a line, two of them misattributing a section of the
anchor.

**Why revision 2 was a rewrite, not an edit.** Revision 1 framed this as *settling* which script
produces which route, and built its receipt check on `walk/CHECKS-two-route-recovery.md:46`. An
independent checker found five blockers, and the root cause was one miss: **the repository settled
this on 2026-09-27**, in `walk/CORRECTION-PXD018299-two-route-independence.md`, a document type
revision 1 never searched. That document also carries an **erratum against the very row revision 1
cited**. Revision 2 is anchored on the correction instead. Everything below that the correction
decides is cited to it rather than re-derived.

**The anchor.** `walk/CORRECTION-PXD018299-two-route-independence.md` (2026-09-27):

- **l.36–39 settles the attribution.** Route 1 is Check 2's *against the deposit's column* readout
  in `walk/CHECKS-PXD018299-imputation-effects.md`, computed by
  `notes/scripts/diagnose_imputation_effects.py`. Route 2 is block LL of
  `notes/scripts/diagnose_round16.py`.
- **l.14–32 withdraws the independence claim and the supersession claim resting on it** (l.8–9 fixes *withdrawn* as *false as stated*; l.10 applies the label); **l.41–81 names four dependences** between the routes.
- **l.89–98 is an erratum on the route-1 label:** the row at `CHECKS-two-route-recovery.md:46` calls
  that band *readout C* and it is not — readout C is defined in
  `walk/RESULT-PXD018299-H10-attempt2.md` §5 against S1's significant rows and is **superseded** at
  `walk/CHECKS-PXD018299-imputation-effects.md:75–77`. The same mislabel sits at
  `diagnose_round16.py:127` and `notes/logs/round16.txt:18`, **neither edited, by design**.
- **l.100–109 lists what does not change**, including both bands, the sensitivity table, the
  bootstrap standard error, and route 1's column-by-column table, each with its home.
- **l.115–134 enumerates every home of the withdrawn claims** and closes: *"No home outside
  `walk/` and `notes/` asserts the independence of these two recoveries."*

**What is wrong in `bzk/audit.py`, and it is one error and one staleness, not two errors.** Stage
4's note (l.607–616) says the two-route recovery *"is produced by
notes/scripts/diagnose_imputation_effects.py and recorded in walk/CHECKS-two-route-recovery.md"*.

- **Wrong:** the script half. That script is route 1's, per the correction l.36–39. The **document
  half is right** and survives — `CHECKS-two-route-recovery.md` is where route 2's figures live.
- **Stale:** the `NOT_AUTOMATED` label. Route 1 has been computed under `--live` since
  `8de0ea4` added `_live_whole_column_reference` (l.429). The note's *"is not in any committed
  fixture"* is literally true — no fixture holds either band — but the label claims the figures
  cannot be regenerated, and after this prompt neither can claim that.

**That drift has a named mechanism.** The correction's homes table enumerates homes of the
*independence* claim. Stage 4's note asserts a wrong *attribution*, which is a different claim, so
the table's closing sentence is true as written and the note was never in scope for it. This is
worth one line in the build's point 3, not a fix here.

**What this builds.** One pure function, one live wrapper, the key that carries it, and a rewritten
note. **Three files:** `bzk/audit.py`, `tests/test_audit.py`, and `tests/test_tautology_sweep.py`
if the new tests add asserts — its floor is the literal in the assert at l.2334 (holding `60` and
`2641`), and `PINNED` is l.206 with 342 entries. Read the live surface off `sweep()` and move the
floor by hand; `sweep()` does not return the floor.

---

## 0. Receipt check — answer, then stop and wait

**Run everything you can without the content store first, and report which of these your machine
can do.** Items 2 and 3 need the deposit bytes; the rest do not. **A missing store is not a stop
condition anywhere in this prompt** — revision 1 made that mistake, halting in §0 on the machine the
rest of it assumed. Use `.venv/bin/python`, not bare `python`: the latter lacks `kuzu`.

1. **Line references.** Report the line of each, as measured now: `stage4_imputation`;
   `whole_column_reference`; `_live_whole_column_reference`; `_live_drawn_cell_census`;
   `_cell_provided`; stage 4's `stage.not_automated = [` and the closing `]` of that assignment;
   the `against_whole_deposit_column` key and the line holding its `NOT COMPUTED` phrase; the sweep
   floor assertion with its two numbers; `PINNED`. This prompt says 570, 398, 429, 525, 512, 607 and
   616, 601 and 604, 2334 holding `60` and `2641`, and 206. Report any difference with its size.
2. **Route 1, if the store is here.** Run `.venv/bin/python -m bzk.audit --live` and report stage
   4's `against_whole_deposit_column` **per column, all six**. Compare against route 1's
   column-by-column table, `walk/CHECKS-PXD018299-imputation-effects.md:59–66`: WT_IFN_1/2/3 at
   down 1.76 / 1.77 / 1.78 and **KO_IFN_1/2/3 at down 1.49 / 1.39 / 1.51**. **Do not compare against
   "1.76–1.78" alone** — three of the six sit well below it, and `:78–80` explains why the knockout columns are noisy and not read
   into, and `:75–77` is the separate bullet superseding readout C. **Do not call this band readout C** (erratum, l.89–98).
   Storeless, report that the key says `NOT COMPUTED` with a `FileNotFoundError` and move on.
3. **Route 2's baseline, if the store is here.** Run `notes/scripts/diagnose_round16.py` to a file
   under `/tmp` and diff its `LL —` block, through the line beginning *"downshifts consistent"*,
   against `notes/logs/round16.txt`. Report the diff or that it is empty. **If it is non-empty,
   stop:** §1.4's expected values are then not the baseline. Storeless, say so and take §1.4's
   values from the log, which is the committed baseline either way.
4. **The two drawn rules are different, and that decides §1.2.** Read route 2's `provided()`
   (`diagnose_round16.py` l.67–70) and route 1's `cell()` (`diagnose_imputation_effects.py`
   l.51–57), and report whether each consults the `___1`/`___2`/`___3` sub-columns. Then report
   whether `audit._cell_provided` (l.512) matches one of them, and which. The correction's first
   dependence (l.41–54) is the account to check against.
5. **The eleven standard errors.** In `diagnose_round16.py`, report the line that computes `spread`,
   whether it is inside or outside the downshift loop, which iteration's value the script prints,
   and therefore which downshift value the log's `0.077` belongs to. Report what `WIDTH` (l.49) is
   set to and, from the correction's fourth dependence (l.77–81), where that value came from.

Then stop and wait.

## 1. Build

### 1.1 The pure function

`downshift_band(...)` in `bzk/audit.py`, beside `whole_column_reference` (l.398). No path, no file
read, so it is testable on synthetic input. It takes the comparable claims' published values, their
`drawn` flags, each claim's measured-only fold change, the per-column mean and SD, the downshift
values to scan, **the width as a given**, and a seed.

**Port LL's computation and scan as written, and split them at l.100/101** — including the draw
order and the single shared generator. The wrapper owns l.78–85 (the per-column mean and SD) and
l.89–100 (the per-claim extraction). The pure function owns **l.101–124**: the observed median, the
scan, the per-value spread, the consistency test and the band. **l.125–126 are `print` calls** —
return those two values instead of printing them; a pure function whose result is serialised to
JSON must not print. **Port nothing of l.127–128**, LL's closing sentences, which carry the *readout C* mislabel the
erratum records as deliberately unedited. §0.3's diff stops at the same place, the log's l.17. Two properties of the original are load-bearing and must survive:

- **`spread` is computed inside the loop**, once per downshift value, from the same generator the
  simulation draws from, and the consistency test at each value uses *that* value's spread.
  **Return all eleven**, keyed by downshift value. The log prints only the last, which is why
  §1.4's `0.077` belongs to downshift 2.5 and not to the scan as a whole.
- **The width is fixed, not re-derived.** `WIDTH = 0.29` (l.49) is the width route 1 recovered for
  the wild-type columns (`walk/CHECKS-PXD018299-imputation-effects.md:64–66`, read at `:71–72`).
  The correction's fourth dependence is exactly this: route 2 consumes route 1's output. The
  function takes it as an argument and must not compute it.

Consistency is `abs(predicted - observed) <= 2 * spread`, as the script defines it. Do not
substitute a confidence interval of your own.

### 1.2 The live wrapper

`_live_downshift_band(home)`, modelled on **`_live_drawn_cell_census` (l.525)** — not on
`_live_whole_column_reference`, whose signature takes a fixture and which reports no hashes. So:
never raises; on any failure returns `{"NOT COMPUTED": "<ExceptionType>: <message>"}`; reads the
sites table and Supplementary Data 1 through `verify`, **not `pxd018299_h10._supplement_path`**,
whose `SystemExit` the docstring at l.528–531 already explains; and reports the `sha256` of both
files it read.

**Reuse `_cell_provided` (l.512) for the drawn rule, and the prompt owes you the reason.** It is the
multiplicity-aware rule — summed column **or** any sub-column — which is route 2's `provided()`. It
is **not** route 1's rule, which reads the summed column alone. The correction's first dependence
(l.41–54) is why they differ and why route 2's drawn set is a subset of route 1's. So sharing this
helper is right for route 2 and would be wrong for route 1; say so in the code comment rather than
leaving a future reader to assume one rule serves both.

The comparable class is the one `drawn_cell_census` partitions at l.464–470 and emits under
`some_drawn_both_arms_measured` (the key itself is l.493). Its three-way condition is the exact
complement of `diagnose_round16.py:94`, which skips a claim with no drawn cell or a wholly drawn arm.

### 1.3 The key, and the note

`stage4_imputation` gains `downshift_band_from_fold_changes`: the wrapper's result when `home` is
given, and `"NOT COMPUTED: needs the deposit bytes; run with --live"` when it is not — the phrase
`against_whole_deposit_column` already uses at l.604.

**Rewrite the note.** Delete the `not_automated` assignment entirely if nothing true is left in it;
both routes are computed under `--live` after this build, so the label no longer applies. Three
things must land somewhere in the stage, in a `findings` key of its own, in the existing `reference_distribution`
text (itself a `findings` key, l.595), or in `limitations`, whichever reads best beside what each
qualifies:

- **The reading warning** the old note's last clause carried: the per-sample range above is this
  fixture's readout C, a different statistic that should not be read as FINDINGS §2's figure. This
  is the clause the erratum makes *more* important, not less — readout C is superseded at
  `CHECKS-PXD018299-imputation-effects.md:75–77`.
- **The document pointer**, which was the true half of the old note — but **name both homes**, since
  the stage reports both bands side by side after this build: route 2's figures live in
  `walk/CHECKS-two-route-recovery.md`, route 1's column-by-column table in
  `walk/CHECKS-PXD018299-imputation-effects.md:59–66`. The correction's closing lines (l.111–113)
  say every figure in this recovery lives in those two documents. Drop the
  `diagnose_imputation_effects.py` attribution, which is route 1's script.
- **That the two routes are not independent**, with a pointer to
  `walk/CORRECTION-PXD018299-two-route-independence.md`. Reporting both bands side by side without
  this would re-create in the audit exactly the claim that document withdrew. **Do not restate the
  four dependences** — they have a home.

**Do not carry either unedited claim — there are three homes, not two.** The erratum records that
`diagnose_round16.py:127` and `notes/logs/round16.txt:18` call route 1's band *readout C*, both
deliberately unedited. The correction's homes table (l.129) lists a **third**:
`diagnose_round16.py:14–15`, LL's own docstring, which calls route 2 *"a SECOND, independent
recovery of the parameter"* — the withdrawn independence claim itself. A port that copies LL's
docstring prose into `bzk/audit.py` would re-assert in the audit exactly what the correction
withdrew. Neither phrasing may appear in the ported code or in any string it emits.

The `limitations` line at l.617–620 about per-sample downshift hiding arm structure is unrelated and
stays.

### 1.4 Expected values — registered before the run

From `notes/logs/round16.txt` at `d44da28`, the committed baseline:

| quantity | expected |
|---|---|
| comparable claims | 43 |
| observed median gap | +1.055 |
| predicted median gap at downshift 1.0 | +0.291 |
| predicted median gap at 2.5 | +1.728 |
| bootstrap standard error **at downshift 2.5** | 0.077 |
| consistent band | `[1.7, 1.77, 1.8, 1.9]` |

`walk/FINDINGS.md` §2 quotes **five** of these six rows — all but the claim count — at l.52 and
l.59–60: rows 3, 4 and the band **rounded** (*"+0.29"*, *"+1.73"*, *"1.70 – 1.90"*), and rows 2 and
5 **verbatim** (*"+1.055"*, *"0.077"*). The log carries all six and is the home to compare against.
The bootstrap standard error also has a dated home at `walk/CHECKS-two-route-recovery.md:42`, and
the sensitivity table at `:30–40` — which carries **9 of the 11 scanned values**, omitting 1.2 and
2.2, so do not read eleven rows against it. The correction's *"what does not change"* list names
both. **A difference is reported at its size and
not adjusted.** Do not edit the expected column.

Suite, after the build: **1231 passed, 14 skipped** plus this turn's tests, on a container with no
raw store — re-measured in the reviewer's clone at `d44da28`. With the PXD018299 sites table
present, three more passing and three fewer skipped. Report which machine, and measure both ways if
the store is present.

### 1.5 Tests

In `tests/test_audit.py`, in the style of the stage 3 census tests:

1. The pure function on synthetic input: two claims, hand-computed column statistics, a fixed seed,
   and **two downshift values chosen so one is consistent at `2 * spread` and the other is not** —
   the band must therefore be a strict subset of the values scanned. Assert the observed gap, the
   band, and that eleven-style per-value spreads come back one per value.
2. `stage4_imputation(_committed())` without `home` says `NOT COMPUTED` for the new key, and still
   says it for `against_whole_deposit_column`.
3. `stage4_imputation(_committed(), tmp_path)` with no store returns a failure for both keys and
   does not raise.
4. **S1 absent, with the sites table stubbed — and assert the exact finding, not merely that it says
   `NOT COMPUTED`.** Use the stage-3 helpers `_live_inputs(...)` and `_sites_table(...)`
   (`tests/test_audit.py` l.319–359, `_INTENSITY` at l.319 included) with `s1=False`; without them
   the sites table's `verify` raises first and `_supplement_path` is never reached. **Pin the
   exception type:** assert the finding equals
   `{"NOT COMPUTED": f"FileNotFoundError: {SUPP_DATA_1.filename} is not in {tmp_path}"}`, exactly as
   the stage-3 analogue at l.362–372. **A weaker assertion cannot detect mutation 3.** Since prompt
   38 the wrapper's handler is `except (Exception, SystemExit)` (l.566), so reading S1 through
   `_supplement_path` still returns a `NOT COMPUTED` finding and still lets nothing escape — only
   the exception *name* inside it changes.
5. The same seed twice gives the same band; pin determinism, not the value.

**Mutation proof**, per `CLAUDE.md` l.97 including its cache rule — delete every `__pycache__`, then
run with `PYTHONDONTWRITEBYTECODE=1`, mutate by content, confirm each applied by reading the file
back, revert each, confirm green. Each list is a floor; report what actually failed.

1. Widen consistency from `2 * spread` to `4 * spread`: test 1's band must gain its inconsistent
   value. This is why test 1's two values must straddle the boundary.
2. Give each downshift value a fresh generator instead of the shared one: test 1 must fail.
   **Choose test 1's seed and values so it does — such a case exists**, one having been constructed
   during this prompt's audit at two claims and two downshift values. Two things make a case
   insensitive. With a fresh `default_rng(seed)` per value the **first** value's draws are identical
   to the shared run, so a case resting on the first value alone cannot move. And claims whose drawn
   cells sit in **opposite arms** give a pooled-gap median that barely responds to the downshift, so
   draw both claims' cells in the **same** arm. The sensitive window is narrow, and **the mutation moves two quantities whose effects may cancel**:
   the second value's predicted median by about 0.01, and its spread by about 0.003 — roughly 0.007
   on the `2 * spread` threshold it is compared against. **They are independent in sign.** Measured
   over twenty seeds they reinforced on eight and opposed on twelve, and cases exist that flip on
   either one alone. So do not pick a case expecting them to reinforce: **run both variants and
   confirm the band differs.** Assert the band, not either shift. If after that guidance you still cannot construct one, report it rather
   than reporting a pass as a proof.
3. Read S1 through `_supplement_path`: test 4 must fail **on the exception name in the finding**,
   `SystemExit` where `FileNotFoundError` was expected — not by anything escaping, which the
   handler prevents.

Then the sweep: classify whatever the new tests add, regenerate `PINNED` with the command in the comment at
l.201–202, run under `.venv/bin/python` (the comment itself writes bare `python`) — strip the `#: ` prefixes, the leading *"Regenerate with"* and its opening
backtick, the closing backtick, and the trailing *"**after** classifying whatever is"*, then rejoin
— and report `PINNED`'s size and the floor before and after.

## 2. Out of scope

- **FINDINGS §5 and §6** (stages 6 and 7, whose notes are at l.730 and l.778). Their attributions
  are **unverified**, and revision 1's failure is the reason to treat them as unmeasured: search
  `walk/CORRECTION-*` and `walk/CHECKS-membership-and-corrections.md` before asserting anything
  about them. A separate prompt.
- **`diagnose_round16.py` section MM**, which follows LL and needs MOESM5 and the protein groups.
- **Route 1.** `_live_whole_column_reference` is not touched. If §0.2 shows it does not reproduce
  the six column values, **report it and stop** — but a storeless `NOT COMPUTED` is not that case.
- **Every `walk/` document.** None is edited. The erratum's deliberately unedited mislabels at
  `diagnose_round16.py:127` and `notes/logs/round16.txt:18` stay as they are.
- **The eight unguarded source-readers** (prompt 39) and **the unguarded producer class** that
  prompt 40's build reported. Both open, neither this prompt's.
- Any fixture, and anything under `decisions/`.

## 3. Report

Close with the four points of `CLAUDE.md` l.96–99 (l.95 is their parent bullet):

1. Each check by name at its actual result and target: `pytest` (full suite), `pytest
   tests/test_schema.py`, `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk tests`.
   A check not run is reported as not run. State which machine and whether the raw store held
   anything.
2. The mutations, each with its confirmed application and what failed; §0's five items with which
   needed the store; and §1.4's table, expected beside observed.
3. What this did not cover, including at least: that test 1 necessarily sits within a few per cent
   of the consistency boundary, so it pins a verdict a change of numpy version could move —
   brittleness bought deliberately to make mutation 2 provable; that the band depends on the draw
   order and so on
   porting the loop faithfully; that the width is route 1's output taken as given, so the two routes
   remain dependent by construction; that §1.5's synthetic case pins determinism and shape rather
   than any published figure; and that stage 4's note drifted because the correction's homes table
   enumerates homes of the independence claim and the note asserted a wrong attribution instead.
4. Any instruction from this prompt dropped or partly done.
