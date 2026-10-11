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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-017), 2026-10-11

Fresh HEADLESS session on harry1 (M4), claude-sonnet-5-5 (Q2). Nobody answers questions
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

Your packet: C-017-T050. Read ops/campaigns/C-017/tasks/C-017-T050/TASK.json.
Z80 ISOLATION: archaeon/, prometheus/z80atlas/ and roles/Archaeon/ are
read-only (Archaeon is active on its own Beta campaign). Never use an
Archaeon registered seed; never touch the 13.75 GB evidence bundle. Work
against a pinned SHA in your own worktree.

BRANCH RULE: commit your work to YOUR BRANCH and push the branch; only
the small workgraph state commits (CLAIMED / INTEGRATION_READY) go to
main. In C-016 both your packets were pushed straight to main -- do not
repeat that; the integrator merges your branch.

EXECUTE the frozen Z80 attribution confirmatory run and write a bounded
RESULT. Your packet's TASK.json `problem` field is the exact command
sequence (six shards, ONE per foreground call, timeout 600000 -- you are
headless: no background jobs) and the five things RESULT.md must contain;
read it, then rso/z80/PREREGISTRATION.md s5 and s11 and
rso/z80/challenge/R2/REPORT.md. Measure CPU-seconds and peak memory per
shard (e.g. a small psutil wrapper in YOUR scratch dir, not in rso/z80/).
You change NO file pinned in rso/z80/FROZEN.json; if `freeze check` or
`confirm` refuses, stop and escalate. Never read partial outcomes to
decide anything. If the output is ambiguous under the registered rule,
write the ambiguity down; the integrator reads it.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-017-T050. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c017-t050 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
