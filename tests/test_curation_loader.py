"""The curation loader (`HANDOFF.md` §3 item 3, `ONTOLOGY.md` §5.3).

Written before the loader and failing first, per `CLAUDE.md` § Working style. The refusal path is
the substance here, not a guard bolted onto a working loader: under ADR-0021 a node cannot be minted
without its identifying values, so *refusing* is the loader's principal behaviour on the one real
record it has, and the success path is exercised against a fixture marked synthetic.

Two independent layers are tested separately on purpose:

1. the **`pending` marker** — machine-detectable dotted paths, so the loader refuses by field name
   rather than failing late on a null (`HANDOFF.md` §8);
2. a **completeness check against `schema.IDENTITY` and `schema.ABSENCE`** — every identifying field
   of every node the loader mints must be present unless §3 classifies its absence.

Layer 2 is what stops the marker becoming the only guard. `test_refuses_an_unmarked_null` deletes
the `pending` block and asserts the loader still refuses, which is the case that matters: a record
whose curator forgot the marker must not load a null into an identifying position.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.adapters.base import SampleMapping
from bzk.curation.loader import (
    CurationIncomplete,
    CurationInvalid,
    LoadedCuration,
    load,
    load_path,
)
from bzk.ontology import invariants
from bzk.ontology.invariants import NODE_TYPE_KEY

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_RECORD = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"
SYNTHETIC = REPO_ROOT / "tests" / "fixtures" / "curation_synthetic_loadable.json"


def _record(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(path.read_text()))


@pytest.fixture
def synthetic() -> dict[str, Any]:
    return _record(SYNTHETIC)


@pytest.fixture
def loaded(synthetic: dict[str, Any]) -> LoadedCuration:
    return load(synthetic)


def _nodes(result: LoadedCuration, label: str) -> list[dict[str, Any]]:
    return [n for n in result.nodes if n[NODE_TYPE_KEY] == label]


# ── Refusal: the real record ────────────────────────────────────────────────────────────────────


def test_refuses_the_real_record_naming_the_pending_fields() -> None:
    """`data/curation/curation_PXD018299.json` is not loadable, and the loader says exactly why.

    When the curator supplies the titles this test fails, which is the point: the failure is the
    prompt to re-check what the record now yields rather than a silent change in behaviour.
    """
    with pytest.raises(CurationIncomplete) as exc:
        load_path(REAL_RECORD)
    assert "project.title" in exc.value.paths
    assert "experiment.title" in exc.value.paths
    message = str(exc.value)
    assert "project.title" in message and "experiment.title" in message


def test_refusal_carries_the_curators_note_not_just_the_field_name() -> None:
    """The `pending` notes state the consequence — re-minting every Sample id — at the point
    someone is editing. A refusal that dropped them would send the curator to the document."""
    with pytest.raises(CurationIncomplete) as exc:
        load_path(REAL_RECORD)
    assert "IDENTIFYING" in str(exc.value)


def test_the_unstimulated_arms_null_timepoint_is_accepted() -> None:
    """`Sample.timepoint_h` is null on the six non-IFN samples, and that is now a *determined*
    absence rather than a refusal.

    It was a refusal until 2026-08-07, and the fix was not to reclassify the null but to define the
    column: §5's DDL had a comment on every `Sample` field except this one, so "hours since
    treatment" and "hours in culture" were both readable and only the first makes the null
    inapplicable rather than unknown. With `timepoint_h` defined as hours since treatment, §3
    classifies the absence as determined by `treatment`, and these six key as they stand.

    Asserted as *what is not owed* rather than as a passing load, because the record is still
    incomplete for other reasons — the two titles. If the classification were dropped, this fails.
    """
    with pytest.raises(CurationIncomplete) as exc:
        load_path(REAL_RECORD)
    assert not [p for p in exc.value.paths if "timepoint_h" in p], exc.value.paths


def test_the_real_record_now_owes_only_the_two_titles() -> None:
    """The whole of what the curator still owes, in one assertion, so the count cannot drift.

    Eight items before the timepoint column was defined; two after. When the titles arrive this
    fails and the record loads — which is the prompt to check what it then yields.
    """
    with pytest.raises(CurationIncomplete) as exc:
        load_path(REAL_RECORD)
    assert set(exc.value.paths) == {"project.title", "experiment.title"}


def test_refuses_an_unmarked_null(synthetic: dict[str, Any]) -> None:
    """Layer 2 stands alone: strip every marker and the null is still refused.

    This is the case the marker cannot cover — a curator who nulls a field without recording it.
    """
    record = copy.deepcopy(synthetic)
    record["project"]["title"] = None
    assert "pending" not in record
    with pytest.raises(CurationIncomplete) as exc:
        load(record)
    assert "project.title" in exc.value.paths


def test_a_classified_absence_is_not_refused(loaded: LoadedCuration) -> None:
    """`Sample.model_system` is identifying and absent throughout — §3 classifies it `determined`
    (NULL in vitro, fixed by `source_type`), so it must load rather than refuse."""
    samples = _nodes(loaded, "Sample")
    assert samples
    assert all(s.get("model_system") is None for s in samples)


def test_every_owed_field_names_a_reason(loaded: LoadedCuration) -> None:
    """A refusal lists what is owed *and* why; `loaded` here only proves the happy path is clean."""
    with pytest.raises(CurationIncomplete) as exc:
        load_path(REAL_RECORD)
    assert all(item.why.strip() for item in exc.value.owed)


# ── Refusal: closed vocabularies (§5.3) ─────────────────────────────────────────────────────────


def test_unknown_basis_is_refused(synthetic: dict[str, Any]) -> None:
    """`Analysis.basis` is identifying, so a misspelling forks an id rather than failing (§5.3)."""
    record = copy.deepcopy(synthetic)
    record["basis"] = "publication_method"  # singular — a plausible typo
    with pytest.raises(CurationInvalid):
        load(record)


def test_basis_and_confidence_must_agree(synthetic: dict[str, Any]) -> None:
    """§5.3 states the confidence each basis carries. `publication_methods` is `inferred`;
    claiming `authoritative` for it asserts more than the basis supports."""
    record = copy.deepcopy(synthetic)
    record["confidence"] = "authoritative"
    with pytest.raises(CurationInvalid) as exc:
        load(record)
    assert "publication_methods" in str(exc.value)


# ── The change-set ──────────────────────────────────────────────────────────────────────────────


def test_change_set_satisfies_the_invariant_layer(loaded: LoadedCuration) -> None:
    """ADR-0019: what the loader emits must be a self-contained, valid change-set."""
    invariants.validate(loaded.nodes, loaded.edges)


def test_emits_one_project_one_experiment_one_dataset_and_a_sample_each(
    loaded: LoadedCuration,
) -> None:
    assert len(_nodes(loaded, "Project")) == 1
    assert len(_nodes(loaded, "Experiment")) == 1
    assert len(_nodes(loaded, "Dataset")) == 1
    assert len(_nodes(loaded, "Analysis")) == 1
    assert len(_nodes(loaded, "Sample")) == 4


def test_curation_analysis_defaults(loaded: LoadedCuration) -> None:
    """The loader defaults settled in `HANDOFF.md` §8, asserted rather than assumed.

    `parameters_observed = true` is the only case that defaults true: the curation act is performed
    *for* the platform and its JSON record **is** the artifact (I19). `quantity` is null because a
    curation analysis consumes none (I16 skips it, §3 classifies the absence), and
    `filters_applied` is an empty list rather than a null — a curation analysis applied no filters,
    which is a value, and §3 does not classify that field's absence.
    """
    analysis = _nodes(loaded, "Analysis")[0]
    assert analysis["kind"] == "curation"
    assert analysis["parameters_observed"] is True
    assert analysis["quantity"] is None
    assert analysis["filters_applied"] == []


def test_samples_are_linked_to_the_curation_analysis(loaded: LoadedCuration) -> None:
    """I5/I8: a Sample that reaches no curation activity is permanently `unprovenanced` (§5.3)."""
    generated = {e["to"] for e in loaded.edges if e["type"] == "SAMPLE_GENERATED_BY"}
    sources = {e["from"] for e in loaded.edges if e["type"] == "SAMPLE_GENERATED_BY"}
    assert generated == {loaded.analysis_id}
    assert sources == set(loaded.sample_ids.values())


def test_the_label_column_is_written_alongside_the_node_type(loaded: LoadedCuration) -> None:
    """`label` is a real DDL column on six node types *and* was the change-set's node-type key.

    While the discriminator owned that name the six columns were unwritable through the documented
    ingestion path — `{**props}` would have overwritten the node type — and the loader's first draft
    declined to emit them, which was a workaround, not a fix. The discriminator is now `__label__`
    (ADR-0019, 2026-08-07) and both live side by side. This asserts the pair, not just the column:
    a regression that reinstated the collision would silently satisfy a column-only check.

    `Sample.label` is the mapping key verbatim — the column header the curation was written
    against, un-normalised, because tidying `KO_1_181212063719` is the adapter's job.
    """
    for node in _nodes(loaded, "Sample"):
        assert node[NODE_TYPE_KEY] == "Sample"
        assert node["label"] in loaded.sample_ids
    assert {n["label"] for n in _nodes(loaded, "Sample")} == set(loaded.sample_ids)
    dataset = _nodes(loaded, "Dataset")[0]
    assert dataset[NODE_TYPE_KEY] == "Dataset"
    assert dataset["label"] == "SYNTHETIC_GlyGlyKSites.txt"


def test_ids_do_not_depend_on_the_label_column(
    loaded: LoadedCuration, synthetic: dict[str, Any]
) -> None:
    """`label` is excluded from identity on every node that has one (§3), so writing it moves no id.

    Worth pinning: the column became writable in the same change that started writing it, and if it
    had leaked into the identity tuple every `Sample` and `Dataset` id in the graph would shift the
    day an adapter set a different label for the same sample.
    """
    changed = copy.deepcopy(synthetic)
    changed["mapping"]["Intensity CTRL_1 renamed"] = changed["mapping"].pop("Intensity CTRL_1")
    assert set(load(changed).sample_ids.values()) == set(loaded.sample_ids.values())


def test_dataset_records_pipeline_metadata_without_branching(loaded: LoadedCuration) -> None:
    """I13 — `search_engine` and `acquisition_mode` are recorded data, carried not consulted."""
    dataset = _nodes(loaded, "Dataset")[0]
    assert dataset["search_engine"] == "maxquant"
    assert dataset["acquisition_mode"] == "dda"
    assert dataset["external_accession"] == "SYNTHETIC-0001"


def test_no_contrast_node_is_materialised(loaded: LoadedCuration) -> None:
    """`Contrast`'s reference-vs-evidence placement is unsettled (§11 Q1), so the loader reads the
    contrasts and hands them on rather than minting nodes (`HANDOFF.md` §8)."""
    assert _nodes(loaded, "Contrast") == []
    assert [c["id"] for c in loaded.contrasts] == ["treated_vs_untreated"]


def test_no_publication_node_is_invented(loaded: LoadedCuration) -> None:
    """The real record cites a DOI inside free-text `rationale` and nowhere structured.

    Regex-extracting it would be inventing an identifier from prose. The record format needs a
    structured `publication` field; until it has one, `CURATION_CITES` is not emitted.
    """
    assert _nodes(loaded, "Publication") == []
    assert not [e for e in loaded.edges if e["type"] == "CURATION_CITES"]


def test_no_person_node_without_a_name(loaded: LoadedCuration) -> None:
    """`curated_by` is null. `Person` keys on `orcid` + `name`, and only `orcid`'s absence is
    classified (`curated`, §3) — a nameless Person cannot be keyed, so none is emitted."""
    assert _nodes(loaded, "Person") == []


# ── Identity (ADR-0020, ADR-0021) ───────────────────────────────────────────────────────────────


def test_ids_are_deterministic(synthetic: dict[str, Any]) -> None:
    """Idempotent replay under I9: the same record yields the same ids, run to run."""
    first, second = load(synthetic), load(copy.deepcopy(synthetic))
    assert [n["id"] for n in first.nodes] == [n["id"] for n in second.nodes]


def test_changing_the_experiment_title_re_mints_every_sample_id(
    synthetic: dict[str, Any],
) -> None:
    """Exactly the consequence the `pending` note warns about, checked rather than asserted.

    `Sample` anchors on `Experiment` and `Experiment` on `Project`, so a title edit propagates down
    the whole chain. This is why the loader may not invent a title to get past the refusal.
    """
    before = load(synthetic)
    changed = copy.deepcopy(synthetic)
    changed["experiment"]["title"] = "A different title"
    after = load(changed)
    assert after.experiment_id != before.experiment_id
    assert set(after.sample_ids.values()).isdisjoint(before.sample_ids.values())
    assert after.project_id == before.project_id  # Project is above the change


def test_samples_differing_only_by_replicate_get_distinct_ids(loaded: LoadedCuration) -> None:
    assert len(set(loaded.sample_ids.values())) == len(loaded.sample_ids)


def test_dataset_id_follows_the_content_hash(
    loaded: LoadedCuration, synthetic: dict[str, Any]
) -> None:
    """`Dataset` keys on `content_hash` alone (§3), so re-curating the same bytes converges."""
    changed = copy.deepcopy(synthetic)
    changed["instrument"] = "Orbitrap Fusion Lumos"  # non-identifying
    assert load(changed).dataset_id == loaded.dataset_id


# ── The handover to the adapter ─────────────────────────────────────────────────────────────────


def test_sample_mapping_hands_the_adapter_the_analysis_id(loaded: LoadedCuration) -> None:
    """`ARCHITECTURE.md` §3: the adapter consumes a `SampleMapping` already written to the graph as
    a curation `Analysis`, never a configuration file."""
    mapping = loaded.sample_mapping()
    assert isinstance(mapping, SampleMapping)
    assert mapping.curation_analysis_id == loaded.analysis_id
    assert len(mapping.samples) == 4
    assert {s["id"] for s in mapping.samples} == set(loaded.sample_ids.values())
