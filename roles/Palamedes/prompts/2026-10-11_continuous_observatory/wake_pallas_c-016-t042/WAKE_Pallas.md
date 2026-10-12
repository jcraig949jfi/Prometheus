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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-016), 2026-10-11

Fresh HEADLESS session on harry1 (M4), claude-fable-5-1 (Q3; no downgrade). Nobody answers questions
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

Your packet: C-016-T042. Read ops/campaigns/C-016/tasks/C-016-T042/TASK.json.
ENSORAIN ISOLATION (directive s3): Ensorain's WTP-05 DEEP is running on
ubu006 now (ETA ~2026-10-11T13:00Z). Read-only: never edit ensorain/ or
roles/Ensorain/, never use a WTP-05 registered seed, never run anything on
ubu006. Work against a pinned SHA in your own worktree.

SHORT Q3 re-check of the REPAIRED Ensorain assay (FREEZE_ENSORAIN v1.1.0,
PREREGISTRATION v1.1.0; the one repair round C-016-T041 by Argus answered
your C-016-T040 REPORT). Not an open-ended second challenge. Verify first:
`python -m rso.ensorain.freeze check`; the amendment commit (030f1746f)
precedes the re-freeze (ebe4860c1); each new test is RED on its mutant
(rso/ensorain/repair_v110/red_rows.jsonl -- re-run at least E1, E2, E4, R1
yourself with python -B).

Then, committing your predictions BEFORE running (rso/ensorain/challenge/
R2/): re-run W1-W5 and B1, S5, P3, B2, B3 against the v1.1.0 rule, and
attack the NEW parts once each: the whole-life `revised` endpoint, the
noise-matched arm (is eta -> 1e-9 really "perturbation without update"?),
the intersection-union K1, G_R5's 371/400 bound, family S from structure.
Build at least one new adversarial genome aimed at the repaired K1. No
confirmatory seeds (16_330_xxx), no `assay confirm`; your own challenge
seed range, declared, disjoint from PREREGISTRATION s6.

Report CLOSED / NOT CLOSED per surface (inference, instrument,
interpretation) under rso/ensorain/challenge/R2/REPORT.md. There is NO
further repair round: a survivor now becomes a recorded limitation the
result must carry, so say exactly what the result must state. You never
repair production code. <= 2 processes on harry1.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-016-T042. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/pallas-c016-t042 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Pallas` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
