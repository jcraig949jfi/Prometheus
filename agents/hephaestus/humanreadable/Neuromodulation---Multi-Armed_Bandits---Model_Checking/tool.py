import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Neuromodulator-Guided Bandit Controller for Hypothesis Verification.
    
    Mechanism:
    1. Arms: Each candidate answer is treated as a hypothesis arm.
    2. Model Checking (Simulation): We perform structural parsing (negations, comparatives, 
       conditionals, numeric evaluation) on the prompt and candidate to generate a 'verification trace'.
    3. Prediction Error & Neuromodulation:
       - Dopamine (Reward): Based on structural alignment (e.g., if prompt has negation, candidate must reflect it).
       - Serotonin (Exploration): Increased if the candidate is short/trivial or if structural complexity is high.
       - Acetylcholine (Uncertainty): Scales the exploration bonus based on parsing ambiguity.
    4. Bandit Selection: Uses Upper Confidence Bound (UCB) logic to rank candidates, balancing 
       structural correctness (exploitation) with complexity/exploration needs.
    5. Tiebreaker: NCD is used only when structural scores are identical.
    """

    def __init__(self):
        # State for bandit arms: {candidate: {'visits': int, 'reward': float, 'complexity': float}}
        self.arm_state: Dict[str, Dict] = {}
        self.total_pulls = 0

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        # Convert numbers to float for comparison
        try:
            features['numeric_val'] = float(features['numbers'][0]) if features['numbers'] else None
        except ValueError:
            features['numeric_val'] = None
        return features

    def _verify_hypothesis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulate model checking via structural constraint propagation.
        Returns (reward_score, reasoning_trace).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        reasons = []

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation, correct answer often acknowledges it or flips logic
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0 or any(word in candidate.lower() for word in ['false', 'incorrect', 'no']):
                score += 2.0
                reasons.append("Negation constraint satisfied")
            else:
                score -= 1.0
                reasons.append("Negation constraint violated")
        
        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0 or c_feat['length'] > 5: # Heuristic: comparatives need elaboration
                score += 1.5
                reasons.append("Comparative structure detected")
        
        # 3. Numeric Evaluation
        if p_feat['numeric_val'] is not None and c_feat['numeric_val'] is not None:
            # Simple consistency check: if prompt implies a value, candidate should be close or logically derived
            # Since we can't do full math without eval, we check presence
            score += 1.0
            reasons.append("Numeric consistency present")
            
        # 4. Conditional Depth
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > p_feat['length'] * 0.5:
                score += 1.0
                reasons.append("Conditional depth maintained")

        # Base reward for length matching (avoiding trivial "Yes"/"No" on complex prompts)
        if p_feat['length'] > 10 and c_feat['length'] < 3:
            score -= 2.0
            reasons.append("Trivial response to complex prompt")
        elif c_feat['length'] > 0:
            score += 0.5 # Basic participation reward

        return score, "; ".join(reasons) if reasons else "Structural baseline"

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _get_bandit_score(self, candidate: str, base_reward: float) -> float:
        """
        Calculate UCB-style score with neuromodulatory adjustments.
        """
        if candidate not in self.arm_state:
            self.arm_state[candidate] = {'visits': 0, 'reward_sum': 0.0, 'complexity': 0.0}
        
        state = self.arm_state[candidate]
        visits = state['visits']
        
        # Update state
        state['visits'] += 1
        state['reward_sum'] += base_reward
        state['complexity'] = len(candidate) # Simple complexity metric

        # Exploitation term (average reward)
        if visits == 0:
            return float('inf') # Ensure new arms are tried
        
        avg_reward = state['reward_sum'] / visits
        
        # Exploration term (UCB1)
        # Serotonin-like: boost exploration if total pulls are low or candidate is novel
        exploration_bonus = 0.0
        if self.total_pulls > 0:
            import math
            exploration_bonus = math.sqrt((2 * math.log(self.total_pulls + 1)) / visits)
        
        # Acetylcholine-like: Uncertainty scaling based on length variance (proxy)
        uncertainty_scale = 1.0 + (0.1 * (len(candidate) % 5)) 
        
        return avg_reward + (exploration_bonus * uncertainty_scale)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        self.total_pulls += 1
        ranked_results = []
        
        # Temporary storage for sorting
        scored_candidates = []
        
        for cand in candidates:
            # 1. Model Check (Structural Parsing)
            reward, reasoning = self._verify_hypothesis(prompt, cand)
            
            # 2. Bandit Selection Logic
            bandit_score = self._get_bandit_score(cand, reward)
            
            # 3. NCD Tiebreaker (computed lazily if needed, but here pre-computed for simplicity in sorting key)
            # We store NCD separately to use as secondary key
            ncd_val = self._compute_ncd(prompt, cand)
            
            scored_candidates.append({
                'candidate': cand,
                'bandit_score': bandit_score,
                'ncd': ncd_val,
                'reasoning': reasoning
            })
        
        # Sort: Primary by bandit_score (desc), Secondary by NCD (asc - lower distance is better)
        # Note: NCD is a tiebreaker, so we prioritize the structural/bandit score heavily.
        scored_candidates.sort(key=lambda x: (-x['bandit_score'], x['ncd']))
        
        # Normalize scores to 0-1 range for output
        max_score = max(c['bandit_score'] for c in scored_candidates) if scored_candidates else 1.0
        min_score = min(c['bandit_score'] for c in scored_candidates) if scored_candidates else 0.0
        score_range = max_score - min_score if max_score != min_score else 1.0
        
        for item in scored_candidates:
            normalized_score = (item['bandit_score'] - min_score) / score_range
            ranked_results.append({
                'candidate': item['candidate'],
                'score': round(normalized_score, 4),
                'reasoning': f"Bandit Score: {item['bandit_score']:.2f}; NCD: {item['ncd']:.2f}; {item['reasoning']}"
            })
            
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural verification strength.
        """
        reward, _ = self._verify_hypothesis(prompt, answer)
        
        # Map reward to 0-1. 
        # Heuristic: Reward > 2 is high confidence, < 0 is low.
        # Sigmoid-like mapping manually
        confidence = 1 / (1 + pow(2.718, -reward)) # Softmax approximation
        
        # Clamp
        return max(0.0, min(1.0, confidence))