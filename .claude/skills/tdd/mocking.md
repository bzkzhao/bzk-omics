# When to mock

Mock at **system boundaries** only:

- External HTTP APIs — UniProt, PRIDE, ontology services
- The filesystem, sometimes
- Time and randomness
- Databases, sometimes — but here prefer a real temporary store

Don't mock:

- Your own modules
- Internal collaborators
- Anything you control

**Prefer a real store over a mocked one.** Kùzu and DuckDB both open on a temporary path, so an
integration test can use the real engine. A mocked store cannot catch a DDL divergence from
`ONTOLOGY.md`, which is the class of bug that matters most here.

**Never mock across a contract boundary in a way that hides a subtype.** Code consuming the
`Observation` or `EvidencedInference` contract must work for every subtype — `ONTOLOGY.md` §10. A
test that mocks one subtype's behaviour into the contract proves nothing about the others, and an
`isinstance` branch outside a subtype module is a defect whether it appears in `bzk/` or `tests/`.

## Designing for mockability

**1. Pass external dependencies in**

```python
# Easy to mock — the caller supplies the boundary
def fetch_protein(accession: str, client: HttpClient) -> Protein:
    return parse(client.get(f"/uniprot/{accession}"))


# Hard to mock — the boundary is constructed inside
def fetch_protein(accession: str) -> Protein:
    client = HttpClient(base_url=os.environ["UNIPROT_URL"])
    return parse(client.get(f"/uniprot/{accession}"))
```

**2. Prefer one function per external operation over a generic fetcher**

```python
# GOOD: each is independently mockable, each returns one shape
class UniProtClient(Protocol):
    def get_entry(self, accession: str) -> Entry: ...
    def get_isoforms(self, accession: str) -> list[Isoform]: ...


# BAD: mocking it requires conditional logic inside the mock
class UniProtClient(Protocol):
    def get(self, path: str) -> dict: ...
```

The first shape means each mock returns one specific type, there is no branching in test setup,
and it is visible from the test which endpoints are exercised.

**3. Cache fixtures rather than mocking the network**

External responses are cached — see `OPERATIONS.md` for the cache policy. A cached real response
is better than a hand-written mock: it cannot drift from a shape the service never returned.

**Never invent an identifier to fill a fixture.** No fabricated UniProt accession, PXD accession,
or ontology term. Use a real one or mark the fixture synthetic — `CLAUDE.md` § Working style.

## Never branch on pipeline metadata

Invariant I13, in `ONTOLOGY.md` §8, names the fields it covers; read them there rather than from a
copy. They are recorded data, and a conditional on their value outside `adapters/` or the
statistics registry is a defect — including in a test helper or a fixture factory.
