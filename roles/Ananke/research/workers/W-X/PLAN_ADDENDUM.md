# W-X PLAN_ADDENDUM (POST-FREEZE). Plan = roles/Ananke/research/plans/T-SWAP-REL5_PLAN.md, frozen at 22b9bbd51
# (2026-09-30T10:34:50Z). Written 2026-09-30 ~10:40Z BEFORE any REL5 simulation (validation or grid).
# These are implementation readings of under-specified plan text. No candidate, threshold, model family or grid
# value is changed.

D1 (DEGEN model, exact reading of s2). Per dataset, per pair, independently: with prob d the pair is
   DETERMINISTIC, else it follows W-Q swap_rel2.simulate("realistic", p, z, P, K) unchanged.
   Deterministic pair: normal arm all-correct, a = 1 (K/K). Swap arm constant across its K trials, so s in {0, 1},
   drawn with the realistic model's own coupling at the pair's accuracy 1: with t,u = (-z,0) if z<0 else (0,z),
   r ~ U(0,1): r < t -> flip (s = 1-a = 0); r < t+u -> same (s = a = 1); else the "fresh" swap arm is a constant
   fair coin (s = 0 or 1, 1/2 each) instead of Bin(K,.5)/K.
   Then E[s] = .5 + z(1 - .5) for a deterministic pair and E[s] = .5 + z(p - .5) for a realistic pair, so every
   pair type has E[DF] = (p_pair - .5)(z + .5) = 0 at z = -1/2 and E[DN] = (p_pair - .5)(z - .5) = 0 at z = +1/2:
   the truth is EXACTLY at the verdict boundary, for every d, as s2 requires. "normal p" in s2 is the accuracy
   of the non-deterministic (realistic) pairs (an overall-accuracy reading is infeasible: d=.95 with overall
   p=.90 would need negative accuracy on the rest).
   Rejected reading (recorded, not run): "swap arm constant" = one common value c for all deterministic pairs.
   With a = 1 that gives DF = c - .25, which is 0 only for c = .25, not a multiple of 1/K for K in {3, 11}; any
   other c puts the deterministic block off the boundary, and the realistic block (DF in [-.75,.75]) cannot
   rebalance the mean to 0 for d >= .75. So that reading cannot place the truth at the boundary and is not s2.
D2 (FC per point). As W-U/W-W: FLIP FC = P(FLIP_REL | z=-1/2), NO_EFFECT FC = P(NO_EFFECT_REL | z=+1/2),
   CHANCE FC = max over the two truths of P(CHANCE_REL). Pooled over stage 1 (+ stage 2). Wilson 99% CI.
D3 (stage 2). +60,000 datasets at a point (both truths) iff any H2 verdict FC in (0.8%, 1.2%] after stage 1
   (H2 only, as s2 says). Seeds: rng = default_rng([0x660, stage, P, K, round(d*1000), round(p*1000),
   round(z*1000)+5000]); stage 0 = the degeneracy validation draw (separate data), 1, 2 = FC grid.
D4 (candidates). H0 = W-W intervals4 H0 (= W-U BOOTT, REL3). H2 = intervals4 _tq(..., floor=sd_floor(P,K))
   unchanged. ZW = H0 with t*_b := 0 wherever sd*_b <= 1e-9 (REL3's own degeneracy test) instead of
   sign(d)*inf; the original-sample sd = 0 case keeps REL3's point interval [m, m] (zero width). Same B=2000
   seed-0 resample counts (W-Q boot_counts). Verdict precedence FLIP > NO_EFFECT > CHANCE as REL3.
D5 (degeneracy validation, required before the grid). At each of the 36 points, n = 2000 datasets (stage-0 seed)
   per truth: report (i) mean share of resamples with sd*_b <= 1e-9 for the statistic that decides the verdict
   at that truth (DF at z=-1/2, DN at z=+1/2), (ii) share of datasets with at least one such resample,
   (iii) share of datasets with >= 0.5% (= the 99% two-sided tail) such resamples (the level at which infinite
   t* can move a quantile), (iv) share of datasets where the H2 or ZW interval differs from H0. The same
   counters are also accumulated during the FC grid. If (iii) is ~0 everywhere, the model does not probe the
   degenerate region; per s4 the check is then expected to be uninformative, and the model is NOT tuned; the
   frozen s4 rule (ZW must fail) still decides.
D6 (s4 sanity "H0 FC <= H2 FC at every point") is evaluated on counts from the same data, per verdict.
