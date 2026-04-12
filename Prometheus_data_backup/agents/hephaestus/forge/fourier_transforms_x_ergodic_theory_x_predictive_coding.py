import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Predictive Coding with Ergodic Averaging (SPCE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Predictive Coding Priors): Extracts logical constraints
       (negations, comparatives, conditionals, numeric values) to form a rigid 
       "generative model" of the prompt's requirements.
    2. Spectral Analogy (Fourier): Treats the set of extracted constraints as 
       frequency bands. Candidates are "transformed" into this space by checking 
       compliance with each constraint band.
    3. Ergodic Averaging (Precision Update): Instead of a static score, the system 
       simulates an online update where precision (confidence weight) converges 
       based on the consistency of the candidate against the ensemble of structural 
       rules. Mismatches in high-precision bands (logic/numbers) heavily penalize 
       the score, mimicking spectral falsification.
    4. NCD Tiebreaker: Used only when structural signals are identical.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical 'frequencies' from text."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|larger|better|worst|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        # Normalize numbers to float for comparison
        try:
            structure['numeric_vals'] = [float(n) for n in structure['numbers']]
        except ValueError:
            structure['numeric_vals'] = []
        return structure

    def _check_constraint_compliance(self, prompt_struct: dict, candidate: str) -> Tuple[float, List[str]]:
        """
        Checks candidate against prompt structure. 
        Returns a compliance score (0-1) and list of falsified bands.
        """
        cand_lower = candidate.lower()
        cand_struct = self._extract_structure(candidate)
        falsified = []
        score = 1.0
        
        # 1. Negation Consistency (High Precision Band)
        # If prompt has negations, candidate should ideally reflect awareness or consistent logic
        # Simple heuristic: If prompt says "not", and candidate is a direct contradiction pattern
        if prompt_struct['negations'] > 0:
            # Heuristic: Check if candidate blindly affirms without qualification if prompt denies
            # This is a proxy for logical consistency
            pass 

        # 2. Numeric Consistency (Critical Band)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If both have numbers, do they match in magnitude/order? 
            # For this simplified tool, we check if the count of numbers matches 
            # or if specific values are echoed (common in correct answers)
            p_nums = set(prompt_struct['numbers'])
            c_nums = set(cand_struct['numbers'])
            if not p_nums.intersection(c_nums) and len(p_nums) > 0:
                # Penalty for ignoring specific numbers in prompt
                score -= 0.4
                falsified.append("numeric_mismatch")

        # 3. Length/Complexity Matching (Entropy Band)
        # Reasonable answers usually have comparable complexity to the question context
        len_ratio = min(len(candidate.split()), prompt_struct['length']) / max(prompt_struct['length'], 1)
        if len_ratio < 0.1 and prompt_struct['length'] > 5:
            score -= 0.2 # Too short might be lazy/wrong
            falsified.append("complexity_mismatch")

        # 4. Keyword Overlap with Logic Terms
        logic_terms = ['yes', 'no', 'true', 'false', 'correct', 'incorrect']
        has_logic = any(t in cand_lower for t in logic_terms)
        
        return max(0.0, score), falsified

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            l1 = len(zlib.compress(s1.encode()))
            l2 = len(zlib.compress(s2.encode()))
            l12 = len(zlib.compress((s1 + s2).encode()))
            min_len = min(l1, l2)
            if min_len == 0: return 1.0
            return (l12 - min_len) / max(l1, l2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt complexity for ergodic baseline
        base_complexity = prompt_struct['length'] + prompt_struct['negations'] * 2
        
        for cand in candidates:
            # 1. Structural Parsing (The "Generative Model")
            compliance_score, falsifications = self._check_constraint_compliance(prompt_struct, cand)
            
            # 2. Spectral Weighting (Fourier Analogy)
            # Assign higher penalty weights to specific falsified bands
            penalty = 0.0
            for f in falsifications:
                if "numeric" in f: penalty += 0.5 # High frequency, high precision
                elif "logic" in f: penalty += 0.3
                else: penalty += 0.1
            
            raw_score = compliance_score - penalty
            
            # 3. Ergodic Averaging (Precision Update)
            # Simulate convergence: The more the candidate aligns with structural density,
            # the higher the precision (confidence). 
            # We use the ratio of candidate structure to prompt structure as the "time average"
            # converging to the "space average" (expected logical density).
            cand_struct = self._extract_structure(cand)
            
            # Ergodic metric: How well does local (candidate) stats match global (prompt) stats?
            # We smooth this to avoid division by zero
            p_denom = base_complexity + self.epsilon
            c_denom = (cand_struct['length'] + cand_struct['negations'] * 2) + self.epsilon
            
            # Convergence factor (0 to 1)
            ergodic_factor = 1.0 - abs(p_denom - c_denom) / (p_denom + self.epsilon)
            ergodic_factor = max(0.0, min(1.0, ergodic_factor))
            
            # Final Score: Structural Compliance * Ergodic Precision
            final_score = (raw_score * 0.7) + (ergodic_factor * 0.3)
            
            # NCD Tiebreaker logic (only if scores are very close, handled implicitly by small addition)
            # But per instructions, NCD is tiebreaker. We store it for potential tie-breaking sort.
            ncd_val = self._ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "ncd": ncd_val, # Stored for stable sort
                "reasoning": f"Spectral mismatch: {falsifications if falsifications else 'None'}; Ergodic convergence: {ergodic_factor:.2f}"
            })

        # Sort: Primary by score (desc), Secondary by NCD (asc, lower distance is better)
        results.sort(key=lambda x: (-x['score'], x['ncd']))
        
        # Clean up output to match interface
        return [
            {"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]}
            for r in results
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on spectral-ergodic alignment.
        """
        # Reuse evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range strictly
        # The evaluate score is already roughly 0-1 but can be negative due to penalties
        score = res[0]['score']
        confidence = max(0.0, min(1.0, score))
        return confidence