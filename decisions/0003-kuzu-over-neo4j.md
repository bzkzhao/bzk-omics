# ADR-0003 — Kùzu for the graph store

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-06 |
| Supersedes | — |
| Superseded by | — |

## Context

`VISION.md` commits to local-first: full functionality on a laptop, no cloud account, no institutional IT request, install-to-value in one afternoon. The target user is a graduate student, not a team with infrastructure support.

The data model is a property graph with a modest number of richly connected nodes, queried by traversal.

## Decision

Kùzu, embedded, as the graph store. Quantitative matrices live separately in DuckDB (see ADR-0004).

## Consequences

**Positive.** Kùzu is embedded — a library, not a server. Nothing to install, configure, start or secure. It speaks Cypher, so the DDL in `ONTOLOGY.md` is directly executable and the query language is one a collaborator may already know. It is columnar, so traversals over a few million nodes stay fast on laptop hardware. MIT licence, compatible with any eventual choice for this project.

**Negative.** Younger and less battle-tested than Neo4j, with a smaller community and less documentation. Cypher support is broad but not complete. If it were abandoned, migration would be needed — mitigated by invariant I9: the graph is derived, so migration means re-ingestion rather than a data rescue.

## Alternatives considered

**Neo4j Community.** The obvious default, mature and well documented. Rejected: it requires a running server process, which contradicts local-first directly and adds an operational burden a single researcher should not carry.

**SQLite or DuckDB with an explicit edge table.** Would work and is maximally boring. Rejected because the product thesis is that relationships are the object of interest; expressing traversals as recursive SQL joins would make the central query patterns awkward to write and slow to iterate on.

**Oxigraph (embedded RDF, SPARQL).** Attractive because provenance is modelled in PROV-O and RDF is native to that. Rejected for v0.1: RDF tooling is heavier, the query language is less familiar, and PROV-O can be expressed as property-graph edges without loss. Worth revisiting if RO-Crate export proves awkward.
