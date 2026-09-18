# Report — correct the imputation ADR's premise, then land it as Proposed

**Run at:** 2026-09-18 · **Landed as:** `decisions/0034-declaring-an-unrecorded-imputation.md` · **Commit:** `d46a3ab`

---

## R0 — state at the open

```
59d9433 2026-09-18 00:43:42 +0100 notes(adr): correct zero-handling home in the imputation ADR draft
?? data/frame/
?? notes/prompts/
?? notes/reports/
## main...origin/main [ahead 4]
```

**HEAD was not pushed.** Four commits are unpushed, and this turn's makes five:

```
59d9433 notes(adr): correct zero-handling home in the imputation ADR draft
3a4387c notes(adr): record the zero-handling receipt checks for the imputation ADR
d09bdae decisions: add ADR-0033, the frame as a query-set repair
fda3cb9 notes: add two ADR drafts for verification
```

Three untracked paths were present and remain so: `data/frame/`, `notes/prompts/`, `notes/reports/` (this file's directory).

---

## Receipt checks

### R1 — `schema.ABSENCE`'s Imputation entries

**Four**, each carrying `"determined"`:

```python
("Imputation", "downshift_sd"): "determined",
("Imputation", "width_sd"): "determined",
("Imputation", "seed"): "determined",
("Imputation", "scope"): "determined",
```

### R2 — §3's absence table, rows whose Node cell is `Imputation`

Four rows, `ONTOLOGY.md:156`–`:159`. Field, Kind and determiner verbatim:

| line | Field | Kind | determiner cell |
|---|---|---|---|
| 156 | `downshift_sd` | determined | `` `method` — NULL unless downshifted normal `` |
| 157 | `width_sd` | determined | `` `method` — as `downshift_sd` `` |
| 158 | `seed` | determined | `` `method` — stochastic methods only (I15) `` |
| 159 | `scope` | determined | `` `method` — NULL when nothing is imputed `` |

### R3 — what the ABSENCE guard compares

`tests/test_schema.py::test_schema_absence_matches_ontology_table`:

```python
rows = re.findall(r"^\| `(\w+)` \| `(\w+)` \| (\w+) \| (.+?) \|\s*$", block, re.MULTILINE)
assert rows, "absence-classification table not found in §3"
documented = {(label, field): kind for label, field, kind, _why in rows}
assert schema.ABSENCE == documented, (...)
```

**It compares `(node, field) → kind` only.** The determiner is captured as the fourth group and then discarded — the comprehension binds it to `_why` and never uses it. **The determiner text is not checked.**

### R4 — where the I15 clause-(b) rationale is restated

**Three homes, as the reviewer said.** All quoted from `ONTOLOGY.md` at `59d9433`:

- **`:83`**, *Configuration belongs in identity* — "*`Imputation` is configuration: §6.5 and I15 make the seed mandatory precisely because it materially determines the result, and two runs differing only in seed produce different numbers.*"
- **`:853`**, §6.5 — "*A seed is mandatory for stochastic methods: without it, the analysis is not reproducible even from the same inputs, which defeats I9.*"
- **`:962`**, I15 — "*Stochastic methods record a seed; without one the analysis is irreproducible from its own inputs and I9 fails.*"

**Two further mentions state the requirement or the classification without the rationale**, and are recorded so a later edit does not miss them:

- **`:839`**, the `Imputation` DDL comment — `seed INT64,  -- REQUIRED where the method is stochastic`
- **`:158`**, §3's `seed` row — "*`method` — stochastic methods only (I15)*", which is itself one of the four cells being amended.

### R5 — the next free number

`decisions/` held `0001`–`0017`, `0019`–`0033`, with `0018` reserved-and-unwritten in the Queued table. **Next free: `0034`**, used. `0033` is taken by the frame record, which landed first.

---

## Expectations

| # | expectation | result |
|---|---|---|
| **E1** | ABSENCE carries exactly four Imputation entries, each "determined" | **Held**, exactly — `downshift_sd`, `width_sd`, `seed`, `scope` |
| **E2** | §3 carries the same four rows, each determiner `method` | **Held**, exactly |
| **E3** | The guard compares `(node, field) → kind` only, not determiner prose | **Held.** The determiner is parsed and discarded (`_why`). Amending it needs no code change and breaks no test |
| **E4** | The rationale has three homes, not two | **Held** — `:83`, `:853`, `:962`, plus two non-rationale mentions |

---

## The number used

**0034.** The draft was filed as 0033, which the frame record took by landing first; numbers go to records in landing order.

---

## What the Decision says now, and what it said before

**Before**, the Decision ran: I15 requires a declaration; PXD065158 can make one with four nulls; `ONTOLOGY.md:156`–`:159` classify all four as determined by `method`, and this method requires all four present — "**Decision: amend those four rows so `method` is joined by the parent's `parameters_observed`**", with the `parameters_observed` reproducibility argument and the rejected `Software.container_digest` alternative.

**The framing was already "amend", not "add" — the prompt's premise is half right.** What carried the error was **open item 3**, which read "**`schema.ABSENCE` must be amended in step**" and described the change as "a row added to the document without an entry here".

**After**, the Decision adds four things:

1. **The measurement, stated in the record**: the four rows exist in §3 *and* in `schema.ABSENCE`, quoted, so "nothing is missing and nothing needs adding" and the act is amending a determiner cell.
2. **The ADR-0021 argument made explicit**: for an external analysis whose method *is* stated, `method` determines the four fields non-null; they are null anyway because the publication never stated them, which is a contingent null on an identifying field — "*a defect to redesign rather than a state to declare*".
3. **The parent-field question decided**, on modelling ground rather than on the guard's silence: §3's test for `determined` is whether something outside the moment of ingest forces the null, not where that something lives; `Imputation` anchors `MANY_ONE` to one `Analysis`, `parameters_observed` is REQUIRED by I19, and the identity fold at `:169` already draws parent and child together.
4. **"No code change is required"**, with the guard's own line quoted, and open item 3 struck in place.

---

## Implied changes, listed and not made

The record carries a section of that name, following ADR-0031. **`ONTOLOGY.md` was not edited; `schema.py` was not edited; no adapter or invariant was touched.** Listed:

1. The four determiner cells at `ONTOLOGY.md:156`–`:159`, each gaining `Analysis.parameters_observed` beside `method`. `Kind` stays `determined`, so `schema.ABSENCE` does not move with them.
2. The I15 clause-(b) rationale in all three homes or none — `:83`, `:853`, `:962` — with `:839` and `:158` named as the two further mentions.
3. No ordering fixed between 1 and 2; 1 alone suffices for PXD065158 to be declarable.

**Confirmation: none of these was made.** The only files this commit touches are the record itself, `decisions/README.md` and `tests/test_decision_index.py`.

---

## Test result and commit

- `pytest tests/test_decision_index.py` → **9 passed**. The suite was not run.
- Index updated: a Written row for 0034, and the pins moved `EXPECTED_FILES` 32→33, `EXPECTED_WRITTEN_ROWS` 32→33, `Proposed` 10→11.
- Status row reads `| Status | Proposed |`, plain. **No `Reviewed` row** — `grep -c Reviewed` returns 0.
- `notes/ADR-0033-imputation-state.md` deleted; git recorded the change as a rename into `decisions/`.
- **Commit `d46a3ab`**, on `main`, unpushed.

---

## Could not verify either way

- **Everything about PXD065158 itself** — that `combined_site_K_114.0429.tsv` is the pre-imputation matrix at 15,619 × 18, that FragPipe imputed nothing and Perseus did downstream, that its publication states the method without the parameters, and the three imputation percentages (14.96 / 17.78 / 28.47). The deposit is not in this repository.
- **`perseus.py::_withheld_because` as quoted in the record's first section** — the sentence is a quotation the draft brought with it; this turn's checks were R1–R5 and did not re-derive it.
- **§11 Q8 and the "adapter constraints note"** referenced in Consequences — the note is not in this repository.
- **Whether the amended determiner wording is *true*** — the guard cannot check it, as the record itself says, and neither can I: it is the modelling judgement the review exists to test.
