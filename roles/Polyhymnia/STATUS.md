# Polyhymnia status

Currency: 2026-09-11 (re-premise pass; PROBE-01 run).

seat state: ACTIVE. Re-premised by the operator 2026-09-11 as the
  representation scavenger (prompts/2026-09-11_reactivation_direction/).
  Standing state after this pass: ACTIVE on backlog items that need no
  reply (POLY-09..13, 18..21), BLOCKED for consumption on POLY-06
  (Archaeon's five-field answer to the H5 contract question).
what it asserts: PRESENT (booted in comms 14:46 UTC), ACTIVE (this pass
  ran), PRODUCTIVE in the narrow sense (one candidate family admitted by
  a real gate and measured exactly; rows committed), NOT YET CONSUMED
  (no experiment has taken a lincode member; the contract question is
  open), VALID for the analytic rows (8/8 controls PASS) and for the
  measured rows as exact enumeration; no usefulness claim.
workspace: F:\Prometheus-worktrees\polyhymnia-base-role, branch
  polyhymnia/base-role-adopt-2026-09-11; commits this pass 54221bfdb
  (archive, POLY-05, POLY-03), e6f0b64fb (preregistration), 8313700c1
  (probe run); merged origin/main 05b1134e6.
guard: linked worktree (git-dir differs from git-common-dir).
comms: synced 15:50 UTC (ack #43 from Archaeon); question to Archaeon
  (H5 contract) posted this pass, see journal for the id.
monitors owned: PolyhymniaDaemon, DORMANT, not to be restarted
  (operator). Fed: none.
done this pass:
  POLY-XL-01 DONE: body archived byte-identical (11,529,754 B, sha256
    020f5a43...), residue not substrate; census 2,415 cells / 13
    coordinate signatures / 6 of 9 axes constant.
  POLY-05 DONE: saturation curve; 2,137 of 2,415 tesserae on day one;
    last new tessera 2026-05-30T10:01Z, then 12 null ticks.
  POLY-03 DONE: 11 section markers on the old charter, 0 deletions.
  POLY-01 DONE: consumer = the H5 decoder slot (check_exact gate,
    exact_reference observable, campaign_h5.h5_readout live dict).
    PROBE-01: lincode family; hamming mean reach 5.6875 (0..7), mean
    neutral 2.25 with 256 fully neutral centers; direct 8.0 / 4.0;
    balanced_7 11.73 / 0.044; classes hamming 5.61 vs direct 7.78.
    8/8 controls PASS; M1 direction right; M2 direction WRONG (ledgered);
    P3 derivation wrong, corrected before the run (ledgered).
blockers: POLY-06 (Archaeon); POLY-XL-03 (operator: may an unlearned
  structured decoder be a beta arm); POLY-08 (ARCH-28, engine).
next executable action: POLY-12 (the collision-count check, so the M2
  error cannot recur), then POLY-10 (Gray family, second candidate
  through the same gate), while POLY-06 waits.
