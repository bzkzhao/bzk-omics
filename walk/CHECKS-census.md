# CHECKS — the census: 95% of published fold changes contain a drawn value

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round14.py`,
output `notes/logs/round14.txt`. Not an independent path: the same instruments
the registered runs use. **Attempt 3's registered verdict stands.**

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. The census

Data Table S1 has no gaps. Every S1 cell the deposit does not provide — in the
summed column **or at any multiplicity** — is the authors' own imputed draw.
That makes this an enumeration of the published table, not a sample of it.

| class | claims |
|---|---|
| no drawn cell | 40 |
| some drawn, both arms still measured somewhere | 43 |
| **a whole arm drawn, no measured counterpart** | **715** |
| **published fold change contains a drawn value** | **758 of 798 (95%)** |

**Where the comparison can be made** (the 43), |published fold change −
measured-only fold change|:

| quartile | log2 units |
|---|---|
| 25th | 0.691 |
| **median** | **1.055** |
| 75th | 1.524 |
| max | 3.428 |

PKM (`id 1107`) sits at 0.472, at the low end.

**Readings (judged).**
- **95% of the published effect sizes in this table contain at least one value
  the authors drew**, and for 715 of them an entire arm is drawn, so no
  measured counterpart exists at any threshold or population.
- **Where a measured comparison exists, imputation moves the published effect
  size by about a doubling at the median.** That is the magnitude of the draw's
  contribution to published numbers, measured on the authors' own values.
- **This needs no threshold argument and no population argument.** Unlike the
  instability figure, it does not depend on reproducing the paper's selection:
  it reads the published table against the deposit.
- It generalises `walk/CHECKS-draws-and-threshold.md`'s finding about the 14
  named targets (38 of 39 target rows with a wholly drawn arm) from a curated
  list to **the whole published table**.

**What it is not.** It is not a claim that the sites are absent, nor that the
effects are not real. A drawn value is the analysis's estimate of an
unmeasured quantity; the finding is that the published magnitudes rest on those
estimates, at this rate.

## 2. The collateral channel: report the jitter, not the count

Rows whose own values never move still have moving q values, because other rows'
draws move the shared threshold. Measured on those rows: **median q range
0.0015**.

| band around the 0.01 cut | published claims inside it |
|---|---|
| ±0.0007 | 2 of 791 (0.3%) |
| **±0.0015 (the measured jitter)** | **5 of 791 (0.6%)** |
| ±0.0029 | 17 of 791 (2.1%) |

**The channel's reach is small here.** One of 40 fully measured claims was
moved across the cut, a rate of 2.5% with a 95% interval of roughly 0.1% to 13%,
and the band holds about 0.6% of all published claims.

**It earns a taxonomy entry on mechanism, not on frequency.** The rate is
design-specific: it scales with how much of the matrix is drawn and how crowded
the threshold region is, and this deposit is 3-against-3 with a narrow
imputation width. The entry is warranted because **it is why "this claim is
fragile" is never well formed** — fragility is a property of a claim *in a
matrix* — and because no existing class covers support lost through data about
other claims. It also reaches beyond PTM work, to any shared-FDR selection.

## 3. The 2,341: narrowed from "wrong unit" to "unreproducible filter"

The union of the site table's `Mod. peptide IDs`, which is the peptide-level
count the table can provide:

| reading | distinct modified-peptide ids |
|---|---|
| all rows | 2,377 |
| minus reverse and contaminants | **2,359** |
| localisation ≥ 0.75 | 2,271 |

The paper states **2,341**, which sits between the last two: 18 below one, 70
above the other.

**`walk/CHECKS-collateral-and-pkm.md` §3 is superseded.** It concluded the count
"lives at a unit the deposit's processed tables do not provide". The grain is
available; **what cannot be reproduced is the filter**. No combination tried
lands on 2,341.

**Also narrowed:** the claim set itself is site-keyed. The 798 published rows map
one-to-one onto 798 distinct site rows, so only the identification count is
affected. The paper's prose calls site-level rows "peptides", which is loose
usage rather than a different table, and is recorded as such.

## 4. No parameter or summary files

The raw store holds the site tables, the protein groups and the supplements
only. Whether the deposited table was regenerated after the analysis — which
would explain the 23-row gap between 2,318 rows and the stated 2,341, and would
be a defeater instance of a kind this project has no example of — **cannot be
answered from what is held.** PRIDE's file listing for PXD018299 would say.

## 5. What this changes about the headline

Two findings now stand at different evidential levels:

| finding | figure | what it needs |
|---|---|---|
| **the census** | 95% of published fold changes contain a drawn value; median gap 1.055 log2 where comparable | the published table and the deposit. **No threshold, no population, no reconstruction.** |
| selection instability | 26.5% of published claims change support across re-draws | a reconstruction of the paper's selection, whose threshold and population are not recoverable |

**The census is the stronger claim and should lead.** The instability figure
remains the registered result and the answer to H10, but it carries two
unrecoverable conditions; the census carries none.
