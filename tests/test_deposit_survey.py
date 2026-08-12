"""The survey instrument's guards, exercised offline.

**Why this file exists.** `bzk/drift.py` and `bzk/fetch_progress.py` — the two modules
`bzk/deposit_survey.py`'s docstring names as its siblings — both have test files. This one did not,
which left the class guarded and one member outside it.

**Nothing here touches the network.** `bzk/http.py` declares `RestSession` as a `Protocol` so a
stub can be injected, and that is what every test below does. Eleven tests in this suite already
skip in a sandboxed clone for want of a network; a guard against silent zeroes that skips exactly
where the network is unavailable would be absent in the case it exists for.

**The load-bearing one is `self_check`.** `files/byProject` answers `200 application/json` with an
empty body, so a broken call and a fileless deposit are indistinguishable, and `self_check` is the
only thing that separates them. It is also the guard most easily made worthless: filtered by
`SITE_TABLE_MARKER` it would pass on whatever the marker had been widened to match, which is the
"passes for the wrong reason" shape. Both properties are asserted.
"""

from __future__ import annotations

from typing import Any

import pytest

from bzk.deposit_survey import (
    SITE_ABSENT,
    SITE_CANDIDATE,
    SITE_PRESENT,
    Candidate,
    expand_archives,
    file_names,
    search,
    self_check,
    survey,
)
from bzk.sources.pride import PXD018299_SITES


class _Response:
    def __init__(self, payload: Any, status: int = 200) -> None:
        self._payload = payload
        self.status_code = status

    @property
    def text(self) -> str:
        return str(self._payload)

    def json(self) -> Any:
        return self._payload


class _Session:
    """A `RestSession` that answers from a dict of URL-fragment -> payload."""

    def __init__(self, routes: dict[str, Any], status: int = 200) -> None:
        self.routes = routes
        self.status = status
        self.seen: list[str] = []

    def get(self, url: str, *, timeout: int = 0) -> _Response:
        self.seen.append(url)
        for fragment, payload in self.routes.items():
            if fragment in url:
                return _Response(payload, self.status)
        return _Response([], self.status)


def _listing(*names: str) -> list[dict[str, Any]]:
    return [{"fileName": n} for n in names]


# ── self_check: the guard against a silently empty endpoint ───────────────────────────────────


def test_self_check_passes_when_the_canary_file_is_listed() -> None:
    session = _Session({"/files": _listing(PXD018299_SITES.filename, "other.raw")})
    self_check(session=session)  # must not raise


def test_self_check_fails_on_the_empty_body_that_files_by_project_returns() -> None:
    """The exact failure it exists for: `200 application/json` and nothing in it."""
    session = _Session({"/files": []})
    with pytest.raises(RuntimeError) as ei:
        self_check(session=session)
    assert "listed 0 file(s)" in str(ei.value)
    assert PXD018299_SITES.filename in str(ei.value)


def test_self_check_fails_when_the_listing_answers_without_the_canary_file() -> None:
    """A non-empty listing missing the one file that must be there is also a broken endpoint."""
    session = _Session({"/files": _listing("HAP1_USP18KO_proteinGroups.txt", "run1.raw")})
    with pytest.raises(RuntimeError):
        self_check(session=session)


def test_self_check_cannot_be_satisfied_by_widening_the_site_marker() -> None:
    """The coupling this guard was rewritten for, asserted rather than commented.

    The first version filtered the listing with `SITE_TABLE_MARKER`. Any deposit carrying *some*
    file matching whatever that constant had grown to would then satisfy the canary — so widening
    site detection would silently widen the thing guarding it. This asserts the canary is now
    keyed to one exact filename: a listing full of files that satisfy every site rule in the
    module, without that filename, still fails.
    """
    plausible = _listing(
        "SomeOther_GlyGlySites.txt",  # matches SITE_TABLE_MARKER
        "abundance_single-site_MS2quant_Norm.tsv",  # matches SITE_TABLE_HINTS
        "UbPTMs_PTMs_Summary.txt",  # matches SITE_TABLE_HINTS
    )
    assert Candidate("x", "", "", files=tuple(f["fileName"] for f in plausible)).site_state == (
        SITE_PRESENT
    )
    with pytest.raises(RuntimeError):
        self_check(session=_Session({"/files": plausible}))


# ── C0(c): three states, because a name is evidence and not proof ─────────────────────────────


def _c(*names: str) -> Candidate:
    return Candidate("PXD000000", "t", "PARTIAL", files=names)


def test_the_three_state_values_are_what_they_say() -> None:
    """Every other site-state assertion here compares against these names, so if a name's *value*
    drifted both sides would drift with it — the tautology shape, one level out. What those tests
    pin is which branch was taken, which is what mutating the branch has to break; what this one
    pins is the vocabulary, so `candidate` cannot quietly become `present`."""
    assert (SITE_PRESENT, SITE_CANDIDATE, SITE_ABSENT) == ("present", "candidate", "absent")


def test_site_state_is_present_only_for_maxquants_own_convention() -> None:
    assert _c("HAP1_USP18KO_GlyGlyKSites.txt").site_state == SITE_PRESENT
    assert _c("HAP1_USP18KO_GlyGlyKSites.txt").site_tables == ("HAP1_USP18KO_GlyGlyKSites.txt",)


def test_a_site_grain_table_outside_that_convention_is_candidate_not_absent() -> None:
    """`PXD076163`'s real filename. Reported `absent` before this turn, which is the under-report
    the survey's own limits paragraph named."""
    got = _c("abundance_single-site_MS2quant_Norm.tsv", "proteinGroups.txt")
    assert got.site_state == SITE_CANDIDATE
    assert got.site_candidates == ("abundance_single-site_MS2quant_Norm.tsv",)
    assert got.site_tables == ()


def test_a_candidate_is_never_promoted_to_present() -> None:
    """The over-inclusive failure, which is the same defect facing the other way. `PTMs_Summary`
    says PTM and settles no grain, so it must not satisfy C0(c) on its name."""
    assert _c("UbPTMs_PTMs_Summary.txt").site_state == SITE_CANDIDATE
    assert _c("UbPTMs_PTMs_Summary.txt").site_tables == ()


def test_a_hint_inside_a_spectra_filename_is_not_a_candidate_table() -> None:
    assert _c("20190520_phospho_run1.raw").site_state == SITE_ABSENT
    assert _c("S1_1_site-enriched.mzML").site_state == SITE_ABSENT


def test_site_state_is_absent_when_nothing_suggests_grain() -> None:
    assert _c("proteinGroups.txt", "run.raw").site_state == SITE_ABSENT


def test_a_site_table_inside_an_archive_is_seen_through_the_entry_name() -> None:
    """`expand_archives` returns `archive!entry`, so detection must read the basename."""
    assert _c("Search.zip!Output/GlyGly (K)Sites.txt").site_state == SITE_PRESENT


# ── C0(d): no processed output and unclassified output are different findings ─────────────────


def test_engine_state_separates_no_output_from_unclassified_output() -> None:
    """Five of twelve read *none identifiable* in the first run, collapsing both."""
    assert _c("run1.raw", "run2.mzML").engine_state == "no_processed_output"
    assert _c("Peptides_UbPTMs.txt", "UbPTMs_PTMs_Summary.txt").engine_state == "unclassified"
    assert _c("proteinGroups.txt", "evidence.txt").engine_state == "maxquant"


def test_an_engine_marker_in_the_middle_of_a_name_does_not_classify() -> None:
    """The suffix rule itself, pinned — and it was missing.

    A mutation restoring `m in b` substring matching passed all nineteen tests on the first
    mutation run, because the same change also dropped the generic `summary.txt` marker that made
    substring matching visible. Two fixes, one assertion: the defect was unobservable through the
    suite that had just caught it. This asserts the rule rather than one instance of it.
    """
    from bzk.deposit_survey import ENGINE_MARKERS

    for engine, marks in ENGINE_MARKERS.items():
        for mark in marks:
            embedded = _c(f"prefix_{mark}_suffix.txt")
            assert engine not in embedded.engines, f"{mark} classified from mid-name"
    assert _c("HAP1_USP18KO_proteinGroups.txt").engines == ("maxquant",)


def test_a_compressed_table_still_classifies() -> None:
    """Stripping one compression wrapper before matching, so the suffix rule does not trade one
    under-report for another: a gzipped `evidence.txt` is a MaxQuant table."""
    assert _c("evidence.txt.gz").engines == ("maxquant",)
    assert _c("Search/GlyGly (K)Sites.txt.gz").site_state == SITE_PRESENT


def test_a_site_table_alone_no_longer_marks_a_deposit_maxquant() -> None:
    """`sites.txt` was both C0(c)'s marker and a MaxQuant engine marker, so one constant answered
    two questions and a non-MaxQuant site table marked the whole deposit MaxQuant."""
    got = _c("abundance_single-site_MS2quant_Norm.tsv")
    assert "maxquant" not in got.engines
    assert got.engine_state == "unclassified"


# ── expand_archives: every skip is accounted for ──────────────────────────────────────────────


def test_archives_skipped_by_format_are_recorded_not_silent() -> None:
    """The quieter of the two skips: hint-filtered archives left no trace at all, because the
    unlisted count only ever counted archives beyond the cap."""
    _, _, skipped = expand_archives("PXD000000", ("S1_1.d.zip", "S1_2.d.zip"), limit=3)
    assert len(skipped) == 2
    assert all("instrument format" in s for s in skipped)


def test_archives_beyond_the_cap_are_recorded_individually() -> None:
    names = tuple(f"Search_{i}.zip" for i in range(5))
    _, _, skipped = expand_archives("PXD000000", names, limit=0)
    assert len(skipped) == 5
    assert all("beyond the limit of 0" in s for s in skipped)


def test_a_name_habit_no_longer_skips_an_archive() -> None:
    """`raw_` and `_raw` were guesses about naming and are gone; only container formats remain."""
    _, _, skipped = expand_archives("PXD000000", ("raw_search_output.zip",), limit=0)
    assert skipped == ("raw_search_output.zip: beyond the limit of 0",)


# ── search and survey: the draw, offline ──────────────────────────────────────────────────────


def test_survey_shares_the_cap_across_the_registered_queries() -> None:
    """Straight iteration gave the first query every slot; `diGly` and `ubiquitinome` — 25 results
    each — were never queried at all in the first run."""
    routes = {
        "keyword=A": [{"accession": f"PXA{i}"} for i in range(10)],
        "keyword=B": [{"accession": f"PXB{i}"} for i in range(10)],
    }
    got = survey(("A", "B"), cap=4, session=_Session(routes))
    assert [c.accession for c in got] == ["PXA0", "PXB0", "PXA1", "PXB1"]


def test_a_query_returning_nothing_contributes_nothing_and_does_not_stall() -> None:
    """`ubiquitin GlyGly` returns 0 against the live API."""
    routes = {"keyword=A": [], "keyword=B": [{"accession": "PXB0"}, {"accession": "PXB1"}]}
    got = survey(("A", "B"), cap=4, session=_Session(routes))
    assert [c.accession for c in got] == ["PXB0", "PXB1"]


def test_file_names_falls_back_to_the_public_location_when_filename_is_absent() -> None:
    rows = [{"publicFileLocations": [{"value": "ftp://ftp.pride.ebi.ac.uk/a/b/thing.txt"}]}]
    assert file_names("PXD000000", session=_Session({"/files": rows})) == ("thing.txt",)


def test_a_non_200_is_an_error_rather_than_an_empty_result() -> None:
    """An endpoint that fails must not read as a deposit with no files."""
    with pytest.raises(RuntimeError):
        search("anything", session=_Session({"search": []}, status=503))
