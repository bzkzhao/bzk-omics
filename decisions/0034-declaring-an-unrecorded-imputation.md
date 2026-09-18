# ADR-0034 — Declaring an imputation whose parameters were never recorded

| | |
|---|---|
| Status | Proposed |
| Date | 2026-09-18 |
| Supersedes | — |
| Superseded by | — |

Lands `Proposed` per `decisions/README.md`. It becomes `Accepted` only once the
round-trip completes. Numbered 0034 on landing: 0033 went to the frame record,
which landed first.

**Every check in this record was re-derived at `59d9433` (2026-09-18).** The
draft's own citations were written against `019c711`; nothing under
`bzk/adapters/`, `bzk/curation/`, `bzk/ontology/` or in `ONTOLOGY.md` moved
between the two.

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

**The four rows already exist, in both homes, and the act this record proposes
is amending a determiner rather than adding a classification.** Measured at
`59d9433`:

- `ONTOLOGY.md:156`–`:159` carry the four rows — `downshift_sd` (*"`method` —
  NULL unless downshifted normal"*), `width_sd` (*"`method` — as
  `downshift_sd`"*), `seed` (*"`method` — stochastic methods only (I15)"*) and
  `scope` (*"`method` — NULL when nothing is imputed"*), each `determined`.
- `bzk/ontology/schema.py`'s `ABSENCE` carries exactly the same four keys,
  `("Imputation", …)`, each mapped to `"determined"`.

So nothing is missing and nothing needs adding. **What is wrong is the
determiner cell.** For an external analysis whose method *is* stated —
imputation from a normal distribution around the detection limit — `method`
determines those four fields to be **non-null**. They are null anyway, because
the publication never stated them. That null is contingent on what a paper
happened to record, and ADR-0021 calls a contingent null on an identifying
field *"a defect to redesign rather than a state to declare"*.

**Decision: amend those four determiner cells so `method` is joined by the
parent's `parameters_observed`.** The rows read: *determined by `method` and
`Analysis.parameters_observed` — NULL where the method would require the field
but the analysis was run outside the platform.* No new field, no new row, and no
change of `Kind`: all four stay `determined`.

`parameters_observed` is REQUIRED on every `Analysis` (I19, `:495`), never null,
and `Imputation` already anchors to its `Analysis`. Replay reproduces the null
every time, which is `determined`'s own test at `:136`. Where
`parameters_observed` is `false`, the null is fixed by a recorded fact — the
analysis was not observed, so its parameters are not recoverable from it — which
is outside the moment of ingest and is exactly what ADR-0021 requires of a
`determined` absence.

**This decides the parent-field question rather than leaving it open: a
`determined` absence may name a field of the node's anchor, and this is the
instance.** The ground is not that the guard permits it — it does, and that is
recorded below as a fact about the guard rather than as a licence. The ground is
that §3's own test for `determined` is whether *something outside the moment of
ingest forces the null*, and it does not say that something must live on the same
node. `Imputation` anchors to exactly one `Analysis` (`IMPUTATION_FOR`,
`MANY_ONE`), that `Analysis` always carries `parameters_observed` (I19), and the
fold at `:169` already draws the child's identity and the parent's together. A
determiner that names `Analysis.parameters_observed` is therefore as reproducible
on replay as one naming `method`, which is the property `determined` is asking
about. What would fail the test is a determiner naming something *contingent* —
a value read at ingest time, or a field that may be absent — and
`parameters_observed` is neither.

**No code change is required, and the draft's claim that it is has been struck.**
`tests/test_schema.py::test_schema_absence_matches_ontology_table` parses §3's
table with four capture groups and then discards the fourth:
`documented = {(label, field): kind for label, field, kind, _why in rows}`. It
compares `schema.ABSENCE == documented` — a `(node, field) → kind` mapping.
**The determiner prose is not compared**, so amending it moves no code and
breaks no test. `schema.ABSENCE` is already correct and stays untouched.

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
forbid. Read at `019c711` and re-derived unchanged at `d09bdae` (2026-09-18;
nothing under `bzk/adapters/`, `bzk/curation/` or in `ONTOLOGY.md` moved between
them), `bzk/adapters/maxquant.py:93`–`:96`:

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
- **The live values, measured at `d09bdae` across `bzk/` and `data/curation/`,
  already include parameterised tokens** — so a named filter is expressible in
  the form it would need, not merely in principle. In committed code:
  `("reverse", "potential_contaminant", "localization_prob")`
  (`maxquant_sites.py:100`), `("reverse", "potential_contaminant")`
  (`maxquant_protein_groups.py:78`), and the differential's run declaration
  (`pxd018299_differential.py:470`–`475`), which builds
  `localization_prob>=0.75` and `presence>=2_in_either_group` from the values it
  ran at. In committed records: `["reverse", "potential_contaminant"]`
  (`analysis_PXD018299_KOIFN_vs_WTIFN.json`) and `["presence>=3_in_either_group"]`
  (`analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`). The suite adds
  `only_identified_by_site` (`tests/test_perseus.py:64`). Two adapters carrying
  **different** tuples, and `invariants.py:499` checking only that the field is
  not null while the adjacent `quantity` branch checks enum membership, are the
  same fact from two other directions.

  **This settles expressibility and nothing else.** Every value observed above is
  a row **removal** — including the two parameterised ones, which remove rows on
  a threshold and on a presence count. So it leaves the question below exactly
  where it was.

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

## Implied changes, described and not made

Following ADR-0031's section of the same name. **Nothing below is done in this
record**, and `ONTOLOGY.md` is not edited here.

1. **The four determiner cells at `ONTOLOGY.md:156`–`:159`**, each gaining
   `Analysis.parameters_observed` beside `method`, in the wording the Decision
   gives. `Kind` stays `determined` on all four, so `schema.ABSENCE` does not
   move with them.
2. **The I15 clause-(b) rationale, in all three of its homes or in none.** The
   single-source rule binds them together, and there are three rather than the
   two the draft named — measured at `59d9433`:
   - `:83`, *Configuration belongs in identity* — *"§6.5 and I15 make the seed
     mandatory precisely because it materially determines the result, and two
     runs differing only in seed produce different numbers."*
   - `:853`, §6.5 — *"A seed is mandatory for stochastic methods: without it,
     the analysis is not reproducible even from the same inputs, which defeats
     I9."*
   - `:962`, I15 itself — *"Stochastic methods record a seed; without one the
     analysis is irreproducible from its own inputs and I9 fails."*

   Two further places state the *requirement* or the *classification* without the
   rationale, and are listed so a later edit does not miss them: the DDL comment
   at `:839` (*"REQUIRED where the method is stochastic"*) and §3's `seed` row at
   `:158`, which is one of the four cells in 1.
3. **Neither before the other is decided**, and this record fixes no ordering
   between 1 and 2. What it does fix is that 1 alone is enough for PXD065158 to
   be declarable; 2 is a documentation-consistency question that the amendment
   surfaces rather than creates.

---

## Open before commit

1. ~~**§6.5** (`:853`) restates I15 clause (b). Both homes or neither.~~
   **Re-measured: three homes, not two** — `:83`, `:853` and `:962`. Carried into
   *Implied changes* 2 rather than left here, since it is an edit to describe
   rather than a question to answer.
2. ~~Whether a `determined` absence may name a **parent** field.~~ **Decided in
   the Decision above**, on the modelling ground rather than on the guard's
   silence. The mechanical fact stands and is recorded there as a fact about the
   guard: `tests/test_schema.py` checks the node exists, the field is a real
   column, the field is identifying for that node, the kind is `determined` or
   `curated`, and the reason is non-empty — it never parses the reason. Its own
   docstring says it *"cannot check that a `determined` classification is TRUE —
   that a null is genuinely forced by the data rather than merely customary. That
   stays a modelling judgement."* **The guard will not catch this row if it is
   wrong**, which is why the argument is in the record.
3. ~~**`schema.ABSENCE` must be amended in step.**~~ **Struck — measured false at
   `59d9433`.** `ABSENCE` already carries all four `("Imputation", …)` keys as
   `determined`, so no row is being added to §3 and none is missing from the
   mirror. `test_schema_absence_matches_ontology_table` compares
   `(node, field) → kind` and discards the determiner text, so amending a
   determiner needs no code change and breaks no test. What the struck item got
   right, and what survives: the data-half check requires that any identifying
   field absent in committed data already be classified — and all four already
   are, so PXD065158's curation record is not blocked on an ordering either.
4. Generalising to unrecorded transformations as a class. Left open.
