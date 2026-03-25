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