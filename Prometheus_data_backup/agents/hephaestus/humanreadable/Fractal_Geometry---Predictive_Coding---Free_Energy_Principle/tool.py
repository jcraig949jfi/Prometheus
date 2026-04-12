import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Predictive Coding Network (FPCN) Approximation.
    
    Mechanism:
    1. Free Energy Principle (Core): Minimizes 'surprise' by evaluating how well a candidate
       satisfies logical constraints derived from the prompt. Lower prediction error = higher score.
    2. Fractal Geometry (Structural): Implements self-similarity by recursively parsing logical
       structures (negations, conditionals) at sentence and clause levels. The 'fractal prior'
       assumes valid reasoning maintains consistent truth values across these scales.
    3. Predictive Coding: Computes prediction errors (mismatch between expected logical outcomes
       and candidate implications) to rank candidates.
       
    Implementation Strategy:
    - Uses structural parsing (negations, comparatives, conditionals) as the primary signal.
    - Applies a recursive 'fractal' scan to detect constraint violations at multiple granularities.
    - Uses NCD only as a tiebreaker for candidates with identical logical scores.
    """

    def __init__(self):
        self.comparators = ['greater than', 'less than', 'equal to', 'larger than', 'smaller than']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.logic_keywords = ['therefore', 'thus', 'hence', 'because', 'so']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        count = 0
        for k in keywords:
            # Simple word boundary approximation
            pattern = r'\b' + re.escape(k) + r'\b'
            count += len(re.findall(pattern, text))
        return count

    def _extract_numbers(self, text: str) -> List[float]:
        # Extracts floating point numbers
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Checks if numeric relationships in candidate match prompt logic."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric signal
        
        # Simple heuristic: If prompt has comparison words, check if candidate numbers align
        p_low = min(p_nums)
        p_high = max(p_nums) if len(p_nums) > 1 else p_nums[0]
        
        if len(c_nums) == 0:
            return 0.0
            
        c_val = c_nums[0]
        
        # Detect intent
        is_greater = any(k in prompt for k in ['greater', 'larger', 'more', 'max'])
        is_less = any(k in prompt for k in ['less', 'smaller', 'min', 'fewer'])
        
        score = 0.0
        if is_greater and c_val == max(c_nums + [p_high]): # Candidate picks max if asked for greater
            score += 1.0
        if is_less and c_val == min(c_nums + [p_low]): # Candidate picks min if asked for less
            score += 1.0
            
        # Penalty if numbers are present but completely unrelated magnitude (rough check)
        if p_nums and c_nums:
            if abs(c_val) > 0 and all(abs(c_val - n) > abs(c_val)*0.5 for n in p_nums if n != 0):
                # Only penalize if it's not a direct extraction
                pass 
        return score

    def _fractal_logical_scan(self, text: str, depth: int = 0) -> Dict[str, float]:
        """
        Recursively scans text for logical structures (self-similar patterns).
        Returns a dict of logical features: {negation_count, conditional_count, contradiction_risk}
        """
        features = {
            'negations': 0.0,
            'conditionals': 0.0,
            'logic_ops': 0.0,
            'complexity': 0.0
        }
        
        norm_text = self._normalize(text)
        words = norm_text.split()
        if not words:
            return features

        # Base scale
        features['negations'] = self._count_keywords(norm_text, self.negations)
        features['conditionals'] = self._count_keywords(norm_text, self.conditionals)
        features['logic_ops'] = self._count_keywords(norm_text, self.logic_keywords)
        features['complexity'] = len(words) ** 0.5  # Fractal dimension approximation

        # Recursive scale (sub-clauses split by commas or 'and'/'or')
        if depth < 2: # Limit recursion depth to prevent explosion
            separators = [',', ' and ', ' or ', ';']
            parts = [text]
            for sep in separators:
                new_parts = []
                for p in parts:
                    new_parts.extend(p.split(sep))
                if len(new_parts) > len(parts):
                    parts = new_parts
            
            if len(parts) > 1:
                sub_features = {'negations': 0, 'conditionals': 0, 'logic_ops': 0, 'complexity': 0}
                for part in parts:
                    res = self._fractal_logical_scan(part, depth + 1)
                    for k in sub_features:
                        sub_features[k] += res[k]
                
                # Aggregate with scaling factor (fractal weighting)
                scale = 0.5
                features['negations'] += sub_features['negations'] * scale
                features['conditionals'] += sub_features['conditionals'] * scale

        return features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a 'Free Energy' score (lower is better, so we invert for final score).
        F = Prediction Error + Complexity Penalty
        """
        p_features = self._fractal_logical_scan(prompt)
        c_features = self._fractal_logical_scan(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Predictive Coding)
        # If prompt has strong negation logic, candidate should reflect awareness (simplified)
        if p_features['negations'] > 0:
            # Expect candidate to potentially have negations or logic ops to handle the constraint
            if c_features['negations'] == 0 and c_features['logic_ops'] == 0:
                error += 2.0 # High penalty for ignoring negation context
        
        # 2. Conditional Logic
        if p_features['conditionals'] > 0:
            if c_features['conditionals'] == 0 and c_features['logic_ops'] == 0:
                error += 1.0

        # 3. Numeric Consistency
        num_score = self._check_numeric_consistency(prompt, candidate)
        if num_score == 0.0 and (self._extract_numbers(prompt) and any(k in prompt for k in ['greater', 'less', 'max', 'min', 'compare'])):
            error += 3.0 # High penalty for failing numeric reasoning
        elif num_score > 0:
            error -= 2.0 # Reward for correct numeric handling

        # 4. Length/Complexity Prior (Occam's razor)
        # Penalize extremely long rambling answers if prompt is short, unless logic demands it
        if len(candidate) > len(prompt) * 3 and p_features['complexity'] < 2:
            error += 0.5

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_norm = self._normalize(prompt)
        
        # Calculate base free energy for all candidates
        scores = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt_norm, self._normalize(cand))
            scores.append((cand, fe))
        
        # Sort by Free Energy (lower is better)
        scores.sort(key=lambda x: x[1])
        
        # Group by score to apply NCD tiebreaker only within ties
        # Since FE is float, we group by small epsilon
        final_ranking = []
        if not scores:
            return []
            
        current_group = [scores[0]]
        current_fe = scores[0][1]
        
        for i in range(1, len(scores)):
            cand, fe = scores[i]
            if abs(fe - current_fe) < 1e-6:
                current_group.append((cand, fe))
            else:
                # Process group
                if len(current_group) > 1:
                    # Apply NCD tiebreaker within group
                    current_group.sort(key=lambda x: self._ncd(prompt_norm, self._normalize(x[0])))
                for c, f in current_group:
                    # Convert Free Energy to a positive score (inverse)
                    # Base score 1.0, subtract normalized error
                    score_val = max(0.0, 1.0 - (f * 0.2)) 
                    final_ranking.append({"candidate": c, "score": score_val, "reasoning": "Fractal predictive coding analysis"})
                current_group = [(cand, fe)]
                current_fe = fe
        
        # Process last group
        if len(current_group) > 1:
            current_group.sort(key=lambda x: self._ncd(prompt_norm, self._normalize(x[0])))
        for c, f in current_group:
            score_val = max(0.0, 1.0 - (f * 0.2))
            final_ranking.append({"candidate": c, "score": score_val, "reasoning": "Fractal predictive coding analysis"})

        return final_ranking

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low free energy (low prediction error) = High confidence.
        """
        fe = self._compute_free_energy(self._normalize(prompt), self._normalize(answer))
        # Map free energy to 0-1. 
        # FE=0 -> 1.0, FE=5 -> 0.0 (approx)
        conf = max(0.0, min(1.0, 1.0 - (fe * 0.2)))
        return conf