# OPERATIONS.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.13 |
| Last reviewed | 2026-08-09 |
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
| `raw/` source files | **Only if the deposit is unchanged** — re-fetchable from PRIDE, not reproducible | High for embargoed data, **high** otherwise |
| `cache/uniprot/` | **No** — captured external state, see below | **High.** An I9 input since 2026-08-07 |
| `graph.kuzu/` | Yes, from the four I9 inputs | Low |
| `quant.duckdb` | Yes — **value-for-value, established by running 2026-08-08**, not byte-for-byte | Low |

**What "regenerable" means for `quant.duckdb`, measured rather than assumed (2026-08-08).** Two
rebuilds produce **different file digests and identical row digests**, and deleting the file and
rebuilding reproduces its content exactly. Byte equality is the wrong question to ask of a DuckDB
file — it carries metadata and free-space layout that a byte comparison would compare as well — so
the claim this table makes is over content, and `bzk/quant/store.py::digest_rows` is what checks it.
Established by running because the row two above is the correction of a regenerability
classification that was asserted and wrong.

**The asymmetry is the point.** A few megabytes of JSON are irreplaceable; tens of gigabytes of graph and matrices are a compute cost. Backing up the small irreplaceable set frequently is both cheaper and more effective than snapshotting everything occasionally.

**Corrected 2026-08-07: `cache/uniprot/` was listed as *"Yes, slowly"* and low priority. Both were wrong, and the word *cache* is what made them plausible.** It is not a performance optimisation — it is the pinned sequence content every `ModificationSite` position is meaningful against, fetched from an authority that mutates and that may not serve a superseded version at all. `ONTOLOGY.md` §8 I9 now names it as a fourth input alongside `raw/`, the curation export and the DDL, and §11 Q6 records why: it is the same class of thing as `raw/` — captured external state, addressed so a new version is a new entry. Neither is regenerable; both are archives.

**Narrowed 2026-08-09, third home of one sentence.** *"Immutable once captured, addressed so a new version is a new entry"* is true of `cache/uniprot/seq/` — the sequence files and the pins — and was never true of `cache/uniprot/entry/`, which has no version in its path. §3.1 settles that split; this row's **backup priority is unchanged by it**, because the priority rests on §11 Q6's second cost, that losing the archive destroys the ability to detect drift at all, and the split does nothing about loss.

**What losing it costs.** No id changes, because `ModificationSite` keys on the sequence *version* and not on its content, so nothing looks broken. What happens instead is that a rebuild re-resolves against today's UniProt, the residue check refuses every site whose sequence has since been amended, and the graph regenerates **smaller** — visible only as a changed refusal count that reads like data drift. And because the drift check works by comparing the stored copy against a fresh fetch, with no stored copy the fresh fetch becomes its own reference: **drift stops being detectable, including retrospectively.** The cache is the sole record of what the graph's positions were validated against. Losing it is silent in both directions, which is precisely why it cannot be low priority.

At PXD018299's scale the archive is ~1,029 sequence files plus their entry metadata — **8.3 MB measured**, against 19 MB for the whole of `raw/` (of which the ingested site table is 2.7 MB) — so this is a correction of classification, not a meaningful new storage burden.

---

## 2. Backup policy

**Human-authored content — continuous.** Curation records, analysis records and manual inferences serialise to JSON under `data/curation/` and live in the git repository. They are versioned, diffable, and survive independently of any machine.

Each record identifies its input file by a `content_hash` — the SHA-256 of the raw table — alongside the bare filename it carries today. The filename is not an identity: two deposits, or a re-download after a deposit is revised, can share a name and differ in content. I9 replay reconstructs the graph from `raw/` plus these records, so the hash is what lets a rebuild confirm it is replaying against the same bytes the curation was written for, rather than a file that merely matches by name. Back-filled 2026-08-07: all three PXD018299 records now cite `sha256:a4a503e39581334c3553d3631456ad8aca22e193ba928810f6d46fde15622009`, produced by `bzk/sources/pride.py` through the content-addressed store. The hash a record cites and the hash a rebuild recomputes come from one module (`bzk/provenance/raw_store.py`), so they cannot disagree.

This requires a nightly export of manual assertions from the graph to JSON, since the graph itself is not committed. Without it, an assignment made in the UI exists only inside `graph.kuzu/` and violates I9.

**Retractions travel as their own records.** `retracted_at` is deliberately outside evidence-node identity (ADR-0020), so a rebuild reconstructs the node but not the fact that it was retracted — and nothing in `raw/` supplies that field. I6 requires a retraction to propagate to every downstream figure and report, so the curation export carries a **retraction record** for each retracted assertion: the retracted node's `id`, its `retracted_at`, and a `reason`. Replay reconstructs the nodes, then applies these records — setting `retracted_at` on the named node and propagating the retraction. Omit them and every retraction is silently lost on the next rebuild: the append-only model survives in the live graph but not across regeneration, which is I6 failing exactly where I9 is supposed to make it cheap.

**Embargoed source data — mirrored, never committed.** Unpublished collaborator data cannot go in a public repository (I18) and cannot be re-downloaded from PRIDE. It needs a second copy on separate physical media, and that is a manual responsibility with no software answer.

**Everything else — rely on rebuild.** A weekly `bzk rebuild` verifies that the derived state genuinely is derivable. A rebuild that fails is a more useful alarm than a backup that silently stopped running.

---

## 3. Cache policy

The UniProt cache is **two tiers, and only one of them is content-addressed and immutable.** A *sequence* is keyed on the full accession — isoform suffix included — and its sequence version, `seq/{accession}#sv{n}.txt`, so a new version is a new file rather than an overwrite (I2). An *entry* is keyed on the bare canonical accession, `entry/{canonical}.json`, with no version in the path, so a re-fetch replaces it. Over a multi-year project both grow without bound.

**Corrected 2026-08-09: this section said the property held of "the cache", describing the sequence tier's key while doing so.** `ONTOLOGY.md` §8 I9 carried the same overstatement in the same words, and both were written after `bzk/resolve/uniprot.py`'s docstring had already called the entry tier *"a mutable snapshot of the current UniProt entry"* — the code was accurate and the two documents were not. It matters because the entry tier is where `sequence_version` is read from, and that value is embedded in every `ModificationSite` key: refresh the entry tier and a rebuild re-keys sites against today's UniProt. **Measured 2026-08-09, the exposure is latent and not realised** — all 2,261 entry files still carry their original ingestion `fetched_at`, and `bzk drift` fetches into a throwaway directory rather than through the live cache, which is the only reason a weekly drift run has not been silently re-capturing an I9 input all along. Nothing enforces that; it is one `refresh=True` against the default cache directory away from happening.

### 3.1 The entry tier's key — decided 2026-08-09

**The entry file keeps its non-versioned key and is *declared* a mutable snapshot. Everything identity-bearing moves out of it.** Three shapes were available and the archive chose between them.

**Rejected: version the entry key.** It exchanges a silent overwrite for an ambiguous read. With two captures on disk, nothing says which one a rebuild must use — and the two inputs that avoid this avoid it for reasons the entry tier cannot borrow: `raw/` is named by the `content_hash` its curation record cites (§2), and a sequence file is named by the version the site key already carries. The entry tier is read *before* any id exists, so the graph cannot point at the right capture. Resolving that needs a per-accession manifest, and the record that might have served — `data/curation/resolution_PXD018299.json` — is a 642-byte summary (`n_sampled: 20`, `sequence_versions: [1,2,3,4]`), not a per-accession pin. Every candidate version component fails independently as well: `sequence_version` is circular, since the fetch is what reveals it; a content digest changes on every re-fetch, because `fetched_at` sits inside the payload; and `fetched_at` itself is settled below rather than promoted into a key.

**Adopted: split the tier by whether a field bears on identity.**

| Field | Bears on identity? | Home |
|---|---|---|
| `sequence_version` | **Yes** — embedded in every `ModificationSite` and `ProteinSequence` id | pin |
| `sequence` | **Yes**, indirectly — the residue check decides whether a site exists at all | sequence file, and the pin names its version |
| `entry_type` / `reviewed` | **Yes**, indirectly — steers I17's promotion, so it decides *which protein* a site is keyed against | pin |
| `gene`, `hgnc_id`, `last_seq_update`, `fetched_at` | No | snapshot |

**Narrowed 2026-08-09, when `Gene` was minted and `Gene.id` turned out to read from the snapshot.**
This table's column said *"bears on identity"* and the surrounding text said *"nothing an id depends
on is read from the mutable tier"* — a description of what happened to be in the pin, not a
principle, and false the moment a primary key was derived from `hgnc_id`. The principle is:

> **A snapshot field may not reach the composition of a composed key, directly or by selection.**

That is `ONTOLOGY.md` §4's own division of reference nodes into *composed* and *authority-assigned*,
and it sorts every field in the table above without a special case. `sequence_version` is a
**component** of `uniprot:{acc}#sv{n}` and of every `ModificationSite` built on it. `reviewed`
**selects** which protein a site keys against (I17), so it reaches composition indirectly. `gene`,
`last_seq_update` and `hgnc_id` reach neither: `Gene.id` is authority-assigned — §3's identity table
gives its identifying fields as `—`, and §4's shape is *"the id **is** the external identifier,
CURIE-prefixed; nothing local composes it"*, which makes prefixing explicitly not composition.

**What the narrowing costs, and why it is not the failure the pin prevents.** A changed
cross-reference produces a different `Gene` node and a different `ENCODES` edge between rebuilds.
That is a real difference and it is accepted, because it is a different failure in kind: a pinned
field moving **re-keys an existing node and every evidence digest anchored on it**, silently and
without changing any count, whereas a `Gene` change moves no id, cascades into no digest — `Gene`
appears in no `schema.IDENTITY` anchor list, asserted in `tests/test_keys.py` — and changes a node
count, which is visible. **Moving `hgnc_id` into the pin was considered and is wrong, not merely
harder:** 2,183 pins predate the field, and filling one means rewriting a write-once record, which
is the negation of the property rather than a cost. It does not reopen the backfill window either —
that window was about preserving an *original* capture, and `hgnc_id` was never captured at
ingestion, so there is nothing earlier to lose. Independently, the pin is keyed `#sv{n}`, and an
HGNC id has no relation to a sequence version.

The pin is `cache/uniprot/seq/{canonical}#sv{n}.meta.json`, written **once and never overwritten**, the same discipline `_seq_cache_put` already applies to the sequence beside it. It sits in the sequence tier because that is the tier the version keys, and it makes the tier self-describing: the version can be recovered by globbing `#sv*.meta.json` without knowing it in advance, which is what breaks the circularity `bzk/resolve/uniprot.py` used to record as the reason the tiers could not merge.

**Why this makes a mutable snapshot safe, rather than merely calling it one.** `ONTOLOGY.md` §11 Q6 sets the bar: a re-resolve refuses sites keyed against amended sequences, and the only visible signal is a changed refusal count that reads as data drift rather than as data loss. That mechanism runs entirely through `sequence` and `sequence_version` — and both are now read from the pin, so the path Q6 describes is removed rather than restated. Measured before deciding: `entry.sequence` is byte-identical to `seq/{acc}#sv{n}.txt` on **all 2,014** entries that have both and differs on none, so the snapshot's copy was already a duplicate of an immutable file; and the version is recoverable from the immutable tier for **2,183 of 2,261** entries, agreeing in every case and disagreeing in none, the remaining **78** being exactly the `Inactive` entries, which carry no version and key nothing. What was *not* already covered is `reviewed` — nothing immutable recorded it, its effect on identity is one step removed through I17, and it is the reason the pin exists rather than a note.

**Existing files.** The 2,261 snapshots are left untouched; the pin is backfilled from them, which is correct **only because they are still the original capture** — every one carries its ingestion `fetched_at` and no code path has rewritten one. That window is what makes the backfill sound, and it closes the first time anything re-fetches.

**`fetched_at` is a fetch clock.** It is written in `_fetch_entry` and nowhere else, never updated on a cache hit, and read by nothing in `bzk/` or `tests/`. As a record of *when this file was written* it is exactly right, and this section uses it for that and nothing else. The **Retention** rule below spends it as an *access* clock, which it is not and cannot become without a write on every hit; that clause is unimplementable as written and is corrected there rather than here.

**Retention:** keep entries **fetched** within 90 days, plus every entry referenced by a live `ModificationSite` regardless of age. Evict the remainder.

**Corrected 2026-08-09: this read *"accessed within 90 days"* and no clock in the code measures access.** `fetched_at` is written on fetch and never on a cache hit (§3.1), so the rule as written could not be implemented against anything that exists, and `bzk/resolve/uniprot.py` said it carried `fetched_at` *"so the 90-day retention policy has something to expire against"* while the two meant different clocks. An access clock would need a write on every read — turning a read-mostly archive into a write-mostly one for a policy whose second clause already protects everything the graph depends on. The rule is narrowed to the clock that exists rather than the code changed to serve the rule. **Pins are never evicted by age**: they are the immutable half and are governed by the second clause alone.

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

**Two commands since 2026-08-07, with different cadences.** `bzk rebuild` reconstructs and is cheap (**83.9–100.6 s on PXD018299, n = 3, measured 2026-08-09**, and dominated by the write path rather than by anything irreducible); run it after every schema change, as above. **The figure was 119.9 s and that was one draw** — corrected here rather than noted, by the turn whose own opening rebuild (96.1 s, on the unchanged tree) contradicted it. It is a range with *n* stated because replacing one draw with another is what the 62.2 s figure cost (`ROADMAP.md` § *Measured findings*); the spread across three runs is 16.7 s, so any comparison finer than that is not available from this instrument. `bzk drift` validates the sequence archive against UniProt and is expensive (**2,069.8 s measured** for 2,845 sequences on 2026-08-08, and 973.7 s for 1,029 on 2026-08-07 — call it **35 minutes** at the current archive size, and note it scales with the archive, not with the deposit); run it **weekly**. Both runs so far reported zero drift and **neither number means anything about the archive.** The first compared a fetch against a fetch under two hours older; the second ran at 05:03 UTC over an archive whose oldest member was written 13 hours earlier and whose 1,816 newest members were written the same day, so it too compared fetches against fetches of the same UniProt release. They are evidence the check runs, not evidence the sequences are stable. **The first meaningful drift run is one over an archive that has aged** — weeks at least, since UniProt releases roughly monthly — and until then no conclusion about exposure may be drawn from a clean result. Running it again today would produce a third clean result and would not move that sentence. They were one command until the archive grew past a thousand sequences and the combined cost reached 17.6 minutes — at which point the honest thing and the convenient thing diverged, and the convenient thing won: the session that introduced the cost changed the schema twice and ran a full rebuild once, at the end.

**Staleness threshold: 7 days.** A receipt older than that is reported as `STALE` by every `bzk rebuild`. This document owns the number because this section owns cadence; `bzk/drift.py`'s `STALE_AFTER_DAYS` mirrors it and `tests/test_drift.py` asserts the two agree, the same way `schema.py` is guarded against `ONTOLOGY.md` §4–§7. It was a constant in the code citing this section as its owner, which is a comment rather than an arrangement — the number lived in one place and the authority in another.

`bzk drift` leaves a receipt in `cache/uniprot/.drift`, and every `bzk rebuild` reports how stale it is. **Rebuild never refuses on staleness** — it is the disaster-recovery path, and a network check standing in front of recovery would be worse than a stale check. The obligation that gives staleness teeth belongs at the export boundary with I18 and is recorded in `HANDOFF.md` §8; until it exists, the receipt is a report and not a control.

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
