# PROMPT — wire the adapter dispatch in `bzk/rebuild.py`

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.
Base: `67a6763`. Verify HEAD before anything else; if it differs, report the
commits between and stop.

**This container has no raw store.** `~/.bzk-omics/raw/` exists only on bzk's
machine. So R5 and E3 do NOT run here. Record each as "raw store absent — not
run". Do not stop, and do not fetch or copy any deposit in to make them run.
bzk runs both on his machine after your push, and the turn is not closed until
he has.

Build the environment with `uv sync` from the committed `uv.lock` before running
anything. Report the `kuzu` version that `.venv/bin/python` imports.

This is piece 1 of the shotgun-arm work, and it is its own commit because it
touches the ingest path for every deposit. It is justified without reference to
`PXD026748`. **This turn ingests nothing new, writes no curation record, and
does not touch the shotgun zip.**

Run every Python command under `.venv/bin/python`. Anaconda's `python3` cannot
import `kuzu`. That interpreter produced the false "pre-existing failure" in
reports 06 and 07.


## Receipt checks

R1. `bzk/rebuild.py:183–192`. Quote it. Name the one adapter class it can
    return. Then quote `:282–283` and name the attribute read at `:283`. State
    whether `ProteinIngestReport` (`bzk/adapters/maxquant_protein_groups.py`)
    has that attribute, and quote the field it has instead.

R2. `bzk/adapters/maxquant_protein_groups.py:71–75` and `:137–142`. Quote both.
    Answer yes or no, with the line that decides it: for THIS adapter, does the
    family of a sample's `mapping_key` have to agree with
    `DeclaredProteinAnalysis.quantity`?

R3. `bzk/adapters/maxquant_sites.py:171`. Quote it. Quote the first key of
    `mapping` in `data/curation/curation_PXD018299.json`, and quote `:624–628`
    of the same adapter. Using those three quotations only, explain why a
    quantity derived from mapping keys would be wrong at SITE grain.

R4. Build these two probe files in a temporary directory. Tabs are literal, and
    each file is exactly three lines.

    `probe_protein.txt`:
    ```
    Protein IDs	LFQ intensity A	id
    #!{Type}E	E	N
    P1	1.0	0
    ```
    `probe_site.txt`:
    ```
    Amino acid	Positions within proteins	Localization prob	Proteins	id
    #!{Type}C	N	N	T	N
    K	12	0.99	P1	0
    ```
    Call `sniff` on each file three times: with `MaxQuantSiteAdapter`, with
    `MaxQuantProteinGroupsAdapter`, and with `PerseusAdapter`. Construct the
    Perseus adapter the way `tests/test_perseus.py:94` does. Report all six
    booleans.

    The reviewer measured two of them on a separate clone:
    - the protein adapter returned `True` on `probe_protein.txt`;
    - the site adapter returned `True` on `probe_site.txt`.

    If you get anything else, report it and stop. Then quote
    `maxquant_sites.py:251–253` and say whether its claim about "the Perseus
    export" holds for a Perseus **site** export.

R5. **Not run in this container.** Record it as not run. bzk runs it on his
    machine after the push, as the first half of his post-push check.
    Here, quote the two `content_hash` values it will locate the files by:
    `PXD018299`'s and `PXD026748`'s, from their committed curation records.


## What changes, and what the reviewer decided

**D1 — Neither MaxQuant sniff claims a Perseus export.** Both
`MaxQuantSiteAdapter.sniff` and `MaxQuantProteinGroupsAdapter.sniff` return
`False` for a tab-separated file carrying a Perseus annotation row. R4 shows the
site sniff already misclaims one, so this is a defect in shipped code, not only a
guard for the new branch.

The annotation prefix has ONE home. It is currently
`bzk/adapters/perseus.py:113`. Import it or move it, but do not restate it, and
do not create an import cycle. Report which you did.

The site sniff's docstring at `:251–253` is corrected in the same edit. Strike
the false claim; do not delete it silently.

**D2 — Dispatch over the two MaxQuant adapters, by sniff.** `_adapter_for`
returns the site adapter, the protein-groups adapter, or `None`.

`PerseusAdapter` is NOT in the dispatch. Its constructor needs `contrasts`, and
those come from an analysis record, not a curation record.
`bzk/sources/pxd055843_perseus.py:8–11` already routes around replay for this
reason. State that in `_adapter_for`'s docstring.

**No branch for "more than one adapter claims the file".** After D1, the three
sniffs are pairwise disjoint. A refusal for a case that cannot occur is an
unreachable branch, and `rebuild.py` already records removing one for that
reason. The disjointness is pinned by a test instead (T1).

**D3 — The protein branch's `quantity` is derived from the record's mapping
keys.** Add one function beside `QUANTITY_COLUMNS` in
`maxquant_protein_groups.py`, so the prefix knowledge keeps one home. It behaves
as follows:
- If every sample's `mapping_key` begins with the prefix of exactly one family,
  it returns that family.
- If the prefixes are mixed, or no key carries a recognised prefix, it raises
  `MaxQuantProteinGroupsError`. It never falls back to the dataclass default.
  An unplaceable mapping is a curation problem, and the adapter's own
  `_sample_columns` already raises on one.

**The derivation runs only after the protein sniff has claimed the file.** The
anchor's mapping keys are `Ratio mod/base …` (R3), so deriving before
dispatching would raise on a record that replays today. `sniff` needs an
instance, and the constructor validates `quantity`. Decide how to resolve that
ordering, and report the decision and its reason. Changing the
`ObservationAdapter` protocol at `bzk/adapters/base.py:150` is NOT an acceptable
resolution this turn.

**This derivation is protein-grain only**, per R3. `_adapter_for`'s docstring
at `:178–181` currently says every declared parameter comes from the record.
After this turn that is true of the protein branch and still false of the site
branch. Rewrite the sentence to say exactly that, and name the site default as
an open defect. Do not fix the site default.

**D4 — The report path stops assuming sites.** `ReplayReport` gains a
`protein_observations` count beside `site_observations`, and the meaning of
`site_observations` is unchanged. The per-deposit log line at `:285–290` and
the summary at `:291–296` name the unit the adapter actually emitted.
`ingestions_skipped` and `main`'s exit status are unchanged.


## Tests — each one seen to fail before it passes

For each test, report the mutation that made it fail and the failing assertion's
message.

T1. **Disjointness.** Over the two R4 probes and every `.txt` fixture in
    `tests/fixtures/`, at most one of the three sniffs returns `True`. Also:
    - `probe_protein.txt` is claimed by Perseus alone;
    - `probe_site.txt` is claimed by Perseus alone.

    Commit the probes as fixtures, named in the `perseus_synthetic_*`
    convention.
T2. **Prefix exclusivity.** No value in `QUANTITY_COLUMNS` is a prefix of
    another. Derivation depends on this, so it is asserted, not assumed.
T3. **Derivation.** Four cases:
    - uniform `LFQ intensity` keys give `lfq`;
    - uniform `Intensity` keys give `intensity`;
    - mixed keys raise;
    - `Ratio mod/base` keys raise.

    Each error message must name the offending keys.
T4. **Dispatch.** `_adapter_for` returns:
    - the site adapter for a synthetic site table;
    - the protein adapter for a synthetic `proteinGroups.txt`, with `quantity`
      equal to the derived family;
    - `None` for a Perseus export.
T5. **Replay over a protein-groups deposit.** This test does not crash at
    `:283`. It reports `protein_observations` equal to the adapter's
    `groups_emitted` and `site_observations == 0`.

    It uses a synthetic record and a synthetic file under `tmp_path`, with an
    explicit `home`, never the real store. `replay_ingestion`'s docstring
    records the 78-second hazard.


## Registered expectations

E1. Suite total = 694 + the number of new tests, all passing under
    `.venv/bin/python`.
    - The 694 is the reviewer's measure: 680 passed and 14 skipped on a
      container with no raw store.
    - This container also has no raw store, so the 680/14 split should
      reproduce before your change. bzk's machine gives 686/8. Report your
      split, and if it matches neither, say why.
    - **No existing test changes** except docstring-quoting tests that the D1
      correction touches, if any. Name each one.
E2. **No committed id pin moves.** `test_rebuilt_ids_match_the_committed_pin`
    passes unmodified. The site branch's declared quantity is unchanged, so no
    `Analysis` id can move. If one moves, STOP and report it.
E3. **Registered here, run by bzk on his machine after the push. Not run in this
    container.** A full rebuild over the real raw store replays the three
    records as follows:
    - **`PXD018299`**: 2,029 sites and 27 refusals, unchanged.
    - **`PXD026748`**: 2,166 sites, 21 refusals and 51,984 cells, unchanged.
    - **`PXD055843`**: still skipped with "no adapter recognises". Its file is
      a workbook and neither MaxQuant sniff reads workbooks.

    Because of that skip, the rebuild CLI exits 1, and that is expected. If the
    protein adapter claims `PXD055843`'s file, the turn is reopened.

    Here, record E3 as "raw store absent — not run". Do not approximate it with
    synthetic files; T4 and T5 already cover the synthetic shape.


## Task

1. Run the receipt checks R1–R4, and quote R5's two digests. Stop conditions:
   HEAD not `67a6763`, or an R4 mismatch.
2. Make D1–D4 and write T1–T5.
3. Run E1 and E2, plus every check `CLAUDE.md` point 1 enumerates, with its target
   stated:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit the code and tests as ONE commit (`rebuild:` prefix), without the
   report. Push.
5. Write the report to `notes/reports/10-wire-the-adapter-dispatch-report.md`,
   and commit it together with this prompt at
   `notes/prompts/10-wire-the-adapter-dispatch.md`. Push.


## Out of scope

- The shotgun zip. The second curation record and the record-count pin.
- Any `PXD026748` ingest.
- `protein_adjusted`, `ADJUSTED_BY`, I4 and I21. This turn cannot reach
  `'applied'`; nothing on the replay path writes a `DifferentialResult`.
- `PerseusAdapter` in the dispatch.
- Changing `ObservationAdapter`.
- Any ADR, and ONTOLOGY.md, `schema.py` or any invariant.
- The published cascade for `PXD026748`, and the fixture for its ingest figures.
- The handoff documents, committed or revised.
- SILAC-channel keys such as `Intensity L …`, which would derive as `intensity`.
  Name this as not covered; do not guard it.

**New defect, carried and not repaired:** the site branch's `quantity` is a
constant (`maxquant_sites.py:171`), not a declaration.

**Standing defects, carried from prompt 09:**
- the tautology sweep's stale floor;
- `resolve` not caching errors;
- `resolve` splitting accessions on a hyphen;
- `Resolution` collapsing deleted and gene-less active entries;
- the snapshot cache storing no synonyms;
- `Reverse` / `Potential contaminant` absent from `REQUIRED_COLUMNS`;
- `pxd018299_refusals.json` carrying no date;
- `SUPP_DATA_3`'s label;
- `distinct_gene_multi`.


## Report

- R1–R4 quoted and answered. R5's two digests quoted, and R5 recorded as not run.
- For D1: where the annotation prefix now lives.
- For D3: the ordering resolution and its reason.
- T1–T5, each with its mutation and failure message.
- E1 and E2, each held or missed, with figures. E3 recorded as not run and
  handed to bzk.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this change does NOT cover, per `CLAUDE.md` point 3. For each class this
  turn touched, say whether the class is closed and by what.
- Commit SHAs and the push range.
- Anything you could not verify either way.
