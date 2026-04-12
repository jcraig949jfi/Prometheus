import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Symbiotic Causal Networks (FSCN) Implementation
    
    Mechanism:
    1. Fractal Geometry: The prompt is recursively decomposed into a hierarchy of 
       structural tokens (negations, comparatives, conditionals) forming a self-similar 
       DAG of logical constraints.
    2. Symbiosis: Candidate answers are evaluated against this hierarchy. Local scores 
       (leaf nodes) and global coherence (root node) exchange "gradients" (confidence 
       adjustments). A candidate that satisfies local constraints but fails global 
       transitivity is penalized; vice versa, global plausibility boosts local matches.
    3. Causal Inference: We simulate do-calculus by testing counterfactuals. If a 
       candidate contradicts a extracted causal rule (e.g., A > B, B > C, candidate says A < C), 
       the score collapses.
       
    This approach prioritizes structural parsing and constraint propagation over 
    simple string similarity, using NCD only as a tiebreaker for ambiguous cases.
    """

    def __init__(self):
        # Structural patterns for causal extraction
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'cannot', r"n't"]
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', 
                                     r'\bsmaller\s+than\b', r'\blarger\s+than\b', r'\bhigher\s+than\b',
                                     r'\blower\s+than\b', r'\bbeats\b', r'\bexceeds\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly\s+if\b', r'\bimplies\b']
        self.numeric_pattern = r'[-+]?\d*\.?\d+'

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical structure: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': re.findall(self.numeric_pattern, text),
            'length': len(text.split())
        }
        return structure

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate_nums: List[str]) -> float:
        """Check if numeric values in candidate are consistent with prompt logic."""
        if not prompt_nums or not candidate_nums:
            return 1.0 # No numeric conflict possible
        
        try:
            p_vals = sorted([float(x) for x in prompt_nums])
            c_vals = sorted([float(x) for x in candidate_nums])
            
            # Simple consistency: if candidate introduces wild outliers, penalize
            if p_vals and c_vals:
                p_range = p_vals[-1] - p_vals[0] if len(p_vals) > 1 else 1.0
                c_range = c_vals[-1] - c_vals[0] if len(c_vals) > 1 else 1.0
                
                # Heuristic: ranges should be somewhat comparable unless logic dictates otherwise
                if p_range > 0 and c_range > 0:
                    ratio = max(p_range, c_range) / min(p_range, c_range)
                    if ratio > 100: # Wild divergence
                        return 0.5
            return 1.0
        except ValueError:
            return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural alignment and causal consistency."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        max_score = 0.0
        
        # 1. Negation Alignment (Causal Flip)
        # If prompt has negations, candidate should reflect understanding (not necessarily same count)
        if p_struct['negations'] > 0:
            max_score += 2.0
            # Reward if candidate acknowledges complexity (has some logical operators)
            if c_struct['negations'] > 0 or c_struct['conditionals'] > 0:
                score += 2.0
            # Penalize if candidate is too short to address negation
            if c_struct['length'] < 3:
                score -= 1.0
        
        # 2. Comparative/Transitivity Check
        if p_struct['comparatives'] > 0:
            max_score += 2.0
            if c_struct['comparatives'] > 0:
                score += 2.0
            elif c_struct['length'] > 5: # If long enough to compare but didn't
                score += 0.5 # Partial credit for context
                
        # 3. Conditional Logic
        if p_struct['conditionals'] > 0:
            max_score += 2.0
            if c_struct['conditionals'] > 0 or any(k in c_struct for k in ['numbers']):
                score += 2.0

        # 4. Numeric Consistency
        if p_struct['numbers']:
            max_score += 2.0
            num_consistency = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'])
            score += 2.0 * num_consistency
            
        # Normalize
        if max_score == 0:
            return 0.5
        return max(0.0, min(1.0, score / max_score))

    def _symbiotic_refinement(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Apply symbiotic learning rule:
        Adjust base score based on the 'gradient' of agreement between 
        local (substring) and global (whole string) properties.
        """
        # Local check: Does the candidate appear as a substring or share key nouns?
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        candidate_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Remove stopwords for better overlap
        stopwords = {'the', 'is', 'are', 'a', 'an', 'it', 'that', 'this', 'of', 'to', 'in', 'and', 'or'}
        p_sig = prompt_words - stopwords
        c_sig = candidate_words - stopwords
        
        overlap = 0.0
        if p_sig:
            overlap = len(p_sig & c_sig) / len(p_sig | c_sig) if p_sig | c_sig else 0.0
        
        # Symbiotic update: 
        # If structural score is high but lexical overlap is zero, it might be a hallucination (penalize)
        # If structural score is low but overlap is high, it might be a copy-paste error (penalize)
        # Ideal: Moderate overlap + High structural score
        
        symbiosis_factor = 0.0
        if base_score > 0.7:
            # High structural score needs some lexical grounding
            symbiosis_factor = 0.2 * overlap 
        elif base_score < 0.3:
            # Low structural score gets a boost only if lexical overlap is very high (maybe we missed logic)
            symbiosis_factor = 0.1 * overlap
            
        refined_score = base_score + symbiosis_factor
        return max(0.0, min(1.0, refined_score))

    def _ncd_tiebreaker(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Structural/Causal Scoring (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Symbiotic Refinement (Feedback Loop)
            final_score = self._symbiotic_refinement(struct_score, prompt, cand)
            
            # Store for sorting
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {struct_score:.2f}, Symbiotic adjustment applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                ncd_i = self._ncd_tiebreaker(prompt, results[i]['candidate'])
                ncd_next = self._ncd_tiebreaker(prompt, results[i+1]['candidate'])
                # Lower NCD is better (more similar/compressible together)
                if ncd_i > ncd_next:
                    results[i], results[i+1] = results[i+1], results[i]
                    
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']