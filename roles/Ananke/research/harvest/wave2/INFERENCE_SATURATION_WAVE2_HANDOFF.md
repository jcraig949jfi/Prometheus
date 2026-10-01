# INFERENCE SATURATION WAVE 2: HANDOFF (Ananke / PTE)

Status: FINAL (written 09:05Z). Worker inference stopped at ~03:20Z when the Opus weekly API limit was reached (HTTP 429), so the planned 04:30-05:00 ET close was compressed. All durable work is committed and on main.
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
From the W2-AG register (harvest/wave2/W2-AG/STRANGE_REGISTER.md, 15 entries):
- SR-01, the exact one-hop wall: 13/14 native 2-hop conditions are exactly .500 with zero variance, and
  in 4/5 single-rule D laws non-sensing sites can never emit.
- Multi-hop SIGNALs exist only as once-per-episode flood latches (E-W22).
- SR-03 (candidate): 4781b0a1 integrates by reverberation between adjacent cued sensors.
- Distractor-strobed HOLD memory (5/86) and the rule-mosaic lottery.

## Started but not completed
Seven workers were terminated at ~03:20Z by the API weekly limit with no final report. Their dirs hold
partial outputs and are marked INCOMPLETE.md (do not cite):
- W2-AD: C2 admission census.
- W2-AE: explib promotion package.
- W2-AF: 69 unscored MAJ NULLs + RELAY binding dials.
- W2-AH: economy energy ceiling (the last open SUPPORTED boundary).
- W2-AJ: emitter census + 4781b0a1 edge cut.
- W2-AK: MAJ seeded-GA retention.
- W2-AL: latch prevalence across all SIGNAL champions.
These are the highest-value next items. W2-AL and W2-AH decide how much of C1's RELAY competence is
per-trial and whether economy is physics.
Also not done: C4 R-STAT FINAL (blocked on Cosmos; notes in roles/Ananke/research/c4/).

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
- Worker reports W2-A1 .. W2-AC, W2-AG, W2-AI, W2-V, W2-W, W2-X, W2-Y, W2-Z: harvest/wave2/<id>/REPORT.md
  plus .provenance.json.
- Principal: harvest/wave2/P-1/ (H6_ADVERSARIAL.md v1-v4 + sections 14-15; DEFECT_PATTERNS.md;
  decay_plant*), INFERENCE_LEDGER.md.
- Errata: roles/Ananke/pte/C1_ERRATA.md E-W1..E-W23 plus the corrections block.
- C2 draft: harvest/wave2/W2-AB/PREREG_PTE_C2_DRAFT.md (NOT frozen, NOT authorized).
- Per-cell NULL placement: harvest/wave2/W2-W/null_placement.csv.
- Code: prometheus/ananke/{campaign.py, report.py, c1b_run.py, inference.py} and tests/;
  roles/Ananke/research/{deposit.py, tools/kind_audit.py, tests/}.
- All on origin/main; see git log --author on 2026-10-01 for commits.
