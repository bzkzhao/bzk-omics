# ADR format

ADRs live in `decisions/` as `NNNN-slug.md`, sequentially numbered. The directory already exists
and holds 24 records. **Read `decisions/README.md` before writing one** — it carries the status
convention, and corrections that could not be made inside the records themselves.

## The two rules that bind

**A record lands as `Proposed`.** It becomes `Accepted` only once a review round-trip completes.
Correcting a record during review is an ordinary edit to a `Proposed` document — that is what the
status is for. Do not land a record as `Accepted` to save a step: that asserts a review that did
not happen, which is the one thing this project refuses everywhere else.

**Once `Accepted`, a record is append-only.** It is never edited. A changed decision gets a new
record that supersedes the old, and both remain readable — the same discipline the product applies
to `ModifierAssignment` and `EnzymeAssociation`. A decision should die visibly.

`Superseded` is the third status, used when the round-trip does not apply: the record documents a
decision that was made and then replaced. `Proposed` would be false of a decision nobody is
proposing. The `Superseded by` row carries the successor.

## Writing one is a multi-file, test-guarded change

`tests/test_decision_index.py` checks three enumerations of ADR numbers against each other and
against the directory, and **pins exact counts** so a parser that stops matching fails loudly
instead of comparing two empty sets. A new record must move all of these in the same commit:

| Surface | What changes |
|---|---|
| `decisions/NNNN-slug.md` | the new file |
| `decisions/README.md` § Written | a new row |
| `decisions/README.md` § Queued | remove the row, if the number was reserved there |
| `ARCHITECTURE.md` §5 seed list | strike the number, if it is within `0001`–`0018` |
| `tests/test_decision_index.py` | `EXPECTED_FILES`, `EXPECTED_WRITTEN_ROWS`, `EXPECTED_QUEUED_ROWS`, `EXPECTED_STATUSES` |

Run `pytest tests/test_decision_index.py` before claiming the record is written. A green run is
the check; the exit status alone is not — read the count it asserted.

## Numbering

Scan `decisions/` for the highest existing number and increment. Check the **Queued** table in
`decisions/README.md` first: a number may already be reserved for a record nobody has written.

## Template

Match the records already in the directory rather than a generic template. Each carries a header
table with `Status`, and `Superseded by` / `Supersedes` rows where they apply, then the context,
the decision, and what was rejected.

The value is in recording *that* a decision was made, *why*, and *what was turned down* — not in
filling out sections. An ADR can be short.

## When to offer one

All three must be true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the code and wonder why
3. **The result of a real trade-off** — there were genuine alternatives and you picked one

If a decision is easy to reverse, skip it — you will just reverse it. If it is not surprising,
nobody will wonder. If there was no real alternative, there is nothing to record.

### What qualifies here

The existing records are the calibration. They cover the storage boundary (0004), key composition
(0005, 0021), what a modifier assignment *is* (0006, 0024), append-only assertions (0008),
contracts over tables (0010), the derived graph (0012), permanent matrix retention (0013), and
positioning (0017). All are architectural shape, boundary decisions, or deliberate deviations from
the obvious path.

**Do not write an ADR to record an invariant.** Invariants live in `ONTOLOGY.md` §8 and are
normative there. An ADR explains *why* an invariant was chosen; it does not define it. ADR-0008 and
ADR-0012 sit beside I6 and I9 exactly this way.
