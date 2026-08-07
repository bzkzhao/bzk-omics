"""PRIDE deposit retrieval (`ARCHITECTURE.md` §3, `HANDOFF.md` §4).

**The `ftp://` → `https://` conversion is permanent behaviour, not a workaround.** PRIDE's file API
returns `ftp://` locations and `requests` speaks only HTTP, raising
`InvalidSchema: No connection adapters were found`. Converting at the point of use is the fix, and
it was one of the failure modes recorded during exploration (`HANDOFF.md` §4, §6).

Fetched bytes go straight into the content-addressed store (`bzk/provenance/raw_store.py`), so a
download and the hash a curation record cites can never disagree. The HTTP session is injectable,
as in `bzk/rebuild.py`, so callers can exercise the path offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import requests

from bzk.provenance.raw_store import StoredFile, store

FTP_HOST = "ftp://ftp.pride.ebi.ac.uk"
HTTPS_HOST = "https://ftp.pride.ebi.ac.uk"
ARCHIVE = f"{HTTPS_HOST}/pride/data/archive"


def to_https(url: str) -> str:
    """Rewrite a PRIDE `ftp://` location to its HTTPS equivalent. Idempotent."""
    return HTTPS_HOST + url[len(FTP_HOST) :] if url.startswith(FTP_HOST) else url


@dataclass(frozen=True)
class DepositFile:
    """One file in a PRIDE deposit. `year`/`month` are the archive path segments — PRIDE lays the
    archive out by publication month, so they are part of the location, not a version."""

    accession: str
    year: int
    month: int
    filename: str

    @property
    def url(self) -> str:
        return f"{ARCHIVE}/{self.year:04d}/{self.month:02d}/{self.accession}/{self.filename}"


# The GlyGly site table the notebooks and the 12-of-14 baseline are built on
# (colab_reproducefigure.ipynb cell 2; colab_identityresolution.ipynb Step 1).
PXD018299_SITES = DepositFile(
    accession="PXD018299", year=2022, month=2, filename="HAP1_USP18KO_GlyGlyKSites.txt"
)


def fetch_bytes(url: str, *, session: requests.Session | None = None, timeout: int = 600) -> bytes:
    sess = session or requests.Session()
    response = sess.get(to_https(url), timeout=timeout)
    response.raise_for_status()
    return response.content


def fetch(
    deposit: DepositFile,
    *,
    home: Path | None = None,
    session: requests.Session | None = None,
) -> StoredFile:
    """Fetch a deposit file into the content-addressed store, and report its SHA-256.

    Idempotent by way of the store: re-running when the bytes are unchanged rewrites nothing and
    returns `already_present=True`.
    """
    data = fetch_bytes(deposit.url, session=session)
    stored = store(data, deposit.filename, home=home)
    state = "already present" if stored.already_present else "stored"
    print(f"[pride] {deposit.accession}/{deposit.filename}: {len(data):,} bytes, {state}")
    print(f"[pride] content_hash {stored.content_hash}")
    print(f"[pride] {stored.path}")
    return stored


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    fetch(PXD018299_SITES)
