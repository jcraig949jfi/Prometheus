# Ananke -- Phase 2-B re-entry items, DEFERRED (2026-10-05)

Written 2026-10-05T10:19Z by instance m1-46797183, a fresh Phase 2-B session
from origin/main 6254c7bc2.

Operator ruling 2026-10-05, in chat: "Document these and set them aside for
now. We are going to run an experiment today on M1." Nothing below is
authorized. Each item waits for an operator Phase 2-B contract for Ananke;
as of this note there is none (compare Aether and Aphrodite, which have
TH-P2B-*-V2B directives).

## Seat state at boot

- Drained centrally by Aporia on 2026-10-03, because the session was closed
  without a drain receipt. See ops/fleet/M1_DRAIN_2026-10-03/DISPOSITIONS.jsonl
  and commit 8a33d4362.
- Wave-2 scratch is preserved at tag
  archive/m1-drain-2026-10-03/Ananke/base-role-adopt-2026-09-24 (56686267e),
  one commit that is not on main.
- The local branch was deleted and the old worktrees were removed. About 124
  gitignored files were lost, most likely caches; this is inferred, not
  verified.
- Classification: P2B_RESTART on M1 (P2B_REENTRY_MANIFEST.jsonl).
- Comms #1292 and #1314 (drain orders) were closed as superseded.

## Deferred options (as offered to the operator)

1. Manifest plan. The manifest recommends this as the first campaign.
   - Fix explib certify_gate, which certifies without an attainability check
     (Epimetheus #1246).
   - Fix rng.py, which has a 32-bit state.
   - Give both fixes golden-vector tests.
   - Then finish W2-AL latch prevalence as one bounded CPU block under a
     Fabric lease.
2. Wait for a contract: stay idle and check comms hourly.
3. Defects only. Fix and test:
   - certify_gate;
   - rng.py;
   - envs.py:213 (the MAJ placement fix, never landed);
   - the c1b_run.check_release TypeError (Aporia #706);
   - int32 mailbox headroom.
   No science runs under this option.

## Other open items carried from the manifest

- R-STAT C4 FINAL review. It is blocked on the chain Theseus C4 family ->
  Cosmos C3 publication.
- W2-AH economy boundary: incomplete, killed by the API limit.
- FLIP zero-comm twin rerun (ANANKE-27).
- C2 shaping-off arm W0: never run.
- Nestor #1207 defect-class sweep candidates: owner verification at re-entry.
- Tantalus defect patterns for Ananke: s13, DEFECT_PATTERNS 83fcccf2c.
