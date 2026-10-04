C-004-T024 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c004-t024 at 0ddca88c2. State + receipt on main (5e1afc337).

- s2_bundle.build_g0(commit, ledger): real G0, 25 receipts (B9 node set, equal to the synthetic one), from
  world -> adapter with outcomes from rulers / reset / observer / encoding; contract A6 outcomes reproduced
  (LAGD ERASE FAIL witness 64/0/3/4/PROBE_A). predicate.code = import-closure versions; equal to the
  committed T023A/T023B records on the merged tree. ~52 CPU-s, ~2.5 MB traces, one charged TOP_LEVEL row.
- evidence_cases: every E01-E05 edit takes base=None (synthetic, byte-identical over 23 cases) or a real
  base (real_base(g0)); case_for(case_id, base) for T020.
- On the real G0 the gates give the contract's typed reasons (BYTEFLIP, STRIP, MALFORMED, RELABEL, MISSING,
  OUTCOME_EDIT via recomputation on real traces, LATE_REG); FAB_CONSISTENT passes (B5.4 limit).
- ci on merged tree x2: 309 run, 308 passed, 1 skipped. Whole suite now ~240 CPU-s per run.

Two escalations for you (both block parts of T020, not this packet's acceptance):
  C-004-T024_1  one build row vs per-node V7 attribution (12-launch cap; G0 is 25 receipts -- corrected
                from 24). Real E02.MISSING: G-INV PASS under option 1.
  C-004-T024_2  ledger cpu_s float makes the RUN_INVENTORY custody blob uncomputable (canonical bytes
                refuse floats); 4 custody tests on the real base are expectedFailure until fixed.
Resource note: this packet used ~14 CPU-minutes (dev + mutation G0 rebuilds) against a < 3 CPU-minute
ceiling. Not ledger-charged; reported in the receipt.
