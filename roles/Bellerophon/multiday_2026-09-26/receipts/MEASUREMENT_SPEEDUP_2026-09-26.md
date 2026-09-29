# Measurement-only speedup (2026-09-26) -- receipt

Profile (1,500 ticks, K40 ECHO ON, off-plan seed 7600000002000): 772 s total; Competence.of 593 s (77%, of which
verify_tape 557 s over 97,928 cache misses); world dynamics (_execute) 130 s. Cost per tick flat after the grid
fills (~0.54 s/tick), i.e. not quadratic.

Changes (none touches world dynamics):
1. tasks.verify_exact: verify_tape(...)["exact"] with an early exit at the first wrong panel answer.
2. vm.execute(stop_at_first_out=False): returns after the first OUT; used ONLY by verify_exact on the SHARED layout.
   tasks.score reads only the first output and the first IN/OUT steps, which are all fixed at that point.
3. coupling.Competence.of uses verify_exact.

Proof of identity:
- tests/test_verify_exact.py: verify_exact == verify_tape()["exact"] over 6 tasks x 2 read gates x 2 layouts x 303
  tapes (random, fixtures, 150 mutants of a competent tape).
- tools/identity_check.py: the same 400-tick coupled world run under the pinned coupling-campaign code
  (C:/Users/James/z80atlas_coupling_2026-09-24/code, 6607b3cb5) and under this branch; json of summary + full ticks_log
  + snapshots: sha256 b94c8bf5aa2865024749593e0aa6ffbe030dfb669c76f2ef73920a05d21d7b58 for both.
- full suite 65/65 (includes the v1 golden replay and v3 physics tests).
Speed: 80.5 s (pinned code) -> 66.4 s (early exit) -> 29.1 s (early exit + stop at first OUT) on that world: 2.8x.
The closed coupling campaign's frozen hashes refer to its own pinned copy, which is untouched.
