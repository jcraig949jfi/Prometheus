import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, maximum-entropy constraint satisfaction,
    and chaos-theoretic stability analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, numbers).
    2. Feature Vectorization: Maps candidates to a binary/real-valued vector space based on prompt constraints.
    3. MaxEnt Scoring: Uses an exponential family model (approximated via feature matching) to score 
       how well a candidate satisfies the extracted linear expectations.
    4. Chaos Sensitivity: Perturbs the feature vector slightly to compute a Lyapunov-like exponent.
       Candidates with high sensitivity (fragile logic) are penalized.
    5. Final Score: Expected correctness minus a stability penalty.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|every|none|any)\b', re.IGNORECASE)
        }
        self.alpha = 0.2  # Chaos penalty weight
        self.epsilon = 0.01 # Perturbation magnitude

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': int(bool(self.patterns['negation'].search(text))),
            'has_comparative': int(bool(self.patterns['comparative'].search(text))),
            'has_conditional': int(bool(self.patterns['conditional'].search(text))),
            'has_causal': int(bool(self.patterns['causal'].search(text))),
            'has_quantifier': int(bool(self.patterns['quantifier'].search(text))),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text.split())
        }
        return features

    def _compute_constraint_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute a score based on constraint satisfaction (MaxEnt proxy).
        We check if the candidate respects the structural expectations set by the prompt.
        """
        score = 0.0
        
        # 1. Negation consistency: If prompt has negation, candidate should ideally reflect it or not contradict
        if prompt_feats['has_negation']:
            score += 1.0 if cand_feats['has_negation'] else 0.5
            
        # 2. Comparative consistency
        if prompt_feats['has_comparative']:
            score += 1.0 if cand_feats['has_comparative'] else 0.0
            
        # 3. Conditional logic presence
        if prompt_feats['has_conditional']:
            score += 1.0 if cand_feats['has_conditional'] else 0.5

        # 4. Numeric consistency (Heuristic: if prompt has numbers, candidate should too)
        if len(prompt_feats['numbers']) > 0:
            if len(cand_feats['numbers']) > 0:
                # Check magnitude alignment (simplified)
                p_max = max(prompt_feats['numbers'])
                c_max = max(cand_feats['numbers']) if cand_feats['numbers'] else 0
                # Reward if candidate numbers are in similar order of magnitude or logically derived
                if p_max == 0: p_max = 1e-6
                ratio = c_max / p_max
                if 0.1 < ratio < 10.0:
                    score += 1.0
                else:
                    score += 0.2
            else:
                score += 0.0
        
        # Normalize by potential max score (approx 4.0)
        return score / 4.0

    def _compute_chaos_penalty(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Compute Lyapunov-like exponent via finite differences.
        Perturb the candidate string slightly and measure score deviation.
        """
        # Create a perturbed version of the candidate (add noise to numbers or shuffle words slightly)
        # Since we need deterministic behavior, we use a fixed seed based on string hash
        seed = hash(prompt + candidate) % (2**32)
        rng = np.random.default_rng(seed)
        
        cand_feats = self._extract_features(candidate)
        base_vec = np.array([
            cand_feats['has_negation'],
            cand_feats['has_comparative'],
            cand_feats['has_conditional'],
            len(cand_feats['numbers']),
            cand_feats['length']
        ], dtype=float)
        
        # Normalize vector for stability
        if np.max(base_vec) > 0:
            base_vec = base_vec / np.max(base_vec)
            
        # Perturb
        delta = rng.uniform(-self.epsilon, self.epsilon, size=base_vec.shape)
        perturbed_vec = base_vec + delta
        
        # Reconstruct a dummy score from perturbed vector (simulating S(x+delta))
        # In a real system, this would re-run parsing on a perturbed string.
        # Here we approximate sensitivity by checking if the feature vector is near a decision boundary.
        # If small changes flip the binary features (0->1 or 1->0), it's chaotic.
        
        # Simulate score function S(x) as dot product with uniform weights (simplified MaxEnt)
        weights = np.array([0.3, 0.3, 0.2, 0.1, 0.1])
        
        s_orig = np.dot(base_vec, weights)
        s_pert = np.dot(perturbed_vec, weights)
        
        lyapunov_exp = abs(s_pert - s_orig) / (self.epsilon + 1e-9)
        return lyapunov_exp

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Step 1 & 2: Structural parsing and feature vector construction
            # Step 3: MaxEnt scoring (approximated via constraint satisfaction)
            s_score = self._compute_constraint_score(prompt_feats, cand_feats)
            
            # Step 4: Chaos theoretic sensitivity
            chaos_pen = self._compute_chaos_penalty(prompt, cand, s_score)
            
            # Step 5: Final Score
            final_score = s_score - (self.alpha * chaos_pen)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {s_score:.2f}, Chaos penalty: {chaos_pen:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the evaluation logic to determine robustness.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 range. 
        # Theoretical max score ~1.0, min could be negative due to chaos penalty.
        confidence = max(0.0, min(1.0, score))
        return confidence