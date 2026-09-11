# Arachne STATUS

Currency: 2026-09-11 (written at the base-role adoption pass). Plain language.

## Seat state: BLOCKED

- Blocker: an operator ruling on roles/Arachne/ARCHAEOLOGY_2026-09-11.md
  (BACKLOG ARACHNE-01). The operator's instruction on 2026-09-11 was set-up
  only: "Don't execute anything. Just set up."
- Asserting: PRESENT (folder, code, archive, registry rows). Not ACTIVE,
  not PRODUCTIVE. Nothing under agents/arachne/ has run since 2026-06-04.

## Where the seat is

- workspace: F:\Prometheus-worktrees\arachne-base-role (linked worktree; the
  canonical guard passes: git-dir differs from git-common-dir)
- branch: arachne/base-role-adopt-2026-09-11, base_sha 56125e9e4
- base role: read at 56125e9e4 (origin/main at the fetch), adopted; receipt
  roles/Arachne/BASE_ROLE_ADOPTION_2026-09-11.txt
- comms: synced (read through message 1 at 56125e9e4); status blocked
- machine: M1
- long-running processes owned: none
- worktrees owned: this one only
- last run of the seat's code: 2026-06-04T11:21Z, tick 700, from the
  canonical checkout (pre-D-23); residue archived at
  roles/Arachne/archive/run_2026-06-04/

## What is live and what is dormant (base rule 7)

- ArachneSwarm loop (agents/arachne/swarm.py --loop): DORMANT since
  2026-06-04. Never scheduled; no freshness file; no productivity signal;
  landscape availability unmeasured since June. Registered in
  roles/base-role/MONITORS.md.
- Landscape adapters: UNVERIFIED. Six answered on 2026-06-04. The LMFDB
  host moved after that (192.168.1.176 dead by 2026-06-23; local restore
  per roles/Ergon/DB_DIAGNOSIS_2026-06-23.md). Not probed on this pass
  (no execution).
- damage.py: code present, 9/9 operators per its June commit; in use by
  Ergon's damage lane as a reference implementation; no test fixtures
  (ARACHNE-20).
- Consumers of Arachne output: none with a receipt.

## What the June run left (facts, from the archive)

- 700 ticks; 21,209 edges; 5,621 nodes; six landscapes available.
- 21,209 of 21,209 edges carry crawler, landscape, op and null_p.
- Edge mix: oeis shares_prefix 6,393; knots same_determinant 4,492; groups
  same_order 3,636; lmfdb same_conductor 2,090; rosetta shares_concept
  1,870; mathlib uses 998; algolib calls 701; lmfdb isogenous 484; oeis
  similar_growth 273; groups same_exponent 188; operational computes 57;
  knots same_crossing 14; groups same_n_conjugacy 13.
- Lineage: 82 branches, 124 deaths, 42 floor revivals, 219 rosetta weaves,
  3 operational weaves; 7 alive at tick 700.
- Judge: holdout real_closer_frac 0.088 (bridge-only fabric; negative).
- Harvest: 5 verified computes anchors; 58 void targets; no consumer.

## Today (2026-09-11)

- Adopted the base role; created roles/Arachne with entry file, archaeology,
  backlog (30 items), calibration ledger (7 rows), status, journal, the
  operator prompt verbatim with manifest, the June archive with manifest.
- Added the D-23 guard to swarm.py (tick) and traverse.py (harvest).
- Added the ArachneSwarm row to MONITORS.md and the Arachne rows to
  INHERITANCE.md.
- Executed: nothing of the seat's science. Ran: comms boot/sync, a syntax
  check on the two patched files, the base-role self-test on the merged tree.

## Next executable action

None until ARACHNE-01. On an ACTIVE ruling: ARACHNE-02 (landscape census)
then ARACHNE-03, -06, -07 before any tick.
