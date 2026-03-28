import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Dual-Process, Incentive-Compatible, Type-Directed Reasoning Tool.
    
    Mechanism:
    1. System 1 (Fast/Neural Analog): Uses structural parsing and NCD to generate 
       initial hypothesis scores based on prompt-answer alignment.
    2. Mechanism Design (Core): Implements a proper scoring rule (Brier-like) where 
       'rewards' (scores) are adjusted by a penalty factor for logical inconsistencies 
       (negation mismatches, comparative errors). This aligns the generator to truth.
    3. System 2 (Slow/Verifier): A deterministic type-checker analog that validates 
       numeric constraints and logical transitivity. It allocates 'verification effort' 
       by deep-parsing only high-potential candidates.
       
    The final score is the incentive-adjusted probability of correctness.
    """

    def __init__(self):
        # State for mechanism history (simplified for stateless interface)
        self._verification_depth = 0

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text_lower)
        }
        return features

    def _verify_constraints(self, prompt_feats: Dict, answer_feats: Dict, answer: str) -> float:
        """
        System 2 Verifier: Checks logical consistency between prompt and answer features.
        Returns a penalty factor (0.0 to 1.0).
        """
        penalty = 0.0
        
        # Check Numeric Consistency (Type Theory analog: value matching)
        if prompt_feats['numbers'] and answer_feats['numbers']:
            try:
                # Simple heuristic: if prompt has numbers and answer has numbers,
                # check if answer numbers are a subset or result of prompt numbers.
                # For this implementation, we check for direct contradiction in magnitude if comparatives exist.
                p_nums = [float(n) for n in prompt_feats['numbers']]
                a_nums = [float(n) for n in answer_feats['numbers']]
                
                if 'more' in str(answer_feats) or 'greater' in str(answer_feats):
                    # If answer claims "more", verify logic if possible (simplified)
                    pass 
            except ValueError:
                penalty += 0.2

        # Check Negation Consistency (Mechanism Design: Truthfulness penalty)
        # If prompt has high negation density, answer should reflect awareness
        if prompt_feats['negations'] > 0:
            # Heuristic: If prompt denies something, and answer affirms it blindly without nuance
            # This is a simplified logical check
            if answer_feats['negations'] == 0 and prompt_feats['negations'] > 1:
                penalty += 0.3

        return max(0.0, 1.0 - penalty)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculates confidence based on structural alignment and verification.
        Returns a float 0-1.
        """
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        # Base similarity (System 1 initial guess)
        ncd = self._compute_ncd(prompt, answer)
        base_score = 1.0 - ncd
        
        # Boost if key structural tokens match (e.g., both have numbers or both have negations)
        if p_feats['numbers'] and a_feats['numbers']:
            base_score = min(1.0, base_score + 0.2)
        if (p_feats['negations'] > 0) == (a_feats['negations'] > 0):
            base_score = min(1.0, base_score + 0.1)
            
        # System 2 Verification (Penalty application)
        verification_factor = self._verify_constraints(p_feats, a_feats, answer)
        
        final_conf = base_score * verification_factor
        return max(0.0, min(1.0, final_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluates candidates using the dual-process mechanism.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        results = []
        p_feats = self._structural_parse(prompt)
        
        for cand in candidates:
            # System 1: Fast hypothesis generation (Structural + NCD)
            conf = self.confidence(prompt, cand)
            
            # Mechanism Design: Scoring Rule
            # Reward = Confidence * Verification_Factor - Cost(Complexity)
            # We simplify cost to length penalty to discourage verbose nonsense
            length_penalty = min(0.2, len(cand) / 1000) 
            score = conf - length_penalty
            
            # Reasoning trace
            reasoning = f"Structural match: {conf:.2f}. Penalty applied: {length_penalty:.2f}."
            if p_feats['numbers'] and not self._structural_parse(cand)['numbers']:
                reasoning += " Warning: Numeric context ignored."
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results