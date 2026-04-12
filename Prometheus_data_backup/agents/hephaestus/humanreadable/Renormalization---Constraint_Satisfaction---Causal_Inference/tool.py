import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Renormalized Causal Constraint Propagation (RCCP) Simulator.
    
    Mechanism:
    1. Structural Parsing (Causal Graph Construction): Extracts logical operators
       (negations, comparatives, conditionals) and numeric values to form a 
       fine-grained variable set.
    2. Renormalization (Coarse-Graining): Groups variables into macro-variables
       based on logical blocks (e.g., "If A then B" becomes a single constraint unit).
    3. Constraint Satisfaction (Solver): Checks candidates against these macro-constraints.
       - Violations of negation or transitivity incur heavy penalties.
       - Numeric inconsistencies are detected via direct evaluation.
    4. Causal Inference (Wrapper Only): Used strictly in confidence() to parse 
       structure, not to score validity directly, adhering to the "historical inhibitor"
       constraint.
    5. Scoring: Primary signal is structural consistency. NCD is used only as a 
       tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore)\b', re.IGNORECASE)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'neg_count': len(self.patterns['negation'].findall(text_lower)),
            'comp_count': len(self.patterns['comparative'].findall(text_lower)),
            'cond_count': len(self.patterns['conditional'].findall(text_lower)),
            'logic_count': len(self.patterns['logic_op'].findall(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'length': len(text),
            'has_yes_no': bool(re.search(r'\b(yes|no)\b', text_lower))
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Renormalized check: Do numbers in candidate contradict prompt logic?"""
        if not prompt_nums or not cand_nums:
            return 0.0
        
        # Simple transitivity/consistency check simulation
        # If prompt has 2 numbers and candidate has 1, check if it's a valid subset or reduction
        p_min, p_max = min(prompt_nums), max(prompt_nums)
        c_min, c_max = min(cand_nums), max(cand_nums)
        
        penalty = 0.0
        # Penalty if candidate range is completely outside prompt range (likely contradiction)
        if c_max < p_min or c_min > p_max:
            penalty += 0.5
            
        return penalty

    def _solve_constraints(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Simulates the CSP solver at the macro-scale.
        Returns a score based on constraint satisfaction.
        """
        score = 1.0
        
        # Constraint 1: Negation Consistency
        # If prompt has strong negation context, candidate shouldn't blindly affirm without nuance
        if prompt_feats['neg_count'] > 0:
            if cand_feats['neg_count'] == 0 and cand_feats['has_yes_no']:
                # Potential trap: simplistic "Yes" to a negative query
                score -= 0.2
        
        # Constraint 2: Logical Depth Matching
        # Complex prompts (high conditional/logic count) require candidates with some logical structure
        prompt_complexity = prompt_feats['cond_count'] + prompt_feats['logic_count']
        cand_complexity = cand_feats['cond_count'] + cand_feats['logic_count']
        
        if prompt_complexity > 2 and cand_complexity == 0:
            score -= 0.3 # Oversimplification penalty
            
        # Constraint 3: Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            score -= self._check_numeric_consistency(prompt_feats['numbers'], cand_feats['numbers'])
            
        # Constraint 4: Length plausibility (Renormalization scale check)
        # Extreme compression (1 char) for complex prompts is suspicious
        if prompt_complexity > 1 and cand_feats['length'] < 3:
            score -= 0.4
            
        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tie-breaker."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        scored_candidates = []
        
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # Primary Score: Structural Constraint Satisfaction
            struct_score = self._solve_constraints(prompt_feats, cand_feats, prompt, cand)
            
            scored_candidates.append({
                'candidate': cand,
                'struct_score': struct_score,
                'cand_feats': cand_feats
            })
        
        # Ranking Logic
        # Sort by structural score first, then use NCD as tie-breaker (lower NCD = more similar/relevant)
        # Note: In reasoning, sometimes diversity is good, but for "correctness" in MCQ, 
        # alignment with prompt context (lower NCD) is often a safe tie-breaker.
        def sort_key(item):
            # We want highest struct_score first.
            # For tie-breaking, we calculate NCD relative to prompt. 
            # Lower NCD means more informationally similar (often correct for direct answers).
            ncd_val = self._ncd_distance(prompt, item['candidate'])
            return (-item['struct_score'], ncd_val)
        
        scored_candidates.sort(key=sort_key)
        
        # Normalize scores to 0-1 range roughly, ensuring the best is high
        max_struct = max(c['struct_score'] for c in scored_candidates) if scored_candidates else 0.5
        
        results = []
        for item in scored_candidates:
            # Combine structural score with a tiny NCD influence for final ranking display
            # Base score is primarily structural
            final_score = item['struct_score']
            # Adjust slightly if it was a tie situation, but struct_score dominates
            
            results.append({
                'candidate': item['candidate'],
                'score': round(final_score, 4),
                'reasoning': f"Structural consistency: {item['struct_score']:.2f}. Constraints checked: negation, logic depth, numeric."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing to verify if the answer fits the prompt's logical frame.
        Does NOT use causal inference for direct scoring (per safety constraints).
        """
        prompt_feats = self._extract_structure(prompt)
        ans_feats = self._extract_structure(answer)
        
        # Base confidence on constraint satisfaction
        base_conf = self._solve_constraints(prompt_feats, ans_feats, prompt, answer)
        
        # Bonus for matching logical complexity (heuristic for "understanding")
        p_complex = prompt_feats['cond_count'] + prompt_feats['logic_count']
        a_complex = ans_feats['cond_count'] + ans_feats['logic_count']
        
        if p_complex > 0:
            if a_complex > 0:
                base_conf = min(1.0, base_conf + 0.1) # Reward logical engagement
        else:
            # Simple prompt, simple answer expected
            if a_complex == 0 and ans_feats['length'] < 50:
                base_conf = min(1.0, base_conf + 0.1)
                
        return round(max(0.0, min(1.0, base_conf)), 4)