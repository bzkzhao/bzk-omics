# Prompt 33 — Three rules the code follows and nothing enforces

**Repository:** `main` at the commit adding this prompt.

**Why these three together.** They are one shape, not three features: **a rule this repository
already obeys, relied on by a record or a build, and checked by nothing.** Each was found by the
turn that had to work around it, each was carried rather than built, and each would be broken the
same silent way — a green suite over a rule that stopped holding. None adds a capability. The
handoff of 2026-10-10 §6(A) lists them.

**Governing:**
- `notes/REVIEWER-HANDOFF-2026-10-10.md` §6(A), which names all three and why they share a prompt;
- for §2.1: ADR-0038 D5 l.218–219 (*"a column is bound to a `Sample` in exactly one place per
  format"*) and handoff 10-09 §2;
- for §2.2: ADR-0038 D7's *Where each refusal sits* (l.444–457) and handoff 10-09 §7;
- for §2.3: ADR-0038 D6-revised (a) and (b) (l.350–393), and handoff 10-10 §6(A) item 3;
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** **ADR-0038 is fully built** (handoff 10-10 §1). `ONTOLOGY.md` v1.48. This
prompt builds no decision and amends no record: every rule here is already decided and already
obeyed. It only makes each one checkable.

**This changes no behaviour on any committed input.** No DDL, no id moves, `tables_created` stays
**60**, `ONTOLOGY.md` is **not edited**, and every existing test passes unchanged. The only new
failures possible are the ones this prompt's own mutations produce. That is the claim §3 is built
to falsify.

**Edits are limited to** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/adapters/perseus.py` and `tests/`. No ADR, no `ONTOLOGY.md`, no curation record, no
`ROADMAP.md`, no `HANDOFF.md`, nothing under `notes/` other than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - `git log --oneline -3`, `git status --short`. HEAD is this prompt's commit, tree clean.
   - Open-of-turn: `uv run pytest`, `uv run pytest tests/test_schema.py`, `uv run mypy bzk tests`,
     both `ruff` targets.
   - Expected **in a container**: `982 passed, 14 skipped`; 20 passed; `Success` over 117 files;
     clean / 117. Bzk's Mac reports six more passing and six fewer skipped (handoff 10-08 §4.4).
2. **Rule one, and its three obedient callers.**
   - Quote `bzk/adapters/maxquant_sites.py`'s `_compose` with its docstring.
   - List every call site by line, and say how each differs.
   - Expected: **three** — l.141 `_sample_columns` (any family), l.176 `bind_column` (the one
     asked for), l.711 `_site`'s I11 retention (each family in turn).
   - Say what happened the last time this rule was broken, and what caught it.
   - Expected: `_site` composed `f"{prefix}{label}"` itself and tested membership; **nothing
     caught it** — prompt 30's build found it by reading, and routed it through `_compose`.
3. **Rule two, and the field that cannot express it.**
   - Quote `site_change_set`'s signature and its `arms.kind` refusal.
   - Quote `ContrastArms`' field list from `bzk/curation/loader.py`.
   - State why a caller can pass arms belonging to a different contrast than the `contrast` node
     it also passes.
   - Expected: `ContrastArms` carries `numerator`, `denominator` and `kind` and **no contrast id**,
     so the two arguments are independent and nothing relates them.
4. **Rule three, and the four places it is broken.**
   - Run `grep -n "float(row\[" bzk/adapters/perseus.py` and list every line with the method it
     sits in.
   - Expected: **five**, in three methods — l.397 `difference_of`; l.400 and l.405 `result`;
     l.416 and l.421 `untested`. Report what you find; if it is not five, say so before going on.
   - State what each raises on a blank cell and what the message contains.
   - Expected: a bare `ValueError` from `float()`, naming **neither the row nor the column**.
5. **Why `_cell_value` is not the fix.**
   - Quote `_cell_value`'s docstring.
   - State what it returns for a blank cell, and say **why that is right for a quantitative column
     and wrong for a statistics column**.
   - Expected: it returns `None` — blank, unparseable and `NaN` are all absences. For a statistics
     column that would be a silent reclassification: rule (a) must distinguish `0` from *blank*
     (a blank Difference cannot be judged zero), and rule (b) cannot recompute against an absent
     Difference. **Routing the statistics reads through `_cell_value` would turn a malformed row
     into a quietly untested one** — the shape D6-revised (c) exists to prevent.
6. **What an AST guard in this repository looks like.**
   - Name two test modules that already parse source with `ast` and say what each checks.
   - Expected: among them `tests/test_tautology_sweep.py` (every equality in every assert) and
     `tests/test_analysis_record.py` (`_literal_reads`, string keys read off a receiver).
   - Say what `_literal_reads`' known blind spot is, from handoff 10-09 §7.
   - Expected: it cannot see a key read off `json.loads(...)`, because the receiver is a call and
     not a name. **An AST guard sees syntax, not behaviour** — §2.1 must say what its own blind
     spot is.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds

Three guards. Each closes a class, none changes behaviour.

**The reading this prompt adds, and it applies to all three:** *a guard that cannot fail is worse
than no guard, because it reads as coverage.* Every one of these must be made to fail by a
mutation that is itself read back — and for §2.1, the mutation is the historical defect: restore
`_site`'s own composition and the guard must catch it.

---

## 2. The build

### 2.1 `maxquant_sites.py` — only `_compose` composes

- A test parsing `bzk/adapters/maxquant_sites.py` with `ast` and refusing any **f-string or
  concatenation that joins a `QUANTITY_COLUMNS` prefix to a label** outside `_compose`.
- The three existing callers pass unchanged. `_run_label`'s prefix *stripping* is not composition
  and must not be caught — say so in the test, or the guard will be loosened the first time
  someone trips over it.
- **State the blind spot in the docstring.** An AST guard sees syntax. A caller that builds the
  same string by `str.join`, `%`, `.format`, or through a local variable, defeats it. The guard
  catches the shape the defect actually took (`f"{prefix}{label}"`) and the obvious neighbours, and
  it is a tripwire rather than a proof.
- **Mutation:** restore the pre-prompt-30 composition inside `_site` — the real historical defect —
  and show the guard fires.

### 2.2 `differential.py` — arms must belong to the contrast

- `site_change_set` refuses when its `arms` do not belong to its `contrast`.
- **`ContrastArms` has no contrast id**, so decide how the relation is established and say why in
  the code. Two shapes, and the choice is yours to argue:
  - **(i)** `ContrastArms` gains the record contrast id, and the check compares it against the
    `Contrast` node. The loader already knows it — `contrast_arms` is keyed by it.
  - **(ii)** `site_change_set` takes the arms **keyed**, or takes the handle and looks them up,
    so the mismatch is unrepresentable rather than refused.
  - **(ii) is the stronger shape** where it fits — a refusal is a check that can be forgotten; an
    unrepresentable state cannot. Take (ii) if it does not force the producer to re-resolve
    anything; otherwise (i), with the reason.
- **This must not make `ContrastArms`' id identifying or reach any node's properties.** The arms
  are non-identifying (D4) and nothing about this changes that.
- **Mutation:** pass arms from the other PXD018299 contrast and show the refusal; confirm the
  unmutated tree still writes the 1,362-result change-set.

### 2.3 `perseus.py` — a statistics cell that is not a number

- Every statistics read names the row and the column when the cell is not a finite number.
  **Do not route through `_cell_value`** (§0.5): a malformed statistics cell is a refusal, not an
  absence.
- One helper, used by all five sites §0.4 found, so the message is one sentence in one place.
- The message carries: the file line number, the column name, and the raw cell as it appeared.
  Follow prompt 31's four refusals in the same module for form — they already name line and
  column.
- **The absence/refusal line must be stated where the helper lives**: a quantitative column's blank
  is an absence (I19, `_cell_value`), a statistics column's blank is a malformed row. Both rules
  are correct and they are not interchangeable.
- **Mutation:** a fixture row with a blank Difference, one with a blank q, and one with a
  non-numeric statistic — each refused, each naming its own column.

---

## 3. Pre-registration — this container

**Not rehearsed.**

**E1 — nothing changes on committed input.** `uv run pytest` passes with **no existing test
edited** except where a new refusal needs a case. State any test you did edit and why.
`tests/fixtures/` unchanged except for fixtures §2.3's mutations need; name them.

**E2 — each guard fails under its own mutation, and the mutation is read back.** Five mutations at
least: §2.1's historical restoration; §2.2's wrong-contrast arms; §2.3's three malformed cells.

**E3 — `tables_created` stays 60, no id moves, `ONTOLOGY.md` is not edited.**

**E4 — the AST guard's blind spot is demonstrated, not just described.** Write the composition a
way the guard does **not** catch, show it passes, and keep that as a documented limit rather than
widening the guard until it catches everything. A guard whose limits are measured is worth more
than one whose limits are assumed.

| Check (target) | Before | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 982 passed, 14 skipped | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed, file unedited |
| `uv run mypy bzk tests` | Success, 117 files | Success; state the count |
| `ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean; state the count |

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, single subject line naming the three guards and that
no behaviour changes.

**Files expected:** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/adapters/perseus.py`, `tests/`. Any other file needs a reason.

**Report:** the commit hash; §0's answers; E1–E4 as measured; §3's table with "After" measured;
each new refusal's message on the unmutated tree; the mutation evidence; `git diff --stat`; the
four-point close. **In point 3, say for each guard what it does not catch** — §2.1's blind spot
measured, §2.2's shape if you took (i) rather than (ii), §2.3's reads that are not statistics
columns.

Then stop.

---

## 5. For bzk's Mac

**Nothing.** No behaviour changes on any committed input, so there is nothing to re-measure. If
you want reassurance, the differential and the `differential_table` query from prompt 32 §5 should
both return exactly what they returned at `fa3ffca` — 1,362 results, all
*stoichiometry-uncorrected*, `platform_targets.json` byte-identical.

---

## Out of scope

- **Order item 3** (PXD018299's `ISG15_interactome`, the first real IP ingestion) — handoff
  10-10 §6(B). The protein-groups binding and M8's silently dropped family belong there.
- **The untested derivation's one-external-analysis-per-`Dataset` assumption** (handoff 10-10 §7).
  Unguarded, and a fourth item of this same shape — but it needs a second external analysis to
  exist before a guard means anything.
- **`_literal_reads`' blindness to `json.loads(...)["contrast"]`** — a fifth, and the same shape
  again. Its own prompt.
- **ADR-0032 taking D6-revised (c) into its review** (ADR-0038 l.399). Overdue; not a build.
- `write_cells` over-reporting; the drift checker; the stale tautology floor; F-b; F-d; R6's
  prefix-only check; the D2/D3 invariant-level check; I22's reliance on a single `Contrast`
  minter; `pxd055843_perseus.py`'s stale module docstring; the seventeen `claude/*` branches.
