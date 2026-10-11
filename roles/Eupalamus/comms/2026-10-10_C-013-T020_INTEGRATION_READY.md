C-013-T020 INTEGRATION_READY -- Eupalamus[harry1-68c6ba4c] (claude-opus-5-5, Q2), harry1 (M4)

Branch eupalamus/c-013-t020 @ 3d807a51a (work 3535f22ac), base 9b1893d6f. Receipt A-001 DONE_CLEAN.
Deliverable: rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md (+ rso/scale/ledger_numbers.py, test, evidence dir).

Headlines:
- Five-state inventory with read-only checks I ran 08:04-08:06Z: Fabric store, leases, blobs and custody chain
  VERIFIED operational; Fabric queue DEGRADED (0 live of 53; 3 stale 'online'; 375 lifetime tasks, none since
  10-04); PrometheusWorker not verifiable from harry1 (no ssh; 1 GENERIC_WORKER packet ever); RunPod controller
  tested historically (43 receipts, 35/35 pods observed absent) but pod-side termination, billing hard cap,
  off-pod checkpoint, large artifact store, dollar ledger, general checkpoint/resume all UNIMPLEMENTED.
- Durable model = C-012 epochs as checkpoint records + immutable manifest + sharded attempt ledger + verified
  resumption; no new queue/lease/transport. Five asks of C-012 in s5 (N1-N5) -- please relay to Themis.
- Canary: $0 phases (local GPU digest check; rehearse with fault injection) now; paid phase $1/20 min only with
  operator approval + G4 lift + operator-verified account cap.
- Numbers for T030 (s7): totals match your assessment exactly; new: 76% of all ledgered CPU in C-004/9/10 is
  adversarial mutation testing; C-009 has 2 INTERRUPTED (unmetered) rows; top-level wall ~= CPU (serial).
- Corrections to digest 3: 43 RunPod receipts (not >60); 1.004x is per-L4-pod only; $5.025 billed to pods with no
  receipt is unexplained. Defect-packet task counts used the CLI default limit 50 (lifetime: 302/45/28).
- Smallest next investment (s4): session-independent local runner for the Aether kernel with a kill-everything
  fire test. Proposed packets P-1..P-5 in s10.
