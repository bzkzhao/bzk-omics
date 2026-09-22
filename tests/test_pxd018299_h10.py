"""`bzk/sources/pxd018299_h10.py` — gate G, check A and H10's readouts, on synthetic inputs.

**Entirely offline, and nothing here touches PXD018299 or PXD026748.** The module reads two
deposits and two journal supplements that exist only on bzk's machine; what can be tested here is
everything between reading them and the verdict — which rule picks the column family, which
valid-value candidate is taken, what happens when no variant is admitted, how the primary variant
is chosen, where the verdict's boundaries fall, how the two random steps are paired, what counts as
an imputed cell, and what the author file can and cannot move.

**Each case is built to discriminate.** The valid-value case is one where the strictest and the
loosest candidates disagree about the answer, not merely about a count; the author-configuration
case is one where a tracked file changes readout A's primary and changes nothing about the verdict.
A case that agrees under both readings would establish nothing about which reading the code applies.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from bzk.sources import pxd018299_h10 as h10
from bzk.sources.pxd026748_reconstruction import Member

GENOTYPES = ("WT", "ISG15-/-")


def _matrix(rows: list[list[float]]) -> np.ndarray:
    return np.array(rows, dtype=float)


# ── §3 · the column and normalisation check ─────────────────────────────────────────────────────


def _check(published: np.ndarray, summed: np.ndarray, multiplicity: np.ndarray) -> h10.MatrixCheck:
    return h10.matrix_check(
        published=published,
        deposit_by_family={"summed": summed, "multiplicity_1": multiplicity},
        population_by_family={"summed": summed, "multiplicity_1": multiplicity},
    )


def test_the_check_takes_no_normalisation_where_s1_equals_log2_of_the_deposit() -> None:
    """§3's first clause. The summed family matches unnormalised, so that is what is used."""
    summed = _matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    other = summed + 7.0

    check = _check(published=summed.copy(), summed=summed, multiplicity=other)

    assert check.family == "summed"
    assert check.normalisation == "none"
    assert check.undetermined is False
    assert check.fractions["summed+none"]["share"] == 1.0


def test_the_check_takes_median_subtraction_where_that_is_what_matches() -> None:
    """§3's second clause. Nothing matches raw; the per-column median-subtracted form does."""
    summed = _matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    published = summed - np.nanmedian(summed, axis=0)

    check = _check(published=published, summed=summed, multiplicity=summed + 7.0)

    assert check.family == "summed"
    assert check.normalisation == "median_subtracted"
    assert check.undetermined is False


def test_the_check_prefers_the_summed_family_where_both_meet_the_criterion() -> None:
    """§3: *"if both do, the summed columns are used, since they are the platform's"*."""
    summed = _matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    check = _check(published=summed.copy(), summed=summed, multiplicity=summed.copy())

    assert check.family == "summed"


def test_the_check_takes_the_multiplicity_family_where_only_it_matches() -> None:
    """The fallback's other side: the rule is not *always* the summed columns."""
    summed = _matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    multiplicity = summed + 7.0

    check = _check(published=multiplicity.copy(), summed=summed, multiplicity=multiplicity)

    assert check.family == "multiplicity_1"
    assert check.normalisation == "none"


def test_the_check_falls_back_to_undetermined_where_nothing_meets_the_criterion() -> None:
    """§3's last clause: the summed columns unnormalised, and every result flagged.

    `undetermined` is not `none` wearing another name — the run carries the flag, so a reader can
    see that the normalisation was not established rather than established to be absent.
    """
    summed = _matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    check = _check(published=summed + 0.5, summed=summed, multiplicity=summed * 3.0)

    assert check.family == "summed"
    assert check.normalisation == "undetermined"
    assert check.undetermined is True
    assert all(f["share"] < h10.MATCH_CRITERION for f in check.fractions.values())


def test_the_criterion_is_ninety_nine_percent_of_the_deposit_measured_cells() -> None:
    """Cells the deposit does not report are not comparable and are not counted, either way.

    Ninety-nine of a hundred comparable cells agreeing meets the criterion; ninety-eight does not.
    The two matrices differ in one cell, which is what makes this a test of the threshold rather
    than of the comparison.
    """
    summed = np.arange(100.0).reshape(50, 2)
    just_enough = summed.copy()
    just_enough[0, 0] += 1.0
    not_enough = just_enough.copy()
    not_enough[0, 1] += 1.0

    assert _check(just_enough, summed, summed * 5).normalisation == "none"
    assert _check(not_enough, summed, summed * 5).normalisation == "undetermined"


# ── §3 · the valid-value rule ───────────────────────────────────────────────────────────────────


def test_the_valid_value_rule_is_the_strictest_that_retains_every_published_row() -> None:
    """§3, and the case is built so the strictest and the loosest give different answers.

    Row 0 is a published claim with three measured values in one group, row 1 a claim with two,
    and row 2 an unpublished row with one. Under `>= 3` the second claim is lost, so the rule may
    not take it; under `>= 1` a rule that retains everything would also retain rows the paper's
    own filter plainly dropped. `>= 2` is the strictest that keeps both claims, and is what the
    rule takes.
    """
    matrix = _matrix(
        [
            [1.0, 1.0, 1.0, np.nan, np.nan, np.nan],
            [1.0, 1.0, np.nan, np.nan, np.nan, np.nan],
            [1.0, np.nan, np.nan, np.nan, np.nan, np.nan],
        ]
    )

    choice = h10.valid_value_choice(matrix, claim_rows=[0, 1])

    assert choice["taken"] == 2
    assert choice["retains_every_claim"] is True
    assert choice["candidates"]["3"]["claims_retained"] == 1
    assert choice["candidates"]["2"]["claims_retained"] == 2
    assert choice["candidates"]["1"]["rows_retained"] == 3


def test_where_no_candidate_retains_every_claim_the_rule_takes_the_most_and_says_so() -> None:
    """§3's fallback. A claim with no measured value at all cannot be retained by any candidate,
    so the run reports the miss rather than inventing a fourth, looser rule."""
    matrix = _matrix([[1.0, 1.0, 1.0, np.nan, np.nan, np.nan], [np.nan] * 6])

    choice = h10.valid_value_choice(matrix, claim_rows=[0, 1])

    assert choice["taken"] == 1
    assert choice["retains_every_claim"] is False
    assert choice["candidates"]["1"]["claims_retained"] == 1


# ── §4 · the gate, the variants, and the primary ────────────────────────────────────────────────


def _gate(f1_by_name: dict[str, float | None], passing: set[str]) -> dict[str, Any]:
    return {
        "variants": {
            v.name: {"f1": f1_by_name.get(v.name), "passes": v.name in passing}
            for v in h10.VARIANTS
        }
    }


def test_the_primary_variant_is_the_admitted_one_with_the_highest_gate_f1() -> None:
    first, second, third = (v.name for v in h10.VARIANTS[:3])
    gate = _gate({first: 0.90, second: 0.97, third: 0.97}, {first, second, third})

    assert h10.primary_variant([first, second, third], gate) == second


def test_a_tie_on_f1_goes_to_the_earlier_variant_in_the_registered_list() -> None:
    """§4: *"Ties go to the earlier variant in the list above"* — positional, not alphabetical.

    The two tied names are chosen so their alphabetical order is the reverse of their registered
    order, which is what makes this a test of the rule rather than of `min`.
    """
    order = [v.name for v in h10.VARIANTS]
    earlier, later = order[1], order[3]
    gate = _gate({earlier: 0.97, later: 0.97}, {earlier, later})

    assert min(earlier, later) != earlier  # the alphabetical winner is the later one
    assert h10.primary_variant([later, earlier], gate) == earlier


def test_a_variant_that_called_nothing_cannot_be_primary() -> None:
    """Its F1 is undefined, and scoring it zero would rank it against variants whose F1 exists."""
    first, second = (v.name for v in h10.VARIANTS[:2])
    gate = _gate({first: None, second: 0.10}, {first, second})

    assert h10.primary_variant([first, second], gate) == second
    assert h10.primary_variant([first], gate) is None


def test_admission_needs_both_the_gate_and_attainability() -> None:
    """§4: a variant survives only if it passes G **and** reaches 0.01 on the anchor."""
    names = [v.name for v in h10.VARIANTS]
    gate = _gate(dict.fromkeys(names, 0.99), {names[0], names[1]})
    attainability = {n: {"reached": n in {names[1], names[2]}, "seed": 0} for n in names}

    assert h10.admitted_variants(gate, attainability) == [names[1]]


def test_the_gate_majority_is_ten_of_twenty() -> None:
    """§4 fixes *"at least 10 of the 20 seeds"*, and the module computes a majority instead so a
    reduced-seed run means the same thing. At the registered twenty they are the same number, and
    that identity is what makes the generalisation safe rather than a loosening."""
    from bzk.sources.pxd026748_reconstruction import SEEDS

    assert h10.gate_majority(SEEDS) == h10.GATE_MAJORITY == 10
    assert h10.gate_majority((0, 1, 2)) == 2
    assert h10.gate_majority((0,)) == 1


def test_gate_metrics_are_precision_recall_and_their_harmonic_mean() -> None:
    called = np.array([True, True, True, False])
    target = np.array([True, True, False, True])

    metrics = h10.gate_metrics(called, target)

    assert metrics["precision"] == {"numerator": 2, "denominator": 3, "share": pytest.approx(2 / 3)}
    assert metrics["recall"] == {"numerator": 2, "denominator": 3, "share": pytest.approx(2 / 3)}
    assert metrics["f1"] == pytest.approx(2 / 3)
    assert h10.gate_metrics(np.zeros(4, dtype=bool), target)["f1"] is None

    # **An asymmetric case, because the symmetric one cannot tell a harmonic mean from an
    # arithmetic one**: at precision == recall the two are the same number, and the case above has
    # both at 2/3. Found by a mutation that left this test green. Here precision is 1/2 and recall
    # 1/4, so the harmonic mean is 1/3 and the arithmetic mean 3/8.
    lopsided = h10.gate_metrics(
        np.array([True, True, False, False]), np.array([True, False, True, True])
    )
    assert lopsided["precision"]["share"] == pytest.approx(0.5)
    assert lopsided["recall"]["share"] == pytest.approx(1 / 3)
    assert lopsided["f1"] == pytest.approx(0.4)


# ── §6 B · the verdict ──────────────────────────────────────────────────────────────────────────


def test_the_verdict_at_the_registered_boundaries() -> None:
    """Recurs at 5%, absent at 1%, indeterminate between — each boundary inclusive, with the
    1e-9 slack turn 17 established for the same reason: these shares are rationals, and a
    registered direction decided by binary floating point at its own boundary is not it."""
    assert h10.h10_verdict(0.05)["outcome"] == "recurs"
    assert h10.h10_verdict(0.15 - 0.10)["outcome"] == "recurs"
    assert h10.h10_verdict(0.0499)["outcome"] == "indeterminate"
    assert h10.h10_verdict(0.01)["outcome"] == "absent"
    assert h10.h10_verdict(0.0101)["outcome"] == "indeterminate"
    assert h10.h10_verdict(0.03)["outcome"] == "indeterminate"
    assert h10.h10_verdict(None)["outcome"] == "undefined"


def test_instability_is_support_that_differs_across_draws() -> None:
    """Not "sometimes supported" and not "sometimes unsupported" — both, which is the same row
    answering differently to two draws of the same registered cell."""
    support = np.array([[True, True], [False, False], [True, False]])

    assert h10.instability(support).tolist() == [False, False, True]


# ── §5 · the paired seeds ───────────────────────────────────────────────────────────────────────


def _axes_matrix(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(20.0, 1.0, size=(40, 6))
    matrix[:20, 3] = np.nan
    return matrix


def test_a_member_uses_its_own_seed_for_both_random_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """§5: *"Draw k uses imputation seed k and permutation seed k."*

    The two seeds are captured at the call rather than inferred from the output: an implementation
    that paired them by accident on one member and not another would still produce plausible
    numbers, and only the calls say which seed reached which step.
    """
    seen: list[tuple[str, int]] = []
    from bzk.stats import downshifted_normal as real_impute
    from bzk.stats.perseus_s0 import perseus_s0 as real_test

    def _impute(values: np.ndarray, **kwargs: Any) -> Any:
        seen.append(("imputation", int(kwargs["seed"])))
        return real_impute(values, **kwargs)

    def _test(a: np.ndarray, b: np.ndarray, **kwargs: Any) -> Any:
        seen.append(("permutation", int(kwargs["seed"])))
        return real_test(a, b, **kwargs)

    monkeypatch.setattr(h10, "downshifted_normal", _impute)
    monkeypatch.setattr(h10, "perseus_s0", _test)
    matrix = _axes_matrix()
    member = Member(width_sd=0.3, downshift_sd=1.8, scope="per_sample", seed=7)
    variant = h10.VARIANTS[-1]

    h10.run_paired_member(matrix, 3, member, variant, randomisations=20)
    assert seen == [("imputation", 7), ("permutation", 7)]

    seen.clear()
    h10.run_paired_member(matrix, 3, member, variant, randomisations=20, permutation_seed=0)
    assert seen == [("imputation", 7), ("permutation", 0)]


def test_support_means_q_below_the_threshold_and_a_positive_direction() -> None:
    """§1: support is `q <= 0.01` **and** `d > 0` (higher in KO + IFN). A claim significant in the
    other direction is not supported, and a run that dropped the direction would report it."""
    rng = np.random.default_rng(3)
    matrix = np.hstack([rng.normal(20.0, 0.3, size=(60, 3)), rng.normal(20.0, 0.3, size=(60, 3))])
    matrix[:20, :3] += 4.0  # up in KO
    matrix[20:40, 3:] += 4.0  # up in WT, and never supported

    member = Member(width_sd=0.3, downshift_sd=1.8, scope="per_sample", seed=0)
    variant = next(v for v in h10.VARIANTS if v.name == "per_side+exhaustive_excluding_trivial")
    support = h10.run_paired_member(matrix, 3, member, variant, randomisations=250)

    assert support[:20].any()
    assert not support[20:40].any()


# ── the end-to-end run ──────────────────────────────────────────────────────────────────────────


#: The variant the synthetic Table 3 is written from — see `_synthetic`.
GATE_VARIANT = "per_side+exhaustive_excluding_trivial"
GATE_SEEDS = (0, 1, 2)
GATE_RANDOMISATIONS = 30


def _synthetic(tmp_path: Path, *, author: dict[str, Any] | None = None) -> dict[str, Any]:
    """Every byte `main` reads, built here. Returns the paths and declarations it is handed.

    **The synthetic Table 3's `+` calls are generated from one variant's own majority calls**, so
    that variant passes G with precision and recall of 1 and the run continues into check A and
    the family. That circularity is deliberate and bounded, exactly as turn 16's was: it buys a
    gate that passes so the control flow downstream can be asserted, and it establishes **nothing**
    about whether G's precision and recall are computed correctly — a mutation to the metric would
    move both sides together. What establishes the metric is `test_gate_metrics_are_precision_…`
    above, against counts written by hand.
    """
    from openpyxl import Workbook
    from test_pxd026748_reconstruction import _record, _shotgun_bytes

    from bzk.provenance import raw_store

    home = tmp_path / "home"
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    shotgun = raw_store.store(_shotgun_bytes(24), "proteinGroups.txt", home=home)
    shotgun_record = _record(
        tmp_path,
        name="curation_SYNTHETIC_shotgun.json",
        filename="proteinGroups.txt",
        content_hash=shotgun.content_hash,
        prefix="LFQ intensity ",
    )

    # The anchor deposit: eight rows, six intensity columns per family, one reverse decoy.
    rng = np.random.default_rng(5)
    header = [
        "Protein",
        "Position",
        "Reverse",
        "Potential contaminant",
        "Localization prob",
        "id",
        *[f"Intensity {arm}_{i}" for arm in ("KO_IFN", "WT_IFN") for i in (1, 2, 3)],
        *[f"Intensity {arm}_{i}___1" for arm in ("KO_IFN", "WT_IFN") for i in (1, 2, 3)],
    ]
    lines = ["\t".join(header)]
    published: list[list[float]] = []
    for row_id in range(8):
        values = rng.lognormal(mean=16.0, sigma=0.2, size=6)
        if row_id < 4:
            values[:3] *= 16.0  # up in KO, so some claims are supported
        cells: list[str] = [f"{v:.4f}" for v in values]
        lines.append(
            "\t".join(
                [
                    f"SYNTHETIC-{row_id}",
                    str(10 + row_id),
                    "+" if row_id == 7 else "",
                    # §2 keeps contaminants, so one is present to be kept.
                    "+" if row_id == 6 else "",
                    "0.99",
                    str(row_id),
                    *cells,
                    *[f"{v / 2:.4f}" for v in values],
                ]
            )
        )
        if row_id < 6:
            published.append([float(x) for x in np.log2(values)])
    deposit = raw_store.store(("\r\n".join(lines) + "\r\n").encode("utf-8"), "sites.txt", home=home)
    anchor_record = _record(
        tmp_path,
        name="curation_SYNTHETIC_anchor.json",
        filename="sites.txt",
        content_hash=deposit.content_hash,
        prefix="Intensity ",
    )

    # S1: a title row, then Perseus-prefixed headers, then one row per claim.
    book = Workbook()
    sheet = book.active
    sheet.title = "S1"
    sheet.append(["Supplementary Data 1 — synthetic"])
    sheet.append(
        [
            "T: Protein",
            "N: Position",
            "T: Gene names",
            *[f"N: Intensity {arm}_{i}" for arm in ("KO_IFN", "WT_IFN") for i in (1, 2, 3)],
        ]
    )
    for row_id, published_values in enumerate(published):
        sheet.append([f"SYNTHETIC-{row_id}", 10 + row_id, f"GENE{row_id}", *published_values])
    s1_path = tmp_path / "s1.xlsx"
    book.save(s1_path)
    s1 = raw_store.store(s1_path.read_bytes(), "s1.xlsx", home=home)

    # The gate supplement: Table 3, with `+` on exactly what one variant calls — see the docstring.
    from bzk.adapters import maxquant as _maxquant
    from bzk.curation.loader import load_path
    from bzk.sources.pxd026748_reconstruction import (
        first_accession,
        intensity_matrix,
        pipeline,
        sample_axes,
        shotgun_rows,
    )
    from bzk.stats import downshifted_normal
    from bzk.stats.perseus_s0 import perseus_s0

    shotgun_table = _maxquant.read_table(shotgun.path)
    rows, column = shotgun_rows(shotgun_table)
    axes = sample_axes(load_path(shotgun_record))
    normalised, keep = pipeline(intensity_matrix(rows, column, axes.labels), axes)
    gate_values = normalised[keep]
    gate_accessions = [
        a for a, k in zip((first_accession(r, column) for r in rows), keep, strict=True) if k
    ]
    wt = list(axes.columns_where("WT"))
    ko = list(axes.columns_where("ISG15-/-"))
    variant = next(v for v in h10.VARIANTS if v.name == GATE_VARIANT)
    counts = np.zeros(gate_values.shape[0], dtype=int)
    for seed in GATE_SEEDS:
        filled = downshifted_normal(
            gate_values, downshift_sd=1.8, width_sd=0.3, seed=seed, scope="per_sample"
        ).values
        counts += perseus_s0(
            filled[:, wt],
            filled[:, ko],
            s0=h10.GATE_S0,
            alpha=h10.GATE_ALPHA,
            randomisations=GATE_RANDOMISATIONS,
            seed=seed,
            sidedness=variant.sidedness,
            scheme=variant.scheme,
        ).significant.astype(int)
    majority = counts >= (len(GATE_SEEDS) + 1) // 2

    gate_book = Workbook()
    gate_sheet = gate_book.active
    gate_sheet.title = "Table 3"
    gate_sheet.append(["Supplementary Table 3 — synthetic"])
    gate_sheet.append(["Uniprot ID", "Significant", "Log2 fold change", "-Log P value"])
    for accession, called in zip(gate_accessions, majority.tolist(), strict=True):
        gate_sheet.append([accession, "+" if called else "", 0.0, 0.0])
    gate_path = tmp_path / "table3.xlsx"
    gate_book.save(gate_path)
    gate = raw_store.store(gate_path.read_bytes(), "table3.xlsx", home=home)

    cascade = tmp_path / "cascade.json"
    cascade.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "row": 3 + i,
                        "deposit_id": str(i),
                        "gene_names": f"GENE{i}",
                        "lost_at": None,
                    }
                    for i in range(len(published))
                ]
            }
        ),
        encoding="utf-8",
    )
    targets = tmp_path / "targets.json"
    targets.write_text(
        json.dumps({"targets": [{"gene": f"GENE{i}"} for i in range(3)]}), encoding="utf-8"
    )

    author_path = tmp_path / "author.json"
    if author is not None:
        author_path.write_text(json.dumps(author), encoding="utf-8")

    from bzk.sources import protein_groups

    return {
        "home": home,
        "fixtures_dir": fixtures_dir,
        "anchor_curation_path": anchor_record,
        "shotgun_curation_path": shotgun_record,
        "cascade_fixture_path": cascade,
        "targets_fixture_path": targets,
        "author_parameters_path": author_path,
        "anchor_supplement": protein_groups.SupplementaryFile(
            label="synthetic S1", filename="s1.xlsx", expected_content_hash=s1.content_hash
        ),
        "gate_supplement": protein_groups.SupplementaryFile(
            label="synthetic T3", filename="table3.xlsx", expected_content_hash=gate.content_hash
        ),
        "anchor_deposit_file": protein_groups.SupplementaryFile(
            label="synthetic sites",
            filename="sites.txt",
            expected_content_hash=deposit.content_hash,
        ),
    }


def _run(paths: dict[str, Any], **overrides: Any) -> tuple[int, dict[str, Any]]:
    settings: dict[str, Any] = {
        **paths,
        "randomisations": GATE_RANDOMISATIONS,
        "seeds": GATE_SEEDS,
        "members": [
            Member(width_sd=w, downshift_sd=1.8, scope="per_sample", seed=s)
            for w in (0.3, 0.4)
            for s in (0, 1)
        ],
        "repo_root": Path(paths["home"]).parent,
        "progress": False,
    }
    settings.update(overrides)
    code = h10.main(**settings)
    # The attempt's own file, not attempt 1's: reading `FIXTURE_NAME` unconditionally would hand
    # back the wrong run's fixture the moment `attempt=2` is passed, and silently, because an
    # attempt 1 file is usually sitting there from an earlier call.
    name = h10.fixture_name_for(int(settings.get("attempt", 1)))
    written = json.loads((Path(paths["fixtures_dir"]) / name).read_text(encoding="utf-8"))
    return code, written


def test_main_runs_the_gate_the_check_and_the_readouts(tmp_path: Path) -> None:
    """The one test that executes `main`, `anchor_block`, `gate_block` and `family_block_for`.

    The arithmetic is established by the pure tests above; what this establishes is that the IO
    seam holds — both deposits located and parsed, both workbooks read, the header found by
    content, the two checks run, and the result serialised. bzk runs the instrument, and a
    signature error here would surface only there.
    """
    code, written = _run(_synthetic(tmp_path))

    assert code == 0
    assert written["anchor_run"] is True
    assert GATE_VARIANT in written["admitted_variants"]
    assert written["registration"] == "walk/PREREG-PXD018299-H10.md"
    assert set(written["gate_g"]["variants"]) == {v.name for v in h10.VARIANTS}
    assert written["anchor_matrix"]["column_family"] in h10.COLUMN_FAMILIES
    assert written["anchor_matrix"]["normalisation"] in (*h10.NORMALISATIONS, "undetermined")
    # Eight rows, less the one reverse decoy. **The contaminant row is kept**, which is §2's own
    # decision and the one place in this repository where the decoy filter runs without the
    # contaminant one: the paper's table retains three flagged contaminants, so dropping them
    # would reproduce the D6 error this run exists to replace.
    assert written["anchor_matrix"]["population_rows"] == 7
    assert written["anchor_matrix"]["published_rows"] == 6
    if written["anchor_run"]:
        assert written["readouts"]["readout_b"]["verdict"]["outcome"] in {
            "recurs",
            "absent",
            "indeterminate",
            "undefined",
        }
        assert (
            len(written["readouts"]["per_claim_support"]["rows"])
            == written["anchor_matrix"]["exposure"]
        )


def test_no_variant_admitted_means_no_anchor_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§4: *"If none is admitted, the anchor readouts below do not run."*

    The gate is made impossible by a threshold nothing can meet — which is a property of the run,
    not of the data — so the module's own admission path decides, and the fixture records the
    refusal rather than an empty family.
    """
    paths = _synthetic(tmp_path)
    monkeypatch.setattr(h10, "GATE_MIN_PRECISION", 2.0)  # unreachable: precision is a share
    code, written = _run(paths)

    assert code == 1
    assert written["anchor_run"] is False
    assert written["primary_variant"] is None
    assert written["admitted_variants"] == []
    assert written["result"] == "named test not reproduced"
    assert "readouts" not in written


# ── §6 A · the author configuration ─────────────────────────────────────────────────────────────


AUTHOR = {
    "source": "synthetic — nobody stated these",
    "date_received": "2026-09-22",
    "width_sd": 0.4,
    "downshift_sd": 2.0,
    "seed": 3,
}


def test_an_unknown_key_in_the_author_file_refuses_by_name(tmp_path: Path) -> None:
    """A misspelled key would otherwise be dropped and the registered default run in its place,
    under a record claiming the authors' value."""
    path = tmp_path / "author.json"
    path.write_text(json.dumps({**AUTHOR, "downshfit_sd": 2.0}), encoding="utf-8")

    with pytest.raises(h10.H10Error, match="downshfit_sd"):
        h10.read_author_parameters(path, repo_root=tmp_path)


def test_the_author_file_needs_its_provenance(tmp_path: Path) -> None:
    """*"Received and before the run are established by the record, not by memory."*"""
    path = tmp_path / "author.json"
    path.write_text(json.dumps({"width_sd": 0.4}), encoding="utf-8")

    with pytest.raises(h10.H10Error, match="date_received"):
        h10.read_author_parameters(path, repo_root=tmp_path)


def test_an_absent_author_file_is_none_and_an_untracked_one_is_not_primary(tmp_path: Path) -> None:
    """§6 A turns on *committed*, not on *present*."""
    assert h10.read_author_parameters(tmp_path / "absent.json", repo_root=tmp_path) is None

    path = tmp_path / "author.json"
    path.write_text(json.dumps(AUTHOR), encoding="utf-8")
    configuration = h10.read_author_parameters(path, repo_root=tmp_path)

    assert configuration is not None
    assert configuration.tracked is False
    assert configuration.member() == Member(
        width_sd=0.4, downshift_sd=2.0, scope="per_sample", seed=3
    )


def test_the_author_configuration_moves_readout_a_only_when_tracked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tracked, it is readout A's primary and the default cell is reported beside it. Untracked,
    it is an added readout and the default cell stays primary. Nothing else moves either way."""
    paths = _synthetic(tmp_path, author=AUTHOR)
    _, untracked = _run(paths)

    monkeypatch.setattr(h10, "is_tracked", lambda path, *, repo_root=None: True)
    paths["fixtures_dir"] = tmp_path / "tracked"
    Path(paths["fixtures_dir"]).mkdir()
    _, tracked = _run(paths)

    assert untracked["anchor_run"] and tracked["anchor_run"]
    assert untracked["readouts"]["readout_a"]["primary"] == "default_cell"
    assert tracked["readouts"]["readout_a"]["primary"] == "author_configuration"
    assert untracked["readouts"]["readout_a"]["author_configuration"]["tracked_in_git"] is False
    assert tracked["readouts"]["readout_a"]["author_configuration"]["tracked_in_git"] is True


def test_the_verdict_is_identical_with_and_without_the_author_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§6 B, and v8's rule: readout B stays on the registered default cell either way.

    **The support pattern is stubbed rather than drawn**, for one reason: readout B's quantity is
    *instability*, and a synthetic matrix small enough to run in a test is stable — every draw
    agrees, the share is 0, and "identical with and without" would then be true of two zeroes. The
    stub makes the share non-zero by construction (one of two imputed claims flips between the
    default cell's two draws, so the share is 0.5 and the verdict `recurs`), which is what makes
    the comparison mean something. What is under test is which members readout B reads, not how
    support is computed — `test_support_means_q_below_the_threshold_and_a_positive_direction`
    covers that against the real arithmetic.
    """
    matrix = np.array(
        [
            [1.0, 1.0, 1.0, np.nan, 1.0, 1.0],
            [1.0, 1.0, 1.0, np.nan, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ]
    )
    #: Seed 0 supports rows 0 and 1; seed 1 supports only row 1. Row 0 therefore flips, and it is
    #: one of the two rows carrying an imputed cell.
    pattern = {0: [True, True, False, False], 1: [False, True, False, False]}

    def _stub(
        _matrix: np.ndarray,
        _half: int,
        member: Member,
        _variant: h10.Variant,
        **_kwargs: Any,
    ) -> np.ndarray:
        return np.array(pattern.get(member.seed, [False] * 4), dtype=bool)

    monkeypatch.setattr(h10, "run_paired_member", _stub)
    anchor = {
        "matrix": matrix,
        "claim_rows": [0, 1, 2, 3],
        "claims": [
            {"deposit_id": str(i), "row": 3 + i, "gene_names": f"GENE{i}"} for i in range(4)
        ],
        "published_draw": {},
    }
    members = [Member(0.3, 1.8, "per_sample", s) for s in (0, 1)]
    primary = h10.VARIANTS[0]
    author = h10.AuthorConfiguration(
        parameters={"width_sd": 0.4, "downshift_sd": 2.0, "seed": 3},
        source="synthetic — nobody stated these",
        date_received="2026-09-22",
        tracked=True,
    )

    plain = h10.family_block_for(
        anchor=anchor,
        variants=[primary],
        primary=primary,
        members=members,
        targets=["GENE0"],
        author=None,
        randomisations=20,
        progress=False,
    )
    authored = h10.family_block_for(
        anchor=anchor,
        variants=[primary],
        primary=primary,
        members=members,
        targets=["GENE0"],
        author=author,
        randomisations=20,
        progress=False,
    )

    # Non-vacuous: one of the two imputed claims flips, so the share is a half and the verdict is
    # `recurs` rather than a shared zero.
    assert plain["readout_b"]["conditional_on_imputation"]["share"] == pytest.approx(0.5)
    assert plain["readout_b"]["verdict"]["outcome"] == "recurs"
    assert plain["readout_b"] == authored["readout_b"]
    # And the author configuration did reach readout A, so the two runs are not simply identical.
    assert plain["readout_a"]["primary"] == "default_cell"
    assert authored["readout_a"]["primary"] == "author_configuration"


# ── attempt 2 ───────────────────────────────────────────────────────────────────────────────────


def test_attempt_1s_variant_list_and_fixture_name_are_untouched() -> None:
    """`perseus_s0.SIDEDNESS` gained a third value; attempt 1's eight variants did not.

    Attempt 1 has run and its result is committed. Reading its variant list off a constant that
    grows would have made that result a description of a twelve-variant run.
    """
    assert [v.name for v in h10.VARIANTS] == [
        "joint+random",
        "joint+random_excluding_trivial",
        "joint+exhaustive_when_small",
        "joint+exhaustive_excluding_trivial",
        "per_side+random",
        "per_side+random_excluding_trivial",
        "per_side+exhaustive_when_small",
        "per_side+exhaustive_excluding_trivial",
    ]
    assert [v.name for v in h10.ATTEMPT_2_VARIANTS] == [
        "joint_half+random",
        "joint_half+random_excluding_trivial",
        "joint_half+exhaustive_when_small",
        "joint_half+exhaustive_excluding_trivial",
    ]
    assert h10.variants_for(1) == h10.VARIANTS
    assert h10.variants_for(2) == h10.ATTEMPT_2_VARIANTS
    assert h10.fixture_name_for(1) == "pxd018299_h10.json"
    assert h10.fixture_name_for(2) == "pxd018299_h10_attempt2.json"


#: Attempt 1's synthetic end-to-end fixture, canonically serialised and hashed, **measured at
#: `36b344a`** — the commit before attempt 2 was written — in a `git worktree` of it, with
#: `PYTHONPATH` pointed at that tree so the worktree's `bzk` was the one imported rather than the
#: editable install's. Re-measured unchanged at `e13f06c`, before attempt 3 was written.
ATTEMPT_1_DIGEST = "512a0a4f374d732ca54b78101b35a515c3af0484f110fa53c7db010402ba4fd8"

#: Attempt 2's, the same way, measured at **`e13f06c`** — the commit before attempt 3 was
#: written. Its run needs the G2b bands widened to reach the anchor at synthetic scale, so the
#: measurement widened them exactly as `_run_attempt_2` below does; a digest of a run that
#: stopped at the gate would pin the gate and nothing after it.
ATTEMPT_2_DIGEST = "eb593fe7a529c2b27a6da0ec714ad6cd9dd96826e0c7c5614c7f04418e708b27"

#: What a rerun must move, and which therefore cannot be in the digest. The first four are a
#: run's own identity; the last two are the synthetic workbooks' content hashes, which move
#: between runs because `openpyxl` stamps a creation time into every `.xlsx` it writes — a
#: property of the test's fixture generator, not of the module under test.
DIGEST_EXCLUSIONS = (
    "runtime_seconds",
    "anchor_published_content_hash",
    "gate_published_content_hash",
)
DIGEST_EXCLUSIONS_UNDER = ("generated_at", "commit", "working_tree_clean")


def _digest(written: dict[str, Any]) -> str:
    written = json.loads(json.dumps(written))
    for key in DIGEST_EXCLUSIONS:
        written.pop(key, None)
    for key in DIGEST_EXCLUSIONS_UNDER:
        written["generated_under"].pop(key, None)
    return hashlib.sha256(json.dumps(written, sort_keys=True).encode()).hexdigest()


def _run_attempt_2(
    paths: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> tuple[int, dict[str, Any]]:
    """Attempt 2 end to end, with G2b's bands widened so the run reaches the anchor.

    [58, 86] and [168, 252] are absolute counts calibrated to the deposit's 2,438 rows; nothing at
    synthetic scale reaches 58 of anything, so with the registered bands no variant is admitted
    and the run stops at the gate. What the bands themselves do is asserted at their own endpoints
    by `test_g2b_bands_are_inclusive_at_both_ends`.
    """
    monkeypatch.setattr(h10, "G2B_WT_BAND", (0, 100))
    monkeypatch.setattr(h10, "G2B_KO_BAND", (0, 100))
    return _run(paths, attempt=2)


def test_attempts_1_and_2_are_unchanged_by_attempt_3(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both earlier attempts' synthetic fixtures, against digests measured before attempt 3.

    **Against the old code, not against itself.** A first version of this test ran the live module
    twice and compared the two, which establishes determinism and nothing else — and it passed
    under a mutation that turned attempt 2's direction split on for everyone, because both runs
    carried it. The attempt 1 digest comes from a worktree of `36b344a` and was re-measured
    unchanged at `e13f06c`; the attempt 2 digest comes from `e13f06c`.

    It also caught a real change once: `anchor_block` gained an `s1_gene_column` key for readout
    D′, and that key reached attempt 1's `anchor_matrix` block. Attempt 1 has run and its result
    is committed; a fixture that gains a field is a fixture of something else.
    """
    paths = _synthetic(tmp_path)
    _, one = _run(paths)
    _, two = _run_attempt_2(paths, monkeypatch)

    assert _digest(one) == ATTEMPT_1_DIGEST
    assert _digest(two) == ATTEMPT_2_DIGEST
    assert "attempt" not in one
    assert "validation" not in one
    assert all("direction_split" not in v for v in one["gate_g"]["variants"].values())
    assert two["attempt"] == 2
    assert "matrix" not in two  # attempt 3's second flag is attempt 3's alone
    assert "disclosed_before_run" not in two["readouts"]["readout_a"]


def _counts(up: int, down: int, rows: int = 400) -> tuple[np.ndarray, np.ndarray]:
    """Per-row seed counts with `up` rows called up by every seed and `down` called down."""
    up_counts = np.zeros(rows, dtype=int)
    down_counts = np.zeros(rows, dtype=int)
    up_counts[:up] = 20
    down_counts[up : up + down] = 20
    return up_counts, down_counts


def test_g2b_bands_are_inclusive_at_both_ends() -> None:
    """§3's bands are [58, 86] and [168, 252]. Counts at the endpoints pass; one outside fails."""
    for wt, ko in ((58, 168), (86, 252), (72, 210)):
        up, down = _counts(wt, ko)
        assert h10.direction_split(up, down, majority=10)["passes"], (wt, ko)
    for wt, ko in ((57, 210), (253, 210), (72, 167), (72, 253)):
        up, down = _counts(wt, ko)
        assert not h10.direction_split(up, down, majority=10)["passes"], (wt, ko)


def test_g2b_counts_each_direction_by_its_own_majority() -> None:
    """A row called by a majority in neither direction is in neither count, and the overlap is
    reported rather than assumed away."""
    up = np.array([20, 9, 20, 0])
    down = np.array([0, 9, 20, 20])

    split = h10.direction_split(up, down, majority=10)

    assert split["higher_in_wt"] == 2
    assert split["higher_in_knockout"] == 2
    assert split["both"] == 1


def test_the_direction_orientation_puts_wt_above_zero() -> None:
    """`direction > 0` means *higher in WT* under the argument order `gate_block` uses.

    Asserted on the probe the module itself runs, and then on a whole synthetic protein: a row
    raised in every WT column is counted in the WT band, not the knockout one. A swap would leave
    both counts plausible and exchange the two bands silently.
    """
    values = np.zeros((1, 12))
    assert h10.orientation_holds(values, [0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11])

    rng = np.random.default_rng(4)
    matrix = rng.normal(20.0, 0.3, size=(80, 12))
    matrix[:12, :6] += 5.0  # up in WT, under the WT-first column order below
    gate = h10.gate_block(
        values=matrix,
        wt_columns=[0, 1, 2, 3, 4, 5],
        ko_columns=[6, 7, 8, 9, 10, 11],
        complete=np.ones(80, dtype=bool),
        accessions=[f"SYNTHETIC-{i}" for i in range(80)],
        calls=set(),
        call_values={},
        randomisations=40,
        seeds=(0, 1, 2),
        variants=[h10.ATTEMPT_2_VARIANTS[1]],
        direction=True,
        progress=False,
    )
    split = gate["variants"]["joint_half+random_excluding_trivial"]["direction_split"]

    assert split["higher_in_wt"] >= 1
    assert split["higher_in_knockout"] == 0


def test_attempt_2_admits_only_what_passes_g2a_g2b_and_a() -> None:
    """§3: *"A variant is admitted only if it passes G2a, G2b and A."*

    The case is one where G2a passes and G2b fails — the shape attempt 1's own figures had, 33 up
    against a band starting at 58 — so skipping G2b would admit a variant the registration
    excludes.
    """
    names = [v.name for v in h10.ATTEMPT_2_VARIANTS]
    gate = {
        "variants": {
            name: {
                "f1": 0.99,
                "passes": True,
                "direction_split": {"passes": name != names[0]},
            }
            for name in names
        }
    }
    attainability = {name: {"reached": True, "seed": 0} for name in names}

    admitted = h10.admitted_variants(
        gate, attainability, variants=h10.ATTEMPT_2_VARIANTS, direction=True
    )

    assert names[0] not in admitted
    assert admitted == names[1:]
    # Attempt 1's rule does not read the split at all, which is what keeps it unchanged.
    assert h10.admitted_variants(gate, attainability, variants=h10.ATTEMPT_2_VARIANTS) == names


# ── readout D′ ──────────────────────────────────────────────────────────────────────────────────


def _dprime(supported: list[bool], gene_names: list[str], intensity: list[float]) -> dict[str, Any]:
    return h10.dprime_block(
        targets={
            "results_curated": ["ADAR"],
            "results_not_curated": ["DDX3X", "DHX9"],
            "discussion": ["MAGE", "STAT1"],
        },
        gene_names=gene_names,
        intensity=intensity,
        claim_rows=list(range(len(gene_names))),
        supported=np.array(supported, dtype=bool),
    )


def test_dprime_reports_the_three_tiers_separately() -> None:
    """§4 lists them separately and they are different kinds of claim: a target in the paper's
    Results is not the same evidence as one in its Discussion."""
    block = _dprime(
        [True, False, True, False],
        ["ADAR", "DDX3X", "STAT1", "MAGEA4"],
        [10.0, 9.0, 8.0, 7.0],
    )

    assert set(block["tiers"]) == {"results_curated", "results_not_curated", "discussion"}
    assert block["tiers"]["results_curated"]["ADAR"]["any_site"] is True
    assert block["tiers"]["results_not_curated"]["DDX3X"]["any_site"] is False
    assert block["tiers"]["discussion"]["STAT1"]["any_site"] is True


def test_dprime_matches_mage_by_prefix_and_nothing_else_by_prefix() -> None:
    """§4's one declared exception. `STAT1` must not match `STAT1B`, and `MAGE` must match
    `MAGEA4` — the asymmetry is the rule, and it is named in `prefix_matched_symbols`."""
    block = _dprime([True, True], ["MAGEA4", "STAT1B"], [10.0, 9.0])

    assert block["tiers"]["discussion"]["MAGE"]["absent_from_s1"] is False
    assert block["tiers"]["discussion"]["MAGE"]["sites"] == 1
    assert block["tiers"]["discussion"]["STAT1"]["absent_from_s1"] is True
    assert block["prefix_matched_symbols"] == ["MAGE"]
    assert h10.matches_symbol("MAGE", "MAGEA4;OTHER") is True
    assert h10.matches_symbol("STAT1", "STAT1B") is False
    assert h10.matches_symbol("STAT1", "OTHER;STAT1") is True


def test_dprime_reports_an_absent_symbol_as_absent_and_not_as_unrecovered() -> None:
    """§4: *"A symbol that matches nothing in S1 is reported as absent from S1, never as not
    recovered."* A claim the file does not carry has no recovery figure, and reporting one would
    assert a measurement over an empty set."""
    block = _dprime([True], ["ADAR"], [10.0])
    absent = block["tiers"]["results_not_curated"]["DHX9"]

    assert absent == {"absent_from_s1": True, "sites": 0}
    assert "any_site" not in absent
    assert "largest_site" not in absent


def test_dprime_takes_the_largest_site_by_published_intensity() -> None:
    """Two peptides for one symbol, only the weaker supported: `any_site` is true and
    `largest_site` is false, which is the whole reason both grains are reported."""
    block = _dprime([True, False], ["ADAR", "ADAR"], [5.0, 9.0])
    adar = block["tiers"]["results_curated"]["ADAR"]

    assert adar["sites"] == 2
    assert adar["any_site"] is True
    assert adar["largest_site"] is False
    assert adar["largest_site_intensity"] == pytest.approx(9.0)


# ── the staged-file loophole ────────────────────────────────────────────────────────────────────


def test_a_staged_but_uncommitted_file_does_not_count_as_committed(tmp_path: Path) -> None:
    """The pre-registration's rule is *committed before the run*, and `git add` is not a commit.

    `git ls-files --error-unmatch` answers *is this path in the index*, and a staged file is in
    the index — so the check this replaced passed for a file nobody else could see. Asking `HEAD`
    asks the commit.
    """
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@example.com"],
        ["git", "config", "user.name", "t"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "seed.txt"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=repo, check=True, capture_output=True)

    staged = repo / "author.json"
    staged.write_text(json.dumps(AUTHOR), encoding="utf-8")
    subprocess.run(["git", "add", "author.json"], cwd=repo, check=True, capture_output=True)

    assert h10.is_tracked(staged, repo_root=repo) is False

    subprocess.run(["git", "commit", "-qm", "author"], cwd=repo, check=True, capture_output=True)
    assert h10.is_tracked(staged, repo_root=repo) is True


def test_attempt_2_writes_its_own_fixture_and_never_attempt_1s(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """*"Attempt 1 is not replaced. Its result stands, and this attempt is reported beside it."*

    Run end to end at attempt 2 into a directory already holding an attempt 1 fixture, and that
    file's bytes are untouched while a second file appears beside it.

    **G2b's bands are widened for this run alone, and that is not a loosening of the check.**
    [58, 86] and [168, 252] are absolute counts calibrated to the deposit's 2,438 rows; a
    synthetic matrix small enough to run in a test cannot reach 58 of anything, so with the
    registered bands no variant is ever admitted here and the anchor path, readout D′ and the
    `validation` labels would all go untested. What the bands themselves do is asserted directly,
    at their own endpoints, by `test_g2b_bands_are_inclusive_at_both_ends`.
    """
    monkeypatch.setattr(h10, "G2B_WT_BAND", (0, 100))
    monkeypatch.setattr(h10, "G2B_KO_BAND", (0, 100))
    paths = _synthetic(tmp_path)
    _run(paths)
    attempt_1_path = Path(paths["fixtures_dir"]) / h10.FIXTURE_NAME
    before = attempt_1_path.read_bytes()

    _run(paths, attempt=2)

    assert attempt_1_path.read_bytes() == before
    attempt_2_path = Path(paths["fixtures_dir"]) / h10.FIXTURE_NAME_ATTEMPT_2
    assert attempt_2_path.exists()
    written = json.loads(attempt_2_path.read_text(encoding="utf-8"))
    assert written["anchor_run"] is True
    assert written["attempt"] == 2
    assert written["validation"] == "in-sample; independent confirmation pending"
    assert set(written["gate_g"]["variants"]) == {v.name for v in h10.ATTEMPT_2_VARIANTS}
    assert all("direction_split" in v for v in written["gate_g"]["variants"].values())
    assert written["readouts"]["validation"] == "in-sample; independent confirmation pending"
    assert set(written["readouts"]["readout_d_prime"]["tiers"]) == {
        "results_curated",
        "results_not_curated",
        "discussion",
    }
    # `_default_cell_supported` is `family_block_for`'s internal hand-off to D′ and must not reach
    # the file: attempt 1's fixture would otherwise have gained a key it never had.
    assert "_default_cell_supported" not in written["readouts"]


# ── attempt 3 ───────────────────────────────────────────────────────────────────────────────────


def _run_attempt_3(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    patch: Callable[[], None] | None = None,
    **overrides: Any,
) -> tuple[dict[str, Any], int, dict[str, Any]]:
    """Attempts 1, 2 and 3 in order, returning the paths and attempt 3's exit code and fixture.

    Attempt 2 runs first because attempt 3 §3 compares its own G2a and G2b against **attempt 2's
    committed fixture**, so that file has to exist before attempt 3 does anything.

    `patch` is called after those two runs and before attempt 3, and is where a test that stubs a
    module-level function installs it. Installing such a stub around the whole helper would apply
    it to attempts 1 and 2 as well — which is not merely wasteful but wrong: a spy returning an
    attempt-3 variant name made attempt 1's own `next(v for v in registered if v.name == primary)`
    raise `StopIteration`, so the test failed in a run it was not about. The two earlier attempts
    are the unstubbed instrument attempt 3 is measured against, and they stay that way.
    """
    paths = _synthetic(tmp_path)
    _run(paths)
    _run_attempt_2(paths, monkeypatch)
    if patch is not None:
        patch()
    code, written = _run(paths, attempt=3, **overrides)
    return paths, code, written


def test_attempt_3_runs_both_variants_and_reads_the_verdict_from_the_primary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§4: *"computed for both variants in full"*, and the verdict from the primary alone.

    Attempt 2 gave its secondaries readout A and nothing else, which is why readouts B, D and D′
    were never seen for these two variants — and why attempt 3 can still test H10 at all. Both
    blocks carry the full set here.
    """
    _, code, written = _run_attempt_3(tmp_path, monkeypatch)

    assert code == 0
    assert written["attempt"] == 3
    assert written["anchor_run"] is True
    assert set(written["readouts"]) == {"primary", "secondary"}
    for role, name in (
        ("primary", "joint_half+random_excluding_trivial"),
        ("secondary", "joint_half+exhaustive_excluding_trivial"),
    ):
        block = written["readouts"][role]
        assert block["variant"] == name
        assert block["admitted"] is True
        assert {"readout_a", "readout_b", "readout_c", "readout_d", "readout_d_prime"} <= set(block)
        # Each variant is its own primary here, so nothing is reported as a secondary inside it.
        assert "secondary_variants" not in block
    assert written["verdict_read_from"] == "primary"
    assert written["h10"] == written["readouts"]["primary"]["readout_b"]["verdict"]


def test_the_verdict_reads_the_primary_and_not_the_secondary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The two blocks are stubbed to carry **different** verdicts, so which one is read shows.

    On synthetic data both variants reach the same verdict, and an assertion that `h10` equals the
    primary's would then also hold of the secondary's — true of two identical things and a test of
    nothing. The stub makes them differ by construction.
    """
    real = h10.family_block_for
    verdicts = {
        "joint_half+random_excluding_trivial": "recurs",
        "joint_half+exhaustive_excluding_trivial": "absent",
    }

    def _stub(*, primary: h10.Variant, **kwargs: Any) -> dict[str, Any]:
        block = real(primary=primary, **kwargs)
        block["readout_b"]["verdict"] = {"outcome": verdicts[primary.name], "share": None}
        return block

    _, code, written = _run_attempt_3(
        tmp_path, monkeypatch, patch=lambda: monkeypatch.setattr(h10, "family_block_for", _stub)
    )

    assert code == 0
    assert written["readouts"]["primary"]["readout_b"]["verdict"]["outcome"] == "recurs"
    assert written["readouts"]["secondary"]["readout_b"]["verdict"]["outcome"] == "absent"
    assert written["h10"]["outcome"] == "recurs"


def test_readout_a_is_labelled_disclosed_before_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§1: readout A was measured in attempt 2 — 725 and 724 of 791 — so it *"is reported for
    completeness and is not scored as a prediction"*. A figure known before the run is a different
    kind of claim from one that was not, and only the file will be read later."""
    _, _, written = _run_attempt_3(tmp_path, monkeypatch)

    for role in ("primary", "secondary"):
        assert written["readouts"][role]["readout_a"]["disclosed_before_run"] is True


def test_every_attempt_3_result_block_carries_both_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§4's two: the fitted convention, and the matrix the run actually used.

    Attempt 2 §4 measured the second one — about 2% of S1's cells match log2 of the deposit, and
    7 published claims carry six S1 values apiece with no measured value in any deposit column —
    so every attempt-3 figure is about the deposit and has to say so where it is read.
    """
    _, _, written = _run_attempt_3(tmp_path, monkeypatch)

    for block in (written, written["readouts"]["primary"], written["readouts"]["secondary"]):
        assert block["validation"] == "in-sample; independent confirmation pending"
        assert block["matrix"] == "deposit, not the published S1"


def test_attempt_3_never_writes_the_earlier_fixture_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """*"Attempts 1 and 2 stand and are reported beside this one."* Beside, not over."""
    paths = _synthetic(tmp_path)
    _run(paths)
    _run_attempt_2(paths, monkeypatch)
    fixtures = Path(paths["fixtures_dir"])
    before = {
        name: (fixtures / name).read_bytes()
        for name in (h10.FIXTURE_NAME, h10.FIXTURE_NAME_ATTEMPT_2)
    }

    _run(paths, attempt=3)

    for name, bytes_ in before.items():
        assert (fixtures / name).read_bytes() == bytes_
    assert (fixtures / h10.FIXTURE_NAME_ATTEMPT_3).exists()
    assert h10.fixture_name_for(3) not in (h10.FIXTURE_NAME, h10.FIXTURE_NAME_ATTEMPT_2)


# ── §2 · the primary is fixed, not scored ───────────────────────────────────────────────────────


def test_the_attempt_3_primary_is_fixed_and_never_scored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§2: the primary is *"fixed by principle rather than by tie"* — not by F1, not by a readout.

    `primary_variant` is replaced by a spy that would hand back the **secondary** if anything
    asked it. Nothing does, and the primary is the registered one. The gate is also doctored so
    the secondary wins on every metric a scorer could read, which is what makes "never scored"
    testable rather than merely true of this data.
    """
    calls: list[Any] = []

    def _spy(*args: Any, **kwargs: Any) -> str:
        calls.append(args)
        return h10.ATTEMPT_3_SECONDARY.name

    real_gate = h10.gate_block

    def _favour_the_secondary(**kwargs: Any) -> dict[str, Any]:
        gate = real_gate(**kwargs)
        if h10.ATTEMPT_3_PRIMARY.name in gate["variants"]:
            gate["variants"][h10.ATTEMPT_3_PRIMARY.name]["f1"] = 0.10
            gate["variants"][h10.ATTEMPT_3_SECONDARY.name]["f1"] = 0.99
        return gate

    def _install() -> None:
        monkeypatch.setattr(h10, "primary_variant", _spy)
        monkeypatch.setattr(h10, "gate_block", _favour_the_secondary)

    _, code, written = _run_attempt_3(tmp_path, monkeypatch, patch=_install)

    assert code == 0
    assert calls == []
    assert written["primary_variant"] == "joint_half+random_excluding_trivial"
    assert written["readouts"]["primary"]["variant"] == "joint_half+random_excluding_trivial"
    assert written["gate_g"]["variants"][h10.ATTEMPT_3_SECONDARY.name]["f1"] == 0.99


# ── §3 · check A on the typical draw ────────────────────────────────────────────────────────────


def test_check_a_uses_the_median_over_seeds_and_not_any_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§3's correction, and the case it was written for.

    One seed reaches a claim and the other nineteen reach none, so the median is 0 and the
    variant is **not** admitted — while attempt 2's *any seed* rule would admit it. That is
    exactly what happened to `joint_half+random`: reached at seed 4, nothing in a typical draw,
    made primary by a tie rule, and H10 went untested in substance.

    The test statistic is stubbed rather than drawn, because a matrix small enough to run here
    does not produce a one-seed-in-twenty result on demand; what is under test is which summary
    of the twenty counts admits a variant.
    """

    class _Outcome:
        def __init__(self, seed: int) -> None:
            self.significant = np.array([seed == 4, False])
            self.d = np.array([1.0, 1.0])

    monkeypatch.setattr(h10, "perseus_s0", lambda *a, **k: _Outcome(int(k["seed"])))
    result = h10.check_a_typical(
        numerator=np.ones((2, 3)),
        denominator=np.ones((2, 3)) * 2,
        claim_rows=[0, 1],
        variants=[h10.ATTEMPT_3_PRIMARY],
        randomisations=10,
        seeds=tuple(range(20)),
        progress=False,
    )

    entry = result[h10.ATTEMPT_3_PRIMARY.name]
    # **The counts must not be constant**, or every summary of them is the same number and no test
    # over them can tell one from another. This is asserted rather than read off the stub because
    # it is the condition that makes the test below meaningful, and because it is exactly what
    # fails at synthetic scale: in `test_check_a_reports_every_seeds_count` every seed returns the
    # same count, so reporting the mean instead of the median leaves that test green — the same
    # shape as the pooled-versus-Welch and harmonic-versus-arithmetic traps this suite has hit.
    assert len(set(entry["counts_by_seed"])) > 1
    assert entry["counts_by_seed"][4] == 1
    assert sum(entry["counts_by_seed"]) == 1
    assert entry["median"] == 0.0
    assert entry["reached"] is False
    # The *any seed* rule is still reported, so the difference between the two is visible rather
    # than only its consequence.
    assert entry["reached_under_any_seed"] is True


def test_check_a_reports_every_seeds_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """§3: *"Report every seed's count."* A median of 1 over `[0, 0, 1, 40]` and one over
    `[1, 1, 1, 1]` are different facts about a variant."""
    _, _, written = _run_attempt_3(tmp_path, monkeypatch)

    for name in ("joint_half+random_excluding_trivial", "joint_half+exhaustive_excluding_trivial"):
        entry = written["check_a"][name]
        assert len(entry["counts_by_seed"]) == len(GATE_SEEDS)
        assert entry["minimum_required"] == 1
        assert entry["median"] == float(np.median(entry["counts_by_seed"]))
        assert entry["reached"] is (entry["median"] >= 1)


# ── §3 · the rerun-consistency check ────────────────────────────────────────────────────────────


def test_a_g2_mismatch_stops_the_run_as_an_instrument_fault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§3: G2a and G2b are deterministic given the seeds, so a difference is the instrument having
    changed under a registration that assumes it did not — not a finding about the anchor.

    One direction count in the committed attempt-2 fixture is moved by one, which is the smallest
    difference the comparison can see, and the run stops with nothing after the gate computed.
    """
    paths = _synthetic(tmp_path)
    _run(paths)
    _run_attempt_2(paths, monkeypatch)
    attempt_2_path = Path(paths["fixtures_dir"]) / h10.FIXTURE_NAME_ATTEMPT_2
    doctored = json.loads(attempt_2_path.read_text(encoding="utf-8"))
    split = doctored["gate_g"]["variants"][h10.ATTEMPT_3_PRIMARY.name]["direction_split"]
    split["higher_in_wt"] += 1
    attempt_2_path.write_text(json.dumps(doctored), encoding="utf-8")

    code, written = _run(paths, attempt=3)

    assert code == 1
    assert written["instrument_fault"] is True
    assert written["g2_rerun_consistency"]["consistent"] is False
    assert [d["field"] for d in written["g2_rerun_consistency"]["differences"]] == ["higher_in_wt"]
    # Nothing after the gate ran.
    assert "check_a" not in written
    assert "readouts" not in written
    assert "h10" not in written


def test_the_consistency_check_compares_counts_and_not_shares() -> None:
    """Six integers per variant. A share is a quotient, and two different pairs of counts can
    produce the same one — 83/83 and 1/1 are both a precision of 1.00."""
    gate = {
        "variants": {
            h10.ATTEMPT_3_PRIMARY.name: {
                "precision": {"numerator": 1, "denominator": 1, "share": 1.0},
                "recall": {"numerator": 1, "denominator": 1, "share": 1.0},
                "direction_split": {"higher_in_wt": 64, "higher_in_knockout": 212},
            }
        }
    }
    earlier = {
        "gate_g": {
            "variants": {
                h10.ATTEMPT_3_PRIMARY.name: {
                    "precision": {"numerator": 83, "denominator": 83, "share": 1.0},
                    "recall": {"numerator": 83, "denominator": 86, "share": 0.965},
                    "direction_split": {"higher_in_wt": 64, "higher_in_knockout": 212},
                }
            }
        }
    }

    result = h10.g2_rerun_consistency(gate, earlier, variants=[h10.ATTEMPT_3_PRIMARY])

    assert result["consistent"] is False
    assert {d["field"] for d in result["differences"]} == {
        "precision_numerator",
        "precision_denominator",
        "recall_numerator",
        "recall_denominator",
    }


def test_a_variant_absent_from_the_earlier_fixture_is_a_mismatch() -> None:
    """Attempt 2 ran four variants and attempt 3 runs two of them, so this should never fire. It
    fires if the committed fixture is not the run attempt 3 thinks it is."""
    gate: dict[str, Any] = {"variants": {h10.ATTEMPT_3_PRIMARY.name: {}}}

    result = h10.g2_rerun_consistency(gate, {}, variants=[h10.ATTEMPT_3_PRIMARY])

    assert result["consistent"] is False
    assert result["differences"][0]["reason"] == "absent"


def test_an_unadmitted_primary_leaves_h10_not_tested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§3: *"If the primary is not admitted, no readout is reported as primary, and the result is
    H10 not tested (attempt 3)."* The family does not run at all."""
    _, code, written = _run_attempt_3(
        tmp_path,
        monkeypatch,
        patch=lambda: monkeypatch.setattr(h10, "CHECK_A_MEDIAN_MINIMUM", 10**6),
    )

    assert code == 1
    assert written["h10"] == "not tested (attempt 3)"
    assert written["primary_admitted"] is False
    assert written["admitted_variants"] == []
    assert "readouts" not in written
    # The checks that did run are still reported: the result is a finding, not a blank.
    assert written["g2_rerun_consistency"]["consistent"] is True
    assert set(written["check_a"]) == {v.name for v in h10.ATTEMPT_3_VARIANTS}
