import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Falsificationism, and Thermodynamics.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, causals, numbers).
    2. Kalman Update: Treats belief as a Gaussian (mu, sigma). Updates belief based on 
       feature evidence (z) and observation variance (R). Negative evidence (falsification)
       sharply reduces mu.
    3. Thermodynamic Scoring: Computes Free Energy F = U - T*S. 
       U (Internal Energy) ~ mu^2 (plausibility). 
       S (Entropy) ~ log(sigma) (uncertainty).
       Lower F implies higher stability/truth. Score = -F.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|never|no|none|neither|without)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|-er)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
        'causal': re.compile(r'\b(cause|causes|because|therefore|thus|lead|leads|due to)\b', re.I),
        'ordering': re.compile(r'\b(first|last|before|after|next|previous|sequence)\b', re.I),
        'quantifier': re.compile(r'\b(all|some|every|each|any|most|few)\b', re.I),
        'numbers': re.compile(r'\b(\d+(?:\.\d+)?)\b')
    }

    def __init__(self):
        self.T = 0.5  # Temperature parameter for entropy weight
        self.R_default = 1.0  # Default observation variance
        self.R_ambiguous = 2.0  # Higher variance for ambiguous patterns

    def _extract_features(self, text: str) -> Dict[str, List]:
        """Extract structural features and numeric values from text."""
        features = {}
        for key, pattern in self.PATTERNS.items():
            if key == 'numbers':
                matches = pattern.findall(text)
                features[key] = [float(m) for m in matches]
            else:
                features[key] = pattern.findall(text)
        return features

    def _compute_observation(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Compute observation z (support/contradiction) and variance R.
        Returns (z, R). z in {-1, 0, 1}.
        """
        z_total = 0.0
        r_total = 0.0
        count = 0
        
        # Check logical consistency of features
        # If prompt has negation, candidate should reflect it or not contradict
        has_prompt_neg = len(prompt_feats['negation']) > 0
        has_cand_neg = len(cand_feats['negation']) > 0
        
        # Simple heuristic: Matching presence/absence of logical markers suggests consistency
        # This is a simplification; real logic requires NLI, but we use structural overlap.
        
        # 1. Negation consistency
        if has_prompt_neg and has_cand_neg:
            z_total += 1.0; r_total += self.R_default; count += 1
        elif not has_prompt_neg and not has_cand_neg:
            z_total += 0.5; r_total += self.R_default; count += 1 # Neutral-positive
        elif has_prompt_neg and not has_cand_neg:
            # Potential falsification if candidate ignores a critical negation
            # But only if the candidate claims something positive that the negation denies
            z_total -= 0.5; r_total += self.R_ambiguous; count += 1
            
        # 2. Comparative/Ordering alignment
        if prompt_feats['comparative'] or prompt_feats['ordering']:
            if cand_feats['comparative'] or cand_feats['ordering']:
                z_total += 1.0; r_total += self.R_default; count += 1
            else:
                z_total -= 0.2; r_total += self.R_ambiguous; count += 1

        # 3. Causal/Conditional alignment
        if prompt_feats['causal'] or prompt_feats['conditional']:
            if cand_feats['causal'] or cand_feats['conditional']:
                z_total += 0.8; r_total += self.R_default; count += 1
        
        # 4. Numeric consistency (Heuristic)
        # If numbers exist in both, check magnitude relations if comparatives exist
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        if p_nums and c_nums:
            # If prompt implies a relation (e.g., "greater than"), check if candidate respects it
            # Since we don't parse full semantics, we reward numeric presence in complex queries
            z_total += 0.5; r_total += self.R_default; count += 1

        if count == 0:
            return 0.0, self.R_ambiguous
        
        return z_total / count, r_total / count

    def _kalman_update(self, mu: float, sigma: float, z: float, R: float) -> Tuple[float, float]:
        """Perform scalar Kalman update."""
        H = 1.0
        # Kalman Gain
        K = sigma * H / (H * H * sigma + R)
        # Update mean (Falsification: negative z reduces mu)
        mu_new = mu + K * (z - H * mu)
        # Update variance
        sigma_new = (1.0 - K * H) * sigma
        return mu_new, sigma_new

    def _compute_free_energy(self, mu: float, sigma: float) -> float:
        """Compute Free Energy F = U - T*S. Return -F as score."""
        # U = 0.5 * mu^2 (Energy of belief)
        U = 0.5 * (mu ** 2)
        # S = 0.5 * log(sigma + epsilon) (Entropy/Uncertainty)
        epsilon = 1e-6
        S = 0.5 * np.log(sigma + epsilon)
        F = U - self.T * S
        return -F  # Higher score = lower free energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Initial state: neutral belief, high uncertainty
            mu = 0.0
            sigma = 1.0
            
            # Get observation from structural analysis
            z, R = self._compute_observation(prompt_feats, cand_feats, prompt, cand)
            
            # Kalman Update (Falsification step)
            mu, sigma = self._kalman_update(mu, sigma, z, R)
            
            # Additional falsification check: 
            # If prompt has "not" and candidate lacks it while making a strong claim, penalize heavily
            if len(prompt_feats['negation']) > 0 and len(cand_feats['negation']) == 0:
                if len(cand_feats['causal']) > 0 or len(cand_feats['comparative']) > 0:
                    mu -= 0.5 # Direct penalty
                    sigma *= 1.5 # Increase uncertainty due to conflict

            score = self._compute_free_energy(mu, sigma)
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Belief(mu={mu:.2f}, var={sigma:.2f}), Obs(z={z:.2f})"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 range. 
        # Typical scores range from -2 (bad) to 2 (good). 
        # Sigmoid-like mapping: 1 / (1 + exp(-score))
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))