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
  3. structured strings     — ``parameters_json`` is parsed and re-serialized with sorted keys and
     normalized numeric forms, so key order, spacing and the int/float boundary cannot fork an id
     (§3, ADR-0020). **This one both normalizes and refuses**, and the boundary is stated at the
     raise: numeric *forms* normalize, because two spellings of one JSON number are one value;
     malformed JSON and **non-finite numbers** are refused, because neither can be canonically
     re-serialized *as JSON*, which is what this function's contract says it produces;
  4. mis-cased identifiers  — an accession, a CURIE prefix, or a UniProt CURIE's local part that
     departs from §4's fixed form is **refused, not repaired** (2026-08-08; the reasoning, and the
     one half of §4 l.266 that stays unenforced, are in `HANDOFF.md` §8).

Families 1–3 converge by normalizing and family 4 by refusing, and the split is not arbitrary. A
value normalizes when both spellings are legal renderings of one value — 250 and 250.0 are the same
JSON number, and there is nothing to refuse. It is refused when one spelling is simply wrong: a
lowercase UniProt accession is not another way of writing an accession, and rewriting it would (a)
leave the raw string in the node's own ``accession`` column and in every edge endpoint, so the id
and the content it identifies would disagree, and (b) make a curator's typo permanently invisible,
since the repaired id is well-formed and resolves. Refusing is also what this module already does
one clause over: ``modification_site_key`` raises on a PSI-MOD accession rather than translating it.

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

#: §3's authority prefixes plus the locally generated namespace §3's prose defines. The union is
#: built here rather than in `schema.py` so the mirror of the §3 *table* stays a mirror of it.
_KNOWN_PREFIXES: frozenset[str] = schema.CURIE_PREFIXES | {"bzk"}


class KeyError_(ValueError):
    """A node cannot be keyed — a required identifying value is missing or malformed."""


def check_accession_case(accession: str) -> str:
    """§4: *"`accession` keeps UniProt's own casing, uppercase, with any `-N` suffix"*.

    Refused rather than uppercased — see the module docstring. Returns the accession so a caller can
    use this inline; the return is the input, never a repaired version of it.

    This guards the **cache path** as well as the id. `bzk/resolve/uniprot.py` builds
    `cache/uniprot/entry/{canonical}.json` and `cache/uniprot/seq/{accession}#sv{n}.txt` from the
    accession string verbatim, where canonical means isoform-stripped and not case-folded. So a
    casing departure forks the sequence archive and the drift receipt's digest too — and forks them
    *differently by platform*, since a case-insensitive volume gives the two spellings one cache
    file while the graph still gets two ids. That divergence does not need UniProt to be case-
    insensitive to be real; it is a property of this code and this filesystem.

    Only the casing clause is enforced. Validating the whole accession grammar is a different and
    wider claim, and §4 does not make it.
    """
    if accession != accession.upper():
        raise KeyError_(
            f"accession {accession!r} is not uppercase; §4 fixes the accession at UniProt's own "
            "casing, so this is a malformed accession rather than another spelling of one. It is "
            "refused rather than repaired: uppercasing it here would leave the raw string in the "
            "node's `accession` column and in the cache path, and would hide the input error"
        )
    return accession


def check_curie_case(value: str) -> str:
    """§4 l.266, **which is two clauses**, enforced to different depths — deliberately.

    *"CURIE prefixes are lowercase and spelled exactly as in the §3 map"* is enforced for every
    prefix. It fires only when a prefix case-folds onto a *known* prefix but is not spelled the way
    the map spells it, and that precision is what makes the check safe to run over values that may
    not be CURIEs at all: a `filters_applied` token has no colon, and a title beginning "Note: …"
    case-folds to a prefix the map does not contain, so neither is touched. The cost is that it
    cannot catch an *unknown* prefix, which is a §3-map question rather than a casing one.

    *"The local part is the authority's own identifier rendered verbatim"* is enforced **for
    `uniprot` and `hgnc`**, and the scoping is a decision rather than an omission. §3's map spans
    authorities whose local parts are numeric (`unimod:121`, `pmid:21139048`), uppercase
    (`ensembl:ENSG…`) or carry the authority's own prefix (`chebi:CHEBI:15377`, `go:GO:0032020`,
    `mondo:MONDO_…`, and — since 2026-08-09 — `hgnc:HGNC:4053`). These two are enforced because
    they are the two in an identifying position: `candidate_proteins` is identifying on four node
    types and holds `uniprot:` ids, and `Gene.id` is the whole of `Gene`'s identity.

    **`hgnc` added 2026-08-09 with §4's sharpening, and it is the reason the sharpening happened.**
    The clause used to read *"keeps its authority's casing"*, which says nothing about a missing
    prefix, and §3's own map stripped HGNC's. So `hgnc:7532`, `hgnc:HGNC:7532` and `hgnc:hgnc:7532`
    were all accepted — three spellings of one gene, in the field that *is* that gene's identity —
    and the fork was invisible because no `Gene` node exists yet to fork. Enforced before the first
    one is minted rather than after, which is the only time it is free.

    What is checked is the authority's rendering, not the authority's grammar: `hgnc:HGNC:abc`
    passes. Validating the whole identifier is a wider claim than §4 makes, and the same line is
    drawn for `uniprot` — `check_accession_case` refuses a mis-cased accession and says nothing
    about a malformed one.

    `chebi`, `go` and `mondo` are now *determined* by §4's rule and merely unguarded; the rest are
    unenforced because the document fixes nothing to enforce. Both are recorded with a trigger in
    `HANDOFF.md` §8, and neither is in an identifying position today.

    The local-part check is scoped to the segment before the first `#`, because a composed §4 key
    continues past it in lowercase — `uniprot:P20591#sv4#K48#unimod:121` is canonical as written.
    """
    prefix, separator, local = value.partition(":")
    if not separator:
        return value
    if prefix != prefix.lower() and prefix.lower() in _KNOWN_PREFIXES:
        raise KeyError_(
            f"{value!r} spells the CURIE prefix {prefix!r}; §4 fixes it lowercase as "
            f"{prefix.lower()!r}. Refused rather than lowercased: this value is a node id, and "
            "normalizing the hashed copy would leave the raw string in the node's own column and "
            "in every edge endpoint, so the id and the content it identifies would disagree"
        )
    if prefix == "uniprot":
        # One home for the rule: the message names the accession segment, which is the part at
        # fault. Refusal mode follows `check_accession_case` for the same reasons.
        check_accession_case(local.split("#", 1)[0])
    if prefix == "hgnc" and not local.startswith("HGNC:"):
        # No `#` split here, unlike the UniProt branch: `hgnc:` anchors no composed key in §4, and
        # splitting would change nothing for any value this can be handed — `hgnc:7532#x` fails on
        # either side of it. Left out rather than copied across for symmetry it does not have.
        raise KeyError_(
            f"{value!r} does not render HGNC's identifier verbatim in the local part; §4 fixes it "
            "as the authority spells it, 'HGNC:' and the number, giving 'hgnc:HGNC:7532'. Refused "
            "rather than repaired, for `check_accession_case`'s reasons: this value is a node id "
            "and the whole of a `Gene`'s identity, so normalizing the hashed copy alone would "
            "leave the id and the node's own column disagreeing"
        )
    return value


def canonical_value(value: Any, column_type: str) -> str:
    """Render one value into its canonical string form. The whole of the discipline lives here."""
    if value is None:
        return _NULL
    if column_type == "STRING[]":
        # The CURIE check runs over list elements and anchor ids only — the two positions the
        # builder *knows* hold ids. Every identifying `STRING[]` in the DDL is a set of tokens
        # (four candidate-id lists and `filters_applied`); free text is always a scalar column, and
        # scalars are deliberately left alone so a title cannot be refused for containing a colon.
        # `None` passes through unchecked rather than through `str()`, so a null element still
        # renders `_NULL` and does not become the four characters "None".
        checked = [v if v is None else check_curie_case(str(v)) for v in value]
        return "[" + ",".join(sorted(canonical_value(v, "STRING") for v in checked)) + "]"
    if column_type == "DOUBLE":
        return repr(float(value))  # 1.8, 1.80 and 1.8000 all render '1.8'
    if column_type == "INT64":
        return str(int(value))
    if column_type == "BOOLEAN":
        return "true" if value else "false"
    return str(value)


def _canonical_json_numbers(value: Any) -> Any:
    """Collapse JSON's one number type back onto one Python form, recursively.

    `json.loads` preserves the written form — `250` parses to `int` and `250.0` to `float` — and
    `json.dumps` writes each back as it found it, so the two survive into the hash as different
    bytes. JSON has a single number type and they are the same value, so this is normalized rather
    than refused. **Every** integral float collapses to `int`; everything else keeps its parsed
    form, since `repr` already gives a float its shortest round-trip spelling (`0.1`, `0.10` and
    `1e-1` all reach `0.1` through the parse alone).

    **There was a `2**53` cutoff here, and its stated reason was false — removed 2026-08-08.** It
    said collapsing above that bound "would merge values rather than spellings". It cannot:
    `int()` on an integral float is exact at any magnitude (Python ints are arbitrary precision)
    and therefore injective, so no two distinct floats can collapse together — measured across
    `2**53`, `2**60`, `1e22` and `1e308`. Whatever precision was lost was lost at `json.loads`,
    before this function is reached. The only pair the collapse *can* merge is an int and the
    integral float of equal value, which JSON says is one number — the clause, not a defect.

    What the cutoff actually did was leave the int/float fork standing above the bound: `1e16` and
    `10000000000000000` hashed differently, which is the very defect this function exists to close,
    unfixed in a range. **The wrong reason was the worse half.** `s0` and a randomisation count will
    never approach `2**53`, so the unreachable fork cost nothing; a justification that reads as
    principled is what gets copied into the next boundary decision.

    Non-integral and non-finite floats are untouched: `0.1`, `inf` and `nan` all report
    `is_integer()` false, and a JSON literal too large for a float (`1e400`) parses to `inf`.
    """
    if isinstance(value, dict):
        return {k: _canonical_json_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_canonical_json_numbers(v) for v in value]
    # bool before int: `isinstance(True, int)` is True, and JSON's true is not the number 1.
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def canonical_parameters_json(raw: str | None) -> str:
    """Parse and re-serialize with sorted keys and normalized numbers (§3).

    Malformed JSON is an error rather than a passthrough: hashing it as raw text is precisely the
    behaviour §3 forbids, and silently doing so would reintroduce the defect for the field §5.4
    leaves open — the DDL says *"test-specific parameters, **e.g.** s0, n_randomisations"*, so the
    value space is whatever a test declares, not those two.

    **Non-finite values are refused at the same door — decided 2026-08-08.** Until then this
    function refused input that was not JSON and emitted output that was not JSON: Python's parser
    accepts `Infinity` and `NaN` as an extension, `json.dumps` writes them straight back, and
    `{"n": 1e400}` overflows to `inf` with no literal involved at all. No *fork* resulted — the
    parse is symmetric, `Infinity` and `1e400` converge, and distinct non-finite values stay
    distinct — so the defect was never a second id for one fact. It was that the function's stated
    contract, a canonical *JSON* re-serialization, produced a string no JSON parser accepts, and a
    test pinned that output as expected while nothing recorded it as a choice.

    Refused rather than accepted, for reasons beyond symmetry. `NaN` is `determined`/`curated`
    absence wearing a value's clothes (ADR-0021): it is identifying, it means *not a number*, and
    two analyses whose parameter failed to compute would converge on one id — asserting they are
    the same analysis when the data says only that both are broken. And family 4's rule applies:
    refuse when one spelling is simply wrong, and `NaN` is not a spelling of a parameter value.

    **The mechanism is `allow_nan=False` at the exit, not `parse_constant` at the entrance**, and
    that is deliberate: `parse_constant` fires only for the literals `Infinity`/`-Infinity`/`NaN`
    and never sees a decimal that overflows to `inf`, so it would leave `1e400` through. Checking on
    the way out catches both, at any nesting depth, with no second traversal that could drift from
    the first.

    **Reachability today is nil, and that is stated rather than hidden.** No code in this repository
    puts anything into `parameters_json`: `maxquant_sites.py` writes `None`, the curation loader
    never touches it, and `perseus.py` passes through a caller-supplied `DeclaredAnalysis` whose
    only constructors are in `tests/`. So this refusal — like the test it replaces — pins behaviour
    on an input no path produces, and establishes less than its name suggests. It is written for the
    producer that arrives next, and `json.dumps` defaults to `allow_nan=True`, so any producer
    serialising a params dict that holds a computed `nan` emits `{"s0": NaN}` without noticing.
    """
    if raw is None:
        return _NULL
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KeyError_(f"parameters_json is not valid JSON, so it cannot be canonicalized: {exc}")
    try:
        return json.dumps(
            _canonical_json_numbers(parsed), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
    except ValueError as exc:
        raise KeyError_(
            f"parameters_json holds a non-finite number, so it cannot be canonically re-serialized "
            f"as JSON: {exc}. Refused at the same door as malformed JSON — Python accepts "
            "`Infinity` and `NaN` as an extension and a decimal can overflow to `inf`, but neither "
            "is JSON, and a `NaN` in an identifying field is an absence wearing a value's clothes "
            "(ADR-0021)"
        )


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
    # `label=` here is the hashed identity tuple, NOT the change-set's node-type key — which was
    # renamed to `__label__` in 2026-08-07's ADR-0019 addendum. This one deliberately did not
    # follow: these bytes are hash input, so renaming the prefix would re-mint every evidence id in
    # the graph to fix a name collision that does not exist here (a node's *columns* never enter
    # the tuple by this route — only `spec.fields` do, and `label` is excluded from identity on
    # every node that has such a column).
    parts = [f"label={label}"]

    for field in sorted(spec.fields):
        if field == "parameters_json":
            rendered = canonical_parameters_json(node.get(field))
        else:
            rendered = canonical_value(node.get(field), types.get(field, "STRING"))
        parts.append(f"{field}={rendered}")

    anchors = anchor_ids or {}
    for anchor_type, _rel in sorted(spec.anchors):
        anchor_id = anchors.get(anchor_type)
        # An anchor id is an id by definition — a §4 reference CURIE or a `bzk:` digest — so §4's
        # prefix clause applies to it unambiguously, unlike a scalar STRING column.
        parts.append(
            f"@{anchor_type}={_NULL if anchor_id is None else check_curie_case(anchor_id)}"
        )

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
    return f"uniprot:{check_accession_case(accession)}"


def protein_sequence_key(protein_id: str, sequence_version: int | str | None) -> str:
    """`{Protein.id}#sv{n}` — n unpadded, per §4's canonicalization.

    The declared type is widened from `int` to match the accepted domain, which the body always
    had: `int(...)` is what performs §4's unpadding, so `'04'` and `4` both key `#sv4`, and
    `tests/test_keys.py` depends on that. A version arrives as text — from a FASTA header, from a
    cache path segment — far more often than as an int, and narrowing the signature to `int` would
    push `int()` out to every caller, which is where a zero-padded value would survive into an id.
    `None` is declared for the same reason: the I2 guard below exists to reject it loudly, and a
    signature that pretended it could not arrive would make that guard look like dead code.
    (`HANDOFF.md` §8 — this mismatch is what type-checking `tests/` surfaced.)
    """
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
