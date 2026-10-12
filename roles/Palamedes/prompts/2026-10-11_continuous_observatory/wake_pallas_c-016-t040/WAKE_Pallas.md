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

Your packet: C-016-T040. Read ops/campaigns/C-016/tasks/C-016-T040/TASK.json.
ENSORAIN ISOLATION (directive s3): Ensorain's WTP-05 DEEP is running on
ubu006 now (ETA ~2026-10-11T13:00Z). Read-only: never edit ensorain/ or
roles/Ensorain/, never use a WTP-05 registered seed, never run anything on
ubu006. Work against a pinned SHA in your own worktree.

Q3 challenge of the FROZEN Ensorain assay (directive s9). Read
rso/ensorain/PREREGISTRATION.md, FREEZE.md, FROZEN.json (verify every pinned
hash against the committed bytes first: python -m rso.ensorain.freeze check),
COMPATIBILITY.md, ONBOARDING.md, SUBJECTS.json, DEV_QUALIFICATION.json and
the code in rso/ensorain/. No confirmatory outcome exists; you must not run
the confirmatory seeds 16_330_001..400 or call `assay confirm`. Use your own
challenge seeds (declare a range disjoint from every range in
PREREGISTRATION s6 and from WTP-05's registered seeds) and development-
size runs only.

Spend Q3 effort on claim-critical surfaces, not plumbing deterministic
tests settle (directive s9):
- INFERENCE: does the decision rule license each verdict row? K1 is
  declared near-automatic (s11.4) -- does K1 + the four-policy argument (s3)
  really cover the memoryless class? Is the sign test with seed pairing
  valid when arm rng streams diverge after block 0 (s11.2)? Holm families?
  N = 400 power claims?
- INSTRUMENT: can a forbidden channel or fixed prior pass G_PRE (e.g. a
  genome that is pre-competent AND reads the switch some other way, a
  plastic parameter that is decorative, a Smuggler that learns the first
  sign then flips on a block counter or any observable it can reach)? Can
  memory_check or recompute_check be fooled? Is G_PRE itself what makes the
  reference pass rather than revision?
- INTERPRETATION: does REVISION_HISTORY_DEPENDENT mean revision of a
  learned parameter driven by own reward history, or could shuffle hurt for
  another reason (noise injection; COMPATIBILITY s4 notes shuffle also
  damages PRE accuracy)? Does "search accessibility" read correctly given
  5 of 8 searched subjects have no plastic parameter?
At least 1 sound, 2 broken and 2 semantic edits, plus adversarial subject
genomes, COMMITTED BEFORE you run any of them (rso/ensorain/challenge/). The
registry's mutation-runner (rso/slice001/mutation.py) or the RED-edit
pattern (rso/reach/repair_v101/run_red.py) may be reused; run python -B
(stale .pyc pitfall) and say whether each kill is behavioural or only a
freeze-hash guard.

Report CLOSED / NOT CLOSED per surface (inference, instrument,
interpretation), every survivor with its bearing on the registered
verdicts, under rso/ensorain/challenge/. You never repair production code.
One bounded repair round follows your report. <= 2 processes on harry1.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-016-T040. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/pallas-c016-t040 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Pallas` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
