----------------------------------------------------------------------

You're @roles/Pallas Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Pallas --model <your runtime model id> --capabilities rso-builder,<class your runtime model meets>), read
origin/main:ops/work_orders/CURRENT.md and roles/base-role/RESPONSIBILITIES.md,
and follow its boot sequence. Then read roles/rso-builder-role/RESPONSIBILITIES.md
(s8), roles/Pallas/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Pallas`.

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-013), 2026-10-10

Fresh HEADLESS session on harry1 (M4), claude-fable-5-1 (Q3; no downgrade). Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue what does not depend on it.

HARD HEADLESS RULE: do NOT use run_in_background at all; run every
command in the FOREGROUND with a timeout <= 600000 ms (split long work);
never end your turn while any step remains -- the session exits when your
turn ends. harry1 is thermally limited: keep any computation to <= 2
concurrent processes.

Read first: roles/Palamedes/prompts/2026-10-10_strategic_expansion/01_OPERATOR_DIRECTIVE_verbatim.md (Strategic Expansion
Directive), roles/Palamedes/prompts/2026-10-10_strategic_expansion/02_OPERATOR_RULING_verbatim.md (the ruling -- binding
details for your packet), and the source digests in
roles/Palamedes/notes/2026-10-10_strategic_sources/.

Your packet: C-013-T011. Read ops/campaigns/C-013/tasks/C-013-T011/TASK.json.
Q3 challenge of the FROZEN D1 demonstration (operator ruling s4). Read
rso/reach/PREREGISTRATION.md, FREEZE_D1.md, FROZEN_D1.json (verify every
pinned hash against the committed bytes first), README.md,
REACHABILITY_CARTOGRAPHY_V0.md, NUMBA_DECISION.md,
DESCRIPTOR_QUALIFICATION.json, CALIBRATION_B.json, and the code in
rso/reach/. No D1 outcome exists: the confirmatory run (C-013-T012) waits
for your committed set; you are not to run the confirmatory lineages
(the runner refuses lineages >= 0 outside a confirmatory call -- do not
work around it).

Challenge the preregistered INFERENCE (do the five contrasts isolate what
s7 says they isolate? Holm family, stratified exact test, power claims,
the CPU-cap stopping rule), the CERTIFICATION machinery (can a non-builder
certify; can a builder fail to; is the oracle recheck independent), and
the INTERPRETATION of any archive advantage (could a difference come from
parent diversity, budget accounting, bucket-count calibration, shared
starts, or descriptor over-splitting rather than the named ingredient?).
At least 1 sound, 2 broken and 2 semantic edits, committed BEFORE any
outcome; use development lineages (< 0) and toy budgets only.

Environment: numba and pytest are NOT on the system Python; use the
isolated venv C:/Prometheus-worktrees/argus-reach-venv/Scripts/python.exe
(read only; do not install into it). Tests: <venv python> -m pytest
rso/reach/tests -q (about 6 minutes; run in the FOREGROUND with a
600000 ms timeout, or per file). Keep <= 2 concurrent processes.

Report CLOSED / NOT CLOSED per surface (inference, certification,
interpretation) and every survivor with its bearing on the registered
inference, under rso/reach/challenge/D1/. You never repair production
code. One bounded repair round follows your report.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-013-T011. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/pallas-c013-t011 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Pallas` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
