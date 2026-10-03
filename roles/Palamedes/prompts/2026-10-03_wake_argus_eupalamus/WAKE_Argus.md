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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-004), 2026-10-03

You are running as a fresh HEADLESS session on harry1 (M4), started by
Palamedes on the operator's instruction (roles/Palamedes/prompts/
2026-10-03_wake_argus_eupalamus/00_README.md). Nobody will answer
questions in this session: never end on a question; escalate in the
DISTRIBUTED_WORK s6 shape and continue what does not depend on it.

Your packet: C-004-T002 (owner_role Argus, READY, dependencies satisfied). After the
boot steps, claim it (state commit, push = claim), do it exactly as the
packet says, write attempts/A-NNN/RECEIPT.json, move it to
INTEGRATION_READY, push your work branch, and post the task notes to
Palamedes (CLAIMED, INTEGRATION_READY) with --task-ref C-004-T002. Palamedes
integrates. If the claim push shows the packet already CLAIMED by another
instance of your seat, you lost the race: say so in a note and stop.

Mechanics on this host:
- Worktree root C:/Prometheus-worktrees/ (e.g. C:/Prometheus-worktrees/argus-c004-t002); canonical checkout
  C:/Prometheus is fetch-only. Never git pull.
- No git identity is configured here: commit with
  git -c user.name=jcraig949jfi -c user.email=jcraig@jfi.ai commit -F <file>
- EW_DB_HOST=192.168.1.202 for every comms/workgraph call (not M1).
- Wrap git/network calls in timeouts; worktree add needs >= 900 s.
- Your roles/Argus/WORK_STATE.json on main is invalid JSON (line 11,
  unescaped backslashes in worktree_path); fix it in your first commit.
- Draft A (Cadmus, C-004-T001) is on main at
  rso/slice001/contract/drafts/A_world_reset_observer.md. Read it so
  draft B meets it at the receipt boundary; do not edit it. Its FD-A3
  CHANNEL clamp is a proposed clause Palamedes resolves at T004.
- Operator rulings are recorded in C-004-OP1..OP3 (all CLOSED): custody is
  operator authority with Aporia as registrar (OP-2); write the C5 field
  for that, not NONE.
Scope: this packet only. When it is INTEGRATION_READY and pushed, do the
session close (base RESPONSIBILITIES s7) and stop; do not take further
packets in this session.
----------------------------------------------------------------------
