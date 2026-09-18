# PROMPT — correct the imputation ADR's premise, then land it as Proposed

Working copy: /Users/bzk/bzk-omics
Draft at: notes/ADR-0033-imputation-state.md (corrected in place at 59d9433)

The draft's central decision is WRONG, and not in a small way. It proposes
adding four rows to section 3's absence table and amending schema.ABSENCE in
step. Both already exist. The draft proposes work the repository completed
before the draft was written.

Verify that before correcting anything. If the rows do NOT exist, this prompt's
premise is wrong and you should stop and report.

## Receipt checks

R0. `git log -1 --format='%h %ci %s'` and `git status --porcelain`.
    Report whether HEAD has been pushed: `git status -sb` and
    `git log --oneline origin/main..HEAD`.

R1. bzk/ontology/schema.py — quote the ABSENCE dict's entries whose first
    element is "Imputation". How many, and what value does each carry?

R2. ONTOLOGY.md section 3 absence table — quote every row whose Node cell is
    `Imputation`. Give the Field, the Kind and the DETERMINER cell verbatim.

R3. tests/test_schema.py — what exactly does the ABSENCE guard compare? Does it
    check the determiner text, or only the (node, field) -> kind mapping?
    Quote the assertion.

R4. Where is the I15 clause-(b) rationale — that a seed is mandatory for
    stochastic methods because the analysis is otherwise irreproducible —
    restated? Search ONTOLOGY.md for every occurrence. Report each with its
    line and the sentence. The reviewer found three candidate homes: the
    "Configuration belongs in identity" paragraph, section 6.5, and I15 itself.
    Confirm or correct that count.

R5. ls decisions/ — the next free number N. The draft is filed as 0033, which
    is now TAKEN by the frame record. Renumber to N in the filename, the title
    line and any self-reference.

## Registered expectations

E1. ABSENCE carries exactly four Imputation entries — downshift_sd, width_sd,
    seed, scope — each "determined".
E2. Section 3's table carries the same four rows, each with determiner
    `method`.
E3. The guard compares (node, field) -> kind only, NOT the determiner prose. So
    amending a determiner needs no code change and breaks no test.
E4. The I15 rationale has three homes in ONTOLOGY.md, not two.

E3 matters most: if the guard DOES check determiner text, the amendment is a
code change too and the draft's "amend schema.ABSENCE simultaneously" is right
after all for a different reason. Report either way.

## What the record should decide, once the premise is corrected

The reviewer's reading, to be checked rather than adopted:

The four rows exist and their Kind is right. What is wrong is the DETERMINER.
Each currently reads `method`. For an external analysis whose method IS stated -
imputation from a normal distribution around the detection limit - `method`
determines those fields to be NON-NULL. They are null anyway, because the
publication never stated them. That null is contingent on what a paper happened
to record, and ADR-0021 calls a contingent null on an identifying field "a
defect to redesign rather than a state to declare."

So the amendment is to the determiner: `method` AND
`Analysis.parameters_observed` together. Where parameters_observed is FALSE, the
nulls are fixed by that recorded fact - the analysis was not observed, so its
parameters are not recoverable from it - which is outside the moment of ingest
and satisfies ADR-0021.

This also DECIDES the draft's third open item rather than leaving it open:
whether a determined absence may name a PARENT field. It may, and this is the
instance. Record the reasoning, not just the verdict.

## Task

1. Run R0-R5 and E1-E4. Report both before editing.
2. Rewrite the draft's Decision section against what you measured. The premise
   correction is the point of this turn: the record must say the rows exist and
   that the act is amending a determiner, not adding rows.
3. State the ONTOLOGY.md edits as IMPLIED CHANGES DESCRIBED AND NOT MADE,
   following ADR-0031's own section of that name. Do not edit ONTOLOGY.md in
   this turn. List every home R4 found - the single-source rule binds the
   amendment, so all homes move together or none does.
4. If E3 holds, say plainly in the record that no code change is required, and
   strike the draft's claim that schema.ABSENCE must be amended in step.
5. Renumber to N per R5. Write to decisions/NNNN-<slug>.md.
6. Delete notes/ADR-0033-imputation-state.md once landed.
7. Status row reads Proposed, plain, not bolded - tests/test_decision_index.py
   parses it. No Reviewed row: the round-trip has not happened.
8. Update decisions/README.md's Written table and the pinned counts in
   tests/test_decision_index.py. Run that one test file. Do not run the suite.
9. Commit. Message: `decisions: add ADR-NNNN, declaring an unrecorded
   imputation`. Body names the premise correction, the determiner amendment,
   the parent-field decision, and every implied change left unmade.

## Out of scope

1. Editing ONTOLOGY.md, schema.py, any adapter or any invariant. Described, not
   made.
2. The zero-handling section. Verified and corrected at 59d9433; leave it.
3. Deciding one filters_applied entry or two. Open; it stays open.
4. The lysate question, any curation record, any adapter work.
5. Ingesting anything.
6. ADR-0033 (the frame record). Cited if useful, not edited.
7. The standing defect list: the tautology sweep's stale floor; `resolve` not
   caching errors; `resolve` splitting accessions on a hyphen; `Resolution`
   collapsing deleted and gene-less active entries; the snapshot cache storing
   no synonyms; `Reverse` / `Potential contaminant` absent from
   `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date;
   `SUPP_DATA_3`'s label; `distinct_gene_multi`.

## Report

- R0's output, including whether HEAD is pushed and what is unpushed.
- Each receipt check with its quoted answer.
- Each expectation, measured, held or not.
- The number used.
- What the Decision section now says, and what it said before.
- Every implied change listed, and confirmation none was made.
- The test result and the commit SHA.
- Anything you could not verify either way.

Write this report to notes/reports/03-imputation-adr-report.md as well as to
stdout, so it survives the terminal.

End at the report.
