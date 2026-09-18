# PROMPT — commit the frame and walk artefacts, then push

Working copy: /Users/bzk/bzk-omics

ADR-0033 is Accepted and cites FRAME-SPEC v1 and FRAME v1 as its evidence base.
Neither is in the repository. Its own review recorded that it could not verify
Frame B's eleven members, their species or their search engines, because those
artefacts live outside. An Accepted record resting on evidence a reader cannot
reach is the defect this turn closes.

Files have been copied in by hand before this prompt runs. Confirm they are
there before doing anything else.


## Receipt checks

R0. `git log -1 --format='%h %ci %s'`, `git status --porcelain`, and the push
    state: `git log --oneline origin/main..HEAD`.

R1. Quote .gitignore's opening comment — the paragraph stating why deposits are
    not committed and why curation records are. What is the TEST it states?

R2. `git ls-files data/` — what is tracked under data/ today, and what is the
    naming convention of those files?

R3. List every untracked path: `git status --porcelain --untracked-files=all`.
    Report every file, not just the directories.

R4. Does the repository have a top-level directory for instruments or standards
    that are neither code, decisions, nor curation records? Report what exists
    at top level.


## Registered expectations

E1. .gitignore's stated test is RECOVERABILITY, not size: things fetchable from
    PRIDE are excluded because committing them adds weight without adding
    recoverability; curation records are committed because they cannot be
    regenerated.
E2. data/ contains only data/curation/, with five tracked files.

E1 is the one that decides this turn. Report the exact wording.


## The argument to check, not to accept

The reviewer earlier called data/frame/frame_raw.tsv "closer to a cache than a
record" on the ground that it is re-derivable by re-running the PRIDE query.
**That was wrong, and the correction is the reason this turn exists.**

Re-running the query in six months returns a DIFFERENT answer, because PRIDE's
index grows. frame_raw.tsv is therefore a DATED OBSERVATION, not a cache: it
records what the repository looked like on 2026-09-17 and nothing regenerates
that. Under .gitignore's own test it is on the curation-record side of the line,
not the deposit side.

Check that reasoning against R1's wording before acting on it. If .gitignore's
test is something other than recoverability, say so and stop.


## Task

1. Run R0-R4 and E1-E2. Report both.
2. Stage and commit the frame evidence under data/frame/: frame_raw.tsv,
   FRAME-SPEC.md, FRAME-v1.md. These are the evidence base for an Accepted
   record.
3. Stage and commit the walk artefacts. WHERE THEY GO IS A STRUCTURAL CHOICE
   AND YOU SHOULD MAKE IT EXPLICIT RATHER THAN QUIETLY:
   - the reviewer's proposal is a top-level walk/ directory, on the ground that
     WALK-STANDARD is a first-class instrument now cited by an Accepted ADR and
     the walk records are dated determinations;
   - the conservative alternative is notes/walk/, which adds no top-level
     directory.
   Pick one, say which and why, and put WALK-STANDARD.md, the walk_*.json
   records, STEP2-R1-SCAN.md and PREREG-PXD026748-ingest.md there together.
4. PREREG-PXD026748-ingest.md is a registered prediction whose whole value is
   being committed BEFORE the result it predicts. Say so in the commit body.
5. notes/prompts/ and notes/reports/ are untracked. Commit them too: they are
   the audit trail this project keeps, and the reports are not regenerable.
6. Do NOT commit any draft curation record for PXD026748 into data/curation/.
   It is blocked on the lysate question and committing it beside the two valid
   records would misrepresent its status. If such a file was copied in, leave it
   untracked and say so.
7. Commit in SEPARATE commits by kind — evidence, instrument and records, audit
   trail — not one mixed commit. Each body states what the files are and why
   they are committed under R1's test.
8. Push main.
9. Write the full report to notes/reports/05-land-artefacts-report.md and append
   to notes/reports/log.md if it exists. Commit the report too, or say why not.


## Out of scope

1. Screening any deposit against C0. The registered expectation stays a
   prediction.
2. Editing any artefact being committed. They land as copied; this is transport
   and tracking, not revision. If something in them looks wrong, REPORT it.
3. ADR-0033 and ADR-0034 — cited, not edited.
4. Amending C0-C4, ONTOLOGY.md, schema.py, any adapter, any invariant.
5. The lysate question, the curation record, any adapter work.
6. Running the suite. If a test breaks on a new path, report it and fix only
   that.
7. The standing defect list: the tautology sweep's stale floor; `resolve` not
   caching errors; `resolve` splitting accessions on a hyphen; `Resolution`
   collapsing deleted and gene-less active entries; the snapshot cache storing
   no synonyms; `Reverse` / `Potential contaminant` absent from
   `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date;
   `SUPP_DATA_3`'s label; `distinct_gene_multi`.


## Report

- R0 with push state, and each receipt check quoted.
- E1 and E2 measured; whether the dated-observation argument survives R1.
- Every file committed, its path, and which commit.
- The structural choice made for the walk artefacts, and why.
- Anything left untracked deliberately, and why.
- The push result and the new origin/main SHA.
- Anything you noticed in the copied files that you left alone.

End at the report.
