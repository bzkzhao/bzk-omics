# REVIEWER HANDOFF — 2026-11-07b

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-11-07.md`
(written 02:20) as the starting point. That file stays as the record; it was
written before both of this day's builds and its §1 figures are stale.

**Two briefs closed since it was written.** Prompt 36 (the reader-only
PXD032267 audit) and prompt 33 (the three guards 2026-10-10 §6(A) named). With
prompt 33 built, **10-10 §6(A) is closed in full** — it was the last item of
that handoff's open list that was actionable without the PI.

**What is not restated here.** Items the earlier handoffs carry which neither
build touched are not repeated. 11-07 (02:20) §3 stands for what the third
deposit found; 10-10 §6(B)–(C) stands for the platform line.

**Line references** are to `main` at `f61f6fd` unless stated, and every one was re-measured
there — `f61f6fd` moved `perseus.py` by 51 lines and `differential.py` by 13, so a reference
carried over from before the build is wrong by that much.

---

## 1. Starting point

- **`main` at `f61f6fd`**, linear, no merges. **36 commits** from `8d71ec4`.
- **Suite, measured in a container at `f61f6fd`:** `1206 passed, 14 skipped`;
  `pytest tests/test_schema.py` `20 passed`; `mypy bzk tests` Success over
  **127** files; `ruff check` clean, `ruff format --check` **127** formatted.
- **bzk's Mac** runs six more passing and six fewer skipped (the raw-store
  tests), so expect `1212 passed, 8 skipped`. **That is the relation applied to
  a measured container figure, not a measured Mac figure.**
- `ONTOLOGY.md` v1.48, unedited by either build. `tables_created` 60
  (`tests/test_rebuild.py` l.138).
- **Every figure above carries the commit it was measured at.** Adopted this
  session after rev 9's figures went stale within ten hours; see §4.

## 2. Commits since `8297e58`, in order

| commit | what |
|---|---|
| `93ac652` | README readability |
| `07e1d91`, `4621735` | prompt 36: `python -m bzk.audit_pxd032267`, a reader-only ten-stage audit that computes nothing |
| `dc3145a` | prompt 36 follow-up: tests for three audit checks that shipped untested, mutation proof for six more |
| `d35ea87` | **Y8 corrected** — eight of ten claims at or below 6 of 20 under readout D, not seven. A reviewer miscount, found by prompt 36's build |
| `d4084a3`, `d369216`, `7f5bc70` | prompt 33 revs 9, 10, 11 |
| `f61f6fd` | **prompt 33 built** — the three guards |

## 3. What prompt 33 built

Three guards, no behaviour change on committed input. `maxquant_sites.py` is
**not** in the diff: it was edited only by mutations, each reverted.

- **§2.1 — only `_compose` composes a site column.** New module
  `tests/test_maxquant_sites_composition.py` (280 lines). An AST tripwire that
  classifies **by shape, never by identifier name**: a value is tainted if it
  comes from `QUANTITY_COLUMNS` or a prefix-ending constant, propagated through
  assignment, walrus, loop targets and call sites. The binding/message
  discriminator is **adjacency** — a binding puts a bare prefix flush against
  another bare interpolation; a message names a prefix with `!r`. Match set:
  two bindings, both in `_compose`; three messages (`bind_column` l.163–166 and
  l.178–183, `_run_label` l.196–198). It reaches `_site` despite that
  function's reversed parameter names, via the walrus at l.711.
- **§2.2 — `site_change_set` refuses arms from another contrast.**
  `ContrastArms` gains `contrast_id`, filled by the loader with the **minted
  node's** id. The record handle cannot serve: nothing on the node carries it.
  The check sits at **l.164**, after the shape refusal at **l.154** and before the `Contrast`
  is staged at **l.171**. The field reaches no node or edge.
- **§2.3 — one helper for statistics cells.** `_statistic` (`perseus.py`
  l.264) serves all five reads, refusing a cell that will not parse **or is
  not finite**, naming the file line, the column and the raw cell. The three
  methods now take `line_no`; `_ContrastColumns` gains `names`.

**E3 verified independently in the reviewer's clone**, not inferred from a
green suite: all four curation records load to byte-identical node-id digests
at `7f5bc70` and `f61f6fd` (`a6df428d…`, `35a4f9c9…`, `2d5b01d8…`,
`9b70c271…`), and `tables_created` is 60 at both.

**`PINNED`'s regenerate comment was broken and is fixed.** The old command
printed `sorted(sweep()[0])` — 2-tuples, silently dropping every count, where
`PINNED` holds 3-tuples. **Three wrong versions existed**: the repository's
original, and the reviewer's own suggested replacement
(`sorted(sweep()[0].items())`, which gives nested pairs). The build wrote the
flat form and confirmed its width.

## 4. Dated home — the non-finite statistics measurement

**Measured on bzk's Mac, 2026-11-07, at `f61f6fd`.** §2.3's refusal reaches
real data, so it was checked against the content store before PXD055843
unblocks. `notes/scripts/probe_nonfinite_statistics.py` reads through the
adapter's own `_read`, so the composed header is the one ingestion will see.

| file | data rows | statistics columns | non-finite cells |
|---|---|---|---|
| `Supplementary_Data_S1_TP.xlsx` | 7,610 | 4 (suffix `siUSP24_IFN_siCTRL_IFN`) | **0** |
| `Supplementary_Data_S3_ISG15_IP.xlsx` | 4,410 | 4 (suffix `siUSP24 (+IFN)_sic (+IFN)`) | **0** |

**So §2.3 changes nothing for the two Perseus files that exist.**

- **Three cross-checks say the probe read S1 as the adapter does:** 7,610 rows
  matches `curation_PXD055843.json`'s *"over 7,610 rows"*; the composed suffix
  is the one that record states; and 29 columns matches `perseus.py` l.188's
  own recorded measurement of this file (*"nine non-empty cells of 29"*).
- **Why it needed checking at all.** Perseus writes the negated log
  (`perseus.py` l.438), and `-log10(0)` is `inf`, so an underflowed p is a
  plausible `Inf`. `PerseusError` is never downgraded (l.260), so one such cell
  would refuse the whole file — surfacing whenever the PI answers, looking like
  a new defect.
- **Reachability bounded:** `_statistic` has one caller, `_ContrastColumns._read`
  (l.428), bound only during a Perseus parse. `maxquant.py` imports only
  `ANNOTATION_PREFIX` from `perseus.py`, so the MaxQuant `.txt` exports in the
  store cannot reach the refusal and are out of scope rather than uncovered.
- **Not covered:** `S2_GG` and `S4` are not in the content store and are named
  nowhere in this repository. If either carries a non-finite statistic the
  question reopens when it is added.
- **11-07 (02:20) §5's "Nothing" for the Mac was wrong**, and prompt 33 §5
  inherited it. A build that changes a refusal reaching real data owes a
  read-only check there.

## 5. Open, in priority order

1. **ROADMAP open questions 1 and 3:** public or private v0.1; a paper on the
   tool or on the biology. **bzk's decision**, blocks nothing, sets how urgent
   item 2 is.
2. **The four FINDINGS figures `bzk.audit` cannot regenerate:** §1 census, §2
   two-route downshift, §5 changing-support count, §6 q-ranges. A paper needs
   them from one command. **Prompt 36 added `bzk/audit_pxd032267.py` as a
   separate audit — whether it moved any of the four is unmeasured.**
3. **The S1 item's remaining half:** were Fig. 2f's labelled points chosen by
   hand? (11-07 §9.)
4. **ADR-0032's review — now owed two inputs, not one.** Still `Proposed`
   (l.5), overdue since 10-10. It is titled *what the Perseus adapter reads and
   whether the platform converts*, and `f61f6fd` changed exactly that. So it
   owes both D6-revised (c) and §2.3.
5. **Instrument items:**
   - `walk/FINDINGS.md` l.3 still opens *"Two deposits"* — **wrong by one**
     since PXD032267, whose audit prompt 36 then built;
   - the H10 `MATCH_TOLERANCE` 1e-6 defect behind the withdrawn S1 finding
     (`bzk/sources/pxd018299_h10.py` l.164);
   - the tautology-sweep floor still moves **only by hand** — `f61f6fd` moved
     it 59/2599 → 60/2612 manually (`tests/test_tautology_sweep.py` l.2301);
   - attempt 2 marked its own tree dirty (11-07 §5.4).
6. **Platform line**, unchanged from 10-10 §6: order item 3 (PXD018299's
   `ISG15_interactome`, the first real IP ingestion), and the PI questions.
   **PXD055843's block is the imputation *seed*, not whether imputation ran** —
   `curation_PXD055843.json` states the method from the paper's methods and puts
   only the seed and the "Perseus defaults" values in `unresolved`.

**New, from prompt 33, each reported rather than built:**
- **`DeclaredContrast` carries the same unrelated pair** (`perseus.py` l.311–312;
  l.643 anchors every result on `str(declared.contrast["id"])`, `_prove` binds over
  `declared.arms` at l.979).
  **Blocked on a decision: identity or extension.** `test_the_count_is_per_contrast`
  (`tests/test_perseus.py` l.1383) deliberately pairs a second contrast with the
  same arms, so an identity check breaks a test whose subject is that scenario.
  Needs an ADR, not a guard.
- **The `dataset` gap.** Neither check relates `arms` or `contrast` to
  `dataset`, so a `dataset` from another record stays representable. By design.
- **`contrast_id` is a claim, not a proof.** Hand-built `ContrastArms` can state
  any id; the loader is the only production site.
- **`test_tautology_sweep.py` l.10–11 over-claims**, saying every equality is
  pinned where only Pass C/D matches are. It is the source the prompt inherited
  its own wrong wording from. Unfixed.
- **A `NaN` Difference no longer reads as tested.** `float()` accepts `NaN`, and
  `NaN == 0.0` is `False`, so such a row previously passed `untested` and minted
  a result with `log2fc` `NaN`. §2.3's helper closes it as a side effect;
  `test_a_nan_difference_no_longer_reads_as_tested` pins it. **Rev 11 told the
  build to report and not fix this while specifying the helper that fixes it** —
  a contradictory instruction, resolved correctly by building only the helper.
- **Twenty `claude/*` branches** on the remote, several stale;
  `claude/friendly-cray-dcs2hj` was fast-forwarded to `d369216` by a build
  session and carries nothing of its own. `CLAUDE.md` says development lands
  directly on `main`.

## 6. How this session ran

- **Nine prompt audits found twenty-three blockers; §0's receipt check then
  found seven more in one pass**, including the broken `PINNED` command, which
  would have stopped the build. **§0 executes against the repository; the audits
  read it.** Argues for keeping §0 heavy and pre-release auditing lighter.
- **Three of those twenty-three were introduced by the fix for the previous
  one**, each reproducing the shape it repaired: a wrong exclusion inside the
  fix for a wrong exclusion; a miscounted file list inside the paragraph
  announcing it had stopped miscounting; a bare countable inside the sentence
  arguing countables must be measured. Rev 9 onward tells the build to distrust
  passages marked as fixes **specifically**.
- **Anchor every stated figure to its measurement commit.** Rev 9's figures went
  stale between measurement and commit, because prompt 36 landed in between.
  The specification survived five commits untouched; the numbers about it did
  not. Anchoring turns that from a halt into a signal.
- **A hand-maintained census in a prompt header was wrong in four consecutive
  revisions** — short by three, by nine, a hedged total, then a count asserted
  of `git diff --numstat` that held only of cited paths. Deleted in rev 6
  rather than corrected a fifth time. `CLAUDE.md`'s single-source rule covers
  it: *"Each fact has exactly one home. Cross-reference; never restate."*
- **A probe that scans nothing must not return a pass.** The first
  non-finite probe reimplemented Perseus header reading, found zero statistics
  columns in S1, and reported no non-finite cells — a vacuous pass on the one
  question in the session that touched real data. It now returns INCONCLUSIVE
  when no file yields a statistics column, and drives the adapter's own reader.
- **Shell sent to bzk must run as pasted.** `<path>` placeholders are zsh
  redirection; a probe that imports `bzk` cannot run from `~/Downloads`, since
  Python puts the script's directory on `sys.path` and not the cwd.
- **Write probes against the dataclass, not its current fields.** The probe
  named `ContrastArms.contrast_id` and so refused to run on the pre-`f61f6fd`
  tree — the comparison it existed to make. It reads
  `dataclasses.fields()` now.

## 7. The pivot, for orientation only

Unchanged from 11-07 (02:20) §6: provenance-aware **dataset weighting** for
public proteomics (immunopeptidomics, cryptic antigens), using the curation and
attrition measures this platform already produces. §5 items 1–2 remain the
recommended finish line before it. Nothing in the repository has been started.
