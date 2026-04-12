import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Kalman-RL Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (The 'Observation'): Extracts logical constraints 
       (negations, comparatives, conditionals) and numeric values from the prompt.
    2. Kalman Belief State (The 'State'): Maintains a running estimate of 
       'uncertainty' (variance) based on the density of logical operators.
       High operator density -> High uncertainty -> High 'Information Gain' potential.
    3. Thermodynamic Free Energy (The 'Objective'): Scores candidates by:
       - Energy (E): Penalty for violating extracted structural constraints.
       - Entropy (S): Bonus for matching the 'complexity' (compression) profile 
         expected given the prompt's logical depth.
       - Cost: Penalty for length deviations (thermodynamic efficiency).
       
    The final score is a variational free-energy minimization: G = E - T*S + Cost.
    """

    def __init__(self):
        # Kalman Filter State: Mean (mu) and Variance (sigma_sq) of logical complexity
        self.mu = 0.0
        self.sigma_sq = 1.0
        self.process_noise = 0.1
        self.measurement_noise = 0.2
        
        # Thermodynamic constants
        self.temperature = 0.5  # Weight of entropy term
        self.energy_weight = 2.0 # Weight of constraint violation
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'logic_conn': re.compile(r'\b(and|or|but|however|therefore)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features acting as observations."""
        features = {
            'neg_count': len(self.patterns['negation'].findall(text)),
            'comp_count': len(self.patterns['comparative'].findall(text)),
            'cond_count': len(self.patterns['conditional'].findall(text)),
            'num_count': len(self.patterns['numeric'].findall(text)),
            'logic_count': len(self.patterns['logic_conn'].findall(text)),
            'length': len(text),
            'has_numbers': bool(self.patterns['numeric'].findall(text))
        }
        features['structural_density'] = (features['neg_count'] + features['comp_count'] + 
                                          features['cond_count'] + features['logic_count'])
        return features

    def _kalman_predict(self):
        """Prediction step: Uncertainty grows over time/steps."""
        self.sigma_sq += self.process_noise

    def _kalman_update(self, observation: float):
        """Update step: Refine belief based on observed structural density."""
        if self.sigma_sq + self.measurement_noise == 0:
            return
            
        k = self.sigma_sq / (self.sigma_sq + self.measurement_noise)
        self.mu = self.mu + k * (observation - self.mu)
        self.sigma_sq = (1 - k) * self.sigma_sq

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker/similarity metric."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Numeric evaluation: Detect number comparisons.
        Returns 0.0 if consistent, 1.0 if contradictory (Energy penalty).
        """
        p_nums = self.patterns['numeric'].findall(prompt)
        c_nums = self.patterns['numeric'].findall(candidate)
        
        if not p_nums or not c_nums:
            return 0.0 # No numbers to check
            
        try:
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            # Simple heuristic: If prompt has specific numbers, candidate shouldn't 
            # wildly contradict order if it implies a sequence, or should match if direct answer.
            # Here we check for gross contradictions in magnitude if counts match.
            if len(p_vals) == len(c_vals):
                for pv, cv in zip(p_vals, c_vals):
                    if pv != 0 and abs(cv - pv) > abs(pv) * 2.0: # Allow some slack, flag gross errors
                        return 0.5
            return 0.0
        except ValueError:
            return 0.0

    def _check_constraint_propagation(self, prompt: str, candidate: str) -> float:
        """
        Constraint propagation: Check for negation flips.
        Returns energy penalty (0.0 = good, >0 = bad).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        penalty = 0.0
        
        # If prompt has strong negation, and candidate is affirmative without context, slight penalty
        # This is a simplified proxy for modus tollens checking
        if p_feats['neg_count'] > 0 and c_feats['neg_count'] == 0:
            # Check if candidate explicitly contradicts a negative premise
            if re.search(r'\b(yes|true|correct)\b', candidate, re.IGNORECASE):
                penalty += 0.3
                
        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Analyze Prompt (Observation)
        p_feats = self._extract_features(prompt)
        
        # Reset Kalman state for this evaluation context
        self.mu = p_feats['structural_density'] * 0.5
        self.sigma_sq = 1.0
        self._kalman_predict()
        self._kalman_update(p_feats['structural_density'])
        
        # Expected complexity based on thermodynamic analogy
        expected_complexity = self.mu
        results = []
        
        for cand in candidates:
            c_feats = self._extract_features(cand)
            
            # --- Energy Term (E) ---
            # Penalty for constraint violations and numeric inconsistency
            e_numeric = self._check_numeric_consistency(prompt, cand)
            e_constraints = self._check_constraint_propagation(prompt, cand)
            energy = self.energy_weight * (e_numeric + e_constraints)
            
            # --- Entropy Term (S) ---
            # Measure of information content relative to expectation
            # Using compression ratio as proxy for entropy
            try:
                c_comp = len(zlib.compress(cand.encode()))
                p_comp = len(zlib.compress(prompt.encode()))
                # Normalized entropy estimate
                entropy_estimate = c_comp / (p_comp + 1) 
            except:
                entropy_estimate = 0.0
                
            # Deviation from expected complexity (Free Energy minimization)
            # We want candidates that match the logical depth of the prompt
            complexity_diff = abs(entropy_estimate - (expected_complexity / 10.0))
            entropy_term = -self.temperature * (1.0 - min(1.0, complexity_diff))
            
            # --- NCD Tiebreaker ---
            # Prefer candidates that are compressibly similar to prompt (contextual relevance)
            ncd_score = self._compute_ncd(prompt, cand)
            
            # Final Score: Minimize Free Energy (Lower is better physically, but we want Higher score = better)
            # Score = -Energy + EntropyBonus - NCD_Penalty
            score = -energy + entropy_term - (0.1 * ncd_score)
            
            # Boost for structural alignment (heuristic boost)
            if p_feats['has_numbers'] and c_feats['has_numbers']:
                score += 0.2
            if p_feats['neg_count'] > 0 and c_feats['neg_count'] > 0:
                score += 0.1
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"E={energy:.2f}, S={entropy_term:.2f}, NCD={ncd_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on thermodynamic consistency.
        """
        # Re-use evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score to 0-1 using a sigmoid-like mapping centered around 0
        # Assuming typical scores range between -1.0 and 1.0
        confidence = 1.0 / (1.0 + math.exp(-2.0 * raw_score))
        
        # Clamp
        return max(0.0, min(1.0, confidence))