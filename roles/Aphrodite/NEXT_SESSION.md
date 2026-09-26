# Aphrodite -- pick-up state for the next session

Written 2026-09-25, before an operator-requested reset. READ THIS FIRST,
then STATUS.md, then journal/2026-09-23.md (it covers 09-23 to 09-24, every
error in full). The previous handoff (2026-09-22) is
superseded/NEXT_SESSION_2026-09-22.md.

--------------------------------------------------------------------------
1. WHERE THE SCIENCE STANDS (dispositions, never pooled)
--------------------------------------------------------------------------

  DIRECT_COMPETENCE_REUSE             NO          slice 3
  STRUCTURAL_SEARCH_LEVERAGE          YES         slice 4
  TRANSFERABLE_SEARCH_LEVERAGE        YES_LOCAL   Tier 3B 47x, Tier 3C 345x
  BOUNDED_RECURSIVE_SELF_IMPROVEMENT  NO          Tiers 3A-3C (old criterion)
  GLOBAL_BEHAVIOR_IDENTITY            FAIL        permanent (S1 runs 1-3)
  CAMPAIGN_RELEVANT_IDENTITY          PASS        class certificates (cert.py)
  FAIR_META_SELECTION (S2)            PASS
  ENDOGENOUS_ABSTRACTION (S3)         YES         donor derived + selected (acc + {H})
  ABSTRACTION_TRANSPLANT (S4)         YES         ACCEPTED by operator 2026-09-24
  BOUNDED_RSI (operator)              NOT YET ESTABLISHED
  AMENDMENT 15 (G1->G2)               BRSI = NO, INTERPRETATION = UNTESTABLE_CATALOG
                                      (no donor ran; not evidence either way)
  AMENDMENT 16 (4-h campaign)         returned early for TIME:
      catalogs A/B FOUNDRY_INCOMPLETE_TIME; E1/E2 UNTESTABLE; E3 UNTESTABLE;
      E4 S1_NECESSITY = INCONCLUSIVE (WHOLE 3/3, BODY_ONLY 1/3; F3 was not
      fully adversarial -- my prereg flaw); cloud $0 (no credentials)

The operator's S4 review (2026-09-24), in short: it is a real positive for
endogenous derivation plus causal transplant INSIDE THIS DSL, and recursion is
not established. The catalog partly funnelled toward (acc + {H}) (Q1).
Condition 7 must be rewritten before reuse -- no grandfathering (Q3; done in
AMENDMENT 15 R3). Positive-control admission is to be removed in future
(done: treatment-blind admission).

--------------------------------------------------------------------------
2. WHERE TO RESUME THE SCIENCE
--------------------------------------------------------------------------

The live question is exactly one: does the inherited G1 abstraction help
produce a NEW, semantically distinct abstraction that improves a fresh G2
relative to G1 (AMENDMENT 15 chain, R1-R5)? It has NEVER been tested: both
attempts died at family supply.

Before any retry (needs a NEW preregistration and operator authorisation):
  (1) FIX THE FOUNDRY: make Q2 calibration exact-fast (bitmask agreement
      masks over the 240-probe pool); checkpoint every evaluated draw to disk;
      budget from a CONTENDED pilot, not a solo timing (wave 1 took 62 min for
      112 draws, ~6% acceptance).
  (2) DECIDE FEASIBILITY: in G4, the mul/fdiv/gcd/powr strata accepted 0/64
      draws each. A 4-per-stratum quota may be infeasible -- itself a finding
      about the G4 task space. Options: drop the per-stratum quota for a
      global one, or measure acceptance per stratum first (cheap once Q2 is
      fast).
  (3) OPTIONAL: E4 again with three genuinely adversarial forced observation
      sets, to turn S1_NECESSITY from INCONCLUSIVE into a verdict.
  (4) The G5 (depth-3) ceiling probe stays conditional on valid G4 negatives.

--------------------------------------------------------------------------
3. OPEN QUESTIONS FOR THE OPERATOR
--------------------------------------------------------------------------

  Q-A  Authorise AMENDMENT 17 = the AMENDMENT 16 E1/E2 design, with the
       foundry fixes of s2(1), and with the quota rule chosen under s2(2)?
  Q-B  Per-stratum quota vs a global quota with mechanical diversity, given
       that 4 of 7 G4 operator strata looked empty?
  Q-C  Provide cloud credentials (RUNPOD_API_KEY in the environment; az login
       plus FSv2 quota) so the acceleration canaries can run ($1 per
       provider)? RunPod fasteval is the stronger candidate (~12x end to end
       locally, exact).
  Q-D  Re-run E4 with a corrected fully-adversarial F3?
  Q-E  Or declare the engine line complete at S4 (the "stop" answer remains
       first-class).

--------------------------------------------------------------------------
4. REPORTS AND FROZEN DESIGNS (all under roles/Aphrodite/)
--------------------------------------------------------------------------

  pivot/APHRODITE_ENGINE_REVIEW_11_2026-09-24.md        S1-S4 chain packet
  pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-24.md  4-h campaign
  engine/AMENDMENT_12_2026-09-23.md + ADDENDUM_1/_2/_3  S1 and certification
  engine/AMENDMENT_13_2026-09-23.md                     S2
  engine/AMENDMENT_14_2026-09-23.md                     S3 + S4
  engine/AMENDMENT_15_2026-09-24.md                     G1->G2 assay (frozen)
  engine/AMENDMENT_16_2026-09-24.md                     4-h master prereg
  Results: engine/S1_GATE_RUN{1,2,3}*, S1_LOCAL_GATE, S2_GATE, S3_ARTIFACT,
    S4_RESULTS, T3E_*, G2_RESULTS, A16_DRAWS, A16_E4_RESULT (+ .log files)
  Code: identity.py, cert.py, fair.py, tier3d.py, tier3e.py, run_s3s4.py,
    run_g2.py, a16.py, a16_report.py, s1_gate.py, s1_local_gate.py, s2_gate.py

--------------------------------------------------------------------------
5. APPARATUS FACTS TO REMEMBER
--------------------------------------------------------------------------

  - behavior_id is a PROVISIONAL BUCKET; any class that affects science
    needs a cert.py certificate (fresh B_CERT + threshold-adversarial A(S)).
  - Identity domain D_TASK_T3_v1 (lengths 2-60, 80, 150, 200; values 2-30;
    query 1-97). Conformance covers the ceiling edges (B1_BOUNDARY).
  - Emitter v2 (output ceiling guard) for everything from S2 on; v1 is kept
    byte-identical for reproducing Tiers 3A-3C.
  - Recipient.fresh() wipes a GLOBAL marker dir: every process pool must use
    a per-worker MARKER_DIR (see run_s3s4._worker_init).
  - Family names must contain no digits (prompts are parsed by regex).
  - The host Python has no pytest (use a venv). Commit with
    -c user.name=Aphrodite. Never `git pull` in C:\Prometheus. Verify every
    stopped process by PID (TaskStop does not kill detached children).
  - Acceleration branches (engineering only, merged to main 2026-09-25):
    accel-azure-cpu (process pool, 480/480 exact) and accel-runpod
    (fasteval, 1.16M evaluations exact, ~12x). NEITHER is science-eligible
    until its cloud canary passes.

Campaign 1 remains FROZEN and UNRUN (contracts from Archaeon, Harmonia and
Vivarium, plus benchmark receipts from Nestor and Archaeon, still outstanding).

--------------------------------------------------------------------------
UPDATE 2026-09-26 -- AMENDMENT 16 CAMPAIGN, SECOND EXECUTION (AMENDMENT 17)
--------------------------------------------------------------------------
Operator lifted the Q-A..Q-E hold 2026-09-26 and authorised the campaign.
Report: pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md
Prereg: engine/AMENDMENT_17_2026-09-26.md @ 373d7ef28. 48 min of 4 h; $0.
  E0 CATALOG_A TESTABLE (O4/V3/T4); CATALOG_B UNTESTABLE (O2/V2), not redrawn
  E1_BOUNDED_RSI = NO   (valid R1 novelty failure: G1 donors only met successes
                         (acc + {H}) already explains and re-derived it)
  E2_BOUNDED_RSI = UNTESTABLE (catalog); REPLICATED = NO
  G4_REPRESENTATIONAL_CEILING = UNTESTABLE (E2 never reached donors)
  S1_NECESSITY = SUPPORTED (WHOLE 3/3, BODY_ONLY 0/3; F3 repaired to F3*)
  RUNPOD/AZURE_UNAVAILABLE_TO_APHRODITE.
Binding constraint now: family SUPPLY for non-additive G4 operators (Q3/Q2
reject degenerate draws; mul/mod/powr 0/32 in both catalogs). Any new sampler
is an operator design choice. Engineering now available: a17.py exact-fast
Q2 (gated) + checkpointing; fasteval admitted by a 288k-pair gate.
Comms: experiments are no longer managed via Aporia or Cyclops; ignore them.
Branch aphrodite/a16-campaign-2026-09-26 (pushed; not yet merged to main).
