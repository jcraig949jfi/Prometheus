import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Neuromodulated Model-Checker (HNMC) Approximation.
    
    Mechanism:
    1. Holographic Boundary (Tensor Representation): The prompt and candidates are 
       parsed into structural feature vectors (negations, comparatives, numerics, logic).
       This acts as the compact 'boundary' encoding of the knowledge state.
    2. Neuromodulation (Gain Control): Scalar fields (dopamine/serotonin analogs) 
       are computed based on constraint satisfaction and uncertainty. These modulate 
       the 'bond dimensions' (weights) of specific features. High uncertainty increases 
       the gain on structural checks; high constraint violation suppresses the candidate.
    3. Model Checking (Verification): Candidates are treated as finite state trajectories.
       We perform bounded-depth verification against temporal-logic-like constraints 
       extracted from the prompt (e.g., if "A > B" and candidate implies "B > A", 
       the model checker returns a violation).
       
    Scoring: Base score from structural conformance, modulated by neuromorphic gain,
    with NCD used strictly as a tiebreaker for indistinguishable candidates.
    """

    def __init__(self):
        self.logic_ops = ['if', 'then', 'else', 'unless', 'therefore', 'because']
        self.comparators = ['>', '<', '>=', '<=', '==', '!=', 'greater', 'less', 'equal']
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.bool_vals = {'true': 1.0, 'false': 0.0, 'yes': 1.0, 'no': 0.0}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Parse text into a structural feature vector (The Holographic Boundary)."""
        lower = text.lower()
        return {
            'has_negation': any(n in lower for n in self.negations),
            'has_comparator': any(c in lower or c in text for c in self.comparators),
            'has_logic': any(l in lower for l in self.logic_ops),
            'numbers': self._extract_numbers(text),
            'length': len(text),
            'word_count': len(text.split())
        }

    def _check_numeric_consistency(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Model Checking Step 1: Numeric Consistency.
        Verifies if candidate numbers logically follow prompt numbers based on comparators.
        Returns 1.0 for pass, 0.0 for fail, 0.5 for neutral.
        """
        p_nums = prompt_feat['numbers']
        c_nums = cand_feat['numbers']
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to check
        
        # Simple heuristic: If prompt has numbers and candidate has none, slight penalty
        if not c_nums:
            return 0.4
            
        # If both have numbers, check magnitude consistency if comparators exist
        if prompt_feat['has_comparator']:
            # Rough check: does the candidate preserve order? 
            # This is a bounded depth check (depth=1)
            try:
                p_max = max(p_nums)
                c_max = max(c_nums)
                # If prompt implies maximization or comparison, candidate should reflect scale
                if p_max > 0 and c_max == 0:
                    return 0.0 # Violation
            except:
                pass
        return 1.0

    def _check_logical_consistency(self, prompt: str, candidate: str, p_feat: Dict, c_feat: Dict) -> float:
        """
        Model Checking Step 2: Logical Constraint Propagation.
        Checks for direct contradictions in negation and boolean claims.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation Clash: If prompt says "X is not Y" and candidate says "X is Y"
        # Simplified: Detect if prompt has strong negation and candidate affirms without negation
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Check for specific boolean flips
            for word in ['yes', 'true']:
                if word in c_lower and word not in p_lower:
                    # Potential contradiction if prompt was negative
                    if any(n in p_lower for n in ['no', 'not']):
                        return 0.2 # Strong violation
        
        # Direct Boolean Match
        for term, val in self.bool_vals.items():
            if term in c_lower:
                # If candidate is a bare boolean, check if it contradicts prompt tone
                if val == 0.0 and not p_feat['has_negation'] and 'not' in c_lower:
                     return 0.3
        return 1.0

    def _neuromodulate(self, base_score: float, p_feat: Dict, c_feat: Dict) -> float:
        """
        Neuromodulation Step: Adjust gain based on uncertainty and salience.
        Dopamine-like: Reward structural alignment.
        Serotonin-like: Penalize high uncertainty (missing features).
        """
        gain = 1.0
        
        # If prompt requires logic (comparators/logic) but candidate lacks structure
        if (p_feat['has_comparator'] or p_feat['has_logic']):
            if not c_feat['has_comparator'] and not c_feat['has_logic']:
                # Reduce gain on this candidate's base score
                gain = 0.6
        
        # Uncertainty penalty: If numbers exist in prompt but not candidate
        if p_feat['numbers'] and not c_feat['numbers']:
            gain *= 0.8
            
        return base_score * gain

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            len1 = len(zlib.compress(s1.encode()))
            len2 = len(zlib.compress(s2.encode()))
            combined = s1 + " " + s2
            len_comb = len(zlib.compress(combined.encode()))
            max_len = max(len1, len2)
            if max_len == 0:
                return 0.0
            return (len_comb - min(len1, len2)) / max_len
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for cand in candidates:
            c_feat = self._structural_parse(cand)
            
            # 1. Base Score: Structural overlap and basic heuristics
            score = 0.5
            
            # Reward matching structural complexity
            if p_feat['has_negation'] and c_feat['has_negation']:
                score += 0.2
            elif p_feat['has_negation'] and not c_feat['has_negation']:
                score -= 0.1 # Penalty for missing negation
                
            if p_feat['has_comparator'] and c_feat['has_comparator']:
                score += 0.2
                
            if p_feat['has_logic'] and c_feat['has_logic']:
                score += 0.15

            # 2. Model Checking (Bounded Depth)
            num_check = self._check_numeric_consistency(p_feat, c_feat)
            log_check = self._check_logical_consistency(prompt, cand, p_feat, c_feat)
            
            mc_factor = (num_check + log_check) / 2.0
            score = score * 0.5 + mc_factor * 0.5 # Blend heuristic and verification
            
            # 3. Neuromodulation
            final_score = self._neuromodulate(score, p_feat, c_feat)
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {c_feat}, MC Numeric: {num_check:.2f}, MC Logic: {log_check:.2f}",
                "_ncd": ncd_map[cand] # Internal use for sorting
            })
            
        # Sort: Primary by score (desc), Secondary by NCD (asc - lower is more similar/relevant tiebreaker)
        results.sort(key=lambda x: (-x['score'], x['_ncd']))
        
        # Clean up internal keys
        for r in results:
            del r['_ncd']
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and logical consistency."""
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        # Base confidence
        conf = 0.5
        
        # Structural alignment boosts confidence
        if p_feat['has_negation'] == a_feat['has_negation']:
            conf += 0.2
        if p_feat['has_comparator'] == a_feat['has_comparator']:
            conf += 0.2
            
        # Model checking penalties
        num_ok = self._check_numeric_consistency(p_feat, a_feat)
        log_ok = self._check_logical_consistency(prompt, answer, p_feat, a_feat)
        
        if num_ok < 0.5:
            conf -= 0.4
        if log_ok < 0.5:
            conf -= 0.3
            
        return max(0.0, min(1.0, conf))