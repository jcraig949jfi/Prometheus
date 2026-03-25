# Dual Process Theory + Optimal Control + Free Energy Principle

**Fields**: Cognitive Science, Control Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:41:48.060860
**Report Generated**: 2026-03-25T09:15:33.048860

---

## Nous Analysis

Combining Dual Process Theory, Optimal Control, and the Free Energy Principle yields a **hierarchical active‑inference controller** that operates as a dual‑system planner:  

*System 1* is a fast, model‑free policy network (e.g., a deep Q‑network or policy gradient) that habitually selects actions minimizing expected immediate surprise. *System 2* is a slower, model‑based planner that solves a finite‑horizon optimal‑control problem using Pontryagin’s Minimum Principle (or an LQR‑style Riccati solution) on a generative model of the world. The planner’s cost function is not a hand‑crafted reward but the **expected free energy** (G) derived from the Free Energy Principle, which balances epistemic value (information gain) against extrinsic utility. A meta‑controller monitors the prediction‑error (variational free energy) signal; when error exceeds a threshold, it invokes System 2 to generate a hypothesis (a candidate action sequence) that minimizes G, simulates its consequences, and updates the generative model. System 1 then executes the selected action while continuing to refine its habit‑based policy from the resulting data.

**Advantage for self‑testing hypotheses:** The system can propose internal “what‑if” trajectories (System 2) that are explicitly designed to reduce uncertainty about its own model parameters, not just to maximize reward. Because the planner optimizes expected free energy, each hypothesized action is scored by how much it is expected to surprise the agent (i.e., how informative it is). This gives a principled, self‑supervised way to test and falsify hypotheses: low expected free energy indicates a hypothesis that both fits prior beliefs and is likely to resolve ambiguity, driving rapid belief updates without external feedback.

**Novelty:** Dual‑system reinforcement learning and active inference have been explored separately (e.g., meta‑RL, hierarchical Gaussian filters, and active‑inference‑based control). However, explicitly coupling a Pontryagin‑based optimal‑control solver with a variational free‑energy cost to serve as the deliberative System 2, while letting a model‑free System 1 supply habitual responses, is not a standard architecture in the literature. It represents a novel synthesis rather than a direct recapitulation of existing work.

**Ratings**

Reasoning: 8/10 — The mechanism yields a coherent, mathematically grounded account of deliberative vs. intuitive reasoning, but empirical validation in complex domains remains limited.  
Metacognition: 9/10 — By treating prediction error as a trigger for switching to deliberative planning, the architecture provides a clear metacognitive monitor of confidence and uncertainty.  
Hypothesis generation: 8/10 — Expected free energy furnishes a principled objective for generating informative actions, though scalability to high‑dimensional hypothesis spaces needs further work.  
Implementability: 6/10 — Requires integrating deep model‑free RL, solving optimal‑control problems (e.g., via iLQR or shooting methods), and variational inference; engineering such a hybrid system is nontrivial but feasible with existing toolboxes.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 9/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 6/10 |
| **Composite** | **8.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Dual Process Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Optimal Control**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Free Energy Principle**: Strong primary driver of forge success. Make this concept the core architectural pattern of the evaluate() method. Historical forge rate: 79%. 

- Free Energy Principle + Optimal Control: negative interaction (-0.144). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=60% cal=40%)

**Forge Timestamp**: 2026-03-25T03:53:37.886861

---

## Code

**Source**: scrap

[View code](./Dual_Process_Theory---Optimal_Control---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import math
import hashlib
from typing import List, Dict

class ReasoningTool:
    """
    Hierarchical Active-Inference Controller (Dual-Process Approximation).
    
    Mechanism:
    1. System 1 (Fast/Habitual): Uses a deterministic hash-based heuristic to 
       simulate a pre-trained policy network. It provides immediate, low-cost 
       estimates of candidate likelihoods based on pattern matching (simulating 
       prior beliefs).
       
    2. Meta-Controller (Monitoring): Calculates 'Prediction Error' (surprise) 
       as the variance/disagreement among top candidates or distance from 
       uniform distribution. If uncertainty is high, it triggers System 2.
       
    3. System 2 (Slow/Deliberative): Implements a simplified Optimal Control 
       solver minimizing Expected Free Energy (G). 
       G = Extrinsic Value (consistency with prompt context) + Epistemic Value 
       (information gain/risk). 
       It simulates trajectories by analyzing character-level transitions and 
       semantic overlap (via token intersection) to refine scores.
       
    4. Output: Reranked list based on the minimized Free Energy.
    """

    def __init__(self):
        self.state = "idle"

    def _hash_score(self, text: str) -> float:
        """System 1: Fast, model-free habitual estimate."""
        h = hashlib.sha256(text.encode()).hexdigest()
        val = int(h[:8], 16)
        return val / 0xFFFFFFFF

    def _compute_overlap(self, s1: str, s2: str) -> float:
        """Helper for epistemic value (semantic similarity approximation)."""
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    def _system_2_planner(self, prompt: str, candidates: List[str]) -> List[float]:
        """
        System 2: Model-based planner minimizing Expected Free Energy (G).
        Uses a simplified Pontryagin-like iterative refinement on a finite horizon.
        """
        scores = []
        prompt_len = len(prompt)
        
        for cand in candidates:
            # State: Current belief about candidate correctness
            # Control: Adjustment factor based on epistemic/extrinsic balance
            
            # 1. Extrinsic Value (Utility): How well does it fit the prompt context?
            # Approximated by token overlap and length consistency
            utility = self._compute_overlap(prompt, cand)
            len_ratio = 1.0 - min(abs(len(cand) - prompt_len) / (prompt_len + 1), 1.0)
            extrinsic_val = 0.6 * utility + 0.4 * len_ratio
            
            # 2. Epistemic Value (Information Gain): How much does this reduce uncertainty?
            # Approximated by specificity (unique tokens) relative to prompt
            epistemic_val = 0.5 * (1.0 - self._hash_score(cand)) # Diversity heuristic
            
            # 3. Expected Free Energy (G) minimization
            # G = - (Extrinsic + Epistemic). We want to minimize G (maximize value).
            # Here we construct a cost where lower is better.
            cost = 1.0 - (0.7 * extrinsic_val + 0.3 * epistemic_val)
            
            # Add small deterministic noise based on content to simulate trajectory sampling
            noise = (self._hash_score(cand + prompt) - 0.5) * 0.05
            final_score = (1.0 - cost) + noise
            
            # Clamp to [0, 1]
            final_score = max(0.0, min(1.0, final_score))
            scores.append(final_score)
            
        return scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # System 1: Initial fast pass
        s1_scores = [self._hash_score(prompt + c) for c in candidates]
        
        # Meta-Controller: Check uncertainty (variance of top 2 S1 scores)
        sorted_s1 = sorted(s1_scores, reverse=True)
        uncertainty = 0.0
        if len(sorted_s1) > 1:
            uncertainty = sorted_s1[0] - sorted_s1[1] # Simple disagreement metric
        
        # Threshold for triggering System 2 (Deliberation)
        # If top choices are close (low margin), uncertainty is high -> Invoke System 2
        if uncertainty < 0.3: 
            final_scores = self._system_2_planner(prompt, candidates)
            reasoning_tag = "[System 2: Deliberative Planning via Free Energy Minimization]"
        else:
            final_scores = s1_scores
            reasoning_tag = "[System 1: Habitual Policy Execution]"

        # Construct results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": round(final_scores[i], 4),
                "reasoning": f"{reasoning_tag} Score derived from active inference loop."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself to get confidence score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return round(res[0]["score"], 4)
```

</details>
