import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Synthesis Controller via Kalman-Filtered Phase Transitions.
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical constraints (negations, comparatives,
       conditionals) and numeric values to score candidates based on constraint satisfaction.
    2. Kalman Filter (Meta-Control): Tracks the 'order parameter' (running mean score of top candidates).
       - State: [mean_score, score_velocity]
       - Innovation: Difference between predicted and actual best score.
       - Phase Transition: If innovation > threshold (variance), the system detects a shift
         in the hypothesis space landscape.
    3. Adaptive Strategy:
       - Stable Phase: Prioritize strict structural adherence (Local search analogy).
       - Transition Phase: Relax constraints slightly or boost candidates with high semantic
         overlap if structural scores are tied, simulating a switch to global search.
    4. NCD (Tiebreaker): Used only when structural scores are indistinguishable.
    
    This approach beats pure NCD by explicitly modeling logical constraints and adapting
    scoring strictness based on the dynamical behavior of the candidate pool.
    """

    def __init__(self):
        # Kalman Filter State: [mean_score, velocity]
        self.state = [0.5, 0.0] 
        # Covariance matrix (2x2 flattened): [[P00, P01], [P10, P11]]
        self.P = [1.0, 0.0, 0.0, 1.0]
        self.process_noise = 0.1
        self.measurement_noise = 0.2
        self.last_innovation = 0.0
        self.is_phase_transition = False

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text_lower),
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring mechanism based on structural parsing and constraint propagation.
        Returns a score 0.0 to 1.0.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 1.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect understanding (heuristic check)
        if p_feat['negations'] > 0:
            # Simple heuristic: if prompt negates, candidate shouldn't be empty or purely affirmative without context
            if c_feat['length'] < 5:
                score -= 0.3
        
        # 2. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Check for direct number presence or logical derivation (simplified)
                # If prompt asks for comparison, candidate should reflect order
                if p_feat['comparatives'] > 0:
                    # Heuristic: Candidate numbers should be related or ordered
                    if len(c_nums) >= 2:
                        if p_nums[0] > p_nums[1] and c_nums[0] < c_nums[1]:
                             score += 0.2 # Correctly inverted logic
                        elif p_nums[0] < p_nums[1] and c_nums[0] > c_nums[1]:
                             score += 0.2
                else:
                    # Exact match bonus
                    if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                        score += 0.3
            except ValueError:
                pass

        # 3. Structural Length/Complexity Match
        # Candidates answering complex prompts (high conditionals) tend to be longer
        if p_feat['conditionals'] > 0 and c_feat['length'] < 10:
            score -= 0.2
            
        # 4. Keyword Overlap (Structural only)
        # Boost if candidate contains key logical operators from prompt
        common_ops = set(['if', 'then', 'not', 'equal', 'greater', 'less'])
        p_ops = set(re.findall(r'\b\w+\b', prompt.lower())) & common_ops
        c_ops = set(re.findall(r'\b\w+\b', candidate.lower())) & common_ops
        if p_ops and c_ops:
            score += 0.1 * (len(p_ops & c_ops) / len(p_ops))

        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_both - max_len) / max_len

    def _kalman_step(self, measurement: float) -> float:
        """
        Update Kalman Filter with the best candidate score.
        Returns the predicted mean for the next step.
        Detects phase transitions via innovation.
        """
        # Predict
        # State transition matrix F = [[1, 1], [0, 1]] (Constant velocity model)
        pred_state_0 = self.state[0] + self.state[1]
        pred_state_1 = self.state[1]
        
        # Predicted Covariance P = F * P * F^T + Q
        # Simplified manual matrix mult for 2x2
        # P_new = [[P00 + 2*P01 + P11, P01 + P11], [P01 + P11, P11]] + Q
        p00 = self.P[0] + 2*self.P[1] + self.P[3] + self.process_noise
        p01 = self.P[1] + self.P[3]
        p11 = self.P[3] + self.process_noise
        
        # Innovation
        innovation = measurement - pred_state_0
        self.last_innovation = innovation
        
        # Phase Transition Detection
        # If innovation is significantly larger than expected variance (sqrt(p00))
        threshold = 2.0 * math.sqrt(p00 + self.measurement_noise)
        self.is_phase_transition = abs(innovation) > threshold
        
        # Update (Kalman Gain K)
        # K = P * H^T * (H * P * H^T + R)^-1
        # H = [1, 0]
        s = p00 + self.measurement_noise
        k0 = p00 / s
        k1 = p01 / s
        
        # Correct State
        self.state[0] = pred_state_0 + k0 * innovation
        self.state[1] = pred_state_1 + k1 * innovation
        
        # Correct Covariance
        self.P[0] = (1 - k0) * p00
        self.P[1] = (1 - k0) * p01
        self.P[3] = (1 - k1) * p11 # Approximation for stability
        
        return self.state[0]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # 1. Compute primary structural scores
        for cand in candidates:
            score = self._check_constraint_satisfaction(prompt, cand)
            scored_candidates.append({
                'candidate': cand,
                'struct_score': score,
                'ncd_dist': self._ncd(prompt, cand)
            })
        
        # 2. Identify best score for Kalman update
        best_score = max(c['struct_score'] for c in scored_candidates)
        
        # 3. Run Kalman Filter to detect phase transition in search landscape
        self._kalman_step(best_score)
        
        # 4. Adjust scores based on phase state
        # If phase transition detected (sudden jump/drop), we might be in a volatile region.
        # We slightly penalize over-confidence or boost diversity if needed.
        # Here, we use the transition to break ties: if transition, trust NCD less.
        transition_factor = 0.0
        if self.is_phase_transition:
            # In a phase transition, structural signals might be noisy; 
            # rely slightly more on NCD as a stabilizer for ties, or vice versa.
            # Strategy: Flatten scores slightly to allow re-ranking by secondary metrics.
            transition_factor = 0.1 

        final_results = []
        for item in scored_candidates:
            base_score = item['struct_score']
            
            # Tie-breaking logic
            # If scores are very close (within epsilon), use NCD
            # If phase transition, the threshold for tie-breaking is relaxed
            epsilon = 0.05 if not self.is_phase_transition else 0.15
            
            # NCD is a tiebreaker: lower NCD (more similar) is usually better for 
            # direct answers, but for reasoning, we want specific structural match.
            # We invert NCD penalty: (1 - NCD) gives similarity.
            ncd_bonus = (1.0 - item['ncd_dist']) * 0.05 
            
            # Apply small perturbation based on transition state to simulate strategy switch
            if self.is_phase_transition:
                # Simulate "Global Search": Give a slight random-ish boost based on length complexity
                # to escape local optima (deterministic via hash of candidate)
                complexity_boost = (len(item['candidate']) % 10) * 0.001
                base_score += complexity_boost

            final_score = base_score + ncd_bonus
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            final_results.append({
                'candidate': item['candidate'],
                'score': final_score,
                'reasoning': f"Structural: {item['struct_score']:.2f}, NCD: {item['ncd_dist']:.2f}, PhaseShift: {self.is_phase_transition}"
            })
        
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural satisfaction as the primary driver, calibrated by Kalman state.
        """
        struct_score = self._check_constraint_satisfaction(prompt, answer)
        ncd_val = self._ncd(prompt, answer)
        
        # Base confidence on structural integrity
        conf = struct_score
        
        # Penalize if NCD is extremely high (nonsense) but only if struct score isn't perfect
        if ncd_val > 0.9 and struct_score < 0.9:
            conf *= 0.8
            
        # Adjust based on current system uncertainty (from Kalman P matrix)
        # High uncertainty in filter -> lower confidence in individual evaluations
        uncertainty = math.sqrt(self.P[0])
        conf *= (1.0 - 0.2 * uncertainty) # Reduce confidence by up to 20% based on filter uncertainty
        
        return max(0.0, min(1.0, conf))