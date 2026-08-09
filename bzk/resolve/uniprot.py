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

2. **A persistent cache split by whether a field bears on identity** (OPERATIONS.md §3.1). The
   *snapshot*, ``entry/{canonical}.json``, is keyed on the base accession and is overwritten by
   every re-fetch — that was true from the first commit and is now declared rather than worked
   around. The *archive* is keyed on the full accession and version — ``P09914-2#sv2.txt`` for the
   sequence, ``P09914-2#sv2.meta.json`` for the pin — and is written once and never overwritten
   (ARCHITECTURE.md §2: cached under the full form, never collapsed to canonical).

   **What changed 2026-08-09, and it is a correction to this paragraph.** It used to end *"the
   immutable key needs the sequence version, only known after the entry fetch, so the tiers cannot
   merge"*. The premise is right and the conclusion was too strong: the version need not be
   *known* if it can be *recovered*, and putting the pin in the tier the version already keys makes
   it recoverable by glob. So ``resolve`` reads ``sequence_version``, ``entry_type`` and
   ``reviewed`` from the pin and only ``gene``, ``last_seq_update`` and ``hgnc_id`` from the
   snapshot. The tiers still do not merge; the identity-bearing half simply stopped living in the
   mutable one. ``fetched_at`` records when a record was **fetched** and nothing reads it — the
   90-day clause this once claimed it served wanted an *access* clock, which is a different thing
   and is corrected in OPERATIONS.md §3.

3. **The isoform ``sequence_version`` source is made explicit.** It is taken from the parent
   entry's ``entryAudit.sequenceVersion`` (ONTOLOGY.md §4): UniProt versions the canonical entry,
   and the isoform FASTA carries no independent version. The notebook already did this implicitly.

Network access is injectable (``session``) so the logic is testable offline; drift detection
(a stored sequence that UniProt has since amended) is `rebuild.py`'s job, not this module's.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, replace
from datetime import UTC, datetime
from pathlib import Path

import requests

from bzk.http import RestSession
from bzk.ontology.keys import KeyError_, check_accession_case

UNIPROT_REST = "https://rest.uniprot.org/uniprotkb"
DEFAULT_CACHE_DIR = Path.home() / ".bzk-omics" / "cache" / "uniprot"
TIMEOUT = 30


def _now() -> str:
    """UTC timestamp recording when an entry was fetched (OPERATIONS.md §3 retention)."""
    return datetime.now(UTC).isoformat()


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


#: Sentinel for `hgnc_id` meaning *this record predates the field*, as distinct from `None`, which
#: means *captured, and UniProt reports no HGNC cross-reference* (`ONTOLOGY.md` §11 Q12). The two
#: are distinguishable on disk — a pre-widening file has no `hgnc_id` key, a post-widening one has
#: `"hgnc_id": null` — and `_load_entry` is what collapsed them, filling both from the default.
#: Measured before the field was added, which is why the default is this and not `None`.
NOT_CAPTURED = "\x00not-captured"


@dataclass(frozen=True)
class _Entry:
    """Canonical-entry metadata, as cached in the **snapshot** tier (keyed on the base accession).

    Snapshot, not archive: this file is overwritten on every re-fetch, and `OPERATIONS.md` §3.1
    declares that rather than working around it. Nothing identity-bearing is read from here —
    `sequence_version`, `entry_type` and `reviewed` come from the write-once pin beside the
    sequence, and `sequence` from the sequence file itself. The fields that remain the snapshot's
    own are the ones no id depends on.
    """

    status: str
    entry_type: str = ""
    reviewed: bool = False
    sequence: str = ""
    sequence_version: int | None = None
    last_seq_update: str | None = None
    gene: str | None = None
    fetched_at: str | None = None  # when this record was FETCHED — not when it was last read
    hgnc_id: str | None = NOT_CAPTURED  # `NOT_CAPTURED` for a file written before the field


@dataclass(frozen=True)
class _Pin:
    """The identity-bearing half, written once per `{canonical}#sv{n}` and never overwritten.

    `sequence_version` is not a field: it is the key, which is what lets it be recovered by glob
    without being known in advance. That is the circularity `resolve` used to have — the immutable
    key needed a version only the fetch could reveal — and it is broken by putting the pin in the
    tier the version already keys rather than beside the snapshot.
    """

    entry_type: str
    reviewed: bool


def _entry_path(cache_dir: Path, canonical: str) -> Path:
    return cache_dir / "entry" / f"{canonical}.json"


def _pin_path(cache_dir: Path, canonical: str, sv: int) -> Path:
    return cache_dir / "seq" / f"{canonical}#sv{sv}.meta.json"


def _pin_put(cache_dir: Path, canonical: str, sv: int | None, entry: _Entry) -> None:
    """Write the pin if it is absent. A given `{canonical}#sv{n}` is never overwritten.

    Deliberately the same shape as `_seq_cache_put`, and beside it in the same directory, because
    it is the same discipline over the same key.
    """
    if sv is None or entry.status != "ok":
        return
    path = _pin_path(cache_dir, canonical, sv)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(_Pin(entry.entry_type, entry.reviewed))))


def _pin_get(cache_dir: Path, canonical: str) -> tuple[int, _Pin] | None:
    """Recover the pinned version and its metadata, or `None` if nothing is pinned.

    The selection rule, and its behaviour at every size the archive can present it with:
    **0 matches** — nothing pinned, the caller falls through to the snapshot and the network, which
    is the pre-2026-08-09 path unchanged. **1 match** — use it. **≥2 matches** — refuse. Two
    captures mean the archive holds two versions of one accession and nothing on disk says which is
    authoritative; taking the newest would silently reinstate the overwrite this arrangement exists
    to remove, and taking the oldest would be a guess wearing a rule's clothes. The ≥2 branch is
    unreachable from the current archive (every one of its 2,845 accessions has exactly one
    version), so it is exercised synthetically in `tests/test_resolve.py` rather than by the corpus.
    """
    found = sorted((cache_dir / "seq").glob(f"{canonical}#sv*.meta.json"))
    if not found:
        return None
    if len(found) > 1:
        raise KeyError_(
            f"{canonical} has {len(found)} pinned sequence versions — "
            f"{[p.name for p in found]}. A rebuild cannot choose between them: nothing on disk "
            "names which capture the graph was built against, and picking one would be the "
            "overwrite this tier exists to prevent (OPERATIONS.md §3.1)"
        )
    path = found[0]
    sv = int(path.name.rsplit("#sv", 1)[1].split(".", 1)[0])
    return sv, _Pin(**json.loads(path.read_text()))


def _seq_path(cache_dir: Path, accession: str, sv: int) -> Path:
    # Full accession, never collapsed to canonical (ARCHITECTURE.md §2): P09914-2#sv2.txt
    return cache_dir / "seq" / f"{accession}#sv{sv}.txt"


def _fetch_entry(session: RestSession, canonical: str) -> _Entry:
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
    # `None`, never `NOT_CAPTURED`: this payload *was* read, so an absent cross-reference is a fact
    # about the entry rather than about the cache. Sampled coverage is 40/40 Swiss-Prot, 37/40
    # TrEMBL and 0 of 78 inactive (§11 Q12), and no entry in 198 carried more than one, so the
    # first match is taken rather than a list being kept.
    hgnc = next(
        (
            str(x["id"])
            for x in (d.get("uniProtKBCrossReferences") or [])
            if x.get("database") == "HGNC" and x.get("id")
        ),
        None,
    )
    return _Entry(
        status="ok",
        entry_type=entry_type,
        reviewed="reviewed" in lower and "unreviewed" not in lower,
        sequence=str(d.get("sequence", {}).get("value", "")),
        sequence_version=d.get("entryAudit", {}).get("sequenceVersion"),
        last_seq_update=d.get("entryAudit", {}).get("lastSequenceUpdateDate"),
        gene=(genes[0].get("geneName", {}) or {}).get("value"),
        fetched_at=_now(),
        hgnc_id=hgnc,
    )


def _load_entry(cache_dir: Path, canonical: str, *, refresh: bool, session: RestSession) -> _Entry:
    """The snapshot tier: return the cached record, or fetch and cache it. Errors are never cached.

    Cache loading is tolerant of format drift: unknown keys are dropped and a record that cannot be
    reconstructed (a field removed, the file corrupt) is treated as a miss and refetched, rather
    than raising ``TypeError`` on every stale file the first time ``_Entry`` changes shape.

    **A defaulted field is not enough, and the loader is where that is fixed (§11 Q12).** Adding
    ``hgnc_id: str | None = None`` would have loaded every pre-widening file clean with the field
    ``None`` and fetched nothing — measured — so 2,261 entries would sit permanently at *no HGNC
    id* when they mean *never captured*, and coverage would become a function of which accessions
    happened to be re-resolved. The distinction is present on disk (no key at all, against
    ``"hgnc_id": null``) and it was only the reconstruction above that collapsed it. So the default
    is ``NOT_CAPTURED`` and a record carrying it is treated as a miss. That makes the widening a
    correct incremental backfill instead of a silent no-op, and it is affordable only because
    ``OPERATIONS.md`` §3.1 moved every identity-bearing field out of this file first: the refetch
    it provokes rewrites nothing an id depends on.
    """
    path = _entry_path(cache_dir, canonical)
    if not refresh and path.exists():
        try:
            data = json.loads(path.read_text())
            known = {f.name for f in fields(_Entry)}
            cached = _Entry(**{k: v for k, v in data.items() if k in known})
            if cached.hgnc_id != NOT_CAPTURED:
                return cached
        except (json.JSONDecodeError, TypeError, ValueError):
            pass  # incompatible or corrupt cache → refetch below
    entry = _fetch_entry(session, canonical)
    if entry.status == "ok":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(entry)))
    return entry


def _seq_cache_get(cache_dir: Path, accession: str, sv: int | None) -> str | None:
    if sv is None:
        return None
    path = _seq_path(cache_dir, accession, sv)
    return path.read_text() if path.exists() else None


def _seq_cache_put(cache_dir: Path, accession: str, sv: int | None, sequence: str) -> None:
    """Tier 2: write a sequence immutably. A given full accession + version is never overwritten."""
    if sv is None or not sequence:
        return
    path = _seq_path(cache_dir, accession, sv)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sequence)


def _isoform_sequence(
    session: RestSession, cache_dir: Path, requested: str, sv: int | None
) -> tuple[str | None, str]:
    """Fetch the isoform sequence from the FASTA endpoint at its full accession (never stripped).

    Returns ``(None, source)`` when the isoform sequence cannot be retrieved — the guard that keeps
    the canonical sequence from silently standing in for the isoform's (change 1).
    """
    cached = _seq_cache_get(cache_dir, requested, sv)
    if cached is not None:
        return cached, "isoform"
    try:
        f = session.get(f"{UNIPROT_REST}/{requested}.fasta", timeout=TIMEOUT)
    except requests.RequestException:
        return None, "isoform_fetch_failed"
    if f.status_code == 200 and f.text.startswith(">"):
        seq = "".join(f.text.split("\n")[1:]).strip()
        if seq:
            _seq_cache_put(cache_dir, requested, sv, seq)
            return seq, "isoform"
    return None, "isoform_unavailable"


def resolve(
    accession: str,
    *,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    refresh: bool = False,
    session: RestSession | None = None,
) -> Resolution:
    """Resolve an accession to its sequence and metadata, honouring isoform suffixes.

    Isoform accessions are fetched at their full accession via the FASTA endpoint and never
    stripped to canonical (ONTOLOGY.md §4). Pass ``refresh=True`` to bypass **both** the snapshot
    and the pin (used by `bzk/drift.py`, into a throwaway directory).

    **The pin wins over the snapshot on every identity-bearing field (OPERATIONS.md §3.1).** Where
    a pin exists, ``sequence_version``, ``entry_type`` and ``reviewed`` come from it and the
    snapshot supplies only ``gene``, ``last_seq_update`` and ``hgnc_id`` — none of which any id
    depends on. That ordering is the whole of the guarantee: the snapshot may be overwritten by any
    re-fetch, and after this it cannot move a `ModificationSite` key, a `ProteinSequence` id, or —
    through I17's promotion — which protein a site is keyed against.
    """
    sess = session if session is not None else requests.Session()
    # §4's accession-casing clause, enforced here as well as in `keys.protein_key`, because both
    # cache tiers below build their paths from this string verbatim: `entry/{canonical}.json` and
    # `seq/{accession}#sv{n}.txt`. Canonical there means isoform-stripped, not case-folded, so
    # without this a casing departure forks the sequence archive and the drift receipt's digest as
    # well as the graph — and forks them differently by platform, since a case-insensitive volume
    # would hand both spellings one cache file while the graph still minted two ids. Checked before
    # `requested` is used for anything, so no path is built and no file is written on the way out.
    requested = check_accession_case(str(accession).strip())
    is_isoform = "-" in requested
    canonical = requested.split("-", 1)[0]
    isoform = requested.split("-", 1)[1] if is_isoform else None

    pinned = None if refresh else _pin_get(cache_dir, canonical)
    entry = _load_entry(cache_dir, canonical, refresh=refresh, session=sess)
    if pinned is not None and entry.status == "ok":
        # The pin overrides, rather than the snapshot being consulted only on a pin miss: a
        # snapshot is still needed for `gene` and `hgnc_id`, so both are read and the pinned
        # fields are the ones that survive the merge. `sequence` follows `sequence_version` — the
        # archived bytes at the pinned version, not whatever today's payload carries — because a
        # sequence amended at an unchanged version is exactly the drift §11 Q6 describes.
        sv_pinned, pin = pinned
        archived = _seq_cache_get(cache_dir, canonical, sv_pinned)
        entry = replace(
            entry,
            sequence_version=sv_pinned,
            entry_type=pin.entry_type,
            reviewed=pin.reviewed,
            sequence=archived if archived is not None else entry.sequence,
        )
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
    if not refresh:
        # Written after the status check and before anything is returned, so a pin exists for every
        # accession this function has ever resolved successfully — including one resolved only as
        # an isoform, whose canonical sequence would otherwise never be archived. Write-once, so
        # this is a no-op on all but the first call.
        _pin_put(cache_dir, canonical, sv, entry)
        _seq_cache_put(cache_dir, canonical, sv, entry.sequence)
    if isoform is None:
        sequence: str | None = entry.sequence or None
        source = "canonical"
        _seq_cache_put(cache_dir, canonical, sv, entry.sequence)
    else:
        sequence, source = _isoform_sequence(sess, cache_dir, requested, sv)

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
    ``wrong_residue``, ``out_of_range``, ``isoform_unavailable`` (an isoform whose own sequence
    could not be retrieved), ``no_sequence`` (a resolved canonical entry that carries no sequence),
    or the resolution's failure status. Never validates against a canonical sequence standing in
    for an isoform.
    """
    if resolution.status != "ok":
        return resolution.status
    seq = resolution.sequence
    if seq is None:
        if resolution.sequence_source in ("isoform_unavailable", "isoform_fetch_failed"):
            return "isoform_unavailable"
        return "no_sequence"  # canonical entry resolved but carries an empty sequence
    if position is None or position < 1 or position > len(seq):
        return "out_of_range"
    return "ok" if seq[position - 1] == expected else "wrong_residue"
