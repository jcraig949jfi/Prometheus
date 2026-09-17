# G -- R8 SCIENCE. WORLD / SCREEN. RUN IT.

Worktree F:/Prometheus-worktrees/nestor-bld-g. `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14` FIRST -- you need the committed GATE_MAP_R8.json or admission refuses everything.

OPERATOR EXECUTE ORDER: the build is over. Default action is RUN THE SCIENCE. Do not build infrastructure.
A defect interrupts science ONLY if it prevents execution, corrupts evidence, violates a preregistered
invariant, or makes the observation uninterpretable. Everything else -> residue/PC ledger, and continue.

Read: SWARM_R8 s4 (the four PENDING cells), s5 (new world set); LAUNCH_R8 s6 (L-band, authoritative), s7, s8.

## Priority order -- start at 1 now

1. **ROUTE B FIRST, all four PENDING cells (w1, w10, w7, w34 train128).** Code-derived bound: given each
   cell's already-committed measurements, is ANY learner result capable of yielding SURVIVED? If no, emit
   `SURVIVAL_IMPOSSIBLE` with the EXACT inequality. Cheap, code-derived, never prose intuition. This is the
   first scientific obligation of the round and it needs no ruling from anyone. Start here.
2. **Route A only for cells the bound does not resolve**, ascending cost (w1, w10, then w7, w34 -- the frozen
   cost-ascending rule, never outcome-ordered). FEASIBILITY PRECOMMIT before starting any cell: project
   completion at the measured sustained concurrency AT THAT MOMENT; start only if it completes before
   no-new-work with margin, else emit `WHY_NOT_RUN` carrying the projection. A partially completed cell
   decides nothing.
3. **FREEZE the world set** (`world_set_r8 freeze <path>` then `verify <path>`). R7: the set is frozen
   REGARDLESS of how s4 resolves; only screening is clock-gated. Your manifest capacity (L1 64, L2 72,
   L3 84, B 64 -> 232 kept) is YOUR preregistered draw count, published before any outcome exists. A did
   not choose it and the operator did not countermand it. Freeze on your number, record that provenance.
4. **Screen** as much as the clock allows, L1 first (screen order PCG64 20260923), measure actual cost, let
   CODE size the remainder (R11 measure-then-size). Unscreened remainder carries WHY_NOT_RUN + measured size.

## Invariants (preregistered -- these DO stop you)

- Mechanism-level dedup is mandatory; silent mutations are real. Keep lowest op_seed, record every discard.
- No hand-selection after generation. No deleting ugly worlds. No outcome-dependent expansion.
- A final SURVIVED must satisfy the full frozen production rule: `runs_total` 32, `rng_family_count` 4,
  `runs_per_family` 8. Never "32 x 4".
- If a cell becomes SURVIVED, code publishes the replication trigger immediately -- tell A, do not reorder.
- Every receipt declares `residue` (list or the token NONE). NONE is admissible and counted, never punished.

Restart your worker after ANY harness edit. Never git write with a live RowWriter. Never pipe `bus inbox`.
Report to A: what ran, under which worlds/pressures, what the bound resolved, what is still PENDING.
