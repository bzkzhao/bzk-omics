# PROMPT — close the four gaps report 05 found, and record one that cannot be closed

Working copy: /Users/bzk/bzk-omics

Report 05 committed the frame and walk artefacts and found four gaps. Three are
closed by committing files. The fourth CANNOT be closed and must be recorded as
a permanent loss rather than quietly left.

Files have been copied in by hand before this prompt runs.


## The loss, stated first because it governs one of the tasks

`WALK-STANDARD.md` v1 no longer exists. The reviewer wrote v2 by OVERWRITING v1
in place rather than keeping the prior version, so v1's text is not recoverable
from anywhere — not from this repository, not from the reviewer's working
directory. Only v2 and its changelog survive.

This matters because `walk/walk_PXD026748.json` records
`"standard_version": "WALK-STANDARD v1"`. Its verdicts were judged against a
text the repository does not hold and cannot obtain. The changelog names every
change v2 made, so the delta is readable — but a reader cannot see the text the
verdicts were actually measured against.

**Do not reconstruct v1 from the changelog.** A reversed-out reconstruction is
not the original and committing it as such would be worse than the gap.


## Receipt checks

R0. `git log -1 --format='%h %ci %s'`, `git status --porcelain --untracked-files=all`,
    and the push state.

R1. `walk/WALK-STANDARD.md` — quote its version line and its changelog's v1
    entry.

R2. `walk/walk_PXD026748.json` — quote its `standard_version` field.

R3. `git ls-files walk/ data/frame/` — what is tracked in each today?

R4. `data/frame/frame.py` — confirm it is present and untracked. Report its size
    and the term set it queries, so the term set can be checked against
    `FRAME-SPEC.md`'s section 1.


## Registered expectations

E1. frame.py's term set matches FRAME-SPEC section 1's twenty-two terms exactly.
E2. WALK-STANDARD.md cites walk_PXD074990_m6.json and walk_PXD065158.json, and
    neither is tracked today.

E1 is the reason frame.py is being committed. If the term set does NOT match the
spec, that is a finding, not a formality — report the difference and commit the
script anyway, because a divergence between a pre-registration and the code that
ran is exactly what a committed script exists to expose.


## Task

1. Run R0-R4 and E1-E2. Report both.

2. **Commit `data/frame/frame.py`.** Ground: report 05's own words — a dated
   observation whose query is absent is only half-auditable, and a reader cannot
   check the term set against FRAME-SPEC section 1 without it. Same commit kind
   as the frame evidence. State E1's result in the body.

3. **Commit the four missing walk records** into `walk/`:
   `walk_PXD065158.json`, `walk_PXD074990_m6.json`, `walk_PXD071724.json`,
   `walk_M4_M5.json`, and `STEP2-R1-SCAN.md`. Ground: WALK-STANDARD cites two of
   them, and a committed standard resting on evidence a reader cannot reach is
   the defect turn 05 existed to close, recursing one level in.

4. **Record the v1 loss in `walk/WALK-STANDARD.md`'s changelog**, as a short
   entry under the v1 line. It must say: v1's text was overwritten in place when
   v2 was written and is not recoverable; v2's changelog is the only record of
   what v1 said; and `walk_PXD026748.json` was judged against v1. Do not soften
   it and do not reconstruct v1.

5. **Record the same in `walk/walk_PXD026748.json`**, as a field alongside
   `standard_version` — the standard it names is not in the repository, and a
   reader of that record should learn it there rather than by grepping.

6. Commit in separate commits by kind, as turn 05 did. Push main.

7. Write the full report to `notes/reports/06-close-artefact-gaps-report.md`
   and commit it.


## Out of scope

1. Reconstructing WALK-STANDARD v1 in any form.
2. Editing any walk record's verdicts, grains or sources. They land as copied.
   If a verdict looks wrong, REPORT it.
3. Screening any deposit against C0.
4. `curation_PXD026748.json` — still blocked on the lysate question. If copied
   in, leave it untracked and say so.
5. `notes/reports/last.md` and `run.md` — correctly excluded in turn 05 as
   regenerable from git log. Leave them.
6. ADR-0033, ADR-0034, ONTOLOGY.md, schema.py, any adapter, any invariant.
7. Running the full suite. Run only the tests that scan repository paths.
8. The standing defect list: the tautology sweep's stale floor; `resolve` not
   caching errors; `resolve` splitting accessions on a hyphen; `Resolution`
   collapsing deleted and gene-less active entries; the snapshot cache storing
   no synonyms; `Reverse` / `Potential contaminant` absent from
   `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date;
   `SUPP_DATA_3`'s label; `distinct_gene_multi`.


## Report

- R0 with push state; each receipt check quoted.
- E1 and E2 measured. If E1 failed, the exact difference between frame.py's
  term set and FRAME-SPEC section 1.
- Every file committed and in which commit.
- The wording used for the v1 loss, in both places.
- Anything you noticed in the newly copied walk records that you left alone —
  in particular any further citation to an artefact still not in the repository.
- The push result and the new origin/main SHA.

End at the report.
