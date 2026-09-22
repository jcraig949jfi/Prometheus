# The wake directive (conformant wording for the operator to paste)

Currency: 2026-09-17 (Herakles, adding the comms host line under the
operator's ruling of that day: all agents use comms on the M1 database).
Previously 2026-09-11 (Archaeon, on Hypatia #90 and Atalanta L-09: two
seats ran `git pull` in the canonical checkout because the directive they
were woken with said "Pull the latest from the repo first", and they read
WORKING_CONTRACT.md s3 only afterwards). The directive's source is the
operator's chat template; this file is the replacement text. Paste the
block; edit only the seat name and the task line.

----------------------------------------------------------------------

You're @roles/<Seat> Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot <Seat> --model <id>), read
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

<task line, if any>

----------------------------------------------------------------------

What the wording guarantees: the first three commands a fresh seat can
literally execute are all conformant (fetch, rev-parse, worktree add), so
a seat that acts before it reads still cannot mutate the canonical tree.
A seat that was woken with the OLD wording and pulled a no-op before
reading s3 records it as a boot transient (s3 ruling); it is not chased.
The comms host line (2026-09-17) exists because a seat booting on M2, M3
or M4 with EW_DB_HOST unset resolves to localhost and is refused with
WRONG_ENVIRONMENT (or, on a host with a same-named local cluster, reaches
a quarantined fork); the guard makes the mistake loud, this line makes it
rare.
