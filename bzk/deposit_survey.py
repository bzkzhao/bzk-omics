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
import zlib
from dataclasses import dataclass, field
from typing import Any

import requests

from bzk.http import RangedSession, RestSession
from bzk.sources.pride import PXD018299_SITES

API = "https://www.ebi.ac.uk/pride/ws/archive/v3"

#: The query set fixed in `ROADMAP.md` § *Pre-registration: criteria for a second deposit* before
#: the survey ran. Listed here so the run is reproducible from the module rather than from a shell
#: history, and ordered as registered — the API's own ordering is taken within each query.
QUERIES: tuple[str, ...] = (
    "ISG15",
    "ISGylome",
    "diGly",
    "GlyGly",
    "K-GG",
    "diglycine",
    "ubiquitinome",
    "ubiquitylome",
    "ubiquitin remnant",
    "ubiquitination site",
    "ubiquitylation site",
    "UbiSite",
    "ubiquitin GlyGly",
)

#: C3's cap. A survey that quietly grows past its registered size is choosing its own sample.
MAX_CANDIDATES = 60

#: Filename markers that settle the search engine without fetching the file, matched against the
#: **basename** rather than as a substring anywhere in the path. MaxQuant's are matched by
#: `_marker_matches` below; the other four keep plain `endswith` — see `_TOKEN_MATCHED_ENGINES`.
#:
#: **Two constants were doing damage here and both are fixed.** `sites.txt` was a MaxQuant marker
#: *and* C0(c)'s marker, so one constant answered two questions and a non-MaxQuant site table
#: marked the whole deposit MaxQuant; it is gone from this table. And the match was `m in f`, a
#: substring anywhere — under which `summary.txt` classified `PXD075792`'s `UbPTMs_PTMs_Summary.txt`
#: as MaxQuant, which `tests/test_deposit_survey.py` caught on its first run. A submitter may
#: *prefix* MaxQuant's names — PXD018299 deposits `HAP1_USP18KO_proteinGroups.txt` — so exact
#: equality is too strict and substring is too loose; a suffix of the basename is the rule that
#: admits the prefix without admitting the coincidence.
#:
#: **`endswith` was defeated from the other side, 2026-08-12.** A submitter may also *append* a
#: token before the extension: `PXD027328` deposits `modificationSpecificPeptides_ntermUb.txt`, which
#: is MaxQuant's own table name and does not end with it, so the deposit read `unclassified` on a
#: table it plainly wrote. MaxQuant's markers now anchor to either end of the basename's stem — see
#: `_marker_matches`. The names below are MaxQuant's documented `combined/txt` output (Cox Labs,
#: *Output Tables*) plus its parameter file, and are settled in `ROADMAP.md` § *The MaxQuant matcher*.
#:
#: `summary.txt` and `parameters.txt` are dropped outright: they are MaxQuant filenames and they
#: are also names anybody might use, so even as suffixes they carry no evidence. **`peptides.txt` is
#: refused for the same reason** although MaxQuant writes it — and independently, admitting it would
#: classify `PXD075792`'s `Peptides_UbPTMs.txt` as MaxQuant.
#:
#: **`mqpar.xml` is here and is not a result table.** It is MaxQuant's parameter file (Cox Labs,
#: *Download & Installation*: created in the GUI or by `MaxQuantCmd --create`, consumed by
#: `MaxQuantCmd`) and no other tool writes that name, so it settles C0(d) at **file level** — which
#: is what the project-level `softwares` field could not do. It cannot touch C0(c): `.xml` is not in
#: `_TABLE_EXTENSIONS`, so it is never a processed file, a site table or a site candidate.
ENGINE_MARKERS: dict[str, tuple[str, ...]] = {
    "maxquant": (
        "proteingroups.txt",
        "evidence.txt",
        "modificationspecificpeptides.txt",
        "msms.txt",
        "allpeptides.txt",
        "msmsscans.txt",
        "msscans.txt",
        "mzrange.txt",
        "aifmsms.txt",
        "mqpar.xml",
    ),
    "diann": ("report.tsv", "report.parquet", "report.pr_matrix.tsv", "report.pg_matrix.tsv"),
    "spectronaut": ("_report.xls", "_report.tsv"),
    "fragpipe": ("psm.tsv", "combined_protein.tsv", "combined_peptide.tsv", "peptide.tsv"),
    "proteomediscoverer": (".pdresult", ".msf"),
}

#: Engines whose markers anchor to a stem boundary rather than matching by plain `endswith`. Only
#: MaxQuant's do, and the reason is scope rather than taste: **C0(d) is the MaxQuant gate**, and the
#: other four are v0.2 deferrals that gate nothing, so re-matching them would move recorded
#: `engine_state` cells with no criterion consequence. They are also structurally unsuited to it —
#: `.pdresult` and `.msf` are bare extensions with no stem, and `_report.xls` carries a leading
#: separator written for `endswith`. Their standing exposure is recorded rather than fixed: under
#: `endswith`, `report.tsv` matches any `*_report.tsv` and `peptide.tsv` any `*peptide.tsv`, and
#: DIA-NN's and Spectronaut's markers overlap on every `*_report.tsv`.
_TOKEN_MATCHED_ENGINES: frozenset[str] = frozenset({"maxquant"})


def _marker_matches(base: str, marker: str, *, token: bool) -> bool:
    """Does `base` carry `marker`? `token=False` is plain `endswith`, unchanged.

    **`token=True` anchors the marker's stem to one end of the basename's stem**, requiring the
    extensions to be equal and the inner side to be a non-alphanumeric. That admits both shapes a
    submitter actually produces — a prefix (`HAP1_USP18KO_proteinGroups.txt`) and an appended token
    (`modificationSpecificPeptides_ntermUb.txt`) — while staying **stricter than `endswith` on the
    left**, which admitted any string ending in a marker.

    **It is anchored rather than merely token-delimited, and an existing test is why.** The first
    form allowed the marker's stem anywhere between two separators, which classifies
    `prefix_proteinGroups.txt_suffix.txt` — the exact shape
    `test_an_engine_marker_in_the_middle_of_a_name_does_not_classify` was written to forbid. Rather
    than weaken that guard to fit a new rule, the rule was tightened to fit the guard, so the marker
    must begin or end the stem and not merely sit inside it.
    """
    if not token:
        return base.endswith(marker)
    bstem, _, bext = base.rpartition(".")
    mstem, _, mext = marker.rpartition(".")
    if not bstem or not mstem or bext != mext:
        return base.endswith(marker)
    if bstem == mstem:
        return True
    if bstem.endswith(mstem) and not bstem[-len(mstem) - 1].isalnum():
        return True
    return bstem.startswith(mstem) and not bstem[len(mstem)].isalnum()


#: A **MaxQuant** site table, by its own naming convention: `<Mod> (<residue>)Sites.txt`, of which
#: PXD018299's `HAP1_USP18KO_GlyGlyKSites.txt` is one. A name matching this is reported `present`.
SITE_TABLE_MARKER = "sites.txt"

#: Names that *suggest* site grain without following MaxQuant's convention. A match here is
#: reported `candidate` and **never** `present`, because the name is evidence and not proof —
#: `PXD076163`'s `abundance_single-site_MS2quant_Norm.tsv` is site grain and is not MaxQuant's, and
#: `PXD075792`'s `UbPTMs_PTMs_Summary.txt` says PTM and settles no grain at all. Widening
#: `SITE_TABLE_MARKER` to cover these would have converted C0(c) from under-inclusive to
#: over-inclusive, which is the same defect facing the other way.
SITE_TABLE_HINTS: tuple[str, ...] = ("site", "ptm", "modification", "modsite", "phospho", "glygly")

#: Extensions a table can arrive as. A hint inside a `.raw` filename is not a candidate table.
_TABLE_EXTENSIONS: tuple[str, ...] = (".txt", ".tsv", ".csv", ".xlsx", ".xls", ".parquet", ".mztab")

#: Files that are instrument output or spectra, never a processed table.
_SPECTRA_EXTENSIONS: tuple[str, ...] = (
    ".raw",
    ".mzml",
    ".mzxml",
    ".wiff",
    ".wiff.scan",
    ".baf",
    ".fid",
    ".d.zip",
    ".d",
    ".mgf",
)

#: The three states C0(c) can be in. Modelled on this repository's `Absence` vocabulary rather than
#: on a boolean, because *we looked and there is none* and *we cannot tell from a name* are
#: different findings and only the second is an instrument gap.
SITE_PRESENT = "present"
SITE_CANDIDATE = "candidate"
SITE_ABSENT = "absent"


#: Compression wrappers stripped before a marker is matched. Without this the suffix rule misses a
#: gzipped `evidence.txt.gz`, which is a real MaxQuant table under a real deposit habit — the rule
#: would have traded one under-report for another.
_COMPRESSION_SUFFIXES: tuple[str, ...] = (".gz", ".bz2", ".xz", ".zst")


def _basename(path: str) -> str:
    """The filename, lowercased, with any archive prefix and one compression suffix removed."""
    base = path.rsplit("/", 1)[-1].rsplit("!", 1)[-1].lower()
    for suffix in _COMPRESSION_SUFFIXES:
        if base.endswith(suffix):
            return base[: -len(suffix)]
    return base


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

    #: PRIDE's declared reuse terms. **C0(b) cannot be evaluated without it**, and the first
    #: widened draw could not answer *does this pass C0 entirely* for that reason — the field is on
    #: the project record and was simply not read. Empty means *not stated by the deposit*, which
    #: C0(b) treats as an exclusion rather than as permission.
    license: str = ""

    #: Archives skipped and why, filled in by `expand_archives`. A survey that cannot say what it
    #: did not look at is reporting a smaller field than it searched.
    skipped: tuple[str, ...] = field(default=())

    @property
    def engines(self) -> tuple[str, ...]:
        bases = [_basename(f) for f in self.files]
        hit = [
            engine
            for engine, marks in ENGINE_MARKERS.items()
            if any(
                _marker_matches(b, m, token=engine in _TOKEN_MATCHED_ENGINES)
                for b in bases
                for m in marks
            )
        ]
        return tuple(sorted(hit))

    @property
    def processed_files(self) -> tuple[str, ...]:
        """Files that are tables rather than spectra, whether or not an engine marker matched."""
        out = []
        for name in self.files:
            low = _basename(name)
            if low.endswith(_SPECTRA_EXTENSIONS) or not low.endswith(_TABLE_EXTENSIONS):
                continue
            out.append(name)
        return tuple(out)

    @property
    def engine_state(self) -> str:
        """`<engines>`, `unclassified`, or `no_processed_output` — three states, not two.

        The survey's first run reported *none identifiable* for five of twelve candidates, which
        collapsed two different findings: `PXD078284` deposits no processed output at all, while
        `PXD075792` deposits `Peptides_UbPTMs.txt` and `UbPTMs_PTMs_Summary.txt` that this
        instrument does not recognise. The first is a fact about the deposit; the second is a gap
        in `ENGINE_MARKERS`, and a column that renders them identically hides the gap.
        """
        if self.engines:
            return ",".join(self.engines)
        return "unclassified" if self.processed_files else "no_processed_output"

    @property
    def site_tables(self) -> tuple[str, ...]:
        """Files matching MaxQuant's own site-table convention."""
        return tuple(f for f in self.files if _basename(f).endswith(SITE_TABLE_MARKER))

    @property
    def site_candidates(self) -> tuple[str, ...]:
        """Tables whose name suggests site grain without following that convention."""
        out = []
        for name in self.processed_files:
            low = _basename(name)
            if low.endswith(SITE_TABLE_MARKER):
                continue
            if any(h in low for h in SITE_TABLE_HINTS):
                out.append(name)
        return tuple(out)

    @property
    def site_state(self) -> str:
        if self.site_tables:
            return SITE_PRESENT
        return SITE_CANDIDATE if self.site_candidates else SITE_ABSENT

    @property
    def has_sdrf(self) -> bool:
        return any(f.lower().endswith(".sdrf.tsv") or "sdrf" in f.lower() for f in self.files)


def _cv_names(values: Any) -> tuple[str, ...]:
    """The `name` of each CvParam, or the bare string where a plain one is given.

    PRIDE returns `softwares`, `organisms` and `instruments` as CvParam objects. `str(x)` on one
    yields `"{'@type': 'CvParam', 'cvLabel': 'MS', 'accession': 'MS:1001583', 'name': 'MaxQuant'}"`
    — carried, stored, and unreadable, which is how a field can be populated for two turns and
    consulted by nothing. This is a parsing repair, not a widening: the same values, legible.
    """
    out = []
    for value in values or []:
        if isinstance(value, dict):
            name = str(value.get("name", "") or "")
        else:
            name = str(value)
        if name:
            out.append(name)
    return tuple(sorted(set(out)))


def _get(session: RestSession, url: str) -> Any:
    response = session.get(url, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"{url} returned {response.status_code}")
    return response.json()


def search(keyword: str, *, size: int = 100, session: RestSession | None = None) -> list[Candidate]:
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
                species=_cv_names(row.get("organisms")),
                instruments=_cv_names(row.get("instruments")),
                software=_cv_names(row.get("softwares")),
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

    **The canary names one exact file and does not use `SITE_TABLE_MARKER`, deliberately.** It did,
    and that made it worthless the moment site-table detection widened: a guard filtered by the
    same constant the widening loosens passes on a broader test than the one that made this deposit
    a valid check — it would go green because *something* matched, which is what a canary is for
    ruling out. So it asserts the presence of `PXD018299_SITES.filename`, read from
    `bzk/sources/pride.py`, whose digest that module also owns. No widening of `SITE_TABLE_MARKER`,
    `SITE_TABLE_HINTS` or `ENGINE_MARKERS` can loosen it.

    What it is guarding against is specific: `files/byProject` answers `200 application/json` with
    an **empty body**, so a broken call and a fileless deposit are indistinguishable, and a survey
    on top of one reports a field of nothing that reads as a finding.
    """
    expected = PXD018299_SITES.filename
    names = file_names(PXD018299_SITES.accession, session=session)
    if expected not in names:
        raise RuntimeError(
            f"self-check failed: {PXD018299_SITES.accession} listed {len(names)} file(s) and "
            f"{expected!r} was not among them. That file is on disk in this repository, so the "
            "endpoint is not answering — do not trust a survey run on top of this, because an "
            "empty listing reads as a finding rather than as a broken call"
        )
    print(
        f"[survey] self-check: {PXD018299_SITES.accession} lists {len(names)} files, "
        f"including {expected}"
    )


#: Archives that are instrument output *by format*, not by naming habit. Listing one costs three
#: requests and cannot change a classification, because a `.d` is a Bruker acquisition directory
#: and a `.raw` is a Thermo file — that is a fact about the container, not a guess about the name.
#:
#: **`raw_` and `_raw` were here and are removed.** They were guesses about naming, and
#: `PXD065158`'s `Search_GlyGly.zip` is the standing proof that an archive's name can say nothing
#: about what is inside it — a 405 MB processed search under a name with no marker at all. A
#: substring rule would have skipped `raw_search_output.zip` on the same evidence, silently.
_RAW_ARCHIVE_HINTS = (".d.zip", ".raw.zip")


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


@dataclass(frozen=True)
class ArchiveMember:
    """One entry of a remote zip's central directory, as the parser reads it.

    **The raw name bytes are carried beside the decoded name, and that is what makes extraction
    safe.** `name` is decoded `"utf-8", "replace"`, so a member whose name is not valid UTF-8 — the
    format permits it, since bit 11 of `flags` clear means the bytes are in the writer's own code
    page — comes back with replacement characters. An extractor that selected members *by that
    string* could fail to match, or match the wrong entry where two raw names mangle alike. Selecting
    by this record instead makes the question disappear: `extract_member` never parses a name.

    Field offsets are into the 46-byte central-directory file header and were verified against
    archives built by `zipfile` rather than taken from a summary.
    """

    #: bytes 46.. — decoded for display and for `archive_entries`' contract.
    name: str
    #: bytes 46.. — the bytes themselves, which are what identifies the member.
    name_bytes: bytes
    #: bytes 10–12. `0` stored, `8` deflate; anything else is refused at extraction.
    method: int
    #: bytes 8–10. Bit 0 encrypted, bit 3 data descriptor, bit 11 UTF-8 name.
    flags: int
    #: bytes 16–20, checked against the inflated bytes.
    crc32: int
    #: bytes 20–24, or the zip64 extra field where that reads `0xFFFFFFFF`.
    compressed_size: int
    #: bytes 24–28, likewise.
    uncompressed_size: int
    #: bytes 42–46, likewise. Where the member's local header starts.
    local_header_offset: int

    @property
    def is_encrypted(self) -> bool:
        return bool(self.flags & 0x0001)

    @property
    def has_data_descriptor(self) -> bool:
        """Bit 3: the **local** header's sizes and CRC are placeholders.

        Handled rather than refused, because nothing here reads those fields — sizes and CRC come
        from the central record, which is authoritative under bit 3. Only the local header's name
        and extra *lengths* are read, and bit 3 does not touch them.
        """
        return bool(self.flags & 0x0008)

    @property
    def is_directory(self) -> bool:
        return self.name_bytes.endswith(b"/")


#: The zip64 extended-information extra field. Where a 32-bit field in the fixed record reads this
#: sentinel, the real value is in the extra field — and `MaxQUANT_HpH.zip` at 16,993,871,159 bytes
#: is past the 32-bit ceiling, so this is a certainty for that archive rather than a contingency.
_ZIP64_SENTINEL = 0xFFFFFFFF
_ZIP64_EXTRA_ID = 0x0001


def _zip64_values(extra: bytes, wanted: int) -> list[int]:
    """The first `wanted` 64-bit values of the zip64 extra field, if it is present.

    The field lists **only** the members that were sentinels, in a fixed order — uncompressed size,
    compressed size, local-header offset — so the caller counts its own sentinels and takes that
    many. Returns `[]` when the field is absent, which is the correct answer for an entry that had
    no sentinel to resolve.
    """
    p = 0
    while p + 4 <= len(extra):
        header_id, data_size = struct.unpack("<HH", extra[p : p + 4])
        body = extra[p + 4 : p + 4 + data_size]
        if header_id == _ZIP64_EXTRA_ID:
            have = len(body) // 8
            return [
                int(struct.unpack("<Q", body[i * 8 : i * 8 + 8])[0])
                for i in range(min(have, wanted))
            ]
        p += 4 + data_size
    return []


def _ranged(http: RangedSession, url: str, start: int, end: int | None = None) -> bytes:
    """One ranged read, with the ignored-`Range` guard that both readers depend on.

    **Guard 2 lives here and nowhere else.** `raise_for_status` passes on a 200, and a 200 to a
    ranged request means the server sent the whole file from byte zero. Nothing downstream can tell
    that from a correctly served range, so it is caught at the read rather than surfacing as no
    entries — or, for `extract_member`, as the head of the archive inflating to nothing.
    """
    rng = f"bytes={start}-" + ("" if end is None else str(end))
    response = http.get(url, headers={"Range": rng}, timeout=120)
    response.raise_for_status()
    if start > 0 and response.status_code == 200:
        raise RuntimeError(
            f"{url}: ranged request answered 200, not 206 — the server ignored Range, so the "
            "bytes are the head of the file and not the part asked for"
        )
    return bytes(response.content)


def extract_member(
    url: str, member: ArchiveMember, *, session: RangedSession | None = None
) -> bytes:
    """One member's bytes, range-read out of a remote zip and verified against its CRC.

    **Two ranged reads, and the first is not optional.** The central directory gives the local
    header's offset but *not* where the member's data begins: the local header carries its **own**
    name and extra lengths, and they need not match the central record's. Measured on an archive
    built here — a zip64 entry gave a central extra length of `0` against a local `20`, so computing
    the data start from the central directory alone lands twenty bytes short, inside the member's
    first bytes. So the local header is read, its lengths are used, and only then is the body asked
    for.

    **The CRC check is the point of the function, not a courtesy.** The four guards on
    `archive_members` all detect *absence or truncation* — a short directory, an ignored range, a
    parse that stopped early. This one detects a **wrong answer**: bytes that arrived, inflated, and
    are not what the archive says they should be. An extractor returning plausible bytes it cannot
    vouch for is the silent-zero failure wearing different clothes.

    **What is refused, and what is handled.** Encrypted entries and any compression method other
    than stored or deflate are refused by name; a directory entry is refused because it has no data.
    A data descriptor (`flags` bit 3) is **handled**: it makes the *local* header's sizes and CRC
    placeholders, and nothing here reads those — they come from the central record. Zip64 sizes are
    resolved during the directory parse, before this function sees them.

    **Nothing is retained.** The bytes are returned to the caller; this writes no file.
    """
    if member.is_encrypted:
        raise RuntimeError(f"{url}: {member.name!r} is encrypted (flag bit 0); refusing to guess")
    if member.is_directory:
        raise RuntimeError(f"{url}: {member.name!r} is a directory entry and carries no data")
    if member.method not in (0, 8):
        raise RuntimeError(
            f"{url}: {member.name!r} uses compression method {member.method}, which is neither "
            "stored (0) nor deflate (8); refusing rather than returning bytes it cannot decode"
        )
    http = session or requests.Session()

    at = member.local_header_offset
    nlen = len(member.name_bytes)
    head = _ranged(http, url, at, at + 30 + nlen - 1)
    # Found by a test rather than by design: a short local header reached `struct.unpack` and came
    # back as `struct.error`, which `expand_archives` catches and records as `unreadable` with no
    # indication the read was truncated. Length first, so truncation is not reported as a bad offset.
    if len(head) != 30 + nlen:
        raise RuntimeError(
            f"{url}: asked for {30 + nlen} bytes of local header for {member.name!r} and received "
            f"{len(head)}; a truncated header gives a data start that is not this member's"
        )
    if head[:4] != b"PK\x03\x04":
        raise RuntimeError(
            f"{url}: no local file header at offset {at} for {member.name!r}; the central directory "
            "points somewhere that is not a member, so the bytes after it are not this member's"
        )
    local_nlen, local_elen = struct.unpack("<HH", head[26:30])
    if local_nlen != nlen or head[30 : 30 + nlen] != member.name_bytes:
        raise RuntimeError(
            f"{url}: the local header at offset {at} names "
            f"{head[30 : 30 + local_nlen]!r}, not {member.name_bytes!r}; extracting it would return "
            "a different member's bytes under this member's name"
        )
    start = at + 30 + local_nlen + local_elen
    body = _ranged(http, url, start, start + member.compressed_size - 1)
    if len(body) != member.compressed_size:
        raise RuntimeError(
            f"{url}: asked for {member.compressed_size} bytes of {member.name!r} and received "
            f"{len(body)}; a truncated body inflates to a shorter table that reads as a small one"
        )

    raw = body if member.method == 0 else zlib.decompress(body, -15)
    if len(raw) != member.uncompressed_size:
        raise RuntimeError(
            f"{url}: {member.name!r} declares {member.uncompressed_size} bytes and inflated to "
            f"{len(raw)}"
        )
    if zlib.crc32(raw) & 0xFFFFFFFF != member.crc32:
        raise RuntimeError(
            f"{url}: {member.name!r} failed its CRC-32 — the archive declares "
            f"{member.crc32:#010x} and the bytes give {zlib.crc32(raw) & 0xFFFFFFFF:#010x}. "
            "These bytes are wrong, not merely short"
        )
    return raw


def archive_entries(
    url: str, *, tail: int = 65536, session: RangedSession | None = None
) -> tuple[str, ...]:
    """Entry names inside a remote zip. A thin projection of `archive_members`, which does the work.

    Kept as its own function because the survey path wants names and nothing else — `expand_archives`
    grows `f"{name}!{entry}"` strings and counts them — and because every caller and test written
    against it stays correct. **There is still one parse**: a second implementation of the
    central-directory walk would carry a second copy of the four guards, and two copies drift.
    """
    return tuple(m.name for m in archive_members(url, tail=tail, session=session))


def archive_members(
    url: str, *, tail: int = 65536, session: RangedSession | None = None
) -> tuple[ArchiveMember, ...]:
    """Every entry of a remote zip's central directory, with the fields extraction needs.

    **Written because the filename-only survey produced a false zero.** `PXD065158` deposits its
    entire search as `Search_GlyGly.zip` — 405 MB — so a survey that reads names off the file
    listing records *no processed files, engine unknown* for a deposit carrying a complete search.
    The archive is not downloaded: PRIDE's host answers `Accept-Ranges: bytes`, so this reads the
    last 64 KiB, finds the end-of-central-directory, and range-reads the directory itself. Two
    range requests against 405 MB.

    **The seam was recorded as unclosed three times before it was closed, 2026-08-12.** It needs
    `head(...)` and a `headers=` keyword, which neither `BytesSession` nor `RestSession` declares;
    `RangedSession` was added beside them rather than either being widened, for the reason
    `bzk/http.py` gives. It matters more than a footnote: 14 of the widened draw's 60 rows, and 7 of
    the 12 that pass C0, rest on this parser.

    **Four silent-zero routes are guarded, each because the loop below exits *structurally* and a
    truncated directory therefore returns fewer names with no signal.** A server that ignores
    `Range` answers 200 with the file's head, so `directory` starts `PK\x03\x04`, the loop never
    runs, and an empty tuple comes back — the exact false zero this function was written to fix,
    one function away from the `self_check` that exists to prevent it.
    """
    http = session or requests.Session()
    size = int(http.head(url, timeout=60).headers["Content-Length"])

    def chunk(start: int, end: int | None = None) -> bytes:
        # Guard 2 lives in `_ranged`, so both this parser and `extract_member` inherit it.
        return _ranged(http, url, start, end)

    blob = chunk(max(0, size - tail))
    at = blob.rfind(b"PK\x05\x06")
    if at < 0:
        raise RuntimeError(f"{url}: no end-of-central-directory in the last {tail} bytes")
    declared = struct.unpack("<H", blob[at + 10 : at + 12])[0]
    cd_size = struct.unpack("<I", blob[at + 12 : at + 16])[0]
    cd_off = struct.unpack("<I", blob[at + 16 : at + 20])[0]
    if cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:  # zip64
        loc = blob.rfind(b"PK\x06\x07")
        # Guard 1: `rfind` answers -1 when absent, and `blob[-1 + 8 : -1 + 16]` is `blob[7:15]` —
        # eight arbitrary bytes unpacked into an offset the reader would then trust.
        if loc < 0:
            raise RuntimeError(
                f"{url}: the end-of-central-directory declares zip64 but no zip64 locator is in "
                f"the last {tail} bytes"
            )
        head = chunk(struct.unpack("<Q", blob[loc + 8 : loc + 16])[0], None)[:56]
        declared = struct.unpack("<Q", head[32:40])[0]
        cd_size = struct.unpack("<Q", head[40:48])[0]
        cd_off = struct.unpack("<Q", head[48:56])[0]
    directory = chunk(cd_off, cd_off + cd_size - 1)
    # Guard 4: a short partial-content body truncates the directory by a route the count check
    # below does not always see — a body cut on an entry boundary parses cleanly and short.
    if len(directory) != cd_size:
        raise RuntimeError(
            f"{url}: asked for {cd_size} bytes of central directory and received "
            f"{len(directory)}; a truncated directory parses cleanly and returns fewer names"
        )
    members: list[ArchiveMember] = []
    p = 0
    while p + 46 <= len(directory) and directory[p : p + 4] == b"PK\x01\x02":
        nlen, elen, clen = struct.unpack("<HHH", directory[p + 28 : p + 34])
        name_bytes = directory[p + 46 : p + 46 + nlen]
        extra = directory[p + 46 + nlen : p + 46 + nlen + elen]
        usize = int(struct.unpack("<I", directory[p + 24 : p + 28])[0])
        csize = int(struct.unpack("<I", directory[p + 20 : p + 24])[0])
        offset = int(struct.unpack("<I", directory[p + 42 : p + 46])[0])
        # The zip64 extra lists only the fields that were sentinels, in this order, so the count of
        # sentinels is what decides how many values to take.
        sentinels = [v == _ZIP64_SENTINEL for v in (usize, csize, offset)]
        if any(sentinels):
            wide = _zip64_values(extra, sum(sentinels))
            values = [usize, csize, offset]
            for i, is_sentinel in enumerate(sentinels):
                if is_sentinel and wide:
                    values[i] = wide.pop(0)
            usize, csize, offset = values
        members.append(
            ArchiveMember(
                name=name_bytes.decode("utf-8", "replace"),
                name_bytes=name_bytes,
                method=int(struct.unpack("<H", directory[p + 10 : p + 12])[0]),
                flags=int(struct.unpack("<H", directory[p + 8 : p + 10])[0]),
                crc32=int(struct.unpack("<I", directory[p + 16 : p + 20])[0]),
                compressed_size=csize,
                uncompressed_size=usize,
                local_header_offset=offset,
            )
        )
        p += 46 + nlen + elen + clen
    # Guard 3: the loop's exit is structural, so anything that stops it early — a corrupt header, a
    # directory cut mid-entry — returns a short list that reads as a small archive.
    if len(members) != declared:
        raise RuntimeError(
            f"{url}: the end-of-central-directory declares {declared} entries and {len(members)} "
            "parsed; a short parse reads as a small archive rather than as a failure"
        )
    return tuple(members)


def expand_archives(
    accession: str,
    names: tuple[str, ...],
    *,
    limit: int = 3,
    session: RestSession | None = None,
    ranged: RangedSession | None = None,
) -> tuple[tuple[str, ...], list[str], tuple[str, ...]]:
    """`names` plus the entries of up to `limit` inspectable zips.

    Returns `(names, notes, skipped)`. **`skipped` is the third return value because the second
    was not enough.** The first version noted archives dropped by the *cap* and said nothing at all
    about archives dropped by `_RAW_ARCHIVE_HINTS`, which are filtered out before the cap is
    applied — so a hint-skipped archive left no trace anywhere, and the unlisted count under-stated
    what had not been looked at. Both kinds are now recorded, and both reach the caller as data
    rather than as prose, so a table can carry *read to a cap* in a column instead of leaving a
    reader to infer it from a `Files` count.

    **Two things about how it reaches the network were wrong and are fixed together, 2026-08-12.**

    *The fetch was unconditional.* `file_urls(accession)` was this function's first statement, ahead
    of the filtering that decides whether any archive will be opened at all — so a call with
    `limit=0`, or one whose names are all instrument formats, fetched a deposit's whole URL map and
    used none of it. It is now deferred to the first archive that actually needs a URL. That alone
    would have turned three red tests green while leaving the loop below as unreachable offline as
    it was, which is why it is not the whole repair.

    *There was no seam.* Every sibling here — `search`, `file_names`, `file_urls`, `self_check` —
    takes an injectable `session`, and this one did not, so its first statement called an
    injectable function without a session to thread. `bzk/rebuild.py` is the established pattern.
    Passing it fixes the seam whether or not the fetch is deferred, and deferring the fetch fixes a
    request no caller needed whether or not there is a seam; neither substitutes for the other.

    **Two session parameters, not one, and the single one was tried first.** `file_urls` needs a
    `RestSession` and `archive_entries` a `RangedSession`, and no Protocol can express *both*:
    composing them is rejected outright — *Definition of "get" in base class "RestSession" is
    incompatible with definition in base class "RangedSession"* — because one returns a JSON
    response and the other a ranged one. The alternatives were a `type: ignore` at the call, which
    is the silenced-checker failure `bzk/http.py` was written against, or changing `RestSession`,
    which is the widening this module's third Protocol exists to avoid. So the contracts are
    declared separately; one `requests.Session` satisfies both and can be passed to each.
    """
    notes: list[str] = []
    skipped: list[str] = []
    grown = list(names)
    urls: dict[str, str] | None = None

    zips = [n for n in names if n.lower().endswith(".zip")]
    by_format = [n for n in zips if any(n.lower().endswith(h) for h in _RAW_ARCHIVE_HINTS)]
    archives = [n for n in zips if n not in by_format]
    for name in by_format:
        skipped.append(f"{name}: instrument format, not listed")

    for name in archives[:limit]:
        if urls is None:
            urls = file_urls(accession, session=session)
        url = urls.get(name)
        if not url:
            skipped.append(f"{name}: no public URL")
            continue
        try:
            inner = archive_entries(url, session=ranged)
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
            skipped.append(f"{name}: unreadable ({type(exc).__name__})")
            continue
        notes.append(f"{name}: {len(inner)} entries")
        grown.extend(f"{name}!{e}" for e in inner)

    for name in archives[limit:]:
        skipped.append(f"{name}: beyond the limit of {limit}")
    return tuple(grown), notes, tuple(skipped)


def classify(
    accession: str, *, session: RestSession | None = None, ranged: RangedSession | None = None
) -> Candidate:
    """One named deposit, classified — without going through the query path.

    **Added 2026-08-12 to re-measure the recorded twelve after six under-reporting modes closed.**
    `survey` takes *queries*; `--files` listed names and returned before any classification ran; so
    there was no way to ask *what does the current instrument say about this accession* without
    issuing a search. That matters beyond convenience: the re-run must not widen the draw, and a
    search is how a draw widens by accident.

    It reaches the project record for the title and submission type, then the file listing and the
    archives, and builds the same `Candidate` the survey builds — the same properties, so the
    comparison is against the instrument rather than against a second implementation of it.
    """
    s = session or requests.Session()
    row = _get(s, f"{API}/projects/{accession}") or {}
    names = file_names(accession, session=session)
    names, _notes, skipped = expand_archives(accession, names, session=session, ranged=ranged)
    return Candidate(
        accession=accession,
        title=str(row.get("title", "")),
        submission_type=str(row.get("submissionType", "")),
        species=_cv_names(row.get("organisms")),
        instruments=_cv_names(row.get("instruments")),
        software=_cv_names(row.get("softwares")),
        files=names,
        skipped=skipped,
        license=str(row.get("license", "") or ""),
    )


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
    parser.add_argument(
        "--classify",
        metavar="ACCESSION",
        nargs="+",
        help="classify named deposits and exit; no query is issued",
    )
    parser.add_argument("--cap", type=int, default=MAX_CANDIDATES)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if args.classify:
        self_check()
        for accession in args.classify:
            c = classify(accession)
            print(
                f"  {c.accession}  {c.submission_type:10s} files={len(c.files):4d} "
                f"engine={c.engine_state:20s} site={c.site_state:9s} "
                f"skipped={len(c.skipped)} sdrf={'Y' if c.has_sdrf else 'N'}  {c.title[:52]}"
            )
            for entry in c.site_tables:
                print(f"      site table: {entry}")
            for entry in c.site_candidates:
                print(f"      site candidate: {entry}")
            for entry in c.skipped:
                print(f"      ✕ {entry}")
        return 0

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
        try:
            names = file_names(c.accession)
            names, notes, skipped = expand_archives(c.accession, names)
        except (OSError, RuntimeError, requests.RequestException) as exc:
            # One accession that will not answer must not end the run. It did: `_get` raised on
            # any non-200 and the exception reached `main`, so a survey of twelve could report
            # three and stop, with the remaining nine looking like a field that was searched.
            print(f"  {c.accession}  UNREADABLE ({type(exc).__name__}) — recorded, not skipped")
            rows.append(Candidate(**{**c.__dict__, "skipped": (f"listing failed: {exc}",)}))
            continue
        c = Candidate(**{**c.__dict__, "files": names, "skipped": skipped})
        rows.append(c)
        for note in notes:
            print(f"      · {note}")
        for note in skipped:
            print(f"      ✕ {note}")
        print(
            f"  {c.accession}  {c.submission_type:10s} files={len(c.files):4d} "
            f"engine={c.engine_state:20s} site={c.site_state:9s} "
            f"skipped={len(c.skipped)} sdrf={'Y' if c.has_sdrf else 'N'}  {c.title[:52]}"
        )
    if args.json:
        json.dump([r.__dict__ for r in rows], sys.stdout, indent=2, default=list)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
