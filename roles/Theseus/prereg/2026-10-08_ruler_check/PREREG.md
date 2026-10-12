# THESEUS-23a preregistration -- can the rulers tell designed structure from random wiring?

Currency: 2026-10-08. Committed before the run. Code: theseus/synth/ruler_check.py
(blob id in CODE_SHA256.txt). One smoke run (2 per family) proved the
harness; its outputs were deleted, only the per-family block was seen.

## Why (failure shape of v0 / v0_1)

In v0 and v0_1, random programs were NOT_REPRODUCED_YET as often as deep
descendants, and they gained more from evolved lenses. Hestia's audit
(comms #1735) independently reads Theseus as "loses to random programs on 2
of 3 rulers" and names this test. Before the ecology is asked anything more,
the rulers must show they can tell designed structure from random wiring.

## Design

- PLANTED: 6 designed motif families (gated delay loop, memory relay ring,
  rank-threshold sorter, driven cross-scale feedback, replicate-select-
  mirror, phase-wrapped coupled advection), none of them in the known
  library, 40 members each (240), parameters uniform within stated bounds.
- RANDOM: 240 substrate programs, each complexity-matched one-to-one to a
  planted member (n_rules, C, max sources).
- Frozen references from run v0_1_2026-09-30: CAL.json, the known library
  (480 members) and the G0 fingerprints.
- Rulers: R1 viable; R2 sparseness vs G0 (euclid_z, k=5); R3 distance to
  the nearest known-library member; R4 jitter smoothness (negative mean
  fingerprint distance under 4 jitters of +-10% on float params);
  R5 response mid-band share (0.05 < r < 0.9); R6 replicate stability
  (negative IC-seed replicate distance).
- Statistic: AUC planted-vs-random, 1000-bootstrap 95% CI, primary scope =
  viable candidates only, secondary = all.

## Decision rule (per ruler, viable-only scope)

  DISCRIMINATING      AUC >= 0.75 and CI lower bound >= 0.60
  ANTI-DISCRIMINATING AUC <= 0.25 and CI upper bound <= 0.40 (the ruler
                      prefers random wiring -- itself a finding)
  NON-DISCRIMINATING  CI contains 0.5
  WEAK                otherwise
If n viable in either class < 40: that ruler is INDETERMINATE.

## Predictions (scored after the run; wrong ones go to the ledger)

Q1 R2 (sparseness vs G0) is NON-DISCRIMINATING or ANTI.          p = 0.7
Q2 R3 (known-library distance) is NON-DISCRIMINATING or ANTI.    p = 0.7
Q3 R4 (jitter smoothness) is DISCRIMINATING.                      p = 0.5
Q4 R5 (response mid-band) is DISCRIMINATING.                      p = 0.4
Q5 Planted viable fraction > random viable fraction.              p = 0.8

## What follows from the result (frozen now)

- If no ruler discriminates: the fingerprint itself cannot see designed
  structure; the next item is a new fingerprint, not more ecology runs.
- If R4 and/or R5 discriminate: they become the v1 rulers, and H1 is
  re-scored on the committed v0/v0_1 rows with them as a POST-HOC
  analysis, labelled as such, before any new ecology run.
- R2/R3 discriminating in the anti direction confirms that "far from the
  known" rewards randomness; they are then demoted to descriptive.

Compute: < 1 CPU-hour, 4 local CPUs (MWO R2). COI: the planted families
were designed by the same model that built the rulers.
