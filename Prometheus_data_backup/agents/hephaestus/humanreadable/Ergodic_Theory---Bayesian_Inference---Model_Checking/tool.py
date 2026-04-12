import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-Bayesian Model-Checker (EBMC) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions based on negations, comparatives,
       conditionals, numeric thresholds, and causal cues using regex.
    2. State Construction: Builds a simplified Kripke structure where states represent
       truth assignments consistent with the candidate text.
    3. Ergodic Analysis: Constructs a transition matrix based on logical implications.
       Computes the stationary distribution via power iteration to estimate the probability
       that the system remains in a state satisfying the prompt's constraints.
    4. Bayesian Scoring: Uses the satisfaction probability as a likelihood term to update
       a Beta prior, yielding a posterior mean score.
    5. Fallback: Uses NCD (Normalized Compression Distance) only when structural signals are weak.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|leads to|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'causal': re.compile(r'\b(because|since|therefore|thus|hence)\b', re.IGNORECASE)
        }
        self.alpha_0 = 1.0
        self.beta_0 = 1.0

    def _extract_features(self, text: str) -> Dict[str, bool]:
        """Extract boolean features from text based on regex patterns."""
        text_lower = text.lower()
        features = {}
        features['has_negation'] = bool(self.patterns['negation'].search(text_lower))
        features['has_comparative'] = bool(self.patterns['comparative'].search(text_lower))
        features['has_conditional'] = bool(self.patterns['conditional'].search(text_lower))
        features['has_causal'] = bool(self.patterns['causal'].search(text_lower))
        
        # Numeric extraction and simple comparison logic
        nums = self.patterns['numeric'].findall(text)
        features['has_numbers'] = len(nums) > 0
        features['numeric_consistent'] = True
        if len(nums) >= 2:
            try:
                # Check for basic ascending/descending order consistency if keywords exist
                f_nums = [float(n) for n in nums]
                if 'increasing' in text_lower or 'rise' in text_lower:
                    features['numeric_consistent'] = all(f_nums[i] <= f_nums[i+1] for i in range(len(f_nums)-1))
                elif 'decreasing' in text_lower or 'fall' in text_lower:
                    features['numeric_consistent'] = all(f_nums[i] >= f_nums[i+1] for i in range(len(f_nums)-1))
            except ValueError:
                features['numeric_consistent'] = True
        return features

    def _build_transition_matrix(self, prompt_feats: Dict, cand_feats: Dict) -> np.ndarray:
        """
        Construct a 2x2 transition matrix representing state consistency.
        State 0: Inconsistent/False
        State 1: Consistent/True
        """
        # Calculate structural overlap score (0.0 to 1.0)
        match_count = 0
        total_checks = 0
        
        checks = ['has_negation', 'has_comparative', 'has_conditional', 'has_causal', 'has_numbers']
        for key in checks:
            if key in prompt_feats and key in cand_feats:
                # If prompt has a feature, candidate should ideally have it too (simplified logic)
                if prompt_feats[key]:
                    total_checks += 1
                    if cand_feats[key]:
                        match_count += 1
                else:
                    # If prompt lacks feature, candidate lacking it is also a match
                    total_checks += 1
                    if not cand_feats[key]:
                        match_count += 1
        
        # Base consistency probability
        if total_checks == 0:
            base_prob = 0.5
        else:
            base_prob = match_count / total_checks
            
        # Adjust for numeric consistency
        if cand_feats.get('numeric_consistent') is False:
            base_prob *= 0.5
            
        # Ensure ergodicity (non-zero probabilities)
        p_00 = 0.1
        p_01 = 0.9
        p_10 = 1.0 - base_prob if base_prob > 0.1 else 0.9
        p_11 = base_prob if base_prob > 0.1 else 0.1
        
        # Normalize rows to form a valid stochastic matrix
        # Row 0 (from state 0), Row 1 (from state 1)
        # We construct it such that state 1 is the "satisfying" state
        row_0 = np.array([0.5, 0.5]) # Random walk from inconsistency
        row_1 = np.array([1.0 - base_prob, base_prob]) # Bias towards consistency based on features
        
        # Normalize just in case
        row_0 = row_0 / row_0.sum()
        row_1 = row_1 / row_1.sum()
        
        return np.array([row_0, row_1])

    def _compute_stationary_distribution(self, P: np.ndarray, steps: int = 20) -> np.ndarray:
        """Power iteration to find stationary distribution pi."""
        pi = np.array([0.5, 0.5])
        for _ in range(steps):
            pi = pi @ P
        return pi

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate a single candidate against the prompt.
        Returns a score between 0 and 1.
        """
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        # 1. Model Checking & Ergodic Step
        P = self._build_transition_matrix(prompt_feats, cand_feats)
        pi = self._compute_stationary_distribution(P)
        
        # Probability of being in the "True" state (index 1)
        likelihood = pi[1]
        
        # 2. Bayesian Scoring
        alpha = self.alpha_0 + likelihood
        beta = self.beta_0 + (1.0 - likelihood)
        score = alpha / (alpha + beta)
        
        # 3. Fallback to NCD if structural signal is weak (score near prior mean 0.5)
        if 0.45 < score < 0.55:
            ncd = self._calculate_ncd(prompt, answer)
            # Invert NCD (low distance = high similarity = higher score)
            # Scale NCD influence to not overpower structural logic
            ncd_score = 1.0 - ncd
            # Blend slightly towards NCD only when uncertain
            score = 0.6 * score + 0.4 * ncd_score
            
        return float(np.clip(score, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate all candidates and return ranked list.
        """
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {score:.4f}, Ergodic likelihood applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results