# Tyche v2 Block R report -- latent option value under unannounced regime change

Currency: 2026-09-30. PREREG roles/Tyche/prereg/2026-09-30_v2/PREREG_BLOCK_R.md
(e9fd76349) + amendment 1 (7fc0cf97a, memory). 36 runs: H {STRICT, LEX,
RES} x V {solo x4 worlds, related, broad} x seeds {1, 2}; 50 generations,
law switch at 20 (unannounced), 30 post-switch generations. All 36 rc 0.
Verdicts from tyche/v2/report_v2.py (PHASE_DIAGRAM.json, block_r);
histories from tyche/v2/history_v2.py (HISTORIES.json per run).

## Verdicts (preregistered)

    RH1 mean OV RES < LEX < STRICT ......... FALSE (RES 30.12, LEX 31.0, STRICT 31.0;
                                             censor = 31)
    RH2 stored optionality RES > LEX > STRICT FALSE (LEX 0.115 > RES 0.075 > STRICT 0.055)
    RH3 mean OV broad < solo ............... FALSE (broad 31.0, solo 31.0, related 30.12)
    RH4 mean OV R3 < R4 .................... FALSE (both 31.0)
    RH5 R2 (order-3) adapted cells ......... 0 of 18 (predicted 0: held)

## What happened

Adaptation to a new zero-marginal law within 30 generations was almost
absent: 2 of 72 (world x condition x seed) cells produced a replicated L2
sense, both in the related condition, seed 2.
  RES  R1 (L2 = xor of 2 new delays): fused coalition, test +0.496,
       option value 10 generations.
  STRICT R3 (L2 reuses one L1 precursor): fused coalition, test +0.337
       (admitted; the option-value clock did not register it -- see
       instrument gap).

Stored optionality at the switch (fraction of living lenses whose outputs
functionally carry an L2 precursor):
                 any precursor    ALL precursors
    LEX             0.115            0.000
    RES             0.075            0.0006
    STRICT          0.055            0.000
    broad           0.120            0.0003
    related         0.079            0.0003
    solo            0.045            0.000
  Diversity raises fragment storage monotonically; lexicase stores more
  fragments than the explicit reserve; the COMPLETE precursor set is
  essentially never co-stored (max 0.007 of living lenses in any run).

## Natural histories (92 senses across all Block R runs, all phases)

  assembly: COALITION 16 + COALITION+EXAPTATION 46 = 62; MUTATION 10 +
    MUTATION+EXAPTATION 11 = 21; GRAFT 2 + GRAFT+EXAPTATION 6 = 8;
    INITIAL 1. Exaptation (a transition parent or donor significantly
    valued on another world) in 63 of 92.
  why zero-utility precursor lines persisted (event counts, all runs):
    parent choice decided by a NOISE-level case 395; by a SIGNIFICANT case
    (another world or organism) 280; drift-born 120; reserve age/credit
    94; elite 53; reserve novelty 36; reserve random 2.
  mean fraction of solution-path ancestors that ever held a significant
    case (would survive STRICT gating): 0.929.

The one reserve-arm L2 adaptation, traced (RES related s2, R1 -> L2):
  precursor 0 first carried at generation 2 by a DRIFT-born reserve
  lens; precursor 1 present at initialisation; neither was valued
  anywhere; for ~20 generations of zero utility the lines persisted by
  drift-born members 56, reserve age/credit 39, reserve novelty 18,
  noise-level parent choice 1; after the switch a coalition fused them
  (+0.496, replicated) within 10 generations; only 0.50 of its path
  ancestors would have survived strict gating. This is the directive's
  mechanism -- useless variation preserved by an explicit reserve until
  the world changed -- observed once (1 of 24 RES cells), not a rate.
The STRICT R3 adaptation took the exaptation route instead: its reused
  precursor line was significantly valued on R1 and R2 throughout (155
  significant parent choices, 137 noise-level; strict-survivable 0.97).

## Instrument gap (found in analysis)

The option-value clock reads the population's best val gain per slot; it
does not see admitted coalitions, which are fused and never re-enter the
population matrix. A coalition-built adaptation is therefore counted as
L2-solved but may be censored in OV (STRICT R3). RH1/RH3/RH4 are
unaffected in direction here (almost everything is censored), but the
clock must read admitted coalitions in Block M and later.

## Reading

1. Unannounced regime change to a zero-marginal law is a hard wall for
   every ecology tested within 30 generations; latent option value is
   near zero for all of them.
2. What ecologies store is FRAGMENTS of future senses; storage of any
   fragment scales with world diversity; complete precursor sets are not
   stored by any mechanism tested.
3. Senses that did appear were overwhelmingly coalitions with exapted
   parts; noise-level selection and significance elsewhere carry most
   precursor persistence; the explicit reserve produced the one clean
   "preserved-useless-until-needed" adaptation.
4. My predictions RH1-RH4 were wrong; RH5 held.

## Successors

- Longer post-switch horizons (the wall may be a clock artefact of 30
  generations) and the OV clock reading coalitions.
- Precursor-SET storage as the target of reserve design (novelty over
  pairs of outputs, not single signatures).
- Block M (static pressure map) with the same tracer, as designed.
