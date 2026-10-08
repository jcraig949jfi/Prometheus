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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07 07:20Z

Fresh HEADLESS session on harry1, claude-fable-5-1 (Q3): same-seat
relaunch (operator directive 2026-10-07 s10). C-009-T034 is READY, Q3,
can_downgrade false; the live Pallas session (m2-1500b878) is Opus 5
(Q2) and declined it (#1786). Nobody answers questions here: never end
on a question; escalate in the DISTRIBUTED_WORK s6 shape and continue.

HEADLESS RULE (your own seat lost a session to this on T030): never end
your turn while work remains -- the session exits when the turn ends.
Run long jobs in the FOREGROUND with a timeout (<= 600 s per call; split
the mutation driver into per-edit calls if needed) or poll a background
job from a foreground until-loop.

Your packet: C-009-T034, the ONLY re-check CC3 allows. Read its
TASK.json, comms #1785 (roles/Palamedes/comms/2026-10-07_pallas_T034.md),
rso/binding/FREEZE_B2.md (verify every hash against the committed bytes
first), rso/binding/ADJUDICATION_CC3.md, rso/binding/CONTRACT.md
(s6 v1.0.1, s7 v1.1.0 BX5b), rso/binding/R1/R2CHECK/REGRESSION.md, the
T031 receipt (declared escapes, e.g. FD-T031-1), and your own B1 REPORT.
Write the exposure record first.

Set: 1 fresh sound, 1 fresh broken, 1 semantic edit on BX1 / BX2 /
BX5-BX5b, committed BEFORE any outcome; not the CC1 or B1 shapes. You
may reuse your B1 drivers. <= 3 launches (8 of 12 used), every launch
and mutation child on rso/binding/LEDGER.jsonl. Report CLOSED / NOT
CLOSED for BX1, BX2, BX5 and every survivor with its applicability to
the native witness path (rso/witness/ares_client.py, run_witness.py).
You never repair production code.

Claim (state commit to main; push = claim), set, run, rows, REPORT.md
under rso/binding/challenge/B2/, receipt, INTEGRATION_READY, comms to
Palamedes --task-ref C-009-T034. Mechanics: worktree C:/Prometheus-
worktrees/pallas-c009-t034 (checkout timeout >= 600 s); canonical
fetch-only; git -c user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on
every commit AND rebase; EW_DB_HOST=192.168.1.202. Then close and stop.
----------------------------------------------------------------------
