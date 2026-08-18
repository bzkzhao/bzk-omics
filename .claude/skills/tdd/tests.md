# Good and bad tests

Examples are `pytest`, matching `tests/`. Assertions are plain `assert`.

## Good tests

**Integration-style** — test through real interfaces, not mocks of internal parts.

```python
def test_site_is_retrievable_after_ingestion(store):
    """GOOD: observable behaviour, through the public interface."""
    ingest_sites(store, [site(protein="uniprot:P05161", position=29)])

    found = store.sites_for_protein("uniprot:P05161")

    assert [s.position for s in found] == [29]
```

Characteristics:

- Tests behaviour a caller cares about
- Uses the public interface only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad tests

**Implementation-detail tests** — coupled to internal structure.

```python
def test_ingest_calls_the_key_builder(monkeypatch):
    """BAD: asserts on an internal collaborator."""
    calls = []
    monkeypatch.setattr(keys, "build_site_key", lambda *a: calls.append(a))

    ingest_sites(store, [site(...)])

    assert len(calls) == 1
```

Red flags:

- Mocking internal collaborators
- Testing private functions
- Asserting on call counts or call order
- The test breaks when you refactor and behaviour has not changed
- The test name describes HOW, not WHAT
- Verifying through a side channel instead of the interface

```python
def test_ingest_writes_the_row(store):
    """BAD: bypasses the interface to verify."""
    ingest_sites(store, [site(protein="uniprot:P05161", position=29)])

    rows = store._conn.execute("SELECT * FROM ModificationSite").fetchall()

    assert rows


def test_ingested_site_is_retrievable(store):
    """GOOD: verifies through the same interface a caller would use."""
    ingest_sites(store, [site(protein="uniprot:P05161", position=29)])

    assert store.sites_for_protein("uniprot:P05161")
```

**Tautological tests** — the expected value is recomputed the way the code computes it, so the
test passes by construction and can never disagree with the code.

```python
def test_key_is_built_from_its_parts():
    """BAD: the expectation restates the implementation."""
    parts = ("uniprot:P05161", 2, 29)
    expected = "|".join(str(p) for p in parts)

    assert build_site_key(*parts) == expected


def test_key_is_built_from_its_parts():
    """GOOD: an independent, known-good literal."""
    assert build_site_key("uniprot:P05161", 2, 29) == "uniprot:P05161|2|29"
```

Expected values must come from an independent source of truth — a known-good literal, a worked
example, or the spec. This repo runs `tests/test_tautology_sweep.py` against exactly this shape,
with a pinned floor so a sweep that stops matching fails loudly instead of reporting clean.

## Two failures this repo actually had

Both are green-suite failures — the run passed and the check had not happened. Read them as the
calibration for what "verified" means here.

**Vacuous passes (ADR-0019).** Four invariant checks passed while fully tested, because the
condition they asserted was never reachable with the fixtures in play. A check that cannot fail is
not a check. **A new guard is not verified until it has been made to fail.**

**A count asserted against its own source.** `test_rebuild` asserted a table count computed from
the same place the code read it. It could only agree with itself.

**The mutation must be confirmed to have applied.** On 2026-08-07 a shell quoting error left the
file untouched during a guard's mutation test; `pytest` reported `1 passed`, indistinguishable
from a guard that does not fire. Read the mutated file back, or read the failure message — never
take the exit status alone. Revert each mutation, and confirm the suite is green again, before
reporting.

## Where tests go

`tests/`, per `[tool.pytest.ini_options] testpaths`. The schema mirror has its own module,
`tests/test_schema.py`, which checks `bzk/schema.py` against `ONTOLOGY.md` §4–§7.

**Every mirror between two sources in this repo is guarded by a test.** `schema.py` ↔ §4–§7,
`ABSENCE` ↔ §3, `CURATION_BASIS` ↔ §5.3, the deposit digest ↔ `bzk/sources/pride.py`, and the
three ADR-number enumerations ↔ `decisions/`. If your change introduces a new mirror, it needs a
guard in the same commit — a note in `HANDOFF.md` §8 does not close a class that is
machine-checkable.
