# ADR-0004 — Split storage: graph identity in Kùzu, quantitative matrices in DuckDB

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-08-08 |
| Reserved as | `decisions/README.md` #0004 |
| Supersedes | — |

## Context

`ONTOLOGY.md` §2 has held the split since the schema was written: the graph stores identity,
relationships and provenance; per-sample quantitative values live in columnar storage. The rule is
stated there as *"if a value is one-per-entity, it is a graph property. If it is
one-per-entity-per-sample, it is columnar."*

The split was never contentious. What was never settled is **the contract across it**, and building
`bzk/quant/` forced the question, because three normative homes said three different things:

* `ONTOLOGY.md` §2 — values are *"keyed by `SiteObservation.id`"*.
* `ARCHITECTURE.md` §2 — *"`SiteObservation.quant_ref` is the join key into `quant.duckdb`."*
* `ONTOLOGY.md` §5.1, the `Observation` contract table — `quant_ref` is *"key into the columnar
  store"*.

Both cannot be the join key. If the store is keyed by the observation id, `quant_ref` carries
nothing the join does not already have, and a column that duplicates a fact is the defect
`CLAUDE.md` § Single source of truth names rather than redundancy. `CLAUDE.md` § Conventions
requires the document to be amended before code that would otherwise reconcile the divergence
silently, which is why this record exists rather than a commit message.

`ARCHITECTURE.md` §2 also names two matrices — *"site × sample and protein × sample"* — in one
store, which constrains the layout without settling whether that is one table or two.

## Decision

**1. The columnar store is keyed by the observation id, exactly as §2 says.** A row is
`(observation_id, sample_id, quantity, value)`, and the join from graph to matrix is
`SiteObservation.id = site_values.observation_id`. `ARCHITECTURE.md` §2 is amended: the id is the
join key, not `quant_ref`.

**2. `quant_ref` names the table the observation's values are in, and its absence is meaningful.**
`site_values` or `protein_values`, or `NULL`. This is the one job it can hold that the id cannot:
**`quant_ref IS NULL` means no per-sample values are retained for that observation, which is
exactly the I11 violation state**, readable at the node without opening DuckDB. `ONTOLOGY.md` §5.1
is amended from *"key into"* to say this.

**3. Two tables, not one**, matching the two matrices `ARCHITECTURE.md` §2 already names. A single
table would need a grain discriminator, and its only content would be the label already fixed by
the observation id's identity tuple — a second home for a fact.

**4. `quantity` is part of the row key**, because one observation legitimately has more than one
per-sample vector. Measured on PXD018299: the deposit carries 48 `Intensity <sample>` columns and 12
`Ratio mod/base <sample>` columns over the same 12 samples, and `ROADMAP.md` § Measured findings
already records both as usable quantities at this grain. Without `quantity` in the key, ingesting
the second collides with the first. The primary key is `(observation_id, sample_id, quantity)`.

## What was rejected

**`quant_ref` as the join key, with the store keyed by it.** This is what `ARCHITECTURE.md` §2 said.
Rejected because the value would then be minted, and a minted per-observation locator is a second
identity for a node that already has a content-derived one (ADR-0020) — two ids for one thing, and
the one in the columnar store would not be reproducible from the identity tuple.

**Dropping `quant_ref` from the DDL.** Consistent, and it was the tempting answer once the column
was seen to be redundant *as a join key*. Rejected because the column has the non-redundant job
decision 2 gives it, and because removing it is a §3 partition change reaching `test_schema.py`'s
identity guard for a column that is about to become useful.

**One table with a `grain` column.** Rejected under decision 3.

**Parquet files rather than DuckDB tables.** `ONTOLOGY.md` §2 permits either (*"DuckDB / Parquet"*).
Rejected for now because `rebuild.py` already drops `quant.duckdb` as a unit and a single file makes
the regenerability claim in `OPERATIONS.md` §1 checkable by deleting one path. Nothing here
forecloses Parquet: the row shape is the contract, not the container.

## Consequences

`quant_ref` becomes an I11 witness readable from the graph alone. The two grains stay separable
without a discriminator column. A second quantity over the same observations is an insert rather
than a migration. And `ARCHITECTURE.md` §2's *"Nothing per-sample enters the graph"* is unchanged —
`quant_ref` is one-per-entity, so §2's own rule puts it on the node.
