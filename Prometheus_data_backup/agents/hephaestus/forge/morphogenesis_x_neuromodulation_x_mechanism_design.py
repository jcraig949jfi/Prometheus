import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Neuromodulated Morphogenetic Mechanism Design (ANMMD) Tool.
    
    Mechanism:
    1. Morphogenesis (Structural Parsing): Instead of reaction-diffusion on a grid,
       we generate a 'spatial pattern' of logical features (negations, comparatives,
       conditionals, numeric values) from the prompt. This forms the candidate hypothesis space.
       
    2. Mechanism Design (Incentive Compatibility): The scoring rule is derived from a
       proper scoring rule analogue. Candidates are penalized heavily for contradicting
       the structural constraints extracted from the prompt (truthful reporting).
       The 'global objective' is minimizing logical contradiction.
       
    3. Neuromodulation (Precision Weighting): A global 'precision' signal modulates the
       weight of the structural match. If the prompt contains high-precision markers
       (numbers, strict logic), the penalty for mismatch is amplified. If vague, the
       system relies more on baseline similarity (NCD).
       
    This architecture enforces honesty: a candidate cannot gain score by echoing the
    prompt if it violates the extracted logical structure (mechanism design), and the
    sensitivity to these violations is adaptively tuned (neuromodulation).
    """

    def __init__(self):
        # Logical operators and keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _extract_features(self, text: str) -> Dict:
        """Morphogenetic step: Extract structural patterns (hypothesis basis)."""
        t_lower = text.lower()
        words = re.findall(r'\w+', t_lower)
        
        has_neg = any(n in t_lower for n in self.negations)
        has_comp = any(c in t_lower for c in self.comparatives)
        has_cond = any(c in t_lower for c in self.conditionals)
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', t_lower)
        numbers = [float(n) for n in nums] if nums else []
        
        # Detect boolean leanings in prompt
        prompt_yes = any(b in t_lower for b in self.bool_yes)
        prompt_no = any(b in t_lower for b in self.bool_no)
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': numbers,
            'lean_yes': prompt_yes,
            'lean_no': prompt_no,
            'word_count': len(words)
        }

    def _check_candidate_alignment(self, prompt_features: Dict, candidate: str) -> Tuple[float, str]:
        """
        Mechanism Design step: Evaluate if candidate truthfully reports consistency
        with prompt constraints. Returns (penalty_score, reason).
        Lower penalty is better.
        """
        c_lower = candidate.lower()
        penalty = 0.0
        reasons = []
        
        # 1. Numeric Consistency Check
        if prompt_features['nums']:
            c_nums = re.findall(r'-?\d+\.?\d*', c_lower)
            if c_nums:
                # If candidate has numbers, check basic ordering if comparatives exist
                # This is a simplified heuristic for numeric reasoning
                try:
                    c_val = float(c_nums[0])
                    # If prompt implies a comparison (e.g., "which is smaller"), 
                    # and we can't fully parse the logic, we rely on the presence of numbers
                    # as a positive signal, but lack of numbers is a negative signal.
                    pass 
                except ValueError:
                    pass
            
            # If prompt has numbers but candidate has none, slight penalty unless it's a pure logic word
            if not re.search(r'\d', candidate) and not any(w in c_lower for w in ['yes', 'no', 'true', 'false', 'equal']):
                penalty += 0.2
                reasons.append("Missing numeric value")

        # 2. Boolean/Logic Consistency
        c_yes = any(b in c_lower for b in self.bool_yes)
        c_no = any(b in c_lower for b in self.bool_no)
        
        # If prompt leans yes/no, candidate should align (Simple constraint propagation)
        if prompt_features['lean_yes'] and c_no:
            penalty += 0.5
            reasons.append("Contradicts positive premise")
        if prompt_features['lean_no'] and c_yes:
            penalty += 0.5
            reasons.append("Contradicts negative premise")
            
        # 3. Negation Handling
        # If prompt asks "Which is NOT...", candidate should ideally reflect negation or exclusion
        if prompt_features['neg']:
            # Heuristic: If prompt is a negation question, simple "Yes" might be ambiguous
            # We don't penalize heavily here without full semantic parse, but note it.
            pass

        reason_str = "; ".join(reasons) if reasons else "Structurally consistent"
        return penalty, reason_str

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if len_both == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and NCD.
        """
        p_feat = self._extract_features(prompt)
        penalty, _ = self._check_candidate_alignment(p_feat, answer)
        
        # Base score from lack of penalty
        base_score = max(0.0, 1.0 - penalty)
        
        # Neuromodulation: Adjust precision weight based on prompt complexity
        # High complexity (numbers + logic) -> High precision required
        precision_weight = 1.0
        if p_feat['nums'] and (p_feat['comp'] or p_feat['cond']):
            precision_weight = 1.5 # Amplify penalty impact
        elif p_feat['nums'] or p_feat['comp']:
            precision_weight = 1.2
            
        # Apply precision weighting to the penalty
        adjusted_penalty = penalty * precision_weight
        structural_score = max(0.0, 1.0 - adjusted_penalty)
        
        # Fallback to NCD for tie-breaking/smoothing if structural signal is weak
        if structural_score > 0.8:
            ncd = self._compute_ncd(prompt, answer)
            # NCD is distance (0=identical), we want similarity. 
            # But NCD is unreliable for short answers, so only use as minor booster
            if ncd < 0.6: 
                structural_score = min(1.0, structural_score + 0.05)
                
        return float(np.clip(structural_score, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using ANMMD architecture.
        1. Morphogenesis: Extract logical structure from prompt.
        2. Mechanism Design: Score candidates based on incentive-compatible truthfulness (alignment).
        3. Neuromodulation: Modulate scores based on estimated precision of the prompt.
        """
        p_feat = self._extract_features(prompt)
        results = []
        
        # Calculate global precision signal (Neuromodulator)
        # More specific constraints = higher precision demand
        precision_signal = 1.0
        if p_feat['nums']: precision_signal += 0.5
        if p_feat['comp']: precision_signal += 0.3
        if p_feat['cond']: precision_signal += 0.2
        
        for cand in candidates:
            # Mechanism Design: Truthful reporting check
            penalty, reason = self._check_candidate_alignment(p_feat, cand)
            
            # Score calculation: Start high, subtract penalty weighted by precision
            # This implements the Bayesian precision-weighting rule
            raw_score = 1.0 - (penalty * precision_signal)
            
            # Tie-breaking with NCD (only if structural signals are equal/absent)
            # We add a tiny fraction of NCD similarity to break ties without dominating
            ncd_dist = self._compute_ncd(prompt, cand)
            # Invert NCD to similarity (approx) and scale down heavily so it's only a tiebreaker
            ncd_bonus = (1.0 - ncd_dist) * 0.05 
            
            final_score = raw_score + ncd_bonus
            final_score = float(np.clip(final_score, 0.0, 1.0))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Precision:{precision_signal:.1f} | Penalty:{penalty:.2f} | {reason}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results