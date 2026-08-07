"""Load a `data/curation/*.json` record into a change-set (`HANDOFF.md` §3 item 3, `ONTOLOGY.md`
§5.3).

The mapping from raw file to experimental condition is an *assertion about an experiment this
laboratory did not perform*, and it is frequently wrong. §5.3 therefore models it as an activity
rather than configuration: this module emits `Project → Experiment → Sample` plus the `Dataset` and
a curation `Analysis`, with every `Sample` carrying `SAMPLE_GENERATED_BY` to that `Analysis`. A
`Sample` reaching no curation activity is permanently and correctly flagged `unprovenanced` (I5).

**Refusing is the principal behaviour, not a guard bolted on.** Under ADR-0021 a node cannot be
minted without its identifying values, and the one real record on disk is still missing two of them
(`project.title`, `experiment.title`). So the loader collects everything the curator owes and raises
once, by exact field name. Two independent layers find them:

1. the record's top-level **`pending`** object — dotted paths to values the curator has explicitly
   marked, so the refusal is by name rather than a late failure on a null, and the curator's note
   travels with it;
2. a **completeness check against `schema.IDENTITY` and `schema.ABSENCE`** — every identifying field
   of every node this module mints must be present unless §3 classifies its absence `determined` or
   `curated`. This layer does not consult the markers, which is the point: a curator who nulls a
   field without recording it must not get a null into an identifying position.

Layer 2 is what makes the marker a convenience rather than the guard. It is also what surfaced a
third blocker the markers said nothing about, since closed: `Sample.timepoint_h` is identifying and
null on the six unstimulated PXD018299 samples, and §3 classified no such absence. The fix was not
to reclassify the null but to define the column — §5 gave `timepoint_h` no comment, so "unknown"
and "inapplicable" were indistinguishable. It is hours *since treatment*, so an untreated arm has
none, and §3 now classifies the absence as determined by `treatment` (ONTOLOGY v1.17).

**Nothing here derives a missing value.** Not a title from an accession, not a DOI from the prose in
`rationale`, not a tidied sample name from a column header. Inventing one is forbidden (`CLAUDE.md`:
real external identifiers only) and, because all three of these are identifying or feed something
that is, an invented value silently forks an id.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bzk.adapters.base import Edge, Node, SampleMapping
from bzk.ontology import invariants, schema
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.keys import evidence_id

# Record key -> the node field it supplies, for the flat blocks. Sample fields come from `mapping`
# and are named identically in both, so they need no table.
_DATASET_FROM_RECORD = {
    "acquisition_mode": "acquisition_mode",
    "instrument": "instrument",
    "search_engine": "search_engine",
    "search_engine_version": "search_engine_version",
}

# `Sample` columns the loader reads out of a `mapping` entry. `label` is not among them: it is not
# a curator-supplied field but the mapping key itself, set in `load`. `model_system` is read even
# though no record supplies it, so that a record which does supply it is not silently dropped.
_SAMPLE_FIELDS = (
    "source_type",
    "cell_line",
    "model_system",
    "organism_taxid",
    "genotype",
    "treatment",
    "timepoint_h",
    "replicate",
    "replicate_type",
)


class CurationError(ValueError):
    """A curation record cannot be loaded. Never downgraded to a warning (`CLAUDE.md`)."""


@dataclass(frozen=True)
class Owed:
    """One identifying value the curator still owes, named where they would edit it."""

    # The record path, as the curator would type it: 'experiment.title', or
    # "mapping['Intensity CTRL_1'].timepoint_h" for a value inside the sample mapping.
    path: str
    node: str  # the node type that cannot be keyed without it
    field: str  # the identifying column
    why: str

    def __str__(self) -> str:
        return f"{self.path} ({self.node}.{self.field}) — {self.why}"


class CurationIncomplete(CurationError):
    """Identifying values are absent and unclassified, so the nodes cannot be keyed (ADR-0021).

    Carries every outstanding item rather than the first: a curator fixing one field should not have
    to re-run to discover the next.
    """

    def __init__(self, owed: Sequence[Owed]) -> None:
        self.owed: tuple[Owed, ...] = tuple(owed)
        self.paths: tuple[str, ...] = tuple(item.path for item in self.owed)
        listing = "\n  ".join(str(item) for item in self.owed)
        super().__init__(
            f"{len(self.owed)} identifying value(s) are missing, so no id can be minted "
            f"(ADR-0021). Supply them in the record — the loader will not derive one:\n  {listing}"
        )


class CurationInvalid(CurationError):
    """A value is present but outside the vocabulary `ONTOLOGY.md` closes."""


@dataclass(frozen=True)
class LoadedCuration:
    """One curation record as a change-set, plus the ids an adapter needs to attach to it."""

    nodes: list[Node]
    edges: list[Edge]
    project_id: str
    experiment_id: str
    dataset_id: str
    analysis_id: str
    sample_ids: dict[str, str]  # record mapping key (verbatim) -> Sample id
    contrasts: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def sample_mapping(self) -> SampleMapping:
        """The handover to an `ObservationAdapter` (`ARCHITECTURE.md` §3).

        The adapter consumes this, never a configuration file. Each descriptor carries the minted
        `Sample` id and the record's mapping key, which is the column header the curation was
        written against — the adapter needs both to line a quantitative column up with a sample.
        """
        by_id = {node["id"]: node for node in self.nodes}
        samples = [
            {**by_id[sample_id], "mapping_key": key} for key, sample_id in self.sample_ids.items()
        ]
        return SampleMapping(curation_analysis_id=self.analysis_id, samples=samples)


def _node(label: str, node_id: str, props: Mapping[str, Any]) -> Node:
    """Assemble one change-set node.

    No column check here. This module used to verify `props` against the DDL, because a typo'd
    field would otherwise be dropped silently and change no id — that reasoning still holds, but
    `bzk/ontology/store.py` now enforces it for *every* producer on the write path, so keeping a
    second copy would be two homes for one rule. The trade is that a bad column now surfaces at the
    store rather than at the loader; it is exercised in the suite either way, since
    `tests/test_rebuild.py` writes this loader's output through `store.write_change_set`.
    """
    return {NODE_TYPE_KEY: label, "id": node_id, **props}


def _check_identifying(
    label: str, props: Mapping[str, Any], paths: Mapping[str, str], owed: list[Owed]
) -> None:
    """Layer 2 — every identifying field present, or its absence classified in §3 (ADR-0021).

    Reads `schema.IDENTITY` and `schema.ABSENCE` rather than a list local to this module, so a
    field becoming identifying in `ONTOLOGY.md` §3 tightens the loader without an edit here.
    """
    for name in schema.IDENTITY[label].fields:
        if props.get(name) is not None:
            continue
        if (label, name) in schema.ABSENCE:
            continue
        owed.append(
            Owed(
                path=paths.get(name, f"{label.lower()}.{name}"),
                node=label,
                field=name,
                why=(
                    f"identifying on {label} (ONTOLOGY.md §3) and §3 classifies no absence for it, "
                    "so the null is contingent — it describes when the record was written, not the "
                    "entity (ADR-0021). Supply the value, or classify the absence in §3 with what "
                    "determines it."
                ),
            )
        )


def _pending_owed(record: Mapping[str, Any]) -> list[Owed]:
    """Layer 1 — the record's own markers, which carry the consequence the curator needs to read."""
    pending = record.get("pending") or {}
    owed = []
    for path in sorted(pending):
        node, _, field_name = path.partition(".")
        owed.append(
            Owed(
                path=path, node=node.capitalize(), field=field_name or path, why=str(pending[path])
            )
        )
    return owed


def _curation_analysis(record: Mapping[str, Any]) -> dict[str, Any]:
    """The §5.3 curation `Analysis`, with the loader defaults settled in `HANDOFF.md` §8."""
    basis = record.get("basis")
    confidence = record.get("confidence")
    if basis not in schema.CURATION_BASIS:
        raise CurationInvalid(
            f"basis={basis!r} is not in the closed §5.3 enum {sorted(schema.CURATION_BASIS)}. "
            "It is identifying on Analysis (§3), so a misspelling forks an id rather than failing."
        )
    expected = schema.CURATION_BASIS[basis]
    if confidence != expected:
        raise CurationInvalid(
            f"basis={basis!r} carries confidence {expected!r} in ONTOLOGY.md §5.3, but the record "
            f"states {confidence!r}. A design read from a paper is `inferred`; only SDRF or the "
            "submitters themselves make it `authoritative`."
        )
    return {
        "kind": "curation",
        "basis": basis,
        "confidence": confidence,
        "rationale": record.get("rationale"),
        # `parameters_observed = true` is the ONE case that defaults true (HANDOFF §8): the curation
        # act is performed *for* the platform and this JSON record **is** the artifact, so the
        # platform observes the whole of what the analysis consists of. An analysis_*.json record
        # transcribing a notebook run defaults FALSE — that split is platform-executed vs not.
        "parameters_observed": True,
        # A curation analysis consumes no quantity (I16 skips it; §3 classifies the absence), and
        # applied no filters — which is a value, not an absence, so an empty list and not a null.
        # §3 does not classify `filters_applied`'s absence, so a null here would be refused.
        "quantity": None,
        "filters_applied": [],
    }


def load(record: Mapping[str, Any]) -> LoadedCuration:
    """Build the change-set, or raise `CurationIncomplete` / `CurationInvalid`.

    Vocabulary is checked before completeness so a misspelled `basis` is reported as the wrong value
    it is, rather than surfacing as a missing one.
    """
    analysis_props = _curation_analysis(record)

    project = {"title": (record.get("project") or {}).get("title")}
    experiment_block = record.get("experiment") or {}
    experiment = {
        "title": experiment_block.get("title"),
        "modality": experiment_block.get("modality"),
        "organism_taxid": experiment_block.get("organism_taxid"),
    }
    dataset = {
        # `label` is writable again since the discriminator moved to `__label__` (ADR-0019,
        # 2026-08-07). It carries the recorded filename, not a composed sentence: the loader emits
        # values the record holds and does not write display prose of its own.
        "label": record.get("file"),
        "content_hash": record.get("content_hash"),
        "external_accession": record.get("accession") or record.get("dataset"),
        **{col: record.get(key) for key, col in _DATASET_FROM_RECORD.items()},
    }
    mapping: dict[str, dict[str, Any]] = dict(record.get("mapping") or {})
    samples = {
        # `label` is the mapping key verbatim — the column header this curation was written
        # against, un-normalised. Tidying `KO_1_181212063719` is the adapter's job (`ROADMAP.md`
        # § Measured findings); doing it here would add information the record does not carry.
        # Non-identifying (§3), so it moves no id.
        key: {"label": key, **{name: entry.get(name) for name in _SAMPLE_FIELDS}}
        for key, entry in mapping.items()
    }

    # Both layers run over everything before anything is raised, so one pass tells the curator the
    # whole of what is outstanding. Markers first: their notes are richer than layer 2's generic
    # reason, and de-duplicating by path keeps a marked field from being reported twice.
    owed = _pending_owed(record)
    marked = {item.path for item in owed}
    unmarked: list[Owed] = []
    _check_identifying("Project", project, {"title": "project.title"}, unmarked)
    _check_identifying(
        "Experiment",
        experiment,
        {name: f"experiment.{name}" for name in experiment},
        unmarked,
    )
    _check_identifying("Dataset", dataset, {"content_hash": "content_hash"}, unmarked)
    _check_identifying("Analysis", analysis_props, {}, unmarked)
    for key, props in samples.items():
        _check_identifying(
            "Sample", props, {name: f"mapping[{key!r}].{name}" for name in _SAMPLE_FIELDS}, unmarked
        )
    owed += [item for item in unmarked if item.path not in marked]
    if owed:
        raise CurationIncomplete(owed)

    project_id = evidence_id("Project", project)
    experiment_id = evidence_id("Experiment", experiment, {"Project": project_id})
    dataset_id = evidence_id("Dataset", dataset)
    analysis_id = evidence_id("Analysis", analysis_props, {"Dataset": dataset_id})
    sample_ids = {
        key: evidence_id("Sample", props, {"Experiment": experiment_id})
        for key, props in samples.items()
    }

    nodes: list[Node] = [
        _node("Project", project_id, project),
        _node("Experiment", experiment_id, experiment),
        _node("Dataset", dataset_id, dataset),
        _node("Analysis", analysis_id, analysis_props),
    ]
    nodes += [_node("Sample", sample_ids[key], props) for key, props in samples.items()]

    edges: list[Edge] = [
        {"type": "CONTAINS", "from": project_id, "to": experiment_id},
        {"type": "USED", "from": analysis_id, "to": dataset_id},
    ]
    for sample_id in sample_ids.values():
        edges.append({"type": "PERFORMED_ON", "from": experiment_id, "to": sample_id})
        edges.append({"type": "PRODUCED", "from": sample_id, "to": dataset_id})
        edges.append({"type": "SAMPLE_GENERATED_BY", "from": sample_id, "to": analysis_id})

    # The loader's output is held to the same contract as an adapter's (ADR-0019). Running it here
    # rather than at the call site means a record can never be half-written into the graph.
    invariants.validate(nodes, edges)

    return LoadedCuration(
        nodes=nodes,
        edges=edges,
        project_id=project_id,
        experiment_id=experiment_id,
        dataset_id=dataset_id,
        analysis_id=analysis_id,
        sample_ids=sample_ids,
        # Read and handed on, not materialised: `Contrast`'s reference-vs-evidence placement is
        # unsettled (§11 Q1) and the adapter builds the contrast inline (HANDOFF §8).
        contrasts=tuple(record.get("contrasts_of_interest") or ()),
    )


def load_path(path: Path) -> LoadedCuration:
    """Load one record from disk. The filename is not read for meaning — the record states its own
    accession and digest, and a name is not an identifier."""
    return load(json.loads(path.read_text()))
