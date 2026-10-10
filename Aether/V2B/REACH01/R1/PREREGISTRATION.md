# REACH01 R1 / TEST-4 preregistration: recoil + exchange -- information or arithmetic?

Order: roles/Aether/prompts/2026-10-10_reach01 (R1). Design: the TEST-4/DEV-4 design agreed with the operator in
Aether/V2B/TEST-3/OPERATOR_REVIEW.md, implemented without new physics.

## Laws (exact, bit-identical to aeth03_variants: R1/qual/conformance.json)
V1 aeth01.v1; X mob_r0x1e0 (exchange only, the negative baseline); R mob_r1x0e0 (recoil only); RX mob_r1x1e0
(recoil + exchange). B_balanced, P0, D50 soup, 512^2, warm-up 1000, seeds k = 0..7 (rng 0xE2010000+k,
physics 0xE2011000+k).
Difference from TEST-3: TEST-3 ran at 128^2 with a perturbation-ON warm-up. Here the world follows the
P0 / B_balanced / D50 conventions used since ER01.

## Decodability (r1_test4.py, r1_reduce.py)
- Branching: 256 origins per world on a 32-spaced grid (each moved to the nearest active WRITE site within 3), and
  8 branches planting V = [0x03, 0x2A, 0x51, 0x7C, 0x96, 0xB5, 0xD8, 0xF7] in every origin's payload, plus an
  unplanted BASE.
- Features: 200 observed ticks. At ticks 25/50/100/200, for radius r = 1..6 rings, a 256-bin histogram per template
  field.
- Decoder: nearest-centroid on per-origin mean-centred features (label-free centring); leave-one-seed-out held-out
  accuracy; null = per-origin label-permuted training.
- Dstat = mean over r in 2..6 and all ticks of (accuracy - 1/8).
- Ruler qualification (Aether/test/test_reach01_r1_ruler.py, 3/3 pass):
  - exchange decodes at r = 1 only;
  - a copy relay chain decodes at r = 1..6;
  - label-unrelated divergence decodes at chance.

## Causal depth (r1_trace.py = the qualified PROP01 tracer with the R1 law set)
- Payload bit-0 impulse, 3000 ticks.
- Clamp B (earliest gen-1 site with a STRUCT/CARRY child).
- NON-ANCESTOR control: clamp a non-tree site at B's distance from the origin, from the same tick.
- Classes as PROP01 (RULES.json trace_rules).
- A seed is CAUSAL-CERTIFIED if its class is MULTIGENERATION AND, in the non-ancestor world, >= 0.5 of B's
  descendants still diverge.

## Decision (agreed criteria, made numeric)
- DECODABILITY REACH: RX Dstat > X Dstat + 0.02 AND > RX null Dstat + 0.02 in >= 6/8 seeds.
- CAUSAL DESCENDANTS: RX causal-certified seeds >= 3 AND >= X's count + 2.
- RECOIL_EXCHANGE_CONTENT_REACH_SUPPORTED iff both hold.
- Otherwise RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED: TEST-3's P1 mobility finding is retained, and not promoted
  to circuitry.
- Gates: dup_RX_s0 trace identical; all units rc = 0; one table hash per tool.

## Seen before freezing
- Scout: 4 decode units for seed 0 only. A decoder needs >= 2 seeds, so no decodability number was seen; only
  runtime (176 s per unit at 4 concurrent, ~3 MB of features).
- PROP01 (published) had no RX/R arms.

## Plan
- Phase 1: 32 decode units + 33 uncut trace units.
- Phase 2: 64 clamp / non-ancestor units.
- Evidence: C:/Prometheus-data/aether_reach01/R1/ (features untracked). Unit JSONs and reductions are copied into
  R1/evidence/.

Hashes:
  1c8b515cb5f881214214dad307fc2aebec6b53e5f68785516f5c6ac3cb8cb3e7 RULES.json
  e49a269cd43a8a60a146a27acd0ffdcc67bd44fb38ce565a5d4da2b78a7f9a08 plan_phase1.json
  5fa5e5c2985d8ebca0be4bb568d21235f69cd85b7dc73d8247f3304a2941382b plan_phase2.json
  aa57a736803d6e65219db16b203793edca4c58dca5b8acf7ad5e347d4ef88c98 r1_test4.py
  f211843ebc70c6d873bd25d098688dfe69264a43c485609904513b70f5568fd4 r1_reduce.py
  879b7d3f3113d429a9304f1621c9fe460eedb26723067dfd0b8cbaed8be039f8 r1_trace.py
  2b594c81418d1fa1f845dd09216dc12c805c209b834b711edbd46c82919e8b54 ../reach_flight.py
  625872e05766701c6a354d214718e5ccf62916962f13888077a1adbe04d4650d ../../PROP01/prop01_run.py
  9d034fc4c1dddb2e633fe683d60260e5b28b7b958dd8c72ddc2f76fb31c09b3c ../../PROP01/prop01_tree.py
  2946602ab3d88a356da5f5256eab56c65517db6f25f74d1191ea642fc398df22 ../../PROP01/prop01_reduce.py
