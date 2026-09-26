+==============================================================================+
|  APHRODITE -- AMENDMENT 16 CAMPAIGN REPORT (four-hour recursion campaign)    |
|  Author: Aphrodite (RSI seat), host harry1 / M4.  Date: 2026-09-24           |
|  For: James (HITL) and external reviewers. Self-contained.                   |
+==============================================================================+

Prereg: AMENDMENT_16_2026-09-24.md @ 46e477d81 (T0 18:35:51Z). Code a16.py @ 5c74e4c58.
AMENDMENT 15 stands: BRSI = NO, INTERPRETATION = UNTESTABLE_CATALOG (not redrawn).
GLOBAL_BEHAVIOR_IDENTITY = FAIL (permanent). Campaign 1 frozen and unrun. No G3.

------------------------------------------------------------------------------
0. DISPOSITIONS
------------------------------------------------------------------------------
  CATALOG_A = FOUNDRY_INCOMPLETE_TIME (no disposition; draw stream sha 0f3b69de7355; wave 1: 3/56 accepted)
  CATALOG_B = FOUNDRY_INCOMPLETE_TIME (no disposition; draw stream sha 8258ec194a8e; wave 1: 4/56 accepted)
  CATALOG_C = draw stream generated and hashed only (sha debc93aa75bf); never qualified (E3 not triggered)

  E1 (catalog A):
  E1_BOUNDED_RSI = UNTESTABLE (time: catalog A never completed; no donor ran)


  E2 (catalog B):
  E2_BOUNDED_RSI = UNTESTABLE (time: catalog B never completed; no donor ran)


  REPLICATED_BOUNDED_RSI = NOT TESTED (neither experiment ran)
  G4_REPRESENTATIONAL_CEILING = UNTESTABLE
    precondition (1) unmet: E1 and E2 never reached donor adjudication.

  S1_NECESSITY = INCONCLUSIVE  (WHOLE recovered 3/3, BODY_ONLY 1/3)
    F1/BODY_ONLY derived [] selected INHERITED RECOVERED False
    F1/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    F2/BODY_ONLY derived [] selected INHERITED RECOVERED False
    F2/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    F3/BODY_ONLY derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    F3/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    note: On F1 and F2 -- the sets whose ONLY sum-of-squares observation is the compensating form -- BODY_ONLY derives nothing and WHOLE recovers and selects (acc + {H}). F3 (Tier 3A) also contains a plain additive sumsq observation, so it was not fully adversarial and BODY_ONLY recovers there too. By the frozen rule that makes the outcome INCONCLUSIVE; the F3 design flaw is the seat's.

------------------------------------------------------------------------------
1. CLOUD, TIME, SPEND
------------------------------------------------------------------------------
  CLOUD_UNAVAILABLE at T0 (no RunPod key, no Azure CLI/credential); not polled.
  Total cloud spend: $0.00. No remote resource created.
  Total elapsed: 1 h 15 min of the 4 h envelope (T0 18:35:51Z -> stop 19:50:46Z; report ~19:55Z)
  Wall-clock under concurrent stages is CONTAMINATED; all endpoints are charges.

------------------------------------------------------------------------------
2. APPARATUS DEFECTS AND DEVIATIONS
------------------------------------------------------------------------------
  - FOUNDRY THROUGHPUT DEFECT (planning): Q2 was budgeted at ~80 s/family from a solo timing. Under 6-way contention, and for FAILING families (where every calibration draw re-scans thousands of surviving wrong classes), wave 1 took 62 min for 112 draws. Acceptance was ~6% (A 3/56, B 4/56). Wave-1 per stratum accepted/evaluated: A add 0/8, sub 2/8, mul 0/8, fdiv 0/8, mod 1/8, gcd 0/8, powr 0/8; B add 2/8, sub 1/8, mul 0/8, fdiv 0/8, mod 1/8, gcd 0/8, powr 0/8.
  - FOUNDRY STOPPED FOR TIME at 19:50:46Z, during wave 2, so no catalog reached its frozen 32-draw limit. Projected completion was ~3 h more, after which E1 alone needs ~50 min; nothing admissible could finish before the 22:20:51Z reserve. Catalogs A and B therefore have NO disposition (neither TESTABLE nor UNTESTABLE); they are FOUNDRY_INCOMPLETE_TIME. The wave-1 evaluations were in memory only and are lost (only the log counts survive) -- a second defect: the foundry did not checkpoint.
  - Q2 is O(draws x wrong-classes x dev-size) in pure Python. An exact bitmask form (agreement masks over the 240-probe pool) would cut its calibration half by ~100x without changing any decision; reachable-program enumeration (86,400 x 240 evaluations) is the other half and needs a certified faster evaluator.
  - The stratified G4 draw is extremely sparse in qualifiable families: across both catalogs mul, fdiv, gcd and powr accepted 0 of 64 draws each in wave 1. A 4-per-stratum quota may be infeasible for those operators at any draw limit.
  - E4 ran concurrently with the foundry (2 + 6 workers): the wall-clock of both is CONTAMINATED; E4's endpoints are selections and charges, which are unaffected.
  - CLOUD_UNAVAILABLE: no canary could run; $0 spent.

------------------------------------------------------------------------------
3. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------
  DOES: E4 shows, on the two genuinely adversarial observation sets, that whole-program member enumeration + certification recovers (acc + {H}) where body-only anti-unification derives nothing -- suggestive of S1 necessity, but the frozen verdict is INCONCLUSIVE.
  DOES NOT: say anything about recursion. E1 and E2 never started; BOUNDED_RECURSIVE_SELF_IMPROVEMENT remains UNTESTED under AMENDMENT 16 (and NO/UNTESTABLE_CATALOG under AMENDMENT 15). No catalog disposition exists. Nothing here is Campaign 1 evidence.
  RECOMMENDATION: before any retry, (1) make Q2 exact-fast (bitmask) and checkpoint foundry evaluations; (2) budget the foundry from a CONTENDED pilot; (3) decide whether a per-stratum quota is feasible for mul/fdiv/gcd/powr in G4 -- the evidence says probably not, which is itself a finding about the G4 task space.

------------------------------------------------------------------------------
4. ARTIFACTS
------------------------------------------------------------------------------
  A16_DRAWS_2026-09-24.json (A/B/C draw streams + hashes), A16_E4_RESULT_2026-09-24.json,
  A16_FOUNDRY_2026-09-24.log, A16_E4_2026-09-24.log, a16.py (5c74e4c58), a16_report.py
  (roles/Aphrodite/engine/). No A16_CATALOGS / DONORS / E1 / E2 artifacts exist.
  branch aphrodite/engine-2026-09-21

+==============================================================================+
|  END. 'Not worth continuing' remains a first-class answer.                    |
+==============================================================================+
