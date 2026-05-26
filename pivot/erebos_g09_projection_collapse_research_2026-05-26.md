# G09 Projection-Collapse Generator — Research Notes

**Date:** 2026-05-26
**Author:** Charon
**Status:** Iteration-1 research; implementation target v0.9
(Iteration 2 of current loop). Tier S per spec — first to ship in v0.9.

---

## Spec recap

- **Core mechanism:** Occam's Razor generator. Attempts to prove a
  complex multi-dimensional pattern is actually a single trivial
  rule in disguise.
- **Input / Provenance:** A complex, surviving Erebos composition
  (in our current state: any G01/G02 emission with multi-field
  composition_payload).
- **Transformation:** Isolates the single highest-variance
  coordinate and projects the entire claim onto it.
- **Output Claim:** `>95% of the predictive power of Complex Claim
  C is captured by the single variable Trivial Coordinate T`.
- **Falsification Route:** Ablation. Stygian drops the trivial
  coordinate and checks if the complex claim still holds any
  residual predictive power.
- **Expected Kill Pattern:** `residual_survival` (killing this
  generator means the complex claim IS genuinely complex).
- **Loader Feasibility:** EASY (Tier S). Pure data-column dropping.

---

## Reasoning Ladder mapping

- **Primary tier:** R3 (abstraction — projection-onto-single-
  coordinate IS the MDL compression move).
- **Secondary tier:** R6 (self-correction — Occam's razor as a
  swarm-level discipline).
- **Why not R5:** projection doesn't make a causal claim, it
  makes a sufficiency claim (the single coordinate SUFFICES; not
  that it CAUSES).

---

## Adjacent fields touched

1. **Sparse coding / dictionary learning** — sparse
   representations as compression. G09 picks the most-sparse
   1-element representation.
2. **MDL / Kolmogorov complexity** — single-variable explanation
   = shorter description = lower Kolmogorov complexity.
3. **Feature ablation** in ML interpretability — Shapley values,
   permutation importance, SHAP. The falsification route IS
   single-feature ablation.
4. **Symbolic regression with parsimony pressure** — PySR's
   parsimony penalty embodies the same Occam principle.
5. **Active interventions in causal inference** — testing whether
   removing X breaks the prediction is causal-interventional.
6. **AIC / BIC model selection** — penalizing model complexity.
   G09 is the extreme case (1-parameter model wins iff complex
   model adds no predictive power).
7. **Stepwise regression** (classical) — start with full model,
   drop weakest predictor, refit. G09's ablation falsification is
   the first-step-of-stepwise version.

---

## Relevant literature

**MDL and parsimony:**
- Rissanen 1978 "Modeling by shortest data description"
  (Automatica).
- Grünwald 2007 "The Minimum Description Length Principle" (book).
- Hutter 2005 "Universal Artificial Intelligence."

**Feature importance:**
- Breiman 2001 "Random Forests" — permutation importance.
- Lundberg & Lee 2017 "A Unified Approach to Interpreting Model
  Predictions" (SHAP).

**Symbolic regression with parsimony:**
- Cranmer 2023 "Interpretable Machine Learning for Science with
  PySR and SymbolicRegression.jl" — direct parsimony-vs-fit
  tradeoff.

**Pythia DR candidates:**
- "Occam's razor in hypothesis-generation systems: formal
  treatments and empirical evidence."
- "Single-feature sufficient statistics in high-dimensional
  mathematical conjectures."

---

## Datasets in the repo that apply

- **`charon/agents/erebos/state/kill_ledger.jsonl`** — Erebos's
  own outputs are the primary G09 input. Per current state, all
  Erebos rows are UNVERIFIED (composition-aware loader pending),
  so G09 operates on the *composition structure* (which fields are
  in `composition_payload`?), not on a tested predictive-power
  measure.

- **`charon/agents/pollux/state/kill_ledger.jsonl`** — Pollux's
  `correlation_survives_normalization` rows have 2 coordinates
  (raw correlation + normalized correlation). G09 could project
  onto raw alone and emit "raw correlation suffices; normalization
  is decorative" as a candidate-claim (likely false; the whole
  point of Pollux is normalization matters).

- **`charon/agents/stygian/state/kill_ledger.jsonl`** — Stygian's
  battery sub-tests are a natural multi-coordinate set (F15, F16,
  F18, F20, F24 etc.). G09 could project a Stygian POSSIBLE
  verdict onto its highest-information sub-test and claim that
  sub-test alone determines the verdict.

---

## Open-source tools to evaluate

- **`scikit-learn`** — `SelectKBest`, `mutual_info_classif`,
  permutation_importance. Trivial integration; no new dep.
- **`shap`** — SHAP value computation. Heavier dep but high-value
  for feature-attribution-level G09 ablation.
- **`MilesCranmer/PySR`** — parsimony-aware symbolic regression
  could BE G09's substrate-claim-generator (find shortest formula
  explaining a Stygian verdict).

---

## Simple test claims for MVP

**MVP test set v0:**

1. Input: Erebos G01 intersection claim with composition_payload
   containing 3 fields (stygian_claim_text, pollux_corr_raw,
   pollux_corr_norm).
   Transformation: pick the field with highest variance across
   recent G01 emissions (say `pollux_corr_norm` because it spans
   [-1, 1] while raw correlations cluster near 1.0).
   Output: "The G01 intersection claim's predictive power is
   captured almost entirely by `pollux_corr_norm`; the
   `stygian_claim_text` and `pollux_corr_raw` fields are decorative."
   Falsification: ablate pollux_corr_norm from a synthetic
   evaluation; check whether the remaining 2-field version of
   the claim predicts as well.

2. Input: Erebos G02 contrast claim with permutation_n + margin_delta
   + split_metadata.
   Transformation: project onto split_metadata alone.
   Output: "The G02 contrast claim reduces to: 'the split metadata
   itself determines the divergence'; permutation_n + margin_delta
   are framing."
   Falsification: same as above — ablate; check residual signal.

---

## Frontier-model questions

```
You are an independent technical reviewer. A research swarm wants
to build a generator called "Projection-Collapse" that takes
complex multi-dimensional candidate-claims and emits a single-
coordinate sufficient-statistic version: "this complex claim is
explained by ONE coordinate; the rest is decorative." The
expected falsification kill-pattern is "residual_survival" — when
the ablation shows the dropped coordinates DO add predictive
power, the simplification fails and the complex claim is genuinely
complex.

Q1. This is essentially Occam's razor as a swarm-level discipline.
    What's the cleanest formal treatment in the MDL / Kolmogorov-
    complexity literature for "this complex model collapses to a
    1-parameter version"?

Q2. Permutation importance, Shapley values, and SHAP all attribute
    predictive power to features. Which is the right primitive for
    G09's ablation falsification, and why?

Q3. The risk: G09 will emit FALSE projection claims when the
    high-variance coordinate is also high-noise. How does the
    falsification route guard against this?

Q4. In symbolic regression with parsimony pressure (PySR, etc.),
    the tradeoff curve is between fit and formula length. Is G09's
    "single coordinate" choice equivalent to "shortest formula"?
    If not, what's the difference?

Q5. When is G09 the WRONG generator to use? Name a class of
    complex claims for which projecting to single-coordinate
    actively misleads.

Q6. The composition-aware Stygian loader (currently not shipped)
    is supposed to programmatically construct the restricted-
    dataset. For G09's ablation, the restriction is "drop the
    projected-onto coordinate." Is this loader contract well-
    defined, or does it need additional structure (e.g., joint
    distribution of remaining coordinates)?
```

---

## TDD test list

1. `test_g09_applicability_no_erebos_compositions` — applicable()
   returns False when no Erebos composition rows exist.
2. `test_g09_picks_highest_variance_coord` — given fixture of 3
   Erebos compositions with known per-coord variances, picks the
   one with highest variance.
3. `test_g09_emits_six_field_spec` — emitted ComposedClaim has all
   six required fields.
4. `test_g09_falsification_route_names_ablation` — falsification_route
   text mentions "ablation" and the specific coord to drop.
5. `test_g09_does_not_re_project_same_parent` — tried_pairs prevents
   re-projecting the same Erebos parent claim.
6. `test_g09_kill_pattern_is_residual_survival` — exactly the spec
   constant.
7. `test_g09_reasoning_tier_R3` — declared attribute.
8. `test_g09_handles_single_coord_input` — given a parent claim
   with only 1 coordinate, applicable() returns False (nothing to
   project).
9. `test_g09_variance_estimation_robust_to_outliers` — given a
   coord with 1 outlier value 10000x the others, variance is
   computed via robust estimator (MAD or trimmed-variance).

---

## Logging requirements

- `transformation_path`: which projection target was selected
  (e.g., `proj_to_pollux_corr_norm`).
- G09-specific extras: per-coord variance estimates; the chosen
  coordinate name; the variance ratio (chosen / sum of others).
- `inputs_summary`: count of Erebos composition rows considered +
  median per-coord-count (proxy for composition complexity).

---

## HITL escalation conditions

- **PLATEAUED:** G09 needs Erebos compositions to operate on. If
  v0.8/v0.9 G01+G02 emissions plateau (combinatorial space
  exhausted), G09's input dries up too.
- **DOMAIN-EXPERT NEEDED:** when the highest-variance coordinate
  is also high-noise (e.g., a near-uniform distribution), the
  projection is information-poor. HITL ticket flags this and asks
  whether the variance picker should use information-gain instead
  of variance.

---

## Implementation sketch for v0.9

```python
class ProjectionCollapseGenerator:
    id = "g09_projection_collapse"
    name = "Projection-Collapse"
    spec_phase = 2
    feasibility_tier = "S"
    reasoning_tier = "R3"
    expected_kill_pattern = "residual_survival"

    def applicable(self, state: SwarmState) -> bool:
        # Need Erebos compositions with multi-coord composition_payload
        if not state.erebos_self_ledger:
            return False
        for r in state.erebos_self_ledger:
            payload = r.get("extras", {}).get("composition_payload", {})
            if len(payload) >= 2:
                key = f"{self.id}|{r.get('record_id','')}"
                if key not in state.tried_pairs:
                    return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        for r in sorted(state.erebos_self_ledger,
                       key=lambda x: x.get("emitted_at", ""), reverse=True):
            key = f"{self.id}|{r.get('record_id','')}"
            if key in state.tried_pairs:
                continue
            payload = r.get("extras", {}).get("composition_payload", {})
            if len(payload) < 2:
                continue
            # Pick highest-variance numeric field across THIS row's
            # composition_payload (MVP: just pick the first numeric)
            numeric_fields = {
                k: v for k, v in payload.items()
                if isinstance(v, (int, float))
            }
            if not numeric_fields:
                continue
            # For MVP: pick max by absolute value as variance proxy
            chosen = max(numeric_fields, key=lambda k: abs(numeric_fields[k]))
            return self._build_claim(r, chosen, numeric_fields, state)
        return None

    # ... _build_claim emits ComposedClaim per six-field spec
```

ETA: ~200 LOC including tests + logging hooks.

---

## Cross-iteration handoff

- **Iteration 2:** implement per the sketch; smoke-test against
  current Erebos ledger; verify G09 actually picks meaningful
  coordinates from G01 + G02 emissions.
- **Iteration 3:** add variance-vs-information-gain choice
  parameter; review G09 emissions for false-projection cases.
- **Iteration 4+:** integrate with composition-aware loader when
  it exists; falsification ablation becomes mechanical.

— Charon, 2026-05-26
