# INFERENCE SATURATION WAVE 2: HANDOFF (Ananke / PTE)

Status: DRAFT v2 (~03:05Z), revised after the W2-X adversarial review. FINAL at the 08:30Z close.
Directive: roles/Ananke/prompts/2026-09-30_inference_saturation_wave2/ (sha256 3c68feac...).
Ledger: harvest/wave2/INFERENCE_LEDGER.md. Common worker brief: harvest/wave2/COMMON_BRIEF_W2.md.
Workers ran on Opus, plus principal investigations P-1..P-4 and X-1/X-2. Each worker report is
deposited verbatim with provenance (and, from 02:52Z, a kind_audit record) at
harvest/wave2/<id>/REPORT.md.
Errata: roles/Ananke/pte/C1_ERRATA.md, E-W1..E-W21 plus the "Corrections to the Wave-2 errata" block.
C1 labels and rows are unchanged.

## Strongest new result since Wave 1
C1's NULLs and "phase boundaries" are mostly not evidence about search or physics as reported.
- NULLs (E-W20, W2-W per-cell table): of 454 C1 evolve NULLs,
  - 139 (30.6%) are physics-capped by a sound bound (light cone + exact wake, joint ceiling, LC2, or
    epidemic bound);
  - 62-65 (~14%) are eligible for any search-limitation reading (admissible, and a plant fits the row's
    own genome);
  - 250 are open.
  - 0/113 replayed NULLs were broken experiments (W2-T).
- Boundaries (E-W21, W2-Y): of C1's 13 SUPPORTED boundaries, NONE is established physics beyond the
  transport bound:
  - delta = transport-time identity;
  - RELAY decay = relay_flood plant design (a refresh plant is flat on the actual transect rows);
  - HOLD decay = non-refreshing-latch artefact [I];
  - emit-vs-rules = program space;
  - economy = OPEN (W2-AH running).

## Strongest Wave-1 conclusion weakened or killed
"Evolved PTE transport is one hop" (Wave-1 handoff 1.2), as a law.
- It is a description of the 6 independent lineages found (E-W19).
- In the unbiased A1 frame: one-hop 3/32 vs multi-hop 1/39, p = .32.
- The D-wave "topology-bound" collapse is hop count, refined to cluster and latency-label dependence for
  4 laws (E-W1).
- Whether C1 search can discover forwarding is UNDECIDED: 2 marginal multi-hop SIGNALs, mechanism being
  tested by W2-AI.
Also killed:
- "17% of XOR capped" (it is >= 43%, and 75% under LC2);
- C1's decay physics map for relay_flood (E-W13, scoped to matched counterfactuals and transect rows);
- XOR_PIVOT and FLIP_FEEDBACK as certificates (E-W6, E-W17).

## Most important unresolved contradiction
Search versus plant at the open NULLs. 250/454 NULLs are neither capped nor plant-eligible. Two
explanations remain:
- (a) search failed;
- (b) no adequate plant has been found.
Either can explain them. FLIP@d9cc is the only fully chained cell: S, with U not observed over 2 seeds.
C2 (W2-AB draft) is designed to decide this at admitted cells.

## Best reusable infrastructure improvement
The pre-freeze instrument-certification stack:
- W2-B attainability certifier;
- W2-C mutation gate + guards (W2-O G12 patch);
- W2-F explib;
- ceiling bounds (lcwake / LC2 / flood / epidemic);
- the FLIP B certificate;
- XOR_SYM;
- inference.py (BOOTT/t/BH/Holm, reading3 with DEGENERATE, keep_prob with f);
- kind_audit wired into deposit.
W2-AE is packaging these as one additive, tested library.

## Best future experiment not yet authorized
PTE-C2 (W2-AB/PREREG_PTE_C2_DRAFT.md; DRAFT, NOT FROZEN, NOT AUTHORIZED).
- Question: H6 at admitted cells (P/R/V excluded by admission), with arms BASE (12 seeds), W0 (shaping
  off), M32, B4X, PSEED, KSEED and STEP.
- Decisive tier 9-15 GPU-h. It needs operator/s7 authorization.
- The admission census (W2-AD, running) decides whether 4 cells per core family exist.

## Strangest observation deserving preservation
(W2-AG register pending.) Current candidates:
- distractor-strobed HOLD memory: 5/86 champions use the first awake distractor as a store strobe, at
  physics identical to schedule-robust siblings;
- the rule-mosaic lottery: one live rule plus one dead rule, decided by the actuator's random initial
  rule.

## Started but not completed
(filled at close.)

## Code changes on main (each with tests that fail before and pass after)
1. c1b_run fresh-eligibility key (W2-A2 F8).
2. report.py additive TRANSFER_SUPPORT_EFFECTIVE + P1 phys-track filter (W2-A2 F6/F9; vacuous on C1).
3. inference.py (W2-H): BOOTT/t/BH/Holm/replication gate; reading3/kill_eligible (W2-K); f parameter
   (W2-AB); zero-variance reads DEGENERATE (W2-X).
4. campaign.py batch:
   - the effective dest_mode record, with dest_mode_drawn kept so transects derive from the drawn value
     (W2-A1 + W2-X fix; neutral for C1; it restores future semantics my first version had changed);
   - FLIP transplant -> NOT_APPLICABLE (W2-A1);
   - transfer REACH_BEYOND_HOP=None (W2-A2);
   - persisted wave clock + exact-resume PARK (W2-A2).
5. Harvest H-INST reach_certificate window patch (W2-B).
6. research/tools/kind_audit.py + advisory deposit hook (W2-AA).
Incident: a failing test was committed in dc46fd00f (pushed via merge 96b47d73e). It was fixed next
commit, and commits are now gated on the test exit code.

## Durable outputs (paths / commits)
(filled at close.)
