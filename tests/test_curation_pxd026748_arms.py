"""`PXD026748`'s two arms — one deposit, two curation records, and what keeps them apart.

The deposit carries two files: the GG-enriched `GlyGly (K)Sites.txt` and the shotgun
`proteinGroups.txt` that measures the unenriched input to that enrichment. One record carries one
file and one `content_hash`, so there are two records, and per ADR-0035 R1 a `Sample` is *the
material measured* — so the shotgun runs are twelve `Sample`s of their own, not the GG record's
twelve seen again.

**The Samples' identity fields are deliberately identical across the two records**, because the
material *is* the same up to the digest split: the Methods sentence the shotgun record quotes says
an aliquot of each replicate's digest went to shotgun and the remainder to GG immunocapture. What
makes the two sets distinct is `schema.py`'s `Sample` anchor on `Experiment`, and nothing else.
That is a load-bearing subtlety with no visible failure mode: copying the GG record's `experiment`
block into the shotgun record merges all twelve `Sample`s into the GG record's, the loader accepts
it, the graph is smaller by twelve nodes, and nothing says so. **Measured, not argued** — the
counterfactual is `test_sharing_an_experiment_would_merge_every_sample` below, and it is the reason
this module exists rather than a note.

Entirely offline. Every mutation is written under `tmp_path`; the committed records are read and
never edited.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bzk.adapters.maxquant_protein_groups import (
    MaxQuantProteinGroupsError,
    quantity_from_mapping_keys,
)
from bzk.curation.loader import LoadedCuration, load_path
from bzk.ontology.invariants import NODE_TYPE_KEY
from bzk.ontology.schema import IDENTITY

CURATION_DIR = Path(__file__).resolve().parent.parent / "data" / "curation"
GG_RECORD = CURATION_DIR / "curation_PXD026748.json"
SHOTGUN_RECORD = CURATION_DIR / "curation_PXD026748_shotgun.json"


def _ids(loaded: LoadedCuration, label: str) -> set[str]:
    return {str(n["id"]) for n in loaded.nodes if n[NODE_TYPE_KEY] == label}


def _identity_tuples(loaded: LoadedCuration) -> list[tuple[Any, ...]]:
    """Each `Sample`'s identity **fields**, in `schema.py`'s order — the anchor deliberately left
    out, because the anchor is the whole difference this module is about."""
    return sorted(
        tuple(n.get(f) for f in IDENTITY["Sample"].fields)
        for n in loaded.nodes
        if n[NODE_TYPE_KEY] == "Sample"
    )


def _loaded_with(tmp_path: Path, path: Path, **replacements: Any) -> LoadedCuration:
    """One committed record, reloaded with some top-level blocks replaced, under `tmp_path`.

    Never writes into `data/curation/`. Every mutation in this module goes through here, so a test
    that forgot to copy first would have to go out of its way.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    record.update(replacements)
    mutated = tmp_path / path.name
    mutated.write_text(json.dumps(record), encoding="utf-8")
    return load_path(mutated)


# ── T1 · the arms share a Project and nothing else ──────────────────────────────────────────────


def test_the_two_arms_share_a_project_and_nothing_else() -> None:
    """One deposit, one publication, one project — and two experiments, two files, two ingestions
    and twenty-four samples."""
    gg = load_path(GG_RECORD)
    shotgun = load_path(SHOTGUN_RECORD)

    assert len(_ids(gg, "Project") & _ids(shotgun, "Project")) == 1

    # **Samples on their own line, and first.** They are the disjointness this module exists for,
    # and inside a loop they would never be reached: an `experiment` block copied from the GG
    # record collides on `Experiment` too, so the loop would fail one label early and report the
    # anchor rather than the twelve materials that silently merged behind it.
    shared_samples = _ids(gg, "Sample") & _ids(shotgun, "Sample")
    assert not shared_samples, (
        f"the two arms share {len(shared_samples)} Sample id(s): {sorted(shared_samples)}"
    )

    for label in ("Experiment", "Dataset", "Analysis"):
        shared = _ids(gg, label) & _ids(shotgun, label)
        assert not shared, f"the two arms share {len(shared)} {label} id(s): {sorted(shared)}"

    assert len(_ids(gg, "Sample")) == 12
    assert len(_ids(shotgun, "Sample")) == 12


def test_sharing_an_experiment_would_merge_every_sample(tmp_path: Path) -> None:
    """The counterfactual that makes the test above mean something.

    With the GG record's `experiment` block in place, all twelve shotgun `Sample`s collapse onto
    the GG record's — because their identity fields are already identical and only the anchor kept
    them apart. The loader accepts it without complaint, which is exactly why this is asserted:
    the failure mode of getting the `experiment` block wrong is a *smaller* graph, not an error.
    """
    gg = load_path(GG_RECORD)
    merged = _loaded_with(
        tmp_path, SHOTGUN_RECORD, experiment=json.loads(GG_RECORD.read_text())["experiment"]
    )

    assert len(_ids(gg, "Sample") & _ids(merged, "Sample")) == 12
    assert len(_ids(gg, "Experiment") & _ids(merged, "Experiment")) == 1


# ── T2 · same biology, different Experiment ────────────────────────────────────────────────────


def test_every_shotgun_sample_matches_a_gg_sample_on_every_identity_field() -> None:
    """The record's rationale (3) as an assertion: *"Their biology fields are deliberately
    identical to the GG record's, because the material is the same up to the split; they are
    distinct because Sample identity is anchored on Experiment."*

    Both halves matter and this is the half that would rot quietly. If a later edit changed a
    `treatment` or a `genotype` on one arm to make a mapping read better, the ids would still be
    distinct — T1 would stay green — while the two records had silently stopped describing the same
    twelve materials.
    """
    gg = _identity_tuples(load_path(GG_RECORD))
    shotgun = _identity_tuples(load_path(SHOTGUN_RECORD))

    assert len(shotgun) == 12
    # The message is built from the symmetric difference rather than left to the list comparison.
    # Both sides are sorted, so a single changed field moves one tuple and the `==` diff then
    # reports the first index where the re-sorted lists diverge — a pair that differs in some
    # *other* field, naming the wrong one. Measured on the mutation that pins this test.
    unmatched = sorted(set(shotgun) ^ set(gg))
    assert not unmatched, (
        f"{len(unmatched)} Sample identity tuple(s) appear in one arm and not the other: "
        f"{unmatched}. The two arms' Samples no longer agree field-for-field, so the distinctness "
        "between them is no longer the Experiment anchor alone — which is what the shotgun "
        "record's rationale (3) claims and what ADR-0035 R1 rests on here"
    )
    assert shotgun == gg, "the two arms' Sample identity tuples differ in multiplicity"


# ── T3 · the derived quantity ───────────────────────────────────────────────────────────────────


def test_the_shotgun_mapping_keys_derive_lfq() -> None:
    """Rationale (4): the mapping keys are the `LFQ intensity ` family, so the ingestion declares
    `lfq`. Since turn 10d the adapter retains every family the file reports, so this fixes the key
    family and the recorded `Analysis.quantity` (I16) — not what is stored (I11)."""
    assert quantity_from_mapping_keys(load_path(SHOTGUN_RECORD).sample_mapping()) == "lfq"


def test_a_mapping_key_from_a_second_family_cannot_derive_a_quantity(tmp_path: Path) -> None:
    """One key re-prefixed to `Intensity ` and the derivation refuses, naming both families.

    A record whose keys span two families has no quantity to declare: `_sample_columns` would
    refuse the odd key at ingestion, and guessing one here would put a quantity on the `Analysis`
    that the record does not support.
    """
    mapping = json.loads(SHOTGUN_RECORD.read_text())["mapping"]
    first = next(iter(mapping))
    mapping = {
        ("Intensity " + k.removeprefix("LFQ intensity ") if k == first else k): v
        for k, v in mapping.items()
    }
    loaded = _loaded_with(tmp_path, SHOTGUN_RECORD, mapping=mapping)

    with pytest.raises(MaxQuantProteinGroupsError) as caught:
        quantity_from_mapping_keys(loaded.sample_mapping())

    message = str(caught.value)
    assert "intensity" in message
    assert "lfq" in message
