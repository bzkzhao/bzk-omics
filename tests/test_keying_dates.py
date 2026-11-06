"""`uniprot.keying_dates` over a synthetic cache: every branch built here, none read from `~/.bzk-omics`.

The rule from `HANDOFF.md` §8: a reporting path is tested against a synthetic twin, never against
real data being in a particular state, so a change to the user's cache cannot turn this green.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from bzk.resolve.uniprot import keying_dates

EARLY = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
LATE = datetime(2026, 9, 14, 8, 30, tzinfo=UTC)


def _pin(cache: Path, canonical: str, sv: int, when: datetime) -> None:
    path = cache / "seq" / f"{canonical}#sv{sv}.meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"entry_type": "Swiss-Prot", "reviewed": True}))
    os.utime(path, (when.timestamp(), when.timestamp()))


def _entry(cache: Path, canonical: str, fetched_at: str | None) -> None:
    path = cache / "entry" / f"{canonical}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"status": "ok"} if fetched_at is None else {"status": "ok", "fetched_at": fetched_at}
    path.write_text(json.dumps(body))


def test_the_two_clocks_are_read_separately_and_every_gap_is_counted(tmp_path: Path) -> None:
    _pin(tmp_path, "P1", 1, EARLY)
    _entry(tmp_path, "P1", "2026-10-01T00:00:00+00:00")  # refreshed after the pin: later
    _pin(tmp_path, "P2", 3, LATE)
    _entry(tmp_path, "P2", None)
    _pin(tmp_path, "P3", 1, EARLY)
    _pin(tmp_path, "P3", 2, LATE)  # two pins: counted, not raised, and not dated
    _entry(tmp_path, "P4", "2026-08-10T00:00:00+00:00")  # snapshot with no pin

    report = keying_dates(["P2", "P1", "P3", "P4", "P5", "P1"], cache_dir=tmp_path)

    assert report["accessions"] == 5  # duplicates collapse; P5 has nothing on disk
    assert report["pin_written_earliest"] == "2026-08-09T12:00:00+00:00"
    assert report["pin_written_latest"] == "2026-09-14T08:30:00+00:00"
    assert report["snapshot_fetched_earliest"] == "2026-08-10T00:00:00+00:00"
    assert report["snapshot_fetched_latest"] == "2026-10-01T00:00:00+00:00"
    assert report["unpinned"] == 2  # P4, P5
    assert report["multiply_pinned"] == 1  # P3
    assert report["no_entry"] == 2  # P3, P5
    assert report["entry_without_fetched_at"] == 1  # P2


def test_an_empty_cache_reports_no_dates_rather_than_inventing_one(tmp_path: Path) -> None:
    report = keying_dates(["P1"], cache_dir=tmp_path)
    assert report["pin_written_earliest"] is None
    assert report["snapshot_fetched_latest"] is None
    assert report["unpinned"] == 1 and report["no_entry"] == 1
