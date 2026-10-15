----------------------------------------------------------------------

You're @roles/Cadmus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Cadmus --model <your runtime model id> --capabilities rso-builder,<class your runtime model meets>), read
origin/main:ops/work_orders/CURRENT.md and roles/base-role/RESPONSIBILITIES.md,
and follow its boot sequence. Then read roles/rso-builder-role/RESPONSIBILITIES.md
(s8), roles/Cadmus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Cadmus`.

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-019), 2026-10-15

Fresh HEADLESS session on harry1 (M4), claude-sonnet-5-5 (Q2). Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue what does not depend on it.

HARD HEADLESS RULE: do NOT use run_in_background at all; run every
command in the FOREGROUND with a timeout <= 600000 ms (split long work);
never end your turn while any step remains -- the session exits when your
turn ends. harry1 is thermally limited: keep any computation to <= 2
concurrent processes.

Read first: roles/Palamedes/prompts/2026-10-15_generation5/01_OPERATOR_DIRECTIVE_verbatim.md (the Generation 5
directive -- binding for your packet), rso/registry/README.md
and `python -m rso.registry.registry for-adapter` (what is reusable, at
which scope).

Your packet: C-019-T020. Read ops/campaigns/C-019/tasks/C-019-T020/TASK.json.
ISOLATION: Aether/, roles/Aether/, crius/, roles/Crius/,
prometheus/ananke/ and roles/Ananke/ are READ-ONLY. Never edit an engine's
source, seeds, frozen results or running experiments; never run anything on
M2. C-018's frozen files (rso/aether/FROZEN.json and everything it pins,
rso/aether/runs/, rso/aether/RESULT.md) must not change. Pin a SHA in your
own worktree.

BRANCH RULE: commit work to YOUR BRANCH and push the branch; only the small
workgraph state commits (CLAIMED / INTEGRATION_READY) go to main.

LONG JOBS: anything longer than one foreground call runs as a DETACHED OS
process (PowerShell Start-Process, logs redirected, PID recorded, results
written to files so a restart resumes); poll with short foreground checks.
Never use run_in_background; never end your turn while work is pending.

Your packets: C-019-T020 (Aether post-confirmation replay audit) and
C-019-T021 (Crius selection gate), both READY, one session. Claim both.
ORDER: start T020's replay FIRST as ONE detached process (about one
core-hour; that leaves one slot for T021's small runs, so the seat's
total stays <= 2 processes), then work on T021 while it runs; finish T020's
AUDIT.md when the replays are done. Each packet's TASK.json `problem`
field is the full brief: read it twice.

T020 is an audit, not a repair: never modify the committed evidence,
never re-run C-018's analysis in place, no new seeds. If any unit
mismatches, record it with both digests and say plainly what it changes.

T021: the operator named you temporary read-only compatibility steward of
the frozen Crius interface (directive s2B). That is NOT a reopening of
the Crius seat: no edit to crius/ or roles/Crius/, no physics change, no
forbidden rescue move. Commit GATE_RULE.md with predictions BEFORE running
any condition. WORLD_DEMAND_NOT_QUALIFIED is a legitimate, valuable
outcome; do not tune toward a pass. Separate INTEGRATION_READY per packet
(T020 may land before T021).
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-019-T020. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/cadmus-c019 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Cadmus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
