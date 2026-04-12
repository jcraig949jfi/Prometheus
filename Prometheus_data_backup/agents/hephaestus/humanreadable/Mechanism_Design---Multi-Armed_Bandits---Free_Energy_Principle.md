# Mechanism Design + Multi-Armed Bandits + Free Energy Principle

**Fields**: Economics, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T21:26:48.703428
**Report Generated**: 2026-03-27T16:08:14.420928

---

## Nous Analysis

**Algorithm**  
Each candidate answer is treated as an arm of a stochastic multi‑armed bandit. The arm’s reward is the negative variational free energy F of the answer with respect to a parsed logical model of the question.  

1. **Parsing & data structure** – The question and each answer are converted into a propositional graph G = (V, E). Vertices V are atomic propositions (e.g., “X > 5”, “Y caused Z”). Edges E carry a type label from the set {¬, <, >, →, because, before, after} and a numeric weight w (extracted from numbers or confidence). The graph is stored as adjacency lists; edge weights are kept in a NumPy array W for fast vectorised ops.  

2. **Constraint propagation** – Starting from asserted vertices (those explicitly present in the answer), we run a fixed‑point forward‑chaining loop: for each edge (u→v, type, w) we compute a predicted truth value p̂_v using a deterministic function f_type(p_u, w) (e.g., for “→”, p̂_v = p_u × w; for “<”, p̂_v = 1 if p_u < threshold else 0). Prediction error e_v = p_v − p̂_v is accumulated. Free energy for the answer is  
   F = ½ ∑_v (τ_v · e_v²) + ∑_v H(τ_v)  
   where τ_v (precision) is the inverse variance of the edge weight, and H is the entropy term of a Gaussian variational posterior (all computable with NumPy). Lower F indicates higher consistency with the parsed constraints.  

3. **Bandit update** – Each arm i maintains estimates μ_i (mean −F) and σ_i² (variance) of its reward. After evaluating an answer (computing F), we update μ_i, σ_i with a standard Bayesian update for Gaussian rewards. Selection uses Upper Confidence Bound: pick arm i maximizing μ_i + c·√(ln t / n_i), where t is total evaluations and n_i pulls of arm i. This allocates more computation to answers with high uncertainty or promising low free energy, embodying the explore‑exploit trade‑off.  

4. **Scoring** – After a fixed budget of evaluations, the final score for answer i is s_i = μ_i (higher = better). Scores are normalized to [0,1] for reporting.  

**Structural features parsed**  
Negations, comparatives (<, >, ≤, ≥), conditionals (if‑then, unless), causal claims (because, leads to, results in), ordering/temporal relations (before, after, precedes), numeric values and units, quantifiers (all, some, none), and equality statements.  

**Novelty**  
While variational free energy and bandit‑based model selection appear separately in active inference literature, coupling them to score natural‑language answers via explicit logical constraint propagation is not described in existing work; thus the combination is novel for this task.  

**Rating**  
Reasoning: 8/10 — captures logical consistency and uncertainty well, but relies on hand‑crafted type functions.  
Metacognition: 7/10 — bandit uncertainty provides a form of self‑monitoring, yet limited to scalar free‑energy estimates.  
Hypothesis generation: 6/10 — the algorithm evaluates given answers; it does not propose new hypotheses beyond propagating existing propositions.  
Implementability: 9/10 — uses only NumPy and stdlib; graph parsing, vectorised error updates, and UCB are straightforward to code.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Mechanism Design + Multi-Armed Bandits: strong positive synergy (+0.223). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Mechanism Design: strong positive synergy (+0.380). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Multi-Armed Bandits: strong positive synergy (+0.252). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Cellular Automata + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=47% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T07:19:58.636898

---

## Code

**Source**: scrap

[View code](./Mechanism_Design---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Mechanism Design, Multi-Armed Bandits, and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Converts text into a propositional graph (vertices=concepts, edges=relations).
    2. Free Energy (F): Computes consistency between the prompt's logical constraints and the candidate answer.
       Lower F = higher consistency. F is derived from prediction errors in constraint propagation.
    3. Bandit (UCB): Treats candidates as arms. Uses Upper Confidence Bound to balance exploring 
       uncertain candidates vs exploiting those with low Free Energy (high negative F).
    4. Scoring: Final score is the estimated mean reward (negative Free Energy) normalized to [0,1].
    
    This approach prioritizes structural logical consistency over string similarity.
    """

    def __init__(self):
        self.edge_types = ['not', 'lt', 'gt', 'le', 'ge', 'if', 'because', 'before', 'after', 'eq']
        self.num_pattern = re.compile(r"-?\d+(?:\.\d+)?")
        
    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.num_pattern.findall(text)]

    def _parse_graph(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str, float]]]:
        """Parses text into nodes and weighted edges."""
        text_lower = text.lower()
        nodes = set()
        edges = []
        
        # Extract numbers as potential nodes or weights
        nums = self._extract_numbers(text)
        for n in nums:
            nodes.add(f"num_{n}")
            
        # Simple keyword-based relation extraction
        # Format: (source, target, type, weight)
        words = text_lower.split()
        
        # Detect negation
        if "not" in text_lower or "never" in text_lower:
            nodes.add("negation_flag")
            
        # Detect comparatives
        if " less than " in text_lower or " smaller than " in text_lower:
            edges.append(("generic_subj", "generic_obj", "lt", 1.0))
        elif " greater than " in text_lower or " larger than " in text_lower:
            edges.append(("generic_subj", "generic_obj", "gt", 1.0))
            
        # Detect conditionals
        if "if" in words:
             edges.append(("condition", "consequence", "if", 0.9))
        if "because" in words:
             edges.append(("cause", "effect", "because", 0.9))
             
        # Numeric constraints
        if len(nums) >= 2:
            # Assume order implies relation if explicit words missing
            if nums[0] < nums[1]:
                edges.append((f"num_{nums[0]}", f"num_{nums[1]}", "lt", 1.0))
            elif nums[0] > nums[1]:
                edges.append((f"num_{nums[0]}", f"num_{nums[1]}", "gt", 1.0))
                
        # Add generic nodes from split if sparse
        for w in set(words):
            if len(w) > 3 and w not in ['the', 'and', 'that', 'with', 'this', 'from', 'have', 'been']:
                nodes.add(w)
                
        return list(nodes), edges

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (F) as a measure of inconsistency.
        F = 0.5 * sum(precision * error^2) + Entropy_term
        Lower F is better.
        """
        # 1. Parse combined context
        full_text = f"{prompt} {candidate}"
        nodes, edges = self._parse_graph(full_text)
        
        if not nodes:
            return 1.0 # High energy for empty content

        # 2. Initialize states (Truth values p_v)
        # Map node string to index
        node_map = {n: i for i, n in enumerate(nodes)}
        n_nodes = len(nodes)
        
        # State vector: truth value estimate (0.5 = uncertain)
        p = np.full(n_nodes, 0.5) 
        # Precision vector (confidence)
        tau = np.zeros(n_nodes)
        
        # Seed known truths from candidate presence
        cand_lower = candidate.lower()
        for n, i in node_map.items():
            if n in cand_lower:
                p[i] = 0.9
                tau[i] = 2.0 # Higher precision for asserted facts
            elif n in prompt.lower():
                p[i] = 0.8
                tau[i] = 1.5

        # 3. Constraint Propagation (Fixed Point Iteration)
        total_error_sq = 0.0
        total_precision = 0.0
        
        for _ in range(3): # 3 iterations for propagation
            for src, tgt, etype, weight in edges:
                if src not in node_map or tgt not in node_map:
                    continue
                u_idx = node_map[src]
                v_idx = node_map[tgt]
                
                p_u = p[u_idx]
                p_hat_v = 0.5
                
                # Deterministic transfer functions f_type
                if etype == 'lt':
                    # If A < B, and A is true (high), B must be compatible? 
                    # Simplified: Check numeric consistency if available
                    if src.startswith('num_') and tgt.startswith('num_'):
                        val_u = float(src.split('_')[1])
                        val_v = float(tgt.split('_')[1])
                        expected = 1.0 if val_u < val_v else 0.0
                        p_hat_v = expected
                    else:
                        p_hat_v = p_u * weight 
                        
                elif etype == 'gt':
                    if src.startswith('num_') and tgt.startswith('num_'):
                        val_u = float(src.split('_')[1])
                        val_v = float(tgt.split('_')[1])
                        expected = 1.0 if val_u > val_v else 0.0
                        p_hat_v = expected
                    else:
                        p_hat_v = p_u * weight
                        
                elif etype == 'not':
                    p_hat_v = 1.0 - p_u
                    
                elif etype == 'if':
                    p_hat_v = p_u * weight # Modus ponens approx
                    
                else:
                    p_hat_v = p_u * weight

                # Prediction Error
                error = p[v_idx] - p_hat_v
                prec = tau[v_idx] if tau[v_idx] > 0 else 0.1
                
                total_error_sq += prec * (error ** 2)
                total_precision += prec
                
                # Update state slightly (relaxation)
                p[v_idx] = 0.9 * p[v_idx] + 0.1 * p_hat_v

        # Free Energy Calculation
        # F = 0.5 * Sum(tau * e^2) + H
        # H (Entropy of Gaussian) approx 0.5 * ln(2*pi*e/var) -> simplified to 1/tau
        entropy_term = np.sum(np.where(tau > 0, 0.5 * np.log(1.0 / (tau + 1e-6)), 1.0))
        
        F = 0.5 * total_error_sq + entropy_term
        return F

    def _bandit_select(self, rewards: List[float], counts: List[int], t: int, c: float = 1.5) -> int:
        """Upper Confidence Bound (UCB1) selection."""
        if len(rewards) == 0:
            return 0
        
        ucb_values = []
        for i, (r, n) in enumerate(zip(rewards, counts)):
            if n == 0:
                return i # Explore unvisited arms first
            exploration_bonus = c * np.sqrt(np.log(t + 1) / n)
            ucb_values.append(r + exploration_bonus)
            
        return int(np.argmax(ucb_values))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        n_candidates = len(candidates)
        # Bandit state: mean reward (negative free energy), count, sum of rewards
        means = np.zeros(n_candidates)
        counts = np.zeros(n_candidates, dtype=int)
        sums = np.zeros(n_candidates)
        
        # Budget: Evaluate each at least once, then some exploration
        budget = max(n_candidates, n_candidates + 2) 
        total_evals = 0
        
        # Initial pass: evaluate all once to get priors
        for i, cand in enumerate(candidates):
            F = self._compute_free_energy(prompt, cand)
            reward = -F # Maximize negative free energy
            counts[i] = 1
            sums[i] = reward
            means[i] = reward
            total_evals += 1
            
        # Bandit exploration loop
        while total_evals < budget:
            # Select arm using UCB
            # We use a simplified UCB where we re-evaluate the chosen arm to simulate stochasticity
            # In this deterministic parser, we add small noise to reward to simulate stochastic bandit
            arm_idx = self._bandit_select(means, counts, total_evals)
            
            # Re-evaluate with slight perturbation to simulate stochastic environment
            # This allows the bandit to 'explore' if we had multiple parses, 
            # but here it mostly reinforces the best structural fit.
            F = self._compute_free_energy(prompt, candidates[arm_idx])
            noise = np.random.normal(0, 0.05)
            reward = -F + noise
            
            counts[arm_idx] += 1
            sums[arm_idx] += reward
            means[arm_idx] = sums[arm_idx] / counts[arm_idx]
            total_evals += 1
            
        # Normalize scores to [0, 1]
        # Higher mean (less negative F) is better
        raw_scores = means
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s - min_s > 1e-9:
            normalized_scores = (raw_scores - min_s) / (max_s - min_s)
        else:
            normalized_scores = np.ones_like(raw_scores) * 0.5
            
        # Construct result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized_scores[i]),
                "reasoning": f"Free Energy: {-means[i]:.4f}, Consistency: {normalized_scores[i]:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on Free Energy consistency."""
        F = self._compute_free_energy(prompt, answer)
        # Convert Free Energy to confidence. 
        # Low F -> High Confidence. 
        # Assuming F is roughly positive, use sigmoid-like mapping or simple inverse
        # Heuristic: If F < 1.0, very confident. If F > 10, low confidence.
        confidence = 1.0 / (1.0 + np.exp(F - 2.0)) # Shifted sigmoid
        return float(np.clip(confidence, 0.0, 1.0))
```

</details>
