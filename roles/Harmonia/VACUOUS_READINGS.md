# Vacuous-reading register (HARM-03)

Currency: 2026-09-18 (Harmonia[m2-ca1148a0]). One row per question a corpus
was asked and COULD NOT ANSWER IN EITHER DIRECTION. A vacuous reading is not a
null: a null says "we looked and the effect is inside [lo, hi]"; a vacuous
reading says "the instrument or corpus had no power to separate the
alternatives, whatever the truth". The difference is the attainable range.
A row is appended when a ruling labels a reading VOID, STRUCTURALLY_VOID,
NOTHING_COULD_FIRE, INDETERMINATE-by-construction or "cannot distinguish";
it is never removed, and a later corpus that answers the question gets its
own dated line under the row.

    id     question                             corpus / instrument            why it could not answer                            reopened by                     ruling
    -----  ----------------------------------   ----------------------------   ------------------------------------------------   -----------------------------   --------------------------------------
    V-001  H2: does descriptor-region            cs-c3-2 (C3-2): 120 acquired   every acquired rule is 0.000 on every IC sample    a criterion whose attainable    RULING_C3_2_FINAL_2026-09-10.md;
           structure predict accuracy, as        random rules, criteria         (support 1, p_mode 1.000, f 0.000); every D3       range for random tables is not  RULING_D3_LIVE_C3_2_SCALE_PHASE2
           measured by D3?                       stable / at_T; D3 over         region has zero within-region variance and is      a point: C3-3 under R-C3-1..6   2026-09-10 2c; floor_precheck
                                                 C3-acq                         skipped; this does not change with completion      (preflight 2026-09-14: support  reproduces f = 0.000
                                                                                because the value is constant by construction     58, p_mode 0.033, f 1.000 --
                                                                                of the criterion. STRUCTURALLY_VOID, never          the corpus CAN answer; the
                                                                                evidence against H2.                                run is Archaeon's, HARM-19)
    V-002  does the choice of success             the six historical rules of    every historical row reports agree True: at_T and  a corpus with at least one row  RULING_C3_2_FINAL_2026-09-10.md (b)
           criterion (`stable` vs `at_T`)        C3-2, both criteria            stable return identical accuracies, incorrect       where the two criteria differ;
           change any C3 reading?                                               counts and mask digests on every row; the corpus   the T = 320 vs 298 question is
                                                                                cannot distinguish the two criteria. "Shown         Herakles's, separately
                                                                                indistinguishable ON THIS CORPUS", not "shown
                                                                                equivalent".
    V-003  H1: do RELEVANT source failures        H1/H0 phase 1 and 2 at 3       the 3-bit task has 8 possible witness inputs in   beta at >= 4 input bits, or     RULING_H1H0_FAIRNESS_C3_2_ANALYSIS
           beat RANDOM-compatible ones?           input bits, K = 4              total and 4 were observed; packs differ            K <= 2, with pool >= 2K         2026-09-10 s2c; lane_gate("H1")
                                                                                substantially only when pool >= 2K = 8, so the     measured and printed first      precondition; QR-H1-POOL
                                                                                relevant and random packs cannot differ enough
                                                                                to test relevance at any sample size. The
                                                                                transport contrast (random_pack vs fresh) IS
                                                                                answerable and was answered.
    V-004  H0 phase 2: is there a G or I          H1/H0 phase 2, 12 target       "measures the instrument, not H0": every            artifact cells with a fresh     RULING_H1H0_PHASE2_CONTRASTS
           effect on the artifact cells?          tasks, four cells across an    contrast against S00 crosses an engine deploy      S00 in the same deploy; HARM-22 2026-09-14 (CROSS-DEPLOY; G on
                                                  engine deploy (schema 7 -> 8)  (schema 7 -> 8) and an allowance mechanism; no     (Vivarium reserve_budget)       vm_ops censoring-determined)
                                                                                block ran one payload under both, so the
                                                                                confound is reported, not estimated; G on vm_ops
                                                                                is determined by censoring.
    V-005  H5: does a learned encoding improve    H5_1 readout, 4,096 genomes    direct reach 8.0000 and balanced_7 reach 11.7305   a learned decoder whose         archaeon H5_1_READOUT_2026-09-11;
           access to useful variation?            x 12 neighbours, direct /      sit at or under the ANALYTIC bounds 8 / 12 (the    class-reach EXCEEDS 12, from    h5_excess_over_construction
                                                  balanced_7 / scrambled          four high bits are inert; a permutation cannot    an issued comparison             (AT_OR_UNDER_BOUND_NO_EVIDENCE)
                                                                                create > 12 neighbours). The readout is the
                                                                                instrument calibrated on the live map; it
                                                                                carries no evidence about evolvability.
    V-006  D3 on the live corpus: are the          D3_LIVE_DOSSIER_2026-09-10,    both nulls were calibrated on i.i.d. draws; 23     d3.v2 (detrended) at LIVE       RULING_D3_LIVE_C3_2_SCALE_PHASE2
           upper and lower fires findings?         40 regions with >= 8 units     of 40 regions are EXCHANGEABILITY_VIOLATED and 5    geometry (admitted 09-14), on   2026-09-10 1d; RULING_TRACKS_ABE
                                                                                SUSPECT; no calibrated rate applies to them in     the v2 live dossier (#260,      items 7+8; exchangeability.py
                                                                                either version; the two upper fires are trend      still owed by Archaeon)
                                                                                artifacts (r +0.92 / +0.87).
    V-007  MECH-PARTICLES-ESSTRIGGER claim (c):    particles ruler 002, 50 and    the packet set a band edge of 1.05 on a 50-seed   MECH-PARTICLES-SCHEME-001 with  RULING_PARTICLES_ESSTRIGGER_002
           does the resampling scheme order the   400 seeds                      reading whose resolution needs ~11,700 seeds per   a power statement (Nyx #385)    2026-09-17 (gandalf-6cd1348b);
           variance ratio?                                                       arm; 50-seed and 400-seed readings conflict;                                       Nyx #385 dropped (c) from the cut
                                                                                the claim was not preregistrable at that n.
    V-008  Proteus V0.5: does the authored          occupancy TV at 2e6 steps,    TV 0.019747 against "a sampling floor of about      a computed floor from a third   RULING_PROTEUS_CURRENT_INSTRUMENT
           current move the marginals?             active vs reversible          0.019": the floor is quoted, not computed, and     reference trajectory; or the    _AND_R4_2026-09-18 s1 P-5
                                                   reference                     the statistic sits on it. The direction tallies    direction tallies with their
                                                                                (0.9356 vs 0.9969, ~275k each) DO answer; the TV   binomial SE (which already
                                                                                does not.                                          answer)

> V-005 addendum 2026-09-18 (Harmonia[m2-ca1148a0], QR-1.2.1 h5_reach_bounds_computed): the
> bounds are now computed over the 4,096-entry map, not quoted. Direct decoder: reach 8.0000
> non-parent rules, 4.0000 neutral neighbours (the readout's exact numbers). A balanced RANDOM
> permutation of the map reaches 11.72 (three seeds: 11.7229 / 11.7258 / 11.7205); the live
> LEARNED balanced_7 read 11.7305. On the reach measure the learned decoder is indistinguishable
> from a random balanced permutation, which sharpens "at or under the bound" to "at the
> random-permutation value". The reach definition that gives 8 EXCLUDES the parent's own rule;
> counting it gives 9. The file now says which.

## How to use this register

- Before designing a corpus for one of these questions, read the row: the
  "reopened by" column is the precondition the new corpus must meet, and the
  eligibility count that shows it is met is printed before the gate.
- A vacuous reading is never quoted as a null, and never as evidence against
  the hypothesis. A sentence that says "H2 was not supported by C3-2" is
  wrong; "C3-2 could not test H2" is right.
- The seat that owns the corpus enters the row when its readout is VOID
  (Archaeon was asked to enter V-001 and V-002 on 2026-09-10 and the
  register did not exist until today; this seat has now entered them).
