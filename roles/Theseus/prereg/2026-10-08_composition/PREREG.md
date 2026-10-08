# THESEUS-23b preregistration -- the composition wall, measured inside Theseus

Currency: 2026-10-08. Committed before the run. Code: theseus/synth/
composition.py (blob id in CODE_SHA256.txt). No run of this code on real
genomes has happened; the detector logic was tested on a synthetic
fingerprint (theseus/synth/tests: test_composition_detector_fires_on_
synthetic_synergy).

## Why

Hestia's audit (comms #1735) reports one wall across seven substrates:
1-part mechanisms are found, 2-part mechanisms whose parts are each worth
nothing alone are not. Theseus's charter claim -- recursive synthetic
ancestry builds what one-shot collisions cannot -- predicts that deep
descendants should contain such compositions more often than one-shot G0
collisions or matched random programs. This tests that directly, on the
committed v0_1 genomes, with no new ecology run.

## Design

Arms (viable genomes with >= 2 rules from run v0_1_2026-09-30, up to 120
each, seeded sample 20261008): D (DEEP+VERY_DEEP), E (DEEP_LENS), S
(SHALLOW), G (G0 lane), P/B/C (one-shot G0 pairs/triplets/sextuplets), R
(random, complexity-matched to D), A (LLM semantic synthesis, <= 51).
For every split point s: A = rules[:s], B = rules[s:]. COMPOSITION if some
split has d(A, EMPTY) <= EPS and d(B, EMPTY) <= EPS and d(G, EMPTY) > TAU,
with EPS = 1.63 (median G0 replicate distance, the noise floor) and TAU =
4.31 (tau_rep), both frozen from v0_1. Fingerprint at IC seed 0, euclid_z.

## Decision rule

- If every arm has 0 compositions: INDETERMINATE (wall or detector
  blindness cannot be separated: no substrate-level planted composition
  exists yet -- a stated limitation).
- Else H-COMP: D's composition rate exceeds BOTH the one-shot rate
  (P+B+C pooled) and R's rate, each by a one-sided Fisher exact test at
  p < 0.05 -> SUPPORTED. D's rate <= both -> NOT SUPPORTED. Otherwise
  INDETERMINATE.
- Descriptive: per-arm rate with Wilson CI, median best synergy ratio.

## Predictions

K1 Every arm has a composition rate below 5%.                     p = 0.6
K2 H-COMP is NOT SUPPORTED or INDETERMINATE.                      p = 0.75
K3 R (random) has the highest composition rate of all arms.       p = 0.35

Compute: about 1000 genomes x ~20 fingerprints x 0.45 s / 4 CPUs, about
40 min wall, under 3 CPU-hours (MWO R2). COI: same builder as the rulers.
