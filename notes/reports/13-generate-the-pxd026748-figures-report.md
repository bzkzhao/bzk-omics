# Report — a generator for PXD026748's ingest figures

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `c1f121a`, reached by fast-forward · **Commits:** `7a25f35`, and this report's own · **Pushed, every push a fast-forward** · **`kuzu`:** 0.11.3

**Headline.** `bzk/sources/pxd026748_ingest_figures.py` writes both arms' figures from the deposits' bytes, following `pxd018299_refusals.py` exactly. **R3's answer is that neither the PREREG nor report 09 states the method** behind the multi-protein and isoform shares, so both are defined here and written into each fixture as a `method` string — and they may differ from whatever turn 09 did. E1 held at 724/14, E2 held. **One limit worth reading before the rest:** T3's "writes neither fixture" is a live assertion but its second arm is not independently reachable in this container, explained under T3.

---

## Receipt checks

### R1 — the base

```
$ git diff --stat cae91c6..origin/main
 data/curation/curation_PXD026748_shotgun.json |   2 +-
 walk/RESULT-PXD026748-shotgun-ingest.md       | 111 ++++++++++++++++++++++++++
 2 files changed, 112 insertions(+), 1 deletion(-)
```

One commit, `c1f121a walk: score the shotgun ingest, and correct the record's site-only figure (93 → 73)`. The record's single changed line is the FILTERS item, and the correction is the one described: 93 site-only rows, 20 of them also `Reverse` or `Potential contaminant`, **73** reaching the graph — the first wording *"include those 93"* having assumed an overlap of zero that was never measured.

```
$ sha256sum data/curation/curation_PXD026748_shotgun.json
9501e5ca5b61b2957a1cc6ccf2a79358943f7b88e196b7b1af57bef67d95bd8a
```

**Both checks pass.** No stop condition fired.

### R2 — the anchor generator

`bzk/sources/pxd018299_refusals.py`, `main()`:

```python
def main() -> int:
    # Located and configured exactly as `replay_ingestion` does it, rather than by constructing a
    # `MaxQuantSiteAdapter` from constants here as `pxd018299_sites.py` does. The refusals this
    # file records must be the refusals an ingestion produces, and an adapter configured from a
    # different declaration is a second population wearing the same name.
    curation = load_path(CURATION)
    deposit = _deposit_for(curation, HOME)
    if deposit is None:
        raise SystemExit("deposit not in the content store; run `python -m bzk.sources.pride`")
    adapter = _adapter_for(curation, deposit, None)
    if adapter is None:
        raise SystemExit(f"no adapter recognises {deposit.name}; nothing to refuse")

    parsed = adapter.parse(deposit, curation.sample_mapping())
    fixture = refusal_fixture(parsed.refusals)
    FIXTURE_PATH.write_text(json.dumps(fixture, indent=2) + "\n")
    …
    return 0
```

**Its outputs:** one file, `tests/fixtures/pxd018299_refusals.json`, plus a progress summary on stdout — the deposit and adapter names, the refusal total, and a count per reason.

**How it locates the deposit and configures the adapter:** `load_path(CURATION)` for the record, then `rebuild._deposit_for(curation, HOME)` and `rebuild._adapter_for(curation, deposit, None)` — the same two functions `replay_ingestion` uses. Nothing is constructed from a constant.

**Its comment on why, quoted:** *"Located and configured exactly as `replay_ingestion` does it, rather than by constructing a `MaxQuantSiteAdapter` from constants here as `pxd018299_sites.py` does. The refusals this file records must be the refusals an ingestion produces, and an adapter configured from a different declaration is a second population wearing the same name."*

### R3 — the multi-protein and isoform figures, and their method

`notes/reports/09-ingest-PXD026748-report.md:176–177`:

> | 4 | multi-protein share **70–90%** | **9.0%** (232 / 2,587, the anchor's denominator: rows after decoy/contaminant). 9.4% after the localisation filter (205 / 2,187); 9.4% of emitted observations (203 / 2,166) | **Missed, below, by 61 points.** … |
> | 5 | isoform razor picks **20–40%** | **0 / 2,187 rows = 0%**; 0 / 1,033 distinct picks. **No isoform accession appears among any of the 1,185 candidates** | **Missed, below, by 20 points.** … |

So the numerators and denominators are:

| figure | numerator / denominator |
|---|---|
| multi-protein, after decoy/contaminant | 232 / 2,587 |
| multi-protein, after localisation | 205 / 2,187 |
| multi-protein, emitted observations | 203 / 2,166 |
| isoform razor picks, rows | 0 / 2,187 |
| isoform razor picks, distinct picks | 0 / 1,033 |
| isoform accessions among candidates | 0 / 1,185 |

**Where turn 09 said how it computed them: nowhere. The report does not state the method.** Searched for it directly — every occurrence of *multi-protein*, *isoform*, *candidates*, *razor pick* and the figures themselves across report 09, and the registration table in `walk/PREREG-PXD026748-ingest.md`. What exists is a statement of the **quantities**, in the PREREG at `:42–43`:

> | 4 | share of sites whose `candidate_proteins` names more than one protein | **70% to 90%** | … |
> | 5 | share of razor picks that are isoform accessions | **20% to 40%** | The anchor measured 30%. … |

and nothing anywhere about **which column was read, which rows were counted, or what counts as an isoform**. Report 09's nearest approach is a remark at `:184` that *"Zero isoform candidates in the whole table is what that text predicts"* and a note that the anchor's 30% was *"6 of 20, a sample of twenty"* — observations about the numbers, not a derivation.

**Stated plainly, as the prompt asks: the report does not state the method.** A share with no stated method cannot be reproduced, and the three denominators are not interchangeable — the PREREG registered one interval and report 09 answered it with three different fractions without saying which one the registration was about. So the generator defines both methods, writes each definition into its fixture as a `method` string, and the fixture is the first place either method is written down.

### R4 — the two report classes' fields

`SiteIngestReport` (`bzk/adapters/maxquant_sites.py:193–219`), ten fields:

`rows_read`, `dropped_decoy_or_contaminant`, `dropped_below_localization`, `sites_emitted`, `refused_no_razor_pick`, `refused_unresolved_protein`, `refused_residue_mismatch`, `promoted_reviewed` — the eight counts — then `unresolved: dict[str, str]` and `observation_of_row: dict[str, str]`.

`ProteinIngestReport` (`bzk/adapters/maxquant_protein_groups.py`), eight fields:

`rows_read`, `spill_lines`, `dropped_decoy_or_contaminant`, `groups_emitted`, `refused_empty_group`, `distinct_accessions`, `cells`, then `observation_of_row: dict[str, str]`.

---

## The module's outputs, field by field

`bzk/sources/pxd026748_ingest_figures.py`. Two fixtures, written only after both arms parse.

### `tests/fixtures/pxd026748_digly_ingest.json`, from `curation_PXD026748.json`

| field | source |
|---|---|
| `dataset` | the loaded `Dataset` node's `external_accession` |
| `file` | the `Dataset` node's `label` |
| `content_hash` | the `Dataset` node's `content_hash` |
| `note`, `generated_by` | this module |
| `generated_under` | `{"python": platform.python_version()}` — as the anchor records, nothing here computes a statistic |
| `report.*` (8 keys) | every count field of `SiteIngestReport`; the two `dict` fields are not counts and are not carried |
| `cells.total` | `sum(len(batch) for _, batch in parsed.cells)` |
| `cells.by_quantity` | `collections.Counter(c.quantity …)`, sorted keys |
| `refusals` | `asdict(r)` per `Refusal` — `row`, `reason`, `detail` — in parse order |
| `multi_protein.method` | `MULTI_PROTEIN_METHOD`, defined in the module |
| `multi_protein.after_decoy_or_contaminant` | numerator over `maxquant.drop_decoys_and_contaminants(table)` |
| `multi_protein.after_localisation` | numerator over the adapter's own `_filter(table, column)[0]` |
| `multi_protein.emitted_observations` | numerator over `SiteObservation` nodes with `len(candidate_proteins) > 1` |
| `isoform_razor_picks.method` | `ISOFORM_METHOD`, defined in the module |
| `isoform_razor_picks.rows` | picks containing `-` / every row after localisation |
| `isoform_razor_picks.distinct_picks` | distinct non-empty picks containing `-` / distinct non-empty picks |

**The two row populations are the adapter's, not re-derived.** `drop_decoys_and_contaminants` is the function `_filter` itself calls first, and `_filter` is the function the ingestion applied — so the denominators are the same rows the ingestion counted. Calling a private method across modules is the pattern R2's comment establishes and the anchor already uses (`_deposit_for`, `_adapter_for`); a second implementation of either filter would be the second population that comment names.

**Every share is two integers, never a float.** A percentage is a derivation, and the fixture records what was counted.

### `tests/fixtures/pxd026748_shotgun_ingest.json`, from `curation_PXD026748_shotgun.json`

| field | source |
|---|---|
| the five header keys | as above |
| `report.*` (7 keys) | every `ProteinIngestReport` field except `observation_of_row` |
| `cells.by_quantity` | `Counter` over `parsed.cells` |
| `cells.positive_by_quantity` | the same, restricted to `value is not None and value > 0` |
| `refusals` | `asdict(r)` per `Refusal` |
| `analysis_quantity` | the ingestion `Analysis` node's `quantity` |
| `only_identified_by_site.column_present` | whether the file has an `Only identified by site` column |
| `only_identified_by_site.in_file` | rows with `+` in that column |
| `only_identified_by_site.emitted` | those rows whose `id` is a key of `report.observation_of_row` |
| `only_identified_by_site.dropped_as_decoy_or_contaminant` | those rows also carrying `Reverse` or `Potential contaminant` |

**`emitted` is counted through `observation_of_row`, not as `in_file - dropped`.** The subtraction happens to be right on this file and is wrong in general: a row can also fail to be emitted by being refused, and the difference would fold that into the decoy count and report a row as dropped for a reason it was not. T1a is the mutation that establishes the difference.

**Nulls rather than zeros when the column is absent.** `Only identified by site` is a MaxQuant output option; a file without it has no such rows *recorded*, which is not the same as having none, and writing `0` would state a measurement the file cannot support. `column_present` says which case it is.

---

## The two methods

**Both are newly defined by this module. Neither is turn 09's, because turn 09's is unrecorded.**

**Multi-protein** — a row is multi-protein when its `Proteins` column, split on `;` with blanks dropped, names more than one accession; an emitted observation is multi-protein when its `candidate_proteins` list has more than one member. Denominators as above.

**Isoform razor picks** — a razor pick is MaxQuant's `Protein` column for a row, stripped, **before any I17 promotion**, because promotion replaces the pick with a reviewed entry and *"razor pick"* names what MaxQuant chose. It is an isoform accession when it contains `-`, which is **the test the resolver already applies** at `bzk/resolve/uniprot.py:357` (`is_isoform = "-" in requested`) — reused rather than reinvented, because two definitions of *isoform* in one repository would be a mirror with nothing holding them equal, and the resolver's is the one that decides what gets fetched. `rows.denominator` counts every row after the localisation filter, including rows whose `Protein` is empty and which the adapter then refuses as `no_razor_pick`; those contribute to the denominator and never to the numerator.

Both strings are in the fixtures. Both say, in the fixture itself, that the PREREG and report 09 state no method and that these may differ from theirs.

**One figure report 09 gives is deliberately not generated:** *"No isoform accession appears among any of the 1,185 candidates"*. The prompt asked for isoform **razor picks** as a numerator and denominator; a candidate-level share is a third population and is named here rather than added unasked.

---

## Tests — each seen to fail before it passes

`tests/test_pxd026748_ingest_figures.py`, five tests, entirely offline on synthetic tables under `tmp_path`. No deposit and no generated fixture is committed. Every mutation was confirmed applied by reading the file back and confirmed reverted after.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T1a** | `emitted` computed as `in_file - dropped` (+1, so the arithmetic differs) | `test_only_identified_by_site_separates_dropped_from_emitted` | `AssertionError: … Differing items: {'emitted': 2} != {'emitted': 1}` |
| **T1b** | the `Reverse` half of the decoy overlap ignored — the assumption the record's FILTERS item was corrected for | same | `Differing items: {'dropped_as_decoy_or_contaminant': 0} != {'dropped_as_decoy_or_contaminant': 1}` |
| **T1c** | positive cells counted as non-null rather than `> 0` | `test_shotgun_cells_are_counted_by_quantity_and_by_positivity` | `assert {'intensity': 4, 'lfq': 3} == {'intensity': 4, 'lfq': 2}` |
| **T2a** | `after_localisation` computed over the after-decoy rows | `test_the_three_multi_protein_denominators_are_three_different_populations` | `Differing items: {'numerator': 2} != {'numerator': 1}; {'denominator': 3} != {'denominator': 2}` |
| **T2b** | multi-protein read as `>= 1` rather than `> 1` | same | `Differing items: {'numerator': 3} != {'numerator': 2}` |
| **T2c** | the emitted share read off the rows rather than off `candidate_proteins` | same | `Differing items: {'numerator': 2} != {'numerator': 1}` |
| **T2d** | `distinct_picks` counted per row rather than once each | `test_an_isoform_razor_pick_counts_once_per_row_and_once_per_distinct_pick` | `Differing items: {'denominator': 3} != {'denominator': 2}; {'numerator': 2} != {'numerator': 1}` |
| **T3a** | the absent-deposit message replaced by `"deposit missing"` | `test_main_writes_neither_fixture_when_a_deposit_is_absent` | `assert 'curation_PXD026748.json' in 'deposit missing'` |
| **T3b** | a write of the GG fixture moved ahead of both parses | same | `assert [PosixPath('…/pxd026748_digly_ingest.json')] == []` |

**T1's fixture is the case the record was corrected for.** Its three rows are a decoy that is *also* only-identified-by-site, a site-only row that is kept, and an ordinary row — exactly the overlap the shotgun record's FILTERS item first assumed away (93 → 73 on 2026-09-19).

**T3's limit, stated rather than left to be assumed.** The test passes an empty `home`, so **both** deposits are absent and the GG arm exits first. `list(fixtures_dir.iterdir()) == []` is a live assertion — T3b makes it fail — but what it demonstrates is that nothing is written before the *first* arm parses. It does **not** demonstrate that a failure in the *second* arm leaves the first arm's fixture unwritten, because that state is not reachable here: `_deposit_for` locates a deposit by the record's `content_hash`, and no synthetic bytes can hash to the committed record's digest, so a temporary home can never hold one deposit and not the other. The ordering is enforced structurally — both dicts are built before either is written — and that structure is readable but unguarded. Named here rather than papered over.

---

## Registered expectations

### E1 — **held**

| | at `c1f121a` | after |
|---|---|---|
| passed | 719 | **724** |
| skipped | 14 | **14** |

724 = 719 + 5 new tests.

### E2 — **held**

**No existing test changed.** `git status` before the commit showed two untracked files and nothing modified; the commit is `2 files changed, all insertions`. In particular `tests/test_tautology_sweep.py` needed no entry — every equality in the new module's tests compares against a literal display, which that module's Pass C excludes by construction.

**No id pin moved.** `test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. Nothing this turn writes to the graph or changes an identity field; the module is an entry point that nothing in the package imports.

The base's record correction is noted rather than re-verified: the reviewer measured all 16 of its node ids unchanged across the edit, and the changed text is inside `unresolved`, which is not an identity field of any node.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **724 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **102 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 102 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The module was never run against a real deposit**, because none exists here. What is verified is the arithmetic, on synthetic tables parsed through the same two adapters, and the failure path of `main`. The IO path — `_deposit_for`, `_adapter_for`, the write loop — is exercised only as far as its first guard. **That is the honest boundary of this turn's evidence**, and bzk's run is what tests the rest.
- **Each of the nine mutations was confirmed applied by read-back and reverted**, and the suite is green as this is written.
- **R3's negative was established by searching, not by not-finding.** Every occurrence of the figures and of the four relevant terms across report 09 and the PREREG was read before concluding the method is unstated.
- **Two mypy errors and two lint errors were fixed rather than suppressed** — an `accession` key the `Dataset` node does not carry (it is `external_accession`, checked against a loaded record), and an unused `type: ignore`.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **Neither fixture is generated or committed**, and no guard exists against any value either would carry. That is the next turn's, and it needs bzk's run first. Until then the module's arithmetic is guarded and its output is not.
- **T3's second arm is unreachable here**, as above. The "never a partial fixture" property is structural and unguarded against a mid-run failure.
- **The methods may not be turn 09's.** If bzk's run produces 232 / 2,587 and 205 / 2,187, that is evidence the definitions agree; if it does not, the difference is a finding about report 09 and not necessarily a defect in either. **Nothing in this turn can tell those two cases apart**, and the fixture's `method` strings exist so that the next reader can.
- **The candidate-level isoform figure** report 09 gives (0 / 1,185) is not generated — a third population, not asked for.
- **`promoted_reviewed` is carried but the isoform method deliberately ignores promotion.** A reader comparing the two could reasonably want the post-promotion pick counted too; that is a second share and is not written.
- **Out of scope and untouched:** the published cascade and the MOESM3 declaration, ADR-0035's review, the six superseded homes of `67,158`, the site branch's constant `quantity`, the unenumerated-mirrors class, the drift line, `notes/prompts/`.
- **The tautology sweep's floor** — still `modules >= 32 and asserts >= 1129` against a larger surface, still not re-denominated. No `PINNED` entry was needed this turn.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **Nothing was dropped.** The one instruction whose premise did not hold is R3's *"find where turn 09 said how it computed them"* — it did not, and that negative is reported as the prompt directs, with the definitions supplied and recorded in the fixtures.
- **`main` gained a `fixtures_dir` parameter the prompt did not name.** The prompt asked for `home` to be parameterised; `fixtures_dir` is the same discipline one step along, and without it a test that ever reached the write path would write into the repository's committed fixtures directory. Reported rather than folded in silently.
- **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `7a25f35` | `sources: generate PXD026748's ingest figures from the bytes, not from the reports` — the module and its five tests, one commit |
| this report's own, `notes: report the figure-generator turn` | `notes/reports/13-generate-the-pxd026748-figures-report.md`, alone |

**Push range:** `c1f121a..7a25f35` for the module, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `58a92aa..7a25f35` on the branch and `c1f121a..7a25f35` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase. This report does not quote its own SHA; `git log --oneline -2` on either ref gives both.
