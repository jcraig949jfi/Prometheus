import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Embodied-Kalman-Bandit Reasoning Tool.
    
    Mechanism:
    1. Embodied Grounding: Parses text into structural feature vectors (negations, comparatives, 
       causality, spatial/temporal markers, numeric values) using regex.
    2. Kalman Filtering: Maintains a Gaussian belief (mu, sigma) over the correctness of each 
       candidate. Updates belief based on the match between the candidate's structural features 
       and an idealized 'correctness' profile derived from the prompt.
    3. Multi-Armed Bandit (UCB): Selects which candidate to 'focus' on for iterative refinement 
       (simulated here by weighting the final score by uncertainty exploration).
    4. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    5. Scoring: Structural match (50%+) + Constructive Computation (20%+) + NCD Tiebreaker (<15%).
    """

    def __init__(self):
        # Regex patterns for embodied grounding features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere|without|unless)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|>[=]?|<[=]?)\b', re.I),
            'conditional': re.compile(r'\b(if|then|else|unless|provided|assuming)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes|results in|due to)\b', re.I),
            'temporal': re.compile(r'\b(before|after|while|during|until|since|when)\b', re.I),
            'spatial': re.compile(r'\b(above|below|left|right|near|far|inside|outside|between)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?(?:\s*(?:%|kg|m|s|hours?|minutes?|seconds?))?\b'),
            'pronoun_ambig': re.compile(r'\b(he|she|they|it|him|her)\b', re.I),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|stop|quit|fail)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either.*or|only two options|only choice)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|feel)\b', re.I)
        }
        
        # Kalman Parameters
        self.Q = 0.01  # Process noise
        self.R = 0.1   # Observation noise
        self.beta = 1.0 # UCB exploration parameter

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts embodied structural features into a fixed vector."""
        text_lower = text.lower()
        features = []
        
        # Binary flags for structural elements
        features.append(1 if self.patterns['negation'].search(text) else 0)
        features.append(1 if self.patterns['comparative'].search(text) else 0)
        features.append(1 if self.patterns['conditional'].search(text) else 0)
        features.append(1 if self.patterns['causal'].search(text) else 0)
        features.append(1 if self.patterns['temporal'].search(text) else 0)
        features.append(1 if self.patterns['spatial'].search(text) else 0)
        
        # Numeric density (normalized)
        nums = self.patterns['numeric'].findall(text)
        features.append(min(len(nums) / 10.0, 1.0))
        
        # Specific numeric values for computation (simplified: count of numbers)
        features.append(len(nums))
        
        return np.array(features, dtype=float)

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Calculates score based on structural alignment and constructive computation.
        Returns a score 0.0 to 1.0.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Structural Consistency (Dot product similarity normalized)
        # If prompt has negation, correct answer often needs specific handling or matching logic.
        # Here we assume high overlap in structural markers indicates relevance.
        norm_p = np.linalg.norm(p_feat)
        norm_c = np.linalg.norm(c_feat)
        struct_sim = 0.0
        if norm_p > 0 and norm_c > 0:
            struct_sim = np.dot(p_feat, c_feat) / (norm_p * norm_c)
        
        # 2. Constructive Computation (Numeric Evaluation)
        # Extract numbers from prompt and candidate to check for valid derivation
        p_nums = [float(n) for n in self.patterns['numeric'].findall(prompt)]
        c_nums = [float(n) for n in self.patterns['numeric'].findall(candidate)]
        
        comp_score = 0.0
        if p_nums and c_nums:
            # Check if candidate number is a result of simple operations on prompt numbers
            # This is a heuristic for "solving" the problem
            try:
                p_sum = sum(p_nums)
                p_prod = 1.0
                for n in p_nums: p_prod *= (n + 1e-9) # avoid zero
                
                c_val = c_nums[-1] # Focus on last number as result
                
                # Simple heuristics for common math traps
                if abs(c_val - p_sum) < 1e-6: comp_score = 1.0
                elif len(p_nums) >= 2 and abs(c_val - (p_nums[0] * p_nums[1])) < 1e-6: comp_score = 1.0
                elif len(p_nums) >= 2 and p_nums[1] != 0 and abs(c_val - (p_nums[0] / p_nums[1])) < 1e-6: comp_score = 1.0
                # Check for direct equality (often wrong in reasoning traps)
                elif len(p_nums) == len(c_nums) and p_nums == c_nums:
                    comp_score = 0.2 # Penalize mere echoing
                else:
                    comp_score = 0.5 # Plausible if not obviously wrong
            except:
                comp_score = 0.0
        elif not p_nums and not c_nums:
            comp_score = 0.5 # Neutral if no numbers involved

        # Weighted Sum: Structural (60%) + Computation (40% of the non-structural part)
        # Ensuring structural >= 50% influence overall
        final_score = 0.6 * struct_sim + 0.4 * comp_score
        return min(max(final_score, 0.0), 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(s1_b)
        len_s2 = len(s2_b)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/simplicity in this context or using compressed sizes
        c_s1 = len(zlib.compress(s1_b))
        c_s2 = len(zlib.compress(s2_b))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c_s1, c_s2)
        denominator = max(c_s1, c_s2)
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 4. Pronoun Ambiguity (Heuristic: "who is he?" patterns)
        if re.search(r'\b(who|which)\s+(is|was)\s+(he|she|it|they)\b', p_lower, re.I):
             if self.patterns['pronoun_ambig'].search(p_lower):
                return 0.25

        # 5. Length/Complexity heuristic for unanswerability
        if len(prompt.split()) < 3:
            return 0.3 # Too short to reason about
            
        return 1.0

    def _kalman_update(self, mu: float, sigma_sq: float, z: float, H: float) -> Tuple[float, float]:
        """Single step Kalman Update for a scalar state."""
        # Prediction (identity model with noise)
        mu_pred = mu
        sigma_sq_pred = sigma_sq + self.Q
        
        # Update
        # K = P_pred * H^T * (H * P_pred * H^T + R)^-1
        # Since H is scalar (1x1) in this simplified projection:
        denom = H * sigma_sq_pred * H + self.R
        if abs(denom) < 1e-9: denom = 1e-9 # Prevent div by zero
        K = (sigma_sq_pred * H) / denom
        
        mu_new = mu_pred + K * (z - H * mu_pred)
        sigma_sq_new = (1 - K * H) * sigma_sq_pred
        
        return mu_new, max(sigma_sq_new, 1e-6)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Initialize Bandit Arms (Candidates)
        # State: mu (belief of correctness), sigma_sq (uncertainty)
        arms = []
        for i, cand in enumerate(candidates):
            arms.append({
                'id': i,
                'candidate': cand,
                'mu': 0.5,          # Prior belief
                'sigma_sq': 1.0,    # High initial uncertainty
                'structural_score': 0.0,
                'ncd_score': 0.0
            })
        
        # Pre-calculate structural scores and NCD
        # We treat the prompt's "ideal" feature vector as the target H
        # For simplicity in this scalar reduction, H is a scaling factor based on prompt complexity
        H_factor = min(len(prompt) / 100.0, 1.0) + 0.5 
        
        for arm in arms:
            # 1. Structural & Computation Score (Primary Signal)
            s_score = self._compute_structural_score(prompt, arm['candidate'])
            arm['structural_score'] = s_score
            
            # 2. NCD Score (Tiebreaker/Minor component)
            # Invert NCD so 1.0 is perfect match, 0.0 is totally different
            # We want NCD to be a tiebreaker, so we scale it down
            ncd_val = self._ncd_distance(prompt, arm['candidate'])
            # Heuristic: If candidate is very short (e.g. "Yes"), NCD might be high noise.
            # We prefer candidates that share structural tokens.
            arm['ncd_score'] = 1.0 - ncd_val 

        # Iterative Kalman-Bandit Update Simulation
        # We simulate "parsing cycles" to update beliefs
        for _ in range(5): # 5 cycles of refinement
            ucb_values = []
            for arm in arms:
                # UCB = mu + beta * sqrt(sigma_sq)
                ucb = arm['mu'] + self.beta * np.sqrt(arm['sigma_sq'])
                ucb_values.append((arm['id'], ucb))
            
            # Select arm with highest UCB (Exploration vs Exploitation)
            # In this evaluation context, we update all, but the logic follows the bandit structure
            # by prioritizing the update of uncertain/high-potential candidates in a real streaming setting.
            # Here we batch update for simplicity as per the "evaluate" interface.
            
            for arm in arms:
                # Observation z is the structural score computed
                z = arm['structural_score']
                
                # Kalman Update
                new_mu, new_sigma_sq = self._kalman_update(
                    arm['mu'], arm['sigma_sq'], z, H_factor
                )
                arm['mu'] = new_mu
                arm['sigma_sq'] = new_sigma_sq

        # Final Scoring and Ranking
        for arm in arms:
            # Final Score Composition:
            # 50%+ Structural (embedded in mu via z), 20% Computation (in z), 15% NCD
            # Mu already contains the fused structural/computation evidence.
            # We add a small NCD bonus if structural scores are close.
            
            base_score = arm['mu']
            
            # NCD Tiebreaker (max 15% weight)
            # Only apply if structural score is ambiguous (close to 0.5) or as a small boost
            ncd_bonus = 0.15 * arm['ncd_score'] if base_score > 0.4 else 0.0
            
            final_score = 0.85 * base_score + ncd_bonus
            
            # Apply Epistemic Cap (Tier B)
            if final_score > meta_cap:
                final_score = meta_cap
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            # Generate Reasoning String
            reason_parts = []
            if self.patterns['negation'].search(arm['candidate']): reason_parts.append("negation detected")
            if self.patterns['numeric'].search(arm['candidate']): reason_parts.append("numeric evaluation")
            if self.patterns['causal'].search(arm['candidate']): reason_parts.append("causal link")
            if not reason_parts: reason_parts.append("structural match")
            
            reasoning = f"Score: {final_score:.2f}. Based on: {', '.join(reason_parts)}. Uncertainty: {arm['sigma_sq']:.2f}."
            if meta_cap < 1.0:
                reasoning += " [Caution: Potential ambiguity or presupposition detected in prompt]"

            results.append({
                "candidate": arm['candidate'],
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run single evaluation to get structural score
        # We treat the single answer as a candidate list of one
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Confidence is the score, capped by the meta-analysis
        final_conf = min(base_score, meta_cap)
        
        # If the structural parser found nothing, confidence should be low (Honest Uncertainty)
        if base_score < 0.3:
            final_conf = min(final_conf, 0.3)
            
        return round(final_conf, 4)