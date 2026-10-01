# INFERENCE SATURATION WAVE 2: HANDOFF (Ananke / PTE)

Status: DRAFT, filled progressively. FINAL at 08:30Z close.
Directive: roles/Ananke/prompts/2026-09-30_inference_saturation_wave2/ (sha256 3c68feac...).
Ledger: harvest/wave2/INFERENCE_LEDGER.md. Common worker brief: harvest/wave2/COMMON_BRIEF_W2.md.
Workers ran on Opus. Each report is deposited verbatim with provenance at harvest/wave2/<id>/REPORT.md.

## Strongest new result since Wave 1
(draft) Most of C1's structural "laws" and NULLs are decided by construction (env placement, light
cone, ruler, sampling) before search runs:
- 43% of XOR searches were light-cone-capped (W2-G F3, W2-A2 F5);
- all MAJ SIGNALs are one-hop placements, and MAJ "d" does not mean distance (W2-A2 F3);
- "topology-bound" laws are hop-bound (W2-G F1);
- the GA selects for exactly what the twin ruler measures (W2-A2 F1).

## Strongest Wave-1 conclusion weakened or killed
(draft)
- "Evolved PTE transport is one hop": ~77% of RELAY tasks only demanded one hop, and MAJ placement
  forced it; a sampling fact.
- "Topology-bound laws": KILL candidate (hop count).
- "17% XOR capped": the true figure is 43%.
- FLIP @ d9cc "two NULLs": one is a transfer.

## Most important unresolved contradiction
(draft) Search vs representation vs plant at uncapped rows. relay_flood fails at most light-cone-
reachable multi-hop A-wave rows (P-1b), yet succeeds at d9cc. Is it physics beyond the light cone
(loss/cap/decay), or the plant's design?

## Best reusable infrastructure improvement
(draft) prometheus/ananke/inference.py (BOOTT/t/BH/Holm/replication gate; W2-H). Pending: W2-F
library, W2-C mutation harness, W2-I kind auditor.

## Best future experiment not yet authorized
(draft) ANANKE-14 w=0 shaping A/B, plus plant-seeded GA retention at the uncapped rows. Both need
search authorization.

## Strangest observation deserving preservation
(draft)

## Started but not completed
(draft)

## Code changes (NEUTRAL, each with regression tests that fail before and pass after)
- c1b_run fresh-eligibility key (W2-A2 F8): tests/test_c1b_run_fresh_eligibility.py
- report additive TRANSFER_SUPPORT_EFFECTIVE + P1 phys-track filter (W2-A2 F6/F9):
  tests/test_report_transfer_effective_p1.py
- inference.py (W2-H): tests/test_inference_w2h.py

## Durable outputs (paths / commits)
(filled at close)
