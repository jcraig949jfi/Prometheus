# Active Inference + Theory of Mind + Compositionality

**Fields**: Cognitive Science, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:22:04.065125
**Report Generated**: 2026-03-31T16:21:16.443114

---

## Nous Analysis

**Algorithm: Compositional Belief‑Propagation Scorer (CBPS)**  

1. **Data structures**  
   - **Parse tree**: each sentence is converted into a directed acyclic graph (DAG) where nodes are atomic propositions (e.g., “X is Y”, “X > 5”, “¬P”) and edges are syntactic relations (subject‑verb‑object, modifier, conjunction). Built with regex‑based chunking and a deterministic shift‑reduce parser (no external libraries).  
   - **Belief matrix** **B** ∈ ℝ^{N×M}: N propositions, M possible truth‑states (True, False, Unknown). Each entry b_{i,s} is a log‑probability (negative free‑energy) for proposition i being in state s. Initialized from lexical priors (e.g., “is” → 0.8 True, “is not” → 0.8 False).  
   - **Intent model** **I** ∈ ℝ^{K}: a vector over K candidate answer intents (e.g., “affirm”, “deny”, “quantify”, “explain”). Updated by inverse‑planning from the expected free‑energy of actions that would produce the answer.  

2. **Operations**  
   - **Compositional scoring**: For each node, combine child beliefs using the semantic rule attached to the edge (e.g., conjunction → log‑sum‑exp, negation → flip True/False, comparative → numeric comparison via numpy). This yields updated b_{i,s} via belief propagation (message passing) until convergence (≤1e‑3 change).  
   - **Active inference step**: Compute expected free‑energy G(a) = ∑_s b_{i,s}·[log b_{i,s} − log p(o|s,a)] for each candidate answer action a (producing a textual string). The term p(o|s,a) is a deterministic likelihood: 1 if the generated string matches the propositional content under state s, else 0. Choose action minimizing G.  
   - **Theory‑of‑Mind update**: Treat the answer as an observation of another agent’s belief. Update a second‑order belief matrix **B²** over the answerer’s internal states using Bayes rule: b²_{j} ∝ p(answer|j)·prior_j, where j indexes possible mental states (e.g., believes X, doubts X). The final score for an answer is –G(a) + log ∑_j b²_j ( epistemic value + social plausibility).  

3. **Structural features parsed**  
   - Negations (“not”, “no”), comparatives (“greater than”, “less than”), equality/inequality numerals, conjunctive/disjunctive connectives, conditionals (“if … then …”), causal verbs (“cause”, “lead to”), ordering relations (“before”, “after”), and quantified terms (“all”, “some”, “none”). Numeric tokens are extracted with regex and fed directly into comparative rules.  

4. **Novelty**  
   The combination mirrors recent neuro‑cognitive proposals (e.g., Friston et al., 2022; Rabinowitz et al., 2018) but instantiates them as a deterministic, numpy‑based belief‑propagation engine with explicit Theory‑of‑Mind updates. No published tool couples compositional semantics with active‑inference expected free‑energy and recursive mentalizing in a single scoring function, so the approach is novel in the evaluation‑tool space.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via belief propagation, though limited to hand‑crafted semantic rules.  
Metacognition: 7/10 — models second‑order beliefs about the answerer, but recursion depth is fixed at one level.  
Hypothesis generation: 6/10 — expected free‑energy drives epistemic foraging, yet hypothesis space is restricted to candidate answers supplied.  
Implementability: 9/10 — relies only on regex, numpy arrays, and simple message‑passing loops; no external dependencies or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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

**Forge Timestamp**: 2026-03-31T16:20:56.442339

---

## Code

*No code was produced for this combination.*
