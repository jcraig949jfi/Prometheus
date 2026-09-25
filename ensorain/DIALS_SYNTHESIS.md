# Dials of intelligence in Ensorain's worlds -- synthesis after 4 rounds

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5]. ~19,300 lives across
Round 1 (4,800 random), Round 2 (3,192 confirmation grids), Round 3
(4,800 local design), Round 4 (1,536 confirmation grids), plus dev and
sensitivity rows. Every round preregistered before its rows
(PREREG_D1/D2/D3; Round 4 fixed inside PREREG_D3). Reports:
D1_ROUND1.md, D2_ROUND2.md, D3_ROUND3.md, this file for Round 4.

## Round 4 (fresh seeds 90000+, 16 lives per cell, alpha .05/11)

    nom  pair                     ruler  F      p        r     result
    M1   scratch x start          NLMSE  11.39  3.9e-5   .93   REPLICATED
    M2   cap x replay             NLMSE  2.27   .065     .92   shape holds, not significant
    M3   sweeps x kappa           EFF    5.31   5.3e-4   .34   --
    M4-M11 (x kappa, scratch x cap, scratch x drift)  EFF  p >= .0065  --
EFF couplings that are TRUE BY CONSTRUCTION (price x compute) did not
replicate at 16 lives per cell: Round 4 is under-powered for EFF; its
EFF nulls are not evidence.

M1 shape, NLMSE by scratch level (58 / 181 / 430):
    correct start   -0.21   0.14   0.66    (+0.87)
    random start    -0.37  -0.18  -0.18    (+0.19, saturates)

## What survived (the whole claim, and nothing more)

ONE organism-intrinsic coupling replicated on fresh seeds: TIMESCALE
SEPARATION (samples gathered between slow consolidations) x
REPRESENTATION CORRECTNESS (is the memory's mode order the world's). Slow,
batched consolidation pays ~4.5x more when the representation is right;
with the wrong representation its benefit saturates early. An amplifier,
not a crossover, not a phase transition.

One candidate is alive but under-powered: CAPACITY x REPLAY (replay is
costly only under capacity pressure; neutral with slack) -- the
compression <-> fidelity trade, shape replicated (r .92), p .065.

## What did not survive

T2 PHASES: not supported in any round. The only sharp dichotomy in dial
space is DIVERGED vs not (about half of all random-dial lives), and it
is predicted by main effects alone (AUC .86 with or without couplings).
T3 PRECURSORS: none in any round (Round 3: 319 firing lives; surprise
falls before FIRE in both halves but q .40).
T1 as a GENERAL law: most nominated couplings were construction
artifacts -- accounting (price x compute inside EFF), definitional
(memory family x a knob acting on family-specific parameters), or floor
compression (clipped rulers). Main effects dominate every ruler in every
round: stability, timescale separation (scratch), consolidation depth
(fewer sweeps is better once divergence is possible), drift, capacity,
representation correctness.

## Dial-by-dial, in these worlds (main effects, local design, NLMSE)

  timescale separation (scratch)   strongest positive (+.35)
  drift                            negative (-.20)
  stability (lam)                  positive (+.17)
  representation fluidity          NEGATIVE (-.17): in-life restructuring
    (p_restruct)                   by batch-accepted swaps is destructive
                                   and does not rescue a wrong order
  consolidation depth (sweeps)     negative (-.16)
  forgetting-as-shrinkage          positive (+.14)
  capacity                         positive (+.14)
  replay / error persistence       negative when they steal capacity
  internal generation (dreams)     ~0
  self-disturbance                 ~0 locally, harmful at wide ranges
  surprise weighting               harmful above ~.3

## Method lessons (transferable to any dial search, including Cosmos's)

1. Uniform random dials spend ~97% of lives in dead or divergent regions;
   search for couplings where the ruler moves.
2. Clipped rulers create floor compression that erases true couplings;
   use unclipped rulers (NLMSE) and a rank-scale check.
3. Most "couplings" in a naive nomination list are the experiment's own
   accounting or definitions; classify before confirming.
4. Every coupling test needs a shuffled control, a planted control, and
   a mechanism planted in the DESIGN. Ours was recovered -- and its shape
   refuted the seat's story about it.
5. Confirmation must be on fresh seeds with a stated alpha; 1 of 11
   Round-3 nominations and 2 of 6 Round-1 nominations replicated.

## Reading against the operator's thesis

"Intelligence = phase behaviour of a coupled adaptive system" is not
supported in these worlds at this scale: no phases, no precursors, one
replicated coupling that amplifies rather than transforms. The one
survivor is, however, exactly the kind the thesis predicts: its value is
the RELATIONSHIP between a timescale dial and the fit of the
representation, not either dial alone. Whether it survives a world whose
mechanisms are entirely different (E0's navigation world, a different
learner) is the test that would make it a law rather than a property of
ALS in tensor worlds.
