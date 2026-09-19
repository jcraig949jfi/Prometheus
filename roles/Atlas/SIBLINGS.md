# Atlas and its sibling seats

Currency: 2026-09-19 10:25 UTC. Supersedes this file's first version
(f89c9e57b, then named INSTANCES.md), which read the operator's "a
brother to you and not to assume your role" as one seat with two
instances. That was wrong: the operator made the M2 helper a separate
SEAT, Atlas-M2 ("recognize that you are not an instance of Atlas",
roles/Atlas-M2/prompts/2026-09-19_bootstrap/). Atlas-M2 pointed this out
in comms #499; the correction is in calibration/LEDGER.md.

    seat       instance      host  scope
    ---------  ------------  ----  ------------------------------------------
    Atlas      m1-1c645957   M1    the index, git history, M1-local evidence,
                                   PEW/viv pointers, comb + report
    Atlas-M2   m2-8f915f3d   M2    assists Atlas with the M2-resident part
                                   of the index, on the operator's
                                   instructions to Atlas-M2

Neither seat directs the other. Atlas-M2 keeps its own journal, STATUS
and commit prefix under roles/Atlas-M2/.

## Shared rules (adopted by Atlas-M2 in #499)

1. SAME KEYS, NEVER A SECOND HISTORY. Both write through
   atlas/harvest/common.py; keys come from native ids, so an M2 harvest
   enriches the M1 rows (MODEL.md s5). Neither seat deletes or rewrites
   rows whose last harvest ran on the other host (prune is host-scoped;
   a cheat-control test proves it).
2. HOST-SCOPED ROOTS. Each seat edits only its own host's entries in
   atlas/registry.json "local_roots".
3. SHARED CODE. Changes to shared modules (common.py, db.py, classify.py,
   an existing harvester, views.sql) are announced to the other seat in
   comms before the commit, bump the harvester VERSION, and pass
   atlas/tests on the merged tree. A new harvester module is owned by
   the seat that writes it.
4. MIGRATIONS are named NNN_<instance tag>_<topic>.sql, with NNN claimed
   in comms first. migrate() keys on the file stem.
5. comb and report read the whole index and are idempotent; either seat
   may run them. Signals a human has moved off OPEN are never touched.
