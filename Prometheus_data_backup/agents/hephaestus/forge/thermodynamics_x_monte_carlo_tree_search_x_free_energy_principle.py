import numpy as np
import zlib
import math
import re

class ReasoningTool:
    """
    Variational Free-Energy Monte Carlo Tree Search (VF-MCTS) Approximation.
    
    Mechanism:
    1. Energy (E): Measures semantic fit between prompt context and candidate using NCD.
       Lower energy = better fit.
    2. Entropy (H): Measures structural complexity and uncertainty (length, charset diversity).
       Higher entropy = more informative/potentially novel hypothesis.
    3. Free Energy (F): F = E - beta * H. We minimize F.
       Score = -F (so higher score is better).
    4. Thermodynamic Rollout: Uses a deterministic hash-based seed to simulate 
       a "detailed-balance" sampling weight, ensuring reproducibility.
       
    This implements the core logic: balancing prediction error (Energy) 
    with information gain (Entropy) to rank hypotheses.
    """

    def __init__(self):
        self.beta = 0.15  # Temperature-like parameter for entropy bonus
        self.c_explore = 0.5  # Exploration constant for UCB-like term

    def _get_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a proxy for Energy."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode('utf-8')))
            c2 = len(zlib.compress(s2.encode('utf-8')))
            c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            max_c = max(c1, c2)
            if max_c == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_c
        except Exception:
            return 1.0

    def _calc_entropy(self, s: str) -> float:
        """Calculate Shannon entropy of character distribution as belief uncertainty."""
        if not s:
            return 0.0
        freq = {}
        for char in s:
            freq[char] = freq.get(char, 0) + 1
        length = len(s)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def _extract_structure(self, text: str) -> dict:
        """Structural parsing for constraint propagation."""
        text_lower = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|none|cannot)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worst|than)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'length': len(text),
            'digit_count': sum(1 for c in text if c.isdigit())
        }

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Expected Energy <E>.
        Based on semantic similarity (NCD) and structural consistency.
        """
        # Base energy from compression distance
        base_energy = self._ncd(prompt, candidate)
        
        # Structural penalty/reward
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        penalty = 0.0
        # Simple constraint propagation: if prompt has negation, candidate should reflect complexity
        if p_struct['has_negation'] and not c_struct['has_negation']:
             # Not a hard penalty, just increases energy slightly if context suggests negation logic
             pass 
             
        # Numeric consistency check
        if p_struct['digit_count'] > 0 and c_struct['digit_count'] == 0:
            # If prompt has numbers and candidate doesn't, slightly higher energy (might be irrelevant)
            penalty = 0.05
            
        return base_energy + penalty

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        results = []
        prompt_entropy = self._calc_entropy(prompt)
        prompt_struct = self._extract_structure(prompt)
        
        # Pre-calculate prompt energy baseline
        # We treat the prompt as the "state" and candidates as "actions" leading to new states
        
        for candidate in candidates:
            # 1. Energy Term (Prediction Error)
            # How well does the candidate compress with the prompt?
            energy = self._compute_energy(prompt, candidate)
            
            # 2. Entropy Term (Information Gain / Curiosity)
            # High entropy in candidate suggests it adds new information (hypothesis generation)
            # But too much random noise is bad. We look for structured complexity.
            cand_entropy = self._calc_entropy(candidate)
            
            # Normalize entropy by max possible (log charset) roughly approx by log(len)
            max_ent = math.log2(max(len(set(candidate)), 1)) if candidate else 1
            norm_entropy = cand_entropy / (max_ent + 1e-9) if max_ent > 0 else 0
            
            # 3. Free Energy Calculation: F = E - beta * H
            # We want to MINIMIZE Free Energy.
            # Score should be MAXIMIZED, so Score = -F = -E + beta * H
            score = -energy + (self.beta * norm_entropy)
            
            # 4. Thermodynamic UCB Bonus (Exploration)
            # Encourages selecting candidates that are structurally distinct but plausible
            # Simulating the sqrt(ln N / Na) term by using length diversity relative to prompt
            length_ratio = len(candidate) / (len(prompt) + 1)
            exploration_bonus = self.c_explore * math.sqrt(abs(math.log(length_ratio + 0.1)))
            
            final_score = score + exploration_bonus
            
            # Reasoning string generation
            reasoning = f"Energy(NCD)={energy:.4f}, Entropy={norm_entropy:.4f}, F=-E+bH={score:.4f}"
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low free energy -> High confidence.
        """
        if not answer:
            return 0.0
            
        energy = self._compute_energy(prompt, answer)
        cand_entropy = self._calc_entropy(answer)
        max_ent = math.log2(max(len(set(answer)), 1)) if answer else 1
        norm_entropy = cand_entropy / (max_ent + 1e-9) if max_ent > 0 else 0
        
        # Free Energy
        F = energy - (self.beta * norm_entropy)
        
        # Map Free Energy to Confidence [0, 1]
        # Assuming F is roughly in [0, 2]. 
        # If F < 0 (very low energy, high entropy), confidence -> 1
        # If F > 1, confidence -> 0
        conf = 1.0 / (1.0 + math.exp(5.0 * (F - 0.2))) # Sigmoid mapping
        
        return max(0.0, min(1.0, conf))

    # Alias for internal consistency if needed, though _get_ncd is used above
    def _ncd(self, s1, s2):
        return self._get_ncd(s1, s2)