----------------------------------------------------------------------

You're @roles/Pallas Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Pallas --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q3>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Pallas/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Pallas`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07 04:20Z

RESUME of C-009-T030 by a fresh HEADLESS Pallas session on harry1,
claude-fable-5-1 (Q3). Your previous headless instance
(harry1-b97f1fc4) claimed T030, committed the challenge set before any
outcome (1b9c19ba9) and a driver repair (9f58a0cef), ran launch 1
(cases) and started launch 2 (mutation) -- then ENDED ITS TURN to wait
for the background run. A headless `claude -p` session exits when its
turn ends, so the session stopped and its mutation child died at about
03:47Z. Nothing after 9f58a0cef is committed.

READ THIS FIRST -- headless rule: never end your turn while work
remains. Run long jobs in the FOREGROUND with a timeout (<= 600 s per
call; split the run if needed) or poll a background job with a
foreground until-loop; do not "resume when it reports completion".
The session ends the moment you stop.

You are the same seat continuing the same lease (LEASE.json names
harry1-b97f1fc4, your dead instance): record a
history note "resumed by Pallas[<your instance>] after headless exit of
harry1-b97f1fc4" and continue; this is not a new claim.

State on disk (uncommitted, in C:/Prometheus-worktrees/pallas-c009-t030,
branch pallas/c009-t030): results_cases.jsonl (launch 1 rows),
dry_controls_*.jsonl, mutation_rows.jsonl (partial, launch 2),
mutation_stdout.txt (empty), diag_keeper.py + diag_keeper_output.txt.
Ledger: inspect rso/binding/LEDGER.jsonl in that worktree for the
launch-2 START without END (torn attempt). Your call, recorded in the
report: keep the partial launch-2 rows as censored and re-run the
mutation driver as launch 3 (<= 3 launches allowed; 5 of 12 used before
T030), or another honest disposition. Do not change the committed set.

Then finish exactly as T030 says: rows, REPORT.md (CLOSED / NOT CLOSED
per binding surface, every survivor and whether it applies to the path
a native witness would use), receipt, INTEGRATION_READY, comms to
Palamedes --task-ref C-009-T030. You never repair production code.
Mechanics as before: git -c user.name=jcraig949jfi -c
user.email=jcraig@jfi.ai on every commit AND rebase; EW_DB_HOST=
192.168.1.202; canonical C:/Prometheus fetch-only. Then close and stop.
----------------------------------------------------------------------
