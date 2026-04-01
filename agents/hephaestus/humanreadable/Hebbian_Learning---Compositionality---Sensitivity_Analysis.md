# Hebbian Learning + Compositionality + Sensitivity Analysis

**Fields**: Neuroscience, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T00:04:49.483879
**Report Generated**: 2026-03-31T14:34:57.413072

---

## Nous Analysis

**Algorithm**  
1. **Parse** both prompt and each candidate answer into a set of *relation tuples* `(type, arg1, arg2)` using a handful of regex patterns:  
   - *type* ∈ {`subj‑verb`, `verb‑obj`, `neg`, `comp`, `cond`, `cause`, `order`, `num‑mod`}.  
   - Arguments are lemmatized tokens (lower‑cased, stop‑words removed).  
2. **Hebbian weighting** – Scan a large background corpus (or the prompt itself if no external data) and increment a weight `w[r]` each time a relation `r` appears inside the same clause. Store weights in a NumPy array indexed by a dictionary `rel2idx`. This yields a symmetric association matrix where frequently co‑occurring concepts have higher weights (activity‑dependent strengthening).  
3. **Compositional scoring** – For a candidate, compute a base score as the sum of weights of its relations that also appear in the prompt’s relation set:  

   ```
   base = Σ w[r] for r in candidate_relations ∩ prompt_relations
   ```  

   If a relation is present but with a polarity mismatch (e.g., negation), subtract its weight instead of adding.  
4. **Sensitivity analysis** – Generate *k* perturbed versions of the candidate by applying stochastic edits: flip a negation, swap numeric values, replace a comparator with its opposite, or toggle a conditional antecedent/consequent. Compute the score for each perturbation using the same base‑score formula. Let `σ` be the standard deviation of these perturbed scores. The final score penalizes fragility:  

   ```
   final = base / (1 + λ * σ)      λ = 0.5 (tunable)
   ```  

   Low variance → high robustness → higher final score.  

**Structural features parsed**  
- Negations (`not`, `no`, `never`) → `neg` type.  
- Comparatives (`more`, `less`, `>`, `<`) → `comp` type.  
- Conditionals (`if … then`, `unless`) → `cond` type.  
- Causal verbs (`cause`, `lead to`, `result in`) → `cause` type.  
- Ordering/temporal (`before`, `after`, `first`, `last`) → `order` type.  
- Numeric values and modifiers (`≈`, `approximately`, `exactly`) → `num‑mod` type.  
- Quantifiers (`all`, `some`, `none`) → treated as arguments of the relation.  

**Novelty**  
Pure Hebbian weighting of syntactic relations is uncommon in rule‑based QA scorers; most existing work uses static vector similarity or dependency‑tree kernels. Adding a sensitivity‑analysis robustness step that explicitly perturbs logical form and measures score variance has not been widely combined with Hebbian‑style co‑occurrence weights in a numpy‑only pipeline, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but relies on hand‑crafted regexes that may miss complex syntax.  
Metacognition: 5/10 — the algorithm can estimate its own uncertainty via σ, yet it does not reason about when to seek more information.  
Hypothesis generation: 4/10 — generates perturbations for sensitivity but does not propose new candidate answers beyond the given set.  
Implementability: 9/10 — all steps use only regex, NumPy arrays, and stdlib data structures; no external libraries or training required.

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
