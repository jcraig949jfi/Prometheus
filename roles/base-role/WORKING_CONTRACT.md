# The Prometheus working contract (repository and workspace)

Adopted by the operator 2026-09-11 as decision D-23 (archaeon/docs/expansion/DECISIONS.md).
Every role inherits this file through roles/base-role/RESPONSIBILITIES.md.
The missive that introduced it, with the evidence that motivated it, is
roles/Archaeon/prompts/2026-09-11_workspace/MISSIVE_ALL_SEATS.md.

## 1. One repository, many worktrees, never one shared working directory

- F:\Prometheus (the path is the operator's; the rule is not about the
  path) is the CANONICAL CLONE: the repository's main worktree. It is
  read-mostly. It is used for `git fetch`, inspection, and worktree
  management. Nothing else.
- NO seat performs a mutating git operation in the canonical checkout:
  checkout, switch, pull, merge, rebase, reset, restore, cherry-pick,
  branch creation, stash. NO seat creates, edits or deletes source files
  there. The one permitted write is the once-only deletion of your OWN
  untracked scratch during a declared clean-up, reported afterwards.
- A seat whose working directory resolves to the canonical checkout must
  REFUSE to run. Detection needs no path: only in the main worktree does
  `git rev-parse --git-dir` equal `git rev-parse --git-common-dir`.
  Reference implementation: archaeon/workspace.py (`is_main_worktree`,
  `assert_not_canonical`, `receipt`). Copy the check into every entry
  point you own; a queue or engine write never gets an override.

## 2. A worktree per seat, a short-lived branch per task

    git -C F:\Prometheus fetch origin
    git -C F:\Prometheus worktree add F:\Prometheus-worktrees\<seat>-<task> ^
        -b <seat>/<task> origin/main

- Work only in that worktree. Never CREATE a worktree by hand beneath the
  canonical checkout's own directory, and never under a session-temporary
  scratchpad for anything that must outlive the session. The invariant is
  ISOLATION -- never mutate the canonical working tree, never let task
  state share its index -- not the path. A harness-managed linked worktree
  that happens to live under the canonical path (the Claude Code harness
  assigns .claude/worktrees/<name>) is permitted PROVIDED the guard passes
  (git-dir differs from git-common-dir) and the receipt records the path.
  (Operator ruling 2026-09-11 on Vivarium's adoption pass; the earlier
  wording declared the execution environment itself nonconformant.)
- Record the base SHA the branch was created from. It goes in every
  receipt (section 4).
- Long-lived seat branches are retired; task branches replace them.

## 3. Never `git pull`

- THE PRE-WORKTREE STEP, in the order a fresh seat meets it: `git fetch
  origin` in the canonical checkout (read-only for the tree), record
  `git rev-parse origin/main`, then `git worktree add <path> -b <branch>
  <that sha>` and do everything else there. A wake directive that says
  "pull the latest first" MEANS this; a seat that pulls before it has read
  this contract has violated s1 and s3 without knowing (Atalanta L-09,
  2026-09-11), so the directive is reworded at its source and this clause
  exists for the seat that reads in order.
- Fetch, then merge or rebase EXPLICITLY from a named SHA:
  `git fetch origin && git merge <sha>`. Every state transition is then
  observable and recorded. A `pull` fetches and rewrites the tree in one
  invisible step; it is forbidden.
- Wrap git calls in a timeout sized to the operation. NEVER give
  `worktree add`, `checkout`, `switch`, `merge` or `restore` of a large
  tree a short timeout: a checkout killed mid-update leaves the index
  intact and thousands of tracked files missing from disk, deletions
  staged -- the same signature CLASS as the canonical checkout's two losses.
  Observed on 2026-09-11: `timeout 120 git worktree add` on the 39,067-
  file tree was killed at ~80% and left 39,067 files missing with a lock
  (CORRECTION, Elenchus C-07 2026-09-11: this is a different count and a
  different location from the canonical losses -- a worktree being created,
  not an established checkout -- and a rival explanation, a concurrent
  rewrite, is live in Harmonia's compliance record. The observation is
  sufficient to justify this rule and insufficient to close the incident.)
  reason "initializing". Budget such operations at 900 s or more, or run
  them unbounded and watch. If a command does time out, do not retry in a
  loop; look at the tree, then act once (rule 7: destroy and recreate).
- Never remove another seat's lock (`index.lock`, `next-index-*.lock`).
  You may remove a stale lock in YOUR OWN worktree's gitdir only.

## 4. Every receipt records where it was built

- base_sha, branch, worktree_path, dirty (tracked changes present) -- on
  every campaign issue receipt, tick receipt, queue row, readout and
  report. "Built from a15e12ffe in F:\Prometheus-worktrees\harmonia-17"
  is the form. archaeon.workspace.receipt() returns exactly this.
- Push THEN verify: after `git push`, confirm
  `git merge-base --is-ancestor <sha> origin/main` before quoting the SHA
  anywhere. A SHA quoted before it is an ancestor of origin/main can be
  orphaned by someone else's rebase.

## 5. Integration is a fast-forward after tests

- Run the tests on the MERGED tree (your branch with origin/main merged
  in), then `git push origin <branch>:main` only when origin/main is an
  ancestor of your HEAD. If it is not, fetch, merge the new SHA
  explicitly, test again, push again. Never force.
- Commit by EXPLICIT PATHS with a message file (`git add <paths>` then
  `git commit -F <file>`); never a pathspec-less commit that sweeps
  another seat's staged work; never `git add -A`.
- Rows ship in the same commit as the verdict they support. A verdict
  whose raw ledger is not committed is an assertion.
- Then `git worktree remove` the worktree and `git branch -d` the branch
  (locally and `git push origin --delete` remotely) once merged. Delete
  only your own branches, only when `git branch -r --merged origin/main`
  lists them.

## 6. Long-running processes run from pinned worktrees

- Consumers, ticks, engines and watchers run from a worktree checked out
  DETACHED at a recorded SHA under F:\Prometheus-worktrees\<seat>-<process>,
  advanced only by an explicit, logged command after tests pass at the
  new SHA. Their receipts carry that SHA. Nobody edits in a pinned
  worktree.

## 7. Dirty or corrupt worktree: destroy, do not nurse

- If a worktree reports missing tracked files or an inconsistent index,
  preserve the diagnostics (`git status --short`, the missing-file list,
  the process list, the time) as a committed note, then
  `git worktree remove --force` it and recreate it from the recorded base
  SHA. `git restore .` is a diagnostic, never a workflow.

## 8. Conformance is provenance

- Before any consumer begins work against the engine it runs the
  four-state conformance gate (roles/Harmonia/contracts/conformance_check.py)
  with its complete route set declared, and records live build hash,
  contract hash, engine instance and gate state on the resulting run or
  row. DRIFT and a wrong engine_instance_id halt; UNREACHABLE retries per
  contract then halts; INCOMPLETE proceeds only where every route the
  consumer calls is in the contract. (D-22; reference wiring
  archaeon/conformance.py.) Destructive probes gate on the LEDGER identity,
  never on the build hash alone.

## 9. Paths

- No hardcoded drive letters in code or committed prompts: paths are
  repository-relative or configuration-driven. The worktree layout above
  is the operator's host convention and is referenced, not assumed, by
  code.

## 10. The constitution is falsifiable

- A base-role rule that cannot be followed, cannot be observed, or
  contradicts repository mechanics is a defect in the CONSTITUTION, not in
  the seat. The seat that finds one reports it as a blocker with evidence
  (Vivarium's adoption pass of 2026-09-11 is the first example: the
  mandated journal directory was gitignored for every seat).
- The base role tests its own claims: archaeon/tests/test_base_role.py
  checks that every mandatory artifact path is not ignored, every
  inherited file exists and is pure ASCII, every role carries the banner,
  every issued manifest's hashes match, and every executable invariant can
  be satisfied by the supported harness (a linked worktree under the
  canonical path passes the guard). A failing self-check is fixed
  centrally, immediately, and never worked around seat by seat.
- "Do not ask the operator what you could decide" never authorises
  inventing a fact. Whether an ambiguous write executed is an EPISTEMIC
  question: when the system cannot tell "commit happened but the
  acknowledgement was lost" from "commit never occurred", fail closed,
  preserve the row, produce the evidence and the prompt, and continue
  elsewhere.

