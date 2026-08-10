"""`python -m bzk.fetch_progress` — the poller four recorded figures rest on.

**Why this is a module and not a shell script written from memory each time.** Four figures in the
document set are measurements taken with a poller — `ROADMAP.md`'s 12× correction (*~1.0 s per
accession*, 15-second spacing), the second rehearsal's 706-second window (*1.14 s per accession and
0.50 s per round trip*), the third rehearsal's *~129 round trips per minute* at 60-second spacing,
and `OPERATIONS.md` §5's decomposition, which quotes the second. Until 2026-08-10 no such instrument
existed in the repository: each run rebuilt one from memory, and *what it counted* had to be
recovered from prose. A figure whose instrument is not on disk is a figure nobody can re-derive.

**It lives in `bzk/` beside `drift.py`, which is the exact precedent** — an operational instrument
that the platform does not import, run as `python -m bzk.drift`. That placement is what keeps this
out of `ruff`'s and `mypy`'s target question entirely: `bzk` is already a target of both, so nothing
here widens one and no new root-level directory falsifies `ARCHITECTURE.md` §3's module tree.

**What it counts, and it is the same quantity all three recorded pollers counted.** Files appearing
in the two UniProt cache tiers: `cache/uniprot/entry/*.json` (one per accession) and
`cache/uniprot/seq/*.txt` (one per accession#sv). **Both units are reported on every line**, because
the records use both and their conversion is what makes them commensurable — a cold PXD018299
rebuild fetches 2,260 entries and 3,013 sequences, so a round trip is **0.4287** of an accession and
*1.0 s per accession* and *0.43 s per round trip* are the same measurement. Nothing in the documents
states that factor beside the two figures, which is how *1.0 s per accession* can be read against
*0.40 s per fetch* as a 2.5× disagreement that does not exist.

**The spacing is recorded on every sample, not stated once in prose.** `ROADMAP.md` § *Weeks 7–8*
makes that a standing requirement, and the 12× error is what it is a requirement against: three spot
counts with no clock produced a rate that was wrong by an order of magnitude, and the instrument was
the problem rather than the network. So each line carries the interval it was taken at and the
elapsed time, and the rate columns are computed from the previous sample rather than from the start.

**It terminates itself, and that is the point of `--watch-pid`.** Both cold rehearsals ended with
`pkill -f "…/poll.sh"` killing the shell that issued it, exiting 144 while the rebuild exited 0 —
recorded twice as *a property of the harness rather than of the tree*. **`pkill -f` matches the full
command line of every process, and the killer's own command line contains the pattern**, so it
matches itself. A narrower pattern is the same bug waiting for a different path: any pattern
sufficient to find the poller is a pattern present in the argv of the process searching for it. The
fix is therefore not a better pattern but no pattern — this exits when the process it watches exits,
and `--max-seconds` bounds it so an orphan cannot outlive the session either way.

Usage during a cold rebuild::

    .venv/bin/python -m bzk.rebuild & REBUILD=$!
    .venv/bin/python -m bzk.fetch_progress --watch-pid $REBUILD --interval 60
    wait $REBUILD

**Deliberately not generalised.** It measures fetch progress into one cache during a cold rebuild.
A watcher over arbitrary directories would need a name for what it counts, and the whole value here
is that the quantity is fixed and matches the figures already on record.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

#: A cold PXD018299 rebuild fetches this many of each — `OPERATIONS.md` §5, the same integers across
#: all three cold runs. Carried here only to convert between the two units the records use; nothing
#: asserts them, because a different deposit has a different ratio and this is a reporting aid.
PXD018299_ENTRIES = 2260
PXD018299_SEQUENCES = 3013


@dataclass(frozen=True)
class Sample:
    """One reading, carrying the spacing it was taken at rather than leaving it to prose."""

    elapsed_s: float
    interval_s: float
    entries: int
    sequences: int

    @property
    def round_trips(self) -> int:
        return self.entries + self.sequences


def cache_counts(home: Path) -> tuple[int, int]:
    """`(entries, sequences)` currently on disk in the two UniProt cache tiers."""
    cache = home / "cache" / "uniprot"
    entries = sum(1 for _ in (cache / "entry").glob("*.json")) if (cache / "entry").is_dir() else 0
    sequences = sum(1 for _ in (cache / "seq").glob("*.txt")) if (cache / "seq").is_dir() else 0
    return entries, sequences


def is_running(pid: int) -> bool:
    """Whether a pid is still live.

    `os.kill(pid, 0)` sends no signal and raises `ProcessLookupError` when the process is gone —
    the check without a pattern, which is the whole reason this module does not use `pkill -f`.
    `PermissionError` means it exists and belongs to another user, which is still *running*.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def format_sample(sample: Sample, previous: Sample | None) -> str:
    """One line: the counts, the spacing, and the rate **since the previous sample**.

    Since the previous sample rather than since the start, because a rate averaged from t=0 hides
    exactly what the second rehearsal found — that the within-run rate is not flat, and that the
    whole-run figure is the one to quote. Both units appear because both are on record.
    """
    head = (
        f"[{sample.elapsed_s:7.1f}s +{sample.interval_s:.0f}s] "
        f"entry={sample.entries:5d} seq={sample.sequences:5d} trips={sample.round_trips:5d}"
    )
    if previous is None:
        return head + "  (first sample — no rate yet)"
    span = sample.elapsed_s - previous.elapsed_s
    trips = sample.round_trips - previous.round_trips
    accessions = sample.entries - previous.entries
    if span <= 0 or trips <= 0:
        return head + "  no progress in this window"
    per_trip = span / trips
    # Reported as `—` rather than as a division by zero: a window in which sequences arrived and no
    # entry did is real (the two tiers are not fetched in lockstep), and printing an infinity there
    # would be a number where there is none.
    per_accession = f"{span / accessions:.2f}s/accession" if accessions > 0 else "—/accession"
    return f"{head}  {per_trip:.2f}s/trip  {per_accession}"


def poll(
    home: Path,
    *,
    interval_s: float,
    watch_pid: int | None,
    max_seconds: float,
    out: TextIO | None = None,
) -> list[Sample]:
    """Sample until the watched process exits or `max_seconds` elapses. Returns every sample."""
    stream = sys.stdout if out is None else out
    started = time.monotonic()
    samples: list[Sample] = []
    previous: Sample | None = None
    while True:
        entries, sequences = cache_counts(home)
        sample = Sample(
            elapsed_s=time.monotonic() - started,
            interval_s=interval_s,
            entries=entries,
            sequences=sequences,
        )
        print(format_sample(sample, previous), file=stream, flush=True)
        samples.append(sample)
        previous = sample
        if watch_pid is not None and not is_running(watch_pid):
            print(f"[watched pid {watch_pid} exited — stopping]", file=stream, flush=True)
            return samples
        if sample.elapsed_s >= max_seconds:
            print(f"[max-seconds {max_seconds:.0f} reached — stopping]", file=stream, flush=True)
            return samples
        time.sleep(interval_s)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m bzk.fetch_progress",
        description="Poll UniProt cache growth during a cold rebuild, recording the spacing.",
    )
    parser.add_argument("--interval", type=float, default=60.0, help="seconds between samples")
    parser.add_argument(
        "--watch-pid",
        type=int,
        default=None,
        help="stop when this process exits — no pattern, so nothing can match the poller itself",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=3600.0,
        help="hard stop, so an orphan cannot outlive the session",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home() / ".bzk-omics",
        help="the tree whose cache is watched",
    )
    args = parser.parse_args(argv)
    ratio = PXD018299_SEQUENCES / PXD018299_ENTRIES + 1
    print(
        f"polling {args.home} every {args.interval:.0f}s — "
        f"1 accession = {ratio:.4f} round trips on PXD018299",
        flush=True,
    )
    poll(
        args.home,
        interval_s=args.interval,
        watch_pid=args.watch_pid,
        max_seconds=args.max_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
