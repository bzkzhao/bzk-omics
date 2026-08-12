"""The injected-HTTP surface, as protocols (`HANDOFF.md` §8, the `tests/` type-checking item).

**Five modules take an optional `session` so their logic is exercisable offline** — `resolve/uniprot`,
`drift`, `sources/pride`, `sources/protein_groups` and `deposit_survey`. *Corrected 2026-08-12: this
read "three modules … `resolve/uniprot`, `sources/pride` and `rebuild`, which passes one through".*
`rebuild` no longer takes one and says so at its own signature — its only network path is the
resolver, injected as `resolver` — and accepting a parameter it ignores would be a worse lie than
not having one; the other three were simply never added here. Each declared the parameter as
`requests.Session | None`, which is stricter than the code needs and stricter than the tests can
satisfy: every test injects a small stub, and `mypy` reported 24 `[arg-type]` errors for it. A
`cast` would have silenced them while leaving the declaration wrong. The parameter's real
requirement is structural — *something with a `get`* — and that is what a `Protocol` says.

**One protocol per response surface, not one shared, because the callers read different things.** A
deposit fetch reads `content` and calls `raise_for_status`; the UniProt resolver reads
`status_code` and `text` and calls `json`; a ranged read needs `head` and a `headers=` keyword. One
protocol carrying all of that would force every stub to grow members it never uses — fake methods
written only to satisfy a checker, which is worse than the untyped state it replaced.
`requests.Session` satisfies all three structurally, so nothing at the call sites changes.

**There are three since 2026-08-12, and the third was added rather than an existing one widened.**
`archive_entries` reads a remote zip's central directory over byte ranges, which needs `head(...)`
and `get(..., headers=...)`; widening `RestSession` would have been fewer declarations and would
have made `resolve/uniprot` and `drift` advertise a `head` neither calls, forcing their stubs to
grow one. That is the failure the paragraph above already rejects, so the choice follows the
principle this file was written on rather than the line count.

Members are declared as read-only properties rather than attributes: `requests.Response` implements
`text` and `content` as properties, and a settable protocol attribute is not satisfied by one.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class BytesResponse(Protocol):
    """What `sources/pride.py` reads off a response: the bytes, and the status raise."""

    @property
    def content(self) -> bytes: ...

    def raise_for_status(self) -> object: ...


class BytesSession(Protocol):
    """An HTTP session that can fetch a file. `requests.Session` is one."""

    def get(self, url: str, *, timeout: int = ...) -> BytesResponse: ...


class RestResponse(Protocol):
    """What `resolve/uniprot.py` reads: the status, the body as text, and the body as JSON.

    `status_code` is inspected rather than raised on — 404 is a resolution outcome (an accession
    that does not exist), not an error, which is why there is no `raise_for_status` here.
    """

    @property
    def status_code(self) -> int: ...

    @property
    def text(self) -> str: ...

    def json(self) -> Any: ...


class RestSession(Protocol):
    """An HTTP session that can query a JSON/FASTA REST API. `requests.Session` is one."""

    def get(self, url: str, *, timeout: int = ...) -> RestResponse: ...


class RangedResponse(Protocol):
    """What a ranged read needs off a response: the bytes, the headers, and the status raise.

    `headers` is a mapping rather than a `dict` because `requests` returns a case-insensitive one
    and the reader asks for `Content-Length` without caring which case the server sent.
    """

    @property
    def content(self) -> bytes: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    #: Declared because the ranged reader *checks* it: a 200 answering a `Range` request means the
    #: server ignored the header and sent the file's head. Reading it through `getattr` would have
    #: kept the Protocol silent about something the caller depends on.
    @property
    def status_code(self) -> int: ...

    def raise_for_status(self) -> object: ...


class RangedSession(Protocol):
    """An HTTP session that can ask for a byte range. `requests.Session` is one.

    Separate from `BytesSession` because that one fetches whole files and has no `head`, and from
    `RestSession` because that one reads JSON. The only consumer is `deposit_survey`, which reads
    a zip's central directory without downloading the archive.
    """

    def head(self, url: str, *, timeout: int = ...) -> RangedResponse: ...

    def get(
        self, url: str, *, headers: Mapping[str, str] = ..., timeout: int = ...
    ) -> RangedResponse: ...
