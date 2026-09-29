# W-N PLAN — T-SWAP-LOWACC (E-ANANKE-W-N, thr-5df816e9b844, MWO-0001 B-10)

FROZEN 2026-09-29 before any specimen swap arm is run. Worker W-N, CPU only.
Pre-freeze work (all logged in LOG.md): rule code, attainability simulation
(no specimen data), plant fixtures smoke + fork-runner bit-identity selfcheck
(plants only). Context seen before PLAN: W-L carriers_champs.json numbers and
W-F census_table.csv rows (needed to pick specimens); no SYNTHESIS / principal
files, no worker REPORT.md.

## 1 Question
lens.swap_verdict: FLIP iff hi99(swap acc) < .40. Under complete transfer a
mirror-pair swap drives accuracy to 1 - normal, so a specimen with normal ~.6-.8
cannot FLIP and reads CHANCE (eligibility gap). Design a RELATIVE verdict, fix
when it is attainable, validate it on plants with known carrier and controlled
normal accuracy, apply to real low-accuracy champions, report changed verdicts.

## 2 The rule (swap_rel.py, frozen)
Unit = mirror pair i. a_i, s_i = normal and swap accuracy of pair i pooled over
the SAME scored world-trials (paired). g = a - .5. Hypotheses: FLIP s = .5 - g,
CHANCE s = .5, NO_EFFECT s = .5 + g; boundaries at the midpoints z = -1/2, +1/2
(z = (s - .5)/g), written linearly:
  DF_i = (s_i - .5) + (a_i - .5)/2 ;  DN_i = (s_i - .5) - (a_i - .5)/2
99 % pair bootstrap, 2000 resamples, seed 0, pairs resampled jointly.
  0. NOT_ELIGIBLE   lo99(a) < p_min(P, K)            (checked first)
  1. FLIP_REL       hi99(DF) < 0
  2. NO_EFFECT_REL  lo99(DN) > 0
  3. CHANCE_REL     lo99(DF) > 0 and hi99(DN) < 0
  4. INDETERMINATE  otherwise
Each verdict needs its whole CI inside its own cell (CHANCE needs a certificate;
a straddle is INDETERMINATE). Deviation from the brief's wording, stated: FLIP_REL
certifies "closer to 1-normal than to .5", not "equal to 1-normal"; completeness of
transfer is reported separately (z with CI, and flip rate f).
Companion (reported, not a decision rule): flip rate f = P(swap outcome != normal
outcome) over world-trials decisive in both arms: 1 / .5 / 0 under FLIP / CHANCE /
NO_EFFECT at ANY normal accuracy (accuracy-free, like the census).

## 3 Eligibility (computed BEFORE freezing; out/attain_table.json)
p_min(P, K): smallest p (grid .01) such that for all p' >= p the ungated rule
returns the correct verdict in >= 80 % of 200 simulations under each truth, with
ARM-INDEPENDENT Bernoulli noise (worst case: pairing buys nothing), mirror-identical
pair outcomes, K independent trials per pair. Min power over truths:
  P=32  K=3  p_min .91 | P=32  K=11 .73 | P=64  K=3 .81 | P=64  K=11 .67
  P=128 K=3  .72       | P=128 K=11 .62 | P=128 K=12 .61
  P=256 K=10 .59       | P=256 K=11 .59 | P=256 K=12 .58
So at W-L's design (P=32 pairs, K=3 trials pooled) the rule is eligible only for
normal >= .91: the W-L champions (normal .58-.59 there) are NOT_ELIGIBLE at their own
sample size. DESIGN for this work: M = 512 worlds (P = 256), SINGLE arms over ALL
scored trials (n-back n=1: K=11; n=2: K=10; C1: K=12) -> eligible range lo99(normal)
>= .58-.59. The gate uses the specimen's own P, K (p_min computed on the fly).

## 4 SINGLE vs EVERY
Relative verdict is computed on SINGLE arms (swap only trial k, score only trial
k, pooled over k). Reasons fixed in advance: (a) the paired statistic assumes the
swapped trial's normal counterpart is the same world-trial with an unswapped
history; EVERY swaps change the history of later trials (W-M: mirror identity
broken in 5/7 census-JOINT cells); (b) n-back reads the bit of trial k-n, so an
EVERY swap moves several held bits at once. EVERY is also run on the 5 C1 cells
for comparison only (prediction: EVERY and SINGLE agree on FLIP_REL for HOLD
cells; may disagree for RELAY).

## 5 Known-answer plants (plants_rel.py; truth by construction)
n-back n=1 (W-L builder), W-L m2 physics with prog_len 28, M = 512, W-N seeds.
Normal accuracy controlled by the engine's own RAND op flipping the stored cue with
q in {0, .10, .20, .30, .35, .40, .45} (p = 1 - q, mirror-shared).
  P1S  (carrier S1): S1 swap -> FLIP; S swap -> FLIP; S0 swap (non-identical,
       unused) -> NO_EFFECT; S1 swapped in a fixed half of pairs -> CHANCE;
       S1 swapped in 75 % of pairs (z = -1/2) -> INDETERMINATE.
  P1SK (bit in S1 AND Kp[3], readout = sign(S1 + Kp3)): S -> CHANCE (tie),
       Kp -> CHANCE (tie), site_all -> FLIP.
Post-hoc readout-noise modes on the noiseless P1S engine readouts (100 redraws
each, p = 1 - q, q grid above): D2 flip noise ARM-SHARED; D3 flip noise
ARM-INDEPENDENT (the hard case: FLIP truth no longer exact per pair); D4 abstain
noise (readout -> 0, scored .5) arm-independent, q' chosen so p = 1 - q'/2.
Equivalence of post-hoc noise with an in-engine between-tick hook is checked on
one config before use.
PASS criterion per engine cell: if lo99(normal) >= p_min then verdict == truth,
else verdict == NOT_ELIGIBLE. Per post-hoc cell: over the 100 redraws, eligible
draws give the correct verdict in >= 90 % and a WRONG definite verdict (a
different one of FLIP/CHANCE/NO_EFFECT) in <= 2 %. INDETERMINATE truth: CHANCE_REL
or NO_EFFECT_REL or FLIP_REL in <= 5 %.
Negative controls (every check must be shown to FAIL on some input): the same check
fed the wrong arm (e.g. S0 arm into the FLIP check), the old absolute rule on the
FLIP plant at p <= .8 (predicted: CHANCE -> FAIL), and pytest mutation inputs.
Prediction: all eligible cells PASS; absolute rule FAILS FLIP truth for every
p <= .8 (hi99 of 1-p >= .40 there).

## 6 Real specimens (after plants pass)
(a) W-L n-back SUCCESS champions n1_s0, n1_s3, n2_s1, n2_s2 (+ n1_s2 near-miss,
labelled): arms S, site_all, channel_all, inbox, Kp at offset -1 (after tick
k*Pd - 1, as W-L back0); for n=2 also back1 (offset -1 - Pd). Prediction: S and
site_all FLIP_REL where eligible (carrier S), channel/inbox NO_EFFECT_REL.
(b) C1 SIGNAL cells with census class ELSEWHERE and normal < .8 (W-F census_table:
0187372b, 11f3ac85, 83d9d7b5, 42716814, d3c0d182; no class 'CHANCE' exists there):
arms site_all, channel_all, joint at the W-F mid offset and site_all, channel_all at
late offset; SINGLE (primary) and EVERY (comparison); plus lens_swap census on SINGLE
site/channel. Predictions (from W-F's EVERY numbers): HOLD cells 0187372b,
11f3ac85, 83d9d7b5: site_all mid FLIP_REL (was CHANCE); RELAY 42716814, d3c0d182:
joint FLIP_REL, site/channel CHANCE_REL or INDETERMINATE.
Report every verdict that changes (absolute -> relative) and every NOT_ELIGIBLE.
The absolute verdict is recomputed on my own SINGLE data AND compared with the
recorded W-L / W-F verdicts.

## 7 Budget / compute
CPU only, torch threads <= 8. Heavy runs (> 2 threads > 5 min) only under a Fabric
lease skullport:cpu8; if BUSY, run at 2 threads or queue in QUEUE.md.
