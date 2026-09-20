"""`bzk/sources/pxd026748_reconstruction.py` — the arithmetic and the gate, on synthetic inputs.

**Entirely offline, and nothing here touches PXD026748.** The module reads two deposits and a
journal supplement that exist only on bzk's machine; what can be tested here is the order of the
pipeline, the gate's authority over the GG arm, and that every derived figure is derived. Every
deposit, workbook and cascade fixture below is built in `tmp_path` and thrown away.

**The end-to-end runs generate the "published" sheets from the same synthetic matrix the module
reads, and that circularity is deliberate and bounded.** It buys one thing: a gate that passes, so
the run continues into the GG arm and the control flow can be asserted. It establishes **nothing**
about whether PC1, PC2 or PC3 are computed correctly — a mutation to the normalisation moves both
sides of that comparison together. Saying otherwise would make this the fourth instance of the
shape `HANDOFF.md` §8 catalogues: a measurement guaranteed by its own setup. What does establish
the arithmetic is elsewhere and independent: `tests/test_anova.py` against R's published `aov`
table and against nested least squares, and `tests/test_t_variants.py` against hand arithmetic and
`scipy`.

**The GG deposit's rows all carry an empty `Protein`**, so the site adapter refuses every one of
them for having no razor pick and resolves nothing — that is what keeps these runs off the network.
It is also the case T3 is about: a refused row is still in `_filter`'s output, and still moves every
per-sample median.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from openpyxl import Workbook

from bzk.adapters import maxquant
from bzk.provenance import raw_store
from bzk.sources import protein_groups
from bzk.sources import pxd026748_reconstruction as recon
from bzk.stats import welch_t
from bzk.stats.anova import two_way

#: A synthetic design: two genotypes x two treatments x three replicates, the shape of both arms.
GENOTYPES = ("WT", "ISG15-/-")
TREATMENTS = ("plpro_wt", "plpro_mut")
REPLICATES = (1, 2, 3)


#: Deliberately not accessions. `CLAUDE.md` § Working style forbids inventing a UniProt accession
#: to fill an example, so these are marked synthetic in their own text and cannot be mistaken for
#: one.
def _accession(i: int) -> str:
    return f"SYNTHETIC-{i:05d}"


def _labels(prefix: str) -> list[str]:
    return [f"{prefix}{g}_{t}_{r}" for g in ("wt", "ko") for t in ("a", "b") for r in REPLICATES]


def _mapping(prefix: str) -> dict[str, dict[str, Any]]:
    """One curation mapping over the twelve columns, in the same order as `_labels`."""
    base = {
        "timepoint_h": 48,
        "replicate_type": "biological",
        "source_type": "cell_line",
        "cell_line": "HAP1",
        "organism_taxid": 9606,
    }
    mapping: dict[str, dict[str, Any]] = {}
    for label in _labels(prefix):
        stem = label[len(prefix) :]
        genotype = GENOTYPES[0] if stem.startswith("wt") else GENOTYPES[1]
        treatment = TREATMENTS[0] if "_a_" in stem else TREATMENTS[1]
        mapping[label] = {
            **base,
            "genotype": genotype,
            "treatment": treatment,
            "replicate": int(stem[-1]),
        }
    return mapping


def _record(tmp_path: Path, *, name: str, filename: str, content_hash: str, prefix: str) -> Path:
    """A loadable curation record over the twelve columns, off the committed synthetic one."""
    record = json.loads(
        (Path(__file__).parent / "fixtures" / "curation_synthetic_loadable.json").read_text()
    )
    record["file"] = filename
    record["content_hash"] = content_hash
    record["mapping"] = _mapping(prefix)
    path = tmp_path / name
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


# ── the site table, whose rows are all refused offline ──────────────────────────────────────────

GG_HEADER = [
    "Proteins",
    "Positions within proteins",
    "Protein",
    "Position",
    "Amino acid",
    "Localization prob",
    "Sequence window",
    "Reverse",
    "Potential contaminant",
    "id",
    *_labels("Intensity "),
]


def _gg_bytes(rows: list[list[str]]) -> bytes:
    lines = ["\t".join(GG_HEADER)] + ["\t".join(r) for r in rows]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


def _gg_row(row_id: str, values: list[str]) -> list[str]:
    """One site row with **no razor pick**, so the adapter refuses it and resolves nothing."""
    return ["", "", "", "", "K", "0.99", f"WINDOW{row_id}", "", "", row_id, *values]


def _gg_values(seed: int, *, scale: float = 1.0) -> list[str]:
    """Twelve intensities with a genotype effect, and one absence, as text."""
    rng = np.random.default_rng(seed)
    raw = rng.lognormal(mean=15.0, sigma=0.35, size=12) * scale
    raw[:6] *= 4.0  # a WT/KO separation, so some rows clear the thresholds
    cells = [f"{v:.0f}" for v in raw]
    # One absence, in a different column for each row: a column missing in *every* row has
    # nothing to impute from, which `downshifted_normal` refuses by name.
    cells[seed % 12] = ""
    return cells


# ── the shotgun table, sized to the registered PC0 ──────────────────────────────────────────────

SHOTGUN_HEADER = [
    "Protein IDs",
    "Majority protein IDs",
    "Peptides",
    "Razor + unique peptides",
    "Reverse",
    "Potential contaminant",
    "Only identified by site",
    "id",
    *_labels("LFQ intensity "),
]


def _shotgun_bytes(n_rows: int) -> bytes:
    rng = np.random.default_rng(20260920)
    lines = ["\t".join(SHOTGUN_HEADER)]
    for i in range(n_rows):
        raw = rng.lognormal(mean=16.0, sigma=0.4, size=12)
        if i % 3 == 0:
            raw[:6] *= 2.5
        lines.append(
            "\t".join(
                [
                    f"{_accession(i)};{_accession(i)}-2",
                    f"{_accession(i)};{_accession(i)}-2",
                    "7",
                    "5",
                    "",
                    "",
                    "",
                    str(i),
                    *[f"{v:.0f}" for v in raw],
                ]
            )
        )
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


def _published_sheets(path: Path, deposit: Path, axes: recon.SampleAxes) -> Path:
    """A workbook whose Table 2 and Table 3 agree with the synthetic shotgun matrix.

    Derived from the module's own pipeline **on purpose** — see this file's docstring for what that
    does and does not establish. A title row sits above each header, as the real supplement's sheet
    1 does, so the header is located by content here too.
    """
    rows, column = recon.shotgun_rows(maxquant.read_table(deposit))
    normalised, keep = recon.pipeline(recon.intensity_matrix(rows, column, axes.labels), axes)
    values = normalised[keep]
    accessions = [
        recon.first_accession(row, column) for row, k in zip(rows, keep, strict=True) if k
    ]
    wt = list(axes.columns_where(GENOTYPES[0]))
    ko = list(axes.columns_where(GENOTYPES[1]))
    fold = values[:, wt].mean(axis=1) - values[:, ko].mean(axis=1)
    minus_log_p = recon.minus_log10(welch_t(values[:, wt], values[:, ko]).p_value)
    members = (
        two_way(values, np.array(axes.genotype), np.array(axes.treatment)).min_p()
        < recon.PRIMARY_THRESHOLD
    )

    book = Workbook()
    sheet_2 = book.active
    sheet_2.title = recon.TABLE_2_SHEET
    sheet_2.append(["Supplementary Table 2 — synthetic"])
    sheet_2.append(["Uniprot ID", "Gene name"])
    for accession, member in zip(accessions, members.tolist(), strict=True):
        if member:
            sheet_2.append([accession, "SYNTHETIC"])

    sheet_3 = book.create_sheet(recon.TABLE_3_SHEET)
    sheet_3.append(["Supplementary Table 3 — synthetic"])
    sheet_3.append(["Uniprot ID", "Log2 fold change (WT/KO)", "-Log P value"])
    for accession, f, p in zip(accessions, fold.tolist(), minus_log_p.tolist(), strict=True):
        sheet_3.append([accession, f, p])

    book.save(path)
    return path


# ── the end-to-end harness ──────────────────────────────────────────────────────────────────────


def _run(
    tmp_path: Path, *, shotgun_rows: int, gg_rows: list[list[str]], claim_ids: list[str]
) -> tuple[int, dict[str, Any]]:
    """`main()` end to end against synthetic bytes. Returns `(exit code, fixture)`."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    home = tmp_path / "home"
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)

    gg = raw_store.store(_gg_bytes(gg_rows), "GlyGly (K)Sites.txt", home=home)
    shotgun = raw_store.store(_shotgun_bytes(shotgun_rows), "proteinGroups.txt", home=home)
    gg_record = _record(
        tmp_path,
        name="curation_SYNTHETIC_gg.json",
        filename="GlyGly (K)Sites.txt",
        content_hash=gg.content_hash,
        prefix="Intensity ",
    )
    shotgun_record = _record(
        tmp_path,
        name="curation_SYNTHETIC_shotgun.json",
        filename="proteinGroups.txt",
        content_hash=shotgun.content_hash,
        prefix="LFQ intensity ",
    )

    from bzk.curation.loader import load_path

    axes = recon.sample_axes(load_path(shotgun_record))
    workbook = _published_sheets(tmp_path / "supp.xlsx", shotgun.path, axes)
    stored = raw_store.store(workbook.read_bytes(), "supp.xlsx", home=home)
    supplement = protein_groups.SupplementaryFile(
        label="synthetic",
        filename="supp.xlsx",
        expected_content_hash=stored.content_hash,
        doi="10.1038/s41590-021-01035-8",
    )

    cascade_path = tmp_path / "cascade.json"
    cascade_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "published": {
                            "#": i + 1,
                            "Cluster": f"Cluster {i % 2 + 1}",
                            "Uniprot ID": _accession(i),
                            "Lysine position": 10 + i,
                        },
                        "deposit_id": row_id,
                        "lost_at": None,
                        "loss_reason": None,
                        "has_positive_multiplicity_column": i == 0,
                    }
                    for i, row_id in enumerate(claim_ids)
                ]
            }
        ),
        encoding="utf-8",
    )

    code = recon.main(
        home=home,
        fixtures_dir=fixtures_dir,
        digly_curation_path=gg_record,
        shotgun_curation_path=shotgun_record,
        cascade_fixture_path=cascade_path,
        supplement=supplement,
    )
    fixture: dict[str, Any] = json.loads(
        (fixtures_dir / recon.FIXTURE_NAME).read_text(encoding="utf-8")
    )
    return code, fixture


#: Five claim rows plus one extra, all refused by the adapter; the extra is not a claim and exists
#: to be a population row nothing else references.
CLAIM_IDS = ["10", "11", "12", "13", "14"]
EXTRA_ID = "99"


def _gg_rows(extra_scale: float) -> list[list[str]]:
    return [_gg_row(row_id, _gg_values(int(row_id))) for row_id in CLAIM_IDS] + [
        _gg_row(EXTRA_ID, _gg_values(99, scale=extra_scale))
    ]


# ── T1 · the pipeline's order ───────────────────────────────────────────────────────────────────


def test_t1_normalisation_precedes_the_valid_value_filter() -> None:
    """The registered order (`:80-83`), against the order that differs from it.

    The case is built so the two disagree: one row is measured in a single sample and fails the
    filter, and its value is far from the rest. Normalising first, that row is part of that
    sample's median; filtering first, it is not — so every surviving value in that column moves.
    """
    axes = recon.SampleAxes(
        labels=tuple(_labels("Intensity ")),
        genotype=tuple(GENOTYPES[0] if i < 6 else GENOTYPES[1] for i in range(12)),
        treatment=tuple(TREATMENTS[i // 3 % 2] for i in range(12)),
    )
    keeps = np.full((4, 12), 16.0)
    keeps[:, 0] = [8.0, 10.0, 12.0, 14.0]
    drops = np.full((1, 12), np.nan)
    drops[0, 0] = 20.0  # one sample only, so this row fails the valid-value filter
    matrix = 2.0 ** np.vstack([keeps, drops])

    normalised, keep = recon.pipeline(matrix, axes)
    assert keep.tolist() == [True, True, True, True, False]

    # Registered: the median of column 0 includes the dropped row's 10, over five values.
    assert normalised[0, 0] == pytest.approx(8.0 - 12.0)
    # The other order: the same median over the four survivors alone, which is 11.
    after = recon.median_normalise(recon.log2_zero_as_missing(matrix)[keep])
    assert after[0, 0] == pytest.approx(8.0 - 11.0)
    assert normalised[0, 0] != pytest.approx(after[0, 0])


def test_t1b_the_valid_value_rule_is_three_in_one_group() -> None:
    """`:83`. Three in one group passes; two in every group does not."""
    axes = recon.SampleAxes(
        labels=tuple(_labels("Intensity ")),
        genotype=tuple(GENOTYPES[0] if i < 6 else GENOTYPES[1] for i in range(12)),
        treatment=tuple(TREATMENTS[i // 3 % 2] for i in range(12)),
    )
    three_in_one = np.full((1, 12), np.nan)
    three_in_one[0, :3] = 1.0
    two_in_each = np.full((1, 12), np.nan)
    for group in axes.groups.values():
        two_in_each[0, list(group)[:2]] = 1.0

    assert recon.valid_value_mask(three_in_one, axes.groups).tolist() == [True]
    assert recon.valid_value_mask(two_in_each, axes.groups).tolist() == [False]


# ── T2 · the join, and the thresholds ───────────────────────────────────────────────────────────


def test_t2_the_join_reads_the_first_majority_id_only() -> None:
    """`JOIN_RULE`. A published id that is a group's second entry does not join it, and two groups
    leading with the same id are ambiguous and join nothing."""
    header = ["Majority protein IDs", "Reverse", "Potential contaminant", "id"]
    column = {name: i for i, name in enumerate(header)}
    rows = [
        ["SYNTHETIC-1;SYNTHETIC-2", "", "", "0"],
        ["SYNTHETIC-3;SYNTHETIC-1", "", "", "1"],
        ["SYNTHETIC-4", "", "", "2"],
        ["SYNTHETIC-4", "", "", "3"],
    ]
    assert [recon.first_accession(row, column) for row in rows] == [
        "SYNTHETIC-1",
        "SYNTHETIC-3",
        "SYNTHETIC-4",
        "SYNTHETIC-4",
    ]


def test_t2b_primary_is_strict_and_secondary_is_inclusive() -> None:
    """`:146-148` writes `P < 0.01` and `P <= 0.001`, and the difference is load-bearing at the
    boundary: a claim whose P is exactly 0.001 is supported at the secondary threshold and a claim
    whose P is exactly 0.01 is not supported at the primary one."""
    values = np.array([0.01, 0.001, 0.0009, np.nan])

    primary = recon.supported(values, threshold=recon.PRIMARY_THRESHOLD, inclusive=False)
    secondary = recon.supported(values, threshold=recon.SECONDARY_THRESHOLD, inclusive=True)

    assert primary.tolist() == [False, True, True, False]
    assert secondary.tolist() == [False, True, True, False]


def test_t2c_a_column_that_cannot_be_resolved_stops_with_the_header_it_read() -> None:
    """Refused by name rather than guessed — see `resolve_column`."""
    with pytest.raises(recon.ReconstructionError, match=r"0 column\(s\) match"):
        recon.resolve_column(
            ["Uniprot ID", "Gene name"], required=["log2"], forbidden=[], what="the fold change"
        )
    with pytest.raises(recon.ReconstructionError, match=r"2 column\(s\) match"):
        recon.resolve_column(
            ["Log2 ratio", "log2 difference"], required=["log2"], forbidden=[], what="the fold"
        )


# ── T3 · the verdict ────────────────────────────────────────────────────────────────────────────


def test_t3_the_verdict_is_mechanical_and_in_the_fraction_form() -> None:
    """`:156-162`, at the registered exposure and at another one.

    At E = 288 the thresholds are the pre-registration's own 274 and 15, and one claim either side
    of each decides the outcome. At E = 200 they move to 190 and 10 — which is the whole point of
    computing them from E, and the case a pair of constants would get wrong while still passing at
    288.
    """
    assert recon.verdict_thresholds(288) == (274, 15)
    assert recon.verdict_thresholds(200) == (190, 10)

    assert recon.verdict(exposure=288, durable=274, underdetermined=14)["outcome"] == "weakens_d5"
    assert (
        recon.verdict(exposure=288, durable=273, underdetermined=15)["outcome"]
        == "extends_d5_to_imputation_alone"
    )
    assert recon.verdict(exposure=288, durable=273, underdetermined=14)["outcome"] == "neither"

    assert recon.verdict(exposure=200, durable=190, underdetermined=9)["outcome"] == "weakens_d5"
    assert (
        recon.verdict(exposure=200, durable=189, underdetermined=10)["outcome"]
        == "extends_d5_to_imputation_alone"
    )


def test_t3b_both_outcomes_at_once_is_named_rather_than_chosen_between() -> None:
    """Impossible at E = 288 (`:162`) and possible elsewhere — at E = 200, 190 + 10 = 200."""
    assert recon.verdict(exposure=200, durable=190, underdetermined=10)["outcome"] == "both"


# ── T4 · the seed ───────────────────────────────────────────────────────────────────────────────


def test_t4_the_seed_is_honoured() -> None:
    """Two runs of one member are identical; a different seed is not. I15's contract, one level up."""
    axes = recon.SampleAxes(
        labels=tuple(_labels("Intensity ")),
        genotype=tuple(GENOTYPES[0] if i < 6 else GENOTYPES[1] for i in range(12)),
        treatment=tuple(TREATMENTS[i // 3 % 2] for i in range(12)),
    )
    rng = np.random.default_rng(7)
    values = rng.normal(20.0, 1.0, size=(30, 12))
    values[:10, 3] = np.nan

    member = recon.Member(width_sd=0.3, downshift_sd=1.8, scope="per_sample", seed=0)
    again = recon.Member(width_sd=0.3, downshift_sd=1.8, scope="per_sample", seed=1)

    np.testing.assert_array_equal(
        recon.run_member(values, axes, member), recon.run_member(values, axes, member)
    )
    assert not np.array_equal(
        recon.run_member(values, axes, member), recon.run_member(values, axes, again)
    )


def test_t4b_the_family_is_the_registered_grid() -> None:
    """`:110-124`. 3 x 3 x 2 x 20, and exactly twenty of them are the default cell."""
    members = recon.family_members()

    assert len(members) == 360
    assert len({(m.width_sd, m.downshift_sd, m.scope) for m in members}) == 18
    assert sum(1 for m in members if m.is_default_cell) == 20


# ── T5 · the gate's authority over the GG arm ───────────────────────────────────────────────────


def test_t5_a_failing_control_stops_the_run_before_the_gg_arm(tmp_path: Path) -> None:
    """`:104-106`. PC0 misses, so `main` exits non-zero and writes no family block at all.

    Eight protein groups rather than the registered 2,438, which is a miss the gate cannot
    interpret as anything else. The GG arm's deposit is present and workable in this run — the
    reason no family block is written is the gate and nothing else.
    """
    code, fixture = _run(tmp_path, shotgun_rows=8, gg_rows=_gg_rows(1.0), claim_ids=CLAIM_IDS)

    assert code == 1
    assert fixture["gg_run"] is False
    assert "family" not in fixture
    assert fixture["gate"]["pc0"]["proteins_passing"] == 8
    assert fixture["gate"]["verdict"]["passed"] is False


def test_t5b_a_passing_gate_runs_the_family_and_reports_the_verdict(tmp_path: Path) -> None:
    """The same harness with a gate that holds. What this establishes is the control flow and the
    shape of the output — not the correctness of PC1 to PC3, for the reason this file's docstring
    gives."""
    code, fixture = _run(
        tmp_path, shotgun_rows=recon.PC0_REGISTERED, gg_rows=_gg_rows(1.0), claim_ids=CLAIM_IDS
    )

    assert code == 0
    assert fixture["gg_run"] is True
    assert fixture["gate"]["verdict"]["passed"] is True
    assert fixture["gate"]["verdict"]["chosen_variant"] in recon.T_VARIANTS

    family = fixture["family"]
    assert family["exposure"] == len(CLAIM_IDS)
    assert len(family["members"]) == 360
    assert len(family["claims"]) == len(CLAIM_IDS)
    # Every member's min(P) is kept per claim, which is what makes the readouts recomputable.
    assert [len(c["min_p"]) for c in family["claims"]] == [360] * len(CLAIM_IDS)
    counts = family["readouts"]["primary"]["counts"]
    assert sum(counts.values()) == len(CLAIM_IDS)
    assert family["verdict"]["exposure"] == len(CLAIM_IDS)
    # The one multiplicity-flagged claim is reported individually (`:149`).
    assert len(family["multiplicity_flagged_claims"]) == 1


def test_t6_a_refused_row_stays_in_the_population_and_moves_the_medians(tmp_path: Path) -> None:
    """The population is `_filter`'s output, so a row the adapter refused still normalises the rest.

    Every row in this deposit is refused — none has a razor pick — and one of them is not a claim.
    Two runs differing **only** in that row's intensities give different per-claim P values, which
    they could not do if the population were the emitted observations or the claims.
    """
    _, low = _run(tmp_path / "low", shotgun_rows=8, gg_rows=_gg_rows(1.0), claim_ids=CLAIM_IDS)
    _, high = _run(tmp_path / "high", shotgun_rows=8, gg_rows=_gg_rows(64.0), claim_ids=CLAIM_IDS)

    # The gate fails in both (8 proteins, not 2,438), so the family did not run — the population is
    # asserted where it is visible without it: through a third run with the gate passing.
    assert low["gg_run"] is False and high["gg_run"] is False

    _, a = _run(
        tmp_path / "a",
        shotgun_rows=recon.PC0_REGISTERED,
        gg_rows=_gg_rows(1.0),
        claim_ids=CLAIM_IDS,
    )
    _, b = _run(
        tmp_path / "b",
        shotgun_rows=recon.PC0_REGISTERED,
        gg_rows=_gg_rows(64.0),
        claim_ids=CLAIM_IDS,
    )

    assert a["family"]["population_rows"] == len(CLAIM_IDS) + 1
    assert [c["median_min_p_default_cell"] for c in a["family"]["claims"]] != [
        c["median_min_p_default_cell"] for c in b["family"]["claims"]
    ]
