"""The five queries. See the package docstring for the three rules they are built to.

Every function takes an open `kuzu.Connection` rather than opening one, for `resolve/nodes.py`'s
reason: injected, so a test drives a graph it built itself and nothing here reaches for a path.
"""

from __future__ import annotations

import enum
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import kuzu

from bzk.ontology import schema

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


@dataclass(frozen=True)
class DifferentialRow:
    """One `DifferentialResult`, with everything §8 requires to travel beside its numbers.

    `quantity`, `test` and `fdr_method` come from the `Analysis` (I16 puts them there, not on the
    result), and `candidate_proteins` plus `assignment_confidence` come from the observation and
    its `ProteinAssignment` (I14's display half). `protein_adjusted` is I4's declared state.

    **`substantially_imputed` is `None`, and that is a finding rather than an omission.** §8 I15
    says a result *"whose underlying values are more than half imputed"* is flagged in every view
    and export — but the `DifferentialResult` DDL has no such column, and the graph holds the
    numerator (`SiteObservation.n_imputed`) without the denominator, which lives per-sample in
    `quant.duckdb`. So the flag is not derivable from the graph alone. `n_imputed` is carried
    instead of a guessed boolean, because a `False` here would assert the clause is satisfied.
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
    n_imputed: int | None
    #: Always `None` — see the class docstring. Kept in the shape so a caller reads the absence
    #: rather than not finding the field and assuming the flag does not apply.
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
    defined on a `DifferentialResult`, so it is not derivable here and is not offered — a caller
    wanting it reads `DifferentialRow.substantially_imputed`.
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
      conflates everywhere else here. Measured 2026-08-09 the real graph gives
      `{'Dataset': (0, 1), 'SiteObservation': (0, 2029), 'DifferentialResult': (0, 0)}` — and the
      third of those is 0 of 0, which the bare count would have shown as a pass.
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


# ── Q1: the differential table for an Analysis ──────────────────────────────────────────────────


def differential_table(
    conn: kuzu.Connection, analysis_id: str
) -> tuple[list[DifferentialRow], Absence | None]:
    """Site, protein, gene symbol, quantity, statistic — for one `Analysis`.

    Returns `(rows, absence)`. **`absence` is the point of the signature.** An empty list means one
    of two opposite things, and measured on 2026-08-09 the real graph is in the second: there are
    **0** `DifferentialResult` nodes, so an empty table means *no results are stored*, not *no site
    was significant*. Returning a bare list would make those indistinguishable at the call site,
    which is the failure this whole layer is shaped around.
    """
    if "DifferentialResult" not in _node_tables(conn) or _count(conn, "DifferentialResult") == 0:
        return [], Absence.NOT_STORED

    analysis = _rows(
        conn,
        "MATCH (a:Analysis) WHERE a.id = $id RETURN a.quantity, a.test, a.fdr_method",
        id=analysis_id,
    )
    quantity, test, fdr = analysis[0] if analysis else (None, None, None)

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
        "RETURN r.id, r.log2fc, r.p_value, r.adj_p_value, r.protein_adjusted, "
        "r.adjustment_method, o.id, o.candidate_proteins, o.n_imputed, s.id, pa.confidence "
        "ORDER BY r.id",
        id=analysis_id,
    ):
        (rid, log2fc, p_value, adj_p, adjusted, method, oid, candidates, n_imp, sid, conf) = record
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
                n_imputed=n_imp,
                substantially_imputed=None,
                candidate_proteins=candidates,
                assignment_confidence=str(conf) if conf else None,
                provenance=_provenance(conn, "DifferentialResult", str(rid)),
            )
        )
    return rows, (None if rows else Absence.NONE_FOUND)


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
    caller asked about. Measured 2026-08-09, the real graph has **0** `Imputation` nodes, so
    `absence` distinguishes *this analysis has none* from *none are stored at all*.
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
