# OPERATIONS.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.4 |
| Last reviewed | 2026-08-07 |
| Depends on | `ARCHITECTURE.md`, `ONTOLOGY.md` |
| Authoritative for | Backup, cache policy, dependency pinning, rebuild discipline |

Local-first means no cloud provider is silently handling durability. Every operational concern a hosted product would inherit for free has to be answered here, or it is not answered at all.

Created after external review identified backup, cache eviction and testing as absent from the document set. They were absent because a laptop-local design makes them easy to forget, which is precisely why they need a home.

---

## 1. What must survive a disk failure

Not everything. Invariant I9 states that the graph is derived, so most of it is regenerable. The distinction determines what gets backed up and how often.

| Content | Regenerable? | Backup priority |
|---|---|---|
| `curation_*.json` | **No** — human judgement | **Critical.** Version-controlled, not just backed up |
| `analysis_*.json` | **No** — records choices made | **Critical.** Version-controlled |
| Manual `ModifierAssignment`, `EnzymeAssociation` | **No** — asserted by a person | **Critical.** Export nightly (§2) |
| `raw/` source files | Yes, from PRIDE — unless embargoed | High for embargoed data, low otherwise |
| `graph.kuzu/` | Yes, from raw plus curation | Low |
| `quant.duckdb` | Yes | Low |
| `cache/uniprot/` | Yes, slowly | Low |

**The asymmetry is the point.** A few megabytes of JSON are irreplaceable; tens of gigabytes of graph and matrices are a compute cost. Backing up the small irreplaceable set frequently is both cheaper and more effective than snapshotting everything occasionally.

---

## 2. Backup policy

**Human-authored content — continuous.** Curation records, analysis records and manual inferences serialise to JSON under `data/curation/` and live in the git repository. They are versioned, diffable, and survive independently of any machine.

Each record identifies its input file by a `content_hash` — the SHA-256 of the raw table — alongside the bare filename it carries today. The filename is not an identity: two deposits, or a re-download after a deposit is revised, can share a name and differ in content. I9 replay reconstructs the graph from `raw/` plus these records, so the hash is what lets a rebuild confirm it is replaying against the same bytes the curation was written for, rather than a file that merely matches by name. Existing records under `data/curation/` predate this field and must be back-filled when their input is next in hand.

This requires a nightly export of manual assertions from the graph to JSON, since the graph itself is not committed. Without it, an assignment made in the UI exists only inside `graph.kuzu/` and violates I9.

**Retractions travel as their own records.** `retracted_at` is deliberately outside evidence-node identity (ADR-0020), so a rebuild reconstructs the node but not the fact that it was retracted — and nothing in `raw/` supplies that field. I6 requires a retraction to propagate to every downstream figure and report, so the curation export carries a **retraction record** for each retracted assertion: the retracted node's `id`, its `retracted_at`, and a `reason`. Replay reconstructs the nodes, then applies these records — setting `retracted_at` on the named node and propagating the retraction. Omit them and every retraction is silently lost on the next rebuild: the append-only model survives in the live graph but not across regeneration, which is I6 failing exactly where I9 is supposed to make it cheap.

**Embargoed source data — mirrored, never committed.** Unpublished collaborator data cannot go in a public repository (I18) and cannot be re-downloaded from PRIDE. It needs a second copy on separate physical media, and that is a manual responsibility with no software answer.

**Everything else — rely on rebuild.** A weekly `bzk rebuild` verifies that the derived state genuinely is derivable. A rebuild that fails is a more useful alarm than a backup that silently stopped running.

---

## 3. Cache policy

The UniProt cache is content-addressed and immutable: an entry is keyed on accession, isoform and sequence version, and a new version is a new entry rather than an overwrite (I2). Over a multi-year project it grows without bound.

**Retention:** keep entries accessed within 90 days, plus every entry referenced by a live `ModificationSite` regardless of age. Evict the remainder.

The second clause matters. An entry can be years untouched and still be the only record of the sequence a site's position was validated against. Evicting it does not corrupt the graph — the key still carries the version — but it forces a network fetch to re-validate, and for a superseded version that fetch may fail.

**Eviction is never automatic on a schedule.** It runs on explicit command, reports what it would remove, and requires confirmation. A cache that silently discards the sequence underlying a published figure is worse than a large cache.

---

## 4. Dependency pinning

**Kùzu is pre-1.0.** Cypher coverage is incomplete, the Python API is still moving, and minor releases have changed behaviour. Pin an exact version in the lockfile. Do not float, do not use a compatible-release specifier.

Upgrading Kùzu is a deliberate act: bump the pin, run the full rebuild, run the test suite, confirm the 12-of-14 regression still holds, and record the outcome in an ADR. If a rebuild fails after an upgrade, revert the pin rather than patching around it.

The same discipline applies to DuckDB and Polars, though both are more stable.

**This is the mitigation for choosing a young dependency (ADR-0003).** I9 makes the risk survivable — a broken Kùzu means re-ingesting, not losing data — but only if the rebuild path is exercised often enough to be trusted when needed.

---

## 5. Rebuild discipline

`bzk rebuild` drops the graph and the quantitative store, then reconstructs both from `raw/`, the curation export, and the current DDL.

**Run it weekly, and after every schema change.** The claim in I9 — that schema change is a compute cost rather than a migration — is true only while this is verified. An untested rebuild path is an assumption, not an invariant.

A rebuild that produces a different 12-of-14 result is a regression, and the appropriate response is to stop and find out why rather than to accept the new number.

---

## 6. Testing

Three fixture sets, written before the code they exercise.

**Invariant violations.** One case per invariant, each expected to fail ingestion. A `DifferentialResult` with `protein_adjusted = 'applied'` and no `ADJUSTED_BY` edge. A `ModificationSite` without a sequence version. A `SiteObservation` rendered against one protein with a `razor`-basis assignment. These tests exist to prove the invariants are enforced rather than merely documented.

**Adapter contracts.** A small PXD018299 subset committed to `tests/fixtures/`, plus a synthetic Perseus table. Every adapter must produce the same `Observation` contract from its own format.

**Resolution edge cases.** Synthetic and real: an isoform accession, an accession whose sequence was amended after the search, a retired accession, a candidate set containing both Swiss-Prot and TrEMBL entries. These are the cases that produced silent errors during exploration and are the ones most likely to regress.

### Known partial coverage

One test per invariant means `validate()` implements the clause each test targets, not every clause of each invariant. Recorded so the gap is a decision rather than silent.

| Invariant | Enforced | Not yet enforced | Enforceable when |
|---|---|---|---|
| I2 | `SITE_ON` target (a `ProteinSequence`) carries `sequence_version` | Site key embeds sequence version *and* isoform; site-key version equals the target's `sequence_version` (ADR-0005) | Ingestion produces keys |
| I3 | An ambiguous assignment may not name a modifier | Every `SiteObservation` has ≥ 1 `ModifierAssignment` | Ingestion produces full change-sets |

Both remaining clauses are properties of a complete ingestion rather than of a single staged write, so neither is checkable against the current change-set interface. Add them with the first adapter, not before — a test that cannot fail is worse than an absent one.

**The 12-of-14 regression** runs against the full pipeline, not a notebook. It is the end-to-end test and the number is recorded in `ROADMAP.md` § Measured findings.

---

## Open questions

1. Where does the nightly manual-assertion export write to, and what triggers it? A daemon is heavier than this product should be; a check on startup and shutdown may suffice.
2. Should `bzk rebuild` verify against a checksum of the previous graph, or only against the regression test? Checksums would catch silent drift; they would also fire on every legitimate schema change.
3. Is there a defensible way to back up embargoed data that does not depend on the user remembering to do it?
