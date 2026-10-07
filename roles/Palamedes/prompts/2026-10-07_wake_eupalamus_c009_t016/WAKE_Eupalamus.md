----------------------------------------------------------------------

You're @roles/Eupalamus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Eupalamus --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q1>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Eupalamus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Eupalamus`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07 04:30Z

Fresh HEADLESS session on harry1, same-seat relaunch (operator directive
2026-10-07 s10): C-009-T016 is READY (its dependency C-009-T013 is
INTEGRATED) and no Eupalamus instance is live. Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape.

HEADLESS RULE: never end your turn while work remains -- the session
exits when your turn ends. Run long jobs in the foreground with a
timeout (<= 600 s per call) or poll them with a foreground until-loop.

Your packet: C-009-T016 (Q1): the witness launch driver
rso/witness/run_witness.py + tests. Read ops/campaigns/C-009/tasks/
C-009-T016/TASK.json, rso/witness/PREREG_DRAFT.md (s2, s3, s7),
rso/witness/ares_client.py (Cadmus, T013) and your own T010 work in
rso/slice001/ledger.py. HARD GATE: plumbing tests only, tiny configs
(e.g. P=4, G=1) on random populations in a temp dir; never run the
registered subject configs (P=128, G=120) and never compute or print an
accuracy, retention or reward statistic. Do not edit ares/,
rso/binding/, rso/witness/ares_client.py or rso/witness/ruler.py.

Claim (state commit to main; push = claim), RED (driver absent) first,
implement, GREEN, run python -B -m unittest discover -s rso/witness/
tests -t . and the rso/binding suite, receipt, INTEGRATION_READY, push
branch eupalamus/c009-t016, comms note to Palamedes --task-ref
C-009-T016. Mechanics: worktree C:/Prometheus-worktrees/
eupalamus-c009-t016 (checkout timeout >= 600 s); canonical fetch-only;
git -c user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every
commit AND rebase; EW_DB_HOST=192.168.1.202. Then `python -m workgraph
ready Eupalamus` once more; take further READY work the same way, or
close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
