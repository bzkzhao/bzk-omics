# REVIEWER CONVERSATION HANDOFF — 2026-10-10

**This is a handoff between reviewer conversations, not between days of work.** It does **not**
supersede anything. `notes/REVIEWER-HANDOFF-2026-10-10.md` remains the starting point for the
repository's state, and the dated series continues from it.

The reviewer chat that drafted prompts 29–33 and closed ADR-0038 is being retired for length. That
chat held two things no file carries, and this file is those two things only:

1. **the one commit since the 10-10 handoff was written** — prompt 33, `8d71ec4`;
2. **the loop conventions**, which have only ever lived in the conversation (§4).

**What is not restated here.** Repository state, the build record, the open items and the next work
are all in the 10-10 handoff and the dated series behind it. §5 is the pointer table.

**Line references** are to `main` at `8d71ec4`. `8d71ec4` adds one file under `notes/prompts/` and
touches nothing else, so **every line reference in the 10-10 handoff still holds** — it read them
at `fa3ffca`, and no code, DDL, record or document has moved since.

---

## 1. State at `8d71ec4` — the delta, and nothing else

| Item | State at `8d71ec4` |
|---|---|
| `main` | `8d71ec4`, pushed. **One commit since `bb7a60d`**, adding `notes/prompts/33-…md` (217 lines) and nothing else |
| `ONTOLOGY.md` | **v1.48**, unedited since `fa3ffca` |
| ADRs | 38 files: 26 Accepted, 9 Proposed, 3 Superseded — unchanged |
| Checks | Re-measured in the reviewer's container **at `8d71ec4`**: `uv run pytest` **982 passed, 14 skipped**; `pytest tests/test_schema.py` 20 passed; `mypy bzk tests` Success over 117 files; `ruff check bzk tests` clean; `ruff format --check bzk tests` 117 files already formatted. Bzk's Mac reports six more passing and six fewer skipped (10-08 §4.4) |
| Graph on bzk's Mac | Current at `fa3ffca`. **Prompt 33 asks nothing of it** (its §5 is *Nothing*) |
| **Prompt 33** | **Committed, build not released.** Its §0 receipt check is unrun |
| ADR-0038 | Fully built. Nothing outstanding |
| PXD055843 ingestion | Still blocked on the PI's imputation answer and I15's seed |

Those four check figures are also **prompt 33 §3's entire "Before" column, re-measured in a clone
that did not write the prompt.** The prompt's pre-registration is therefore anchored to a
measurement rather than to a recollection, which is what §3's stop rule needs in order to mean
anything.

## 2. What this conversation did after `bb7a60d`

**One deliverable: prompt 33** (`8d71ec4`), covering 10-10 §6(A)'s three guards in one prompt
because they are one shape — *a rule this repository already obeys, relied on by a record or a
build, and checked by nothing.* No ADR, no `ONTOLOGY.md` edit, no curation record, no build.

**One correction to itself, before the patch shipped.** §0.4 first hedged a countable — *"four …
parenthetically five"* `float(row[` sites in `bzk/adapters/perseus.py`. Corrected to **five**,
stated plainly, with the three methods named. This is the shape 10-10 §5 recorded on prompt 32
§0.2 from the other side: **a prompt that offers the build a range has not asked a question**, and
a build that answers inside the range passes a check that measured nothing. The reviewer wrote the
defect it had documented two days earlier, in a prompt whose entire subject is rules that nothing
enforces.

## 3. What the next conversation does first

**Release prompt 33's build session.** Nothing precedes it. §0 is the first thing the build runs
and it ends in *Do not start §1 until bzk replies*, so the release costs one round trip before any
code is written.

**§0 has six items, each with its expected answer already in the prompt.** The reviewer's job is
to check each answer **against the file**, not against the prompt's own expectation — an expected
answer in a prompt is the reviewer's prior, and four prompts running it have each found at least
one place the prior was wrong. The two most likely to come back wrong:

- **§0.2's call-site list.** Three callers of `_compose`, each differing in *which* families it
  asks for (l.141 any, l.176 the one asked for, l.711 each in turn). A build that lists three
  lines without that distinction has not read them, and §2.1's guard has to allow all three.
- **§0.6's AST precedent.** The answer must end at *an AST guard sees syntax, not behaviour*. A
  build that treats `_literal_reads`' blind spot as a bug to avoid rather than a limit to
  reproduce will widen §2.1's guard until E4 cannot be satisfied.

**The pre-registration's stop rule is load-bearing.** §3 E1–E4 and the four-row table, then: *If
any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.* E4 is the
unusual one — the guard's blind spot must be **demonstrated and kept**, not closed.

**One coupling to remember when a failure arrives.** `tests/test_tautology_sweep.py`'s
`_ARCHIVE_DIGEST_EVIDENCE` runs the whole suite inside a mutated copy, so *any* unrelated red
re-breaks the sweep as a second, unrelated-looking failure. Two failures here have been one defect
before (10-08 §4.1). Diagnose the first before believing the second.

## 4. The loop as it actually runs — conventions that lived only in the conversation

**Three parties.** The reviewer drafts prompts, records and handoffs and verifies builds from an
independent clone. A separate build session executes each prompt. **bzk lands every commit from
his Mac.** The reviewer never pushes; the build sessions that did (`ce9e83e`, `402fce8`,
`4724046`, `fa3ffca`) are a distinct authorship class and each handoff says which commits they
are. `CLAUDE.md`: never force-push, never amend or rebase a pushed commit — records cite hashes.

**Every reviewer deliverable ships as a patch, never as a file to copy.** `git format-patch`
against a named parent, with its tree hash stated, plus the terminal block bzk pastes. Standing
since 2026-10-08, at bzk's instruction: *"from now on, ask me (by sending the terminal code) to
commit before sending to claude code."* The reviewer then **waits for bzk's confirmation of the
push** before releasing the build session — a prompt that cites its own commit cannot be released
before that commit exists.

**Every prompt opens with a §0 receipt check ending in *stop and wait*.** Four for four on finding
defects before a line was written. It is the cheapest verification in the loop: the build reads
the ground the prompt claims and reports what it actually found.

**Figures are pre-registered in the prompt, before the run.** The build does not get to choose the
number after seeing it, and cannot adjust code, fixtures or pins to match a prediction. A
prediction that fails is a finding.

**Mac-only runs go to bzk as commands, with their predictions registered first** (10-03 §4).
Rebuild and differential cannot run in the reviewer's container. **Any after-snapshot must be
taken before the pull** — `rebuild` drops the stores, so a comparison asked for afterwards is
unmeasurable (10-09).

**A check line is only comparable against a run in the same environment — state which.** Container
982/14 at `8d71ec4`; bzk's Mac six more passing, six fewer skipped, on local PXD055843 state
(10-08 §4.4).

**The three standing rules** are at `notes/REVIEWER-HANDOFF-2026-10-10.md` l.143–146, one per
handoff since 10-07. Not restated here; that file is pushed and will not move.

## 5. Where everything else lives

| Looking for | Read |
|---|---|
| Repository state, ADR-0038's build record, the judgements it made | 10-10 §1–§3 |
| **Next work** — §6(A)'s three guards (prompt 33), §6(B) order item 3, §6(C) blocked | 10-10 §6 |
| **Open items**, and the questions collected for the PI | 10-10 §7 |
| Order items 3–5 | 10-07 §6.7 |
| The environment split, and the h10/sweep two-failures-one-defect episode | 10-08 §4.1, §4.4 |
| Why the loop lost its independence in October, and the four-stage shape to return to | 10-03 §4 |
| The four-point close, the mutation-evidence rule, single-source-of-truth | `CLAUDE.md` l.95–99 |
