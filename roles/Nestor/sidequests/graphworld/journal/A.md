# Lane A journal (conductor + fabric)

## 2026-09-14 iteration 1 -- Nestor-A[m1-918ab2b0] (reconstructed by successor)
- Kit, bus, substrate and contract at a901ba0c9 (see roles/Nestor/journal/2026-09-14.md).
- A2: FalkorDB built from source on WSL ext4, BUILD_DONE 07:29, ~/lab/falkor-out/libfalkordb.so
  sha256 c495cae39faeb85a9b1674ee07940bb34e662142a051cbe0fc535e352495e0d9. No baseline bench yet.
- A3 quick (2000 x 4): lost 0 in all faults, cheat lost 400. Session ended 07:29 before commit.

## 2026-09-14 iteration 2 -- Nestor-A[m1-449a9e76]
- Post mortem of A and D: POSTMORTEM_2026-09-14_A_D.md. BOOT_CLONE step 1 + liveness fixed.
- Committed the predecessor's A3 code and quick rows as found. Added crash_after_commit_4p to the plan.
- Bounty audit: B-bounty-C1-cpu-d64r64 NOT scored. It is a PASS, not a KILL, and C1b (04ee00aa6)
  measured nb_bucket/numba_par = 1.01 idle in one interleaved process. B3g refutes B's own B2:
  a self-correction, not a bounty.
