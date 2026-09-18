# Report — commit the frame and walk artefacts, then push

**Run at:** 2026-09-18 · **Opened at:** `700d5bf` · **Commits:** `3422d51`, `e481547`, `8a1b4b7`, and this report's own

---

## R0 — state at the open

```
700d5bf 2026-09-18 15:39:42 +0100 decisions: review ADR-0033 and accept it as a coverage repair

?? data/frame/
?? notes/prompts/
?? notes/reports/
?? walk/

git log --oneline origin/main..HEAD
700d5bf decisions: review ADR-0033 and accept it as a coverage repair
```

**HEAD was not pushed.** One commit — last turn's acceptance of ADR-0033 — was ahead of `origin/main` at `d46a3ab`. Four untracked directories, `walk/` among them because the copy step ran before this prompt.

---

## Receipt checks

### R1 — `.gitignore`'s opening comment, quoted

```
# Source data — never committed.
# Deposits are fetched from PRIDE by the notebooks and the ingestion adapters.
# Under invariant I9 the graph is derived from these, so committing them adds
# weight without adding recoverability. Curation records ARE committed, because
# they are the one thing that cannot be regenerated.
```

**The test it states is recoverability, not size.** Both halves say so explicitly: deposits are excluded because committing them "adds weight **without adding recoverability**", and curation records are included because they "are the one thing that **cannot be regenerated**". Size is named only as the cost side of a term whose benefit is recoverability; it is never the criterion on its own.

### R2 — what is tracked under `data/`

```
data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json
data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json
data/curation/curation_PXD018299.json
data/curation/curation_PXD055843.json
data/curation/resolution_PXD018299.json
```

Five files, all under `data/curation/`, all JSON. The convention is `<kind>_<PXD accession>[_<contrast>].json` — kind first, accession second, and for an analysis record the contrast appended. No other subdirectory of `data/` is tracked.

### R3 — every untracked path, file by file

```
?? data/frame/200
?? data/frame/FRAME-SPEC.md
?? data/frame/FRAME-v1.md
?? data/frame/frame.py
?? data/frame/frame_raw.tsv
?? data/frame/probe.py
?? data/frame/probe_v2.json
?? data/frame/probe_v3.json
?? notes/prompts/01-verify-and-land-selection-adr.md
?? notes/prompts/02-verify-imputation-adr-zero-handling.md
?? notes/prompts/03-correct-and-land-imputation-adr.md
?? notes/prompts/05-land-the-frame-and-walk-artefacts.md
?? notes/reports/03-imputation-adr-report.md
?? notes/reports/04-adr-0033-review-report.md
?? notes/reports/REVIEW-ADR-0033.md
?? notes/reports/last.md
?? notes/reports/run.md
?? walk/PREREG-PXD026748-ingest.md
?? walk/WALK-STANDARD.md
?? walk/walk_PXD026748.json
```

Twenty files. **`STEP2-R1-SCAN.md` is not among them: it does not exist in `~/Downloads`**, so the copy step's `2>/dev/null` swallowed the failure and the file named in the task was never available to commit.

### R4 — what exists at top level

```
ARCHITECTURE.md  CLAUDE.md  GLOSSARY.md  HANDOFF.md  ONTOLOGY.md  OPERATIONS.md
README.md  RESPONSIBILITY.md  ROADMAP.md  VISION.md
bzk/  data/  decisions/  notes/  tests/
colab_identityresolution.ipynb  colab_reproducefigure.ipynb  colab_seethedata.ipynb
pyproject.toml  uv.lock
walk/   (untracked, created by the copy step)
```

**There is no top-level home for an instrument or standard that is neither code, decision, nor curation record.** The ten governing documents are single files; `decisions/` holds ADRs; `data/` holds curation records; `notes/` tracks exactly one file today — `notes/adr-0033-zero-handling-verification.md`, a working note — so in practice `notes/` is where unlanded drafts sit.

---

## Expectations

| # | expectation | result |
|---|---|---|
| **E1** | `.gitignore`'s test is recoverability, not size | **Held.** Quoted in full above: "adds weight without adding recoverability" / "the one thing that cannot be regenerated" |
| **E2** | `data/` contains only `data/curation/`, five tracked files | **Held exactly.** Five files, one directory |

### Does the dated-observation argument survive R1?

**Yes, and R1 is what carries it.** `.gitignore` excludes a deposit because re-fetching it from PRIDE returns the same artefact — the exclusion costs nothing in recoverability. `frame_raw.tsv` does not have that property: **re-running the query returns a different answer**, because PRIDE's index grows and the term hits with it. What the file records is the state of the archive under a fixed term set on **2026-09-17**, and nothing regenerates a past state of a live index.

So the earlier note calling it "closer to a cache than a record" fails on `.gitignore`'s own test rather than on taste: a cache is discardable because it is re-derivable, and this is not re-derivable. It is a dated observation, which is the same class as a curation record — not regenerable — and it is committed for that reason.

Had R1's test turned out to be size or file type, the argument would not have carried and the instruction was to stop. It did not.

---

## Every file committed

### `3422d51` — `data(frame): commit the frame evidence ADR-0033 rests on`

| file | bytes |
|---|---|
| `data/frame/FRAME-SPEC.md` | 7,810 |
| `data/frame/FRAME-v1.md` | 4,793 |
| `data/frame/frame_raw.tsv` | 400,825 |

327 insertions. The defect closed: ADR-0033 is Accepted and cites `FRAME-SPEC v1` and `FRAME v1` as its evidence base, and its own review recorded that it could not verify Frame B's eleven members because those artefacts lived outside the repository.

### `e481547` — `walk: add WALK-STANDARD v2, the PXD026748 walk and its pre-registration`

| file | bytes |
|---|---|
| `walk/WALK-STANDARD.md` | 15,174 |
| `walk/walk_PXD026748.json` | 14,403 |
| `walk/PREREG-PXD026748-ingest.md` | 5,411 |

602 insertions. The commit body states that `PREREG-PXD026748-ingest.md` is a **registered prediction whose whole value is being committed before the run it predicts**, that every figure in it carries its basis, expected direction and falsifier, and that no ingest of `PXD026748` has been run.

### `8a1b4b7` — `notes: track the audit trail — task prompts, reports and the ADR-0033 review`

| file |
|---|
| `notes/prompts/01-verify-and-land-selection-adr.md` |
| `notes/prompts/02-verify-imputation-adr-zero-handling.md` |
| `notes/prompts/03-correct-and-land-imputation-adr.md` |
| `notes/prompts/05-land-the-frame-and-walk-artefacts.md` |
| `notes/reports/03-imputation-adr-report.md` |
| `notes/reports/04-adr-0033-review-report.md` |
| `notes/reports/REVIEW-ADR-0033.md` |

934 insertions. **There is no `04` prompt file** — that task was given inline and never written to `notes/prompts/`, so `04-adr-0033-review-report.md` is the only record of what was asked.

### This report

`notes/reports/05-land-artefacts-report.md`, committed on its own as a fourth commit of the audit-trail kind. `notes/reports/log.md` does not exist, so nothing was appended to it. A file cannot carry its own commit hash; that SHA is in the session report.

---

## The structural choice for the walk artefacts

**Top-level `walk/`, not `notes/walk/`.** The grounds are two measurements from the receipt checks, not preference:

1. **`notes/` is the drafts area.** R4 found exactly one tracked file in it — a verification working note. A standard that an **Accepted** ADR leans on does not belong in the directory where unlanded drafts live; that would understate its status in the one place a reader looks to judge status.
2. **ADR-0033 cites it as an instrument.** Its R3 reads that `WALK-STANDARD`'s R1–R5 is the thesis-side assessment standing beside C0, and its closing section proposes treating `FRAME` plus `WALK-STANDARD` as the per-artefact instrument. Two instruments, one of which already has a top-level home in `data/frame/`.

**The argument against, stated because it is real:** `CLAUDE.md` says the document set is deliberately small and to prefer amending a document over adding one. A new top-level directory is the heavier move, and `notes/walk/` would have cost nothing structurally. The reason it loses is that `notes/` currently *means* draft, and putting a cited instrument there changes what the directory means rather than what the file means.

**A third option I did not take, recorded so the choice is visible:** `data/walk/`, beside `data/curation/`. The walk records are dated determinations of exactly that class, and it would have added no top-level directory. It fails because `WALK-STANDARD.md` is an instrument, not a record, and splitting the standard from the records it governs is worse than housing both outside `data/`. The prompt offered two options; this is the one it did not, and it is named rather than silently discarded.

---

## Left untracked deliberately

| path | why |
|---|---|
| `data/frame/frame.py` | **The one I would revisit.** It is the query script that produced `frame_raw.tsv` — 3,466 bytes, the term set and the PRIDE v3 call in full. The task enumerated three files as the frame evidence and this is not one of them, so it stays out; but a dated observation whose query is absent is only half-auditable, and a reader cannot check the term set against `FRAME-SPEC`'s §1 without it. Recorded as a gap, not a decision |
| `data/frame/probe.py`, `probe_v2.json`, `probe_v3.json` | Scratch from working out the API's response shape. `probe_v2.json` and `probe_v3.json` are **byte-identical** (44,412 bytes each), which is itself the sign that they are iterations rather than records |
| `data/frame/200` | Zero bytes. A stray from a shell redirection, not an artefact |
| `notes/reports/last.md`, `notes/reports/run.md` | Both are `git log` output redirected to a file. They are regenerable from the history itself, so under R1's test they are on the excluded side for the same reason a re-fetchable deposit is |
| any `PXD026748` curation record | **None was copied in.** The task said to leave such a file untracked if present; there is no such file anywhere in the working copy or in `~/Downloads`. Nothing was excluded on this ground because nothing existed to exclude |

---

## Checks run

The suite was **not** run, as instructed. Three tests were run because they are the ones that scan repository paths and could break on a new directory:

- `tests/test_command_blocks.py` — globs top-level `*.md` and `decisions/*.md`; the new files are in `data/frame/`, `walk/` and `notes/`, so out of its reach
- `tests/test_curation_content_hash.py` — globs `data/curation/*.json` and `tests/fixtures/*.json`; `data/frame/` is out of its reach
- `tests/test_decision_index.py` — unchanged by this turn

```
29 passed in 0.88s
```

`tests/test_tautology_sweep.py` scans `*.py` under `tests/` and `bzk/` only, so `data/frame/frame.py` would be outside it even had it been committed. **Not run:** `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk tests`, and the full `pytest` — this turn adds no Python and no source file.

---

## Push

```
To github.com:bzkzhao/bzk-omics.git
   d46a3ab..8a1b4b7  main -> main
```

`origin/main` after the first push: **`8a1b4b7`**. The report commit follows it and is pushed immediately after; its SHA is the new `origin/main` and is recorded in the session report.

---

## Noticed in the copied files, and left alone

Nothing below was edited. This is transport and tracking.

1. **`WALK-STANDARD.md` cites two walk records that are not in the repository** — `walk_PXD074990_m6.json` at l.13, which carries the correction to v1's motivating instance, and `walk_PXD065158.json` at l.163, which carries a recorded instance of a deposit misreporting its parameters. **This is the same defect this turn exists to close, one level in:** a committed standard resting on evidence a reader cannot reach.
2. **`walk_PXD026748.json` records `"standard_version": "WALK-STANDARD v1"`**, walked 2026-09-17, while the standard committed beside it is **v2**, dated 2026-09-18. The record was judged under a version that is not in the repository and is not recoverable from it — only its successor is. The v2 changelog names every change, so the delta is readable, but the text the walk was actually judged against is not.
3. **`REVIEW-ADR-0033.md` says "Four findings"**; the record it produced, `decisions/0033-frame-is-a-coverage-repair.md`, carries **five** — E, the unchecked C0(b), was added during the review turn. Committed unedited: it is the reviewing document as written, and correcting its count now would be back-dating.
4. **Its title still reads "the frame as a query-set repair"**, the name review finding A struck. Same reason.
5. **Two cross-checks that held**, worth recording because they are the cheapest evidence that the frame files belong together: `frame_raw.tsv` carries **73 data rows**, matching `FRAME-v1.md`'s "term-confirmed locally across the four fields — 73"; and `FRAME-v1.md`'s accession tables carry **16 rows**, matching its 11 Frame B plus 5 undecided.
6. **`FRAME-v1.md` closes the first of ADR-0033's four unverifiable items.** Frame B's eleven members are now named in-repo, with file counts and titles. It does **not** close the other three: the members' species and search engines are not in the table, `PXD026748`'s PRIDE record is still unfetched, and whether Frame B's criterion tracks C0(c) remains what the registered falsifier exists to test. The eleven are still the reviewer's judgement, now readable rather than independently confirmed.
