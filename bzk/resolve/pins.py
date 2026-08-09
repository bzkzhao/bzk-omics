"""Backfill the identity pins from snapshots written before the pin existed.

`OPERATIONS.md` §3.1 moved `sequence_version`, `entry_type` and `reviewed` out of the mutable
`entry/{canonical}.json` snapshot and into a write-once pin at `seq/{canonical}#sv{n}.meta.json`.
Every cache written before that date has the fields only in the snapshot, and `resolve` writes a
pin for the accessions it resolves — so on such a cache the pin would be minted from **whatever the
snapshot holds at that moment**, which after a re-fetch is today's UniProt rather than the capture
the graph was built against.

That is why this is a module and not a scratch script. **The window in which the backfill is
correct is the window in which the snapshots are still the original capture**, and that window
closes the first time anything re-fetches. On this repository's cache it was still open on
2026-08-09 — every one of the 2,261 snapshots carried its ingestion `fetched_at` and no code path
had rewritten one — so the pins minted then record the state the 11,730 committed ids were derived
from. A cache that has already been re-fetched cannot recover that, and this module cannot pretend
otherwise: it pins what is on disk and reports how many, and `--dry-run` exists so the count can be
read before anything is written.

**It never reaches the network.** A backfill that could fetch would be able to fill a gap with
today's answer, which is the failure it exists to prevent.

    python -m bzk.resolve.pins [--dry-run]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bzk.resolve.uniprot import DEFAULT_CACHE_DIR, _Pin, _pin_path


@dataclass(frozen=True)
class BackfillReport:
    """What a backfill did, in the four categories a snapshot can fall into."""

    written: int
    already_pinned: int
    #: Snapshots with no `sequence_version` — nothing to key a pin on. These are the `Inactive`
    #: entries: they mint no `ProteinSequence` and key no site, so they bear on no id.
    no_version: int
    unreadable: int

    @property
    def considered(self) -> int:
        return self.written + self.already_pinned + self.no_version + self.unreadable


def backfill(cache_dir: Path = DEFAULT_CACHE_DIR, *, dry_run: bool = False) -> BackfillReport:
    """Write a pin for every snapshot that carries a `sequence_version` and has none.

    Write-once is honoured through `uniprot._pin_path` plus an existence check rather than by
    trusting the caller: re-running this is a no-op, and an existing pin is never overwritten even
    if the snapshot beside it now disagrees. A snapshot that disagrees with its pin is the signal
    that the snapshot has been re-fetched, and the pin is the half that is supposed to win.
    """
    written = already = no_version = unreadable = 0
    entry_dir = cache_dir / "entry"
    if not entry_dir.exists():
        return BackfillReport(0, 0, 0, 0)

    for path in sorted(entry_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, ValueError):
            unreadable += 1
            continue
        sv = data.get("sequence_version")
        if not isinstance(sv, int):
            no_version += 1
            continue
        pin = _pin_path(cache_dir, path.stem, sv)
        if pin.exists():
            already += 1
            continue
        written += 1
        if not dry_run:
            # Built through `_Pin` rather than as a dict literal, so the two writers of this file
            # cannot drift apart: adding a field to the pin fails here at construction instead of
            # producing backfilled pins that are a field short of the ones `resolve` writes. The
            # two values are extracted by name first, so nothing from the snapshot's wider shape
            # reaches the record.
            record = _Pin(
                entry_type=str(data.get("entry_type", "")),
                reviewed=bool(data.get("reviewed", False)),
            )
            pin.parent.mkdir(parents=True, exist_ok=True)
            pin.write_text(json.dumps(asdict(record)))
    return BackfillReport(written, already, no_version, unreadable)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()
    report = backfill(dry_run=args.dry_run)
    verb = "would write" if args.dry_run else "wrote"
    print(
        f"[pins] {verb} {report.written} pin(s); {report.already_pinned} already pinned, "
        f"{report.no_version} snapshot(s) with no sequence_version, "
        f"{report.unreadable} unreadable, {report.considered} considered"
    )


if __name__ == "__main__":
    main()
