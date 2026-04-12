# Dual Process Theory + Matched Filtering + Sensitivity Analysis

**Fields**: Cognitive Science, Signal Processing, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T00:43:01.243527
**Report Generated**: 2026-03-31T14:34:55.541389

---

## Nous Analysis

**Algorithm: Dual‑Stage Signal‑to‑Noise Sensitivity Scorer (DS‑SNSS)**  

1. **Parsing stage (System 1‑like fast extraction)**  
   - Input: raw prompt `P` and each candidate answer `C_i`.  
   - Using only `re` (standard library) we extract a ordered list of atomic propositions `A = [a₁,…,aₙ]` from each text. Propositions are defined by patterns:  
     * Negation: `not\s+(\w+)` → `¬x`  
     * Comparative: `(\w+)\s+(more|less|greater|smaller|>\|<\|>=|<=)\s+(\w+)` → `x op y`  
     * Conditional: `if\s+(.+?)\s*,\s*then\s+(.+)` → `antecedent → consequent`  
     * Causal claim: `(.+?)\s+(causes|leads\sto|results\in)\s+(.+)` → `cause → effect`  
     * Numeric value: `\d+(\.\d+)?` → float token  
     * Ordering relation: `(\w+)\s+(before|after|precedes|follows)\s+(\w+)` → temporal order.  
   - Each proposition is encoded as a one‑hot vector in a fixed‑dimension space `ℝᵐ` (m = number of distinct predicate‑argument templates observed in the corpus). The resulting representation for a text is the sum of its proposition vectors → `s(P)`, `s(C_i)`.

2. **Matched‑filtering stage (System 2‑like deliberate correlation)**  
   - Treat `s(P)` as a known signal template and each `s(C_i)` as a noisy observation.  
   - Compute the normalized cross‑correlation (dot product) using NumPy:  
     `ρ_i = (s(P)·s(C_i)) / (‖s(P)‖‖s(C_i)‖)`.  
   - This yields a similarity score in `[‑1,1]` that is maximal when the structural proposition patterns align exactly.

3. **Sensitivity‑analysis stage (perturbation robustness)**  
   - Generate a set of small perturbations `Δ` on `s(C_i)` by randomly flipping the sign of a subset of proposition dimensions (probability p = 0.05) to simulate missing or spurious logical cues.  
   - For each perturbed version compute `ρ_i(Δ)`.  
   - The sensitivity metric is the variance of these correlations: `σ_i² = Var_Δ[ρ_i(Δ)]`.  
   - Final score combines match and robustness:  
     `Score_i = ρ_i – λ·σ_i`, with λ = 0.2 (empirically balances peak similarity against stability). Higher scores indicate answers that both closely mirror the prompt’s logical structure and are robust to minor propositional noise.

**Parsed structural features**: negations, comparatives, conditionals, causal claims, numeric values, temporal/ordering relations, and conjunctions (implicit in proposition aggregation).

**Novelty**: While each component—template matching, cross‑correlation, and sensitivity perturbation—has precedents (e.g., kernel methods, robustness checks), their conjunction as a deterministic, numpy‑only scorer that explicitly operates on extracted logical propositions is not documented in the literature on reasoning evaluation tools.

---

Reasoning: 7/10 — The algorithm provides a principled, similarity‑based metric that rewards structural alignment, but it treats propositions as bag‑like sums, losing higher‑order interaction nuances.  
Metacognition: 5/10 — No explicit self‑monitoring or uncertainty calibration beyond variance; the system does not reflect on its own parsing failures.  
Hypothesis generation: 4/10 — The method scores existing candidates; it does not generate new answer hypotheses or explore alternative logical constructions.  
Implementability: 9/10 — Relies solely on `re` for parsing and NumPy for vector operations; no external libraries or training data are required, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
