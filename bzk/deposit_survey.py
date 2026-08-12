"""``python -m bzk.deposit_survey`` — survey PRIDE for a candidate second deposit.

**An operational instrument, not part of the platform.** It lives beside `drift.py` and
`fetch_progress.py` for the reason those two do: it produces figures that reach documents, and a
figure whose instrument was rebuilt from memory each time is how four recorded numbers once came to
rest on a poller that had never been written. Nothing in `bzk/` imports it; it is run as
`python -m`, so no lint or type target widens.

**It reads metadata and retains nothing.** `bzk/sources/pride.py` fetches *known* files and stores
their bytes through `raw_store`; this asks the archive **which** deposits exist and what files they
carry, and writes no bytes to disk. The two are deliberately separate modules — a search path inside
`pride.py` would give a fetcher a query surface it has never had, and `ROADMAP.md`'s criteria section
turns on that module having none.

**Classification follows the established rule.** Perseus versus raw search-engine output is decided
by the type-prefix stamp (`C:`/`N:`/`T:`/`M:`) and never by the presence of a statistics column —
`ROADMAP.md` § *Deposit and supplementary survey* records a `Q-value` column producing a false
positive, because raw MaxQuant carries one too. Where a file listing settles engine and grain by
filename, this does not fetch the file at all.

The two endpoints, both measured reachable from this container on 2026-08-12::

    https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects?keyword=…
    https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{accession}/files

Usage::

    python -m bzk.deposit_survey                     # the pre-registered query set
    python -m bzk.deposit_survey --keyword ISG15     # one query
    python -m bzk.deposit_survey --files PXD018299   # one deposit's file inventory
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

import requests

from bzk.http import RestSession

API = "https://www.ebi.ac.uk/pride/ws/archive/v3"

#: The query set fixed in `ROADMAP.md` § *Pre-registration: criteria for a second deposit* before
#: the survey ran. Listed here so the run is reproducible from the module rather than from a shell
#: history, and ordered as registered — the API's own ordering is taken within each query.
QUERIES: tuple[str, ...] = ("ISG15", "ubiquitin GlyGly", "diGly", "ubiquitinome")

#: C3's cap. A survey that quietly grows past its registered size is choosing its own sample.
MAX_CANDIDATES = 12

#: Filename markers that settle the search engine without fetching the file. MaxQuant writes a
#: fixed set of table names; DIA-NN writes `report.tsv`/`report.parquet`; Spectronaut and FragPipe
#: have their own. Absence of every marker is reported as `unknown`, never guessed.
ENGINE_MARKERS: dict[str, tuple[str, ...]] = {
    "maxquant": ("proteingroups.txt", "evidence.txt", "peptides.txt", "msms.txt", "sites.txt"),
    "diann": ("report.tsv", "report.parquet", "report.pr_matrix", "report.pg_matrix"),
    "spectronaut": ("_report.xls", "spectronaut"),
    "fragpipe": ("psm.tsv", "combined_protein.tsv", "combined_peptide.tsv"),
    "proteomediscoverer": (".pdresult", ".msf"),
}

#: A site-grain MaxQuant table. `GlyGly (K)Sites.txt` is the one PXD018299 carries; the general
#: form is `<Mod> (<residue>)Sites.txt`, so the marker is the suffix rather than the modification.
SITE_TABLE_MARKER = "sites.txt"


@dataclass(frozen=True)
class Candidate:
    """One deposit as the survey sees it. Every field is read, none inferred."""

    accession: str
    title: str
    submission_type: str
    species: tuple[str, ...] = ()
    instruments: tuple[str, ...] = ()
    software: tuple[str, ...] = ()
    files: tuple[str, ...] = field(default=())

    @property
    def engines(self) -> tuple[str, ...]:
        lower = [f.lower() for f in self.files]
        hit = [
            engine
            for engine, marks in ENGINE_MARKERS.items()
            if any(m in f for f in lower for m in marks)
        ]
        return tuple(sorted(hit))

    @property
    def site_tables(self) -> tuple[str, ...]:
        return tuple(f for f in self.files if f.lower().endswith(SITE_TABLE_MARKER))

    @property
    def has_sdrf(self) -> bool:
        return any(f.lower().endswith(".sdrf.tsv") or "sdrf" in f.lower() for f in self.files)


def _get(session: RestSession, url: str) -> Any:
    response = session.get(url, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"{url} returned {response.status_code}")
    return response.json()


def search(keyword: str, *, size: int = 25, session: RestSession | None = None) -> list[Candidate]:
    """Projects matching one keyword, in the API's own order. No reordering here."""
    s = session or requests.Session()
    url = f"{API}/search/projects?keyword={urllib.parse.quote(keyword)}&pageSize={size}"
    out = []
    for row in _get(s, url) or []:
        out.append(
            Candidate(
                accession=str(row.get("accession", "")),
                title=str(row.get("title", "")),
                submission_type=str(row.get("submissionType", "")),
                species=tuple(sorted({str(x) for x in row.get("organisms", []) or []})),
                instruments=tuple(sorted({str(x) for x in row.get("instruments", []) or []})),
                software=tuple(sorted({str(x) for x in row.get("softwares", []) or []})),
            )
        )
    return out


def file_names(accession: str, *, session: RestSession | None = None) -> tuple[str, ...]:
    """Every filename in one deposit. Names only — no bytes are fetched and none are retained.

    **`files/byProject?accession=…` is not used, and the reason is worth keeping.** It answers
    `200 application/json` with an **empty body** for an accession that plainly has files, so a
    survey built on it reports every deposit as fileless and looks like a finding rather than a
    broken call. `projects/{accession}/files` is the path that answers. `self_check` below exists
    because that failure was silent: a survey whose file listing is empty everywhere is
    indistinguishable from a field of protein-only deposits.
    """
    s = session or requests.Session()
    rows = _get(s, f"{API}/projects/{accession}/files?pageSize=500") or []
    names = set()
    for row in rows:
        name = str(row.get("fileName", "") or "")
        if not name:
            for loc in row.get("publicFileLocations", []) or []:
                value = str(loc.get("value", "") or "")
                if value:
                    name = value.rsplit("/", 1)[-1]
                    break
        if name:
            names.add(name)
    return tuple(sorted(names))


def self_check(*, session: RestSession | None = None) -> None:
    """Refuse to survey if the file endpoint is answering emptily.

    PXD018299 is the deposit this repository has on disk and is known to carry a MaxQuant site
    table. If the listing for it comes back without one, the instrument is broken and every result
    below it would be a silent zero — so this raises instead of reporting a field of nothing.
    """
    names = file_names("PXD018299", session=session)
    sites = [n for n in names if n.lower().endswith(SITE_TABLE_MARKER)]
    if not names or not sites:
        raise RuntimeError(
            f"self-check failed: PXD018299 listed {len(names)} file(s) and {len(sites)} site "
            "table(s); it has both. The file endpoint is not answering — do not trust a survey run "
            "on top of this, because an empty listing reads as a finding"
        )
    print(f"[survey] self-check: PXD018299 lists {len(names)} files, {len(sites)} site table(s)")


#: Archives whose *names* say they hold raw instrument data. Listing these costs three requests
#: each and cannot change a classification, so they are skipped.
_RAW_ARCHIVE_HINTS = (".d.zip", ".raw.zip", "raw_", "_raw")


def file_urls(accession: str, *, session: RestSession | None = None) -> dict[str, str]:
    """`{filename: https URL}` for one deposit, `ftp://` rewritten as `pride.py` rewrites it."""
    s = session or requests.Session()
    out: dict[str, str] = {}
    for row in _get(s, f"{API}/projects/{accession}/files?pageSize=500") or []:
        name = str(row.get("fileName", "") or "")
        for loc in row.get("publicFileLocations", []) or []:
            value = str(loc.get("value", "") or "")
            if value.startswith("ftp://ftp.pride.ebi.ac.uk"):
                value = "https://ftp.pride.ebi.ac.uk" + value[len("ftp://ftp.pride.ebi.ac.uk") :]
            if value.startswith("https://"):
                out[name or value.rsplit("/", 1)[-1]] = value
                break
    return out


def archive_entries(url: str, *, tail: int = 65536) -> tuple[str, ...]:
    """Entry names inside a remote zip, read from its central directory. Nothing is retained.

    **Written because the filename-only survey produced a false zero.** `PXD065158` deposits its
    entire search as `Search_GlyGly.zip` — 405 MB — so a survey that reads names off the file
    listing records *no processed files, engine unknown* for a deposit carrying a complete search.
    The archive is not downloaded: PRIDE's host answers `Accept-Ranges: bytes`, so this reads the
    last 64 KiB, finds the end-of-central-directory, and range-reads the directory itself. Two
    range requests against 405 MB.
    """
    session = requests.Session()
    size = int(session.head(url, timeout=60).headers["Content-Length"])

    def chunk(start: int, end: int | None = None) -> bytes:
        rng = f"bytes={start}-" + ("" if end is None else str(end))
        response = session.get(url, headers={"Range": rng}, timeout=120)
        response.raise_for_status()
        return bytes(response.content)

    blob = chunk(max(0, size - tail))
    at = blob.rfind(b"PK\x05\x06")
    if at < 0:
        raise RuntimeError(f"{url}: no end-of-central-directory in the last {tail} bytes")
    cd_size = struct.unpack("<I", blob[at + 12 : at + 16])[0]
    cd_off = struct.unpack("<I", blob[at + 16 : at + 20])[0]
    if cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:  # zip64
        loc = blob.rfind(b"PK\x06\x07")
        head = chunk(struct.unpack("<Q", blob[loc + 8 : loc + 16])[0], None)[:56]
        cd_size = struct.unpack("<Q", head[40:48])[0]
        cd_off = struct.unpack("<Q", head[48:56])[0]
    directory = chunk(cd_off, cd_off + cd_size - 1)
    names, p = [], 0
    while p + 46 <= len(directory) and directory[p : p + 4] == b"PK\x01\x02":
        nlen, elen, clen = struct.unpack("<HHH", directory[p + 28 : p + 34])
        names.append(directory[p + 46 : p + 46 + nlen].decode("utf-8", "replace"))
        p += 46 + nlen + elen + clen
    return tuple(names)


def expand_archives(
    accession: str, names: tuple[str, ...], *, limit: int = 3
) -> tuple[tuple[str, ...], list[str]]:
    """`names` plus the entries of up to `limit` non-raw zips. Returns the notes too."""
    urls = file_urls(accession)
    notes: list[str] = []
    grown = list(names)
    archives = [
        n
        for n in names
        if n.lower().endswith(".zip") and not any(h in n.lower() for h in _RAW_ARCHIVE_HINTS)
    ]
    for name in archives[:limit]:
        url = urls.get(name)
        if not url:
            notes.append(f"{name}: no public URL")
            continue
        try:
            inner = archive_entries(url)
        except (
            OSError,
            ValueError,
            KeyError,
            RuntimeError,
            struct.error,
            requests.RequestException,
        ) as exc:
            # A survey records a failed read; it never silently skips one, because a skipped
            # archive and an archive with nothing in it produce the same empty column.
            notes.append(f"{name}: unreadable ({type(exc).__name__})")
            continue
        notes.append(f"{name}: {len(inner)} entries")
        grown.extend(f"{name}!{e}" for e in inner)
    if len(archives) > limit:
        notes.append(f"{len(archives) - limit} further archive(s) not listed")
    return tuple(grown), notes


def survey(
    queries: tuple[str, ...] = QUERIES,
    *,
    cap: int = MAX_CANDIDATES,
    session: RestSession | None = None,
) -> list[Candidate]:
    """The registered query set, deduplicated by accession, capped at `cap`.

    Order is first-seen across the query list, which is the API's own ordering within each query —
    so the sample is determined by the registered queries rather than by what looked promising.
    """
    per_query: dict[str, list[Candidate]] = {
        keyword: search(keyword, session=session) for keyword in queries
    }
    seen: dict[str, Candidate] = {}
    # Round-robin, so the cap is shared rather than consumed by whichever query the registered
    # list happens to put first. Straight iteration gave `ISG15` all twelve slots and left
    # `diGly` and `ubiquitinome` — 25 results each — entirely unsurveyed.
    for rank in range(max((len(v) for v in per_query.values()), default=0)):
        for keyword in queries:
            rows = per_query[keyword]
            if rank >= len(rows):
                continue
            candidate = rows[rank]
            if candidate.accession and candidate.accession not in seen:
                seen[candidate.accession] = candidate
            if len(seen) >= cap:
                return list(seen.values())
    return list(seen.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bzk.deposit_survey", description=__doc__)
    parser.add_argument("--keyword", help="one query instead of the registered set")
    parser.add_argument("--files", metavar="ACCESSION", help="list one deposit's files and exit")
    parser.add_argument("--cap", type=int, default=MAX_CANDIDATES)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if args.files:
        names = file_names(args.files)
        print(f"[survey] {args.files}: {len(names)} file(s)")
        for name in names:
            print(f"    {name}")
        return 0

    self_check()
    queries = (args.keyword,) if args.keyword else QUERIES
    candidates = survey(queries, cap=args.cap)
    print(f"[survey] queries={list(queries)} cap={args.cap} -> {len(candidates)} candidate(s)")
    rows = []
    for c in candidates:
        names = file_names(c.accession)
        names, notes = expand_archives(c.accession, names)
        c = Candidate(**{**c.__dict__, "files": names})
        rows.append(c)
        for note in notes:
            print(f"      · {note}")
        print(
            f"  {c.accession}  {c.submission_type:10s} files={len(c.files):4d} "
            f"engines={','.join(c.engines) or '-':14s} site_tables={len(c.site_tables)} "
            f"sdrf={'Y' if c.has_sdrf else 'N'}  {c.title[:64]}"
        )
    if args.json:
        json.dump([r.__dict__ for r in rows], sys.stdout, indent=2, default=list)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
