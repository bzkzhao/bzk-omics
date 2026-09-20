# Report — apply ADR-0035's review

**Run at:** 2026-09-20 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `ff54bf2`, the tree the review names · **Commits:** `82ee6d5`, `101bd4f`, `4b3f53f`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** The review's seven edits are applied and ADR-0035 is `Accepted`; its two consequences are landed as separate commits. **Every measurable claim in the review was re-derived here before anything was edited, and all of them held** — including the one that does the damage, the `sampleProcessing` field. E1-equivalent: 724 passed, 14 skipped, unchanged, because nothing this turn touches behaviour. **Two things I did beyond the review's list and one I deliberately did not do** are under point 4.

---

## Verification before editing

The review marks its figures **measured**, **read** or **judged**. I re-derived every one that could be, because the review's ruling (a) turns on a single quotation and applying it means striking a landed decision's premise.

| claim | marked | re-derived here |
|---|---|---|
| *"seeded in triplicate for each condition (WT or mutant PLpro)"* | read | **Present, verbatim**, in `data/frame/frame_raw.tsv`, `PXD026748` row, field 14 `sampleProcessing`. The actual text reads *"five millions cells"* (sic) |
| *"7.2 mg total protein of each replicate was treated with recombinant WT or mutant PLpro"* | read | **Present, verbatim**, same field |
| the aliquot sentence | read | **Present, verbatim**, same field: *"At this point, an aliquot of 30 µg total peptide was taken for shotgun proteomics analysis. The remaining peptide solution was incubated with antibody-bead slurry"* |
| `schema.py` names no Sample-to-Sample relation | measured | **Held.** The only three touching `Sample` are `PERFORMED_ON` (Experiment→Sample), `PRODUCED` (Sample→Dataset) and `SAMPLE_GENERATED_BY` (Sample→Analysis) |
| both records give `replicate` 1–3 | measured | **Held.** 12 keys each, values `[1, 2, 3]` in both |
| the two arms use different naming schemes | measured | **Held.** GG keys carry `Gly-Gly-{WT\|KO}[_mut]_repN`; shotgun keys carry `shotgun-{ctrl\|ko}_{wt\|mut}-N` |
| `Gly-Gly-WT_rep1` and `Gly-Gly-WT_mut_rep1` are in the GG record's keys | measured | **Held.** Both present; all 24 run names are now recorded across the two records |
| `tests/test_curation_pxd026748_arms.py` pins disjointness and field equality | measured | **Held** — it is the module landed at turn 11 |
| the GG record's PAIRING item records the contradiction | read | **Held.** Its `unresolved` opens *"PAIRING — the premise ADR-0035 records is contradicted by the deposit's own protocol"* |
| `decisions/README.md` allows editing a `Proposed` record | read | **Held.** *"Correcting a record during review is an ordinary edit to a `Proposed` document — that is what the status is for."* |

**One claim I could not check and did not assert.** F3's *"The publication's methods make the mutant C111A and call it the catalytic dead mutant"*. The paper is not on disk — report 09 says so at `:268` — so the ADR now **attributes** it to the reviewer rather than stating it, and says in the same sentence that this repository cannot check it. That is the treatment the ADR's own *Not verifiable from the repository* list already uses.

**The review's own framing, confirmed.** `frame_raw.tsv` was committed at `3422d51` on 2026-09-17; ADR-0035 landed at `3b7e969`, whose parent `0bd9653` its Landing verification was re-derived against. The protocol field was in the repository before the record landed and was not read for this point. That is not a hindsight finding.

---

## What changed

### `82ee6d5` — the ADR, edits 1–7

| edit | where | what |
|---|---|---|
| **A** | Context | *"one culture, split after lysis"* **struck**, with the seeding clause quoted as the ground and the dish phrase explicitly **not** relied on. The *compartment* claim is untouched — the protocol still puts the PLpro incubation after lysis; what is struck is the *split* |
| **A** | Context | The `WALK-STANDARD` v2 quotation is kept **verbatim**, because it is what v2 says, with a sentence noting its third clause does not survive and that v2 carries its own correction |
| **B** | R2 | Re-grounded on the **shared-source** relation, citing the aliquot sentence. Both of R2's reasons carried over, with the three `Sample` relations named. The `replicate` ground is marked as tested for the first time. Consequence narrowed to I4 `'applied'` at condition grain, with *no published analysis depends on it* stated |
| **C** | The defeater this produces | Narrowed to the **unstated block**; the *"unrepresentable design"* paragraph struck, with the thesis consequence stated rather than smoothed |
| **D** | R1 | The caution corrected to **24 materials over 12 dishes**, plus the two committed records and the test that pins them |
| **E** | R5 | The instance-count reset, and the note that the next instance must be counted as shared-source |
| **F1/F2** | The reading that looks right | The 24-run pattern claim and the one-filename claim **struck**; the *Not verifiable* entry for the two filenames struck |
| **F3** | Context | *"catalytically dead"* attributed to the publication, marked uncheckable here |
| **7** | header + new *Review* section | `Status` → `Accepted`, a `Reviewed` row citing the review file, and a six-row finding table |

**Every struck sentence is struck, not deleted.** I checked this the way 10b taught me to: the file contains real `~~` strikethroughs, and the ADR's new header says *"struck rather than deleted, so the correction is visible"* only because that is what was done.

**The review file is committed** as `notes/reports/REVIEW-ADR-0035.md`, following `REVIEW-ADR-0033.md`. Edit 7 says *"citing this file"*, which requires the file to exist.

**`EXPECTED_STATUSES` moved 20/11/3 → 21/10/3, seen to fail first:**

```
E  AssertionError: assert {'Accepted': 21, …} == {'Accepted': 20, …}
E    Differing items: {'Accepted': 21} != {'Accepted': 20}; {'Proposed': 10} != {'Proposed': 11}
```

That pin moving is what records the round-trip closing, and the comment beside it now says so.

### `101bd4f` — `WALK-STANDARD` v2

§7's `PXD026748` row moves **FAIL → UNRESOLVED**, its stated reason struck, with the new reason and a new *To clear* (author correspondence on the block structure).

**Why UNRESOLVED and not PASS**, stated in the row and again below it: the deposit does carry an unrepresentable relation — the cross-arm digest split — but it bears on this platform's protein adjustment rather than on any published claim, and the block structure that would decide R5 either way is unstated. PASS would assert nothing is lost; FAIL would name a lost relation the publication does not use.

The sentence *"The `PXD026748` instance is why R5 exists"* is **withdrawn**, and §7's *What R5 gives the thesis* loses its worked example while keeping its claim. The changelog gains a dated `v2, corrected in place 2026-09-19` entry saying why this is a correction and not a v3.

**The second-time observation is recorded rather than smoothed**, in both the row's note and the changelog: v1's motivating instance was `PXD074990` and was withdrawn in v2's preamble; v2's was this row. Both were picked from a read that stopped short of an artefact this repository already held.

### `4b3f53f` — `curation_PXD026748_shotgun.json`, rationale (2)

The item said the aliquot sentence is read from the publication *"not from the PRIDE record, which describes only the GG workflow"*. The committed protocol carries it verbatim, so the item named a secondary source as primary. Corrected in place with the date and the reason, per the record's own convention.

**One line changed. All 16 node ids unchanged**, measured before and after — `rationale` is not an identity field on any node. The file's sha256 moves `9501e5ca…95bd8a` → `2df1f719…71e8ad1`, which matters because prompt 13's base check quoted the old one; that quotation was true of that tree and is not edited.

---

## Checks — `CLAUDE.md` point 1, every one at its actual result, with its target

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **724 passed, 14 skipped** — unchanged from base |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **102 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 102 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

**The suite total does not move, and that is the expected result rather than a weak one.** This turn edits three documents and one pinned integer; no behaviour changes, so a moved total would have meant something went wrong. The one guard that had to move did move, and was seen to fail first.

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The ruling-(a) quotation was read out of the file before the premise was struck**, not taken from the review. So was every other measurable claim, in the table above.
- **The pin was seen to fail** before it was moved, with the message recorded.
- **Id stability was measured**, before and after, rather than argued from *"rationale is not identifying"*.
- **The strikethroughs were verified present in the file**, because 10b is the turn where I wrote *"struck rather than deleted"* about an edit that had struck nothing.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **The two design questions stay open**, and nothing here can close them: which shotgun `-N` came from which GG `_repN` digest, and whether same-index dishes were processed as blocks. **The second is now load-bearing in a way it was not before**: it is the whole of what survives of ADR-0035's defeater, so if the answer is *no blocks*, the record's defeater section loses its narrowed form too and the deposit has no reconstruction defeater from design at all.
- **The thesis is not updated.** Finding C says the claim-durability thesis loses this record as the motivating instance of an *"unrepresentable design"* class. I struck the claim inside ADR-0035 and inside `WALK-STANDARD`; **I did not go looking for other places the thesis asserts that class**, and did not grep for them. If the thesis has its own document that names `PXD026748` as the instance, it is still saying so.
- **`walk/walk_PXD026748.json`** — the machine-readable walk record — was not touched. It carries `"standard_version": "WALK-STANDARD v1"` and its own R5 verdict, and the review named only the standard's §7 row. Whether a v1-judged record should carry a v2 correction is a question the changelog already flags for every walk artefact, and it is not this turn's.
- **`notes/reports/HANDOFF-2026-09-19.md`'s *For Adán, 21 September* section** was not edited. It is a dated snapshot and lists three questions; the review adds two. I did not revise a dated report — see point 4.
- **ADR-0035 is now `Accepted` and therefore append-only.** Anything the review missed needs a superseding record, not an edit. I have no candidate; this is a statement of what the status now costs.
- **The tautology sweep's floor** — still stale, untouched. No new equality needed classifying.
- **`notes/prompts/`** — not written, not retyped, not committed.

---

## `CLAUDE.md` point 4 — instructions dropped, partially done, or exceeded

**Two things beyond the review's list, both small and both reported rather than folded in:**

1. **`decisions/README.md`'s Written row for 0035** described the record as *"the split-lysate pairing is declared in `unresolved`"*. After finding A that phrase names a thing the deposit does not have, so the index would have gone on describing the struck premise. Rewritten to the unrepresentable relation, with the review's correction named. The review did not ask for this; leaving it is the defect point 3 exists to catch.
2. **`tests/test_decision_index.py`'s `EXPECTED_STATUSES`** had to move for edit 7 to land at all. Not optional, and named here because it is the only test this turn changes.

**One thing deliberately not done.** The review's third consequence is *"For Adán, 21 September: the two design questions this review cannot settle"*. I put them in ADR-0035's new *Review* section, which is a live document, and they are in this report. **I did not add them to `notes/reports/HANDOFF-2026-09-19.md`'s Adán list**, because that file is a dated snapshot of 2026-09-19 and editing it would revise a past record to carry a later day's findings. If the intent was that the list is live rather than dated, that is a one-line addition and bzk's call — flagged rather than made.

**One judgement inside an edit, worth naming.** The review says finding A strikes *"`WALK-STANDARD` v2's 'three cultures split two ways', quoted in the Context as the reason being answered"*. I did **not** strike text inside the quotation: a quotation's job is to say what the quoted document says, and editing one to match a later finding makes the ADR misreport v2. The quotation stands verbatim, with a sentence after it saying which clause does not survive, and `WALK-STANDARD` carries the strikethrough in its own text where it belongs.

Nothing else was dropped. **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `82ee6d5` | `decisions: accept ADR-0035 on six findings, and re-ground R2 on the split the deposit has` — edits 1–7, the review file, the pin, the index row |
| `101bd4f` | `walk: correct WALK-STANDARD v2's PXD026748 row, FAIL to UNRESOLVED` |
| `4b3f53f` | `curation: name the committed protocol as rationale (2)'s primary source, not the publication` |
| this report's own | `notes/reports/14-apply-the-adr-0035-review-report.md`, alone |

**Push range:** `ff54bf2..4b3f53f` for the three changes, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `e05f2ae..4b3f53f` on the branch and `ff54bf2..4b3f53f` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase.
