"""The content-addressed store and the PRIDE fetch, exercised offline.

`OPERATIONS.md` §2 makes the SHA-256 the thing a curation record cites, so the store's job is that
a record's hash and a rebuild's recomputation cannot disagree. Retrieval is injectable, as in
`rebuild.py`, so the whole path is testable without a network.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from bzk.provenance.raw_store import content_hash, sha256_hex, store, verify
from bzk.sources.pride import PXD018299_SITES, DepositFile, fetch, to_https

PAYLOAD = b"Proteins\tPosition\tAmino acid\nA0A024R4E5\t88\tK\n"

# The same deposit with its digest pin dropped. These tests feed synthetic bytes to exercise
# store mechanics, so the real deposit's expected_content_hash does not apply to them — and
# `fetch` rightly refuses bytes that do not match a pin. Dropping it explicitly keeps that
# refusal strict for the real deposit instead of loosening it to accommodate the stubs.
UNPINNED = replace(PXD018299_SITES, expected_content_hash=None)


class _StubResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


class _StubSession:
    """Records the URL it was asked for, so the ftp→https conversion is observable."""

    def __init__(self, content: bytes = PAYLOAD) -> None:
        self.content = content
        self.urls: list[str] = []

    def get(self, url: str, timeout: int = 0) -> Any:
        self.urls.append(url)
        return _StubResponse(self.content)


# ── the store ───────────────────────────────────────────────────────────────────────────────────


def test_content_hash_is_the_prefixed_form_records_cite(tmp_path: Path) -> None:
    assert content_hash(PAYLOAD) == f"sha256:{sha256_hex(PAYLOAD)}"
    assert store(PAYLOAD, "sites.txt", home=tmp_path).content_hash == content_hash(PAYLOAD)


def test_storing_is_idempotent(tmp_path: Path) -> None:
    first = store(PAYLOAD, "sites.txt", home=tmp_path)
    second = store(PAYLOAD, "sites.txt", home=tmp_path)
    assert first.already_present is False and second.already_present is True
    assert first.path == second.path and first.content_hash == second.content_hash


def test_different_bytes_get_different_addresses(tmp_path: Path) -> None:
    a = store(PAYLOAD, "sites.txt", home=tmp_path)
    b = store(PAYLOAD + b"extra\n", "sites.txt", home=tmp_path)
    assert a.content_hash != b.content_hash and a.path != b.path
    assert a.path.exists() and b.path.exists(), "a revised deposit must not overwrite the original"


def test_a_corrupted_file_at_the_right_address_is_rewritten(tmp_path: Path) -> None:
    # Trusting the path rather than the bytes would report a truncated write as a valid input.
    stored = store(PAYLOAD, "sites.txt", home=tmp_path)
    stored.path.write_bytes(b"truncated")
    again = store(PAYLOAD, "sites.txt", home=tmp_path)
    assert again.already_present is False
    assert again.path.read_bytes() == PAYLOAD


def test_verify_resolves_a_cited_hash_and_rejects_a_changed_one(tmp_path: Path) -> None:
    stored = store(PAYLOAD, "sites.txt", home=tmp_path)
    assert verify(stored.content_hash, filename="sites.txt", home=tmp_path) == stored.path
    stored.path.write_bytes(b"altered")
    with pytest.raises(ValueError, match="corrupt"):
        verify(stored.content_hash, filename="sites.txt", home=tmp_path)


def test_verify_reports_an_absent_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        verify(content_hash(PAYLOAD), filename="sites.txt", home=tmp_path)


# ── PRIDE retrieval ─────────────────────────────────────────────────────────────────────────────


def test_ftp_urls_are_rewritten_to_https_and_the_rewrite_is_idempotent() -> None:
    ftp = "ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/x.txt"
    https = "https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/x.txt"
    assert to_https(ftp) == https
    assert to_https(https) == https, "conversion must not double-apply"


def test_a_non_pride_url_is_left_alone() -> None:
    assert to_https("https://rest.uniprot.org/uniprotkb/P20591.json").endswith("P20591.json")


def test_the_deposit_url_matches_the_notebooks() -> None:
    assert PXD018299_SITES.url == (
        "https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/"
        "HAP1_USP18KO_GlyGlyKSites.txt"
    )


def test_fetch_stores_under_the_hash_of_what_it_received(tmp_path: Path) -> None:
    session = _StubSession()
    stored = fetch(UNPINNED, home=tmp_path, session=session)
    assert stored.content_hash == content_hash(PAYLOAD)
    assert stored.path.read_bytes() == PAYLOAD
    assert session.urls == [UNPINNED.url]


def test_refetching_unchanged_bytes_rewrites_nothing(tmp_path: Path) -> None:
    fetch(UNPINNED, home=tmp_path, session=_StubSession())
    assert fetch(UNPINNED, home=tmp_path, session=_StubSession()).already_present is True


def test_a_revised_deposit_is_a_new_address_not_an_overwrite(tmp_path: Path) -> None:
    original = fetch(UNPINNED, home=tmp_path, session=_StubSession())
    revised = fetch(UNPINNED, home=tmp_path, session=_StubSession(PAYLOAD + b"revised\n"))
    assert original.content_hash != revised.content_hash
    assert original.path.exists(), "OPERATIONS §2: a same-named re-download must not clobber"


def test_deposit_url_is_built_from_the_archive_layout() -> None:
    other = DepositFile(accession="PXD000001", year=2012, month=3, filename="f.txt")
    assert other.url.endswith("/2012/03/PXD000001/f.txt")


def test_bytes_that_do_not_match_the_pin_are_refused(tmp_path: Path) -> None:
    """A pinned deposit that returns different bytes is a revision or a truncated download.

    `HANDOFF.md` §3 records that this deposit is byte-stable, so a mismatch is never routine drift.
    Failing loudly here is what stops a rebuild from running against bytes the curation records
    were not written for — the silent-wrongness this project keeps designing against.
    """
    pinned = replace(PXD018299_SITES, expected_content_hash=content_hash(b"not what arrives"))
    with pytest.raises(ValueError, match="not the expected"):
        fetch(pinned, home=tmp_path, session=_StubSession())


def test_refused_bytes_are_still_stored_for_comparison(tmp_path: Path) -> None:
    """The raise happens after the write, so what actually arrived can be diffed against the pin."""
    pinned = replace(PXD018299_SITES, expected_content_hash=content_hash(b"not what arrives"))
    with pytest.raises(ValueError):
        fetch(pinned, home=tmp_path, session=_StubSession())
    assert verify(content_hash(PAYLOAD), filename=pinned.filename, home=tmp_path).exists()


def test_matching_bytes_pass_the_pin(tmp_path: Path) -> None:
    """The pin must not reject the bytes it names — otherwise the real fetch could never succeed."""
    pinned = replace(PXD018299_SITES, expected_content_hash=content_hash(PAYLOAD))
    assert fetch(pinned, home=tmp_path, session=_StubSession()).content_hash == content_hash(
        PAYLOAD
    )
