# Epigenetics + Pragmatics + Sensitivity Analysis

**Fields**: Biology, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:07:38.707673
**Report Generated**: 2026-04-01T20:30:43.644122

---

## Nous Analysis

**Algorithm: Weighted Pragmatic‑Epistemic Constraint Propagation (WPECP)**  

1. **Data structures**  
   - `Prop`: a namedtuple `(id, text, type, weight, ctx)` where `type` ∈ {‘neg’, ‘cond’, ‘comp’, ‘causal’, ‘num’}.  
   - `props`: list of `Prop` objects extracted from the prompt and each candidate answer via regex‑based pattern matching.  
   - `W`: numpy array of shape `(n,)` holding the current weights (initial weight = 1.0).  
   - `C`: boolean adjacency matrix `(n,n)` where `C[i,j]=True` if proposition *i* entails *j* (derived from syntactic rules: e.g., “If A then B” → edge A→B; “A is greater than B” → edge A→B for ordering; “Not A” → self‑negation flag).  

2. **Operations**  
   - **Contextual weighting (pragmatics)**: adjust each weight by a context factor `ctx` computed from surrounding discourse markers (e.g., “however” reduces weight of preceding claim, “therefore” increases it). `ctx` is a scalar in `[0.5,1.5]` looked up from a small hand‑crafted table.  
   - **Epigenetic marking**: treat `W` as heritable marks; after each propagation step, apply a decay `W ← W * λ` (λ=0.95) to simulate methylation‑like attenuation, then renormalize to keep mean weight =1.  
   - **Constraint propagation**: compute transitive closure of `C` using Floyd‑Warshall (boolean) → `Reach`. For each candidate, compute satisfaction score `S = Σ_j W[j] * Reach[ans_idx, j]` where `ans_idx` indexes propositions asserted by the answer. This sums weights of all entailed claims.  
   - **Sensitivity analysis**: perturb `W` by adding a small epsilon vector `ε` (drawn from `numpy.random.normal(0,0.01,n)`) and recompute `S`. Repeat `k=20` times; the variance `Var(S)` measures robustness. Final score = `S / (1 + Var(S))`.  

3. **Structural features parsed**  
   - Negations (“not”, “no”), conditionals (“if … then …”), comparatives (“greater than”, “less than”), numeric values and units, causal verbs (“causes”, “leads to”), ordering relations (“before”, “after”), quantifiers (“all”, “some”).  

4. **Novelty**  
   - Purely symbolic weighted argumentation frameworks exist, and sensitivity analysis is used in causal inference, but coupling them with an epigenetics‑inspired decay/renormalization step and pragmatic contextual weighting has not been described in the literature. The triple blend is therefore novel.  

**Ratings**  
Reasoning: 7/10 — captures logical entailment and robustness but relies on hand‑crafted pragmatics tables.  
Metacognition: 5/10 — limited self‑reflection; sensitivity gives uncertainty estimate but no higher‑order monitoring.  
Hypothesis generation: 6/10 — can propose alternative weight perturbations, yet lacks generative conjecture mechanisms.  
Implementability: 8/10 — uses only numpy/regex, straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

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
