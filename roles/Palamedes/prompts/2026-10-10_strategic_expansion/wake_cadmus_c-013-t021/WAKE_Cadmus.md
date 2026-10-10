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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-013), 2026-10-10

Fresh HEADLESS session on harry1 (M4), claude-sonnet-5-5 (code inspection packet). Nobody answers questions
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

Your packet: C-013-T021. Read ops/campaigns/C-013/tasks/C-013-T021/TASK.json.
Checkpoint/replay survey: rso/scale/CHECKPOINT_REPLAY_SURVEY.md. For each
runtime with an evolutionary or lifetime loop (Ares, Ensorain, Ananke/PTE,
z80atlas, SFE/Proteus, Tyche, Crius, Theseus, Primordial, Aether, the
p1_slice wm_mini): can full state incl. RNG be saved and restored, is
replay deterministic, checkpoint granularity and size, what blocks it,
with file:line evidence and at most tiny smoke runs. Then a short list of
next native runtimes for onboarding with the adapter cost. Read only; do
not change any engine's files or charter.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-013-T021. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/cadmus-c013-t021 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Cadmus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
