# DESIGN_P -- a coverage-controlled alien family (induction vs coverage)

Date: 2026-09-30. Hecate, DESIGN ONLY (no model calls, no subject runs, no git
writes); draft for a future prereg -- under the current work order Hecate starts
no new program. Prototype: hecate/alien/coverage_family_DRAFT.py (pure stdlib;
imports nothing from the frozen pilot and reads no pilot data).
Motivation (INV_E): on table-driven aliens, Claude's accuracy on uncovered entries
equals a coverage oracle (pooled II_ocd -0.08). Induction appeared only for
architecture and for compact parametric laws (poly_sym, shear, vm affine). INV_E
could not tell the two apart cleanly, because in the pilot coverage was
generator luck, laws were sometimes textbook, and the coverage oracle (OCD) was
used only after the fact. This family fixes coverage by construction and holds
everything constant except whether the unseen entries follow a law.

## 1. System (one architecture for every member)

Ring of 6 sites with values in Z_7. Update rule: x_i' = T[x_i][x_{i+1 mod 6}],
with ONE shared 7x7 table T (49 keys). Each component has exactly one witness
key, (x_i, x_{i+1}). One observed transition reveals the VALUE of every key its
source state consults. So covered == revealed, which removes INV_E caveat 2
("consulted is not revealed"). The state space is 7^6 = 117649 states.
Presentation: the architecture is disclosed in the primary arm ("each site's
next value is one fixed function of its own value and its right neighbour's
value, the same function at every site"). INV_E showed that architecture is
induced separately, and this arm isolates entry-level induction. An
undisclosed arm is optional and secondary. Observations: 40 single-step
transitions (source -> next), with no trajectories, so next states never
become sources. Task: write step() code (T5-style, sandboxed), scored on 200
held-out states.

## 2. Matched pair (LAW, ARB) and the scoring-only SHADOW

All members of a pair share the same architecture, the same revealed key set R
with |R| = m exactly, the same 40 source states and the same 200 eval states.
  LAW    T follows a hidden compact law (section 3). The unseen set U = keys not
         in R, so |U| = 49 - m.
  ARB    R-values are a random shuffle of LAW's R-values, and U-values are a
         random shuffle of LAW's U-values. The draw is accepted only if (a) the
         count of U entries with T=a, T=b and T=0 matches LAW exactly, and (b)
         no library class and no generating class fits ARB's R-values.
  SHADOW Truth = LAW on R and ARB on U. The LAW run is rescored against it at
         no cost and must come out at chance. This is a scoring-leak control.
Deviation from the brief's "unseen entries i.i.d.": i.i.d.-uniform U-values let
a histogram learner (predict the mode of the observed values) or a default
learner score differently on LAW and ARB without any induction. An exchangeable
shuffle with matched histogram and matched defaults makes those learners tie
EXACTLY. The self-test verifies this: OCD_a, OCD_b, OCD_0 and MODE are
identical on LAW and ARB in every pair. Within U the values are still
exchangeable, so no position carries information.
Coverage levels: m = 25 (f = 25/49 = 0.510) and m = 37 (37/49 = 0.755); exact
50/75% is impossible with 49 keys, and Z_7 is kept because a field makes linear
identifiability exact. f is reported as a Fraction.

## 3. Generator algorithm (make_pair; deterministic, random.Random(seed))

repeat (<= 400 tries):
 1. Draw the law.
    ALIEN classes, which lie outside the library:
      2R  T = f(L1) + g(L2) mod 7. L1 and L2 are two distinct projective
          directions (alpha*a + beta*b) out of the 8, and the pair {a, b}
          (= separable, which is a library class) is excluded. f and g are
          arbitrary non-constant 7-value lookup tables. 13 effective parameters.
      3R  T = f(L1) + g(L2) + h(L3) with three directions. 19 effective
          parameters.
    LIB classes, which form the positive-control stratum and lie inside the
    library: affine, a degree-2 polynomial, or a named op (max, min, absdiff,
    fmean, pow, lt) composed with an affine map u*op + v.
 2. R = a uniform m-subset of the 49 keys.
 3. Sources: 40 distinct closed 6-walks in the digraph R (arc a->b iff (a,b) is
    in R), seeded arc by arc until every R key has appeared at >= 2 sites.
    The draw is rejected if some arc lies on no closed 6-walk.
 4. Identifiability certificate. Fit the GENERATING CLASS (the union over all of
    its direction combos, solved by linear algebra mod 7) to LAW on R. Every
    u in U must be determined: all consistent combos agree, and the agreed
    value is T[u]. Otherwise reject. So the law fixes every unseen entry.
 5. Not-alien filter (ALIEN only). Run LAWFIT (section 5) on LAW's R. If it gets
    more U keys right than OCD_a does (an integer comparison), reject the draw
    as NOT_ALIEN and log the library class that solved it. For LIB, LAWFIT must
    solve every U key.
 6. Build ARB (section 2) with up to 3000 shuffles. If no shuffle matches,
    reject the draw.
 7. Eval set: 200 uniform states that are not sources. Every u in U must occur
    >= 5 times as a component key.
verify_pair (fail-closed): seen keys == R; |R| = m, (R, U) a partition; sources
distinct and disjoint from eval; equal R/U histograms; equal default counts.

## 4. Metrics (the INV_E definitions, made exact)

Unit = one component of an eval state. Uncovered = its key is in U.
  UCA        uncovered-component accuracy = right / n (reported as a Fraction)
  KUA count  the number of u in U that the subject predicts right at EVERY eval
             occurrence. This is the decision metric. Components that share a
             key are perfectly correlated, so the key, not the component, is
             the independent unit.
  II_ocd     KUA(subject) - KUA(OCD_a) on the same member. By construction
             OCD_a(LAW) == OCD_a(ARB).
  pair d     KUA_LAW - KUA_ARB, an integer.
  covered    covered-component accuracy = the engagement check.
Every rule compares (cross-multiplied) integers; no float thresholds (AUDIT_A F01).

## 5. Controls and comparators

  ORACLE    true table; 1.000 everywhere; must (and does) trip the leak alarm.
  OCD_a/b/0 coverage oracle: true architecture + seen values + default (own /
            neighbour / 0) for unseen keys; ties LAW vs ARB by construction.
  MODE      predicts the most frequent observed value. Ties by construction.
  LOCAL     unseen key <- cyclically nearest seen key in its row (reported only).
  LAWFIT    the law-fitting baseline over a frozen LIBRARY, simplest class
            first: const, affine, poly2, poly3, 6 named ops with affine output,
            the 8 single ridges f(L), separable f(a)+g(b), antisymmetric,
            symmetric, then Latin-square completion by elimination. A class
            predicts u only if it is consistent with all of R AND determines u.
  INDUCER   LAWFIT + the 2R/3R generating classes (class oracle; positive ctrl).
Detecting and rejecting "not alien enough":
 (i)   Per-draw filter (step 5): LAWFIT beats OCD_a on U -> reject.
 (ii)  Detector validation: deliberately library-solvable "aliens" must never
       be accepted. 2R_AXES (= sep) and 1R_DEGEN (= one ridge) were accepted
       0 times in 400 tries each, and every rejection named the solving class.
 (iii) Class rule: if more than 50% of a class's draws are rejected as
       NOT_ALIEN, the class is library-adjacent and dropped. In the self-test,
       2R and 3R had 0 NOT_ALIEN rejections.
 (iv)  The library is frozen at prereg. If a later reviewer adds a class, it is
       applied retroactively, and pairs it would have rejected are reported
       both ways (included and excluded). "Alien" is RELATIVE to this declared
       library, and that caveat is stated in every verdict.
Negative and cheat controls:
  LEAK (permutation). ARB and SHADOW U-values are exchangeable. Re-shuffle the
       U-values 2000 times (seeded) and count the shuffles that match the
       subject's per-key predictions at least as often as the truth does. If
       that count is <= 2, flag the pair. Two or more flagged pairs ->
       INVALID. A first version used a Bin(|U|, 1/7) bound and falsely flagged
       MODE on skewed LIB histograms; the permutation version fixes this.
  SHADOW at chance: the scorer is not reading LAW truth into ARB. Engagement:
  20*covered_right >= 19*covered_n, else INDETERMINATE.
  Blinding: LAW/ARB in separate sessions, random order, opaque IDs; no U value
  is in any prompt (next states are values of R keys only).

## 6. Decision rules (exact counts; primary = ALIEN stratum pooled over m)

  d_j = KUA_LAW - KUA_ARB. n+ = #{d_j > 0}, n- = #{d_j < 0}; ties are dropped.
  crit(n) = the least k with 100 * sum_{i>=k} C(n,i) <= 2^n (one-sided sign
  test, alpha = 0.01, exact integers).
  INVALID        if OCD_a(LAW) != OCD_a(ARB) in any pair, or >= 2 leak flags.
  INDETERMINATE  if engagement fails.
  INDUCTION      if n+ >= crit(n+ + n-) AND 4 * sum d_j >= sum |U_j|. That is,
                 at least 25% of all unseen keys are recovered beyond coverage,
                 which corresponds to cracking roughly 30% of the laws.
  NO_INDUCTION   if n+ < crit AND 20 * sum d_j <= sum |U_j| (at most 5% excess).
                 Falsification needs demonstrated use, so this verdict is
                 reportable only if the instrument controls pass (INDUCER ->
                 INDUCTION, OCD/MODE -> exact ties).
  else           INDETERMINATE.
  LIB gets the same rule. Joint reading: ALIEN_INDUCTION; TEXTBOOK_ONLY (LIB
  yes, ALIEN NO_INDUCTION); COVERAGE_ONLY (neither); else INDETERMINATE.
  Per-m and per-class results are descriptive (the coverage curve).
## 7. Sample size and power

A subject that cracks a law gives d of about 6/7 * |U| > 0. A subject that does
not crack it gives a tie (when it uses defaults) or a sign-symmetric d. If q is
the crack rate and every non-crack is untied, p = P(d > 0 | d != 0) = q +
(1-q)/2, which is a lower bound. Exact power from the self-test (alpha = 0.01):
  n=24: crit 19; power 0.23 / 0.66 / 0.97 at p = 0.7 / 0.8 / 0.9
  n=48: crit 33; power 0.64 / 0.98 / 1.00
Proposal: 24 ALIEN pairs per m (16 x 2R and 8 x 3R) plus 12 LIB pairs per m.
That is 48 ALIEN pairs (primary, n = 48), 72 pairs in total, and 144 subject
runs, comparable to the 100-system pilot. At q = 0.4 (p >= 0.7) power is
>= 0.64. At q >= 0.6 it is >= 0.98. The effect floor (25%) is the binding
constraint below q ~ 0.3. Per-m tests (n = 24) are secondary and
underpowered for p < 0.8.
## 8. Self-test output (python -m hecate.alien.coverage_family_DRAFT; 51 s)

Abridged: 36 per-pair lines condensed to two; reason lists truncated.
  pairs 0-17  m=25: 8x2R, 4x3R, 6xLIB  coverage=25/49 (=0.510) |U|=24 verify=PASS
  pairs 18-35 m=37: 8x2R, 4x3R, 6xLIB  coverage=37/49 (=0.755) |U|=12 verify=PASS
  generator failures: 0
  rejection reasons (m, class, reason): count
    (25, '2R', 'R_not_walk_realizable'): 1
    (25, '2R', 'U_not_determined_by_class'): 1
    (25, 'LIB_poly2', 'R_not_walk_realizable'): 1
    (37, 'LIB_op', 'ARB_unmatchable'): 1
NOT-ALIEN detector (deliberately library-solvable 'aliens' must be rejected):
  2R_AXES  m=25 accepted=False NOT_ALIEN rejections=346 reasons=[..sep, R_not_walk..]
  2R_AXES  m=37 accepted=False NOT_ALIEN rejections=400 reasons=[..sep]
  1R_DEGEN m=25 accepted=False NOT_ALIEN rejections=276 reasons=[..ridge(*)..]
  1R_DEGEN m=37 accepted=False NOT_ALIEN rejections=399 reasons=[..poly3, ridge(*)..]
Learner scores (key-level, summed: LAW / ARB / SHADOW | comp-unc LAW ARB | verdict)
  ORACLE  ALIEN 432/432 432  82 | 1.000 1.000 | INVALID(leak_alarm=24)
  ORACLE  LIB   216/216 216  48 | 1.000 1.000 | INVALID(leak_alarm=12)
  OCD_a   ALIEN  56/432  56  56 | 0.132 0.128 | NO_INDUCTION n+=0 n-=0 sum_d=0
  OCD_a   LIB    25/216  25  25 | 0.115 0.110 | NO_INDUCTION sum_d=0
  OCD_b/0 ALIEN  60, 64/432 on LAW == ARB == SHADOW | NO_INDUCTION sum_d=0
  MODE    ALIEN  60/432  60  60 | 0.139 0.141 | NO_INDUCTION sum_d=0
  MODE    LIB    44/216  44  44 | 0.201 0.200 | NO_INDUCTION sum_d=0
  LOCAL   ALIEN  50/432  64  64 | 0.118 0.143 | NO_INDUCTION n+=5 n-=11 sum_d=-14
  LAWFIT  ALIEN  56/432  56  56 | 0.132 0.128 | NO_INDUCTION sum_d=0
  LAWFIT  LIB   216/216  25  48 | 1.000 0.110 | INDUCTION n+=12 crit=11 sum_d=191/216
  INDUCER ALIEN 432/432  56  82 | 1.000 0.128 | INDUCTION n+=24 crit=19 sum_d=376/432
  INDUCER LIB   216/216  25  48 | 1.000 0.110 | INDUCTION n+=12 crit=11 sum_d=191/216
Construction checks (all True): OCD_a/b/0 and MODE identical LAW vs ARB in
  every pair; LAWFIT == OCD_a on accepted ALIEN LAW; LAWFIT solves LIB; INDUCER
  solves ALIEN.
Leak control (reads the true table of the member it runs on): INVALID(leak_alarm=24)
Power: n=12/16/24/32/48 -> crit 11/14/19/24/33, size <= .0066 (power in s.7)

Reading: coverage/default/histogram learners tie exactly; the library solves
LIB but adds nothing on ALIEN; the class oracle gets INDUCTION (24/24 pairs); a
table-reading cheat is flagged on every pair; SHADOW stays unflagged (the
permutation test, not the raw 82 vs 56, is the arbiter).
## 9. Open issues before any prereg

- "Alien" means outside a declared finite library. 2R/3R are ridge sums, and a
  reviewer may say they are nameable. The remedy is (iv): extend the library
  and report both ways. Do not claim absolute alienness.
- KUA needs per-key consistency (right at only some occurrences scores 0), so
  UCA is reported beside it. Disclosed architecture differs from the pilot;
  the undisclosed arm measures that confound (secondary).
- 3R at m=25 has a thin determinacy margin (19 params vs 25 equations); expect
  more rejections at scale and log them. Power assumes independent pairs (one
  session per member). Simulated learners only; no subject has seen this family.
