# Global Workspace Theory + Causal Inference + Sensitivity Analysis

**Fields**: Cognitive Science, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:48:48.565693
**Report Generated**: 2026-03-31T14:34:55.976913

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using regex‑based patterns we extract atomic propositions *pᵢ* from the prompt and each candidate answer. Each proposition receives a node in a directed acyclic graph (DAG). Edges represent causal or conditional relations identified by cue phrases (“because”, “if … then”, “leads to”, “results in”). Negations flip a node’s polarity flag; comparatives and ordering relations generate auxiliary nodes (e.g., *x>y*). Numeric literals become value‑attached nodes.  
2. **Global workspace initialization** – All nodes from the prompt are inserted into the workspace with an initial activation *aᵢ = confidence(pᵢ)* (confidence derived from cue strength: explicit statements = 1.0, hedged = 0.7, speculative = 0.4). Nodes not present start at 0.  
3. **Ignition & broadcasting** – Repeatedly apply a constraint‑propagation rule: for each edge *u → v*, if *aᵤ* exceeds a threshold τ (e.g., 0.5), increase *aᵥ* by *w·aᵤ* where *w* is the edge weight (default 0.6). After each sweep, renormalize activations to [0,1]. This mimics global broadcast: activated information spreads until convergence (no change >1e‑3).  
4. **Answer scoring** – For a candidate answer, compute *S = Σᵢ aᵢ·I(pᵢ∈answer)*, where *I* is 1 if the proposition (or its negation) appears in the answer. This yields a raw consistency score.  
5. **Sensitivity analysis** – Perturb each prompt node’s initial confidence by ±ε (ε=0.1) and re‑run steps 2‑4, recording the variation ΔSᵢ. The robustness metric *R = 1 / (1 + std(ΔS))*. Final score = *S·R*. High scores require strong, widely activated support and low sensitivity to input noise.  

**Structural features parsed** – Negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then”, “provided that”), causal claims (“because”, “leads to”, “results in”), ordering/temporal relations (“before”, “after”, “greater than”), numeric values and units, quantifiers (“all”, “some”, “none”).  

**Novelty** – While argument‑graph models and causal DAGs appear in QA literature, coupling them with a Global Workspace‑style activation broadcast and an explicit sensitivity‑analysis robustness term is not documented in existing systems. The triple combination yields a distinct scoring mechanism that evaluates both consistency and stability of reasoning.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and propagates support, but relies on hand‑crafted cue weights.  
Metacognition: 6/10 — sensitivity term provides a crude self‑check, yet no explicit monitoring of reasoning steps.  
Hypothesis generation: 5/10 — focuses on evaluating given hypotheses; generation would need additional abductive modules.  
Implementability: 9/10 — uses only regex, numpy for matrix‑style updates, and standard‑library containers; no external APIs or learning.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
