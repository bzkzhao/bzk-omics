"""The survey instrument's guards, exercised offline.

**Why this file exists.** `bzk/drift.py` and `bzk/fetch_progress.py` — the two modules
`bzk/deposit_survey.py`'s docstring names as its siblings — both have test files. This one did not,
which left the class guarded and one member outside it.

**Nothing here touches the network — true as of 2026-08-12 and false when this sentence was first
written.** Three of the archive tests reached `www.ebi.ac.uk` and **failed** in a clone that cannot,
which is worse than the skipping this paragraph was warning about: a clean checkout reported a red
suite, and the guard that went missing covered the archive-visibility fixes those tests were written
for. They passed here only because this container can reach the API. `expand_archives` now takes a
`session` like every sibling and defers its URL fetch until an archive is actually opened, and
`test_expand_archives_makes_no_request_when_no_archive_will_be_opened` asserts the absence directly
— because a container with a network cannot tell a deferred fetch from an eager one by outcome.

**That path is exercised as of 2026-08-12.** `archive_entries` took no session because it needs
`head` and a `headers=` keyword; `bzk/http.py` now declares a third Protocol for exactly that, so
the parser is tested here against archives `zipfile` builds — a fixture assembled by hand would
restate the parser's own arithmetic. Four silent-zero routes are closed with it, each made to fail
before it passed.

**The load-bearing one is `self_check`.** `files/byProject` answers `200 application/json` with an
empty body, so a broken call and a fileless deposit are indistinguishable, and `self_check` is the
only thing that separates them. It is also the guard most easily made worthless: filtered by
`SITE_TABLE_MARKER` it would pass on whatever the marker had been widened to match, which is the
"passes for the wrong reason" shape. Both properties are asserted.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib
from collections.abc import Mapping
from typing import Any

import pytest

from bzk.deposit_survey import (
    SITE_ABSENT,
    SITE_CANDIDATE,
    SITE_PRESENT,
    ArchiveMember,
    Candidate,
    archive_entries,
    archive_members,
    classify,
    expand_archives,
    extract_member,
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


# ── the MaxQuant matcher: anchored token matching, derived from the tool's documentation ──────


def test_a_token_appended_before_the_extension_still_classifies() -> None:
    """`endswith` was defeated by a suffix inserted before the extension. `PXD027328` deposits
    `modificationSpecificPeptides_ntermUb.txt`, which is MaxQuant's own table name with `_ntermUb`
    appended, and the deposit read `unclassified` on a table it plainly wrote."""
    assert _c("modificationSpecificPeptides_ntermUb.txt").engines == ("maxquant",)
    assert _c("proteinGroups_filtered.txt").engines == ("maxquant",)


def test_the_anchor_deposits_prefixed_filename_still_matches() -> None:
    """The constraint a stricter form would silently break. `PXD018299` is already ingested and
    deposits `HAP1_USP18KO_proteinGroups.txt`; dropping it would be a worse failure than any false
    positive, so exact equality and prefix-only anchoring are both ruled out here."""
    assert _c("HAP1_USP18KO_proteinGroups.txt").engines == ("maxquant",)
    assert _c("HAP1_USP18KO_proteinGroups.txt").engine_state == "maxquant"


def test_a_marker_run_into_a_preceding_word_no_longer_classifies() -> None:
    """The other direction of the same change: the token form is *stricter* on the left than
    `endswith`, which admitted any string ending in a marker."""
    assert "maxquant" not in _c("foobarproteingroups.txt").engines
    assert _c("foobarproteingroups.txt").engine_state == "unclassified"


def test_the_parameter_file_evidences_the_engine_without_being_a_table() -> None:
    """`mqpar.xml` is MaxQuant's parameter file and no other tool writes that name, so it settles
    C0(d) at file level. It must not touch C0(c): `.xml` is not a table extension, so it can never
    become a processed file, a site table or a site candidate."""
    got = _c("run1.raw", "mqpar.xml")
    assert got.engines == ("maxquant",)
    assert got.site_state == SITE_ABSENT
    assert got.processed_files == ()
    assert _c("mqpar_DP.xml").engines == ("maxquant",)


def test_the_documented_scan_tables_classify() -> None:
    """Added from Cox Labs' *Output Tables* because MaxQuant writes them, not because any deposit
    needed them — excluding a documented distinctive marker for having no effect would be choosing
    the matcher by its consequences."""
    assert _c("msmsScans.txt").engines == ("maxquant",)
    assert _c("msScans.txt").engines == ("maxquant",)
    assert _c("mzRange.txt").engines == ("maxquant",)
    assert _c("aifMsms.txt").engines == ("maxquant",)


def test_a_generic_peptides_table_is_still_not_a_marker() -> None:
    """`peptides.txt` is documented MaxQuant output and is refused for the reason `summary.txt` and
    `parameters.txt` are: anybody may write it. The refusal was decided from the documentation, and
    the existing `Peptides_UbPTMs.txt` case agrees with it independently."""
    assert "maxquant" not in _c("peptides.txt").engines
    assert "maxquant" not in _c("Peptides_UbPTMs.txt").engines


def test_the_four_deferred_engines_still_match_by_suffix() -> None:
    """Only MaxQuant's markers are token-matched. The other four gate nothing, and their markers
    are structurally different — two are bare extensions and one carries a leading separator.

    **`SAMPLE_report.tsv` reads as two engines and that is pre-existing, not introduced here.**
    DIA-NN's `report.tsv` and Spectronaut's `_report.tsv` both match it under `endswith`, so the
    marker table has an overlap on any `*_report.tsv`. It is pinned rather than fixed: these four
    gate nothing, and re-matching them is out of this turn's scope.
    """
    assert _c("SAMPLE_report.tsv").engines == ("diann", "spectronaut")
    assert _c("results.pdresult").engines == ("proteomediscoverer",)
    assert _c("x_report.xls").engines == ("spectronaut",)
    assert _c("a_final_report_v2.tsv").engines == ()


def test_the_new_matcher_reaches_its_verdict_without_any_request() -> None:
    """`_Forbidden` shape: the token form and `mqpar.xml` are filename rules, so a classification
    that used them must still cost nothing on the network."""
    names, notes, skipped = expand_archives(
        "PXD000000",
        ("mqpar.xml", "modificationSpecificPeptides_ntermUb.txt"),
        limit=0,
        session=_Forbidden(),
    )
    assert (notes, skipped) == ([], ())
    assert Candidate("PXD000000", "t", "PARTIAL", files=names).engines == ("maxquant",)


# ── expand_archives: every skip is accounted for ──────────────────────────────────────────────


class _Forbidden:
    """A session that fails the test if anything calls it. `RestSession`-shaped."""

    def get(self, url: str, *, timeout: int = 0) -> _Response:
        raise AssertionError(f"a request was made when none should have been: {url}")


def test_expand_archives_makes_no_request_when_no_archive_will_be_opened() -> None:
    """The property the three tests below *relied on* and did not assert, 2026-08-12.

    `file_urls(accession)` was `expand_archives`' first statement, ahead of the filtering that
    decides whether any archive is opened — so these three reached `www.ebi.ac.uk` and **failed**,
    not skipped, in a clone that cannot. They passed here only because this container can reach the
    API, which is the worst way for a guard to be green.

    Asserting *no request was made* is what stops that returning: a container with a network cannot
    tell a deferred fetch from an eager one by outcome, so the absence has to be asserted directly.
    The property is carried by `_Forbidden` raising, not by the shapes below — which is why they are
    membership checks rather than equalities, and why this file adds no new entry to
    `tests/test_tautology_sweep.py`'s pinned multiset.
    """
    names = ("a.d.zip", "b.raw.zip")
    grown, notes, skipped = expand_archives("PXD000000", names, limit=3, session=_Forbidden())
    assert not notes
    assert all(n in grown for n in names)
    assert all("instrument format" in entry for entry in skipped)

    # …and with a real archive present but the cap at zero, still nothing is fetched.
    _, _, capped = expand_archives("PXD000000", ("Search.zip",), limit=0, session=_Forbidden())
    assert any("beyond the limit of 0" in entry for entry in capped)


def test_expand_archives_threads_the_session_it_is_given() -> None:
    """The seam, asserted rather than assumed. `expand_archives` took no `session` while every
    sibling did, so its first statement called an injectable function with nothing to inject."""
    session = _Session({"/files": [{"fileName": "Search.zip"}]})  # listed, but no public location
    _, _, skipped = expand_archives("PXD000000", ("Search.zip",), limit=3, session=session)
    assert session.seen, "expand_archives did not use the session it was given"
    assert "/projects/PXD000000/files" in session.seen[0]
    assert any("no public URL" in entry for entry in skipped)


def test_archives_skipped_by_format_are_recorded_not_silent() -> None:
    """The quieter of the two skips: hint-filtered archives left no trace at all, because the
    unlisted count only ever counted archives beyond the cap."""
    _, _, skipped = expand_archives(
        "PXD000000", ("S1_1.d.zip", "S1_2.d.zip"), limit=3, session=_Forbidden()
    )
    assert len(skipped) == 2
    assert all("instrument format" in s for s in skipped)


def test_archives_beyond_the_cap_are_recorded_individually() -> None:
    names = tuple(f"Search_{i}.zip" for i in range(5))
    _, _, skipped = expand_archives("PXD000000", names, limit=0, session=_Forbidden())
    assert len(skipped) == 5
    assert all("beyond the limit of 0" in s for s in skipped)


def test_a_name_habit_no_longer_skips_an_archive() -> None:
    """`raw_` and `_raw` were guesses about naming and are gone; only container formats remain."""
    _, _, skipped = expand_archives(
        "PXD000000", ("raw_search_output.zip",), limit=0, session=_Forbidden()
    )
    assert skipped == ("raw_search_output.zip: beyond the limit of 0",)


# ── classify: one named accession, offline, and no query issued ───────────────────────────────


def test_classify_builds_a_candidate_without_issuing_a_query() -> None:
    """The property the re-run turns on: naming an accession must not widen the draw.

    `survey` takes queries and `--files` returned before classifying, so there was no way to ask
    what the instrument says about one accession without searching. `classify` closes that, and
    this asserts it reaches only the project record and the file listing — never `/search/`.
    """
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("HAP1_GlyGlyKSites.txt", "proteinGroups.txt"),
            "/projects/PXD000000": {"title": "A title", "submissionType": "PARTIAL"},
        }
    )
    got = classify("PXD000000", session=session)
    assert got.accession == "PXD000000"
    assert got.site_state == SITE_PRESENT
    assert got.engine_state == "maxquant"
    assert not any("/search/" in url for url in session.seen), session.seen


def test_classify_threads_its_session_into_the_archive_expansion() -> None:
    """`classify` calls `expand_archives`, whose seam was the last turn's repair. If it built its
    own session instead of passing this one on, the archive path would reach the network again."""
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("Search.zip"),
            "/projects/PXD000000": {"title": "t", "submissionType": "PARTIAL"},
        }
    )
    got = classify("PXD000000", session=session)
    assert any("no public URL" in entry for entry in got.skipped)
    assert not any("/search/" in url for url in session.seen)


def test_classify_makes_no_request_at_all_when_the_session_forbids_it() -> None:
    """A blunt check that nothing in `classify` constructs its own session behind the seam."""
    with pytest.raises(AssertionError, match="a request was made"):
        classify("PXD000000", session=_Forbidden())


def test_declared_software_is_read_as_a_name_not_a_dict_repr() -> None:
    """PRIDE returns CvParam objects; `str(x)` on one yields an unreadable blob. The field was
    populated for two turns and consulted by nothing, which is how that survived."""
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("run.raw"),
            "/projects/PXD000000": {
                "title": "t",
                "submissionType": "PARTIAL",
                "softwares": [{"@type": "CvParam", "accession": "MS:1001583", "name": "MaxQuant"}],
                "organisms": [{"name": "Homo sapiens"}],
            },
        }
    )
    got = classify("PXD000000", session=session)
    assert got.software == ("MaxQuant",)
    assert got.species == ("Homo sapiens",)


def test_a_plain_string_software_value_still_reads() -> None:
    """Not every field comes back as a CvParam, so the bare form must survive the repair."""
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("run.raw"),
            "/projects/PXD000000": {"title": "t", "submissionType": "P", "softwares": ["MaxQuant"]},
        }
    )
    assert classify("PXD000000", session=session).software == ("MaxQuant",)


def test_reuse_terms_are_carried_because_c0b_cannot_be_evaluated_without_them() -> None:
    """C0(b) asks whether reuse terms are establishable from the deposit's own metadata, and treats
    *not stated* as an exclusion rather than as permission. The field is on the project record; the
    first widened draw could not answer C0 because nothing read it."""
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("run.raw"),
            "/projects/PXD000000": {"title": "t", "submissionType": "P", "license": "CC0"},
        }
    )
    assert classify("PXD000000", session=session).license == "CC0"


def test_an_unstated_licence_reads_as_empty_and_not_as_permission() -> None:
    session = _Session(
        {
            "/projects/PXD000000/files": _listing("run.raw"),
            "/projects/PXD000000": {"title": "t", "submissionType": "P"},
        }
    )
    assert not classify("PXD000000", session=session).license


# ── archive_entries: the parser, against zipfile rather than against a hand-built blob ────────
#
# 14 of the widened draw's 60 rows rest on this parser, and 7 of the 12 that pass C0. It had no
# test because it could not take a session; `RangedSession` closes that. The archives below are
# built by `zipfile`, so the parse is checked against the reference implementation — a fixture
# assembled by hand would restate the parser's own arithmetic, which is the tautology shape.


def _zip_bytes(names: tuple[str, ...]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            zf.writestr(name, b"x" * 32)
    return buf.getvalue()


class _RangedSession:
    """Serves one blob, honouring `Range`. `RangedSession`-shaped.

    `honour_range=False` reproduces a server that ignores the header and answers 200 with the head
    of the file — the case that yields an empty tuple rather than an error.
    """

    def __init__(self, blob: bytes, *, honour_range: bool = True, truncate: int | None = None):
        self.blob = blob
        self.honour_range = honour_range
        self.truncate = truncate
        self.ranges: list[str] = []

    class _R:
        def __init__(self, content: bytes, headers: dict[str, str], status: int = 206) -> None:
            self.content = content
            self.headers = headers
            self.status_code = status

        def raise_for_status(self) -> object:
            return None

    def head(self, url: str, *, timeout: int = 0) -> _RangedSession._R:
        return self._R(b"", {"Content-Length": str(len(self.blob))}, 200)

    def get(
        self, url: str, *, headers: Mapping[str, str] | None = None, timeout: int = 0
    ) -> _RangedSession._R:
        spec = (headers or {}).get("Range", "")
        self.ranges.append(spec)
        if not self.honour_range:
            return self._R(self.blob[:512], {}, 200)
        body = spec[len("bytes=") :]
        start_s, _, end_s = body.partition("-")
        start = int(start_s)
        part = self.blob[start : int(end_s) + 1] if end_s else self.blob[start:]
        # Truncation applies only to a bounded read — the central-directory fetch. Applying it to
        # the open-ended tail read as well destroyed the end-of-central-directory, so the parser
        # raised for the wrong reason and the test passed on a message it was not testing for.
        if self.truncate is not None and end_s:
            part = part[: self.truncate]
        return self._R(part, {}, 206)


def test_the_parser_returns_every_entry_name_in_order() -> None:
    """The expected names are written out at the assertion rather than compared against the input
    variable. That keeps it a comparison against a literal display, which the tautology sweep
    excludes — so the parse is pinned exactly and `tests/test_tautology_sweep.py` is not edited."""
    session = _RangedSession(_zip_bytes(("a.txt", "dir/b.tsv", "dir/nested/c.parquet", "d.raw")))
    assert archive_entries("http://x/a.zip", session=session) == (
        "a.txt",
        "dir/b.tsv",
        "dir/nested/c.parquet",
        "d.raw",
    )


def test_utf8_and_long_names_survive_the_46_byte_header_arithmetic() -> None:
    """A name long enough to cross the fixed-header stride, and one needing multi-byte decoding."""
    long_name = "x" * 300 + ".txt"
    names = (
        "Ünïcödé_ø_名前.tsv",
        long_name,
        "Search_GlyGly/report.UniMod_121_sites_90.tsv",
    )
    got = archive_entries("http://x/a.zip", session=_RangedSession(_zip_bytes(names)))
    assert all(name in got for name in names)
    assert not [name for name in got if name not in names]
    assert got.index(names[0]) < got.index(long_name) < got.index(names[2])


def test_an_archive_smaller_than_the_tail_reads_from_byte_zero() -> None:
    """`max(0, size - tail)` — a small archive must not ask for a negative offset."""
    blob = _zip_bytes(("only.txt",))
    assert len(blob) < 65536
    session = _RangedSession(blob)
    assert archive_entries("http://x/a.zip", session=session) == ("only.txt",)
    assert session.ranges[0] == "bytes=0-"


def test_a_body_with_no_end_of_central_directory_raises() -> None:
    session = _RangedSession(b"not a zip at all" * 64)
    with pytest.raises(RuntimeError, match="no end-of-central-directory"):
        archive_entries("http://x/a.zip", session=session)


# ── the four silent-zero routes, each made to fail before it was closed ───────────────────────


def test_a_server_that_ignores_range_is_an_error_not_an_empty_archive() -> None:
    """Defect 2. `raise_for_status` passes on a 200, so the directory read came back as the head of
    the file, the parse loop never ran, and an empty tuple was returned — the false zero this
    function exists to fix, unguarded one function away from `self_check`."""
    session = _RangedSession(_zip_bytes(("a.txt", "b.txt")), honour_range=False)
    with pytest.raises(RuntimeError, match="ignored Range"):
        archive_entries("http://x/a.zip", session=session)


def test_a_zip64_marker_with_no_locator_raises_rather_than_unpacking_garbage() -> None:
    """Defect 1. `rfind` answers -1 when absent, and `blob[-1 + 8 : -1 + 16]` is `blob[7:15]` —
    eight arbitrary bytes unpacked into an offset the reader would then trust."""
    blob = bytearray(_zip_bytes(("a.txt",)))
    at = blob.rfind(b"PK\x05\x06")
    blob[at + 12 : at + 20] = b"\xff" * 8  # declare zip64, and there is no locator
    with pytest.raises(RuntimeError, match="no zip64 locator"):
        archive_entries("http://x/a.zip", session=_RangedSession(bytes(blob)))


def test_a_short_directory_raises_rather_than_returning_fewer_names() -> None:
    """Defect 4. A partial-content body shorter than `cd_size`. The loop's exit is structural, so
    this parsed cleanly and returned a short list that reads as a small archive."""
    session = _RangedSession(_zip_bytes(("a.txt", "b.txt", "c.txt")), truncate=40)
    with pytest.raises(RuntimeError, match="central directory and received"):
        archive_entries("http://x/a.zip", session=session)


def test_the_parsed_count_is_compared_against_the_declared_total() -> None:
    """Defect 3, and it is kept separate from defect 4 because the guards do not cover the same
    set: a directory corrupted on an entry boundary is the right length and still parses short."""
    names = ("a.txt", "b.txt", "c.txt")
    blob = bytearray(_zip_bytes(names))
    first = blob.find(b"PK\x01\x02")
    second = blob.find(b"PK\x01\x02", first + 4)
    blob[second : second + 4] = b"XXXX"  # same length, second entry unreadable
    with pytest.raises(RuntimeError, match="declares 3 entries and 1 parsed"):
        archive_entries("http://x/a.zip", session=_RangedSession(bytes(blob)))


# ── extract_member: one member's bytes, range-read and verified against its CRC ────────────────


def _payload(n: int = 40) -> bytes:
    """Compressible content, so deflate actually deflates and a stored member differs in size."""
    return b"Proteins\tIntensity\n" + b"".join(b"P%05d\t%d\n" % (i, i * 7) for i in range(n))


def _archive(entries: tuple[tuple[str, bytes, int], ...]) -> bytes:
    """`(name, content, method)` per member, built by `zipfile` so the parser is checked against a
    reference implementation rather than against arithmetic restated from the parser itself."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content, method in entries:
            zf.writestr(zipfile.ZipInfo(name), content, method)
    return buf.getvalue()


def _member(blob: bytes, name: str) -> ArchiveMember:
    session = _RangedSession(blob)
    return next(m for m in archive_members("http://x/a.zip", session=session) if m.name == name)


def _central_entries(blob: bytearray) -> list[int]:
    """Offsets of each central-directory file header within `blob`."""
    at = blob.rfind(b"PK\x05\x06")
    cd_off = struct.unpack("<I", blob[at + 16 : at + 20])[0]
    cd_size = struct.unpack("<I", blob[at + 12 : at + 16])[0]
    out, p = [], cd_off
    while p < cd_off + cd_size and blob[p : p + 4] == b"PK\x01\x02":
        nlen, elen, clen = struct.unpack("<HHH", blob[p + 28 : p + 34])
        out.append(p)
        p += 46 + nlen + elen + clen
    return out


class _ForbiddenRanged:
    """`_Forbidden`'s ranged sibling. That one is `RestSession`-shaped and declares no `headers`, so
    passing it here raised `TypeError` and would have proved nothing about reaching the network."""

    def head(self, url: str, *, timeout: int = 0) -> Any:
        raise AssertionError(f"a request was made when none should have been: {url}")

    def get(self, url: str, *, headers: Mapping[str, str] | None = None, timeout: int = 0) -> Any:
        raise AssertionError(f"a request was made when none should have been: {url}")


def test_a_deflated_member_extracts_byte_identically() -> None:
    """Checked against `zipfile`'s own read of the same archive, not against the input variable."""
    content = _payload()
    blob = _archive((("combined/txt/GlyGly (K)Sites.txt", content, zipfile.ZIP_DEFLATED),))
    member = _member(blob, "combined/txt/GlyGly (K)Sites.txt")
    assert member.method == 8
    got = extract_member("http://x/a.zip", member, session=_RangedSession(blob))
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        assert got == zf.read("combined/txt/GlyGly (K)Sites.txt")


def test_a_stored_member_extracts_without_inflating() -> None:
    """Method 0 is supported rather than refused: it is a legitimate zip method and refusing it
    would fail on a real archive for no reason."""
    content = _payload()
    blob = _archive((("stored.txt", content, zipfile.ZIP_STORED),))
    member = _member(blob, "stored.txt")
    assert member.method == 0
    assert extract_member("http://x/a.zip", member, session=_RangedSession(blob)) == content


def test_the_right_member_comes_back_from_a_multi_member_archive() -> None:
    blob = _archive(
        tuple(
            (n, b"body of " + n.encode(), zipfile.ZIP_DEFLATED)
            for n in ("a.txt", "b.txt", "GlyGly (K)Sites.txt", "d.txt")
        )
    )
    member = _member(blob, "GlyGly (K)Sites.txt")
    got = extract_member("http://x/a.zip", member, session=_RangedSession(blob))
    assert got == b"body of GlyGly (K)Sites.txt"


def test_a_member_far_larger_than_the_tail_read_extracts_whole() -> None:
    """The archives this is written for are gigabytes; the member must not be silently clipped to
    whatever window the directory read used."""
    content = _payload(20_000)
    assert len(content) > 65536
    blob = _archive((("big.txt", content, zipfile.ZIP_DEFLATED),))
    member = _member(blob, "big.txt")
    got = extract_member("http://x/a.zip", member, session=_RangedSession(blob))
    assert len(got) == len(content)
    assert got == content


def test_the_local_headers_own_extra_length_locates_the_data() -> None:
    """The measurement the retrieval decision rests on: a zip64 entry carries a 20-byte extra field
    in its **local** header that its central record does not, so a data start computed from the
    central directory lands inside the member's first bytes."""
    buf = io.BytesIO()
    with (
        zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf,
        zf.open("streamed.txt", "w", force_zip64=True) as fh,
    ):
        fh.write(_payload())
    blob = buf.getvalue()
    member = _member(blob, "streamed.txt")

    at = member.local_header_offset
    local_elen = struct.unpack("<H", blob[at + 28 : at + 30])[0]
    central_elen = struct.unpack("<H", blob[_central_entries(bytearray(blob))[0] + 30 :][:2])[0]
    assert (central_elen, local_elen) == (0, 20)

    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        expected = zf.read("streamed.txt")
    assert extract_member("http://x/a.zip", member, session=_RangedSession(blob)) == expected


def test_a_crc_mismatch_raises_rather_than_returning_the_bytes() -> None:
    """The guard the other four do not cover. Theirs detect absence or truncation; this detects a
    **wrong answer** — bytes that arrived, inflated, and are not what the archive declares."""
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    struct.pack_into("<I", blob, _central_entries(blob)[0] + 16, 0xDEADBEEF)
    member = _member(bytes(blob), "t.txt")
    with pytest.raises(RuntimeError, match="failed its CRC-32"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_an_unsupported_compression_method_is_refused_by_number() -> None:
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    struct.pack_into("<H", blob, _central_entries(blob)[0] + 10, 12)  # bzip2
    member = _member(bytes(blob), "t.txt")
    with pytest.raises(RuntimeError, match="compression method 12"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_an_encrypted_entry_is_refused() -> None:
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    entry = _central_entries(blob)[0]
    flags = struct.unpack("<H", blob[entry + 8 : entry + 10])[0]
    struct.pack_into("<H", blob, entry + 8, flags | 0x0001)
    member = _member(bytes(blob), "t.txt")
    assert member.is_encrypted
    with pytest.raises(RuntimeError, match="encrypted"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_a_data_descriptor_entry_still_extracts() -> None:
    """Bit 3 makes the **local** header's sizes and CRC placeholders. Nothing here reads those —
    they come from the central record, which is authoritative — so it is handled, not refused."""
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    entry = _central_entries(blob)[0]
    flags = struct.unpack("<H", blob[entry + 8 : entry + 10])[0]
    struct.pack_into("<H", blob, entry + 8, flags | 0x0008)
    member = _member(bytes(blob), "t.txt")
    assert member.has_data_descriptor
    with zipfile.ZipFile(io.BytesIO(bytes(blob))) as zf:
        expected = zf.read("t.txt")
    assert extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob))) == expected


def test_a_directory_entry_is_refused_because_it_has_no_data() -> None:
    blob = _archive((("combined/txt/", b"", zipfile.ZIP_STORED),))
    member = _member(blob, "combined/txt/")
    assert member.is_directory
    with pytest.raises(RuntimeError, match="directory entry"):
        extract_member("http://x/a.zip", member, session=_RangedSession(blob))


def test_a_local_header_that_is_not_where_the_directory_says_is_refused() -> None:
    """The offset is trusted from the central record; if it does not land on `PK\x03\x04` the
    bytes after it are not this member's, and inflating them would return something plausible."""
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    struct.pack_into("<I", blob, _central_entries(blob)[0] + 42, 3)
    member = _member(bytes(blob), "t.txt")
    with pytest.raises(RuntimeError, match="no local file header"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_a_local_header_naming_a_different_member_is_refused() -> None:
    """Two members of equal name length: pointing one central record at the other's local header
    would return the wrong table under the right name, which no CRC check downstream would catch
    because the CRC would also be the wrong member's."""
    blob = bytearray(
        _archive(
            (
                ("aaa.txt", b"first body", zipfile.ZIP_DEFLATED),
                ("bbb.txt", b"second body", zipfile.ZIP_DEFLATED),
            )
        )
    )
    entries = _central_entries(blob)
    other = struct.unpack("<I", blob[entries[1] + 42 : entries[1] + 46])[0]
    struct.pack_into("<I", blob, entries[0] + 42, other)
    member = _member(bytes(blob), "aaa.txt")
    with pytest.raises(RuntimeError, match="not b'aaa.txt'"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_a_name_that_is_not_utf8_is_still_identified_by_its_bytes() -> None:
    """Why the member record carries raw bytes. `\xef` alone is not valid UTF-8, so the decoded
    name comes back with a replacement character — and a caller selecting by that string could not
    match it. Selecting by the record makes the question disappear."""
    blob = _archive((("naive_x.txt", _payload(), zipfile.ZIP_DEFLATED),)).replace(
        b"naive_x.txt", b"na\xefve_x.txt"
    )
    member = _member(blob, "na\ufffdve_x.txt")
    assert member.name_bytes == b"na\xefve_x.txt"
    assert member.name != member.name_bytes.decode("latin-1")
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        expected = zf.read(zf.namelist()[0])
    assert extract_member("http://x/a.zip", member, session=_RangedSession(blob)) == expected


class _TruncateBody(_RangedSession):
    """Serves the local header whole and truncates the body read, so the two short-read guards can
    be told apart. `_RangedSession(truncate=...)` cuts every bounded read, which reaches the local
    header first and never gets to the body."""

    def get(self, url: str, *, headers: Mapping[str, str] | None = None, timeout: int = 0):  # type: ignore[no-untyped-def]
        bounded = sum(1 for r in self.ranges if not r.endswith("-"))
        out = super().get(url, headers=headers, timeout=timeout)
        if bounded >= 1:
            return self._R(out.content[:-4], {}, 206)
        return out


def test_a_short_local_header_is_refused_rather_than_unpacked() -> None:
    """Found while writing the body test: this reached `struct.unpack` and surfaced as
    `struct.error`, which `expand_archives` records as `unreadable` with no sign it was truncated."""
    blob = _archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),))
    member = _member(blob, "t.txt")
    with pytest.raises(RuntimeError, match="bytes of local header"):
        extract_member("http://x/a.zip", member, session=_RangedSession(blob, truncate=5))


def test_a_short_body_is_refused_rather_than_inflated() -> None:
    blob = _archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),))
    member = _member(blob, "t.txt")
    with pytest.raises(RuntimeError, match="bytes of 't.txt' and received"):
        extract_member("http://x/a.zip", member, session=_TruncateBody(blob))


def test_extraction_costs_two_ranged_reads() -> None:
    """One for the local header and its name, one for the body. The first is not optional: the
    data start needs the local header's own extra length."""
    blob = _archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),))
    member = _member(blob, "t.txt")
    session = _RangedSession(blob)
    extract_member("http://x/a.zip", member, session=session)
    assert len(session.ranges) == 2


def test_a_server_that_ignores_range_is_caught_during_extraction_too() -> None:
    """Guard 2 has one home in `_ranged`, so the extractor inherits it rather than re-deriving it.

    **Its bound here is the same one it has in the parser, and the second member is what shows it.**
    Guard 2 tests `start > 0`, so a member whose local header sits at offset **0** cannot trip it —
    the first read starts at zero. That case is not left uncovered: the length check catches it
    instead, which is why both are asserted rather than only the one that reads better.
    """
    blob = _archive(
        (
            ("first.txt", _payload(), zipfile.ZIP_DEFLATED),
            ("second.txt", _payload(), zipfile.ZIP_DEFLATED),
        )
    )
    at_zero = _member(blob, "first.txt")
    assert at_zero.local_header_offset == 0
    with pytest.raises(RuntimeError, match="bytes of local header"):
        extract_member("http://x/a.zip", at_zero, session=_RangedSession(blob, honour_range=False))

    beyond_zero = _member(blob, "second.txt")
    assert beyond_zero.local_header_offset > 0
    with pytest.raises(RuntimeError, match="ignored Range"):
        extract_member(
            "http://x/a.zip", beyond_zero, session=_RangedSession(blob, honour_range=False)
        )


def test_zip64_sizes_are_read_from_the_extra_field() -> None:
    """`MaxQUANT_HpH.zip` at 16,993,871,159 bytes is past the 32-bit ceiling, so a sentinel in the
    fixed record is a certainty for it rather than a contingency."""
    real = 0x1_0000_0003
    extra = struct.pack("<HHQQ", 0x0001, 16, 999, real)
    from bzk.deposit_survey import _zip64_values

    assert _zip64_values(extra, 2) == [999, real]
    assert _zip64_values(extra, 1) == [999]
    assert _zip64_values(b"", 2) == []
    assert _zip64_values(struct.pack("<HH", 0x000A, 0), 2) == []


def _zip64_csize(blob: bytes) -> bytes:
    """Rewrite the first central entry so its compressed size is a zip64 sentinel in the fixed
    record and its real value sits in the extra field — the shape a >4 GiB archive produces, built
    here because no archive small enough to test with will produce it on its own."""
    b = bytearray(blob)
    at = b.rfind(b"PK\x05\x06")
    cd_off = struct.unpack("<I", b[at + 16 : at + 20])[0]
    cd_size = struct.unpack("<I", b[at + 12 : at + 16])[0]
    d = bytearray(b[cd_off : cd_off + cd_size])
    nlen, elen, clen = struct.unpack("<HHH", d[28:34])
    real = struct.unpack("<I", d[20:24])[0]
    struct.pack_into("<I", d, 20, 0xFFFFFFFF)
    extra = struct.pack("<HHQ", 0x0001, 8, real)
    struct.pack_into("<H", d, 30, elen + len(extra))
    rebuilt = (
        bytes(d[:46])
        + bytes(d[46 : 46 + nlen])
        + bytes(d[46 + nlen : 46 + nlen + elen])
        + extra
        + bytes(d[46 + nlen + elen : 46 + nlen + elen + clen])
        + bytes(d[46 + nlen + elen + clen :])
    )
    out = bytearray(bytes(b[:cd_off]) + rebuilt + bytes(b[cd_off + cd_size :]))
    struct.pack_into("<I", out, out.rfind(b"PK\x05\x06") + 12, len(rebuilt))
    return bytes(out)


def test_a_zip64_sentinel_is_resolved_from_the_extra_field_and_extracts() -> None:
    """The unit test of `_zip64_values` did not cover the assignment back into the record: removing
    it left every test green. This builds the sentinel into a real central directory."""
    content = _payload()
    plain = _archive((("t.txt", content, zipfile.ZIP_DEFLATED),))
    with zipfile.ZipFile(io.BytesIO(plain)) as zf:
        real = zf.getinfo("t.txt").compress_size
    blob = _zip64_csize(plain)
    member = _member(blob, "t.txt")
    assert member.compressed_size == real
    assert member.compressed_size != 0xFFFFFFFF
    assert extract_member("http://x/a.zip", member, session=_RangedSession(blob)) == content


def test_a_declared_uncompressed_size_that_disagrees_with_the_bytes_is_refused() -> None:
    """Isolated from the CRC check, which otherwise subsumes it: the CRC here is left correct, so
    only the length disagrees. Removing the length check left every test green until this existed."""
    blob = bytearray(_archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),)))
    struct.pack_into("<I", blob, _central_entries(blob)[0] + 24, 999_999)
    member = _member(bytes(blob), "t.txt")
    with pytest.raises(RuntimeError, match="declares 999999 bytes and inflated to"):
        extract_member("http://x/a.zip", member, session=_RangedSession(bytes(blob)))


def test_the_member_record_carries_what_the_parser_used_to_step_past() -> None:
    """Offsets into the 46-byte central header, verified against `zipfile` rather than a summary."""
    content = _payload()
    blob = _archive((("t.txt", content, zipfile.ZIP_DEFLATED),))
    member = _member(blob, "t.txt")
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        info = zf.getinfo("t.txt")
    assert member.crc32 == info.CRC == zlib.crc32(content) & 0xFFFFFFFF
    assert member.compressed_size == info.compress_size
    assert member.uncompressed_size == info.file_size == len(content)
    assert member.local_header_offset == info.header_offset
    assert member.method == info.compress_type


def test_archive_entries_is_still_names_and_only_names() -> None:
    """The projection the survey path depends on, unchanged by the record type beneath it."""
    blob = _archive(
        tuple((n, b"x" * 16, zipfile.ZIP_DEFLATED) for n in ("a.txt", "dir/b.tsv", "c.raw"))
    )
    assert archive_entries("http://x/a.zip", session=_RangedSession(blob)) == (
        "a.txt",
        "dir/b.tsv",
        "c.raw",
    )


def test_extraction_reaches_no_network_of_its_own() -> None:
    """`_Forbidden` shape: every read goes through the injected session, so an extractor that
    reached out on its own would fail here rather than pass quietly in a container with a network."""
    blob = _archive((("t.txt", _payload(), zipfile.ZIP_DEFLATED),))
    member = _member(blob, "t.txt")
    session = _RangedSession(blob)
    extract_member("http://x/a.zip", member, session=session)
    assert session.ranges and all(r.startswith("bytes=") for r in session.ranges)
    with pytest.raises(AssertionError, match="a request was made"):
        extract_member("http://x/a.zip", member, session=_ForbiddenRanged())


def test_expand_archives_threads_the_ranged_session_it_is_given() -> None:
    """The seam, end to end: a real archive listed through an injected session and no network."""
    session = _Session(
        {
            "/files": [
                {
                    "fileName": "Search.zip",
                    "publicFileLocations": [{"value": "https://ftp.pride.ebi.ac.uk/x/Search.zip"}],
                }
            ]
        }
    )
    ranged = _RangedSession(_zip_bytes(("Output/GlyGly (K)Sites.txt", "Output/psm.tsv")))
    grown, notes, skipped = expand_archives(
        "PXD000000", ("Search.zip",), session=session, ranged=ranged
    )
    assert "Search.zip!Output/GlyGly (K)Sites.txt" in grown
    assert any("2 entries" in note for note in notes)
    assert not skipped


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
