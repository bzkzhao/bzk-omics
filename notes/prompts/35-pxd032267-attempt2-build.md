# Prompt 35 — Build attempt 2 of the PXD032267 gate

**Repository:** `main` at the commit adding this prompt.

**What this builds.** The changes `walk/PREREG-PXD032267-gate-attempt2.md` §6
requires, and nothing else. The attempt-2 registration is **final**: once a
readout has been computed on the real data, no defect can be corrected. So this
build is the last point at which a mistake is cheap. Treat every gap you find
as a finding to report, not something to smooth over.

**Governing:**
- `walk/PREREG-PXD032267-gate-attempt2.md`, in full. Where it and this prompt
  disagree, the registration wins, and the disagreement is reported.
- `walk/PREREG-PXD032267-gate.md` (attempt 1), for everything attempt 2 carries
  over.
- `walk/RESULT-PXD032267-gate-attempt1.md`, and the committed attempt-1 fixture
  `tests/fixtures/pxd032267_gate.json`. **Neither is edited or overwritten.**
- `CLAUDE.md`'s four-point close.

**Settled ground.**
- Prompt 34's build (`18e6e41`) and the digest pin (`c1f23e1`) are in place.
  Attempt 1 ran at `c1f23e1`, and its result is committed at `02251d0`.
- **No readout has ever been computed on this deposit.** Nothing in this turn
  may compute one: real data is not available in the container, and `main()`
  is not run.

**Edits are limited to:**
- `bzk/sources/pxd032267_gate.py`;
- `tests/test_pxd032267_gate.py`;
- `tests/test_tautology_sweep.py`, for classifications and the floor only.

No other file. Nothing under `walk/`, `notes/` (other than this prompt) or
`data/`. Neither fixture is touched.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **State.**
   - Run `git log --oneline -3` and `git status --short`. HEAD should be this
     prompt's commit, with a clean tree.
   - Run `uv run pytest`, `uv run pytest tests/test_schema.py`,
     `uv run mypy bzk tests`, `ruff check bzk tests` and
     `ruff format --check bzk tests`.
   - Expected **in a container:** `1066 passed, 14 skipped`; `Success` over 124
     files; ruff clean. bzk's Mac reports `1072 passed, 8 skipped`.
2. **The registration's changes, verbatim.** Quote attempt 2's §2 *Change 1*
   and *Change 2* paragraphs, §3's three numbered checks and its *A failure in
   §3 is an instrument fault* paragraph, and §6 in full.
3. **Where each change lands.** With line numbers at HEAD, give:
   - `values_matrix`, and say which value it returns that rounding would
     apply to;
   - the lines in `run()` where the gate is computed and where readouts are
     dispatched;
   - `main()`'s signature, and the fixture path it writes.

   Say whether, today, anything other than an `if gate["status"] ...` test
   stands between the gate and the readouts. Expected: nothing.
4. **The attempt-1 fixture.** Report its `gate_g.status`, `gate_g.gate_rows`,
   `gate_g.input_check.rows[*].abs_delta`, `valid_value_rule.taken`,
   `valid_value_rule.rows_reaching_imputation`, the joined ids,
   `sites_content_hash`, `parameters_content_hash` and
   `generated_under.commit`.
   - Expected: `input_not_reproduced`; three rows; deltas of about 1.8e-6,
     1.1e-5 and 3.0e-5; taken 3; 1,131 rows; ids 57, 151, 281, 405, 553, 901,
     1252, 1270, 1276, 1282; the two pinned digests; and `c1f23e1`.
5. **Rounding semantics.** The registered operation is **numpy's `round`**
   (attempt 2, l.55), whatever it does. Show on a short example:
   - NaN stays NaN;
   - `np.round(1.00005, 4)` and `np.round(0.00015, 4)`.

   numpy scales, rounds and unscales, so at four decimals it is **not**
   textbook half-to-even on decimal halves. Report what it does. **Do not
   replace it with `Decimal` or any other rounding;** the registration names
   `np.round`. Then state where rounding must be applied so that it reaches
   the input check, the gate, the valid-value rule, imputation and every
   readout, readout D's masked re-preparation included, while drawn values
   are **not** rounded.
6. **Who calls what today.** List every test that calls `readouts_for`,
   `readout_a`, `readout_b`, `readout_c` or `readout_d` directly, with line
   numbers. List every call site of `run()`. Expected: `readout_d` at l.542
   and `readout_b` at l.662 in the tests; `_run` at l.384 as the only
   `run()` call.
7. **The exploratory script.** Quote
   `notes/scripts/explore_pxd032267_gate_only.py` l.23–24, and say what §1.3
   below does to it.

**Do not start §1 until bzk replies.**

---

## 1. Build

### 1.1 The attempt switch

- **Constants**, each citing its registration line, held in
  `types.MappingProxyType` so assignment raises:
  - `ATTEMPT_ROUNDING_DECIMALS = {1: None, 2: 4}`;
  - `ATTEMPT_INPUT_TOLERANCE = {1: 1e-5, 2: 5e-7 + 1e-9}`.

  The guard test parses `5e-7` and `1e-9` separately from attempt 2's l.64
  and compares their **sum**. `5e-7 + 1e-9` is not the float `5.01e-7`.
- **`run()`** takes `attempt: int` with **no default**, and
  `reference_fixture: Path` defaulting to the committed attempt-1 fixture,
  `tests/fixtures/pxd032267_gate.json`. The reference is injectable so that
  synthetic tests can supply their own; that is a bypass route, and §3 lists
  it.
- **`main()`** takes `--attempt {1,2}`, **required**:
  - **`--attempt 1` refuses to run if `tests/fixtures/pxd032267_gate.json`
    exists**, which it does. Attempt 1 is on the record and is never
    re-written.
  - **`--attempt 2` refuses if `tests/fixtures/pxd032267_gate_attempt2.json`
    exists, or if the readouts-started marker exists.** A completed attempt-2
    fixture is never overwritten (§5 of the registration).
  - **The readouts-started marker.**
    - `run()` takes an `on_licence` callback, called once, immediately after
      `ConsistencyPassed` is minted and **before the first readout call**.
    - Under `--attempt 2`, `main` passes one that writes
      `tests/fixtures/pxd032267_gate_attempt2.started.json`: timestamp,
      commit, digests.
    - **Any exception after that point** is written into the marker by
      `main`, not into the faults file, and the run ends. **So is every
      readout completed before the exception.** `run()` writes each block
      into a **caller-supplied dict** (`run(..., output=out)`) as it
      completes, and `main` writes whatever that dict holds. §5 says a defect
      found once readouts exist is *"reported"*, so nothing computed may be
      lost.
    - A crash after readouts were computed in memory therefore still leaves a
      record and blocks a repeat. That is §5's *"once a readout has been
      computed"*, made physical.
    - A test raises inside readout D and proves three things: the marker
      holds the exception, it holds readouts A–C as completed, and the refusal
      that follows.
  - Both refusals happen before any computation, and both are tested.
- **Attempt-2 fixture header:**
  - `registration` = the attempt-2 registration path;
  - `governing_registration` = attempt 1's;
  - `attempt` = 2, `rounding_decimals` = 4, `input_tolerance` = 5e-7 + 1e-9;
  - the label (§1.5);
  - `reference_fixture` and its sha256;
  - the rest as attempt 1's header.

  Attempt 1's header code is unchanged.

### 1.2 Rounding (Change 1)

- In `run()`, immediately after `values_matrix`, rebind
  `matrix = np.round(matrix, decimals)` when decimals is not `None`. Everything
  downstream reads that rebound name, readout D's masking at its current l.1062
  included. Nothing after imputation rounds again.
- **Attempt 1 is unchanged.** The proof: with `attempt=1`, every existing
  attempt-1 test passes with its **assertions unmodified**. The only permitted
  edits to existing tests are:
  - adding `attempt=1` at `run()` call sites;
  - passing a licence where §1.4 requires one: the direct `readout_d` and
    `readout_b` callers listed in §0.6;
  - passing `decimals=None` at the direct `readout_d` call (tests l.542) and at
    any direct `prepare()` call.

  Any other change to an existing test is reported, test by test.

### 1.3 The input tolerance (Change 2)

`gate_g` takes `input_tolerance` as a **required** keyword and no longer reads
any module global.
- `INPUT_TOLERANCE` **stays** as the attempt-1 constant, with its existing
  guard (tests l.59–61, pinned in the sweep) unchanged.
- `ATTEMPT_INPUT_TOLERANCE[1]` is defined **as** `INPUT_TOLERANCE`, not as a
  second literal.

**This breaks `notes/scripts/explore_pxd032267_gate_only.py`**, which assigns
the global and calls `gate_g` without the new keyword, so it now raises
`TypeError`. That is intended. The script is a
record of what ran at `c1f23e1`, cited by sha256, and it reproduces at
`02251d0`, not at HEAD. **Do not edit it.** The report says so.

### 1.4 The §3 consistency checks, made structural

The registration says *"a readout function that runs before §3 has passed is
a defect"*, and that the order is *"structural, not incidental"*.

**Readout licences.** Every readout entry point takes a **required positional**
`licence: ReadoutLicence` as its first argument. The entry points are exactly
`readouts_for`, `readout_a`, `readout_b`, `readout_c` and `readout_d`. Helpers
that compute no readout on their own (`support`, `run_members`,
`readout_a_verdict`) take none; say so in their docstrings.

`ReadoutLicence` has two kinds:
- **`Attempt1Status`:** minted by `_mint_attempt1`, called only from `run()`'s
  attempt-1 branch, and only when decimals is `None` and gate status is
  `passed` or `not_separated`. This is attempt 1's existing path, unchanged in
  behaviour.
- **`ConsistencyPassed`:** minted by `_mint_consistency`, called only from
  `consistency_checks(...)`, which only `run()` calls, only when
  `attempt == 2` and all three checks hold.

Each licence records, at minting, the attempt and the rounding decimals it was
minted for.

**The runtime match check.** `Prepared` gains a `decimals` field. `prepare()`
and `readout_d()` each take `decimals` as a **required keyword**, and
`readout_d` passes it on to the `prepare()` call it makes internally.
- `readouts_for` and `readout_d` compare the licence's recorded decimals with
  the decimals of the data they receive, and raise `InstrumentFault` on a
  mismatch.
- `readout_a`, `readout_b` and `readout_c` receive support arrays, not a
  matrix, so they take the licence for mypy's sake only, with no runtime
  check. Their docstrings say so.
- Never infer the decimals from the values.

**What can and cannot be enforced, stated honestly.**
- **mypy can enforce** that no readout is called without a licence. Show the
  error on a scratch file **in `/tmp`**, then delete it.
- **mypy cannot enforce a private constructor.** Make forging require naming a
  private symbol (`_mint_attempt1`, `_mint_consistency`). Add one test-only
  factory, `licence_for_tests(attempt)`.
- **A guard test** greps `bzk/`, `tests/` and `notes/scripts/` and fails if
  either `_mint_*` name appears outside the module's definitions and call
  sites and the factory. It **excludes `notes/prompts/`**, which names them in
  prose, and **builds its search pattern from parts**, so its own source does
  not match. A test may use the factory **only** in direct readout-function
  tests; `run()`-level tests never use it.

**The three checks (attempt 2, §3), all evaluated and all recorded.** Every
check runs even after one fails, so the output shows every failure, not just
the first.
1. **Attempt 1 reproduced.** Against the reference fixture: both digests,
   the joined ids, `valid_value_rule.taken` and `rows_reaching_imputation`.
   Read them from the fixture; never copy them into the module.
2. **The input check passes on the reference fixture's three gate rows.** The
   gate-row labels must equal the reference's `gate_g.gate_rows`, three of
   them, and all must pass at `ATTEMPT_INPUT_TOLERANCE[2]`.
3. **Gate G passes, with T1 the only passing variant.** Each variant's max
   |Δp| is recorded beside the exploratory value. The exploratory values are
   parsed from the verbatim block in `walk/RESULT-PXD032267-gate-attempt1.md`
   by a guard test, never retyped, and **never tested against**.

**What is recorded:**
- The attempt-2 output carries a `consistency` block: each check's inputs,
  result and reason.
- On any failure, `consistency_checks` raises `InstrumentFault` carrying that
  block, and **no licence exists**. `main --attempt 2` then appends the block,
  timestamped, to `tests/fixtures/pxd032267_gate_attempt2_faults.json`, and
  writes **no** attempt-2 fixture.
- **Earlier failures under attempt 2** (pinning, join) raise `GateError`
  before §3. **[reading]** Registration l.97–101 defines a *§3* failure as an
  instrument fault. Pinning and join failures come earlier, no readout exists
  when they happen, and the same logic applies, so they are treated the same
  way. `main` records them in the same faults file, and the report lists this
  reading. Attempt 1
  is unchanged.
- **[reading]** The registration says *"the run's output records every §3
  failure and fix"* (l.100–101). The faults file records the failures. A fix
  is code, so it is recorded by the commit that makes it. Each fault entry
  gains `fixed_by_commit`, filled in by that commit, and the report lists this
  reading.
- **The faults file is committed with the build fix, before any repeat run,**
  so the repeat starts from a clean tree. `_commit()` counts untracked files,
  so an uncommitted faults file would record `working_tree_clean: false`.

### 1.5 Labels

Every attempt-2 output block carries this label, verbatim:
`"second attempt, after a registration defect; test identified exploratorily"`.
That covers readouts A–D, their secondaries, the consistency block and the
fixture header.
- It is parsed from the attempt-2 registration, §4 (l.123–124), not retyped.
- It is italic there and **wraps across a line break**, so the parse
  normalises whitespace. A literal single-line match finds nothing.

### 1.6 Tests, synthetic only

At minimum:
- every existing attempt-1 test passes with its assertions unmodified (§1.2);
- under attempt 2, rounding reaches:
  - the input check;
  - the valid-value rule;
  - imputation's input;
  - **readout D's masked matrix**;

  and drawn values carry more than four decimals;
- **each check fails on its own twin, and all three fail together**, with all
  three recorded. A counting spy on every licence-taking function records
  **zero** calls. No licence is minted;
- the T1-only check fails when a second variant also passes;
- check 2 fails when the twin's gate rows differ from the reference's, even if
  all pass. This needs a **new twin with three gate rows**; the existing twin
  has two (tests l.300–316). Build it, and leave the old one unchanged;
- a readout given an attempt-1 licence over a four-decimal matrix, or the
  reverse, raises `InstrumentFault`;
- the `_mint_*` guard fails on a planted use outside the allowed sites;
- `main --attempt 1` refuses because its fixture exists; `main --attempt 2`
  refuses when its fixture exists;
- the label appears on every attempt-2 block;
- both new constants and the label are parsed from the attempt-2
  registration, with the tolerance as a sum;
- the `MappingProxyType` constants refuse assignment.

**Mutation-prove four, with `PYTHONDONTWRITEBYTECODE=1`:**
- the rounding placement;
- the spy test;
- the T1-only check;
- the `_mint_*` guard.

Classify new matches in the tautology sweep by its own procedure, and
re-denominate the floor.

## 2. Out of scope — do not do these, and report if tempted

1. Running `main()`, fetching, or computing anything on real data.
2. Editing either registration, the attempt-1 result or either fixture.
3. Changing any attempt-1 behaviour, constant or output.
4. Any change not traceable to attempt 2 §2, §3 or §6.
5. Restating or adjusting expectations Y4–Y8.

## 3. Report

Close with `CLAUDE.md`'s four points, with checks named with their targets. Then
add:
- the mutation evidence;
- the sweep classifications;
- **how the structural guarantee could still be bypassed.** Name every route
  you can find, and say which are closed and which are only documented. At
  least: `object.__new__`, the test factory, the injectable reference fixture,
  and module globals;
- that `notes/scripts/explore_pxd032267_gate_only.py` no longer runs at HEAD
  and reproduces at `02251d0`;
- every place the registration needed a reading, quoted.
