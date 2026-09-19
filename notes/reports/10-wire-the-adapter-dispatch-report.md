# Report — wire the adapter dispatch in `bzk/rebuild.py`

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `67a6763`, verified before anything else · **Commits:** `0d81b48`, and this report's own · **Pushed** · **`kuzu` imported by `.venv/bin/python`:** **0.11.3**

**Headline.** The dispatch is wired and the report path no longer assumes sites. Both receipt mismatches the reviewer measured reproduced exactly, so no stop condition fired. **R4 found a second live defect beyond the one registered:** the site `sniff` claimed a Perseus site export *and* its docstring asserted it could not — both are fixed in the same edit. E1 held at **718 = 694 + 24**, E2 held. **R5 and E3 did not run: this container has no raw store**, and both are handed to bzk. The turn is not closed until he has run them.

---

## Receipt checks

### R1 — what `_adapter_for` could return, and what the report path read

`bzk/rebuild.py:183–192` at `67a6763`:

```python
    dataset = next(n for n in loaded.nodes if n[NODE_TYPE_KEY] == "Dataset")
    adapter = MaxQuantSiteAdapter(
        DeclaredSiteAnalysis(
            search_engine=str(dataset.get("search_engine") or "unknown"),
            external_version=str(dataset.get("search_engine_version") or "unknown"),
            acquisition_mode=dataset.get("acquisition_mode"),
        ),
        resolver=resolver,
    )
    return adapter if adapter.sniff(path) else None
```

**The one adapter class it can return: `MaxQuantSiteAdapter`.**

`bzk/rebuild.py:282–283`:

```python
        report = adapter.report
        emitted = report.sites_emitted if report is not None else 0
```

**The attribute read at `:283` is `sites_emitted`.**

**`ProteinIngestReport` (`bzk/adapters/maxquant_protein_groups.py:101`) does not have it.** The field it has instead, at `:107`:

```python
    groups_emitted: int
```

So a curation record naming a `proteinGroups.txt` could not reach `:283` without raising `AttributeError` — and it would raise *after* `store.write_change_set` at `:272` had already written the change-set.

### R2 — must a sample's `mapping_key` family agree with `DeclaredProteinAnalysis.quantity`?

`bzk/adapters/maxquant_protein_groups.py:71–75`:

```python
QUANTITY_COLUMNS: dict[str, str] = {
    "intensity": "Intensity ",
    "lfq": "LFQ intensity ",
    "ibaq": "iBAQ ",
}
```

`:137–142`:

```python
        if not key.startswith(prefix):
            raise MaxQuantProteinGroupsError(
                f"sample mapping key {key!r} is not of the declared quantity's family {prefix!r}. "
                "The declared quantity chooses the columns, so a mapping naming another family "
                "would record one quantity on the Analysis and store another (I16)."
            )
```

**Yes.** The deciding line is `:137`, `if not key.startswith(prefix):` — where `prefix` is `QUANTITY_COLUMNS[self.declared.quantity]`. For **this** adapter the two cannot disagree without the ingestion failing. That is the premise D3 rests on: a declaration the record already forces is not a declaration, it is a second copy of what the record says.

### R3 — why a quantity derived from mapping keys would be wrong at SITE grain

`bzk/adapters/maxquant_sites.py:171`:

```python
    quantity: str = "intensity_multiplicity_summed"
```

First key of `mapping` in `data/curation/curation_PXD018299.json`:

```json
    "Ratio mod/base WT_1": {
```

`bzk/adapters/maxquant_sites.py:624–628`:

```python
        # **Every quantity the deposit reports, not only the one the `Analysis` declares.** I11 says
        # *its per-sample quantitative values*, and PXD018299 reports two per sample; keeping one
        # would discard a matrix at ingestion, and would leave ADR-0004's `quantity` key column
        # justified by a case it did not handle. The declared quantity says what this ingestion
        # consumed (I16); the store says what was reported.
```

Read together: at site grain a mapping key names **one column family out of several the adapter reads** — the comment at `:624–628` says the adapter stores every quantity the deposit reports, not just the declared one — so a key cannot stand for the quantity of the ingestion the way it does at protein grain, where `_sample_columns` forces exactly one family. And the anchor's key is `Ratio mod/base WT_1`, which is not a family in `QUANTITY_COLUMNS` at all and is not the §5 term at `:171` either, so the derivation would not merely be imprecise here — it would raise on the record that replays today. **The derivation is protein-grain only, and is the reason the dispatch must sniff before it derives.**

### R4 — six sniffs over two probes

Probe files built in a temporary directory, tabs literal, three lines each, then committed as fixtures (T1). All six booleans, measured under `.venv/bin/python`:

| file | `MaxQuantSiteAdapter` | `MaxQuantProteinGroupsAdapter` | `PerseusAdapter` |
|---|---|---|---|
| `probe_protein.txt` | `False` | **`True`** | `True` |
| `probe_site.txt` | **`True`** | `False` | `True` |

The Perseus adapter was constructed as `tests/test_perseus.py:94` does — `PerseusAdapter(declared=DECLARED, contrasts=[CONTRAST])`.

**Both of the reviewer's measurements reproduced**: the protein adapter returned `True` on `probe_protein.txt`, the site adapter returned `True` on `probe_site.txt`. **No stop condition fired.**

`bzk/adapters/maxquant_sites.py:251–253` at `67a6763`:

```
        Content, not name (`ARCHITECTURE.md` §3): `proteinGroups.txt` and the Perseus export in this
        same deposit are also tab-separated `.txt`. What distinguishes a *site* table is that it
        carries a per-site residue and a position within the protein, which neither of those has.
```

**The claim does not hold for a Perseus site export.** A Perseus tab-separated export keeps its source table's header and adds annotation rows beneath it, so a Perseus export *of a site table* carries `Amino acid`, `Positions within proteins` and `Localization prob` exactly as the source did. The clause *"which neither of those has"* is true of `proteinGroups.txt` and false of the Perseus export, and the `True` in the table above is that falsehood measured. It is corrected in the same edit and struck rather than deleted.

### R5 — **not run in this container**

`~/.bzk-omics/` does not exist here (`ls` → *No such file or directory*). R5 is recorded as **raw store absent — not run**, and is handed to bzk as the first half of his post-push check. No deposit was fetched or copied in to make it run.

The two `content_hash` values it will locate the files by, quoted from the committed curation records:

| record | `content_hash` |
|---|---|
| `data/curation/curation_PXD018299.json` | `sha256:a4a503e39581334c3553d3631456ad8aca22e193ba928810f6d46fde15622009` |
| `data/curation/curation_PXD026748.json` | `sha256:59000733f3b6b9fa8be31d4f8ae7e1868c0bb5099a8bbada580d28b3db647f50` |

---

## What changed

### D1 — where the annotation prefix lives

**Imported, not moved.** `ANNOTATION_PREFIX` stays at `bzk/adapters/perseus.py:113`, where its comment explains why only the prefix is relied on. The new reader is `bzk/adapters/maxquant.py`, which both MaxQuant adapters already import, and which now carries:

```python
def carries_perseus_annotation(path: Path) -> bool:
```

`perseus.py` imports nothing from `maxquant.py`, so the direction is acyclic. Putting the test in `maxquant.py` rather than writing the same `any(... startswith ...)` line into each of the two `sniff`s keeps the *logic* single-homed too, which matters because the two `sniff`s must agree by construction for the disjointness T1 pins.

The site `sniff`'s docstring at `:251–253` is corrected in the same edit: the false clause is struck, named as a measured error rather than a simplification, and pointed at the guard that actually separates the two.

### D3 — the ordering resolution, and its reason

**Sniff first with a throwaway probe instance built on the dataclass default; derive only after the file is claimed; then construct the adapter that parses with the derived quantity.**

The reason is R3's, made concrete. PXD018299's mapping keys are `Ratio mod/base …`, which place in no family, so `quantity_from_mapping_keys` raises on them — correctly, at protein grain. Deriving *before* dispatching would therefore turn a file the protein adapter never claimed into a rebuild-stopping error on a record that replays today. But `sniff` is an instance method (`bzk/adapters/base.py:150`, not changed this turn) and `MaxQuantProteinGroupsAdapter.__init__` validates `quantity`, so there is no way to ask the question without an instance.

The probe is safe for a checkable reason, not a hopeful one: **`sniff` reads only the file.** It touches no field of `declared`, so the probe's `quantity` cannot affect the answer, and the instance that goes on to `parse` is constructed fresh with the derived value. The alternative — passing the derived value into the probe — is exactly the ordering this rejects. The comment in `_adapter_for` says so at the point of the decision.

`_adapter_for`'s docstring sentence at the old `:178–181` is rewritten. It now says what is true branch by branch: `search_engine` and its version come from the record on both branches; the protein branch's `quantity` comes from the record too; **the site branch's `quantity` is `DeclaredSiteAnalysis`' constant default and is named there as an open defect**, deliberately not repaired, because repairing it would move an `Analysis` id and needs its own turn with its own pin to re-measure.

---

## Tests — each seen to fail before it passes

New module `tests/test_adapter_dispatch.py`, **24 tests**. Every mutation below was confirmed to have applied by reading the file back before the run, and confirmed reverted by reading it back after; the suite was green again before this report was written.

### T1 — disjointness

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| T1a | the Perseus guard struck from `MaxQuantSiteAdapter.sniff` | `test_a_perseus_export_over_sites_is_claimed_by_perseus_alone` | `AssertionError: assert ['maxquant_sites', 'perseus'] == ['perseus']` |
| T1b | the Perseus guard struck from `MaxQuantProteinGroupsAdapter.sniff` | `test_a_perseus_export_over_protein_groups_is_claimed_by_perseus_alone` | `AssertionError: assert ['maxquant_pr...s', 'perseus'] == ['perseus']` |
| T1c | `carries_perseus_annotation` returns `False` unconditionally | `test_at_most_one_adapter_claims_any_file[perseus_synthetic_over_protein_groups.txt]` | `AssertionError: perseus_synthetic_over_protein_groups.txt is claimed by more than one adapter` / `assert 2 <= 1` |

The disjointness test is parametrized over **every `.txt` fixture in `tests/fixtures/`**, which now includes the two probes, committed in the `perseus_synthetic_*` convention as `perseus_synthetic_over_protein_groups.txt` and `perseus_synthetic_over_sites.txt`. Both are claimed by **Perseus alone** after D1.

### T2 — prefix exclusivity

Mutation: a fourth row `"silac_light": "Intensity L "` added to `QUANTITY_COLUMNS`.
`test_no_quantity_prefix_is_a_prefix_of_another` →

```
AssertionError: 'Intensity L ' extends 'Intensity ', so a key matching both is ambiguous
```

### T3 — derivation

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| T3a | `return "lfq"` added as a fallback instead of raising | `test_mixed_families_raise_and_name_the_keys` | `Failed: DID NOT RAISE MaxQuantProteinGroupsError` |
| T3a′ | same mutation | `test_ratio_keys_raise_and_name_the_keys` | `Failed: DID NOT RAISE MaxQuantProteinGroupsError` |
| T3b | the uniform branch returns `"lfq"` rather than the family it found | `test_uniform_intensity_keys_derive_intensity` | `AssertionError: assert 'lfq' == 'intensity'` |
| T3c | the error message stops interpolating `unplaceable` | `test_ratio_keys_raise_and_name_the_keys` | `assert 'Ratio mod/base WT_1' in "the sample mapping does not name exactly one quantity's column family, …"` |

T3c is the one that pins *"each error message must name the offending keys"* rather than merely that something raised.

### T4 — dispatch

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| T4a | `quantity=quantity_from_mapping_keys(...)` deleted from the protein branch | `test_dispatch_returns_the_protein_adapter_with_the_derived_quantity` | `AssertionError: assert 'lfq' == 'intensity'` |
| T4b | the protein branch short-circuited to `return None` | same | `assert False` / `where False = isinstance(None, MaxQuantProteinGroupsAdapter)` |
| T4c | the site branch's `if site.sniff(path)` made unreachable | `test_dispatch_returns_the_site_adapter_for_a_site_table` | `assert False` / `where False = isinstance(None, MaxQuantSiteAdapter)` |
| T4d | `carries_perseus_annotation` returns `False`, so the protein branch claims a Perseus export | `test_dispatch_returns_none_for_a_perseus_export` | `AssertionError: assert <MaxQuantProteinGroupsAdapter object …> is None` |

T4a is the one that matters: with the derivation gone the dispatch still returns the right *class*, and only the declared `quantity` is wrong — the silent failure D3 exists to prevent.

### T5 — replay over a protein-groups deposit

Synthetic record and synthetic file under `tmp_path`, with an explicit `home`; nothing reads the real store.

| # | mutation | failing assertion's message |
|---|---|---|
| T5a | the report path reverted to `adapter.report.sites_emitted`, unconditionally | `AttributeError: 'ProteinIngestReport' object has no attribute 'sites_emitted'. Did you mean: 'groups_emitted'?` — **the crash at `:283`, reproduced** |
| T5b | `groups_emitted` re-pointed at the `site_observations` counter | `KeyError: 'protein_observations'`, raised from the summary log line. A real failure, and an honest one to note: it is a `KeyError` rather than a clean assertion, because the counter dict is built from the same registry the mutation edits |
| T5d | the parsed change-set written as `([], [])` | `KeyError: 'ProteinObservation'` at `assert store.count_nodes(conn)["ProteinObservation"] == 1` — the observations reach the report but not the graph |
| T5c | *"78 seconds"* struck from `replay_ingestion`'s docstring | `AssertionError: assert '78 seconds' in 'Load every curation record, …'` |

The test asserts `report.protein_observations == adapter.report.groups_emitted` against an adapter parsed separately, not against a literal on both sides. `site_observations == 0` and `deposits_ingested == 1` are asserted alongside. `replay_ingestion`'s docstring still records the 78-second hazard, and T5c pins that it does.

**One assertion was reshaped after the tautology sweep flagged it.** `store.count_nodes(conn)["ProteinObservation"] == adapter.report.groups_emitted` was reported by `test_tautology_sweep.py` as an unclassified new matching expression. It is not a tautology, but the line above it already ties the report to the adapter, so repeating `groups_emitted` here checks the graph against nothing new. It now reads `== 1` — the literal one row `_synthetic_protein_groups` writes, which Pass C excludes as a literal display — and T5d establishes that it fires.

---

## Registered expectations

### E1 — **held**

| | before the change | after |
|---|---|---|
| passed | 680 | **704** |
| skipped | 14 | **14** |
| total | **694** | **718** |

The 680/14 split reproduced exactly before the change, as the reviewer measured on a container with no raw store. 718 = 694 + 24 new tests, all passing under `.venv/bin/python`.

**No existing test changed.** `git diff --stat` against `67a6763` touches four files under `bzk/` and adds three under `tests/`; no existing test file is modified. **No docstring-quoting test was touched by the D1 correction** — none quotes `maxquant_sites.py:251–253`, so there is no such test to name.

### E2 — **held**

`tests/test_rebuild.py::test_rebuilt_ids_match_the_committed_pin` passes **unmodified** — `1 passed`. The site branch's declared `quantity` is unchanged, so no `Analysis` id moved. No committed id pin moved.

### E3 — **raw store absent — not run.** Handed to bzk.

To be run on his machine after this push, as registered:

- `PXD018299`: 2,029 sites and 27 refusals, unchanged;
- `PXD026748`: 2,166 sites, 21 refusals and 51,984 cells, unchanged;
- `PXD055843`: still skipped with *"no adapter recognises"*, and the rebuild CLI exits 1 because of that skip, as expected.

Not approximated with synthetic files. **One thing was checked here that lowers the risk on the third line and does not substitute for it:** a synthetic `.xlsx` carrying `Protein IDs` and a Perseus type-stamp row was sniffed by both MaxQuant adapters, and both returned `False` — so neither reads a workbook, which is the premise `PXD055843` still being skipped rests on. That is a property of the adapters, not a replay over the real deposit, and it is not committed as a test. **If the protein adapter claims `PXD055843`'s file on his machine, the turn is reopened.**

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock` before anything ran. Every command under `.venv/bin/python`; Anaconda's `python3` was not used.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **704 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **98 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 98 source files** |

The `ruff` and `mypy` targets are `bzk tests`, not the repository: `ruff check .` additionally covers the three notebooks, which are deliberately and permanently out of scope as records of experiments rather than maintained source. **`ruff check .` was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

Checked directly, not inferred from a green suite:

- **The two R4 mismatches are gone, measured the same way they were found.** Both probes are now claimed by Perseus alone; the table in R4 was re-measured after the edit through `_claims`.
- **Every new guard was made to fail**, with the mutation confirmed applied by reading the file back before each run and confirmed reverted after — twelve mutations, listed above with their messages. T5a reproduces the exact `AttributeError` at `:283` that motivated the turn, which is the strongest single piece of evidence that the defect was real and is closed.
- **The baseline was measured before the change** (680/14), not assumed from the reviewer's number.
- **The E2 pin was run on its own**, not merely observed to be inside a green suite.

---

## `CLAUDE.md` point 3 — what this change does not cover

**Closed by this turn, and by what:**

- *A MaxQuant `sniff` claiming a Perseus export.* **Closed for both tab-separated cases, by a test, not a note.** `test_at_most_one_adapter_claims_any_file` is parametrized over every `.txt` fixture in the tree, so a fixture added later is covered without anyone remembering, and the two named tests pin the specific direction. The class is *not* closed for containers: the workbook case is argued (a workbook decodes to bytes neither adapter's header test accepts) and measured ad hoc above, but **no committed test asserts that either MaxQuant `sniff` refuses a workbook**. That is the residue, and it is the premise E3's third line rests on.
- *The dispatch assuming one grain.* **Closed by `EMITTED_FIELDS` plus T5.** The registry is the single place a third grain would be added, and T5a fails if the report path goes back to reading a fixed attribute.
- *The protein branch's `quantity` being a constant.* **Closed by T4a**, which fails when the derivation is removed while the dispatch still returns the right class.
- *The derivation's dependence on non-overlapping prefixes.* **Closed by T2**, which is machine-checkable and is written rather than left as a note, per point 3's own standard. A fourth row added to `QUANTITY_COLUMNS` fails it.

**Not covered, stated plainly:**

- **SILAC-channel keys such as `Intensity L …`.** Out of scope by the prompt, and **not guarded**. They begin with `Intensity `, so `quantity_from_mapping_keys` would derive `intensity` for them and be wrong. T2 is adjacent but does not cover this: it fails only if `Intensity L ` is *added to `QUANTITY_COLUMNS`*, and the SILAC hazard is a key that is never added there. No record in `data/curation/` carries such a key today.
- **The site branch's declared `quantity`.** Carried, not repaired: `maxquant_sites.py:171` is a constant, not a declaration. Named in `_adapter_for`'s docstring as an open defect. Repairing it moves an `Analysis` id and needs the pin re-measured, which E2 explicitly forbids this turn.
- **R5 and E3.** Not run here. Not approximated. Handed to bzk, and the turn is not closed until he has run both.
- **The tautology sweep's floor did not move for this turn, and was already well behind the surface.** `tests/test_tautology_sweep.py:1356` reads `assert modules >= 32 and asserts >= 1129`. Measured with `sweep()`: **41 modules / 1,489 asserts at `67a6763`**, and **42 / 1,510** after this turn. So the floor was stale by nine modules and 360 assertions before this change and is stale by ten and 381 now — a `>=` is silent about a surface that grew, which is exactly the standing defect carried from prompt 09 and exactly the slack that test's own comment says re-denomination exists to remove. It was **not** re-denominated here because E1 registered *no existing test changes*. Flagged rather than fixed, with the two numbers measured so whoever next has licence to edit that file does not have to re-derive them.

  The sweep's *multiset* half did fire on this turn's new module and was answered — see the reshaped assertion under T5 — so the half that catches new matching expressions is working; it is only the floor that is inert.
- **Everything the prompt put out of scope** was left alone: the shotgun zip, the second curation record and the record-count pin, any `PXD026748` ingest, `protein_adjusted` / `ADJUSTED_BY` / I4 / I21, `PerseusAdapter` in the dispatch, `ObservationAdapter`, any ADR, `ONTOLOGY.md`, `schema.py`, any invariant, the published cascade, and the handoff documents. Nothing was ingested, no curation record was written.
- **The standing defects carried from prompt 09** are all still open and untouched: the tautology sweep's stale floor; `resolve` not caching errors; `resolve` splitting accessions on a hyphen; `Resolution` collapsing deleted and gene-less active entries; the snapshot cache storing no synonyms; `Reverse` / `Potential contaminant` absent from `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying no date; `SUPP_DATA_3`'s label; `distinct_gene_multi`.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **R5 and E3 were not run**, as the prompt instructed. Recorded as *raw store absent — not run* in both places and handed to bzk. Not a drop, but the turn stays open on them.
- **`RebuildReport` was not given `protein_observations`.** D4 named `ReplayReport` only, and `rebuild()`'s `done:` line at what is now `:434` still reports `replay.site_observations` alone. That line's meaning is unchanged and correct, but a protein-grain rebuild's figure does not reach a `RebuildReport` caller. Reported here rather than done silently: widening it was not asked for and it is the kind of scope creep D4's precision was guarding against. It is the one place where "the report path stops assuming sites" is true of the replay and not yet of the rebuild wrapper.
- **The working branch.** The harness handed this session `claude/eloquent-fermat-or15bq`. Per `CLAUDE.md` § Working style the change was fast-forwarded onto `main` when complete and both refs were pushed; `main` and the branch are the same commit.
- Nothing else from the prompt was dropped or partially done.

---

## Anything not verifiable either way

- **E3's three lines.** No raw store here, so the replay figures for `PXD018299`, `PXD026748` and `PXD055843` are unverified in this container by construction. The workbook check above narrows the third line's risk and does not settle it.
- **`_sample_columns`' behaviour against the real `HAP1_USP18KO_proteinGroups.txt`.** The derivation is exercised against a synthetic four-column mapping only; whether the real deposit's mapping keys place in exactly one family is a fact about a file that is not in this container.
- **Whether `PerseusAdapter.sniff` is disjoint from the two MaxQuant `sniff`s over containers other than `.txt`.** T1 is parametrized over `.txt` fixtures, which is the whole committed set; a workbook fixture would extend it and none exists.

---

## Commits and push range

| commit | contents |
|---|---|
| `0d81b48` | `rebuild: dispatch over both MaxQuant adapters, and stop assuming sites` — D1–D4 and T1–T5, code and tests, one commit, no report |
| this report's own, `notes: report the adapter dispatch turn, and track prompt 10` | `notes/reports/10-wire-the-adapter-dispatch-report.md` and `notes/prompts/10-wire-the-adapter-dispatch.md` |

**Push range:** `67a6763..0d81b48` for the code commit, then one commit on top carrying this report and its prompt. Both pushed to `origin/claude/eloquent-fermat-or15bq` and fast-forwarded onto `origin/main`.

This report does not quote its own SHA. A first attempt did, by amending the SHA in after committing — which changed the SHA, so the quoted value was wrong the moment it was written. The commit is named by its subject line instead, which is stable. `git log --oneline -2` on either ref gives both SHAs.
