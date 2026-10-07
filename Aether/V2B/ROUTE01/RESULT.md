# AETH-V2B-ROUTE01 RESULT: content-dependent retargeting (Branch B)

Order: roles/Aether/prompts/2026-10-07_three_flight, Experiment 3 (Branch B: PROP01 was MULTIGENERATION_WEAK).
Freeze 5e31c2763. Production 02:34Z-04:30Z: uncut 57/57 rc=0, clamp 48/48 rc=0. Reduction production/REDUCTION.json
(route01_reduce.py over the PROP01 rules; frozen RULES.json).

## Technical disposition: PASS
- All units rc=0.
- dup_RT_s0 identical: digests, tree, series.
- V1/L1 identical to PROP01's runner; CPU == GPU for V1/L1/RT/RN.
- UNKNOWN parents: RT 15, RN 16, L1 9, V1 0 (conservative attribution).

## Preregistered verdict: ROUTING_NO_GAIN
route1's median reach (3 ever-divergent sites) is below reaim1's (5). The candidate-law disposition under the PROP01
rules is MULTIGENERATION_WEAK (4/16 seeds; 12/16 needed).

| law | MULTIGENERATION | UNCLAMPED | LOCAL_ONLY | median ever sites | median max gen | max gen / max sites / max radius (best seed) |
|---|---|---|---|---|---|---|
| RT route1 (arg0 := displaced & 3) | 4/16 | 1 | 11 | 3 | 1 | 3 / 21 / 7 |
| RN random-aim null | 5/16 | 1 | 10 | 5 | 1 | 6 / 25 / 5 |
| L1 reaim1 | 4/16 | 0 | 12 | 5 | 1 | 4 / 14 / 6 |
| V1 aeth01.v1 | 0/8 | 2 | 6 | 2 | 1 | 2 / 3 / 1 |

Clamp-verified chains (A alters B, altered B alters C, clamping B removes all of C), given as (seed: max gen, sites,
B's descendants):
- RT: s5 (3, 21, 3), s7 (2, 5, 1), s8 (2, 6, 1), s9 (3, 8, 4).
- RN: s0 (5, 10, 5), s1 (3, 11, 5), s11 (5, 19, 11), s13 (2, 9, 3), s8 (6, 25, 11).
- L1: s1 (2, 8, 3), s4 (3, 14, 5), s6 (4, 14, 4), s13 (2, 6, 1).
- In every case 0% of B's descendants re-diverge when B is clamped.

## Reading
- Coupling route choice to encountered content does NOT add causal reach. route1 is at or below deterministic re-aim
  on median reach. Its chains are as rare as reaim1's (4/16), and shallower than the random-aim null's (max gen 3
  vs 6; descendants per chain <= 4 vs <= 11).
- The content-free random-aim null does at least as well as content routing on every reach measure, so the order's
  "false friend" question resolves the other way: the content rule is not even as good as random aiming. A
  plausible mechanism (not tested): displaced bytes in a near-frozen, copy-homogenized medium have low-2-bit
  diversity, so content-keyed aim tends to re-pin writers rather than vary them.
- Across all three re-aiming laws, clamp-verified multi-generation chains occur in ~25-30% of seeds and stay small
  (<= 6 generations, <= 25 sites, radius <= 7 in 3000 ticks). The frozen law v1 shows none. Any re-aiming at all
  (deterministic, random, or content-keyed) is what makes rare short causal chains possible; how the aim is chosen
  does not move the rate.

## Limitations
- 512^2, warm-up 1000, horizon 3000, bit-0 payload impulses, P0, B_balanced, D50.
- The RN null uses uniform 2-bit aims. A null matched to the empirical distribution of displaced & 3 was not run.
- The UNKNOWN counts (15-16) mean some divergence in RT/RN was left unattributed. Chains through them are not
  credited.
