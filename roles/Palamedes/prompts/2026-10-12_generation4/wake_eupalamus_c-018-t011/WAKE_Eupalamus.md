----------------------------------------------------------------------

You're @roles/Eupalamus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Eupalamus --model <your runtime model id> --capabilities rso-builder,<class your runtime model meets>), read
origin/main:ops/work_orders/CURRENT.md and roles/base-role/RESPONSIBILITIES.md,
and follow its boot sequence. Then read roles/rso-builder-role/RESPONSIBILITIES.md
(s8), roles/Eupalamus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Eupalamus`.

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-018), 2026-10-12

Fresh HEADLESS session on harry1 (M4), claude-sonnet-5-5 (Q2). Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue what does not depend on it.

HARD HEADLESS RULE: do NOT use run_in_background at all; run every
command in the FOREGROUND with a timeout <= 600000 ms (split long work);
never end your turn while any step remains -- the session exits when your
turn ends. harry1 is thermally limited: keep any computation to <= 2
concurrent processes.

Read first: roles/Palamedes/prompts/2026-10-12_generation4/01_OPERATOR_DIRECTIVE_verbatim.md (the Generation 4
directive -- binding for your packet), rso/registry/README.md
and `python -m rso.registry.registry for-adapter` (what is reusable, at
which scope).

Your packet: C-018-T011. Read ops/campaigns/C-018/tasks/C-018-T011/TASK.json.
BRANCH RULE: commit work to YOUR BRANCH and push it; only state commits
go to main.

Your packet's TASK.json `problem` field is the spec. The frozen C-017 files
under rso/z80/ must NOT change (directive s2A: do not retrospectively change
C-017's frozen result) -- your fixture reads them. The core property: a
missing shard never silently turns the experiment into a smaller one; a
preregistered early stop is declared in the manifest with its trigger and
is distinguishable from unplanned missing evidence. Every corruption kind
gets a test that is RED before the verifier exists. Keep it small and
engine-agnostic: a manifest format, a verifier, the Z80 wrapper. No service,
no DB schema.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-018-T011. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/eupalamus-c018-t011 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Eupalamus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
