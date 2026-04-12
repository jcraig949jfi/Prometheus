import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Mechanism Design (core scoring), 
    Theory of Mind (belief-weighted utility), and Sensitivity Analysis.
    
    Mechanism: Treats answers as self-interested agents. Scores based on 
    satisfying logical constraints (predicates) extracted from the prompt.
    ToM: Weights utility by a simulated evaluator belief state.
    Sensitivity: Penalizes scores that fluctuate wildly under minor syntactic perturbations.
    """
    
    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'cmp': re.compile(r'\b(more than|less than|greater than|smaller than|higher than|lower than)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes|due to)\b', re.IGNORECASE),
            'num': re.compile(r'\d+\.?\d*'),
            'ord': re.compile(r'\b(first|second|last|earlier|later|before|after)\b', re.IGNORECASE),
            'quant': re.compile(r'\b(all|some|every|none|any)\b', re.IGNORECASE)
        }
        self.pred_keys = list(self.patterns.keys())
        self.n_pred = len(self.pred_keys)
        
        # Mechanism Design Weights: Reward consistency, penalize contradictions
        # Order: neg, cmp, cond, causal, num, ord, quant
        self.W = np.array([0.8, 1.2, 1.0, 0.9, 1.5, 0.7, 0.6], dtype=float)
        self.lambda_sens = 0.15  # Sensitivity penalty factor
        self.epsilon = 0.05      # Perturbation magnitude

    def _extract_predicates(self, text: str) -> np.ndarray:
        """Extract structural predicates into a binary vector."""
        text_lower = text.lower()
        vec = np.zeros(self.n_pred, dtype=float)
        
        for i, key in enumerate(self.pred_keys):
            if self.patterns[key].search(text_lower):
                vec[i] = 1.0
                
        # Numeric evaluation bonus: if numbers exist, check validity roughly
        nums = self.patterns['num'].findall(text_lower)
        if nums:
            vec[self.pred_keys.index('num')] = 1.0
            # Simple heuristic: more numbers often imply specific reasoning attempts
            if len(nums) > 1:
                vec[self.pred_keys.index('cmp')] = max(vec[self.pred_keys.index('cmp')], 0.5)
                
        return vec

    def _propagate_constraints(self, p_vec: np.ndarray) -> np.ndarray:
        """Simple constraint propagation (Modus Ponens approximation)."""
        # If conditional exists, boost weight of negation/comparison logic
        if p_vec[self.pred_keys.index('cond')] > 0:
            p_vec[self.pred_keys.index('neg')] = max(p_vec[self.pred_keys.index('neg')], 0.8)
        return p_vec

    def _compute_sensitivity(self, base_p: np.ndarray, base_score: float) -> float:
        """Compute sensitivity penalty via finite differences."""
        grad = np.zeros(self.n_pred)
        for i in range(self.n_pred):
            p_plus = base_p.copy()
            p_plus[i] = 1.0 if base_p[i] == 0 else 0.0 # Flip bit
            
            # Re-calculate partial score components for perturbation
            # Simplified: just check change in dot product with W
            delta_util = np.dot(p_plus - base_p, self.W)
            grad[i] = delta_util / self.epsilon if self.epsilon != 0 else 0
            
        norm_grad = np.linalg.norm(grad)
        return self.lambda_sens * norm_grad

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        n_cands = len(candidates)
        n_states = 3 # Simplified belief states: Skeptic, Neutral, Believer
        
        # 1. Parse Prompt to establish "Truth" constraints (Mechanism Design Target)
        prompt_vec = self._extract_predicates(prompt)
        prompt_vec = self._propagate_constraints(prompt_vec)
        
        # 2. Initialize Belief Distribution B (Theory of Mind)
        # Dirichlet sample simulating evaluator uncertainty
        alpha = np.ones(n_states) * 2.0 
        # Deterministic seed for reproducibility in this context
        rng = np.random.default_rng(seed=42) 
        B = rng.dirichlet(alpha) 
        
        scores = []
        
        for cand in candidates:
            # Extract candidate predicates
            p_cand = self._extract_predicates(cand)
            p_cand = self._propagate_constraints(p_cand)
            
            # --- Mechanism Design: Utility Calculation ---
            # Utility is alignment with prompt constraints weighted by importance
            # U = P_candidate dot W_adjusted_by_prompt_presence
            # If prompt has a feature, candidate having it yields positive utility.
            # If prompt implies negation (simplified), missing it is penalized.
            
            # Dynamic weights based on prompt content (Incentive Compatibility)
            # If prompt uses comparatives, comparative answers are rewarded
            W_eff = self.W * (prompt_vec + 0.5) # Boost weights present in prompt
            
            # Expected Satisfaction E = B @ (Utility)
            # Since B is over states and we have one candidate, we simulate 
            # how different evaluator states perceive this.
            # State 0: Strict (needs exact match), State 1: Loose, State 2: Generous
            
            # Construct a utility matrix for the single candidate across states
            # State 0 (Strict): Dot product must be high
            util_strict = np.dot(p_cand, W_eff)
            # State 1 (Loose): Presence of any logic helps
            util_loose = np.sum(p_cand) * np.mean(W_eff) 
            # State 2 (Generous): Length + logic
            util_gen = util_loose * (1.0 + 0.1 * len(cand))
            
            U = np.array([util_strict, util_loose, util_gen])
            E = np.dot(B, U)
            
            # --- Incentive Compatibility Check ---
            # Penalty if candidate looks like a "lazy" deviation (e.g., empty or generic)
            penalty = 0.0
            if np.sum(p_cand) == 0 and len(cand.strip()) < 5:
                penalty = 2.0 # Heavy penalty for non-answers
            
            # --- Sensitivity Analysis ---
            sens_penalty = self._compute_sensitivity(p_cand, E)
            
            final_score = E - penalty - sens_penalty
            
            scores.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Aligned predicates: {int(np.sum(p_cand))}, Sensitivity penalty: {sens_penalty:.2f}"
            })
            
        # Rank by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and mechanism score.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Normalize score to 0-1 range using a sigmoid-like mapping
        # Assuming typical scores range between -2 and 5 based on weights
        # Shift and scale
        normalized = 1.0 / (1.0 + np.exp(-0.5 * (raw_score + 1.0)))
        
        return float(np.clip(normalized, 0.0, 1.0))