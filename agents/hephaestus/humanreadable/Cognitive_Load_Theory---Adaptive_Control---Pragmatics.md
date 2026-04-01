# Cognitive Load Theory + Adaptive Control + Pragmatics

**Fields**: Cognitive Science, Control Theory, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:47:29.754647
**Report Generated**: 2026-03-31T16:31:50.616897

---

## Nous Analysis

The algorithm builds a lightweight propositional graph from each prompt‑answer pair, then scores the answer by balancing cognitive‑load estimates, adaptive‑control weight updates, and pragmatic‑violation penalties — all using only NumPy and the Python standard library.

**Data structures**  
- `tokens`: list of strings from regex‑split text.  
- `props`: list of proposition objects `(id, type, args)` extracted via patterns for negations (`not`), comparatives (`> < =`), conditionals (`if … then`), causal verbs (`because`, `leads to`), numeric values, and ordering relations (`before`, `after`).  
- `C`: NumPy boolean adjacency matrix (`n_props × n_props`) where `C[i,j]=True` iff a logical relation (e.g., `A → B`) links proposition *i* to *j*.  
- `w`: NumPy weight vector `[w_intr, w_extr, w_germ, w_prag]` adapted online.  
- `f`: feature vector `[intr_load, extr_load, germ_load, prag_penalty]` for the current answer.

**Operations**  
1. **Parsing** – regexes extract the structural features listed above; each yields a proposition and populates `C`.  
2. **Load calculation** –  
   - Intrinsic load = number of propositions (`len(props)`).  
   - Extraneous load = count of tokens not mapped to any proposition (stopwords, filler).  
   - Germane load = proportion of satisfied constraints: compute transitive closure of `C` with Floyd‑Warshall (`np.linalg.matrix_power` or iterative Boolean multiplication), then count how many asserted relations in the answer hold in the closure; germane = satisfied / total asserted.  
3. **Pragmatic penalty** – counts of hedge words (`maybe`, `perhaps`), vague quantifiers (`some`, `many`), and relevance loss (1‑cosine TF‑IDF between prompt and answer, TF‑IDF computed with NumPy).  
4. **Scoring** – `score = -(w[0]*intr + w[1]*extr) + w[2]*germ - w[3]*prag`.  
5. **Adaptive update** – after each batch, compute error `e = target_score - score` (target can be a heuristic like human‑ranked grade). Update weights with LMS rule: `w ← w + η * e * f`, where η is a small learning rate (e.g., 0.01).  

**Structural features parsed** – negations, comparatives, conditionals, causal verbs, numeric values, ordering/temporal relations, quantifiers, and modal verbs.

**Novelty** – While each theory has been used separately in tutoring systems, fusing CLT load metrics with an adaptive‑control weight‑tuning loop and a pragmatic‑violation penalty in a pure‑NumPy scorer is not documented in the literature; it extends constraint‑propagation methods by adding online weight adaptation and Grice‑based penalties.

**Ratings**  
Reasoning: 8/10 — captures logical structure and load balance, but relies on shallow heuristics for deeper inference.  
Metacognition: 6/10 — weight adaptation offers rudimentary self‑regulation, yet lacks explicit monitoring of one’s own reasoning process.  
Hypothesis generation: 5/10 — the model can propose alternative parses via constraint relaxation, but does not actively generate new hypotheses.  
Implementability: 9/10 — all components are implementable with NumPy and stdlib; no external dependencies or neural nets required.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:31:28.426608

---

## Code

*No code was produced for this combination.*
