# Receipt checks — zero handling and `filters_applied`, for the ADR-0033 imputation draft

| Field | Value |
|---|---|
| Status | Working note, not a decision |
| Version | 1.0 |
| Last reviewed | 2026-09-17 |
| Authoritative for | Nothing. Quotes below are copies; the cited files are the sources |

Written to verify the corrected zero-handling paragraph of the imputation-state ADR draft.
**The draft itself was not present in the working copy when these checks were run** — see
§ What could not be checked. The checks below stand on their own and are what the paragraph
must be measured against when the draft is supplied.

Run against `019c711` (`Refresh the README's status table and changelog`, 2026-09-17), clean tree.

---

## R1 — `cell_value`'s "A reported" sentence

`bzk/adapters/maxquant.py:93-96`, to its terminator:

> **A reported `0` stays `0`**: MaxQuant writes zero for an undetected intensity, and reading
> that convention as absence is an interpretation the adapter has no licence to make (I19) — it
> is the statistics layer's to make and record.

## R2 — which adapter folded `0` to `None`

`bzk/adapters/maxquant.py:101-103`:

> **Lives here, and not in `maxquant_sites.py` where it was written, since 2026-08-10.** The
> protein adapter's first draft folded `0` to `None` on the reasoning that MaxQuant writes zero
> for an unquantified protein — true, and a decision this module had already made the other way.

The module docstring (`:10-12`) says the same from the other side: the protein adapter wrote its
own value reader and folded `0` to `None`, *"which `maxquant_sites.py` had already refused to do
(I19)"*. So `maxquant_sites.py` is the adapter that got it **right** and is the reader's birthplace;
the protein adapter is the one that got it wrong. Attributing the fold to `maxquant_sites.py`
inverts both facts at once.

## R3 — `filters_applied`'s absence in the curation loader

`bzk/curation/loader.py:316-320`:

> A curation analysis consumes no quantity (I16 skips it; §3 classifies the absence), and
> applied no filters — which is a value, not an absence, so an empty list and not a null.
> §3 does not classify `filters_applied`'s absence, so a null here would be refused.

Assigned value: `"filters_applied": []`.

## R4 — which column of the §3 identity table

`ONTOLOGY.md:120`, Analysis row, **Identifying fields** column:

> `kind`, `basis`, `confidence`, `quantity`, `localization_threshold`, `filters_applied`, `test`,
> `fdr_method`, `external_tool`, `external_version`, `parameters_observed`, `parameters_json`

Its Excluded columns cell is `label`, `rationale`, `started_at`, `ended_at`, `workflow_id`,
`workflow_revision` — `filters_applied` is not in it. **Identifying.**

## R5 — closed enum for `filters_applied` values

`ONTOLOGY.md:485`:

```
  filters_applied STRING[],     -- e.g. ['reverse','potential_contaminant']
```

**No closed enum exists, anywhere in `ONTOLOGY.md`.** Four independent confirmations:

1. The comment reads `e.g.` — illustrative by construction. Fourteen lines up, `quantity` reads
   `CLOSED enum (mirror: schema.py QUANTITY_VALUES)`, so the document distinguishes the two cases
   and puts `filters_applied` on the open side.
2. `bzk/ontology/invariants.py:499` checks `filters_applied` for `is None` only. The adjacent
   `quantity` branch checks membership in `QUANTITY_VALUES` and names the closed enum in its error.
3. The two MaxQuant adapters carry **different** tuples —
   `("reverse", "potential_contaminant")` (`maxquant_protein_groups.py:78`) versus
   `("reverse", "potential_contaminant", "localization_prob")` (`maxquant_sites.py:100`) — as
   per-adapter module constants, not a shared ontology enum.
4. Live values in the suite include parameterised tokens no enum could hold:
   `localization_prob>=0.75` (`tests/test_ui.py:98`, `tests/test_query.py:83`,
   `tests/test_analysis_differential.py:34`) and `only_identified_by_site`
   (`tests/test_perseus.py:64`). `bzk/ontology/keys.py:111` treats a `filters_applied` token as
   free text explicitly — *"a `filters_applied` token has no colon"*.

A named filter is therefore expressible without amending anything. The draft's claim needs no
qualifying.

---

## What this settles for the draft's corrected paragraph

- The reversal is supported. `filters_applied` is the home: it is identifying (R4), so a filter
  recorded there mints a distinct `Analysis` id, and the adapter reader is the wrong home because
  `cell_value` is bound by I19 not to interpret (R1). The interpretation is the statistics layer's,
  and `Analysis.filters_applied` is where the statistics layer's declaration lands.
- The misattribution is real and is the protein adapter's. `maxquant_sites.py` refused the fold
  and is where `cell_value` was written before it moved on 2026-08-10 (R2).
- A named filter such as a zero-handling rule is expressible today (R5). No enum blocks it.

## What could not be checked

- **The draft.** `ADR-0033-imputation-state.md` is not in the working copy, in `decisions/`, in
  any branch or stash, in the scratchpad, or anywhere on the container's filesystem. Every claim
  attributed to it in this note comes from the prompt's description of it, not from its text, and
  the corrected paragraph has therefore **not** been read or edited. The checks above are what it
  must be measured against; the measurement is not done.
- Whether the draft's paragraph states the reversal in terms these checks actually support, as
  opposed to a different reading that happens to reach the same home.

## Deliberately out of scope

Landing the ADR (three open items), numbering, amending `ONTOLOGY.md` / `schema.py` / any adapter
or invariant, one `filters_applied` entry or two, the lysate question, the selection ADR, and the
standing defect list.
