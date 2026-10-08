----------------------------------------------------------------------

You're @roles/Pallas Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Pallas --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q3>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Pallas/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Pallas`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-010), 2026-10-07 10:40Z

Fresh HEADLESS session on harry1, claude-fable-5-1 (Q3): same-seat
relaunch (operator directive 2026-10-07 s10). C-010-T014 is READY, Q3;
the live SPECTREX5 Pallas session is Opus 5 (Q2; it declined T034,
#1786). Never end on a question.

HARD HEADLESS RULE (two Pallas sessions were lost to this today): do NOT
use run_in_background at all. Run every command in the FOREGROUND with
a timeout <= 600000 ms; split long runs (e.g. one mutation edit per
call). Never end your turn while any step below remains.

Your packet: C-010-T014 -- the independent challenge on the FROZEN
witness path, BEFORE any witness outcome exists. Read its TASK.json,
rso/witness/FREEZE_W1.md (verify every hash against the committed
bytes first), rso/witness/PREREGISTRATION.md (frozen; sha256 in
CAMPAIGN.json), rso/witness/RULER.md, ERASE_PROBES.md,
rso/binding/CLOSURE.md, ops/campaigns/C-010/escalations/
C-010-T012_1_RESPONSE.md, and the T010-T013 receipts/notes. Write the
exposure record first.

Set: at least 1 sound, 2 broken and 2 semantic edits on the witness
path (evaluate.py, ruler.py, ares_client.py node executions,
run_witness.py storage / per-launch inventory / seed refusals,
make_configs.py), committed BEFORE outcomes. Ideas the packet names: a
counterfeit P-RET input, a leak that passes P-ERASE, a stored artifact
that does not match its receipt. HARD GATE: synthetic or hand-wired
organisms ONLY (rso/witness/dry_run.py shows the tiny random-subject
pattern); never run a registered subject config (P=128, G=120) or any
registered arm on registered seeds; never print an accuracy/retention
number of anything resembling the registered subjects. <= 2 launches on
rso/witness/LEDGER.jsonl (contract rso/witness/contract.json). Report
CLOSED / NOT CLOSED per surface and every survivor with whether it
bears on the registered witness run. You never repair production code.

Claim (state commit to main; push = claim), set, run, rows, REPORT.md
under rso/witness/challenge/W1/, receipt, INTEGRATION_READY, comms to
Palamedes --task-ref C-010-T014. Mechanics: worktree C:/Prometheus-
worktrees/pallas-c010-t014 (checkout timeout >= 600 s); canonical
fetch-only; git -c user.name=jcraig949jfi -c user.email=jcraig@jfi.ai
on every commit AND rebase; EW_DB_HOST=192.168.1.202. Then stop.
----------------------------------------------------------------------
