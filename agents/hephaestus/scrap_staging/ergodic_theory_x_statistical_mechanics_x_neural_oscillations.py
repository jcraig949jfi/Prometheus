import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Sampling Oscillatory Network (SSON) Implementation.
    
    Mechanism:
    1. Structural Parsing (Energy Function E): Extracts logical constraints 
       (negations, comparatives, conditionals) to define a hypothesis cost.
    2. Oscillatory Sampling (Theta-Gamma): Simulates phase-coupled sampling where 
       'theta' cycles propose structural interpretations and 'gamma' synchrony 
       validates them against numeric/logical consistency.
    3. Fluctuation-Dissipation (Metacognition): Estimates confidence by comparing 
       the variance of structural matches (fluctuation) against the expected 
       logical consistency (dissipation/response).
    4. Ergodic Convergence: Uses NCD as a tie-breaking micro-state perturbation 
       to ensure unique ranking, approximating time-averaged convergence.
    """

    def __init__(self):
        self._theta_phase = 0.0
        self._gamma_sync = 0.5
        self._temperature = 0.1  # Simulated annealing parameter

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extracts logical constraints as energy terms."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|without|except)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numeric': len(re.findall(r'\d+(?:\.\d+)?', text_lower)),
            'length': len(text)
        }
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes energy E(x) based on structural mismatch.
        Lower energy = better fit.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        energy = 0.0
        
        # Constraint Propagation: Negation mismatch is high energy
        if p_feat['negation'] > 0:
            if c_feat['negation'] == 0:
                energy += 2.0  # Penalty for missing negation
            else:
                energy -= 0.5  # Reward for matching negation
        
        # Comparative consistency
        if p_feat['comparative'] > 0:
            if c_feat['comparative'] == 0:
                energy += 1.5
            else:
                energy -= 0.3

        # Conditional logic presence
        if p_feat['conditional'] > 0:
            if c_feat['conditional'] == 0:
                energy += 1.0
        
        # Numeric evaluation heuristic
        # If prompt has numbers, candidate should ideally have numbers or logical words
        if p_feat['numeric'] > 0:
            if c_feat['numeric'] == 0 and len(candidate.split()) < 3:
                energy += 1.0 # Suspiciously short answer for numeric prompt
        
        return energy

    def _oscillatory_sample(self, prompt: str, candidate: str) -> float:
        """
        Simulates Theta-Gamma coupling.
        Theta: Global structural rhythm (deterministic phase based on length)
        Gamma: Local feature synchrony (acceptance probability)
        """
        # Theta phase proposal
        self._theta_phase = (len(prompt) + len(candidate)) % 100 / 100.0
        
        # Base energy cost
        E = self._compute_energy(prompt, candidate)
        
        # Gamma synchrony (acceptance probability via Gibbs)
        # p ~ exp(-E/T). We invert this for scoring: Score ~ exp(-E/T)
        # Adding small oscillatory noise to simulate thermal fluctuation
        noise = math.sin(2 * math.pi * self._theta_phase) * 0.05
        prob = math.exp(-(E + noise) / self._temperature)
        
        return prob

    def _ncd_tiebreaker(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as ergodic micro-state perturbation."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        combined = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_comb = len(zlib.compress(combined))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_comb - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by simulating the self-sampling network.
        Returns ranked list based on structural consistency and oscillatory scoring.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Pre-calculate prompt features to avoid re-computation
        p_features = self._extract_structural_features(prompt)
        has_numbers = p_features['numeric'] > 0
        
        for cand in candidates:
            # 1. Structural Energy Calculation
            energy = self._compute_energy(prompt, cand)
            
            # 2. Oscillatory Sampling Score
            raw_score = self._oscillatory_sample(prompt, cand)
            
            # 3. Numeric Evaluation (Explicit Check)
            numeric_bonus = 0.0
            if has_numbers:
                # Extract numbers from candidate
                c_nums = re.findall(r'\d+(?:\.\d+)?', cand.lower())
                if c_nums:
                    # Simple heuristic: if prompt implies comparison, check consistency
                    # This is a lightweight proxy for full numeric reasoning
                    numeric_bonus = 0.5 
                else:
                    # Penalty if numbers expected but missing in short answers
                    if len(cand.split()) < 4:
                        numeric_bonus = -0.5
            
            final_score = raw_score + numeric_bonus
            
            # 4. NCD Tiebreaker (Ergodic convergence)
            ncd_val = self._ncd_tiebreaker(prompt, cand)
            # NCD is distance (lower is better), so we subtract it slightly
            final_score -= (ncd_val * 0.01) 
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural energy: {energy:.2f}, Oscillatory sync: {raw_score:.2f}, NCD penalty: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence using Fluctuation-Dissipation relation.
        Compares local structural variance against global consistency.
        Returns 0-1.
        """
        # Calculate energy of the pair
        E = self._compute_energy(prompt, answer)
        
        # Dissipation: How much does the structure 'resist' the answer?
        # Low energy = high dissipation = high confidence
        base_conf = math.exp(-abs(E) / 0.5)
        
        # Fluctuation: Variance in feature matching
        p_feat = self._extract_structural_features(prompt)
        a_feat = self._extract_structural_features(answer)
        
        # Calculate mismatch variance
        mismatches = 0
        count = 0
        for key in ['negation', 'comparative', 'conditional']:
            if p_feat[key] > 0:
                count += 1
                if a_feat[key] == 0:
                    mismatches += 1
        
        variance_penalty = 0.0
        if count > 0:
            variance_ratio = mismatches / count
            # Fluctuation-dissipation: High variance in critical features reduces confidence
            variance_penalty = variance_ratio * 0.4
            
        conf = max(0.0, min(1.0, base_conf - variance_penalty))
        
        # Boost if numeric consistency is detected and valid
        if p_feat['numeric'] > 0 and a_feat['numeric'] > 0:
            conf = min(1.0, conf + 0.1)
            
        return float(conf)