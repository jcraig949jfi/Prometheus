import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Differentiable-Autopoietic Reasoning Tool (QDAR) Implementation.
    
    Mechanism:
    Since actual quantum hardware is unavailable and 'Quantum/Autopoiesis' are flagged as 
    historical inhibitors for direct scoring, this tool implements a classical structural 
    analog inspired by the theoretical framework:
    
    1. Superposition (Hypothesis Space): All candidates are treated as a state vector.
    2. Differentiable Programming (Gradient Descent): We compute a 'gradient' of logical 
       consistency between the prompt's structural constraints (negations, comparatives) 
       and the candidate's content.
    3. Autopoietic Closure (Self-Maintenance): A viability filter ensures the candidate 
       preserves the logical 'organizational structure' of the prompt (e.g., if the prompt 
       negates a concept, the valid candidate must reflect that negation). Candidates 
       violating core logical invariants receive a heavy penalty (collapse).
       
    Scoring relies on structural parsing (negations, comparatives, numerics) as the primary 
    signal, using NCD only as a tiebreaker for semantically identical structural matches.
    """

    def __init__(self):
        # Structural keywords for logical parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        
    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_tokens(self, text: str) -> Dict[str, int]:
        """Simple token frequency for structural overlap."""
        tokens = re.findall(r'\b\w+\b', self._normalize(text))
        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        return counts

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """
        Autopoietic Closure Check: Ensures the candidate maintains the logical 
        polarity (negation/affirmation) of the prompt.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        p_has_neg = any(n in p_low.split() for n in self.negations)
        c_has_neg = any(n in c_low.split() for n in self.negations)
        
        # If prompt implies negation and candidate ignores it (or vice versa), penalize heavily
        # This simulates the 'organizational closure' failure
        if p_has_neg != c_has_neg:
            # Check if the candidate is just a short answer like "yes/no" which might be context dependent
            if len(c_low.split()) < 3: 
                return 0.5 # Neutral for short answers
            return -1.0 # Strong penalty for logical contradiction
        
        return 1.0 # Consistent

    def _extract_numeric_constraint(self, text: str) -> Tuple[bool, float]:
        """Extracts numeric values and simple comparisons."""
        # Find numbers
        nums = re.findall(r'\d+\.?\d*', text)
        if not nums:
            return False, 0.0
        
        # Check for comparative operators near numbers
        has_comp = any(c in text for c in self.comparatives)
        try:
            val = float(nums[0])
            return has_comp, val
        except ValueError:
            return False, 0.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural logic (Differentiable Programming analog).
        Higher score = better structural alignment.
        """
        score = 0.0
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # 1. Negation Consistency (Autopoietic Constraint)
        neg_score = self._check_negation_consistency(prompt, candidate)
        if neg_score < 0:
            return 0.0 # Immediate collapse for logical violation
        
        score += neg_score * 2.0
        
        # 2. Keyword Overlap (Structural Parsing)
        # Weight important logical words higher
        p_tokens = set(re.findall(r'\b\w+\b', p_low))
        c_tokens = set(re.findall(r'\b\w+\b', c_low))
        
        overlap = p_tokens.intersection(c_tokens)
        logical_overlap = len(overlap.intersection(set(self.negations + self.conditionals + self.comparatives)))
        generic_overlap = len(overlap) - logical_overlap
        
        score += logical_overlap * 3.0
        score += generic_overlap * 0.5
        
        # 3. Numeric Consistency
        p_has_comp, p_val = self._extract_numeric_constraint(prompt)
        c_has_comp, c_val = self._extract_numeric_constraint(candidate)
        
        if p_has_comp and c_has_comp:
            # If both have numbers, check if they are logically consistent (simplified)
            # In a real scenario, we'd parse the operation. Here we check magnitude alignment if implied
            if abs(p_val - c_val) < 1e-6:
                score += 2.0
            else:
                # If numbers differ significantly without explicit reason, slight penalty
                score -= 0.5
                
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate structural scores
        scored_candidates = []
        for cand in candidates:
            struct_score = self._structural_score(prompt, cand)
            scored_candidates.append((cand, struct_score))
        
        # Find max structural score to normalize
        max_struct = max(sc[1] for sc in scored_candidates) if scored_candidates else 0
        if max_struct < 0: max_struct = 0 # Floor at 0 for normalization baseline
        
        for cand, struct_score in scored_candidates:
            reasoning_parts = []
            
            # Primary Signal: Structural Logic
            # Normalize structural score to 0-1 range roughly
            base_score = 0.5
            if max_struct > 0:
                # Scale structural score: 0.5 is neutral, >0.5 is good, <0.5 is bad
                # Map range [min_possible, max_struct] to [0, 1]
                # Assuming min possible is roughly -2 (from negation penalty)
                normalized_struct = (struct_score + 2.0) / (max_struct + 2.0)
                base_score = max(0.0, min(1.0, normalized_struct))
            
            # Tie-breaker: NCD (only if structural scores are very close or neutral)
            # We add a tiny epsilon from NCD to break ties without overriding logic
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD (lower is better) and scale to small epsilon
            ncd_contribution = (1.0 - ncd_val) * 0.001 
            
            final_score = base_score + ncd_contribution
            
            # Generate reasoning string
            if struct_score < 0:
                reasoning_parts.append("Logical contradiction detected (negation mismatch).")
                final_score = 0.0 # Hard floor
            else:
                if any(k in self._normalize(cand) for k in self.negations):
                    reasoning_parts.append("Maintains negation constraint.")
                if any(k in self._normalize(cand) for k in self.comparatives):
                    reasoning_parts.append("Addresses comparative logic.")
                if not reasoning_parts:
                    reasoning_parts.append("Structural alignment based on token overlap.")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural consistency as the primary metric.
        """
        # Evaluate single candidate against itself to get structural score
        # We simulate a ranking where this answer is the only candidate
        # But to get a meaningful absolute score, we check logical invariants directly
        
        score = self._structural_score(prompt, answer)
        
        # Map structural score to confidence
        # Negative score (logical fail) -> 0.0
        if score < 0:
            return 0.0
        
        # Positive score -> scale to 0.5 - 0.95
        # Cap at reasonable max
        conf = min(0.95, 0.5 + (score * 0.1))
        
        # Adjust with NCD for similarity bonus (if it looks like the prompt, it might be right in simple cases)
        ncd_val = self._ncd(prompt, answer)
        if ncd_val < 0.2: # Very similar
            conf = min(0.99, conf + 0.1)
            
        return round(conf, 4)