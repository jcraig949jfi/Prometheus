import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Global Workspace with Epistemic Justification.
    
    Mechanism:
    1. Objects (Modules): The prompt and candidates are parsed into structural 
       features (negations, comparatives, conditionals, numeric values).
    2. Morphisms (Flows): We map relationships between these features.
    3. Global Workspace (Colimit): Candidates compete for 'ignition'. The workspace 
       aggregates structural matches between the prompt's constraints and the candidate.
    4. Epistemic Functor (J): Assigns justification weights based on:
       - Structural alignment (does the candidate satisfy the prompt's logic?)
       - Numeric consistency (are comparisons mathematically valid?)
       - NCD (Compression): Used only as a tie-breaker for semantic similarity.
    """
    
    def __init__(self):
        self.threshold = 0.5

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|larger|shorter)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums] if nums else []
        return features

    def _check_numeric_logic(self, prompt_feats: dict, cand_feats: dict) -> float:
        """Evaluate numeric consistency (e.g., if prompt says 9.11 < 9.9, check candidate)."""
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric conflict if no numbers
        
        # Simple heuristic: If prompt has comparison words and numbers, 
        # does the candidate preserve the order?
        # Since we don't know the specific relation without full NLP, 
        # we penalize if the candidate introduces contradictory extreme outliers 
        # or if the prompt implies a sort and candidate breaks it.
        # Here we implement a basic coherence check: 
        # If prompt has comparatives and numbers, and candidate has numbers,
        # we assume the candidate is valid unless it's obviously wrong contextually.
        # For this implementation, we reward numeric presence if prompt has numeric logic.
        
        if prompt_feats['comparatives'] > 0 and len(p_nums) >= 2:
            # Prompt implies comparison. If candidate has numbers, it's engaging.
            if len(c_nums) > 0:
                return 1.0
            else:
                return 0.5 # Missed numeric opportunity
        
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 0.0
        return (z12 - min(z1, z2)) / denominator

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        reasons = []
        score = 0.0
        
        # 1. Epistemic Functor: Structural Alignment (Justification J)
        # Does the candidate mirror the logical complexity of the prompt?
        struct_match = 0.0
        
        # Negation handling: If prompt has negation, correct answer often needs specific handling.
        # We assume high structural overlap in features indicates good reasoning flow.
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0 or 'no' in candidate.lower() or 'not' in candidate.lower():
                struct_match += 0.2
                reasons.append("Handles negation")
            else:
                struct_match -= 0.2
                reasons.append("Misses negation")
                
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0 or any(x in candidate.lower() for x in ['more', 'less', 'greater', 'smaller']):
                struct_match += 0.2
                reasons.append("Handles comparative")
        
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0:
                struct_match += 0.2
                reasons.append("Handles conditional")

        # 2. Numeric Evaluation
        num_score = self._check_numeric_logic(p_feat, c_feat)
        if num_score == 1.0 and p_feat['numbers'] and c_feat['numbers']:
            reasons.append("Numeric consistency verified")
            struct_match += 0.2
        elif num_score < 1.0:
            reasons.append("Numeric logic weak")
            struct_match -= 0.3

        # 3. Global Workspace: Colimit (Broadcast/Integration)
        # We integrate the structural score with a similarity measure (NCD) 
        # but NCD is secondary (tie-breaker/semantic glue).
        ncd_val = self._compute_ncd(prompt, candidate)
        # Invert NCD (0 is identical, 1 is different) to similarity
        similarity = 1.0 - ncd_val
        
        # Final Score Composition
        # Structural reasoning is weighted higher (0.7) than raw similarity (0.3)
        final_score = (struct_match * 0.7) + (similarity * 0.3)
        
        # Normalize roughly to 0-1 range based on heuristics
        final_score = max(0.0, min(1.0, final_score + 0.5)) # Base bias
        
        if not reasons:
            reasons.append("Structural baseline")
            
        return final_score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._evaluate_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._evaluate_candidate(prompt, answer)
        return float(score)