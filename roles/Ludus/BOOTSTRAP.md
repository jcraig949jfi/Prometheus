# LUDUS -- BOOTSTRAP (read this first)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Resolve and obey the current base-role inheritance
chain BEFORE this seat's local bootstrap; boot mechanics are not restated
here.

Then, in this order:

1. CHARTER_v3_WORLD_FOUNDRY.md -- the current mandate (World Foundry).
   CHARTER.md (v2) and CHARTER_v1.md are retained history; v3 s10 lists
   what in them is superseded.
2. ROLE.md -- the seat's accumulated method (GATE-W1, r0001/r0002, the
   standing rules earned in s10). Its s3 A1, s7.4, s8 and s10 "Next, in
   order" are superseded; the file is annotated, not rewritten.
3. ARCHAEOLOGY_2026-09-11.md -- every 2026-09-01 queue item classified;
   the five defects found on adoption (L-1..L-5).
4. BACKLOG_H0H5.md -- the live queue, first five first.
5. STATUS.md -- machine-readable state, currency date at the top.
6. The newest prompt under prompts/ (verify its MANIFEST hash first).
7. journal/ -- the newest dated entry.

Seat facts that a fresh session otherwise rediscovers by exploration:

- Code lives under ludus/ (bench/, arena/, atlas/, atlas_of_worlds/,
  worlds.py + stopworlds.py from cycles 001-002). Three world
  interfaces exist today (archaeology L-2); P1 proposes the arena
  interface as the survivor.
- ludus/atlas_of_worlds/atlas.db is NOT tracked (.gitignore *.db).
  It must be copied into a new worktree from the previous one or from
  the canonical checkout; its sha256 is recorded in the newest receipt.
  store.py opens it in WAL mode; atlas.db-wal / atlas.db-shm are
  ignored and are normal while a connection is open.
- Run bench tools from the repository root with PYTHONPATH=. ;
  arena tools run from ludus/arena/ (they import siblings).
- Verification commands: `PYTHONPATH=. python ludus/bench/verify.py`
  (writes ludus/atlas/rules_fidelity.json -- revert unless committing
  a verification), `python ludus/arena/verify.py`,
  `python ludus/arena/test_epistemic.py`.
- The seat owns no standing loop (MONITORS.md row: NONE). Do not
  create one without a named input and a productivity signal.
- Review packets: roles/Ludus/REVIEW_PACKET_<n>_<date>_<topic>.txt,
  pure ASCII, also delivered in chat as one block.
