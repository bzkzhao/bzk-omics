---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `GLOSSARY.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

This repo is single-context and both files already exist. Nothing is created lazily; nothing is
scaffolded.

```
/
├── GLOSSARY.md          ← definitions (the role upstream assigns to CONTEXT.md)
├── ONTOLOGY.md          ← normative: node/edge types, field semantics, invariants
└── decisions/
    ├── 0001-two-graph-model.md
    ├── ...
    └── README.md        ← status convention; read before writing a record
```

Upstream's multi-context layout — `CONTEXT-MAP.md`, per-package glossaries, per-context ADR
directories — does not apply. Do not create it.

**`GLOSSARY.md` is additive only.** Terms are added, not removed. Where a definition there
conflicts with usage elsewhere, the glossary wins and the other document is corrected.

**A term's definition and its type are separate homes.** `GLOSSARY.md` defines what a term means;
`ONTOLOGY.md` types it and states its invariants. Do not restate one in the other —
`CLAUDE.md` § Single source of truth calls a duplicated fact a defect, not redundancy.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right there. Don't batch these up — capture them as they happen. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat `GLOSSARY.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for
   specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

**Writing an ADR here is a test-guarded, multi-file change.** It is not one file.
`tests/test_decision_index.py` checks three enumerations of ADR numbers against each other and
against the directory, with pinned counts. See `.claude/config/domain.md` for the full checklist
and run `pytest tests/test_decision_index.py` before claiming the record is written.

**Never edit an `Accepted` record.** A changed decision gets a new record that supersedes the old,
and both stay readable. A record lands as `Proposed` and becomes `Accepted` only after a review
round-trip actually happens — read `decisions/README.md`, which measures how far the directory's
own history falls short of that rule rather than relabelling it away.
