import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Causal Analogical Evolutionary Search (CAES) Approximation.
    
    Mechanism:
    1. Structural Parsing (Causal Priors): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a 'causal skeleton'.
    2. Analogical Fitness: Scores candidates based on structural alignment with the 
       prompt's skeleton (e.g., if prompt has "not", candidate must handle negation).
    3. Evolutionary Selection: Candidates are ranked by structural validity first.
    4. Compression Tiebreaker: Uses NCD only when structural scores are identical.
    
    This mimics the CAES loop: Hypothesis (candidate) -> Intervention (structural test) -> Fitness.
    """

    def __init__(self):
        # Keywords defining logical structure
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'only if']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric signatures from text."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Logical counts
        has_neg = any(n in text_lower for n in self.negations)
        has_comp = any(c in text_lower for c in self.comparatives)
        has_cond = any(c in text_lower for c in self.conditionals)
        has_bool = any(b in text_lower for b in self.booleans)
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        
        return {
            'neg_count': int(has_neg),
            'comp_count': int(has_comp),
            'cond_count': int(has_cond),
            'bool_count': int(has_bool),
            'numbers': tuple(sorted(numbers)),
            'length': len(words)
        }

    def _structural_score(self, prompt_struct: dict, cand_struct: dict) -> float:
        """
        Computes fitness based on causal consistency.
        High score = candidate respects the logical constraints of the prompt.
        """
        score = 0.0
        
        # 1. Negation Consistency: If prompt negates, candidate should reflect it or 
        #    explicitly address it (simplified: presence alignment for short answers)
        if prompt_struct['neg_count'] > 0:
            # If prompt has negation, candidate gets penalty if it's a simple 'yes/no' 
            # without negation context, unless the prompt asks a question.
            # Heuristic: Reward if candidate also contains negation or is not a bare boolean
            if cand_struct['neg_count'] > 0:
                score += 2.0
            elif cand_struct['bool_count'] > 0 and cand_struct['neg_count'] == 0:
                score -= 1.0 # Potential trap
        else:
            if cand_struct['neg_count'] > 0 and cand_struct['bool_count'] > 0:
                 score -= 0.5 # Unwarranted negation

        # 2. Comparative/Numeric Consistency
        if prompt_struct['comp_count'] > 0 or len(prompt_struct['numbers']) > 0:
            if len(cand_struct['numbers']) > 0:
                # Check numeric logic if both have numbers
                if len(prompt_struct['numbers']) == len(cand_struct['numbers']):
                    # Simple transitivity check approximation
                    p_dir = 1 if prompt_struct['numbers'][-1] > prompt_struct['numbers'][0] else -1
                    c_dir = 1 if cand_struct['numbers'][-1] > cand_struct['numbers'][0] else -1
                    if p_dir == c_dir:
                        score += 3.0
            elif cand_struct['comp_count'] > 0:
                score += 1.5 # Acknowledges comparison without specific numbers

        # 3. Conditional Logic
        if prompt_struct['cond_count'] > 0:
            if cand_struct['cond_count'] > 0 or cand_struct['bool_count'] > 0:
                score += 1.0

        # 4. Length plausibility (Avoids trivial "Yes" to complex questions)
        if prompt_struct['length'] > 10 and cand_struct['length'] < 3:
            score -= 0.5
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD for tie-breaking (expensive op, do once)
        # We compare candidate to prompt to see relevance
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        
        for i, cand in enumerate(candidates):
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Structural/Causal Fitness
            struct_score = self._structural_score(prompt_struct, cand_struct)
            
            # Secondary Score: NCD (Inverted: lower distance is better, so subtract)
            # We scale NCD to be a minor tiebreaker relative to structural logic
            ncd_val = ncd_scores[i][1]
            
            # Final Score: Structural Dominance + NCD Tiebreaker
            # Structural score is integer-ish, NCD is 0-1. 
            # We prioritize structural integrity.
            final_score = struct_score - (ncd_val * 0.01)
            
            reasoning = f"Structural fit: {struct_score:.2f}, NCD: {ncd_val:.3f}"
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment strength.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the top score to 0-1 range heuristically
        # Max theoretical structural score approx 6.0, min approx -2.0
        raw_score = results[0]['score']
        
        # Map range [-2, 6] to [0, 1]
        # (x - min) / (max - min)
        min_s, max_s = -2.0, 6.0
        conf = (raw_score - min_s) / (max_s - min_s)
        return max(0.0, min(1.0, conf))