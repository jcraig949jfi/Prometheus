----------------------------------------------------------------------

You're @roles/Eupalamus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Eupalamus --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q1>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Eupalamus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Eupalamus`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-010), 2026-10-07 08:40Z

Fresh HEADLESS session on harry1, same-seat relaunch (operator directive
2026-10-07 s10): C-010-T011 is READY and no Eupalamus instance is live.
Never end on a question. HEADLESS RULE: do NOT use run_in_background at
all; run every test command in the FOREGROUND (timeout <= 600000 ms);
never end your turn while work remains -- the session exits when it ends.

Your packet: C-010-T011 (Q1). Read its TASK.json, comms #(cell notice)
roles/Palamedes/comms/2026-10-07_cell_C010_open.md, rso/witness/
PREREGISTRATION.md s7 (artifact interface) and your own
rso/witness/run_witness.py. Store each receipt's artifact bytes as
artifacts/<sha256> in the bundle, verify sha256 + length against the
receipt, list them in MANIFEST.json node artifacts; keep rows flat
(parent = launch; digest on every COMPLETED row). Cadmus (C-010-T010)
is changing ares_client.py in parallel to return artifact bytes: build
against the current receipt_dict plus a narrow seam (e.g. receipt_dict
returning (rec, {sha256: bytes})) and say in your receipt which seam you
assumed. Do not edit ares_client.py, ruler.py or evaluate.py. Plumbing
tests only (tiny config, random population, temp dir). No registered
subject run, no statistic.

Claim (state commit to main; push = claim), RED first, implement,
GREEN, python -B -m unittest discover -s rso/witness/tests -t . and the
rso/binding suite, receipt, INTEGRATION_READY, push branch
eupalamus/c010-t011, comms note to Palamedes --task-ref C-010-T011.
Mechanics: worktree C:/Prometheus-worktrees/eupalamus-c010-t011
(checkout timeout >= 600 s); canonical fetch-only; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202. Then close and stop.
----------------------------------------------------------------------
