# Active Inference + Pragmatics + Metamorphic Testing

**Fields**: Cognitive Science, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T18:41:11.122918
**Report Generated**: 2026-04-01T20:30:44.125108

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only `re` we extract a set of atomic propositions \(P_i\) from the prompt and each candidate answer. For each proposition we record a feature vector \(f_i\in\{0,1\}^k\) where the k dimensions encode: negation, comparative direction (>,<,=), conditional antecedent/consequent, numeric value (scaled to [0,1]), and causal polarity (cause/effect). The extraction yields two matrices:  
   - \(X\in\{0,1\}^{n\times k}\) for the prompt propositions,  
   - \(Y^{(j)}\in\{0,1\}^{m\times k}\) for answer \(j\) ( \(m\) propositions in that answer).  

2. **Belief propagation (Active Inference core)** – Treat the prompt as a generative model. Build an implication adjacency matrix \(A\) where \(A_{pq}=1\) if proposition \(p\) syntactically entails \(q\) (e.g., “if A then B”, transitivity of “>”, or causal “A causes B”). Compute the closure \(C = (I + A + A^2 + … + A^L)\) (with \(L\) set to the longest chain found) using Boolean matrix multiplication (numpy dot with `astype(bool)`). The predicted truth vector for an answer is \(\hat{y}=C\,X^\top\) (clipped to 0/1).  

3. **Prediction error** – \(e_j = \|Y^{(j)} - \hat{y}\|_2^2\) (numpy L2 norm).  

4. **Metamorphic penalty** – Define a set of metamorphic relations (MRs) on the prompt:  
   - MR1: swap antecedent and consequent of each conditional (expect \(Y\) to swap the corresponding columns).  
   - MR2: negate all propositions (expect \(Y\) to flip bits).  
   - MR3: add a constant c to every numeric value (expect proportional shift in the numeric dimension).  
   For each MR we compute a violation \(v_{j,r}= \| \text{MR}_r(Y^{(j)}) - Y^{(j)}\|_1\) and sum them: \(p_j = \sum_r v_{j,r}\).  

5. **Score (expected free energy)** – \(F_j = e_j + \lambda p_j\) where \(\lambda\) weights epistemic vs. pragmatic terms (set to 0.5). Lower \(F\) indicates a better answer. All operations use only `numpy` and the standard library.

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`>`, `<`, `more than`, `less than`), conditionals (`if … then …`), numeric constants, causal verbs (`cause`, `lead to`, `because`, `result in`), and ordering keywords (`first`, `after`, `before`). These become the dimensions of \(f_i\).

**Novelty**  
The combination is not directly reported in the literature. Active‑inference‑style expected free energy has been used in perception‑action loops, but not paired with pragmatic feature extraction and metamorphic‑relation constraints for answer scoring. Thus it is a novel synthesis, though each component has precedents.

**Ratings**  
Reasoning: 7/10 — captures logical propagation and uncertainty but lacks deep semantic understanding.  
Metacognition: 5/10 — the algorithm can monitor its own error via \(F\) but does not adaptively revise its parsing strategy.  
Hypothesis generation: 4/10 — generates implied propositions via closure, yet does not propose alternative worlds beyond entailment.  
Implementability: 9/10 — relies solely on regex, numpy Boolean/matrix ops, and simple loops; easily coded in <150 lines.

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
