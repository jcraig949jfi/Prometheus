MISSIVE TO EVERY SEAT -- WORKSPACE HYGIENE IS NOW AN ECOSYSTEM INVARIANT
(operator, 2026-09-11, via Archaeon; applies to Archaeon, Vivarium, Daedalus,
Techne, Harmonia, Herakles, Proteus, Mnemosyne, Elenchus, Aporia, and every
Necropolis/Necromancer seat)

WHY. The canonical checkout F:\Prometheus has twice lost ~11,000 tracked
files from disk with HEAD and index intact and nothing staged -- the
signature of an interrupted or concurrent working-tree rewrite, not of a
deletion. Today it sits on a branch that no longer exists on origin
(vivarium/v0-2026-09-05) with 35 modified tracked files and 96 untracked
files that belong to at least six seats. Several seats run long-lived
processes from worktrees INSIDE that directory. Lost files set us back.
Sharing a repository is safe; sharing a mutable working directory is not.

THE INVARIANT (D-23)
1. F:\Prometheus is the CANONICAL CLONE. It is read-mostly: fetch,
   inspection, and worktree management only. NO seat performs a mutating
   git operation there (checkout, switch, pull, merge, rebase, reset,
   restore, cherry-pick, branch creation) and NO seat edits, creates or
   deletes source files there. A seat whose working directory resolves to
   the canonical checkout must REFUSE to run (detect it: `git rev-parse
   --git-dir` equals `git rev-parse --git-common-dir` only in the main
   worktree). Archaeon's guard is archaeon/workspace.py; copy the check.
2. EVERY SEAT WORKS IN ITS OWN WORKTREE on a SHORT-LIVED BRANCH, created
   from a recorded base SHA:
       git -C F:\Prometheus fetch origin
       git -C F:\Prometheus worktree add F:\Prometheus-worktrees\<seat>-<task> ^
           -b <seat>/<task> origin/main
   Work only there. Never place a worktree under F:\Prometheus\ itself
   (F:\Prometheus\.claude\worktrees\... moves out) and never under a
   session-temporary scratchpad for anything that outlives the session.
3. NEVER `git pull`. Fetch, then merge or rebase EXPLICITLY from a named
   SHA (`git merge <sha>`), so every state transition is observable.
4. EVERY RECEIPT RECORDS base_sha, branch, worktree_path (and whether the
   tree was dirty). "Built from a15e12ffe in F:\Prometheus-worktrees\..."
   is the form. Archaeon's `workspace.receipt()` is one way to get it.
5. INTEGRATE by fast-forwarding origin/main after tests pass on the merged
   tree (`git push origin <branch>:main` only when origin/main is an
   ancestor); then `git worktree remove` the worktree and `git branch -d`
   the branch. Long-lived seat branches end today; task branches replace
   them.
6. LONG-RUNNING PROCESSES (consumers, ticks, engines) run from a PINNED
   worktree checked out DETACHED at a recorded SHA under
   F:\Prometheus-worktrees\<seat>-<process>, advanced only by an explicit,
   logged command after tests; their receipts carry that SHA.
7. DIRTY OR CORRUPT WORKTREE = DESTROY, DO NOT NURSE. If a worktree reports
   missing tracked files, preserve the diagnostics (`git status --short`,
   the missing-file list, the process list) as a committed note, remove
   the worktree, and recreate it from the recorded base SHA. `git restore .`
   is a diagnostic, never a workflow.

CLEAN-UP, EACH SEAT, TODAY
a. Claim your files in the canonical checkout. The snapshot is committed
   beside this missive (CANONICAL_STATUS_2026-09-11.txt: 35 M + 96 ??).
   For each of yours: commit it from YOUR worktree if it is work, or
   delete it from the canonical checkout if it is scratch -- deletion of
   YOUR OWN untracked scratch there is the one permitted write, done once,
   and reported. Files nobody claims by 2026-09-12 are listed for the
   operator, not deleted.
b. Remove every worktree you created that is stale, detached and idle, or
   under a temp path that has outlived its session (`git -C F:\Prometheus
   worktree list`, then `worktree remove` / `worktree prune`). Delete
   every branch of yours that is merged into origin/main.
c. Move any long-lived process you run out of F:\Prometheus\ and out of
   temp paths into a pinned worktree (rule 6); restart it at a quiet
   moment you announce; record the SHA it runs.
d. Add the startup refusal (rule 1) to every entry point you own.
e. Report: your worktree path(s), branch(es), base SHA(s), what you claimed
   or deleted in the canonical checkout, and the SHA of the commit that
   records it.

Archaeon's own compliance, done first and committed with this missive:
the refusal guard and the workspace receipt on its entry points; its
scheduled tick moved to a pinned worktree F:\Prometheus-worktrees\archaeon-tick;
archaeon/v0 retired as a long-lived branch in favour of task branches.
