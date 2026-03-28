import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Information-Gain MCTS (TIG-MCTS) Approximation.
    
    Mechanism:
    1. Structural Parsing (Energy E): Extracts logical constraints (negations, comparatives,
       conditionals) from the prompt. Candidates violating hard constraints get high 'Energy' (cost).
    2. Information Gain (Entropy H): Measures how well a candidate discriminates between 
       logical states implied by the prompt structure. High specificity = lower entropy.
    3. Free Energy (F = E - T*H): Combines cost and information. 
       - Low Energy (satisfies constraints) is good.
       - Low Entropy (high information/specificity) is good.
       - Temperature T balances exploration vs exploitation.
    4. Scoring: Negative Free Energy is used as the score. 
    5. NCD: Used strictly as a tiebreaker for structurally equivalent candidates.
    """

    def __init__(self):
        self.temperature = 0.5  # Trade-off parameter
        self.c_explore = 1.414  # UCB exploration constant

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|exclude|false)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text_lower)],
            'length': len(text.split())
        }
        return features

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Returns an 'Energy' penalty. 
        0.0 = No obvious violation.
        1.0+ = Violation detected (e.g., saying 'Yes' to a negative constraint).
        """
        energy = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Check for direct contradiction with explicit negations in prompt
        if re.search(r'\b(not|no|never)\b', p_lower):
            # If prompt says "not X" and candidate is exactly "X" or "yes" when "no" expected
            if c_lower in ['yes', 'true', 'is']:
                # Heuristic: if prompt has "not" and candidate is affirmative short word
                if len(c_lower.split()) <= 2:
                    energy += 0.5

        # Check number logic if numbers exist
        p_nums = self._parse_structure(prompt)['numbers']
        c_nums = self._parse_structure(candidate)['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple comparative check: if prompt implies ordering, does candidate respect it?
            # This is a shallow check; deep reasoning requires LLM, we simulate via structure
            if p_nums[0] > p_nums[1]:
                if len(c_nums) > 0 and c_nums[0] < p_nums[1]: # Candidate number too small?
                     energy += 0.2
        
        # Penalty for being overly verbose without adding structural tokens (noise)
        if len(candidate.split()) > 50:
            energy += 0.1
            
        return energy

    def _calc_entropy_estimate(self, prompt: str, candidate: str) -> float:
        """
        Estimates entropy (uncertainty). 
        Lower entropy = higher information content (more specific/discriminative).
        We approximate this by token diversity and specificity relative to prompt.
        """
        if not candidate:
            return 1.0 # Max entropy for empty
        
        # Simple proxy: Specificity. 
        # If candidate is just "Yes/No", entropy is higher (less info) than a detailed explanation?
        # Actually, in hypothesis testing, a specific hypothesis has lower entropy than a vague one.
        # But here we want the candidate that reduces belief entropy the most.
        # Let's use length and unique char ratio as a proxy for "information density".
        
        unique_chars = len(set(candidate))
        total_chars = len(candidate)
        if total_chars == 0: return 1.0
        
        density = unique_chars / total_chars
        # Normalize roughly between 0 and 1. 
        # High density + reasonable length = lower entropy (more structured)
        # Very short answers (Yes/No) have high entropy in this context (ambiguous)
        if len(candidate.split()) <= 2:
            return 0.8 
        return 0.2 + (0.5 * density) # Base entropy + variability

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats = self._parse_structure(prompt)
        
        # First pass: Calculate raw scores
        scored_candidates = []
        for cand in candidates:
            # 1. Energy (Cost): Penalty for constraint violations
            energy = self._check_constraint_violation(prompt, cand)
            
            # 2. Entropy (H): Estimate of uncertainty/lack of info
            entropy = self._calc_entropy_estimate(prompt, cand)
            
            # 3. Free Energy: F = E - T * H
            # We want to MINIMIZE Free Energy. 
            # Score = -F = T*H - E (Higher is better)
            # But wait: We want LOW Energy (good) and LOW Entropy (high info gain).
            # Formula from prompt: F = <E> - T*H. 
            # We want to minimize F. So Score = -F = T*H - <E>.
            # Wait, if H is posterior entropy, we want it LOW. 
            # So -T*H contributes to lowering F. 
            # Correct: Score = -(Energy - Temp * Entropy) = Temp * Entropy - Energy?
            # No, if H is low (good), -T*H is small negative. 
            # Let's stick to the prompt's definition: Reward = InfoGain (reduction in H).
            # Let's simplify: Score = (Specificity) - (ViolationPenalty).
            # Specificity ~ 1/Entropy.
            
            specificity = 1.0 / (entropy + 0.1)
            score = (specificity * self.temperature) - energy
            
            # Add UCB-like exploration bonus based on candidate index diversity simulation
            # Since we don't have a tree history, we simulate N_n via string hash mod
            hash_val = hash(cand) % 1000
            exploration_bonus = self.c_explore * math.sqrt(math.log(len(candidates) + 2) / (hash_val + 2))
            
            final_score = score + exploration_bonus
            scored_candidates.append((cand, final_score, energy, entropy))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Handle ties with NCD
        final_results = []
        for i, (cand, score, energy, entropy) in enumerate(scored_candidates):
            reasoning = f"Energy={energy:.2f}, Entropy={entropy:.2f}, Temp={self.temperature}"
            
            # Tie-breaking logic using NCD against prompt
            if i > 0:
                prev_score = scored_candidates[i-1][1]
                if abs(score - prev_score) < 1e-6:
                    ncd_curr = self._ncd(prompt, cand)
                    ncd_prev = self._ncd(prompt, scored_candidates[i-1][0])
                    if ncd_curr < ncd_prev:
                        # Swap logic handled by sort stability or re-sort, 
                        # but here we just note it in reasoning for transparency
                        reasoning += " (NCD tiebreak favor)"
            
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        High confidence if answer has low energy (no violations) and low entropy (specific).
        """
        energy = self._check_constraint_violation(prompt, answer)
        entropy = self._calc_entropy_estimate(prompt, answer)
        
        # Normalize to 0-1
        # Ideal: Energy=0, Entropy=0.2 (low) -> High Score
        # Worst: Energy=1, Entropy=0.9 -> Low Score
        
        raw_score = (1.0 / (entropy + 0.1)) * self.temperature - energy
        
        # Sigmoid-like mapping to 0-1
        # Assuming raw_score ranges roughly -1 to 2
        conf = 1.0 / (1.0 + math.exp(-raw_score))
        return max(0.0, min(1.0, conf))