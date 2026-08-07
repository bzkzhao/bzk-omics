# ADR-0020 — Deterministic, content-derived ids for evidence nodes

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |
| Revised in place | **2026-08-07, three commits after acceptance** — `bf8c837` (pointer to §3's identity table; the retraction-export consequence), `86dba42` (the `parameters_json` canonicalization rule; the consequence recording that the identity table exposed the `test`/`fdr_method` contradiction), `120be8b` (corrected "discharges I7" to the future tense, since no key builder exists). The edits stand and are not reversed. **They were a breach of the append-only convention** in `decisions/README.md`, recorded here so the exception is visible rather than silent. From 2026-08-07 the convention holds strictly: an Accepted ADR is amended only by a superseding ADR. |

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

A field that is itself structured — `Analysis.parameters_json`, which carries a test's `s0` and
randomisation count — is **parsed and canonically re-serialized** (sorted keys, normalized numeric
forms) before it enters the tuple, never hashed as raw text. Canonicalizing the tuple treats a field
as a value and does not reach inside a string, so without this rule two ingesters emitting the same
parameters with different key order or float formatting would mint different `Analysis` ids. See
`ONTOLOGY.md` §3.

Identity **excludes** mutable and provenance-timestamp fields — `asserted_at`, `retracted_at`,
`created_at` — and the quantitative matrix, which is referenced by `quant_ref`, not hashed into
identity.

The identifying fields and anchors for each evidence node type are enumerated in the **per-label
identity table in `ONTOLOGY.md` §3**. That table — not this ADR, and not the builder — is the source
of truth for identity; the key builder mirrors it, guarded by a test against it when it lands.

One key builder serves both reference and evidence nodes. This is the decision that **will**
discharge the "single key builder" I7 is recorded as waiting on (`HANDOFF.md` §8, CON class) — the
builder is not yet written, and `invariants.py` still tracks I7 as pending. An earlier revision of
this paragraph read "discharges", which would have told a reader that evidence ids are already
deterministic in code. They are not.

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

**Excluding `retracted_at` from identity makes the export responsible for carrying retraction.** The
same exclusion that keeps an id stable under retraction means a rebuild reconstructs a node *without*
its retraction — nothing in `raw/` supplies the field. Retraction therefore lives in the curation
export as its own record (retracted node id, `retracted_at`, reason), which replay re-applies after
reconstruction; see `OPERATIONS.md` §2. Omit it and every retraction is lost on the next rebuild,
silently violating I6 — the field being out of identity is precisely why the export, not the digest,
must carry it.

**"Local ids are never reused" is deliberately inverted.** Under ULIDs each allocation was unique;
under content-derivation, identical content yields the same id *by design*. That is reuse, and it is
precisely the idempotency I9 needs — not accidental collision.

**Collision.** A truncated SHA-256 over a full identity tuple; 128 bits is ample for a single-lab
graph. If two genuinely distinct nodes ever canonicalize identically, that is a modelling defect — a
missing identifying field — and it surfaces as the change-set duplicate-`id` failure already enforced
by structural validation (ADR-0019, rule 4), not as silent data loss.

**The §9 worked-example ids become illustrative digest stubs, not literal ULIDs.**

**The identity table earns its keep immediately.** Making §3 the source of truth for identity (and
guarding it with a test in `tests/test_schema.py`) surfaced a pre-existing contradiction the DDL had
carried on its own: `test` and `fdr_method` sat on `DifferentialResult` while `ARCHITECTURE.md` §4
recorded a test's parameters on the `Analysis`. Since every result of an analysis shares its test,
two analyses differing only by test collapsed to one id — this ADR's own missing-field collision.
Resolved by moving both columns onto `Analysis` (ONTOLOGY v1.6, I16); the table did not create the
defect, it exposed one already latent.

## Alternatives considered

**Keep ULIDs; dedupe on replay by matching content.** Rejected: it pushes a content-equality merge
into every rebuild — the exact merge step I7 exists to remove — and makes "same graph" a fuzzy
comparison rather than id equality, which is not a property `rebuild.py` can assert cheaply.

**Per-type structured composite keys (as `ModificationSite` uses).** Rejected as the general form:
readable where content is simple, but evidence identity spans peptides, parameter sets, and multiple
anchors, so the keys grow unwieldy and inconsistent across node types. A uniform opaque digest keeps
one builder and one format. Human-readability is served by the identity tuple — recorded in §3 and
here — not by the id string.
