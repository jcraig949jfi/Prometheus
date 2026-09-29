# Ensorain: resume procedure (MWO seat loop)

A fresh session pointed at roles/Ensorain needs nothing else. Do this, in order.

1. Worktree: `D:\Prometheus-worktrees\ensorain-base-role`, branch `ensorain/base-role-adopt-2026-09-23`.
   - Never `git pull`. Fetch only; fast-forward only when work needs new code.
   - On M2, set `EW_DB_HOST=192.168.1.202` for comms and Fabric.
2. `git fetch origin`. Read `origin/main:ops/work_orders/CURRENT.md`.
   - Verify it with `git show origin/main:<archive path> | sha256sum` against `ops/work_orders/PUBLICATIONS.md`. Never
     hash the CRLF working file.
   - Compare its MWO ID with `roles/Ensorain/WORK_STATE.json` `mwo_id`.
   - If it is new: read the whole order (its ENSORAIN items and any census or seat instruction), adopt it, and update
     WORK_STATE.
3. `python -m comms boot Ensorain --model <model id>` once per session, then `python -m comms sync Ensorain` at every
   loop point.
   - Act only on messages addressed to Ensorain or on real dependencies/conflicts.
   - No idle broadcasts, no ACKs. Git is the durable record.
4. `python -m fabric tasks` / `python -m fabric show <tsk-id>` for the tasks listed in WORK_STATE `fabric_tasks`.
   - Code execution on Fabric uses the `script` executor over a committed file. The `claude` executor cannot run
     python (fabric/README.md D3).
5. Work: WORK_STATE `next_actions`, ensorain/arc3/THREADS.md, ensorain/arc3/HIERARCHY.md.
   - Dev experiments: write the precommitment into the result file and commit it BEFORE the eval run. Debug only on
     held-out seeds.
6. Update WORK_STATE after any material transition. Push the branch, and mirror WORK_STATE to main as a single-file
   commit from a temporary worktree at origin/main.
7. Self-pace with a long wakeup (~30 min) when nothing is pending.

HARD GATE: E-ENS-LM01 (WTP-LM01 v0.3.2, frozen at ee8cbe0c8cb1ef131e6bc8181c8272656eaa5a6e) is NOT LAUNCHED.
- Launch ONLY on an operator-approved MWO containing the exact line
  `LAUNCH WTP-LM01 using frozen prereg <prefix of ee8cbe0c8...>`.
- Before launching:
  - resolve the carrier as that MWO directs (DEF-ENS-001 in DEFECTS.md);
  - take the Fabric lease (`python -m fabric lease acquire <m2 host>:cpu8`);
  - pin a fresh worktree at ee8cbe0c8;
  - verify the freeze (`ensorain/lm01/freeze.py verify`);
  - census the host.

Blind-lane rule: do not message Bellerophon about the program.
Secrets: never read .env, key or credential files (CLAUDE.md).
