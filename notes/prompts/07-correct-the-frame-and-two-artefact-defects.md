# PROMPT — correct the frame's 53, repair one record, land the off-repo documents

Working copy: /Users/bzk/bzk-omics

Three defects in committed artefacts. The first is the reviewer's and is the
reason this turn is first in the sequence: a number in the evidence base of an
ACCEPTED record was produced by a rule that is written down nowhere.


## Defect 1 — FRAME v1's 53

`data/frame/FRAME-v1.md`'s counts table reads *"after the conditional-term rule
(secondary enzymes need a modifier co-hit) — 53"*. Report 06 found no rule that
reproduces 53 from `frame_raw.tsv`.

**The cause, established since:** 53 came from a THIRD rule, neither the spec's
nor the code's. Every analysis the reviewer ran used a SIX-term secondary set —
the three cross-reactive DUBs PLUS `TRIM25`, `ARIH1`, `HHARI` — and dropped any
row whose terms fell entirely inside it. `FRAME-SPEC` section 2 puts those three
in *conjugation machinery*, NOT in the conditional row.

Re-derive all three before editing:

- **spec rule** — conditional = {USP16, USP24, USP36}, drop a row carrying one
  with no MODIFIER co-hit. Expected: drops 0, keeps 73.
- **code rule** — `frame.py`'s `any(t in hits for t in MODIFIER+MACHINERY+REMOVAL)`.
  Expected: drops 0, keeps 73.
- **the reviewer's undocumented rule** — drop a row whose terms are a subset of
  {USP16, USP24, USP36, TRIM25, ARIH1, HHARI}. Expected: drops 20, keeps 53.

**The decision, and it is the reviewer's: the registered spec governs. The frame
is 73.** `FRAME-SPEC` section 2 was written before the query ran; amending it now
to fit a rule invented after seeing results would be amending a pre-registration
to match its own output.

Correct `FRAME-v1.md`: the count is 73, the conditional-term rule removed ZERO
deposits, and a note records that 53 was published in error, what produced it,
and that the rule producing it was never registered. Do NOT delete the 53 — the
error is the record.

Also report, without acting on it: the 20 rows the unregistered rule would have
dropped, by accession. Whether they belong in the frame is a FRAME-SPEC question
with its own turn.


## Defect 2 — `walk/walk_PXD065158.json` is not valid JSON

`json.load` fails at l.84: `"recurring_error_shape"` sits at element level inside
the `requirements` array rather than as a key of the top-level object.

Repair it by moving that block to the top level, beside `requirements`. Change
nothing else — no verdict, no grain, no source, no wording. Confirm `json.load`
succeeds on all five records in `walk/` afterwards.


## Defect 3 — four documents cited and absent

`HYPOTHESIS.md` is cited twice in the walk records and is not in the repository.
The findings document names three more: `PXD018299_WRITE_UP_AMENDED.md`,
`AUDIT_PLAN_2026-09-17.md`, and itself.

Files have been copied in by hand before this prompt runs. Commit whichever are
present, under the same recoverability ground turn 05 used. Report which are
missing.

**One thing to flag, not fix:** the findings document's section 6.4 states
*"PXD074990 recorded absent for a source that exists"*. `WALK-STANDARD` v2's
preamble WITHDRAWS that claim and `walk/walk_PXD074990_m6.json` carries the
determination. Do not edit the findings document — it is a dated record. Note
the supersession in the commit body so the repository does not hold a withdrawn
claim and its withdrawal with nothing linking them.


## Task

Separate commits by defect. Push. Write the report to
`notes/reports/07-correct-frame-and-artefacts-report.md` and commit it.


## Out of scope

Amending FRAME-SPEC. Re-running the frame query. Screening any deposit. ADR-0033,
ADR-0034, ONTOLOGY.md, schema.py, any adapter, any invariant. The standing defect
list: the tautology sweep's stale floor; `resolve` not caching errors; `resolve`
splitting accessions on a hyphen; `Resolution` collapsing deleted and gene-less
active entries; the snapshot cache storing no synonyms; `Reverse` / `Potential
contaminant` absent from `REQUIRED_COLUMNS`; `pxd018299_refusals.json` carrying
no date; `SUPP_DATA_3`'s label; `distinct_gene_multi`.
