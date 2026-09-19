# PROMPT 10b — close four gaps the audit of turn 10 found

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.
Base: `554a37d`. Verify HEAD before anything else; if it differs, report the
commits between and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`.

This is a correction turn. It adds no capability.

**Do not write, retype or commit any file under `notes/prompts/`.** The
committed `10-wire-the-adapter-dispatch.md` has the same words as the prompt
that was issued, but its headings, emphasis and wrapping were lost and the R4
code fences are mis-nested. The issued files are committed by bzk from his own
copy, not re-typed here.


## Where turn 10 closed

bzk ran R5 and E3 on his machine against `554a37d`. Every figure held:

- **R5:** 0 `#!{` lines in both real site tables.
- **E3:**
  - `PXD018299`: 2,029 sites and 27 refused.
  - `PXD026748`: 2,166 sites, 21 refused (all `residue_mismatch`, on nine
    proteins) and 51,984 cells.
  - `PXD055843`: skipped with "no adapter recognises
    Supplementary_Data_S1_TP.xlsx".
  - Totals: 4,195 sites, 48 refusals, 100,680 cells.

The same run shows gap C2 below live. The replay summary printed `0 protein
observation(s)`, but the `done:` line and the `RebuildReport` repr carry no
protein count.


## Receipt checks

R1. `bzk/rebuild.py:444–454`. Quote it. Which `ReplayReport` field is not
    carried into `RebuildReport`?

R2. `bzk/rebuild.py:433–436`, `:354–357` and `:362`. Quote all three. Which of
    them names a grain, and which grain?

R3. `tests/test_adapter_dispatch.py`: `_every_txt_fixture`, and the
    parametrised disjointness test that uses it. Quote both. What container
    format does the parametrisation never include? Then quote
    `bzk/adapters/perseus.py:408–413` and say which branch of the Perseus sniff
    that format reaches.

R4. `bzk/adapters/maxquant_sites.py`, the paragraph around `:260`. Quote the
    sentence containing "struck rather than deleted". Was the original sentence
    struck with `~~`, or removed and quoted?


## Changes

**C1 — Pin disjointness for the workbook container.** Add tests that build
workbooks in `tmp_path` with `openpyxl`, following `tests/test_perseus.py:112`'s
`_sheet`. Commit no workbook fixture.

- **A Perseus-stamped workbook.** Assert first that `PerseusAdapter.sniff`
  returns `True` on it, so the case is not vacuous. Then assert that
  `_claims(...) == ["perseus"]`.
- **A plain workbook with no stamp**, whose header carries `Protein IDs`, `id`
  and one `LFQ intensity` column. Assert that no adapter claims it.

This covers the only committed record whose deposit is a workbook,
`PXD055843`.

**C2 — `RebuildReport` carries `protein_observations`.** It is populated from
the replay, and the `done:` line names it beside `site_observations`, in the
same wording the replay summary already uses. `main`'s exit status is
unchanged.

**C3 — The two skip messages stop saying "sites".** A skipped deposit has not
had its grain determined, so the message names no grain:
- at `:356`, "sites not ingested" becomes "not ingested";
- at `:362`, likewise.

Search the tests for any that match either string, and update them in the same
commit. Name each one.

**C4 — Correct the "struck" wording in the site sniff's docstring.** Say what
was done: the sentence was removed and is quoted in full in the paragraph.
Change nothing else in that docstring.


## Tests — each seen to fail before it passes

For each test, report the mutation and the failing assertion's message.

- **For C1:** remove the workbook branch of `PerseusAdapter.sniff` in a copy.
  The stamped-workbook test must fail at its non-vacuity assertion, not later.
- **For C2:** a rebuild over a synthetic protein-groups record, in `tmp_path`
  with an explicit `home`, reports
  `RebuildReport.protein_observations == ReplayReport.protein_observations`.
  Check both sides against the adapter, as `tests/test_adapter_dispatch.py`'s
  T5 does, not against a literal on both sides.

C3 and C4 change strings only. If a test pins either string, report it.
Otherwise report that none does.


## Registered expectations

E1. Suite = 704 passed + the new tests, 14 skipped, on a container with no raw
    store. Report the split.
E2. `test_rebuilt_ids_match_the_committed_pin` passes unmodified.
E3. Handed to bzk; not run here. A re-run of turn 10's E3 command prints the
    same figures, plus `0 protein observation(s)` on the `done:` line and
    `protein_observations=0` in the repr.


## Task

1. Run R1–R4.
2. Make C1–C4 and write the tests.
3. Run E1 and E2, plus every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit code and tests as one commit (`rebuild:` prefix). Push.
5. Write `notes/reports/10b-close-the-dispatch-gaps-report.md` and commit it
   alone. No prompt file. Push.


## Out of scope

- Everything turn 10's out-of-scope list named.
- The site branch's constant `quantity`, which stays an open defect.
- The drift line's "different set (3,013 then, 3,579 now)".
- `adapter.name` reading `maxquant` for the site adapter.
- Any change to `notes/prompts/`.


## Report

- R1–R4 quoted and answered.
- C1–C4, each with the file and lines changed.
- Each test's mutation and failure message.
- E1 and E2, each held or missed, with figures. E3 recorded as handed to bzk.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range.
