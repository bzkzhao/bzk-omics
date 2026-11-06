# PXD018299 research audit (report v1)

Generated 2026-10-31T03:12:56+00:00 at commit `45bbd08a1ca7` (DIRTY working tree), Python 3.12.14, numpy 2.5.1.

## 1. Source verification and ingestion  [LIVE]

- **pinned_files**:
  ```json
  {
    "GlyGly site table": {
      "filename": "HAP1_USP18KO_GlyGlyKSites.txt",
      "pinned_sha256": "sha256:a4a503e39581334c3553d3631456ad8aca22e193ba928810f6d46fde15622009",
      "accession": "PXD018299",
      "store_status": "present, hash verified",
      "bytes": 2759052
    },
    "proteinGroups table": {
      "filename": "HAP1_USP18KO_proteinGroups.txt",
      "pinned_sha256": "sha256:669ded1d95285c8f9cc47df7705d85b792609a866ab35a6930afacf83abc9708",
      "accession": "PXD018299",
      "store_status": "present, hash verified",
      "bytes": 16061245
    },
    "BJC Supplementary Data 1": {
      "filename": "41416_2020_1167_MOESM3_ESM.xlsx",
      "pinned_sha256": "sha256:e2680e30fd6ea73a327f9e1736eab815245cd16fb1f0c4a8e8f517fa2b88a0db",
      "accession": "PXD018299",
      "store_status": "present, hash verified",
      "bytes": 197495
    },
    "BJC Supplementary Data 2": {
      "filename": "41416_2020_1167_MOESM4_ESM.xlsx",
      "pinned_sha256": "sha256:da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509",
      "accession": "PXD018299",
      "store_status": "present, hash verified",
      "bytes": 16127
    },
    "BJC Supplementary Data 3": {
      "filename": "41416_2020_1167_MOESM5_ESM.xlsx",
      "pinned_sha256": "sha256:9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca",
      "accession": "PXD018299",
      "store_status": "present, hash verified",
      "bytes": 74388
    }
  }
  ```
- **verified_in_store**: 5
- **of**: 5
- **sequence_archive**: sequence archive last drift-checked 26 day(s) ago over 3,579 sequence(s) — STALE (>7d), run `python -m bzk.drift`

Sources: bzk/sources/pride.py, bzk/sources/protein_groups.py, bzk/drift.py

## 2. Evidence graph reconstruction  [FIXTURE+LIVE]

- **site_table_rows**: 2341
- **after_decoys**: 2298
- **after_localisation**: 2056
- **ingested**: 2029
- **refused**: 27
- **refusals_by_reason**:
  ```json
  {
    "no_razor_pick": 1,
    "residue_mismatch": 15,
    "unresolved_protein": 11
  }
  ```
- **refusal_records**: 27
- **protein_group_ambiguity**:
  ```json
  [
    {
      "artefact": "BJC Supplementary Data 2 (proteins up in USP18-/- +IFN)",
      "column": "T: Majority protein IDs",
      "rows": 25,
      "multi_accession_fraction": 0.72,
      "max_group_size": 6,
      "distinct_gene_multi": 9
    },
    {
      "artefact": "BJC Supplementary Data 2 (proteins up in USP18-/- +IFN)",
      "column": "T: Protein IDs",
      "rows": 25,
      "multi_accession_fraction": 0.88,
      "max_group_size": 28,
      "distinct_gene_multi": 19
    },
    {
      "artefact": "BJC Supplementary Data 3 (proteins up in WT +IFN)",
      "column": "T: Majority protein IDs",
      "rows": 323,
      "multi_accession_fraction": 0.774,
      "max_group_size": 18,
      "distinct_gene_multi": 166
    },
    {
      "artefact": "BJC Supplementary Data 3 (proteins up in WT +IFN)",
      "column": "T: Protein IDs",
      "rows": 323,
      "multi_accession_fraction": 0.9102,
      "max_group_size": 27,
      "distinct_gene_multi": 255
    },
    {
      "artefact": "PXD018299 HAP1_USP18KO_proteinGroups.txt (MaxQuant)",
      "column": "Majority protein IDs",
      "rows": 4797,
      "multi_accession_fraction": 0.7709,
      "max_group_size": 33,
      "distinct_gene_multi": 2707
    },
    {
      "artefact": "PXD018299 HAP1_USP18KO_proteinGroups.txt (MaxQuant)",
      "column": "Protein IDs",
      "rows": 4797,
      "multi_accession_fraction": 0.8616,
      "max_group_size": 57,
      "distinct_gene_multi": 3584
    }
  ]
  ```
- **live_rebuild**:
  ```json
  {
    "exit_code": 1,
    "seconds": 487.5,
    "stdout_tail": [
      "[rebuild] replayed curation_PXD018299.json: 18 node statement(s), 52 edge statement(s)",
      "[rebuild]   ingested HAP1_USP18KO_GlyGlyKSites.txt via maxquant: 2029 site(s), 27 refused, 12766 node statement(s), 10245 edge statement(s), 48,696 quantitative cell(s)",
      "[rebuild] replayed curation_PXD026748.json: 18 node statement(s), 52 edge statement(s)",
      "[rebuild]   ingested GlyGly (K)Sites.txt via maxquant: 2166 site(s), 21 refused, 9762 node statement(s), 10740 edge statement(s), 51,984 quantitative cell(s)",
      "[rebuild] replayed curation_PXD026748_shotgun.json: 16 node statement(s), 38 edge statement(s)",
      "[rebuild]   ingested proteinGroups.txt via maxquant_protein_groups: 4768 protein group(s), 0 refused, 10190 node statement(s), 10189 edge statement(s), 171,648 quantitative cell(s)",
      "[rebuild] replayed curation_PXD055843.json: 23 node statement(s), 63 edge statement(s)",
      "[rebuild]   no adapter recognises Supplementary_Data_S1_TP.xlsx; not ingested",
      "[rebuild] ingestion replay: 4 curation record(s), 3 deposit(s), 4195 site observation(s), 4768 protein observation(s), 48 refusal(s), 32793 node statement(s), 31379 edge statement(s), 272,328 quantitative cell(s), 1 ingestion(s) skipped",
      "[rebuild] sequence archive last drift-checked 26 day(s) ago over 3,579 sequence(s) \u2014 STALE (>7d), run `python -m bzk.drift`",
      "[rebuild] done: 60 tables, 4 curation record(s), 3 deposit(s), 4195 site observation(s), 4768 protein observation(s), 48 refused, 32793 node statement(s), 31379 edge statement(s), 272,328 quantitative cell(s)",
      "[rebuild] INCOMPLETE: 1 curation record(s) named a deposit that was not ingested. The stores are written and are a subset of the export \u2014 run `python -m bzk.sources.pride` and rebuild (OPERATIONS.md \u00a75)"
    ],
    "stderr_tail": [],
    "home": "/Users/bzk/.bzk-omics"
  }
  ```
- _Limitation_: Refusals and ambiguity are the committed fixtures' record of the last generating run, not a rebuild performed now.

Sources: tests/fixtures/pxd018299_refusals.json, tests/fixtures/pxd018299_platform_targets.json, tests/fixtures/pxd018299_protein_groups.json

## 3. Published-claim alignment and measurement census  [FIXTURE]

- **published_claims**: 798
- **claims_in_tested_population**: 791
- **tested_claims_with_an_imputed_cell**: 751
- **tested_claims_fully_measured**: 40
- **claims_lost_before_test_by_stage**:
  ```json
  {
    "localisation": 33,
    "significance": 237,
    "ingestion": 6,
    "presence": 7,
    "decoy_contaminant": 3
  }
  ```
- **reading**: Counts cover the claims that reach the test. Claims lost earlier never enter the matrix, and the fixture does not record how many of them are wholly drawn.
- _NOT_AUTOMATED_: The whole-table census over all published claims (drawn-cell classes, the measured-only fold-change comparison) and the count of contrasts with no observed values: produced by notes/scripts/diagnose_round14.py, needs the raw store, records in walk/CHECKS-census.md.

Sources: tests/fixtures/pxd018299_h10_attempt3.json, tests/fixtures/pxd018299_published_cascade.json

## 4. Perseus imputation reconstruction  [FIXTURE]

- **matrix**: deposit, not the published S1
- **rule**: A cell is an imputed cell when the DEPOSIT reports no value for it, never when its published value falls below a cut-off. PREREG §3: identifying them by value would be the circularity this readout exists to avoid. Estimation only — it locates the published run and changes no family member and no primary readout.
- **per_sample**:
  ```json
  {
    "Intensity KO_IFN_1": {
      "n_imputed": 38,
      "downshift_sd": 1.767,
      "width_sd": 0.241
    },
    "Intensity KO_IFN_2": {
      "n_imputed": 49,
      "downshift_sd": 1.695,
      "width_sd": 0.226
    },
    "Intensity KO_IFN_3": {
      "n_imputed": 49,
      "downshift_sd": 1.791,
      "width_sd": 0.282
    },
    "Intensity WT_IFN_1": {
      "n_imputed": 738,
      "downshift_sd": 2.441,
      "width_sd": 0.486
    },
    "Intensity WT_IFN_2": {
      "n_imputed": 735,
      "downshift_sd": 2.171,
      "width_sd": 0.461
    },
    "Intensity WT_IFN_3": {
      "n_imputed": 742,
      "downshift_sd": 2.577,
      "width_sd": 0.509
    }
  }
  ```
- **per_sample_downshift_range**:
  ```json
  [
    1.695,
    2.577
  ]
  ```
- **whole_matrix**:
  ```json
  {
    "n_imputed": 2351,
    "downshift_sd": 2.461,
    "width_sd": 0.414
  }
  ```
- _Limitation_: Per-sample downshift differs sharply between arms (the WT columns carry most of the drawn cells), so a single downshift number hides that structure.
- _NOT_AUTOMATED_: The two-route downshift recovery quoted in walk/FINDINGS.md section 2 (drawn cells against column statistics; fold-change gap against measured-only part) is produced by notes/scripts/diagnose_imputation_effects.py and recorded in walk/CHECKS-two-route-recovery.md. It is not in any committed fixture, and the per-sample range above (this fixture's readout C) is a different statistic that should not be read as that figure.

Sources: tests/fixtures/pxd018299_h10_attempt3.json

## 5. Differential analysis and target recovery  [FIXTURE]

- **tested_sites**: 1362
- **significant_up**: 516
- **values_imputed**: 3997
- **values_total**: 8172
- **imputed_fraction**: 0.4891
- **targets_present**: 13
- **targets_recovered**: 12
- **targets_total**: 14
- **target_status_counts**:
  ```json
  {
    "recovered": 12,
    "absent_from_tested": 1,
    "tested_not_recovered": 1
  }
  ```
- **welch_baseline_targets**: 14
- **recovery_rule_note**: platform rule: recovered if any tested site for the target is significant; the notebook baseline selects best site by log2FC. Different rules - see python -m bzk.target_recovery_rules.

Sources: tests/fixtures/pxd018299_platform_targets.json, tests/fixtures/pxd018299_welch_baseline.json

## 6. Stochastic imputation sensitivity  [FIXTURE]

- **claims**: 791
- **default_cell**:
  ```json
  {
    "width_sd": 0.3,
    "downshift_sd": 1.8,
    "scope": "per_sample",
    "draws": 20
  }
  ```
- **changing_in_default_cell**: 159
- **changing_in_default_cell_share**: 0.201
- **family_members**: 360
- **changing_somewhere_in_family**: 479
- **supported_in_every_default_draw**: 631
- **supported_in_no_default_draw**: 1
- **per_claim_csv**: audit-out-live/per_claim_selection_frequency.csv
- _NOT_AUTOMATED_: walk/FINDINGS.md section 5 quotes a changing-support count under 'Perseus's documented FDR rule at the recovered imputation parameters, 20 paired draws'. That is the output of notes/scripts/diagnose_round11.py / diagnose_round12.py (walk/CHECKS-draws-and-threshold.md), a different instrument from the registered attempt-3 family computed here, and it is not reproduced by this fixture. Do not quote the two interchangeably.

Sources: tests/fixtures/pxd018299_h10_attempt3.json

## 7. Multiple-testing propagation  [FIXTURE]

- **fully_measured_claims**: 40
- **moved_across_cut_in_family**: 3
- **moved_across_cut_in_default_cell**: 0
- **claims**:
  ```json
  [
    {
      "published_row": 280,
      "deposit_id": "859",
      "gene_names": "ALDOA",
      "supported_in_family": "294/360",
      "supported_in_default_cell": "20/20"
    },
    {
      "published_row": 294,
      "deposit_id": "889",
      "gene_names": "ATP1A1;ATP1A2;ATP1A3",
      "supported_in_family": "184/360",
      "supported_in_default_cell": "20/20"
    },
    {
      "published_row": 577,
      "deposit_id": "1623",
      "gene_names": "HIST1H4A",
      "supported_in_family": "347/360",
      "supported_in_default_cell": "20/20"
    }
  ]
  ```
- **mechanism**: A fully measured claim has a frozen statistic; any change in its support comes from draws made for other rows moving the shared FDR threshold.
- _NOT_AUTOMATED_: q-value ranges per claim (e.g. the ATP1A1 K605 range in walk/FINDINGS.md section 6) are not stored in the fixture, which keeps support as 0/1. Source: notes/scripts/diagnose_round12.py, walk/CHECKS-draws-and-threshold.md.

Sources: tests/fixtures/pxd018299_h10_attempt3.json

## 8. Biological discrepancy inspection  [FIXTURE]

- **instruments**:
  ```json
  {
    "platform_path": "Welch, BH-FDR, ingested + presence-filtered population (stage 5)",
    "reconstruction_default_cell": "attempt-3 Perseus-shaped test, median support over the default cell's draws, population retains the published claim set (stages 6-7)"
  }
  ```
- **targets**:
  ```json
  [
    {
      "gene": "ADAR",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 4,
        "best_adj_p": 0.0019,
        "best_log2fc": 1.343
      },
      "reconstruction_default_cell": "1/2 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "EIF2AK2",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 7,
        "best_adj_p": 0.0008,
        "best_log2fc": 5.013
      },
      "reconstruction_default_cell": "4/4 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "DDX58",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 4,
        "best_adj_p": 0.0009,
        "best_log2fc": 2.736
      },
      "reconstruction_default_cell": "4/4 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "DDX60",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 4,
        "best_adj_p": 0.0021,
        "best_log2fc": 2.864
      },
      "reconstruction_default_cell": "2/2 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "DHX58",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 1,
        "best_adj_p": 0.0199,
        "best_log2fc": 3.038
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "OAS1",
      "platform_path": {
        "status": "absent_from_tested",
        "tested_sites": 0,
        "best_adj_p": null,
        "best_log2fc": null
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": true
    },
    {
      "gene": "OAS2",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 7,
        "best_adj_p": 0.0004,
        "best_log2fc": 4.65
      },
      "reconstruction_default_cell": "5/6 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "IFIH1",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 1,
        "best_adj_p": 0.0013,
        "best_log2fc": 6.073
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "STAT1",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 4,
        "best_adj_p": 0.0005,
        "best_log2fc": 5.574
      },
      "reconstruction_default_cell": "3/3 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "PSMB9",
      "platform_path": {
        "status": "tested_not_recovered",
        "tested_sites": 1,
        "best_adj_p": 0.1148,
        "best_log2fc": 1.401
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": true
    },
    {
      "gene": "PSMB10",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 1,
        "best_adj_p": 0.0068,
        "best_log2fc": 3.032
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "PSMA7",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 2,
        "best_adj_p": 0.0059,
        "best_log2fc": 3.535
      },
      "reconstruction_default_cell": "2/2 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "PSME2",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 1,
        "best_adj_p": 0.0424,
        "best_log2fc": 3.884
      },
      "reconstruction_default_cell": "1/1 S1 peptides supported",
      "instruments_disagree": false
    },
    {
      "gene": "TAP1",
      "platform_path": {
        "status": "recovered",
        "tested_sites": 2,
        "best_adj_p": 0.0048,
        "best_log2fc": 2.379
      },
      "reconstruction_default_cell": "2/2 S1 peptides supported",
      "instruments_disagree": false
    }
  ]
  ```
- **not_recovered_on_platform_path**:
  ```json
  [
    "OAS1",
    "PSMB9"
  ]
  ```
- **instruments_disagree_on**:
  ```json
  [
    "OAS1",
    "PSMB9"
  ]
  ```
- **protein_group_ambiguity_artefacts**:
  ```json
  [
    "BJC Supplementary Data 2 (proteins up in USP18-/- +IFN) [T: Majority protein IDs]",
    "BJC Supplementary Data 2 (proteins up in USP18-/- +IFN) [T: Protein IDs]",
    "BJC Supplementary Data 3 (proteins up in WT +IFN) [T: Majority protein IDs]",
    "BJC Supplementary Data 3 (proteins up in WT +IFN) [T: Protein IDs]",
    "PXD018299 HAP1_USP18KO_proteinGroups.txt (MaxQuant) [Majority protein IDs]",
    "PXD018299 HAP1_USP18KO_proteinGroups.txt (MaxQuant) [Protein IDs]"
  ]
  ```
- _Limitation_: The two instruments use different populations, so a target can be absent or non-significant on one and supported on the other. This stage does not adjudicate.

Sources: tests/fixtures/pxd018299_platform_targets.json, tests/fixtures/pxd018299_h10_attempt3.json

## 9. Evidence report and export  [FIXTURE]

- **written**:
  ```json
  [
    "audit-out-live/audit_PXD018299.json",
    "audit-out-live/audit_PXD018299.md"
  ]
  ```
- **published_claim_cascade_report**: python -m bzk.published_cascade

Sources: this module

## 10. Reasons for every rejection and non-recovery, and drift  [FIXTURE]

- **published_claims_lost**: 286
- **by_stage_and_reason**:
  ```json
  {
    "localisation/localization_prob_below_threshold": 33,
    "significance/p_value": 179,
    "significance/both": 44,
    "significance/fold_change": 14,
    "ingestion/residue_mismatch": 4,
    "presence/presence_rule": 7,
    "decoy_contaminant/potential_contaminant": 3,
    "ingestion/unresolved_protein": 2
  }
  ```
- **ingestion_losses_joined_to_refusal_detail**: 6
- **ingestion_losses_total**: 6
- **platform_refusals_total**: 27
- **unrecovered_targets**:
  ```json
  [
    {
      "gene": "OAS1",
      "status": "absent_from_tested",
      "explanation": "no site of this gene reached the tested population",
      "tested_sites": []
    },
    {
      "gene": "PSMB9",
      "status": "tested_not_recovered",
      "explanation": "tested, no site passed the significance rule",
      "tested_sites": [
        {
          "site": "uniprot:P28065#sv2#K53#unimod:121",
          "log2fc": 1.4007282630495936,
          "p": 0.0658237329669327,
          "adj_p": 0.11479119628804396
        }
      ]
    }
  ]
  ```
- **written**:
  ```json
  [
    "audit-out-live/rejected_published_claims.csv",
    "audit-out-live/ingestion_refusals.csv"
  ]
  ```
- **drift**: not run (needs --drift: refetches every archived sequence)
- _Limitation_: Reason codes on lost published claims are labels, not sentences; only ingestion refusals carry prose, and the join is on site-table row.

Sources: tests/fixtures/pxd018299_published_cascade.json, tests/fixtures/pxd018299_refusals.json, tests/fixtures/pxd018299_platform_targets.json

## Fixture hashes (sha256)

- `pxd018299_h10_attempt3.json`: `1893f2acff733edfe6fbbb4092a4993739291722cff8e4816e5c439544059748`
- `pxd018299_platform_targets.json`: `a900600140838191b2939d4d9538fe9a7010ffb56df33ccfcac6907590adab7b`
- `pxd018299_protein_groups.json`: `2d40b1bd544e570b9aefbf1ef27c3c66c8384194ae11af2988b13b18240f7e8e`
- `pxd018299_published_cascade.json`: `5f0911e6ce7d5652a197d65720c9d0fb35c5ee789e9414e74b3c23215a4efb3c`
- `pxd018299_refusals.json`: `60b934dad697c73efe7e37319a34d34a168cd11933ed7160164e40f14b0415ab`
- `pxd018299_welch_baseline.json`: `76fc738bcc639bcd04e2810621dc2c6fa7c63ca63897c1dc7100a84c0a1e06f1`
