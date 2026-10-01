# W-Q PLAN (E-ANANKE-W-Q, T-SWAP-REL2, MWO-0002; MWO-0001 rules carried)

Frozen 2026-09-29 ~11:35Z, BEFORE any per-verdict row of W-O's rerun_table
(in particular the 42 cases) is read, and before any simulation or engine run
(LOG A0 declares the aggregate counts I saw).

## 1 Question
Replace W-N's single worst-case eligibility gate (NOT_ELIGIBLE for everything if
lo99(normal) < p_min(P,K), p_min = the normal at which ALL THREE verdicts have
>= 80% power) by PER-VERDICT attainability, and re-read W-O's 733 verdicts.

## 2 The frozen rule (swap_rel2.py)
Unit = mirror pair. a_i, s_i = normal and swap accuracy of pair i over the same
scored world-trials. P = pairs, K = scored trials per world (W-N convention:
cells / (2P)).

2.1 CERTIFICATE (unchanged from W-N, copied): DF = (s-.5)+(a-.5)/2,
DN = (s-.5)-(a-.5)/2, 99% percentile pair bootstrap, 2000 resamples, seed 0,
pairs resampled jointly.
  FLIP_REL hi(DF)<0; NO_EFFECT_REL lo(DN)>0; CHANCE_REL lo(DF)>0 and hi(DN)<0;
  else no certificate (INDETERMINATE). Truth regions: FLIP z<-1/2, CHANCE
  |z|<1/2, NO_EFFECT z>1/2, z = (s-.5)/(a-.5).

2.2 IDENTIFICATION GUARD (definitional, not an error-rate gate): if
lo99(normal) <= .50 the three hypotheses may coincide (g = 0 means s = .5 is
FLIP, CHANCE and NO_EFFECT at once), so every verdict is NOT_ELIGIBLE.

2.3 ERROR TARGETS, per verdict V in {FLIP_REL, NO_EFFECT_REL, CHANCE_REL}:
  (T1) false-certificate rate FC_V <= 1%: the probability that the rule issues V
       when the truth sits on the nearest boundary of V's region (z = -1/2 for
       FLIP; z = +1/2 for NO_EFFECT; the max over z = -1/2 and z = +1/2 for
       CHANCE), at every normal p on the FC grid {.50,.51,.52,.55,.58,.60,.65,
       .70,.80,.90,.95,.99} (p=.50: z-free truth s=.5), n_sim = 4000,
       under BOTH dependence models below.  CERT_OK_V(P,K) := T1 holds.
  (T2) power >= 80% when V is exactly true (FLIP z=-1, CHANCE z=0, NO_EFFECT
       z=+1).  p_min_V(P,K,model) = smallest p on the grid .50:.01:1.00 such
       that power_V(p') >= .80 for all grid p' >= p (n_sim = 400).
       REACH_V := lo99(normal) >= max over the two models of p_min_V.
Dependence models (pair-level; mirror partners identical, the engine's case,
since both partners share the world seed):
  WORST (W-N's): a_i ~ Bin(K,p)/K; s_i ~ Bin(K, .5 + z(p-.5))/K INDEPENDENT of
       a_i (pairing buys nothing).
  REALISTIC (coupled mixture): normal cells x_ik ~ Bern(p) iid; each pair is,
       independently, TRANSFERRED (swap cells = 1-x) w.p. t, UNAFFECTED (swap =
       x) w.p. u, else CHANCE (swap cells fresh Bern(.5)); z<0: t=-z,u=0;
       z>=0: u=z,t=0. (Matches the engine plants: S1 = transferred, S0 =
       unaffected, S1_half = pair mixture.)

2.4 LABEL (primary rule "REL2"):
  - guard fails                          -> NOT_ELIGIBLE (all three flagged)
  - certificate V issued, CERT_OK_V      -> V
  - certificate V issued, not CERT_OK_V  -> NOT_ELIGIBLE (V flagged)
  - no certificate: INDETERMINATE if some V has REACH_V and CERT_OK_V, else
    NOT_ELIGIBLE.
  Every row also carries the per-verdict flags ATTAIN_V = guard and CERT_OK_V
  and REACH_V, and the list NE = {V : not ATTAIN_V} (reported as e.g.
  "INDETERMINATE [NE: CHANCE_REL]": the absence of CHANCE_REL is uninformative).
  Rationale: a certificate is positive evidence; its error is FC (T1), which is
  controlled whatever the power. Power (T2) governs only what an ABSENCE of V
  means (burden symmetry: support needs a certificate, falsification needs
  demonstrated reach).
2.5 SENSITIVITY variant "REL2-STRICT" (reported, not primary): a certificate V
  also needs REACH_V, else NOT_ELIGIBLE. It shows which certificates depend on
  the choice in 2.4.

## 3 Predictions (before any table is computed)
P1 FC of the certificate is ~.5% (all <= .8%) under both models at P >= 32 on
   the whole grid; CERT_OK true at every design present in the data. FC > 1%
   only at a looser CI level (e.g. 80%) or tiny P.
P2 p_min per verdict at P256 K11, worst model: FLIP ~.55, NO_EFFECT ~.55,
   CHANCE ~.58-.59 (CHANCE is what binds W-N's .59). Realistic lower for FLIP/NE.
P3 All 42 are certified FLIP_REL under REL2 (they already passed W-N's gate).
   Of the 53 CHANCE/FLIP_REL/NOT_ELIGIBLE, >= 40 become FLIP_REL (those with
   lo99 > .50). The 21 CHANCE/CHANCE_REL/NOT_ELIGIBLE become CHANCE_REL.

## 4 Validation (every check has a must-fail input, shown to fail)
V1 synthetic FC table: CERT_OK at P256 K11/K12, P64 K11, P32 K3 under W, R and an
   OUT-OF-MODEL heterogeneous model (pair p_i ~ Beta with mean p, concentration
   4; arms independent). PASS iff all FC <= 1%. MUST-FAIL: the same rule at CI
   level .80 at p=.52 (FLIP boundary) has FC > 1% -> check fails.
V2 identification guard. MUST-FAIL: with the guard disabled, a synthetic
   p=.50 input whose swap is .49 (s bias, no bit) gets a FLIP_REL certificate.
V3 engine plants, W-N saved rep 0 (P1S/P1SK, q in {0,.1,.2,.3,.35,.4,.45}) from
   saved (ungated certificate, normal CI, P, K); and a FRESH replicate rep 1
   (seeds H_int(NS_WN,0x9A,1), M=512, q in {0,.05,...,.45}) with pair arrays
   saved, certificate recomputed by swap_rel2. Truth z per arm: S1, S, P1SK
   site_all -> -1; S0 -> +1; P1SK S, Kp -> 0 (tie); S1_half, S1_3q -> 1 - 2f
   with f = realized fraction of masked pairs (read from the q=0 noiseless
   swap). PASS iff (a) 0 false certificates (issued V whose region excludes
   z_true); (b) among cells whose true verdict V is ATTAIN_V, V is issued in
   >= 80%; (c) NOT_ELIGIBLE appears only where the rule says no verdict is
   attainable. MUST-FAIL inputs: (a) fed with truth labels swapped (S0 as FLIP)
   -> false certificates > 0; (b) W-N's gated verdicts on the same cells fail
   (b) at q = .40 if its p_min exceeds lo99 while REL2 attains FLIP.
V4 synthetic "too strict / too loose" gate checks (pytest):
   - a true complete transfer at normal .60, P256 K11 must be FLIP_REL (W-N's
     gate must fail this: NOT_ELIGIBLE);
   - a too-loose rule (level .80, or no guard) must issue a false FLIP_REL at
     normal .52 (boundary / no-bit input) in > 1% of draws, REL2 must not;
   - REACH computed at the point estimate instead of lo99 must mislabel an
     INDETERMINATE whose lo99 < p_min_CHANCE.

## 5 Application to W-O (after V1-V4 are run)
Input: W-O out/rerun_s*.jsonl (M=512, P, cells, normal CI, rel_ungated, z) joined to
rerun_table.csv (vid, source, specimen, family, arm, timing, single, rel, rel_gated).
Output: out/rel2_table.csv; transition tables REL2 x absolute (single), REL2 x
W-N gated, REL2 x ungated, REL2-STRICT; proportions with Wilson 99% and specimen-
cluster bootstrap 99% (2000, seed 0). The 42 (absolute CHANCE, W-N gated FLIP_REL)
listed individually with specimen, arm, timing/offset, normal CI, swap CI, z, REL2,
REL2-STRICT. No threshold above is changed after this point; any deviation is
logged as such.

## 6 Compute
Engine rep 1 under a Fabric skullport:cpu8 lease (--as Ananke), total threads <= 8
(3 processes: P1S q-halves x 3 threads, P1SK x 1 thread; simulations x 1 thread).
No GPU. Budget <= 3 h wall.
