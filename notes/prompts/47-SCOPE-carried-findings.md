# Prompt 47 — scope, and the findings carried into it

| Field | Value |
|---|---|
| Status | scope note, not a build prompt |
| Written | reviewer, 2026-11-24 |
| Depends on | prompt 46 (`ADR-0042`) having landed |
| Register items | P4 (**narrows**, does not close), R37, R36 |

**Why this file exists.** Prompt 46's adversarial rounds produced findings that
are not prompt 46's — they are defects in the *deferred* half. `CLAUDE.md` names
the failure these would otherwise hit: *"a session starting a turn … does not
hold the previous turn's instructions, so point 4 is unrecoverable at the open;
that is how the `RESULT_FOR_PROTEIN` fixture fix was lost."* Recorded here so
prompt 47 is written from them rather than rediscovering them.

---

## 1. Scope

`HYPOTHESIS.md` **v11**, plus the guard on §4's count, plus the line-reference
sweep the version forces. `ADR-0042` licenses it.

---

## 2. Findings carried in, each verified at `88b52e3`

### 2.1 The voice split has no precedent where revision 1 put it — BLOCKING

Measured: **zero `~~` marks anywhere in `HYPOTHESIS.md:1-369`** — not in the
three `**Previous version line (vN):**` entries, not in any of the **eight**
carried changelogs. `~~` appears on **ten lines** — `:548`, `:628`, `:630`,
`:759`, `:761`, `:768`, `:1066`, `:1095`, `:1174`, `:1200` — every one of them in
a body section, the lowest at `:548`, well below the `:369` where the carried
changelogs end. (Round 1 reported this list as six lines while calling it ten;
re-measured here. The load-bearing half — **none in `:1-369`** — is unchanged.)

So a strike inside the demoted v10 line or the carried `## 0-v10` is an
**invented correction form**, and every carried changelog is headed
*(carried, unchanged)* — striking inside one makes its own heading false.
`decisions/README.md` requires an invented form to be **named as invented**, or
it is *"an in-place edit with better manners, which is what the three routes
above refuse."*

**Disposition:** carry the historical lines **byte-identical** and put the whole
correction in the new `## 0`. No invented form, no false heading.

### 2.2 `:1203` is a live re-assertion, not an already-struck line — BLOCKING

The strike at `:1200` covers the **old label only**
(`~~**Threshold parity, open and answerable today.**~~`). The phrase *"reproduces
the anchor's own published call count with nothing fitted"* sits at `:1203` in
the bullet's **live, unstruck bold replacement text**, written 2026-11-06 in the
document's own voice — which is why it *"was re-added after the withdrawal"* and
is the fact P4 turns on. It therefore belongs in the **corrected** bucket.
Striking it would also nest a strike inside a completed `~~…~~ **…**`
replacement, a form that exists nowhere in the repository.

### 2.3 `:638`'s `**v10:**` prefix makes rule and enumeration disagree — BLOCKING

`:638` reads `- **v10:** the level is **27.8%** … reproduces this deposit's own
published call count to within 2% with nothing fitted.` A voice *rule* reads the
`**v10:**` prefix as marking a record; an *enumeration* that omits `:638` leaves
it live body text. Two compliant readings, two different artifacts in a
registered document — this project's recurring prompt defect.

**Disposition:** the prefix **dates the restatement**; it does not quote v10's
changelog. `:638` states D7's current status in the document's own voice and is
**corrected**. Say that explicitly rather than leaving it to the rule.

### 2.4 `within 2%` is a third search key, and half the claim has no successor supplied — BLOCKING

The withdrawal falsifies **two** halves. Revision 1 named two search keys
(`nothing fitted`, `781 calls against 798`) and supplied a successor for the
*"nothing fitted"* half only.

`within 2%` is live at `HYPOTHESIS.md:48` and `:637`. At `:637` it sits on a
**different line** from `nothing fitted` at `:638`, so a builder applying the
supplied wording leaves *"reproduces … to within 2%"* standing — half a withdrawn
claim, which is the *"partial withdrawal"* the vocabulary refuses
(`walk/CHECKS-membership-and-corrections.md:15`).

**Disposition:** three keys, each with its own floor, and a stated successor for
**both** halves: the 689-against-798 figure and the **14% shortfall** replace
*"within 2%"*.

### 2.5 The new guard turns the suite red unless `PINNED` moves — BLOCKING

Confirmed empirically by the round-1 build:

```
AssertionError: 5 matching expression(s) or occurrence count(s) are not
classified: [('test_hypothesis_taxonomy.py',
'counts_claimed(document) == counts_present(document)', 1), …]
```

**The mechanism is `assert not new` at `tests/test_tautology_sweep.py:2416`,
not the floor.** `assert modules >= 60 and asserts >= 2726` at `:2409` is a
**floor**: adding a module and asserts passes it. What fails is any matching
`parse(x) == parse(y)` expression absent from `PINNED`.

**Disposition:** require the new comparisons classified in `PINNED` with a dated
block saying why none is an instance; **forbid** rewriting an assertion against a
literal to dodge the sweep. Move the floor too, per that file's own recorded
convention (read off `sweep()`, before and after, both reported). Name the sweep
in the report's check list.

### 2.6 `CAUGHT` cases cannot establish non-vacuity — MAJOR, guard design

From the round-1 mutation run: breaking the heading parser so it matched nothing
reddened the pins and **all three `UNCAUGHT` cases**, but **all four `CAUGHT`
cases stayed green** — they assert `!=`, and `(6, 1) != (0, 0)` holds when the
parser returns nothing.

**So `CAUGHT` alone is compatible with a parser that matches nothing.** The pins
and the `UNCAUGHT` set are what close the vacuous-pass mode. A guard spec that
leans on `CAUGHT` for non-vacuity has the failure it claims to prevent.

**Disposition:** pin **both** parsers' outputs, not just the section side, and
assert the pins **before** the comparison. Specify the signature as a pure
function of text (`disagreements(text: str)`), with the pins asserted in a
separate test that reads the real `HYPOTHESIS.md` — the two patterns
(`test_decision_index.py` reads real files; `test_maxquant_sites_composition.py`
is pure over synthetics) are different architectures and must be composed
deliberately.

### 2.7 Guard regexes must not be capped at the current classes — MAJOR

`^### D[1-7] ` cannot see a `### D8`, so a guard reusing it silently ignores the
next class to land — the exact event that produced R37. Mandate
`^### D(\d+) ` and `^### C(\d+) `. `CAUGHT` needs a `### D8` case; `UNCAUGHT`
needs `### D4 — Construction *(reinstated)*`, a marker form a marker-aware regex
can wrongly reject.

### 2.8 The line-reference sweep — BLOCKING

**At least 40 line-anchored references**, and the figure is a floor because
**two forms exist and only one is greppable.** The prefixed form —
`git grep -oh 'HYPOTHESIS\.md:[0-9]\+'`, excluding prompt 46 and this file —
gives 40 across ten files, at targets 5, 22, 30, 37, 39, 43, 56, 57, 81, 84,
310, 904, 918, 1018, all ≥ 5. **The repository's prevailing continuation form is
a bare backticked `` `:NNN` `` under a `HYPOTHESIS.md` antecedent**, which no
path-anchored grep reaches and which breaks identically. `decisions/0041-...:526`
cites P4's own four sites that way. Read the bare form **by eye, per file**. The version line begins at `HYPOTHESIS.md:3`, so
the shift starts at **line 3**, not line 5. **The shift is not uniform**:
references above the new `## 0` move by one amount, those below by another, so no
single offset applies. Nothing reads the file programmatically — the only hits
under `bzk/` and `tests/` are comments — so the suite stays green and the rot is
silent.

**The live repair burden is 23, not 40.** Of the 40, **17 sit in
`notes/prompts/43-` (4), `44-` (8) and `45-` (5)** — dated build prompts, which
are historical quotes under the same rule that leaves dated register rows alone.
The remaining 23 are in `decisions/0041-*.md` (9),
`walk/CORRECTION-PXD018299-H10-headline.md` (5),
`notes/REVIEWER-MAP-findings-5-and-6.md` (3),
`walk/CORRECTION-PXD018299-2341.md` (2), `tests/test_audit.py` (2),
`walk/CORRECTION-PXD018299-two-route-independence.md` (1) and `bzk/audit.py` (1).

**Plus this document's own four**, which are *not* historical quotes — they are
prompt 47's live input, and the v11 insert moves the targets they name.

**The breakdown by disposition is the point, and prompt 47 must measure it
itself from both instruments rather than inherit a number.** What is established:

- **`decisions/0041-*.md` is the largest block and is unrepairable by rule** — 9
  prefixed plus at least 12 bare (`:82-83`, `:177`, `:303`, `:526`). The record
  is `Accepted`, so the append-only rule bars repair. Record it as accepted rot
  or open an item; do not carry it silently.
- **`notes/REVIEWER-DEFECTS.md` has no settled disposition** — 8 bare (`:61`,
  `:134`), and it is neither a build prompt nor the one reviewer record
  `decisions/0041-...:481-482` exempts, so the historical-quote rule does not
  plainly cover it. Prompt 47 decides.
- **Exempt:** `notes/REVIEWER-MAP-findings-5-and-6.md` (3), which
  `decisions/0041-...:481-482` classifies as a *"Dated reviewer record"*; and the
  17 in prompts 43/44/45.
- **Repairable:** `walk/CORRECTION-PXD018299-H10-headline.md` (5 prefixed, +3
  bare at `:189`), `walk/CORRECTION-PXD018299-2341.md` (2),
  `tests/test_audit.py` (2, comments),
  `walk/CORRECTION-PXD018299-two-route-independence.md` (1), `bzk/audit.py` (1,
  a comment), plus this document's own four.

**Two levels of the same error, both recorded because the class recurs.** A
burden measured without asking which of it is dischargeable is one level short
of the countable — that is how "23 to repair" stood through two revisions. An
instrument defended without asking what *form* it matches is one level short of
that — `[0-9]\+` against `[0-9]*`, the exclusions and the refusal to quote a
self-referential total were all argued before anyone asked whether the pattern
matched the form the repository actually writes. It does not.

**And this document invalidated its own measurement by recording it** — the
references above and in §2.4 are themselves `HYPOTHESIS.md:NNNN` strings, so the
working-tree figure is higher than the committed one. Prompt 47 measures against
the commit it is based on and states which figure it repairs against. The
general lesson is the one `decisions/README.md:11` already records: a figure
*recorded* here rather than *derived* here goes stale, including when the act of
recording it is what moves it.

**Disposition:** compute each reference's new line from the actual diff; repair
those in live documents; leave those in dated records as historical quotes, with
the count stated. Where a reference points at a section rather than a sentence,
**re-anchor it by content**, per `decisions/README.md:11` (*"Cited by its content
rather than by its line, because this write moved that line and a within-file
line number in this file is a referent waiting to be lost"*). A bare "report
zero" against a three-string instrument is `CLAUDE.md` point 1's *"zero against
an unstated target"*, one level in.

### 2.9 Two smaller ones

- **The formula is v9's alone.** *"No registered hypothesis, threshold or class
  definition changes"* occurs **exactly once** in `HYPOTHESIS.md`, at `:11-12`
  (the v9 line). v10 uses a variant (*"as are D7's status and every threshold and
  class definition"*); v8 and v7 use neither. Quote v9 verbatim and attribute it
  to v9.
- **`**Status:**` is stale and nothing in revision 1 touched it.**
  `HYPOTHESIS.md:22-24` reads *"v1 to v8 are superseded"* — already wrong by one
  at v10, by two at v11. Update to `v1 to v10`, and record the pre-existing
  off-by-one under report point 3.
- **Naming the withdrawn claim is not reinstating it.** v11's `## 0` cannot
  identify the claim without quoting *"nothing fitted"*, which a flat "do not
  reinstate in any form" rule forbids. Say that quoting it as the *subject of the
  withdrawal* is required and is not a reinstatement.
- **Cite `:9-11`, not `:8-13`,** for the definition of *withdrawn*. `:12-13`
  defines the contrasting word, *superseded*; `ADR-0041` cites the two halves
  separately and correctly.

---

## 3. What prompt 47 still leaves open

**P4 narrows; it does not close.** Two live, unbannered restatements sit outside
`HYPOTHESIS.md`:

- `walk/CHECKS-convention-resolved.md:11` — *"## 1. The documented rule
  reproduces the anchor's own published count"*, the claim asserted as a
  **section heading**. The document's banner at `:3-7` supersedes only *"the
  *level* it was computed at, and nothing else"*, so it does not reach this.
  **This instance was missed by two rounds of enumeration** and found only in
  round 2 — the list was short by one in the item whose purpose is to record
  that P4 narrows;
- `walk/CHECKS-convention-resolved.md:24-26` — the claim's **origin**, which
  `notes/REVIEWER-DEFECTS.md:61` records as carrying no banner. The span is
  `:24-26`, not `:24-25`: `:26` carries *"That is a validation on the deposit
  under test"*, which is the clause the withdrawal names, and a narrower span
  drops it;
- `walk/PREREG-PXD032267-gate.md:225` — inside a **pre-registration** document,
  which carries no withdrawal banner anywhere.

**Three instances, and the enumeration is a floor rather than an exhaustive
measurement.** Cite each with its quoted text beside its line: the spanning
correction will add banners and shift these very lines.

After v11, `HYPOTHESIS.md` is corrected and the document it inherited the claim
from still asserts it. **That divergence is created by prompt 47, not inherited
by it**, and must be named in its report rather than left to be discovered. A
withdrawal spanning documents is the `walk/CORRECTION-*.md` form's job; that
record is a later prompt's, and the PREREG instance needs care because
pre-registrations are not ordinarily edited.
