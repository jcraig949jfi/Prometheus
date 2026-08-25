# Provenance note — a shared-worktree collision, recorded rather than rewritten

**Seat:** Lexis · **Date:** 2026-08-25

## What happened

`roles/Lexis/SESSION_2026-08-25.md` and `roles/Lexis/EXTERNAL_REVIEW_REQUEST_2026-08-25.md` were
written by Lexis and are Lexis's work. They are committed in **`438c16ee`**, whose message reads
*"Aporia SELECTOR pre-flight: VACUOUS — the DV cannot vary, and the one positive is a constant."*

The cause is `.git/index.lock` contention on a worktree with several agents committing at once. My
`git add roles/Lexis` staged the two files; before my `git commit` could take the lock, another
seat's commit took it and swept the already-staged paths into its own commit. Same mechanism family
as `feedback_autostash_empty_diff_is_not_committed`: the working tree looked clean afterwards, and
"clean" did not mean "committed by me."

## Verification, not assumption

Per the standing rule that a clean `git status` proves nothing on its own, the content was checked
against the committed blob rather than the file on disk:

- `git cat-file -e HEAD:<path>` — both present.
- `git show HEAD:roles/Lexis/SESSION_2026-08-25.md | grep -c "484,218"` → 1
- `git show HEAD:roles/Lexis/EXTERNAL_REVIEW_REQUEST_2026-08-25.md | grep -c "BEGIN REVIEWER BLOCK"` → 1
- `git merge-base --is-ancestor 438c16ee origin/main` → true. Already pushed.

**Content is intact and on `origin/main`. Only the attribution is wrong.**

## Why it was not fixed by rewriting

`438c16ee` is already on the remote and other seats have pulled from it. Rewriting it would rewrite
shared history for every agent on this repo to correct a commit message — a much larger hazard than
a misattributed message. This note is the correction.

## Two pieces of shared state flagged for James, not touched

1. **A leftover `.git/rebase-merge/` directory.** Its todo list is empty and `HEAD` is on
   `refs/heads/main`, so it is stale debris rather than an interrupted replay — but while it exists
   every `git status` in this worktree prints *"You are currently rebasing."* That is a false alarm
   every agent here will read. Removing it belongs to whoever started the rebase; I have not touched
   it.
2. **Two local commits ahead of `origin/main`** belonging to other seats at the moment this was
   written.

## The durable lesson

On a worktree with concurrent agents, `git add` followed by a separate `git commit` is not atomic,
and the window is wide enough to lose authorship. Prefer `git commit <paths>` (which stages and
commits in one operation) over `git add <paths>` then `git commit`, and always verify the commit
that actually contains your work with `git log -- <path>` rather than inferring it from a clean
status.
