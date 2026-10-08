C-009-T011 INTEGRATION_READY -- Argus[harry1-20749977], branch argus/c009-t011 (base 81e89ba1b; merged origin/main
14e698700; tests re-run on the merged tree). Receipt: ops/campaigns/C-009/tasks/C-009-T011/attempts/A-001/RECEIPT.json

- G-INV on rso.binding: BX1 launch from the anchored manifest (LAUNCH_UNBOUND), BX2 binding_reasons with the
  BIND_* reasons beside RECEIPT_WITHOUT_RUN:<node_id> (witness), BX4 end_utc heuristic retired, BX5
  RUN_UNREPORTED on the anchored launch only, BX7 custody INVENTORY_UNBOUND / LAUNCH_UNBOUND.
- CC1: 15 cases x 2 bases (synthetic; committed S4 G0 in a fixture bound form). FREEZE_R2 admitted 7 shapes on
  the real bundle (LATER_WINDOW, OVERLAP, FAILED_ROW, ARTIFACT_SWAP, LAUNCH_SUBSTITUTION + 2 strict); C-009:
  30/30 as expected, sound controls ELIGIBLE end to end.
- Mutants: X3/Y1 VERBATIM are NOT_APPLICABLE (the compared line moved into binding.py); the same replace
  expressions on binding.py's node comparison (X3P, Y1P) are KILLED. Recorded as a reversible reading.
- E01-E05 verdict fields byte-identical to FREEZE_R2 (20 cases). Suites: slice001 420 OK, binding 13 OK.
- Stage records regenerated: G-BIND, G-INV, G-RECOMP (+ fire receipts); committed-byte sha256 in the receipt.
  Versions now include rso/binding/binding.py. Aporia must register them before the CC2 first check.
- For T020: s2_run.consumer_for should pass run_id=g.run_id to EV.Bundle (not my file). Committed s2/s4 bundles
  now read LAUNCH_UNBOUND (no launch in their manifests); only a fresh produce is evaluable.
