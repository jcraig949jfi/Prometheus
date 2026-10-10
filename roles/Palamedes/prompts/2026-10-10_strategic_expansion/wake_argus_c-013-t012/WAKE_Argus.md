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

Fresh HEADLESS session on harry1 (M4), claude-sonnet-5-5 (Q2). Nobody answers questions
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

Your packet: C-013-T012. Read ops/campaigns/C-013/tasks/C-013-T012/TASK.json.
EXECUTE the frozen D1 demonstration (FREEZE_D1 v1.0.1; PREREGISTRATION
v1.0.1 -- s9 amendment A1 governs s4, s5 and s7). Read
rso/reach/PREREGISTRATION.md (all of it, especially s4, s6, s7, s9),
FREEZE_D1.md, README.md, and ops/campaigns/C-013/tasks/C-013-T012/
TASK.json. You change NO file pinned in FROZEN_D1.json; the runner
refuses if any differs -- if it refuses, stop and escalate, do not
"fix" a pinned file.

Run (venv python, NUMBA_NUM_THREADS=1, from your worktree root):
  <venv> -B -m rso.reach.run_d1 --out-dir rso/reach/runs/D1 --workers 2 --max-rounds-this-call 1
then repeatedly
  <venv> -B -m rso.reach.run_d1 --out-dir rso/reach/runs/D1 --resume --workers 2 --max-rounds-this-call 1
each in the FOREGROUND with timeout 600000 ms (one round is ~220-300 s
wall on harry1; if a call ever times out, --resume continues at the
first missing round -- that is designed and tested). Continue until the
runner reports the run STOPPED (CPU cap 3.2 core-hours) or COMPLETE
(N_MAX). Commit + push the ledger to your branch every ~4 rounds so a
dead session loses little. Never inspect per-arm outcomes to decide
whether to continue: the stopping rule is the runner's, not yours.
If the venv python first-run raises a NUMBA_NUM_THREADS RuntimeError
(recorded once as ANOMALY 1 in Argus's journal), re-run the same
command once and record it.

Then run the registered analysis (rso/reach/analyze.py as the
preregistration names it) and write rso/reach/RESULT.md: the result
class; completed rounds N and whether N >= 12; CPU core-hours from the
ledger; for each contrast C1-C5 the raw and Holm-adjusted p and the
per-(arm, d) certified counts beside it (A1.3), flagging any stratum
whose direction opposes the pooled sign; interpretation ONLY in the
words of the s7 / A1.4 permitted-conclusion rows (the stepping-stone
row is WITHDRAWN; C5 is matched at end-of-budget only; a certified hit
means reachable-at-this-budget, not built-by-design). Seeded controls
are reported apart from discovered solutions. State what D1 does NOT
establish. No post-hoc contrast is presented as confirmatory; label
any exploratory look as such.

Model note: you are on Sonnet because this is execution of a frozen
design plus a bounded read; if the analysis output is ambiguous under
the A1 rows, write the ambiguity down rather than resolving it by
choice -- the integrator reads it.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-013-T012. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/argus-c013-t012 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Argus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
