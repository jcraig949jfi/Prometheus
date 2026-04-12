# Symbiosis + Theory of Mind + Matched Filtering

**Fields**: Biology, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:47:42.552598
**Report Generated**: 2026-04-01T20:30:44.104108

---

## Nous Analysis

**Algorithm – Symbiotic Belief‑Matched Filter (SBMF)**  
1. **Parsing (structural extraction)** – Using only `re` from the std‑lib, the prompt *P* and each candidate answer *C* are scanned for:  
   - atomic propositions `subj‑pred‑obj` (e.g., “The cat chased the mouse”),  
   - negations (`not`, `never`),  
   - comparatives (`greater than`, `less than`, `more … than`),  
   - conditionals (`if … then …`),  
   - causal markers (`because`, `since`, `leads to`),  
   - numeric values and units,  
   - ordering relations (`before`, `after`, `first`, `last`).  
   Each match yields a tuple `(type, head, modifier, tail)` stored in a list `props`.

2. **Belief‑graph construction (Theory of Mind)** – For each text we build a directed graph *G* = (V, E) where V = unique entities (subjects/objects) and E encodes asserted relations (e.g., `chased(cat, mouse)`). Negations insert a special “¬” edge. Recursive mentalizing is approximated by limiting walks to depth 2: for each node we compute the set of reachable nodes via one or two hops, representing “what the agent believes others believe”.

3. **Constraint propagation** – Using Floyd‑Warshall‑style transitive closure on the adjacency matrix (numpy boolean array) we infer implicit relations (e.g., `A > B` and `B > C → A > C`). The proportion of propagated edges that are consistent with the original set gives a *constraint‑satisfaction score* `cs ∈ [0,1]`.

4. **Feature vectors & matched filtering** – Each proposition list is converted to a fixed‑length binary vector *v* (size = number of distinct proposition templates discovered across all inputs). The prompt vector *vp* and candidate vector *vc* are obtained. The matched‑filter response is the normalized cross‑correlation:  
   `mf = (vp · vc) / (||vp||·||vc||)` (numpy dot product and norms). This maximizes SNR for detecting the prompt’s signal in the candidate.

5. **Symbiosis (mutual benefit)** – Compute belief‑graph overlap Jaccard index `j = |E_P ∩ E_C| / |E_P ∪ E_C|`. The mutual benefit term is `mb = j * (1 + depth_weight)`, where `depth_weight` rewards higher‑order Theory‑of‑Mind walks (depth 2) present in both graphs.

6. **Final score** –  
   `score = α·mf + β·mb + γ·cs`  
   with α+β+γ=1 (e.g., 0.4,0.4,0.2). Higher scores indicate answers that structurally match the prompt, share belief content, and satisfy logical constraints.

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations, and entity‑role bindings.

**Novelty** – While individual components (graph‑based belief modeling, constraint propagation, matched‑filter detection) exist in neuro‑symbolic or program‑synthesis literature, their tight coupling as a single scoring function that treats candidate answers as symbiotic organisms cross‑correlated with a prompt’s logical signal has not been reported in public work. The approach is therefore novel in this specific combination.

**Rating**  
Reasoning: 8/10 — captures deep logical structure via constraint propagation and signal detection.  
Metacognition: 7/10 — models first‑ and second‑order beliefs but lacks deeper recursive reasoning.  
Implementability: 9/10 — relies only on regex, numpy, and std‑lib; no external dependencies.  
Hypothesis generation: 6/10 — generates implied propositions through closure but does not invent novel hypotheses beyond entailment.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
