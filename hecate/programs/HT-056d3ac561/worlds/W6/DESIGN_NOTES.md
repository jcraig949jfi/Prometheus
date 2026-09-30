# HT-056d3ac561 / W6 -- design notes (Pass 3 v2 generator)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: implemented candidate (controls only). Nothing here is evidence about M9.

## What it tests

M9 (sparse test selection), lens L3 (hidden truth measures what the chosen
relations can see). A 2-sparse fault in R^64; a pool of 256 relations, each
a noisy linear residual touching 6 fault components; budget 24. The
treatment chooses each next relation by expected covariance reduction of a
Kalman belief whose prior variances are re-estimated as sparse (SBL/ARD EM)
after every result. Decoding is a fixed OMP shared by all arms, so the arms
differ only in which relations are run.

Why the three concepts are load-bearing: under a fixed Gaussian belief the
covariance recursion is data-independent (Riccati), so greedy Kalman
selection is a fixed design (REFERENCE_GAUSSIAN_GREEDY). Only the sparse
re-estimation can make selection adaptive. Metamorphic relations are the
measurements (residuals without an oracle).

## Control values (1500 pooled trials, 5 seeds)

| arm | accuracy |
|---|---|
| POSITIVE_CONTROL (oracle-targeted) | 0.987 |
| REFERENCE_GAUSSIAN_GREEDY (knockout control) | 0.282 |
| REFERENCE_RANDOM (control) | 0.233 |
| NULL_TWIN (decoy-targeted) | 0.187 |

S1 accuracy >= 0.60; S2 >= random + 0.25 (= 0.483); S3 >= Gaussian greedy
+ 0.15 (= 0.432). Positive: 0.987 / +0.754 / +0.705. Twin: 0.187 / -0.046 /
-0.095. Cheat passes all. Frozen.

## How it avoids the earlier failures

- W1: an oracle that could not see the effect. Here the oracle is measured
  at 0.99 against random 0.23 before freezing.
- W4: a positive control that could not meet its own clause, and a
  per-cell vs pooled ambiguity that decided the class. Here each clause is
  one pooled number and was checked on the positive control.
- W4's open stupid explanation (incoherent dictionary makes any method
  work): here random and a good fixed design both fail (0.23, 0.28), so a
  pass cannot come from the pool being easy.
- Budget revision (rev 1): at budget 12 even the oracle only reached 0.86;
  a world that no non-oracle could pass would be a guaranteed, uninformative
  failure.

## Ambiguities resolved

1. "Tests needed to localize" (M9's observable) turned into accuracy at a
   fixed budget of 24: one number per trial, no stopping-rule ambiguity.
2. Relation residual noise is drawn once per (trial, relation), so every
   arm sees the same residual for the same relation.
3. Controls REFERENCE_RANDOM and REFERENCE_GAUSSIAN_GREEDY are computed in
   controls.py only because S2 and S3 are differences from them; the
   implementer reruns them in the same code path (values must reproduce
   0.2333 and 0.2820).
4. Treatment gamma update: 10 EM iterations after every result, floor 1e-6,
   initial tau2 = 2*(7/3)/64 (matches E||f||^2); written in the spec so no
   treatment parameter is left for the implementer to tune.
5. The treatment may not read the fault, the decoy, or the oracle's
   choices; its rng is its own.

Honest caveat (not resolved here): a pass would not distinguish M9 from
generic adaptive group testing (the alternative explanation); that needs a
further world.

CPU: < 0.1 core-min per control run.
