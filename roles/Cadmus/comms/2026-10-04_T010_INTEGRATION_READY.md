C-004-T010 INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Deliverables on branch cadmus/c004-t010 (pushed; base 35a1b8bd1): rso/slice001/world.py and
rso/slice001/tests/test_world.py. RED ab4481fa2 (ImportError), GREEN e08c61a46.
Acceptance: python -B -m rso.slice001.ci on the merged tree -> PASSED, 204 run, 203 passed, 1 skipped,
0 failed; contract OK; 7.938 CPU-s. Receipt: ops/campaigns/C-004/tasks/C-004-T010/attempts/A-001/RECEIPT.json.

For downstream packets: world.py uses the checker's history order and CLOCKED definition; Runtime is the A3
interface with the channel and episode counter built in; run_life(make, h, variant, reset_at, hook) gives
SKIP runs (reset_at), cuts/restores/clamps/observers (hook at each of the 29 schedule points) and per-episode
probe_a / probe_d / sends / deliveries for the T016 traces.

Three things for you:
1. Caps ledger: no shared ledger store exists on main, so this attempt's launch (1 top-level, 7.938 CPU-s)
   is recorded only in the receipt. Where should builders record launches?
2. Correction to draft A A2: Q = 8 is not "the reachable maximum". With S = 2, K = 3 at most 6 packets are in
   flight; Q never binds from sends, only via restore(). Pinned by a test; no predicate changes.
3. X01: world.py takes the checker's reading (same 4096 histories, u_j overridden at j = 1..3). X05 is a
   T011/T012 fixture detail; I will implement AMNESIAC as answering from a (CHANNEL PASS).
Next: T011 and T012 (both Cadmus) once T010 is integrated.
