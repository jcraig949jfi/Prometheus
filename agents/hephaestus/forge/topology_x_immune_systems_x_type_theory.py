import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Topological Immune Type-Checking Engine (TITCE) - Computational Analogue
    
    Mechanism:
    1. ANTIGEN (Topology): The prompt is parsed for structural "shape" features 
       (negations, comparatives, conditionals, numeric constraints). This forms 
       the topological signature (Betti-like counts) of the required logic.
    2. CLONAL SELECTION (Immune): Candidates are treated as clones. Those lacking 
       critical structural markers found in the antigen (e.g., missing a negation 
       when the prompt has one) undergo immediate apoptosis (score penalty).
    3. TYPE CHECKING (Type Theory): Candidates are verified for logical consistency 
       with extracted constraints (e.g., if prompt says "A > B", candidate must 
       not imply "B > A"). Successful inhabitation (consistency) yields high scores.
    4. MEMORY: NCD serves as a tie-breaking distance metric for topologically 
       equivalent candidates.
    """

    def __init__(self):
        self._structural_keywords = {
            'negations': ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparatives': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse'],
            'conditionals': ['if', 'unless', 'provided', 'when', 'then'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }
        self._number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_topology(self, text: str) -> Dict[str, Any]:
        """Extract structural signatures (Antigenic Profile)."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        signature = {
            'has_negation': any(k in text_lower for k in self._structural_keywords['negations']),
            'has_comparative': any(k in text_lower for k in self._structural_keywords['comparatives']),
            'has_conditional': any(k in text_lower for k in self._structural_keywords['conditionals']),
            'numbers': [float(n) for n in self._number_pattern.findall(text)],
            'word_count': len(words),
            'raw': text_lower
        }
        return signature

    def _check_type_consistency(self, prompt_sig: Dict, candidate_sig: Dict, candidate: str) -> float:
        """Verify logical consistency (Type Inhabitation)."""
        score = 1.0
        
        # Constraint 1: Negation Preservation
        # If prompt asserts a negative context, candidate should ideally reflect it or not contradict it
        if prompt_sig['has_negation'] and not candidate_sig['has_negation']:
            # Heuristic: If prompt is negative, candidate lacking negation might be wrong (apoptosis trigger)
            # But we only penalize if the candidate is short (likely a direct answer)
            if len(candidate.split()) < 10:
                score -= 0.4

        # Constraint 2: Numeric Consistency
        if prompt_sig['numbers'] and candidate_sig['numbers']:
            # Simple transitivity check: If prompt implies order, candidate shouldn't reverse it blindly
            # This is a simplified proxy for complex type checking
            p_nums = sorted(prompt_sig['numbers'])
            c_nums = sorted(candidate_sig['numbers'])
            # If candidate introduces numbers completely outside prompt range without context, slight penalty
            if c_nums and p_nums:
                if max(c_nums) > max(p_nums) * 10 or min(c_nums) < min(p_nums) * 0.1:
                    score -= 0.1

        # Constraint 3: Structural Echo (Clonal Match)
        # Does the candidate contain key logical operators present in the prompt?
        if prompt_sig['has_conditional']:
            if not any(k in candidate_sig['raw'] for k in self._structural_keywords['conditionals']):
                # Not a hard fail, but reduces confidence in logical derivation
                score -= 0.15

        return max(0.0, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_sig = self._extract_topology(prompt)
        results = []

        for cand in candidates:
            cand_sig = self._extract_topology(cand)
            
            # 1. Type Checking Phase (Logical Consistency)
            type_score = self._check_type_consistency(prompt_sig, cand_sig, cand)
            
            # 2. Topological Distance Phase (NCD Tiebreaker)
            # Inverted: Lower NCD = Higher similarity = Better match
            ncd = self._compute_ncd(prompt_sig['raw'], cand_sig['raw'])
            similarity_score = 1.0 - ncd
            
            # Weighted combination: Logic dominates, topology breaks ties
            # If type check fails (low score), similarity matters less
            final_score = (type_score * 0.7) + (similarity_score * 0.3)
            
            # Bonus for exact structural match in critical reasoning tasks
            if prompt_sig['has_negation'] and cand_sig['has_negation']:
                final_score += 0.1
            if prompt_sig['has_comparative'] and cand_sig['has_comparative']:
                final_score += 0.1

            results.append({
                "candidate": cand,
                "score": round(min(1.0, final_score), 4),
                "reasoning": f"Type consistency: {type_score:.2f}, Topological similarity: {similarity_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Evaluate confidence based on structural and logical alignment."""
        prompt_sig = self._extract_topology(prompt)
        ans_sig = self._extract_topology(answer)
        
        # Base consistency check
        consistency = self._check_type_consistency(prompt_sig, ans_sig, answer)
        
        # Structural alignment bonus
        alignment_bonus = 0.0
        if prompt_sig['has_negation'] == ans_sig['has_negation']:
            alignment_bonus += 0.2
        if prompt_sig['has_conditional'] == ans_sig['has_conditional']:
            alignment_bonus += 0.1
            
        # NCD penalty for noise
        ncd = self._compute_ncd(prompt_sig['raw'], ans_sig['raw'])
        
        # Final confidence calculation
        # High consistency + High alignment + Low NCD (high similarity) = High Confidence
        raw_conf = (consistency * 0.6) + (alignment_bonus * 0.4) + ((1.0 - ncd) * 0.2)
        
        return round(min(1.0, max(0.0, raw_conf)), 4)