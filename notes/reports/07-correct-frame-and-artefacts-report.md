# Report — correct the frame's 53, repair one record, land the off-repo documents

**Run at:** 2026-09-18 · **Opened at:** `4976521`, level with `origin/main` · **Commits:** `947cc7d` (defect 1), `2f1d6e5` (defect 2), none for defect 3, and this report's own

---

## Defect 1: FRAME v1's 53. Corrected; the frame is 73

### The three rules, re-derived against `frame_raw.tsv` before editing

| rule | expected | measured |
|---|---|---|
| **spec**: FRAME-SPEC §2, conditional = {`USP16`, `USP24`, `USP36`}; drop a row carrying one with no modifier co-hit | drops 0, keeps 73 | **drops 0, keeps 73** |
| **code**: `frame.py`, `any(t in hits for t in MODIFIER+MACHINERY+REMOVAL)` | drops 0, keeps 73 | **drops 0, keeps 73** |
| **the reviewer's unregistered rule**: drop a row whose terms ⊆ {`USP16`, `USP24`, `USP36`, `TRIM25`, `ARIH1`, `HHARI`} | drops 20, keeps 53 | **drops 20, keeps 53** |

All three held exactly. The cause the prompt states is confirmed: 53 is reproduced by the six-term rule and by nothing else.

### What was edited in `data/frame/FRAME-v1.md`

- **Counts row**: now reads *"after the conditional-term rule — FRAME-SPEC §2: `USP16`, `USP24`, `USP36` need a modifier co-hit. **Removed 0**"*, with the figure written as `~~53~~ **73** — corrected 2026-09-18`.
- **The Frame A sentence**: *"Frame A is not yet ~~53~~ 73"*. This is the second place 53 appeared. The prompt did not name it, but leaving it would have left the error standing one line below its correction.
- **A dated *Correction* note** under the counts. It records that 53 was published in error, that it came from a six-term secondary set FRAME-SPEC §2 never registered (§2 puts `TRIM25`, `ARIH1` and `HHARI` in *conjugation machinery*), the three-rule table above, and the ground for the decision: the registered spec governs, because amending §2 to fit a rule devised after seeing the results would amend a pre-registration to match its own output.

**53 is struck, not deleted, in both places.** FRAME-SPEC was not amended.

**Nothing else in the repository cites the frame's 53.** I grepped `decisions/`, `ROADMAP.md`, `README.md`, `HANDOFF.md`, `walk/` and `data/`. The only hits were unrelated: `2**53`, a line number, and two ROADMAP survey-table cells. ADR-0033 does not carry the figure. Reports 05 and 06 mention it, but they are dated records and are left as written.

### The twenty rows the unregistered rule would have dropped

Reported, not acted on. Whether they belong in the frame is a FRAME-SPEC question for its own turn.

| accession | matching terms | title (truncated) |
|---|---|---|
| `PXD007960` | TRIM25 | RNA-binding activity of TRIM25 is mediated by its PRY/SPRY domain |
| `PXD008914` | TRIM25 | RNA-binding protein repertoire of embryonic stem cells |
| `PXD011840` | TRIM25 | Structural and functional characterization of ubiquitin variant inhibitors |
| `PXD024808` | TRIM25 | Profile of the SARS-CoV-2 RNA interactome |
| `PXD028122` | TRIM25 | Ubiquitination of DEAD-box RNA helicase DDX3X by TRIM25 |
| `PXD030849` | ARIH1; HHARI | Cullin-independent recognition of HHARI substrates by a dynamic RBR |
| `PXD031993` | TRIM25 | An anti-influenza A virus microbial metabolite acts by degrading viral |
| `PXD033447` | TRIM25 | ERG activity is regulated by endothelial FAK coupling with TRIM25/USP9 |
| `PXD034024` | TRIM25 | Substrate trapping approach identifies TRIM25 ubiquitination targets |
| `PXD036675` | TRIM25 | A degradation motif in STAU1 defines a novel family of proteins |
| `PXD037182` | TRIM25 | The E3 ligase TRIM25 impairs apoptotic cell death in colon carcinoma |
| `PXD037703` | TRIM25 | A degradation motif in STAU1 defines a novel family of proteins |
| `PXD041514` | TRIM25 | LINC00955 Suppresses Colorectal Cancer Growth by Acting as a Molecular |
| `PXD041773` | TRIM25 | LINC00955 Suppresses Colorectal Cancer Growth by Acting as a Molecular |
| `PXD043737` | TRIM25 | A novel microprotein HDSP encoded by HOXA10-HOXA9 triggers progression |
| `PXD053200` | TRIM25 | A novel microprotein HDSP encoded by HOXA10-HOXA9 triggers progression |
| `PXD053707` | ARIH1 | Absolute quantification analysis of ubiquitin chains conjugated to GP8 |
| `PXD061182` | TRIM25 | Discovery and optimisation of a covalent ligand for TRIM25 |
| `PXD063222` | ARIH1 | The major lysine residues of PD-L1 ubiquitinated by ARIH1 |
| `PXD073759` | ARIH1 | Proteomic analysis of HEK293T cells deficient in PRDX4 protein |

The unregistered rule's whole effect came from the three machinery terms it reclassified:

- **Sixteen** rows match `TRIM25` alone, **three** `ARIH1` alone, **one** `ARIH1` with `HHARI`. These counts were computed with a `Counter`; a first hand count in this report's draft read 15/4/1 and was wrong.
- **Not one** matches on a conditional DUB.
- **None of the twenty is among Frame B's eleven or the five undecided**, so both of those figures stand.

Three pairs share a title: `PXD036675`/`PXD037703`, `PXD041514`/`PXD041773` and `PXD043737`/`PXD053200`. That points to companion deposits rather than duplicates, and it is not examined here.

---

## Defect 2: `walk/walk_PXD065158.json`. Repaired

`"recurring_error_shape"` sat between R3 and R4 inside the `"requirements"` array. It is now at the top level, directly after `"requirements"`, dedented two spaces to match its new depth.

**The repair was checked directly, not inferred from a successful parse:**

- The sorted multiset of non-blank content lines is **identical** before and after, and the line count is unchanged at 401.
- `git diff --stat` shows **11 lines out, 11 in**: the ten-line block and its blank line, nothing else.
- `"requirements"` now reads **R1, R2, R3, R4**, and `"recurring_error_shape"` keeps its four keys.

`json.load` succeeds on **all five** records in `walk/`: `walk_M4_M5.json`, `walk_PXD026748.json`, `walk_PXD065158.json`, `walk_PXD071724.json`, `walk_PXD074990_m6.json`.

One check I ran was wrong for a move, and I'm recording it so a reader isn't misled by its result. It compared the file with all spaces stripped and reported False. A move changes order, so that comparison could never pass. The multiset check is the right one, and it held.

---

## Defect 3: four documents cited and absent. **Nothing committed; all four are missing**

The prompt says the files were copied in before it ran. **They were not.** No file named `HYPOTHESIS*`, `*WRITE_UP*`, `AUDIT_PLAN*` or `FINDINGS*` exists anywhere in the working copy. "Commit whichever are present" therefore commits nothing.

I did not copy them in from `~/Downloads` myself, because what is there does not match what is cited:

| cited as | in the repository | in `~/Downloads` |
|---|---|---|
| the findings document | missing | present as **`FINDINGS_runs_A1_A2_A3_G (1).md`**, 24,216 bytes. The `(1)` is a duplicate-download suffix, so the file's intended name is unknown |
| **`HYPOTHESIS.md` v3**, which the findings document stands against | missing | **only `HYPOTHESIS.md` v2 exists.** Its header reads *"Version: 2, superseding v1"*, so the one copy available is not the version cited |
| `PXD018299_WRITE_UP_AMENDED.md` | missing | **not found.** `PXD018299-writeup-2026-09-21.md` exists but has a different name, and HYPOTHESIS v2 names yet another, `PXD018299_WRITE_UP_FINAL_DRAFT.md`. Neither was substituted |
| `AUDIT_PLAN_2026-09-17.md` | missing | **not found** |

The findings document does name itself and the three others. Its header reads *"Standing against: `PXD018299_WRITE_UP_AMENDED.md`, `HYPOTHESIS.md` v3, `AUDIT_PLAN_2026-09-17.md`"*.

The `HYPOTHESIS.md` citations in the walk records are at `walk_PXD065158.json` l.263 and l.370. Both cite it only to place a question *out of this walk's scope*. Neither rests a determination on it.

### The §6.4 supersession: flagged here, since there is no defect-3 commit to carry it

The findings document's §6.4, *"The walk had no stopping rule"*, reads:

> `PXD074990` recorded *absent* for a source that exists because the walk followed a stale pointer and stopped.

`WALK-STANDARD` v2's preamble **withdraws** that claim, and `walk/walk_PXD074990_m6.json` carries the determination (*"M6 CLOSED. PXD074990's recorded verdict stands"*). The prompt wanted the link recorded in the defect-3 commit body. There is no such commit, so the link is recorded here, in a committed report.

**When the findings document lands, its commit body must carry the same note.** Otherwise the repository will hold a withdrawn claim and its withdrawal with nothing linking them.

---

## Checks run

Path-scanning tests only, as in turn 06:

```
tests/test_command_blocks.py, test_curation_content_hash.py,
test_decision_index.py, test_tautology_sweep.py
1 failed, 34 passed in 1.82s
```

The one failure is `test_every_classified_instance_re_runs_its_recorded_evidence`. It is the same failure turn 06 showed was **pre-existing**, by running it at `775ef51` in a throwaway worktree. This turn touched no file under `bzk/` or `tests/`.

`ruff`, `mypy` and the full `pytest` were **not run**. No Python was added or changed.

---

## Push

```
4976521..2f1d6e5  main -> main
```

After the two defect commits, `origin/main` is **`2f1d6e5`**. The report commit follows and is pushed immediately after it.

---

## Left untracked

- `notes/ADR-lysate-draft.md` and prompts `08` and `09`. They belong to the next two turns.
- `data/frame/probe.py`, `probe_v2.json`, `probe_v3.json`, the zero-byte `data/frame/200`, and `notes/reports/last.md` and `run.md`. All are unchanged since turn 05.
- `notes/prompts/07-…` **is** committed with this report.
