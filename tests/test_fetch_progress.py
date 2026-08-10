"""`bzk/fetch_progress.py` — the poller, and the two properties four recorded figures need from it.

**What is guarded and why each is here rather than left to a reading.** *It stops on its own*, which
is the failure that reached the record twice — `pkill -f` matching the shell that issued it, exit
144 against a rebuild's exit 0. And *the spacing is on every sample*, which is what `ROADMAP.md`
§ *Weeks 7–8* requires and what the 12× rate error came from lacking.

**No test starts a real subprocess to be watched.** `os.kill(pid, 0)` is the whole mechanism, and a
pid that never existed is a sharper input than a spawned one: `is_running` must say *gone* without
consulting a name or a pattern, which is the property that makes the `pkill` class unreachable here.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

from bzk import fetch_progress as fp


def _cache(tmp_path: Path, entries: int, sequences: int) -> Path:
    home = tmp_path / ".bzk-omics"
    (home / "cache" / "uniprot" / "entry").mkdir(parents=True)
    (home / "cache" / "uniprot" / "seq").mkdir(parents=True)
    for i in range(entries):
        (home / "cache" / "uniprot" / "entry" / f"P{i:05d}.json").write_text("{}")
    for i in range(sequences):
        (home / "cache" / "uniprot" / "seq" / f"P{i:05d}#sv1.txt").write_text("M")
    return home


# ── What it counts: the two tiers, separately ───────────────────────────────────────────────────


def test_it_counts_the_two_cache_tiers_apart(tmp_path: Path) -> None:
    """Both units are on record — *per accession* and *per round trip* — so the two tiers cannot be
    summed at the point of reading. `OPERATIONS.md` §5 quotes one and `ROADMAP.md` the other."""
    assert fp.cache_counts(_cache(tmp_path, entries=7, sequences=11)) == (7, 11)


def test_an_absent_cache_counts_zero_rather_than_raising(tmp_path: Path) -> None:
    """The poller is started **beside** a cold rebuild, so it reads the directories before the
    rebuild has created them. Raising there would kill the instrument at t=0, which is the one
    moment a cold run's rate cannot be recovered from anywhere else."""
    assert fp.cache_counts(tmp_path / "nothing-here") == (0, 0)


def test_the_pinned_ratio_is_the_one_that_makes_the_two_units_agree() -> None:
    """`1.0 s per accession` and `0.43 s per round trip` are the same measurement, and nothing in
    the document set states the factor beside them. 2,260 entries and 3,013 sequences give 2.3332
    round trips per accession, and 1.0 / 2.3332 = 0.4286 — which is the whole-run figure
    `OPERATIONS.md` §5 records as 0.40–0.44 s per fetch."""
    trips_per_accession = (fp.PXD018299_ENTRIES + fp.PXD018299_SEQUENCES) / fp.PXD018299_ENTRIES
    assert round(trips_per_accession, 4) == 2.3332
    assert 0.40 <= 1.0 / trips_per_accession <= 0.44


# ── That it stops: the failure that reached the record twice ────────────────────────────────────


def test_a_dead_pid_is_reported_gone_without_any_pattern(tmp_path: Path) -> None:
    """`pkill -f` matched the shell that issued it because that shell's own command line contained
    the pattern. This asks the kernel about one pid instead, so there is no pattern to match."""
    assert fp.is_running(os.getpid()) is True
    # A pid that has never run in this namespace. `os.kill(pid, 0)` raises `ProcessLookupError`,
    # which is the branch under test; a spawned-and-reaped pid could be recycled and would make
    # this flaky rather than sharper.
    assert fp.is_running(2**22 - 1) is False


def test_it_stops_when_the_watched_process_is_gone(tmp_path: Path) -> None:
    """*Leave nothing running when the watched command exits.* Watched against a dead pid, so the
    stop is taken on the first sample and the test cannot hang waiting for a real process.

    `max_seconds` is 5 rather than 30 so that a **broken** pid-stop fails in five seconds instead of
    thirty: with the stop removed the backstop still returns, and what fails is the sample count.
    Measured under that mutation — 1 failure, this test — so the count is what discriminates and the
    bound only decides how long the wrong answer takes to arrive.
    """
    out = io.StringIO()
    samples = fp.poll(
        _cache(tmp_path, entries=1, sequences=1),
        interval_s=0.01,
        watch_pid=2**22 - 1,
        max_seconds=5.0,
        out=out,
    )
    assert len(samples) == 1
    assert "exited — stopping" in out.getvalue()


def test_it_stops_at_max_seconds_even_with_nothing_to_watch(tmp_path: Path) -> None:
    """The backstop. An orphan poller outliving the session is the same litter `pkill` was reached
    for, so the bound holds when `--watch-pid` is not given at all.

    **Its failure mode is a hang, not a red line, and that is recorded rather than left to surprise
    someone.** Removing the `max_seconds` branch leaves an unwatched poller with no termination
    condition at all, so this call never returns and the suite stops instead of failing — measured,
    at 45 seconds under the mutation harness. A hung suite is a worse signal than a failing one and
    it is still a signal; what would make it a silent pass is nothing here, which is why no
    in-process watchdog is added to soften it.
    """
    out = io.StringIO()
    samples = fp.poll(
        _cache(tmp_path, entries=1, sequences=1),
        interval_s=0.01,
        watch_pid=None,
        max_seconds=0.0,
        out=out,
    )
    assert len(samples) == 1
    assert "max-seconds" in out.getvalue()


# ── That the spacing travels with the sample ────────────────────────────────────────────────────


def test_every_sample_line_carries_its_spacing() -> None:
    """`ROADMAP.md` § *Weeks 7–8* makes recorded spacing a requirement, and a rate whose clock lives
    in prose beside it is the 12× error's exact shape. The interval is in the line, not the caption.
    """
    first = fp.Sample(elapsed_s=0.0, interval_s=15.0, entries=10, sequences=20)
    assert "+15s" in fp.format_sample(first, None)
    later = fp.Sample(elapsed_s=15.0, interval_s=15.0, entries=20, sequences=45)
    assert "+15s" in fp.format_sample(later, first)


def test_the_first_sample_reports_no_rate(tmp_path: Path) -> None:
    """A rate needs two readings. Printing one from a single sample — dividing by elapsed-from-zero
    — is what makes a start-up transient look like a steady state."""
    line = fp.format_sample(fp.Sample(elapsed_s=0.0, interval_s=60.0, entries=5, sequences=6), None)
    assert "no rate yet" in line
    assert "s/trip" not in line


def test_the_rate_is_taken_from_the_previous_sample_not_from_the_start() -> None:
    """The second rehearsal's finding was that the within-run rate is **not flat**. A rate averaged
    from t=0 cannot show that, so a window-local rate is the measurement and the whole-run figure is
    what the documents quote. Here the window is 10 s for 10 trips — 1.0 s/trip — while the average
    since t=0 would be 100/110, i.e. 0.91, and reporting that would smooth the very change the
    instrument exists to see."""
    previous = fp.Sample(elapsed_s=90.0, interval_s=10.0, entries=50, sequences=50)
    current = fp.Sample(elapsed_s=100.0, interval_s=10.0, entries=55, sequences=55)
    assert "1.00s/trip" in fp.format_sample(current, previous)


def test_both_units_appear_because_both_are_on_record() -> None:
    """One poller reported per accession, two reported per round trip, and the documents place the
    two side by side without the conversion. Emitting both makes a reader's comparison exact."""
    previous = fp.Sample(elapsed_s=0.0, interval_s=15.0, entries=0, sequences=0)
    current = fp.Sample(elapsed_s=15.0, interval_s=15.0, entries=10, sequences=20)
    line = fp.format_sample(current, previous)
    assert "s/trip" in line
    assert "s/accession" in line


def test_a_window_with_no_new_entry_says_so_rather_than_dividing_by_zero() -> None:
    """The two tiers are not fetched in lockstep, so a window in which only sequences arrive is a
    real state. A per-accession figure there would be an infinity presented as a rate."""
    previous = fp.Sample(elapsed_s=0.0, interval_s=15.0, entries=10, sequences=0)
    current = fp.Sample(elapsed_s=15.0, interval_s=15.0, entries=10, sequences=30)
    line = fp.format_sample(current, previous)
    assert "—/accession" in line
    assert "s/trip" in line
