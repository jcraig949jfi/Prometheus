# Aether wake block -- paste this to boot this seat

Currency: 2026-09-23.

This is `roles/base-role/WAKE_DIRECTIVE.md`'s conformant wording with
this seat's name filled in and its task line supplied. The base file is
the template and is not edited here: the task line is exactly the slot
it reserves for "<task line, if any>", so an Aether-specific
instruction belongs here, in Aether's own lane, and not in the shared
block every seat pastes.

----------------------------------------------------------------------

You're @roles/Aether Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Aether --model <id>), read
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Read roles/Aether/TODO.md first.

----------------------------------------------------------------------

## The branch clause was RETIRED 2026-09-23

The task line briefly read:

    Work from branch aether/aeth01-memwall-2026-09-22, not main. Read
    roles/Aether/TODO.md first.

It is gone because the condition it named has been met. The branch was
merged to main at `183388e39` and `origin/main` now carries the whole
lane; the check it set for itself passes:

    git ls-tree --name-only origin/main roles/Aether/
      -> BACKLOG_H0H5, RESPONSIBILITIES, STATUS, TODO, WAKE,
         calibration, journal, prompts
    git ls-tree --name-only origin/main Aether/
      -> AETH-01, AETHER_*, notes, observatory, production, runpod, test

A boot from `origin/main` now finds `roles/Aether/TODO.md` and the
standing directive without being told where to look, which is the whole
point: a seat should not need oral tradition to find its own work. The
clause was removed rather than left as a comfort, because the next task
branch will have a different name and a wake block naming a dead branch
is a trap of its own.

## The history it came from

For about an hour on 2026-09-23 the AETH-01 lane, the AETH-02
directive, `TODO.md` and the `CURRENT DIRECTIVE` block existed only on
a task branch. `origin/main` had no `Aether/` directory at all and a
`roles/Aether/RESPONSIBILITIES.md` that was still the stale pre-charter
version with no pointer in it, so a seat following the base wake block
literally would have built its worktree from `origin/main`, found none
of the lane, and reasonably concluded it had no standing work.

That is recorded because the failure mode is general and will recur:
any lane that accumulates durable state on a long-lived task branch is
one bootstrap away from looking empty. Integration is not housekeeping
for such a lane; it is recoverability.
