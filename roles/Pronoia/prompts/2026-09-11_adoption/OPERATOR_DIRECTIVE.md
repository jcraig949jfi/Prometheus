# Operator directive -- Pronoia adoption pass, 2026-09-11

Recorded verbatim. The verbatim directive beats any summary of it,
including this seat's own (base role, boot step 2).

Received 2026-09-11 in the Claude Code session that produced
roles/Pronoia/. Line breaks and spacing as received; the "@" forms are
the harness's path-reference syntax.

---BEGIN VERBATIM---
You're @agents\pronoia\ You were an agent back in April but haven't been seated since.  Bootstrap and then create a role for yourself in the @roles\ directory like the others.  Adhere to the base-role concept.  Pull the latest from the repo first as that's where you'll see the new roles and requirements.  Don't do anything other than this bootstrap and registration except remind me what you did when you were active
---END VERBATIM---

## How this seat read it

Four instructions and one prohibition.

1. BOOTSTRAP. Base-role boot sequence, in order (RESPONSIBILITIES.md
   section 1): worktree guard, entry files, sibling commits, doctrine,
   manifest hashes, suggest work, comms sync, feed watchdogs.

2. CREATE A ROLE UNDER roles/ LIKE THE OTHERS. roles/Pronoia/ with the
   entry file, status, backlog, journal, calibration ledger and prompts,
   in the shape the seats adopted earlier the same day used, plus this
   seat's own two rows in INHERITANCE.md and MONITORS.md.

3. ADHERE TO THE BASE-ROLE CONCEPT. roles/base-role/ is the
   constitution; this seat's files add to it and may not contradict it.

4. PULL THE LATEST FIRST. Read literally at first and acted on, which
   was an error: D-23 section 3 states that a wake directive saying
   "pull the latest first" MEANS fetch, record origin/main, then
   worktree add, and that a seat which pulls before reading the contract
   has violated sections 1 and 3 without knowing. The `git pull` was
   killed before it reached a mutating step and the canonical tree was
   verified unchanged. Recorded as PRON-CAL-004. The clause in D-23
   exists because Atalanta made the identical mistake earlier the same
   day (L-09).

5. THE PROHIBITION: "Don't do anything other than this bootstrap and
   registration except remind me what you did when you were active."

   Read as: no loop started, no loop stopped, no process on M4 touched,
   no file deleted, no dashboard or brief regenerated, no email sent, no
   scheduled task created, no other seat's document rewritten, no claim
   promoted. Measurement and reading are part of "remind me what you did
   when you were active" and were performed; every one of them was
   read-only against the repository, the host filesystem and the
   canonical Postgres.

   The one thing this pass found that would normally demand action -- a
   runnable, untracked, gitignored pronoia.py on M2 whose publish step
   pushes to main from the canonical checkout -- was RECORDED AND NOT
   TOUCHED, because deleting an untracked file on a shared host is
   destructive and outward-facing and the prohibition is explicit. It is
   PRON-02 with a recommendation attached.

## What "remind me what you did when you were active" turned out to mean

The directive assumes one active period. There were two, four months
apart, under one name, and the repository record conflates them:
Era 1, the pronoia.py research-scanning orchestrator (2026-03-23 to
2026-04-01, deleted 2026-04-23), and Era 2,
scripts/intelligence_loop.py, the fleet-visibility loop, which is
running on M4 right now. Both are reported. The second was not expected
by this seat at the start of the pass and is the reason the pass
produced a finding rather than only an inventory.
