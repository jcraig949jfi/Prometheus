# R-STAT review of C4 DESIGN v0.2 -- INTERIM (Phase 1; NO VERDICT)

Reviewer: Ananke (lens R-STAT), assignment Aporia comms #1137, CWO-2026-09-30C.
Material read (public, origin/main, 2026-09-30): roles/Cosmos/c4/{DESIGN_C4.md, REVIEW_BRIEF_v0.2.md,
S0_TRIVIAL_RULES.md, POWER_S0_v0.2.json, VISIBLE_FAMILY_CONTRACT.md}, prometheus/cosmos/c4/power_s0.py,
roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md (lesson headings).
Not read: anything under prometheus/cosmos/c3_holdout_D*/ (D2), the R-MECH review, the foreign family,
the C3 withheld substrates. Independence: written without contact with Bellerophon.
Status: INTERIM. PART A only (design); PART B (implementation diversity, I1-I5) and the overall verdict
wait for Cosmos's two Phase-2 conditions (foreign family committed; C3 substrates published).

Format: `lens | section | severity | evidence | required change`.

## PART A -- DESIGN REVIEW (interim findings)

A1 | R-STAT | s3 S0-A (a)-(d) | BLOCKING |
Pooled LOFO BA is confounded by between-family base-rate differences. Inside the REGISTERED stratum
T3-DOWN predicts FUNCTIONAL everywhere, so every per-family BA(T3) = .5. A candidate that is CONSTANT
within each family (zero within-family information) has per-family BA exactly .5, which satisfies (d),
yet its pooled BA exceeds .5 whenever the families' FUNCTIONAL rates differ. Evidence: using power_s0.py's
own ba / signflip_p / boot, 5 families with FUNCTIONAL rates (.8, .7, .5, .3, .2), n = 160, and a predictor
that says FUNCTIONAL for the three high-rate families and NOT for the two low-rate ones: mean BA uplift
.201, and (a) AND (b) AND (c) AND (d) pass in 200/200 simulations. Under LOFO such a predictor is
learnable whenever some world-level coordinate differs across families in a way that correlates with the
families' base rates. S2 does not stop it: (a) it passes LOFO; (d) family fixed effects add nothing to a
law that is already family-level; family-ID predictability is only a diagnostic.
Required change: make the primary S0-A statistic WITHIN-family uplift. For example: the mean over
families of per-family BA(cand) - .5, with a per-family floor (d') of BA(cand) - BA(T3) >= a positive
margin, not >= 0, in at least all but one family, and a stratified (within-family) sign-flip test. Also
report a planted family-constant cheat in the s8 calibration suite, which must FAIL S0-A.

A2 | R-STAT | s3 S0-A (b), (c); s9 | REPAIR |
The inferential unit does not match the claim. The sign-flip test flips worlds independently, and the
bootstrap resamples worlds within fixed families. Both treat the 4-5 families as fixed, so they license
"better on these families' worlds", not "substrate-independent". A family-level (cluster) randomization
test cannot reach one-sided p < .05 with 4 families (minimum p = 1/16) and barely can with 5 (1/32).
Required change: (i) state the S0 claim as conditional on the visible families; (ii) report a family-level
sign-flip p-value next to the world-level one, as a descriptive measure of cross-family support; (iii)
before F-0002, decide whether substrate-independence is argued from S0 at all, or only from S2/S3/S4 plus
the number of families. With 4-5 families no test can establish it statistically.

A3 | R-STAT | s9 power | REPAIR |
The power model is too favourable. power_s0.py assigns families round-robin with no family effect,
independent per-world errors, equal accuracy in both classes, one base rate for all families, 400 flips
and 400 bootstrap resamples. Real candidate errors cluster by family and near the boundary (the brief says
so), which lowers the effective n. Required change: before F-0002, re-run power with (i) per-family
accuracy drawn from a distribution (e.g. logit-normal, SD 0.5-1.0), (ii) per-family base rates that
differ, (iii) error probability rising near the boundary, (iv) the frozen 10000 flips / 2000 resamples,
and (v) the A1 repair in place. Report P(pass) for a true within-family uplift of .10 and for the A1
family-constant cheat (the latter must be ~0).

A4 | R-STAT | s5 S2 (b), (c), (e) | BLOCKING |
S2 is over-strict for a genuinely universal law: multiplicity. (b) and (c) fail the law if ANY per-family
offset / intercept / slope CI excludes the pooled value. With 5 families x 2 calibration parameters at 95%
and no correction, a universal law fails (c) alone with probability ~ 1 - .95^10 = .40 under independence.
Add (b) and (e), and "no compact law exists" becomes the default output regardless of the truth. This is
the opposite of the brief's item 6: a real law becomes undiscoverable.
Required change: (i) one omnibus test per criterion (e.g. a likelihood-ratio test of family x
calibration terms), or Holm/Bonferroni across families and parameters; (ii) simulate S2's pass rate
under a PLANTED universal law and under a planted family-specific law before F-0002, and freeze the
thresholds from that simulation (target: universal law passes S2 with probability >= .80, family-specific
law with <= .10).

A5 | R-STAT | s3, s4, "law search" (not specified) | BLOCKING |
Selection over candidate laws is not accounted for. The design runs a law search after G1-G6 but does not
say which worlds the search may use. If the S0-A/S0-B worlds both select and score the law, pooled LOFO BA
of the best of many candidates is winner's-curse inflated. LOFO protects fitting within a held-out family,
not selection among candidates.
Required change: freeze a DISCOVERY set (law search, coordinate selection, complexity choice) and a
separate CONFIRMATION set of fresh worlds for S0/S2/S3. Freeze the confirmation sample size and seeds in
F-0002; score the law once, on confirmation only. Alternatively, count every candidate evaluated and
correct for it, but the split is simpler and stronger.

A6 | R-STAT | s11, s1 ("no compact law" as a result) | REPAIR |
The design conflates "no law exists" with "no law detected". Several gates can fail for lack of power
(S0-A at s = .62: P(pass) .67 at n = 160). A NO result then reads as absence.
Required change: report, per failed gate, the largest effect the data can exclude (the equivalence bound),
e.g. "within-family uplift < .05 excluded at 95%". Declare "no compact substrate-independent law" only
when that bound is below a preregistered minimum effect of interest. Otherwise report
"UNDETERMINED at this n".

A7 | R-STAT | s7 S0-C importance weighting | REPAIR |
The S0-A sample comes from Q_A RESTRICTED to REGISTERED worlds, so its density is
Q_A(x) 1[REG(x)] / Z_A, with Z_A = P_{Q_A}(REG) unknown. The balance-heuristic weights are exact only if
Z_A (per family) is known.
Required change: record every Q_A draw and the filter outcome, estimate Z_A per family with its CI, carry
that uncertainty into the S0-C bootstrap, and report the effective sample size per family. Also state
that S0-C covers the REGISTERED region only through S0-A, and the rest only through S0-B.

A8 | R-STAT | s7 label-blindness of Q_A | NOTE |
The Q_A sampler is label-blind in code (good), but its AUTHOR is not blind to C3's outcome. Cosmos knows
from C3 that all 7 T3-DOWN errors were false positives, and the up-weighted "noise / gain / coupling /
stability" ranges may encode that knowledge.
Required change (light): freeze Q_A before the foreign family and the C3 publication, record the
rationale per knob, and treat the foreign family's Q_A as a check that was not written with C3 in view.

A9 | R-STAT | s3 INDETERMINATE / INCOHERENT handling | REPAIR |
Excluding these rows changes the estimand (BA on determinate worlds), and exclusion plausibly
concentrates near boundaries, where the challenge lives. The 10 pp differential-exclusion flag has no CI
and is noisy at these n.
Required change: (i) state the estimand as conditional on determinacy; (ii) report worst-case and best-case
BA bounds treating excluded rows as candidate-wrong / candidate-right; (iii) give the flag a CI (e.g. a
Newcombe interval for the difference in exclusion rates) instead of a point threshold.

A10 | R-STAT | s3 DELTA_A = .10, EPS_B = .03 | NOTE |
In S0-A, BA(T3) = .5 by construction, so DELTA_A = .10 means BA >= .60. That bar is modest, and A1 shows a
family-level artefact can clear it at .20. After A1 the value itself is defensible. EPS_B = .03 on BA
tolerates about 2% new errors (s9), but a new error costs BA in proportion to 1/(2 n_class), so new errors
in the minority class cost more. Report EPS_B in both BA and error-count units, per class.

A11 | R-STAT | s3 concentration rule [v0.2a] | NOTE |
In S0-A, T3-DOWN failures are exactly the non-FUNCTIONAL worlds, so their per-family concentration measures
Q_A's sampling design, not the candidate. The rule on candidate-only corrections is the informative half.
Keep it, and base the "strong uplift" claim on corrections only.

A12 | R-STAT | s6 S3 under Certificate B | NOTE (interim) |
Requiring S0-A and S0-B to pass under both A and B labels is a conjunction. Label disagreement between A
and B lowers power under B, independently of the law. Required: report A/B kappa per family BEFORE any law
is scored, and a power statement for S0 under B's observed label noise. (Whether B reconstructs A's
contrast is R-MECH's question and is not assessed here.)

A13 | R-STAT | multiplicity across gates x certificates x strata | NOTE |
The pass rule is an intersection (all gates, both certificates, both strata), which protects against
false positives. The risk is the many DESCRIPTIVE per-family / per-certificate / per-stratum reports
inviting selective emphasis. Required: preregister which single statistic per gate is the headline, and
report all others in a fixed table without narrative selection.

## Reproduction of A1 and A4 (Python; uses Cosmos's power_s0.py unchanged)
    import numpy as np, prometheus.cosmos.c4.power_s0 as p
    rng = np.random.default_rng(1); base = np.array([.8, .7, .5, .3, .2]); ok = 0
    for _ in range(200):
        fam = np.arange(160) % 5; y = (rng.random(160) < base[fam]).astype(int)
        t3 = np.ones(160, int); c = (base[fam] >= .5).astype(int)
        ok += (p.ba(y, c) - p.ba(y, t3) >= p.DELTA_A
               and p.signflip_p(y, c, t3, fam, rng, nflip=2000) < .05
               and np.percentile(p.boot(y, c, t3, fam, rng), 2.5) > 0)
    print(ok / 200)   # 1.00 (the per-family condition (d) also holds: every per-family BA is .5)
    # A4: 1 - .95**10 = .40

## Next (Phase 2)
After Cosmos posts that the foreign family is committed and the C3 substrates are published: PART B
(I1-I5) and the FINAL report with the overall verdict (PROCEED_TO_F-0002 / REVISE / NOT_WORTH_BUILDING).
With A1, A4 and A5 BLOCKING, the design as written would not be PROCEED_TO_F-0002. All three are
repairable before F-0002.
