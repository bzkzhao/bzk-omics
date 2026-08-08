# ADR-0013 — Quantitative matrices retained permanently, never only derived statistics

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-08-08 |
| Reserved as | `decisions/README.md` #0013 |
| Depends on | ADR-0004 (the split's contract) |

## Context

I11 (`ONTOLOGY.md` §8) is a **positive** obligation: *"Every observation persists its per-sample
quantitative values in the columnar store, not merely the statistics derived from them."* Until this
record it was unmet in the plainest way — `SiteObservation.quant_ref` was null on all 2,029 nodes,
`quant.duckdb` was never created, and the matrix was re-read from the deposit on every run.

"Every observation" is today exactly `SiteObservation` and `ProteinObservation`. `PeptideObservation`
and `EnrichmentObservation` are deferred subtypes with no table, so the obligation is discharged when
those two persist their values, not deferred until the contract has more members.

Retention raises one question the split itself does not: **which values** — the measured ones, or
the ones an analysis will use after imputation.

## Decision

**1. The matrix holds measured values and nulls. Pre-imputation.**

This was already decided and is followed rather than re-decided. `ARCHITECTURE.md` § *Imputation is
part of the statistics layer, not the adapter* states: *"Imputation never happens in the adapter.
Adapters emit measured values and nulls; what to do about the nulls is an analysis decision that
must be recorded."* The writer here **is** the adapter — it is the only component that has read the
per-sample columns and the only one that mints the `quant_ref` it must set — so that sentence
settles the question directly. Had the matrix been written anywhere else the question would have
reopened, and the reasoning would have had to say why the writer moved; it did not move.

**2. `n_imputed` is a cross-check, not the record of which cells were generated.**

`ONTOLOGY.md` §5 gives `SiteObservation` `n_imputed INT64` — *"how many of that site's values were
generated rather than measured"* (§6.5). It is a **count, not a mask**, so it cannot say *which*
cells. That column's standing depends entirely on decision 1, and the dependency runs in only one
direction:

* **Pre-imputation storage (chosen).** The mask is reconstructible — the retained measured matrix
  says which cells were null, and I15 makes the `Imputation` node's `method`, `downshift_sd`,
  `width_sd` and `seed` mandatory precisely so the generated values are reproducible from them.
  `n_imputed` is then a redundant-but-checkable summary: it must equal the count of nulls the
  analysis filled, and disagreement is a detectable defect.
* **Post-imputation storage (rejected).** `n_imputed` would become the *sole* surviving trace that
  any cell was generated, and being a count it could not identify one. I15 (*"stochastic imputation
  records its seed"*) and `ONTOLOGY.md` §6.5's requirement that generated values never be displayed
  as measurements would be unenforceable at cell level, because nothing would distinguish the cells.
  `CLAUDE.md` § *Generated values are never displayed as measurements* is the same rule one level
  out: a volcano plot that cannot tell a measured point from an imputed one is wrong, and a matrix
  that cannot either makes that plot impossible to build correctly.

**3. Permanently, and the store is derived rather than authoritative.**

`OPERATIONS.md` §1 already classifies `quant.duckdb` as regenerable and low backup priority. That
classification is *established by running* rather than inherited here — §1's own neighbouring
paragraph is the correction of a regenerability claim (`cache/uniprot/`) that was asserted and
wrong. Permanence therefore means *never discarded by a pipeline stage after computing a statistic*
(I11's own words), not *never deleted*: `rebuild.py` drops and recreates it, which is the same
standing the graph has under I9 and ADR-0012.

## What was rejected

**Storing the post-imputation matrix**, or both. Rejected under decision 2. Storing both was the
weaker temptation and fails for a different reason: two matrices for one observation with no
recorded relationship between them is two homes for one fact, and the imputed one is derivable from
the measured one plus a seeded `Imputation`, so it is a cache, not a record.

**Deferring until `PeptideObservation` and `EnrichmentObservation` exist**, so the layer is written
once against the full contract. Rejected because I11 is unmet *now* for the subtypes that exist, and
the row shape ADR-0004 fixes is grain-agnostic — a third grain is a third table, not a redesign.

## Consequences

I11 moves from unmet to met for both live observation subtypes. Recomputation and the comparison
capability `ARCHITECTURE.md` §4 gives the statistics registry both become possible without
re-ingestion, which is the reason the invariant exists. And the imputation mask stays reconstructible
from stored content, so `n_imputed` can be checked rather than trusted.
