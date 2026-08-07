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
