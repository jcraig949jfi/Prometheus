# Atlas-M2 -- resume after a reboot or a cold start

Currency: 2026-09-25 10:30 UTC (written at the operator's request just
before an M2 reboot; the seat's loop was already PARKED on 2026-09-19).
Read RESPONSIBILITIES.md first (it is the entry file); this file is the
operational how-to-come-back and nothing in it overrides that one or the
base role.

## 0. In one paragraph

Atlas-M2 is a seat on M2 that gathers what the M2 science benches emit
into the ONE Atlas index (schema `atlas`) on the M1 Postgres cluster. It
is not an instance of Atlas (M1). Its queue items (a)-(f) are all done.
Its loop is PARKED by the operator's instruction of 2026-09-19 ("kick out
of the loops if all the work is done; I will tell you to resume after
some more research piles up", comms #512). Research HAS piled up since
(section 3): the resume is a real piece of work, not a formality.

## 1. State at the reboot (all verified, not recalled)

    worktree      D:\Prometheus-worktrees\atlas-m2-boot-2026-09-19
    branch        atlas-m2/boot-2026-09-19
    HEAD          3982fd720 -- an ancestor of origin/main; NOTHING unpushed
    origin/main   c6f3ee198 at 2026-09-25 10:24 UTC (the fleet moved 6 days;
                  merge it explicitly before working, never pull)
    comms         last sync 2026-09-25 06:24 local as Atlas-M2[m2-8f915f3d];
                  queue length 0; 12 messages since #514 all read (section 4)
    index writes  local_files/4 and frontier_runs_m2/2 passes of 2026-09-19;
                  no write since
    loop          PARKED (roles/base-role/MONITORS.md state DISABLED); the
                  session wakeup was stopped, so nothing restarts by itself

A reboot does not touch any of this: the worktree, the receipt trees and
the M1 store all survive. The only thing the reboot ends is the session.

## 2. The five commands that put a fresh session back to work

Run them in the worktree above (it already exists -- do NOT create a
second one, and do not touch the canonical checkout beyond `git fetch`):

    cd D:\Prometheus-worktrees\atlas-m2-boot-2026-09-19
    export EW_DB_HOST=192.168.1.202          # comms AND the atlas index live on M1
    export ATLAS_SEAT=Atlas-M2               # stamps harvest_run.seat (SIBLINGS rule 7)
    export PYTHONPATH=$PWD                   # `python -m atlas ...` needs it from a worktree
    git -C D:/Prometheus fetch origin && git merge <the new origin/main sha>
    python -m comms boot Atlas-M2 --model <your model id> --capabilities any
    python -m comms sync Atlas-M2

Forgetting EW_DB_HOST is the classic M2 failure: the client resolves to
this host's quarantined local Postgres and the identity guard refuses it
with WRONG_ENVIRONMENT (which is the correct failure, not a bug).
PYTHONPATH is needed because atlas/ is imported as a package from a
linked worktree.

## 3. The work waiting (measured at 10:24 UTC, 2026-09-25)

BENCH OUTPUT MOVED A LOT while the loop was parked -- this is the resume
trigger the operator described:

    frontier runs/   230 -> 540 files, newest 2026-09-22T19:07:50Z
    receipts         58 -> 129 RECEIPT.json (+71), 0 still RUNNING
    frontier logs/   7 -> 9 files, newest 2026-09-22T19:09:57Z
    D:/Prometheus-data/{archaeon,sfe,sfe-scratch}   unchanged since 09-17
    vivarium var/    live (deadman/deliverer heartbeats; not bench output)
    frontier pointers in the index: still 167, all FS:M2

PREDICTION, written before the pass so it can be wrong: most of the 71
new receipts will land UNMATCHED (linked to their experiment with a
`receipt.present_no_run_event` fact, no attempt minted), because Atlas's
git-side frontier harvester last ran 2026-09-19 07:32 local and the RUN
events for these runs are not in the index yet. They resolve by
themselves when Atlas re-harvests and my next pass flips them through his
pointers (his #513). If instead they match, the index moved on M1 without
my seeing it and that is worth a line in the journal.

First actions on resume, in order:

    python -m atlas harvest local_files
    python -m atlas harvest frontier_runs_m2
    python -m atlas comb
    python -m atlas report --out roles/Atlas-M2/reports/REPORT_<date>_M2.txt
    python -m pytest -q atlas/tests          # 28 controls; all passed 09-19

Record BEFORE/AFTER counts (EXPECTED:M2 vs FS:M2, matched vs unmatched,
attempts minted = 0) and post one comms report to Atlas with what moved.
The rest of the queue is roles/Atlas-M2/TODO_2026-09-25.md.

## 4. What arrived while the loop was parked (all read, none was a task)

    #517 Atlas   migration 008 claimed (atlas.ecosystem + ecosystem_reference)
    #523 Atlas   FYI: external ALife ecosystem catalogue (352 systems)
    #531 Atlas   FYI: 34-experiment prior-art queue, Engine Five
    #556 Atlas   migration 010 claimed (research-policy tables: theory graph,
                 primitives, combinations, scoring, portfolio, blind spots);
                 the operator promoted Atlas from index to research-policy
                 layer on 2026-09-24. Nothing Atlas-M2 writes is touched.
    #541..#566   Ensorain broadcasts (E0-E2, dials, WTP-01..03) -- a new M2
                 seat running heavy benches; see section 5
    Atlas itself last synced 2026-09-24 07:33 at f8df65681 and is offline.

Migrations 006, 007, 008 and 010 are Atlas's. Before claiming a number,
list atlas/sql/ and claim it in comms first (SIBLINGS rule 4); migrate()
keys on the file stem, so a numbering race cannot silently overwrite.

## 5. Two gather targets discovered at the reboot (not yet in the registry)

- ENSORAIN and ARES, new seats on M2, emit large git-ignored run trees
  inside their worktrees (ensorain-base-role/ensorain 146 MB / 317 files;
  ares-base-role/ares 51 MB / 1,076 files; copies of both appear in
  several other seats' worktrees, which is a de-duplication question
  before any registry row: the same run must not be indexed twice under
  two paths). Neither engine is in atlas/registry.json. Their output is
  exactly what this seat exists to shadow, and Ensorain's WTP campaigns
  are the most active science on M2 right now.
- C:/Prometheus-data/evidence -- a root that did not exist on 2026-09-19,
  holding envgate01_2026-09-24/ and z80atlas_campaign_2026-09-19/. Owner
  not yet identified; ask before indexing (it may be Cosmos, Crius or
  Ensorain).
Neither contains any .db/.sqlite/.duckdb file (checked at 10:28 UTC),
which is worth saying out loud given the operator's migration away from
SQLite: the NEW work on M2 is not adding any.

## 6. Standing rules a resuming session must not rediscover the hard way

- NEVER touch a bench. Reads are stat/listdir, small JSON receipts, and
  sha256 of files <= 5 MB. The LIVE SFE ledger (C:/Prometheus-data/sfe/
  engine.db) is NEVER opened -- not even read-only/immutable -- by this
  seat; it is a declared, stat-only pointer. No signal to a process, no
  SFE API load, no git command in another seat's worktree, no write
  outside schema atlas and this seat's own paths.
- Identity of a frontier attempt comes ONLY from the receipt pointer
  Atlas already linked. A receipt time is never minted into an attempt
  key: the RUN-event time and the receipt's finished_at differ by one
  second for 8 of 42 matched receipts. A cheat control asserts this
  (atlas/tests/test_frontier_runs_m2.py).
- Service heartbeats (sfengine_m2_watchdog.*, deadman-*/deliverer-*.
  state.json, engine.db-wal/-shm) are NOT bench movement; counting them
  would make the loop's non-productive bound decorative.
- Shared-code changes (common.py, db.py, an existing harvester, ORDER,
  registry fields) are announced to Atlas in comms BEFORE the commit,
  with a VERSION bump and tests on the merged tree.
- Do not restart the loop without the operator's word. The seat stays
  ACTIVE for comms either way; a parked loop's silence is expected, and
  MONITORS.md says so.
