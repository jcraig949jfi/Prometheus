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
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07 08:20Z

FINISH C-009-T034. Fresh HEADLESS session on harry1, claude-fable-5-1,
same seat, same lease (holder Pallas[harry1-2b71b1e1], your previous
instance). That instance committed the exposure record (6b02d25a0) and
the set before outcomes (a9ef80a07), ran both launches to completion
(ledger END rows written), wrote REPORT.md, the receipt and the comms
bodies -- all UNCOMMITTED in C:/Prometheus-worktrees/pallas-c009-t034 --
then ended its turn waiting for a BACKGROUND acceptance run and the
session exited (headless sessions exit when the turn ends). The
acceptance run died with it (acceptance_stdout.txt is partial).

HARD RULE FOR THIS SESSION: do NOT use run_in_background at all, and do
not end your turn until every step below is done. Run each suite in the
FOREGROUND with a timeout of 600000 ms:
  python -B -m unittest discover -s rso/slice001/tests -t .   (~5 min)
  python -B -m unittest discover -s rso/binding/tests -t .
  python -B -m unittest discover -s rso/witness/tests -t .

Steps, in the existing worktree (do not re-run any launch; do not change
the committed set, the rows, or the outcomes):
 1. Record a history note "resumed by Pallas[<you>] to finish after
    headless exit of harry1-2b71b1e1" (no new claim).
 2. Re-run the acceptance command in the foreground; put its output in
    acceptance_stdout.txt (replace the partial file; say so in REPORT.md
    s1 and the receipt).
 3. Review REPORT.md and the receipt for anything that depended on the
    acceptance result; complete them; commit results, rows, ledger rows,
    REPORT.md and seat records on branch pallas/c009-t034; push.
 4. State commits on main: GREEN, INTEGRATION_READY, receipt; release
    nothing else. Post the INTEGRATION_READY comms body to Palamedes
    --task-ref C-009-T034.
Mechanics: git -c user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on
every commit AND rebase; EW_DB_HOST=192.168.1.202; canonical
C:/Prometheus fetch-only. Then stop.
----------------------------------------------------------------------
