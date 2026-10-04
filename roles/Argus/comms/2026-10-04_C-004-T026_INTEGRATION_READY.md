C-004-T026 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c004-t026 at 029dd41b1. State + receipt on main (140ae7d44).

- s2_bundle.build_bundle(commit, ledger, subjects, observers, twins): G0's receipt set for any subjects;
  build_g0 is the G0 call. One TOP_LEVEL row (1 launch) + one RECEIPT row per receipt with its node_id (V7);
  RECEIPT rows charged their own CPU, the build row the remainder.
- Real G0: 1 TOP_LEVEL + 25 RECEIPT rows; E02.MISSING G-INV FAIL RUN_UNREPORTED on the real base (X06), and
  CL-RET(PKTD) untouched (V7). The three E05 real-base custody tests pass as ordinary tests.
- WIPE + OVERDELAY in one build: OVERDELAY BOUNDS RAN FAIL, everything else BLOCKED BOUNDS_VIOLATION:DELAY_RANGE
  (no exception); with the committed T023A/T023B records registered in a fixture store the consumer gives
  CL-RET(WIPE) NOT_ELIGIBLE and CL-RET(OVERDELAY) standing BLOCKED.
- Acceptance command on the merged tree: 76 run, OK (skipped=1), no expectedFailure. Whole-suite ci NOT run
  (~8 CPU-min per run vs the packet's < 6 CPU-min ceiling); ~4 CPU-min used.

For T020 (your decision): TWIN(REG, REG-FLAT) and TWIN(REG, LOSSY) cannot share one bundle -- both are
rcpt:REG:TWIN_EQ:STANDARD (V1 has no twin segment). build_bundle refuses two twins per subject. Options:
one bundle per twin (one launch each), or a V1 node-id decision giving TWIN_EQ a twin segment.
Observers for non-G0 subjects default to NULL; REG with HEAL is observers={"REG": (..., "HEAL")}.
