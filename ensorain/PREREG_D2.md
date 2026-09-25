# D-series Round 2 preregistration (confirmation of Round-1 nominations)

Currency: 2026-09-24. Committed after Round 1 (ensorain/D1_ROUND1.md) and
BEFORE any Round-2 row. Selection by PREREG_D1 s6 (no crossovers exist):
the replicated couplings with the largest discovery effect, primary ruler
(held-out R^2, clipped) first, then EFF, max 6:
  N1 world_family x org_family   (R^2)  -- known-by-construction: POSITIVE
                                          control for the Round-2 instrument
  N2 lam x org_family            (R^2)
  N3 forget x org_family         (R^2)
  N4 scratch x surprise_alpha    (R^2)  -- the only organism-intrinsic
                                          candidate
  N5 sweeps x kappa_mult         (EFF)  -- accounting-by-construction:
                                          second POSITIVE control
  N6 cap_actual x org_family     (EFF)
No precursor or phase nomination exists.

Design, per nomination: the pair on a grid (continuous dials at the
Round-1 tercile midpoints; categoricals at every level), fresh seeds
70000+, two BACKGROUNDS for all other dials:
  RANDOM      every other dial drawn as in Round 1 (the discovery
              condition); 40 lives per cell
  COMPETENT   every other dial fixed where learning works: lam 30,
              sweeps 10, scratch 128, cap 192, replay/dream/surprise/
              disturb/forget/err/p_restruct 0, persist 5, drift .3,
              noise .1, kappa 1, org TT with correct start, world TT;
              16 lives per cell
Test: two-way OLS on the grid with an interaction block (the Round-1
test), ruler as nominated. REPLICATED iff interaction p < .05/6 in the
RANDOM background AND the interaction pattern correlates with Round 1's
(r > .5). The COMPETENT result is reported as "does the coupling matter
where learning happens" and is not a replication criterion.
Instrument controls (both backgrounds): N1 and N5 must replicate (they
are true by construction); if either fails, Round 2 is under-powered and
no null is reported as evidence.
Seat predictions: N1, N5 replicate (controls). N4 replicates in RANDOM
(p .6) but vanishes in COMPETENT (p .6): it is a divergence-avoidance
coupling (bigger batches + surprise weighting = fewer runaway refits), not
a competence coupling. N2, N3, N6 replicate in RANDOM (definitional).
