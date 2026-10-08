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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07

Fresh HEADLESS session on harry1 (M4), claude-fable-5-1 (Q3): same-seat
relaunch (operator directive 2026-10-07 s10). C-009-T030 is READY, it is
Q3 with can_downgrade false, and no Q3 Pallas instance is live (your last
session ran claude-opus-5, Q2; you planned this relaunch yourself in
97606378c). Nobody answers questions here: never end on a question;
escalate in the DISTRIBUTED_WORK s6 shape and continue. Directive:
roles/Palamedes/prompts/2026-10-07_rso_completion_push/
01_OPERATOR_DIRECTIVE_verbatim.md.

Your packet: C-009-T030, the CC3 independent challenge on the frozen
binding surface. Read ops/campaigns/C-009/tasks/C-009-T030/TASK.json,
rso/binding/FREEZE_B1.md (verify its hashes against the committed bytes
before writing anything), rso/binding/CONTRACT.md (BX1-BX7 and the s6
v1.0.1 clarification), rso/binding/R1/REGRESSION.md, and the T011 and
T010 receipts (their declared escapes). Write your exposure record
first, as in R2.

CC3: at least 1 fresh sound case, 2 fresh broken cases and 2 semantic
edits on the binding path (rso/binding/binding.py; evidence.py g_inv /
launch_unbound / custody; producer ledger.py + s2_bundle.py), committed
BEFORE any outcome. Fresh: not the CC1 shapes (S3 RUN_BORROW, S4
OBS_RUN_BORROW/X3, STALE_RUN, Y1, LATER_WINDOW, OVERLAP, FAILED_ROW,
ARTIFACT_SWAP, LAUNCH_SUBSTITUTION), which are T011 regressions. Report
each surface CLOSED / NOT CLOSED and every survivor, stating whether it
is applicable to the path a native witness would use (receipts bound
through rso.binding, custody QUALIFIED required by s6). Charge every
launch and mutation child to rso/binding/LEDGER.jsonl (<= 3 launches;
5 of 12 used). You never repair production code.

Claim (state commit to main; push = claim), set, run, rows, REPORT.md,
receipt, INTEGRATION_READY, comms to Palamedes --task-ref C-009-T030.
Mechanics: worktrees under C:/Prometheus-worktrees/ (pallas-c009-t030;
checkout needs a timeout of at least 600 s); canonical C:/Prometheus
fetch-only, never pull; git -c user.name=jcraig949jfi -c
user.email=jcraig@jfi.ai on every commit AND rebase; EW_DB_HOST=
192.168.1.202; timeouts on git/network. This packet only; then close
(base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
