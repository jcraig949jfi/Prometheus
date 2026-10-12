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

Your packet: C-018-T040. Read ops/campaigns/C-018/tasks/C-018-T040/TASK.json.
AETHER ISOLATION: Aether/ and roles/Aether/ are read-only (the Aether seat
is ACTIVE on M2). Never edit its source, seeds, frozen results or running
experiments; never run anything on M2. Pin a SHA in your own worktree.

BRANCH RULE: commit work to YOUR BRANCH and push the branch; only the small
workgraph state commits (CLAIMED / INTEGRATION_READY) go to main.

Q3 challenge of the FROZEN Aether ancestry-vs-content assay (directive
s9). Read rso/aether/PREREGISTRATION.md, FREEZE.md, FROZEN.json (verify:
python -m rso.aether.freeze check), SELECTION.md, the falsifiability table
(PREREG s4, qual/FALSIFIABILITY_AUDIT.json), the completeness manifest
(manifests/), and the code. No confirmatory outcome exists; the
confirmatory seeds (k = 0x2000+i) are never run by you, and k =
0x1000..0x10FF is burned (PREREG s5 incident). Use your own declared seed
range, disjoint from every range in PREREG s5 and SELECTION.md.

The directive (s9) names the attacks: causal ancestry mistaken for
information transmission; a decoder exploiting initial geometry; a
negative control unable to pass (or fail); observations predictable from
recipes alone; the evaluator trusting derived producer fields; missing or
altered evidence preserving a qualified result (the completeness gate);
results not surviving relevant counterfactual interventions. Also: the
NO_CUT incidence (5 of 6 dev units) -- can the experiment end with too
few evaluable units, and does the rule then say so honestly? Commit the
challenge set with predictions BEFORE running any of it
(rso/aether/challenge/); python -B. Report CLOSED / NOT CLOSED per surface
with every survivor's bearing. One bounded repair round follows.

MODEL CONTINUITY (directive s9): your runtime must be claude-fable-5-1 for
the whole session. If the harness tells you the model changed (a
refusal fallback), keep working on the deterministic findings but record
the switch at the top of your REPORT and do NOT claim the Q3 requirement
is met; the coordinator verifies this from the launch log anyway. Frame
attacks as tests of a scientific instrument. <= 2 processes on harry1.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-018-T040. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/pallas-c018-t040 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Pallas` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
