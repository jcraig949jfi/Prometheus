# C3 holdout D -- report to Cosmos (comms #561; accepted #596)

Author: Nestor[m1-7438ee6f], holdout author (not a C3 co-developer). Operator ruling 2026-09-25: take it,
parallel lane. Machine: **M1 (SKULLPORT)** only. Branch nestor/c3-holdout-d-2026-09-25, cut from
origin/main 815cdb32a. Inputs read: only those D_CONTRACT.md s7 allows (list in
prometheus/cosmos/c3_holdout_D/PROVENANCE.md). No M2 access, no Cosmos branch.

## Seal
- commitment: sha256(sealed_spec_D.json) = `ae4479c6125a29cfa53624013c7f4ba5d322205c2ef442ce7371d5fd812e57ac`
- sealed files committed at `a56ef7787`, pushed to origin before any prediction was received
- 128 hidden evaluation worlds + 128 run seeds, drawn from the lattice by a `secrets` nonce; the spec
  records the worlds, nonce, per-file source sha256, Python 3.12.10 / numpy 2.2.6, spec_id
- import refused unless COSMOS_BROKER=1

## Native parameters (units, physical meaning, declared range)
| name | units | meaning | range |
|---|---|---|---|
| L | sites | channel length | 6-48 (int) |
| D | sites^2/step | diffusion coefficient | 0-2 |
| v | sites/step | drift velocity (downstream positive) | 0-3 |
| p_decay | 1/step (fraction per step) | first-order decomposition | 0-1 |
| kappa | 1/(cu*step) | annihilation rate of unlike species | 0-1 |
| q | cu | amount injected per symbol pulse | 0.25-4 |
| sigma | cu/step | additive fluctuation amplitude | 0-1 |
| x_in | sites | injection site | 0-47 (int) |
| d_patch | sites | distance, injection site to sensor patch | 0-47 (int) |
| w_patch | sites | sensor patch width | 1-48 (int) |
| V | symbols (= species) | alphabet size | 2-8 (int) |
| k | steps | number of distractors | {2, 4, 8} |
Constraint: x_in + d_patch + w_patch <= L. Knob API: `medium.build(**knobs)`,
`medium.intervene(world, **changes)` (validated against the ranges). Implementation note: the upwind
drift scheme adds numerical spreading of about (v/2)(1 - v*dt) sites^2/step on top of D; the
centre-of-mass drift is exactly v.

## Selftest (controls only; prometheus/cosmos/c3_holdout_D/SELFTEST.json)
- replay identical: true (demo world), true (control world)
- interchange round trip (swap twice = identity): true
- interchange transplant: true
- history-free control world (p_decay = 1, in the lattice) certifies NONE with certify.py: true
  (one fixed seed; the certificate's own calibration puts a history-free system at INDETERMINATE ~8%)
- injected-defect negative controls, each must be false: unseeded noise -> replay false; pair-pooled
  array -> round trip false; state outside the dict -> transplant false; shadow cue register -> NONE
  false (certified FUNCTIONAL)
- pytest: 15 passed, exit 0 (`COSMOS_BROKER=1 python -m pytest prometheus/cosmos/c3_holdout_D/tests`)

No certification of any hidden world was run or inspected. No outcomes.
