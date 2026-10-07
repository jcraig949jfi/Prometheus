# AETH-V2B-PROP01 RESULT: multi-generation causal reach

Order: roles/Aether/prompts/2026-10-07_three_flight, Experiment 2. Freeze 3aac2b57c. Production 01:22Z-02:21Z
(uncut 25/25 rc=0; clamp units 24/24 rc=0). Reduction production/REDUCTION.json (prop01_reduce.v1, frozen RULES.json).
Candidate L2 = aeth01.reaim_offer1 (frozen rule after OFFER01 SUPPORTED); comparators X (exchange-only) and L1
(reaim1).

## Technical disposition: PASS
- All units rc=0.
- dup_L2_s0 identical: digests, tree, series.
- Tracer known answers 4/4 (copy chain, clamp positive, clamp negative, isolated).
- CPU == GPU for every law.
- UNKNOWN parents: L2 0, X 0, L1 9 (seeds s4/s6). Attribution was conservative and never inferred from state
  differencing.

## Preregistered disposition (candidate L2): MULTIGENERATION_WEAK
Per-seed classes (8 seeds each):

| law | MULTIGENERATION | MULTIGEN_UNCLAMPED | DIRECT_TRANSPORT | LOCAL_ONLY | median ever-divergent sites | median max generation | radius range |
|---|---|---|---|---|---|---|---|
| L2 reaim1 + exchange (candidate) | 1 | 0 | 2 | 5 | 5 | 1 | 1-3 |
| X exchange only | 3 | 0 | 2 | 3 | 3 | 2 | 1-2 |
| L1 reaim1 | 3 | 0 | 0 | 5 | 5 | 1 | 0-6 |

- L2 does not exceed its comparators; the SUPPORTED clause needs >= 6/8 MULTIGENERATION seeds and >= 2x reach.
  WEAK because one seed qualifies.

The qualifying chains (A alters B, altered B alters C, clamping B removes C):

| seed | max gen | sites | peak concurrent | STRUCT at gen >= 2 | B's descendants | fraction re-diverging when B clamped | non-descendant control fraction |
|---|---|---|---|---|---|---|---|
| L2 s4 | 3 | 14 | 14 | 4 | 5 | 0.0 | 1.0 |
| L1 s1 | 2 | 8 | 8 | 0 | 3 | 0.0 | 0.50 |
| L1 s4 | 3 | 14 | 12 | 3 | 5 | 0.0 | 0.50 |
| L1 s6 | 4 | 14 | 11 | 3 | 4 | 0.0 | 0.44 |
| X s2 / s3 / s6 | 2 | 3 | 3 | 1 / 0 / 1 | 1 | 0.0 | 0.0 |

- The X chains are minimal: 1 descendant, and with a control fraction of 0.0 the clamp test passes but cannot
  discriminate.
- The L1 and L2 s4 chains are the real ones: 3-5 descendants all vanish when B is clamped, while 44-100% of
  non-descendant impulse sites still diverge.

Shape of the divergence (all seeds):
- Exchange laws keep the impulse a single token. L2 peak concurrent divergent sites is 1 in 6/8 seeds, re-entries
  are ~570 (median) as the token bounces between a few sites, and it never goes extinct.
- reaim1 (copy) either dies or saturates locally (re-entry 0) and multiplies in 3/8 seeds.
- Type totals:
  - L2: 4 STRUCT / 37 CARRY / 3 RULE.
  - X: 2 / 9 / 2.
  - L1: 9 / 29 / 8.

## Reading
- Multi-generation causal chains EXIST in Aether: a payload bit alters B, altered B alters C, and clamping B removes
  C. They appear under reaim1 alone (3/8 seeds) and under the candidate (1/8), with depth <= 4 generations and
  radius <= 6 sites in 3000 ticks.
- They are rare and short. They are not reproducible at the preregistered rate in any law. The candidate is no
  better than reaim1.
- OFFER01's repertoire release does NOT buy causal reach. The exchange swap turns a difference into a conserved
  TOKEN (peak concurrent 1), which moves and bounces but does not multiply. Copy semantics (reaim1) is what lets a
  difference multiply, and only rarely.
- The order's threshold ("A alters B, altered B alters C, intervening on B removes the effect at C") is met in
  individual seeds of L1 and L2 (4/16), not reproducibly within a law at the frozen bar.

## Answers (s2 measures)
- Divergent sites: candidate median 5 (max 14).
- Fields: mostly single-field CARRY.
- Max radius: candidate 3, L1 6.
- Depth: <= 4 generations.
- Branching: present only in the MULTIGENERATION seeds.
- Duration: the exchange-law token never goes extinct in 3000 ticks; it persists without spreading.
- Re-entry: dominant under exchange (token bouncing).
- Direct transport vs secondary writers: L2 is 84% CARRY; STRUCT (a changed writer identity) occurs at gen >= 2
  only in s4.

## Limitations
- 512^2, warm-up 1000, horizon 3000, payload bit-0 impulses only, one origin per seed, P0, B_balanced.
- The clamp is chosen on the first generation-1 site with a STRUCT/CARRY child, so chains passing only through
  RULE-type children have no cut (L2 s1, generation 3).
- The clamp's non-descendant control set can be empty or all-converged (X seeds), making a pass uninformative
  there.
- The thresholds (multiply >= 3, clamp <= 0.2 / 0.5x) were frozen after qualification (disclosed).

## Next (frozen rule)
PROP01 is not CAUSAL_PROPAGATION_SUPPORTED, so Experiment 3 = Branch B, ROUTE01 (content-dependent retargeting).
