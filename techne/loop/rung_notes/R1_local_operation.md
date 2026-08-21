# Rung R1 — Local Operation · Circuit Study (Loop pass 1, cycle 002)

**Canon:** Band E. R1 = applies one known operation correctly. Kill tests: survives variable
rename (else R0); dies on transfer probes needing an operation it was not given, and on
chains needing supplied ORDER (that is R2).

## 1. Circuits for R1

- **C-R1a: guarded template-rule circuit (built this cycle).** A rule =
  (template AST with typed slots, legality guard, answer function on slot bindings).
  Matching = AST unification against the template after alpha-canonicalization. Applying =
  evaluate the answer function on the matched literals, IF the guard passes. "One known
  operation" is exactly one rule firing once.
- **C-R1b: e-graph single-rewrite.** Same content in egg/egraph vocabulary: one rewrite rule,
  one application, extract. Heavier machinery for the same rung; noted for later rungs where
  rule COMPOSITION (R2) and equivalence saturation start paying rent.
- **C-R1c: learned template regressor** (fit the answer function from examples instead of
  being given it). Deliberately NOT built: learning the rule is a different capability than
  applying it, and mixing them re-creates the exact ambiguity the ladder exists to split.

## 2. Pressure test of the cycle-001 AST-congruence claim

Claim was: rung = coarseness of the AST congruence the lookup key respects. R1 forces the
first **amendment**:

> A congruence alone returns a class-constant answer. R1's answer VARIES within a class
> (root of 3x+7 ≠ root of 5x+2, same template class). So the R1 object is not a coarser
> congruence but a **fibration**: key ↦ (equivalence class, witness), answer = function of
> the witness. Plus a **guard**: the legality domain (a ≠ 0) restricts the class.

Amended claim for Band E, v2: *rung = (congruence coarseness, witness arity, guard
complexity)*. R0 = (identity, 0 witnesses, no guard). R1 = (template classes, finitely many
literal witnesses, quantifier-free guard on witnesses). Prediction for R2 to test next cycle:
composition along a SUPPLIED order = a pipeline of R1 fibrations where witnesses flow; if R2
needs anything beyond witness-passing (e.g. growing state not expressible as slot bindings),
the frame breaks there. The claim survived R1 only by amendment — recorded as such, not as
confirmation.

## 3. TDD tests (built: `techne/ladder_circuits/tests/test_r1_local_op.py`)

- Applies the given linear rule across renames AND fresh coefficients (the R0 kill test must
  PASS here — capability, not failure).
- **Kill enforced as test:** abstains on quadratic (no rule given), abstains on two-step
  problems (rule would need to fire twice) — an R1 circuit that chains is mislabeled R2.
- **Guard honesty:** 0·x + 7 matches the linear template but the guard (a ≠ 0) must abstain,
  never divide by zero. Legality is part of the operation (reasoning_phase0 R1 legality
  probes make the same point from the probe side).
- Determinism; abstention on unseen structure.

## 4. Gaming traps for R1 batteries

- **Trap 5 — answer-function overfit.** A gamed circuit interpolates answers from nearby
  seen coefficients instead of applying the rule. Catch: probe with coefficients far outside
  the training hull (e.g. 10^9, rationals, symbolic parameter `p`); rule application is exact
  everywhere, interpolation is not. Symbolic-parameter probes are the sharpest version.
- **Trap 6 — guard learned as class prior.** If 90% of probes are legal, "always apply" games
  the guard. Catch: legality-balanced batteries + score guards separately from answers
  (reasoning_phase0's legal/illegal split already does this; keep the split when wiring
  circuits to the oracle).
- **Trap 7 — template overreach via associativity/commutativity.** AC-matching lets ax+b
  match things like b+xa AND unintended forms (x·a·x when flattening is sloppy). Catch:
  adversarial near-miss probes that AC-match but are semantically different (a·x² + b
  flattened to products). Test included.

## 5. Open questions (HITL)

- e-graphs (egg/Python bindings) as the standard substrate from R2 up: worth an arsenal spike
  next pass? My stand: yes at R2 (composition is where saturation starts paying), via the
  `egglog` Python package.

*— Techne loop, cycle 002.*
