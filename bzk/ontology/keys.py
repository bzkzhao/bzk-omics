"""Deterministic id construction — the single key builder (ADR-0020, ADR-0021, ONTOLOGY.md §3–§4).

One builder serves both halves of the graph because both use one identity *model* — label,
identifying fields, anchor ids, and any qualifying-child field values — and differ only in
encoding. Reference nodes get the human-readable composite keys of §4; evidence nodes get a
`bzk:` digest.

**Canonicalization is defined once here, not per field** (`HANDOFF.md` §8, the key builder's
contract). Patching it field by field is what produced the defect it exists to prevent: two
spellings of one fact minting two ids. The three families the audit found:

  1. order-sensitive lists  — `STRING[]` values are sorted before hashing, so a search engine's
     candidate ordering cannot fork an id (``filters_applied``, ``candidate_modifiers``,
     ``candidate_proteins``);
  2. unformatted floats     — ``DOUBLE`` values are normalized through ``repr(float(v))``, so 1.8
     and 1.80 and the integer 8 and 8.0 agree;
  3. structured strings     — ``parameters_json`` is parsed and re-serialized with sorted keys, so
     key order and spacing cannot fork an id (§3, ADR-0020).

Absent values are permitted only where §3 classifies the absence ``determined`` or ``curated``
(ADR-0021); a null is encoded distinctly from an empty string so the two never collide.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from bzk.ontology import schema

# Length of the truncated SHA-256 in hex characters. 32 hex = 128 bits — ample for a single-lab
# graph, and a genuine collision would be a modelling defect surfacing as a duplicate id under
# ADR-0019's structural validation rather than as silent data loss.
DIGEST_HEX = 32

_NULL = "\x00null"  # distinct from "" so an absent value never collides with an empty one
_COLUMN_TYPES: dict[str, dict[str, str]] = {t.name: dict(t.columns) for t in schema.NODE_TABLES}


class KeyError_(ValueError):
    """A node cannot be keyed — a required identifying value is missing or malformed."""


def canonical_value(value: Any, column_type: str) -> str:
    """Render one value into its canonical string form. The whole of the discipline lives here."""
    if value is None:
        return _NULL
    if column_type == "STRING[]":
        return "[" + ",".join(sorted(canonical_value(v, "STRING") for v in value)) + "]"
    if column_type == "DOUBLE":
        return repr(float(value))  # 1.8, 1.80 and 1.8000 all render '1.8'
    if column_type == "INT64":
        return str(int(value))
    if column_type == "BOOLEAN":
        return "true" if value else "false"
    return str(value)


def canonical_parameters_json(raw: str | None) -> str:
    """Parse and re-serialize with sorted keys, so key order and spacing cannot fork an id.

    Malformed JSON is an error rather than a passthrough: hashing it as raw text is precisely the
    behaviour §3 forbids, and silently doing so would reintroduce the defect for the one field most
    likely to carry it (`s0` and the randomisation count).
    """
    if raw is None:
        return _NULL
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KeyError_(f"parameters_json is not valid JSON, so it cannot be canonicalized: {exc}")
    return json.dumps(parsed, sort_keys=True, separators=(",", ":"))


def identity_tuple(
    label: str,
    node: dict[str, Any],
    anchor_ids: dict[str, str] | None = None,
    child_values: dict[str, list[dict[str, Any]]] | None = None,
) -> str:
    """The canonical serialization an evidence id is hashed over (§3).

    `anchor_ids` maps anchor node type -> that node's id; absent anchors are permitted (not every
    anchor applies to every instance — a `DifferentialResult` has either a site or a protein).
    `child_values` maps child node type -> the child nodes, whose *values* are folded in; the set is
    sorted so several children of one parent cannot fork the id by enumeration order.
    """
    spec = schema.IDENTITY.get(label)
    if spec is None:
        raise KeyError_(f"{label!r} has no identity spec in schema.IDENTITY")
    types = _COLUMN_TYPES.get(label, {})
    parts = [f"label={label}"]

    for field in sorted(spec.fields):
        if field == "parameters_json":
            rendered = canonical_parameters_json(node.get(field))
        else:
            rendered = canonical_value(node.get(field), types.get(field, "STRING"))
        parts.append(f"{field}={rendered}")

    anchors = anchor_ids or {}
    for anchor_type, _rel in sorted(spec.anchors):
        parts.append(f"@{anchor_type}={anchors.get(anchor_type, _NULL)}")

    children = child_values or {}
    for child_type, _rel, fields in sorted(spec.child_fields):
        child_types = _COLUMN_TYPES.get(child_type, {})
        # Named apart from the per-field `rendered` above: this is a list of whole-child
        # renderings, and the two roles previously shared one name. `Analysis` runs both loops in
        # one call, so a str and a list[str] were bound to `rendered` in sequence. Harmless as
        # written — the assignment here always precedes its own read below — but `",".join()`
        # accepts a str and would silently join it character-by-character, so the reuse made a
        # future reordering fail quietly rather than loudly. Distinct names, distinct roles.
        child_renderings = sorted(
            "|".join(
                f"{f}={canonical_value(child.get(f), child_types.get(f, 'STRING'))}"
                for f in sorted(fields)
            )
            for child in children.get(child_type, [])
        )
        parts.append(f"~{child_type}=[" + ",".join(child_renderings) + "]")

    return "\n".join(parts)


def evidence_id(
    label: str,
    node: dict[str, Any],
    anchor_ids: dict[str, str] | None = None,
    child_values: dict[str, list[dict[str, Any]]] | None = None,
) -> str:
    """`bzk:` + truncated SHA-256 over the canonical identity tuple (ADR-0020)."""
    tup = identity_tuple(label, node, anchor_ids, child_values)
    return "bzk:" + hashlib.sha256(tup.encode("utf-8")).hexdigest()[:DIGEST_HEX]


# ── Reference keys: the readable composite templates of §4 ──────────────────────────────────────


def protein_key(accession: str) -> str:
    """`uniprot:{accession}` — the full accession, isoform suffix included (ADR-0005)."""
    if not accession:
        raise KeyError_("Protein requires an accession")
    return f"uniprot:{accession}"


def protein_sequence_key(protein_id: str, sequence_version: int) -> str:
    """`{Protein.id}#sv{n}` — n unpadded, per §4's canonicalization."""
    if sequence_version is None:
        raise KeyError_(f"ProteinSequence of {protein_id} requires a sequence_version (I2)")
    return f"{protein_id}#sv{int(sequence_version)}"


def modification_site_key(
    protein_sequence_id: str, residue: str, position: int, modification_type: str
) -> str:
    """`{ProteinSequence.id}#{residue}{position}#{modification_type}` (§4).

    Enforces §4's canonical forms at the point of construction: uppercase residue, and Unimod as
    the sole key authority — a PSI-MOD accession is a cross-reference and would fragment the site
    into a second node, defeating I7.
    """
    if not modification_type.startswith("unimod:"):
        raise KeyError_(
            f"modification_type {modification_type!r} is not a Unimod CURIE; §4 pins Unimod as the "
            "sole key authority and treats PSI-MOD as a cross-reference only"
        )
    return f"{protein_sequence_id}#{residue.upper()}{int(position)}#{modification_type}"
