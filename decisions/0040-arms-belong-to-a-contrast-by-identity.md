# ADR-0040 — Arms belong to a contrast by identity; `DeclaredContrast` enforces it

| | |
|---|---|
| Status | Proposed |
| Date | 2026-11-08 |
| Supersedes | — |
| Superseded by | — |

**It supersedes nothing.** `f61f6fd` (prompt 33) answered this question for one producer,
`site_change_set`, without a record; this one asks it, gives the same answer, and extends it to the
second producer, the Perseus adapter's `DeclaredContrast`.

## Context

A producer is handed a `Contrast` node and that contrast's arms (`ContrastArms`, ADR-0038 D1) as two
independently chosen arguments. Nothing else relates them. In `bzk/adapters/perseus.py` every result
is attributed through `declared.contrast["id"]`, and the proof is keyed by it too, while `_prove`
binds and recomputes the Difference over `declared.arms`. A mismatched pair therefore proves the
binding over one comparison's samples and attributes every result to another. `site_change_set`
refuses that pair (`bzk/analysis/differential.py`, the `arms.contrast_id != contrast_id` check);
`DeclaredContrast` did not.

Measured in prompt 40's receipt check (§0.2, 2026-11-08), confirmed at runtime by wrapping
`DeclaredContrast.__init__` across the full suite: eight construction sites under `bzk/` and
`tests/`, two of them mismatched and passing with nothing flagging them —
`test_the_count_is_per_contrast` and `test_refuses_when_a_declared_contrast_has_no_columns`. The
production site, `bzk/sources/pxd055843_perseus.py`, takes both from one `LoadedCuration` under one
handle. Every real record already agrees: five contrasts across `data/curation/curation_*.json`,
zero mismatches (§0.4).

## Decision

**Arms belong to a contrast by identity.** *Belong* means the `ContrastArms` object was minted for
this contrast, compared by the minted node's id: `arms.contrast_id == str(contrast["id"])`. It does
not mean *these samples are this contrast's arms*.

`DeclaredContrast.__post_init__` refuses a pair that fails this, raising `PerseusError` naming both
ids and pointing at `LoadedCuration.contrast_arms` under the same handle as
`LoadedCuration.contrast` — the same rule and the same wording as `site_change_set`'s refusal.

## Consequences

- **Two contrasts may still share arm samples.** Each carries arms minted for it. The two readings,
  identity and extension, diverge only where arms minted for A are handed to B with identical
  samples; identity refuses that, extension would admit it.
- **The cost, measured in the build turn** on a container with no raw store: the two mismatched
  tests were repaired by giving each contrast arms minted for it (same samples, so neither test's
  subject moved), which left the suite at 1230 passed / 14 skipped, unchanged from baseline — so no
  third test needed touching. The guard's own test takes it to 1231 / 14.
- **`contrast_id` is a claim, not a proof.** A hand-built `ContrastArms` can state any id, and the
  loader is the only production site that fills it. The check catches accidents, not intent.
- **The `dataset` gap is unchanged, by design.** Neither this check nor `site_change_set`'s relates
  `arms` or `contrast` to the `dataset` a producer is given, so a `dataset` from another record stays
  representable.

## Alternatives considered

**Extension — compare the arm samples with the contrast's own arm membership.** Rejected, on two
grounds measured in prompt 40's receipt check (§0.5), re-run over both arms in the build turn.

1. *It is not checkable at the adapter today.* ADR-0038 D4 puts membership in `NUMERATOR_SAMPLE` /
   `DENOMINATOR_SAMPLE` edges, and nothing reachable from `DeclaredContrast` carries them: the
   `Contrast` node's `numerator` / `denominator` are condition labels, not `Sample` ids; `arms`
   holds the ids but is the claim under test; `SampleMapping` carries no contrast edges. A producer
   would have to be given `LoadedCuration.edges` for that contrast, or the graph. Deriving membership
   from the labels instead would re-resolve mapping keys, which the adapter does not do.
2. *Where it could be checked, it distinguishes nothing identity does not.* The loader builds the
   D4 edges and the `ContrastArms` from the same `arms` dict in one pass
   (`bzk/curation/loader.py` l.669–672 and l.685–698, at `a65b90f`). For all five real contrasts the
   edge-derived numerator and denominator equal `arms.numerator` and `arms.denominator`, in order. So
   wherever both come from one `LoadedCuration`, extension holds exactly when identity holds.

**Where the two would differ is the same place for both:** arms taken from another record, or built
by hand. That is the residue identity already leaves under *`contrast_id` is a claim*; extension
would leave its own version of it, since edges handed to a producer are a claim of the same kind. It
is recorded as **a limit both readings share, not an advantage of either.** No test or production
site asks for extension.

**No check.** Rejected: the two committed tests are the hazard already present, passing silently.
