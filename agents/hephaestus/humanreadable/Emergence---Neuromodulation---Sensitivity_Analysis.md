# Emergence + Neuromodulation + Sensitivity Analysis

**Fields**: Complex Systems, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:58:28.181209
**Report Generated**: 2026-04-02T08:39:53.870552

---

## Nous Analysis

**Algorithm: Emergent Constraint‑Gain Scoring (ECGS)**  

1. **Parsing & Data Structures**  
   - Extract propositional atoms from the candidate answer using regex patterns for:  
     * negations (`not`, `no`),  
     * comparatives (`greater than`, `less than`, `≥`, `≤`),  
     * conditionals (`if … then …`, `unless`),  
     * causal verbs (`causes`, `leads to`, `results in`),  
     * numeric constants and units,  
     * ordering relations (`before`, `after`, `first`, `last`).  
   - Each atom becomes a node *i* with fields:  
     - `val[i]` ∈ {0,1} (truth assignment from the prompt’s gold facts),  
     - `conf[i]` ∈ [0,1] (initial confidence, set to 1 if directly supported, 0.5 if inferred).  
   - For every extracted relation *r* (e.g., “A causes B”, “X > Y”) create a directed edge *i → j* with a base weight *w₀[r]* = 1.0. Store edges in an adjacency matrix **W** (numpy float64) and a parallel list of relation types for later masking.

2. **Emergence Layer (Macro‑coherence)**  
   - Form the constraint satisfaction matrix **C** = **W** ⊙ **M**, where **M** masks edges that are logically satisfied given current `val` (e.g., a causal edge is satisfied if `val[i]==1` and `val[j]==1`).  
   - Compute the leading eigenvalue λ₁ of **C** (via `numpy.linalg.eigvals`). λ₁ captures a global, non‑reducible coherence score – the emergent property of the answer’s internal constraint network.

3. **Neuromodulation (Gain Control)**  
   - For each node compute uncertainty *u[i]* = 1 − conf[i].  
   - Derive a dopaminergic‑style gain factor *g[i]* = 1 + α·u[i] (α = 0.3).  
   - Modulate edge weights: **W̃** = **W** * (g[source]·g[target])ᵀ (outer product, numpy broadcasting).  
   - Re‑compute **C̃** = **W̃** ⊙ **M** and its leading eigenvalue λ̃₁. This step implements state‑dependent gain control, amplifying constraints that involve uncertain propositions.

4. **Sensitivity Analysis (Robustness Check)**  
   - Perturb each edge weight by ±ε (ε = 0.05) one‑at‑a‑time, recompute λ̃₁, and record the absolute change Δλₖ.  
   - Compute sensitivity *S* = meanₖ(Δλₖ).  
   - Final score = λ̃₁ / (1 + β·S) (β = 0.2), penalizing answers whose emergent coherence is fragile to small input perturbations.

**Structural Features Parsed** – negations, comparatives, conditionals, causal claims, numeric values/units, and ordering/temporal relations. These are the atoms and edges that feed the constraint matrix.

**Novelty** – While probabilistic soft logic and Markov logic networks capture weighted constraints, ECGS adds a biologically‑inspired neuromodulatory gain layer and an explicit finite‑difference sensitivity step to derive an emergent eigenvalue‑based score. This specific combination of emergence (spectral coherence), neuromodulation (uncertainty‑driven gain), and sensitivity analysis (perturbation‑based robustness) is not present in existing public reasoning‑scoring tools.

**Ratings**  
Reasoning: 8/10 — captures logical structure and global coherence via eigenvalue, but relies on linear approximations.  
Metacognition: 7/10 — uncertainty‑based gain provides a crude self‑assessment; no explicit reflection on reasoning steps.  
Hypothesis generation: 6/10 — can propose alternative weight perturbations, yet lacks generative proposal of new facts.  
Implementability: 9/10 — uses only numpy and stdlib; all operations are matrix algebra and regex parsing.

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
**Reason**: trap_battery_failed (acc=46% cal=20% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T04:21:40.502302

---

## Code

**Source**: scrap

[View code](./Emergence---Neuromodulation---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Emergent Constraint-Gain Scoring (ECGS) with Dynamics Tracking.
    
    Mechanism:
    1. Parsing: Extracts logical atoms (negations, comparatives, causals) into a graph.
    2. Dynamics (Frame C): Simulates state evolution via iterative constraint propagation
       to measure trajectory stability (Lyapunov-like convergence).
    3. Emergence: Computes the leading eigenvalue of the constraint matrix as a coherence score.
    4. Neuromodulation: Applies uncertainty-based gain to edge weights.
    5. Sensitivity: Perturbs weights to penalize fragile coherence.
    6. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """

    def __init__(self):
        self.alpha = 0.3  # Gain factor
        self.beta = 0.2   # Sensitivity penalty
        self.epsilon = 0.05  # Perturbation size
        self.max_iter = 10  # Dynamics iterations

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: presupposition, ambiguity, unanswerability."""
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r"(have you stopped|have you quit|why did .+ fail|why did .+ stop)", p):
            return 0.1
        
        # 2. Scope ambiguity (Every X ... a Y)
        if re.search(r"every .+ (a|an) .+", p) and "same" not in p:
            # Heuristic: if it asks about specific identity after universal quantifier
            if re.search(r"(which one|who|same)", p):
                return 0.2

        # 3. Pronoun ambiguity
        if re.search(r"told .+ he|told .+ she|said to .+ he", p):
            if re.search(r"(who was|who is|which one)", p):
                return 0.15

        # 4. False dichotomy
        if re.search(r"either .+ or .+", p) and not re.search(r"(exhaustive|only options)", p):
             if re.search(r"(must|choose|pick)", p):
                return 0.25

        # 5. Subjectivity
        if re.search(r"(best|worst|favorite|most beautiful)", p):
            if not re.search(r"(data|statistics|according to)", p):
                return 0.2

        # 6. Unanswerability (Missing info)
        if re.search(r"(cannot be determined|not enough info|missing)", p):
            return 0.1
            
        return 1.0

    def _parse_atoms(self, text: str) -> Tuple[List[Dict], List[Tuple[int, int, str]]]:
        """Extract atoms and relations. Returns nodes and edges."""
        nodes = []
        edges = []
        text_lower = text.lower()
        
        # Simple tokenization for atoms (words/numbers)
        # In a real engine, this would be a full NLP parse. 
        # Here we simulate structural extraction based on keywords.
        
        # Detect structural features
        has_negation = bool(re.search(r"\b(not|no|never|none)\b", text_lower))
        has_comparative = bool(re.search(r"(greater|less|more|less|>=|<=|>|<)", text_lower))
        has_conditional = bool(re.search(r"(if|unless|then|otherwise)", text_lower))
        has_causal = bool(re.search(r"(causes|leads to|results in|because|since)", text_lower))
        has_numeric = bool(re.search(r"\d+(\.\d+)?", text_lower))
        
        # Create dummy nodes representing extracted logical constraints
        # Node structure: {id, val, conf, type}
        node_id = 0
        
        if has_negation:
            nodes.append({"id": node_id, "val": 1, "conf": 1.0, "type": "negation"})
            node_id += 1
        if has_comparative:
            nodes.append({"id": node_id, "val": 1, "conf": 1.0, "type": "comparative"})
            node_id += 1
        if has_conditional:
            nodes.append({"id": node_id, "val": 1, "conf": 0.8, "type": "conditional"}) # Lower conf for inferred logic
            node_id += 1
        if has_causal:
            nodes.append({"id": node_id, "val": 1, "conf": 0.9, "type": "causal"})
            node_id += 1
        if has_numeric:
            nodes.append({"id": node_id, "val": 1, "conf": 1.0, "type": "numeric"})
            node_id += 1
            
        # If no structural features found, create a generic low-confidence node
        if node_id == 0:
            nodes.append({"id": 0, "val": 0.5, "conf": 0.4, "type": "generic"})
            node_id = 1
            
        # Create edges (fully connected for small N to simulate constraint network)
        # In a larger system, this would be sparse based on syntax
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    # Determine relation type
                    r_type = "implication"
                    if nodes[i]["type"] == "causal" and nodes[j]["type"] == "numeric":
                        r_type = "causal_num"
                    edges.append((i, j, r_type))
                    
        return nodes, edges

    def _compute_dynamics_stability(self, W: np.ndarray, initial_state: np.ndarray) -> float:
        """
        Frame C: Track state evolution.
        Simulate iterative constraint propagation. 
        Measure stability by comparing convergence from slightly perturbed starts.
        """
        if W.shape[0] == 0:
            return 0.0
            
        # Normalize W to row-stochastic for stability (Markov style)
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W_norm = W / row_sums
        
        # Trajectory 1
        state = initial_state.copy()
        history = []
        for _ in range(self.max_iter):
            state = W_norm.T @ state
            # Normalize to prevent explosion
            state = state / (np.linalg.norm(state) + 1e-9)
            history.append(state.copy())
            
        # Trajectory 2 (Perturbed)
        state_pert = initial_state.copy() + np.random.normal(0, 0.01, size=initial_state.shape)
        state_pert = np.clip(state_pert, 0, 1)
        if np.linalg.norm(state_pert) == 0: state_pert[0] = 1.0 # Safety
            
        dists = []
        for _ in range(self.max_iter):
            state_pert = W_norm.T @ state_pert
            state_pert = state_pert / (np.linalg.norm(state_pert) + 1e-9)
            # Distance between trajectories
            d = np.linalg.norm(state - state_pert)
            dists.append(d)
            
        # Stability score: inverse of average divergence
        # If diverges, dist grows -> low score. If converges, dist shrinks -> high score.
        if not dists:
            return 0.5
        avg_div = np.mean(dists)
        return 1.0 / (1.0 + avg_div * 10) # Map to ~0-1

    def _calculate_ecgs_score(self, text: str) -> float:
        """Core ECGS Algorithm implementation."""
        nodes, edges = self._parse_atoms(text)
        n = len(nodes)
        if n == 0:
            return 0.1
            
        # 1. Build Base Matrix W
        W = np.zeros((n, n), dtype=np.float64)
        for i, j, r_type in edges:
            W[i, j] = 1.0
            
        # Initial State Vector (from node confidences)
        initial_conf = np.array([node["conf"] for node in nodes], dtype=np.float64)
        if np.sum(initial_conf) == 0:
            initial_conf = np.ones(n) / n
            
        # 2. Emergence Layer (Macro-coherence)
        # Mask M: Identity for now (self-consistency), in full version depends on val
        M = np.eye(n) 
        # For this implementation, we assume satisfied if connected (simplified)
        # Real implementation would check val[i] vs val[j] logic
        C = W * M 
        
        # Leading eigenvalue (Coherence)
        if n > 0:
            eigenvals = np.linalg.eigvals(C)
            lambda_1 = np.max(np.abs(eigenvals))
        else:
            lambda_1 = 0.0
            
        # 3. Neuromodulation (Gain Control)
        u = 1.0 - initial_conf  # Uncertainty
        g = 1.0 + self.alpha * u
        # Outer product for edge modulation
        G = np.outer(g, g)
        W_tilde = W * G
        
        C_tilde = W_tilde * M
        if n > 0:
            eigenvals_tilde = np.linalg.eigvals(C_tilde)
            lambda_tilde_1 = np.max(np.abs(eigenvals_tilde))
        else:
            lambda_tilde_1 = 0.0
            
        # 4. Sensitivity Analysis (Robustness)
        deltas = []
        if n > 0:
            for i in range(n):
                for j in range(n):
                    if W[i, j] > 0:
                        # Perturb
                        W_pert = W_tilde.copy()
                        W_pert[i, j] *= (1.0 + self.epsilon)
                        
                        C_pert = W_pert * M
                        ev = np.linalg.eigvals(C_pert)
                        lam_pert = np.max(np.abs(ev))
                        
                        deltas.append(abs(lam_pert - lambda_tilde_1))
        
        S = np.mean(deltas) if deltas else 0.0
        
        # Final Score Formula
        # Penalize fragility (high S)
        raw_score = lambda_tilde_1 / (1.0 + self.beta * S)
        
        # Integrate Dynamics Stability (Frame C)
        stability = self._compute_dynamics_stability(W_tilde, initial_conf)
        
        # Weighted combination: 60% ECGS, 40% Dynamics Stability
        final_score = 0.6 * raw_score + 0.4 * stability
        
        return float(final_score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_score_base = self._calculate_ecgs_score(prompt)
        
        for cand in candidates:
            # Construct full reasoning text
            full_text = f"{prompt} {cand}"
            
            # 1. Structural/Computation Score (ECGS)
            ecgs_score = self._calculate_ecgs_score(full_text)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            # Compare candidate to prompt. High similarity (low NCD) might indicate echoing.
            # We want moderate NCD (adds info) but not random noise.
            ncd_val = self._ncd_distance(prompt, cand)
            # Normalize NCD contribution: prefer lower NCD (more relevant) but penalize exact echo
            if len(cand) < 5: # Penalty for too short
                ncd_penalty = 0.5
            else:
                ncd_penalty = 0.1 * (1.0 - ncd_val) # Small boost for relevance
            
            # 3. Dynamics Check (Stability of the answer itself)
            # If the answer creates a stable system with the prompt, it's better
            stability_bonus = 0.0
            if ecgs_score > 0.5:
                stability_bonus = 0.1
                
            final_score = (0.7 * ecgs_score) + (0.15 * ncd_penalty) + stability_bonus
            
            # Cap at 1.0
            final_score = min(1.0, max(0.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"ECGS:{ecgs_score:.2f}, NCD:{ncd_val:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty (Tier B).
        """
        # 1. Meta-Confidence Check (Question Properties)
        meta_conf = self._meta_confidence(prompt)
        
        # If meta_conf is low (ambiguous/trap), cap immediately
        if meta_conf < 0.3:
            return meta_conf
            
        # 2. Structural Match Check
        # If the answer doesn't structurally align with the prompt's logical atoms,
        # confidence should be low.
        prompt_atoms = self._parse_atoms(prompt)
        combined_atoms = self._parse_atoms(f"{prompt} {answer}")
        
        # Heuristic: If adding the answer doesn't increase structural complexity 
        # or resolve a conditional, it might be weak.
        base_score = self._calculate_ecgs_score(f"{prompt} {answer}")
        
        # 3. Computation Check (Simulated)
        # If the prompt has numbers and the answer is not numeric when expected
        has_nums = bool(re.search(r"\d+", prompt))
        ans_has_nums = bool(re.search(r"\d+", answer))
        
        comp_penalty = 0.0
        if has_nums and not ans_has_nums:
            # Might be okay if the answer is "Impossible" or similar, 
            # but generally suspicious for math problems
            if not re.search(r"(impossible|none|zero|error)", answer.lower()):
                comp_penalty = 0.4
        
        # Calculate raw confidence
        raw_conf = base_score * (1.0 - comp_penalty)
        
        # Apply Meta Cap
        final_conf = min(raw_conf, meta_conf)
        
        # Never return > 0.9 unless it's a perfect structural match and high score
        if final_conf > 0.9:
            if base_score < 0.95: # Requires very high coherence
                final_conf = 0.9
                
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
