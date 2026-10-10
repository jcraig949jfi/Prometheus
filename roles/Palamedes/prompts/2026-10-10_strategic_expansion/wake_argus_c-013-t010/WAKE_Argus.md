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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-013), 2026-10-10

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5 (Q2). Nobody answers questions
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

Your packet: C-013-T010. Read ops/campaigns/C-013/tasks/C-013-T010/TASK.json.
Workstream B. (1) rso/reach/REACHABILITY_CARTOGRAPHY_V0.md -- the reusable
protocol (the directive s5 measurement list; budget-relative upper bounds,
never impossibility; keep genome retention, neutral stepping stones,
environment-state restoration, genotype paths and populations around
incomplete mechanisms distinct). (2) ONE small demonstration on the
FABLE-5.1 p1_slice reach world (docs/phase3/design/FABLE-5.1/prototype/
p1_slice/, READ ONLY) using Nyx's corrected ladder (nyx/atlas/experiments/
reach_archive/ @ 3318a2098, READ ONLY; cite it; build your own harness in
rso/reach/). Arms must separate retention, neutral acceptance, visit-count
novelty selection and admission of worse candidates into new behaviour
cells; plus the chain baseline and a structure-free genotype-hash archive
with bucket count matched to the behaviour cells. Before freezing:
independent certification of hits (not training fitness); a TIMED
measurement deciding whether the numba port is needed (port + differential
test only if justified); a planted near-miss test that the behaviour
descriptor separates shortest-edit-path intermediates from equal-score
arbitrary genomes; seeded controls kept apart from discovered solutions;
a preregistered analysis for a 1/24 baseline with the number of contrasts
(e.g. exact tests + Holm) and the lineage count it implies. Never call
genotype copying Go-Explore state restoration. Commit PREREGISTRATION.md
and FREEZE_D1.md BEFORE any outcome, then STOP at INTEGRATION_READY: the
run itself (C-013-T012) waits for Pallas's Q3 challenge (C-013-T011).
Notify Nyx by comms of the derivative experiment (attribution, SHA).
Budget for the whole demonstration <= 4 CPU core-hours; development runs
on toy settings only before the freeze.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-013-T010. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c013-t010 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
