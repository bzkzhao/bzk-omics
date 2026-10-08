"""A site-grain differential run as an ADR-0019 change-set.

One `Analysis`, one `Imputation`, one `Contrast`, and one `DifferentialResult` per tested
observation. Nothing here computes anything: the caller passes the statistics it already has.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bzk.curation.loader import ContrastArms
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.keys import evidence_id

Node = dict[str, Any]
Edge = dict[str, Any]


@dataclass(frozen=True)
class DeclaredRun:
    """Everything I16 requires an `Analysis` to record, stated once by the caller.

    **`parameters_observed` is fixed `True` here and is not a parameter.** I19's `false` means the
    analysis ran outside the platform and its parameters are *as stated* rather than *as executed*;
    everything this module can emit was executed by the platform. Accepting the flag as an argument
    would let a caller claim the weaker standing for a run the platform performed, which is I19 read
    backwards — and it would let the stronger one be claimed by a caller that had not executed
    anything, which is worse. The obligation the `True` carries is on the caller instead: the values
    below must be **the ones the computation used**, not a second transcription of them, which is
    why they are passed rather than re-declared here.
    """

    quantity: str
    test: str
    fdr_method: str
    localization_threshold: float | None
    filters_applied: tuple[str, ...]
    imputation: dict[str, Any]
    parameters_json: str | None = None
    #: Free-text, excluded from identity (§3). Never load-bearing.
    label: str | None = None


@dataclass(frozen=True)
class SiteResult:
    """One tested observation's statistics. `observation_id` is the `SiteObservation` it measures.

    The four counts are ADR-0036 D8's: how many values entered the test in each arm, and how many of
    those were generated. Required, because every run this module emits has
    `parameters_observed = True` and so its mask is in hand (§6.5).
    """

    observation_id: str
    log2fc: float
    p_value: float
    adj_p_value: float
    n_values_numerator: int
    n_values_denominator: int
    n_imputed_numerator: int
    n_imputed_denominator: int


@dataclass(frozen=True)
class ChangeSet:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


def site_change_set(
    run: DeclaredRun,
    results: list[SiteResult],
    *,
    dataset: Node,
    contrast: Node,
    arms: ContrastArms,
    attached_nodes: list[Node],
    attached_edges: list[Edge],
) -> ChangeSet:
    """The change-set for one site-grain differential run.

    `dataset`, `attached_nodes` and `attached_edges` are the slice of the ingestion change-set the
    results attach to, passed in **whole, as the adapter minted them**, and not reconstructed here. Two reasons, and the second is the one that forced it. `store.write_change_set`
    resolves an edge's endpoint labels from the change-set's **own** nodes, so an edge to an
    observation the batch does not carry raises rather than matching the stored one — ADR-0019's
    self-containment, enforced at the write path. And once the observation is in the batch, I3
    refuses it without its `ModifierAssignment`, so those come too. Re-keying either here would put
    a second source of truth for identity beside the adapter's; taking the nodes it already built
    cannot disagree with it.

    `contrast` is the `Contrast` the curation loader minted (`LoadedCuration.contrast`), passed
    whole and staged as a referent, exactly as `dataset` is. **This function mints no `Contrast`**
    (ADR-0029 E): until 2026-10-03 it minted one from `DeclaredRun.numerator` / `.denominator`,
    which the PXD018299 caller filled with column tokens (`KO_IFN`, `WT_IFN`) while the curation
    record declares `'USP18-/- + IFN'` / `'WT + IFN'` — two nodes for one comparison once the loader
    materialised its own. One minting site cannot disagree with itself.

    `arms` are that contrast's arms as the loader resolved them (`LoadedCuration.contrast_arms`),
    with the kind it derived. **A kind other than `condition` is refused here** (ADR-0038 D7): a
    site-grain result has no display label in either IP kind. The refusal sits at the producer and
    not in an invariant because kind is not visible at write time — the `Contrast` above is staged
    as a bare referent, without the arm samples or the anchor's `modality` it is derived from.

    `parameters_observed` is `True` and `kind` is `'processing'`: §5's enum offers
    `'processing' | 'curation' | 'external'` and there is no fourth value for *the platform ran it*
    — `'external'` is the one that means it did not.

    Each result carries its `SiteResult`'s per-arm counts (ADR-0036 D8), which `True` makes
    obligatory: I15 refuses a platform-run result without them (§6.5).
    """
    if arms.kind != "condition":
        raise ValueError(
            f"site_change_set writes site-grain results only for a 'condition' contrast; got kind "
            f"{arms.kind!r}, which no site-grain result may occupy (ADR-0038 D7). Refused here "
            "rather than by an invariant because kind is not visible at write time: the Contrast "
            "is staged as a bare referent, without the arms and modality it is derived from"
        )
    nodes: list[Node] = [dataset, *attached_nodes]
    edges: list[Edge] = list(attached_edges)

    analysis: Node = {
        "kind": "processing",
        # I19. True is the standing a platform-produced result has, and it is a claim about *this*
        # run: the fields beside it are the values the computation used, handed over by the caller.
        "parameters_observed": True,
        "quantity": run.quantity,
        "test": run.test,
        "fdr_method": run.fdr_method,
        "localization_threshold": run.localization_threshold,
        "filters_applied": sorted(run.filters_applied),
        "parameters_json": run.parameters_json,
        # Determined by `kind`: `basis` and `confidence` are curation's fields (§3, §5.3).
        "basis": None,
        "confidence": None,
        # Determined by `kind` the other way: an external tool is what did not run this.
        "external_tool": None,
        "external_version": None,
    }
    if run.label is not None:
        analysis["label"] = run.label
    imputation = dict(run.imputation)
    analysis_id = evidence_id(
        "Analysis", analysis, {"Dataset": str(dataset["id"])}, {"Imputation": [imputation]}
    )
    nodes.append({NODE_TYPE_KEY: "Analysis", "id": analysis_id, **analysis})
    edges.append({"type": "USED", "from": analysis_id, "to": str(dataset["id"])})

    imputation_id = evidence_id("Imputation", imputation, {"Analysis": analysis_id})
    nodes.append({NODE_TYPE_KEY: "Imputation", "id": imputation_id, **imputation})
    edges.append({"type": "IMPUTATION_FOR", "from": imputation_id, "to": analysis_id})

    if contrast.get(NODE_TYPE_KEY) != "Contrast" or not contrast.get("id"):
        raise ValueError(
            "site_change_set needs the curation loader's Contrast node (LoadedCuration.contrast), "
            f"got {contrast.get(NODE_TYPE_KEY)!r} with id {contrast.get('id')!r}"
        )
    contrast_id = str(contrast["id"])
    nodes.append(dict(contrast))

    for result in results:
        # I4. Site-grain and uncorrected by construction on this route: correcting against parent
        # protein abundance needs a matched proteome result to point `ADJUSTED_BY` at, and none is
        # ingested. `not_applied` is labelled *stoichiometry-uncorrected* in every view and export;
        # `adjustment_method` is null, which §3 classifies as determined by `protein_adjusted`.
        row: Node = {
            "log2fc": result.log2fc,
            "p_value": result.p_value,
            "adj_p_value": result.adj_p_value,
            "protein_adjusted": "not_applied",
            "adjustment_method": None,
            "n_values_numerator": result.n_values_numerator,
            "n_values_denominator": result.n_values_denominator,
            "n_imputed_numerator": result.n_imputed_numerator,
            "n_imputed_denominator": result.n_imputed_denominator,
        }
        # The three numbers are **excluded** from identity (§3): a result is identified by which
        # analysis, which observation, which contrast and which correction state, so re-running the
        # same analysis over the same observation rewrites the row rather than forking it.
        result_id = evidence_id(
            "DifferentialResult",
            row,
            {
                "Analysis": analysis_id,
                "SiteObservation": result.observation_id,
                "Contrast": contrast_id,
            },
        )
        nodes.append({NODE_TYPE_KEY: "DifferentialResult", "id": result_id, **row})
        edges.append({"type": "WAS_GENERATED_BY", "from": result_id, "to": analysis_id})
        edges.append({"type": "RESULT_FOR_SITE", "from": result_id, "to": result.observation_id})
        edges.append({"type": "RESULT_IN_CONTRAST", "from": result_id, "to": contrast_id})

    # `WAS_DERIVED_FROM` is deliberately not emitted. §7 declares it over the same endpoints as
    # `RESULT_FOR_SITE` and saying the same thing; §11 Q11 proposes projecting §7's duplicates at
    # export rather than storing them, and `perseus.py` already emits only the domain edge. Writing
    # both would create the second home that question exists to close.
    return ChangeSet(nodes=nodes, edges=edges)
