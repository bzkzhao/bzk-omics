# Report — write the review into ADR-0033 and complete its round-trip

**Run at:** 2026-09-18 · **Reviewed at:** `d46a3ab` · **Commit:** `700d5bf` · **Record:** `decisions/0033-frame-is-a-coverage-repair.md`

---

## R0 — state at the open

```
d46a3ab 2026-09-18 01:02:44 +0100 decisions: add ADR-0034, declaring an unrecorded imputation
?? data/frame/
?? notes/prompts/
?? notes/reports/
## main...origin/main
```

**HEAD was pushed.** `git log origin/main..HEAD` was empty; `main` and `origin/main` were level at `d46a3ab`. Three untracked paths were present and remain so.

---

## Receipt checks

### R1 — what completes the round-trip

`decisions/README.md`:

> **An ADR lands as `Proposed`, is reviewed, and becomes `Accepted` only once that round-trip completes.** Correcting a record during review is an ordinary edit to a `Proposed` document — that is what the status is for.

### R2 — ADR-0031's Review form

Heading: `## Review`. Its opening states where the record landed, where it was reviewed, and a one-line tally of what the findings did. Its reviewer-supplied marker:

> **A reading is supplied to this record by the reviewer and is written in as decided, not as read.** It is marked as such at its site, and its origin is named there.

One finding in full, as the house form:

> ### A — R3 substitutes a screening status for a laboratory. Ground struck
>
> **What the source conditions the clause on: nothing about screening.** The sentence reads *"A deposit could still be selected by hand or by the anchor laboratory's own next dataset; what (d) forecloses is the *survey's* route to a selection, not selection itself."* It names **two routes** — by hand, and the anchor laboratory's own next dataset — and **conditions neither on whether C0 screened the deposit**. The only condition in the sentence governs what (d) forecloses.
>
> **R3 says *"That is what the 'anchor laboratory's own next dataset' is"* of a deposit C0 never screened. That identification is not in the source**: the source names a laboratory and a dataset, and R3 substitutes a screening status for both. **Ruling (b) — the ground is struck.**
>
> **What survives, and what does not.** R3's first half — that selection outside the route remains available — **survives**, and on the source's own words rather than on the substitution. R3's second half — that the class it is available for is *a deposit C0 never screened* — **does not**. …

So: `### <letter> — <claim>. <disposition>`, then the sentence it turns on, then **Ruling (x)**, then **What survives, and what does not.**

### R3 — what C0's gate is decided by

ADR-0031, quoting the survey:

> The table-wide statement is that *"Every one of the sixty is CC0 with a resolvable organism, so C0(a), (b) and (e) never bind in this draw"* and that the gate *"is decided entirely by (c) and (d)"*.

### R4 — the distinct `C0 gates met` values

ADR-0031's measurement row:

> | distinct `C0 gates met` values over the sixty rows | `awk` on the tenth pipe-delimited field of l.4573–4632 | `abcde` ×10, `abce` ×2, `abde` ×3, **`abe` ×45** — 60 rows, **zero cells containing an `f`** |

### R5 — the pinned counts, and which move on Proposed → Accepted

Pinned: `EXPECTED_FILES = 33`, `EXPECTED_WRITTEN_ROWS = 33`, `EXPECTED_QUEUED_ROWS = 1`, `EXPECTED_SEED_LINES = 18`, `EXPECTED_SEED_STRUCK = 17`, and `EXPECTED_STATUSES = {"Accepted": 19, "Proposed": 11, "Superseded": 3}`.

**Only `EXPECTED_STATUSES` moves on a status change** — Accepted 19→20, Proposed 11→10. A rename moves neither count, but `test_every_written_link_resolves` requires the README link to follow the filename.

---

## Expectations

| # | expectation | result |
|---|---|---|
| **E1** | R3 says the gate is decided entirely by (c) and (d) | **Held**, verbatim |
| **E2** | `abcde` ×10, `abce` ×2, `abde` ×3, `abe` ×45 — 60 rows, zero `f` | **Held exactly** |
| **E3** | Deposits passing (c) or (d) = 15 of 60 = 25% | **Held** — 10 + 2 + 3 = 15; 15/60 = 25.0% |
| **E4** | ADR-0031's review supplies a reading to its own operative ruling and marks it reviewer-supplied | **Held** — the marker is quoted under R2, and the reading sits under its finding A as *"The reading, decided here and not read from the source"* |

**E2 did not differ, so the falsifier carries through at 25% unchanged.** One arithmetic distinction is recorded in the record rather than left implicit: 15/60 is the rate of passing *(c) or (d)*, which is what the enrichment claim is about; the rate of passing C0 **outright** is `abcde` alone, **10 of 60 = 16.7%**, and no row of the sixty was evaluated against (f) at all. A screening turn reporting whole-C0 verdicts must say which baseline it beats. This is carried in Finding C and in the registered-expectation table.

---

## The five findings, as written

All five were written as given; **none was corrected or dropped against a check**, because every measured claim they rest on re-derived exactly (E1–E4).

- **A — ruling (b): the name struck and replaced.** R1 called the frame a *query-set repair*, which asserts reach; Context says reach cannot be separated from the cap. Coverage is true under both mechanisms and is the superset. R1's content survives untouched.
- **B — ruling (b): R2's reach widened by a ground.** Under reach, R2 is right as written. Under coverage it is stronger and unstated: 390 pool members are unscreened, so offering eleven of them continues a classification the cap interrupted and needs no appeal to ADR-0031's gap. Both grounds now written in, one per mechanism.
- **C — ruling (b), with a reading supplied by the reviewer and marked as such.** The objection is eleven versus 390, not eleven versus one. The reading: C0 is decided entirely by (c) and (d); 45 of 60 failed there; Frame B's site-directed enrichment tests nearly the property C0(c) tests — enrichment is a wet-lab fact and a processed table a deposited artefact, so not identically, but the first is close to necessary for the second. The eleven are therefore enriched for passes by construction, and continuing there is **prioritisation, not selection**; the remainder is unscreened, not foreclosed. **What does not survive:** any reading under which the frame's output is a sufficient ground on its own.
- **D — ruling (b): confidence struck, referral stands.** *"Screening a candidate is not drawing one"* holds under reach; under coverage the sixty exist because of the cap, so screening eleven more moves the cap per-deposit and without a record — the shape (ii) rejects. R5's referral of the draw question survives.
- **E — ruling (c): stands, outstanding item recorded.** C0(b) is `unchecked` for both candidates and the record says so, but the worked consequence — `PXD026748` as the first deposit evaluated against all six gates — rests on it. One project-record lookup closes it.

**Explicitly untouched, as instructed:** R3 stands entirely, R4 stands, and the Context's correction stands as the best work in the record — A, B and D are all consequences of that correction not having been carried through the rest of the document.

---

## Edits, each with the finding that forced it

| edit | forced by |
|---|---|
| Title → *The frame is a coverage repair…* | A |
| Filename → `decisions/0033-frame-is-a-coverage-repair.md` (git-recorded rename) | A |
| R1's text → *coverage repair*, with the strike-and-replace note and the both-mechanisms ground | A |
| Context's *"a repair to the query set"* → *"a repair to the survey's coverage"* | A |
| *"not a query-set repair"* → *"not a coverage repair"* in § What this record does not settle and § What the route excludes | A |
| R2 gains **Two grounds, one per mechanism**, with the 450/60/390 arithmetic | B |
| `## Review` section added with all five findings, in ADR-0031's house form, including the reviewer-supplied marker | C (and the task) |
| **Registered expectation** table added to § What applying C0 is expected to produce — baseline, prediction, mechanism, falsifier, and the 16.7% caveat | C |
| R5's closing sentence qualified in place; referral preserved | D |
| Status row `Proposed` → `Accepted`, plain | R1's rule |
| Landing note rewritten to record landed-at, reviewed-at and accepted-on | R1's rule |
| README's Written row → new link and *coverage repair* wording | A + `test_every_written_link_resolves` |
| `EXPECTED_STATUSES` → Accepted 20, Proposed 10 | R5 |

---

## Result

- **New filename:** `decisions/0033-frame-is-a-coverage-repair.md`
- **Status row as written:** `| Status | Accepted |` — plain, not bolded. No `Reviewed` row was added; the Review section itself carries the round-trip record, as ADR-0031 does.
- **Test:** `pytest tests/test_decision_index.py` → **9 passed**. The suite was not run.
- **Commit:** `700d5bf`, on `main`, **not pushed** (HEAD was level with the remote at the open; this commit is one ahead).

---

## Could not verify either way

- **`FRAME v1`'s eleven Frame B members** — their identity, their titles, and which of them are among the 390 unscreened pool members rather than outside the pool. `FRAME-SPEC v1` and `FRAME v1` live outside this repository, and the 450-accession pool is not enumerated in it.
- **The three mouse members and the non-MaxQuant members** named in Finding C's predicted mechanism — same reason. The prediction is registered on the reviewer's authority and marked as a prediction.
- **`PXD026748`'s PRIDE record** — its title, submitter, lab head and reuse terms. No network call was made, and the record already marks the submitter and lab head as reviewer-supplied.
- **Whether Frame B's membership criterion and C0(c) really do track each other** — the claim that site-directed enrichment is close to necessary for a site-grain processed table is the reading's load-bearing premise, and it is exactly what the registered falsifier exists to test.
