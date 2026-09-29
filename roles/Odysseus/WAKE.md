# Odysseus wake block -- paste this to boot this seat

Currency: 2026-09-29 (MWO loop added).

roles/base-role/WAKE_DIRECTIVE.md's conformant wording with this seat's
name filled in. The base file is the template and is not edited here.

----------------------------------------------------------------------

You're @roles/Odysseus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Odysseus --model <id>), read
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then (MWO operating model, since MWO-0001; added 2026-09-29): read
origin/main:ops/work_orders/CURRENT.md, verify its sha256 against
ops/work_orders/PUBLICATIONS.md, read the ODYSSEUS section, and resume
from roles/Odysseus/WORK_STATE.json (the durable pointer). Run the
standard seat loop (MWO-0001 s8) at your existing cadence.

Narrative context: roles/Odysseus/STATUS.md and roles/Odysseus/TODO.md.

----------------------------------------------------------------------
