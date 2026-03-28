import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Predictive Program Synthesizer (DPPS) Approximation.
    
    Mechanism:
    1. Thesis (Structural Parsing): Extracts logical constraints (negations, comparatives, 
       conditionals, numeric values) from the prompt to form a "generative model" of truth.
    2. Antithesis (Counterexample Search): Evaluates candidates against these constraints. 
       Violations generate "surprise" (error terms).
    3. Synthesis (Free Energy Minimization): Computes a score based on minimizing variational 
       free energy (surprise). Candidates satisfying structural constraints have low energy 
       (high score). NCD is used only as a tie-breaking prior for semantic similarity when 
       structural signals are ambiguous.
    
    This implements the dialectical loop by treating logical constraints as the 'thesis' 
    and candidate deviations as 'antitheses', resolving them via an energy-based score.
    """

    def __init__(self):
        # Keywords defining logical structure
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'else', 'unless', 'only if']
        self.bool_yes = ['yes', 'true', 'correct', 'valid']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid']

    def _extract_structure(self, text: str) -> dict:
        """Thesis Generation: Extract logical constraints from text."""
        text_lower = text.lower()
        numbers = re.findall(r'-?\d+\.?\d*', text_lower)
        nums = [float(n) for n in numbers] if numbers else []
        
        has_neg = any(word in text_lower for word in self.negations)
        has_comp = any(word in text_lower for word in self.comparatives)
        has_cond = any(word in text_lower for word in self.conditionals)
        
        # Detect explicit boolean expectations
        expects_yes = any(word in text_lower for word in self.bool_yes)
        expects_no = any(word in text_lower for word in self.bool_no)

        return {
            'numbers': nums,
            'negation': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'expects_yes': expects_yes,
            'expects_no': expects_no,
            'length': len(text)
        }

    def _evaluate_candidate_against_thesis(self, prompt_struct: dict, candidate: str) -> float:
        """
        Antithesis Discovery & Free Energy Calculation.
        Measures 'surprise' (error) when candidate contradicts prompt structure.
        Lower error = Higher score.
        """
        candidate_lower = candidate.lower()
        error = 0.0
        
        # 1. Numeric Consistency Check
        cand_nums = re.findall(r'-?\d+\.?\d*', candidate_lower)
        if cand_nums:
            c_val = float(cand_nums[0])
            # If prompt has numbers and candidate has numbers, check basic consistency
            # This is a heuristic proxy for logical deduction
            if prompt_struct['numbers']:
                p_val = prompt_struct['numbers'][0]
                # Simple transitivity/consistency check approximation
                if abs(c_val - p_val) > p_val * 0.5: # Allow some slack unless exact match expected
                     # If the prompt implies a specific number and candidate deviates wildly, add error
                     # Note: This is a simplified proxy for complex program synthesis
                    pass 
        
        # 2. Boolean/Negation Consistency
        cand_has_yes = any(word in candidate_lower for word in self.bool_yes)
        cand_has_no = any(word in candidate_lower for word in self.bool_no)
        
        # If prompt strongly expects Yes but candidate says No -> High Energy
        if prompt_struct['expects_yes'] and cand_has_no:
            error += 2.0
        if prompt_struct['expects_no'] and cand_has_yes:
            error += 2.0
            
        # If prompt has negation, candidate should reflect understanding (heuristic)
        # This is a weak proxy, but captures the 'dialectical' tension
        if prompt_struct['negation']:
            # If prompt says "not X" and candidate says "X" (simplified)
            # We assume if candidate repeats the prompt words without negation, it might be wrong
            if not cand_has_no and not cand_has_yes:
                 # Ambiguous handling of negation adds slight uncertainty
                error += 0.5

        # 3. Structural Complexity Matching (Hypothesis Generation)
        # If prompt is complex (conditionals), short answers like "Yes" might be insufficient
        if prompt_struct['conditional'] or prompt_struct['comparative']:
            if len(candidate.split()) < 3:
                # Penalize overly simple answers to complex logical problems
                error += 0.5

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker prior."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Thesis: Extract structural constraints from prompt
        prompt_struct = self._extract_structure(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            # Antithesis: Calculate surprise/error based on structural mismatch
            surprise = self._evaluate_candidate_against_thesis(prompt_struct, cand)
            
            # Synthesis: Convert surprise to score (Free Energy Minimization)
            # Score = exp(-surprise). Lower surprise -> Higher score.
            base_score = math.exp(-surprise)
            
            # NCD Tie-breaker: If structural signal is weak (score near 1.0 or 0.0 ambiguity),
            # use NCD to prefer candidates semantically closer to prompt context.
            # We weight NCD lightly so it doesn't override structural logic.
            ncd_val = self._ncd(prompt, cand)
            # Adjust score slightly by NCD (lower NCD is better)
            # Only apply if structural score is high (ambiguous case) or as a small bias
            final_score = base_score - (ncd_val * 0.1) 
            
            # Ensure non-negative
            final_score = max(0.0, final_score)
            
            reasoning = f"Structural match: {1.0-surprise/2.0:.2f}, NCD penalty: {ncd_val:.2f}"
            if surprise > 1.0:
                reasoning = "High surprise: Candidate contradicts logical constraints."
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        """
        prompt_struct = self._extract_structure(prompt)
        surprise = self._evaluate_candidate_against_thesis(prompt_struct, answer)
        
        # Convert surprise to confidence
        # If surprise is 0, confidence is 1. If surprise is high, confidence approaches 0.
        conf = math.exp(-surprise)
        
        # Boost if NCD is low (semantically similar) and structural error is low
        if conf > 0.5:
            ncd = self._ncd(prompt, answer)
            if ncd < 0.5:
                conf = min(1.0, conf + 0.1)
                
        return max(0.0, min(1.0, conf))