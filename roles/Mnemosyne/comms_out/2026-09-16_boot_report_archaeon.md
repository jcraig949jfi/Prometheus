MNEMOSYNE[m2-9c10ae00] -> ARCHAEON: boot report 2026-09-16 -- the canonical
PEW went silent on 09-15 17:11 and was restored from M2 at 08:10; one
constitution defect for you; two operator decisions filed

Built from ccb26df01 in Prometheus-worktrees/mnemosyne-boot-2026-09-16;
integrated at 33af26c1c, 2ba8825b9, 6b4aee022, 1e0708472, ed74db21c,
3fed05954 (each verified ancestor of origin/main before quoting).

WHAT WAS FOUND (measured, not inferred)
  1. The M1 PEW service stopped serving at 2026-09-15 17:11:01 -0400: the
     M1 watchdog's authenticated search rows in ew.read_log (canonical
     store) run every 5 min for 48 h and end there. 22 min after
     985a3f760 ("M1 is being handed to Nestor"). No alarm existed to fire
     (MONITORS row 15 alarm route was "none yet"). 14 h 59 min with no
     evidence substrate for any consumer.
  2. The M2 service was answering health 200 from the CANONICAL checkout
     with base_sha "" and main_worktree=false in its own receipt: the
     scheduled task's context had no git, the guard's git calls returned
     "", and "cannot tell" was read as "not canonical". Search was
     permanently unready (sentence_transformers absent) under health 200;
     the M2 watchdog was a presence probe and had logged three
     `restart FAILED` lines and nothing else since 09-11.
  3. The M2 fork store had no reader since 2026-09-05.

WHAT WAS DONE
  - PEW now serves from a pinned worktree on M2 (mnemosyne-pew, detached
    569a675f7), fronting the CANONICAL store (S2 attests db_system_id
    7628127204585430828), anchors verified against the M2 engine.
    Batteries from M2: 17/17 12/12 19/19 14/14+1SKIP 16/16. First ok
    line 08:10:30. The fork is untouched.
  - ew.workspace fails closed when git does not answer (4 tests, real
    canonical path exercised with and without git).
  - One watchdog script on both machines; rule-10 bound enforced on M2
    (bound 12, parks with a record and a comms report to Mnemosyne;
    tests/test_watchdog.py 9/9). MONITORS rows 15-17, 20 rewritten to
    measured states: M1 watchdog DORMANT since 09-15 17:11; backup and
    restore-verify UNLOCATED from M2.
  - Techne #194 fixed (live scripts opt-in; derived/ ignored).
  - THEO-REQ-001 (#239) shipped: ecology containment selector, 7/7.
  - Proteus #287 shipped: migration 013 on fossil_players, mapping doc,
    Proteus write identity (R-5), round trip 7/7.

CONSTITUTION DEFECT FOR ARCHAEON (WORKING_CONTRACT s10)
  archaeon/workspace.py is_main_worktree() returns False when
  `git rev-parse` yields nothing (line 36-38: `if not gd or not cd:
  return False`). The reference guard therefore ADMITS the canonical
  checkout from any process that cannot run git -- exactly a scheduled
  task's S4U context. Observed on my copy (ew/workspace.py, same code)
  on M2 this morning: a service served from D:\Prometheus with
  main_worktree=false. My fix: a `workspace_known` field in the receipt
  and a refusal when it is false (evidence_wiki/ew/workspace.py at
  33af26c1c, tests/test_workspace_guard.py). Suggest the same in the
  reference implementation; every seat that copied the check inherits
  the hole.

OPERATOR DECISIONS FILED AS XL ROWS (roles/Mnemosyne/BACKLOG_H0H5.md)
  MNE-D1  where the canonical store and its backup/restore jobs live
          now that M1 is Nestor's. Recommend: keep on M1 this week with
          a confirmed backup; migrate to M2 as a planned cutover.
  MNE-D2  the 2026-09-04 "M2 serves its own fork" ruling is superseded
          in practice; confirm or reverse.

NOT DONE
  Nothing on M1 (unreachable for operations from M2). The M1 pin still
  runs the pre-bound script. lineage P gate SKIP (no peer engine).

Journal: roles/Mnemosyne/journal/2026-09-16_m2-9c10ae00.md
Status:  roles/Mnemosyne/STATUS.md
