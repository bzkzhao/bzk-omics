# Prompt 37 — `bzk.audit` stage 3: the §1 census and the exceeds count, computed from the pinned bytes (revision 1)

**Repository:** `main` at the commit adding this prompt. Every line reference below was measured at
`8654365` and is wrong by however far later commits moved the file; §0 re-measures them.

**Why.** `walk/FINDINGS.md` §1 quotes a census of drawn cells over the 798 published claims and an
"exceeds in 41" count. `bzk.audit` stage 3 flags both `NOT_AUTOMATED` (`bzk/audit.py` l.389–396),
so a paper cannot regenerate them from one command. Decision recorded 2026-11-08: they are
**computed**, in `--live` mode only, from hash-verified bytes. No fixture is added and no
third-party data is committed.

**What this builds.** One pure function, one never-raising live wrapper, and the wiring that gives
`stage3_census` a `home`. Nothing else. Three files are in the diff: `bzk/audit.py`,
`tests/test_audit.py`, and `tests/test_tautology_sweep.py` (its `PINNED` set, l.206, and its floor,
l.2301, move with any new test equality — §1.6).

**Where the figures come from.** The census is `notes/scripts/diagnose_round14.py` section EE,
output `notes/logs/round14.txt`. The exceeds count is `notes/scripts/diagnose_round15.py` section
II, output `notes/logs/round15.txt`. **Round 14 does not print it** — stage 3's current note names
round 14 alone, which is one script short.

---

## 0. Receipt check — answer, then stop and wait

Execute these against the repository. Do not answer from this prompt.

1. **Line references.** Report the line of each, as measured now: `stage3_census`,
   `whole_column_reference`, `_live_whole_column_reference`, the `stage.not_automated = [` of stage
   3, and the builder lambda that calls `stage3_census`. This prompt says 371, 401, 432, 389 and
   978. Any difference is reported with its size.
2. **One `SUPP_DATA_1`.** `bzk/audit.py` imports it from `bzk.sources.protein_groups` (l.47);
   `bzk/sources/pxd018299_h10.py` imports it from the same module (l.84). Confirm by running
   `python -c` that `audit.SUPP_DATA_1 is h10.SUPP_DATA_1`, and report the output.
3. **The baseline reproduces before anything is built.** On this machine, with the raw store
   present, run `notes/scripts/diagnose_round14.py` and `notes/scripts/diagnose_round15.py`, each to
   a file under `/tmp`. Diff the `EE —` block (through the line containing `PKM`) against
   `notes/logs/round14.txt`, and the `II —` block (through the line containing `absolute gap`)
   against `notes/logs/round15.txt`. Report each diff, or that it is empty. **If either differs,
   stop: §1.5's expected values are then not the baseline.**
4. **The trap.** `_supplement_path` (`bzk/sources/pxd018299_h10.py` l.1087) turns a missing file
   into `SystemExit`. Run `python -c "print(issubclass(SystemExit, Exception))"` and report it.
   State what that means for a wrapper written as `except Exception`, as
   `_live_whole_column_reference` is.

Then stop and wait.

---

## 1. Build

### 1.1 The pure function

`drawn_cell_census(...)` in `bzk/audit.py`, beside `whole_column_reference` (l.401). It takes no
path and reads no file, so it is testable on synthetic input. Per claim it receives the six
published values (KO 1–3, WT 1–3, in that order) and six booleans, `drawn`, in the same order. It
returns:

- the count of claims with **no drawn cell**; **some drawn, both arms still measured somewhere**
  (the comparable class); and **a whole arm drawn** (`all(drawn[:3]) or all(drawn[3:])`, which
  includes a claim with all six drawn);
- the count containing a drawn cell, the total, and their ratio;
- over the comparable class only: the signed gap `published − measured-only` where
  `published = mean(KO values) − mean(WT values)` and `measured-only` uses the undrawn cells of
  each arm; its quartiles; the median of its absolute value; and the count with gap `> 0`.

Port the classification and the gap arithmetic from `diagnose_round14.py` and
`diagnose_round15.py` **as written**. Do not restate them from this prompt.

### 1.2 The drawn rule

A cell is **provided** if the deposit's summed column is `> 0` **or any** of the `___1`, `___2`,
`___3` multiplicity columns is `> 0`; it is drawn otherwise. This is `provided()` in both scripts
(`diagnose_round14.py` section EE, `diagnose_round15.py` section II). The pure function takes the
booleans already computed; the **wrapper** (§1.3) computes them, and so owns this rule.

### 1.3 The live wrapper

`_live_drawn_cell_census(fixture, home)`, modelled on `_live_whole_column_reference` (l.432):

- never raises; on any failure returns `{"NOT COMPUTED": "<ExceptionType>: <message>"}`;
- reads the sites table with `verify(PXD018299_SITES.expected_content_hash ...)` exactly as l.432
  does, then `h10.anchor_population`, and matches each cascade claim to its row by
  `deposit_id` against the id column, as both scripts do;
- reads Supplementary Data 1 with `verify(SUPP_DATA_1.expected_content_hash,
  filename=SUPP_DATA_1.filename, home=home)` — **not `_supplement_path`** (§0.4) — then
  `h10._s1_rows`, `h10.s1_columns` and `h10._float_cell`;
- returns the pure function's result plus the `sha256` of each of the two files it read, so the
  report states what was read.

### 1.4 The wiring

`stage3_census(fixture, home=None)`, with the builder at l.978 passing `home if live else None`, as
l.979 does for stage 4. The findings gain one key, `drawn_cell_census`: the wrapper's result when
`home` is given, and `"NOT COMPUTED: needs the deposit bytes; run with --live"` when it is not,
the phrase stage 4 uses at l.489–491. **No mode label changes.** The existing relabelling under
`--live` (l.950) is untouched; the new key carries its own provenance.

The stage's `not_automated` note is rewritten to say only what is still not automated. Its clause
about the count of contrasts with no observed values is **left as it is**: this prompt has not
measured which script produces it. Say so in §3.

### 1.5 Expected values — registered before the run

Read from `notes/logs/round14.txt` and `round15.txt` at `8654365`; they are the recorded baseline,
not a prediction about the code.

| quantity | expected |
|---|---|
| published claims | 798 |
| no drawn cell | 40 |
| comparable (some drawn, both arms measured somewhere) | 43 |
| whole arm drawn | 715 |
| containing a drawn cell | 758 of 798 |
| signed gap, quartiles | +0.691 / +1.055 / +1.524 |
| absolute gap, median | 1.055 |
| signed gap `> 0` | 41 of 43 |

Run on this machine: `.venv/bin/python -m bzk.audit --live --out audit-live-37`. How long `--live`
takes was not measured when this was written. Compare stage 3's `drawn_cell_census` to the table.
**A difference is reported at its size and not adjusted.** Do not edit the expected column.

### 1.6 Tests

In `tests/test_audit.py`, after the whole-column tests (l.248–276, the end of the file), in their
style:

1. The pure function on a synthetic table with one claim in each class — none drawn; one KO cell
   drawn; a whole KO arm drawn; a whole WT arm drawn; all six drawn — with hand-computed counts and
   gap. The three class counts sum to the total.
2. `stage3_census(_committed())` without `home` says `NOT COMPUTED`.
3. `stage3_census(_committed(), tmp_path)` with no store returns the failure and does not raise.
4. With the sites table present and **S1 absent** (monkeypatch `verify` to raise
   `FileNotFoundError` for S1's filename only), the wrapper returns `NOT COMPUTED` and no
   `SystemExit` escapes.
5. A multiplicity-only cell (summed column `0`, `___1 > 0`) is **provided**, not drawn.

**Mutation proof, per `CLAUDE.md` l.97.** Mutate the provided rule to ignore the multiplicity
columns; confirm the mutation applied by reading the file back; confirm test 5 fails and name the
failure message; revert; confirm green. Do the same for the class split (swap `all(drawn[:3])` for
`any`) against test 1. Never take the exit status alone.

**The tautology sweep.** `tests/test_tautology_sweep.py` pins every equality in every assert under
`tests/`. After adding the tests, run it, classify the new equalities as its failure message
instructs, and regenerate `PINNED` with the command in the comment at l.201–202 **after**
classifying. Report the floor before and after (l.2301 holds it now: `60` and `2612`). The floor
moves by hand; do not guess its new value.

---

## 2. Out of scope

- **§2 route 2** (`diagnose_round16.py`, section LL) and stage 4's stale note: prompt 38.
- **§5 and §6** (stages 6 and 7): their source attribution is not verified either. Not this prompt.
- Round 15's imputation simulation, round 14's FF, GG and HH sections, and the PKM line. None is a
  FINDINGS §1 figure.
- Any fixture, any change to `notes/scripts/` or `notes/logs/`, and any edit to `walk/FINDINGS.md`.
  FINDINGS §1 says the published figure exceeds the measured-only one "in 41 cases, by a median of
  1.055"; the 1.055 is the median over all 43 comparable claims, not over the 41. **Report it; do
  not fix it.**
- The Mac measurements of the non-finite probe, and anything in `maxquant_sites.py`.

---

## 3. Report

Close with the four points of `CLAUDE.md` l.95–99:

1. Each check by name at its actual result and target: `pytest` (full suite), `pytest
   tests/test_schema.py`, `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk
   tests`. A check not run is reported as not run.
2. The §1.6 mutations, each with its confirmed application and its failure message; and the §1.5
   comparison table, expected beside observed.
3. What this did not cover: at least that the contrasts-with-no-observed-values clause is
   unmeasured, that only fixture mode is exercised in CI, and whether the live path was run here.
4. Any instruction from this prompt dropped or partly done.
