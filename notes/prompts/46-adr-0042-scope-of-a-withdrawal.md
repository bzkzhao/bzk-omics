# Prompt 46 — ADR-0042, the scope of a withdrawal under ADR-0041(a)

| Field | Value |
|---|---|
| Base | the commit on `main` that adds this prompt file. **Verified by content below, not by hash** — see §0 |
| Register items | **R38 is discharged by this build. Its register closure is a later turn** — §2 forbids the build from touching the register. P4 and R37 are not closed at all; see below |
| Critical nodes | one new ADR |
| Successor | prompt 47 (HYPOTHESIS v11); scope and carried findings in `notes/prompts/47-SCOPE-carried-findings.md` |
| Author | reviewer, 2026-11-24 |

**What this prompt is for.** `ADR-0041` decided that a registered headline moves
only through a versioned `HYPOTHESIS.md` restatement, and left as its **Open
question 1** whether that covers a *withdrawal* rather than a moved headline —
naming reviewer defect **P4** as the case and saying, in terms, *"Not decided
here."* bzk answered it on 2026-11-24. This prompt does one thing: record that
answer as `ADR-0042`.

**What this prompt deliberately does not do.** It does not touch
`HYPOTHESIS.md`. The version this record licenses is **prompt 47**, split out
for two measured reasons:

1. The current version line begins at `HYPOTHESIS.md:3`, so inserting a new
   `**Version:** 11` block and a new `## 0` section shifts every line from
   **line 3** down. **40 line-anchored references of the form
   `HYPOTHESIS.md:NNNN` exist across ten files**, at targets 5, 22, 30, 37, 39,
   43, 56, 57, 81, 84, 310, 904, 918 and 1018 — all ≥ 5, so all break.
   **Two instruments, because one form is greppable and the other is not.**
   `git grep -oh 'HYPOTHESIS\.md:[0-9]\+'` over the tree *excluding this prompt
   and `notes/prompts/47-SCOPE-carried-findings.md`* finds the **prefixed** form
   and nothing else. **The repository's prevailing continuation form is a bare
   backticked `` `:NNN` `` under a `HYPOTHESIS.md` antecedent**, which no
   path-anchored grep can reach and which breaks on the same insertion at line 3.
   `decisions/0041-...:526` cites P4's own sites that way — *"(`:5`, `:48-49`,
   `:637-638`, `:1203`)"* — so the form the deferral turns on is the form the
   grep misses. The bare form must be read **by eye, per file**, and any count of
   it is a floor.

   **Why the exclusion, and why no all-files total is quoted here.** Those two
   files cite references in order to discuss them, adding targets `:1`, `:3`,
   `:22` and `:48` — and `:1` and `:3` are **below 5**, which falsifies the
   "all ≥ 5" claim the 40 figure is cited for. They also write the literal
   string `HYPOTHESIS.md:NNNN`, which a `[0-9]*` instrument admits with zero
   digits; use `[0-9]\+`. An all-files total would also **move every time this
   prompt is revised**, since the prompt is inside its own measurement — so it
   is deliberately not stated. Three successive revisions of this prompt quoted
   such a total and all three were wrong. Measure it yourself if you need it;
   do not inherit it. They are excluded
   because prompt 47's own repair turn rewrites both, and because a figure
   recorded in the document that cites it moves by the act of recording it. The shift is **not uniform**: references above the new
   `## 0` move by one amount, those below by another, so no single offset
   applies. Nothing reads the file programmatically — the only hits under `bzk/`
   and `tests/` are comments — so the suite stays green and the rot is silent.
   **Of the 40, 17 sit in `notes/prompts/43-`, `44-` and `45-`** (4, 8 and 5),
   which are dated build prompts and are historical quotes under §2's own rule,
   so the live burden is **23, not 40** — plus `47-SCOPE`'s own four, which are
   *not* historical quotes but prompt 47's live input.

   **The burden must be broken down by disposition, and every figure below is a
   floor** — the prefixed count is exact, the bare-form count is by eye:

   | file | prefixed | bare (floor) | disposition |
   |---|---|---|---|
   | `decisions/0041-...md` | 9 | **+12** (`:82-83`, `:177`, `:303`, `:526`) | **cannot be repaired.** `Accepted`, so the append-only rule bars it and §2 says *"no edit, no note"*. **Permanent rot, and the largest single block** |
   | `notes/REVIEWER-DEFECTS.md` | 0 | **+8** (`:61` P4, `:134` R37) | **disposition not settled.** Neither a build prompt nor the one reviewer record `0041:481-482` exempts, so §2's historical-quote rule does not plainly dispose of it. Prompt 47 decides |
   | `notes/REVIEWER-MAP-findings-5-and-6.md` | 3 | — | **exempt**, a dated reviewer record; `decisions/0041-...:481-482` classifies this very file that way |
   | `walk/CORRECTION-PXD018299-H10-headline.md` | 5 | **+3** (`:189`) | repairable |
   | `walk/CORRECTION-PXD018299-2341.md` | 2 | — | repairable |
   | `tests/test_audit.py` | 2 | — | repairable (comments) |
   | `walk/CORRECTION-PXD018299-two-route-independence.md` | 1 | — | repairable |
   | `bzk/audit.py` | 1 | — | repairable (comment) |

   **Prompt 47 measures its own burden from both instruments and states it; it
   does not inherit a number from here.** What this prompt asserts is only that
   the burden is large, that the biggest single block is unrepairable by rule,
   and that one file's disposition is undecided.

   **Why this paragraph was wrong for three revisions, recorded because the class
   recurs:** the instrument was defended at length — `[0-9]\+` against `[0-9]*`,
   the two-file exclusion, the refusal to quote a self-referential total — without
   once asking whether the *form* it matches is the form the repository writes.
   A burden measured without asking which of it is dischargeable is one level
   short of the countable; an instrument defended without asking what form it
   matches is one level short of that.
2. v11 also needs a new guard, which brings `tests/test_tautology_sweep.py`'s
   `PINNED` set with it.

Carrying all of that plus a new ADR in one turn gives two critical nodes and one
report. `CLAUDE.md` asks for verification *"as the closing act of the turn that
reaches it"*; one critical node per turn is how that is honoured here.

**So P4 does not close in this prompt, and it does not close in prompt 47
either.** It **narrows**. The withdrawn claim is live and unbannered in **three
places outside `HYPOTHESIS.md`**, measured 2026-11-24 — two of them in the
claim's own origin document, whose banner block reaches neither:

| site | text it carries | note |
|---|---|---|
| `walk/CHECKS-convention-resolved.md:11` | *"The documented rule reproduces the anchor's own published count"* | the claim asserted as a **section heading**. The document's banner at `:5-7` supersedes only *"the *level* it was computed at, and nothing else"*, so it does not reach this |
| `walk/CHECKS-convention-resolved.md:24-26` | *"the documented rule lands within 2% of the published count, with nothing fitted. That is a validation on the deposit under test"* | the claim's **origin**. `notes/REVIEWER-DEFECTS.md:61` records the span as `:24-26` and names that it *"carries no banner"* |
| `walk/PREREG-PXD032267-gate.md:225` | *"The anchor's documented rule came within 2% of its count"* | inside a **pre-registration** document, which carries no withdrawal banner anywhere |

**This enumeration is three instances and was not exhaustively measured.** It is
a floor. A withdrawal spanning documents is what the `walk/CORRECTION-*.md` form
is for, so those three need a spanning record rather than a banner bolted onto
this. That is a later prompt's.

---

## 0. Receipt check — before any edit

Report this table filled in, and **stop if any row does not match**, except
where a row says otherwise.

**No row identifies the base by a commit hash, and none pins a line number.**
(R11 names three hashes, but as facts expected to be *unresolvable*, not as the
base.) A hash goes stale
the moment anything lands, and a receipt check run against a *working* tree
races with any other session writing to it — which happened while this prompt
was being reviewed. The rows below are content receipts against a committed
tree. Line numbers elsewhere in this prompt are starting points for a search,
never the instrument: find each site by its text.

| # | Check | Expected |
|---|---|---|
| R1 | `git log -1 --name-only --format=` | lists `notes/prompts/46-adr-0042-scope-of-a-withdrawal.md`. If it does not, you are not on the commit this prompt was written against — stop. |
| R2 | `git status --porcelain` | **empty.** This prompt is committed with its own supporting edits, so the tree is clean at the base. Any entry means another session is mid-write — stop and say so. |
| R3 | `ls decisions/ \| grep -c '^00[0-9][0-9]-'` | 40 |
| R4 | `decisions/0042-*.md` does not exist | absent |
| R5 | `decisions/0041-...md` `\| Status \|` row | `Accepted` |
| R6 | `grep -c 'Not decided here' decisions/0041-*.md` | 1 |
| R7 | `EXPECTED_FILES`, `EXPECTED_WRITTEN_ROWS` in `tests/test_decision_index.py` | 40, 40 |
| R8 | `EXPECTED_STATUSES` in the same file | `{"Accepted": 28, "Proposed": 9, "Superseded": 3}` |
| R9 | `EXPECTED_QUEUED_ROWS`, `EXPECTED_SEED_LINES`, `EXPECTED_SEED_STRUCK` | 1, 18, 17 |
| R10 | `ARCHITECTURE.md` §5 carries *"this list stops at `0018` and `0019`–`0025` were never seeded"* | confirmed. **Note:** a naive grep for ADR numbers across §5 also returns `0019` and `0025` — from that very sentence. The seed *lines* are 18, which is R9. Do not read those two as seeded. |
| R11 | **Three hashes this prompt carries are expected to be unresolvable.** `git cat-file -t 783138a`, `1019744`, `4c88e9a` | **All three fail — measured: `fatal: Not a valid object name 783138a` — and that does not stop the build.** The clone is shallow. All three are attested by `notes/REVIEWER-DEFECTS.md:61` and are carried with that provenance — see §1.4. |
| R12 | `pytest -p no:cacheprovider` | `1305 passed, 15 skipped`. The 15 skips are the base state and are **not** a mismatch. Report both numbers rather than the word "green". |
| R13 | `ruff check bzk tests`; `ruff format --check bzk tests`; `mypy bzk tests` | clean |

**Environment.** Copy the whole repository to `/tmp` — `uv sync --frozen` fails
on a bare `pyproject.toml` — then `uv sync --frozen` in the copy and use
`.venv/bin/*` with `PYTHONPATH` set to the copy. Use `pytest -p no:cacheprovider`.
Export `LC_ALL=C.UTF-8` for every search: a bracket range over an en dash
truncated under a different locale on a previous build.

**`ruff check .` reports 43 at base** — 18 in the three notebooks, 23 in
`notes/scripts/`, 2 in `data/frame/frame.py`. It is **not** this build's target.
If you report a zero, state which target it is zero against.

---

## 1. The build

### 1.1 The file

Exact path, so two builders cannot produce two filenames:

```
decisions/0042-a-withdrawal-of-a-stated-claim-takes-a-version.md
```

Exact title line:

```
# ADR-0042 — A withdrawal of a claim HYPOTHESIS states takes a version; one of a claim it does not state does not oblige one
```

**The title's second clause is worded that way for the reason §1.5 gives, and
must not be re-narrowed to "one confined to a CHECKS document".** An earlier
revision carried that phrasing in the title while §1.5 forbade it in the body,
so a builder following both shipped a record whose headline stated the rejected
rule — and §1.6's row, which "must carry: the rule", would have inherited
whichever branch was read last.

### 1.2 The header block

Write it verbatim in `decisions/README.md`'s template form — a headerless
two-column table, **not** a `| row | value |` table:

```
| | |
|---|---|
| Status | Proposed |
| Date | 2026-11-24 |
| Supersedes | — |
| Superseded by | — |
```

No `Reviewed` row: the review has not happened. `tests/test_decision_index.py`
reads only `Status`, `Supersedes` and `Superseded by`, so a record with no `Date`
row ships green — write it anyway.

**`Status` is `Proposed`, not `Accepted`, and the objection that the decision is
already settled is already answered.** `decisions/README.md` requires a record to
land `Proposed` and become `Accepted` *"only once that round-trip completes"*,
and says of exactly this case that the status is *"a property of **the record's**
review state, not of the decision's settledness"*. Landing it `Accepted` would
*"do it by asserting a review that had not happened, which is the one thing this
project refuses everywhere else."* The review is a later turn and is neither this
build's to perform nor to claim.

### 1.3 The sections, which are a closed set

Write **exactly** these, in this order, and no others:

```
## Context
## Decision
## Consequences
## Alternatives considered
## Not decided here
```

The first four are `decisions/README.md`'s Format template. The fifth has a
three-record precedent — `decisions/0023-...:146`, `decisions/0024-...:113` and
`decisions/0039-...:140` — and is where Open question 2 goes (§1.5). **The order
above is this prompt's, not a precedent's:** `ADR-0024` is the only record
carrying both of the last two and it puts `## Not decided here` *first* (`:113`
against `:120`). Follow the order above anyway.

**Do not add any other section.** `ADR-0039` has no `## Alternatives considered`
at all, and neither does `ADR-0023`; `ADR-0038` uses `## Decisions` plural; and
`ADR-0041` carries **three** non-template headings — `## Review` (`:18`),
`## Landing verification` (`:278`) and `## Open questions` (`:521`). Those are
all live precedents, which is exactly why the set is closed here rather than
left to be inferred from a neighbour. **`## Landing verification` in particular
is not to be added**, however verification-heavy this build feels: the
verification goes in the turn's report, not into the record.

### 1.4 The preamble, which is load-bearing

**Four** records open with a bolded `**It supersedes nothing.**` disclaimer after
the header block and **before the first `##` heading** — not necessarily before
`## Context`, since `ADR-0041`'s first heading is `## Review`. `ADR-0040` is the
fourth, excluded below because it amends nothing, as §1.6 also treats it. (This
is a different trio from §1.3's `## Not decided here` set, which is
`0023`/`0024`/`0039`, and neither `0023` nor `0024` carries a disclaimer at all.)
The disclaimers run to several lines, not one:

- `decisions/0038-...:11-14` — *"**It supersedes nothing.** It amends ADR-0036's
  **mechanism**, not its rules …"*
- `decisions/0039-...:11-13` — *"**It supersedes nothing.** It amends the scope of
  a guard ADR-0023 wrote under *Consequences*, not any of ADR-0023's three
  numbered decisions …"*
- `decisions/0041-...:11-16` — the same opening.

`ADR-0042`'s must say that it supersedes nothing and that it **amends the scope
of `ADR-0041`(a)**.

**Name what is left intact, and get the count right.** `ADR-0041` has exactly
**two** lettered decisions — **(a)** at `:143` and **(b)** at `:145` (H10's
headline stays at the registered denominator). `ADR-0039`'s row says *"not its
three decisions"* because the guard it amends sat under `ADR-0023`'s
*Consequences* — outside its numbered decisions entirely. **That structural
parallel does not exist here**: `0042`'s target *is* a numbered decision, (a) at
`:143`. So do not carry `0039`'s phrasing or its number across. Write it as:
`0042` amends (a)'s **scope** and leaves both decisions standing.

**On the closing principle:** `decisions/0039-...:13` reads *"an amendment to a
mechanism is not a supersession."* — unbolded there. (The bolded
**mechanism** is in a different record, `decisions/0038-...:11`; `0039:11`
contains the word nowhere.) A scope is not a mechanism, so if you
write the scope form, write it as that sentence **generalised**, not as a quote.

**Why no other route was available.** `ADR-0041` is `Accepted`, so
`decisions/README.md`'s append-only rule binds it. Write this unambiguously —
the register's own phrasing (*"the three routes … apply"*) has two readings, and
only one is meant:

> The rejection `decisions/README.md` records for its three routes — an in-place
> edit, a superseding record, and a note inside the ADR — binds here too. None of
> them is needed, because answering an open question *decides something*, which
> is what the README says a correcting-only record does not.

Do not write that the three routes *"do not apply"*, which inverts it and would
read as licensing the note-inside-the-ADR route.

### 1.5 The decision to record

**bzk, 2026-11-24.** `ADR-0041`(a) extends to a withdrawal, **but only to a
withdrawal of a claim `HYPOTHESIS.md` itself states.** Such a withdrawal is taken
up by a versioned restatement. A withdrawal of a claim `HYPOTHESIS.md` does not
state **does not oblige a HYPOTHESIS version.**

**Write the second branch that way, not as "a withdrawal confined to a
`walk/CHECKS-*` document".** The narrower phrasing is false of an instance this
prompt itself enumerates: the claim is restated at
`walk/PREREG-PXD032267-gate.md:225`, which is neither `HYPOTHESIS.md` nor the
CHECKS document the withdrawal sits in, so a rule written over "confined to a
CHECKS document" leaves the restated-elsewhere case unaddressed while appearing
to cover it.

`## Context` carries:

- The question, quoted from `ADR-0041`'s Open question 1, including that it is
  left *"Not decided here"* and that it names P4 as its case.
- **The cost of the other branch, in `ADR-0041`'s own words:** if (a) does not
  extend, *"the two chains disagree, with no rule saying which governs"* — which
  would require a third rule choosing between them. **This quote lives here and
  is not repeated in `## Alternatives considered`**, which refers back to it.
  `decisions/README.md` § Format says *"Keep them short"*, and a duplicated fact
  is a defect under `CLAUDE.md`'s single-source rule.
- P4's facts. **Source them, do not assert them.** `notes/REVIEWER-DEFECTS.md:61`
  carries **three** hashes — `783138a` (the withdrawal, 2026-09-22 22:23),
  `1019744` (HYPOTHESIS v10, sixteen minutes earlier) and `4c88e9a` (where
  `:1203` was re-added after the withdrawal). **All three are unresolvable in a
  shallow clone** (R11). Cite that register row as the attesting source for all
  three in the record itself. `CLAUDE.md`'s working style is *"Real external
  identifiers only"*; an identifier you cannot resolve is carried with its
  provenance, not asserted bare and not silently dropped.
- **A warning about that same source.** `notes/REVIEWER-DEFECTS.md:135` (R38)
  states the decision in the phrasing §1.1 and §1.5 bar — *"withdrawals confined
  to CHECKS documents"*. It is left exactly as it stands (§2) and is **not** the
  wording to record. Take the facts from it; take the wording from §1.5.

`## Decision` carries the rule above, in one or two sentences.

`## Consequences` states, at minimum:

1. **P4's HYPOTHESIS half is fixed by a HYPOTHESIS version**, which is prompt 47.
2. P4 does **not** close on that version. Reproduce the three-row table from this
   prompt's preamble — **each citation carrying its quoted text beside its line**,
   not a bare `path:line`. This matters because the record is append-only once
   accepted, and the later spanning-correction prompt will add banners to both
   documents and shift those lines; `decisions/README.md:11` names the hazard
   (*"a within-file line number … is a referent waiting to be lost"*) and
   `walk/CORRECTION-PXD018299-H10-headline.md:178-179` shows the
   `| path:line | *"quote"* | disposition |` form that survives it. State that
   the enumeration is a floor, not an exhaustive measurement.
3. What a withdrawal of a claim `HYPOTHESIS.md` does not state fails to oblige
   is **a HYPOTHESIS version**. Do not write that it *"remains settled inside its
   own document"*: `notes/REVIEWER-DEFECTS.md:135` records that this withdrawal
   **spans documents**, and item 2's own table shows it restated in a third one,
   so that sentence would be false of the instance beside it.

`## Alternatives considered` records the **wider** reading — every withdrawal,
wherever it sits, takes a version — as available and not taken; and the
**declining** reading, referring to the chain-disagreement cost quoted in
`## Context`.

**Do not write a motive. bzk recorded no reason, and the record says so.**
`ADR-0041` sets the form at `:264-265`, bold run-in included: *"**Not chosen:**
bzk chose A on 2026-11-13 and recorded no reason. What each costs is noted for
the record, not as the ground of the choice:"* — a colon in the source,
introducing its two cost bullets; do not copy it as a full stop. Follow it
exactly: the version-frequency cost of the wider reading may
be **noted as a cost**, never as the ground of the choice. A rationale no source
records is one the builder would be inventing, which `CLAUDE.md` forbids twice
over — *"Ask rather than invent"* and *"Never assert what the data cannot
support."*

`## Not decided here` carries two items, each in a line or two:

- `ADR-0041`'s **Open question 2** — may `walk/RESULT-*` or `walk/FINDINGS.md`
  *propose* a move — as not answered by this record, so no later reader takes
  `0042`'s existence as having closed both.
- **Whether a withdrawal obliges a spanning `walk/CORRECTION-*.md` record where
  the claim is restated in a third document.** `0042` decides what obliges a
  *version*; it does not decide that. The three sites in `## Consequences` item 2
  are the live case.

### 1.6 `decisions/README.md`

**The Written rows carrying an amendment are summaries, not titles — but not
every row is, and not every summary carries an amendment clause.** Rows 91–93
(`0038`, `0039`, `0040`) are multi-clause summaries that diverge from their
titles; of those, the two that **amend** something — 91 and 92 — carry the
amendment clause in the row. Row 93 (`0040`) carries none, because `ADR-0040`
amends nothing. **Row 94 (`0041`) is byte-for-byte its own title** minus the
`# ADR-0041 — ` prefix. Follow **91 and 92**: `0042`'s row is a summary and
carries the amendment clause.

**Row 94 also gains a forward pointer, and this is an instruction, not a
choice.** Without it a reader of `ADR-0041`'s Open question 1 has no route to
the record that answers it: `ADR-0041` itself is untouched (§2), so `0042`'s row
would be the only cross-reference and it points only backwards. `README` is the
one file in `decisions/` the append-only rule does not bind, and the precedent
for amending an earlier row to point forward is three rows — `:61`, `:65` and
`:68` — the complete set of forward pointers in the table. **They establish the
form, not the act:** whether any was appended after its row was first written is
unreadable in a shallow clone. Two of them (`:61`,
`:68`) use the `— **superseded by NNNN**` form; `:65` carries its clause after a
comma, its em dash belonging to an earlier `supersedes 0007`. Append to row 94 exactly this, bold
markers included and nothing else changed:

```
 — **Open question 1 answered by 0042**
```

`EXPECTED_WRITTEN_ROWS` is unaffected: `_written()`'s regex captures the first
cell only.

Pin the first cell literally — `tests/test_decision_index.py` matches
`^\|\s*\[(\d{4})\]\(([^)]+)\)\s*\|` and checks the link resolves on disk, so a
plain `| 0042 |` ships red:

```
| [0042](0042-a-withdrawal-of-a-stated-claim-takes-a-version.md) | … |
```

The row must carry: the rule; that it answers `ADR-0041`'s Open question 1 with
P4 as the case; that Open question 2 is left open; and that it **amends
`ADR-0041`(a)'s scope and supersedes neither of its two decisions**. Place it in
number order after `0041`.

**Do not write "amends the scope of (a), not either of its two decisions".** It
asserts and denies the same thing in one clause: (a) *is* one of the two. The
coherent form is the one above and in §1.4 — the scope of (a) is amended, both
decisions stand.

### 1.7 The index pins

`tests/test_decision_index.py` pins every parsed count, for the reason its own
comments give: a regex that matches nothing compares equal to another that
matched nothing. *"A legitimate addition moves these in the same commit."* Move:

- `EXPECTED_FILES` 40 → 41
- `EXPECTED_WRITTEN_ROWS` 40 → 41
- `EXPECTED_STATUSES` — `Proposed` 9 → 10. `Accepted` stays 28, `Superseded`
  stays 3.

**Do not move** `EXPECTED_QUEUED_ROWS`, `EXPECTED_SEED_LINES` or
`EXPECTED_SEED_STRUCK`: `0042` is not in `ARCHITECTURE.md` §5's seed list, which
holds `0001`–`0018`. Do not add it there.

Add a dated `#:` comment in that file's established style recording what landed
and that it landed `Proposed`. Two blocks move — the two counts at `:52-53` and
`EXPECTED_STATUSES` at `:85`; the file's convention, as `:79-81` does for
`0041`, records the whole move in the `EXPECTED_STATUSES` comment block.

**`tests/test_command_blocks.py` reads `decisions/*.md` too** — its surface at `:38` is
`DOCS = sorted(ROOT.glob("*.md")) + sorted(ROOT.glob("decisions/*.md"))` — so the new record
enters it. Nothing in §1 requires a fenced block, and the guard fires only on a
block whose command spends a shell variable the block does not set. If you write
a fenced block anywhere in the record, do not spend an unset `$VAR`.

**`tests/test_tautology_sweep.py` is untouched by this build, and that has been
verified rather than assumed.** Its `PINNED` entries hold assertion *source
text* keyed `(module, source, count)`, so changing a pin's **value** changes no
source; no new module and no new assertion is added here, so `assert not new`,
`assert not gone` and the `modules`/`asserts` floor are all unaffected. Confirm
it by running `pytest tests/test_tautology_sweep.py` and reporting the result.

---

## 2. Out of scope

- **`HYPOTHESIS.md`.** Not one byte. No version, no §4 count, no phrase
  correction. That is prompt 47.
- **`decisions/0041-*.md`.** It is `Accepted`: no edit, no note, and its Open
  questions section is left exactly as it stands, including *"Not decided here."*
- **`notes/REVIEWER-DEFECTS.md`.** Do not add or tick a closure row. The register
  closures are the reviewer's later turn, on the precedent `ADR-0041`'s own
  Consequences item 9 sets (*"The reviewer records the closing commit in
  `notes/REVIEWER-DEFECTS.md`"*).
- **The three `walk/` sites in the preamble table.** Named so the record can say
  P4 narrows; **not** to be edited here. No banner, no correction record.
- **R36, R37, W4, W8, W9, W12.** Later prompts.
- **`notes/scripts/`** — protected by `ADR-0041` item 8 (*"Execution records are
  not edited."*). It carries 23 of the 43 `ruff check .` errors; that is R35's
  subject.
- The three notebooks. Permanently out of scope per `CLAUDE.md`.

- **`decisions/README.md:11`'s dated round-trip count.** It reads *"against the
  39 records `decisions/` now holds"*, already stale at 40 and two stale after
  this build. **Leave it**, on the reason prompt 43 gave when it declined the
  same repair (`notes/prompts/43-land-adr-0041.md:86`): it is a 2026-11-11
  measurement, and a dated measurement is not corrected by a later build that
  happens to move the number. Report it as seen and left.

**Stale-key search.** With `LC_ALL=C.UTF-8`, search the tree for `ADR-0041`,
`0041-a-registered-headline` and `Not decided here`, and report every hit with
its disposition. `ADR-0041` has hits in the low hundreds across thirteen files, and **no count is
quoted here on purpose**: this prompt itself carries about a quarter of them, so
any figure written here is stale the moment the prompt is edited — which
happened twice, in two revisions, before the figure was dropped. Measure it if
you want it; the instruction does not depend on it. **Group by file with one
disposition per group**; enumerate individually only
where a hit's disposition differs from its file's. Expect most to be correct as they stand: this build adds a
record and renames nothing. **A dated reviewer or build record that quotes
`ADR-0041` as it stood is a historical quote and is left alone.** Report the hits
and their dispositions; do not report a bare zero.

---

## 3. Report

Close with `CLAUDE.md`'s four points. Points 1, 5 and 6 below are **refinements
of** points 1, 3 and 4; points 2, 3 and 4 are refinements of point 2. None is an
addition — do not write any of them twice.

1. **The five checks, each with its target stated:**
   `pytest -p no:cacheprovider` (full suite); `pytest tests/test_schema.py`;
   `ruff check bzk tests`; `ruff format --check bzk tests`; `mypy bzk tests`.
   Five, not four. A check not run is reported as **not run**. Report the suite
   as its two numbers (passed, skipped), not as "green".
2. **`pytest tests/test_decision_index.py`** on its own, with the pin values
   before and after, and **`pytest tests/test_tautology_sweep.py`** confirming
   the sweep is untouched.
3. **The index guard made to fail.** It is the thing this build could most
   plausibly break silently, so prove it fires. Revert **`EXPECTED_WRITTEN_ROWS`
   alone**, from 41 back to 40, leaving the other two moved; confirm
   **`pytest tests/test_decision_index.py`** goes red and **quote the failure
   message**. Mutation discipline, in this order: delete every `__pycache__`
   **first**, then run with `PYTHONDONTWRITEBYTECODE=1` — the variable stops a
   run writing a cache but not reading one already on disk. Read the mutated file
   back off disk to prove the source changed, and read the **failure message**
   rather than taking the exit status: a source-based `.pyc` is reused when size
   and mtime-to-the-second both match, so two mutations of equal length in the
   same second are indistinguishable to the import system and the second runs the
   first one's code. That produced a false *pass* on 2026-11-08. Revert, and
   confirm the full suite back at `1305 passed, 15 skipped` **plus** the record's
   own effect before writing the report.
4. **A closing table**, one row per claim this prompt makes, with the quoted
   minimum text that carries it and whether the build confirmed or contradicted
   it. Quoting conventions: the minimum text carrying what the row claims;
   leading and trailing whitespace is not content; line furniture is not content
   (table pipes, separator rows, `- `, `## n. `, `> `, JSON punctuation); a bold
   run-in label follows its paragraph.
5. **What this build did not cover**, plainly. State these explicitly rather
   than leaving them inferred:
   - Whether `ADR-0042`'s narrow reading leaves any *other* live `HYPOTHESIS.md`
     claim withdrawn elsewhere and not taken up. **Do not go looking** — say it
     was not checked, and that it is a named later item rather than a settled
     question.
   - That the three-site enumeration in `## Consequences` is a floor, not an
     exhaustive measurement.
   - That the record is `Proposed`, so the decision is recorded but the record is
     unreviewed.
   - **That the `0041` ↔ `0042` cross-reference is guarded by nothing.** Both
     directions are now written — `0042`'s row and row 94's forward pointer — but
     no test asserts that a record whose preamble amends another names it in that
     record's README row. The assertion is writable, so `CLAUDE.md` point 3 says
     it should be written; it is **not** written here. Name it as a later item,
     not as a settled question, so it does not die in this sentence the way
     point 3 records the change-set discriminator doing.
6. **Anything in this prompt dropped or partially done** — only this turn can
   report it.

**Landing it.** Commit to `main` per `CLAUDE.md`, as one commit, after the report
is written and the suite is green. Do not push a correction by amending: if you
find something after pushing, it is a new commit with a line saying why.
