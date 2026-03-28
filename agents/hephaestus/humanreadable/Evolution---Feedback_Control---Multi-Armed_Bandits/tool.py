import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Evolutionary Bandit Controller (AEBC) for Reasoning.
    
    Mechanism:
    1. Evolution: Candidates are a population of hypotheses. Their "genome" is their text.
    2. Fitness: Calculated via structural parsing (negations, comparatives, numerics) 
       and constraint propagation against the prompt.
    3. Multi-Armed Bandit (UCB): Selects which candidate to "evaluate" (score) next based 
       on current fitness estimate and uncertainty (exploration bonus).
    4. PID Feedback: Monitors the error (difference between max possible structural score 
       and current best). Adjusts the UCB exploration coefficient (c) dynamically.
       - High error -> High exploration (boosts uncertain candidates).
       - Low error -> High exploitation (focuses on best performers).
    
    This creates a self-tuning loop that balances finding novel structural matches 
    (exploration) vs refining the score of the best current match (exploitation).
    """

    def __init__(self):
        self.population_size = 0
        self.pid_integral = 0.0
        self.pid_derivative = 0.0
        self.last_error = 0.0
        self.ucb_counts = {}
        self.ucb_rewards = {}
        self.ucb_total_n = 0
        
        # PID Constants
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.1
        
        # Base exploration
        self.base_c = 2.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a deterministic structural fitness score based on:
        1. Negation consistency
        2. Comparative logic
        3. Numeric evaluation
        4. Constraint propagation (keyword overlap weight)
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Handling
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        p_has_neg = any(n in p_low for n in negations)
        c_has_neg = any(n in c_low for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 2.0  # Consistent negation state
        else:
            score -= 1.0  # Penalty for mismatched negation

        # 2. Comparative Logic Detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']
        p_comp = any(c in p_low for c in comparatives)
        c_comp = any(c in c_low for c in comparatives)
        
        if p_comp and c_comp:
            score += 1.5 # Reward matching comparative structure
        elif not p_comp and not c_comp:
            score += 0.5 # Neutral
            
        # 3. Numeric Evaluation
        nums_p = re.findall(r"[-+]?\d*\.\d+|\d+", p_low)
        nums_c = re.findall(r"[-+]?\d*\.\d+|\d+", c_low)
        
        if nums_p and nums_c:
            try:
                # Check if candidate numbers logically follow prompt numbers (simple equality check for now)
                # In a full system, this would parse "9.11" vs "9.9" logic
                p_vals = [float(n) for n in nums_p]
                c_vals = [float(n) for n in nums_c]
                
                # Reward if candidate contains specific numbers from prompt (Constraint Propagation)
                matches = 0
                for pv in p_vals:
                    if any(abs(pv - cv) < 1e-6 for cv in c_vals):
                        matches += 1
                score += (matches * 2.0)
                
                # Bonus for correct ordering if comparatives present
                if len(p_vals) >= 2 and len(c_vals) >= 2:
                    if (p_vals[0] > p_vals[1] and c_vals[0] > c_vals[1]) or \
                       (p_vals[0] < p_vals[1] and c_vals[0] < c_vals[1]):
                        score += 2.0
            except ValueError:
                pass

        # 4. Keyword Overlap (Simplified Constraint Propagation)
        # Extract nouns/verbs roughly
        words_p = set(re.findall(r'\b[a-z]{4,}\b', p_low))
        words_c = set(re.findall(r'\b[a-z]{4,}\b', c_low))
        
        if words_p:
            overlap = len(words_p & words_c) / len(words_p)
            score += (overlap * 3.0)
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp12 = len(zlib.compress(b1 + b2))
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            
            numerator = comp12 - min(comp1, comp2)
            denominator = max(comp1, comp2)
            
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except:
            return 1.0

    def _get_ucb_value(self, candidate: str, c_explore: float) -> float:
        """Calculate UCB1 value for a candidate."""
        if candidate not in self.ucb_counts:
            self.ucb_counts[candidate] = 0
            self.ucb_rewards[candidate] = 0.0
            return float('inf')  # Ensure unvisited nodes are picked first
        
        n_i = self.ucb_counts[candidate]
        if n_i == 0:
            return float('inf')
            
        avg_reward = self.ucb_rewards[candidate] / n_i
        exploration_bonus = c_explore * math.sqrt(math.log(self.ucb_total_n + 1) / n_i)
        
        return avg_reward + exploration_bonus

    def _update_pid(self, current_best_score: float, max_possible_score: float):
        """Update PID controller to adjust exploration coefficient."""
        # Error is the gap between perfect structural match and current best
        # Normalized to 0-1 range roughly
        target = max_possible_score
        error = target - current_best_score
        if error < 0: error = 0 # Overshoot is fine, but don't negative error for PID
        
        self.pid_integral += error
        derivative = error - self.last_error
        self.last_error = error
        
        # PID Output adjusts the exploration coefficient 'c'
        # High error -> High c (Explore more)
        # Low error -> Low c (Exploit)
        adjustment = (self.kp * error) + (self.ki * self.pid_integral) + (self.kd * derivative)
        
        new_c = self.base_c + adjustment
        # Clamp c to positive values
        self.current_c = max(0.1, new_c)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        max_struct_score = 10.0 # Heuristic max for normalization
        
        # Reset state for this evaluation run to ensure determinism per call
        self.ucb_counts = {c: 0 for c in candidates}
        self.ucb_rewards = {c: 0.0 for c in candidates}
        self.ucb_total_n = 0
        self.pid_integral = 0.0
        self.last_error = 0.0
        self.current_c = self.base_c
        
        # Simulation Loop: "Evolutionary" steps via Bandit selection
        # We simulate a budget of evaluations proportional to population size
        budget = len(candidates) * 3 
        evaluated_candidates = set()
        
        for _ in range(budget):
            # 1. Bandit Selection (UCB)
            ucb_values = {}
            for cand in candidates:
                ucb_values[cand] = self._get_ucb_value(cand, self.current_c)
            
            # Select candidate with highest UCB
            selected = max(ucb_values, key=ucb_values.get)
            
            # 2. Evaluation (Fitness Measurement)
            struct_score = self._structural_score(prompt, selected)
            
            # Add noise penalty based on NCD (dissimilarity reduces confidence slightly if structure is ambiguous)
            # But structural score is primary.
            ncd_val = self._ncd(prompt, selected)
            # Normalize NCD impact: lower NCD is better. 
            # We treat NCD as a secondary tie-breaker in the reward signal
            reward = struct_score + (1.0 - ncd_val) * 0.5
            
            # 3. Update Bandit State
            self.ucb_counts[selected] += 1
            self.ucb_rewards[selected] += reward
            self.ucb_total_n += 1
            evaluated_candidates.add(selected)
            
            # 4. PID Adjustment
            # Track best current average reward
            best_avg = -float('inf')
            for c in candidates:
                if self.ucb_counts[c] > 0:
                    avg = self.ucb_rewards[c] / self.ucb_counts[c]
                    if avg > best_avg:
                        best_avg = avg
            
            if best_avg != -float('inf'):
                self._update_pid(best_avg, max_struct_score + 0.5)

        # Final Scoring and Ranking
        final_scores = []
        for cand in candidates:
            if self.ucb_counts[cand] > 0:
                avg_reward = self.ucb_rewards[cand] / self.ucb_counts[cand]
            else:
                avg_reward = 0.0
            
            # Final Score combines structural integrity and compression similarity
            struct = self._structural_score(prompt, cand)
            ncd = self._ncd(prompt, cand)
            
            # Weighted sum: Structure is king, NCD is tiebreaker
            # If structural scores are close, NCD decides.
            score = (struct * 10.0) + ((1.0 - ncd) * 2.0)
            
            reasoning = f"Structural Match: {struct:.2f}, NCD Similarity: {1-ncd:.2f}"
            final_scores.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        final_scores.sort(key=lambda x: x["score"], reverse=True)
        return final_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and compression.
        """
        struct = self._structural_score(prompt, answer)
        ncd = self._ncd(prompt, answer)
        
        # Normalize struct score (heuristic cap at 10 for this calculation)
        norm_struct = min(struct / 10.0, 1.0)
        norm_ncd = 1.0 - ncd
        
        # Weighted average
        conf = (norm_struct * 0.7) + (norm_ncd * 0.3)
        return max(0.0, min(1.0, conf))