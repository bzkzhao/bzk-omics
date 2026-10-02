# Prompt 24 — Fix the statistics binning in `walk/survey_ip_tables.py`

**Repository:** `main` at the commit adding this prompt, directly on top of `8cfb5d6`.
**Governing:** prompt 23 §3 (the "Full or hits-only" row) and `walk/SURVEY-public-IP-tables.md`.

This is an **instrument fix only**. No new measurement and no change under `bzk/`. The four public
files are rerun only to show that the output does not change. The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. Run `git log --oneline -2` and `git status --short`. HEAD must be this prompt's commit, with
   `8cfb5d6` beneath it, and the working tree must be clean. If either fails, stop.
2. Quote `walk/survey_ip_tables.py` l.56–58 (the `STATISTIC` pattern) and l.238–255 (the loop
   that bins statistics columns), verbatim.
3. Quote the "Statistics columns" line for each of the four tables in
   `walk/SURVEY-public-IP-tables.md` §6, with its line number. The expected answer is `none` for
   all four.
4. Is `scratch/survey-23/` present, and does each file's SHA-256 match §1 of the findings file?
   If not, say which files you would refetch, and from where (the same sources as in findings §1).

**Do not start §1 until bzk replies.**

---

## 1. The defect (reviewer audit of `8cfb5d6`)

`STATISTIC` matches `p-value`, `difference` and `test statistic` anywhere in a header. The loop
then bins every matching numeric column as if it held raw p-values (`<0.01`, `<0.05`, `>=0.05`).

| Perseus header | Values | Current bins |
|---|---|---|
| `-Log Student's T-test p-value …` | −log10 p, so a significant value is ≥ 1.3 | nearly all land in `>=0.05` |
| `Student's T-test Difference …` | log2 differences, negative or positive | binned as p |
| `Student's T-test Test statistic …` | t, any sign | binned as p |

No surveyed table had a statistics column, so `8cfb5d6`'s output is unaffected. PXD055843 S3 is a
Perseus export, and its P1 verdict (full or hits-only) depends on this code path.

## 2. The fix

Move the per-column statistics handling into one function,
`describe_statistic(header: str, cells: list[Any]) -> str`, which returns the report line. Classify
by the header after `strip_prefix`, checked in this order:

| # | Header | Report |
|---|---|---|
| 1 | contains `significant` | `+` / blank counts, as now |
| 2 | contains `-log` and `p-value` | convert x → p = 10^(−x), then bin as in row 3. Values < 0 are invalid for −log10 p: count them separately and leave them out of the bins |
| 3 | contains `p-value` or `q-value` (not `-log`) | bin `<0.01`, `<0.05`, `>=0.05` as now. Values outside [0, 1] are invalid for p or q: count them separately and leave them out of the bins |
| 4 | contains `difference` | counts only, by sign: `>0`, `<0`, `=0`. No magnitudes |
| 5 | contains `test statistic` | counts only, by sign, as in row 4 |
| 6 | anything else matching `STATISTIC` | the numeric count only, with the label `unclassified statistic` |

Every line also gives the numeric count out of all rows, as now. Leave `STATISTIC` itself unchanged
unless the receipt shows a header it would miss; if you change it, say why.

**Blindness (prompt 23 §1) still applies.** Only counts and bins are printed. Never values, never
row identities.

## 3. Test

Add `tests/test_survey_ip_tables.py`. Load the script with `importlib`, because `walk/` is not a
package. Test `describe_statistic` on synthetic columns:

- `-Log … p-value` with values {0.5, 2.0, 3.0, −0.1} → bins `<0.01`: 1, `<0.05`: 1, `>=0.05`: 1;
  invalid: 1
- `… p-value` with {0.001, 0.03, 0.2, 1.5} → `<0.01`: 1, `<0.05`: 1, `>=0.05`: 1; out of [0, 1]: 1
- `… Difference …` with {1.2, −0.4, 0.0} → `>0` 1, `<0` 1, `=0` 1
- `… Significant …` with {"+", "", "+"} → `+` 2, blank 1
- a header matching `STATISTIC` but none of rows 1–5 → `unclassified statistic`

Each assertion must check computed output against literal expected values, so that
`tests/test_tautology_sweep.py` passes.

## 4. Rerun and compare

Run the fixed script on the four files, refetched if needed, with the SHA-256 checked against
findings §1. The output must be **byte-identical** to findings §6's verbatim block. Show the diff
command and its result.

If it differs, stop and report the difference. Don't edit the findings file to match.

## 5. Record, commit, report

- **Findings file:** add one dated line to `walk/SURVEY-public-IP-tables.md` §5:
  `Instrument fix (prompt 24, <date>): statistics binning now handles −log p and difference
  columns; rerun on the four files byte-identical.` Change nothing else in the file.
- **Commit:** one commit containing the script, the test and that line, with the message
  `SURVEY: fix statistics binning for -log p / difference columns (prompt 24); rerun identical`.
  Fast-forward `main`, as in prompt 23.
- **Checks:** run the full `pytest`, `ruff check bzk tests walk/survey_ip_tables.py`,
  `ruff format --check` on the same paths, and `mypy bzk tests`.
- **Report:**
  - the commit hash;
  - the receipt answers already given;
  - the diff result;
  - the check results;
  - the new function's line range.

Then stop.

## Out of scope

- Running anything on PXD055843 S3. bzk runs it locally afterwards.
- The `protein_groups.py:117` label mismatch, and `scratch/` in `.gitignore`.
- The design step, ADRs, ONTOLOGY.md, and the concordance pre-registration.
- The walk line (`b960c9a`) and prompt 22.
