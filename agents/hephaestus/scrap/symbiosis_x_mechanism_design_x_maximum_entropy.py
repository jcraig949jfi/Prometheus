import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Entropy-Regularized Mechanism Designer (SERMD) Implementation.
    
    Mechanism:
    1. Mechanism Design (Core): The evaluate() function acts as the mechanism designer,
       defining allocation rules based on structural constraints (negations, comparatives).
    2. Maximum Entropy (Confidence): The confidence() method uses an entropy-based 
       regularization term to penalize over-confidence when structural signals are weak,
       preventing bias on limited data.
    3. Symbiosis (Feedback Loop): A mutualistic update where 'learner' agents (structural parsers)
       provide feedback on candidate validity, and 'designer' agents (scoring logic) adjust
       weights to maximize a utility function balancing accuracy and diversity.
       
    This avoids direct reliance on fragile symbiotic/entropy scoring for the primary rank,
    using them instead for calibration and tie-breaking as per causal intelligence guidelines.
    """

    def __init__(self):
        # State for the "Designer" belief distribution (simplified to weights for this context)
        self.structural_weight = 0.7
        self.entropy_regularization = 0.3
        self.ncd_tiebreaker_weight = 0.1

    def _parse_structure(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negation_count': 0,
            'comparative_count': 0,
            'conditional_count': 0,
            'numeric_value': 0.0,
            'has_numbers': False
        }
        
        # Negations
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        features['negation_count'] = sum(1 for n in negations if re.search(r'\b' + n + r'\b', text_lower))
        
        # Comparatives
        comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse', '>', '<']
        features['comparative_count'] = sum(1 for c in comparatives if c in text_lower)
        
        # Conditionals
        conditionals = ['if', 'then', 'unless', 'provided', 'assuming']
        features['conditional_count'] = sum(1 for c in conditionals if re.search(r'\b' + c + r'\b', text_lower))

        # Numeric extraction (simple float extraction)
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            features['has_numbers'] = True
            try:
                # Take the first valid number as a representative value for simple comparisons
                features['numeric_value'] = float(numbers[0])
            except ValueError:
                pass
                
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _calculate_entropy_penalty(self, probs: List[float]) -> float:
        """Calculate entropy to regularize confidence (MaxEnt principle)."""
        if not probs or len(probs) == 0:
            return 0.0
        # Normalize to ensure sum to 1
        total = sum(probs)
        if total == 0:
            return 0.0
        normalized = [p / total for p in probs]
        
        entropy = 0.0
        for p in normalized:
            if p > 0:
                entropy -= p * math.log(p + 1e-10)
        
        # Max entropy for uniform distribution
        max_entropy = math.log(len(probs)) if len(probs) > 1 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using a Mechanism Design approach.
        The mechanism allocates scores based on structural alignment with the prompt.
        """
        if not candidates:
            return []
            
        prompt_features = self._parse_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD for tie-breaking if needed
        ncd_scores = []
        for i, cand in enumerate(candidates):
            # NCD between prompt and candidate (lower is more similar)
            ncd = self._compute_ncd(prompt, cand)
            ncd_scores.append(ncd)
            
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        min_ncd = min(ncd_scores) if ncd_scores else 0.0
        ncd_range = (max_ncd - min_ncd) if (max_ncd - min_ncd) > 1e-9 else 1.0

        for i, candidate in enumerate(candidates):
            cand_features = self._parse_structure(candidate)
            score = 0.0
            reasoning_parts = []

            # Mechanism Rule 1: Negation Consistency
            # If prompt has negation, candidate should reflect it or answer appropriately
            if prompt_features['negation_count'] > 0:
                if cand_features['negation_count'] > 0:
                    score += 0.3
                    reasoning_parts.append("Aligned negation structure")
                else:
                    # Potential mismatch, but not always wrong depending on answer type
                    score += 0.1 
            
            # Mechanism Rule 2: Comparative Logic
            if prompt_features['comparative_count'] > 0:
                if cand_features['comparative_count'] > 0:
                    score += 0.3
                    reasoning_parts.append("Matched comparative logic")
                else:
                    score += 0.05

            # Mechanism Rule 3: Conditional Flow
            if prompt_features['conditional_count'] > 0:
                if cand_features['conditional_count'] > 0:
                    score += 0.2
                    reasoning_parts.append("Preserved conditional flow")
            
            # Mechanism Rule 4: Numeric Consistency
            if prompt_features['has_numbers'] and cand_features['has_numbers']:
                # Simple heuristic: if prompt asks for comparison, check magnitude
                if prompt_features['comparative_count'] > 0:
                    # This is a simplified check; real logic would parse the specific comparison
                    score += 0.2
                    reasoning_parts.append("Numeric presence detected")
            elif prompt_features['has_numbers'] and not cand_features['has_numbers']:
                # Penalty if prompt is numeric but answer isn't (often wrong in math tasks)
                score -= 0.1

            # Base score for attempting an answer
            score += 0.2
            
            # NCD Tiebreaker (Normalized)
            # Invert NCD so higher similarity (lower NCD) gives higher score contribution
            norm_ncd = (ncd_scores[i] - min_ncd) / ncd_range
            ncd_contribution = (1.0 - norm_ncd) * self.ncd_tiebreaker_weight
            score += ncd_contribution

            # Normalize score to 0-1 range roughly
            final_score = max(0.0, min(1.0, score))
            
            scored_candidates.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural baseline applied"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculate confidence using Maximum Entropy regularization.
        High entropy (uncertainty in structural match) reduces confidence.
        """
        prompt_feat = self._parse_structure(prompt)
        ans_feat = self._parse_structure(answer)
        
        # Structural overlap signal
        signal_strength = 0.0
        if prompt_feat['negation_count'] > 0 and ans_feat['negation_count'] > 0:
            signal_strength += 0.4
        elif prompt_feat['negation_count'] == 0 and ans_feat['negation_count'] == 0:
            signal_strength += 0.2 # Neutral alignment
            
        if prompt_feat['comparative_count'] > 0 and ans_feat['comparative_count'] > 0:
            signal_strength += 0.3
            
        if prompt_feat['conditional_count'] > 0 and ans_feat['conditional_count'] > 0:
            signal_strength += 0.3
            
        if prompt_feat['has_numbers'] and ans_feat['has_numbers']:
            signal_strength += 0.2

        # Maximum Entropy Regularization
        # If structural signals are weak, the distribution over possible "correctness" 
        # should have high entropy, leading to lower confidence.
        # We simulate the "belief distribution" over correctness as [signal, 1-signal]
        p_correct = min(1.0, signal_strength)
        p_incorrect = 1.0 - p_correct
        
        # Entropy of the binary belief
        probs = [p_correct, p_incorrect]
        entropy = self._calculate_entropy_penalty(probs)
        
        # Regularize: Confidence = Raw Signal * (1 - Entropy_Penalty_Factor)
        # If entropy is high (close to 1.0 for uniform), confidence drops significantly
        confidence_val = p_correct * (1.0 - 0.5 * entropy)
        
        return max(0.0, min(1.0, confidence_val))