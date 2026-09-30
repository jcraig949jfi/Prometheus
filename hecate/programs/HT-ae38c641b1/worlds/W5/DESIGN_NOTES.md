# W5 -- does a box verifier imprint its axes on evolved dynamics? (M2, M14; lenses L3, L2)

Generator: Pass 3 v2 (prompt pass3_v2.md, sha256 2adcfc8d...d461). Layer: implemented
candidate design only; no treatment exists. Nothing here is an observation about the
treatment.

## What the world tests
M2's stated observable: when survival needs a proof from a budgeted box-domain verifier,
the principal directions of evolved maps align with the domain axes (4-fold, mod 90 deg),
and a rotated domain rotates the alignment. S1 = alignment under the unrotated verifier,
S2 = alignment to the rotated axes under a verifier rotated by 22.5 deg (the angle at which
4-fold alignment to the world axes and to the domain axes are orthogonal: cos(4*22.5) = 0).

## Why it can fail cleanly
Before running anything I worked out that the box verifier's invariance group is the
signed permutations, which include the 45-deg diagonal reflections. For symmetric maps
with same-sign eigenvalues rho(|A|) = rho(A) at EVERY angle, and for a rank-1 symmetric
map the inductive-box condition is the same at 0 and 45 deg and worst near 22.5 deg. So
the physics I expect gives either no 4-fold imprint or an 8-fold one (axes AND diagonals),
which the 4-fold statistic reads as roughly zero. The success clauses test M2 as written;
A8 and rho(|A|)/rho(A) are preregistered diagnostics so a NULL on S1 can still say what,
if anything, was imprinted. This is an expectation, not an observation.

## How it avoids the earlier failures
- W4 deferred its map family and decided test to another world: this spec is
  self-contained (verifier, task, GA, random streams all stated).
- W3's observable fired on the control (continuous variation counted as breakpoints):
  here the twin was run and reads 0.003 / -0.039 against a threshold of 0.40.
- W4's positive control depended on a grid-alignment convention: no grids here; the only
  anisotropy in the world is the verifier's domain.
- Unattainable thresholds: every success clause was checked on the controls before
  freezing (ATTAINABILITY.json).

## Ambiguities resolved
1. "Principal directions": M2 says eigenvectors; evolved non-normal maps can have complex
   eigenvectors, so I use the top RIGHT-SINGULAR vector (allowed by L3), weighted by
   w = (s1-s2)/(s1+s2) so near-isotropic maps (undefined direction) count for nothing.
2. Clonal drift: a (mu+lambda) population becomes near-clonal, so per-seed A4 is roughly
   cos(4*random angle) under the null (per-seed SD 0.58). I use the SIGNED statistic
   averaged over 20 seeds (SD of the mean 0.13), not R4 = |mean| per seed, which would be
   large under the null. Threshold 0.40 = 3.1 null SDs.
3. Null-twin acceptance matching: the twin must match the compared arm's acceptance
   schedule, but no treatment may exist at generation time; in controls.py it is matched
   to POSITIVE_CONTROL of the same seed. In the probe it must be matched to V (S1) and
   V_rot (S2). A twin's A4 does not depend on which schedule it copies except through
   drift, which is covered by the 20-seed average.
4. "Cheat detected" = the clause evaluator reports success when success is injected
   (every final map conjugated onto the domain axis): A4 = 1.0 for S1 and S2.
5. Task choice: revision 0 used affine maps and a spread task; that task was solved with
   A ~ 0 and b_1 = -b_2 (orbit hopping between two antipodal points), leaving the
   observable unselected. Revision 1 uses linear maps only and a persistence task with a
   rotation-invariant shape penalty, so the linear part is what every gate and the task
   act on. Recorded in revisions.json; rev0 files in _rev0/.
6. Values between the F1 and S1 thresholds (0.15 to 0.40) are INCONCLUSIVE.
7. Budget: rev0 alone cost 6.2 core-min, over the 5 core-min budget; the frozen controls
   cost 24 core-s. The overrun is recorded in ATTAINABILITY.json.
