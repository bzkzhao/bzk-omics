"""Content-addressed storage for ingested source files (`ARCHITECTURE.md` §2, `OPERATIONS.md` §2).

I9 requires the graph to be regenerable from `raw/` plus the curation export, and `OPERATIONS.md`
§2 requires each curation record to cite its input by SHA-256 rather than by filename: *"two
deposits, or a re-download after a deposit is revised, can share a name and differ in content."*
This module is the one place that hash is computed, so the value a record cites and the value a
rebuild recomputes come from the same code.

Storage is `raw/{hex}/{filename}`. The directory is the address; the filename is kept because the
curation records cite it and because a bare digest on disk is unreadable. Writing is **idempotent**:
a file already present whose own bytes hash to the same digest is left untouched, so re-running a
fetch is free and cannot corrupt a stored input.

No network here — retrieval lives in `bzk/sources/`, so the store is testable offline.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOME = Path.home() / ".bzk-omics"  # mirrors bzk/rebuild.py
RAW_DIRNAME = "raw"
_CHUNK = 1 << 20


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def content_hash(data: bytes) -> str:
    """The prefixed form the curation records and `Dataset.content_hash` carry (ONTOLOGY.md §9)."""
    return f"sha256:{sha256_hex(data)}"


@dataclass(frozen=True)
class StoredFile:
    content_hash: str  # 'sha256:<hex>' — the value a curation record cites
    path: Path
    size_bytes: int
    already_present: bool  # True when an identical file was already stored (idempotent re-run)

    @property
    def hex_digest(self) -> str:
        return self.content_hash.split(":", 1)[1]


def raw_root(home: Path | None = None) -> Path:
    return (home or DEFAULT_HOME) / RAW_DIRNAME


def store(data: bytes, filename: str, *, home: Path | None = None) -> StoredFile:
    """Write `data` under its own digest, or confirm it is already there.

    Verifies an existing file's bytes rather than trusting its path: a truncated or corrupted write
    that merely *sits* at the right address would otherwise be reported as a valid stored input,
    which is precisely the silent-wrongness this project keeps designing against.
    """
    digest = sha256_hex(data)
    target = raw_root(home) / digest / filename
    if target.exists() and sha256_file(target) == digest:
        return StoredFile(f"sha256:{digest}", target, target.stat().st_size, already_present=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return StoredFile(f"sha256:{digest}", target, len(data), already_present=False)


def verify(stored_hash: str, *, filename: str, home: Path | None = None) -> Path:
    """Resolve a cited hash back to its file, checking the bytes. Raises if absent or altered."""
    hex_digest = stored_hash.split(":", 1)[-1]
    path = raw_root(home) / hex_digest / filename
    if not path.exists():
        raise FileNotFoundError(f"{stored_hash} is not in {raw_root(home)} — re-fetch the input")
    actual = sha256_file(path)
    if actual != hex_digest:
        raise ValueError(
            f"{path} hashes to sha256:{actual}, not {stored_hash}; the store is corrupt"
        )
    return path
