"""UniProt resolution — isoform-aware, per ONTOLOGY.md §4.

Ported from ``colab_identityresolution.ipynb`` (Steps 4-5), validated 20/20 including the two
isoform cases — ``P09914-2:376`` and ``P62195-2:47`` — that the earlier isoform-stripping
resolver failed. This is **not a verbatim port**; three deliberate changes from the notebook:

1. **The ``sequence_source`` guard is moved into the module.** In the notebook an isoform whose
   sequence could not be fetched still carried the *canonical* sequence in its ``sequence`` field,
   and Step 5 was safe only because it checked ``sequence_source`` before reading it. Here that is
   impossible to get wrong: when the requested isoform's sequence is unavailable, ``sequence`` is
   ``None``. A caller that forgets the guard and validates a position gets a crash on ``None`` —
   never a silent match against the canonical sequence, which for a K-GG site mostly returns K.

2. **A two-tier persistent cache** (OPERATIONS.md §3). Entry metadata is keyed on the base
   accession (a mutable snapshot of the current UniProt entry); sequence is keyed on
   ``accession#isoform#sv`` and is immutable — a new sequence version is a new file, never an
   overwrite. The immutable key needs the sequence version, which is only known *after* the entry
   fetch, so the two tiers cannot collapse into one.

3. **The isoform ``sequence_version`` source is made explicit.** It is taken from the parent
   entry's ``entryAudit.sequenceVersion`` (ONTOLOGY.md §4): UniProt versions the canonical entry,
   and the isoform FASTA carries no independent version. The notebook already did this implicitly.

Network access is injectable (``session``) so the logic is testable offline; drift detection
(a stored sequence that UniProt has since amended) is `rebuild.py`'s job, not this module's.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

UNIPROT_REST = "https://rest.uniprot.org/uniprotkb"
DEFAULT_CACHE_DIR = Path.home() / ".bzk-omics" / "cache" / "uniprot"
TIMEOUT = 30


@dataclass(frozen=True)
class Resolution:
    """The outcome of resolving one accession. ``sequence`` matches ``requested`` or is ``None``.

    Invariant: ``sequence`` is only ever the sequence of the *requested* accession (canonical for a
    canonical request, the isoform's for an isoform request) or ``None`` — never the canonical
    sequence standing in for an isoform whose own sequence could not be retrieved.
    """

    status: str  # 'ok' | 'not_found' | 'network_error' | 'http_<code>'
    requested: str
    canonical: str
    isoform: str | None
    is_isoform: bool
    reviewed: bool | None
    entry_type: str
    sequence: str | None
    sequence_version: int | None
    last_seq_update: str | None
    gene: str | None
    sequence_source: str  # 'canonical' | 'isoform' | 'isoform_unavailable' | 'isoform_fetch_failed'


@dataclass(frozen=True)
class _Entry:
    """Canonical-entry metadata, as cached in tier 1 (keyed on the base accession)."""

    status: str
    entry_type: str = ""
    reviewed: bool = False
    sequence: str = ""
    sequence_version: int | None = None
    last_seq_update: str | None = None
    gene: str | None = None


def _entry_path(cache_dir: Path, canonical: str) -> Path:
    return cache_dir / "entry" / f"{canonical}.json"


def _seq_path(cache_dir: Path, canonical: str, isoform_key: str, sv: int) -> Path:
    return cache_dir / "seq" / f"{canonical}#{isoform_key}#sv{sv}.txt"


def _fetch_entry(session: requests.Session, canonical: str) -> _Entry:
    """Fetch canonical-entry metadata from the JSON endpoint (mirrors notebook Step 4)."""
    try:
        r = session.get(f"{UNIPROT_REST}/{canonical}.json", timeout=TIMEOUT)
    except requests.RequestException:
        return _Entry(status="network_error")
    if r.status_code == 404:
        return _Entry(status="not_found")
    if r.status_code != 200:
        return _Entry(status=f"http_{r.status_code}")

    d = r.json()
    entry_type = str(d.get("entryType", ""))
    lower = entry_type.lower()
    genes = d.get("genes") or [{}]
    return _Entry(
        status="ok",
        entry_type=entry_type,
        reviewed="reviewed" in lower and "unreviewed" not in lower,
        sequence=str(d.get("sequence", {}).get("value", "")),
        sequence_version=d.get("entryAudit", {}).get("sequenceVersion"),
        last_seq_update=d.get("entryAudit", {}).get("lastSequenceUpdateDate"),
        gene=(genes[0].get("geneName", {}) or {}).get("value"),
    )


def _load_entry(
    cache_dir: Path, canonical: str, *, refresh: bool, session: requests.Session
) -> _Entry:
    """Tier 1: return cached entry metadata, or fetch and cache it. Errors are never cached."""
    path = _entry_path(cache_dir, canonical)
    if not refresh and path.exists():
        return _Entry(**json.loads(path.read_text()))
    entry = _fetch_entry(session, canonical)
    if entry.status == "ok":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(entry)))
    return entry


def _seq_cache_get(cache_dir: Path, canonical: str, isoform_key: str, sv: int | None) -> str | None:
    if sv is None:
        return None
    path = _seq_path(cache_dir, canonical, isoform_key, sv)
    return path.read_text() if path.exists() else None


def _seq_cache_put(
    cache_dir: Path, canonical: str, isoform_key: str, sv: int | None, sequence: str
) -> None:
    """Tier 2: write a sequence immutably. A given (accession, isoform, sv) is never overwritten."""
    if sv is None or not sequence:
        return
    path = _seq_path(cache_dir, canonical, isoform_key, sv)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sequence)


def _isoform_sequence(
    session: requests.Session,
    cache_dir: Path,
    requested: str,
    canonical: str,
    isoform: str,
    sv: int | None,
) -> tuple[str | None, str]:
    """Fetch the isoform sequence from the FASTA endpoint at its full accession (never stripped).

    Returns ``(None, source)`` when the isoform sequence cannot be retrieved — the guard that keeps
    the canonical sequence from silently standing in for the isoform's (change 1).
    """
    cached = _seq_cache_get(cache_dir, canonical, isoform, sv)
    if cached is not None:
        return cached, "isoform"
    try:
        f = session.get(f"{UNIPROT_REST}/{requested}.fasta", timeout=TIMEOUT)
    except requests.RequestException:
        return None, "isoform_fetch_failed"
    if f.status_code == 200 and f.text.startswith(">"):
        seq = "".join(f.text.split("\n")[1:]).strip()
        if seq:
            _seq_cache_put(cache_dir, canonical, isoform, sv, seq)
            return seq, "isoform"
    return None, "isoform_unavailable"


def resolve(
    accession: str,
    *,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    refresh: bool = False,
    session: requests.Session | None = None,
) -> Resolution:
    """Resolve an accession to its sequence and metadata, honouring isoform suffixes.

    Isoform accessions are fetched at their full accession via the FASTA endpoint and never
    stripped to canonical (ONTOLOGY.md §4). Pass ``refresh=True`` to bypass the tier-1 metadata
    cache (used by `rebuild.py` for drift detection).
    """
    sess = session if session is not None else requests.Session()
    requested = str(accession).strip()
    is_isoform = "-" in requested
    canonical = requested.split("-", 1)[0]
    isoform = requested.split("-", 1)[1] if is_isoform else None

    entry = _load_entry(cache_dir, canonical, refresh=refresh, session=sess)
    if entry.status != "ok":
        return Resolution(
            status=entry.status,
            requested=requested,
            canonical=canonical,
            isoform=isoform,
            is_isoform=is_isoform,
            reviewed=None,
            entry_type="",
            sequence=None,
            sequence_version=None,
            last_seq_update=None,
            gene=None,
            sequence_source="none",
        )

    sv = entry.sequence_version
    if isoform is None:
        sequence: str | None = entry.sequence or None
        source = "canonical"
        _seq_cache_put(cache_dir, canonical, "canonical", sv, entry.sequence)
    else:
        sequence, source = _isoform_sequence(sess, cache_dir, requested, canonical, isoform, sv)

    return Resolution(
        status="ok",
        requested=requested,
        canonical=canonical,
        isoform=isoform,
        is_isoform=is_isoform,
        reviewed=entry.reviewed,
        entry_type=entry.entry_type,
        sequence=sequence,
        sequence_version=sv,
        last_seq_update=entry.last_seq_update,
        gene=entry.gene,
        sequence_source=source,
    )


def validate_position(resolution: Resolution, position: int | None, *, expected: str = "K") -> str:
    """Check that ``position`` (1-based) holds ``expected`` in the resolved sequence.

    ``expected`` defaults to K for the diGly K-ε-GG remnant. Returns one of: ``ok``,
    ``wrong_residue``, ``out_of_range``, ``isoform_unavailable``, or the resolution's failure
    status. Never validates against a canonical sequence standing in for an isoform — an
    unavailable isoform sequence yields ``isoform_unavailable``, not a spurious match.
    """
    if resolution.status != "ok":
        return resolution.status
    seq = resolution.sequence
    if seq is None:
        return "isoform_unavailable"
    if position is None or position < 1 or position > len(seq):
        return "out_of_range"
    return "ok" if seq[position - 1] == expected else "wrong_residue"
