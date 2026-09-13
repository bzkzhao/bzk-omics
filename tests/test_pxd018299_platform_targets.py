"""Guards for the platform path's per-target fixture (`pxd018299_platform_targets.json`).

`bzk/sources/pxd018299_differential.py` computed which of the fourteen published targets the
platform path recovers and, until this fixture existed, printed the answer and kept none of it.
The membership survived a run as terminal output only — and that membership is exactly the figure
the slice is about, since `ROADMAP.md`'s 12-of-14 is a statement about *identifiability* and this
path's number counts something else (the module's docstring says so at length). A number that
exists nowhere durable cannot be compared against the next run of it.

`tests/test_pxd018299_baseline.py` does this for the notebook transcription; this is the same
shape for the other path, and the two fixtures are deliberately not interchangeable — `path`
separates them and a test below pins it.

**What is deliberately *not* asserted here: which genes are recovered.** The baseline fixture pins
ADAR and PSMB9 as misses because those two are established — `ROADMAP.md` § Measured findings
measured them. This path's membership is the open question, so a pinned list written today would
be a list written from prose, which is the failure `CLAUDE.md` § Working style names. What is
pinned instead is *internal agreement*: that each verdict follows from the sites recorded under it,
against thresholds read from the module rather than restated here.

Every check is offline: the fixture is a committed artefact, so it is read unconditionally the way
`tests/test_pxd018299_baseline.py` reads its own. Nothing here needs `raw/` or the populated graph.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from bzk.sources.pxd018299_differential import (
    EXPECTED_TARGETS,
    SIG_ADJ_P,
    SIG_LOG2FC,
    STATUS_ABSENT_FROM_TESTED,
    STATUS_RECOVERED,
    STATUS_TESTED_NOT_RECOVERED,
    STATUS_VALUES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "pxd018299_platform_targets.json"


def _fixture() -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(FIXTURE.read_text()))


def _rows() -> list[dict[str, Any]]:
    return cast("list[dict[str, Any]]", _fixture()["targets"])


def _clears_thresholds(site: dict[str, Any]) -> bool:
    """The module's own criterion, over one recorded site. Thresholds imported, never retyped.

    A site whose statistics are null (NaN in the run) clears nothing, which is the module's
    behaviour too: `up` is built from comparisons, and every comparison against NaN is false.
    """
    if site["adj_p"] is None or site["log2fc"] is None:
        return False
    return bool(site["adj_p"] < SIG_ADJ_P and site["log2fc"] > SIG_LOG2FC)


def test_fixture_covers_exactly_the_published_targets() -> None:
    """Membership against the module's own constant, not a count.

    By membership rather than length because fourteen rows and fourteen *published targets* are
    different claims, and a fixture regenerated after the target list changed would satisfy the
    weaker one while naming a different set.
    """
    assert {row["gene"] for row in _rows()} == set(EXPECTED_TARGETS)


def test_fixture_declares_the_platform_path() -> None:
    """`path` is what stops this being read as the baseline fixture, so it is pinned."""
    assert _fixture()["path"] == "platform"


def test_every_status_is_one_of_the_three_permitted_values() -> None:
    assert {row["status"] for row in _rows()} <= set(STATUS_VALUES)


def test_absence_from_the_tested_population_is_not_collapsed_into_a_threshold_miss() -> None:
    """The two negative states are distinguishable from the rows themselves, in both directions.

    A target absent from the tested population has no sites; a target tested and not recovered has
    at least one. Collapsing them is the failure `HANDOFF.md` §6 records — a broken gene lookup
    that "reads exactly like a real negative result" — and the boolean `recovered` the baseline
    carries could not express the difference at all.
    """
    for row in _rows():
        if row["status"] == STATUS_ABSENT_FROM_TESTED:
            assert row["sites"] == [], row["gene"]
        else:
            assert row["sites"], row["gene"]


def test_each_site_agrees_with_the_status_of_the_target_it_sits_under() -> None:
    """The verdict must follow from the recorded numbers, or the fixture asserts its own conclusion.

    This is the check `test_recovered_flag_agrees_with_the_row_it_sits_on` makes for the baseline,
    over all of a target's sites rather than one picked site. A hand-edit that flipped a status
    without touching the statistics behind it fails here.
    """
    for row in _rows():
        cleared = [site for site in row["sites"] if _clears_thresholds(site)]
        if row["status"] == STATUS_RECOVERED:
            assert cleared, row["gene"]
        else:
            assert not cleared, row["gene"]


def test_every_recovered_target_has_a_site_clearing_both_thresholds() -> None:
    """Stated separately from the agreement check because it is the load-bearing half.

    A recovered target whose sites all fail the thresholds would be a recovery claim with nothing
    under it, which is the one failure this fixture exists to make impossible to commit quietly.
    """
    for row in _rows():
        if row["status"] != STATUS_RECOVERED:
            continue
        assert any(_clears_thresholds(site) for site in row["sites"]), row["gene"]


def test_no_tested_target_is_marked_recovered_without_being_tested() -> None:
    """`tested_not_recovered` and `recovered` both require sites; only absence may have none."""
    for row in _rows():
        if row["status"] in (STATUS_RECOVERED, STATUS_TESTED_NOT_RECOVERED):
            assert row["sites"], row["gene"]


def test_every_site_carries_its_identifier_and_its_three_statistics() -> None:
    """Identifiers are the point: three integers cannot tell one twelve from a different twelve.

    `site` is the resolved `ModificationSite` key and `observation` the `SiteObservation` the row
    became; `observation` is required because it is what the graph's `RESULT_FOR_SITE` attaches to.
    """
    for row in _rows():
        for site in row["sites"]:
            assert {"site", "observation", "log2fc", "p", "adj_p"} == set(site), row["gene"]
            assert site["observation"], row["gene"]


def test_the_note_discloses_why_population_is_recorded_here() -> None:
    """The baseline fixture restates no counts; this one does, and the reason must travel with it.

    `CLAUDE.md` § Single source of truth makes a second copy of a fact a defect. These counts are
    not a second copy — no analysis record holds this path's population — but a reader cannot
    know that from the file unless the file says so.
    """
    note = _fixture()["note"]
    assert "population" in note
    assert "analysis_PXD018299_KOIFN_vs_WTIFN.json" in note


def test_the_note_says_a_change_here_is_explained_rather_than_regenerated() -> None:
    """Without this the fixture is a ratchet: regenerate, commit, and the finding is gone."""
    note = _fixture()["note"]
    assert "explaining" in note
    assert "python -m bzk.sources.pxd018299_differential" in note


def test_fixture_records_the_environment_it_was_generated_under() -> None:
    """numpy and scipy both move these numbers — `welch_t` takes its p-value from `scipy.stats`.

    pandas is deliberately absent, unlike in the baseline fixture: this path never loads it, and a
    version recorded for a library the run did not use is a false provenance claim.
    """
    generated_under = _fixture()["generated_under"]
    assert {"python", "numpy", "scipy"} <= set(generated_under)
    assert "pandas" not in generated_under
