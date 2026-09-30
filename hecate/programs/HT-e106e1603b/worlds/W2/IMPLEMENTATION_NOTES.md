# HT-e106e1603b / W2 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...ea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: PREREG, W2, mechanisms M1 and M6, lenses L1, L2, L6. Nothing else.

## Spec field -> code

- hypothesis / mechanism (M1): `world.py::Tanner` builds a random
  (3,6)-regular Tanner graph (n variables, m = n/2 checks, configuration
  model with multi-edge repair by socket swaps). All-zero codeword, so
  the state is the error vector e. `SandpileState` keeps e, the syndrome
  s, and per-variable unsatisfied counts u incrementally (pure Python).
  Drive: flip one uniformly random bit of e. Relax: parallel sweeps --
  the set F = {v : u_v >= 2} is computed from the pre-sweep state and all
  of F is flipped simultaneously -- repeated until F is empty
  (quiescence) or 50 sweeps. |e| is recorded after each relaxation.
- intervention / null_twin: syndrome-blind relaxation with matched flip
  counts (see ambiguity A2): same graph, same injected bits in the same
  order; at sweep j after injection i the twin flips k_ij uniformly
  random distinct variables, where k_ij is the number the syndrome rule
  flipped at that step of the TREATMENT run on the same (seed, n).
- control: fast drive -- 10 distinct uniformly random bits flipped per
  drive event, then the same relaxation. Same number of drive events
  (30000) as treatment (ambiguity A3). The control has no role in the
  PREREG outcome classes; its rho* and slope are reported only.
- positive_control (L2): for each seed, for n in {1000, 2000}: iid errors
  at 20 values of p, 200 blocks each, decoded by the same parallel
  2-of-3 rule, up to 50 sweeps (vectorised numpy, full recompute each
  sweep; a self-test asserts it gives bit-identical results to the
  incremental Python decoder on test vectors before any arm runs). Block
  failure = any residual error. Logistic regression of failure on log p
  per n (sklearn, C = 1e6); crossing of the two fits = p*_seed. Detected
  iff every seed has a crossing in [0.01, 0.2] with both slopes > 0
  (the spec: "crossing must exist in [0.01, 0.2] or the run is void").
  p* = mean of the per-seed crossings.
- observable: per (arm, seed, n) row, the full series of |e| after each
  relaxation. rho* = mean of |e|/n over the last half (injections
  15000..29999). Drift slope = OLS slope of |e|/n on injection index
  over the last half, times 10^4 (per 10^4 injections). p* as above.
  Also recorded (L1, descriptive only): avalanche size = flips per
  injection (mean, 95th percentile, max), number of relaxations that hit
  the 50-sweep cap. L6 (residue-cluster geometry) is not computed.
- success_criterion, as applied by evaluate.py, for EACH n in
  {1000, 2000} separately (both must hold):
  rho*_T = mean over seeds of rho*; slope_T = mean over seeds of slope;
  (a) |rho*_T - p*|/p* <= 0.2, (b) slope_T < 0.05 * rho*_T,
  (c) |rho*_twin - p*|/p* > 0.5 with rho*_twin the seed-mean twin rho*.
- failure_criterion: rho*_T < 0.2 p*, OR slope_T >= 0.05 rho*_T, OR twin
  within 20% of p*, for any n. Reported alongside; the outcome class
  uses the PREREG definitions (treatment fails the criterion OR meets
  the failure criterion -> NULL).
- CHEAT: for each (seed, n) a series |e|_t = round(n * p* * (1 + 0.02 z_t)),
  z iid standard normal, written directly as the observable (no graph,
  no relaxation). Detected iff clauses (a) and (b) hold for CHEAT.
- null_twin_meets_success: the twin's seed-mean rho* is within 20% of p*
  (|rho*_twin - p*|/p* <= 0.2) for any n (the failure criterion's
  wording "null twin also within 20% of p*"), with slope clause (b) also
  holding for the twin at that n.

## Outcome logic (evaluate.py, from PREREG)

1. If any TREATMENT or NULL_TWIN row is truncated by the compute guard:
   NOT_BUILT (budget).
2. Else if positive control or cheat not detected: INSTRUMENT_FAIL.
3. Else if null_twin_meets_success: CONFOUNDED.
4. Else if success criterion holds for both n: SIGNAL.
5. Else NULL.

## Ambiguities and readings chosen

- A1 seeds: spec says 3 seeds; the PREREG requires >= 5 per arm, so 5
  seeds (0..4) are used. A seed fixes the graph for each n (shared by all
  arms of that seed) and all random streams (SeedSequence([seed, n, arm])).
- A2 null twin "the same size as the syndrome rule would have flipped at
  that step": read as paired with the treatment trajectory (matched flip
  volume, per the null_twin field "preserving drive and flip volume").
  The other reading (count the rule on the twin's own state) was
  rejected also because it is not buildable in budget: from the first
  injection the twin's own count doubles each sweep, the state saturates
  near density 0.5 with ~n/2 flips per sweep and never quiesces, i.e.
  ~50 * n/2 flips per injection x 30000 injections x 10 runs.
- A3 control "inject 10 bits per relaxation": 30000 drive events of 10
  distinct bits each (so 10x the injected bits of treatment).
  "Injections" in rho*/slope for the control means drive events.
- A4 p grid: 20 values geometrically spaced over [0.01, 0.2] (spec gives
  the count and the admissible crossing range, not the spacing). Chosen
  because the criterion is relative (|rho* - p*|/p*), so a log grid gives
  uniform relative resolution; chosen before any run.
- A5 pooling: criterion evaluated on seed means per n; p* is the mean of
  per-seed crossings. Per-seed pass counts are also reported.
- A6 "slope < 0.05 * rho*" is one-sided as written; a negative slope
  passes clause (b).
- A7 injection flips the chosen bit (it can remove an existing error).

## Parameters (all from the spec, none from results)

n in {1000, 2000}; degrees (3,6); t = 2 of 3; max 50 sweeps; 30000
drive events per run; control 10 bits/event; PC: 20 p values in
[0.01, 0.2] (geometric), 200 blocks per p per n per seed; seeds 0..4;
CHEAT noise 2% relative.

## Compute guard (fixed before running)

World.py measures process CPU time. Order: self-test, POSITIVE_CONTROL,
then per (seed, n) TREATMENT + paired NULL_TWIN, then CONTROL, then
CHEAT. If cumulative CPU exceeds 540 s, the running loop stops, the row
is written with "truncated": true and all later simulation runs are
skipped (written as truncated). Truncated TREATMENT/NULL_TWIN ->
NOT_BUILT; truncated CONTROL -> anomaly only. Single process, single core.

## Rows

rows.jsonl: one object per (arm, seed, n) for TREATMENT, NULL_TWIN,
CONTROL, CHEAT; one per seed for POSITIVE_CONTROL (both n inside); a
final META row with attempt number and CPU seconds (cumulative across
attempts via attempts.json). A rerun moves the previous rows to
rows_attempt<k>.jsonl.

## Attempt log

(filled after runs)

### Attempt 1 -- INSTRUMENT_FAIL (positive control not detected), stopped

Self-test passed (numpy and incremental decoders bit-identical). The
L2 positive control gave per-seed crossings 0.0058, 1.82, 0.0087,
0.0139, 0.0064: four of five outside [0.01, 0.2]. Failure fractions at
p = 0.01 were already ~0.44 (n=1000) and ~0.46 (n=2000), and larger n
failed MORE at every low p, so the curves never crossed in range.
Diagnosis (from PC rows and a graph-only count, no dynamics): the
configuration-model graphs kept 21-29 4-cycles each (42-58 variables
lying on one). Under the parallel 2-of-3 rule, an error on a 4-cycle
variable v gives its 4-cycle partner w two unsatisfied checks, so v and
w flip together, then w's error does the same to v: a period-2
oscillation that never decodes. The count of 4-cycles is O(1) in n,
so P(fail) ~ 1 - (1-p)^50 at both n, independent of the threshold,
which reproduces the ~0.4 failure at p = 0.01.
I killed the process (PID 3948) as soon as the PC rows showed the
failure, at ~40 s CPU; the TREATMENT/NULL_TWIN rows for seed 0 that had
already been written were NOT read (only their arm labels were listed).
attempts.json set to 1 attempt, 45 s CPU (conservative upper bound).
The attempt-1 rows are kept as rows_attempt1.jsonl.

### Instrument repair (the one allowed): 4-cycle-free graph

build_tanner now also removes 4-cycles by random socket swaps after the
multi-edge repair and asserts the graph is 4-cycle-free (girth >= 6).
This is still a random (3,6)-regular Tanner graph; 4-cycle removal is
the standard construction for bit-flip-decoded LDPC ensembles. It
applies to every arm (the treatment runs on the same graph as the
threshold measurement, as the spec requires "the same ensemble").
No threshold, grid, seed, or other parameter is changed. The rerun is
attempt 2; a second INSTRUMENT_FAIL makes the world NOT_BUILT.

### Attempt 2 (after the repair) -- INSTRUMENT_FAIL again, so NOT_BUILT under the PREREG

The run finished; evaluate.py (unchanged) gives INSTRUMENT_FAIL. With
the 4-cycle-free graphs the per-seed crossings are 0.0064, 0.0013,
0.0087, 0.0017, 0.0072, all below 0.01. The failure fraction at
p = 0.01 is 0.21-0.33, and n=2000 fails more than n=1000 at every low
p. So the parallel 2-of-3 bit-flip rule has no L2 crossing in
[0.01, 0.2] on these ensembles; the spec voids the run in that case.
The CHEAT arm was detected. Per the PREREG ("a second INSTRUMENT_FAIL
-> NOT_BUILT"), the world is NOT_BUILT as an allocation state. No
further repair was made.
Descriptive only (no reading of the treatment is made under
INSTRUMENT_FAIL): TREATMENT rho* = 0 at both n, all 5 seeds. Every
injected bit was removed in one sweep (avalanche size 1 every time,
max 1), so the density never left zero. NULL_TWIN rho* = 0.50 at both n.
It flips one random bit per injection instead of the injected one, a
random walk to 1/2. CONTROL (10 bits per event) saturated near 0.45-0.50
with relaxations hitting the 50-sweep cap. That was costly: the compute
guard truncated CONTROL for seeds 1-4, so only 3 CONTROL rows
are usable, and it is listed as an anomaly. Total CPU is 9.75
core-minutes over 2 attempts. The attempt-1 figure (45 s) is an upper
bound, because the killed process could not record its own time.
A __pycache__/ directory was left in this folder by an import during
the 4-cycle count.
