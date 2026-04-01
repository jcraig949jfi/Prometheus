# Morphogenesis + Compositional Semantics + Sensitivity Analysis

**Fields**: Biology, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T09:48:59.692961
**Report Generated**: 2026-03-31T14:34:55.935914

---

## Nous Analysis

**Algorithm**  
1. **Parsing & graph construction** – Use a handful of regex patterns to extract atomic propositions and relational predicates from the prompt and each candidate answer:  
   - Negations: `\bnot\b|\bno\b|\bnever\b`  
   - Comparatives: `\b(greater|less|more|fewer|higher|lower)\b.*\bthan\b`  
   - Conditionals: `\bif\b.*\bthen\b|\bunless\b`  
   - Causal claims: `\bcauses?\b|\bleads\s+to\b|\bresults\s+in\b`  
   - Numeric values: `\d+(\.\d+)?\s*[a-zA-Z%]+`  
   - Ordering: `\bbefore\b|\bafter\b|\bfirst\b|\blast\b|\bprevious\b|\bnext\b`  
   Each extracted triple (subject, predicate, object) becomes a node; directed edges encode the predicate type (e.g., “causes”, “>”, “if‑then”). Store the adjacency matrix **A** (float32) and a weight matrix **W** where each edge weight reflects the strength extracted from modality cues (e.g., “strongly” → 0.9, “possibly” → 0.4).  

2. **Initial truth vector** – For every atomic proposition *p* assign a base truth value *x₀[p]* ∈ {0,1} using a simple lookup: affirmative statements → 1, negated → 0, uncertain modal → 0.5. This yields a numpy vector **x₀**.  

3. **Reaction‑diffusion constraint propagation** – Iterate a discrete reaction‑diffusion update that blends diffusion (contextual smoothing) with logical reaction (constraint enforcement):  

   ```
   x_{t+1} = x_t + D * (L @ x_t) + R(x_t)
   ```  

   - *L* = degree‑minus‑adjacency Laplacian derived from **A** (numpy).  
   - *D* diffusion coefficient (fixed 0.1).  
   - *R* enforces logical constraints: for each edge (i→j) with predicate type, apply a numpy‑based truth‑table:  
        *if‑then*: x[j] = max(x[j], x[i])  
        *causes*: x[j] = max(x[j], 0.8 * x[i])  
        *>*: if both nodes are numeric, enforce ordering via a hinge penalty added to **x**.  
   Iterate until ‖x_{t+1}‑x_t‖₂ < 1e‑4 or max 100 steps.  

4. **Sensitivity‑based scoring** – After convergence, compute the Jacobian of the final score *s = mean(x_final)* w.r.t. each atomic proposition using central finite differences (perturb each x₀[p] by ±0.01, re‑run the diffusion, measure Δs). The sensitivity vector **σ** quantifies how fragile the answer is to input perturbations. Define robustness *r = 1 / (1 + ‖σ‖₁)*. The candidate’s final score is *s * r*. Higher scores indicate answers that are both true‑like under the extracted constraints and robust to small perturbations.  

**Structural features parsed** – negations, comparatives, conditionals, causal verbs, numeric quantities with units, and temporal/ordering relations.  

**Novelty** – The triple fusion of reaction‑diffusion smoothing (morphogenesis), compositional truth‑table combination (compositional semantics), and finite‑difference sensitivity analysis is not present in existing QA scoring tools; it resembles soft‑logic networks and differentiable reasoners but adds an explicit robustness layer, making the combination novel.  

**Rating**  
Reasoning: 7/10 — captures logical structure and propagates constraints, but limited to first‑order rules.  
Metacognition: 5/10 — provides a sensitivity metric yet does not reflect on its own parsing failures.  
Hypothesis generation: 4/10 — focuses on evaluating given answers, not generating new ones.  
Implementability: 8/10 — relies only on regex, numpy matrix ops, and simple loops; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
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
