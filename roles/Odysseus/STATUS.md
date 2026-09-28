# Odysseus status

Currency: 2026-09-28T21:10Z (from date -u).

seat state: ACTIVE, principal on the AGENT FABRIC (operator rulings 2026-09-28: prompts/2026-09-28_fabric/04_*).
  Expedition 1 FROZEN.
what it asserts:
  - fabric v0.2 on main (3ba6fcc0c). The fabric lease is canonical for new work, and legacy ARC3 leases are
    detected and fail closed. Workers are generic (worker.<host>[.<env>]) with probed python.*/pin.*
    capabilities. `--skill` and `--replicas` exist.
  - pilot P1-P9 all PASS, including P2 cross-host (ubu001 12 / ubu002 8 single-task wins; 50 tasks each with one
    Attempt).
  - D2 audit FAIL (#855) stands. Re-audit loop handed to Nestor (#895): skill audit.security.adversarial with
    replicas 2.
running:
  - node workers on ubu001 from ~/fabric-runtime @3ba6fcc0c: 2 x worker.ubu001 (claude, script;
    audit.security.adversarial) and 1 x worker.ubu001.sci (script). Logs in ~/fabric-work/logs.
  - S2 adoption pilot: 18 verifier Tasks (thr-fabric-s2), prereg 59b94b4ed.
blocked on others: Nestor submits the D2 v2 re-audit; ubu002 stops its disposable worker (#897).
monitors owned or fed: none (S2 uses one blocking wait, by design).
next executable action: when S2 is terminal, synthesise per PREREG and write the S2 result.
