# Prompt 39 — the handler guard is vacuously green: synthetic sources it must catch and must not catch (revision 4)

**Repository:** `main` at the commit adding this prompt. Every line reference below was measured at
`c8a104e` and is wrong by however far later commits moved the file; §0 re-measures them.

**Why revision 4.** A third independent audit of revision 3 found **no blocker** and six
inaccuracies, all presentational or under-specified, plus one latent defect worth more than its
rating: `ast.walk` is breadth-first, so an extracted function that returns handler lines unsorted
comes back out of source order on a mixed-depth source. §1.1 now requires sorting. All seven are
fixed below. That audit implemented the build end to end, reproduced the measured table, the 13-and-4
scope count, the skip attribution and all four mutation consequences, and found the sweep claim
correct and sharper than stated — the pin moves by exactly two.

**Why revision 3.** A second independent audit of revision 2 found **no blocker** and six
inaccuracies, five of them in revision 2's own rewritten text: a body cited by its logic's span, a
function cited as its parse line, a set count one short of what §1.3 orders, a rejected finding
whose conclusion held but whose premise did not, and two consequences stated incompletely. All six
are fixed below. That audit reproduced revision 2's measured table, its scope count of 13 and 4, its
two-function design and its rejection's conclusion, all of which stand.

**Why revision 2.** An independent checker found **three blockers** in revision 1, and the worst was
that its premise was backwards. Revision 1 claimed the guard would pass with `_caught` returning an
empty set; it **fails**, because the non-empty check at l.419 fires. Revision 1's §0.3 would
therefore have halted the build at its own stop condition. The gap is real but it is the opposite
shape, measured below. Revision 1 also under-counted the source-reading guards by ten and specified
one extracted function where two are needed. One finding was re-measured and rejected; see §4.

**Why.** Prompt 38 added an AST guard over `bzk/audit.py`'s exception handlers
(`tests/test_audit.py` l.407). On a clean module its `offending` list (l.420) is empty **whether the
rule works or not**, so the guard cannot tell "the rule holds" from "the rule is broken". Its
non-empty check (l.419) closes one half of that — a rule that suddenly matches *nothing* is caught,
because `handlers` (l.414–418) is filtered by the same `_caught` the rule uses. Nothing closes the
other half: a rule that accepts *everything* passes silently.

**Measured at `c8a104e`, each with every `__pycache__` deleted and `PYTHONDONTWRITEBYTECODE=1`:**

| mutation of `_caught`'s logic (l.401–404; its body including the docstring is l.398–404) | guard |
|---|---|
| `return set()` | **fails**, on l.419's non-empty check |
| `return {"Exception", "SystemExit"}` unconditionally | **passes** — silent |

The second is the blind spot: handlers stay non-empty, every one looks compliant, and `offending`
is empty for the wrong reason. It is the vacuous-pass shape this repository already names — a check
reporting clean because it never really ran, which `tests/test_tautology_sweep.py` exists to catch
in another form. The only evidence the rule fires is a mutation from prompt 38's build, in a report
**not committed to this repository**, and that build showed such a run can give a false pass through
the bytecode cache. `CLAUDE.md` l.97 now requires synthetic cases for a guard that reads source.
This prompt supplies them.

**Scope is one guard, and the eight others are out of scope by decision, not by absence.** There are
**13** `ast.parse` call sites under `tests/`. **Four** are fed synthetic sources and are untouched
here, each cited at its `def` with its own `ast.parse` line beside it: `candidates`
(`tests/test_maxquant_sites_composition.py` l.132, parse at l.135; its rule wrapper
`bindings_outside_compose` is l.169) with `CAUGHT` l.223 and `UNCAUGHT` l.250; `violations`
(`tests/test_audit_pxd032267.py` l.543, parse at l.547) with planted cases parametrized at l.605,
whose literals begin at l.608;
`_licence_site_violations` (`tests/test_pxd032267_gate.py` l.920, parse at l.945) with
`test_the_licence_site_guard_fails_on_planted_uses` l.976; and `analyse`
(`tests/test_tautology_sweep.py` l.152, parse at l.164) with `PLANTED` l.2345. The handler
guard is first because `CLAUDE.md` l.97's rule was written for it and because it is the newest. The
remaining eight are a known, unclosed class — §3 point 3 records them.

**What this builds.** **Two** extracted functions, **three** synthetic sets — §1.3 orders one per
question, and the third, for `exception_handlers`, fits neither of the other two's shapes — their
parametrized tests, and the guard rewritten to call both functions. **One file: `tests/test_audit.py`** — plus
`tests/test_tautology_sweep.py`, whose `PINNED` (l.206) and floor (l.2319) may move as §1.4
describes. `bzk/` is not touched at all.

---

## 0. Receipt check — answer, then stop and wait

Execute these against the repository. Do not answer from this prompt.

1. **Line references.** Report the line of each, as measured now: `_caught`; the first and last line
   of its **body** (docstring included) and of its **logic** alone; the guard `test_every_handler_that_catches_exception_also_catches_system_exit`; its
   `assert handlers` line; its `offending = [...]` line; the end of `tests/test_audit.py`; `PINNED`;
   the sweep floor assertion with its two numbers. This prompt says 397, 401–404, 407, 419, 420,
   456, 206 and 2319 holding `60` and `2632`, with `_caught`'s body at 398–404 and its logic at
   401–404 — a span that **excludes the local `import ast` at l.399**, which is executable, so a
   mutation replacing only 401–404 leaves it unused and `ruff` would flag it on a mutated tree.
   Report any difference with its size.
2. **The source-reading guards, counted.** List every `ast.parse` call site under `tests/` and for
   each say whether synthetic sources are fed to the rule it serves. Report the total, how many are
   fed, and any disagreement with the four this prompt names. This prompt says 13 sites, 4 fed.
3. **Reproduce the blind spot, both halves**, under `CLAUDE.md` l.97's cache rule — delete every
   `__pycache__`, then run with `PYTHONDONTWRITEBYTECODE=1`, in that order. Confirm each edit
   applied by reading the file back, and revert each.
   - `_caught` body replaced by `return set()`: run the guard alone and report pass or fail.
   - `_caught` body replaced by `return {"Exception", "SystemExit"}`: run the guard alone and report
     pass or fail.

   The table above says fail, then pass. **If the second one fails, stop: this prompt's premise is
   then wrong.** The first one failing is expected and is not a stop condition.
4. **The rule's home.** Quote the two sentences `CLAUDE.md` l.97 now carries about the bytecode cache
   and about a guard shipping synthetic sources, and give their line. Nothing here restates that
   rule; it cites it.

Then stop and wait.

## 1. Build

### 1.1 Two extracted functions

Both in `tests/test_audit.py` beside `_caught`, both taking source text and reading no file, so both
are testable on synthetic input. Follow `candidates` (l.132 of the composition module) and
`violations` (l.543 of the 32267 module) in shape.

- `exception_handlers(source: str) -> list[int]` — the line of every `except` clause in `source`
  that catches `Exception`. This is l.417's filter, moved.
- `handlers_missing_system_exit(source: str) -> list[int]` — of those, the lines that catch neither
  `SystemExit` nor `BaseException`. This is l.420, moved.

**Both return their lines sorted.** `ast.walk` is breadth-first, not source order: on
`bzk/audit.py` it yields handlers at `90, 450, 508, 566, 654, 985, 1085, 295, 297`, the last two
being the more deeply nested ones. The five `Exception` handlers happen to come back in order
because they sit at one depth, so this is latent rather than live — but §1.3 asserts exact returned
lists, and a case mixing depths would fail for a reason that has nothing to do with the rule.

Move each rule as it stands; do not change what either decides. `_caught` keeps its current
behaviour, including reducing a dotted name to its last part (l.404), so `except builtins.Exception`
reads as `Exception`.

**Two functions, not one.** Revision 1 asked for only the second and also told the guard to keep its
non-empty check; with the filter moved away there is nothing left in the guard to assert
non-emptiness on, and `handlers_missing_system_exit` is `[]` on the real module. Both halves need a
name so both can be fed synthetic sources.

### 1.2 The guard calls both

`test_every_handler_that_catches_exception_also_catches_system_exit` keeps its docstring and its
failure message, reads `Path(audit.__file__).read_text(...)` once, and asserts two things: that
`exception_handlers(source)` is **non-empty** — the check that stops the guard passing because it
read the wrong file — and that `handlers_missing_system_exit(source)` is `[]`. The two questions
stay separate, and §1.3 feeds both.

### 1.3 CAUGHT and UNCAUGHT

**`CAUGHT: dict[str, tuple[str, list[int]]]`** — a short name to a source string and the exact lines
`handlers_missing_system_exit` must return. Revision 1 asked for a name-to-source dict and also for
exact line assertions; those are incompatible, since a single parametrized literal cannot cover
cases whose expected lines differ. Assert the returned list, not its length: a length-only assertion
passes for the wrong line.

Cases, at least: `except Exception:` alone; `except Exception as exc:`; `except (Exception,
ValueError):`; `except (Exception, KeyboardInterrupt):` — a `BaseException` sibling that is **not**
`SystemExit` must not satisfy the rule; a handler nested in a function inside a class; and a module
with two handlers where only the second is bad, which must return that one line alone.

**`UNCAUGHT`** — sources `handlers_missing_system_exit` must return `[]` for: `except (Exception,
SystemExit):`; `except (SystemExit, Exception):`, so order carries no meaning; `except
BaseException:`; `except ValueError:`; and a bare `except:`.

In the `CAUGHT` case with two handlers, **make the first one good by catching `(Exception,
SystemExit)`**, matching the live module. Nothing else satisfies §1.5's mutation 2 as written: a
first handler made good with `except BaseException:` would not be flagged under that mutation, and
the case would then fail three things rather than four.

**A third set, for `exception_handlers`.** It carries its own expectations and so fits neither
`CAUGHT`'s type (which holds only the `handlers_missing_system_exit` expectation) nor `UNCAUGHT`
(which holds no lines and has no no-handler case); give it a name of its own. At least: a source
with no handler at all, and one whose only handler catches `ValueError`, must both give `[]` —
those are what the guard's non-empty check exists to catch — and a source with two `Exception`
handlers must give both lines.

**Record the guard's limits rather than widening them**, as `UNCAUGHT`'s comment at l.247–249 does
for the other guard. An aliased import (`from builtins import Exception as E`, then `except E:`)
reads as `E` and is missed; a dotted `except builtins.Exception:` **is** flagged. Put both in a
clearly named test asserting the *current* behaviour, so the limit is documented and any future
widening is deliberate. **Do not change `_caught` to close it.**

`ruff` raises `ISC004` — *unparenthesized implicit string concatenation in collection* — on a
multi-line source string inside a tuple, confirmed at `c8a104e`. Give each such string **its own**
parentheses, inside the tuple's; the tuple's own brackets do not satisfy it.

### 1.4 Expected outcome, and the sweep

| check | expected |
|---|---|
| §0.3's two mutations, re-run after this build | `return set()`: the `CAUGHT` tests fail **and** the guard's own test fails on its non-empty check. `return {"Exception", "SystemExit"}`: the `CAUGHT` tests now fail — this is the point of the prompt |
| `handlers_missing_system_exit` on `bzk/audit.py` | `[]` |
| `exception_handlers` on `bzk/audit.py` | five lines |
| `pytest` | 1215 passed, 14 skipped **plus this turn's tests**, in a container with no raw store |

**1215 / 14 is the container figure at `ebbdbdb`, re-measured in the reviewer's clone**, not
inherited. **All three of the skips that flip are gated on the PXD018299 sites table alone**
(`PXD018299_SITES`, `sha256:a4a503e3…`): `tests/test_pxd018299_baseline.py` l.275 and l.290, and
`tests/test_pxd018299_refusals.py` l.230. `SUPP_DATA_1` gates **no** skip in the suite — prompt 37
fetched it for the live census, not for a test gate. So a machine holding the sites table runs three
more passing and three fewer skipped; prompt 38's build measured 1218 / 11 holding both files. Report which machine you measured on, and if the store is
present, measure both ways as that build did.

**The sweep. Expect `PINNED` to move.** An expectation asserted as a parametrized **name** adds a
matching equality and moves the pin; per-case **literals** do not, because `_is_literalish`
(l.62–75) treats a literal display as not a match. §1.3's typed `CAUGHT` forces the name form, since
the expected lines differ case by case — so the pin moves, and revision 2 was wrong to call that an
open choice. The floor counts asserts and moves either way. Classify whatever appears as the failure message
instructs, regenerate `PINNED` with the command in the comment at l.201–202 — strip the `#: `
prefixes, the leading *"Regenerate with"* and its opening backtick, the closing backtick, and the
trailing *"**after** classifying whatever is"*, then rejoin — and report `PINNED`'s size and the
floor before and after. **Read both off `sweep()`; predict neither.**

### 1.5 Mutation proof

Per `CLAUDE.md` l.97, including its cache rule: delete every `__pycache__`, then run with
`PYTHONDONTWRITEBYTECODE=1`, confirm each mutation applied by reading the file back, revert each,
and confirm green. Mutate by content, never by a line number. Name the failing case and its message
for each.

**Each list below is a floor, not an exhaustive set — except mutation 2, which is exact.** In
particular §1.3's limit test, which asserts `_caught`'s *current* dotted and aliased behaviour, also
fails under mutations 1, 3 and 4 and under §1.4's first row, because each changes what `_caught` or
the rule returns. Report what actually failed, not only what is named here.

1. `_caught` returning `{"Exception", "SystemExit"}` unconditionally — the `CAUGHT` tests must fail.
   **This is the mutation that was silent before this prompt**, so it is the one that proves the
   build did its job.
2. `handlers_missing_system_exit` dropping `SystemExit` from the names it accepts — **four things
   must fail**: both `UNCAUGHT` cases that pair `Exception` with `SystemExit` in either order, the
   `CAUGHT` case with two handlers where only the second is bad (it returns both lines instead of
   the second alone), and **the guard's own test**, because all five live handlers in
   `bzk/audit.py` catch `(Exception, SystemExit)` and are flagged under this mutation. Name each.
3. `handlers_missing_system_exit` returning `[]` unconditionally — the `CAUGHT` tests must fail.
4. `exception_handlers` returning `[]` unconditionally — its own synthetic cases must fail, and so
   must the guard's non-empty assertion.

## 2. Out of scope

- **FINDINGS §2 route 2 and stage 4's note: prompt 40**, renumbered from 39. `notes/prompts/38-...md`
  §2 called it prompt 39; it moved because `CLAUDE.md` l.97's new rule would otherwise reach stage
  4's work with the convention unimplemented. The disagreement that prompt records about route 2's
  producing script is unchanged and still unsettled.
- **The other eight unguarded source-readers** (§0.2). A known class, deliberately left open, not a
  class this prompt claims is closed.
- **The four guards that already ship synthetic sources.** None is touched; whether their sets are
  *complete* is not this prompt's question.
- **`bzk/audit.py` and everything else under `bzk/`.** No handler, message, mode or findings key
  changes. If the build finds a **sixth handler catching `Exception`** — the module has nine `except`
  clauses, five of which catch `Exception` — or a real violation of the rule, **report it and stop**
  rather than fixing it here.
- **`_caught`'s aliased-import limit** (§1.3). Documented, not closed.
- Any fixture, anything under `notes/` or `walk/`, and `CLAUDE.md` itself.

## 3. Report

Close with the four points of `CLAUDE.md` **l.96–99** (l.95 is their parent bullet; earlier prompts
cite the span as l.95–99, which is one line wide — reported, not fixed there):

1. Each check by name at its actual result and target: `pytest` (full suite), `pytest
   tests/test_schema.py`, `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk tests`.
   A check not run is reported as not run. State which machine and whether the raw store held
   anything.
2. The §1.5 mutations, each with its confirmed application, the case that failed and its message;
   §0.3's two reproductions before and after the build; and §1.4's table, expected beside observed.
3. What this did not cover, including at least: the eight source-readers with no synthetic cases,
   listed by file and line; `_caught`'s aliased-import limit; and that the guard's non-empty check
   and the synthetic cases answer different questions.
4. Any instruction from this prompt dropped or partly done.

## 4. Rejected checker finding, recorded so it is not re-raised

- **"The two named artefacts gate five skips, not three."** Rejected in its conclusion: the two
  extra skips it counted (`tests/test_pxd055843_depletion_ranking.py` l.365 and l.380) are gated on
  `Supplementary_Data_S1_TP.xlsx`, the PXD055843 Perseus file, **not** on `SUPP_DATA_1`
  (`41416_2020_1167_MOESM3_ESM.xlsx`, `sha256:e2680e30…`). Two different artefacts are both called
  *Supplementary Data 1* in conversation. Three is right and five is wrong.

  **But revision 2's own defence of it was wrong one level in, and a second audit caught that.** It
  wrote as though the two named artefacts gated three skips between them. They do not:
  `PXD018299_SITES` gates all three, and `SUPP_DATA_1` gates none — `tests/test_protein_groups.py`
  l.130 is gated on `measure_all`, which verifies `SUPP_DATA_2`, `SUPP_DATA_3` and
  `PXD018299_PROTEIN_GROUPS` (`bzk/sources/protein_groups.py` l.215–221), and no test in the suite
  verifies `SUPP_DATA_1`. §1.4 now attributes the three to the sites table alone.
