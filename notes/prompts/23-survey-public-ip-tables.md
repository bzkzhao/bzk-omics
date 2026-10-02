# Prompt 23 — Survey of the public IP tables (measurement only)

**Repository:** `main` at `96c4ece`. Governing text: `notes/REVIEWER-HANDOFF-2026-10-02.md` §7.1
(l.101–110) and the caveats in §6 (l.89–97).

This is **measurement only**. No schema change, no ONTOLOGY edit, nothing under `bzk/` modified.
The prompt ends at the report.

---

## 0. Receipt check — answer all of these before anything else, then stop and wait

1. Run `git log --oneline -2` and `git status --short`. HEAD must be `96c4ece`. The only untracked
   path allowed is `notes/prompts/22-walk-two-route-independence.md`. If either condition fails,
   stop.
2. Quote l.104–109 of `notes/REVIEWER-HANDOFF-2026-10-02.md` verbatim. That is the five fields this
   survey records.
3. In `bzk/sources/pxd055843_perseus.py`, which function decides that a sheet is a Perseus export,
   and on what evidence? Cite the function name and its line numbers, and quote the condition it
   tests.
4. Where does the repository record the locations of the three source sets below? Give the file and
   line for each, or say "not recorded":
   - PXD055843 Supplementary Data S3 (check `data/curation/curation_PXD055843.json` first; give any
     row count recorded there);
   - PXD018299 `ISG15_interactome.xlsx`;
   - PXD018299's BJC supplementary tables.

Report the answers. **Do not start §1 until bzk replies.**

---

## 1. Blindness rule (applies to everything below)

The concordance measurement on PXD018299 is pre-registered later (handoff l.83–85, l.114–115).
The survey must not reveal where any protein falls. So for **both** deposits:

- **Never print, write or commit** gene names, protein accessions, or per-row values.
- **Allowed:** column headers, sample names, Perseus type-prefix rows, row and column counts, and
  aggregate statistics (counts, fractions, deciles).
- No filtering, sorting or lookup by protein: in particular, no check of whether any named protein
  is present.
- If a step can't be done without per-row output, skip it and say so in the report.

---

## 2. Acquire

- Fetch each file from the location found in §0.4. Use the PRIDE archive API for the PXD018299
  file if no URL is recorded.
- Work under `scratch/survey-23/`, untracked, and record the SHA-256 of every file used.
- If a source is unreachable or the file can't be found, **stop for that source**: report the URL
  and the error. Don't substitute another file.

## 3. Measure — for each IP table

| Field | How |
|---|---|
| **Type** | Perseus export or raw search output. Decide by the type-prefix stamp, using the reader logic cited in §0.3 rather than a new heuristic. A statistics column is never evidence either way. |
| **Structure** | Every column header verbatim, grouped as quantitative / categorical / numeric / text. Sample columns, with the role each appears to have (IP, control, input) **as its header states it**, with no inference beyond the header. The control. Replicates per group. |
| **Full or hits-only** | Row count. Whether rows not passing the table's own significance criterion are present: report counts by bin if a statistics column exists, otherwise say "no statistics column". |
| **Missingness** | NaN, empty and zero counts across the quantitative block, in total and per sample column. |
| **Imputation signs** | Whether the quantitative block has any missing values. Per sample column, the intensity deciles (aggregate). Any Perseus imputation marker (type row, categorical column). Report what is there, not a verdict. |
| **PXD018299 only** | For each BJC supplementary table: type-prefix stamp present or not, row count, sample headers. Whether any of them is a Perseus counterpart of `ISG15_interactome.xlsx`, judged by matching sample headers and **not by rows**. |

Write the measurement script as `walk/survey_ip_tables.py`. It must reproduce every number in the
report from the files in `scratch/survey-23/`.

## 4. Predictions (registered here, before the survey)

These come from the reviewer, from records and memory, not from data:

| | Prediction |
|---|---|
| P1 | PXD055843 S3 is a Perseus export with about 4,400 rows (the curation record or prior notes), so it is a **full** table rather than hits-only. If it has a statistics column, rows outside significance are present. |
| P2 | Every PXD018299 BJC supplementary table is hits-only with no per-row statistics (handoff l.91–92). |
| P3 | No prediction for `ISG15_interactome.xlsx` type, structure or imputation. |
| P4 | No prediction for imputation signs in S3. |

The report states, for P1 and P2, held, failed or not measurable, citing the line in the findings
file.

## 5. Home and commit

- **Home:** findings go to `walk/SURVEY-public-IP-tables.md`, dated with the run date. That file is
  their single home: no restating them in FINDINGS.md or the handoff.
- **Commit:** one commit containing `walk/survey_ip_tables.py` and the findings file. Nothing in
  `scratch/` and nothing else.
- **Message:** `SURVEY: public IP tables (PXD018299 interactome + BJC, PXD055843 S3); measurement only`

## 6. Report, then stop

- The commit hash.
- Every SHA-256.
- For each table, the six fields in one short block.
- The P1/P2 verdicts.
- Anything skipped under the blindness rule.
- Anything unreachable.

Then stop. Do not start the design step, an ADR, or the pre-registration.

## Out of scope

- ONTOLOGY.md, ADRs, and anything under `bzk/`. That includes the option B design and G1–G3.
- The walk line: `b960c9a`, its correction, and `notes/prompts/22-walk-two-route-independence.md`.
- The PXD055843 S1_TP imputation question (§1 of the handoff, still blocked). Report S3's imputation
  signs, but **do not resolve or comment on S1_TP**.
- Per-protein anything (§1 above).
- The halving and the two unseparated Perseus mechanisms (handoff §3, §8).
