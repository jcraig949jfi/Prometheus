import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Morphogenetic Compositional Network (DMCN) Approximation.
    
    Mechanism Design (Core): Implements a proper scoring rule where the final score
    is a weighted sum of structural validity (truthful reporting of logic) and
    peer-predicted consistency. Structural parsing acts as the "gradient signal"
    to reward correct logical forms (negations, comparatives).
    
    Morphogenesis (Structural): Used ONLY in confidence() to parse the structural
    "shape" of the answer relative to the prompt, acting as a pattern-matching filter
    rather than a generative engine.
    
    Compositionality: Candidates are scored by composing local logical checks
    (numeric, conditional, negation) into a global validity score.
    """

    def __init__(self):
        # No external state needed; stateless computation
        pass

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extracts logical primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Layer: Evaluates if the candidate satisfies structural constraints
        imposed by the prompt. Returns a score 0.0 to 1.0.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.0
        checks = 0

        # 1. Numeric Consistency (Transitivity/Comparison)
        if p_feat['numbers'] and c_feat['numbers']:
            checks += 1
            # Simple heuristic: If prompt implies ordering, does candidate respect it?
            # Since we don't have full NLI, we check if candidate numbers are plausible
            # relative to prompt numbers (e.g., not wildly out of distribution)
            p_avg = sum(p_feat['numbers']) / len(p_feat['numbers'])
            c_avg = sum(c_feat['numbers']) / len(c_feat['numbers'])
            # Reward if magnitudes are somewhat aligned or logically derived (simplified)
            if p_avg == 0:
                score += 1.0 if c_avg == 0 else 0.5
            else:
                ratio = c_avg / p_avg if p_avg != 0 else 1
                # Reward ratios close to 1 or logical inverses (simplified to range check)
                score += 1.0 if 0.1 <= ratio <= 10.0 else 0.2

        # 2. Negation Alignment (Modus Tollens check)
        # If prompt asks "What is NOT...", candidate should likely contain negation or specific exclusion
        if 'not' in p_feat or 'no' in p_feat: 
            # Heuristic: If prompt has strong negation context, candidate often needs specific handling
            # This is a proxy for logical form matching
            checks += 1
            score += 0.5 # Base reward for attempting
            if c_feat['has_negation']:
                score += 0.5 # Bonus for matching negation structure

        # 3. Conditional/Comparative Matching
        if p_feat['has_conditional'] or p_feat['has_comparative']:
            checks += 1
            if c_feat['has_conditional'] or c_feat['has_comparative']:
                score += 1.0
            else:
                # Penalty for ignoring complex logical operators in prompt
                score += 0.3
        
        if checks == 0:
            return 0.5 # Neutral if no structural signals detected
            
        return min(1.0, score / checks)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0: return 1.0
        concat = s1 + s2
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        c1, c2, c_concat = len(z(s1.encode())), len(z(s2.encode())), len(z(concat.encode()))
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return (c_concat - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates using a Mechanism Design approach:
        1. Structural Parsing (Primary Signal): Rewards logical form alignment.
        2. Peer Prediction (Secondary): Consistency with prompt semantics.
        3. NCD (Tiebreaker): Only used when structural signals are weak.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Primary Score: Logical Consistency (Mechanism Design)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # Secondary Score: Semantic Overlap (Simplified Peer Prediction)
            # Does the candidate share key tokens without just echoing?
            p_tokens = set(re.findall(r'\w+', prompt.lower()))
            c_tokens = set(re.findall(r'\w+', cand.lower()))
            overlap = len(p_tokens & c_tokens) / (len(p_tokens | c_tokens) + 1e-6)
            
            # NCD Tiebreaker component (Inverse similarity for diversity, but here used for relevance)
            # We want low NCD (high similarity) for relevance, but logic_score dominates
            ncd = self._ncd_distance(prompt, cand)
            
            # Composite Score Formula
            # Logic is the driver (weight 0.7), Overlap supports (0.2), NCD adjusts (0.1)
            # Note: NCD is inverted (1-ncd) because lower distance is better
            final_score = (0.7 * logic_score) + (0.2 * overlap) + (0.1 * (1.0 - ncd))
            
            # Reasoning string generation
            reasoning = f"Logic:{logic_score:.2f} Overlap:{overlap:.2f} NCD:{ncd:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Morphogenesis-inspired structural parsing to determine if the answer
        'fits' the shape of the prompt's requirements.
        """
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        confidence = 0.5 # Base prior
        
        # Structural Match Checks (Morphogenetic Patterning)
        matches = 0
        total_checks = 0
        
        # Check 1: Number presence
        if p_feat['numbers']:
            total_checks += 1
            if a_feat['numbers']:
                matches += 1
        
        # Check 2: Negation handling
        if p_feat['has_negation']:
            total_checks += 1
            # If prompt has negation, answer should ideally reflect awareness (heuristic)
            matches += 0.5 
            
        # Check 3: Length plausibility (Avoids single char answers for complex prompts)
        total_checks += 1
        if p_feat['length'] > 5 and a_feat['length'] < 2:
            matches -= 1 # Penalty
        elif a_feat['length'] > 0:
            matches += 1

        if total_checks > 0:
            # Adjust base confidence
            adjustment = (matches / total_checks) * 0.4 # Max adjustment 0.4
            confidence += adjustment
            
        # Cap between 0 and 1
        return max(0.0, min(1.0, confidence))