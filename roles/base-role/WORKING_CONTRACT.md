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

- Work only in that worktree. Never place a worktree under the canonical
  checkout's own directory, and never under a session-temporary
  scratchpad for anything that must outlive the session.
- Record the base SHA the branch was created from. It goes in every
  receipt (section 4).
- Long-lived seat branches are retired; task branches replace them.

## 3. Never `git pull`

- Fetch, then merge or rebase EXPLICITLY from a named SHA:
  `git fetch origin && git merge <sha>`. Every state transition is then
  observable and recorded. A `pull` fetches and rewrites the tree in one
  invisible step; it is forbidden.
- Wrap git calls in a timeout. If a command times out, do not retry in a
  loop; look at the tree, then act once.
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
