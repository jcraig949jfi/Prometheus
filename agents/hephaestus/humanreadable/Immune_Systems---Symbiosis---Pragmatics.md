# Immune Systems + Symbiosis + Pragmatics

**Fields**: Biology, Biology, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:18:08.814430
**Report Generated**: 2026-04-01T20:30:44.095108

---

## Nous Analysis

**Algorithm**  
The scorer builds a propositional representation of both the reference answer and each candidate answer, then iteratively refines a weight vector through a clonal‑selection process that rewards mutually beneficial (symbiotic) feature overlap while penalizing pragmatic violations.

1. **Parsing & proposition extraction** – Using a small set of regex patterns, the text is scanned for atomic propositions:  
   - *Predicates* (verb‑noun pairs) → (`pred`, polarity, tense)  
   - *Negations* (`not`, `no`, `never`) → flag `neg=True`  
   - *Comparatives* (`more`, `less`, `>`, `<`) → (`comp`, direction)  
   - *Conditionals* (`if … then`, `unless`) → (`cond`, antecedent, consequent)  
   - *Causal claims* (`because`, `leads to`, `results in`) → (`cause`, effect)  
   - *Numeric values* (`\d+(\.\d+)?\s*(kg|m|s|%)`) → (`num`, value, unit)  
   - *Ordering/quantifiers* (`first`, `second`, `all`, `some`, `none`) → (`ord`, `quant`)  
   - *Speech‑act tags* (assertion, question, command) identified by sentence‑final punctuation and cue words (`please`, `?`).  
   Each proposition is stored as a structured NumPy array row: `[type_id, polarity, numeric_flag, comparative_dir, causal_link, speech_act, …]`.

2. **Initial affinity** – Compute a raw similarity matrix **S** between reference propositions **R** and candidate propositions **C** using a weighted Jaccard over binary feature columns (weights **w** initialized uniformly).  
   `S_ij = (w·(R_i ∧ C_j)) / (w·(R_i ∨ C_j))`.

3. **Clonal selection loop** (max 5 generations):  
   - **Selection:** keep the top‑k candidate‑reference pairs with highest affinity.  
   - **Cloning:** duplicate each selected pair n_clones times.  
   - **Mutation:** for each clone, randomly flip a small proportion (≈5%) of binary features (simulating somatic hypermutation).  
   - **Affinity re‑evaluation:** compute new **S** for mutated clones.  
   - **Selection of survivors:** retain clones with affinity > threshold τ.  
   - **Memory update:** increase weights **w** for features that consistently appear in high‑affinity survivors (affinity maturation).  
   - **Symbiosis benefit:** after each generation, compute a mutual‑benefit score **B** = Σ_w_shared·w_shared where *w_shared* is the weight of features present in both R and C; add λ·B to the affinity.

4. **Constraint propagation** – After affinity stabilizes, apply deterministic rules (modus ponens on conditionals, transitivity on ordering, numeric inequality propagation) to derive implicit propositions from R and C. Any derived proposition that contradicts the opposite side incurs a penalty μ.

5. **Final score** –  
   `score = α·mean_survivor_affinity + β·(1 – pragmatic_violation_penalty) + γ·B`  
   where pragmatic_violation_penalty counts Grice maxim violations detected from speech‑act and quantity cues (e.g., excess information, lack of relevance). α+β+γ=1.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations, quantifiers, modal verbs, speech‑act markers, and pragmatic hedges.

**Novelty** – Pure immune‑inspired clonal selection with affinity maturation is known in evolutionary computation; symbiosis‑based mutual benefit weighting and explicit pragmatic feature penalties are rarely combined. No existing public tool integrates all three mechanisms in a single deterministic scorer, making the combination novel for this pipeline.

**Rating**  
Reasoning: 7/10 — captures logical consistency and numeric/ordering reasoning but lacks deep multi‑step inference.  
Metacognition: 5/10 — limited self‑monitoring; weight updates are heuristic, not reflective.  
Hypothesis generation: 6/10 — clonal mutation yields variant candidates, yet generation is random, not guided.  
Implementability: 8/10 — relies only on regex, NumPy, and stdlib; clear data structures and loops.

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
