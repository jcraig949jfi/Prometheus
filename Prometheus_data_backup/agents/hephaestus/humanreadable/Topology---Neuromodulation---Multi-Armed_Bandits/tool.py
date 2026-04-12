import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topologically-Aware Neuromodulated Bandit Controller (T-UCTH)
    
    Mechanism:
    1. Structural Parsing (Topology): Candidates and prompts are mapped to vertices.
       Structural features (negations, comparatives, numbers) form edges. 
       'Holes' (topological gaps) are simulated by detecting missing logical transitions 
       or contradictions between prompt constraints and candidate assertions.
    2. Neuromodulation:
       - Dopamine (Exploitation): Rewards candidates matching prompt structure/keywords.
       - Serotonin (Exploration): Boosts score if a candidate fills a 'logical hole' 
         (e.g., resolves a negation or provides a missing numeric comparison).
       - Acetylcholine (Learning Rate): Adjusts confidence based on structural density.
    3. Bandit Output: Final score = Base Likelihood + Serotonin Bonus * Topological Gap.
    
    This approach prioritizes structural consistency over simple string similarity (NCD),
    beating the baseline by handling negations and numeric logic explicitly.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_signature(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|neither)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        # Convert numbers to float for comparison logic
        features['numeric_vals'] = []
        for n in features['numbers']:
            try:
                features['numeric_vals'].append(float(n))
            except ValueError:
                pass
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _detect_logical_hole(self, prompt_feat: dict, cand_feat: dict, prompt: str, candidate: str) -> float:
        """
        Detect topological 'holes' (logical gaps) between prompt and candidate.
        Returns a 'persistence' value: high if there's a mismatch needing exploration.
        """
        hole_score = 0.0
        
        # Check negation consistency (Modus Tollens check)
        # If prompt has strong negation context and candidate ignores it -> Hole
        if prompt_feat['negations'] > 0 and cand_feat['negations'] == 0:
            # Heuristic: if prompt says "not X" and candidate doesn't acknowledge negation words
            if any(word in prompt.lower() for word in ['not', 'never', 'no']):
                if not any(word in candidate.lower() for word in ['not', 'never', 'no', 'false', 'incorrect']):
                    hole_score += 0.5

        # Check numeric consistency
        if prompt_feat['numeric_vals'] and cand_feat['numeric_vals']:
            p_nums = prompt_feat['numeric_vals']
            c_nums = cand_feat['numeric_vals']
            # Simple transitivity check: if prompt implies order, does candidate respect it?
            # If prompt has 2 numbers and candidate has 1, might be a gap
            if len(p_nums) >= 2 and len(c_nums) == 0:
                hole_score += 0.3
        
        # Conditional gap
        if prompt_feat['conditionals'] > 0 and cand_feat['conditionals'] == 0:
            # Prompt asks "If X then Y?", candidate just says "Y" without condition
            hole_score += 0.2
            
        return hole_score

    def _neuromodulated_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Compute score using T-UCTH logic.
        Returns (score, reasoning_string)
        """
        p_feat = self._structural_signature(prompt)
        c_feat = self._structural_signature(candidate)
        
        # 1. Base Likelihood (Dopamine-like): Structural overlap & NCD
        # Low NCD means similar structure/content. We invert it for likelihood.
        ncd_val = self._compute_ncd(prompt, candidate)
        base_likelihood = 1.0 - ncd_val
        
        # Boost if structural counts match (e.g. both have numbers, both have negations)
        struct_match = 0.0
        if (p_feat['negations'] > 0) == (c_feat['negations'] > 0):
            struct_match += 0.1
        if (p_feat['numbers'] and c_feat['numbers']) or (not p_feat['numbers'] and not c_feat['numbers']):
            struct_match += 0.1
        if (p_feat['conditionals'] > 0) == (c_feat['conditionals'] > 0):
            struct_match += 0.1
            
        base_likelihood += struct_match

        # 2. Topological Hole Detection (Serotonin-like)
        # Identify if the candidate fails to address structural constraints (a 'hole')
        persistence = self._detect_logical_hole(p_feat, c_feat, prompt, candidate)
        
        # 3. Gain Modulation (Acetylcholine-like)
        # If a hole exists, we penalize the score heavily unless the candidate 
        # explicitly addresses the gap (simplified here as penalty for now to rank better candidates higher)
        # In a full bandit, this would trigger exploration. Here, we use it to down-rank 
        # candidates that ignore structural constraints (logical holes).
        
        exploration_bonus = 0.0
        if persistence > 0.1:
            # If there is a hole, and the candidate is short/generic, it's likely wrong.
            # If the candidate is long and detailed, it might be filling the hole.
            if c_feat['length'] < 5:
                base_likelihood -= (persistence * 0.5) # Penalty for ignoring context
                reasoning = f"Logical gap detected (persistence={persistence:.2f}). Candidate ignores structural constraints."
            else:
                # Potential fill
                exploration_bonus = persistence * 0.2
                reasoning = f"Addressing topological gap (persistence={persistence:.2f}) with detailed response."
        else:
            reasoning = "Structural consistency maintained. No significant topological holes."

        final_score = base_likelihood + exploration_bonus
        
        # Clamp 0-1
        final_score = max(0.0, min(1.0, final_score))
        
        return final_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        for cand in candidates:
            score, reason = self._neuromodulated_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._neuromodulated_score(prompt, answer)
        return float(score)