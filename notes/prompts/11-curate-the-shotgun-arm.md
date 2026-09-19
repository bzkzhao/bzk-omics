# PROMPT 11 — land the curation record for PXD026748's shotgun arm

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. That must be a
fast-forward of `e3d886a` whose only additions are these four files, which bzk
committed from the reviewer's copies:

- `notes/scripts/inspect_shotgun.py`
- `notes/scripts/check_intensity.py`
- `notes/scripts/coverage_shotgun.py`
- `notes/staging/curation_PXD026748_shotgun.json`

Verify with `git diff --stat e3d886a..origin/main`. If anything else changed,
report it and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`.

**Never force-push, and never amend or rebase a pushed commit. Do not write,
retype or commit any file under `notes/prompts/`.** This container has no raw
store, and no check in this turn needs one. The shotgun file is not ingested
here; that is turn 12, on bzk's machine.


## What this turn does

It lands the second curation record for `PXD026748`. The record covers the
shotgun (total-proteome) arm, whose `proteinGroups.txt` is the unenriched input
to the GG enrichment. The reviewer wrote the record and validated it with the
loader, and bzk staged it byte for byte. **You move it into place. You do not
edit it.** Its content is a curation judgement, and the review loop owns it. If
you believe any field is wrong, report it with your reason and stop before
committing.


## Receipt checks

R1. **Base.** Show `git diff --stat e3d886a..origin/main`, and state that it
    lists exactly the four files above.

R2. **The staged record's identity.** Compute the sha256 of
    `notes/staging/curation_PXD026748_shotgun.json`. The reviewer's copy is:

    `fd20cc7efebc6edc4001a604a2d8ff43d597a6b11257f5c6aea9f2d3b090031f`

    If it differs, report it and STOP.

R3. **Why its Samples are new.** Quote `bzk/ontology/schema.py:243–258`, the
    `Experiment` and `Sample` identities. Then:
    - Load both `PXD026748` records with `bzk.curation.loader.load_path`.
    - Report, for each of `Project`, `Experiment`, `Dataset`, `Analysis` and
      `Sample`, how many ids each record produces and how many the two share.
    - The reviewer measured one shared `Project` and zero of everything else.
    - State which identity field makes the Samples distinct. The two records'
      Sample *fields* are identical by design.

R4. **The counterfactual.** Load the staged record with its `experiment` block
    replaced, in memory only, by the GG record's `experiment` block. Report how
    many Sample ids it now shares with the GG record. The reviewer measured 12
    of 12. This is the silent merge the new test guards against.

R5. **The quantity.** Run `quantity_from_mapping_keys` on the staged record's
    sample mapping, and report the result. The expected value is `lfq`.

R6. **The pin.** Quote `tests/test_curation_loader.py:488–499`. Re-measure the
    docstring's key-set claim with the new record present: which files share a
    key set, and how many share it.


## Changes

**C1 — Move the record into place, byte-identical.**

```
git mv notes/staging/curation_PXD026748_shotgun.json data/curation/curation_PXD026748_shotgun.json
```

Re-compute its sha256 after the move. It must still equal R2's value.
`notes/staging/` should then be empty; do not commit an empty directory.

**C2 — Move the pin from 5 to 6.** Update the assertion message and the
docstring at `tests/test_curation_loader.py:488–499` to match what R6 measured.
The guard must be seen to fail before it moves: report its failure message with
the new record present and the pin still at 5.

**C3 — Tests, in a new module `tests/test_curation_pxd026748_arms.py`.** Each
test must be seen to fail before it passes. Report each mutation and its
failure message.

T1. **The arms share a Project and nothing else.** Assert:
    - exactly one shared `Project` id;
    - disjoint `Experiment`, `Dataset`, `Analysis` and `Sample` ids;
    - twelve Samples in each record.

    Mutation: in a temporary copy of the shotgun record, replace its
    `experiment` block with the GG record's. The Sample-disjointness assertion
    must fail and name the shared ids or their count.
T2. **Same biology, different Experiment.** For each Sample of the shotgun
    record, some GG Sample has equal values for every field in
    `schema.py`'s `Sample` identity. This pins that the distinctness comes from
    the Experiment anchor alone, as the record's rationale says.

    Mutation: change one shotgun sample's `treatment` string in a temporary
    copy.
T3. **The derived quantity is `lfq`.**

    Mutation: rename one mapping key's prefix to `Intensity ` in a temporary
    copy. The derivation must raise and name both families.

Use `tmp_path` for every mutated copy, and never edit the committed record.

**C4 — Point the adapter's docstring at the record.** At
`bzk/adapters/maxquant_protein_groups.py:27` and `:409`, the "three families of
twelve columns" figure is restated about a file the repository did not hold
until now. Replace each restatement with a pointer to
`data/curation/curation_PXD026748_shotgun.json`, whose rationale item (4) is
now that figure's dated home. Change nothing else in the module.


## Registered expectations

E1. Suite = 714 passed, 14 skipped at base, then 714 + the new tests. The pin
    move changes no count. Report the split.
E2. `test_rebuilt_ids_match_the_committed_pin` passes unmodified: it is scoped
    to `PXD018299`.
    `test_every_record_in_the_export_reaches_the_graph` passes with the new
    record included. Its deposit is absent here, so the replay loads the
    record's nodes and skips the ingest.
E3. No test other than C2's pin needs changing. If one does, name it and say
    why.


## Task

1. Run R1–R6. Stop conditions: R1 shows other changes, or R2's hash differs.
2. Make C1–C4.
3. Run E1–E3 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit C1–C3 as one commit (`curation:` prefix). Commit C4 alone
   (`adapters:` prefix). Push, fast-forward only.
5. Write `notes/reports/11-curate-the-shotgun-arm-report.md` and commit it
   alone. Push.


## Out of scope

- Any ingest.
- Placing `proteinGroups.txt` in the raw store.
- Any edit to either curation record's content.
- The published cascade, and the fixture for turn 09's ingest figures.
- ADR-0035's review.
- The six superseded homes of `67,158`.
- The site branch's constant `quantity`.
- The unenumerated-mirrors class.
- `notes/prompts/`.


## Report

- R1–R6 answered, with figures.
- C1's hash after the move.
- C2's pre-move failure message.
- T1–T3, each with its mutation and failure message.
- C4's two replacements, quoted.
- E1–E3, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating that every push was a fast-forward.
