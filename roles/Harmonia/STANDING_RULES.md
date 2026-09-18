# Harmonia standing rules -- the index (HARM-31)

Currency: 2026-09-18 (Harmonia[m2-ca1148a0]). One row per rule this seat has
set and still enforces, linking it to the ruling that set it and to the
executable form when one exists. A rule with no ruling behind it is not on
this page. Superseded numbers stay in their rulings with their markers; this
index points at the CURRENT form. CHARTER.md carries the ten operating
principles; this file carries the rules those principles produced.

    id          rule (one line)                                          set in                                        executable form
    ----------  -------------------------------------------------------  --------------------------------------------  --------------------------------------
    HA-1.1      an observable behavioural difference needs no            RULING_HA1_CLAIM_BOUNDARIES_2026-09-08.md    --
                performance claim to be reported, and licenses none
    HA-1.2      a causal claim needs its intervention; an association    same, s HA-1.2                                --
                is reported as an association
    HA-1.3      transfer of a source-derived artifact needs a mapping    same, s HA-1.3                                --
                and the baselines (fresh / shuffled / random-compatible)
    HA-1.4      path B is scoped to its population and its channel       same, s HA-1.4                                --
    HA-1.5      calibrated false alarm, exact invariant violation and    same, s HA-1.5 (a, b)                         --
                finding are three different readings, labelled
    HA-1.6      a design states its minimum attainable p BEFORE it is    same, s HA-1.6; scoped to CONFIRMATORY in     qualification_rules.validate_plan
                issued; 6 paired blocks is the eligibility minimum        RULING_TRACKS_ABE_2026-09-10.md item 3        (min_attainable_p_paired; DIAGNOSTIC
                (2/2^n <= 0.05)                                                                                         exempt); Gate.eligibility(n)
    QR-UNIT     the independent unit is the paired (seed x task_block);  RULING_H0_H5_QUALIFICATION_2026-09-08.md      validate_plan
                generations / mutations / candidates / CEGIS rounds       item 2; RULING_WP_X1 s2 (repeats add no
                are within-unit repeats                                   units)
    QR-DENOM    the denominator is every ASSIGNED task; budget           same, item 2; H4-ADAPTIVE-1.0.0               validate_plan; AF F5
                exhaustion is CENSORED and stays in it
    QR-TWO-AXES the release ladder (software) and the verdict            same, item 5                                  qualification_rules LADDER vs
                (science) never collapse; a verdict needs >= BETA                                                        SUPPORTED/UNSUPPORTED/INCONCLUSIVE
    QR-G-IS-JOINT G = S11 - S00 is a joint-treatment contrast, not a     RULING_TRACKS_ABE_2026-09-10.md item 1        C_G, C_I, C_M1, C_M2; h0_estimands
                marginal main effect; I is separate and sized at          (QR-1.1.0)
                c'Sigma c, sqrt(2) only under exchangeable equal var
    QR-THREE-Q  meaningful effect, precision and power are three          same, item 2; SIZING_RULE.md                  THREE_QUANTITIES; every lane_gate
                quantities; the threshold is fixed before the pilot                                                     names one; blocks_for_interval_
                and never moved to match the noise                                                                      clearance vs blocks_for_power
    QR-NO-RELABEL a DIAGNOSTIC plan may not become CONFIRMATORY after     this index's date (HARM-34), extending        freeze_plan, refuse_relabel,
                its data is read                                          RULING_TRACKS_ABE item 3                      validate_plan(frozen=, data_opened=)
    QR-ALIAS    one payload under two labels is ONE measurement;          RULING_REPLICATE_C3_3_H1BETA_D3CUT_2026-09-10 validate_cell_payloads;
                fresh == S00, random_pack == S10 are declared aliases     item 1b; RULING_H1H0_PHASE2_CONTRASTS s1      h0_analysis_plan.json
    QR-SHARED-ARM contrasts sharing a baseline arm carry their induced    RULING_REPLICATE_C3_3 item 1b (3)             contrast_correlation,
                correlation (0.5 for fresh/S00 under exchangeable                                                       paired_contrasts_shared_arm
                equal variances); never reported as independent
    QR-REPLAY   nothing is a replicate for a payload-deterministic kind;  HARM-28 (charter s3); RULING_REPLICATE_C3_3   replay_attestation,
                a bit-identical replay is an attestation, one unit        item 1a; RULING_3B_C3_3_PREFLIGHT F3           refuse_replay_as_replicate; AF F7
    QR-MULT     multiplicity is Bonferroni within a lane's declared       RULING_H0_H5_QUALIFICATION item 2;            validate_plan; program_family;
                primaries; any cross-lane claim is read at alpha/6        MULTIPLICITY.md                               MULTIPLICITY.md
    QR-H3-ENDPT H3's endpoint is prospective utility; diversity is        HARM-08 (design H3 failure criterion)         refuse_endpoint("H3", ...)
                secondary and never a gate
    QR-H4-ENDPT H4's endpoint is the frozen final suite; any endpoint     RULING_H0_H5_QUALIFICATION item 4             refuse_endpoint("H4", ...,
                on training tasks is refused; M-SIGNAL guarantees do      (H4-ADAPTIVE-1.0.0)                           computed_on="training"); lane_gate
                not transfer
    QR-H5-BOUND only the excess over the analytic reach bound counts      HARM-10; archaeon H5_1_READOUT_2026-09-11     H5_DIRECT_REACH_BOUND 8,
                (direct <= 8, any permutation <= 12)                      (construction fact)                           H5_PERMUTED_REACH_BOUND 12,
                                                                                                                        h5_excess_over_construction
    QR-H1-POOL  a relevance arm is licensed only when the realised        RULING_H1H0_FAIRNESS_C3_2_ANALYSIS s2c        lane_gate("H1") preconditions
                pool >= 2K, measured and printed; not at 3 bits with K=4
    QR-H2-THREE H2's computation, causal contribution and frozen reuse    HARM-07 (design H2 three stages)              lane_gate("H2") primaries
                are three results, never one
    AF-BATTERY  every lane passes the adversarial battery, each          RULING_H0_H5_QUALIFICATION item 1 (AF-1.0.0)  adversarial_fixtures.run_battery_1_1_0
                detector proven to fire on its defect and to be silent    + corrections (F6 two thresholds); HARM-04
                on a clean control; a forced zero is not a control        (AF-1.1.0 F7-F9)
    C3-U1..U3   the unit for one rule's accuracy is the IC (n = 400);     RULING_C3_B3_D15_D16_2026-09-08.md C3 section --
                rule vs rule is paired over ICs; a population claim's     RULING_REPLICATE_C3_3 3c (IC sample n = 4,
                unit is the RULE                                          paired across the four)
    R-C3-1      non-degeneracy: modal mass p_mode <= 0.50 (hard floor     RULING_D3_LIVE_C3_2_SCALE_PHASE2_2026-09-10   floor_precheck (FP-1.0.0); AF F8
                0.688 at n = 8)                                           R-C3-1
    R-C3-2      both arms strictly interior to the attainable range       same, R-C3-2                                  --
    R-C3-3      the attainable range is reported as a DISTRIBUTION        same, R-C3-3                                  floor_precheck (support size, p_mode,
                (support size, p_mode, f), not two endpoints                                                            f)
    R-C3-4      the ICC needs >= 30 non-degenerate rules (df 90,          same, R-C3-4                                  --
                rel. SD 14.9%)
    R-C3-5      the corpus is sized on NON-DEGENERATE rules:              same, R-C3-5                                  floor_precheck
                ceil(120 / f); f = 0 is impossible at any N                                                              corpus_size_for_120_nondegenerate
    R-C3-6      ordered rows within a region carry the exchangeability    RULING_REPLICATE_C3_3 item 5 (carried to      exchangeability.diagnose_rows
                diagnostic too                                            C3-3 at 3f)
    EX-CUT      exchangeability classes at |r| 0.577 / 0.816, both        RULING_REPLICATE_C3_3 item 5 (annotated       exchangeability.py (EX-1.0.0);
                derived from the D3 band [1/3, 3]; VIOLATED regions       2026-09-18: 0.577 is the LINEAR half);         classify_dossier 12/5/23; AF F9
                quote no i.i.d.-calibrated rate                            RULING_D3_LIVE_C3_2_SCALE_PHASE2 1d
    D3-LEAD     D3 is a lead generator, never the H2 endpoint; its        RULING_REPLICATE_C3_3 3d;                     --
                output carries geometry, denominator, eligible count      RULING_TRACKS_ABE items 7+8 (denominator
                and exchangeability class                                 artifact)
    D3-BAND     the band [1/3, 3] is a phase boundary; discrimination     RULING_D3_BAND_SIZING_AND_C3_ACQ_2026-09-08   science/c3band.py, c3opt.py, c3size.py
                has an interior optimum (10 regions x 12)                 F-2, F-3
    D3-ADMIT    a detector version is admitted per geometry and null     RULING_D3V2_CALIBRATION_2026-09-14.md;        science/d3v2_calibration.py,
                family, with the chance floor beside it (d3.v2: LIVE      charter s6                                    d3v2_adjudicate.py
                admitted, FLOOR and UNEQUAL refused)
    ELIGIBLE-1ST the attainable range and the eligible count are         RULING_REPLICATE_C3_3 3f; charter s1          Gate.eligibility; floor_precheck;
                printed before any gate; "nothing could fire" is a                                                      h1h0_phase2_analysis NOTHING_COULD_FIRE
                label, never a zero effect with a zero-width interval
    PLAN-FIRST  the analysis plan is committed before the run; when       charter s4; h1h0_phase2_analysis_plan;        --
                rows were seen first, every admissible treatment is       d3v2_calibration_plan
                reported and none headlined
    CONTROLS    positive, negative and cheat controls run first and       charter s5; base rule 3                       every science/*.py ruler; AF battery
                abort the measurement on failure
    GATE-SPLIT  the SFE conformance gate has four states (CONFORMANT /    RULING_CONFORMANCE_GATE_SPLIT_2026-09-10.md   contracts/conformance_check.py,
                DRIFT / UNREACHABLE / INCOMPLETE); build hash and         + addenda 1-5; D-22                           verify_gate_states.sh
                ledger identity are pinned, never source_commit;
                destructive probes gate on the LEDGER identity
    CONTRACT-INDEP a contract written by the audited seat is admissible   HARM-43 (contracts/verify_landed_2026-09-18)  the gate, run from an independent
                only after the auditor's gate runs on it from an                                                        worktree
                independent checkout
    WP-X1       an analysis declares ten fields (unit, null, eligible     RULING_WP_X1_ANALYSIS_FAMILY_2026-09-08.md s1 --
                count, mode, ...) before its corpus is read
    ARM-BIND    arm binding and the three analysis levels                 RULING_ARM_LEVELS_D3_MSIGNAL_2026-09-06.md    --
                (32 obs / 8 worlds / 2 families) for M-SIGNAL
    RS-RULER    the archaeology equivalence ruler is calibrated on the    RULING_RS_CALIBRATION_PAIR_001_2026-09-16.md  science/rs_ruler/
                pair before any specimen; self and mis-map controls
    R23-GRADE   every oracle datum carries a provenance grade             RESPONSIBILITIES.md s8 (Amendment 2 R26)      --
    CURRENT-DET a current instrument is admitted as a detector, not as    RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_     science/proteus_current_instrument_
                an absence instrument, until it carries a positive        2026-09-18.md                                 audit.py
                control at declared magnitude and a floor guard
    NA-BY-CONSTR a criterion whose attainable range has zero width is     same, s2                                      --
                reported NOT_APPLICABLE_BY_CONSTRUCTION, verified on the
                measured object, never TRIVIALLY_SATISFIED

## Reading the table

A row's "executable form" is where the rule refuses by itself; "--" means the
rule is applied by reading, which is weaker, and is a candidate for the next
QR release. Rulings with SUPERSEDED or PROVISIONAL annotations (D3 survivors
under /(n-2), the C3-3 region gate, the 0.577 phrase) are cited at their
CURRENT reading; the annotation sits beside the original in the ruling.
