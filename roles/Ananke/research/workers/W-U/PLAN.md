# W-U PLAN (E-ANANKE-W-U, T-SWAP-REL3, successor of T-SWAP-REL2 thr-5df816e9b844, MWO-0004)

FROZEN 2026-09-29 ~15:15Z, BEFORE any candidate interval is simulated under any dependence model.
Nothing below changes after results; any later analysis is labelled POST HOC in LOG.md.
Envelope: <= 16 CPU core-hours, <= 2.5 h wall, CPU only, <= 8 threads under a Fabric skullport:cpu8 lease.

## s1 Question
Which interval, replacing REL2's 99% percentile pair bootstrap on DF=(s-.5)+(a-.5)/2 and DN=(s-.5)-(a-.5)/2,
holds a 1% false-certificate (FC) target at P in {8,16,32,64,128,256}, K in {3,11,12}, under W-Q's WORST,
REALISTIC and out-of-model HETERO (Beta conc 4) pair models? If none does at tiny P, what minimum-P floor?

## s2 Target (per verdict, at its boundary truth, every design point)
FC_V(P,K,model,p) = Pr(certificate V issued | V's boundary truth) <= 1.00%, where
- FLIP_REL boundary z=-1/2; NO_EFFECT_REL z=+1/2; CHANCE_REL max over z=+-1/2; at p=.50 truth z=0 for all three;
- p in W-Q FC_GRID {.50,.51,.52,.55,.58,.60,.65,.70,.80,.90,.95,.99};
- models: worst, realistic, hetero (W-Q swap_rel2.simulate imported unchanged, conc=4);
- design points: 6 P x 3 K = 18; bootstrap counts = W-Q boot_counts(P) (B=2000, seed 0) for every bootstrap candidate.
Simulation sizes: stage 1 n=20000 per truth point (seed [11, P, K, p, z, model]); a truth point gets a stage-2
top-up of n=60000 more (independent seed [12, ...]) if ANY candidate/verdict at it has a stage-1 estimate in
(0.80%, 1.20%]. The decision uses the pooled estimate: PASS iff pooled FC <= 1.00%. Every FC is reported
with a Wilson 99% CI; "ROBUST" = Wilson 99% upper bound <= 1%.
A candidate MEETS THE TARGET at a design point (P,K) iff PASS at all p, all 3 models, all 3 verdicts there.

## s3 Candidates (all two-sided 99%, i.e. 0.5% per tail, applied to DF and DN separately; REL2 precedence
FLIP > NO_EFFECT > CHANCE; degenerate sd=0 samples give the point interval [m,m])
- PCT   percentile pair bootstrap (REL2, the reference).
- BCA   bias-corrected accelerated, same resamples; z0 from Pr*(theta* < theta_hat) (+ half ties, clipped to
        [1/2B, 1-1/2B]); a = sum d^3 / (6 (sum d^2)^1.5), d = x_i - mean (jackknife of the mean).
- BOOTT studentized pair bootstrap: t* = (m* - m)/(sd*/sqrt P) (sd ddof 1; sd*=0 -> t*=+-inf),
        interval [m - t*_{.995} se, m - t*_{.005} se], se = sd/sqrt P.
- TINT  t-interval on pair statistics: m +- t_{P-1,.995} sd/sqrt P.
- XPCT  P-dependent level (expanded percentile, Hesterberg): percentile at tail
        alpha'/2 = Phi(-sqrt(P/(P-1)) t_{P-1,.995}).
Control (never selectable): T90 = t-interval at 90% (MUST FAIL everywhere).
Simplicity order for ties: TINT < XPCT < PCT < BCA < BOOTT.

## s4 Minimum-P floor and selection rule
P_floor(c) = smallest P in the grid such that c MEETS THE TARGET at every design point with P' >= P (all K).
(If c fails at P=256, P_floor = none and c is not selectable.)
SELECTION (lexicographic): 1) lowest P_floor; 2) highest power at P=64 K=11 (s5) - requires P_floor <= 64;
3) ties = power within 1.0 percentage point -> simplest. If every candidate meets the target everywhere
(P_floor = 8), step 1 is a tie and this is exactly the brief's rule. Below P_floor: NOT_ELIGIBLE for every verdict.
For a P not in the grid: eligible iff P >= P_floor; tables are computed on demand for (P,K) (as REL2 design()).

## s5 Power
Selection power = mean over {FLIP z=-1, NO_EFFECT z=+1, CHANCE z=0} x {worst, realistic} x p in {.60,.65,.70,.75}
of Pr(true verdict issued), P=64 K=11, n=4000 per point (seed [21,...]). Reported for all candidates.
REACH tables for the winner only: p_min_V (smallest p with power_V >= .80 at all p' >= p on W-Q POW_GRID,
max over worst/realistic), n=1000 per point, at the 18 grid designs.

## s6 The REL3 rule (structure of REL2 kept; only the interval, the tables and the floor change)
certificate by the selected interval; identification guard lo99(normal) > .50 with the selected interval on the
pair means a; CERT_OK_V = P >= P_floor and FC_V max <= 1% at the design (from the s2 table; on-demand simulation
for unlisted designs); REACH_V = lo99(normal) >= p_min_V; ATTAIN_V = guard & CERT_OK_V & REACH_V.
LABEL: certificate V -> V if CERT_OK_V else NOT_ELIGIBLE; none -> INDETERMINATE if any ATTAIN_V else
NOT_ELIGIBLE; NE list carried. STRICT sensitivity: certificate also needs REACH_V.
Beside every FLIP_REL: z = (s-.5)/(a-.5) with a paired 99% delta-method CI (pair covariance, t_{P-1} quantile):
COMPLETE if the CI contains -1, PARTIAL if lo > -1, OVERSHOOT if hi < -1.

## s7 Re-application to W-O's 733 (saved data only; no pair arrays exist - LOG A0)
From n512/s512 [mean, lo, hi] (3-dec, P=256): sigma = (hi-lo)/(2*2.5758) per arm; DF/DN SE depend on the
unknown pair correlation rho: var = sig_s^2 + sig_a^2/4 +- rho sig_s sig_a. Protocol: rho grid of 41 values in
[-1,1] x halfwidth multiplier {0.9,1.0,1.1} (B=2000 endpoint noise + rounding). Keep the (rho, mult) combos whose
normal-approx PCT certificate equals the recorded REL2/W-N certificate (`rel`); if none, INCONSISTENT. The new
certificate is DETERMINED if it is identical over all kept combos, else AMBIGUOUS (reported, and REL3 label
computed both ways). REL3 labels then use the winner's tables at P256 K11/K12. Report the transition table
REL2 -> REL3, the z class of every FLIP_REL (determined only if identical over rho in [-1,1]), and counts by
specimen x source x offset group.

## s8 Known-answer checks and must-fail inputs
KA1 engine plants rep 1 (W-Q out/plants_r1_*.npz, P=256) with truths as W-Q (FIXED_Z; S1_half/S1_3q from the
    q=0 realized fraction): PASS iff 0 false certificates and issued >= 80% of exact-truth (|z - {-1,0,1}| <= .05)
    cells whose true verdict is attainable.
KA2 the same arrays cut into disjoint pair blocks at P in {32, 64, 128} (256/P blocks each): false certificates
    <= 1% of block-cells (truths are not at a boundary, expected ~0); recovery reported.
KA3 W-N rep 0 noiseless P1S arrays (W-N out/p1s_noiseless_r0.npz) with W-N's post-hoc readout_noise, mode flip,
    arm-shared mask, q in {0,.1,.2,.3,.4} (seed 5): same criteria as KA1.
Must-fail: M1 PCT fails the s2 target at P=32 in my simulation. M2 T90 fails at every one of the 18 design points.
M3 KA1 with FLIP/NO_EFFECT truth labels swapped must show false certificates. M4 floor disabled: the failing
design point(s) below P_floor are shown (if P_floor = 8, M4 is vacuous and says so).

## s9 Predictions (made before simulating)
Pr1 PCT fails at P <= 64 (known from W-Q), TINT and XPCT pass at P >= 32 on worst/realistic; hetero is the hardest.
Pr2 No candidate passes at P=8 under the realistic model with K=3 (discrete pair means) -> a floor of 16 or 32.
Pr3 BOOTT is the most conservative (lowest FC, lowest power); TINT/XPCT ~ equal power, so TINT wins on simplicity.
Pr4 At P=256 the 733 transitions are few (< 10 certificate changes), all AMBIGUOUS or boundary rows.
