# Neural Plasticity + Matched Filtering + Compositionality

**Fields**: Biology, Signal Processing, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T06:46:55.349447
**Report Generated**: 2026-04-02T08:39:55.220855

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – Using a small set of regex patterns we parse the prompt and each candidate answer into a structured predicate list:  
   - *Negations* (`not`, `no`) → flag `neg` on the following predicate.  
   - *Comparatives* (`>`, `<`, `>=`, `<=`, `more than`, `less than`) → predicate `cmp(var1, op, var2)`.  
   - *Conditionals* (`if … then …`) → predicate `cond(antecedent, consequent)`.  
   - *Causal* (`because`, `leads to`, `causes`) → predicate `cause(source, target)`.  
   - *Ordering* (`before`, `after`, `first`, `last`) → predicate `order(e1, e2)`.  
   - *Numeric values* → token `num(value)`.  
   - *Quantifiers* (`all`, `some`, `none`) → predicate `qtype(scope, var)`.  
   Each predicate is assigned an integer index; a sentence becomes a sparse binary vector **x** ∈ {0,1}^D where D is the total predicate vocabulary.

2. **Hebbian weight adaptation (plasticity)** – Treat the prompt vector **p** as the “signal” we want to strengthen. Initialize a weight vector **w** = zeros(D). For each training example (prompt, correct answer) we perform a Hebbian update:  
   ```
   η = 0.1
   w ← w + η * (p ⊙ c_correct)
   ```  
   where ⊙ is element‑wise product. This increases weights for predicates that co‑occur in the prompt and the correct answer, mimicking experience‑dependent synaptic strengthening.

3. **Matched‑filter scoring** – For a new candidate answer with vector **c**, compute the filter output (cross‑correlation under the learned weights):  
   ```
   s = w · c          # dot product = Σ w_i * c_i
   ```  
   Because **w** emphasizes prompt‑relevant predicates, **s** is maximal when the candidate shares those structured features and minimal when it shares only noise‑like predicates. The score is normalized to [0,1] by dividing by ‖w‖‖c‖.

**Structural features parsed** – negations, comparatives, conditionals, causal markers, ordering/temporal relations, numeric constants, and quantifiers. These are the primitives that the regex‑based extractor turns into predicate indices.

**Novelty** – The triple bind of Hebbian plasticity, matched‑filter detection, and strict compositional parsing is not present in existing NLP scoring tools. Related work uses static TF‑IDF or Siamese networks; none combine an online Hebbian weight update with a deterministic matched‑filter operator on logically parsed structures.

**Ratings**  
Reasoning: 7/10 — captures logical structure and adapts weights, but limited to linear interactions.  
Metacognition: 5/10 — no explicit self‑monitoring of uncertainty beyond score magnitude.  
Hypothesis generation: 4/10 — generates scores, not new hypotheses; relies on pre‑extracted predicates.  
Implementability: 9/10 — only numpy, regex, and basic loops; straightforward to code in <150 lines.

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
