import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Pragmatic Predictive Coding (FPPC) Tool.
    
    Mechanism:
    1. Core (Free Energy): Uses structural parsing to extract logical constraints 
       (negations, comparatives, conditionals). It calculates a 'prediction error' 
       by checking if candidates violate these hard constraints.
    2. Fractal Layer: Applies self-similar pattern matching. It checks for semantic 
       consistency across scales: exact substring matches (fine), token overlap (mid), 
       and compression-based similarity (coarse). This mimics iterated function systems.
    3. Pragmatic Layer: Instead of abstract truth, it scores based on 'utility'—defined 
       here as the candidate's ability to satisfy the maximum number of extracted 
       structural constraints with the least complexity (instrumentalism).
       
    This architecture prioritizes structural logic (Free Energy) while using 
    fractal similarity for tie-breaking and pragmatic utility for final ranking.
    """

    def __init__(self):
        # Structural patterns for logical extraction
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bunless\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', 
                                     r'\bsmaller\s+than\b', r'\bequal\s+to\b', r'>', r'<', r'=']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bonly\s+if\b']
        self.number_pattern = r'-?\d+\.?\d*'

    def _extract_structure(self, text: str) -> dict:
        """Extract logical constraints from text (Free Energy Core)."""
        text_lower = text.lower()
        return {
            'has_negation': bool(re.search('|'.join(self.negation_patterns), text_lower)),
            'has_comparative': bool(re.search('|'.join(self.comparative_patterns), text_lower)),
            'has_conditional': bool(re.search('|'.join(self.conditional_patterns), text_lower)),
            'numbers': [float(x) for x in re.findall(self.number_pattern, text)],
            'length': len(text.split())
        }

    def _compute_fractal_similarity(self, s1: str, s2: str) -> float:
        """
        Compute multi-scale similarity (Fractal Geometry).
        Scale 1: Exact inclusion (Fine)
        Scale 2: Token overlap (Mid)
        Scale 3: NCD (Coarse)
        """
        s1_low, s2_low = s1.lower(), s2.lower()
        
        # Scale 1: Exact match bonus
        scale_1 = 1.0 if s1_low in s2_low or s2_low in s1_low else 0.0
        
        # Scale 2: Token Jaccard (simplified)
        t1 = set(s1_low.split())
        t2 = set(s2_low.split())
        if not t1 or not t2:
            scale_2 = 0.0
        else:
            intersection = t1.intersection(t2)
            union = t1.union(t2)
            scale_2 = len(intersection) / len(union) if union else 0.0
            
        # Scale 3: NCD (Normalized Compression Distance)
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # We invert it to be a similarity score (1 - NCD)
        try:
            c1 = len(zlib.compress(s1_low.encode()))
            c2 = len(zlib.compress(s2_low.encode()))
            c12 = len(zlib.compress((s1_low + s2_low).encode()))
            min_c = min(c1, c2)
            max_c = max(c1, c2)
            ncd = (c12 - min_c) / max_c if max_c > 0 else 1.0
            scale_3 = 1.0 - max(0.0, min(1.0, ncd))
        except:
            scale_3 = 0.0
            
        # Weighted sum emulating hierarchical integration
        return 0.3 * scale_1 + 0.4 * scale_2 + 0.3 * scale_3

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Verify numeric consistency (Constraint Propagation)."""
        p_nums = [float(x) for x in re.findall(self.number_pattern, prompt)]
        c_nums = [float(x) for x in re.findall(self.number_pattern, candidate)]
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric conflict possible
            
        # Simple heuristic: If prompt has numbers and candidate has none, penalize
        if len(p_nums) > 0 and len(c_nums) == 0:
            # Check if candidate is a word-number (e.g., "five") - simplified check
            if not any(word in candidate.lower() for word in ['zero','one','two','three','four','five','six','seven','eight','nine','ten']):
                return 0.5
        
        # If both have numbers, do they match roughly? (Loose constraint)
        # This is a weak check to avoid over-penalizing explanatory text
        if abs(sum(p_nums) - sum(c_nums)) > (sum(p_nums) * 0.5 + 1):
            return 0.2
            
        return 1.0

    def _calculate_utility_score(self, prompt: str, candidate: str) -> float:
        """
        Calculate pragmatic utility: How well does the candidate satisfy 
        the structural constraints of the prompt? (Dewey's "what works")
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 1.0
        
        # Constraint 1: Negation consistency
        # If prompt emphasizes negation, candidate should likely reflect it or address it
        if p_struct['has_negation']:
            # If candidate is just "Yes" or "No", it might be ambiguous without context
            # But if prompt has negation and candidate ignores it completely (no overlap), slight penalty
            if self._compute_fractal_similarity(prompt, candidate) < 0.2:
                score -= 0.1

        # Constraint 2: Numeric logic
        score *= self._check_numeric_logic(prompt, candidate)
        
        # Constraint 3: Length utility (Instrumentalism)
        # Prefer concise answers that still maintain similarity
        if len(candidate.split()) > len(prompt.split()) * 2:
            score *= 0.9 # Penalize excessive verbosity
            
        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using FPPC architecture.
        1. Generate prediction error (structural mismatch).
        2. Apply fractal similarity across scales.
        3. Modulate by pragmatic utility.
        """
        results = []
        
        # Pre-calculate prompt structure for global context
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Free Energy: Prediction Error via Structural Parsing
            # High error if structural features in prompt are missing in candidate
            error_term = 0.0
            c_struct = self._extract_structure(cand)
            
            # If prompt has specific logic markers, candidate should ideally respond to them
            if p_struct['has_conditional'] and not c_struct['has_conditional']:
                # Not a hard fail, but increases uncertainty
                error_term += 0.1 
            
            # 2. Fractal Similarity (Multi-scale)
            fractal_score = self._compute_fractal_similarity(prompt, cand)
            
            # 3. Pragmatic Utility
            utility_score = self._calculate_utility_score(prompt, cand)
            
            # Combine: Score = (Fractal Similarity * Utility) - Error
            # Normalize to 0-1 range roughly
            raw_score = (fractal_score * 0.6 + utility_score * 0.4) - error_term
            
            # Boost for exact string matches in prompt (common in reasoning tests)
            if cand.strip().lower() in prompt.lower():
                raw_score += 0.2
                
            results.append({
                "candidate": cand,
                "score": float(max(0.0, min(1.0, raw_score))),
                "reasoning": f"Fractal:{fractal_score:.2f}, Utility:{utility_score:.2f}, Error:{error_term:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on structural and fractal alignment.
        Acts as the meta-cognitive monitor.
        """
        # Re-use evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # The score from evaluate is already a proxy for confidence
        # Add a specific check for "I don't know" or similar low-confidence markers
        if any(x in answer.lower() for x in ["don't know", "cannot determine", "insufficient info"]):
            # If the prompt actually asks for uncertainty, this is high confidence
            # Otherwise, it's low confidence in a definitive answer
            if "not" in prompt.lower() or "impossible" in prompt.lower():
                return res[0]['score']
            return 0.5 # Neutral
            
        return res[0]['score']