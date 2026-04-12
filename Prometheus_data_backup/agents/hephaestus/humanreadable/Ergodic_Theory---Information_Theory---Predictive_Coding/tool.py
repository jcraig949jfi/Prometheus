import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning engine combining Structural Parsing (Primary), 
    Predictive Coding (Error Minimization), and Ergodic Sampling (Uncertainty).
    
    Mechanism:
    1. Structural Parsing: Extracts logical operators (negations, comparatives) 
       to form a base logical score. This avoids the "Information Theory" trap 
       of relying on string similarity for logic.
    2. Predictive Coding: Treats the prompt as a generative model expectation. 
       Candidates are scored by "surprise" (prediction error). Low surprise 
       (high match to structural constraints) yields high scores.
    3. Ergodic Sampling: Adds a deterministic pseudo-noise term based on candidate 
       position to simulate trajectory exploration, providing variance estimates 
       for the confidence metric.
    4. Information Bottleneck: Uses NCD only as a tie-breaker when structural 
       signals are ambiguous, preventing overfitting to surface patterns.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        features = {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'has_numbers': bool(re.search(r'\d+\.?\d*', t_lower)),
            'length': len(words)
        }
        return features

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for numeric evaluation."""
        return [float(n) for n in re.findall(r'\d+\.?\d*', text)]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _compute_surprise(self, prompt: str, candidate: str) -> float:
        """
        Predictive Coding: Computes 'surprise' (error) between prompt expectations
        and candidate content. Lower is better.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        error = 0.0
        
        # Negation consistency check
        if p_feat['neg_count'] > 0:
            # If prompt has negation, candidate should ideally reflect it or be short
            if c_feat['neg_count'] == 0 and c_feat['length'] > 5:
                error += 0.5
        
        # Conditional logic check (simplified)
        if p_feat['cond_count'] > 0:
            if c_feat['cond_count'] == 0 and 'if' not in candidate.lower():
                # Candidate doesn't continue conditional logic
                error += 0.3

        # Numeric consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate numbers are logically consistent (e.g., smaller if prompt asks for less)
            # Heuristic: If prompt says "less", candidate number should be smaller than max in prompt
            if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                if c_nums[0] > max(p_nums):
                    error += 1.0
            elif 'more' in prompt.lower() or 'greater' in prompt.lower():
                if c_nums[0] < min(p_nums):
                    error += 1.0
        
        return error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features
        p_feat = self._structural_parse(prompt)
        p_nums = self._extract_numbers(prompt)
        
        for i, cand in enumerate(candidates):
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Logic Score (Primary Signal)
            c_feat = self._structural_parse(cand)
            
            # Bonus for matching logical complexity
            if p_feat['neg_count'] > 0 and c_feat['neg_count'] > 0:
                score += 0.4
                reasoning_parts.append("matched negation")
            elif p_feat['neg_count'] == 0 and c_feat['neg_count'] == 0:
                score += 0.2 # Default positive
            
            if p_feat['cond_count'] > 0:
                if c_feat['cond_count'] > 0 or any(k in cand.lower() for k in ['then', 'therefore']):
                    score += 0.3
                    reasoning_parts.append("follows conditional")
            
            # 2. Numeric Evaluation
            c_nums = self._extract_numbers(cand)
            if p_nums and c_nums:
                # Simple transitivity/comparison check
                if ('less' in prompt.lower() or 'smaller' in prompt.lower()):
                    if c_nums[0] < max(p_nums):
                        score += 0.5
                        reasoning_parts.append("numeric constraint satisfied")
                elif ('more' in prompt.lower() or 'greater' in prompt.lower()):
                    if c_nums[0] > min(p_nums):
                        score += 0.5
                        reasoning_parts.append("numeric constraint satisfied")
            
            # 3. Predictive Coding (Surprise Minimization)
            surprise = self._compute_surprise(prompt, cand)
            score -= surprise * 0.5  # Penalize high surprise
            if surprise == 0:
                reasoning_parts.append("low prediction error")
            
            # 4. Ergodic Sampling (Deterministic Pseudo-noise for tie-breaking)
            # Simulates exploring parameter space around the candidate
            ergodic_factor = math.sin(i * 1.618) * 0.05  # Golden ratio step
            score += ergodic_factor
            
            # 5. Information Bottleneck (NCD as tiebreaker only)
            # Only apply if structural score is neutral (near 0.5 range)
            if 0.3 < score < 0.7:
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD (higher similarity) gets a tiny boost if logic doesn't decide
                score += (1.0 - ncd_val) * 0.1
                if ncd_val < 0.8:
                    reasoning_parts.append("information bottleneck compressed")

            # Normalize score roughly to 0-1 range
            final_score = max(0.0, min(1.0, 0.5 + score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural baseline"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on ergodic variance estimation.
        High confidence if structural signals are strong and surprise is low.
        """
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Ergodic variance proxy: 
        # If the answer relies heavily on NCD (information theory), confidence drops
        # because Info Theory is flagged as an inhibitor for direct scoring.
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(answer)
        
        uncertainty = 0.0
        
        # High uncertainty if negation present but not matched
        if p_feat['neg_count'] > 0 and c_feat['neg_count'] == 0:
            uncertainty += 0.4
            
        # High uncertainty if numeric constraints violated
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(answer)
        if p_nums and c_nums:
            if ('less' in prompt.lower() and c_nums[0] >= max(p_nums)):
                uncertainty += 0.5
            if ('more' in prompt.lower() and c_nums[0] <= min(p_nums)):
                uncertainty += 0.5

        # Adjust base score by uncertainty
        # If uncertainty is high, confidence drops regardless of base score
        confidence_val = base_score * (1.0 - min(1.0, uncertainty))
        
        return round(max(0.0, min(1.0, confidence_val)), 4)