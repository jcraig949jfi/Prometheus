C-004-T016 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch: argus/c004-t016 (code 0e76f487c; merged origin/main 24824a0a6 -> 83c528216; state + receipt on top).
Receipt: ops/campaigns/C-004/tasks/C-004-T016/attempts/A-001/RECEIPT.json (check-receipt OK).

- adapter.py world_runs: world.run_life over 4096 histories -> RESET, SKIP1..3 (one reset left out),
  CLAMP (capture / a := v / restore into fresh at the reset hook of j). Traces written with
  checker.make_trace, so exactly TRACE_LAYOUT (FD-T015-1); PRESERVE runs travel as SKIP1..3 in
  trace:probe_a; ERASE reads trace:sends.
- make_receipt: outcome verbatim from the ruler/gate callable; identities, outputs, B6.2 deps,
  execution, measured resources; validated Receipt. Out-of-model runtime -> BLOCKED
  BOUNDS_VIOLATION:<bound>, no outcome, no traces.
- Round trip world -> adapter -> checker.g_recomp PASS for REG, PKTD, LAGD with the contract's
  expected outcomes (LAGD ERASE FAIL witness h=64 partner 0 j=3 e=4 PROBE_A reproduced from world runs).
- Cheat controls: swapped probe_a bytes and one flipped sends byte -> BYTES_MISMATCH; ERASE PASS
  claimed over LAGD's true traces -> OUTCOME_MISMATCH:value.
- RED import error; 16/16; mutants M1-M6 killed (M3 survived the first suite; test added).
- ci on merged tree x2: 219 run, 218 passed, 1 skipped, 0 failed. T022's flake fix holds here.

Escapes: no world-run producer for trace:deliveries / capture / observer (caller passes bytes;
T011/T018); real rulers (T012) and reset predicates (T011) meet this layout first at T020.
Field decisions FD-T016-1..5 in the receipt notes.
