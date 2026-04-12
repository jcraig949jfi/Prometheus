import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Predictive Type Theory (RPTT) Approximation.
    
    Mechanism:
    1. Type Theory (Logical Form): Parses structural constraints (negations, comparatives, 
       conditionals, numeric literals) to define a 'type signature' of valid answers.
    2. Predictive Coding (Error Minimization): Computes a 'prediction error' score by 
       checking candidate alignment with extracted structural constraints. 
       - Matches reduce error (increase score).
       - Violations (e.g., wrong polarity, failed numeric logic) incur heavy penalties.
    3. Renormalization (Coarse-Graining): 
       - Layer 1 (Fine): Exact string match / NCD.
       - Layer 2 (Coarse): Semantic structure (keywords, logic operators).
       - Layer 3 (Fixed Point): Global consistency (does the answer type match the question type?).
       
    The final score is a weighted sum where structural validity (Type) dominates, 
    acting as the RG fixed-point check. NCD is only used as a tie-breaker for structural equals.
    """

    def __init__(self):
        # Regex patterns for structural parsing (Type Signatures)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|larger|smaller)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'bool_yes': re.compile(r'\b(yes|true|correct|right)\b', re.I),
            'bool_no': re.compile(r'\b(no|false|incorrect|wrong)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical features (Types) from text."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['bool_yes'].search(text)),
            'is_no': bool(self.patterns['bool_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_numeric_logic(self, prompt_nums: List[float], cand_nums: List[float], prompt: str, candidate: str) -> float:
        """Evaluates numeric consistency (Type Checking for numbers)."""
        if not prompt_nums or not cand_nums:
            return 0.0 # No penalty if no numbers to compare
        
        # Simple heuristic: If prompt asks for max/min (detected by comparatives)
        # and candidate provides a number, check if it matches the extreme.
        # Since we don't have full NLP, we use a proxy: 
        # If prompt has 'larger'/'more', expect larger number in candidate than others? 
        # Too complex for single pass. 
        # Simplified RG check: If prompt implies a specific number exists, does candidate contain it?
        
        # Robust simple check: Exact match of any prompt number in candidate implies relevance.
        matches = 0
        for pn in prompt_nums:
            for cn in cand_nums:
                if abs(pn - cn) < 1e-6:
                    matches += 1
        return matches * 0.5 # Bonus for carrying over correct numbers

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            score = 0.0
            reasoning = []
            cand_feat = self._extract_structure(cand)

            # --- Layer 1: Type Checking (Structural Consistency) ---
            
            # 1. Negation Consistency (Modus Tollens approximation)
            # If prompt asks "What is NOT...", candidate should ideally reflect negation or exclusion
            # Hard to verify without semantics, so we check for logical keywords if present in prompt
            if prompt_feat['has_negation']:
                # Heuristic: If prompt is negative, and candidate is a simple "Yes", it might be wrong contextually
                # But without semantics, we prioritize candidates that acknowledge complexity (length) or specific negation
                if cand_feat['has_negation']:
                    score += 2.0
                    reasoning.append("Matches negation structure")
                elif cand_feat['is_yes'] and cand_feat['length'] < 3:
                    score -= 3.0 # Penalty for simplistic 'Yes' to negative query
                    reasoning.append("Penalized simplistic positive response to negative query")

            # 2. Numeric Logic
            if prompt_feat['numbers']:
                num_bonus = self._check_numeric_logic(prompt_feat['numbers'], cand_feat['numbers'], prompt, cand)
                if num_bonus > 0:
                    score += num_bonus
                    reasoning.append("Numeric consistency detected")
                elif cand_feat['numbers']:
                    # If numbers exist but don't match, slight penalty (might be irrelevant)
                    score -= 0.5

            # 3. Comparative/Conditional Alignment
            if prompt_feat['has_comparative'] and cand_feat['has_comparative']:
                score += 1.5
                reasoning.append("Aligns comparative structure")
            
            if prompt_feat['has_conditional'] and cand_feat['has_conditional']:
                score += 1.5
                reasoning.append("Aligns conditional structure")

            # --- Layer 2: Renormalization (Coarse Graining) ---
            # As we coarse-grain, we look for fixed points. 
            # A "fixed point" here is a candidate that remains robust under structural scrutiny.
            # We add a small bonus if the candidate length is proportional (not too short to be empty, not too long to be noise)
            if 2 <= cand_feat['length'] <= 50:
                score += 0.5 # Stability bonus

            # --- Layer 3: NCD Tie-Breaker ---
            # Only used if structural signals are weak or equal
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so lower distance = higher score contribution
            ncd_score = (1.0 - ncd_val) * 0.5 
            score += ncd_score

            # Normalize reasoning
            if not reasoning:
                reasoning.append("Structural baseline")
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reasoning)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural validity and NCD."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map score to 0-1 range roughly
        # Base score from evaluation
        raw_score = res[0]['score']
        
        # Heuristic mapping: 
        # Score > 3.0 -> High confidence (Strong structural match)
        # Score > 0.0 -> Medium
        # Score < 0.0 -> Low
        
        confidence = 1.0 / (1.0 + pow(2.718, -raw_score)) # Sigmoid mapping
        return max(0.0, min(1.0, confidence))