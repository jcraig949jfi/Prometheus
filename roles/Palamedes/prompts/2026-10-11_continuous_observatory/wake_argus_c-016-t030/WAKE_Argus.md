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

Your packet: C-016-T030. Read ops/campaigns/C-016/tasks/C-016-T030/TASK.json.
ENSORAIN ISOLATION (directive s3): Ensorain's WTP-05 DEEP is running on
ubu006 now (ETA ~2026-10-11T13:00Z). Read-only: never edit ensorain/ or
roles/Ensorain/, never use a WTP-05 registered seed, never run anything on
ubu006. Work against a pinned SHA in your own worktree.

Your packet's TASK.json `problem` field holds the coordinator's decision
and every design constraint: read it twice. Read rso/ensorain/
COMPATIBILITY.md in full (Cadmus, integrated) and re-run its demand check
(python -m rso.ensorain.rerun_c_demand <scratch.json>, ~4 s) before
building on it.

Build the SMALLEST adapter: reuse registry components within their scope
and record in rso/ensorain/ONBOARDING.md every component reused, modified,
or found too narrow, plus bespoke adapter line counts (aspiration ~500;
never drop a control to meet it). The Smuggler analogue and the external
declared-memory check are new work: build them in the RSO lane. Write
PREREGISTRATION.md (question as reworded, subjects, controls, endpoint,
decision rule, N with the power computation, resources per directive s13)
and a freeze manifest (LF-normalised sha256) BEFORE any subject outcome.
Development runs use their own dev seeds (declare the range) and are never
the confirmatory data. Do NOT run the confirmatory experiment: a Q3
challenge (Pallas) of the frozen surface comes first.

If a design choice needs Ensorain to change its code, stop that branch,
write the request (comms body under roles/Argus/comms/, to Ensorain via
Palamedes) and continue the rest.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-016-T030. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c016-t030 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
