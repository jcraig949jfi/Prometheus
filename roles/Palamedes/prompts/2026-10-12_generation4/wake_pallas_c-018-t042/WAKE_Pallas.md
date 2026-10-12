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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-018), 2026-10-12

Fresh HEADLESS session on harry1 (M4), claude-fable-5-1 (Q3; no downgrade). Nobody answers questions
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

Your packet: C-018-T042. Read ops/campaigns/C-018/tasks/C-018-T042/TASK.json.
AETHER ISOLATION: Aether/ and roles/Aether/ are read-only (the Aether seat
is ACTIVE on M2). Never edit its source, seeds, frozen results or running
experiments; never run anything on M2. Pin a SHA in your own worktree.

BRANCH RULE: commit work to YOUR BRANCH and push the branch; only the small
workgraph state commits (CLAIMED / INTEGRATION_READY) go to main.

SHORT Q3 re-check of the REPAIRED Aether assay (PREREGISTRATION v1.1.0,
sections 10-12; the one repair round C-018-T041 by Argus answered your
C-018-T040 REPORT). Not a second open challenge. Verify first:
`python -m rso.aether.freeze check`; the amendment commit b3cc39a56
precedes the dev check and the re-freeze; re-run at least four rows of
rso/aether/red/red_rows_v1_1_0.jsonl yourself with python -B. Then,
predictions committed BEFORE running (rso/aether/challenge/R2/): re-run
B1 (incl. the invariant-respecting tamper vs the new per-unit tree
replay), B2, B5, B6, B8 (0x3004 / 0x3005 shapes), E5/E1h/E3h against
v1.1.0, and attack the NEW parts once each: the N window
ftick(B) <= t < min ftick(targets) (does it leave too many units without
a control, or admit a new upstream path?), EVALUABLE_MIN = 8 and the
ANCESTRY_UNEVALUABLE status, the need-over-evaluable denominator (s10.3:
not stricter in every case -- is that a hole?), and the disclosed effect
that 2 of your 3 NONSPECIFIC units become CONFIRMED. Your own declared
seeds only; never k = 0x2000+i or `confirm run`.
Report CLOSED / NOT CLOSED per surface under
rso/aether/challenge/R2/REPORT.md. No further repair round: a survivor
becomes a limitation the RESULT must carry -- say exactly what.
MODEL CONTINUITY: if the harness reports a model change, record it at the
top of the REPORT and do not claim Q3. <= 2 processes on harry1.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-018-T042. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/pallas-c018-t042 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Pallas` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
