# ADR-0033 — Declaring an imputation whose parameters were never recorded

**Status:** Proposed, 2026-09-17. `/Users/bzk/bzk-omics`. Number is a guess.

**Fourth version, and much smaller than the first three.** Each was written
against a wider read of the repository, and each time the problem shrank. The
first assumed I15 blocked ingestion. It does not, and the thing that does is
not I15.

---

## The blocker is `perseus.py`, not I15

`bzk/adapters/perseus.py::_withheld_because` withholds per-sample cells wherever
`Imputation.method != 'none'` — **including where the seed and the parameters are
stated**:

> A seed reproduces a draw *given the matrix it drew into*, and the
> pre-imputation matrix is exactly what an external export does not contain;
> `store.py`'s *"the mask stays reconstructible because I15 makes the
> `Imputation` seed mandatory"* is true of a run this platform performed and not
> of one it received.

So the parameters were never the point. Knowing PXD065158's width, downshift,
seed and scope would not retain one cell. The earlier drafts proposed to unblock
something that recording cannot unblock.

**What is actually blocked, and what is not.** The `Analysis`, the
`DifferentialResult`s and the published claim set ingest fine. What is withheld
is the columnar half of I11 — and correctly, because `Cell` has four columns and
none separates a measured number from a generated one.

---

## What remains, and it is one question

I15 requires a declaration. PXD065158 can make one:
`method = 'downshifted_normal'`, with `downshift_sd`, `width_sd`, `seed` and
`scope` all null. `ONTOLOGY.md:156`–`:159` classify all four as **determined by
`method`** — and this method requires all four present. That is the whole
conflict.

**Decision: amend those four rows so `method` is joined by the parent's
`parameters_observed`.** The rows read: *determined by `method` and
`Analysis.parameters_observed` — NULL where the method would require the field
but the analysis was run outside the platform.* No new field.

`parameters_observed` is REQUIRED on every `Analysis` (I19, `:495`), never null,
and `Imputation` already anchors to its `Analysis`. Replay reproduces the null
every time, which is `determined`'s own test at `:136`.

**Why not the `Software.container_digest` route.** ADR-0021 removed that field
from identity entirely, reasoning that without a digest there is no evidence two
builds differ. The analogy is close and it fails on one point: `container_digest`
is *never* reliably present, whereas `seed` is reliably present for an internal
imputation and never for an external one. Removing it from identity would strip
the internal case too, contradicting `:83`'s *configuration belongs in identity*
and §6.5's own rationale. Conditional reliability on a recorded field is exactly
what `determined` exists for — and ADR-0021 rejected the blanket rule
(*"if a field can be absent it cannot be identifying"*) for the same reason, since
it would have stripped `Analysis` of six fields at once.

**Zero-handling: the adapter stores `0.0` as `0.0`, and the conversion is
declared on the `Analysis`.**

**Corrected 2026-09-18, and the correction reverses this paragraph's previous
version rather than refining it.** That version read *"an earlier draft put it in
`filters_applied`. Wrong home: it is a cell-value interpretation … it belongs in
the FragPipe adapter's cell-value reader, on the MaxQuant model."* It cited
`maxquant.cell_value` and then prescribed the behaviour that function exists to
forbid. Read at `019c711`, `bzk/adapters/maxquant.py:94`:

> **A reported `0` stays `0`**: MaxQuant writes zero for an undetected intensity,
> and reading that convention as absence is an interpretation the adapter has no
> licence to make (I19) — it is the statistics layer's to make and record.

The same docstring records the precedent, and the attribution matters: it was
**the protein adapter's** first draft that folded `0` to `None`, not
`maxquant_sites.py`'s. `cell_value` was *written* in `maxquant_sites.py` and
moved to `maxquant.py` on 2026-08-10, because *"two MaxQuant adapters reading one
deposit's zero as two different things is not a difference of grain"* — and the
docstring closes *"One home is the fix; which way it points was settled first."* **So the earlier draft's `filters_applied` instinct was right and the
correction of it was wrong.**

**The decision.** A FragPipe or MaxQuant adapter stores a reported `0` as `0`.
The zero-to-missing conversion is the statistics layer's, and it is declared on
the `Analysis` in **`filters_applied`**.

**Why that field, checked rather than assumed** (all read at `019c711`):

- It is a `STRING[]` whose DDL comment gives *examples* — `['reverse',
  'potential_contaminant']` (`ONTOLOGY.md:485`) — and not a closed enum, unlike
  `quantity`. A named filter is expressible.
- It is **identifying** (`ONTOLOGY.md:120`) and order-canonicalised in the fold
  (`:85`). So two reconstructions differing only in zero-handling mint different
  `Analysis` ids, which is the right answer: they are different analyses.
- `bzk/curation/loader.py:318` records that *"§3 does not classify
  `filters_applied`'s absence, so a null here would be refused"*, and defaults it
  to `[]`. The field cannot go unstated.

**Open, and narrower than the question it replaces.** Whether this is one entry
or two. The zero-to-missing reinterpretation removes no row; the valid-value
filter that depends on it does. `filters_applied`'s two examples are both row
removals, so a reinterpretation may not be a filter in the sense the field means.
One entry understates the chain; two assert an ordering the field does not
express.

---

## What this makes the FragPipe adapter

**`combined_site_K_114.0429.tsv` is the pre-imputation matrix.** FragPipe
imputed nothing; the imputation happened downstream in Perseus, whose output is
not deposited. So the FragPipe `Analysis` declares `method = 'none'` **honestly**,
and its cells are retained.

That gives three `Analysis` nodes and a coherent division:

| # | analysis | imputation | cells |
|---|---|---|---|
| 1 | FragPipe search and quant | `method = 'none'` | **retained** — 15,619 × 18 |
| 2 | Perseus, external, produced the published claim set | `downshifted_normal`, four determined nulls | withheld, correctly |
| 3 | the D5 reconstruction, internal | declared with a recorded seed | retained |

**The reconstruction runs off (1), not off (2).** I11's promise — any test
recomputable from stored values without re-ingestion — holds through the
FragPipe route and could never have held through the Perseus route. So the
adapter is not merely R4's remedy: it is the only path by which a retainable
matrix for this deposit enters the store at all.

---

## Consequences

- PXD065158 ingests as above. §6.5's two-`Analysis` prescription is satisfied by
  construction here, since GlyGly and shotgun are separate analyses anyway.
- **PXD055843 is a different problem and always was.** Its block is the same
  `_withheld_because` clause, and its question — did imputation run — decides
  whether `method = 'none'` is *true*, which decides whether its cells may be
  retained. The PI's answer is load-bearing for I11, not for I15.
- Clause (c) does not fire: 14.96% on the tested set, 17.78% on the published
  claim set, 28.47% overall.
- §11 Q8 is reached; see the adapter constraints note.

---

## Open before commit

1. **§6.5** (`:853`) restates I15 clause (b). Both homes or neither.
2. ~~Whether a `determined` absence may name a **parent** field.~~ **Answered:
   yes, mechanically.** `tests/test_schema.py` checks the node exists, the field
   is a real column, the field is identifying for that node, the kind is
   `determined` or `curated`, and the reason is non-empty. It never parses the
   reason, so a parent-field determiner passes. Its own docstring says it
   *"cannot check that a `determined` classification is TRUE — that a null is
   genuinely forced by the data rather than merely customary. That stays a
   modelling judgement."* **The guard will not catch this row if it is wrong**,
   which is the reason to argue it in the ADR rather than rely on the test.
3. **`schema.ABSENCE` must be amended in step.**
   `test_schema_absence_matches_ontology_table` checks the code-side mirror
   agrees with §3 in both directions, so a row added to the document without an
   entry here fails. And the data-half check requires that any identifying field
   absent in committed data already be declared — so the four rows must land
   *before* PXD065158's curation record does, not alongside it.
4. Generalising to unrecorded transformations as a class. Left open.
