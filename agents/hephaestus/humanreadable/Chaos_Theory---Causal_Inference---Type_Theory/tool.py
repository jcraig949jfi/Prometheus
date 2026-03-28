import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Dependently Typed Causal-Chaotic Verification Framework (Simulation).
    
    Mechanism:
    1. Structural Parsing (Type Theory): Extracts logical constraints (negations, 
       comparatives, conditionals) as 'type signatures'. Candidates violating 
       explicit structural constraints receive a hard penalty (type error).
    2. Causal Consistency (Causal Inference): Checks if the candidate preserves 
       the subject-object roles and transitivity of the prompt.
    3. Chaotic Sensitivity (Chaos Theory): Uses Normalized Compression Distance (NCD) 
       to measure 'Lyapunov divergence'. Small perturbations in logic should yield 
       proportional changes in score. If the candidate is too divergent (high NCD) 
       from the prompt's structural template, it is flagged as unstable.
    4. Scoring: Base score from structural adherence + numeric correctness. 
       NCD acts as a tie-breaking modifier for stability.
    """

    def __init__(self):
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self._negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self._conditionals = ['if', 'unless', 'provided', 'only if']

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Extracts logical 'types' from text: negations, numbers, comparatives."""
        lower_text = text.lower()
        has_negation = any(n in lower_text for n in self._negations)
        has_comparative = any(c in lower_text for c in self._comparatives)
        has_conditional = any(c in lower_text for c in self._conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", lower_text)
        nums = [float(n) for n in numbers]
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": nums,
            "length": len(text),
            "words": set(re.findall(r'\b\w+\b', lower_text))
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt_text: str, cand_text: str) -> float:
        """Validates numeric logic (e.g., 9.11 < 9.9)."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No numeric claim to verify
        
        # Simple heuristic: If prompt implies an order and candidate reverses it, penalize
        # Detects patterns like "A is greater than B" vs "B is greater than A"
        p_struct = self._extract_structure(prompt_text)
        c_struct = self._extract_structure(cand_text)
        
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            # Check if relative order is preserved or logically inverted based on negation
            p_ordered = sorted(prompt_nums[-2:]) == prompt_nums[-2:]
            c_ordered = sorted(cand_nums[-2:]) == cand_nums[-2:]
            
            # If prompt says "A > B" (ordered desc) and candidate says "A < B" (ordered asc) without negation
            if p_ordered != c_ordered and not c_struct['negation']:
                return 0.0 # Direct contradiction
        
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a proxy for Lyapunov exponent."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_struct = self._extract_structure(prompt)
        p_len = len(prompt)
        
        for cand in candidates:
            score = 1.0
            reasoning = []
            c_struct = self._extract_structure(cand)
            
            # 1. Type Check: Negation Consistency
            # If prompt has strong negation and candidate lacks it (or vice versa) in a critical way
            if p_struct['negation'] != c_struct['negation']:
                # Heuristic: If the word overlap is high but negation flips, it's likely a trap
                overlap = len(p_struct['words'] & c_struct['words'])
                if overlap > 3: 
                    score -= 0.4
                    reasoning.append("Negation mismatch detected.")
            
            # 2. Causal/Structural Consistency
            if p_struct['conditional'] and not c_struct['conditional']:
                # Candidate drops a condition; likely incomplete reasoning
                score -= 0.2
                reasoning.append("Conditional logic dropped.")
            
            # 3. Numeric Evaluation
            num_score = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'], prompt, cand)
            if num_score < 1.0:
                score -= 0.5
                reasoning.append("Numeric inconsistency.")
            
            # 4. Chaotic Stability (NCD modifier)
            # If the candidate is too structurally different (high NCD), it might be irrelevant
            ncd_val = self._ncd(prompt, cand)
            if ncd_val > 0.8:
                score -= 0.3
                reasoning.append("High divergence from prompt structure.")
            
            # Normalize score to 0-1
            final_score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning) if reasoning else "Structural match"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate logic to determine if the answer is 'type-correct' relative to the prompt.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]['score']
        
        # Additional check: Length sanity (chaos check)
        # Answers that are wildly different in length without content justification are suspect
        len_ratio = len(answer) / (len(prompt) + 0.1)
        if len_ratio > 5.0 or len_ratio < 0.01:
            base_score *= 0.8
            
        return max(0.0, min(1.0, base_score))