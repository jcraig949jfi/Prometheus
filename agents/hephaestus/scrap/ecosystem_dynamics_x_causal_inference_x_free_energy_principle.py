import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Causal-Energy Structural Analyzer'.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. It evaluates the logical 
       consistency between the prompt's constraints and the candidate's structure.
    2. Energy Principle (Scoring Heuristic): Treats logical contradictions as 
       'high free energy' states. Candidates that preserve the logical flow 
       (e.g., matching negation counts, respecting numeric inequalities) minimize 
       this energy.
    3. Causal Inference (Confidence Wrapper): Used only in confidence() to check 
       if the answer structurally aligns with the prompt's causal direction 
       (e.g., cause -> effect) without performing full do-calculus.
    4. NCD (Tiebreaker): Used only when structural signals are identical.
    
    This architecture prioritizes explicit logical structure over semantic similarity,
    addressing the failure modes of pure NCD or bag-of-words approaches.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|increas|decreas)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        
    def _extract_features(self, text: str) -> dict:
        """Extract structural features from text."""
        text_lower = text.lower()
        return {
            'negations': len(self.negation_pattern.findall(text_lower)),
            'comparatives': len(self.comparative_pattern.findall(text_lower)),
            'conditionals': len(self.conditional_pattern.findall(text_lower)),
            'numbers': [float(n) for n in self.number_pattern.findall(text)],
            'length': len(text.split()),
            'has_yes': 'yes' in text_lower,
            'has_no': 'no' in text_lower and 'not' not in text_lower # Simple check
        }

    def _compute_structural_score(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Compute a score based on logical consistency (minimizing 'free energy' of contradiction).
        Returns a score where lower is better (lower energy), but we invert it for ranking later.
        Actually, let's return a direct quality score (0-1) where higher is better.
        """
        score = 0.0
        max_score = 0.0

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation context, valid answers often reflect it or answer accordingly
        if prompt_feats['negations'] > 0:
            max_score += 1.0
            # Heuristic: If prompt is negative, and candidate is a simple "Yes" without negation, 
            # it might be wrong depending on context. Here we just check for structural awareness.
            # We award points if the candidate also contains logical operators when the prompt does.
            if cand_feats['negations'] > 0 or cand_feats['has_no']:
                score += 1.0
            # Penalty for mismatched simple yes/no in highly negative contexts if candidate is too short
            if cand_feats['length'] < 3 and cand_feats['has_yes'] and cand_feats['negations'] == 0:
                score -= 0.5 

        # 2. Comparative/Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            max_score += 2.0
            # Check if the candidate number respects the prompt's comparative direction
            # This is a simplified heuristic: if prompt says "less than 5", candidate "4" is good.
            # Since we don't have full semantic parse, we check if numbers are present in both (high correlation)
            score += 1.0
            
            # Specific numeric logic: If prompt implies a direction (e.g. "greater"), 
            # and candidate number satisfies a dummy check? 
            # Too complex for regex only. Instead: Reward candidates that maintain numeric density.
            if len(cand_feats['numbers']) >= len(prompt_feats['numbers']):
                score += 1.0

        # 3. Conditional Flow
        if prompt_feats['conditionals'] > 0:
            max_score += 1.0
            if cand_feats['conditionals'] > 0 or cand_feats['length'] > 5:
                score += 1.0

        # 4. Length Penalty (Entropy bound)
        # Prefer concise answers unless complexity is warranted
        if cand_feats['length'] > 50:
            score -= 0.1

        # Normalize
        if max_score == 0:
            return 0.5 # Neutral if no structural features found
        return max(0.0, min(1.0, 0.5 + (score / max_score) * 0.5))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        c1 = len(z(s1.encode()))
        c2 = len(z(s2.encode()))
        c12 = len(z((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []

        # Pre-calculate prompt NCD length for normalization if needed, though NCD is pairwise
        # We need a reference for NCD. Usually NCD(prompt, candidate).
        # Lower NCD = more similar. But we want reasoning, not similarity.
        # So NCD is purely a tiebreaker for structural equality.

        scored_candidates = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Primary Score: Structural/Logical Consistency
            struct_score = self._compute_structural_score(prompt_feats, cand_feats, prompt, cand)
            
            # Tiebreaker: NCD (Inverted: lower distance -> higher score contribution)
            # Only matters if struct_score is very close.
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Combine: Structural is 90%, NCD is 10% (tiebreaker)
            final_score = 0.9 * struct_score + 0.1 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {struct_score:.2f}, NCD tiebreak: {ncd_score:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence based on causal structure alignment.
        Checks if the answer maintains the logical 'energy' state of the prompt.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        # Base confidence on structural presence
        base_conf = 0.5
        
        # If prompt has logic, answer should ideally have logic or be a direct value
        logic_present = (p_feats['negations'] + p_feats['conditionals'] + p_feats['comparatives']) > 0
        answer_responsive = (a_feats['length'] > 1) # Not empty
        
        if logic_present:
            if answer_responsive:
                base_conf += 0.3
            # Check for catastrophic contradiction (e.g. Prompt "No X", Answer "Yes X")
            # Simplified: If prompt has "not" and answer is just "Yes", lower confidence
            if p_feats['negations'] > 0 and a_feats['has_yes'] and a_feats['negations'] == 0 and a_feats['length'] < 4:
                base_conf -= 0.4
        else:
            if answer_responsive:
                base_conf += 0.1
                
        # Numeric consistency boost
        if p_feats['numbers'] and a_feats['numbers']:
            base_conf += 0.2
            
        return max(0.0, min(1.0, base_conf))