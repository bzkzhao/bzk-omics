# Report — close the four gaps report 05 found, and record one that cannot be closed

**Run at:** 2026-09-18 · **Opened at:** `775ef51` · **Commits:** `473780d`, `20a2f97`, `c66b2bb`, and this report's own

---

## R0 — state at the open

```
775ef51 2026-09-18 15:55:13 +0100 notes: report the frame and walk artefact landing

?? data/frame/200
?? data/frame/frame.py
?? data/frame/probe.py
?? data/frame/probe_v2.json
?? data/frame/probe_v3.json
?? notes/prompts/06-close-the-artefact-gaps.md
?? notes/reports/last.md
?? notes/reports/run.md
?? walk/STEP2-R1-SCAN.md
?? walk/walk_M4_M5.json
?? walk/walk_PXD065158.json
?? walk/walk_PXD071724.json
?? walk/walk_PXD074990_m6.json

git log --oneline origin/main..HEAD   →   (empty)
```

**HEAD was pushed.** `main` and `origin/main` were level at `775ef51`.

---

## Receipt checks

### R1 — `walk/WALK-STANDARD.md`'s version line and its v1 changelog entry

Version line, l.3–4:

> **v2, 2026-09-18.** Working copy: `/Users/bzk/bzk-omics`.
> Supersedes v1 (2026-09-17). Changelog at the end names every change.

The v1 entry, as it stood at the open — a single line, the whole record of the prior version:

> **v1, 2026-09-17** — first version, written before any candidate was walked.

### R2 — `walk/walk_PXD026748.json`'s `standard_version`

```json
  "standard_version": "WALK-STANDARD v1",
```

### R3 — what is tracked in `walk/` and `data/frame/`

```
data/frame/FRAME-SPEC.md
data/frame/FRAME-v1.md
data/frame/frame_raw.tsv
walk/PREREG-PXD026748-ingest.md
walk/WALK-STANDARD.md
walk/walk_PXD026748.json
```

Three and three, all landed by turn 05.

### R4 — `data/frame/frame.py`

**Present and untracked**, 3,466 bytes, standard library only. Its term set, verbatim:

```python
MODIFIER = ["ISG15","ISGylation","ISGylated","ISGylome","interferon-stimulated gene 15"]
MACHINERY = ["UBA7","UBE1L","UBE2L6","UbcH8","HERC5","HERC6","TRIM25","ARIH1","HHARI"]
REMOVAL = ["USP18","UBP43","deISGylase","deISGylating","deISGylation"]
CONDITIONAL = ["USP16","USP24","USP36"]
TERMS = MODIFIER + MACHINERY + REMOVAL + CONDITIONAL
FIELDS = ["title","projectDescription","keywords","sampleProcessingProtocol"]
```

---

## Expectations

| # | expectation | result |
|---|---|---|
| **E1** | `frame.py`'s term set matches the spec's twenty-two terms exactly | **Held exactly** — 5 + 9 + 5 + 3 = 22, identical as sets *and in the same order*, group for group. Set difference in both directions: empty |
| **E2** | `WALK-STANDARD.md` cites `walk_PXD074990_m6.json` and `walk_PXD065158.json`, neither tracked | **Held** — cited at l.13 and l.163; `git ls-files walk/` at the open listed neither |

**One correction to the prompt's premise, small but worth stating so a later reader is not sent to the wrong section:** the term set is in **FRAME-SPEC §2, "Term set"** (l.41–44), not §1. §1 is *"Why a frame, and why the existing one will not do"*. The comparison was made against §2 and E1 is measured against it.

`FIELDS` also matches §3 — *"Title, description, keywords, and sample-processing protocol. All four"* — and the script's four positive controls (`PXD018299`, `PXD055843`, `PXD065158`, `PXD071724`) match §8's.

### Two divergences the committed script exposes

E1 held, so neither is a term-set failure. Both are what having the script beside the spec is *for*, and both are reported rather than edited.

**1. The conditional-term rule is coded more broadly than the spec states.** §2 admits the cross-reactive DUBs *"only in combination with a modifier term"*, where **modifier** is the name of one specific row — `ISG15`, `ISGylation`, `ISGylated`, `ISGylome`, `interferon-stimulated gene 15`. `frame.py` implements:

```python
mod = any(t in hits for t in MODIFIER + MACHINERY + REMOVAL)
```

which accepts a co-hit on **any** non-conditional term, machinery and removal included. A deposit hitting `USP24` and `UBA7` but no modifier term would be kept by the code and excluded by the spec.

**The divergence is latent in this draw, measured and not assumed:** of the 73 rows in `frame_raw.tsv`, **zero** carry a conditional term without a modifier term. The broader rule admitted nothing extra, so FRAME v1's counts do not move. It would bite on a re-draw.

**2. FRAME v1's figure of 53 is not reproducible from the committed artefacts.** The counts table reads *"after the conditional-term rule (secondary enzymes need a modifier co-hit) — **53**"*. Measured against `frame_raw.tsv`:

| rule | n |
|---|---|
| all rows as written by `frame.py` (already post-rule) | **73** |
| require a co-hit from the `modifier` row | 49 |
| require a co-hit from modifier **or** removal | 51 |
| require a co-hit from modifier **or** machinery | 71 |
| `Homo sapiens` only | 65 |
| two or more terms | 29 |

**None gives 53.** `frame_raw.tsv` is already post-rule at 73, so whatever produced 53 is a step that is not in the committed script and not derivable from the committed TSV. FRAME v1's downstream figures do not depend on it — Frame B's eleven and the five undecided are judged from the rows themselves — but 53 is an intermediate a reader cannot reproduce. Left alone; it is FRAME v1's to correct.

---

## Every file committed

### `473780d` — `data(frame): commit the query that produced frame_raw.tsv`

`data/frame/frame.py`, 76 insertions. The commit body carries E1's result in full, the four groups with their counts, and both divergences above.

### `20a2f97` — `walk: add the four missing walk records and the R1 scan`

| file | bytes |
|---|---|
| `walk/walk_PXD065158.json` | 36,798 |
| `walk/walk_M4_M5.json` | 9,217 |
| `walk/STEP2-R1-SCAN.md` | 8,882 |
| `walk/walk_PXD071724.json` | 5,309 |
| `walk/walk_PXD074990_m6.json` | 4,338 |

827 insertions. **Landed exactly as copied.** The loss note was added in the *next* commit, and the four files were restored from the source copies before staging so that this is verifiable from the diff rather than asserted: `c66b2bb` adds one line to each and nothing else.

### `c66b2bb` — `walk: record that WALK-STANDARD v1 is lost and cannot be recovered`

Six files, 17 insertions: `WALK-STANDARD.md` (+12) and one line in each of the five walk records.

### This report

`notes/reports/06-close-artefact-gaps-report.md`, committed on its own. `notes/reports/log.md` does not exist.

---

## The wording used for the v1 loss

### In `walk/WALK-STANDARD.md`, under the v1 changelog line

> **v1's text is lost, and this changelog is all that survives of it.** v2 was written by overwriting v1 in place rather than by keeping the prior version, so v1 is not recoverable — not from this repository, not from the working directory it was written in. **Every walk artefact in this repository names v1** — all five records (`walk_PXD026748.json`, `walk_PXD065158.json`, `walk_PXD071724.json`, `walk_PXD074990_m6.json`, `walk_M4_M5.json`) carry `"standard_version": "WALK-STANDARD v1"`, and `STEP2-R1-SCAN.md` is headed *against WALK-STANDARD v1*. Their verdicts were measured against a text no reader can now read, and the entries above are the only account of how that text differed from this one. **v1 is deliberately not reconstructed from this changelog.** Reversing the entries out would produce a document that had never governed anything, and committing it as v1 would be worse than the gap it filled.

### In each walk record, beside `standard_version`

```json
"standard_version_note": "WALK-STANDARD v1 is not in this repository and cannot
be obtained. v2 was written by overwriting v1 in place, so v1's text is not
recoverable from anywhere; only WALK-STANDARD.md v2 and its changelog survive.
The verdicts in this record were measured against v1, and a reader cannot see
the text they were measured against. v1 is deliberately not reconstructed from
the changelog."
```

### One extension of the instruction, made deliberately and reported

The prompt named `walk_PXD026748.json` for both the changelog sentence and the new field, because it was written before the other records were copied in. **Measured, the loss is five times wider:** every one of the five walk records carries `"standard_version": "WALK-STANDARD v1"`, and `STEP2-R1-SCAN.md` is headed against v1 on its face.

The note is therefore written into **all five** records, on the prompt's own stated ground — that a reader of the record should learn it there rather than by grepping — which applies identically to each. `STEP2-R1-SCAN.md` has no such field and is named in the changelog instead. Nothing else in any record was touched.

---

## Noticed in the newly copied records, and left alone

1. **`walk_PXD065158.json` is not valid JSON.** At l.84, `"recurring_error_shape"` is written at element level *inside* the `"requirements"` array rather than as a key of the top-level object, so the array is never closed as an array: `json.load` fails with `Expecting ',' delimiter: line 84 column 28 (char 5799)`. The other four records parse. It is committed unrepaired because the repair is a judgement about where that block belongs — `requirements` is an array of R1–R5 objects, and the block is not one of them — and this turn is transport, not revision. It is the largest record of the five, 36,798 bytes, and the one `WALK-STANDARD` cites for a deposit misreporting its parameters. **Nothing in the repository reads `walk/`, so nothing breaks; a reader or a future loader does.**
2. **`HYPOTHESIS.md` is cited twice and is still not in the repository.** This is the "further citation to an artefact a reader cannot reach" the report asks for. It is not at top level and not tracked anywhere; `git ls-files | grep -i hypothesis` returns nothing.
3. **`STEP2-R1-SCAN.md` records its own limit on its face** — *"The recorded term set of WALK-STANDARD §4 source 1 was not applied — this was reading, not a systematic full-text search. Source 1 is therefore not exhausted for any candidate"*, grade P throughout, deepest grain G1, no FAIL available from the pass. Left exactly as written; it is a record of a bounded pass, not a claim to have exhausted one.
4. **`walk_PXD071724.json` carries `"verdict": "unresolved"`.** Committed as copied. An unresolved walk is a determination in its own right and is not a gap to fill here.
5. **Deposit-internal filenames cited across the records** — `Search_GlyGly.zip`, `Design.xlsx`, `sdrf.tsv`, `combined_site_K_114.0429.tsv`, `experiment_annotation.tsv` and a dozen more — are contents of PRIDE deposits, fetchable and therefore correctly not in the repository under `.gitignore`'s recoverability test. They are not gaps of the kind this turn closes.

---

## Checks run

Only the tests that scan repository paths, as instructed. The full suite was not run.

```
tests/test_command_blocks.py .......
tests/test_curation_content_hash.py ....
tests/test_decision_index.py .........
tests/test_tautology_sweep.py ..F....
1 failed, 34 passed in 1.73s
```

**The failure is pre-existing and is not caused by this turn.** `tests/test_tautology_sweep.py::test_every_classified_instance_re_runs_its_recorded_evidence` fails with

> `test_curation_loader.py: "{s['id'] for s in mapping.samples} == set(loaded.sample_ids.values())" is recorded as an instance because (…) stays green under `bzk/curation/loader.py`'s mutation, and it did not (exit 4).`

Two facts establish that it is not this turn's. `git diff --stat 775ef51..HEAD -- bzk tests` is **empty** — this turn touched no file the sweep reads; its roots are `tests/` and `bzk/`, and `data/frame/frame.py` is outside them. And the same test was run **at `775ef51` in a throwaway worktree** and failed identically there, before any of this turn's commits existed. Not fixed: it is neither a break on a new path nor in scope.

`ruff`, `mypy` and the full `pytest` were **not run**. This turn adds one Python file, `data/frame/frame.py`, which is outside `bzk` and `tests` and therefore outside all three of their targets.

---

## Push

```
To github.com:bzkzhao/bzk-omics.git
   775ef51..c66b2bb  main -> main
```

`origin/main` after the three commits: **`c66b2bb`**. The report commit follows and is pushed immediately after; its SHA is the new `origin/main` and is recorded in the session report.

---

## Left untracked, unchanged from turn 05

`data/frame/probe.py`, `probe_v2.json`, `probe_v3.json` (the last two byte-identical), the zero-byte `data/frame/200`, and `notes/reports/last.md` and `run.md` as regenerable from `git log`. **No `curation_PXD026748.json` was copied in** — there is no such file in the working copy or in `~/Downloads`, so nothing was excluded on that ground.
