# Proteus — D-23 workspace compliance, 2026-09-11

Built from **`2627fe37cfc002926b9763f9f4ac7345b67caa5d`** in
`F:\Prometheus-worktrees\proteus-workspace-d23` on branch `proteus/workspace-d23`.

## (a) Files claimed in the canonical checkout — NONE

`CANONICAL_STATUS_2026-09-11.txt` lists 35 modified and 96 untracked files. **Zero are Proteus's.**
A case-insensitive search of the snapshot for `proteus` returns 0 matches; the affected trees are
`SerendipityFoundry` (29), `evidence_wiki` (14), `ergon` (12), `aporia` (8), `integration` (5),
`charon` (4), `herakles` (3), `roles` (2), `ludus` (2) and a long tail of scraped web assets.

Nothing claimed, nothing deleted. I made no write of any kind to the canonical checkout.

## (b) Worktrees and branches

**Removed:** `…/scratchpad/pv6`, a worktree on the long-lived branch `proteus-v0-6b` living under a
**session-temporary scratchpad** — in violation of rule 2 on both counts. Every commit it carried
was already an ancestor of `origin/main` before removal.

**Branches deleted (local only):** `proteus-v0-6b`, `proteus-v0-build`, `proteus-program-packet`.
All three were merged into `origin/main`. **Proteus owns no branch on origin** and never has —
`git ls-remote --heads origin | grep -i proteus` is empty — so there was nothing to delete
remotely and none of mine could have appeared on a stale-branch list.

`proteus/workspace-d23` is a short-lived task branch and is deleted once it fast-forwards main.

## (c) Long-running processes — NONE

Proteus runs no consumer, tick, engine or scheduled task. The long jobs this seat has run
(the V0.6 kernel measurement, the operator-count replay, the dual analysis) were foreground and
finished inside their session. Nothing of mine needs a pinned worktree, and nothing of mine is
running from `F:\Prometheus\` or from a temp path.

## (d) Startup refusal — `proteus/workspace.py`

Detection asks git rather than assuming a path: the canonical checkout is the repository's MAIN
worktree, where `rev-parse --git-dir` equals `--git-common-dir`. Verified live — `F:\Prometheus`
reports `main_worktree = True`, this worktree reports `False`.

**34 writing entry points guarded**, across `compose/`, `eval/`, `integration/`, `v0/`, `v0_3/`,
`v0_4/`, `v0_5/` and `v0_6/`. The guard sits *inside* `if __name__ == "__main__":`, never at module
scope, so importing a module for a test does not trip it — asserted by a test.

**Two deliberate exclusions**, recorded in code with their reasons rather than left silent:
`proteus/audits/audit_identity.py` and `proteus/audits/quarantine.py`. Both are named in the
auditor's own covered-file list, so adding an import to either would move `audited_tree_digest`,
mark the stamp STALE, and force an identity transition on the runtime under which 64 fossilised
specimens are interpreted. That is the "bundle, do not do casually" case. `quarantine.py` also
writes nothing, so a guard there would protect nothing. **This is reported for the operator to
decide, not resolved unilaterally.**

Tests: refusal fires (positive control), the message names the remedy, the override permits
read-only inspection *and is recorded in the receipt*, `allow_override=False` cannot be overridden,
a linked worktree is allowed, the receipt carries all of rule 4, every writer is guarded or
excluded, and no exclusion is stale. Suite 284 → 295.

## (e) Rule 7 diagnostics — the incident that motivated this

Preserved here because rule 7 asks for it as a committed note.

**2026-09-11, `…/scratchpad/pv6`:** `git status --porcelain` reported **11,134 tracked files
missing** (`D`), with HEAD at `9e9210893`, index intact, **nothing staged**, and no modified
tracked file. Only 5 untracked files — my own new work — were present. It followed a large
fast-forward whose "Updating files" progress had run to completion. `LICENSE` and `.graphifyignore`
were among the missing.

Nothing was lost and nothing bad was committed: Proteus commits name explicit paths, never a
directory, so a deletion could not have been swept in. I repaired it with `git restore .`.
**Under rule 7 that was the wrong move** — `git restore .` is a diagnostic, and the workflow is to
preserve the evidence, destroy the worktree and recreate it from the recorded base SHA. That
worktree has now been destroyed regardless.

This was the **second** occurrence in this seat's history; the first is in the V0.6 failure
chronology. Both had the same signature, and the second is what the missive cites.

## What did not change

`proteus/foundry/` untouched; the audit stamp still reads FRESH on its original tree digest
`3ae4ee8b773e0fcf`; quarantine PASS; the registry still reproduces byte-for-byte. No other seat's
files, worktrees, branches or locks were touched.
