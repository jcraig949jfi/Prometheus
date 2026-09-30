# H-CHK PLAN ADDENDUM (post-freeze; written 2026-09-30 BEFORE any gate, C1, C2 or C3 run)

Frozen plan: roles/Ananke/research/plans/H-CHK_PLAN.md at commit 7e156c12b (not edited).
Everything below is post-freeze. It fills in implementation details that the frozen text leaves
open, and adds stricter gates. No threshold in C1-C3 is changed. The only run before this file
was a 100-tick engine timing smoke test (no swap, no classifier; LOG A1).

## X1 Known-answer gate: what exactly is checked (plan s "Known-answer gate")
- G1 (frozen gate). hold_latch and echo_hold through W-P's pipeline (tt.run_table + ana.analyse/summarize),
  with W-P's own KA design (run_ka.py): HOLD gap 8 cue 2 trials 8, seeds world_seeds(0x611, 64), offsets 3..8,
  trials 1..7, coarse components, half cube. Published answers (W-P REPORT): hold_latch fS 1.00, 0 N trials,
  UNDEFINED; echo_hold fC 1.00, UNDEFINED. PASS iff at every offset: latch fS == 1.00, base_N == 0,
  class UNDEFINED; echo fC == 1.00, base_N == 0, class UNDEFINED. Plus the C1 bit-identity check vs lens_swap
  (tt.check_vs_lens) returns all True for both.
- hold_latch / echo_hold cannot go through W-V's classifier (it needs a 5-sensor MAJ readout). So I add,
  stricter than the plan:
  - G2. W-V's PMAJ and PDICT re-run by me at W-V's design (M 128, ns 0x650, trials 1..11) at offsets
    2,4,6,12 must reproduce W-V's ka.py criteria KA-MAJ, KA-DICT, MF1, MF2, MF4 (MF3, the permuted-vote
    control, is re-computed on my PMAJ run). This PMAJ run is also C2's lossless baseline.
  - G3. W-N's z pipeline: P1S (noiseless, plants_rel physics) mirror S-swap at k*Pd-1 must read FLIP_REL with
    z <= -.95 (W-N: 35/35 PASS). This is also C3's first cell.
- If any of G1-G3 fails: STOP before any champion/plant run of C1-C3 and report.

## X2 C1 plant, concrete definition
- Env: 4781b0a1's MAJ env (d 3, delta 16, cue_len 2, 12 trials, flip_p .3, n_maj 5).
- Physics: plants_wv.physics(4781b0a1) (W-V plant physics) with dest_mode 'sample', loss .1, lat_jitter 1 set
  to the champion's values. fanout is already 8; the ring r3 gives 6 ports; w is uniform (16) and
  plastic_route 0, so sampling is uniform over the 6 ports. Latencies stay at W-V's lat_base 5 / lat_hop 2
  (the plan lists loss, sampling, sync period 2 and jitter only; cap stays 0 as W-V).
  A champion-latency variant (lat_base 1, lat_hop 1, cap 2 saturate) is NOT run unless budget remains after
  C1-C3; if run it is labelled SENSITIVITY and cannot change the frozen reading.
- Program (all sites run it; only sensors ever sense):
  - cue tick (|SENSE| = 256, awake): S1 := 256 if SENSE > 0 else 0 (rectified latch; held otherwise);
  - every wake: EMIT := S1, PAY1 := S1, PAY0 := 0 (a positively latched sensor re-emits every wake);
  - every wake: S0 := IN0_1 - theta (readout = sum of payload-1 arrivals in its last wake window minus theta).
- theta: grid 256*j - 128, j = 1..40 (midpoints, so S0 is never 0 and the count threshold is "count >= j").
  theta = the smallest grid value with plant accuracy >= .70 on world_seeds(0xC4C1, 512) (disjoint from the
  test namespaces 0x610 and 0x650), all scored trials. If no j reaches .70: use the accuracy-maximising j and
  flag C1 as run below the bar (still reported).
- Test designs = the workers' champion designs:
  - W-P: tt.run_table, coarse components, half cube, world_seeds(0x610, 256), trials {1,2,5,6,9,10},
    offsets 1..15, ana.analyse/summarize, parity split exactly as W-P analyze.py (parity of k*Pd + o).
  - W-V: wv.run, world_seeds(0x650, 128), trials 1..11, offsets 2,4,...,14, ana.stratum/classify/verdict.
    (W-V's ana.summarize writes into W-V/out, so I call stratum/classify/verdict directly; same code.)
- Operational frozen reading:
  - (i) "AND/OR-dominated N in one clock phase": at least one (offset, parity) stratum with base_N >= 20 whose
    W-P frozen class is JOINT-2(.) (top 2-set AND/OR share >= .60 with lo99 >= .45).
  - (ii) "DISTRIBUTED-NONMAJ (D_piv < .3)": W-V verdict (q0/q1 informative strata, all offsets) is
    DISTRIBUTED-NONMAJ AND the median point D_piv over the informative strata is < .3.
  - DOES NOT REDUCE: W-V verdict MAJORITY, or median D_piv > .7, or no N (no (offset, parity) stratum with
    base_N >= 20).
  - REDUCES iff (i) and (ii); otherwise PARTIAL.

## X3 C2 concrete
- PMAJ genome unchanged; physics = plants_wv.physics(4781b0a1) with dest_mode 'sample', loss .1 (everything else
  as W-V, including jitter 0 and cap 0). Design = W-V's pmaj run: M 128, ns 0x650, trials 1..11,
  offsets 2,4,6,8,12.
- Reading applied to the informative (E >= .5) q0/q1 strata at W-V's KA offsets 2,4,6 (W-V's own KA scope):
  ROBUST iff the W-V verdict there is MAJORITY and every such stratum has D_piv > .7;
  WEAKENED-CONFIRMED iff every such stratum has D_piv < .3; otherwise PARTIAL. If none is informative,
  PARTIAL (undefined), reported as such. Offsets 8 and 12 are reported descriptively.

## X4 C3 concrete
- "cue k" in the plan = the cue the scored trial's answer depends on, c_{k_s - n}, which is the cue a lag-n store
  holds at the swap tick k_s*Pd - 1. The literal reading (the not-yet-presented cue of the scored trial k_s)
  is degenerate: the twins would then share the answer of trial k_s, so z is undefined and the frozen
  "P1S reads z <= -.95 under both" could never hold; the must-fail ("cue k-1 instead of k") also only makes
  sense with k = the held cue.
- Twins exactly as lens.cue_arrival_profile / lens_swap.twin_profile: world 2i+1 := world 2i (the lead-sign
  world) with only the target trial's cue window negated; same world seed; y_B = -y_A for the scored trial.
  One episode per scored trial k_s; only k_s is scored in it (SINGLE).
- Swap = W-N plants_rel.make_fn('S') (whole S array, all sites) after tick k_s*Pd - 1 (W-N 'back0'),
  run with plants_rel.run_fork (ep passed in).
- Specimens / physics / seeds: P1S = plants_rel.body('P1S', plants_rel.physics()) noiseless; n1_s0, n2_s2 =
  W-L out/search_<tag>.json champions at nb.m2() physics. Seeds world_seeds(H_int(NS_WN, 0x4E), 512) (W-N's
  specimen seeds), trials n..11, M 512 (P 256).
- z = (s - .5)/(a - .5), a and s = means over pairs of pair-mean scores (W-N pair_means, same scored
  world-trials); CI = 99% percentile pair bootstrap of the ratio over W-N's resample indices
  (_boot_idx(P, 2000, seed 0)). W-N's swap_verdict_rel verdict is reported alongside.
- "read similarly under both modes" := |z_a - z_b| < .5 for each integrator. CONFUSION CONFIRMED / NOT CONFIRMED
  as frozen; anything else PARTIAL.
- Must-fail: P1S, twin differing at c_{k_s - n - 1} (one cue earlier than the held one), same swap; must NOT read
  z <= -.95. Twins then share y; z is computed the same way.

## X5 Pre-run prediction (mine, recorded before C3 runs; not a threshold)
With single-cue twins the input after the swap tick is identical in A and B. If S holds all of the between-twin
state difference at the swap tick, the S swap puts world A exactly on world B's trajectory, so s = 1 - a pair by
pair and z = -1 whatever the mechanism (integrator or lag-n store). The lag weight changes how many twin pairs
differ at all (it moves a toward .5), not z. So I expect the integrators to read z ~ -1 under (b), i.e.
NOT CONFIRMED, and H-SCI's "|z| ~ lag weight" prediction to fail. The mirror-vs-twin contrast can only show
confusion through state OUTSIDE S or through the post-swap input, and the frozen (b) removes the latter.

## X6 Compute
No lease: at most 2 python processes x 1 thread (OMP/MKL 1, torch.set_num_threads(1)), CPU only,
CUDA_VISIBLE_DEVICES=-1, device="cpu" passed explicitly.
