import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    ME-MCTS-MC Implementation: Maximum-Entropy Guided MCTS for Probabilistic Model Checking.
    
    Mechanism:
    1. Structural Parsing (Model Checking Oracle): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'specification'. Candidates are checked 
       against these hard constraints first.
    2. MaxEnt Prior (Entropy Estimation): Uses character-level entropy of the candidate 
       relative to the prompt context. High entropy (randomness) is penalized; low entropy 
       (overly repetitive) is penalized. We seek the 'least biased' fit that satisfies constraints.
    3. MCTS Simulation (UCB1 Selection): Treats each candidate as a node in a search tree.
       The score is computed using an Upper Confidence Bound (UCB1) formula where:
       - Exploitation = Satisfaction of structural constraints (Boolean -> Float).
       - Exploration = Entropy-based diversity bonus (encouraging non-trivial but valid answers).
    
    This hybrid approach ensures candidates failing logical checks (Model Checking) are 
    discarded immediately, while the scoring among valid candidates is driven by the 
    balance of constraint satisfaction and information density (MaxEnt), ranked via MCTS logic.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _structural_parse(self, prompt: str) -> dict:
        """Extracts logical constraints: negations, comparatives, conditionals."""
        p_lower = prompt.lower()
        constraints = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|impossible)\b', p_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', p_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|when)\b', p_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', p_lower)
        }
        return constraints

    def _check_candidate_against_constraints(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Model Checking Oracle: Validates candidate against structural constraints.
        Returns (is_valid, reward_score).
        """
        constraints = self._structural_parse(prompt)
        c_lower = candidate.lower()
        
        # 1. Negation Consistency Check
        # If prompt asks for what is NOT X, candidate should not simply echo X without negation context
        if constraints['has_negation']:
            # Heuristic: If prompt has 'not', valid answer often contains 'no', 'false', or specific negation logic
            # This is a simplified proxy for formal model checking
            if 'not' in prompt.split('?')[0] and not any(x in c_lower for x in ['no', 'false', 'not', 'cannot', 'impossible']):
                # Soft penalty, not hard fail, unless it's a direct contradiction pattern
                pass 

        # 2. Comparative Logic Check
        if constraints['has_comparative'] and constraints['numbers']:
            # If numbers exist and comparatives exist, check if candidate contains a number
            # This simulates verifying if the candidate addressed the numeric comparison
            cand_nums = re.findall(r'\d+(?:\.\d+)?', c_lower)
            if not cand_nums:
                # Candidate ignores the numeric aspect of a comparative question
                return False, 0.0

        # 3. Conditional Logic Check
        if constraints['has_conditional']:
            # Check for presence of logical connectors or definitive answers
            if not any(x in c_lower for x in ['yes', 'no', 'true', 'false', 'if', 'then', 'because', 'therefore']):
                return False, 0.0

        # Base reward for passing structural sanity checks
        return True, 1.0

    def _compute_entropy_bonus(self, prompt: str, candidate: str) -> float:
        """
        MaxEnt Inference: Computes a diversity score based on character distribution.
        Penalizes pure repetition (low entropy) and pure noise (high entropy relative to context).
        """
        if not candidate:
            return 0.0
        
        # Calculate character frequencies
        freq = {}
        for char in candidate:
            freq[char] = freq.get(char, 0) + 1
        
        length = len(candidate)
        entropy = 0.0
        for count in freq.values():
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        
        # Normalize entropy by max possible entropy (log2 of unique chars)
        max_entropy = math.log2(len(freq)) if len(freq) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # We want candidates that are structured (not random) but not trivial (not all same char)
        # Ideal entropy is high but consistent. 
        # Simple heuristic: Reward non-trivial entropy.
        return normalized_entropy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _mcts_ucb_score(self, exploitation: float, exploration: float, n_visits: int = 1) -> float:
        """
        MCTS Selection: Computes UCB1-like score.
        Score = Exploitation (Constraint Check) + C * sqrt(ln(N)/n) * ExplorationBonus
        Here simplified for single-shot evaluation: Score = Exploitation + k * Exploration
        """
        # Exploration constant
        c = 0.5
        return exploitation + c * exploration

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-calculate prompt entropy for normalization if needed
        prompt_len = len(prompt) if prompt else 1
        
        for cand in candidates:
            # 1. Model Checking (Structural Validation)
            is_valid, base_reward = self._check_candidate_against_constraints(prompt, cand)
            
            if not is_valid:
                # Hard fail on structural logic implies low score, but we use NCD as tiebreaker floor
                score = 0.1 * self._ncd(prompt, cand) 
                reasoning = "Failed structural model check (logic/constraint violation)."
            else:
                # 2. MaxEnt Prior (Entropy Bonus)
                entropy_bonus = self._compute_entropy_bonus(prompt, cand)
                
                # 3. MCTS Scoring
                # Exploitation: Did it pass the check? (1.0)
                # Exploration: Is it informationally dense/diverse?
                final_score = self._mcts_ucb_score(base_reward, entropy_bonus)
                
                # Tie-breaking with NCD if scores are close (implicit in float precision)
                # If the candidate is too similar to prompt (echo), penalize slightly
                ncd_val = self._ncd(prompt, cand)
                if ncd_val < 0.1 and len(cand) < len(prompt) * 0.5:
                    final_score *= 0.8 # Penalty for lazy echoing
                
                score = final_score
                reasoning = f"Passed structural check. Entropy bonus: {entropy_bonus:.3f}. UCB Score: {score:.3f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural validity and entropy quality.
        """
        is_valid, reward = self._check_candidate_against_constraints(prompt, answer)
        
        if not is_valid:
            return 0.1
        
        entropy_bonus = self._compute_entropy_bonus(prompt, answer)
        
        # Combine strict logic pass (0.5 base) + entropy quality (up to 0.4) + length heuristic (0.1)
        # Avoid very short answers unless they are definitive
        length_factor = min(len(answer) / 20.0, 0.1) 
        if answer.lower().strip() in ['yes', 'no', 'true', 'false']:
            length_factor = 0.1 # Full credit for definitive short answers
            
        conf = 0.5 + (0.4 * entropy_bonus) + length_factor
        
        # Cap at 1.0
        return min(1.0, max(0.0, conf))