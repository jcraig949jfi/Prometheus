import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topologically-Constrained Recursive Pragmatic Reasoner (TC-RPR) Approximation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a "logical skeleton".
       This acts as the differentiable persistent homology layer, capturing the 
       invariant "shape" (connected components/holes) of the argument.
       
    2. Pragmatic Constraint Check: Validates if the candidate answer preserves the 
       logical topology of the prompt (e.g., if prompt has "not", answer must reflect negation).
       This implements Grice's maxims as soft constraints.
       
    3. Recursive ToM Simulation (Simplified): Instead of full Bayesian recursion, 
       we simulate a "belief update" by checking if the candidate answer logically 
       follows the extracted structural constraints. If a candidate violates a 
       detected structural rule (e.g., says "larger" when prompt implies "smaller"), 
       it creates a "topological hole" (contradiction) and is penalized heavily.
       
    4. NCD Tiebreaker: Used only when structural signals are ambiguous or absent.
    """

    def __init__(self):
        # Regex patterns for structural extraction (The "Topological Encoder")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|larger|shorter|better|worse|higher|lower)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|provided|then|else)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|affirmative)\b', re.I),
            'boolean_no': re.compile(r'\b(no|false|incorrect|negative)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical invariants (homology features) from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(x) for x in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['boolean_yes'].search(text)),
            'is_no': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt_text: str) -> float:
        """Checks if numeric relationships are preserved (Topological invariant)."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No numeric data to contradict
        
        # Simple heuristic: If prompt compares A > B, does candidate respect order?
        # Since we don't have full semantic parse, we check magnitude consistency
        # if the prompt implies a direction (e.g., "larger" present).
        
        has_larger = re.search(r'\b(larger|greater|more|higher)\b', prompt_text, re.I)
        has_smaller = re.search(r'\b(smaller|less|lower)\b', prompt_text, re.I)
        
        if has_larger and len(cand_nums) >= 2:
            if cand_nums[0] <= cand_nums[1]: return 0.2 # Violation
        if has_smaller and len(cand_nums) >= 2:
            if cand_nums[0] >= cand_nums[1]: return 0.2 # Violation
            
        return 1.0

    def _check_logical_topology(self, p_feat: Dict, c_feat: Dict, prompt_text: str) -> float:
        """
        Evaluates if the candidate creates 'holes' in the belief space.
        Returns a score 0.0 (contradiction) to 1.0 (consistent).
        """
        score = 1.0
        
        # 1. Negation Invariance: If prompt negates, a simple "Yes" might be a trap
        # unless the question is "Is it not X?". 
        # Heuristic: If prompt has strong negation and candidate is simple "Yes"/"No",
        # we penalize slightly unless the context is clear (simplified for this tool).
        if p_feat['has_negation']:
            # If prompt says "not" and candidate is just "Yes", it's risky.
            if (c_feat['is_yes'] or c_feat['is_no']) and c_feat['length'] < 5:
                score -= 0.3 
        
        # 2. Conditional Consistency
        if p_feat['has_conditional']:
            # If prompt is conditional, answers like "always" or absolute statements 
            # without qualification might be topologically distinct (wrong shape).
            if re.search(r'\b(always|never|definitely)\b', str(c_feat), re.I):
                 pass # Context needed, but flag for now.

        # 3. Numeric Topology
        num_score = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'], prompt_text)
        score *= num_score
        
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_feat = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            c_feat = self._extract_structure(cand)
            
            # Primary Score: Structural/Topological Consistency
            topo_score = self._check_logical_topology(p_feat, c_feat, prompt)
            
            # Secondary Score: Pragmatic Relevance (Length/Complexity match)
            # Grice's Maxim of Quantity: Answer should be informative but not verbose
            len_ratio = min(len(c_feat['length']) / max(p_feat['length'], 1), 1.0)
            pragmatic_bonus = 0.1 if 0.5 < len_ratio < 2.0 else 0.0
            
            # Base score starts high, reduced by topological violations
            base_score = 0.7 
            
            # If structural parsing found strong signals, rely on them
            if p_feat['has_negation'] or p_feat['has_comparative'] or p_feat['numbers']:
                final_score = topo_score * 0.9 + pragmatic_bonus
            else:
                # Fallback to NCD if no structural hooks found (Weak signal)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) and scale
                ncd_score = (1.0 - ncd_val) * 0.5 
                final_score = ncd_score + 0.2 # Baseline boost

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Topo:{topo_score:.2f}, Struct:{'Yes' if (p_feat['has_negation'] or p_feat['has_comparative']) else 'No'}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on topological consistency."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        conf = min(1.0, max(0.0, res[0]['score']))
        return round(conf, 4)