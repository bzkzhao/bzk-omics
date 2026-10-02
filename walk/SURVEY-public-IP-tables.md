# SURVEY — public IP tables: PXD018299 interactome + BJC Supplementary Data 1–3, PXD055843 S3 (MEASUREMENT ONLY)

**Run 2026-10-02 in Claude Code's container**, prompt 23 (`notes/prompts/23-survey-public-ip-tables.md`)
with bzk's amendments of the same date. Governing text: `notes/REVIEWER-HANDOFF-2026-10-02.md`
§7.1 (l.101–110) and §6 (l.89–97). Script: `walk/survey_ip_tables.py`, which prints every number
below from the files named in §1; the measurement output is reproduced verbatim in §6. **No schema,
ONTOLOGY, ADR or `bzk/` change.** Nothing here is a design decision.

**Blind.** No gene name, accession or per-row value appears in this file or in the script's output.
Column headers, title rows, counts and per-column deciles only.

## 1. Files

| Source | File | SHA-256 | Verified against |
|---|---|---|---|
| PXD018299 interactome | `HAP1_USP18KO_ISG15_interactome_proteinGroups.xlsx` (4,201,243 bytes) | `214a79cae8ae41143e896fca09d7ab3ee3b894e4dbb4d43f298b388d97fb8ab1` | PRIDE API SHA-1 `b73d05e637a708860aaab27a1807d8a797a7666a`, matched |
| BJC Supplementary Data 1 | `41416_2020_1167_MOESM3_ESM.xlsx` | `e2680e30fd6ea73a327f9e1736eab815245cd16fb1f0c4a8e8f517fa2b88a0db` | `bzk/sources/protein_groups.py` `SUPP_DATA_1`, matched |
| BJC Supplementary Data 2 | `41416_2020_1167_MOESM4_ESM.xlsx` | `da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509` | `SUPP_DATA_2`, matched |
| BJC Supplementary Data 3 | `41416_2020_1167_MOESM5_ESM.xlsx` | `9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca` | `SUPP_DATA_3`, matched |
| PXD055843 Supplementary Data S3 | — | expected `2ea450f3a63721fa6e59898392e8d07d2e002abbb5cf16004340fe838d3f52e9` | **not acquired**, §5 |

- The interactome came from `https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/`.
  The handoff and `ROADMAP.md:12542` call it `ISG15_interactome.xlsx`. The deposit's file is
  `HAP1_USP18KO_ISG15_interactome_proteinGroups.xlsx`, the only file of PXD018299's 3 non-raw
  files (PRIDE API `projects/PXD018299/files`) whose name contains `interactome`.
- BJC files came from Springer's ESM path for doi:10.1038/s41416-020-01167-y
  (`bzk/sources/protein_groups.py:80`). Table 4 was not fetched (amendment 4).

## 2. Per-table fields

**PXD018299 interactome.**
- *Type:* `PerseusAdapter.sniff` → **False**. The header row has no type-prefix stamp, and the 134
  headers are MaxQuant's `proteinGroups` column set.
- *Structure:* 134 named columns. 24 are quantitative: `Intensity 1-1`…`4-3` (4 groups × 3) and
  `LFQ intensity WT-n`, `WT_IFN-n`, `KO-n`, `KO_IFN-n` (4 groups × 3). There are also 15
  categorical, 74 numeric and 21 text columns, classified by content because there is no stamp
  (§6). **No header names a role** (IP, control, input, IgG, mock, beads). The headers do not
  state a control. They also do not state which of `Intensity 1`…`4` is which of the `LFQ` groups.
  Each group has 3 replicates.
- *Full or hits-only:* 3,731 data rows. **No statistics column** (`Q-value` is MaxQuant's
  identification score, `ROADMAP.md:12545`). There is no significance criterion to bin by. The
  table keeps rows marked `Reverse` (40), `Potential contaminant` (108) and `Only identified by
  site` (163).
- *Missingness:* the quantitative block has 89,544 cells: NaN 0, empty 0, **zero 27,658**. Per
  column, the zeros run from 596 to 905 for `Intensity` and from 1,180 to 1,879 for `LFQ intensity`
  (§6).
- *Imputation signs:* the quantitative block **has** missing values (as zeros). No header or
  title contains `imput`. Per-column deciles are in §6. The values span roughly 3e4 to 2e11, on
  a linear scale.

**BJC Supplementary Data 1** (`MOESM3`).
- *Type:* sniff → **True**, with 20 stamped cells in header row 2.
- *Structure:* site grain. The title says this is the GlyGly peptide table for KO+IFN vs WT+IFN,
  shown in Figure 2f. There are 6 quantitative columns (`Intensity KO_IFN_1..3`,
  `Intensity WT_IFN_1..3`), 4 `C:`, 9 `N:`/`M:` and 7 `T:`. No role is named. 3 + 3 replicates.
- *Full or hits-only:* 798 rows. No statistics column. The title row says the rows "are above
  the statistical cut-off values used for proteomic analyses (FDR: 0.01 and s0: 0.1)".
- *Missingness:* 0 of 4,788 cells missing.
- *Imputation signs:* no missing values and no `imput` marker. Deciles are in §6.

**BJC Supplementary Data 2** (`MOESM4`).
- *Type:* sniff → **True**, with 18 stamped cells in header row 2.
- *Structure:* protein grain. The title says it is the KO+IFN vs WT+IFN table, shown in Figure S2b,
  and does not mention IAP-MS. There are 6 quantitative columns (`LFQ intensity KO_IFN_1..3`,
  `WT_IFN_1..3`, with an underscore before the replicate), 3 `C:`, 11 `N:` and 4 `T:`. No role is
  named. 3 + 3 replicates.
- *Full or hits-only:* 25 rows. No statistics column. The title has the same cut-off sentence.
- *Missingness:* 0 of 150 cells missing.
- *Imputation signs:* no missing values and no `imput` marker. Deciles are in §6.

**BJC Supplementary Data 3** (`MOESM5`).
- *Type:* sniff → **True**, with 18 stamped cells in header row 2.
- *Structure:* protein grain. The title reads "Significantly enriched proteins after **ISG15
  IAP-MS** in HAP1 USP18 KO cells treated with IFN compared to wild-type (WT) cells treated with
  IFN … Figure 3e". There are 6 quantitative columns (`LFQ intensity WT_IFN-1..3`,
  `KO_IFN-1..3`), 3 `C:`, 11 `N:` and 4 `T:`. No sample header names a role. The comparison the
  title states is KO+IFN against WT+IFN. 3 + 3 replicates.
- *Full or hits-only:* 323 rows. No statistics column. The title has the same cut-off sentence.
  4 unnamed header columns (25–28) hold 16 non-empty text cells, which are not printed.
- *Missingness:* 0 of 1,938 cells missing.
- *Imputation signs:* no missing values and no `imput` marker. Deciles are in §6. Every column
  holds negative values, with medians between −0.40 and 1.63. That is not the interactome's
  `LFQ intensity` scale. This is a description, not a verdict on the transform.

## 3. PXD018299: is any BJC table a Perseus counterpart of the interactome? (headers, not rows)

- **Supplementary Data 3: yes by sample headers.** All 6 of its sample headers match the
  interactome's headers verbatim: `LFQ intensity WT_IFN-1..3` and `LFQ intensity KO_IFN-1..3`.
  They cover 2 of the interactome's 4 `LFQ` groups. Its title names ISG15 IAP-MS.
- Supplementary Data 1: 0 of 6. It is site grain with `Intensity …_n` headers.
- Supplementary Data 2: 0 of 6 verbatim. It names the same two conditions with `_n` rather than
  `-n`, and its title names no IP.
- Table 4 was not fetched. `ROADMAP.md:12544` records it as hand-curated, with no type prefixes
  and **no per-sample columns**, so it has no sample headers that could match.
- Observation, not repaired (`bzk/` is out of scope): `bzk/sources/protein_groups.py:117` labels
  `SUPP_DATA_3` "(proteins up in WT +IFN)". The file's own title describes enrichment after
  ISG15 IAP-MS in KO+IFN compared to WT+IFN.

## 4. Predictions

| | Prediction | Verdict |
|---|---|---|
| P1 | PXD055843 S3 is a Perseus export of about 4,400 rows, so a full table | **Not measurable.** S3 was not acquired (§5) |
| P2 | Every PXD018299 BJC table is hits-only with no per-row statistics | **Held for Supplementary Data 1–3**, the scope set by amendment 4. None has a statistics column (§2). Each title row states its rows are above the FDR 0.01 / s0 0.1 cut-off. Because there is no statistic, non-significant rows cannot be counted by bin. "Hits-only" rests on the table's own title text |
| P3a | Interactome has no type-prefix stamp | **Held.** sniff is False and the header row has 0 stamped cells (§2) |
| P3b | Interactome is protein grain | **Held.** Its identity columns are `Protein IDs` / `Majority protein IDs` and it uses MaxQuant `proteinGroups` naming (§2) |
| P3c | Interactome has 134 columns | **Held.** 134 named columns and 0 unnamed (§2) |

`ROADMAP.md:12542`'s fourth claim, "no Perseus export deposited", is not re-measured here. Only one
deposit file was read.

## 5. Unreachable and skipped

- **PXD055843 S3: unreachable at the recorded location.** The ORA record
  `https://ora.ox.ac.uk/objects/uuid:49f62049-8742-40b7-b994-ab34667d7ab2` (HTTP 200) offers
  one file, `files/spk02cc75p`, which is `Mukhopadhyay_et_al_2024_USP24_is_an.pdf`
  (`application/pdf`). It has no supplementary data. No other source was tried (amendment 3).
  bzk is to run `walk/survey_ip_tables.py` on his own copy. The script recognises the expected
  digest and prints the same fields, including statistics-column bins and `imput` markers.
- **Skipped under the blindness rule:**
  - the content of SD3's 16 unnamed-column cells;
  - any check of which `Intensity n` group matches which `LFQ` group (that needs per-row values);
  - any per-protein comparison between SD3 and the interactome. The counterpart judgement uses
    headers only.

## 6. Measurement output (verbatim)

Command: `uv run python walk/survey_ip_tables.py <interactome> <MOESM3> <MOESM4> <MOESM5>`, with
the files from §1 under `scratch/survey-23/`.

````markdown
# Survey of public IP tables — measurement output

## PXD018299 ISG15 interactome (HAP1_USP18KO_ISG15_interactome_proteinGroups.xlsx)

- file: `HAP1_USP18KO_ISG15_interactome_proteinGroups.xlsx`
- SHA-256: `214a79cae8ae41143e896fca09d7ab3ee3b894e4dbb4d43f298b388d97fb8ab1`
- sheets: ['HAP1_USP18KO_ISG15_interactome_']
- `PerseusAdapter.sniff` (first sheet): **False** → not a Perseus export (no type-prefix stamp)

### sheet `HAP1_USP18KO_ISG15_interactome_`

- rows in sheet: 3732; widest row: 134 cells
- header row: 1; type-prefix stamped cells in it: 0
- data rows (any non-empty cell under a named header): **3731**
- columns with a named header: 134; unnamed: 0
- non-empty cells under no named header (not printed): 0

Column groups — basis: no stamp: quantitative = per-sample `Intensity`/`LFQ intensity`; others by content (all numeric / ≤10 distinct non-numeric / otherwise text)

- **quantitative** (24): ['Intensity 1-1', 'Intensity 1-2', 'Intensity 1-3', 'Intensity 2-1', 'Intensity 2-2', 'Intensity 2-3', 'Intensity 3-1', 'Intensity 3-2', 'Intensity 3-3', 'Intensity 4-1', 'Intensity 4-2', 'Intensity 4-3', 'LFQ intensity WT-1', 'LFQ intensity WT-2', 'LFQ intensity WT-3', 'LFQ intensity WT_IFN-1', 'LFQ intensity WT_IFN-2', 'LFQ intensity WT_IFN-3', 'LFQ intensity KO-1', 'LFQ intensity KO-2', 'LFQ intensity KO-3', 'LFQ intensity KO_IFN-1', 'LFQ intensity KO_IFN-2', 'LFQ intensity KO_IFN-3']
- **categorical** (15): ['Identification type 1-1', 'Identification type 1-2', 'Identification type 1-3', 'Identification type 2-1', 'Identification type 2-2', 'Identification type 2-3', 'Identification type 3-1', 'Identification type 3-2', 'Identification type 3-3', 'Identification type 4-1', 'Identification type 4-2', 'Identification type 4-3', 'Only identified by site', 'Reverse', 'Potential contaminant']
- **numeric** (74): ['Number of proteins', 'Peptides', 'Razor + unique peptides', 'Unique peptides', 'Peptides 1-1', 'Peptides 1-2', 'Peptides 1-3', 'Peptides 2-1', 'Peptides 2-2', 'Peptides 2-3', 'Peptides 3-1', 'Peptides 3-2', 'Peptides 3-3', 'Peptides 4-1', 'Peptides 4-2', 'Peptides 4-3', 'Razor + unique peptides 1-1', 'Razor + unique peptides 1-2', 'Razor + unique peptides 1-3', 'Razor + unique peptides 2-1', 'Razor + unique peptides 2-2', 'Razor + unique peptides 2-3', 'Razor + unique peptides 3-1', 'Razor + unique peptides 3-2', 'Razor + unique peptides 3-3', 'Razor + unique peptides 4-1', 'Razor + unique peptides 4-2', 'Razor + unique peptides 4-3', 'Unique peptides 1-1', 'Unique peptides 1-2', 'Unique peptides 1-3', 'Unique peptides 2-1', 'Unique peptides 2-2', 'Unique peptides 2-3', 'Unique peptides 3-1', 'Unique peptides 3-2', 'Unique peptides 3-3', 'Unique peptides 4-1', 'Unique peptides 4-2', 'Unique peptides 4-3', 'Sequence coverage [%]', 'Unique + razor sequence coverage [%]', 'Unique sequence coverage [%]', 'Mol. weight [kDa]', 'Sequence length', 'Q-value', 'Score', 'Sequence coverage 1-1 [%]', 'Sequence coverage 1-2 [%]', 'Sequence coverage 1-3 [%]', 'Sequence coverage 2-1 [%]', 'Sequence coverage 2-2 [%]', 'Sequence coverage 2-3 [%]', 'Sequence coverage 3-1 [%]', 'Sequence coverage 3-2 [%]', 'Sequence coverage 3-3 [%]', 'Sequence coverage 4-1 [%]', 'Sequence coverage 4-2 [%]', 'Sequence coverage 4-3 [%]', 'Intensity', 'MS/MS count 1-1', 'MS/MS count 1-2', 'MS/MS count 1-3', 'MS/MS count 2-1', 'MS/MS count 2-2', 'MS/MS count 2-3', 'MS/MS count 3-1', 'MS/MS count 3-2', 'MS/MS count 3-3', 'MS/MS count 4-1', 'MS/MS count 4-2', 'MS/MS count 4-3', 'MS/MS count', 'id']
- **text** (21): ['Protein IDs', 'Majority protein IDs', 'Peptide counts (all)', 'Peptide counts (razor+unique)', 'Peptide counts (unique)', 'Protein names', 'Gene names', 'Fasta headers', 'Sequence lengths', 'Peptide IDs', 'Peptide is razor', 'Mod. peptide IDs', 'Evidence IDs', 'MS/MS IDs', 'Best MS/MS', 'Deamidation (NQ) site IDs', 'GlyGly (K) site IDs', 'Oxidation (M) site IDs', 'Deamidation (NQ) site positions', 'GlyGly (K) site positions', 'Oxidation (M) site positions']

Sample groups as the headers name them (trailing `-n`/`_n` = replicate):

- `Intensity 1`: 3 replicates (1, 2, 3)
- `Intensity 2`: 3 replicates (1, 2, 3)
- `Intensity 3`: 3 replicates (1, 2, 3)
- `Intensity 4`: 3 replicates (1, 2, 3)
- `LFQ intensity WT`: 3 replicates (1, 2, 3)
- `LFQ intensity WT_IFN`: 3 replicates (1, 2, 3)
- `LFQ intensity KO`: 3 replicates (1, 2, 3)
- `LFQ intensity KO_IFN`: 3 replicates (1, 2, 3)
- sample headers naming a role (IP / control / input / IgG / mock / beads): none

Statistics columns (Perseus test naming): none
- `Only identified by site` marked `+`: 163 of 3731 rows
- `Reverse` marked `+`: 40 of 3731 rows
- `Potential contaminant` marked `+`: 108 of 3731 rows

Missingness over the quantitative block (cells under quantitative headers):

- total cells 89544: NaN 0, empty 0, zero 27658, non-numeric text 0, value 61886
- any missing (NaN/empty/zero) in the quantitative block: **True** (27658 of 89544)

| column | NaN | empty | zero | text | value | min, deciles 10–90, max (non-zero finite) |
|---|---|---|---|---|---|---|
| `Intensity 1-1` | 0 | 0 | 596 | 0 | 3135 | 6.745e+04 2.662e+06 8.376e+06 1.61e+07 2.759e+07 4.754e+07 8.285e+07 1.488e+08 3.282e+08 8.784e+08 1.945e+11 |
| `Intensity 1-2` | 0 | 0 | 608 | 0 | 3123 | 1.116e+05 2.693e+06 7.815e+06 1.532e+07 2.648e+07 4.416e+07 7.82e+07 1.427e+08 3.208e+08 8.515e+08 1.929e+11 |
| `Intensity 1-3` | 0 | 0 | 622 | 0 | 3109 | 7.265e+04 2.707e+06 7.747e+06 1.585e+07 2.707e+07 4.595e+07 8.094e+07 1.415e+08 3.224e+08 8.549e+08 1.937e+11 |
| `Intensity 2-1` | 0 | 0 | 616 | 0 | 3115 | 7.271e+04 2.083e+06 6.149e+06 1.197e+07 2.098e+07 3.527e+07 5.906e+07 1.048e+08 2.377e+08 6.717e+08 1.081e+11 |
| `Intensity 2-2` | 0 | 0 | 621 | 0 | 3110 | 5.182e+04 2.287e+06 6.003e+06 1.161e+07 2.032e+07 3.348e+07 5.869e+07 1.063e+08 2.38e+08 6.596e+08 1.063e+11 |
| `Intensity 2-3` | 0 | 0 | 609 | 0 | 3122 | 4.473e+04 1.998e+06 5.938e+06 1.154e+07 2.01e+07 3.314e+07 5.725e+07 1.042e+08 2.38e+08 6.329e+08 9.946e+10 |
| `Intensity 3-1` | 0 | 0 | 905 | 0 | 2826 | 3.103e+04 1.232e+06 3.32e+06 6.141e+06 1.063e+07 1.838e+07 3.369e+07 5.773e+07 1.209e+08 3.295e+08 3.659e+10 |
| `Intensity 3-2` | 0 | 0 | 882 | 0 | 2849 | 5.009e+04 1.032e+06 2.908e+06 5.511e+06 1.029e+07 1.72e+07 3.013e+07 5.24e+07 1.128e+08 3.077e+08 4.041e+10 |
| `Intensity 3-3` | 0 | 0 | 880 | 0 | 2851 | 5.057e+04 9.834e+05 2.854e+06 5.454e+06 1e+07 1.746e+07 3.002e+07 5.208e+07 1.109e+08 3.027e+08 4.89e+10 |
| `Intensity 4-1` | 0 | 0 | 671 | 0 | 3060 | 1.224e+05 2.366e+06 5.704e+06 1.078e+07 1.866e+07 3.229e+07 5.424e+07 9.626e+07 1.951e+08 5.71e+08 1.087e+11 |
| `Intensity 4-2` | 0 | 0 | 681 | 0 | 3050 | 1.111e+05 2.332e+06 5.412e+06 1.086e+07 1.911e+07 3.222e+07 5.538e+07 9.618e+07 2.005e+08 5.62e+08 6.558e+10 |
| `Intensity 4-3` | 0 | 0 | 692 | 0 | 3039 | 9e+04 2.137e+06 5.489e+06 1.089e+07 1.865e+07 3.19e+07 5.423e+07 9.838e+07 1.949e+08 5.555e+08 6.837e+10 |
| `LFQ intensity WT-1` | 0 | 0 | 1574 | 0 | 2157 | 5.458e+05 1.611e+07 2.879e+07 4.429e+07 6.9e+07 1.013e+08 1.624e+08 2.838e+08 5.496e+08 1.353e+09 1.9e+11 |
| `LFQ intensity WT-2` | 0 | 0 | 1570 | 0 | 2161 | 4.837e+05 1.536e+07 2.786e+07 4.372e+07 6.919e+07 1.008e+08 1.661e+08 2.92e+08 5.525e+08 1.38e+09 2.036e+11 |
| `LFQ intensity WT-3` | 0 | 0 | 1569 | 0 | 2162 | 4.374e+05 1.547e+07 2.773e+07 4.455e+07 6.808e+07 1.044e+08 1.639e+08 2.983e+08 5.767e+08 1.372e+09 1.979e+11 |
| `LFQ intensity WT_IFN-1` | 0 | 0 | 1592 | 0 | 2139 | 4.33e+05 1.632e+07 2.826e+07 4.47e+07 6.692e+07 9.99e+07 1.533e+08 2.886e+08 5.363e+08 1.319e+09 1.353e+11 |
| `LFQ intensity WT_IFN-2` | 0 | 0 | 1585 | 0 | 2146 | 6.449e+05 1.582e+07 2.796e+07 4.414e+07 6.42e+07 9.769e+07 1.523e+08 2.893e+08 5.267e+08 1.278e+09 1.384e+11 |
| `LFQ intensity WT_IFN-3` | 0 | 0 | 1547 | 0 | 2184 | 5.983e+04 1.359e+07 2.707e+07 4.159e+07 6.199e+07 9.452e+07 1.51e+08 2.785e+08 5.154e+08 1.235e+09 1.364e+11 |
| `LFQ intensity KO-1` | 0 | 0 | 1879 | 0 | 1852 | 2.104e+05 2.08e+07 3.806e+07 5.794e+07 9.27e+07 1.392e+08 2.131e+08 3.846e+08 6.931e+08 1.656e+09 1.371e+11 |
| `LFQ intensity KO-2` | 0 | 0 | 1851 | 0 | 1880 | 4.984e+05 1.864e+07 3.71e+07 5.732e+07 8.857e+07 1.332e+08 2.052e+08 3.811e+08 6.975e+08 1.622e+09 1.322e+11 |
| `LFQ intensity KO-3` | 0 | 0 | 1768 | 0 | 1963 | 7.611e+05 1.416e+07 3.128e+07 5.239e+07 8.149e+07 1.228e+08 1.96e+08 3.432e+08 6.408e+08 1.583e+09 1.339e+11 |
| `LFQ intensity KO_IFN-1` | 0 | 0 | 1597 | 0 | 2134 | 4.417e+05 1.552e+07 2.894e+07 4.676e+07 6.74e+07 9.581e+07 1.486e+08 2.441e+08 4.655e+08 1.153e+09 9.343e+10 |
| `LFQ intensity KO_IFN-2` | 0 | 0 | 1563 | 0 | 2168 | 3.108e+05 1.367e+07 2.65e+07 4.327e+07 6.466e+07 9.326e+07 1.443e+08 2.386e+08 4.589e+08 1.173e+09 8.278e+10 |
| `LFQ intensity KO_IFN-3` | 0 | 0 | 1180 | 0 | 2551 | 1.425e+05 4.504e+06 1.362e+07 2.62e+07 4.558e+07 6.774e+07 1.08e+08 1.814e+08 3.568e+08 9.356e+08 8.409e+10 |

Imputation markers (any header/title cell containing `imput`): none

## BJC Supplementary Data 1

- file: `41416_2020_1167_MOESM3_ESM.xlsx`
- SHA-256: `e2680e30fd6ea73a327f9e1736eab815245cd16fb1f0c4a8e8f517fa2b88a0db`
- sheets: ['GlyGly peptides significantly u']
- `PerseusAdapter.sniff` (first sheet): **True** → Perseus export

### sheet `GlyGly peptides significantly u`

- rows in sheet: 800; widest row: 26 cells
- header row: 2; type-prefix stamped cells in it: 20
- row 1 above the header (title), verbatim: ['Supplementary Data 1: Significantly enriched GlyGly modified peptides in HAP1 USP18 KO cells treated with IFN compared to wild-type (WT) cells treated with IFN for the same amount of time (48 h.). These peptides, labeled in red in the volcano plot in Figure 2f, are above the statistical cut-off values used for proteomic analyses (FDR: 0.01 and s0: 0.1). ']
- data rows (any non-empty cell under a named header): **798**
- columns with a named header: 26; unnamed: 0
- non-empty cells under no named header (not printed): 0

Column groups — basis: Perseus type prefix (unprefixed = main/quantitative; M: listed as numeric)

- **quantitative** (6): ['Intensity KO_IFN_1', 'Intensity KO_IFN_2', 'Intensity KO_IFN_3', 'Intensity WT_IFN_1', 'Intensity WT_IFN_2', 'Intensity WT_IFN_3']
- **categorical** (4): ['C: Amino acid', 'C: Charge', 'C: Reverse', 'C: Potential contaminant']
- **numeric** (9): ['N: Localization prob', 'N: PEP', 'N: Score', 'N: Delta score', 'N: Score for localization', 'N: Mass error [ppm]', 'N: Intensity', 'N: Position', 'M: Protein group IDs']
- **text** (7): ['T: Proteins', 'T: Positions within proteins', 'T: Leading proteins', 'T: Protein', 'T: Protein names', 'T: Gene names', 'T: Sequence window']

Sample groups as the headers name them (trailing `-n`/`_n` = replicate):

- `Intensity KO_IFN`: 3 replicates (1, 2, 3)
- `Intensity WT_IFN`: 3 replicates (1, 2, 3)
- sample headers naming a role (IP / control / input / IgG / mock / beads): none

Statistics columns (Perseus test naming): none
- `C: Reverse` marked `+`: 0 of 798 rows
- `C: Potential contaminant` marked `+`: 3 of 798 rows

Missingness over the quantitative block (cells under quantitative headers):

- total cells 4788: NaN 0, empty 0, zero 0, non-numeric text 0, value 4788
- any missing (NaN/empty/zero) in the quantitative block: **False** (0 of 4788)

| column | NaN | empty | zero | text | value | min, deciles 10–90, max (non-zero finite) |
|---|---|---|---|---|---|---|
| `Intensity KO_IFN_1` | 0 | 0 | 0 | 0 | 798 | 20.44 21.72 22.25 22.66 23.01 23.28 23.73 24.28 24.88 25.65 29.77 |
| `Intensity KO_IFN_2` | 0 | 0 | 0 | 0 | 798 | 20.22 21.76 22.22 22.7 23.08 23.46 23.86 24.33 25 25.83 30.2 |
| `Intensity KO_IFN_3` | 0 | 0 | 0 | 0 | 798 | 20.34 21.82 22.3 22.76 23.16 23.53 23.94 24.4 25.03 25.87 30.42 |
| `Intensity WT_IFN_1` | 0 | 0 | 0 | 0 | 798 | 18.35 19.21 19.49 19.66 19.81 19.97 20.14 20.31 20.5 20.89 25.67 |
| `Intensity WT_IFN_2` | 0 | 0 | 0 | 0 | 798 | 18.34 19.33 19.63 19.81 19.95 20.1 20.26 20.44 20.64 21.06 25.6 |
| `Intensity WT_IFN_3` | 0 | 0 | 0 | 0 | 798 | 17.56 19.28 19.49 19.67 19.84 19.99 20.12 20.3 20.49 20.86 25.49 |

Imputation markers (any header/title cell containing `imput`): none

## BJC Supplementary Data 2

- file: `41416_2020_1167_MOESM4_ESM.xlsx`
- SHA-256: `da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509`
- sheets: ['Proteins significantly UP in US']
- `PerseusAdapter.sniff` (first sheet): **True** → Perseus export

### sheet `Proteins significantly UP in US`

- rows in sheet: 27; widest row: 24 cells
- header row: 2; type-prefix stamped cells in it: 18
- row 1 above the header (title), verbatim: ['Supplementary Data 2: Significantly enriched proteins in HAP1 USP18 KO cells treated with IFN compared to wild-type (WT) cells treated with IFN for the same amount of time (48 h.). These proteins, labeled in red in the volcano plot in Figure S2b, are above the statistical cut-off values used for proteomic analyses (FDR: 0.01 and s0: 0.1). ']
- data rows (any non-empty cell under a named header): **25**
- columns with a named header: 24; unnamed: 0
- non-empty cells under no named header (not printed): 0

Column groups — basis: Perseus type prefix (unprefixed = main/quantitative; M: listed as numeric)

- **quantitative** (6): ['LFQ intensity KO_IFN_1', 'LFQ intensity KO_IFN_2', 'LFQ intensity KO_IFN_3', 'LFQ intensity WT_IFN_1', 'LFQ intensity WT_IFN_2', 'LFQ intensity WT_IFN_3']
- **categorical** (3): ['C: Only identified by site', 'C: Reverse', 'C: Potential contaminant']
- **numeric** (11): ['N: Peptides', 'N: Razor + unique peptides', 'N: Unique peptides', 'N: Sequence coverage [%]', 'N: Unique + razor sequence coverage [%]', 'N: Unique sequence coverage [%]', 'N: Mol. weight [kDa]', 'N: Q-value', 'N: Score', 'N: Intensity', 'N: MS/MS count']
- **text** (4): ['T: Protein IDs', 'T: Majority protein IDs', 'T: Protein names', 'T: Gene names']

Sample groups as the headers name them (trailing `-n`/`_n` = replicate):

- `LFQ intensity KO_IFN`: 3 replicates (1, 2, 3)
- `LFQ intensity WT_IFN`: 3 replicates (1, 2, 3)
- sample headers naming a role (IP / control / input / IgG / mock / beads): none

Statistics columns (Perseus test naming): none
- `C: Only identified by site` marked `+`: 0 of 25 rows
- `C: Reverse` marked `+`: 0 of 25 rows
- `C: Potential contaminant` marked `+`: 0 of 25 rows

Missingness over the quantitative block (cells under quantitative headers):

- total cells 150: NaN 0, empty 0, zero 0, non-numeric text 0, value 150
- any missing (NaN/empty/zero) in the quantitative block: **False** (0 of 150)

| column | NaN | empty | zero | text | value | min, deciles 10–90, max (non-zero finite) |
|---|---|---|---|---|---|---|
| `LFQ intensity KO_IFN_1` | 0 | 0 | 0 | 0 | 25 | 25.75 26.44 27.35 28.11 28.54 29.87 30.32 30.42 30.87 32.03 33.61 |
| `LFQ intensity KO_IFN_2` | 0 | 0 | 0 | 0 | 25 | 25.53 26.32 27.64 27.98 28.22 29.9 30.12 30.43 31.15 32.17 33.58 |
| `LFQ intensity KO_IFN_3` | 0 | 0 | 0 | 0 | 25 | 25.73 26.3 27.73 28.14 28.84 29.87 30.27 30.48 31.14 32.15 33.42 |
| `LFQ intensity WT_IFN_1` | 0 | 0 | 0 | 0 | 25 | 20.79 21.94 22.74 22.85 23.41 23.54 24.17 26.87 28.52 29.26 30.95 |
| `LFQ intensity WT_IFN_2` | 0 | 0 | 0 | 0 | 25 | 21.03 22.14 22.8 23.06 23.46 23.67 24.32 27.11 28.59 29.26 30.9 |
| `LFQ intensity WT_IFN_3` | 0 | 0 | 0 | 0 | 25 | 20.85 22.31 22.72 23.01 23.27 24.05 24.28 26.79 28.56 29.3 30.92 |

Imputation markers (any header/title cell containing `imput`): none

## BJC Supplementary Data 3

- file: `41416_2020_1167_MOESM5_ESM.xlsx`
- SHA-256: `9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca`
- sheets: ['Proteins significantly UP in US']
- `PerseusAdapter.sniff` (first sheet): **True** → Perseus export

### sheet `Proteins significantly UP in US`

- rows in sheet: 325; widest row: 28 cells
- header row: 2; type-prefix stamped cells in it: 18
- row 1 above the header (title), verbatim: ['Supplementary Data 3: Significantly enriched proteins after ISG15 IAP-MS in HAP1 USP18 KO cells treated with IFN compared to wild-type (WT) cells treated with IFN for the same amount of time (48 h.). These proteins, labeled in red in the volcano plot in Figure 3e, are above the statistical cut-off values used for proteomic analyses (FDR: 0.01 and s0: 0.1). ']
- data rows (any non-empty cell under a named header): **323**
- columns with a named header: 24; unnamed: 4
- non-empty cells under no named header (not printed): 16
  - by (1-based column, content type): col 25 text: 11, col 26 text: 2, col 27 text: 2, col 28 text: 1

Column groups — basis: Perseus type prefix (unprefixed = main/quantitative; M: listed as numeric)

- **quantitative** (6): ['LFQ intensity WT_IFN-1', 'LFQ intensity WT_IFN-2', 'LFQ intensity WT_IFN-3', 'LFQ intensity KO_IFN-1', 'LFQ intensity KO_IFN-2', 'LFQ intensity KO_IFN-3']
- **categorical** (3): ['C: Only identified by site', 'C: Reverse', 'C: Potential contaminant']
- **numeric** (11): ['N: Peptides', 'N: Razor + unique peptides', 'N: Unique peptides', 'N: Sequence coverage [%]', 'N: Unique + razor sequence coverage [%]', 'N: Unique sequence coverage [%]', 'N: Mol. weight [kDa]', 'N: Q-value', 'N: Score', 'N: Intensity', 'N: MS/MS count']
- **text** (4): ['T: Protein IDs', 'T: Majority protein IDs', 'T: Protein names', 'T: Gene names']

Sample groups as the headers name them (trailing `-n`/`_n` = replicate):

- `LFQ intensity WT_IFN`: 3 replicates (1, 2, 3)
- `LFQ intensity KO_IFN`: 3 replicates (1, 2, 3)
- sample headers naming a role (IP / control / input / IgG / mock / beads): none

Statistics columns (Perseus test naming): none
- `C: Only identified by site` marked `+`: 0 of 323 rows
- `C: Reverse` marked `+`: 0 of 323 rows
- `C: Potential contaminant` marked `+`: 12 of 323 rows

Missingness over the quantitative block (cells under quantitative headers):

- total cells 1938: NaN 0, empty 0, zero 0, non-numeric text 0, value 1938
- any missing (NaN/empty/zero) in the quantitative block: **False** (0 of 1938)

| column | NaN | empty | zero | text | value | min, deciles 10–90, max (non-zero finite) |
|---|---|---|---|---|---|---|
| `LFQ intensity WT_IFN-1` | 0 | 0 | 0 | 0 | 323 | -5.992 -4.436 -3.66 -2.368 -1.349 -0.3979 0.6089 1.978 2.918 3.988 9.08 |
| `LFQ intensity WT_IFN-2` | 0 | 0 | 0 | 0 | 323 | -6.228 -4.491 -3.592 -2.455 -1.232 -0.3603 0.6736 1.847 2.947 3.978 8.912 |
| `LFQ intensity WT_IFN-3` | 0 | 0 | 0 | 0 | 323 | -6.331 -4.448 -3.561 -2.319 -1.218 -0.3644 0.6698 1.95 2.918 4.068 8.961 |
| `LFQ intensity KO_IFN-1` | 0 | 0 | 0 | 0 | 323 | -4.662 -1.788 -0.6859 0.3175 0.8427 1.497 2.47 3.359 4.203 5.483 10.73 |
| `LFQ intensity KO_IFN-2` | 0 | 0 | 0 | 0 | 323 | -4.443 -1.85 -0.8306 0.2123 0.9086 1.631 2.478 3.352 4.214 5.506 10.66 |
| `LFQ intensity KO_IFN-3` | 0 | 0 | 0 | 0 | 323 | -4.501 -1.885 -0.7519 0.1767 0.8804 1.549 2.546 3.441 4.26 5.538 10.71 |

Imputation markers (any header/title cell containing `imput`): none

## Sample-header match against the interactome (verbatim, headers only)

- BJC Supplementary Data 1: 0 of 6 sample headers match: []
- BJC Supplementary Data 2: 0 of 6 sample headers match: []
- BJC Supplementary Data 3: 6 of 6 sample headers match: ['LFQ intensity WT_IFN-1', 'LFQ intensity WT_IFN-2', 'LFQ intensity WT_IFN-3', 'LFQ intensity KO_IFN-1', 'LFQ intensity KO_IFN-2', 'LFQ intensity KO_IFN-3']
````
