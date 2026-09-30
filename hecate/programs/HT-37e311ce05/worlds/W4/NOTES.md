# HT-37e311ce05 / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and the
round-1 PREREG. Spec source: program.json experiments[W4], mechanisms M3
and M13, lenses L2 and L5. These notes serve as round 1's
IMPLEMENTATION_NOTES.md.

## Spec field -> code

| spec field | code |
|---|---|
| n=64 functions | `N=64` |
| required set R, abs(R)=24 | per seed, `rng.choice(64,24)` |
| host support S_h (12 of R) | per seed, 12 drawn from R; host_i = 1 on S_h, 0 elsewhere |
| w in R^64 starts at 0.5 | `w0 = 0.5*ones(64)` for NULL_TWIN (and later TREATMENT/CONTROL) |
| Benefit = sum_R min(host_i+w_i,1)/24 | `benefit()` |
| cost 0.01 * L1 norm of w | `cost()` |
| 24 measurements y = A Psi_h^T w | A: 24x64 Gaussian N(0,1/24); Psi_h: Q from QR of a 64x64 Gaussian (random orthonormal), columns = basis vectors |
| OMP recovers 6-sparse Psi_h coefficients | `omp(A, y, k=6)`, batched over the population |
| sanction probability = unexplained energy fraction | `p = norm(y - A c_hat)^2 / norm(y)^2`, clipped to [0,1]; p=0 if y=0 |
| random sanctions, per-generation rate matched | each individual sanctioned independently with prob r_g, where r_g = mean sanction probability of the reference (verifiability) arm at generation g, same seed |
| same sanction magnitude | a sanctioned individual has its benefit withheld: fitness = -cost (both arms) |
| mutation-selection hill-climbing, pop 60, 400 gens | truncation: 30 best by fitness are parents; 60 offspring = uniform parent choice + mutation |
| positive control: 6-sparse in Psi_h, sanction rate < 0.05 | POSITIVE_CONTROL arm: clonal init w = Psi_h c, c 6-sparse (random support, Gaussian values), scaled to norm(w) = norm(w0) = 4; evolved under verifiability sanctions |
| s_Psi | number of Psi_h coefficients (sorted by c_j^2 descending) needed to hold >= 90% of norm(w)^2 |
| overlap fraction | norm(w on S_h)^2 / norm(w)^2 (= L2 a.c. mass fraction, energy version) |
| 10 seeds x 2 arms | seeds 0..9 for every arm (>= 5 required; criterion is stated over 10) |

## Parameters (chosen a priori; not in the spec)

- mutation: each gene independently with prob 0.1, add N(0, 0.05^2).
- no clipping: expression is real-valued. Reason: a 6-sparse vector in a
  random orthonormal basis has negative entries, so clipping to >= 0 would
  make the spec's own positive control impossible to construct. Negative
  w is never beneficial (benefit falls, cost rises).
- truncation fraction 0.5, no elitism.
- per-individual observables, then the population MEDIAN at generation
  400 is the seed's value.
- world RNG: `default_rng(seed)`; evolution RNG per arm:
  `default_rng([seed, arm_code])`. Arms of one seed share R, S_h, Psi_h, A.
- threads pinned to 1 (OMP/MKL/OPENBLAS env) so wall ~ CPU; CPU time
  measured by `time.process_time()` and written to the rows.

## Ambiguities and chosen readings

1. "positive control meets the spec's success criterion" (round-2 PREREG).
   The spec's positive_control is a detection statement (6-sparse symbiont,
   sanction rate < 0.05). Reading: positive_meets_success requires BOTH
   (a) the spec's own PC condition: generation-0 mean sanction probability
   of the 6-sparse population < 0.05 in >= 8/10 seeds, AND
   (b) the full success criterion as written with POSITIVE_CONTROL in the
   sanction slot and NULL_TWIN in the null slot.
2. Success criterion, M13: per seed, paired by seed,
   s_Psi(sanction) <= 0.7 * s_Psi(null); count >= 8/10.
   M3: overlap <= 0.05, counted per arm separately; each arm >= 8/10.
   Success = M13 AND M3 (the spec lists both under success).
3. Failure criterion: M13 fails if ratio > 0.9 in >= 5/10; M3 fails if
   overlap > 0.2 in >= 5/10 seeds in either arm.
4. Null twin and control are specified identically ("random sanctions at
   matched rate"). Pilot: no treatment exists, so the NULL_TWIN's rate is
   matched to the only verifiability-sanction arm in the pilot, the
   POSITIVE_CONTROL (same seed, per generation). Phase 2: CONTROL and
   NULL_TWIN are both matched to TREATMENT and differ only in their
   evolution RNG stream; null_twin_meets_success = criterion with
   NULL_TWIN in the sanction slot and CONTROL in the null slot.
   In the pilot, null_twin_meets_success = criterion with NULL_TWIN in the
   sanction slot and a second, independent NULL_TWIN replicate (arm
   NULL_TWIN_B, same construction, different RNG stream) in the null slot.
5. CHEAT: rows whose observables are injected directly (s_Psi = 1,
   overlap = 0.0) with no dynamics. cheat_detected = the evaluator returns
   success with CHEAT in the sanction slot and NULL_TWIN in the null slot.
   Note: M3 also reads the null slot, so the cheat is detected only if the
   real null twin reaches overlap <= 0.05; this is recorded, not fixed.
6. Lens observables recorded but not used for classification:
   L2 a.c. mass fraction (L1 version: sum over S_h of abs(w) / L1 norm);
   L5 ker-A energy fraction of c = Psi_h^T w (projection onto null space
   of A); norm(w)^2 (for stupid explanation 1).

## Seeds

0..9 for all arms.

## Repair log

### Attempt 1 (pilot_rows_attempt1.jsonl, PILOT_attempt1.json): FAIL
- positive control not met: (a) gen-0 sanction rate < 0.05 in 7/10 seeds
  only (OMP, m=24, k=6, missed recovery of the single clonal 6-sparse
  vector in seeds 5, 6, 8); (b) under its own sanctions plus
  benefit/cost selection the w-space mutations made the PC dense in
  Psi_h (s_Psi 28-35, same as the null twin at 28-36; sanction rate climbed
  0 -> ~0.15), so M13 was 0/10 for the PC.
- cheat detected; null twin did not meet the criterion.

### The one repair (controls only; thresholds, world parameters, sanction
### rule, benefit, cost, selection unchanged; written before attempt 2)
POSITIVE_CONTROL becomes a construction with the M13 effect built in:
1. Each of the 60 symbionts starts with its OWN independent 6-sparse
   Psi_h vector (random support, Gaussian values, scaled to norm 4). The spec's
   "a symbiont ... sanction rate < 0.05" is read as the mean over
   symbionts, not one clonal draw. This removes dependence on a single
   OMP draw.
2. PC genomes are parameterised as w = Psi_h[:, J] c_J with each
   individual's 6-element support J inherited; mutation acts on the 6
   coefficients (each mutated, N(0, 0.05^2), so the expected squared
   mutation norm about equals the w-space operator's 64*0.1*0.05^2). Legibility is
   therefore held by design; selection (benefit, cost, verifiability
   sanctions) is free to choose the direction inside the 6-dim span, which
   is what decides whether M3 (overlap <= 0.05) can also hold.
NULL_TWIN / NULL_TWIN_B / CHEAT unchanged (NULL_TWIN still matched to the
PC's per-generation rate). If attempt 2 fails -> SPEC_UNATTAINABLE.

### Attempt 2 (pilot_rows.jsonl, PILOT.json): FAIL -> SPEC_UNATTAINABLE
- PC gen-0 sanction rate < 0.05 in 10/10 seeds; M13 met 10/10 (s_Psi 3-4
  vs null 26-36); M3 met 0/10 (PC overlap 0.097-0.317; null twin 10/10
  <= 0.05). Cheat detected; null twin did not meet success (M13 ratio
  0.94-1.18 vs its B replicate).
- Second pilot failure -> OUTCOME.json outcome SPEC_UNATTAINABLE. Phase 2
  not built; world.py/evaluate.py do not exist.
