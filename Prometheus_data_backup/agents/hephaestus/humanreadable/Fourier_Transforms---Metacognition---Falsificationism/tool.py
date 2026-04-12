import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Falsification-Metacognitive Engine (SFME) Implementation.
    
    Mechanism:
    Instead of literal Fourier transforms on text (which fails reasoning tasks per 
    causal analysis), we implement the *logical analog* of the SFME:
    
    1. Structural Parsing (The Transform): We decompose the prompt and candidates 
       into a "spectrum" of logical features: negations, comparatives, conditionals, 
       and numeric values. This maps the text into a feature space similar to 
       frequency domains.
       
    2. Metacognitive Confidence (The Weight): We assign confidence weights to 
       specific constraint types. High variance in matching (e.g., missing a 
       critical negation) drastically reduces confidence in that candidate.
       
    3. Falsification Loop (The Scoring): 
       - We treat the Prompt's constraints as the "Hypothesis".
       - We treat the Candidate as the "Data".
       - We compute a "Residual": The count of unmet constraints (logical errors).
       - Candidates are scored by how well they minimize the weighted residual 
         (i.e., satisfying the most critical structural constraints).
       - NCD is used strictly as a tie-breaker for candidates with identical 
         structural scores, ensuring we beat the baseline without relying on it.
    """

    def __init__(self):
        # Metacognitive weights for different logical "bands"
        self.weights = {
            'negation': 2.5,      # High penalty for missing negations
            'comparative': 2.0,   # High penalty for wrong ordering
            'conditional': 1.5,   # Medium penalty for logic flow
            'numeric': 2.2,       # High penalty for math errors
            'constraint': 1.8,    # General constraint matching
            'base': 0.5           # Base similarity
        }
        # Thresholds for falsification
        self.falsification_threshold = 0.6

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extracts logical features (the 'spectrum') from text."""
        t_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none|without)\b', t_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after|first|last)\b', t_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', t_lower)),
            'numbers': [],
            'has_question': '?' in text,
            'length': len(text)
        }
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', t_lower)
        features['numbers'] = [float(n) for n in nums] if nums else []
        
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Evaluates how well the candidate satisfies the prompt's structural constraints.
        Returns (score, reasoning_string).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        reasons = []
        total_weight = 0.0
        
        # 1. Negation Check (Falsification of negative constraints)
        # If prompt has negations, candidate should ideally reflect understanding 
        # (simplified: if prompt says "not", candidate shouldn't blindly echo without context)
        if p_feat['negations'] > 0:
            total_weight += self.weights['negation']
            # Heuristic: If prompt has negation, candidate must not be empty and 
            # should ideally contain logical markers or specific answer patterns.
            # Strict falsification: If candidate is just "Yes" to a negative question, penalize.
            if c_feat['length'] < 3 and p_feat['has_question']:
                score -= self.weights['negation']
                reasons.append("Failed negation handling (too brief)")
            else:
                score += self.weights['negation'] * 0.8 # Partial credit for length
                reasons.append("Negation context acknowledged")

        # 2. Comparative Check
        if p_feat['comparatives'] > 0:
            total_weight += self.weights['comparative']
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += self.weights['comparative']
                reasons.append("Comparative logic detected in answer")
            else:
                # Potential failure to address comparison
                score -= self.weights['comparative'] * 0.5
                reasons.append("Missing comparative reasoning")

        # 3. Numeric Evaluation
        if len(p_feat['numbers']) >= 2:
            total_weight += self.weights['numeric']
            # If prompt has numbers, check if candidate has numbers
            if len(c_feat['numbers']) > 0:
                score += self.weights['numeric']
                reasons.append("Numeric data present")
                
                # Simple transitivity/comparison check if both have 2+ numbers
                if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 2:
                    p_diff = p_feat['numbers'][0] - p_feat['numbers'][1]
                    c_diff = c_feat['numbers'][0] - c_feat['numbers'][1]
                    # Check if direction of difference is preserved (simplified)
                    if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0):
                        score += self.weights['numeric'] * 0.5
                        reasons.append("Numeric trend consistent")
            else:
                score -= self.weights['numeric'] * 0.8
                reasons.append("Numeric reasoning missing")

        # 4. Conditional/Logic Flow
        if p_feat['conditionals'] > 0:
            total_weight += self.weights['conditional']
            if c_feat['conditionals'] > 0 or any(k in c_feat for k in ['if', 'then']):
                score += self.weights['conditional']
                reasons.append("Conditional logic maintained")
        
        # Normalize score to 0-1 range roughly
        if total_weight > 0:
            # Base score starts at 0.5, adjusted by weighted performance
            normalized_score = 0.5 + (score / (total_weight * 2.0)) 
        else:
            normalized_score = 0.5
            
        return min(1.0, max(0.0, normalized_score)), "; ".join(reasons) if reasons else "Structural match"

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            comp_len = len(zlib.compress(b1 + b2))
            min_len = min(len1, len2)
            if min_len == 0: return 1.0
            ncd = (comp_len - min_len) / max(len1, len2) # Standard variant
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing if needed
        # (Though _check_constraint_satisfaction handles internal parsing)
        
        for cand in candidates:
            # Step 1: Structural/Falsification Score (Primary Signal)
            struct_score, reasoning = self._check_constraint_satisfaction(prompt, cand)
            
            # Step 2: Metacognitive Confidence
            # Confidence is high if structural score is extreme (very good or very bad)
            # and low if ambiguous. Here we map score directly to likelihood of correctness.
            final_score = struct_score
            
            # Step 3: NCD Tiebreaker (Only if scores are very close, handled implicitly by small addition)
            # We add a tiny fraction of NCD inverse to break ties without dominating
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so higher is better, scale down significantly
            ncd_bonus = (1.0 - ncd_val) * 0.001 
            
            total_score = final_score + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural evaluation score as the primary confidence metric.
        """
        score, _ = self._check_constraint_satisfaction(prompt, answer)
        
        # Apply a sigmoid-like mapping to ensure strict 0-1 bounds with margin
        # If score > 0.5 (pass), confidence approaches 1. If < 0.5, approaches 0.
        # This acts as the "Kalman update" on the belief state.
        confidence = 1.0 / (1.0 + math.exp(-10 * (score - 0.5)))
        
        return round(confidence, 4)