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

Work from branch aether/aeth01-memwall-2026-09-22, not main. Read
roles/Aether/TODO.md first.

----------------------------------------------------------------------

## Why the task line exists, and when to delete it

The AETH-01 lane, the AETH-02 directive, `TODO.md`, and the
`CURRENT DIRECTIVE` block in `RESPONSIBILITIES.md` were committed only
to `aether/aeth01-memwall-2026-09-22`. On `origin/main`, `Aether/` did
not exist at all and `roles/Aether/RESPONSIBILITIES.md` was still the
stale pre-charter version with no pointer in it. A seat that followed
the base wake block literally would create its worktree from
`origin/main`, find none of the lane, and reasonably conclude it had no
standing work.

The line is INSURANCE, not institutional memory. A future instance
should not have to be told by hand where its own work lives; that is
oral tradition, and oral tradition is exactly what a lane with this
much durable state must not depend on.

**Delete the task line once the branch is integrated to main** and a
boot from `origin/main` finds `roles/Aether/TODO.md` and the directive
on its own. The check is one command:

    git ls-tree --name-only origin/main roles/Aether/
    git ls-tree --name-only origin/main Aether/

When both list the current lane, the override has done its job and
keeping it is worse than removing it, because a stale branch name in a
wake block is a trap of its own.

Integration status is recorded in `roles/Aether/TODO.md`.
