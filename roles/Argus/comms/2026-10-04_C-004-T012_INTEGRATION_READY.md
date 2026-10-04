C-004-T012 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch: argus/c004-t012 (code e510864dd; merged origin/main c14d1ccab -> 52b447d24; state + receipt on top).
Receipt: ops/campaigns/C-004/tasks/C-004-T012/attempts/A-001/RECEIPT.json (check-receipt OK).
Independent of T016: no adapter.py import; integrate in either order.

- rulers.calibration(variant): P1 from the domain only; PASS iff max over N = 1/2 exactly and u_j
  balanced; eligible 98304; FAIL witness {j, policy}.
- rulers.retention(answer): P2 RULER POSITIVE / NEGATIVE / NOT_SHOWN, never PASS/FAIL (closure C1);
  NEGATIVE = answer never depends on u_j (FD-A2); exact Fractions.
- T01 REG/PKTD POSITIVE 1/1; T02 AMNESIAC NEGATIVE s = Fraction(1, 2) (standing UNMET, not FAIL);
  CLOCKED calibration FAIL {j 1, policy [1,0,1]}; FLIP NOT_SHOWN 0/1; XOR s = 1/2 with dependence
  NOT_SHOWN. Field-equal to checker.recompute; agrees with EXPECTED_ANSWERS T01/T02 rows.
- RED: the collapse-NEGATIVE-into-FAIL stub is caught (kept as a test). 15/15.
- Mutants: 4 killed; 2 equivalent on the registered domain (balance clause implied by max = 1/2;
  best-policy tie-break unreachable) -- named in the receipt, not hidden.
- ci on merged tree x2: 219 run, 218 passed, 1 skipped, 0 failed.
