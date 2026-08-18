---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Run this repo's **automated checks** and fix anything the merge broke. `CLAUDE.md`
   § Working style, point 1, enumerates them and their targets; run them from there, not
   from a list copied into this file. Report each by name at its actual result, with its
   target stated — a check not run is reported as not run.

   **Regenerate `uv.lock` rather than hand-merging it.** Same for any other generated file.

   If the merge touched `bzk/ontology/schema.py`, `decisions/`, or anything §3/§5.3 mirrors, run
   `uv run pytest tests/test_schema.py tests/test_decision_index.py` specifically — those modules
   guard mirrors between two sources and a conflict resolution is exactly how a mirror drifts.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
