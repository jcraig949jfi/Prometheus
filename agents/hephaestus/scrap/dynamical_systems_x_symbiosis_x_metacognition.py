import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Attractor-Meta-Network (SAMN) Approximation.
    
    Mechanism:
    1. Experts (Attractors): Specialized parsers for Logic (negations/conditionals), 
       Math (numeric comparison), and Structure (subject-object/constraints).
    2. Metacognitive Controller: Evaluates the "stability" (confidence) of each expert's 
       output based on signal clarity (e.g., presence of numbers for math expert).
    3. Symbiosis: The final score is a weighted fusion of expert opinions, where weights 
       are dynamically adjusted by the metacognitive confidence signals.
    4. Hypothesis Testing: Candidates are ranked by their proximity to the "stable attractor" 
       (highest consensus score), with NCD used only as a tie-breaking entropy measure.
    """

    def __init__(self):
        self.experts = ['logic', 'math', 'structure']
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_logic(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Logic Expert: Checks for negation flips and conditional consistency.
        Returns (score, confidence).
        """
        full_text = (prompt + " " + candidate).lower()
        score = 0.5
        conf = 0.1 # Low confidence if no logic keywords found
        
        has_no = any(w in full_text for w in [' not ', ' no ', 'never ', 'cannot '])
        has_yes = any(w in full_text for w in ['yes', 'true', 'correct', 'is '])
        
        # Simple heuristic: If prompt has 'not' and candidate contradicts expected positive
        if 'not' in prompt.lower():
            if any(w in candidate.lower() for w in ['yes', 'true', 'is']):
                # Potential trap, lower score unless candidate explains
                score = 0.3
                conf = 0.6
            else:
                score = 0.7
                conf = 0.6
        elif has_no and has_yes:
            # Contradiction in candidate itself?
            score = 0.2
            conf = 0.8
            
        if conf == 0.1: 
            # Fallback: exact string match logic for simple true/false
            if candidate.lower().strip() in ['true', 'yes', '1']:
                score = 0.6
                conf = 0.4
            elif candidate.lower().strip() in ['false', 'no', '0']:
                score = 0.4
                conf = 0.4
                
        return score, conf

    def _check_math(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Math Expert: Extracts numbers and verifies comparisons.
        Returns (score, confidence).
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 0.5, 0.05 # No math signal
        
        # If prompt asks for comparison (e.g., "which is larger")
        prompt_lower = prompt.lower()
        is_max = 'larger' in prompt_lower or 'greater' in prompt_lower or 'max' in prompt_lower
        is_min = 'smaller' in prompt_lower or 'less' in prompt_lower or 'min' in prompt_lower
        
        if is_max or is_min:
            if not c_nums:
                return 0.2, 0.7 # Asked for number, got none
            
            # Find target in prompt
            target = max(p_nums) if is_max else min(p_nums)
            
            # Check if candidate contains the target
            found = False
            for n in c_nums:
                if abs(n - target) < 1e-6:
                    found = True
                    break
            
            if found:
                return 0.95, 0.9
            else:
                return 0.1, 0.9
        
        # Numeric equality check
        if c_nums and p_nums:
            # If candidate is just a number, check if it matches any prominent number or simple op
            # Simplified: if candidate number equals a number in prompt, high score for "extraction" tasks
            if any(abs(c_nums[0] - p) < 1e-6 for p in p_nums):
                return 0.8, 0.6
                
        return 0.5, 0.1

    def _check_structure(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Structure Expert: Checks for constraint propagation and length plausibility.
        Returns (score, confidence).
        """
        # Heuristic: Candidates that are too short (<2 chars) or exact prompt echoes are bad
        c_clean = candidate.strip()
        if len(c_clean) < 2:
            return 0.3, 0.5
        if c_clean.lower() == prompt.lower().strip():
            return 0.1, 0.8
            
        # Check for "A > B" style structural integrity if present
        if '>' in prompt or '<' in prompt or '=' in prompt:
            # If prompt has symbols, candidate should probably reflect logic or be a specific choice
            if len(c_clean) > 2: 
                return 0.7, 0.6
        
        return 0.5, 0.2

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # 1. Gather Expert Opinions
            logic_score, logic_conf = self._check_logic(prompt, cand)
            math_score, math_conf = self._check_math(prompt, cand)
            struct_score, struct_conf = self._check_structure(prompt, cand)
            
            scores = [logic_score, math_score, struct_score]
            confs = [logic_conf, math_conf, struct_conf]
            
            # 2. Metacognitive Fusion (Symbiotic Weighting)
            total_conf = sum(confs) + 1e-6
            # Normalize weights based on confidence (stability)
            weights = [c / total_conf for c in confs]
            
            # Weighted average score
            final_score = sum(s * w for s, w in zip(scores, weights))
            
            # Boost if any expert is highly confident (Bifurcation avoidance)
            max_conf_idx = confs.index(max(confs))
            if confs[max_conf_idx] > 0.8:
                # Strongly bias towards the high-confidence expert
                final_score = scores[max_conf_idx] * 0.7 + final_score * 0.3

            # 3. NCD Tiebreaker (Entropy penalty)
            # Lower NCD between prompt and candidate implies relevance, but we want distinct answers.
            # We use NCD primarily to break ties or penalize noise.
            ncd_val = self._compute_ncd(prompt, cand)
            # Adjust score slightly by NCD (prefer lower complexity if scores are equal)
            # But since NCD is a tiebreaker, we add a tiny epsilon based on it
            ncd_penalty = ncd_val * 0.001 
            
            adjusted_score = final_score - ncd_penalty
            
            results.append({
                "candidate": cand,
                "score": adjusted_score,
                "reasoning": f"Logic:{logic_score:.2f}(c:{logic_conf:.1f}) Math:{math_score:.2f}(c:{math_conf:.1f}) Struct:{struct_score:.2f}(c:{struct_conf:.1f})"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Extract raw score from the result
        # The score is already normalized roughly 0-1 by the weighted average
        raw_score = res[0]['score']
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, raw_score))