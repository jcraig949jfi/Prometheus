# Tensor Decomposition + Pragmatics + Sensitivity Analysis

**Fields**: Mathematics, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T03:09:15.560045
**Report Generated**: 2026-03-31T14:34:54.774498

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition Tensor** – Using regex‑based patterns we extract atomic propositions from the prompt and each candidate answer. Each proposition is encoded as a 4‑way tensor **T** ∈ ℝ^{E×R×M×C} where:  
   - *E* = entity index (from a built‑in ontology of noun phrases),  
   - *R* = relation type (e.g., *cause*, *greater‑than*, *equals*, *negated*),  
   - *M* = modal/context flag (assertion, conditional, question, implicature),  
   - *C* = polarity/certainty scalar (1 for positive, –1 for negation, 0 for unknown).  
   The tensor is sparse; each extracted triple sets T[e,r,m,c] = 1 (or –1 for negation).  

2. **Tensor Decomposition → Latent Factors** – Apply CP decomposition (rank = k, k ≪ dimensions) via alternating least squares using only NumPy. This yields factor matrices **A** (E×k), **B** (R×k), **C** (M×k), **D** (C×k) such that **T̂** ≈ ∑_{i=1}^k a_i ∘ b_i ∘ c_i ∘ d_i. The low‑rank core captures the underlying relational structure while filtering noise.  

3. **Pragmatic Weighting** – Compute a pragmatic salience vector **p** ∈ ℝ^{R} from Grice‑style heuristics:  
   - *Relevance* ↑ for relations that appear in the question’s focus (detected via interrogative regex),  
   - *Quantity* ↓ for overly granular relations (high entity count),  
   - *Manner* ↑ for explicit connectives (e.g., “because”, “if”).  
   Multiply the relation factor **B** element‑wise by **p** to obtain **B̂**.  

4. **Scoring** – For each candidate answer, reconstruct its tensor **T̂_ans** using the same factor matrices (with **B̂**) and compute the normalized dot product similarity S = ⟨T̂_prompt, T̂_ans⟩ / (‖T̂_prompt‖‖T̂_ans‖).  

5. **Sensitivity Analysis** – Perturb the prompt tensor by adding i.i.d. Gaussian noise ε∼N(0,σ²) (σ=0.01) to 10% of non‑zero entries, recompute S for each perturbation, and calculate the variance Var(S). Final score = S – λ·Var(S) (λ=0.2), penalizing answers whose similarity is fragile to small input changes.  

**Structural Features Parsed** – negations (via “not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), numeric values (regex for integers/floats), causal claims (“because”, “leads to”), ordering relations (“before”, “after”), and quantifiers (“all”, “some”).  

**Novelty** – Tensor‑based semantic parsing exists, and pragmatic weighting appears in discourse‑aware models, but jointly coupling CP decomposition with Grice‑derived weights and a explicit sensitivity‑penalty step is not documented in the literature; it constitutes a novel hybrid for robustness‑focused reasoning evaluation.  

**Ratings**  
Reasoning: 8/10 — captures multi‑relational structure and filters noise via low‑rank approximation, giving a principled similarity measure.  
Metacognition: 6/10 — the sensitivity step provides a rudimentary self‑check of answer stability, but no higher‑order reflection on the reasoning process itself.  
Hypothesis generation: 5/10 — the method scores existing candidates; it does not propose new answers or alternative explanations.  
Implementability: 9/10 — relies solely on NumPy for ALS CP decomposition and stdlib regex; no external libraries or APIs required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

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
