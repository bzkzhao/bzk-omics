"""The five queries, and since 2026-10-09 the untested-row display beside the first. See the
package docstring for the three rules they are built to.

Every function takes an open `kuzu.Connection` rather than opening one, for `resolve/nodes.py`'s
reason: injected, so a test drives a graph it built itself and nothing here reaches for a path.
"""

from __future__ import annotations

import enum
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import kuzu

from bzk.ontology import invariants, schema

DEFAULT_GRAPH = Path.home() / ".bzk-omics" / "graph.kuzu"

#: `ONTOLOGY.md` §7's `prov:Entity` list. I5 says *entity node*, and this is where the word is
#: defined — so a provenance status is computed for exactly these and claimed for nothing else.
#: `Figure` has no table yet; the tuple is filtered against the DDL rather than trimmed by hand.
PROV_ENTITIES: tuple[str, ...] = ("Dataset", "SiteObservation", "DifferentialResult", "Figure")


class Absence(enum.Enum):
    """Why a query came back with nothing. `ONTOLOGY.md` §5.1's `quant_ref = NULL` treatment.

    An empty list is one object for every reason a list can be empty, and the reasons here are not
    interchangeable: *the analysis produced no significant sites* and *no analysis has been stored*
    are opposite claims about the same absence, and *the graph never retained this* is a third.
    """

    #: The question was answered and the answer is genuinely nothing.
    NONE_FOUND = "none_found"
    #: The node type the question reads is empty, so the question was not answered.
    NOT_STORED = "not_stored"
    #: The fact is not retained anywhere in the graph, so no query can answer it.
    NOT_RETAINED = "not_retained"
    #: The graph holds the fact but cannot attribute it from the key given.
    UNATTRIBUTABLE = "unattributable"


#: Returned in place of a value that does not exist, so a caller destructuring a record gets this
#: rather than `None` — which a column that is legitimately null also yields.
ABSENT = Absence.NONE_FOUND


#: I4's display labels, per (grain, kind, `protein_adjusted`) — the copy of `ONTOLOGY.md` §8 I4's
#: table, which is the rule's home (ADR-0038 D7), guarded against it by `tests/test_query.py`.
#: **A cell absent from this map is a cell no result may occupy**, not a cell awaiting a label:
#: `adjustment_label` raises on it and substitutes nothing.
I4_LABELS: dict[tuple[str, str, str], str] = {
    ("site", "condition", "not_applied"): "stoichiometry-uncorrected",
    ("site", "condition", "native"): "stoichiometry-native (ratiometric source)",
    ("site", "condition", "applied"): "stoichiometry-corrected",
    ("protein", "condition", "not_applied"): "abundance — no adjustment defined",
    ("protein", "differential_association", "not_applied"): "abundance-uncorrected",
    ("protein", "background_enrichment", "not_applied"): "abundance-uncorrected",
}

#: What an observation with no result in a contrast is shown as, once the count agrees (ADR-0038
#: D6-revised (c)). Never shown on absence alone — see `UntestedContrast`.
NOT_TESTED_LABEL = "not tested by the source analysis"


class UnlabelledCell(ValueError):
    """A result whose (grain, kind, state) is a cell with no label — one no result may occupy.

    Raised, never rendered: a blank or a dash in its place is the *runs cleanly and is wrong* shape
    this layer exists to refuse (ADR-0038 D7, `ONTOLOGY.md` §8 I4).
    """


def adjustment_label(result_id: str, grain: str, kind: str, state: object) -> str:
    """I4's label for one result, or `UnlabelledCell` naming the triple. **No fallback.**"""
    label = I4_LABELS.get((grain, kind, str(state)))
    if label is None:
        raise UnlabelledCell(
            f"DifferentialResult {result_id}: (grain {grain!r}, kind {kind!r}, protein_adjusted "
            f"{state!r}) is a cell no result may occupy (ONTOLOGY.md §8 I4, ADR-0038 D7). It has "
            "no label and none is substituted"
        )
    return label


@dataclass(frozen=True)
class Provenance:
    """I5, per entity. `unprovenanced` is the flag §8 names; `path` says what was traversed.

    The path is carried because *provenanced* is only as good as the definition of *reaches*, and a
    caller that cannot see the definition cannot tell a real path from a permissive one.
    """

    provenanced: bool
    analysis_ids: tuple[str, ...]
    path: str = "USED -> Dataset -> REPORTS_SITE"

    @property
    def unprovenanced(self) -> bool:
        return not self.provenanced


def substantially_imputed(
    n_values_numerator: int | None,
    n_values_denominator: int | None,
    n_imputed_numerator: int | None,
    n_imputed_denominator: int | None,
) -> bool | None:
    """§8 I15's *substantially imputed*, as ADR-0036 D8 defines it — the rule's only home in code.

    `True` when (a) more than half of the result's values are generated, **or** (b) either arm's
    values are all generated; (b) is what catches a wholly imputed arm in a small comparison, where
    it can be half or less of the values. `None` when any count is absent: the flag is then
    undeterminable, and is never reported as `False` (§6.5).
    """
    if (
        n_values_numerator is None
        or n_values_denominator is None
        or n_imputed_numerator is None
        or n_imputed_denominator is None
    ):
        return None
    more_than_half = 2 * (n_imputed_numerator + n_imputed_denominator) > (
        n_values_numerator + n_values_denominator
    )
    whole_arm = (
        n_imputed_numerator == n_values_numerator or n_imputed_denominator == n_values_denominator
    )
    return more_than_half or whole_arm


@dataclass(frozen=True)
class DifferentialRow:
    """One `DifferentialResult`, with everything §8 requires to travel beside its numbers.

    `quantity`, `test` and `fdr_method` come from the `Analysis` (I16 puts them there, not on the
    result), and `candidate_proteins` plus `assignment_confidence` come from the observation and
    its `ProteinAssignment` (I14's display half). `protein_adjusted` is I4's declared state.

    **`substantially_imputed` is computed from the result's own per-arm counts** (ADR-0036 D8), by
    `substantially_imputed()`. The four counts travel beside it, so the label can be read back to
    the numbers it came from. Where the generating `Analysis` has `parameters_observed = false` the
    counts are absent and the flag is `None` — undeterminable, never `False`, because a `False`
    would assert §8 I15's clause is satisfied for a result whose mask nobody holds.
    """

    result_id: str
    site_id: str | None
    observation_id: str | None
    protein_ids: tuple[str, ...]
    gene_symbols: tuple[str, ...]
    quantity: str | None
    test: str | None
    fdr_method: str | None
    log2fc: float | None
    p_value: float | None
    adj_p_value: float | None
    protein_adjusted: str | None
    adjustment_method: str | None
    #: `'site'` or `'protein'`, from the result's `RESULT_FOR_*` edge — as `_check_I4` reads it.
    grain: str
    #: The `Contrast` the result is in, and that contrast's kind as `invariants.contrast_kind`
    #: derives it. Derived on every read, never stored (ADR-0038 D2).
    contrast_id: str
    kind: str
    #: I4's display label for (grain, kind, `protein_adjusted`) — `I4_LABELS`, never a fallback.
    adjustment_label: str
    n_values_numerator: int | None
    n_values_denominator: int | None
    n_imputed_numerator: int | None
    n_imputed_denominator: int | None
    #: `None` where the counts are absent — see the class docstring. Never defaulted to `False`.
    substantially_imputed: bool | None
    candidate_proteins: tuple[str, ...]
    assignment_confidence: str | None
    provenance: Provenance


@dataclass(frozen=True)
class SiteKeying:
    """What one `ModificationSite` was keyed against, and on what basis (I17, ADR-0024)."""

    site_id: str
    sequence_id: str | None
    protein_id: str | None
    accession: str | None
    sequence_version: int | None
    residue: str | None
    position: int | None
    modification_type: str | None
    #: `reviewed_preferred` or `razor` (§6.3). Present on every observation of this site.
    keying_basis: tuple[str, ...]
    #: The accession I17 displaced, non-null only where `keying_basis = 'reviewed_preferred'`.
    displaced_protein: tuple[str, ...]
    candidate_proteins: tuple[str, ...]
    modifier_basis: tuple[str, ...]
    modifier_confidence: tuple[str, ...]
    provenance: Provenance


@dataclass(frozen=True)
class ImputationState:
    """An `Analysis`'s imputation state, which is a **set** and not a value.

    `IMPUTATION_FOR` is `MANY_ONE` (§6.5 DDL), so several `Imputation`s may attach to one
    `Analysis`. `ROADMAP.md`'s scope table said *"One per `Analysis`"* until 2026-08-09 and
    contradicted the normative DDL; this type follows the DDL. §8 I15's *substantially imputed* is
    defined on a `DifferentialResult`, from that result's per-arm counts (ADR-0036 D8), so it is not
    derivable from an `Analysis` and is not offered here — a caller wanting it reads
    `DifferentialRow.substantially_imputed`.
    """

    analysis_id: str
    methods: tuple[str, ...]
    seeds: tuple[int | None, ...]
    #: `NONE_FOUND` when the analysis has no `Imputation` — which I15 makes a violation, since it
    #: requires one *including* `method = 'none'`. `NOT_STORED` when no `Imputation` exists at all.
    absence: Absence | None
    #: I15 requires an `Imputation` on every `Analysis` producing differential results. Reported
    #: rather than raised: this is a read path, and refusing to answer would hide the state.
    satisfies_i15: bool


@dataclass(frozen=True)
class RefusalAnswer:
    """The refusals for an ingestion — which the graph does not retain.

    Measured 2026-08-09: there is no refusal node table, and `adapters.base.Refusal` never leaves
    the adapter's in-memory report. So this returns `NOT_RETAINED` and says how many the ingestion
    reported, if a caller supplies that from the run. It exists as a query, rather than being
    omitted, because *the population report is not reconstructible from the graph* is a fact about
    stored content that a caller should be able to discover by asking rather than by reading a
    document.

    **Re-examined the same day and left standing on purpose, which is different from left alone.**
    Whether a refusal should be retained was taken up and answered *no* at the node level: it has no
    entity to be, `evidence_id` refuses a label §3 does not carry, and `unprovenanced` iterates §7's
    `prov:Entity` list, so such a node would sit outside the only invariant this module enforces.
    ADR-0004's rule puts a per-input-row fact in the columnar store, which `bzk/query/` does not
    reach — so storing it there would move this gap rather than close it, in the way
    `substantially_imputed = None` already documents. `adapters/base.py` carries the three-kinds
    enumeration that goes with the decision. **`NOT_RETAINED` therefore keeps a live case**, and it
    is the only one of the four `Absence` values that does: it is the answer to a question no query
    can answer, as distinct from one this graph happens not to hold. (Since 2026-10-09
    `untested_rows` returns it too, for an external analysis carrying no recorded untested count —
    a reachable case with no instance on the real graph, which holds no external analysis.)
    """

    dataset_id: str | None
    reasons: tuple[tuple[str, int], ...]
    #: `None` only if a refusal table is ever added and holds rows; today always an `Absence`.
    absence: Absence | None
    detail: str


@dataclass(frozen=True)
class GeneSymbolAnswer:
    """One requested symbol: present, or absent with the reason attributed as far as it can be.

    **The attribution is per-`Protein`, and a bare symbol does not reach one.** `gene_absence`
    (§4) lives on the protein, and the route from a symbol to a protein runs through the `Gene`
    node that is missing by hypothesis — `Protein.name` is null by decision, so nothing else
    carries a symbol. Hence `UNATTRIBUTABLE` rather than a guess. A caller holding an accession
    gets the real attribution from `gene_absence_census` instead.

    **That reasoning holds only where `Gene` has rows, which was not checked until 2026-08-09.**
    `UNATTRIBUTABLE` means *the graph holds the fact and cannot attribute it from this key*, and
    over an empty table the graph holds nothing — so the absence is `NOT_STORED`, which is defined
    for exactly that condition. The two are not interchangeable on screen: one says the answer is
    somewhere in here, the other says the question was never answerable.
    """

    symbol: str
    present: bool
    gene_id: str | None
    protein_ids: tuple[str, ...]
    absence: Absence | None
    detail: str


class UntestedStatus(enum.Enum):
    """Whether an external analysis's untested rows may be shown as untested."""

    #: The derived count equals the recorded one: the observations are shown with
    #: `NOT_TESTED_LABEL`.
    UNTESTED = "untested"
    #: The two counts disagree, or no count is recorded for the contrast. The observations are
    #: **not** labelled: no result here could equally mean *absent from the file* or *dropped by a
    #: fault*, and only the agreement of two independent numbers separates those from *untested*.
    MISMATCH = "mismatch"


@dataclass(frozen=True)
class UntestedContrast:
    """For one contrast of one external `Analysis`: its observations with no result, checked.

    `derived` is counted from the graph — observations the analysis's `Dataset` reports with no
    `DifferentialResult` of this analysis in this contrast. `recorded` is the analysis's own
    `rows_untested_json` entry, written by the adapter that recognised the rows (ADR-0038
    D6-revised (c)). They are obtained independently, so their agreement is the check.

    **Not an `Absence`, and the distinction is why this type exists.** `Absence` says why a
    question came back empty. Here the question has an answer: the observations are present, their
    results are absent, and the absence is *accounted for* by a recorded count — a positive finding
    about those observations rather than a reason for having nothing to say. Folding it into
    `Absence` would let *untested* and *not stored* share a channel, which is the conflation that
    enum exists to stop.
    """

    contrast_id: str
    recorded: int | None
    derived: int
    status: UntestedStatus
    #: The observations with no result here. Carried in both states so a mismatch can be
    #: investigated; only `UNTESTED` licenses showing them with `NOT_TESTED_LABEL`.
    observation_ids: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class UntestedAnswer:
    """The untested-row display for one `Analysis` (ADR-0038 D6-revised (c)).

    `applies` is `False` for a `processing` or `curation` analysis, whose `rows_untested_json` is
    NULL by definition: a platform run decides itself which rows reach its test and states that rule
    in `filters_applied`, so there is no source analysis whose placeholders it must recognise, and
    a curation run tests nothing. Nothing is derived for one — deriving a count with nothing to
    check it against is exactly the inference from absence D6-revised (c) forbids.
    """

    analysis_id: str
    applies: bool
    contrasts: tuple[UntestedContrast, ...]
    #: `NOT_STORED` where no such `Analysis` exists. `NOT_RETAINED` where an external analysis
    #: carries no recorded count — written before the field existed, or by an adapter that does not
    #: recognise untested rows — so the observations with no result cannot be told apart.
    absence: Absence | None
    detail: str


def connect(graph: Path = DEFAULT_GRAPH, *, read_only: bool = True) -> kuzu.Connection:
    """Open the graph read-only. Separate from the queries so a test can inject its own."""
    return kuzu.Connection(kuzu.Database(str(graph), read_only=read_only))


def _rows(conn: kuzu.Connection, cypher: str, **params: Any) -> list[list[Any]]:
    result = conn.execute(cypher, params) if params else conn.execute(cypher)
    assert not isinstance(result, list), "multi-statement queries are not used here"
    out: list[list[Any]] = []
    while result.has_next():
        row = result.get_next()
        assert isinstance(row, list), f"expected a row, got {type(row).__name__}"
        out.append(row)
    return out


def _node_tables(conn: kuzu.Connection) -> set[str]:
    return {r[0] for r in _rows(conn, "CALL show_tables() RETURN name, type")}


def _count(conn: kuzu.Connection, label: str) -> int:
    return int(_rows(conn, f"MATCH (n:{label}) RETURN count(n)")[0][0])


def _tidy(values: Iterable[Any]) -> tuple[Any, ...]:
    """Deduplicate while keeping order, dropping nulls. Used for the every-observation columns."""
    return tuple(dict.fromkeys(v for v in values if v is not None))


# ── I5, the one invariant this layer enforces ───────────────────────────────────────────────────


def _provenance(conn: kuzu.Connection, label: str, node_id: str) -> Provenance:
    """Whether one entity reaches an `Analysis`, per I5 and §7's `prov:Entity` list.

    The traversal is spelled out per label rather than expressed as a variable-length path, and
    that is a limitation stated rather than hidden: §7 declares five provenance relationships with
    different directions, so a generic `-[*]-` would count a path through any edge at all and would
    report *provenanced* for everything. A named path can be wrong; an unnamed one is meaningless.
    """
    if label == "Dataset":
        cypher = "MATCH (a:Analysis)-[:USED]->(d:Dataset) WHERE d.id = $id RETURN DISTINCT a.id"
        path = "Analysis -USED-> Dataset"
    elif label == "SiteObservation":
        cypher = (
            "MATCH (a:Analysis)-[:USED]->(:Dataset)-[:REPORTS_SITE]->(o:SiteObservation) "
            "WHERE o.id = $id RETURN DISTINCT a.id"
        )
        path = "Analysis -USED-> Dataset -REPORTS_SITE-> SiteObservation"
    elif label == "DifferentialResult":
        cypher = (
            "MATCH (r:DifferentialResult)-[:WAS_GENERATED_BY]->(a:Analysis) "
            "WHERE r.id = $id RETURN DISTINCT a.id"
        )
        path = "DifferentialResult -WAS_GENERATED_BY-> Analysis"
    else:
        # Not a §7 entity, or an entity with no declared provenance relationship yet (`Figure`).
        # Reported as unprovenanced with an empty path rather than as provenanced-by-default, which
        # is the direction I5 fails safe in: *flagged* is the state it asks for when no path exists.
        return Provenance(provenanced=False, analysis_ids=(), path="")
    found = tuple(str(r[0]) for r in _rows(conn, cypher, id=node_id))
    return Provenance(provenanced=bool(found), analysis_ids=found, path=path)


def unprovenanced(conn: kuzu.Connection) -> dict[str, tuple[int, int]]:
    """I5 across the graph: `{label: (unprovenanced, total)}` over §7's entity types.

    The whole-graph form of `_provenance`, so the invariant can be checked rather than only carried
    on rows a caller happened to ask for. Two things this signature is shaped by, both instances of
    the rule the module is built to:

    * **Labels absent from the DDL are skipped, not reported as zero.** `Figure` has no table, and
      `Figure: 0` reads as *checked and clean*.
    * **The total is returned beside the count**, because `DifferentialResult: 0` is true of an
      empty table and of a fully provenanced one, and those are the same two meanings an empty list
      conflates everywhere else here. Measured 2026-08-09 the real graph gave
      `{'Dataset': (0, 1), 'SiteObservation': (0, 2029), 'DifferentialResult': (0, 0)}` — and the
      third of those was 0 of 0, which the bare count would have shown as a pass. **It is
      `(0, 1362)` since the `welch_t` run was written the same day**, so the first number now means
      what it always claimed to; the entry is kept because the 0-of-0 state is what the totals were
      added for and it existed for two days.
    """
    present = _node_tables(conn)
    out: dict[str, tuple[int, int]] = {}
    for label in PROV_ENTITIES:
        if label not in present:
            continue
        ids = [str(r[0]) for r in _rows(conn, f"MATCH (n:{label}) RETURN n.id")]
        out[label] = (sum(1 for i in ids if not _provenance(conn, label, i).provenanced), len(ids))
    return out


# ── Enumeration: the ids a caller needs before it can ask any of the five questions ─────────────


def site_ids(conn: kuzu.Connection) -> list[str]:
    """Every `ModificationSite` id, sorted. See `analysis_ids` for why these two exist."""
    return [str(r[0]) for r in _rows(conn, "MATCH (s:ModificationSite) RETURN s.id ORDER BY s.id")]


def analysis_ids(conn: kuzu.Connection) -> list[str]:
    """Every `Analysis` id, sorted.

    **These two were added 2026-08-09 by the first caller, and the reason is worth keeping.**
    `bzk/ui/` may import `bzk.query` and nothing else from `bzk/` — no `kuzu`, no Cypher — so that
    *the UI derives nothing* is checkable rather than a habit. The first panel written against that
    rule immediately needed a list of site ids to put in a selector, which this layer did not
    expose; the first draft reached for `_rows` with a `MATCH` in it, which is precisely the leak
    the rule exists to catch. The gap was real and it is closed **here**, in the read layer, rather
    than worked around in the renderer.

    They are enumerations and not questions: no `Absence`, no status, no records. A caller that
    needs to *know something* about a site calls `site_keying`; these only say which ones exist.
    """
    return [str(r[0]) for r in _rows(conn, "MATCH (a:Analysis) RETURN a.id ORDER BY a.id")]


# ── Kind, derived and never stored (ADR-0038 D2) ────────────────────────────────────────────────


def _contrast_kind(conn: kuzu.Connection, contrast_id: str) -> str:
    """A contrast's kind, by `invariants.contrast_kind` — **the one derivation**; this function
    only reads what it needs from the graph and never re-implements D2's table.

    What it reads, each property by name: the `CONTRAST_IN_EXPERIMENT` anchor's `modality`, and
    the arms' `Sample`s through `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE` with their `role` and
    `bait`, which are what `contrast_kind` consults.

    **Its I22 refusal propagates from here as the view's refusal, and that is deliberate.** A
    contrast whose arms do not derive a kind — an empty arm, mixed roles, a control numerator — gives
    its results no (grain, kind, state) cell, which is the no-fallback case: catching it would mean
    substituting something for a label that does not exist. A contrast with no anchor is refused
    the same way rather than read as `modality` NULL, which `contrast_kind` would accept as a
    non-IP experiment — a default where the graph says nothing.
    """
    anchor = _rows(
        conn,
        "MATCH (c:Contrast)-[:CONTRAST_IN_EXPERIMENT]->(e:Experiment) WHERE c.id = $id "
        "RETURN e.modality",
        id=contrast_id,
    )
    if not anchor:
        raise UnlabelledCell(
            f"Contrast {contrast_id} has no CONTRAST_IN_EXPERIMENT anchor, so its modality and "
            "therefore its kind cannot be derived; its results have no I4 cell"
        )
    arms: dict[str, list[dict[str, object]]] = {}
    for rel in ("NUMERATOR_SAMPLE", "DENOMINATOR_SAMPLE"):
        arms[rel] = [
            {"id": r[0], "role": r[1], "bait": r[2]}
            for r in _rows(
                conn,
                f"MATCH (c:Contrast)-[:{rel}]->(s:Sample) WHERE c.id = $id "
                "RETURN s.id, s.role, s.bait ORDER BY s.id",
                id=contrast_id,
            )
        ]
    # Raises `invariants.InvariantError` (I22) where no kind derives — the view's refusal, above.
    return invariants.contrast_kind(
        contrast_id, anchor[0][0], arms["NUMERATOR_SAMPLE"], arms["DENOMINATOR_SAMPLE"]
    )


# ── Q1: the differential table for an Analysis ──────────────────────────────────────────────────


def differential_table(
    conn: kuzu.Connection, analysis_id: str
) -> tuple[list[DifferentialRow], Absence | None]:
    """Site, protein, gene symbol, quantity, statistic — for one `Analysis`.

    Returns `(rows, absence)`. **`absence` is the point of the signature**, and the real graph has
    now been in both states in one day. Until the `welch_t` run was written on 2026-08-09 there were
    **0** `DifferentialResult` nodes, so every empty answer meant *no results are stored*. There are
    **1,362** now, all belonging to one analysis — so the same empty list returned for the ingestion
    or curation analysis means *this analysis produced none*, and comes back `NONE_FOUND`. Nothing
    at the call site distinguishes the two without the absence, which is the failure this whole
    layer is shaped around.
    """
    if "DifferentialResult" not in _node_tables(conn) or _count(conn, "DifferentialResult") == 0:
        return [], Absence.NOT_STORED

    analysis = _rows(
        conn,
        "MATCH (a:Analysis) WHERE a.id = $id RETURN a.quantity, a.test, a.fdr_method",
        id=analysis_id,
    )
    quantity, test, fdr = analysis[0] if analysis else (None, None, None)

    # One derivation per contrast, not per row: 1,362 results share one contrast on the real graph.
    kinds: dict[str, str] = {}
    rows: list[DifferentialRow] = []
    for record in _rows(
        conn,
        # `RESULT_FOR_SITE` runs `DifferentialResult -> SiteObservation`, **not** to the
        # `ModificationSite` — the site is one more hop, through `MEASURED_AT`. Corrected here
        # after the fixture refused the change-set: written against the wrong endpoint first, and
        # structural validation named it before any row came back.
        "MATCH (r:DifferentialResult)-[:WAS_GENERATED_BY]->(a:Analysis) WHERE a.id = $id "
        "OPTIONAL MATCH (r)-[:RESULT_FOR_SITE]->(o:SiteObservation) "
        "OPTIONAL MATCH (o)-[:MEASURED_AT]->(s:ModificationSite) "
        "OPTIONAL MATCH (pa:ProteinAssignment)-[:PROTEIN_ASSIGNMENT_FOR]->(o) "
        "OPTIONAL MATCH (r)-[:RESULT_IN_CONTRAST]->(c:Contrast) "
        "RETURN r.id, r.log2fc, r.p_value, r.adj_p_value, r.protein_adjusted, "
        "r.adjustment_method, r.n_values_numerator, r.n_values_denominator, "
        "r.n_imputed_numerator, r.n_imputed_denominator, o.id, o.candidate_proteins, s.id, "
        "pa.confidence, c.id "
        "ORDER BY r.id",
        id=analysis_id,
    ):
        (rid, log2fc, p_value, adj_p, adjusted, method) = record[:6]
        (nv_num, nv_den, ni_num, ni_den) = record[6:10]
        (oid, candidates, sid, conf, cid) = record[10:]
        candidates = tuple(str(c) for c in (candidates or []))
        # `RESULT_FOR_PROTEIN` runs to a `ProteinObservation`, not to a `Protein`, so the protein
        # ids come through it rather than from it.
        at_protein_grain = _rows(
            conn,
            "MATCH (r:DifferentialResult)-[:RESULT_FOR_PROTEIN]->(po:ProteinObservation) "
            "WHERE r.id = $id RETURN po.candidate_proteins",
            id=str(rid),
        )
        proteins = _tidy(c for row in at_protein_grain for c in (row[0] or []))
        # Grain from the `RESULT_FOR_*` edge, as `_check_I4` reads it. I20 makes it exactly one;
        # a result with neither or both has no grain, so no cell, and is refused like one.
        if (oid is None) == (not at_protein_grain):
            raise UnlabelledCell(
                f"DifferentialResult {rid}: it attaches by "
                f"{'both' if oid is not None else 'neither'} of RESULT_FOR_SITE and "
                "RESULT_FOR_PROTEIN, so it has no grain and no I4 cell (I20)"
            )
        grain = "site" if oid is not None else "protein"
        if cid is None:
            raise UnlabelledCell(
                f"DifferentialResult {rid} is in no Contrast (RESULT_IN_CONTRAST), so it has no "
                "kind and no I4 cell (ONTOLOGY.md §8 I4, ADR-0038 D7)"
            )
        if str(cid) not in kinds:
            kinds[str(cid)] = _contrast_kind(conn, str(cid))
        kind = kinds[str(cid)]
        label = adjustment_label(str(rid), grain, kind, adjusted)
        wanted = [str(x) for x in proteins] or list(candidates)
        symbols = (
            _tidy(
                r[0]
                for r in _rows(
                    conn,
                    "MATCH (g:Gene)-[:ENCODES]->(p:Protein) WHERE p.id IN $ids RETURN g.symbol",
                    ids=wanted,
                )
            )
            if wanted
            else ()
        )
        rows.append(
            DifferentialRow(
                result_id=str(rid),
                site_id=str(sid) if sid else None,
                observation_id=str(oid) if oid else None,
                protein_ids=tuple(str(p) for p in proteins),
                gene_symbols=tuple(str(x) for x in symbols),
                quantity=quantity,
                test=test,
                fdr_method=fdr,
                log2fc=log2fc,
                p_value=p_value,
                adj_p_value=adj_p,
                protein_adjusted=adjusted,
                adjustment_method=method,
                grain=grain,
                contrast_id=str(cid),
                kind=kind,
                adjustment_label=label,
                n_values_numerator=nv_num,
                n_values_denominator=nv_den,
                n_imputed_numerator=ni_num,
                n_imputed_denominator=ni_den,
                substantially_imputed=substantially_imputed(nv_num, nv_den, ni_num, ni_den),
                candidate_proteins=candidates,
                assignment_confidence=str(conf) if conf else None,
                provenance=_provenance(conn, "DifferentialResult", str(rid)),
            )
        )
    return rows, (None if rows else Absence.NONE_FOUND)


def untested_rows(conn: kuzu.Connection, analysis_id: str) -> UntestedAnswer:
    """ADR-0038 D6-revised (c)'s display half: for each contrast an external `Analysis` carries,
    the observations with no result there — **shown as untested only where the derived count
    equals the recorded one**, and as a mismatch naming both numbers otherwise. Never the label on
    absence alone.

    The contrasts are those the recorded count names, together with any its results reach, so a
    contrast with results and no recorded count is a mismatch rather than skipped.
    """
    found = _rows(
        conn,
        "MATCH (a:Analysis) WHERE a.id = $id RETURN a.kind, a.rows_untested_json",
        id=analysis_id,
    )
    if not found:
        return UntestedAnswer(
            analysis_id, False, (), Absence.NOT_STORED, f"no Analysis {analysis_id} is stored"
        )
    kind, recorded_json = found[0]
    if kind != "external":
        return UntestedAnswer(
            analysis_id,
            False,
            (),
            None,
            f"a {kind!r} analysis has no source analysis whose untested rows it must recognise: "
            "the rows that reach its test are the ones its filters_applied admit",
        )
    if recorded_json is None:
        return UntestedAnswer(
            analysis_id,
            True,
            (),
            Absence.NOT_RETAINED,
            "this external analysis carries no rows_untested_json, so an observation with no "
            "result cannot be told apart from one absent from the file or dropped by a fault; "
            "none is labelled untested",
        )
    recorded: dict[str, int] = json.loads(str(recorded_json))

    observed = {
        str(r[0])
        for rel, label in (
            ("REPORTS_PROTEIN", "ProteinObservation"),
            ("REPORTS_SITE", "SiteObservation"),
        )
        for r in _rows(
            conn,
            f"MATCH (a:Analysis)-[:USED]->(:Dataset)-[:{rel}]->(o:{label}) WHERE a.id = $id "
            "RETURN o.id",
            id=analysis_id,
        )
    }
    with_result: dict[str, set[str]] = {}
    for rel, label in (
        ("RESULT_FOR_PROTEIN", "ProteinObservation"),
        ("RESULT_FOR_SITE", "SiteObservation"),
    ):
        for contrast_id, observation_id in _rows(
            conn,
            "MATCH (r:DifferentialResult)-[:WAS_GENERATED_BY]->(a:Analysis) WHERE a.id = $id "
            f"MATCH (r)-[:RESULT_IN_CONTRAST]->(c:Contrast) MATCH (r)-[:{rel}]->(o:{label}) "
            "RETURN c.id, o.id",
            id=analysis_id,
        ):
            with_result.setdefault(str(contrast_id), set()).add(str(observation_id))

    contrasts = []
    for contrast_id in sorted(set(recorded) | set(with_result)):
        missing = tuple(sorted(observed - with_result.get(contrast_id, set())))
        count = recorded.get(contrast_id)
        if count == len(missing):
            status, detail = (
                UntestedStatus.UNTESTED,
                (
                    f"{count} observation(s) {NOT_TESTED_LABEL}; the derived count equals "
                    "the analysis's recorded count"
                ),
            )
        else:
            status, detail = (
                UntestedStatus.MISMATCH,
                (
                    f"the graph has {len(missing)} observation(s) with no result in contrast "
                    f"{contrast_id}, but the analysis records "
                    f"{'no count' if count is None else count} untested — so none is labelled "
                    "untested: the difference could be rows absent from the file or dropped by a "
                    "fault, and the graph cannot say which"
                ),
            )
        contrasts.append(
            UntestedContrast(contrast_id, count, len(missing), status, missing, detail)
        )
    return UntestedAnswer(analysis_id, True, tuple(contrasts), None, "")


# ── Q2: what one ModificationSite was keyed against ─────────────────────────────────────────────


def site_keying(conn: kuzu.Connection, site_id: str) -> SiteKeying | None:
    """What a site was keyed against and on what basis (I2, I17, ADR-0024).

    `keying_basis` and `displaced_protein` are tuples because they live on the **observation**, not
    on the site, and a site may be observed more than once. Collapsing them to a scalar would pick
    one silently — which is the shape ADR-0024 rejected one clause over.
    """
    site = _rows(
        conn,
        "MATCH (s:ModificationSite) WHERE s.id = $id "
        "RETURN s.residue, s.position, s.modification_type",
        id=site_id,
    )
    if not site:
        return None
    residue, position, modification_type = site[0][0], site[0][1], site[0][2]

    target = _rows(
        conn,
        "MATCH (s:ModificationSite)-[:SITE_ON]->(q:ProteinSequence) WHERE s.id = $id "
        "OPTIONAL MATCH (p:Protein)-[:HAS_SEQUENCE]->(q) "
        "RETURN q.id, q.sequence_version, p.id, p.accession",
        id=site_id,
    )
    seq_id, sv, protein_id, accession = target[0] if target else (None, None, None, None)

    obs = _rows(
        conn,
        "MATCH (o:SiteObservation)-[:MEASURED_AT]->(s:ModificationSite) WHERE s.id = $id "
        "OPTIONAL MATCH (o)<-[:ASSIGNMENT_FOR]-(ma:ModifierAssignment) "
        "RETURN o.id, o.keying_basis, o.displaced_protein, o.candidate_proteins, "
        "ma.basis, ma.confidence ORDER BY o.id",
        id=site_id,
    )
    observation_ids = _tidy(r[0] for r in obs)
    return SiteKeying(
        site_id=site_id,
        sequence_id=str(seq_id) if seq_id else None,
        protein_id=str(protein_id) if protein_id else None,
        accession=str(accession) if accession else None,
        sequence_version=sv,
        residue=residue,
        position=position,
        modification_type=modification_type,
        keying_basis=tuple(str(v) for v in _tidy(r[1] for r in obs)),
        displaced_protein=tuple(str(v) for v in _tidy(r[2] for r in obs)),
        candidate_proteins=tuple(str(c) for c in _tidy(c for r in obs for c in (r[3] or []))),
        modifier_basis=tuple(str(v) for v in _tidy(r[4] for r in obs)),
        modifier_confidence=tuple(str(v) for v in _tidy(r[5] for r in obs)),
        provenance=(
            _provenance(conn, "SiteObservation", str(observation_ids[0]))
            if observation_ids
            else Provenance(provenanced=False, analysis_ids=(), path="")
        ),
    )


# ── Q3: an Analysis's imputation state ──────────────────────────────────────────────────────────


def imputation_state(conn: kuzu.Connection, analysis_id: str) -> ImputationState:
    """The **set** of `Imputation`s attached to one `Analysis` (§6.5, I15).

    A set, not a value: `IMPUTATION_FOR` is `MANY_ONE`, so several may attach. I15 requires at
    least one — *including* `method = 'none'` — so an empty set is a violation and is reported as
    one rather than raised: this is a read path, and refusing to answer would hide the state a
    caller asked about. Measured 2026-08-09, the real graph had **0** `Imputation` nodes; the
    `welch_t` run written the same day added **1**, so the two older analyses moved from
    `NOT_STORED` to `NONE_FOUND` without their own state changing at all. That transition is what
    `absence` is for: *this analysis has none* and *none are stored at all* are different facts and
    the empty set is the same object for both.
    """
    stored = "Imputation" in _node_tables(conn) and _count(conn, "Imputation") > 0
    rows = _rows(
        conn,
        "MATCH (i:Imputation)-[:IMPUTATION_FOR]->(a:Analysis) WHERE a.id = $id "
        "RETURN i.method, i.seed ORDER BY i.method, i.seed",
        id=analysis_id,
    )
    if not rows:
        return ImputationState(
            analysis_id=analysis_id,
            methods=(),
            seeds=(),
            absence=Absence.NONE_FOUND if stored else Absence.NOT_STORED,
            satisfies_i15=False,
        )
    return ImputationState(
        analysis_id=analysis_id,
        methods=tuple(str(r[0]) for r in rows),
        seeds=tuple(r[1] for r in rows),
        absence=None,
        satisfies_i15=True,
    )


# ── Q4: the refusals for an ingestion ───────────────────────────────────────────────────────────


def refusals(conn: kuzu.Connection, dataset_id: str | None = None) -> RefusalAnswer:
    """The refusals for an ingestion — **not retained in the graph**, established 2026-08-09.

    There is no refusal node table, and `adapters.base.Refusal` never leaves the adapter's report.
    So the honest answer is `NOT_RETAINED`, and the query exists to make that discoverable by
    asking. Returning `[]` would say *this ingestion refused nothing*, which is false: PXD018299's
    ingestion refuses 27 rows and every one of them is a site the graph does not contain.

    The check is against the DDL rather than hard-coded, so if a refusal table is ever added this
    stops reporting `NOT_RETAINED` on its own instead of quietly continuing to.
    """
    tables = _node_tables(conn)
    candidates = sorted(t for t in tables if "refus" in t.lower())
    if candidates:
        rows = _rows(conn, f"MATCH (r:{candidates[0]}) RETURN r.reason, count(r)")
        return RefusalAnswer(
            dataset_id=dataset_id,
            reasons=tuple((str(r[0]), int(r[1])) for r in rows),
            absence=None if rows else Absence.NONE_FOUND,
            detail=f"read from {candidates[0]!r}",
        )
    return RefusalAnswer(
        dataset_id=dataset_id,
        reasons=(),
        absence=Absence.NOT_RETAINED,
        detail=(
            "no refusal node table exists in the DDL; a refusal is recorded only in the adapter's "
            "in-memory report at ingestion time and is not written to the graph, so the ingested "
            "population is not reconstructible from stored content"
        ),
    )


# ── Q5: which gene symbols are present, and why the others are not ──────────────────────────────


def gene_symbols(conn: kuzu.Connection, symbols: Sequence[str]) -> list[GeneSymbolAnswer]:
    """Which of a set of symbols is present in stored content, and why each absent one is not.

    **The absent half is honest about a limit rather than guessing.** §4's three `gene_absence`
    states live on a `Protein`, and the route from a symbol to a protein runs through the `Gene`
    node that is missing by hypothesis; `Protein.name` is null by decision, so nothing else on a
    protein carries a symbol. So an absent symbol gets `UNATTRIBUTABLE` and says why. Registered as
    falsifiable before it was written: if a route existed, some absent symbol would come back
    attributed.

    A present symbol carries the proteins it encodes, because *present* on its own is the bare
    answer this layer does not return — `RIGI` being present does not tell a caller asking about
    `DDX58` anything unless the ids are there to compare.

    **The empty-table check was missing until 2026-08-09 and this was the only one of the five
    queries without it.** `differential_table`, `imputation_state` and `refusals` all consult the
    DDL before choosing an absence; this went straight to the `MATCH`, so over a graph built with
    no `raw/` every symbol came back `UNATTRIBUTABLE` — asserting that the graph held what would
    answer the question, of a graph holding nothing. Found by driving the app during the cold-clone
    rehearsal, not by a test: both fixtures the read layer had were populated, so nothing could
    reach the branch. The check is `Gene`-specific rather than *is the graph empty*, because the
    condition being reported is about the table this query reads and a graph with proteins and no
    genes is a real state — the resolver returning no usable cross-reference for any accession.

    **The class is machine-checked since 2026-08-10, and the sentence above needed one word.** It
    said *the only one of the five queries without it*, which was true of the four that carry an
    `Absence` and silent about the rest: `__all__` exports **nine** queries, and five —
    `site_keying`, `site_ids`, `analysis_ids`, `unprovenanced`, `gene_absence_census` — sat outside
    any statement of the property. `tests/test_query_absence_coverage.py` now runs **all nine**
    against a DDL-only graph and requires the classified answer, keyed off `__all__` so an added
    export is unclassified rather than exempt. What it was written from is that none of the nine is
    silent today: the two censuses key every category at zero and the two enumerations return `[]`,
    which for an enumeration has one reading. So the guard freezes a property rather than repairing
    one — and the *syntactic* version, *every query consults a table before it matches*, stays
    rejected on the grounds this paragraph gives.
    """
    if "Gene" not in _node_tables(conn) or _count(conn, "Gene") == 0:
        return [
            GeneSymbolAnswer(
                symbol=symbol,
                present=False,
                gene_id=None,
                protein_ids=(),
                absence=Absence.NOT_STORED,
                detail=(
                    "the Gene table is empty, so no symbol could have been found and no absence "
                    "is a finding about this symbol. Not UNATTRIBUTABLE: there is nothing stored "
                    "for a key to fail to reach. A rebuild that ingested no deposit leaves the "
                    "graph in this state and reports it (OPERATIONS.md §5)"
                ),
            )
            for symbol in symbols
        ]
    answers: list[GeneSymbolAnswer] = []
    for symbol in symbols:
        found = _rows(
            conn,
            "MATCH (g:Gene) WHERE g.symbol = $s "
            "OPTIONAL MATCH (g)-[:ENCODES]->(p:Protein) RETURN g.id, p.id",
            s=symbol,
        )
        if found:
            answers.append(
                GeneSymbolAnswer(
                    symbol=symbol,
                    present=True,
                    gene_id=str(found[0][0]),
                    protein_ids=tuple(str(r[1]) for r in found if r[1] is not None),
                    absence=None,
                    detail="",
                )
            )
            continue
        answers.append(
            GeneSymbolAnswer(
                symbol=symbol,
                present=False,
                gene_id=None,
                protein_ids=(),
                absence=Absence.UNATTRIBUTABLE,
                detail=(
                    "no Gene carries this symbol. Which of §4's gene_absence states applies cannot "
                    "be determined from a symbol alone: the states are per-Protein and the route "
                    "from a symbol to a protein runs through the Gene node that is absent. Pass an "
                    "accession to gene_absence_census for the attributed form. Note that a symbol "
                    "HGNC has renamed is absent under its old spelling while the gene is present "
                    "under the new one — DDX58 against RIGI, hgnc:HGNC:19102"
                ),
            )
        )
    return answers


def gene_absence_census(conn: kuzu.Connection) -> dict[str, int]:
    """§4's `gene_absence` across every `Protein`, with `None` keyed as `"encoded"`.

    The attributed form `gene_symbols` cannot give, and the whole-graph counterpart of it. Keys are
    the enum plus `encoded`; a state with no members is reported as 0 rather than omitted, because
    an omitted key and a zero read differently and only one of them is a measurement.
    """
    counts = {state: 0 for state in schema.GENE_ABSENCE}
    counts["encoded"] = 0
    for value, n in _rows(conn, "MATCH (p:Protein) RETURN p.gene_absence, count(p)"):
        counts["encoded" if value is None else str(value)] = int(n)
    return counts
