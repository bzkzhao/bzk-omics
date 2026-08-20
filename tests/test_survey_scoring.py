"""`bzk/survey_scoring.py` against synthetic fixtures whose every figure is hand-computable.

**No test here reads a deposit's table.** The three fixtures are written to exercise the branches a
real site table reaches only by accident — a razor pick falling back to `Leading proteins`, an
unparseable base, a zero base with a non-zero total, a 0-100 localisation scale, a SILAC sample with
no multiplicity columns — and they pass in an un-populated container.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bzk.survey_scoring import (
    MIN_MULTIPLICITY_COMPARISONS,
    MIN_PICK_SAMPLE,
    Scores,
    score_site_table,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def basic() -> Scores:
    return score_site_table(FIXTURES / "survey_scoring_basic.txt", ["S1"])


def test_denominator_excludes_reverse_and_contaminant_and_nothing_else(basic: Scores) -> None:
    """The registered denominator (l.8189-8190): both flag columns empty, no localisation cut.

    Eleven data rows, of which one is `Reverse` and one `Potential contaminant`. The blank trailing
    line is not a row and the short row is padded rather than dropped, so the total is eleven.
    """
    assert basic.rows_total == 11
    assert basic.rows_in_denominator == 9


def test_localisation_cut_is_reported_and_is_not_the_denominator(basic: Scores) -> None:
    """The third count is diagnostic (l.8197-8200) and must not be what the rates divide by."""
    assert basic.rows_after_localisation_cut == 8
    assert basic.multi_mapping.total == basic.rows_in_denominator == 9


def test_criterion_1_counts_a_semicolon_list_with_empty_parts_discarded(basic: Scores) -> None:
    """`P3;;P4` is two accessions, not three (l.8206-8207)."""
    assert (basic.multi_mapping.multi, basic.multi_mapping.total) == (3, 9)


def test_criterion_2_falls_back_to_leading_proteins_and_reads_isoforms_from_spelling(
    basic: Scores,
) -> None:
    """`Protein` where present, else the first of `Leading proteins`; isoform iff `-` (l.8218-8220).

    The fallback row is the only source of the `P4-2` isoform, so a regression that dropped the
    fallback would show here as 1 isoform rather than 2.

    **Numerator and denominator are pinned as a pair throughout this module, never as a quotient.**
    The tautology sweep flags `x == pytest.approx(literal)` and it is right to: a quotient asserted
    under a default relative tolerance is satisfied by two wrong counts in the same ratio, where the
    pair is not.
    """
    assert basic.isoform_picks.sample == 9
    assert basic.isoform_picks.isoform == 2


def test_criterion_9_is_the_yes_no_and_the_rate_rides_alongside(basic: Scores) -> None:
    """One row below 0.75, so not pre-filtered (l.8236-8238); the rate is measured, not scored."""
    assert basic.unrecorded_threshold.below_cut == 1
    assert basic.unrecorded_threshold.total == 9
    assert basic.unrecorded_threshold.pre_filtered is False


def test_criterion_6_ignores_unparseable_probabilities_and_leaves_minimum_out_of_the_test(
    basic: Scores,
) -> None:
    """Eight parseable values; the short row's empty cell contributes none (l.8257-8259).

    The minimum is 0.5 and the verdict is still *does not differ*, which is the point: the band
    names median, column name and scale, and the minimum is reported rather than tested.
    """
    assert (basic.localisation.median, basic.localisation.minimum) == (1.0, 0.5)
    assert basic.localisation.maximum == 1.0
    assert basic.localisation.differs is False


def test_criterion_5_tolerance_is_one_absolute_unit(basic: Scores) -> None:
    """`|100 - 99| = 1` agrees and `|10 - 6| = 4` does not (l.8280-8281)."""
    assert (basic.multiplicity.agree, basic.multiplicity.comparisons) == (4, 5)


def test_criterion_5_separates_trivial_from_zero_base_with_a_non_zero_total(basic: Scores) -> None:
    """Trivial rows agree vacuously; a zero base with a non-zero total is neither (l.8283-8284).

    The registration computes the verdict over `base > 0`, which leaves the second shape outside
    both clauses. It is surfaced rather than folded into `trivial`, where it would inflate agreement.
    """
    assert basic.multiplicity.trivial == 1
    assert basic.multiplicity.zero_base_nonzero_total == 1


def test_criterion_5_excludes_an_unparseable_base_and_zeroes_an_unparseable_operand(
    basic: Scores,
) -> None:
    """`NaN` as a base drops the row; empty as a `___j` operand reads as 0 and is counted.

    Both substitutions are in the same fixture and they are not symmetric — that asymmetry is the
    registration's (l.8276-8278) and a single test would let one half rot.
    """
    assert basic.multiplicity.substituted_operands == 2
    assert (
        basic.multiplicity.comparisons
        + basic.multiplicity.trivial
        + (basic.multiplicity.zero_base_nonzero_total)
        == 7
    )  # nine denominator rows less the `NaN` base and the short row's empty base


def test_criterion_5_below_the_floor_is_unscorable_not_a_verdict(basic: Scores) -> None:
    """Five comparisons is under twenty, so no verdict is reported (l.8287-8288)."""
    assert basic.multiplicity.comparisons < MIN_MULTIPLICITY_COMPARISONS
    assert basic.multiplicity.verdict == "unscorable"


def test_a_hundred_scale_and_a_pre_filtered_table() -> None:
    """No row below 0.75 reads as pre-filtered even on a 0-100 scale, and the scale is caught.

    These travel together on purpose: a table rescaled to 0-100 has no row below 0.75 *by
    construction*, so criterion 9's yes/no cannot distinguish it from a genuine pre-filter. The
    scale check in criterion 6 is what catches it, and this fixture pins that division of labour.
    """
    scores = score_site_table(FIXTURES / "survey_scoring_prefiltered.txt", [])
    assert scores.unrecorded_threshold.pre_filtered is True
    assert (scores.localisation.median, scores.localisation.maximum) == (95.0, 100.0)
    assert scores.localisation.differs is True


def test_criterion_2_below_its_band_floor_is_unscorable(basic: Scores) -> None:
    """Three picks is under the band's twenty (l.3885, l.8223-8225) — the third state, not a verdict."""
    scores = score_site_table(FIXTURES / "survey_scoring_prefiltered.txt", [])
    assert scores.isoform_picks.sample == 3 < MIN_PICK_SAMPLE
    assert scores.isoform_picks.scorable is False
    assert basic.isoform_picks.scorable is False  # nine picks, also under the floor


def test_a_sample_with_no_multiplicity_columns_contributes_nothing_rather_than_failures() -> None:
    """A SILAC table splits multiplicity on the ratio family, not on per-sample intensity.

    `S1` has `Intensity S1` and `Intensity L S1` but no `Intensity S1___1`, so there is no identity
    to test and it must not be scored as three disagreements. `S3` is absent from the header
    altogether and is skipped without being counted as a sample lacking columns — the two states are
    different and only one of them says anything about the artefact.
    """
    scores = score_site_table(FIXTURES / "survey_scoring_silac.txt", ["S1", "S2", "S3"])
    assert scores.multiplicity.samples_without_multiplicity_columns == 1
    assert scores.multiplicity.comparisons == 3
    assert scores.multiplicity.agree == 2  # S2: 20=12+8 and 40=40+0 agree, 60 vs 10+10 does not


def test_an_empty_sample_list_leaves_criterion_5_unscorable_and_the_rest_intact(
    basic: Scores,
) -> None:
    """Scoring without sample names is legitimate — four of the five need none."""
    scores = score_site_table(FIXTURES / "survey_scoring_basic.txt", [])
    assert scores.multiplicity.comparisons == 0
    assert scores.multiplicity.verdict == "unscorable"
    assert scores.multi_mapping == basic.multi_mapping
    assert scores.isoform_picks == basic.isoform_picks
    assert scores.unrecorded_threshold == basic.unrecorded_threshold


def test_a_header_only_table_scores_zero_rather_than_raising(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("Proteins\tProtein\tLocalization prob\tReverse\tPotential contaminant\n")
    scores = score_site_table(path, [])
    assert scores.rows_total == 0
    assert scores.multi_mapping.rate is None
    assert scores.localisation.median is None
    assert scores.localisation.differs is None
    assert scores.unrecorded_threshold.pre_filtered is True  # zero rows below the cut, vacuously


def test_a_file_with_no_header_raises(tmp_path: Path) -> None:
    path = tmp_path / "nothing.txt"
    path.write_text("")
    with pytest.raises(ValueError, match="no header line"):
        score_site_table(path, [])
