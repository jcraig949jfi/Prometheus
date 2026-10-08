# AETH-V2B-PROP01 preregistration: multi-generation causal reach

Order: roles/Aether/prompts/2026-10-07_three_flight, Experiment 2. Branch aether/offer01-2026-10-06 (continuing).
Window 2 opened early at 01:12Z, after OFFER01 closed.

## Candidate (rule frozen in the order before Experiment 1)
OFFER01 = OFFER_REPERTOIRE_SUPPORTED, so the candidate is L2 aeth01.reaim_offer1 (reaim1 + TEST-3 exchange).
Comparators: X aeth03.mob_r0x1e0 (exchange-only, the mechanical comparator) and L1 aeth01.reaim1. No other law.

## Assay (prop01_run.py)
- Shared warm-up of 1000 ticks (D50 soup, B_balanced, P0, seeds rng 0xE2010000+k / physics 0xE2011000+k, 512^2).
- IMPULSE = CONTROL except bit 0 of the payload at origin O. O is drawn with rng(0x1A9F + k) uniformly among sites
  that are WRITE with energy >= 1 at warm-up end.
- Then 3000 ticks in lockstep, with identical randomness and no further intervention.
- Conservative attribution via the frozen kernel's observer:
  - parent = a divergent winning source (either world) into a newly divergent field;
  - for rule-driven fields (arg0/payload of a winner), parent = a divergent target the site won into;
  - otherwise UNKNOWN.
- Types:
  - STRUCT: winner identity differs between worlds;
  - CARRY: same winner, different value;
  - RULE: no write.
- Clamp counterfactual: B = the earliest generation-1 site with >= 1 STRUCT or CARRY child (from the uncut tree).
  A third world clamps B to CONTROL from B's first divergence tick onward.
- Fixtures (Aether/test/test_prop01_tracer.py, 4/4):
  - copy chain: generation 4, all CARRY, correct parents, divergence multiplies;
  - clamping B removes all descendants;
  - clamping a non-ancestor leaves them;
  - an isolated difference stays local.
- Conformance (qual/conformance_n64.json): RX == mob_r1x1e0; X == mob_r0x1e0; L1/X/L2 == offer01_run; CPU == GPU
  for all tracer outputs.

## Rules (RULES.json; prop01_reduce.py docstring is the exact text)
- Per seed:
  - LOCAL_ONLY: max_gen <= 1.
  - DIRECT_TRANSPORT: max_gen >= 2, but no multiplication (peak concurrent divergent sites < 3) and no STRUCT at
    generation >= 2.
  - MULTIGENERATION: max_gen >= 2, (multiplies or STRUCT at gen >= 2), and the clamp passes: <= 0.2 of B's
    descendants diverge in the clamped world, and <= 0.5x the rate for non-descendant impulse sites.
  - Otherwise MULTIGEN_UNCLAMPED.
- Candidate disposition:
  - CAUSAL_PROPAGATION_SUPPORTED: >= 6/8 seeds MULTIGENERATION, AND median ever-divergent sites >= 2x each
    comparator, AND median max_gen > each comparator.
  - MULTIGENERATION_WEAK: >= 1 MULTIGENERATION seed.
  - DIRECT_TRANSPORT_ONLY: >= half the seeds are DIRECT_TRANSPORT or MULTIGEN_UNCLAMPED.
  - Otherwise LOCAL_ONLY.
- Gates: dup_L2_s0 has identical digests and tree; every unit rc=0.

## Disclosure: qualification seen (qual/, 512^2, warm 1000, H 3000, seeds 0-1)
| unit | ever sites | radius | max gen | peak concurrent | extinct | re-entries |
|---|---|---|---|---|---|---|
| L2 s0 / s1 | 5 / 8 | 1 / 2 | 1 / 3 | 1 / 1 | no / no | 557 / 686 |
| X s0 / s1 | 3 / 2 | 1 / 1 | 2 / 1 | 1 / 1 | no / no | 1523 / 1547 |
| L1 s0 / s1 | 2 / 8 | 1 / 2 | 1 / 2 | 0 / 8 | 16 / no | 0 / 0 |

Under exchange, the divergence stays a single token (peak 1). Under reaim1 copying it can multiply. The thresholds
above were chosen for their meaning (multiplication >= 3; the clamp removes >= 80% of descendants) with these
numbers known.

## Scale and replication
- 512^2 (footprints have radius <= 2, so lattice area is irrelevant; replication is spent on seeds).
- 8 seeds x 3 laws uncut + dup_L2_s0, then the clamp units.
- ~400 s per unit at 4 concurrent, so ~80 min total.
- Hashes (LF as in git):
  b6ffc2d63388ac3ac4ee74007daeb84abd6a3d3936290b63eeee91030afff480 production/plan_uncut.json
  b0cb59d837c7e36926d804d885575ddd3fc8f11308c8b5758fa9911c565ac8a3 production/plan_cut.json
  29eb8e2bbdfd3ee461068fc4c56d988a740a4c53862a22981bfae3b277822b9f RULES.json
  625872e05766701c6a354d214718e5ccf62916962f13888077a1adbe04d4650d prop01_run.py
  9d034fc4c1dddb2e633fe683d60260e5b28b7b958dd8c72ddc2f76fb31c09b3c prop01_tree.py
  2946602ab3d88a356da5f5256eab56c65517db6f25f74d1191ea642fc398df22 prop01_reduce.py
  1a70598e3d443f167d5bd93725684dcfe7e55f6809cdd1a8334dd040c04fc396 prop01_flight.py
  1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65 ../../runpod/aeth01_canary/aeth01_gpu_kernel.py
