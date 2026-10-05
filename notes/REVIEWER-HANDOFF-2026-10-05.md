# REVIEWER HANDOFF — 2026-10-05

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-04.md` as the starting
point. That file stays as the record of the day before.

**What is not restated here.** Items the earlier handoffs carry, which this session did not touch,
are not repeated. Read this file's §6 and §7 alongside:
- 2026-10-04 §7, open items;
- 2026-10-03 §6, roadmap tensions;
- 2026-10-03 §7, open items;
- 2026-10-03 §8, caveats.

**Line references** are to `main` at `190e696` (`ONTOLOGY.md` v1.45). Re-verify them against the
current commit before citing.

**Dating.** The runs below took place after `d19a670`, in one working session spanning 2026-10-04
and 2026-10-05. They are dated by their position in the commit chain, not by clock date.

**§3 is the dated home for every number those runs produced.** Everything else points to its own
home.

---

## 1. Where things stand

| Item | State at `190e696` |
|---|---|
| `main` | `190e696`, pushed. Two commits since `d19a670` (§2) |
| `ONTOLOGY.md` | v1.45. *Last reviewed* is still 2026-08-31 |
| Checks | Targets per `CLAUDE.md` l.96: `pytest` **908 passed, 14 skipped**; `mypy bzk tests` clean over 117 files; `ruff check bzk tests` and `ruff format --check bzk tests` clean |
| Untracked | On bzk's Mac: `notes/prompts/22-walk-two-route-independence.md`. **Deferred by bzk's decision** (§4 item 4) |
| ADRs | 36 files, no change: 24 Accepted, 9 Proposed, 3 Superseded |
| ADR-0036 | **Built:** D2, D3 (`190e696`) and D8 (`265beac`). **Nothing to build:** D1 (no new type) and D4 as revised (no role fields on `Contrast`). **Not built:** D5 (I22), D6 (concordance) and D7 (I4 widened) |
| Drift receipt | 3,579 sequences, 0 drifts, checked after `d19a670` (§3.2) |
| PXD055843 ingestion | Unchanged: blocked on the PI's imputation answer |

## 2. What this session did

| Commit | What |
|---|---|
| `0610252` | Prompt 28 landed. The hash check passed on the first write. One retry was needed after a `git rev-parse` error aborted the chain before anything was committed |
| `190e696` | ADR-0036 D2 and D3 built. Detail below |

**What `190e696` built:**
- **Identity.** `Sample.role` and `Sample.bait` are identifying, appended after `organism_taxid`.
  Their absence is `determined`: `role` by `Experiment.modality`, `bait` by `role`.
- **New fields.** `Sample.antibody` is non-identifying, and `'ip_ms'` is added to the modality
  comment.
- **Enforcement.** D2/D3 are enforced at the only `Sample` minting site,
  `bzk/curation/loader.py` `_check_sample_roles` (l.315, called at l.437), as R1–R7. All eight
  mutations, R1–R7 and the call site, were made to fail with bytecode disabled from the start.
- **Records.** All four committed records still load, with `role`, `bait` and `antibody` all
  `None`.
- **The pin.** `tests/fixtures/pxd018299_curation_ids.json` `samples` were regenerated, with the
  move explained in the commit message, as the fixture's note demands.

**Prompt 28's findings, all confirmed at §0:**
- **F-a.** `antibody` gets no §3 row, because §3 classifies identifying fields only.
- **F-b.** No `determined` row had its condition checked before this build. R2–R5 are the first
  checks of that kind.
- **F-c.** Two readings beyond D2's text, accepted by bzk: R6 (`bait` is a `uniprot:` CURIE) and
  R7 (`antibody` is NULL unless `role = 'ip'`).
- **F-d.** Unknown keys inside `mapping` entries are dropped silently.

## 3. Dated home — runs after `d19a670`

### 3.1 The 2026-10-04 §3.3 measurement (OAS2 exception; arm split)

**Run** on bzk's Mac, read-only, against the graph written at `265beac`. The instrument was
extracted from the committed handoff `d19a670` and run unchanged. **The pre-registration was public
before the run.**

**Measured lines:**

```
A uniprot:P29728#sv3#K100#unimod:121 | log2FC 4.65 | adj p 0.00039 | KO+IFN imputed 0 of 3 | WT+IFN imputed 3 of 3
A uniprot:P29728#sv3#K388#unimod:121 | log2FC 3.23 | adj p 0.0084 | KO+IFN imputed 0 of 3 | WT+IFN imputed 3 of 3
A uniprot:P29728#sv3#K425#unimod:121 | log2FC 5.74 | adj p 0.021 | KO+IFN imputed 0 of 3 | WT+IFN imputed 1 of 3
A uniprot:P29728#sv3#K470#unimod:121 | log2FC 4.38 | adj p 0.0059 | KO+IFN imputed 0 of 3 | WT+IFN imputed 3 of 3
B tested 1362 | WT+IFN entire 947 | KO+IFN entire 130 | neither 285
B WT+IFN entire and significant up 468 of 947
B significant down 59 | KO+IFN entire 45 | WT+IFN entire 0
```

**Against the pre-registration:**

| # | Kind | Measured | Verdict |
|---|---|---|---|
| A1 | identity | One OAS2 site, K425, has WT+IFN imputed < 3 | held |
| A2 | reasoned, low confidence | K425 | held |
| A3 | reasoned | WT+IFN **1 of 3 imputed (two measured)**; predicted 2 of 3 | **refuted.** "Mean shrinkage" was the wrong model: K425 has two measured WT values *and* OAS2's largest fold change |
| A4 | reasoned | KO+IFN 0 of 3 imputed | held |
| B1 | identity | 947 + 130 = 1,077; neither **285**; 468 | held. The 285 that 2026-10-04 §3.2 derived is now measured |
| B2 | reasoned | WT+IFN entire 947 > KO+IFN entire 130 (7.3 : 1) | held |
| B3 | reasoned | Significant down 59: KO+IFN entire 45 (76.3%); WT+IFN entire 0 | held |

**Derived rates.** These are computed from the measured lines, not measured themselves:

| Population | Rows | Sig up | Sig down |
|---|---|---|---|
| WT+IFN entirely imputed | 947 | 468 (49.4%) | 0 |
| KO+IFN entirely imputed | 130 | 0 | 45 (34.6%) |
| Neither arm entire | 285 | 48 (16.8%) | 14 (4.9%) |
| **All tested** | **1,362** | **516** | **59** |

**What the run establishes:**
- **513 of 575 significant calls (89.2%) rest on one arm being entirely generated.** Only 62
  (10.8%) compare two measured arms.
- **Among rows where the direction is possible, an entire-arm row is far more likely to be called
  significant:**
  - up: 2.9× (49.4% against 16.8%);
  - down: 7.1× (34.6% against 4.9%).
- **The KO-only/WT-only asymmetry** (947 against 130; 516 up against 59 down) fits USP18 loss
  raising conjugation. **But a GlyGly remnant does not distinguish ISG15 from ubiquitin**, so this
  is a modification-level asymmetry, not one specific to ISGylation.
- **R1, restated precisely.** Of the 21 significant-up sites behind the 12 recovered targets, 20
  have WT+IFN entirely generated. The exception is OAS2 K425, with **two** of three WT+IFN values
  measured.

**The K425 observation, on one gene only.** K425 is the only target site with a measured WT+IFN
comparison. It has OAS2's largest effect (log2FC 5.74), yet OAS2's weakest adjusted p:
- K425: 0.021;
- the three sites with a fully generated WT arm: 0.00039, 0.0059 and 0.0084.

The likely mechanism is the imputation width. A generated arm is drawn at 0.3 SD, so it carries
almost no variance, while a measured arm carries real variance. **This is a hypothesis, not a
population result.** §6 step 4 holds its test.

**PI first.** Under 2026-10-03 §8, the 89.2% figure and the K425 observation go to the PI before
any demo.

### 3.2 Drift

**First run.** `python -m bzk.drift` reported 18 `DRIFT` lines, all of the form
`current svNone (0 aa); content_changed=False`.
- They cover 14 distinct entries. Q13098 failed together with three of its isoforms, and P13051
  with one.
- **No figures were pre-registered** (2026-10-04 §6 step 3).

**Diagnosis.** `resolve(..., refresh=True)` was run read-only on all 18.
- **Every one returned `ok`**, with a current sequence version equal to the archived one.
- **No entry was retired, and no version moved.**
- The reviewer's guess that any retirements would be among the five TrEMBL entries was wrong:
  there were none.

**Rerun.** `no sequence drift detected` over 3,579 sequences. This was predicted, and the receipt
now records 0 drifts.

**What it means.** The 18 lines were transient fetch failures. They cluster because an isoform
lookup goes through its canonical entry.

**The instrument defect.** `bzk/drift.py` `drift_check` (l.166–200) keeps `fresh.sequence` (l.186)
and `fresh.sequence_version` (l.188), and discards `Resolution.status`. So a failed fetch prints as
drift and is counted as checked.
- **It cannot hide a failure.** A failed fetch's version is `None`, which never equals the archived
  version, so the defect produces false positives only.
- That makes the clean rerun a true clean result.
- §7 carries the fix.

### 3.3 The `190e696` run (D2/D3) on bzk's Mac

**Pre-registered** in `notes/prompts/28-d2-d3-sample-role-bait-ip-ms.md` §5, committed at
`0610252` before either step ran.

**Step A** ran against the `265beac` graph, after `0610252` was pulled and before the build was
pulled. It photographed every node id to `~/.bzk-omics/ids-before-adr0036-d2.json`:

```
BEFORE {'Gene': 1600, 'Protein': 9054, 'ProteinSequence': 1708, 'ModificationSite': 3744, 'Modifier': 3, 'Project': 3, 'Experiment': 4, 'Sample': 54, 'Dataset': 4, 'SiteObservation': 4195, 'ProteinObservation': 4768, 'Contrast': 5, 'DifferentialResult': 1362, 'Analysis': 8, 'ModifierAssignment': 4195, 'Imputation': 1}
```

Two of these counts are by design, not anomalies:
- `Project` is 3 because the two PXD026748 records share one (ADR-0035).
- `Dataset` is 4 although only 3 deposits are ingested: the PXD055843 record mints its `Dataset`
  when it replays.

**Step B** ran after `190e696` was pulled: rebuild, then differential, then `git status`, then the
`AFTER` instrument.

| # | Predicted | Measured | Verdict |
|---|---|---|---|
| MA | `Sample` 54, `Contrast` 5, `DifferentialResult` 1,362 | as predicted | held |
| M0 | Rebuild figures unchanged from 2026-10-04 §3.1 M0 | 58 tables; 18/40, 18/40, 16/38, 23/57; 32,793 / 31,349; 4,195 / 4,768; 48 refused; INCOMPLETE. The drift line now reads `0 day(s) ago over 3,579 sequence(s), 0 drift(s)` | held |
| M1 | `[4b]` unchanged | 2,341 → 2,298 → 2,056 → 2,029 → 1,362; 3,997 of 8,172; 516; 12 of 14; 4,090 / 5,450 | held |
| MS | `git status` shows only prompt 22 | `?? notes/prompts/22-walk-two-route-independence.md` | held. This corrects 2026-10-04 §3.1 M1's wording defect |
| MB | `Sample` gone 54 / new 54; every other label 0 / 0; pinned 12 of 12 | exactly that across all 16 labels; pinned 12 of 12 | held |

**What it establishes.**
- **ADR-0036 V2 is confirmed at graph scale.** No node anchors on `Sample`: all **30,654** other
  nodes in the graph (Step A's counts, less the 54 `Sample`s) kept their ids through an identity
  change to `Sample`.
- **The D8 counts carry over unchanged**, because no `DifferentialResult` moved.
- **The container-side check agrees.** I1, the loader-level per-record comparison, gave
  12/12/12/18 `Sample` and 0 elsewhere. It was measured both by Claude Code and by the reviewer from
  an independent pre-build snapshot.

## 4. Corrections to the 2026-10-04 handoff

1. **§3.2 derived "285" rows with no arm entirely imputed.** §3.1 B1 has now measured it, at 285.
2. **§3.2 described K425 as "one OAS2 site has a measured WT+IFN value".** It has **two** of three
   measured (§3.1 A3).
3. **§3.1 M1's "`git status` empty" was a wording defect.** Prompt 28's MS states the
   expectation correctly, and it held.
4. **§6 step 4 said prompt 22 "does not stay untracked a fourth time".** bzk has decided it
   belongs to a separate project (the walk / claim-durability line) and will be landed later. This
   is a recorded deferral, not a silent carry.

**One correction made in reports, not in a handoff.** During prompt 28's §0, both Claude Code and
the reviewer said every PXD018299 `mapping` entry carries a `note` key. Each had printed the
**union** of keys across entries. In fact **one** entry does: `Ratio mod/base KO_1_181212063719`.
The test at `tests/test_curation_loader.py` l.534 already pins the behaviour. F-d's substance is
unchanged.

## 5. How this session ran

**The four-stage loop held for both builds.**
- The reviewer rehearsed each prompt in a scratch clone.
- Claude Code executed.
- The reviewer verified from an independent full clone.
- Mac runs were pre-registered in committed files before they ran.

**The checker stage is not recorded for prompt 28 either.**

**Hash-landing is now routine.** Every prompt and handoff since prompt 26 shipped with a filename,
sha256, line count and landing message. This file does too.

**The id photograph is worth keeping for every identity change.** Snapshot all node ids before the
build is pulled, then compare per label after the rebuild. That turns "nothing else moved" from a
reading of the anchor table into a measurement. It needs bzk to run Step A **before** pulling the
build, so a prompt that uses it must say so up front.

**Two process lessons from `190e696`'s mutation runs:**
- **Restore in `finally`.** A harness crash left one mutation applied in the file. It was caught
  and restored, with byte-identity confirmed by `cmp`, and the harness now always restores.
- **Count per entry, not per union.** The `note` miscount (§4) came from printing a union where a
  per-entry count was needed.

## 6. Next, in this order

1. **Land this file** as its own commit (`HANDOFF: …`).
2. **Prompt 29: ADR-0036 D5 (I22, arm-role consistency at the producer) and D7 (I4 widened to IP-vs-IP results).**
   - Per 2026-10-03 §5, I22 is enforced at `differential.py` and `perseus.py`.
   - **Neither has an `ip_ms` input today, so the test cases are constructed, and the record must
     say so.**
   - Nothing should move. Rehearse, and pre-register 0 ids moved and identical figures.
3. **Then IP curation and ingestion**, as 2026-10-03 §5 sets out:
   - PXD018299's interactome needs a protein-grain internal differential writer, taking its
     `Contrast` pre-keyed.
   - PXD055843's S3 waits on the PI and on ADR-0032.
   - Before the concordance writer: the list in 2026-10-03 §5.
4. **Not scheduled: the K425 hypothesis.**
   - **Claim:** among the 516 significant-up results, adjusted p is systematically smaller for
     WT-entire rows than for measured-WT rows at matched log2FC.
   - **Direction wanted:** none yet, so per bzk's own rule it is not yet a diligence question.
   - **Before it runs:** state what a "match" on log2FC means, and register the instrument in a
     committed file.
   - **The 2:1 imbalance** (468 against 48) needs a method chosen in advance, not after the
     numbers are seen.
5. **Not scheduled, but needed before any demo:** the PI conversation (§3.1).

## 7. Open items — what changed since 2026-10-04 §7

**New:**

- **The drift checker reports failed fetches as drift** (§3.2). The fix:
  - carry `status` and `entry_type` into `Drift`;
  - report a non-`ok` lookup as *unchecked*, not as drift;
  - record the unchecked count in the receipt;
  - consider one retry.
- **An unguarded mirror.** `_SAMPLE_ROLES` and `_IP_MODALITY` (`loader.py` l.311–312) copy the
  ONTOLOGY `Sample` DDL comment, and no test checks the two agree.
- **D2/D3 are enforced only in the loader.** That is sufficient while the loader is the only
  `Sample` minter. A second producer would bypass it, so consider an invariant-level check before
  any IP adapter exists.
- **R6 checks the `uniprot:` prefix only**, not the accession's form.
- **F-b, generalised.** No pre-existing `determined` row has its condition enforced: `Sample.cell_line`,
  `model_system` and `timepoint_h`, and the `Analysis` and `Imputation` rows. **I15's seed check**
  (`invariants.py` l.546) **is one-directional**: stochastic implies a seed, but nothing refuses a
  seed on a deterministic method.
- **F-d. Mapping-entry keys are not checked for unknowns.** The live instance is the one
  PXD018299 `note`. A strict fix would refuse the anchor record, so that prompt must decide whether
  `note` becomes a recognised annotation key or moves out of the entry.

**Changed:**

- **The tautology floor is still stale.** It is now at `tests/test_tautology_sweep.py` l.1939,
  asserting ≥ 49 modules and ≥ 1,693 asserts. `190e696` measures 54 and 2,086.
- **Prompt 22 is deferred by decision** (§4 item 4).

**Closed:**

- 2026-10-04 §6 steps 2 (§3.1), 3 (§3.2) and 5 (§3.3).
- The overdue drift check: 0 drifts over 3,579.

Everything else in 2026-10-04 §7 and 2026-10-03 §6–§8 stands unchanged.
