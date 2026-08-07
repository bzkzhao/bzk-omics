# ADR-0020 — Deterministic, content-derived ids for evidence nodes

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

## Context

`ONTOLOGY.md` §3 gave locally-authored (evidence) nodes a `bzk:` **ULID** — a random,
allocation-unique id. Reference nodes, by contrast, are content-derived (I7), so identical entities
converge on one node with no merge step.

I9 requires the whole graph to be regenerable from `raw/` (content-addressed by SHA-256), the
curation export, and this DDL. A random id defeats that: re-ingesting the same input mints *new*
ULIDs, so a rebuild produces duplicate nodes rather than the same nodes, and `rebuild.py` cannot
verify reproduction by identity — the check at the heart of the rebuild-over-migration bet (ADR-0012,
I9). This surfaced during the resolver work as a standing tension between §3 (ULID), I7 (content
keys), and I9 (idempotent replay): three rules that could not all hold.

## Decision

Evidence nodes get **deterministic, content-derived ids**, replacing the ULID.

```
id = "bzk:" + truncated_sha256_hex( canonical( identity_tuple ) )
```

where `identity_tuple` is the node's **label**, its **identifying fields**, and the **ids of the
content-addressed nodes it anchors to**. Anchors bottom out in identifiers that are already
content-addressed — reference CURIEs, the `ModificationSite` key (ADR-0005), and
`Dataset.content_hash` (the SHA-256 of the raw file) — so an evidence id is a pure function of
`raw/` + the curation export + the DDL, which is exactly the I9 input set. `canonical` is a stable
serialization (sorted keys, normalized values) so replay is byte-identical.

Identity **excludes** mutable and provenance-timestamp fields — `asserted_at`, `retracted_at`,
`created_at` — and the quantitative matrix, which is referenced by `quant_ref`, not hashed into
identity.

One key builder serves both reference and evidence nodes. This discharges the "single key builder"
that I7 was recorded as waiting on (`HANDOFF.md` §8, CON class).

## Consequences

**Positive.** Re-ingestion is idempotent: the same input yields the same ids, so `rebuild.py`
verifies reproduction by id equality rather than by a fuzzy content comparison. The I7 / §3 / I9
tension resolves in favour of I7's key discipline, now applied uniformly.

**Supersession and retraction still follow I6, for free.** A superseding assertion differs in
content — `basis`, candidate set, `rationale`, the supporting `Analysis` — so it canonicalizes to a
*different* id automatically; no id needs to be allocated. Retraction sets `retracted_at` in place,
and because that field is outside identity it does **not** change the id — so every inbound edge
survives the retraction. An id that folded in `retracted_at` would mutate under retraction and orphan
those edges; excluding it is what makes the append-only model and content-addressing coexist.

**"Local ids are never reused" is deliberately inverted.** Under ULIDs each allocation was unique;
under content-derivation, identical content yields the same id *by design*. That is reuse, and it is
precisely the idempotency I9 needs — not accidental collision.

**Collision.** A truncated SHA-256 over a full identity tuple; 128 bits is ample for a single-lab
graph. If two genuinely distinct nodes ever canonicalize identically, that is a modelling defect — a
missing identifying field — and it surfaces as the change-set duplicate-`id` failure already enforced
by structural validation (ADR-0019, rule 4), not as silent data loss.

**The §9 worked-example ids become illustrative digest stubs, not literal ULIDs.**

## Alternatives considered

**Keep ULIDs; dedupe on replay by matching content.** Rejected: it pushes a content-equality merge
into every rebuild — the exact merge step I7 exists to remove — and makes "same graph" a fuzzy
comparison rather than id equality, which is not a property `rebuild.py` can assert cheaply.

**Per-type structured composite keys (as `ModificationSite` uses).** Rejected as the general form:
readable where content is simple, but evidence identity spans peptides, parameter sets, and multiple
anchors, so the keys grow unwieldy and inconsistent across node types. A uniform opaque digest keeps
one builder and one format. Human-readability is served by the identity tuple — recorded in §3 and
here — not by the id string.
