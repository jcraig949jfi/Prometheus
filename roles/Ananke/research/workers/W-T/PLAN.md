# W-T PLAN (E-ANANKE-W-T, T-INS-16 successor of T-INS-11 thr-8c7342a7d513, MWO-0004) -- FROZEN 2026-09-29 ~14:20Z
FROZEN before any run on a test unit (plants at ns 0x640 or cells 4781b0a1 / 78f3b0ec / e06701a5).
Nothing below changes after results; any later analysis is labelled POST HOC in LOG.md.

## s1 Question
How far does W-S's first-broadcast latency rule reach? Test W-S's P8 / P8any, frozen, on (a) a
known-answer DIRECT-carrier plant under sync update_period 2 (jitter on; jitter off control; must-fail
inputs), (b) MAJ 4781b0a1 mixed strata, (c) 78f3b0ec mixed strata (follow census), (d) e06701a5 o5
mixed stratum (follow census).

## s2 Predictors -- copied EXACTLY from W-S (PLAN s7 + code)
Source: roles/Ananke/research/workers/W-S/PLAN.md s7, posthoc.py (lines `srcc = sorted(...)` ..
`r["P8_srcfirst"] = ...`) and posthoc_summary.py (`p8any = ...`). My copy: wt.p8_features / wt.p8any_of
(verbatim logic; KA-R below shows it reproduces W-S's rows bit-for-bit).
- Cue-bearing copies: W-S probe.cue_flip_run (world vs. twin with trial k's cue sign flipped, all
  shared draws); pair p uses the union of its two worlds' cue-bearing copies. D = cue-bearing copies to
  the readout a with te >= t0 and arrival <= ro. Source s = sense_idx[:, 0] (W-S; for MAJ this is the
  FIRST of the 5 sensors -- literal, see P8all below).
- P8_srcfirst ("P8"): te1 = earliest te of a source->a copy in D; first = copies with te == te1.
  All first copies arrived <= tau -> S; all > tau -> C; both -> M; no source copy in D -> U.
  (te1 is NOT required to be <= tau: literal.)
- P8any: C iff any first-emission copy is in flight at tau (P8 = C or M), else S (P8 = S or U).
- Accuracy (W-S analyze.accuracy, reused by import): over pair-trials with pattern in {S, C}.
  STRICT: M/U count as errors. DECISIVE: over pair-trials with P8 in {S, C}. COVERAGE = decisive /
  S-or-C pair-trials. 99% bootstrap over mirror pairs, 2000 draws.
- SECONDARY (descriptive, NOT in the decision rule): P8all = the same 3-way rule over the union of
  EACH sensor's own first-emission copies to a (differs from P8 only for MAJ, K = 5).

## s3 Units (M = 256, ns = assays.world_seeds(0x640, 256), trials 1..11)
Mixed stratum rule (fixed from PRIOR data = W-R raw_<cell>.npz at ns 0x620, computed before freezing;
LOG A3): stratum (o, q = (t0+o) mod 2) is MIXED iff prior n(S or C) >= 50 and max(fS, fC) < .80 among
eligible pair-trials.
- (a) Plants (wt.py; RELAY c16d5231 physics with prog_len 24, env d3 delta 8 Pd 11; direct delay
  1 + 3 + jitter; fanout 8 over 6 ring ports, loss .1). Offsets 4, 5; frozen census.
  - PLANT_P1_J1 (PRIMARY KA): the source emits its cue once per trial (its single awake cue tick);
    every site: S0 := sign(IN0_0) if IN0_0 != 0. Mixed strata by construction: o4 q0, o5 q0
    (swap tick = wake tick; first copies land at te1+4 or te1+5). Clean: o4 q1 (C), o5 q1 (S).
  - PLANT_P1_J0: jitter-off control.
  - PLANT_PF_J1: first broadcast on PAY0 + DECOY re-emission of the latched cue on PAY1 every later
    wake (cue-bearing, causally ignored) -- the realistic case (W-S's cells re-broadcast).
  - PLANT_PL_J1 (MUST-FAIL plant): the source re-emits the cue on PAY0 every wake; readout follows the
    LATEST arrivals. P8 must fail here.
- (b) 4781b0a1 (MAJ, frozen census), offsets 0..15; units = the 22 mixed strata:
  0:0,1:0,2:0,3:0,4:0,5:0,5:1,6:0,6:1,7:0,7:1,8:0,8:1,9:0,9:1,10:0,10:1,11:1,12:1,13:1,14:1,15:1
- (c) 78f3b0ec (RELAY delta 16, FOLLOW census = W-R followdiff.follow_table / lens_swap.census_follow),
  offsets 9, 10, 11, 14, 15. PRIMARY units (brief / W-R): 9:0, 11:1, 14:1, 15:1. Additional units (mixed
  by the same rule, no phase effect): 10:0, 10:1.
- (d) e06701a5 (FOLLOW census), offset 5; unit 5:0 (5:1 is a clean S stratum, reported).

## s4 Decision rule per unit (frozen, from the brief)
RULE REACHES iff P8 decisive accuracy lo99 > .90 with coverage >= .25 AND P8any strict lo99 > .80.
Otherwise DOES NOT REACH, naming which part fails, plus cue-traffic descriptors (s5).
Cell-level: the rule reaches a cell iff it REACHES every unit of that cell (78f3b0ec: primary units);
the count of reaching units is reported for all.

## s5 Known-answer checks and must-fail inputs (pass criteria)
- KA-R (done in development, LOG A5): my P8 implementation vs. W-S posthoc_c16d5231_ns632.json on
  pairs 0..31 (M 64 prefix of ns 0x632): pattern, P8, n1_held, n1_flight, te1_rel identical on all rows.
  Must-fail: same rows vs. the ns 0x630 file must mismatch (they do: 282/482).
- KA-P1 (PRIMARY): PLANT_P1_J1 o4 q0 and o5 q0: rule REACHES and P8 decisive point >= .99.
  Must-fail (shuffled first-broadcast labels, analyze.shuffled seed 0 over decisive S/C pair-trials):
  decisive accuracy <= .65 in both strata. Clean strata o4 q1 / o5 q1: P8 decisive >= .99.
- KA-J0 (control): PLANT_P1_J0: zero P8 = M predictions; in every stratum (o4/o5 x q0/q1) the
  P8-decisive S/C pair-trials are >= .99 one class and P8 decisive accuracy >= .99.
- KA-PF (decoy): PLANT_PF_J1 o4 q0, o5 q0: P8 decisive >= .99 on pair-trials where a first-broadcast
  (PAY0 != 0) copy reached the readout; >= 90% of all P8 decisive errors are pair-trials where none did
  (then P8's te1 is a decoy re-emission). Rule verdict reported, no pass criterion.
- KA-PL (must-fail plant): PLANT_PL_J1: rule DOES NOT REACH in both o4 q0 and o5 q0, and P8 decisive
  point < .90 in at least one of the 4 strata.
- Champion units: shuffled-P8 decisive and shuffled-P8any reported per unit (must be near the
  majority-class rate where the real predictor reaches).
- KA-B pytest (test_wt.py): p8_features / p8any_of on synthetic sets (held / flight / split / none /
  later-copy ignored / non-source ignored), decide() thresholds, plant genome sanity.
If KA-P1 fails, champion verdicts are reported but flagged "instrument not validated".

## s6 Descriptors (per unit, over S/C pair-trials and by pattern)
Cue-bearing copies to the readout per pair-trial (mean/median), source copies, first-emission copies,
share re-broadcast (source copies with te > te1 / all source copies to a), share relay (non-source
emitters), relay copies in flight at tau, number of distinct source emission ticks, te1 - tau histogram.

## s7 Budget / hygiene
<= 2.5 h wall, CPU only, torch threads 2 per process, <= 4 processes (<= 8 threads); Fabric lease
skullport:cpu8 --as Ananke for the 0x640 runs; PIDs recorded; no GPU; PYTHONDONTWRITEBYTECODE=1; no git
writes. Envelope <= 16 core-hours (expected < 2).
DEVELOPMENT (declared): plants at ns 0x7ff M 16 (PF/P1/PL/J0): P1 perfect; PF errors all on
no-first-broadcast pair-trials (14/14); PL fails. KA-R at ns 0x632 M 64 (c16d5231).
CONTEXT: read W-S REPORT RESULTS+DISAGREEMENTS (brief), W-S PLAN.md (definitions), W-S/W-R code, W-R strat
logs and raw npz (prior strata). No other worker's REPORT read.
