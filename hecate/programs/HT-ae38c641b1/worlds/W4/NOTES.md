# HT-ae38c641b1 / W4 -- implementation notes (written before any code)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: the two PREREGs, W4, mechanisms M3/M10/M7, lenses L6/L1. Nothing else.

## Spec gaps that force an invented reading (recorded up front)

W4 says "Cantor-escape family k in {4,6,8}" and "decided test as in W1".
The implementer rules forbid reading other worlds (W1) or the I-nodes, so
BOTH the map family and the decided test are this implementer's reading,
not the author's. If W1 defines them differently, this world is a
different world. This is the largest threat to faithfulness.

### Map family (reading)
- u-frame map F_k(u1,u2) = (k*u1 mod 1, k*u2 mod 1) on [0,1]^2.
- Kept digits: the even digits {0,2,...,k-2} (m = k/2 non-adjacent strips,
  so kept squares never merge). A point survives step n iff floor(k*u_i)
  is a kept digit for both coordinates; otherwise it escapes. Points with
  u outside [0,1]^2 escape at once.
- Survive-T set K_T = product Cantor dust truncated at level T; its
  boundary for T -> inf is the dust K itself, box dimension
  D_k = 2 ln(k/2)/ln k  (k=4: 1.000, k=6: 1.226, k=8: 1.333).
- Rotation t: the x-frame map is the conjugate F_t = R_t o F_k o R_t^-1
  about the centre (0.5,0.5). True escape set = rotated K_T (same D).
  lambda = ln k (Lyapunov exponent; rotation does not change it).
  lambda*T grid: 12 distinct values, each at t = 0 and t = 30.

### Decided test (reading of "as in W1")
Sound stepwise interval evaluation of F_t on an axis-aligned x-box, T steps:
  x-box -> u-hull (hull of R^-1 image; t=0: identity) -> meet with kept
  strips per coordinate (the escape guard):
    - empty in either coordinate -> DECIDED escape
    - overlaps >= 2 kept strips in a coordinate -> UNDECIDED, stop,
      width signal saturates to 1.0
    - exactly one strip per coordinate -> restricted box, exact affine
      image k*u - d, then x-hull of R image, next step.
  Survives all T steps: DECIDED survive if the box never lost mass to the
  guard (box wholly inside strips every step); otherwise UNDECIDED (mixed).
At t = 0 this is exact up to the ">= 2 strips" stop (wrapping-free). At
t = 30 every step wraps twice (hull of rotated box, factor (cos+sin)^2 =
1.866 per step): this is the wrapping the hypothesis is about.
t=0 uses no outward padding (dyadic/strip comparisons are made as k*u vs
integer); t=30 pads each hull outward by 1e-12.

### Width signal (for the phase-2 treatment, fixed now)
width = max side of the u-frame interval image at the step the sound
evaluation ended (1.0 if saturated). Sens priority = width * area over
UNDECIDED leaves; ties broken by a per-seed random key.

## Spec field -> code

- mechanism (quadtree over [0,1]^2, split argmax width*area among
  undecided leaves) -> world.py policy "sens" (phase 2 only).
- intervention (T in {2,5,10,20}, t in {0,30}, k in {4,6,8}) -> the 24-config
  grid, CONFIGS in common.py.
- control (uniform, full levels) -> policy "uniform": full levels
  L = 3..7 (B = 64..16384 leaves); undecided area recorded under BOTH the
  ground truth and the sound test.
- positive_control (oracle splits only leaves that truly intersect the
  boundary, ground truth at 2^-12) -> policy "oracle": among leaves that
  truly intersect the boundary and have depth < 12, split the largest
  first (ties random per seed). "Truly intersects" = the cell's interior
  overlaps both the interior of K_T and its complement (positive measure
  of both), computed exactly (rotated-square vs Cantor-square SAT test,
  DFS to level T) for cells of depth <= 12. The oracle's undecided area
  is the area of its leaves that truly intersect the boundary (it is the
  ideal reasoner; it does not use the sound test). If it runs out of
  splittable leaves (all at depth 12) before B = 16384, it stops and the
  fit uses the checkpoints reached (recorded as an anomaly).
- observable gamma = -OLS slope of ln(undecided area) vs ln(B) at
  checkpoints B = 64, 128, ..., 16384 (first moment leaves >= B; leaves
  grow by 3 per split). Uniform: B = 4^L, L = 3..7.
- null_twin (random refinement matched to the policy's leaf-depth
  histogram at each budget) -> policy "null": replays the depth sequence
  of the reference policy's splits, choosing uniformly at random a
  current leaf at that depth each time; this reproduces the reference's
  leaf-depth histogram after every split. Judged by the sound test.
  PILOT: no treatment exists, so the pilot null twin is matched to the
  ORACLE's split-depth sequence (stated deviation; forced by the
  control-first rule). PHASE 2: matched to sens, as the spec says.
- CHEAT (round-1 PREREG): success injected into the observable: area
  trace A_cheat(B) = A_oracle(B)^r(cfg) with
  r = 1 - 0.7*(lambdaT - min lambdaT)/(max lambdaT - min lambdaT)
  (r in [0.3, 1], strictly monotone in lambda*T), so gamma_cheat/gamma_oracle = r
  exactly on a power law. Detected iff the evaluator says it meets success.
- stupid_explanations -> checked in evaluate.py: (1) fit-window
  pre-asymptotics: gamma refit on the upper half of the checkpoints;
  (2) tie order: seeds randomise ties; spread across seeds reported;
  (3) oracle exponent vs grid: oracle stopping at depth 12 flagged.

## Success criterion as applied (arm X = sens in phase 2; null/cheat in pilot)

Statistic per config: ratio_X = gamma_X / gamma_oracle, both seed-means
(gamma averaged over the 5 seeds, then divided).
  PC  : for every config with k^-T <= 2^-12 (the finite-T structure is
        below the ground-truth grid, so D_k is the boundary dimension in
        the whole window: k=4 T in {10,20}; k=6,8 T in {5,10,20}; both t),
        |gamma_oracle/gamma_uniform_true - 2/D_k| <= 0.10 * 2/D_k.
        (16 checks, all must pass.) Configs with coarser cut-off are
        excluded because there D_k is not the boundary's dimension in the
        window -- a reading, recorded.
  S1  : ratio_X >= 0.8 at (t=0, T=2) for EVERY k.
  S2  : ratio_X <= 0.6 at (t=30, T=20) for EVERY k.
  S3  : Spearman rho(ratio_X, lambda*T) over all 24 configs <= -0.7.
  Arm meets success iff S1 and S2 and S3. Spec success = PC and arm(sens).
Failure criterion: ratio_sens >= 0.8 at all 24 configs, or any PC config
misses 2/D by > 20%.
Pilot: positive_meets_success = PC; cheat_detected = cheat meets S1-S3;
null_twin_meets_success = null (oracle-matched) meets S1-S3.

## Parameters (from the spec, fixed before running)
k {4,6,8}; T {2,5,10,20}; t {0,30} deg; budgets 64..16384 (9 checkpoints);
seeds 0..4 (spec says 3 for ties; PREREG requires >= 5); truth depth 12;
sound-policy max depth 24 (float safety; recorded if hit); pad 1e-12 (t=30).

## Pilot attempt 1 -> FAIL (PILOT_attempt1.json, pilot_rows_attempt1.jsonl)
positive_meets_success = true (16/16 within 10%, max rel err 0.062);
null_twin_meets_success = false; cheat_detected = FALSE.
Cause: at (k=4, T=2, t=0) the K_2 squares (side 1/16) lie exactly on the
dyadic quadtree, and the interior-overlap ground truth ("interior meets
both K_T and its complement") counts no cell deeper than 4 as boundary.
The oracle's undecided area reaches exactly 0 at B = 64, so gamma_oracle,
the denominator of every S1-S3 ratio, is undefined there; S1 at k = 4
cannot be evaluated for any arm. (k=8, T=2, t=0 also exhausts after 5
checkpoints.) Not a threshold problem; a ground-truth convention problem.

## Repair (the one allowed; controls only, thresholds unchanged)
The oracle's ground truth switches from the interior (measure) reading to
the literal set reading of "truly intersect the boundary": a CLOSED cell
is a boundary cell iff it meets the boundary of K_T (the union of the
perimeters of the level-T kept squares), i.e. iff it meets some level-T
kept square S (closed overlap) and is not contained in the interior of S.
Cells that share an edge or corner with K_T now count. This changes the
positive control (oracle and the uniform ground-truth area) and the CHEAT
(derived from the oracle trace); the null twin is re-matched to the
repaired oracle's split-depth sequence. The sound decided test and the
width signal are NOT changed. No treatment code exists.

## Pilot attempt 2 -> FAIL -> OUTCOME SPEC_UNATTAINABLE (stop)
cheat_detected = true (rho -0.998); null twin does not meet success
(S1 false, rho 0.02); positive control FAILS: k=8, t=0 ratio 1.330 vs
2/D = 1.5 (11.3% > 10%; within 20%). k=4, t=0 1.834 vs 2.0 (8.3%).
Two pilot failures -> SPEC_UNATTAINABLE. No treatment code was written.
