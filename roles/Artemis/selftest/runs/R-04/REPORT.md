# REPORT

## 1. WHAT I SET OUT TO TEST

Can "not a member of the closure of a frozen primitive set" serve as a preregistered
observable in TINYPROG (the Z6^4 program world)? Such an observable would fire on a mechanism
nobody named in advance, and it would not fire on deeper compositions, on budget effects, or on
old primitives under new names. There were two parts. (a) Does the closure of "all primitives
minus one" reach a real fixed point on the fixed probe set within a CPU budget, so that labels
stop depending on depth? The cases were: remove vec-multiply and double (the two extreme
label-noise cases), plus rotate as the control. (b) If it does, does the frozen membership test
reject compositions and relabels while firing on genuinely new operators?

## 2. WHAT I DID

Inputs: repo commit ca189b020. I exported aporia/lot/world3.py and aporia/q100/probes/ with
git archive into work/R-04/src. I compared against the published numbers in
aporia/q100/dossiers/Q045_search_vs_representation.md sections 9-10 @230d17644. All code is
in /home/jcraig/artemis-selftest/work/R-04 and every script ran with python3 and numpy.

- Method change. Before running, I judged that the proposed method (grow the size bound K
  until one size step adds nothing) could not work. The fixed point turned out to hold about
  1.6e11 signatures for "minus vec-multiply" and 9.4e11 for the full set. The existing probes
  cap out at 3e6 signatures. So the size-indexed loop would hit its cap, and the stated kill rule
  would fire because of the budget, not because of the question (a false KILL).
- Exact closure (exact_closure.py). I used an exact, depth-free closure instead:
  - Vec-add is present, so the reachable V-signatures form an additive subgroup of Z6^24. By the
    Chinese remainder theorem this splits exactly into a GF(2) subspace and a GF(3) subspace. Each
    subspace is the closure of the mod-q system.
  - Each primitive then becomes a linear-algebra closure rule:
    - rotate and reverse: invariance under the permutation.
    - increment: adds the all-ones vector.
    - double: automatic.
    - vec-multiply: closure under products of basis vectors.
    - sum: a linear image.
    - product: the exact span of the image of a degree-4 polynomial map, taken from the reduced
      (x^q = x) coefficient vectors.
    - scalar-add and scalar-multiply: broadcast and module action by span(S).
  - These rules are iterated to a fixed point.
  - The method does not cover removing vec-add itself.
- Validation, three ways.
  1. Soundness against the repo's own enumerator. Every V-signature from build_closure at
     depth 5 (full set) and depth 7 (each removal) must be a member. Script:
     step1_fixedpoint.py.
  2. Brute-force saturation with no depth bound, in 8 small worlds (width 1-2, 2-4 probes), for
     the full set and every removal. Script: validate_bruteforce.py.
  3. Constructive witnesses (witness.py, step1b_witness.py). I re-ran the closure so that
     every added vector is the evaluated signature of an explicit program over the reduced
     primitive list. Then, for every depth-5 "representation failure" target that the closure
     calls reachable, I built a program and checked that its evaluated signature matches exactly.
  - I also ran a random invariance self-test: members pushed through every primitive must stay
    members.
- Probe dependence (probe_scaling.py). I repeated the closure for probe sets of 6, 12, 24
  and 48 inputs, each a superset of the canonical 6. Above dimension 24 the product-span is
  sampled, so it is probabilistic.
- Plant test (step2_plant.py). This used a fixed seed. IT WAS NOT BLIND: I wrote the
  targets myself. For each of the three removals:
  - 60 random deep compositions of the reduced set (size 8-24).
  - 60 relabels: programs using a macro slot that is a composition of the reduced set, such as
    neg, twice (= double), rot2, cyclic-sum and inc-after-add.
  - 60 random full-set programs that use the removed primitive.
  - 9 new operators applied bare, plus 8 random programs containing each. The operators were
    square, sort, max, is-zero, broadcast-coordinate-0, swap-first-two, floor-halve, and
    vec-multiply and rotate under new names.
  - 2-3 near-misses, which are syntactically new but extensionally old: cube (the identity on
    Z6), vmul(X, ones), vmul(X, 2s) = double, and rot^4.
  - I compared the frozen exact detector with the depth-5 detector that produced the existing
    labels. I also scored the bare operators against 48-probe closures.

## 3. RESULT

Fixed point. It is reached exactly, in under a second per primitive set. The number of
closure iterations is 2.

Dimensions over (GF2, GF3), out of 24 each:

| Primitive set      | Dimensions | Closure size                 |
|--------------------|------------|------------------------------|
| Full set           | (16, 15)   | 9.40e11                      |
| Minus vec-multiply | (15, 14)   | 1.57e11                      |
| Minus rotate       | (10, 11)   | 1.81e8                       |
| Minus double       | (16, 15)   | identical to the full set    |

Validation.
- 0 soundness violations. This covers 3,502 depth-5 full signatures and 17k-65k depth-7
  signatures per removal.
- Brute-force saturation agreed in 80 of 80 cases, with 0 mismatches.
- 0 invariance violations.
- Every one of 7,339 membership claims was confirmed by an explicit, evaluated program, with 0
  failures.

Rerun of the published "floor" table. The floor is the fraction of the depth-5 lost class
that is truly unreachable at the fixed point, on the canonical 6 probes.

| Removed primitive | Floor at the fixed point | Published floor (depth 8) |
|-------------------|--------------------------|---------------------------|
| rotate            | 98.8%                    | 99.2%                     |
| increment         | 73.5%                    | 73.8%                     |
| vec-multiply      | 35.6%                    | 93.4%                     |
| reverse           | 0%                       | 93.2%                     |
| sum               | 0%                       | 82.3%                     |
| product           | 0%                       | 59.3%                     |
| scalar-add        | 0%                       | 30.3%                     |
| scalar-multiply   | 0%                       | 27.4%                     |
| double            | 0%                       | 4.2%                      |

- Six of the nine primitives are fully redundant. Removing any one of them changes the
  closure not at all.
- Sum, product, scalar-add and scalar-multiply are redundant at every probe size I tried
  (6-48). They are genuinely definable; for example, sum-broadcast is v + rot v + rot^2 v +
  rot^3 v.
- Reverse is redundant only on the 6 canonical probes. At 12 or more probes it loses
  (8, 0) or more dimensions, so this is probe aliasing.
- For vec-multiply, 1,376 of the 2,136 depth-5 "representation failures" are reachable. The
  published depth-10 figure found only 223 of these.
- The witness programs are tree size about 1e5 (median; minimum 338). These witnesses are not
  minimal, so the true minimum could be smaller. This explains why tree-size enumeration saw
  "collapsing marginal yield" long before the residue was exhausted.
- So the published "89.6% residue / proper subalgebra" reading is wrong for vec-multiply:
  most of that residue is depth and cost.
- The same non-membership gives the missing certificate. For each truly unreachable target
  there is an explicit linear functional mod 2 or mod 3 that vanishes on the closure and not on
  the target. That is an invariant proving a proper subalgebra, exactly for rotate (dims drop
  (6, 4)), increment and vec-multiply.

Plant test (not blind). Results on the canonical 6 probes, exact detector vs depth-5
detector:

| Target class             | Exact detector fires           | Depth-5 detector fires |
|--------------------------|--------------------------------|------------------------|
| Deep compositions, n=180 | 0% in all three removals       | 53-67%                 |
| Relabels, n=180          | 0%                             | 35-48%                 |
| Near-misses, n=8         | 0%                             | 0%                     |

- Sensitivity on 6 probes is poor.
  - Bare new operators fire 4/9 (minus vec-multiply), 6/9 (minus rotate) and 2/9 (minus
    double).
  - Bare vmul(X, inc X) does not fire against "minus vec-multiply" on 6 probes. Removing
    vec-multiply costs only one dimension per prime there.
  - Programs that use the removed primitive fire 22% (vec-multiply), 65% (rotate) and 0%
    (double). The 0% is correct, because double is redundant.
- On 48 probes, the bare operator verdicts match my hand ground truth in 30 of 30 cases.
  - Every non-definable operator fires: sort, max, is-zero, broadcast-coordinate-0, swap, halve,
    and square when vec-multiply is absent.
  - Every definable one is silent: square when vec-multiply is present, the renamed primitive
    when the original is still present, and cube.
  - The ground truth came from CRT-separability and rotation-centre equivariance arguments. It
    was not written blind.

Conclusion. Non-membership in an exactly computed closure is a preregistrable detector, and
it has no depth, budget or relabelling dependence. That dependence was an artefact of tree-size
enumeration. What it does depend on is the probe set: 6 probes are too few to see several
genuinely new mechanisms. So the probe set, not the depth, must be frozen and preregistered.

## 4. DID IT RESOLVE THE QUESTION

PARTLY.
- The convergence part is resolved, yes. There is an exact fixed point, certified in both
  directions, cheap to compute, and with no depth dependence.
- The "rejects compositions and relabels" half of the detector part is resolved on 368
  mechanical targets.
- The blind plant test was not done. It needs a second author who has not seen the closure,
  and my targets and ground truth were written by me.
- Sensitivity is only shown to be probe-set dependent. It was adequate at 48 probes on my own
  small operator set.
- The method does not cover removing vec-add. It also does not cover non-polynomial primitives
  unless their closure rule is derived.
- I did not address the question of an evolved substrate with no declared primitive list. The
  construction needs declared primitives with known algebraic structure.

## 5. CONSEQUENCES

- Harness defect. The proposed size-indexed fixed-point loop is the wrong instrument. It
  cannot terminate at the stated cap (1.6e11 signatures), so its kill rule would issue a false
  KILL. It should be replaced by the algebraic saturation here (about 200 lines, seconds of
  CPU).
- False premise / correction of prior results. The published leave-one-out floor table and
  the depth-10 "89.6% residue" argument for vec-multiply are largely depth/cost artefacts.
  - Six of the nine primitives are exactly redundant on the canonical probes.
  - The vec-multiply floor is 35.6%, not 89-93%.
  - "Collapsing marginal yield" was shown not to be evidence of a floor.
  - The positive control (double) and the negative control (rotate) still come out right. The
    middle of the table does not.
  - Who should know: the owner of the search-vs-representation dossier and its probes (Aporia). This also matters to
    anyone who built task populations or pass thresholds on those labels.
- New positive result. There is now an exact membership test for this world, with a
  certificate in both directions: a program witness for members, and a mod-2 or mod-3 parity
  functional for non-members. It is the invariant the dossier said was missing.
- What must change in any preregistration. The frozen probe set is the free parameter, and
  it must be preregistered with the detector. The canonical 6 probes alias reverse, and they hide
  most of vec-multiply.
- Suggested next step. A blind second-seat plant test at 48 or more probes, plus a
  hidden-transformation world built on this detector.

## 6. COST

- Wall time: about 1.5 hours of my own work.
- CPU: about 15 minutes in total. That includes a brute-force validation run of about 10 CPU
  minutes that I stopped and re-ran smaller. Peak memory was about 120 MB, with one process at a
  time.
- Not done:
  - the blind second-seat plant test;
  - removing vec-add;
  - minimal-size witnesses;
  - the exact (unsampled) product-span above dimension 24;
  - full-domain (1,296-input) closures;
  - any transfer to an evolved substrate.
