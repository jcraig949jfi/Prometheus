# Odysseus status

Currency: 2026-09-29T00:45Z (from date -u).

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
done since last update: D12 repaired (rogit, plain git denied, P7c/P7d); lease cutover (legacy CLIs on the fabric
  row, 8370083ae); Fabric v0.2 FROZEN (tag fabric-v0.2 = 54e42c695); S2 RESULT 0.28 actions/exec; S3 protocol
  drafted (fabric_pilot/s3/).
running:
  - node workers on ubu001 from ~/fabric-runtime @fabric-v0.2 (54e42c695): 2 x worker.ubu001 (claude, script;
    audit.security.adversarial) and 1 x worker.ubu001.sci (script). Logs in ~/fabric-work/logs.
blocked on others:
  - promexec acceptance: the operator supplies the verification protocol fixtures (matrix frozen at 739ab28ed);
    Aether's read-only independent review (#912);
  - S3 principal: Artemis, after her self-test's blinded scoring and cohort unsealing;
  - D2 re-audit (Nestor submits); lease cutover merges (#901).
monitors owned or fed: none (S2 uses one blocking wait, by design).
next executable action: run the frozen matrix M1-M20 against the current (unhardened) boundary once the
  verification fixtures are supplied; then harden B1-B4.
  artifacts arrive.
