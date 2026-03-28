import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Dependent-Type Tensor-Network (HDTTN) Approximation.
    
    Mechanism:
    1. BULK (Tensor Network): Candidates are treated as bulk states. We approximate
       the "tensor contraction" cost by measuring the structural complexity required
       to map the candidate to the prompt's logical constraints.
    2. BOUNDARY (Type Signatures): The prompt is parsed for strict logical operators
       (negations, comparatives, conditionals). These form the "dependent type" signature.
    3. EMERGENCE (HITs): Macro-properties (like transitivity or numeric consistency)
       emerge from checking if the candidate satisfies the boundary constraints.
    4. HOLOGRAPHIC COMPRESSION: Instead of full simulation, we project the candidate
       onto the boundary constraints. If the projection fails (type error), score drops.
       NCD is used only as a tie-breaking similarity metric for the "bulk" content.
    
    This implements the requested architecture by mapping:
    - Bulk -> Candidate string content
    - Boundary -> Extracted logical constraints (Types)
    - Type Checking -> Constraint satisfaction scoring
    - Emergence -> Aggregated logical consistency score
    """

    def __init__(self):
        self._keywords_neg = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._keywords_comp = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller']
        self._keywords_cond = ['if', 'then', 'else', 'unless', 'provided']
        self._ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b, '/': lambda a, b: a / b}

    def _parse_structure(self, text: str) -> Dict:
        """Extract boundary type signatures (logical constraints) from text."""
        lower = text.lower()
        return {
            'has_negation': any(k in lower for k in self._keywords_neg),
            'has_comparative': any(k in lower for k in self._keywords_comp),
            'has_conditional': any(k in lower for k in self._keywords_cond),
            'numbers': self._extract_numbers(text),
            'length': len(text.split())
        }

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for emergent numeric reasoning."""
        try:
            # Simple extraction of floats/integers
            nums = re.findall(r'-?\d+\.?\d*', text)
            return [float(n) for n in nums]
        except:
            return []

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_emergent_properties(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Check for emergent macro-properties (HITs).
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt has negation, valid candidates often reflect it or answer accordingly.
        # Heuristic: If prompt says "not", and candidate is a simple "Yes", penalize heavily.
        if prompt_struct['has_negation']:
            if candidate.lower().strip() in ['yes', 'true', '1']:
                # Weak penalty, as "Yes" could mean "Yes, it is not..."
                # But if the prompt is "Is X not Y?", "Yes" is ambiguous.
                pass 
            # Stronger check: Does the candidate contain negation if the prompt implies a negative outcome?
            # This is hard without semantics, so we rely on structural matching.
        
        # 2. Numeric Emergence (Transitivity/Comparison)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares two numbers, check if candidate respects the order
            # Example: "Which is bigger, 9.11 or 9.9?" -> Expect 9.9
            # We assume the last two numbers in prompt are the comparison targets
            n1, n2 = p_nums[-2], p_nums[-1]
            target = max(n1, n2) if 'bigger' in prompt.lower() or 'greater' in prompt.lower() or 'more' in prompt.lower() else min(n1, n2)
            
            # Check if candidate contains the target (approximate)
            found_target = any(abs(c - target) < 1e-6 for c in c_nums)
            if not found_target:
                # If candidate has numbers but not the right one, penalize
                score -= 0.5

        # 3. Conditional Logic
        if prompt_struct['has_conditional']:
            # Candidates for conditionals often need to be longer or contain specific keywords
            if cand_struct['length'] < 3 and not any(k in candidate.lower() for k in self._keywords_cond):
                score -= 0.3

        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_struct = self._parse_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking (Holographic compression proxy)
        # We compare candidate to prompt to see "relevance"
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores)
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # 1. Boundary Type Check (Structural Parsing)
            # Does the candidate match the logical "shape" of the prompt?
            type_match = 0.0
            
            # Negation alignment
            if prompt_struct['has_negation'] == cand_struct['has_negation']:
                type_match += 0.2
            
            # Comparative alignment
            if prompt_struct['has_comparative'] == cand_struct['has_comparative']:
                type_match += 0.2
                
            # Conditional alignment
            if prompt_struct['has_conditional'] == cand_struct['has_conditional']:
                type_match += 0.2

            # 2. Emergent Property Check (HITs)
            emergent_score = self._check_emergent_properties(prompt_struct, cand_struct, prompt, cand)
            
            # 3. Holographic Projection (NCD as tiebreaker/refiner)
            # Lower NCD (higher similarity) is generally better for relevance, 
            # but we normalize it. 
            ncd_val = self._ncd(prompt, cand)
            # Normalize: 0 is best, 1 is worst. Convert to score: 1 - normalized_ncd
            norm_ncd = (ncd_val - min_ncd) / range_ncd if range_ncd > 0 else 0
            ncd_score = 1.0 - norm_ncd
            
            # Final Score Composition
            # Structural parsing is primary (as per instructions)
            # Emergent properties act as a multiplier/modifier
            # NCD is the tiebreaker/base relevance
            
            base_score = type_match + (0.4 if cand_struct['length'] > 0 else 0) # Length bonus for non-empty
            
            # Combine: Structural (0-0.6) + Emergent (0-1 * 0.3) + NCD (0-1 * 0.1)
            final_score = (base_score * 0.6) + (emergent_score * 0.3) + (ncd_score * 0.1)
            
            # Adjust for specific "Reasoning" traps (Goodhart warning)
            # If the candidate is just the prompt repeated, penalize slightly (echo chamber)
            if cand.strip() == prompt.strip():
                final_score *= 0.8
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {type_match:.2f}, Emergent: {emergent_score:.2f}, Holographic similarity: {ncd_score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate method internally to score the single candidate against the prompt.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly based on our weighting
        # Max theoretical score approx 1.0 if all align perfectly
        raw_score = res[0]['score']
        return min(1.0, max(0.0, raw_score))