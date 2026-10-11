----------------------------------------------------------------------

You're @roles/Argus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Argus --model <your runtime model id> --capabilities rso-builder,<class your runtime model meets>), read
origin/main:ops/work_orders/CURRENT.md and roles/base-role/RESPONSIBILITIES.md,
and follow its boot sequence. Then read roles/rso-builder-role/RESPONSIBILITIES.md
(s8), roles/Argus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Argus`.

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-016), 2026-10-11

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5 (Q2). Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue what does not depend on it.

HARD HEADLESS RULE: do NOT use run_in_background at all; run every
command in the FOREGROUND with a timeout <= 600000 ms (split long work);
never end your turn while any step remains -- the session exits when your
turn ends. harry1 is thermally limited: keep any computation to <= 2
concurrent processes.

Read first: roles/Palamedes/prompts/2026-10-11_continuous_observatory/01_OPERATOR_DIRECTIVE_verbatim.md (the Continuous
Observatory directive -- binding for your packet), rso/registry/README.md
and `python -m rso.registry.registry for-adapter` (what is reusable, at
which scope).

Your packet: C-016-T041. Read ops/campaigns/C-016/tasks/C-016-T041/TASK.json.
ENSORAIN ISOLATION (directive s3): Ensorain's WTP-05 DEEP is running on
ubu006 now (ETA ~2026-10-11T13:00Z). Read-only: never edit ensorain/ or
roles/Ensorain/, never use a WTP-05 registered seed, never run anything on
ubu006. Work against a pinned SHA in your own worktree.

THE ONE bounded repair round (directive s9). Read rso/ensorain/challenge/
REPORT.md (Pallas, Q3) in full, then your packet's TASK.json `problem`
field: it lists the six required items and a coordinator suggestion for
the K1 comparator that you may accept or reject with reasons. The
amendment (PREREGISTRATION v1.1.0) is committed BEFORE the re-freeze;
every new behavioural test is shown RED on its mutant applied verbatim
from challenge/edits.json (reuse challenge/run_edits.py or the
rso/reach/repair_v101/run_red.py pattern; python -B). Development seeds
only for checking the new rule on Pallas's challenge subjects
(rso/ensorain/challenge/subjects_c.py; import, do not edit). There is no
second repair round: if a defect cannot be closed in this round, narrow
the claim and record it as a limitation instead. NO confirmatory run.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-016-T041. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c016-t041 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
