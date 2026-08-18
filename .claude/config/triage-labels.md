# Triage labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the
strings actually used here.

This repo has **no label vocabulary** — it does not use GitHub Issues (see `issue-tracker.md`).
The roles are recorded as a `Status:` line at the top of a ticket file under `.scratch/`, using
the upstream default strings unchanged.

| Canonical role | String used here | Meaning |
|---|---|---|
| `needs-triage` | `needs-triage` | Not yet evaluated |
| `needs-info` | `needs-info` | Waiting on more information before it can be actioned |
| `ready-for-agent` | `ready-for-agent` | Fully specified, ready for an unattended agent session |
| `ready-for-human` | `ready-for-human` | Requires human implementation or a human decision |
| `wontfix` | `wontfix` | Will not be actioned |

Do not create these as GitHub labels. Nothing reads them but the ticket files.

**`ready-for-agent` carries a repo-specific bar.** A ticket is only agent-ready here if it names
which of `ONTOLOGY.md`'s invariants the change touches, or states that it touches none. An
adapter or ingestion ticket that does not is `needs-info` — see `CLAUDE.md`, *Tests before code,
invariants before adapters*.
