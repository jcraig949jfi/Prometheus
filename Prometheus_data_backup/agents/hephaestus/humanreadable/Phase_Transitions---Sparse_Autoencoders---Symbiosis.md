# Phase Transitions + Sparse Autoencoders + Symbiosis

**Fields**: Physics, Computer Science, Biology
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T19:45:44.964265
**Report Generated**: 2026-03-31T19:12:22.189301

---

## Nous Analysis

**Algorithm: Sparse Constraint‑Propagation Scorer (SCPS)**  
The scorer builds a bipartite graph between *propositional units* extracted from the prompt and each candidate answer.  
1. **Parsing stage** – Using only the standard library (`re`, `itertools`), the prompt and each answer are scanned for:  
   - Atomic predicates (noun‑verb‑noun triples) captured by patterns like `(\w+)\s+(is|are|has|have|does|did)\s+(\w+)`  
   - Negations (`not`, `no`, `never`) attached to the predicate  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`) and numeric literals (`\d+(\.\d+)?`)  
   - Conditionals (`if … then …`, `unless`) and causal markers (`because`, `since`, `leads to`)  
   - Ordering relations (`before`, `after`, `first`, `last`)  
   Each extracted unit becomes a node with a feature vector **x** ∈ ℝ⁵: `[presence, polarity (±1), numeric value (0 if absent), comparative direction (−1,0,+1), causal strength (0/1)]`.  
2. **Sparse encoding** – A fixed‑size dictionary **D** ∈ ℝᵏˣ⁵ (k≈200) is learned offline via a simple iterative hard‑thresholding algorithm (akin to a sparse autoencoder) using only numpy: for each unit **x**, solve **z = argmin‖x−Dz‖₂² + λ‖z‖₁** by coordinate descent, keeping the top‑s non‑zero entries (s=5). The sparse code **z** is the unit’s representation.  
3. **Constraint propagation** – Build a directed graph **G** where edges encode logical constraints derived from the prompt:  
   - Modus ponens: if node A asserts P and node B asserts “if P then Q”, add edge A→B with weight w=1.  
   - Transitivity: for ordering edges, propagate via Floyd‑Warshall on the adjacency matrix (numpy).  
   - Negation flips polarity of the target node.  
   After propagation, each node obtains a *consistency score* **cᵢ** = σ(∑ⱼ wⱼ·zⱼ·polarityⱼ), where σ is a logistic function implemented with numpy.  
4. **Answer scoring** – For each candidate answer, compute the mean consistency over its constituent nodes: **score = mean(cᵢ)**. Answers with higher scores better satisfy the prompt’s logical constraints.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations, and polarity‑flipped predicates.  

**Novelty** – The combination of a hard‑thresholded sparse autoencoder‑style dictionary with explicit logical constraint propagation (modus ponens, transitivity) is not present in existing pure‑numpy reasoners; prior work either uses bag‑of‑words similarity or separate rule‑based engines without learned sparse feature disentanglement.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and propagates constraints, but limited to shallow syntactic patterns.  
Metacognition: 6/10 — provides a confidence score via consistency, yet lacks explicit self‑monitoring of parsing failures.  
Hypothesis generation: 5/10 — can propose missing propositions by activating dormant dictionary atoms, but no iterative refinement loop.  
Implementability: 9/10 — relies solely on numpy and stdlib; all steps are matrix/vector operations or simple loops.

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

**Forge Timestamp**: 2026-03-31T19:11:20.369450

---

## Code

*No code was produced for this combination.*
