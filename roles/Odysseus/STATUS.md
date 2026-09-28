# Odysseus status

Currency: 2026-09-28T21:45Z (from date -u).

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
blocked on others: Nestor submits the D2 v2 re-audit (not chased, per ruling); operator picks the S3 principal and
  decides the code-execution sandbox (S3 s2 option A); Nestor/Ananke/Archaeon merge the lease cutover (#901).
monitors owned or fed: none (S2 uses one blocking wait, by design).
next executable action: none of mine on infrastructure (frozen). Next: break the fabric under S3; adjudicate D2 when
  artifacts arrive.
