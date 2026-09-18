# PROMPT — verify the zero-handling correction in the imputation ADR draft

Working copy: /Users/bzk/bzk-omics
Draft at: notes/ADR-0033-imputation-state.md
Transported unchanged at fda3cb9; sha256
874581063a7ce4b5fa9732d9e28e100c99ff0b435771f2665fc1abf4b83bb940

Prior verification of these same checks exists at e2ce7d6 on branch
claude/eloquent-mendel-1ju7eh, in notes/adr-0033-zero-handling-verification.md.
Re-derive rather than inherit — but read it afterwards and reconcile, because it
carries a four-way confirmation this prompt asks for only once.

This turn VERIFIES and CORRECTS a paragraph. It lands NOTHING in decisions/:
the draft has three open items and is not ready.

## Receipt checks

R0. `git log -1 --format='%h %ci %s'`, `git status --porcelain`, and
    `shasum -a 256 notes/ADR-0033-imputation-state.md`. The hash must match.
    If HEAD is not 019c711, report what moved in bzk/adapters/, bzk/curation/
    and ONTOLOGY.md, and run every check against the CURRENT tree.

R1. bzk/adapters/maxquant.py — quote `cell_value`'s docstring sentence
    beginning "A reported" to its terminator.

R2. The same docstring: which adapter's first draft folded `0` to `None`?
    Quote it. The draft asserts the PROTEIN adapter, and that `cell_value` was
    written in maxquant_sites.py and moved on 2026-08-10.

R3. bzk/curation/loader.py — quote the comment on filters_applied's absence and
    give the value assigned to that key.

R4. ONTOLOGY.md section 3 identity table — is `filters_applied` in the Analysis
    row's IDENTIFYING or EXCLUDED cell? Quote the cell.

R5. ONTOLOGY.md section 5 DDL — quote the `filters_applied` line with its
    comment. Is there a closed enum for its values anywhere in ONTOLOGY.md?

R6. What values does `filters_applied` actually take in committed code and
    records? Search bzk/ and data/curation/. Report every distinct value.

## Registered expectations

E1. R1 says a reported 0 stays 0, names the statistics layer, cites I19.
E2. R2 names the protein adapter; cell_value written in maxquant_sites.py,
    moved 2026-08-10.
E3. R3's comment says a null would be refused; the assigned value is [].
E4. filters_applied is IDENTIFYING.
E5. No closed enum exists for its values.
E6. Live values include parameterised tokens — expect something of the form
    `localization_prob>=0.75` and `only_identified_by_site` alongside bare
    names like `reverse`.

E6 is new and bears on the draft's open question. A field already carrying a
parameterised token can express `zero_as_missing`. It does NOT settle whether a
reinterpretation belongs in a field whose every observed value is a row
REMOVAL — and the draft records that as open. Do not close it.

## Task

1. Run R0-R6 and E1-E6. Report both.
2. Where a check disagrees with the draft's zero-handling section, edit the
   draft and name the check that forced it.
3. If E6 holds, add the measured values to the draft's supporting list — as
   evidence that a named filter is expressible, NOT as a resolution of the
   one-entry-or-two question.
4. Read notes/adr-0033-zero-handling-verification.md from
   claude/eloquent-mendel-1ju7eh and reconcile it with what you measured.
   Report any disagreement. If it holds, cherry-pick or re-commit it onto main
   so the confirmation is not stranded on a branch.
5. Commit the corrected draft in place at notes/. Message:
      notes(adr): correct zero-handling home in the imputation ADR draft
   Body names the two corrections — the reversal (adapter reader ->
   Analysis.filters_applied) and the misattribution (protein adapter, not
   maxquant_sites.py) — and states the draft remains unverified as a whole.
6. Do NOT write into decisions/. Do not renumber. Do not run the test suite.

## Out of scope — carried so they do not re-enter

1. Landing this ADR. Three items are open: section 6.5's restatement of I15
   clause (b), schema.ABSENCE's matching entries, and whether a determined
   absence may name a parent field.
2. Numbering. The selection ADR takes the next free number by landing first;
   this draft is renumbered when it lands, not now.
3. Deciding one filters_applied entry or two. Recorded open; it stays open.
4. Amending ONTOLOGY.md, schema.py, any adapter, or any invariant.
5. The lysate question, the selection ADR, any curation record.
6. The standing defect list: the tautology sweep's stale floor; `resolve` not
   caching errors; `resolve` splitting accessions on a hyphen; `Resolution`
   collapsing deleted and gene-less active entries; the snapshot cache storing
   no synonyms; `Reverse` / `Potential contaminant` absent from
   `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date;
   `SUPP_DATA_3`'s label; `distinct_gene_multi`.

## Report

- R0's output, the hash comparison, and what moved if anything.
- Each receipt check with its quoted answer.
- Each expectation, measured, held or not.
- The reconciliation with e2ce7d6, and where it now lives.
- Every edit made, with the check that forced it.
- The commit SHA.
- Anything the draft asserts that you could not verify either way.

End at the report.
