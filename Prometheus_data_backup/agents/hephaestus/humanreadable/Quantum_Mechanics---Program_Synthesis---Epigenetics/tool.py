import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Epigenetic Program Synthesizer (QEPS) - Computational Analogue
    
    Mechanism:
    1. Structural Parsing (The 'Quantum Circuit'): Instead of physical qubits, we encode
       candidate answers as vectors of structural features (negations, comparatives, 
       conditionals, numeric values). This creates a 'superposition' of logical properties.
       
    2. Epigenetic Methylation (The 'Memory'): We maintain a dynamic 'methylation vector' 
       representing the historical reliability of specific structural patterns (e.g., 
       presence of 'not', specific numeric ranges). This vector is updated via a 
       gradient-like rule based on immediate consistency checks.
       
    3. Measurement (Scoring): Candidates are scored by projecting their structural 
       vector onto the current methylation state. High alignment yields high probability 
       amplitude (score).
       
    4. NCD Tiebreaker: Used only when structural scores are indistinguishable.
    """

    def __init__(self):
        # Epigenetic marks: Weights for structural features. 
        # Initialized to neutral (0.5), evolves during evaluation.
        self.methylation_weights = {
            'negation_present': 0.5,
            'comparative_present': 0.5,
            'conditional_present': 0.5,
            'numeric_consistency': 0.5,
            'length_parity': 0.5
        }
        self.learning_rate = 0.1

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features from text (The 'Basis State')."""
        lower_text = text.lower()
        features = {}
        
        # Negation detection
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        features['negation_present'] = 1.0 if any(n in lower_text for n in negations) else 0.0
        
        # Comparative detection
        comparatives = ['more', 'less', 'greater', 'smaller', 'better', 'worse', '>', '<', '==']
        features['comparative_present'] = 1.0 if any(c in lower_text for c in comparatives) else 0.0
        
        # Conditional detection
        conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']
        features['conditional_present'] = 1.0 if any(c in lower_text for c in conditionals) else 0.0
        
        # Numeric extraction (simplified)
        numbers = re.findall(r"-?\d+\.?\d*", text)
        features['has_numbers'] = 1.0 if numbers else 0.0
        features['numeric_value'] = float(numbers[0]) if numbers else 0.0
        
        # Length parity (simple structural hash)
        features['length_parity'] = 1.0 if len(text) % 2 == 0 else 0.0
        
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Immediate 'measurement' to update epigenetic marks.
        Checks for basic logical contradictions between prompt and candidate.
        Returns a consistency score (0.0 to 1.0).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 1.0
        
        # Simple constraint propagation: 
        # If prompt implies negation context and candidate lacks it (or vice versa), penalize.
        # This is a heuristic proxy for logical alignment.
        
        prompt_has_neg = p_feat['negation_present'] > 0.5
        cand_has_neg = c_feat['negation_present'] > 0.5
        
        # Heuristic: If prompt asks "Is it not X?" and answer is "Yes", it's complex.
        # Here we just check feature alignment as a proxy for 'survival'.
        if prompt_has_neg != cand_has_neg:
            # Mismatch in negation structure often indicates error in simple logic puzzles
            score -= 0.5
            
        # Numeric consistency check
        if p_feat['has_numbers'] > 0.5 and c_feat['has_numbers'] > 0.5:
            # If both have numbers, they should ideally be related or consistent.
            # Since we can't solve the math without context, we reward presence.
            score += 0.2
            
        return max(0.0, min(1.0, score))

    def _update_epigenetics(self, consistency_score: float, features: Dict[str, float]):
        """Update methylation weights based on consistency (Gradient-like update)."""
        for key in self.methylation_weights:
            if key in features:
                # If feature was present and result was consistent, increase weight
                # If feature was present and inconsistent, decrease weight
                presence = features[key]
                if presence > 0:
                    delta = self.learning_rate * (consistency_score - 0.5) * presence
                    self.methylation_weights[key] += delta
                    # Clamp weights
                    self.methylation_weights[key] = max(0.1, min(0.9, self.methylation_weights[key]))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0:
            return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-calculate prompt features
        prompt_features = self._extract_features(prompt)
        
        for candidate in candidates:
            cand_features = self._extract_features(candidate)
            
            # 1. Structural Scoring (Quantum Amplitude Simulation)
            # Dot product of candidate features and current methylation weights
            structural_score = 0.0
            weight_sum = 0.0
            
            for key in self.methylation_weights:
                if key in cand_features:
                    # Weighted contribution
                    w = self.methylation_weights.get(key, 0.5)
                    val = cand_features[key]
                    structural_score += w * val
                    weight_sum += w
            
            if weight_sum > 0:
                structural_score /= (weight_sum / len(self.methylation_weights)) # Normalize
            else:
                structural_score = 0.5

            # 2. Consistency Check & Epigenetic Update
            consistency = self._check_logical_consistency(prompt, candidate)
            # Simulate updating the 'environment' based on this candidate's plausibility
            # We do this tentatively for scoring purposes
            temp_score = (structural_score * 0.7) + (consistency * 0.3)
            
            # Update internal state (Epigenetic learning)
            # We treat the current best guess as the 'truth' for updating marks
            if consistency > 0.5:
                self._update_epigenetics(consistency, cand_features)

            # 3. NCD Tiebreaker
            ncd_score = self._compute_ncd(prompt, candidate)
            # Invert NCD (lower distance = higher score) and scale down to be a tiebreaker
            ncd_bonus = (1.0 - ncd_score) * 0.01 

            final_score = temp_score + ncd_bonus
            
            ranked.append({
                "candidate": candidate,
                "score": round(final_score, 6),
                "reasoning": f"Structural alignment: {structural_score:.2f}, Consistency: {consistency:.2f}, NCD bonus: {ncd_bonus:.4f}"
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and epigenetic history.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Calculate alignment with current epigenetic state
        alignment = 0.0
        for key in self.methylation_weights:
            if key in a_feat and key in p_feat:
                # Check if feature presence matches
                if (p_feat[key] > 0.5 and a_feat[key] > 0.5) or (p_feat[key] < 0.5 and a_feat[key] < 0.5):
                    alignment += self.methylation_weights[key]
        
        base_conf = alignment / len(self.methylation_weights) if len(self.methylation_weights) > 0 else 0.5
        
        # Boost if logical consistency is high
        consistency = self._check_logical_consistency(prompt, answer)
        
        final_conf = (base_conf * 0.4) + (consistency * 0.6)
        return round(max(0.0, min(1.0, final_conf)), 4)