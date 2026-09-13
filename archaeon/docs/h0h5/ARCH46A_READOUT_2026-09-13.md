# ARCH-46A -- EXACT MEANS EXACT: readout (2026-09-13)

Order: `roles/Archaeon/prompts/2026-09-12_seasons/ARCH46A_ORDER.md` (sha256 0023bbef...a3bf). Preregistration
`ARCH46A_PREREG_2026-09-13.json` (sha256 36b470d2...d80f, commit 30e5fc1b9, before the rerun; bars, seeds, worlds, gate,
verdict rule identical to S7_PREREG). Candidate GATED_V2W, CANDIDATE_VERSION 6680e382d679d169 (S7: 39093752300ebb85; the only
source change is `s6_endgame.v2w_num`). Rows: `S7_RESULTS_{ELIGIBLE_L8,ELIGIBLE_L9,UNIVERSE,L10}_ARCH46A_2026-09-13.json`;
deltas `ARCH46A_DELTA_2026-09-13.json`; verdict `S7_VERDICT_ARCH46A_2026-09-13.json` from the unchanged `S7_VERDICT` script.

## S7 preserved
GATE_FAILS_TO_ISOLATE (fd5248805) stands; S7's rows are untouched and this rerun wrote under its own tag.

## The one change
v2w = Fraction(sum_e n_e * min_q' sum n'^2, N): every term is an integer over the common denominator N, so mathematically
equal partition values compare equal and fall through to G's existing lexicographic rule; unequal values keep their real
order. Tests (`test_arch46a_exact_v2w.py`): the S7 falsifier's five {6,4,2} probes are exactly 25/3 (the float form gave two
values) and the refinement now returns G's probe; over 300 real endgame states every pair of probes with the same multiset of
(cell size, best next-step numerator) is exactly equal (> 500 tie groups; the float form split some); over > 10,000 probe pairs
the float form separated beyond rounding, the exact order is identical; gated identity unchanged. Recorded before the rerun:
under exact arithmetic the seventh S6 canary root (L9_prod2_a4_b5_uA2_uB1) is an exact five-way tie (697/15) -- its S6/S7
difference from G was itself a float split; the other six remain true v2w preferences the gate suppresses.

## Exact deltas from S7 (per state / per world; every change attributed)
* The sole S7 regression (L 8, evs:914ee3e416304d0d, N 12): GONE -- cost 2.6667 -> 2.5833 = G = V*. Attribution: float tie split
  at step 1 (exact choice 00011101 = G's; float choice 01010111).
* L 8: improved 27 -> 27 (all 27 S7 improvements survive), unchanged 230 -> 231, worsened 1 -> 0; recovery 0.405 -> 0.405;
  aggregate -2.1 % (81 -> 82 probes). No other state changed.
* L 9: improved 49 -> 46, unchanged 161 -> 164, worsened 0 -> 0; recovery 0.700 -> 0.687; aggregate -4.1 % (140 -> 135 probes).
  The three states that changed (evs:95a49d9bcec12636 N 12; evs:5ee44e1de7190b85, evs:70ab99f968e3dbc5 N 14) were S7
  IMPROVEMENTS produced by a float split that happened to pick a better member than G's lexicographic rule; under exact ties
  the candidate falls to G's rule and equals G there (better -> same). All three attributed to float_tie_split at step 1.
  No new regression. 46 of 49 S7 improvements survive; the three that do not were float luck, not repair.
* Universe (233 roots): worsened 1 -> 0 (the +1/35 world L8_prod2_a1_b7_uA0_uB3 was a float split at step 2, N 12; now = G),
  improved 49 -> 50, aggregate -2.00 % -> -2.04 % (205 -> 209 probes). Five worlds changed cost, all attributed to float tie
  splits at in-gate decisions (N 12/14): three stay better, one same -> better, one worse -> same. Root decisions changed at 9
  worlds (all in-gate roots N 6/7 with exact ties now resolved by G's rule); none affects the canaries.
* Seven N 30 canaries: root decision = G at all seven, census cost = G at all seven (3.1000 x6, 3.2667); pass.
* L 10 (never run before S7): identical to S7 to the last decision -- 0 worsened, 17 improved, -1.4 % (53 probes), recovery
  0.683 on 36 gap worlds, 871 decisions (176 in / 695 out), 0 identity violations. No float tie was decisive at L 10.
* Outside-gate identity: 0 violations over 1374 + 1125 + 2092 + 871 = 5462 audited candidate decisions.
* Work: L 8 median 1934 -> 1937 units (ratio 3.8), L 9 3535 -> 3477 (8.3), universe 589 -> 571, L 10 631 -> 630; maxima
  unchanged (18,743 / 51,421 at L 10); invocation 53 / 51 / 40 / 38 %; total incremental units within 0.2 % of S7.
  Fraction arithmetic changed nothing material.
* Decision changes not attributable to a float ordering: NONE (every changed state/world carries `float_tie_split`).

## Verdict under the frozen rule (identical to S7's): LICENSED_ENDGAME_REPAIR
Instrument invariants pass (0 identity violations, no arm below V*, census = solver, permutations). Canaries pass. Inside-gate
EXACT non-regression: 0 worsened on L 8 and L 9. Full-universe bar: 0 worlds worsened (any amount), aggregate -2.0 %. L 10 bar:
0 worsened, -1.4 %. Improvement: L 9 recovery 0.687 >= 0.33, aggregate 4.1 % >= 1 %. Work: median <= 25 k, ratio 8.3 <= 10,
max <= 100 k.

## Ruling on ARCH-46A
PASSED: the N-gated composition passes every original S7 bar when the refinement's implementation matches its intended exact
semantics. The S7 failure was a representation defect and nothing else: with equal values tied, the only losses were three
float-lucky L 9 improvements (recovery 0.700 -> 0.687), and no regression remains anywhere in 233 + 110 root worlds and 468
endgame states.

## Production
NOT integrated (the order forbids it here). A separate return follows with the evidence for a production-canary decision.
ARCH-46(b) (near-tie / deep-search frontier) stays parked. W and M untouched.
