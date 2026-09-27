# W-E PLAN  T-RET-1 retention census (written BEFORE any run)

Worker W-E, analysis namespace 0x5E9 (world seeds = assays.world_seeds(0x5E9, 64)),
64 worlds = 32 twin pairs. CPU, torch.set_num_threads(2). Brief:
threads/T-RET-1_retention_census.md. Rules: handoffs/COMMON_RULES.md.

## Question
After trial k's readout (k = 3), does a PTE champion's endogenous state keep
information about cue k; for how long; is it decodable; does it still act?

## Specimens (16)
- 12 D-wave cells: c1b_run.d_wave_cells(); genome = row["extra"]["genome"],
  physics/env from the row. Carrier class from spikes/out/s_ct.json keyed by the
  row's parent[:8] (site-state FLIP / in-flight FLIP / joint = neither FLIPs).
- 4 M2 champions: spikes/out/champions_m2.json (4ab2ba01, fresh1..3); physics/env
  from c1b_run.load('4ab2ba014aac967e') (HOLD, ring, in-flight pay1 carrier).
All 16 envs have trials = 12, so k = 3 and lags j = 0..6 (trials 3..9) fit.

## Construction: single-cue twins
As lens.cue_arrival_profile: for each pair (2p, 2p+1) both worlds use the lead
seed and the LEAD's schedule (sense_idx, read_idx, sense_val); world 2p+1 has
the sense values negated at trial k's cue ticks only (all K sensor columns:
HOLD/RELAY 1 column, MAJ 5 columns). Twins therefore share every exogenous
draw and every input except cue k. Cue label c_p = lead's y[k] (= sign of cue k
for HOLD/RELAY/MAJ), twin label = -c_p.
Eager run (World.step), recorder after every tick. Endogenous state compared =
World.state_arrays(): S, E, r, Kp, w (if R>0), Acc_sum, Acc_cnt, Msum, Mcnt.

## Definitions (from the brief, made operational)
Period Pd = env.period(); trial m occupies ticks [m*Pd, (m+1)*Pd - 1];
readout tick ro_m = ep.ro_tick[lead, m]; "end of trial m" = state after tick
(m+1)*Pd - 1 (after the ITI).
- MERGE TIME (per pair): first tick t >= ro_k after which the full state of the
  twins is bitwise equal. Reported as t - ro_k. Once merged the cue is provably
  gone (identical future inputs and draws).
- PRESENT DURATION: merge time, or censored at T-1 - ro_k if never merged.
  Per champion: fraction merged by end of trial k, k+1, ..., k+6 and by episode end;
  median (Kaplan-Meier style with censoring noted).
- Per-carrier presence (descriptive): per tick, number of pairs whose carrier
  array differs, and number of differing elements (separation, prior art s3.2).
- RECOVERABLE at lag j (PRIMARY, decides): single-world decoder. Features at end
  of trial k+j, one per carrier sum: S[:, :, d] summed over sites (each d),
  S[actuator, d] (each d), E sum, r sum, Kp sum, w sum (if R), Acc_sum sum,
  Acc_cnt sum, Msum component p summed over ring/sites/channels (each p),
  Msum component p to the actuator (each p), Mcnt sum. Decoder = sign(s*(f - th))
  with polarity s and threshold th = midpoint of class means fitted on the TRAIN
  half of pairs (both worlds of a pair go to the same half); the single feature
  with best train accuracy is selected (ties -> first in list); prediction 0
  scores 0.5. Two folds (fixed split of the 32 pairs, seeded 0x5E9, then swapped);
  statistic A = mean held-out accuracy over the two folds (64 test worlds).
  Permutation null: flip the label sign of each pair independently (exact
  sign-flip randomization within twin pairs), rerun the whole fit + select +
  test; NPERM = 20000; p = (1 + #{A_perm >= A_obs}) / (1 + NPERM).
- RECOVERABLE-PAIRED at lag j (SECONDARY, reported, does not decide): 2AFC
  decoder on the twin difference d_p = f(2p) - f(2p+1): predict c_p = sign(s*d_p),
  s fitted on train pairs, best feature by train accuracy, same folds, same
  sign-flip null. This separates "consistent-signed trace" from chaotic
  divergence without the nuisance of the other trials' cues.
- EFFECTIVE at lag j: full-state carrier swap between the twins after tick
  (k+j)*Pd - 1 (trial k+j's onset); outcome = fraction of pairs where trial
  k+j's answer (sign of S0 at ro_{k+j}, 0 its own value) changes vs the unswapped
  run. Because the twins' inputs are identical after trial k, the swap hands each
  world exactly its twin's future, so for j >= 1 EFFECTIVE(j) must equal the
  fraction of pairs whose twins answer trial k+j differently in the baseline
  run; j = 0 swaps two identical states (no-op). I RUN the swaps anyway (lens.swap
  hook, all 7 lags) and check this identity as guard G5. Signed interference
  also reported: mean over pairs of c_p * (ans_2p - ans_2p+1)/2.

## Multiple-comparison correction
Primary family = 16 champions x 7 lags = 112 single-decoder tests, Holm-Bonferroni
at family alpha 0.01. NPERM = 20000 gives min p = 5.0e-5 < 0.01/112 = 8.9e-5.
The secondary (paired) family is corrected the same way separately (112 tests).
Controls are outside both families.

## Classification (per champion, fixed now)
Flags:
- RR = RETAINS-RECOVERABLE: some j >= 2 with Holm-adjusted primary p < 0.01.
- INT = INTERFERES: some j >= 1 whose swap-changed-answer fraction has 99% pair
  bootstrap (lens.ci) lower bound > 0.
- FORGETS: all 32 pairs merged by end of trial k+1.
- DIVERGES: fewer than 50% of pairs ever merge by episode end.
Primary label, by precedence: RETAINS-RECOVERABLE > INTERFERES > FORGETS >
DIVERGES-UNRECOVERABLE (DIVERGES and no significant decoder at any j >= 1) >
MIXED (anything else: e.g. slow partial merging with no decodability; fractions
reported). All flags are reported, not only the label.

## Decision (from the brief)
"PTE has a nontrivial retention regime" iff >= 1 champion is RR (primary
decoder, j >= 2, Holm p < 0.01 over 112 tests). If only the paired decoder
reaches it, I report "retained-discriminable only" and the decision stays NO.

## Predictions (before running)
P1 HOLD site-state latches (4 D HOLD cells, decay_shift 3/1, latch overwritten
   by each cue): FORGETS - the next cue overwrites the latch; residual
   differences in E / in-flight should drain within a trial. Merge by k+1.
P2 RELAY in-flight carriers on rings with decay_shift 0 (31cd2a8a, 62a7fff9,
   c16d5231 parents): more likely to keep undecayed residue somewhere (S dims
   not driven, Kp via WIMM, w); I predict some pairs never merge, but the
   residue is not sign-consistent -> DIVERGES-UNRECOVERABLE or MIXED.
P3 M2 champions (in-flight pay1, decay 0, e_income 0 so E is not refilled):
   E can differ permanently if the twins emit different counts (E only decreases
   with c_emit; here c_emit = 0 so E constant) - so E will not carry it; I
   predict MIXED/DIVERGES, not RR.
P4 Headline: NO nontrivial retention regime (probability ~0.7). If any RR
   exists I expect it in a decay_shift 0 champion via an unused S dimension or Kp.
P5 INTERFERES: rare (task scores are high and targets iid); at most in
   joint/MAJ cells.

## Guards (a failed guard stops the interpretation of that champion)
G1 Twins bitwise equal at every tick before trial k's first cue tick.
G2 After a pair merges it never re-diverges (determinism + identical futures).
G3 Twin schedules identical except trial k cue ticks (checked on tensors).
G4 Specimen sanity: normal mirrored accuracy (lens.run, same seeds) reported
   next to s_ct/s_m2 normal; a specimen far below its record is flagged.
G5 Swap identity: swap-run answer at trial k+j == twin's baseline answer (j>=1),
   and j=0 swap trace == baseline trace, in every world.
G6 Decoder calibration: permutation p for a pure-noise feature set (the same
   pipeline with features replaced by N(0,1), 200 replicates) is ~uniform
   (fraction p<0.05 in [0.01, 0.10]).

## Known-answer controls (M2 physics, M2 HOLD env; outside the families)
C-NEG hold_latch plant: S0 latch overwritten by the next cue; no packets.
  Expected: every pair merges at trial k+1's cue (FORGETS), decoders at j>=1
  exactly 0.5 (merged twins give 1 right + 1 wrong).
C-POS integrator: hold_latch + (ADD S1 S1 SENSE): S1 accumulates every cue and
  distractor forever (decay 0). Expected: never merges; PAIRED decoder A = 1.0 at
  every lag; SINGLE decoder only partially powered (cue k is 1 of k+j+1 +-512
  terms plus distractors): this calibrates what the primary decoder can see
  against superposed history. Its value is REPORTED, not a pass/fail gate.
C-POS2 own-trial positive control per specimen: single decoder of trial k+1's
  cue (shared by both twins) from end-of-trial-(k+1) state, same null (pairs
  flipped). Shows the decoder reads a champion's current latch when it exists.

## Budget
Brief STOP at 3 h. Per specimen: 1 twin run + 7 swap runs + 1 mirrored normal run
(64 worlds, T = 156-204 ticks, CPU). If the swap runs exceed budget I keep the
baseline-identity EFFECTIVE (G5 checked on a subset) and log it.

## Addendum A (still before any run, 2026-09-27)
Physics check after writing: the 5 ring D cells with decay_shift 0 (RELAY x4,
MAJ 9e72f9b6) have plastic_route = 1 and wimm = 1, so w (routing weights,
clamped 0..1023, never decayed) and Kp are candidate PERMANENT carriers of a
cue-dependent difference. MAJ M3 cells (023539c4, feadc823) have setrule = 1
(rules = 4), so r is a candidate carrier there. This sharpens P2/P4 (where
RR would come from) but changes no definition, threshold or rule.
The global HOLD cells have economy on (e_income 4, c_emit 1): E differs only
while emission counts differ and refills to e_max, so E should re-merge.

## Addendum B (POST-HOC, written after seeing the census; EXPLORATORY ONLY)
Seen: primary decision = NO (no Holm-significant single decoder at j >= 2),
but the preregistered paired decoder is at its floor (A = 1.0, Holm p = 0.0056)
in D_f7e62fe3 and M2_fresh3 via w_sum at every j = 2..6, and the C-POS
integrator showed the single decoder cannot see a trace superposed on the
other trials' cues. Exploratory question: is cue k recoverable from ONE
world's state once the known other inputs are accounted for?
Decoder H ("history-aware"): per feature, OLS on train worlds
f ~ 1 + y_0..y_{k+j} (all trial targets up to k+j; cue k column = world label);
test: residual r = f - b0 - sum_{m != k} b_m y_m, predict sign(b_k * r); best
feature by train accuracy; same folds, same pair sign-flip null (20000),
Holm over 16 x 7. This does NOT change the preregistered decision; it is
reported as exploratory and proposes the rule for a follow-up Thread.
