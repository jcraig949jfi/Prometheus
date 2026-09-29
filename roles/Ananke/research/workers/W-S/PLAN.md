# W-S PLAN (E-ANANKE-W-S, T-INS-11, MWO-0004) -- FROZEN before any champion predictor run

## s1 Question
In the sync update_period-2 RELAY cells, one swap-tick phase q = (t0+o) mod 2 is a ~50/50 per-trial S/C
mixture (W-R: 2dccdaa5 o5 q0, c16d5231 o4 q0, c16d5231 o5 q0, 8c37f32e o5 q0). What decides, pair-trial by
pair-trial, whether it reads S or C?
- H1 delivery timing: the cue-bearing packet(s) the readout depends on are delivered before the swap tick
  (held in a site / inbox -> S) or after it (in flight -> C); latency jitter/routing decides which.
- H2 route (which emitter / hop distance carries it), H3 per-world state (a pair's class is a property of
  the pair, not the trial), H4 other: in the plant, straddling copies cancel and the readout keeps its
  stale previous-trial S0, so S/C follows y_prev == y_now ("stale-state fallback").

## s2 Instrument (probe.py, analyze.py; nothing in prometheus/ananke edited)
- Arms: SINGLE-trial site / chan carrier swaps via a fork runner bit-identical to W-R fork_single (KA-F),
  after tick tau = t0 + o; plus targeted site_a (SITE arrays of the readout site only) and flight_a
  (in-flight slots addressed to the readout site only). Patterns S/C/N/X/tie and eligibility exactly
  lens_swap.pair_trial_table.
- CUE-BEARING PACKETS. For trial k, from the normal state after tick t0-1, run each world m next to a twin
  with trial k's cue sign flipped (same world seed => every route/loss/latency draw shared). A packet copy
  (emitter v, emit tick te, copy f) is cue-bearing iff it differs between world and twin (delivered?,
  recipient, delay, payload). Logged: te, v, recipient, delay, latency jitter draw, hop distance. Mirror
  pair p uses the union of its two worlds' cue-bearing copies. Arrival tick = te + delay.
- Mirror-different packet log (partner vs partner) is kept only for the KA-L bookkeeping check.

## s3 Predictors (per eligible pair-trial; a = readout site, ro = readout tick)
Direct set D = cue-bearing copies delivered to a with te >= t0 and arrival <= ro.
- P3_cone (PRIMARY, 3-way). Backward cone of (a, ro) through cue-bearing deliveries: a copy emitted at
  te <= tau is a leaf -- 'S' if arrival <= tau (held in a site/inbox at the swap), 'F' if arrival > tau
  (in flight at the swap); a copy emitted at te > tau by v recurses into v's cue-bearing deliveries with
  arrival <= te (none => 'S' leaf: v's difference was site-held). Prediction: all leaves S -> S; all F -> C;
  both -> M (straddle, abstain); no cue-bearing delivery -> U (abstain).
- Secondary timing predictors (pre-registered, labelled secondary):
  P1_first: first arrival in D <= tau -> S else C (U if D empty).
  P2_dflight: any copy in D with te <= tau < arrival -> C else S.
  P4_last: last arrival in D <= tau -> S else C.
  P5_dleaf: 3-way over copies in D with te <= tau (all held S / all in flight C / both M / none U).
  P6_share: among copies in D with te <= tau, in-flight share > 1/2 -> C, else S (U if none).
- P7_stale (H4): predict S iff y_k == y_{k-1} (lead world labels), else C, over all pair-trials;
  P7b: the same restricted to P3 = M pair-trials. (Direction fixed by the plant derivation, LOG A6.)
- H3_loo: predict each pair-trial by the majority S/C of the same pair's other pair-trials in the stratum.
- H2 descriptive: pattern x (first arrival from the source?, its hop distance, its jitter draw, whether the
  jitter moved it across tau: arrival - jit <= tau < arrival).
- Causal certificate (descriptive): rate at which flight_a reproduces the chan arm and site_a the site arm,
  by pattern.

## s4 Metrics and decision rules (units U1..U4 = the four mixed phases above; M = 256, ns 0x630)
- Accuracy over eligible pair-trials with pattern in {S, C}. STRICT: M/U count as errors. DECISIVE: over
  pair-trials with prediction in {S, C}; COVERAGE = decisive / all S-or-C pair-trials. 99% bootstrap over
  mirror pairs (2000 resamples).
- H1 SUPPORTED for a unit iff P3 strict lo99 > .80.
- H1 PARTIAL for a unit iff not SUPPORTED and either (P3 decisive lo99 > .80 and coverage >= .50) or some
  secondary timing predictor P1/P2/P4/P5/P6 has strict lo99 > .80 (named, labelled secondary).
- H1 NOT SUPPORTED for a unit otherwise. H1 overall SUPPORTED iff SUPPORTED in all 4 units.
- Clean-phase comparison (same offsets, other phase): H1 predicts P3 strict accuracy >= .90 (point) there.
- H3 SUPPORTED iff H3_loo strict lo99 > .80. H4 SUPPORTED iff P7 strict lo99 > .80 (all pair-trials) in a
  unit; P7b reported for the M subset.
- MUST-FAIL per check: the predictor's labels permuted across the S/C pair-trials of the stratum (seed 0)
  must give accuracy within .15 of the majority-class rate; if a real predictor passes, its shuffle must not.
- Offsets run: o4 and o5 in all three cells (o4 of 2dccdaa5 / 8c37f32e descriptive only), trials 1..11.

## s5 Known-answer checks
- KA-F (done, LOG A3): site/chan arms bit-identical to W-R fork_single; must-fail late=1 not identical.
- KA-L: every real in-flight mirror difference addressed to the readout site at tau is predicted by the
  packet log (real set subset of logged set, 100%); must-fail: log te shifted +1 => < 100%.
- KA-P plant: plants.echo_hold, c1b_echo_physics with update_period 2, HOLD gap 11 cue_len 2 iti 3 (Pd 17),
  M 256, ns 0x630, offsets 5, 6, 11, 12 (the two legs x two cue phases).
  (a) lat_jitter 1: in each offset's straddle phase (the one with both S and C), P3 decisive accuracy
      >= .95 with lo99 > .80 and coverage >= .30; P7b >= .95 on the M subset.
  (b) lat_jitter 0 (MUST-FAIL for "separation"): each of those offset-phases is a single class (>= .99 of
      S/C pair-trials one class) and P3 strict accuracy >= .95 there, i.e. nothing to separate.
  (c) MUST-FAIL: P3 labels shuffled on (a): decisive accuracy must fall to <= .65.
- KA-B pytest: synthetic cones (held / in-flight / straddle / relay after tau), accuracy with M/U as
  errors, shuffle, LOO.

## s6 Budget / hygiene
<= 2.5 h wall, CPU, torch threads 2 per process, <= 3 processes; Fabric lease skullport:cpu8 --as Ananke
held for the KA-P + champion runs; no GPU; PYTHONDONTWRITEBYTECODE=1; no git writes.
DEVELOPMENT (declared, before freeze): plant PLANT2J1 M64 ns 0x631 and 4781b0a1 (MAJ, not a champion) M64
ns 0x631; e06701a5 attempted (0 eligible). In 4781b0a1 cue-bearing traffic was dense (every cone M,
flight share flat across S/C/N): the predictors may saturate in the champions too; that would be a result.

## s7 ADDENDUM (written 2026-09-29 ~13:50Z AFTER the 0x630 champion results; frozen before the 0x632 run)
Post-hoc finding at 0x630 (LOG A13-A14): the readout follows only the SOURCE's FIRST cue broadcast.
P8_srcfirst: copies to the readout a from the source's first cue-emission tick te1: all delivered by tau
-> S, all after -> C, split -> M, none -> U. P8any: C iff any of those copies is in flight at tau, else S.
Confirmatory replication, fresh namespace assays.world_seeds(0x632, 256), same cells/offsets/trials:
- R1: P8 decisive accuracy lo99 > .80 in each of U1-U4 (0x630: 1.00 in all four).
- R2: P8any strict lo99 > .80 in U2 and U3 (0x630: 1.00 [1.00,1.00]); in U1 point in [.80, .95]
  (0x630 .87); in U4 NOT > .80 (0x630 .64) -- straddles there read S/C/N ~thirds.
- R3: straddle (P8 = M) outcomes: c16d5231 >= .95 C; 2dccdaa5 and 8c37f32e S share among S/C in [.30, .70].
- R4: clean phases (o5 q1 all cells, o4 q1 of 2dccdaa5/8c37f32e): P8any strict >= .95.
- Must-fail: shuffled P8any labels in U2/U3 must fall to <= .70.
