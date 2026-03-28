# Reinforcement Learning + Hebbian Learning + Free Energy Principle

**Fields**: Computer Science, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:59:51.782061
**Report Generated**: 2026-03-27T18:24:04.882839

---

## Nous Analysis

**Algorithm**  
We build a lightweight “predictive‑coding agent” that treats a parsed question‑answer pair as a dynamical system.  

1. **Data structures**  
   - `nodes`: list of propositional units extracted from the text (e.g., “X > Y”, “not Z”, numeric constants).  
   - `adj`: `numpy.ndarray` of shape `(n,n)` – weighted adjacency matrix; `adj[i,j]` is the synaptic strength from node j to node i.  
   - `x`: activity vector `(n,)` – current belief levels of each node (initially a one‑hot encoding of lexical features).  
   - `w_score`: weight vector `(n,)` for the policy that maps activity to a scalar score.  
   - Hyper‑parameters: learning rates `η_hebb` (Hebbian), `η_rl` (RL), discount `γ`.  

2. **Forward pass (prediction)**  
   Repeatedly compute `x ← sigmoid(adj @ x)` until ‖Δx‖ < 1e‑3 or 10 iterations. This implements variational free‑energy minimization: the fixed point minimizes prediction error between top‑down predictions (`adj @ x`) and bottom‑up sensory input (the initial lexical encoding).  

3. **Free‑energy (prediction error)**  
   `F = 0.5 * np.sum((x - x0)**2)`, where `x0` is the clamped input vector (lexical features). Lower `F` → higher expected reward.  

4. **Reward signal**  
   `r = -F` (negative free energy). If a ground‑truth correctness label is available, we add a term `+λ * correctness` to shape the reward toward the true answer.  

5. **Hebbian weight update**  
   After each forward pass, adjust synapses:  
   `adj += η_hebb * (np.outer(x, x) * r)`.  
   This is the classic “neurons that fire together wire together” rule, gated by the reward (prediction‑error reduction).  

6. **Policy (score) update – REINFORCE**  
   Compute score `s = sigmoid(w_score @ x)`.  
   Baseline `b` = running average of `r`.  
   Gradient: `∂J/∂w_score = η_rl * (r - b) * s * (1 - s) * x`.  
   Update `w_score += ∂J/∂w_score`.  

The final score `s` is returned for each candidate answer. All operations use only `numpy` and the Python standard library.

**Parsed structural features**  
The parser extracts: negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal claims (“because”, “leads to”), ordering relations (“before”, “after”), numeric values and units, quantifiers (“all”, “some”), and conjunction/disjunction markers. These become nodes and typed edges in `adj`.

**Novelty**  
Pure Hebbian RL or predictive‑coding models exist in neuroscience literature, but their joint application to symbolic text‑reasoning scoring — using free‑energy as a reward signal, Hebbian synaptic updates, and a policy‑gradient scorer — has not been reported in the NLP or automated reasoning communities. Hence the combination is novel for this task.

**Rating**  
Reasoning: 7/10 — captures logical structure and uncertainty via prediction error, but limited depth of inference.  
Metacognition: 6/10 — baseline reward provides crude self‑monitoring; no explicit uncertainty estimation.  
Hypothesis generation: 5/10 — score reflects plausibility, not generative hypothesis formation.  
Implementability: 9/10 — relies only on numpy arrays and simple loops; easily coded in <150 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
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
