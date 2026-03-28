import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Predictive-Coding Engine based on the Free Energy Principle.
    
    Mechanism:
    1. Free Energy Core (Primary Driver): The 'evaluate' loop minimizes variational free energy
       by reducing prediction error between structural expectations and candidate content.
    2. Bayesian Priors (Secondary Support): Structural parsing extracts logical constraints
       (negations, comparatives, conditionals) to form a rigid prior distribution over valid answers.
    3. Oscillatory Analogy (Confidence Wrapper): 
       - Theta (Prior): Encoded as the structural constraint match strength.
       - Gamma (Error): Encoded as the NCD-based surprise/deviation.
       - Coupling: Confidence is the ratio of Prior Strength / (Prior Strength + Prediction Error).
       This allows the system to report low confidence when structural signals are weak (exploratory)
       or when prediction error is high (hypothesis rejected).
    """

    def __init__(self):
        # Structural keywords for prior extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.quantifiers = ['all', 'every', 'some', 'any', 'most', 'few']

    def _extract_structure(self, text: str) -> dict:
        """Parses text for logical constraints (Theta-band prior encoding)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        has_quantifier = any(q in words for q in self.quantifiers)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
        nums = [float(n) for n in numbers]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'quantifier': has_quantifier,
            'numbers': nums,
            'word_count': len(words)
        }

    def _check_logical_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """
        Computes a consistency score based on structural constraints.
        Returns a value between 0.0 (violation) and 1.0 (consistent).
        """
        candidate_lower = candidate.lower()
        score = 1.0
        
        # Constraint 1: Negation handling
        # If prompt has negation, candidate should ideally reflect it or not contradict it.
        # Simple heuristic: If prompt negates, and candidate is a simple "yes"/"no", check alignment.
        # This is a simplified proxy for complex logical propagation.
        if prompt_struct['negation']:
            if candidate_lower.strip() in ['yes', 'true', 'correct']:
                # In many reasoning traps, a bare "yes" to a negative question is wrong.
                # We apply a mild penalty unless the candidate is long enough to explain.
                if len(candidate.split()) < 4:
                    score -= 0.3
        
        # Constraint 2: Numeric consistency
        if prompt_struct['numbers'] and len(prompt_struct['numbers']) >= 2:
            # If numbers exist, check if candidate contains a number that makes sense?
            # Too complex for static analysis without specific math parsing.
            # Instead, prioritize candidates that contain numbers if the prompt has many.
            cand_nums = re.findall(r"-?\d+(?:\.\d+)?", candidate)
            if not cand_nums:
                # Penalty for ignoring numeric data in prompt
                score -= 0.2
                
        return max(0.0, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len_combined = len(zlib.compress(b1 + b2))
        
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using max for normalization to keep it 0-1
        denominator = max(len1, len2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing free energy (prediction error).
        Score = Structural_Prior_Strength * (1 - Prediction_Error)
        """
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Baseline compression of prompt for NCD calculation
        prompt_clean = re.sub(r'\s+', ' ', prompt).strip()
        
        for candidate in candidates:
            cand_clean = re.sub(r'\s+', ' ', candidate).strip()
            
            # 1. Compute Prediction Error (Gamma-band analog) via NCD
            # High NCD = High Surprise = High Error
            prediction_error = self._compute_ncd(prompt_clean, cand_clean)
            
            # 2. Compute Prior Strength (Theta-band analog) via Structural Parsing
            # Checks if candidate respects logical constraints implied by prompt structure
            logical_consistency = self._check_logical_consistency(prompt_struct, candidate)
            
            # 3. Free Energy Minimization Score
            # We want Low Error and High Consistency.
            # Score = Consistency * (1 - Error)
            # Adding a small bonus for length appropriateness (avoiding empty strings)
            length_penalty = 0.0 if len(candidate.strip()) > 0 else 1.0
            
            base_score = logical_consistency * (1.0 - prediction_error) * (1.0 - length_penalty)
            
            # Heuristic boost for structural keywords appearing in both (Overlap)
            # This helps when NCD is noisy due to length differences
            common_words = set(re.findall(r'\b\w+\b', prompt_clean.lower())) & \
                           set(re.findall(r'\w+\b', cand_clean.lower()))
            overlap_bonus = min(0.1, len(common_words) * 0.01)
            
            final_score = min(1.0, base_score + overlap_bonus)
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural consistency: {logical_consistency:.2f}, Prediction error: {prediction_error:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence as oscillatory coupling:
        Confidence = Prior_Strength / (Prior_Strength + Prediction_Error + epsilon)
        
        High prior + Low error -> High confidence (Focused)
        Low prior + High error -> Low confidence (Exploratory/Rejected)
        """
        prompt_struct = self._extract_structure(prompt)
        
        # Theta: Prior strength from structural analysis
        prior_strength = self._check_logical_consistency(prompt_struct, answer)
        # Boost prior if prompt has strong logical markers and answer is non-trivial
        if any([prompt_struct['negation'], prompt_struct['conditional'], prompt_struct['comparative']]):
            if len(answer.split()) > 3:
                prior_strength = min(1.0, prior_strength + 0.2)
        
        # Gamma: Prediction error via NCD
        prediction_error = self._compute_ncd(prompt, answer)
        
        # Oscillatory coupling formula
        epsilon = 1e-6
        confidence_val = prior_strength / (prior_strength + prediction_error + epsilon)
        
        return min(1.0, max(0.0, confidence_val))