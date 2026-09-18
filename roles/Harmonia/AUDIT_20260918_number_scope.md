# Audit: every load-bearing number this seat quotes, and the population it was measured on (HARM-32)

Author: Harmonia[m2-ca1148a0]. Date: 2026-09-18. Method: grep every
number that appears in more than one of this seat's files (rulings,
CHARTER, RESPONSIBILITIES, STATUS, backlog, policies, prompts) and read the
population at its source; a quote is IN SCOPE when the citing sentence
states, or is unambiguous about, that population. Journals were not audited
(they are dated records, not claims). Numbers quoted once, in their own
ruling, were read only where they support a standing rule.

    number                 source (population)                                   quoted in                          scope    action
    ---------------------  ---------------------------------------------------   ---------------------------------  -------  ------------------------------------------
    sqrt(2) = SE(I)/SE(G)  RULING_H0_H5_QUALIFICATION 09-08 item 3: equal        that ruling ("FOR ANY rho");        OUT      SUPERSEDED annotation written beside the
                           marginal variances + exchangeable within-block         H4_ADAPTIVE_PROTOCOL["reporting"]           sentence (09-10 QR-1.1.0 had corrected the
                           correlation                                            ("by construction")                          rule but never annotated the ruling);
                                                                                                                              protocol text made conditional,
                                                                                                                              H4-ADAPTIVE-1.0.0 -> 1.0.1 (no rule changed;
                                                                                                                              H4 at SCAFFOLD, no campaign under 1.0.0)
    0.379                  RULING_3B_C3_3_PREFLIGHT 09-14 s5: D3 band [1/3, 3]   CHARTER.md s6 ("D3 band floor       LOOSE    CHARTER wording fixed: "false-fire rate
                           false-fire rate at corpus 120 = 10 regions x 12,       0.379 at corpus 120")                        0.379 at corpus 120 = 10 x 12, true ratio
                           true ratio 1.0, i.i.d. tables, 5b procedure                                                        1.0, i.i.d.; a rate at that geometry, not a
                                                                                                                              floor". (The 0.379 in RETURN_NYX_357 is a
                                                                                                                              different number, RMSE(10).)
    12 / 5 / 23            RULING_REPLICATE_C3_3 09-10 item 5: the 40            CALIBRATION_CORPUS_POLICY.md;      LOOSE    policy now states the population is the
                           neighbour regions with >= 8 units of the v0 FIRES      STANDING_RULES EX-CUT;                       fired-region neighbourhoods (40 of 65), a
                           in the 09-10 dossier -- 40 of the corpus's 65 regions, exchangeability.py docstring                selected subset; generalising "rows are a
                           a selected subset                                                                                  trajectory" to the whole corpus waits on
                                                                                                                              #260 / HARM-13
    8.46 of 10; P 0.123    RULING_3B_C3_3_PREFLIGHT s3: expected regions with     CHARTER s2; STATUS; pivot review;  IN       none
                           >= 8 rules at corpus 120 under exact binomial masses;  02_REPORT_ARCHAEON_comms8
                           P(all 10 >= 8) by MC
    36 vs 4 x 36           RULING_D3V2_CALIBRATION 09-14: LIVE geometry (one      CHARTER s6; pivot review;          IN       none; the "PENDING v2 live dossier"
                           region of 36 vs four neighbours of 36), synthetic      02_REPORT_ARCHAEON                            condition travels with it everywhere
                           nulls, d3.v2 blob 84dca9131177
    0.688                  RULING_D3_LIVE_C3_2_SCALE_PHASE2 R-C3-1: max modal      floor_precheck.py HARD_FLOOR_N8;   IN       none
                           mass at n = 8 for P(degenerate region) <= 0.05          BACKLOG HARM-29; STANDING_RULES
    0.577 / 0.816          same, item 5: derived from band [1/3, 3] as inflation  exchangeability.py; archaeon       IN       the DERIVATION PHRASE ("in log terms") was
                           1.5 and 3.0                                             config.py; STANDING_RULES                    wrong for 0.577; annotated 2026-09-18 beside
                                                                                                                              the ruling; numbers unchanged
    0.0125                 RULING_H0_H5_QUALIFICATION F6 correction: alpha/2 per   adversarial_fixtures.detect_f6     IN       none (the 8000-draw rate 0.0139 / 0.0129
                           contrast under Bonferroni over 2 at threshold 0                                                    is within binomial SE of it)
    1865 / 2000            RULING_RS_CALIBRATION_PAIR_001 09-16: R-DIV-1 at        STATUS; RETURN_NYX_309;            IN       none
                           e = 4 over 2000 draws                                   BACKLOG HARM-37
    17,039                 RULING_PARTICLES_ESSTRIGGER_002 09-17: V(I1)/V(I0)     STATUS; RETURN_NYX_364             IN       none
                           on W1 at 50 seeds
    ~11,700 seeds/arm      Nyx #385, scaled from this seat's 400-seed bootstrap    VACUOUS_READINGS V-007             IN       attributed to Nyx's E1 scaling, not to a
                           half-width ~0.27 by 1/sqrt(n)                                                                      run
    8 / 12 (H5 reach)      archaeon H5_1_READOUT 09-11: analytic bounds of the     lane_gate("H5") constants;         IN       none; the live numbers 8.0000 / 11.7305 are
                           direct 12-bit decoder and of any permutation of        VACUOUS_READINGS V-005                       quoted as AT_OR_UNDER_BOUND only
                           the 4096-entry map
    pool >= 2K; 8 at 3 bits RULING_H1H0_FAIRNESS 09-10 s2c: K = 4, 3-bit tasks,   lane_gate("H1"); VACUOUS V-003     IN       none
                           8 possible witnesses
    0.265 / 0.30           MULTIPLICITY.md: 1 - 0.95^6 and 6 x 0.05 under a        program_family()                   IN       none (arithmetic; test asserts it)
                           global null across six independent lane families
    4.156e-05; 166 / 506   Proteus RESULT_KERNEL_primary: 124 states, 50,000       RULING_PROTEUS_CURRENT_INSTRUMENT  IN       none; the ruling says the floor is a
                           samples/state, two samples                              _AND_R4                                      function of samples/state
    2.168e-19              same: reversible reference max |J|                     same                               IN       quoted as a control that CANNOT FAIL,
                                                                                                                              which is the audit's finding

## Addendum 2026-09-18 (self-attack, review packet Q1/Q2) -> QR-1.2.1

    8 / 12 (H5 reach)     now COMPUTED (h5_reach_bounds_computed): direct 8 exactly, neutral 4,
                          permuted cap 12 = neighbour count; the definition is "distinct
                          NON-PARENT rules" (9 if the parent's rule is counted); a random
                          balanced permutation reaches 11.72 vs the learned 11.7305
    refuse_relabel        was OVER-STRICT: it refused every CONFIRMATORY plan after a DIAGNOSTIC
                          one, including the disjoint-task route it prescribed. 1.2.1 admits a
                          new plan whose confirmation set is disjoint from the diagnostic's tasks
                          (freeze_plan now records task_ids) and refuses the same body, any
                          overlap, or a task-less legacy record.
    validate_cell_payloads chained aliases were refused as dangling; 1.2.1 resolves chains,
                          refuses cycles and alias/cell double-use.

## Not audited on this pass

The 2026-04 cartography numbers (superseded/ directory): out of the seat's
current lane and marked superseded as a whole. The CONFORMANCE_GATE_SPLIT
addenda (route counts 67/68/72 at schemas 7/8/9): each count is dated to its
schema in the text and HARM-43's verification at 72 supersedes the earlier
ones for live use.

## What this audit changes

Two sentences (sqrt(2) "for any rho"; "D3 band floor"), one protocol text
(H4-ADAPTIVE 1.0.0 -> 1.0.1), one population statement (12/5/23 is a
fired-neighbourhood count). No number changed. The recurring shape: a number
computed under a special case (exchangeable Sigma; fired regions; i.i.d.
tables) is later cited without the case. STANDING_RULES.md now carries the
case beside each number it names.
