# Rung R2 — Multi-Step Execution · Circuit Study (Loop pass 1, cycle 003)

**Canon:** Band E. R2 = chains operations when order is SUPPLIED. Kill separations: survives
distractor-step insertion (vs R1); no planning — wrong supplied order must abort, not
reorder (reordering is R7's business).

## 1. Circuits for R2

- **C-R2a: witness-flow pipeline (built).** `R2PipelineCircuit`: ordered rule names →
  guarded expression→expression steps, one intermediate expression threaded through, full
  trace emitted. ~100 lines over sympy.
- **C-R2b: e-graph program execution.** Same chain in egglog: each step a rewrite applied
  under saturation control. Deferred to next cycle if cheap (HITL #5) — for R2 proper it is
  overkill, but it becomes natural the moment two DIFFERENT rule orders must be recognized
  as confluent (which is an R5/R8 flavor of question).
- **C-R2c (rejected): end-to-end retrieval with decorative traces.** Named to be trapped
  (trap 8), not built.

## 2. Claim v2 pressure test — result: AMENDED AGAIN (v3)

v2 predicted R2 = "R1 fibrations with witnesses flowing." Building the circuit showed the
prediction is right about the SHAPE but wrong about the TYPE: what flows is not fixed-arity
slot bindings — it is the whole intermediate expression, unbounded. `together` grows the
tree; `numer` shrinks it; no fixed witness arity survives contact with the second step.

**Claim v3 (Band E): rung = the TYPE of carried state.**
- R0: no state (key → stored answer)
- R1: fixed-arity witness bindings + quantifier-free guard
- R2: one unbounded expression, threaded linearly through guarded steps (supplied order)
- R3 (prediction): expression + a monotonically GROWING constraint store consulted by later
  guards (excluded values, domain restrictions) — i.e. R2 + a blackboard
The v1→v2→v3 arc is itself evidence the ladder is a real basis: each rung so far has forced
exactly one new state-type ingredient, and the ingredient is checkable in code.

## 3. TDD tests (built: `test_r2_pipeline.py`, 10 green)

Capability: two-step rational chain (hand-verified −1/7), renames, 10⁶-scale coefficients,
distractor-step survival. Kill: wrong order aborts with EMPTY trace (no silent reordering);
unknown rule aborts; empty program = abstention, not identity; multivariate aborts at the
exact failing step (localized failure, F-axis). Lift: **no single rule in the registry
solves the chain problem** — composition is the capability, counter-baseline enforced.

## 4. Traps for gaming R2 batteries

- **Trap 8 — decorative traces (the big one).** A memorizer returns the right answer plus a
  fabricated trace. Catch: independently RE-EXECUTE every claimed step and demand equality
  (built as a test). This is the miniature of the metabolization probe's verdict-redaction
  logic: the trace is the residue, the answer is the answer key.
- **Trap 9 — CAS auto-simplification leakage (found by BUILDING, not theorizing).** sympy
  auto-expands `3*(x+2)+4*(x-5)` at construction, so a "distribute" step tests nothing —
  the capability was in the substrate, not the circuit. Any R2 battery over a CAS must pick
  steps ABOVE the CAS's automatic layer, or the probe silently measures the CAS. This is a
  probe-validity trap, and it bit us within ten minutes of writing rules.
- **Trap 10 — step-count priors.** If most probes need exactly 3 steps, "always run the
  full program" games abort behavior. Mix program lengths, include programs whose correct
  outcome IS abortion, and score abstention separately (reasoning_phase0's legality split,
  lifted to program level).

## 5. Open questions

- Trap 9 generalizes: which reasoning_phase0 probes are (unknowingly) measuring sympy's
  automatic layer rather than the candidate? Worth an audit half-cycle.
- v3's R3 prediction is crisp enough to pre-commit: next cycle builds the blackboard
  (excluded-value store) and tests whether ANY blackboard-free pipeline can pass the R3
  probes (extraneous-root rejection). If one can, v3 is wrong at R3.

*— Techne loop, cycle 003.*
