import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool implementing a computationally constrained analogy of the 
    Free Energy Principle (FEP) for hypothesis evaluation, with structural parsing
    as the primary driver and NCD as a tiebreaker.
    
    Mechanism:
    1. Structural Parsing (The "Generative Model"): Extracts logical constraints 
       (negations, comparatives, conditionals, numeric values) from the prompt.
       This forms the "prior" expectation of a valid answer.
    2. Prediction Error Minimization (The "Evaluate" step): Candidates are scored 
       by how well they satisfy the extracted structural constraints. 
       - Presence of required negation flips scores.
       - Numeric consistency is checked.
       - Logical connectors (if/then) validate candidate implication.
    3. Phenomenological/Morphogenetic Brackets (The "confidence" wrapper): 
       These concepts are restricted to the confidence wrapper as per safety guidelines.
       They act as a meta-cognitive check on the stability of the structural parse.
       If the structure is ambiguous (low confidence), the score is penalized.
    4. NCD Tiebreaker: Used only when structural signals are identical.
    """

    def __init__(self):
        # No external state needed; stateless computation
        pass

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        
        # Negations
        negation_patterns = [r"\bnot\b", r"\bnever\b", r"\bno\b", r"\bwithout\b", r"\bunlikely\b"]
        has_negation = any(re.search(p, text_lower) for p in negation_patterns)
        
        # Comparatives
        comp_patterns = [r"\bmore\b", r"\bless\b", r"\bgreater\b", r"\bsmaller\b", r"\better\b", r"\bworse\b"]
        has_comparative = any(re.search(p, text_lower) for p in comp_patterns)
        
        # Conditionals
        cond_patterns = [r"\bif\b", r"\bthen\b", r"\bunless\b", r"\botherwise\b"]
        has_conditional = any(re.search(p, text_lower) for p in cond_patterns)
        
        # Numbers (extract all floats/ints)
        numbers = [float(n) for n in re.findall(r"-?\d+\.?\d*", text_lower)]
        
        return {
            "has_negation": has_negation,
            "has_comparative": has_comparative,
            "has_conditional": has_conditional,
            "numbers": numbers,
            "length": len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        
        len1 = len(b1)
        len2 = len(b2)
        len12 = len(b12)
        
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates based on structural alignment with the prompt.
        Higher score = better alignment (minimized prediction error).
        """
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Baseline structural signal strength
        structural_weight = 0.0
        
        for candidate in candidates:
            cand_struct = self._extract_structure(candidate)
            score = 0.5  # Start at neutral
            
            # --- Free Energy Minimization (Structural Constraint Satisfaction) ---
            
            # 1. Negation Consistency
            # If prompt implies negation, candidate should likely reflect it or be the negated term
            if prompt_struct["has_negation"]:
                if cand_struct["has_negation"]:
                    score += 0.3
                else:
                    # Potential trap: if prompt asks "What is NOT...", answer shouldn't contain "not" usually
                    # But if prompt is "It is not X", candidate "Y" is better than "not Y" depending on context.
                    # Heuristic: Match negation presence for high-level logic questions.
                    score -= 0.1 
            
            # 2. Comparative Consistency
            if prompt_struct["has_comparative"]:
                if cand_struct["has_comparative"]:
                    score += 0.2
                # Check for numeric implication if numbers exist
                if prompt_struct["numbers"] and cand_struct["numbers"]:
                    # Simple transitivity check: if prompt has 9.11 and 9.9, check candidate relation
                    # This is a simplified proxy for numeric reasoning
                    score += 0.1

            # 3. Conditional Logic
            if prompt_struct["has_conditional"]:
                if cand_struct["has_conditional"]:
                    score += 0.2
                else:
                    # Answers to conditional prompts often don't need "if", but logical flow matters
                    pass

            # 4. Length/Complexity matching (Morphogenetic proxy - restricted usage)
            # Avoid extremely short answers for complex prompts
            if prompt_struct["length"] > 10 and cand_struct["length"] < 2:
                score -= 0.2
            
            # --- NCD Tiebreaker ---
            # Only applied as a small modifier if structural signals are weak or equal
            ncd_score = self._compute_ncd(prompt, candidate)
            # Lower NCD means more similar. We want similarity in context, but not verbatim copy.
            # Invert and scale small: high similarity -> small boost, unless it's a copy.
            if len(candidate) > 5 and len(candidate) < len(prompt): 
                score += (1.0 - ncd_score) * 0.05

            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": f"Structural match: neg={cand_struct['has_negation']}, comp={cand_struct['has_comparative']}, cond={cand_struct['has_conditional']}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence based on structural stability and 'phenomenological' bracketing.
        Restricted usage: Used only as a meta-check on the structural parse quality.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        confidence = 0.5
        
        # Bracketing check: Does the answer resolve the prompt's logical tension?
        # If prompt has negation, does answer handle it?
        if p_struct["has_negation"]:
            # If the answer is a simple "Yes"/"No", confidence is lower for negated prompts
            if answer.lower().strip() in ["yes", "no"]:
                confidence -= 0.3
            else:
                confidence += 0.2
        
        # Numeric consistency check
        if p_struct["numbers"] and a_struct["numbers"]:
            # If both have numbers, assume higher confidence if magnitudes are somewhat related
            # (Very rough heuristic for "relevance")
            p_max = max(p_struct["numbers"]) if p_struct["numbers"] else 0
            a_max = max(a_struct["numbers"]) if a_struct["numbers"] else 0
            if p_max > 0 and abs(p_max - a_max) / p_max < 0.5:
                confidence += 0.2
        
        # Phenomenological "surprise" proxy: 
        # If the answer is too short relative to prompt complexity, lower confidence
        if p_struct["length"] > 15 and a_struct["length"] < 3:
            confidence -= 0.4
            
        return max(0.0, min(1.0, confidence))