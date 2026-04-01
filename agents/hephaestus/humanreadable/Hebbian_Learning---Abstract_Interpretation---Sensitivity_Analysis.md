# Hebbian Learning + Abstract Interpretation + Sensitivity Analysis

**Fields**: Neuroscience, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T18:26:41.363275
**Report Generated**: 2026-03-31T14:34:57.078080

---

## Nous Analysis

The algorithm builds a weighted proposition graph from the prompt and each candidate answer, then propagates abstract constraints and measures sensitivity to perturbations to produce a robustness‑based score.

1. **Parsing & Graph Construction** – Tokenize text with regex to extract atomic propositions:  
   - Literals (e.g., “the cat is black”) → nodes with Boolean domain.  
   - Comparatives (“greater than”, “less than”) → nodes with interval domain.  
   - Conditionals (“if X then Y”) → directed edges labeled *implies*.  
   - Causal phrasing (“because”, “leads to”) → edges labeled *causes*.  
   - Negations flip the polarity flag on the target node.  
   Each co‑occurrence of two propositions within a sliding window increments a Hebbian weight w₍ᵢⱼ₎ (initialized to 0, incremented by 1). After scanning the whole prompt+answer, weights are normalized to [0,1] to form the adjacency matrix W.

2. **Abstract Interpretation (Constraint Propagation)** – Assign each node an abstract value:  
   - Boolean nodes: {True, False, ⊤}.  
   - Numeric nodes: intervals [l,u] initialized from extracted numbers (±ε for uncertainty).  
   Propagate using a work‑list algorithm: for each edge i→j with label *implies*, tighten j’s domain to the intersection of its current domain and the image of i’s domain under the logical operator; for *causes* apply a monotone transfer function (e.g., add a small delta). Iterate until a fixpoint (O(V·E) with numpy matrix ops). The resulting domains give a *base satisfaction score* S₀ = Σ saturation(node) / |nodes|, where saturation is 1 if the domain is a singleton True/False or a narrow interval, 0 otherwise.

3. **Sensitivity Analysis** – For each atomic feature f (token, number, polarity), create a perturbed copy of the prompt+answer where f is flipped (negation toggled, number ±δ, comparative direction reversed). Re‑run the propagation to obtain S₍f₎. Compute sensitivity σ = std₍f₎(|S₀ − S₍f₎|) / (|S₀|+ε). The final robustness score is S = S₀ · (1 − σ), penalizing answers whose satisfaction hinges on fragile propositions.

**Structural features parsed**: negations, comparatives (>/<, ≥/≤), conditionals (if‑then), causal claims (because, leads to), ordering relations (before/after), numeric values, quantifiers (all, some), and conjunctive/disjunctive connectives.

**Novelty**: While Hebbian weighting, abstract interpretation, and sensitivity analysis each appear separately in NLP or program analysis, their tight integration—using co‑occurrence to weight a constraint‑propagation graph and then scoring by perturbation stability—has not been published as a unified answer‑scoring method, making the combination novel for this task.

**Ratings**  
Reasoning: 7/10 — captures logical structure and propagates constraints, but still limited to shallow linguistic patterns.  
Metacognition: 5/10 — provides a sensitivity estimate but lacks explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 6/10 — perturbations generate alternative worlds, enabling rudimentary counter‑factual hypotheses.  
Implementability: 8/10 — relies only on regex, numpy arrays, and standard‑library data structures; no external APIs or neural nets required.

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
