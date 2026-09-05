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

    The four files do not agree on their key sets — `corrections` is in one real record and not the
    other, `note` and `synthetic` are in the fixtures and neither real record, `pending` is in one
    fixture alone — so a check written as an equality would refuse three of the four.
    """
    records = sorted(CURATION_DIR.glob("curation_*.json")) + sorted(
        FIXTURES.glob("curation_synthetic_*.json")
    )
    assert len(records) == 4, f"expected the two records and the two twins, found {records}"
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
