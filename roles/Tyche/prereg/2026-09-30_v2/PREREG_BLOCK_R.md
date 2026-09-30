# PREREG -- Tyche v2 Block R: latent option value under unannounced regime change

Currency: 2026-09-30. Committed BEFORE any Block R run. Directive:
roles/Tyche/prompts/2026-09-30_v2_pressure_map/ (db985709e). Design:
roles/Tyche/design/V2_PRESSURE_MAP_DESIGN.md (ad5e912e6). Code at the
commit adding this file (CODE_SHA256.txt); certificates
tyche/runs/v2_certs/CERTIFICATES.json.

## Question

Does an ecology retain unrealized perceptual optionality? Measured as the
speed of adaptation after an unannounced change of what counts as useful,
and as the fraction of living lenses already carrying the new law's
precursors at the moment of change. No one tells the ecology which lens
will matter; the post-switch world is the ruler.

## Worlds (tyche/v2/worlds_v2.build_regime, master seed 20261002)

Four regime worlds; L1 rules generations 0-19, L2 from generation 20 on
(the ecology is not told; its admitted L1 senses stay in its ecology):
  R1  L1 smooth majority of 3 delays -> L2 xor of 2 delays (disjoint channels)
  R2  L1 smooth                      -> L2 parity of 3 delays
  R3  L1 xor(A, B)                   -> L2 xor(A, C)   (one L1 precursor reused)
  R4  L1 xor(A, B)                   -> L2 xor(C, D)   (nothing shared)
Certificates: L2 lowest informative order 2, 3, 2, 2 (empirical); best
single raw feature <= 0.0010 bits above null for every L2; L1 of R1/R2 is
order 1 (bank 0.196).

## Conditions (36 runs; coalitions PAIRS, chemistry GRAFT, N 96, 50
generations, switch at 20, seeds 1 and 2)

  H  STRICT (significant-case gating, immigrants) | LEX (lexicase, no
     reserve) | RES (lexicase + 48-slot utility-free reserve with drift)
  V  rsolo (each regime world alone: 4 runs per H per seed) | rrelated
     (the 4 regime worlds together) | rbroad (the 4 + 6 unrelated static
     niches: smooth, deceptive, order-2, donor, representation-change,
     generated)

## Measures (tyche/v2/report_v2.py block_r; run-level histories by
tyche/v2/history_v2.py)

  OV   option value = generations after the switch until the slot's best
       val gain reaches 50% of the L2 oracle deficit (measured at the
       switch); not reached within 30 -> censored at 31
  SO   stored optionality = fraction of living lenses (population +
       reserve) at the switch whose outputs carry ANY L2 precursor
       (functional MI above a permutation null), and per precursor
  L1 / L2 solved, histories of every L2 sense (first carriers, zero-
       utility persistence and why, transition operator, assembly mode)

## Hypotheses (computed by code) and my predictions

  RH1 mean OV ordering RES < LEX < STRICT        predict TRUE
  RH2 mean SO ordering RES > LEX > STRICT        predict TRUE
  RH3 mean OV broad < solo                       predict TRUE
  RH4 mean OV R3 (shared precursor) < R4         predict TRUE
  RH5 R2 (order-3 L2) adapted cells              predict 0 of 18
Also expected: STRICT on rsolo collapses to random immigrant search on
zero-marginal phases (no significant case exists), so STRICT rsolo R3/R4
L1 are near-never solved. All of this may be mostly censored; a censored
map is still the result.

## Disclosures

Smoke runs (N 16, 4-6 generations) and a two-configuration timing pilot
(3 generations, seed 9) were executed; their outcomes were not used. The
rbroad set was trimmed from 21 to 10 worlds for compute before any run.
Tests: tyche/tests 37 passed.

## Compute

Estimated upper bound (wall x workers) about 12 core-hours on M2, inside
MWO-0004 R2 (16 per item). WORK_STATE `running` is committed before the
launch and cleared after (Cyclops #1061).
