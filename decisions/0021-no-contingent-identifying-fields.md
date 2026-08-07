# ADR-0021 — An identifying field may be absent only when its absence is determined

| | |
|---|---|
| Status | Accepted |
| Date | 2026-08-07 |
| Supersedes | — |
| Superseded by | — |

Cites ADR-0016 (release mutates non-identifying fields) and ADR-0009 (curation, not configuration)
as precedents; supersedes neither.

## Context

`Person` keyed on `orcid` and **fell back to `name`** when no ORCID was recorded. `Software` keyed on
`name` + `version` + `container_digest`, where the digest may be absent. Both break ADR-0020's
premise — that an id is a pure function of `raw/` + the curation export + the DDL — in two ways, and
the second is the serious one:

1. **Collision.** Two researchers sharing a name, neither with an ORCID — routine for collaborators
   and for submitters read off a methods section — receive one id. Bad, but *stable*: replay
   reproduces it.
2. **Non-determinism.** The same person ingested once without an ORCID and later with one receives
   **two** ids. The id becomes a function of *when you looked* rather than of the person. No care at
   ingest prevents this, and it is exactly what content-derived identity exists to rule out.

`Software`'s case is not quite a fallback and the difference matters: `container_digest` is an
**optional component of a composite key**, which is a simpler and more clear-cut bug — it guarantees
fragmentation the moment the digest arrives, and buys no collision protection in exchange.

The problem is general, so it deserves a rule rather than two patches. `Publication` has the same
shape latent (a preprint DOI and the published DOI/PMID), and any future node keyed on an external
identifier that can arrive late will inherit it.

**The schema already solved this once.** `Dataset` is keyed on `content_hash` — always computable
from the bytes in hand. Its `external_accession` arrives late (on PRIDE deposit), its `source`
changes `local` → `pride`, its `embargo_released_at` gets set, and **all three are non-identifying**.
ADR-0016 states release is an event that mutates non-identifying fields *on the same node*. The
right answer was already in the repository, in one place, contradicted in two.

## Decision

**An identifying field may be absent only when its absence is determined by the data, never when it
is contingent on what was known at ingest.**

The distinction is the whole rule, because the two absences are indistinguishable in storage:

- **Determined** — a protein-grain `Analysis` has no `localization_threshold` because there are no
  residue positions to localise; an `Analysis` outside curation has no `basis`. Replay produces the
  same null every time, so identity is unharmed.
- **Contingent** — an ORCID was not to hand; a container digest had not been recorded. The null
  describes the moment, not the entity.

A simpler rule — *"if a field can be absent it cannot be identifying"* — was considered and rejected
in this form: it would strip `Analysis` of eight identifying fields at once (`basis`, `confidence`,
`external_tool`, `external_version`, `localization_threshold`, `parameters_json`, `workflow_id`,
`workflow_revision` are all legitimately null on the fixture's own nodes), collapsing `Analysis`
identity and the qualifying-child fold with it.

Applied:

- **`Software` keys on `name` + `version`.** `container_digest` becomes a non-identifying attribute.
  Justification is I19's discipline: without a digest there is *no evidence* two builds differ, so a
  key that claims to distinguish them asserts more than the data supports. The cost — two undigested
  builds of one version converge — is the honest representation, not a loss.
- **`Person` identity comes from the curation export, never from an ingest-time inference.** Where no
  ORCID exists the curator supplies a discriminator. The id is then a function of a versioned,
  diffable file that is already in I9's input set, rather than of whatever a particular ingest
  happened to know. `ONTOLOGY.md` §3 classifies `Person.orcid`'s absence as determined *by the
  curation record*.
- **Every identifying field that can be null is classified** `determined` or `contingent` in §3, and
  `tests/test_schema.py` **rejects any `contingent` classification** — the marker exists to force a
  redesign, not to license the state. The guard also requires that an identifying field found absent
  in committed data be declared, so an unclassified absence cannot pass unnoticed. It caught
  `Protein.accession` missing from the fixture on its first run.

## Consequences

**Positive.** No merge step, no provisional state, no reconciliation machinery — the rule costs
nothing at replay because a node exists only when its identifier is in the inputs. It is
mechanically guardable, in the same shape as the §3 partition and key-template guards. And it
generalises: any future node keyed on a late-arriving external identifier is decided in advance.

**`Person` ids change when curation is corrected.** Adding an ORCID to a curation record changes that
person's id on the next rebuild — but *consistently, for every dataset at once*, which is how every
other curated fact already behaves and is cheap because the graph is derived (I9). This is the
accepted cost, and it is qualitatively different from the defect it replaces: the change is a
versioned edit with its own diff, not an accident of ingest order.

**Collisions become a curation responsibility.** Two people recorded identically still collide — but
the curator can add a discriminator, and the act is visible and correctable. This follows ADR-0009,
which made sample-to-condition mapping a curation activity rather than configuration for
structurally the same reason: a judgement that must be made anyway is better made explicitly, with
provenance, than implied by a schema default.

**Ingest cannot mint `Person` opportunistically.** A name in a methods section no longer produces a
node. That is intended — a name read off a paper does not identify a person — but it means
authorship is unrecorded until someone curates it.

**Rejected: `Analysis.operator_name`.** An earlier draft proposed a non-identifying string column to
hold name-only attributions. Dropped: under the curation rule it is unnecessary, and a second
representation of authorship is a real cost that every consumer would have to handle.

**Not decided here: `Publication`.** A preprint DOI and the published DOI/PMID give different ids for
arguably one work, so citations fragment across a version boundary. It may be *correct* that a
preprint and a published paper are different artifacts — but that is a judgement worth making
explicitly rather than by default. Recorded as `ONTOLOGY.md` §11 Q10.

## Alternatives considered

**Provisional minting with reconciliation.** Mint under the fallback flagged `provisional`, reconcile
when the authoritative identifier arrives. Rejected on two grounds. It reintroduces the merge step
I7 exists to eliminate — *"identical entities from different sources converge on one node without a
merge step"* — for one node type. And reconciliation is not an I6 supersession: I6 governs
*assertions*, defeasible claims that can be wrong, whereas learning an ORCID does not make the
earlier record a wrong claim but establishes that two ids denote one entity. Retracting a `Person`
would read as "this person was retracted." Each of the three ways to handle inbound edges is
unsatisfying: rewriting them mutates the graph in place; a `SAME_AS` edge pushes the cost onto every
query and provenance traversal indefinitely; retracting and re-emitting duplicates provenance. It
would also need a reconciliation-record mechanism in the curation export, parallel to the retraction
records of `OPERATIONS.md` §2, which does not exist.

**Keep the fallback and accept it.** Rejected: it leaves ADR-0020's central premise false for two
node types, silently, with nothing marking the exception.
