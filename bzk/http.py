"""The injected-HTTP surface, as protocols (`HANDOFF.md` §8, the `tests/` type-checking item).

Three modules take an optional `session` so their logic is exercisable offline — `resolve/uniprot`,
`sources/pride` and `rebuild`, which passes one through. Each declared the parameter as
`requests.Session | None`, which is stricter than the code needs and stricter than the tests can
satisfy: every test injects a small stub, and `mypy` reported 24 `[arg-type]` errors for it. A
`cast` would have silenced them while leaving the declaration wrong. The parameter's real
requirement is structural — *something with a `get`* — and that is what a `Protocol` says.

**Two protocols, not one, because the two callers need different response surfaces.** A deposit
fetch reads `content` and calls `raise_for_status`; the UniProt resolver reads `status_code` and
`text` and calls `json`. One protocol carrying all five would force every stub to grow members it
never uses — fake methods written only to satisfy a checker, which is worse than the untyped state
it replaced. `requests.Session` satisfies both structurally, so nothing at the call sites changes.

Members are declared as read-only properties rather than attributes: `requests.Response` implements
`text` and `content` as properties, and a settable protocol attribute is not satisfied by one.
"""

from __future__ import annotations

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
