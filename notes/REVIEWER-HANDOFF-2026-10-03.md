# REVIEWER HANDOFF — 2026-10-03

**Public version. Supersedes `notes/REVIEWER-HANDOFF-2026-10-02.md` as the starting point.** That
file stays as the record of the day before. Work on unpublished data is recorded locally and is
not described here.

**Line references are to `main` at `767e6e4` (ONTOLOGY.md v1.43). Re-verify them against the
current commit before citing.**

**§3 of this file is the dated home for the `767e6e4` run's numbers.** No other file records them.
Everything else here points to its own home.

---

## 1. Where things stand

| Item | State at `767e6e4` |
|---|---|
| `main` | `767e6e4`, pushed. Eleven commits since `a74cf18` (see §2) |
| ONTOLOGY.md | v1.43. Last reviewed 2026-08-31, so the header predates today's amendments |
| Suite | 881 passed, 14 skipped. `ruff check` and `ruff format --check` are clean |
| Untracked | `notes/prompts/22-walk-two-route-independence.md`, carried unchanged (§7.8) |
| ADRs | 36 files (0001–0037; 0018 reserved, unwritten): 24 Accepted, 9 Proposed, 3 Superseded (`tests/test_decision_index.py` pins) |
| Option 1 (IP-MS) | **All prerequisites built.** ADR-0036's own amendments are the next step (§5) |
| PXD055843 ingestion | **Still blocked** on the PI's imputation answer, which now covers S1_TP **and** S3 |

## 2. What this session did

**Commits, in order.** Each commit's message carries its own detail.

| Commit | What |
|---|---|
| `2714c76` | Prompt 25: land ADR-0036 |
| `ed38432` | ADR-0036 landed `Proposed`, with landing verification V1–V10 |
| `4825cd5` | ADR-0036 review: R1–R5. D4 revised; D2 revised so `role` is determined by `modality` |
| `2aecd01` | ADR-0036 **Accepted** |
| `b2326e4` | ADR-0029 second review. Finding E: two minting paths, two `Contrast` nodes for one comparison |
| `f7f931c` | ADR-0029 **Accepted**, with E's consequence corrected before acceptance |
| `856c3d1` | ADR-0037 `Proposed`: I21 generalised. Dry-run instrument and its non-vacuity tests |
| `38d456e` | ADR-0037 pre-registration result from bzk's Mac, and its review |
| `0966301` | ADR-0037 **Accepted**, with the D3/P3 corrections made before acceptance |
| `819fe7d` | Generalised I21 enforced. ONTOLOGY v1.42; §11 Q15 opened |
| `767e6e4` | The `Contrast` build: ADR-0029 items 1–3 and 6; ADR-0027 implied changes 1–5. ONTOLOGY v1.43 |

### Decisions now in force

- **ADR-0036 — IP-MS as role-tagged observations.**
  - D1: no new observation type.
  - D2: `Sample.role` and `bait`, identifying. `role` is NULL unless the modality is `ip_ms`.
  - D3: an `ip_ms` modality.
  - D4: IP contrasts are separated by ADR-0027's anchor.
  - D5: I22, arm-role consistency, checked at the producer.
  - D6: concordance is defined on an IP-vs-IP contrast, paired on `external_accession`.
  - D7: I4 is widened to IP-vs-IP results.
  - D8: per-arm imputation counts, and the whole-arm flag.
  - **Built: nothing of D1–D8 yet.**
- **ADR-0029, as revised by finding E.** The loader is the only place a `Contrast` is minted. Producers receive the node pre-keyed. **Built.**
- **ADR-0037 — I21 over every anchored label.** Edge-triggered. Orientation is read from the declared pair. Multi-valued anchors are refused. **Built and enforced.**
- **ADR-0027's anchor.** `CONTRAST_IN_EXPERIMENT`, with the `CONTRAST_ANCHOR` guard. **Built.**

## 3. Baseline — the `767e6e4` run on bzk's Mac, 2026-10-03 (dated home)

Two commands were run: `python -m bzk.rebuild`, then `python -m bzk.sources.pxd018299_differential`.

**Every figure below was predicted before the run and matched exactly.** The prediction table is
in the reviewer chat, not in a file. That is a gap in the record: any rerun should pre-register
against this section instead.

- **Rebuild.**
  - 58 tables.
  - Curation replay lines: PXD018299 18/40, PXD026748 18/40, shotgun 16/38, PXD055843 23/57.
  - Totals: 32,793 node and 31,349 edge statements; 4,195 site observations; 4,768 protein
    observations; 48 refusals.
  - Exit is **INCOMPLETE**: S1_TP has no adapter in the replay, which is expected.
- **Differential.**
  - 2,341 rows → 2,298 → 2,056 → 2,029 ingested → **1,362 tested**.
  - 3,997 of 8,172 values imputed (48.9%).
  - **516 significant up** (adj p < 0.05, log2FC > 1).
  - **12 of 14 recovered.** `PSMB9` was tested and not recovered; `OAS1` is absent from the tested
    population.
  - 4,090 node / 5,450 edge statements.
- **Anchor.** All 1,362 results sit on `bzk:8f9a06344675831a26dd59b2bf8c4393`, `'USP18-/- + IFN'` vs
  `'WT + IFN'`, anchored on the PXD018299 `Experiment`. These are ADR-0029 finding D's predicted ids.
- **Guards.** No `I21` and no `CONTRAST_ANCHOR` refusal. The targets fixture was rewritten
  byte-identical, so `git status` was clean.
- **What the 14 are.** They are the paper's most annotated exemplars, not its significant set. The
  12 of 14 is a tripwire for whether the pipeline moved, not a recall estimate. The population
  claims are §7.5's queued measurements.

## 4. How this session ran — read before the next one

**The reviewer chat executed and committed, and Claude Code did not.** The cloud container cannot
reach the raw store, and the reviewer container could build and test everything except a rebuild.
That cost the loop its independence in two places:

- **ADR-0036, ADR-0029 (second review) and ADR-0037** were each drafted, verified and reviewed by
  one reviewer. **bzk's acceptance was the only independent step.** Each record says so in its
  Reviewed row.
- **Commits carry `reviewer <reviewer@local>` as author and committer.** They reached GitHub by
  `git am` with that committer identity and `--committer-date-is-author-date`, which reproduces the
  exact hashes the records cite. Do not rewrite these commits: rewriting moves the hashes the
  records cite.

**Prompt 25 contained one prompt defect.** It excluded `tests/`, yet landing any ADR moves
`test_decision_index.py`'s pins. This is recorded in ADR-0036's *Landing verification*.

**Two of the reviewer's claims were corrected before acceptance**:
- ADR-0029 E: the result id moves once *only* in the order that keeps it to one move;
- ADR-0037 D3/P3: the unstaged-counterpart refusal is subsumed by structural validation, so P3
  passed vacuously.

Both corrections are on the record, in-place while the ADR was still Proposed.

**Recommended for the next session.** Return to the four-stage loop for code: reviewer writes the
prompt, the checker audits it, Claude Code executes, and the reviewer verifies from an independent
clone. Mac-only runs (rebuild, differential) go to bzk as commands, with their predictions
registered first.

## 5. Next: ADR-0036's amendments, before any IP code

**Settled ground, not to be reopened in passing:** ADR-0036 as accepted at `2aecd01` and the
`Contrast` build at `767e6e4`. Proposed order, **one prompt per step**:

1. **D8 first: imputation counted on the result (G1, G2).**
   - **What it changes.**
     - Four non-identifying counts on `DifferentialResult`. Their absence is determined by
       `Analysis.parameters_observed`.
     - The *substantially imputed* rule gains the whole-arm clause (b).
     - Both homes are amended: ONTOLOGY l.854 §6.5 and l.963 I15. These are the numbers at
       `767e6e4`; the 2026-10-02 handoff's l.853/l.962 moved by one when the new DDL line landed.
     - `SiteObservation.n_imputed` is retired. The `-w` grep finds six consumer files (ADR-0036
       V6).
     - `query/graph.py`'s `substantially_imputed` gets a denominator for the first time.
   - **Why first.**
     - It touches no identity, so no id moves.
     - It applies to the 1,362 results already in the graph.
     - It turns the queued §7.5 whole-arm measurement into a query.
   - **Pre-register:**
     - counts present on all 1,362;
     - the share flagged by rule (a) against rule (b);
     - how many of the 516 have an entirely imputed WT+IFN arm. Direction wanted: **low**.
       R1 predicts that the 12 recovered targets are all among them.
2. **D2 and D3: `Sample.role` and `bait`, and `modality = 'ip_ms'`.**
   - **All 54 `Sample` ids re-mint once.** That count was measured in memory; the anchor table
     was enumerated at `767e6e4`, and nothing anchors on `Sample` there.
   - The 12 pinned ids in `pxd018299_curation_ids.json` are regenerated **with the explanation
     its note demands**. The two `Contrast` ids and the 1,362 results do **not** move, because
     neither anchors on `Sample`.
   - Pre-register: 54 moved, 0 others moved, identical differential numbers.
3. **D5 (I22) and D7 (I4 widened).**
   - I22 is enforced at `differential.py` and `perseus.py`. Neither currently has an `ip_ms`
     input, so the cases are constructed, and the record must say so.
4. **Only then: IP curation and ingestion.**
   - **PXD018299's interactome** needs a protein-grain internal differential writer. That writer
     takes its `Contrast` pre-keyed, per ADR-0029 item 6.
   - **PXD055843's S3** waits on the PI (§7.3) and on ADR-0032.
5. **Before the concordance writer, not during:**
   - ADR-0036's open question: how an assignment cites its two results.
   - §11 Q15: the five anchor rels with no declared multiplicity, because the concordance
     `Analysis` likely `USED` two datasets.
   - The handoff-of-2026-10-02 §7.3 pre-registration: the four outcome rows, the *measured well*
     rule, and predictions including 110-of-312 and 7.

## 6. Roadmap tensions this work creates — decide, do not drift

- **`ROADMAP.md` l.12757–12758 lists *cross-modality concordance* under *"Not in these eight weeks"*.**
  Option 1's concordance is therefore v0.2 by the roadmap as written. Either the roadmap is
  amended (a visible commit), or §5 step 5 stays parked until v0.1's exits close.
- **The Weeks 3–4 exit's *cross-queried against a second dataset* half was blocked on §11 Q1**
  (l.12708). **That block is gone at `767e6e4`**: `Contrast` is anchored and minted once. The exit's
  other half (*a real user's results*) moved to v0.2 on 2026-08-11. Whether the cross-query half is
  now met needs measuring, not asserting.
- **Weeks 7–8 still records the volcano as untouched.** `DifferentialResult` is no longer empty, so
  the stated reason no longer holds.

## 7. Open items, carried — not in scope unless raised

1. **Decisions held `Proposed`**: 0006, 0008, 0009, 0010, 0012, 0025, 0030, 0032, 0034.
   - **ADR-0025 is an anomaly.** `ADJUSTED_BY` as an anchor is built and enforced by I21, yet the
     record has never completed a round-trip.
   - **ADR-0034** bears directly on D8's absence rule and on S1_TP/S3. ADR-0036 R3 and ADR-0037
     note that three records now rest on its "determiner names the anchor's field" rule.
   - **ADR-0032** governs how S3 is read.
2. **ONTOLOGY §11 open questions:**
   - Q2–Q5, Q9–Q11, Q13, Q14;
   - Q8, partly struck;
   - **Q15**, new today;
   - **Q7** (exactly-one `RESULT_FOR_*`) appears answered by I20 but is not struck. Verify and
     close, or say why it stays open.
3. **External dependencies:**
   - **The PI's imputation answer, for PXD055843 S1_TP and S3.**
     - It blocks PXD055843 ingestion, and is the reason the rebuild exits INCOMPLETE.
     - The paper's methods state that imputation ran after a three-of-three filter in at least one
       group. That settles *whether* it ran. What stays open is the seed and the per-cell mask
       (ADR-0036 *Found along the way*).
   - **PXD018299's matched proteome: 14 columns, keyed to no `Sample`** (ROADMAP l.68). Every IP
     result therefore enters `not_applied` (ADR-0036 D7). Keying needs author correspondence
     (ADR-0030).
4. **Carried defects:**
   - **`bzk/sources/protein_groups.py:117` mislabels SD3** as *"proteins up in WT +IFN"*. The file
     title is KO+IFN vs WT+IFN enrichment after ISG15 IAP-MS.
   - **`tests/test_tautology_sweep.py:1916`'s floor is stale.** It reads `modules >= 49 and asserts
     >= 1693`. Measured at `767e6e4`: **54 and 2,044**. Being `>=`, it cannot fail on a drop to the
     old floor.
5. **Science measurements queued:**
   - **The paper's 312 against SD3's 323 rows.** 323 − 12 contaminants = 311, not 312. Fix the
     candidate derivations before counting.
   - **The 516 against BJC SD1's full GlyGly hit list.** Direction wanted: high overlap.
   - **The whole-arm share of the 516**, after D8. Direction wanted: low.
   - **Test 1 instrument defect.** It saved rows for one pre-chosen variant. A rerun saves every
     passing variant.
   - **Why Munnur's analysis needed the halving** (π₀ = 0.493 reading).
   - **Separating Perseus's two FDR mechanisms** needs ≥ 3 replicates per group.
6. **Maintenance.** `python -m bzk.drift` is overdue. The last check was 19 days ago, over 3,013
   sequences; the set is now 3,579.
7. **Memory and documents drift:**
   - `HANDOFF.md`'s header still reads *"Active until week 2 is complete, then delete"*.
   - Several documents name ADRs "through 0032" or "21 invariants". Today's state is 36 files
     (0037 the highest), and I21 has been generalised, with I22 decided but unbuilt.
8. **The walk / claim-durability line.**
   - `b960c9a` withdrew the two-routes-share-no-inputs claim and the supersession built on it.
   - `notes/prompts/22-walk-two-route-independence.md` has stayed untracked through two handoffs.
     **bzk to say whether it is spent or pending.** It should not stay untracked a third time.

## 8. Caveats unchanged from 2026-10-02

1. **Both public deposits are the PI's lab's.** A surprising per-protein result goes to the PI first,
   before any demo.
2. **Unpublished data stays local.** Nothing from it enters this repository.
3. **The environment.**
   - PRIDE is reachable from Claude Code's container, not from the reviewer's.
   - The raw store and the UniProt cache are on bzk's Mac only.
   - Rebuild-dependent measurements are Mac commands, pre-registered here first.
