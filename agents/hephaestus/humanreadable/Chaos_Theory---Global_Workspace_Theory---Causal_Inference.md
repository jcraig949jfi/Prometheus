# Chaos Theory + Global Workspace Theory + Causal Inference

**Fields**: Physics, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T19:34:45.609217
**Report Generated**: 2026-03-31T20:00:10.409576

---

## Nous Analysis

**Algorithm: Sensitivity‑Weighted Causal Broadcast (SWCB)**  
The tool builds a directed acyclic graph (DAG) `G = (V, E)` where each node `v ∈ V` represents a proposition extracted from the prompt or a candidate answer (e.g., “X causes Y”, “¬A”, “B > C”). Edges encode causal or logical relations (do‑calculus style: `X → Y` if the text contains a causal claim, `X ⇒ Y` for conditional statements, `X ≺ Y` for ordering).  

1. **Parsing & Data Structures**  
   - Use regex to extract:  
     * numeric values (`\d+(\.\d+)?`) → stored as floats in a node attribute `value`.  
     * negations (`not`, `no`, `never`) → node attribute `polarity = -1`.  
     * comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`) → edge type `order`.  
     * conditionals (`if … then …`, `when`) → edge type `cond`.  
     * causal cue verbs (`cause`, leads to, results in, because) → edge type `causal`.  
   - Each node gets a feature vector `f_v = [polarity, value_norm, type_onehot]` (numpy arrays).  
   - The adjacency matrix `A` (|V|×|V|) stores edge weights: `1.0` for definite relations, `0.5` for uncertain (e.g., modal verbs), `0.0` otherwise.  

2. **Constraint Propagation (Global Workspace Ignition)**  
   - Initialize activation `a_v = sigmoid(w·f_v)` where `w` are fixed weights (e.g., `[0.4, 0.3, 0.3]`).  
   - Iterate: `a ← σ(Aᵀ a + b)` (bias `b = 0.1`) for `T=5` steps. This mimics a global broadcast: activations spread through the workspace, reinforcing nodes that are jointly supported by multiple premises.  
   - After convergence, compute **Lyapunov‑like sensitivity** for each candidate answer `c`:  
     `S_c = Σ_{v∈c} |a_v - a_v⁰|` where `a_v⁰` is the pre‑propagation activation. Larger `S_c` indicates the answer is highly sensitive to small changes in premise activation — i.e., it relies on fragile chains.  

3. **Scoring Logic**  
   - Base score `B_c = mean(a_v)` over nodes in the candidate.  
   - Final score `Score_c = B_c * exp(-λ·S_c)` with λ=0.5 (penalizes answers that depend on unstable causal paths).  
   - The candidate with the highest `Score_c` is selected.  

**Structural Features Parsed**  
Negations, comparatives, conditionals, numeric values, explicit causal claims, ordering relations, and modal uncertainty (e.g., “might”, “could”).  

**Novelty**  
The combination mirrors existing neuro‑symbolic ideas (e.g., Probabilistic Soft Logic, Neural Theorem Provers) but replaces learned parameters with deterministic, chaos‑inspired sensitivity measures and a global‑workspace style activation spread. No prior work couples Lyapunov exponent‑style sensitivity with a broadcast‑based constraint solver in a pure‑numpy implementation, making the approach novel in this specific formulation.  

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure, causal direction, and sensitivity to perturbations, yielding nuanced scoring beyond simple similarity.  
Metacognition: 6/10 — It can detect unstable reasoning chains (high sensitivity) but does not explicitly reason about its own confidence or revision strategies.  
Hypothesis generation: 5/10 — The system evaluates given candidates; it does not generate new hypotheses beyond the provided answer set.  
Implementability: 9/10 — All components (regex parsing, numpy matrix ops, sigmoid, exponent) rely only on the standard library and numpy, making it straightforward to code and run.

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

**Forge Timestamp**: 2026-03-31T19:59:14.432713

---

## Code

*No code was produced for this combination.*
