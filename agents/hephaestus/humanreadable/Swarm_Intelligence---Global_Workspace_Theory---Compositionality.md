# Swarm Intelligence + Global Workspace Theory + Compositionality

**Fields**: Biology, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T19:00:31.160552
**Report Generated**: 2026-03-27T23:28:38.552718

---

## Nous Analysis

**Algorithm – Swarm‑Workspace Compositional Scorer (SWCS)**  
Each token or multi‑word unit extracted from the prompt and a candidate answer becomes an *agent*. Agents hold a feature vector **f** ∈ ℝ⁵ (negation, comparative, conditional, numeric, causal) built by regex extraction; the vector entries are 1 if the feature is present, 0 otherwise. All agents are stored in a NumPy array **A** of shape (N,5).  

1. **Local activation** – Each agent computes an initial activation *aᵢ* = **w**·**fᵢ**, where **w** is a fixed weight vector (e.g., [0.2,0.2,0.2,0.2,0.2]) reflecting the importance of each structural feature.  
2. **Swarm competition** – Activations are turned into probabilities via a softmax: *pᵢ* = exp(aᵢ)/Σⱼexp(aⱼ). The top‑k agents (k = √N) are selected to enter the *global workspace*.  
3. **Global broadcast (ignition)** – The workspace holds a binary mask **M** (size N) where selected agents have Mᵢ=1. The workspace representation **W** is the sum of feature vectors of active agents: **W** = Σᵢ Mᵢ **fᵢ**. This **W** is broadcast back to all agents, which update their activation by adding a similarity term: *aᵢ ← aᵢ + α·(**fᵢ**·**W**) (α=0.1).  
4. **Compositionality step** – Using a shallow dependency‑like grammar captured by regex patterns (e.g., “X > Y”, “if X then Y”, “not X”, “because X”), we recursively combine pairs of agents whose spans are adjacent and whose relation matches a pattern, producing a new agent whose feature vector is the concatenation (or logical AND) of the parents’ vectors. This process repeats until no further combinations are possible, yielding a set of *compositional agents* that represent higher‑order structures (e.g., a conditional clause).  
5. **Scoring** – For a candidate answer, we compute its final workspace vector **W_cand** after the same swarm‑workspace‑composition cycles. The score is the normalized dot product: *score* = (**W_prompt**·**W_cand**)/(‖**W_prompt**‖‖**W_cand**‖). Higher scores indicate greater structural and semantic alignment.

**Structural features parsed**  
- Negations (“not”, “no”, “never”)  
- Comparatives and superlatives (“more than”, “less than”, “‑est”, “‑er”)  
- Conditionals (“if … then”, “unless”, “provided that”)  
- Numeric values and units (integers, decimals, percentages)  
- Causal claims (“because”, “due to”, “leads to”)  
- Ordering relations (“before”, “after”, “first”, “last”, “>”, “<”)  

These are captured by a handful of regex rules that output triples (span, type, value) fed into the agent feature vectors.

**Novelty**  
The blend mirrors spreading‑activation models (Global Workspace Theory) and swarm‑based optimization, but adds explicit compositional combination of agents via syntactic patterns—a triad not commonly packaged together in existing reasoning scorers, which usually rely on either pure similarity metrics or rule‑based theorem provers.

**Ratings**  
Reasoning: 7/10 — captures logical structure via compositional agents and constraint‑like broadcasting, yet shallow parsing limits deep inference.  
Metacognition: 5/10 — the algorithm can monitor workspace activation but lacks explicit self‑reflection on its own reasoning process.  
Hypothesis generation: 6/10 — swarm competition yields diverse agent sets that can be interpreted as alternative parses, supporting rudimentary hypothesis exploration.  
Implementability: 9/10 — relies only on NumPy for vector ops and Python’s re module for regex; all steps are straightforward loops and matrix operations.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
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
