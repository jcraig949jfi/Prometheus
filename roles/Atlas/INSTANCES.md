# Atlas instances

Currency: 2026-09-19. Pattern: roles/Harmonia/INSTANCES.md (D-24
amendment 3: one seat, many instances, tag = <machine>-<8 of session id>).

Operator, 2026-09-19: the M2 instance boots "as his own instance, a
brother to you and not to assume your role". Both instances ARE the Atlas
seat and share one index and one charter; neither directs the other, and
neither takes over the other's host.

    instance        host  lane (what it harvests)                     boot prompt
    --------------  ----  ------------------------------------------  -----------------------------
    m1-1c645957     M1    git history (all refs), M1-local evidence,  (seat creator)
                          PEW/viv pointers, comb + report
    m2-<pending>    M2    M2-local evidence: frontier runs/ + logs,   prompts/2026-09-19_m2_instance/
                          the live SFE data dir, Vivarium var/,
                          M2 vault frames, M2-only git refs

## Rules that keep two instances from colliding

1. SAME KEYS, NEVER A SECOND HISTORY. Both write through
   atlas/harvest/common.py; keys come from native ids, so an M2 harvest
   enriches the M1 rows (MODEL.md s5). Neither instance deletes or
   rewrites rows whose last harvest ran on the other host (prune is
   host-scoped; a cheat-control test proves it).
2. HOST-SCOPED ROOTS. Each instance edits only its own host's entries in
   atlas/registry.json "local_roots".
3. SHARED CODE. Changes to shared modules (common.py, db.py, classify.py,
   an existing harvester, views.sql) are announced in comms to Atlas
   before the commit, bump the harvester VERSION, and pass
   atlas/tests on the merged tree. A new harvester module is owned by the
   instance that writes it.
4. MIGRATIONS. Name them NNN_<instance tag>_<topic>.sql and claim NNN in
   comms first; migrate() keys on the file stem, so two instances cannot
   overwrite each other's migration even on a numbering race.
5. JOURNALS are per instance: roles/Atlas/journal/<date>_<tag>.md, append
   only (a whole-file write to a shared journal clobbered a sibling's
   entry once in this program). roles/Atlas/journal/2026-09-19.md
   predates this file and belongs to m1-1c645957.
6. comb and report read the whole index and are idempotent; either
   instance may run them. Signals a human has moved off OPEN are never
   touched by either.
7. STATUS.md is shared: each instance edits only its own line in the
   instances section.
8. Commit subjects carry the tag: "Atlas[m1-1c645957]: ...".
