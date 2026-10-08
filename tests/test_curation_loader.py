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
import re
from pathlib import Path
from typing import Any, cast

import pytest

from bzk.adapters.base import SampleMapping
from bzk.curation import loader
from bzk.curation.loader import (
    CurationIncomplete,
    CurationInvalid,
    LoadedCuration,
    load,
    load_path,
)
from bzk.ontology import invariants, schema
from bzk.ontology.invariants import NODE_TYPE_KEY

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_RECORD = REPO_ROOT / "data" / "curation" / "curation_PXD018299.json"
SYNTHETIC = REPO_ROOT / "tests" / "fixtures" / "curation_synthetic_loadable.json"
PENDING = REPO_ROOT / "tests" / "fixtures" / "curation_synthetic_pending.json"
MINTED_IDS = REPO_ROOT / "tests" / "fixtures" / "pxd018299_curation_ids.json"
CURATION_DIR = REPO_ROOT / "data" / "curation"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


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


def test_refuses_a_record_with_pending_markers_naming_the_fields() -> None:
    """The refusal path, on a synthetic record rather than on the real one.

    It ran against `data/curation/curation_PXD018299.json` until the titles arrived on 2026-08-07,
    at which point five tests here failed at once — correctly, as designed, but the lesson is that
    a guard resting on real data being *incomplete* stops guarding the moment the curator completes
    it. `curation_synthetic_pending.json` is the loadable fixture's twin, differing only in what is
    owed, so the machinery stays covered whatever the real records look like.
    """
    with pytest.raises(CurationIncomplete) as exc:
        load_path(PENDING)
    assert set(exc.value.paths) == {"project.title", "experiment.title"}
    message = str(exc.value)
    assert "project.title" in message and "experiment.title" in message


def test_refusal_carries_the_curators_note_not_just_the_field_name() -> None:
    """The `pending` notes state the consequence — re-minting every Sample id — at the point
    someone is editing. A refusal that dropped them would send the curator to the document."""
    with pytest.raises(CurationIncomplete) as exc:
        load_path(PENDING)
    assert "IDENTIFYING" in str(exc.value)


# ── The real record, which now loads ────────────────────────────────────────────────────────────


def test_the_real_record_loads() -> None:
    """`data/curation/curation_PXD018299.json` goes through the loader end to end.

    Every blocker `HANDOFF.md` §3 tracked is closed: the deposit digest, `source_type`, the
    timepoint column's definition, and finally the two titles. Twelve samples, one of each of the
    rest. If a future edit to the record breaks it, this fails rather than the graph quietly
    losing a dataset.
    """
    result = load_path(REAL_RECORD)
    assert len(_nodes(result, "Sample")) == 12
    assert len(_nodes(result, "Project")) == 1
    assert len(_nodes(result, "Experiment")) == 1
    assert len(_nodes(result, "Dataset")) == 1
    assert len(_nodes(result, "Analysis")) == 1
    assert len(set(result.sample_ids.values())) == 12
    invariants.validate(result.nodes, result.edges)


def test_the_unstimulated_arms_key_with_a_null_timepoint() -> None:
    """`Sample.timepoint_h` is null on the six non-IFN samples, and they key regardless.

    This refused until 2026-08-07, and the fix was not to reclassify the null but to define the
    column: §5's DDL had a comment on every `Sample` field except this one, so "hours since
    treatment" and "hours in culture" were both readable and only the first makes the null
    inapplicable rather than unknown. Now that the record loads, the claim can be asserted on the
    nodes themselves instead of on the absence of a refusal — six samples with `treatment = 'none'`
    carry a null timepoint and a minted id.
    """
    samples = _nodes(load_path(REAL_RECORD), "Sample")
    untreated = [s for s in samples if s["treatment"] == "none"]
    assert len(untreated) == 6
    assert all(s["timepoint_h"] is None and s["id"].startswith("bzk:") for s in untreated)
    treated = [s for s in samples if s["treatment"] != "none"]
    assert len(treated) == 6
    assert all(s["timepoint_h"] == 48 for s in treated)


def test_the_two_titles_are_identifying_on_the_real_record() -> None:
    """The consequence the removed `pending` notes warned about, kept as a check once they are gone.

    Both titles are identifying (§3), so editing either re-mints the `Experiment` and every
    `Sample` beneath it. The notes said so; the notes are now deleted, because the values are
    supplied. This asserts what they asserted, and does not depend on prose surviving.
    """
    before = load_path(REAL_RECORD)
    record = _record(REAL_RECORD)
    record["experiment"]["title"] = record["experiment"]["title"] + " (revised)"
    after = load(record)
    assert after.project_id == before.project_id
    assert after.experiment_id != before.experiment_id
    assert set(after.sample_ids.values()).isdisjoint(before.sample_ids.values())


# ── The minted ids, pinned (ADR-0020, ADR-0021) ─────────────────────────────────────────────────


def test_the_minted_ids_have_not_moved() -> None:
    """Every id the record mints, against the values it produced when it first loaded clean.

    Nothing else catches a silent re-mint. A change to `schema.IDENTITY`, to §3's identity table,
    or to the canonicalization in `keys.py` moves these ids with every other test still green —
    and after the first non-vacuous rebuild that is a graph that has quietly forgotten what it
    already knew, which is the failure ADR-0020's idempotent replay exists to prevent.

    This checks **change, not correctness**: the fixture was generated by the code it now guards.
    A failure means the identity model moved, which may well be right — then the fixture is
    regenerated and the move is explained. Regenerating it to turn a test green without that
    explanation is the one thing it must not be used for.

    The natural home is the first non-vacuous rebuild (`HANDOFF.md` §8, I9), which is weeks away.
    The ids are stable now, so they are pinned now — the same argument as
    `tests/fixtures/pxd018299_welch_baseline.json`.
    """
    expected = _record(MINTED_IDS)
    result = load_path(REAL_RECORD)
    assert result.project_id == expected["project"]
    assert result.experiment_id == expected["experiment"]
    assert result.dataset_id == expected["dataset"]
    assert result.analysis_id == expected["analysis"]
    assert result.sample_ids == expected["samples"]


def test_the_pinned_ids_are_well_formed_and_distinct() -> None:
    """A truncated or duplicated paste would make the pin above agree with nothing real.

    `bzk:` plus 32 hex characters is what `keys.DIGEST_HEX` produces (ADR-0020). Sixteen ids, all
    different: a copy-paste that repeated one would still satisfy the equality check above if the
    loader repeated it too, so distinctness is asserted against the count rather than inferred.
    """
    pinned = _record(MINTED_IDS)
    singletons = [pinned[k] for k in ("project", "experiment", "dataset", "analysis")]
    everything = [*singletons, *pinned["samples"].values()]
    assert len(everything) == 16
    assert len(set(everything)) == 16, "a pinned id is duplicated"
    for value in everything:
        assert re.fullmatch(r"bzk:[0-9a-f]{32}", value), value


def test_the_pinned_sample_keys_are_the_records_mapping_keys() -> None:
    """The pin is keyed by mapping key, so it also catches a sample silently disappearing.

    Comparing only the id *values* would pass if a mapping entry were dropped and another added
    with the same resulting id — unlikely, but the keys are free and they make the fixture readable.
    """
    assert set(_record(MINTED_IDS)["samples"]) == set(_record(REAL_RECORD)["mapping"])


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


def test_every_owed_field_names_a_reason() -> None:
    """A refusal lists what is owed *and* why — a bare field list sends the curator to the docs."""
    with pytest.raises(CurationIncomplete) as exc:
        load_path(PENDING)
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
    # The key is renamed wherever the record names it, its arm included (ADR-0038 D1).
    (contrast,) = changed["contrasts_of_interest"]
    contrast["denominator_samples"] = ["Intensity CTRL_1 renamed", "Intensity CTRL_2"]
    assert set(load(changed).sample_ids.values()) == set(loaded.sample_ids.values())


def test_dataset_records_pipeline_metadata_without_branching(loaded: LoadedCuration) -> None:
    """I13 — `search_engine` and `acquisition_mode` are recorded data, carried not consulted."""
    dataset = _nodes(loaded, "Dataset")[0]
    assert dataset["search_engine"] == "maxquant"
    assert dataset["acquisition_mode"] == "dda"
    assert dataset["external_accession"] == "SYNTHETIC-0001"


def test_contrasts_are_materialised_and_anchored_on_the_experiment(loaded: LoadedCuration) -> None:
    """ADR-0027 implied change 4 / ADR-0029 item 2, built 2026-10-03: the loader mints each declared
    contrast, anchored on this record's `Experiment`, and is the only place one is minted.

    Replaces `test_no_contrast_node_is_materialised`, which pinned the pre-ADR-0027 state."""
    from bzk.ontology.keys import evidence_id

    contrasts = _nodes(loaded, "Contrast")
    assert len(contrasts) == 1
    node = loaded.contrast("treated_vs_untreated")
    props = {"numerator": node["numerator"], "denominator": node["denominator"]}
    # Only that the id is not its no-anchor form: comparing it to `evidence_id(..., {Experiment})`
    # would recompute the loader's own expression (`test_tautology_sweep.py`'s instance shape). The
    # value itself is pinned for the real record in `pxd018299_curation_ids.json`.
    assert node["id"] != evidence_id("Contrast", props)
    assert {"type": "CONTRAST_IN_EXPERIMENT", "from": node["id"], "to": loaded.experiment_id} in (
        loaded.edges
    )
    assert [c["id"] for c in loaded.contrasts] == ["treated_vs_untreated"]


def test_an_undeclared_contrast_id_is_refused(loaded: LoadedCuration) -> None:
    from bzk.curation.loader import CurationError

    with pytest.raises(CurationError, match="treated_vs_untreated"):
        loaded.contrast("not_declared")


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


def test_structural_keys_do_not_collide_with_ddl_columns() -> None:
    """ADR-0019's reserved-namespace rule, applied to the second paired key space.

    The change-set format was guarded against the DDL the day the rule was written; the curation
    record's key space was left as a `HANDOFF.md` §8 note with a trigger of *"the second record
    format"*. That was a deferral for something already checkable — a structural key either is a
    column name or it is not — and the answer was, and is, that none collide. Prose that is true
    today is indistinguishable from prose that stopped being true, which is the whole argument for
    writing it down as an assertion.

    A collision would make that column unwritable through the loader, exactly as `label` made six
    node tables unwritable through the change-set.
    """
    columns = {c for t in schema.NODE_TABLES for c, _ in t.columns}
    clash = loader.STRUCTURAL_KEYS & columns
    assert not clash, (
        f"curation structural key(s) {sorted(clash)} are also DDL column names; the column cannot "
        "be written through the loader while the key means something else (ADR-0019)"
    )


def test_declared_structural_keys_are_all_really_used() -> None:
    """Non-vacuity, so the guard above cannot pass over a list that has drifted into fiction.

    Every declared key must appear in at least one record on disk — under `data/curation/` or in
    the synthetic twins under `tests/fixtures/`. `HANDOFF.md` §8: a guard that can be vacuous
    carries a non-vacuity assertion, which is what made the `pending`-marker guard detectable when
    the curator supplied the last two titles and emptied it.
    """
    seen: set[str] = set()

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                seen.add(key)
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    records = sorted(CURATION_DIR.glob("*.json")) + sorted(FIXTURES.glob("curation_*.json"))
    assert records, "no curation records found; this guard would pass over an empty loop"
    for path in records:
        walk(json.loads(path.read_text()))
    missing = loader.STRUCTURAL_KEYS - seen
    assert not missing, f"declared structural key(s) {sorted(missing)} appear in no record on disk"


# ── Unknown keys ────────────────────────────────────────────────────────────────────────────────


def test_an_unknown_top_level_key_is_refused_and_the_message_names_it(tmp_path: Path) -> None:
    """A record could state something the loader never reads, and it was accepted and dropped.

    Nothing in the module asked what else a record carried: keys are read by name — some from
    `STRUCTURAL_KEYS`, some from `_DATASET_FROM_RECORD`, the rest inline — and whatever was not
    read simply went nowhere. So a curator writing `quantity` into a curation record, which is a
    field this format has no place for, would see it load clean and the value vanish.

    Refused rather than warned, because a warning is what the module already effectively did.
    Built in `tmp_path` from a copy of the real record: a committed record that cannot load is a
    trap for the next reader.
    """
    record = _record(REAL_RECORD)
    record["quantity"] = "lfq"
    bad = tmp_path / "curation_bad.json"
    bad.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CurationInvalid) as exc:
        load_path(bad)
    assert "quantity" in str(exc.value)
    assert "recognises" in str(exc.value)


def test_every_record_and_fixture_on_disk_still_loads() -> None:
    """The check is *no key outside the known set*, never *exactly this set*.

    The six files do not agree on their key sets — `corrections` is in one real record and not the
    other three, `note` and `synthetic` are in the fixtures and no real record, `pending` is in one
    fixture alone, and `contrasts_of_interest` is in every file but
    `curation_PXD026748_shotgun.json` — so a check written as an equality would refuse at least four
    of the six: five distinct key sets over six files, and no key set is shared by more than two
    (`curation_PXD026748.json` and `curation_PXD055843.json`, still the only pair).

    **Re-measured 2026-09-19 with the shotgun record present**, rather than carried over: the pair
    is unchanged and the sixth file is a fifth key set of its own, because the shotgun arm names no
    contrast. A record that had matched an existing set would have left the sentence true while the
    reason for it moved.
    """
    records = sorted(CURATION_DIR.glob("curation_*.json")) + sorted(
        FIXTURES.glob("curation_synthetic_*.json")
    )
    assert len(records) == 6, f"expected the four records and the two twins, found {records}"
    for path in records:
        record = _record(path)
        unknown = set(record) - loader.KNOWN_KEYS
        assert not unknown, f"{path.name} carries {sorted(unknown)}, which the loader would refuse"


def test_a_key_inside_a_mapping_entry_is_still_accepted_and_dropped() -> None:
    """Recorded because it is measured, not because it is wanted — the level was left alone.

    The block comment above `STRUCTURAL_KEYS` rules that the *keys of* `mapping` are column headers
    and may be spelled anything. That is the outer level; it says nothing about the keys **inside**
    an entry, which the loader reads through `_SAMPLE_FIELDS` and drops whatever is left.

    A committed record exercises the hole: `data/curation/curation_PXD018299.json` carries a `note`
    in one of its mapping entries, and `_SAMPLE_FIELDS` does not name it. Closing this level would
    refuse a record on disk, and the narrowing that would have to distinguish a deliberate drop from
    an unrecognised key lives in `bzk/adapters/base.py`, which this turn does not touch.
    """
    entry_keys = {key for entry in _record(REAL_RECORD)["mapping"].values() for key in entry}
    assert "note" in entry_keys
    assert "note" not in loader._SAMPLE_FIELDS
    loaded_record = load_path(REAL_RECORD)
    for sample in _nodes(loaded_record, "Sample"):
        assert "note" not in sample


def test_the_inline_key_reads_are_all_declared() -> None:
    """`_INLINE_KEYS` against the module's own source — the mirror that replaces an accessor.

    The block comment above `STRUCTURAL_KEYS` said discovering an undeclared key would need the
    loader to read the record through one accessor. `KNOWN_KEYS` does it by set difference instead,
    and the difference between the two is real: an accessor makes declaring and reading one act, so
    they cannot drift, while two sets can. This is what keeps them in step, and it is the idiom this
    repository already uses for every other mirror — `schema.py` against §4–§7, `ABSENCE` against §3.

    Parsed rather than grepped, and only calls whose receiver is the name `record` are counted, so
    `entry.get(...)` and `experiment_block.get(...)` are not mistaken for record reads.
    """
    import ast

    source = (REPO_ROOT / "bzk" / "curation" / "loader.py").read_text()
    reads = {
        node.args[0].value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "record"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    assert reads, "no `record.get('...')` call was parsed, so the comparison below asserts nothing"
    undeclared = sorted(reads - loader._INLINE_KEYS)
    stale = sorted(loader._INLINE_KEYS - reads)
    assert not undeclared, f"`record.get` reads {undeclared}, which `_INLINE_KEYS` does not declare"
    assert not stale, f"`_INLINE_KEYS` declares {stale}, which no `record.get` call reads"


# ── ADR-0036 D2/D3: `Sample.role`, `bait` and `antibody` ────────────────────────────────────────

#: The control entry in `_ip_ms_record`; every other entry is an `ip` against ISG15.
_CONTROL = "Ratio mod/base WT_1"


def _ip_ms_record() -> dict[str, Any]:
    """The real PXD018299 record turned into a valid `ip_ms` one, here and not on disk.

    Every entry is an `ip` against ISG15 except `_CONTROL`, a `no_antibody_control` with no bait.
    The antibody is the clone ADR-0036 D2 quotes from the methods; nothing here is a claim that
    this dataset was an IP.

    **I22 shapes the contrasts too** (ADR-0038 D2): `KO_vs_WT_unstimulated`'s denominator is
    narrowed to `_CONTROL` alone, since `WT_1`–`WT_3` would otherwise mix `ip` with a control in
    one arm. So the record carries one contrast of each IP kind — `KO_IFN_vs_WT_IFN` IP against
    IP, `KO_vs_WT_unstimulated` IP against the bead control.
    """
    record = _record(REAL_RECORD)
    record["experiment"]["modality"] = "ip_ms"
    for key, entry in record["mapping"].items():
        if key == _CONTROL:
            entry["role"] = "no_antibody_control"
        else:
            entry.update(role="ip", bait="uniprot:P05161", antibody="Boston Biochem A-380")
    unstimulated = _contrast_entry(record, "KO_vs_WT_unstimulated")
    unstimulated["denominator_samples"] = [_CONTROL]
    return record


def _contrast_entry(record: dict[str, Any], handle: str) -> dict[str, Any]:
    (entry,) = (c for c in record["contrasts_of_interest"] if c["id"] == handle)
    return cast("dict[str, Any]", entry)


def _role_refusal(record: dict[str, Any]) -> str:
    with pytest.raises(CurationInvalid) as exc:
        load(record)
    message = str(exc.value)
    assert "ADR-0036 D2/D3" in message and "ONTOLOGY.md §3" in message
    return message


def test_a_valid_ip_ms_record_loads() -> None:
    loaded_record = load(_ip_ms_record())
    roles = sorted(sample["role"] for sample in _nodes(loaded_record, "Sample"))
    assert roles == ["ip"] * 11 + ["no_antibody_control"]


def test_R1_a_role_outside_the_closed_enum_is_refused() -> None:
    record = _ip_ms_record()
    entry = record["mapping"]["Ratio mod/base WT_2"]
    entry.update(role="lysate", bait=None, antibody=None)
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert "mapping['Ratio mod/base WT_2'].role = 'lysate' is not in the closed enum" in message


def test_R2_a_role_outside_ip_ms_is_refused() -> None:
    record = _record(REAL_RECORD)
    record["mapping"]["Ratio mod/base WT_2"].update(role="ip", bait="uniprot:P05161")
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert (
        "mapping['Ratio mod/base WT_2'].role = 'ip' but experiment.modality = 'digly_proteomics'"
        in message
    )


def test_R3_an_ip_ms_sample_without_a_role_is_refused() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base WT_2"].update(role=None, bait=None, antibody=None)
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert "mapping['Ratio mod/base WT_2'].role = None but experiment.modality = 'ip_ms'" in message


def test_R4_a_bait_on_a_control_is_refused() -> None:
    record = _ip_ms_record()
    record["mapping"][_CONTROL]["bait"] = "uniprot:P05161"
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert (
        f"mapping[{_CONTROL!r}].bait = 'uniprot:P05161' but role = 'no_antibody_control'" in message
    )


def test_R5_an_ip_without_a_bait_is_refused() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base WT_2"]["bait"] = None
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert "mapping['Ratio mod/base WT_2'].bait = None but role = 'ip'" in message


def test_R6_a_bait_that_is_not_a_uniprot_curie_is_refused() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base WT_2"]["bait"] = "P05161"
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert "mapping['Ratio mod/base WT_2'].bait = 'P05161' is not a uniprot: CURIE" in message


def test_R7_an_antibody_on_a_control_is_refused() -> None:
    record = _ip_ms_record()
    record["mapping"][_CONTROL]["antibody"] = "Boston Biochem A-380"
    message = _role_refusal(record)
    assert message.startswith("1 sample role fault(s)")
    assert f"mapping[{_CONTROL!r}].antibody = 'Boston Biochem A-380'" in message


def test_every_role_fault_is_named_in_one_message() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base WT_2"]["bait"] = None
    record["mapping"]["Ratio mod/base WT_3"]["bait"] = "P05161"
    message = _role_refusal(record)
    assert message.startswith("2 sample role fault(s)")
    assert "mapping['Ratio mod/base WT_2'].bait = None" in message
    assert "mapping['Ratio mod/base WT_3'].bait = 'P05161'" in message


def test_role_separates_two_samples_that_agree_on_every_other_field() -> None:
    """D2's purpose: a bead control and its IP for one condition are two samples, not one."""
    record = _ip_ms_record()
    ip = record["mapping"]["Ratio mod/base WT_2"]
    control = {k: v for k, v in ip.items() if k not in ("bait", "antibody")}
    control["role"] = "no_antibody_control"
    record["mapping"]["beads WT_2"] = control
    ids = load(record).sample_ids
    assert ids["Ratio mod/base WT_2"] != ids["beads WT_2"]


def test_the_committed_records_carry_no_role_bait_or_antibody() -> None:
    records = sorted(CURATION_DIR.glob("curation_*.json"))
    assert len(records) == 4, records
    for path in records:
        for sample in _nodes(load_path(path), "Sample"):
            assert (sample["role"], sample["bait"], sample["antibody"]) == (None, None, None), path


# ── ADR-0038 D1/D8: arms declared by mapping key and resolved at the loader ────────────────────


def _arm_refusal(record: dict[str, Any]) -> str:
    with pytest.raises(CurationInvalid) as exc:
        load(record)
    message = str(exc.value)
    assert "contrast arm fault(s) (ADR-0038 D1, D3, D8)" in message
    return message


def test_a_contrast_entry_key_outside_the_recognised_set_is_refused(
    synthetic: dict[str, Any],
) -> None:
    """ADR-0038 M3 measured the misspelling loading clean and being dropped. Refused first, so the
    typo is named rather than the arm it failed to supply."""
    (entry,) = synthetic["contrasts_of_interest"]
    entry["numerator_sampels"] = entry.pop("numerator_samples")
    with pytest.raises(CurationInvalid) as exc:
        load(synthetic)
    message = str(exc.value)
    assert message.startswith("1 contrast entry key fault(s): ")
    assert "contrasts_of_interest[0] carries ['numerator_sampels']" in message
    assert "numerator_samples is absent" not in message
    assert str(sorted(loader.CONTRAST_ENTRY_KEYS)) in message


def test_the_recognised_contrast_entry_keys_are_d1s() -> None:
    assert loader.CONTRAST_ENTRY_KEYS == {
        "id",
        "numerator",
        "denominator",
        "numerator_samples",
        "denominator_samples",
        "note",
    }


def test_an_absent_arm_is_refused_there_is_no_optional_form(synthetic: dict[str, Any]) -> None:
    del synthetic["contrasts_of_interest"][0]["denominator_samples"]
    message = _arm_refusal(synthetic)
    assert message.startswith("1 contrast arm fault(s)")
    assert "contrasts_of_interest[0].denominator_samples is absent" in message


def test_an_arm_that_is_not_a_list_of_keys_is_refused(synthetic: dict[str, Any]) -> None:
    synthetic["contrasts_of_interest"][0]["numerator_samples"] = "Intensity TREAT_1"
    message = _arm_refusal(synthetic)
    assert (
        "contrasts_of_interest[0].numerator_samples = 'Intensity TREAT_1' is not a list of "
        "mapping keys" in message
    )


def test_an_empty_arm_is_refused(synthetic: dict[str, Any]) -> None:
    synthetic["contrasts_of_interest"][0]["numerator_samples"] = []
    message = _arm_refusal(synthetic)
    assert "contrasts_of_interest[0].numerator_samples is empty" in message


def test_a_key_absent_from_mapping_is_refused_with_no_normalisation(
    synthetic: dict[str, Any],
) -> None:
    """Exact membership: the trailing space a spreadsheet export leaves names no sample."""
    synthetic["contrasts_of_interest"][0]["numerator_samples"] = [
        "Intensity TREAT_1 ",
        "Intensity TREAT_2",
    ]
    message = _arm_refusal(synthetic)
    assert (
        "contrasts_of_interest[0].numerator_samples names ['Intensity TREAT_1 '], which are not "
        "keys of mapping" in message
    )


def test_a_key_repeated_within_an_arm_is_refused(synthetic: dict[str, Any]) -> None:
    synthetic["contrasts_of_interest"][0]["numerator_samples"] = [
        "Intensity TREAT_1",
        "Intensity TREAT_1",
    ]
    message = _arm_refusal(synthetic)
    assert (
        "contrasts_of_interest[0].numerator_samples names ['Intensity TREAT_1'] more than once"
        in message
    )


def test_a_sample_in_both_arms_is_refused(synthetic: dict[str, Any]) -> None:
    synthetic["contrasts_of_interest"][0]["numerator_samples"].append("Intensity CTRL_1")
    message = _arm_refusal(synthetic)
    assert "contrasts_of_interest[0] puts ['Intensity CTRL_1'] in both arms" in message


def test_a_numerator_equal_to_its_denominator_is_refused(synthetic: dict[str, Any]) -> None:
    synthetic["contrasts_of_interest"][0]["denominator"] = "treated"
    message = _arm_refusal(synthetic)
    assert "contrasts_of_interest[0].numerator and .denominator are both 'treated'" in message


def test_two_entries_with_one_pair_are_refused(synthetic: dict[str, Any]) -> None:
    second = copy.deepcopy(synthetic["contrasts_of_interest"][0])
    second["id"] = "treated_vs_untreated_again"
    synthetic["contrasts_of_interest"].append(second)
    message = _arm_refusal(synthetic)
    assert (
        "contrasts_of_interest[1] repeats the (numerator, denominator) pair "
        "('treated', 'untreated') of contrasts_of_interest[0]" in message
    )


def test_every_arm_fault_is_named_in_one_message(synthetic: dict[str, Any]) -> None:
    (entry,) = synthetic["contrasts_of_interest"]
    entry["numerator_samples"] = []
    entry["denominator_samples"] = ["Intensity CTRL_9"]
    message = _arm_refusal(synthetic)
    assert message.startswith("2 contrast arm fault(s)")
    assert "numerator_samples is empty" in message
    assert "denominator_samples names ['Intensity CTRL_9']" in message


def test_arms_resolve_to_edges_and_ride_beside_the_node(loaded: LoadedCuration) -> None:
    """D1/D4: the arms are `Sample` ids on `LoadedCuration` and two edge types in the change-set,
    and nothing of them reaches the `Contrast` node — its properties are the ones it had."""
    node = loaded.contrast("treated_vs_untreated")
    arms = loaded.contrast_arms["treated_vs_untreated"]
    ids = loaded.sample_ids
    assert arms.numerator == (ids["Intensity TREAT_1"], ids["Intensity TREAT_2"])
    assert arms.denominator == (ids["Intensity CTRL_1"], ids["Intensity CTRL_2"])
    assert arms.kind == "condition"
    for rel, members in (
        ("NUMERATOR_SAMPLE", arms.numerator),
        ("DENOMINATOR_SAMPLE", arms.denominator),
    ):
        assert [e["to"] for e in loaded.edges if e["type"] == rel and e["from"] == node["id"]] == (
            list(members)
        )
    assert set(node) == {NODE_TYPE_KEY, "id", "numerator", "denominator", "label"}


def test_the_arm_edges_are_not_identifying() -> None:
    """D4: absent from `IDENTITY`, which is an allow-list — so no anchor, and no id moves."""
    for spec in schema.IDENTITY.values():
        assert not {rel for _, rel in spec.anchors} & {"NUMERATOR_SAMPLE", "DENOMINATOR_SAMPLE"}
    assert schema.IDENTITY["Contrast"].fields == ("numerator", "denominator")


def test_the_committed_records_declare_thirty_arm_keys_three_against_three() -> None:
    """ADR-0038 M4: five contrasts, 30 keys, 3 against 3, no overlap; every one a `condition`."""
    edges = 0
    for path in sorted(CURATION_DIR.glob("curation_*.json")):
        loaded_record = load_path(path)
        for arms in loaded_record.contrast_arms.values():
            assert (len(arms.numerator), len(arms.denominator)) == (3, 3), path
            assert not set(arms.numerator) & set(arms.denominator), path
            assert arms.kind == "condition", path
        assert set(loaded_record.contrast_arms) == set(loaded_record.contrast_nodes), path
        edges += sum(
            e["type"] in ("NUMERATOR_SAMPLE", "DENOMINATOR_SAMPLE") for e in loaded_record.edges
        )
    assert edges == 30


# ── ADR-0038 D2: I22, each row of the table, on records constructed here ──────────────────────
#
# No committed record is `ip_ms`, so every IP row below runs on `_ip_ms_record`, built here and
# never written to disk.

_KO_UNSTIMULATED = [
    "Ratio mod/base KO_1_181212063719",
    "Ratio mod/base KO_2",
    "Ratio mod/base KO_3",
]


def _i22_refusal(record: dict[str, Any]) -> str:
    with pytest.raises(invariants.InvariantError) as exc:
        load(record)
    assert exc.value.invariant == "I22"
    return str(exc.value)


def _sample_by_key(result: LoadedCuration, key: str) -> dict[str, Any]:
    (node,) = (n for n in result.nodes if n["id"] == result.sample_ids[key])
    return node


def test_I22_derives_each_permitted_kind() -> None:
    """Rows 1–3: `condition` on every committed record (above), and both IP kinds here."""
    arms = load(_ip_ms_record()).contrast_arms
    assert arms["KO_IFN_vs_WT_IFN"].kind == "differential_association"
    assert arms["KO_vs_WT_unstimulated"].kind == "background_enrichment"


def test_I22_admits_an_isotype_control_arm_carrying_its_antibody() -> None:
    """`isotype_control` joins the enum and R7 widens to it (ADR-0038 D2)."""
    record = _ip_ms_record()
    record["mapping"][_CONTROL].update(role="isotype_control", antibody="normal rabbit IgG")
    loaded_record = load(record)
    assert loaded_record.contrast_arms["KO_vs_WT_unstimulated"].kind == "background_enrichment"
    control = _sample_by_key(loaded_record, _CONTROL)
    assert (control["role"], control["bait"], control["antibody"]) == (
        "isotype_control",
        None,
        "normal rabbit IgG",
    )


def test_I22_refuses_a_control_numerator() -> None:
    record = _ip_ms_record()
    entry = _contrast_entry(record, "KO_vs_WT_unstimulated")
    entry["numerator_samples"], entry["denominator_samples"] = [_CONTROL], _KO_UNSTIMULATED
    message = _i22_refusal(record)
    assert "has a 'no_antibody_control' numerator arm in an 'ip_ms' experiment" in message
    assert "a control is never the numerator" in message


def test_I22_refuses_mixed_roles_in_one_arm() -> None:
    record = _ip_ms_record()
    _contrast_entry(record, "KO_vs_WT_unstimulated")["denominator_samples"] = [
        _CONTROL,
        "Ratio mod/base WT_2",
    ]
    message = _i22_refusal(record)
    assert "mixes roles ['ip', 'no_antibody_control'] in its denominator arm" in message


def test_I22_refuses_two_control_roles_in_one_arm() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base WT_2"].update(role="isotype_control", bait=None)
    _contrast_entry(record, "KO_vs_WT_unstimulated")["denominator_samples"] = [
        _CONTROL,
        "Ratio mod/base WT_2",
    ]
    message = _i22_refusal(record)
    assert "mixes roles ['isotype_control', 'no_antibody_control'] in its denominator" in message


def test_I22_refuses_an_ip_arm_with_two_baits() -> None:
    record = _ip_ms_record()
    record["mapping"]["Ratio mod/base KO_IFN_1"]["bait"] = "uniprot:P0CG48"
    message = _i22_refusal(record)
    assert "has a numerator arm pulling down ['uniprot:P05161', 'uniprot:P0CG48']" in message


def test_I22_refuses_ip_arms_against_different_baits() -> None:
    record = _ip_ms_record()
    for n in (1, 2, 3):
        record["mapping"][f"Ratio mod/base KO_IFN_{n}"]["bait"] = "uniprot:P0CG48"
    message = _i22_refusal(record)
    assert (
        "compares IP arms against different baits, ['uniprot:P0CG48'] and ['uniprot:P05161']"
        in message
    )


def _ip_change_set() -> tuple[LoadedCuration, list[dict[str, Any]], list[dict[str, Any]]]:
    loaded_record = load(_ip_ms_record())
    return (
        loaded_record,
        [dict(n) for n in loaded_record.nodes],
        [dict(e) for e in loaded_record.edges],
    )


def test_I22_graph_form_refuses_arm_edges_without_the_anchor() -> None:
    """Arms and anchor are written together; without the anchor the modality cannot be read."""
    loaded_record, nodes, edges = _ip_change_set()
    cid = loaded_record.contrast_nodes["KO_IFN_vs_WT_IFN"]["id"]
    edges = [e for e in edges if not (e["type"] == "CONTRAST_IN_EXPERIMENT" and e["from"] == cid)]
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, edges, only="I22")
    assert exc.value.invariant == "I22"
    assert "carries arm edges but no CONTRAST_IN_EXPERIMENT" in str(exc.value)


def test_I22_graph_form_refuses_a_minted_contrast_without_an_arm() -> None:
    """D8 at the graph: a change-set carrying the anchor is minting the contrast, so it carries
    both arms."""
    loaded_record, nodes, edges = _ip_change_set()
    cid = loaded_record.contrast_nodes["KO_IFN_vs_WT_IFN"]["id"]
    edges = [e for e in edges if not (e["type"] == "DENOMINATOR_SAMPLE" and e["from"] == cid)]
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, edges, only="I22")
    assert "has an empty denominator arm; every contrast declares both (ADR-0038 D8)" in str(
        exc.value
    )


def test_I22_graph_form_refuses_a_sample_in_both_arms() -> None:
    loaded_record, nodes, edges = _ip_change_set()
    cid = loaded_record.contrast_nodes["KO_IFN_vs_WT_IFN"]["id"]
    shared = loaded_record.contrast_arms["KO_IFN_vs_WT_IFN"].denominator[0]
    edges.append({"type": "NUMERATOR_SAMPLE", "from": cid, "to": shared})
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, edges, only="I22")
    assert f"puts [{shared!r}] in both arms" in str(exc.value)


def test_I22_graph_form_refuses_a_role_outside_ip_ms() -> None:
    """Row 1's NULLs: the loader's R2 refuses this first, so only the graph form can reach it —
    which is where it matters, at a store write no loader rule guards."""
    loaded_record = load_path(REAL_RECORD)
    nodes = [dict(n) for n in loaded_record.nodes]
    numerator = set(loaded_record.contrast_arms["KO_IFN_vs_WT_IFN"].numerator)
    for sample in (n for n in nodes if n["id"] in numerator):
        sample.update(role="ip", bait="uniprot:P05161")
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, list(loaded_record.edges), only="I22")
    assert "is in a 'digly_proteomics' experiment, where every role is NULL" in str(exc.value)


def test_I22_graph_form_refuses_an_ip_ms_arm_with_no_role() -> None:
    """R3's case at the graph: an `ip_ms` denominator whose samples carry no role."""
    loaded_record, nodes, edges = _ip_change_set()
    (control,) = (n for n in nodes if n["id"] == loaded_record.sample_ids[_CONTROL])
    control["role"] = None
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, edges, only="I22")
    assert "has a denominator arm with no role in an 'ip_ms' experiment" in str(exc.value)


def test_I22_runs_in_every_validate_not_only_when_asked() -> None:
    """P1: an entry in `invariants._CHECKS`, so the store write's unfiltered `validate` runs it. The
    loader would refuse without it — its own `contrast_kind` call reads the same table — so this is
    the test that sees I22 dropped from `_CHECKS`."""
    loaded_record, nodes, edges = _ip_change_set()
    cid = loaded_record.contrast_nodes["KO_IFN_vs_WT_IFN"]["id"]
    edges = [e for e in edges if not (e["type"] == "DENOMINATOR_SAMPLE" and e["from"] == cid)]
    with pytest.raises(invariants.InvariantError) as exc:
        invariants.validate(nodes, edges)
    assert exc.value.invariant == "I22"


def test_I22_is_vacuous_on_a_referent_contrast() -> None:
    """Every producer stages its `Contrast` without the anchor or the arms (ADR-0029 E), and I22
    has nothing to check there. Sound only while the loader is the only `Contrast` minter."""
    node = load(_ip_ms_record()).contrast("KO_vs_WT_unstimulated")
    invariants.validate([node], [], only="I22")


# ── The `Sample` role mirror (handoff 10-05 §7's unguarded mirror) ────────────────────────────


def _sample_ddl_comments() -> dict[str, str]:
    """`Sample`'s DDL in ONTOLOGY.md §5, as {column -> its comment, continuation lines joined}."""
    text = (REPO_ROOT / "ONTOLOGY.md").read_text()
    body = re.search(r"CREATE NODE TABLE Sample\((.*?)PRIMARY KEY", text, re.DOTALL)
    assert body, "no `Sample` table in ONTOLOGY.md"
    comments: dict[str, str] = {}
    column = None
    for line in body.group(1).splitlines():
        code, _, comment = line.partition("--")
        if code.strip():
            column = code.split()[0]
            comments[column] = comment.strip()
        elif column and comment:
            comments[column] += " " + comment.strip()
    return comments


def test_the_role_vocabulary_mirrors_the_sample_ddl_comment() -> None:
    """`_SAMPLE_ROLES`, `_IP_MODALITY` and R7's `_ANTIBODY_ROLES` against §5's `Sample` comment,
    parsed rather than restated — the house pattern of `schema.py` ↔ §4–§7, `ABSENCE` ↔ §3 and
    `CURATION_BASIS` ↔ §5.3. Built with ADR-0038 D2, the change that would otherwise have widened
    one home and not the other."""
    comments = _sample_ddl_comments()
    enum, _, rest = comments["role"].partition(". ")
    assert set(re.findall(r"'(\w+)'", enum)) == loader._SAMPLE_ROLES, comments["role"]
    modality = re.search(r"modality is '(\w+)'", rest)
    # Both names against the document, not against each other: the loader binds its name to
    # `invariants.IP_MODALITY`, so comparing the two would hold by construction.
    assert modality and {loader._IP_MODALITY, invariants.IP_MODALITY} == {modality.group(1)}
    antibody = re.search(r"NULL unless role ∈ \{([^}]*)\}", comments["antibody"])
    assert antibody, comments["antibody"]
    assert set(re.findall(r"'(\w+)'", antibody.group(1))) == loader._ANTIBODY_ROLES
    bait = re.search(r"NULL unless role = '(\w+)'", comments["bait"])
    assert bait and bait.group(1) == invariants.IP_ROLE
    assert loader._ANTIBODY_ROLES <= loader._SAMPLE_ROLES
