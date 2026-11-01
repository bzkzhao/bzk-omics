"""``bzk drift`` — check the pinned sequence archive against UniProt, and leave a receipt.

**Split out of `rebuild.py` on 2026-08-07, because it was never a rebuild step.** Rebuild
reconstructs derived state from the four I9 inputs; this validates one of those inputs against the
outside world. The graph is byte-identical whether or not this runs — demonstrated rather than
argued, since two replays that skipped it reproduced the same 11,389 ids as one that did not.

They were welded because both were written in week 1 and both needed a cache path. The cost of that
became visible when Slice 4a pinned 1,028 sequences: `rebuild()` went to **1,057 s, of which 973.7 s
was this check** (measured, not estimated) — and a 17-minute command run after every schema change is a command that stops
being run. `OPERATIONS.md` §5 asks for exactly that cadence; this session changed the schema twice
and ran a full rebuild once, at the end, which is the evidence.

**Nothing here is weakened.** The check still refetches every archived sequence with
``refresh=True``, bypassing the snapshot *and* the pin, because the failure it exists to catch —
UniProt
amending a sequence without bumping its version (`ONTOLOGY.md` §11 Q5) — is invisible to any
comparison that trusts the version number. What changed is when it runs, not what it does.

**The receipt is the point of the split.** A check nobody is forced to run is a check nobody runs,
so this writes `~/.bzk-omics/cache/uniprot/.drift` recording when it last ran, over what, and with
what outcome. `rebuild.py` reads it and reports staleness; it never refuses, because a rebuild is
the disaster-recovery path (`OPERATIONS.md` §1) and putting a network check in front of recovery
would be strictly worse than a stale check. The obligation that makes staleness *consequential*
rather than merely visible sits at the export boundary and is recorded against I18 in
`HANDOFF.md` §8 — deliberately named there as unbuilt work rather than assumed.

The receipt lives beside the archive it describes, which is now correct rather than awkward:
`ONTOLOGY.md` §8 I9 names the sequence archive as a fourth input and `OPERATIONS.md` §1 gives it
the same standing as `raw/`, so a directory that holds an I9 input is the right home for the record
of when that input was last validated.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from bzk.http import RestSession
from bzk.resolve.uniprot import Resolution, resolve

DEFAULT_HOME = Path.home() / ".bzk-omics"
RECEIPT_NAME = ".drift"

#: How long a drift check stays fresh before `rebuild` starts saying so. **`OPERATIONS.md` §5 owns
#: this number** — that section owns cadence — and this is its mirror, guarded by
#: `tests/test_drift.py` exactly as `schema.py` is guarded against `ONTOLOGY.md` §4–§7. It was a
#: constant here *citing* §5 as owner, which is a comment rather than an arrangement: the value
#: lived in one place and the authority in another, so either could move without the other.
#: Nothing refuses on it; it is a reporting threshold, and the obligation that would give staleness
#: teeth is the I18 export predicate recorded in `HANDOFF.md` §8.
STALE_AFTER_DAYS = 7

#: Lookups per accession before it is reported **unchecked** rather than drifted or clean, and the
#: back-off unit between them (`RETRY_PAUSE_S * attempt` seconds). One pass over 3,579 sequences
#: produced 137 lookups that returned nothing and all 137 answered correctly when asked again one at
#: a time (2026-10-31), so a single attempt is not a measurement of the entry.
RETRIES = 3
RETRY_PAUSE_S = 2.0


def log(message: str) -> None:
    print(f"[drift] {message}")


@dataclass(frozen=True)
class Drift:
    accession: str
    cached_sv: int
    current_sv: int | None
    content_changed: bool
    stored_len: int
    current_len: int
    #: The resolver's `entry_type` for the fresh lookup. `'Inactive'` is a retirement — UniProt
    #: answered, and the entry no longer exists as a distinct one — which is a finding about the
    #: archive, not a failed fetch.
    entry_type: str = ""


@dataclass(frozen=True)
class Unchecked:
    """An accession this run could not check: UniProt did not give a usable answer.

    **Not a drift and not a clean result.** `resolve` returns no sequence and no version for a 429,
    a 5xx, a network error and a 404 alike, and for an isoform whose FASTA could not be fetched
    under a parent that answered. Reporting any of those as drift put 137 false positives in one
    pass (2026-10-31) and 18 on 2026-10-05; counting them as checked would hide the same failures
    the other way.
    """

    accession: str
    cached_sv: int
    #: The resolver's status (`http_503`, `network_error`, `not_found`, ...), or
    #: `sequence_unavailable:<source>` where the entry answered but its sequence did not.
    status: str


@dataclass(frozen=True)
class Checked:
    drifts: list[Drift]
    unchecked: list[Unchecked]


@dataclass(frozen=True)
class Receipt:
    """What a drift check leaves behind, so a later rebuild can say how stale the archive is."""

    checked_at: str  # ISO-8601, UTC
    sequences_checked: int
    #: Digest over the *set* of `accession#sv` checked. A receipt that reports 1,029 sequences means
    #: nothing if the archive has since gained 400 — this is what lets a reader tell "checked
    #: recently" from "checked recently, over a different archive".
    archive_digest: str
    drifts: int
    #: Accessions the run could not check. Defaults to 0 so a receipt written before this field
    #: existed still loads; `sequences_checked` excludes them.
    unchecked: int = 0

    def age_days(self, *, now: datetime | None = None) -> float:
        moment = now if now is not None else datetime.now(UTC)
        return (moment - datetime.fromisoformat(self.checked_at)).total_seconds() / 86400


def archive_dir(home: Path) -> Path:
    return home / "cache" / "uniprot"


def archived_sequences(home: Path) -> list[tuple[str, int]]:
    """Every `(accession, sv)` in the archive, sorted — the work list, and the digest's input."""
    seq_dir = archive_dir(home) / "seq"
    if not seq_dir.exists():
        return []
    found = []
    for path in sorted(seq_dir.glob("*#sv*.txt")):
        accession, _, sv_text = path.stem.rpartition("#sv")
        if sv_text.isdigit():
            found.append((accession, int(sv_text)))
    return found


def archive_digest(entries: list[tuple[str, int]]) -> str:
    """A digest over the set checked, so a receipt cannot be read as covering a larger archive."""
    joined = "\n".join(f"{accession}#sv{sv}" for accession, sv in sorted(entries))
    return "sha256:" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:32]


def read_receipt(home: Path) -> Receipt | None:
    """The last drift check's receipt, or `None` if none was ever written or it is unreadable.

    Unreadable is treated as absent rather than as an error: a corrupt receipt must not stop a
    rebuild, for the same reason a stale one must not.
    """
    path = archive_dir(home) / RECEIPT_NAME
    if not path.exists():
        return None
    try:
        return Receipt(**json.loads(path.read_text()))
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def write_receipt(home: Path, receipt: Receipt) -> Path:
    path = archive_dir(home) / RECEIPT_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(receipt), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def staleness_line(home: Path, *, now: datetime | None = None) -> str:
    """One line describing how stale the archive's validation is. Never raises, never refuses."""
    entries = archived_sequences(home)
    if not entries:
        return "sequence archive is empty; nothing to drift-check"
    receipt = read_receipt(home)
    if receipt is None:
        return (
            f"sequence archive holds {len(entries):,} sequence(s) and has NEVER been "
            "drift-checked — run `python -m bzk.drift`"
        )
    age = receipt.age_days(now=now)
    current = archive_digest(entries)
    if current != receipt.archive_digest:
        return (
            f"sequence archive last drift-checked {age:.0f} day(s) ago over a DIFFERENT set "
            f"({receipt.sequences_checked:,} then, {len(entries):,} now) — "
            "run `python -m bzk.drift`"
        )
    if age > STALE_AFTER_DAYS:
        return (
            f"sequence archive last drift-checked {age:.0f} day(s) ago over "
            f"{receipt.sequences_checked:,} sequence(s) — STALE (>{STALE_AFTER_DAYS}d), "
            "run `python -m bzk.drift`"
        )
    unchecked = (
        f", {receipt.unchecked} UNCHECKED (no usable answer) — run `python -m bzk.drift`"
        if receipt.unchecked
        else ""
    )
    return (
        f"sequence archive drift-checked {age:.0f} day(s) ago over "
        f"{receipt.sequences_checked:,} sequence(s), {receipt.drifts} drift(s){unchecked}"
    )


def _fresh(
    accession: str, session: RestSession | None, sleep: Callable[[float], None]
) -> Resolution:
    """One accession's current state, asked for up to `RETRIES` times.

    Retries a lookup that is not `ok` and an `ok` one that carries no sequence for an entry that is
    not retired (an isoform whose FASTA failed under a parent that answered). Returns the last
    resolution either way; the caller decides what it is.
    """
    fresh = None
    for attempt in range(1, RETRIES + 1):
        with tempfile.TemporaryDirectory() as tmp:
            fresh = resolve(accession, cache_dir=Path(tmp), refresh=True, session=session)
        retired = fresh.entry_type.lower() == "inactive"
        if fresh.status == "ok" and (fresh.sequence is not None or retired):
            return fresh
        if attempt < RETRIES:
            sleep(RETRY_PAUSE_S * attempt)
    assert fresh is not None
    return fresh


def check(
    home: Path = DEFAULT_HOME,
    *,
    session: RestSession | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Checked:
    """Compare each archived sequence against a fresh UniProt fetch (`ONTOLOGY.md` §11 Q5).

    Fetching into a throwaway cache with ``refresh=True`` bypasses every cached tier — the
    snapshot, the archived sequence and, since `OPERATIONS.md` §3.1, the pin — so an isoform
    sequence UniProt amended without bumping the parent version is caught by content, not just by a
    changed version number.

    **The pin makes this the only place drift can now be seen, which raises the stakes on the
    cadence rather than lowering them.** `resolve` on its ordinary path returns the pinned version
    for an accession the archive holds, so a rebuild no longer notices that UniProt has moved —
    which is the point, since noticing by re-keying the graph was the failure. Detection moves here
    entirely, and `OPERATIONS.md` §5's weekly cadence is what makes that a transfer rather than a
    loss.

    **A lookup that gave no usable answer is `Unchecked`, never drift and never clean.** This used
    to keep `fresh.sequence` and `fresh.sequence_version` and discard `Resolution.status`, so every
    failed fetch printed as a drift — and an isoform whose FASTA failed under an answering parent
    had no sequence to compare and an unchanged version, so it was counted clean. The first
    direction was measured twice (18 on 2026-10-05, 137 on 2026-10-31); the second was found by
    reading the code the 10-05 fix sketch left alone.
    """
    drifts: list[Drift] = []
    unchecked: list[Unchecked] = []
    for accession, cached_sv in archived_sequences(home):
        stored = (archive_dir(home) / "seq" / f"{accession}#sv{cached_sv}.txt").read_text()
        fresh = _fresh(accession, session, sleep)
        retired = fresh.entry_type.lower() == "inactive"
        if fresh.status != "ok":
            unchecked.append(Unchecked(accession, cached_sv, fresh.status))
            continue
        if fresh.sequence is None and not retired:
            unchecked.append(
                Unchecked(accession, cached_sv, f"sequence_unavailable:{fresh.sequence_source}")
            )
            continue
        current = fresh.sequence
        content_changed = current is not None and current != stored
        version_changed = fresh.sequence_version != cached_sv
        if content_changed or version_changed:
            drifts.append(
                Drift(
                    accession=accession,
                    cached_sv=cached_sv,
                    current_sv=fresh.sequence_version,
                    content_changed=content_changed,
                    stored_len=len(stored),
                    current_len=len(current or ""),
                    entry_type=fresh.entry_type,
                )
            )
    return Checked(drifts, unchecked)


def drift_check(
    home: Path = DEFAULT_HOME,
    *,
    session: RestSession | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Drift]:
    """The drifts `check` found. Accessions that could not be checked are not in this list — read
    `check` where that matters."""
    return check(home, session=session, sleep=sleep).drifts


def run(
    home: Path = DEFAULT_HOME,
    *,
    session: RestSession | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Receipt:
    """Drift-check the archive and write the receipt. The entry point."""
    entries = archived_sequences(home)
    log(f"checking {len(entries):,} archived sequence(s) against UniProt")
    report = check(home, session=session, sleep=sleep)
    for d in report.drifts:
        label = "RETIRED" if d.entry_type.lower() == "inactive" else "DRIFT"
        log(
            f"{label}: {d.accession} archived sv{d.cached_sv} ({d.stored_len} aa) vs "
            f"current sv{d.current_sv} ({d.current_len} aa); content_changed={d.content_changed}"
        )
    for u in report.unchecked:
        log(f"UNCHECKED: {u.accession} archived sv{u.cached_sv}: {u.status} after {RETRIES} tries")
    if not report.drifts:
        log("no sequence drift detected" + (" among those checked" if report.unchecked else ""))
    receipt = Receipt(
        checked_at=datetime.now(UTC).isoformat(),
        sequences_checked=len(entries) - len(report.unchecked),
        archive_digest=archive_digest(entries),
        drifts=len(report.drifts),
        unchecked=len(report.unchecked),
    )
    path = write_receipt(home, receipt)
    log(f"receipt written to {path}")
    return receipt


def main() -> None:
    run()


if __name__ == "__main__":
    main()
