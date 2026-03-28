import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological Wavelet Oscillatory Network (TWON) Simulator.
    
    Mechanism:
    1. Wavelet Decomposition (Structural Parsing): The input text is decomposed into 
       "scales" representing logical frequencies: Negations (high freq), Comparatives 
       (mid freq), and Conditionals (low freq).
    2. Topological Filtration (Constraint Propagation): We construct a persistence 
       diagram of logical consistency. Candidates that violate prompt constraints 
       (e.g., answering "Yes" to a negated query) generate high "persistence noise" 
       (topological defects), lowering their score.
    3. Oscillatory Coupling (Numeric/Logic Check): Explicit numeric comparisons and 
       boolean logic checks act as the ground-truth signal, coupling the scales.
    4. Scoring: The final score is a weighted sum of structural adherence (primary) 
       and NCD similarity (tiebreaker only).
    """

    def __init__(self):
        # Keywords defining logical "frequencies"
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when', 'while']
        self.booleans = ['yes', 'no', 'true', 'false']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_features(self, text: str) -> Dict[str, int]:
        """Extract structural features (Wavelet Scales)."""
        t = self._normalize(text)
        words = re.findall(r'\b\w+\b', t)
        return {
            'neg': sum(1 for w in words if w in self.negations),
            'comp': sum(1 for w in words if w in self.comparatives),
            'cond': sum(1 for w in words if w in self.conditionals),
            'bool': sum(1 for w in words if w in self.booleans),
            'nums': len(re.findall(r'\d+\.?\d*', t))
        }

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate explicit numeric comparisons (Oscillatory Coupling)."""
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # Extract numbers from prompt
        p_nums = re.findall(r'\d+\.?\d*', p_low)
        if len(p_nums) < 2:
            return 0.0 # No numeric logic to check

        try:
            vals = [float(x) for x in p_nums]
            # Simple heuristic: if prompt asks for max/largest/greater
            is_max = any(k in p_low for k in ['largest', 'max', 'greater', 'biggest'])
            is_min = any(k in p_low for k in ['smallest', 'min', 'least', 'smallest'])
            
            if is_max or is_min:
                target = str(max(vals)) if is_max else str(min(vals))
                if target in c_low:
                    return 1.0
                # Penalize if candidate contains a number that is definitely wrong
                c_nums = re.findall(r'\d+\.?\d*', c_low)
                if c_nums:
                    if c_nums[0] != target:
                        return -1.0 # Strong penalty for wrong number
        except ValueError:
            pass
        return 0.0

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Topological Defect Detection.
        Checks if the candidate contradicts the logical shape of the prompt.
        Returns 0.0 (no defect) or -1.0 (defect detected).
        """
        p_feats = self._count_features(prompt)
        c_feats = self._count_features(candidate)
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)

        # 1. Negation Trap: If prompt says "Do NOT say X", and candidate says "X"
        # Simplified: If prompt has "not" and candidate is a bare boolean opposite?
        # Harder but effective: If prompt asks "Which is NOT...", candidate should not be the excluded item.
        
        # Specific pattern: "Answer yes if..." vs "Answer no if..."
        if 'answer yes if' in p_low or 'answer no if' in p_low:
            if 'yes' in c_low and 'no' not in p_low.split('if')[1]:
                 # Complex conditional, skip simple check
                pass
        
        # Direct Contradiction Check:
        # If prompt contains "not" + boolean, and candidate is that boolean without negation
        for b in ['yes', 'no', 'true', 'false']:
            if f"not {b}" in p_low or f"is not {b}" in p_low or f"answer not {b}" in p_low:
                if c_low.strip() == b:
                    return -1.0 # Topological void detected
            
        # If prompt asks "Is it false?" and implies false, but candidate says "True"
        # This is hard without full NLI, so we rely on the numeric and structural counts
        
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(s1_b)
        len2 = len(s2_b)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/simplicity if not compressing individually, 
        # but standard NCD uses compressed lengths.
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_feats = self._count_features(prompt)
        p_low = self._normalize(prompt)
        
        # Pre-calculate numeric logic score (Global oscillator)
        numeric_score = self._check_numeric_logic(prompt, "") # Just checking prompt structure first
        # Actually, we need to check against candidate content for numbers
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            c_feats = self._count_features(cand)
            c_low = self._normalize(cand)
            
            # 1. Numeric Logic (High Priority)
            num_check = self._check_numeric_logic(prompt, cand)
            if num_check != 0.0:
                score += num_check * 2.0
                reasoning_parts.append(f"Numeric logic: {num_check}")

            # 2. Topological Constraint (Defect Detection)
            defect = self._check_constraint_violation(prompt, cand)
            if defect < 0:
                score -= 2.0
                reasoning_parts.append("Topological defect: Contradiction detected")
            
            # 3. Structural Resonance (Wavelet Scale Matching)
            # If prompt asks a Yes/No question (has boolean intent), reward boolean answers
            if p_feats['bool'] > 0 or any(q in p_low for q in ['is it', 'does it', 'can it', 'are there']):
                if c_feats['bool'] > 0:
                    score += 0.5
                    reasoning_parts.append("Structural match: Boolean response")
            
            # If prompt has negations, ensure candidate acknowledges complexity (heuristic)
            # This is a weak proxy for "shape preservation"
            if p_feats['neg'] > 0:
                # If prompt is negative, and candidate is a simple "yes", it might be risky
                # But without full NLI, we trust the defect check more.
                pass

            # 4. NCD Tiebreaker (Only if score is neutral)
            # We add a tiny fraction of NCD to break ties, but never let it dominate
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so higher is better, scale down significantly
            ncd_score = (1.0 - ncd_val) * 0.05 
            score += ncd_score
            
            # Normalize score to 0-1 range roughly
            # Base score starts at 0.5 (neutral)
            final_score = 0.5 + score
            final_score = max(0.0, min(1.0, final_score))
            
            reason_str = "; ".join(reasoning_parts) if reasoning_parts else "Standard structural alignment"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason_str
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on topological consistency between prompt and answer.
        Returns 0.0 to 1.0.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map the internal score (0-1) to confidence
        # If the item was ranked first and has a high score, confidence is high
        score = res[0]['score']
        
        # Boost confidence if numeric logic was explicitly satisfied
        if self._check_numeric_logic(prompt, answer) == 1.0:
            return min(1.0, score + 0.4)
        
        # Penalty if defect found
        if self._check_constraint_violation(prompt, answer) < 0:
            return max(0.0, score - 0.5)
            
        return score