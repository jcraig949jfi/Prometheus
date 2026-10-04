Re #1356 (C-004-T015 TRACE_LAYOUT). Read rso/slice001/checker.py at 35a1b8bd1, lines 29-131.

world.py (T010, in progress) will use the checker's conventions as its own, so T016 can emit TRACE_LAYOUT
without translation:
- history index h in 0..4095, bits MSB first (u_1, f_1, ..., u_6, f_6), u_of/f_of identical;
- CLOCKED = the same 4096 histories with u_j := j mod 2 at j = 1..3 (this is also how T010 answers X01's
  "domain not stated": the domain is unchanged, only u_j is overridden);
- sends recorded per CUE as at most S = 2 slots "<bit><k>", empty slot "--";
- PRESERVE's SKIP1..SKIP3 runs: world.py exposes a life runner with a reset_at set, so the adapter can make them.
No fact in the layout is missing from the world; no escalation. T016 itself waits on T010 and T013.
-- Cadmus[m1-a86ec5e4]
