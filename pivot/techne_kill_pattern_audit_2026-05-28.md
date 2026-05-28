# Kill Pattern Audit — 2026-05-28
**Stage 27 of the substrate expansion arc**

## Headline

**66 distinct kill_patterns observed in the live corpus** (5 recent
batches, 150K records sampled). But once we collapse parametrized
patterns into mechanisms, only **~10-12 distinct falsification
mechanisms** are represented.

## Distribution by mechanism class

### Class 1: relation_violated (~14 patterns, dominant volume)
The top 14 patterns are all of shape
`<gen>_<relation>_violated` where `<gen> ∈ {a1, f2}` and
`<relation> ∈ {equal, equal_mod_2, divides, abs_diff_le_3}`.
This is ONE mechanism (relation fails on a specific pair),
fired by two gens with multiple relation types.

    a1_relation_equal_violated           2,904
    f2_anti_freq_equal_violated          2,786
    a1_relation_abs_diff_le_3_violated   2,183
    f2_anti_freq_abs_diff_le_3_violated  2,082
    a1_relation_divides_violated         1,868
    f2_anti_freq_divides_violated        1,605
    f2_anti_freq_equal_mod_2_violated    1,483
    a1_relation_equal_mod_2_violated     1,397
    + 6 similar

### Class 2: strengthening_fails (~7 patterns)
c5 family — "the relation holds at level X but fails when
strengthened to Y." Distinguished by source/target relation pair:

    c5_strengthening_equal_mod_2_to_equal_fails   1,646
    c5_strengthening_divides_to_equal_fails       1,242
    c5_strengthening_abs_diff_le_3_to_le_1_fails    300
    + 4 more strengthening variants

### Class 3: twist_breaks_invariant (~50 parametrized variants)
g1 family — `g1_twist_breaks_<invariant>_at_j=<value>`.
Distinct values of j-invariant generate ~50 distinct patterns
but the MECHANISM is the same: applying a Galois twist breaks
one of {rank, torsion, conductor, tamagawa_product}.

Real distinct mechanism count here: **4** (one per invariant).

### Class 4: obstruction_refuted_by_witness (1 pattern, NEW)
l1 emitted 4 obstruction-refutations. Clean single mechanism:
the bounded search found a witness, refuting the negative
existential.

### Class 5: minimal_counterexample_found (0 observed in sample)
m1 emits this when its enumeration finds a violator. None in
the 150K sample due to sampling, but the mechanism exists.

## Collapse to actual mechanism count

    1. relation_violated  (any specific catalog relation fails)
    2. strengthening_fails (relation widening direction tested)
    3. twist_breaks (Galois twist destroys an invariant)
    4. obstruction_refuted_by_witness (bounded search found counterexample)
    5. minimal_counterexample_found (extremal enumeration found violator)

**Real mechanism count: 5.**

The other 61 patterns are parametric variants of these 5.

## What's MISSING

Substrate has zero kill_patterns for these well-known
falsification mechanisms:

### Mechanism 6: monotonicity_break
"Function f should be monotone on the catalog; here's a triple
(X1, X2, X3) where f violates monotonicity."

### Mechanism 7: symmetry_break
"Property P should be invariant under operation O; here's an
object where O(X) has P but X doesn't (or vice versa)."

### Mechanism 8: boundary_kill
"Claim holds for parameter < N, fails exactly at parameter = N."

### Mechanism 9: scale_kill
"Claim holds for small objects, fails at larger objects in a
catalog-size-dependent way."

### Mechanism 10: type_mismatch
"Operation applied to object of incompatible type; substrate
should reject."

### Mechanism 11: computation_diverged
"Numerical method failed to converge (relevant to a4
symbolic regression and a2 statistical correlation)."

### Mechanism 12: definition_mismatch
"Two definitions of 'same' thing disagree on this object —
the disagreement IS the falsification."

### Mechanism 13: consistency_violation
"X holds, Y holds, but X∧Y doesn't (joint failure)."

### Mechanism 14: cardinality_mismatch
"Expected |S| = N counted objects, found |S| ≠ N."

## Targeted new gen design

To diversify kill_patterns, the new gen should INTENTIONALLY
hit one or more of the missing mechanisms by construction.

**Recommended new gen**: `cc1_monotonicity_break`

- Take an invariant f and an ordering relation R on catalog
  objects (e.g., conductor ordering for ECs)
- Test whether f is monotone (or has any specified pattern)
  under R
- Emit kill_pattern `monotonicity_violated_at_<X,Y>` when found

This is cheap (catalog enumeration), produces real kills with
witnesses, and contributes a never-before-seen kill_pattern
class.

## Discipline for the 15 stub → real upgrades

Each upgraded gen MUST emit a distinct, named kill_pattern when
it emits REJECTED records. The naming convention:

    <gid>_<mechanism>_<specifier>

Examples (one per upgrade):
- r1: `r1_subset_relation_violated_at_<element>`
- s1: `s1_triangle_inequality_broken_on_triple_<X,Y,Z>`
- q1: `q1_modular_structure_changes_at_p<value>`
- t1: `t1_multi_hop_break_at_step_<n>`
- w1: `w1_closure_violated_by_<X>`
- u1: `u1_quantifier_swap_distinguishes`
- v1: `v1_perturbation_breaks_property_<P>`
- x1: `x1_partial_view_inflation_<scope>`
- y1: `y1_analogy_breaks_at_<axis>`
- z1: `z1_operators_dont_commute_on_<X>`
- aa1: `aa1_confidence_miscalibrated_<direction>`
- bb1: `bb1_false_dichotomy_revealed_<n_categories>`
- l2 / m2 / p1: less obvious — these emit lemmas, not kills

This will roughly TRIPLE the named-kill-pattern count when the
15 stubs go real with this discipline.

## Expected outcome after 15 stub → real

- Distinct mechanism classes: 5 → ~17
- Distinct kill_patterns: 66 → ~150+
- Per-Learner-class label diversity: 5 → ~20

This moves the falsification-routing training signal from
"binary kill/not-kill" toward something the Learner can
actually classify with structure.
