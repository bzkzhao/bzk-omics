"""Round-14 descriptive, UNREGISTERED checks (adversarial review, 2026-09-22).

Usage, from the repository root:
    .venv/bin/python notes/scripts/diagnose_round14.py 2>&1 | tee notes/logs/round14.txt

Not an independent path: the same instruments the registered runs use. Nothing registered changes.

EE — THE CENSUS OF DRAWN CELLS. S1 has no gaps, so every S1 cell the deposit does not provide is
     the authors' own draw. That makes this a census, not a sample. Claims are partitioned by how
     many of their six published values are drawn, and split into: none drawn; some drawn but a
     measured-only fold change still computable in both arms; and a whole arm drawn, where no
     measured counterpart exists. For the middle class the published fold change is compared with
     the measured-only one — PKM's 0.47 is one draw from that distribution.
     The identification rule checks the per-multiplicity columns as well as the summed one.

FF — THE JITTER BAND, NOT THE COUNT. Round 13 reported the collateral channel as 1 of 40 fully
     measured claims. The better statistic is the size of the wobble: the q ranges of rows whose own
     values never move (median 0.0015, max 0.0033) measure how far other rows' draws move the shared
     threshold. This counts how many of ALL published claims sit inside that band of the cut, which
     is the channel's real reach.

GG — THE PEPTIDE-LEVEL COUNT. The paper states 2,341 GlyGly peptides; no reading of the site table
     gave it. MaxQuant's sites table carries `Mod. peptide IDs` as semicolon lists, whose union is
     the peptide-level count the site table CAN provide. If it lands on 2,341 the unit question
     closes.

HH — THE DEPOSIT'S PARAMETER FILES. A `parameters.txt` or `summary.txt` would say whether the
     deposited table was regenerated after the analysis. The raw store is listed.
"""

import json
import math

import numpy as np
from bzk.adapters import maxquant
from bzk.provenance.raw_store import raw_root, verify
from bzk.sources.pxd018299_h10 import (
    HOME,
    PXD018299_SITES,
    SUPP_DATA_1,
    _float_cell,
    _s1_rows,
    _supplement_path,
    anchor_population,
    s1_columns,
)
from bzk.stats.imputation import downshifted_normal
from bzk.stats.perseus_s0 import _relabellings, _statistic

ALPHA, S0, R_PERM, DRAWS = 0.01, 0.1, 250, 20
DEFAULT = {"downshift_sd": 1.8, "width_sd": 0.3, "scope": "per_sample"}
KO = ["Intensity KO_IFN_1", "Intensity KO_IFN_2", "Intensity KO_IFN_3"]
WT = ["Intensity WT_IFN_1", "Intensity WT_IFN_2", "Intensity WT_IFN_3"]

table = maxquant.read_table(
    verify(PXD018299_SITES.expected_content_hash, filename=PXD018299_SITES.filename, home=HOME)
)
rows, column = anchor_population(table)
ids = [str(r[column["id"]]).strip() for r in rows]
index_of = {name: i for i, name in enumerate(ids)}


def raw_value(row: list[str], name: str) -> float:
    text = row[column[name]].strip() if name in column else ""
    try:
        return float(text)
    except ValueError:
        return 0.0


def provided(row: list[str], name: str) -> bool:
    """The deposit provides this cell, in the summed column OR at any multiplicity."""
    if raw_value(row, name) > 0:
        return True
    return any(raw_value(row, f"{name}{suffix}") > 0 for suffix in ("___1", "___2", "___3"))


with open("tests/fixtures/pxd018299_published_cascade.json") as handle:
    cascade = json.load(handle)["rows"]
header, s1 = _s1_rows(_supplement_path(SUPP_DATA_1, HOME))
published_columns = s1_columns(header)

print("EE — the census of drawn cells in the published table")
none_drawn, comparable, arm_drawn, gaps = [], [], [], []
for claim in cascade:
    deposit_id = str(claim["deposit_id"])
    row = rows[index_of[deposit_id]]
    values = [_float_cell(s1[int(claim["row"])].get(name)) for name in published_columns]
    drawn = [not provided(row, name) for name in KO + WT]
    record = (deposit_id, values, drawn)
    if not any(drawn):
        none_drawn.append(record)
    elif all(drawn[:3]) or all(drawn[3:]):
        arm_drawn.append(record)
    else:
        comparable.append(record)
        ko_measured = [v for v, d in zip(values[:3], drawn[:3], strict=True) if not d]
        wt_measured = [v for v, d in zip(values[3:], drawn[3:], strict=True) if not d]
        gaps.append(abs((np.mean(values[:3]) - np.mean(values[3:]))
                        - (np.mean(ko_measured) - np.mean(wt_measured))))
print(f"  published claims: {len(cascade)}")
print(f"    no drawn cell:                                   {len(none_drawn)}")
print(f"    some drawn, both arms still measured somewhere:  {len(comparable)}")
print(f"    a whole arm drawn (no measured counterpart):     {len(arm_drawn)}")
print(f"    claims whose published fold change contains a drawn cell: "
      f"{len(comparable) + len(arm_drawn)} of {len(cascade)} "
      f"({(len(comparable) + len(arm_drawn)) / len(cascade):.0%})")
gaps = np.array(gaps)
if gaps.size:
    print(f"  |published fold change - measured-only fold change| over the {gaps.size} comparable claims:")
    print(f"    quartiles {np.percentile(gaps, 25):.3f} / {np.median(gaps):.3f} / "
          f"{np.percentile(gaps, 75):.3f}, max {gaps.max():.3f} (log2 units)")
    pkm = next((i for i, (d, _, _) in enumerate(comparable) if d == "1107"), None)
    print(f"    PKM (id 1107) sits at {gaps[pkm]:.3f}" if pkm is not None
          else "    PKM is not in this class")

print("\nFF — the jitter band: how far the shared threshold moves, and its reach")
matrix = np.array([[math.log2(raw_value(r, n)) if raw_value(r, n) > 0 else math.nan
                    for n in KO + WT] for r in rows])
measured = ~np.isnan(matrix)
keep = (measured[:, :3].sum(1) >= 1) | (measured[:, 3:].sum(1) >= 1)
kept = matrix[keep]
kept_ids = [i for i, k in zip(ids, keep, strict=True) if k]
claim_ids = {str(c["deposit_id"]) for c in cascade}
published = np.array([i in claim_ids for i in kept_ids])
imputed_count = 6 - measured[keep].sum(1)
q_all = []
for seed in range(DRAWS):
    filled = downshifted_normal(kept, seed=seed, **DEFAULT).values
    observed = _statistic(filled[:, :3], filled[:, 3:], S0)
    finite = np.isfinite(observed)
    magnitude = np.abs(observed[finite])
    thresholds = np.sort(magnitude)
    counts = []
    for assignment in _relabellings(3, 3, scheme="random_excluding_trivial",
                                    randomisations=R_PERM, seed=seed)[0]:
        mask = np.zeros(6, dtype=bool)
        mask[np.asarray(assignment[:3])] = True
        null = np.abs(_statistic(filled[:, mask], filled[:, ~mask], S0))[finite]
        null = np.sort(null[np.isfinite(null)])
        counts.append(null.size - np.searchsorted(null, thresholds, side="left"))
    null_count = np.array(counts, dtype=float).mean(axis=0)
    observed_count = magnitude.size - np.searchsorted(thresholds, thresholds, side="left")
    q = np.full(observed.shape, np.inf)
    q[finite] = np.minimum.accumulate(null_count / np.maximum(observed_count, 1))[
        np.searchsorted(thresholds, magnitude, side="right") - 1
    ]
    q_all.append(q)
q_all = np.array(q_all)
fully = published & (imputed_count == 0)
jitter = float(np.median(q_all[:, fully].max(0) - q_all[:, fully].min(0)))
print(f"  jitter measured on rows whose own values never move: median q range {jitter:.4f}")
median_q = np.median(q_all, axis=0)
for band in (jitter / 2, jitter, 2 * jitter):
    inside = published & (np.abs(median_q - ALPHA) <= band)
    print(f"    published claims with median q within +/-{band:.4f} of the cut: "
          f"{int(inside.sum())} of {int(published.sum())} ({inside.sum() / published.sum():.1%})")
print("  With one observed instance among 40 fully measured claims, the rate is 2.5% with a")
print("  95% interval of roughly 0.1% to 13%, and it scales with how much of the matrix is drawn.")

print("\nGG — the peptide-level count the site table can provide")
peptide_field = next((n for n in table.header if n.lower().startswith("mod. peptide id")), None)
print(f"  column used: {peptide_field!r}")
if peptide_field:
    for label, subset in (("all rows", rows),
                          ("minus reverse and contaminants",
                           [r for r in rows
                            if r[column.get("Reverse", 0)].strip() != "+"
                            and r[column.get("Potential contaminant", 0)].strip() != "+"]),
                          ("localisation >= 0.75", [r for r in rows if raw_value(r, "Localization prob") >= 0.75])):
        union: set[str] = set()
        for row in subset:
            union.update(part for part in row[column[peptide_field]].split(";") if part.strip())
        mark = "   <- matches the paper's 2,341" if len(union) == 2341 else ""
        print(f"    {label:>34}: {len(union):>6} distinct modified-peptide ids{mark}")
else:
    print("    the site table carries no modified-peptide id column")

print("\nHH — parameter and summary files in the raw store")
found = False
for path in sorted(raw_root(HOME).glob("*/*")):
    if any(word in path.name.lower() for word in ("parameter", "summary", "msms", "peptides")):
        print(f"  {path.parent.name[:12]}  {path.name}  ({path.stat().st_size:,} bytes)")
        found = True
if not found:
    print("  none — the raw store holds the site tables, the protein groups and the supplements only.")
    print("  PRIDE's file listing for PXD018299 would say whether the deposit carries them.")
