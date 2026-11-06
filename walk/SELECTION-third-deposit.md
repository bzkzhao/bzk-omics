# SELECTION — the third, unaffiliated deposit (2026-11-06)

**Rule:** `HYPOTHESIS.md` §9, registered at v8 before any candidate was examined.
**Frame:** `data/frame/frame_raw.tsv` as committed, ascending PXD order.
**Result: `PXD032267`** (Yerra et al., *J Clin Invest* 2023), the first
candidate to meet all five criteria. It has published per-site statistics that
can serve as a gate, so under the rule the walk stops there. The candidate
record is `walk/walk_PXD032267.json`.

---

## Declared before attrition was counted

The rule asks for attrition *at every criterion* and does not fix the order in
which a candidate is tested. Each frame row is counted once, at the first
criterion it fails, in this order:

**C5 (domain) → C1 (authors) → C4 (site table) → C2 (claim set) → C3 (pipeline).**

The order goes from cheapest to most expensive to determine. It changes where a
row is counted and never whether a row qualifies, since a qualifier must pass
all five whatever the order.

**Reading of C5.** "The ISGylation, ubiquitination or other GG-remnant PTM
domain of the frame" is read as FRAME-v1's site-directed partition: Frame B,
plus the undecided rows once their protocol is read. Every frame row is in the
ISGylation domain by construction, so a looser reading would make C5 pass
everywhere and push the GG test into C2 and C4. This is an interpretation, and
it needs the owner's sign-off.

## Attrition, frame rows up to and including the selection

| criterion | rows counted here | rows |
|---|---|---|
| C5 — not GG-remnant site-directed | 26 | the 26 rows below `PXD032267` that are neither Frame B nor undecided |
| C1 — shares an author | 5 | `PXD001805` (Impens), `PXD011513` (Thery, Beling, Impens), `PXD018299` and `PXD026748` (the earlier publications themselves), `PXD032078` (Thery) |
| C4 | 0 | |
| C2 | 0 | |
| C3 | 0 | |
| **qualifies** | **1** | `PXD032267` |
| **walked** | **32** | |

`PXD001805` is undecided at C5 in FRAME-v1. It is counted at C1 because C1
determines it outright and C5 does not.

## The weakest step, stated

**The 26 C5 exits rest on metadata (G0), not on file listings.** FRAME-v1's
partition was a detector plus judgement over title, description and protocols,
and WALK-STANDARD §2's asymmetry rule asks more of an absence than that. It was
re-checked here by scanning the same four fields of all 26 rows for remnant,
GlyGly, diglycine, K-ε-GG, PTMScan, 114.04 and "-ome" terms. Two rows hit:

- `PXD000459` names diglycine and 114.04. It is SUMO-site mapping, and an
  author it shares (Impens) would exit it at C1 under any order.
- `PXD025753` names an "ISGylome". Its protocols describe an ISG15
  immunoprecipitation quantified label-free at protein grain, with no GlyGly
  variable modification, so it has no site-level claims.

The other 24 name no remnant term in any field. **What would overturn this:** a
row among the 24 whose file listing carries a GlyGly site table and whose
publication lists site-level claims. None was opened at G1. If one existed and
also passed C1–C3, it would precede `PXD032267` and replace it.

## What the selection does not settle

- **Independence.** C1 is a name comparison. `PXD032267`'s proteomics was
  done by a contract provider, so a convention shared with the earlier deposits
  through tooling (MaxQuant plus a Perseus-style downshifted normal) is not
  excluded. It is a different laboratory, not a different practice.
- **The gate's size.** Ten per-site pairs and six counts (record, `gate`).
- **Platform reach.** It is the first mouse deposit and the first MaxQuant 2.x
  site table. Neither is a criterion, and both are untested.

## Next, in order

1. ~~Open `GlyGly__K_Sites.txt` and `parameters.txt` at G3/G4.~~ **Done
   2026-11-06**, recorded under `deposit_read` in the candidate record. The
   site table is adapter-compatible, and all ten published claims join. The
   census figures it produced are disclosed there, before the gate is
   registered.
2. Pre-register the gate's metric and threshold, as `PREREG-PXD018299-H10.md`
   did, before any reconstruction runs.
