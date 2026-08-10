"""The adapter contract (ARCHITECTURE.md §3): a conforming adapter's output validates.

base.py holds no logic, so this pins the contract's two obligations: an adapter satisfies the
`ObservationAdapter` Protocol, and the `ParsedObservations` it returns is a self-contained
change-set the invariant layer accepts (ADR-0019). A trivial adapter that replays the shared valid
change-set stands in for a real one until Perseus lands.
"""

from __future__ import annotations

import json
from pathlib import Path

from bzk.adapters.base import ObservationAdapter, ParsedObservations, SampleMapping
from bzk.ontology import keys, schema
from bzk.ontology.invariants import validate

VALID_CHANGESET = Path(__file__).parent / "fixtures" / "valid_changeset.json"


class _ReplayAdapter:
    """A stand-in adapter that emits the shared valid change-set, ignoring its input."""

    name = "replay"

    def sniff(self, path: Path) -> bool:
        return path.suffix == ".json"

    def parse(self, path: Path, mapping: SampleMapping) -> ParsedObservations:
        cs = json.loads(VALID_CHANGESET.read_text())
        return ParsedObservations(nodes=cs["nodes"], edges=cs["edges"])


def test_adapter_satisfies_the_protocol() -> None:
    assert isinstance(_ReplayAdapter(), ObservationAdapter)


def test_parsed_observations_validate_as_a_changeset() -> None:
    mapping = SampleMapping(curation_analysis_id="bzk:an1", samples=[])
    parsed: ParsedObservations = _ReplayAdapter().parse(Path("x.json"), mapping)
    validate(parsed.nodes, parsed.edges)  # ADR-0019 + all write-time checks: must not raise


def test_sample_mapping_carries_its_curation_analysis() -> None:
    mapping = SampleMapping(curation_analysis_id="bzk:cur1", samples=[{"label": "KO_1"}])
    assert mapping.curation_analysis_id == "bzk:cur1"
    assert mapping.samples[0]["label"] == "KO_1"


def test_a_refusal_is_not_a_node_type_and_the_absence_is_a_decision() -> None:
    """Pins the answer to *is a refusal an entity*, so removing it is a decision and not a drift.

    Answered **no** on 2026-08-09 (`base.Refusal`'s docstring, `ROADMAP.md` § *Measured findings*).
    The reasoning is structural rather than a preference, and both halves are asserted here because
    prose that is true today is indistinguishable from prose that stopped being true: a refusal has
    no id by construction, and `evidence_id` will not mint one for a label §3 does not carry — so a
    node type is not a small addition, it is an identity decision first.

    Adding `Refusal` to the DDL fails this test, which is the intended signal: the row is there to
    make the next person re-open the argument rather than discover the gap.
    """
    tables = {table.name for table in schema.NODE_TABLES}
    # Non-vacuity: a typo'd attribute or an empty registry would satisfy the claim below for the
    # wrong reason, which is this repository's most-repeated failure.
    assert "SiteObservation" in tables and len(tables) > 20
    assert "Refusal" not in tables
    try:
        keys.evidence_id("Refusal", {"row": "1", "reason": "residue_mismatch"})
    except Exception as exc:  # noqa: BLE001 — the type is the point, not the class
        assert "identity" in str(exc).lower()
    else:  # pragma: no cover — reached only if §3 gains a Refusal row
        raise AssertionError("evidence_id minted a Refusal id, so §3 now carries one")
