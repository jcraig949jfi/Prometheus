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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-018), 2026-10-12

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5 (Q2). Nobody answers questions
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

Your packet: C-018-T041. Read ops/campaigns/C-018/tasks/C-018-T041/TASK.json.
AETHER ISOLATION: Aether/ and roles/Aether/ are read-only (the Aether seat
is ACTIVE on M2). Never edit its source, seeds, frozen results or running
experiments; never run anything on M2. Pin a SHA in your own worktree.

BRANCH RULE: commit work to YOUR BRANCH and push the branch; only the small
workgraph state commits (CLAIMED / INTEGRATION_READY) go to main.

THE ONE bounded repair round (directive s9) of your Aether assay. Read
rso/aether/challenge/REPORT.md (Pallas, genuine Q3) in full, then your
packet's TASK.json `problem` field: evidence-chain, instrument (B8 N rule),
inference (B2 unevaluable, B3, B7) and interpretation items. Amendment
v1.1.0 committed BEFORE the re-freeze; every new test RED on its mutant
applied verbatim from rso/aether/challenge/edits.json where one exists
(python -B). Development and your own seeds only; the confirmatory block
k = 0x2000+i and the burned 0x1000..0x10FF stay untouched. There is no
second repair round: what cannot be closed is narrowed and recorded as a
limitation. NO confirmatory run, and do not write rso/aether/RELEASE.json
(the coordinator writes it after the re-check).
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-018-T041. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c018-t041 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
