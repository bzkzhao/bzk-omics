# PROMPT — verify and land the lysate ADR

Working copy: /Users/bzk/bzk-omics
Draft at: notes/ADR-lysate-draft.md (copied in by hand before this prompt)

The draft decides how a perturbation applied AFTER the biological sample ends is
represented. Its central argument rests on three claims about this repository.
Re-derive each. Where a check disagrees, the check is right.


## Receipt checks

R0. `git log -1`, `git status --porcelain`, push state.

R1. ONTOLOGY.md — quote the `Sample` DDL in full. Does `replicate` carry a
    comment? Is it the ONLY field of Sample without one?

R2. `data/curation/curation_PXD018299.json` — for the anchor, do two samples
    differing only in `treatment` share a `replicate` index? Quote two mapping
    entries that settle it.

R3. ONTOLOGY.md section 3 — what does its absence table classify? Quote the
    sentence stating its scope.

R4. ls decisions/ — the next free number N.

R5. `grep -rn "aliquot\|lysate\|post-lysis\|ex vivo" ONTOLOGY.md` — confirm the
    draft's claim that it returns nothing.


## Registered expectations

E1. `replicate` has no DDL comment and is the only Sample field without one.
E2. In PXD018299, replicate index does NOT identify shared source material
    across treatments — separate wells, separate seeding.
E3. Section 3's absence table classifies absent VALUES on fields that exist, not
    absent relations.

E2 is load-bearing: it is what kills the reading that `replicate` carries the
pairing for free. If the anchor DOES pair by replicate index, the draft's R2 is
wrong and the whole record needs rethinking — STOP and report.


## Task

1. Run R0-R5 and E1-E3. Report both.
2. Correct the draft where a check disagrees; name the check.
3. Number it N, write to decisions/NNNN-<slug>.md, status Proposed, plain.
4. Delete notes/ADR-lysate-draft.md.
5. Update decisions/README.md and the pinned counts in
   tests/test_decision_index.py. Run that one test file.
6. Commit, push, write the report to
   `notes/reports/08-lysate-adr-report.md` and commit it.


## Out of scope

Adding any field to Sample. Editing ONTOLOGY.md, including `replicate`'s missing
comment — the draft names it and defers it deliberately. Ingesting anything.
Writing a curation record. ADR-0033, ADR-0034. The standing defect list as in 07.
