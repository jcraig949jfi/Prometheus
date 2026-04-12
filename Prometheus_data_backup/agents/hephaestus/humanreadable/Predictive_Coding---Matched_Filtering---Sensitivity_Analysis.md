# Predictive Coding + Matched Filtering + Sensitivity Analysis

**Fields**: Cognitive Science, Signal Processing, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:46:37.354618
**Report Generated**: 2026-03-31T17:55:19.772043

---

## Nous Analysis

The algorithm builds a hierarchical proposition graph from each candidate answer and scores it by jointly minimizing prediction error, maximizing matched‑filter response, and penalizing sensitivity to input perturbations.

**Data structures** – Each extracted proposition is a NumPy structured record with fields: `type` (negation, comparative, conditional, numeric, causal, ordering), `polarity` (±1), `entities` (string IDs), `relation` (e.g., “greater_than”, “causes”), `value` (float for numeric propositions), and `weight` (initial 1.0). All propositions of an answer form an `N×F` binary feature matrix **X**, where columns correspond to preset feature templates (e.g., “negation+entity”, “comparative+value”, “if‑then‑entity”).  

**Operations**  
1. **Predictive coding step** – Using the prompt, a generative model (hand‑crafted rules) derives a set of expected propositions **P** via forward chaining (modus ponens, transitivity). The prediction error is the squared L2 norm of the residual **E = X – P**, normalized by ‖P‖²:  `error = ‖E‖² / (‖P‖² + ε)`.  
2. **Matched‑filtering step** – A template vector **T** representing the ideal answer (constructed from the gold‑standard answer’s propositions) is cross‑correlated with **X**: `score_mf = (X·T) / (‖X‖‖T‖)`. This maximizes the signal‑to‑noise ratio of matching structural patterns.  
3. **Sensitivity analysis** – Each numeric feature is perturbed ±δ (δ = 5 % of its magnitude) and each polarity is flipped; the resulting change in `score_mf` is measured. Sensitivity `S = mean|Δscore_mf|` across all perturbations.  

**Scoring logic** – Final score = `w1·(1 – error) + w2·score_mf – w3·S`, with weights summing to 1 (e.g., 0.4, 0.4, 0.2). Lower prediction error, higher matched‑filter response, and low sensitivity yield higher scores.

**Structural features parsed** – Negations (“not”, “no”), comparatives (“more than”, “>”, “less than”), conditionals (“if…then”, “unless”, “provided that”), numeric values (integers, decimals with units), causal claims (“because”, “leads to”, “results in”, “causes”), ordering relations (“before”, “after”, “first”, “second”, “greater than”, “less than”), and conjunctions.

**Novelty** – While predictive coding, matched filtering, and sensitivity analysis appear separately in cognitive science and signal processing, their joint use as a concrete, rule‑based scoring mechanism for textual reasoning answers has not been reported in recent NLP evaluation literature, which tends to rely on neural similarity or pure logic solvers.

**Ratings**  
Reasoning: 8/10 — captures logical consistency via prediction error and rule‑based inference.  
Metacognition: 6/10 — sensitivity provides a rudimentary self‑check but lacks explicit reflection on uncertainty.  
Hypothesis generation: 7/10 — perturbations generate alternative proposition sets, enabling hypothesis exploration.  
Implementability: 9/10 — relies only on regex, NumPy, and stdlib; no external models or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:54:05.842001

---

## Code

*No code was produced for this combination.*
