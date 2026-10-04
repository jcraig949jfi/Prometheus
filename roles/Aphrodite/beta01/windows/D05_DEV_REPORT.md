# D05 -- DEV WINDOW 5 REPORT: midpoint synthesis + R7 apparatus

C-006 (C-P2B-APH-BETA-01), cycle 5, DEV. Apparatus v2b-2 + gtc (R7). Evidence tier 2.

## 1. Bottleneck
Midpoint synthesis 1 (beta01/windows/MIDPOINT_1_SYNTHESIS.md): the limiting rung is **R7 (improver change)**. Four
tests never changed the improver. T51 points at its proposal mechanism, which can only re-find or derive what it
observes or is shown. A negative at R8 is uninterpretable while R7 is untested.

## 2. Changes
- `engine/v2b/gtc.py`: donor_g, a genome-parameterised copy of a18.donor with 5 genomes (g0, g2, g3, g4, g5).
  Content-free rules only (W4 s0.1). g1 is deferred.
- `engine/v2b/gtc_run.py`: the chain runner (2 generations), stratified scoring (DEV/UNSEEN by top-level operator) on
  the D endpoint, and the frozen GO/STOP/INCONCLUSIVE rules.

## 3. Qualification
- **Conformance gate:** donor_g('g0') == a18.donor on 3/3 real T51 donor jobs (P, G1, PA), with identical selection,
  entries, table, meta charges and derivations. Took 14 minutes.
- **The operator classifier** returns the correct top-level operator on fixtures.
- **Plan:** 4/4 chains fill their roles and scoring sets. UNSEEN supply is 5-21 per seed, so 8 are used on gen-2
  seeds 4-7.
- **Smoke:** chain 0 with g0/g5 at a 20k scoring cap exercised every stage. Pre-freeze exposure of two chain-0
  selections is disclosed in the T05 spec s6.

## 4. Next frozen experiment
TEST-5 = GTC: `beta01/windows/T05_GTC_SPEC.md`.
