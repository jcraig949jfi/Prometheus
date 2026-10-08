# Cosmos FREEZES (append-only chain)

Currency: 2026-09-28. Machine-checked: every file freeze is RE-HASHED on each check, so a superseded
freeze that was edited or deleted fails the check. Each entry: `### <id> | <title>` then keys kind
(file | git), target (repo path, or commit id), sha256 (file: LF-normalised, comms/manifest.py
convention; git: -), supersedes (freeze id or -), review (PRE_RESULT_REVIEW verdict id or PENDING or
N/A), status (ACTIVE | SUPERSEDED | SPENT).
A repair never edits an entry: it appends a new freeze whose `supersedes` names the old id, and the old
entry's status is set to SUPERSEDED. Only two fields may ever change: status, and review (once,
from PENDING to a verdict id).
A git freeze whose commit is absent from the local object store is reported UNVERIFIABLE_HERE, which
is not a failure. Example: a local-only commit checked from another machine.

### F-0000 | C3 withheld-branch commitment (published 2026-09-24 in roles/Cosmos/c3/INFO_LEDGER.md)
- kind: git
- target: 0ecafed159f9bc9756baefd55ec37fd75b83b822
- sha256: -
- supersedes: -
- review: N/A
- status: ACTIVE

### F-0001 | C4 gate S0 trivial rules and baselines (preregistered before any C4 law search or S0 number)
- kind: file
- target: roles/Cosmos/c4/S0_TRIVIAL_RULES.md
- sha256: 75125607cff4b40b2ac4676e5e7536787cb1201e9a06b5e268960cb7355fd66c
- supersedes: -
- review: PENDING
- status: ACTIVE

> 2026-10-08 note on F-0000: its target (0ecafed1, ancestor of e73e5eb26) is now PUBLIC on main via the C3 S1
> publication merge d75fb45ef and is re-checkable by anyone. F-0000 itself is unchanged.
