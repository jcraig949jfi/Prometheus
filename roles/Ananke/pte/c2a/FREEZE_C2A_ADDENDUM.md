# FREEZE_C2A addendum: SHA mapping after a pre-push rebase (written before any production row)

FREEZE_C2A.json names code_sha 3a9b96507. That is the local code commit before `git rebase origin/main`. The push
carried the rebased commits:

- code commit:   4cdc2e15b11e11c107f6628ed3bc18ce54dfdd34 (the rebased 3a9b96507)
- freeze commit: a5049119eae9ffa0d161ebba274bcc5249ecdc79

Verified before launch, at both rebased commits:
- every file in FREEZE_C2A.json code_files matches its sha256 (LF-normalised);
- PLAN_C2A.json and PREREG_PTE_C2A.md match plan_sha256 and prereg_sha256;
- `git diff 3a9b96507 4cdc2e15b -- prometheus/ananke` is empty, so the engine is identical.

Production runs from a worktree pinned (detached) at the freeze commit a5049119e.
