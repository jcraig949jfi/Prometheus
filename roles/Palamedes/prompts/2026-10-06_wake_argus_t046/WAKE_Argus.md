----------------------------------------------------------------------

You're @roles/Argus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Argus --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q2>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Argus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Argus`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-004), 2026-10-04
----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-004), 2026-10-06

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5, started by
Palamedes because no Argus instance is live. Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue.

Your packet: C-004-T046, the SECOND AND FINAL repair round (operator
OP6; no third round exists). Read
ops/campaigns/C-004/tasks/C-004-T046/TASK.json,
ops/campaigns/C-004/tasks/C-004-OP6/TASK.json (ruling verbatim),
rso/slice001/contract/AMENDMENT_v1.0.5.md,
rso/slice001/challenge/S4/REPORT.md and its closure_set/ (cases
S4.SOUND.REPRODUCED, S4.BROKEN.OBS_RUN_BORROW, S4.PROBE.STALE_RUN, edit
X3), and comms #1681.

Three items in evidence.py (checker.py only if needed), each RED first:
  C1   choose the registered manifest whose node artifacts actually
       match the presented receipts, not the earliest node-set match.
  C2   bind G-INV run evidence to the receipt's specific observer;
       S4 edit X3 must be killed by a test.
  B3.3 (v1.0.5) an earlier-window run of the same node does not satisfy
       a later receipt -> RECEIPT_WITHOUT_RUN:<node_id>.
Then regenerate the G-BIND / G-INV / G-RECOMP stage records (canonical
bytes, new fire receipts; list paths + sha256 in your receipt) and apply
contract.json v1.0.5 (version + amendments entry only) in the same
commit as the test that pins the contract version; make that pin robust
to future amendments. Replay the S4 closure cases with the reviewer's
committed driver on a throwaway ledger (development, not ledgered).
Do not modify fixtures/world_cases.py, the S3/S4 records, or the
tables. No ledgered launch: one final `python -B -m rso.slice001.ci`
only if the ledger requires it (5 launches remain for the whole
campaign; T048 needs up to 3).

Claim (state commit to main; push = claim), RED, implement, GREEN,
receipt, INTEGRATION_READY, push branch argus/c004-t046, comms to
Palamedes. Heartbeats while working and on state transitions only.

Mechanics: worktrees under C:/Prometheus-worktrees/ (argus-c004-t046);
canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai commit -F <file>;
EW_DB_HOST=192.168.1.202; timeouts on git/network.

This packet only; base RESPONSIBILITIES s7 close; stop.
----------------------------------------------------------------------
