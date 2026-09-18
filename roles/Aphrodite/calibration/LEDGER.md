# Aphrodite calibration ledger

Currency: 2026-09-17. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice

2026-09-17 | Asked to "pull the latest from github", ran `git stash push` and `git pull --ff-only` in the canonical checkout (after resolving a leftover stash conflict there), BEFORE reading roles/base-role/WORKING_CONTRACT.md | s1 and s3 forbid pull and stash in the canonical checkout; a pull that MOVES it is an incident, not a boot transient (HYPATIA-08 ruling). This one moved it a6969bfbb -> b70d4f76e (869 commits, fast-forward). No local work was lost: the tracked changes were stashed and popped back cleanly | the seat itself, on reading the contract in the same session | "pull the latest" is read as WAKE_DIRECTIVE.md means it: fetch, record origin/main, worktree add. The base role is read before any mutating git command, never after
