"""UniProt resolver tests — offline, via an injected fake session.

The load-bearing case is the guard (uniprot.py change 1): when an isoform's own sequence cannot
be retrieved, the resolver returns no sequence at all, so a position can never be validated
against the canonical sequence standing in for the isoform's. Synthetic sequences stand in for
the real P09914 canonical/isoform pair (ONTOLOGY.md §4): position 5 is T in the canonical and K
in the isoform, so a test that reaches K at position 5 proves the isoform sequence was used.
"""

from __future__ import annotations

from typing import Any

import requests

from bzk.resolve.uniprot import resolve, validate_position

CANON = "MKAAT"  # position 2 = K, position 5 = T
ISO = "MKAAK"  # position 2 = K, position 5 = K  (differs from canonical at 5)


class _Resp:
    def __init__(self, status_code: int, *, json_data: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> Any:
        return self._json


class _FakeSession:
    """Matches request URLs by substring; records calls. A route value that is an Exception raises."""

    def __init__(self, routes: dict[str, Any]) -> None:
        self._routes = routes
        self.calls: list[str] = []

    def get(self, url: str, *, timeout: int | None = None) -> _Resp:
        self.calls.append(url)
        for key, resp in self._routes.items():
            if key in url:
                if isinstance(resp, Exception):
                    raise resp
                return resp
        return _Resp(404)


def _canon_json(
    seq: str, *, sv: int = 2, reviewed: bool = True, gene: str = "IFIT1"
) -> dict[str, Any]:
    etype = "UniProtKB reviewed (Swiss-Prot)" if reviewed else "UniProtKB unreviewed (TrEMBL)"
    return {
        "entryType": etype,
        "sequence": {"value": seq},
        "entryAudit": {"sequenceVersion": sv, "lastSequenceUpdateDate": "2010-01-01"},
        "genes": [{"geneName": {"value": gene}}],
    }


def test_canonical_resolves_and_validates(tmp_path: Any) -> None:
    sess = _FakeSession({"P09914.json": _Resp(200, json_data=_canon_json(CANON))})
    res = resolve("P09914", cache_dir=tmp_path, session=sess)
    assert res.status == "ok"
    assert res.sequence_source == "canonical"
    assert res.sequence == CANON
    assert res.reviewed is True
    assert res.sequence_version == 2
    assert res.gene == "IFIT1"
    assert validate_position(res, 2) == "ok"  # K
    assert validate_position(res, 5) == "wrong_residue"  # T, not K


def test_isoform_uses_isoform_sequence_not_canonical(tmp_path: Any) -> None:
    sess = _FakeSession(
        {
            "P09914.json": _Resp(200, json_data=_canon_json(CANON)),
            "P09914-2.fasta": _Resp(200, text=">sp|P09914-2|IFIT1_HUMAN Isoform 2\n" + ISO),
        }
    )
    res = resolve("P09914-2", cache_dir=tmp_path, session=sess)
    assert res.is_isoform is True
    assert res.sequence_source == "isoform"
    assert res.sequence == ISO
    assert res.sequence_version == 2  # taken from the parent entry's entryAudit (change 3)
    assert res.reviewed is True  # inherited from the canonical entry
    # position 5 is T in canonical, K in isoform: reaching K proves the isoform sequence was used
    assert validate_position(res, 5) == "ok"


def test_isoform_unavailable_returns_no_sequence(tmp_path: Any) -> None:
    # The guard (change 1): a 404 on the isoform FASTA must not fall back to the canonical sequence.
    sess = _FakeSession(
        {
            "P09914.json": _Resp(200, json_data=_canon_json(CANON)),
            "P09914-2.fasta": _Resp(404),
        }
    )
    res = resolve("P09914-2", cache_dir=tmp_path, session=sess)
    assert res.sequence is None
    assert res.sequence_source == "isoform_unavailable"
    assert validate_position(res, 5) == "isoform_unavailable"  # never 'ok'/'wrong_residue'


def test_isoform_fetch_failure_returns_no_sequence(tmp_path: Any) -> None:
    sess = _FakeSession(
        {
            "P09914.json": _Resp(200, json_data=_canon_json(CANON)),
            "P09914-2.fasta": requests.ConnectionError("boom"),
        }
    )
    res = resolve("P09914-2", cache_dir=tmp_path, session=sess)
    assert res.sequence is None
    assert res.sequence_source == "isoform_fetch_failed"
    assert validate_position(res, 5) == "isoform_unavailable"


def test_not_found_has_no_sequence(tmp_path: Any) -> None:
    sess = _FakeSession({})  # everything 404s
    res = resolve("P99999", cache_dir=tmp_path, session=sess)
    assert res.status == "not_found"
    assert res.sequence is None
    assert validate_position(res, 1) == "not_found"


def test_two_tier_cache_avoids_refetch(tmp_path: Any) -> None:
    sess = _FakeSession(
        {
            "P09914.json": _Resp(200, json_data=_canon_json(CANON)),
            "P09914-2.fasta": _Resp(200, text=">x\n" + ISO),
        }
    )
    resolve("P09914-2", cache_dir=tmp_path, session=sess)
    assert len(sess.calls) == 2  # entry JSON + isoform FASTA
    resolve("P09914-2", cache_dir=tmp_path, session=sess)
    assert len(sess.calls) == 2  # both tiers served from cache
    resolve("P09914-2", cache_dir=tmp_path, session=sess, refresh=True)
    assert len(sess.calls) == 3  # refresh refetches the entry; immutable sequence still cached
    # tier-2 file is named with the full accession, never collapsed to canonical (ARCHITECTURE §2)
    assert any(p.name == "P09914-2#sv2.txt" for p in (tmp_path / "seq").glob("*.txt"))


def test_canonical_empty_sequence_is_no_sequence(tmp_path: Any) -> None:
    # A resolved canonical entry with an empty sequence gets its own status, not 'isoform_unavailable'.
    sess = _FakeSession({"P00000.json": _Resp(200, json_data=_canon_json(""))})
    res = resolve("P00000", cache_dir=tmp_path, session=sess)
    assert res.status == "ok"
    assert res.sequence is None
    assert res.sequence_source == "canonical"
    assert validate_position(res, 1) == "no_sequence"
