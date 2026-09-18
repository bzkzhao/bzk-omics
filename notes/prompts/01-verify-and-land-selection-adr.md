# PROMPT — verify the selection ADR, renumber it, land it as Proposed

Working copy: /Users/bzk/bzk-omics
Draft at: notes/ADR-0034-frame-is-a-query-set-repair.md
Transported unchanged at fda3cb9; sha256
7724d142546463cd70959ab635f63fb3e0abb7f994f000ab5188b75a755e0ecb

The draft is a reviewer's text. It asserts facts about this repository that it
did not derive here, and it was read at a commit that may no longer be HEAD.
Re-derive every one against the CURRENT tree, correct the draft where a check
disagrees, and land it.

WHERE A CHECK DISAGREES WITH THE DRAFT, THE CHECK IS RIGHT AND THE DRAFT IS
EDITED.

## Receipt checks — from the named sources only

R0. `git log -1 --format='%h %ci %s'`, `git status --porcelain`, and
    `shasum -a 256 notes/ADR-0034-frame-is-a-query-set-repair.md`.

    The hash must match the one above. If it does not, the draft changed after
    transport — STOP and report.

    The draft's quotations are pinned to 019c711. If HEAD differs, run
      git log --oneline 019c711..HEAD -- ROADMAP.md ONTOLOGY.md decisions/
    and report what moved. A divergence is not a blocker and is not to be
    absorbed silently: report it, run every check against the CURRENT tree, and
    where a quotation no longer matches the file, the file is right, the draft
    is corrected, and the draft's pinned commit is updated to the one you read
    at.

R1. ROADMAP.md's C0 table: quote gate (d)'s Why cell to its terminator. Does it
    contain "for this survey only"?

R2. decisions/README.md: quote the sentence stating what status an ADR lands at
    and what completes the round-trip.

R3. ls decisions/ — report the highest-numbered record and the next free number
    N.

    The draft is titled and filed as 0034. That was a reservation against a
    second ADR (imputation) that has NOT landed and is not ready. Numbers go to
    records in landing order, so unless N is 0034, RENUMBER this record to N —
    filename, title line, and any self-reference. Report the number used.

    Do not leave a gap: a record filed at 0034 with nothing at 0033 leaves an
    empty number in an immutable series.

R4. ROADMAP.md: quote the sentence describing what the draw pool was built from
    — the one naming what a diGly deposit is titled — plus its paragraph's
    first sentence for context.

Do not proceed past a receipt check you cannot answer from the source.

## Registered expectations

E1. `grep -rn "PXD026748" --include=*.md --include=*.json --include=*.py .`
    returns hits ONLY in notes/ (the transported drafts). Zero elsewhere.

    If HEAD moved past 019c711, state whether any commit in that range
    introduced a mention outside notes/. A clean grep at an older commit is not
    evidence about the current one.

E2. PXD065158 is row 10 of ROADMAP.md's sixty-row table, with `fragpipe` in the
    Engine column and `abe` in the C0 gates met column.

E3. "what limited that draw was its query set, not its gate" appears in
    ROADMAP.md, in words close to that.

E4. C0 has six gate rows, a-f, and f carries "Added 2026-08-18".

E5. ADR-0031's R3 class, as re-decided by its Review finding A, is "any deposit
    of the anchor laboratory not yet used".

E1 is load-bearing: the draft's whole route depends on C0 never having screened
that deposit. If E1 returns hits outside notes/, STOP and report — do not land.

## Task

1. Run the receipt checks and expectations. Report both before editing.
2. Edit the draft where a check disagrees. Name the check that forced each edit.
3. Write it to decisions/NNNN-frame-is-a-query-set-repair.md with the number
   from R3.
4. Delete notes/ADR-0034-frame-is-a-query-set-repair.md. The draft must not
   exist in two places once it has landed.
5. Confirm the status row reads Proposed and NO `Reviewed` row is present. The
   round-trip has not happened and asserting one is the failure this directory
   refuses everywhere.
6. Commit. Message: `decisions: add ADR-NNNN, the frame as a query-set repair`.
   Body names the renumbering and every edit forced by a check.
7. Do not run the test suite; an ADR is prose and nothing mechanical validates
   it.

## Out of scope — carried so they do not re-enter

1. Screening any deposit against C0. This record decides a route, not an
   instance; the expectation table inside it is labelled a prediction and stays
   one.
2. Selecting a deposit. No C1 scoring, no C2 ranking.
3. Amending C0, C1, C2, C3 or C4, in any direction.
4. ADR-0031 — cited, not superseded, not edited.
5. notes/ADR-0033-imputation-state.md. Left in place, untouched, for the next
   turn.
6. The lysate question, any curation record, any adapter work.
7. WALK-STANDARD, FRAME-SPEC and the walk records. They live outside this repo
   and moving them is a separate decision.
8. The standing defect list: the tautology sweep's stale floor; `resolve` not
   caching errors; `resolve` splitting accessions on a hyphen; `Resolution`
   collapsing deleted and gene-less active entries; the snapshot cache storing
   no synonyms; `Reverse` / `Potential contaminant` absent from
   `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date;
   `SUPP_DATA_3`'s label; `distinct_gene_multi`.

## Report

- R0's output, the hash comparison, and what moved if anything did.
- Each receipt check with its quoted answer.
- Each expectation, measured, held or not.
- The number used and why.
- Every edit made, with the check that forced it.
- The path written, the status row as written, the commit SHA.
- Anything the draft asserts that you could not verify either way.

End at the report.
