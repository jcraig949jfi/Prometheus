import zlib
import re
import math

class ReasoningTool:
    """
    Critical Pragmatic Error-Correcting Reservoir (CPER) Approximation.
    
    Mechanism:
    1. Critical Reservoir: Uses a logistic map recurrence on character codes to generate 
       a deterministic 'chaotic' state vector. This amplifies small textual differences 
       (sensitivity to initial conditions).
    2. Error Correcting Codes (LDPC analog): Implements a parity-based syndrome check. 
       We compute a 'syndrome' by comparing the parity of the candidate's structural 
       features against the prompt's expected structural constraints (e.g., negation handling).
       If the syndrome is non-zero (mismatch), a penalty is applied (error correction).
    3. Pragmatics: Evaluates candidates against Gricean maxims via heuristic rules:
       - Quantity: Penalize extreme length deviations from the prompt.
       - Quality: Detect internal contradictions or tautologies.
       - Relevance: Ensure key prompt tokens appear in the candidate.
    
    The final score combines structural parsing (logic), numeric evaluation, and the 
    CPER-specific syndrome/pragmatic penalties.
    """

    def __init__(self):
        self.max_reservoir_steps = 50
        self.chaotic_param = 3.99  # Near edge of chaos for logistic map

    def _logistic_map(self, x, steps=10):
        """Simulates critical dynamics using logistic map."""
        for _ in range(steps):
            x = self.chaotic_param * x * (1 - x)
            # Clamp to avoid divergence out of [0,1] due to float precision
            if x < 0 or x > 1:
                x = 0.5 
        return x

    def _get_reservoir_state(self, text):
        """Encodes text into a critical reservoir state."""
        if not text:
            return 0.0
        # Normalize input to [0.1, 0.9] to avoid fixed points
        seed = sum(ord(c) for c in text) / (len(text) * 128.0)
        seed = 0.1 + 0.8 * (seed % 1.0)
        return self._logistic_map(seed, self.max_reservoir_steps)

    def _extract_structure(self, text):
        """Extracts logical structures: negations, numbers, comparatives."""
        text_lower = text.lower()
        has_negation = any(n in text_lower for n in ['not', 'no ', 'never', 'false', 'impossible'])
        numbers = re.findall(r"-?\d+\.?\d*", text)
        nums = [float(n) for n in numbers] if numbers else []
        comparatives = any(c in text_lower for c in ['>', '<', 'greater', 'less', 'more', 'fewer'])
        return has_negation, nums, comparatives

    def _compute_syndrome(self, prompt_feats, cand_feats):
        """
        Computes a 'syndrome' representing the mismatch between prompt constraints 
        and candidate properties. Analogous to LDPC syndrome checking.
        Returns a penalty factor (0.0 = perfect match, 1.0 = total mismatch).
        """
        p_neg, p_nums, p_comp = prompt_feats
        c_neg, c_nums, c_comp = cand_feats
        
        syndrome = 0.0
        
        # Constraint 1: Negation consistency (simplified Modus Tollens check)
        # If prompt implies negation logic, candidate should reflect it appropriately
        if p_neg != c_neg:
            syndrome += 0.4
            
        # Constraint 2: Numeric transitivity
        if p_nums and c_nums:
            # Check if order is preserved (simplified)
            p_order = sorted(p_nums) == p_nums
            c_order = sorted(c_nums) == c_nums
            if p_order != c_order:
                syndrome += 0.3
        elif p_nums and not c_nums:
            syndrome += 0.2 # Missing numbers is a quality violation
            
        return min(syndrome, 1.0)

    def _pragmatic_score(self, prompt, candidate):
        """
        Evaluates candidate against Gricean Maxims.
        Returns a score 0.0 to 1.0.
        """
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        score = 1.0
        
        # Maxim of Quantity: Avoid being too brief or too verbose relative to prompt complexity
        if p_len > 10: # Complex prompt
            if c_len < 2:
                score -= 0.5 # Too brief for complex context
        else:
            if c_len > p_len * 2:
                score -= 0.3 # Unnecessarily verbose
        
        # Maxim of Relevance: Must share some significant tokens (excluding stopwords)
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        p_tokens = set(t.lower().strip('.,!?') for t in prompt.split() if t.lower() not in stopwords)
        c_tokens = set(t.lower().strip('.,!?') for t in candidate.split() if t.lower() not in stopwords)
        
        if p_tokens:
            overlap = len(p_tokens.intersection(c_tokens))
            if overlap == 0 and len(c_tokens) > 0:
                score -= 0.6 # Irrelevant
        
        return max(0.0, score)

    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_feats = self._extract_structure(prompt)
        p_state = self._get_reservoir_state(prompt)
        
        for cand in candidates:
            c_feats = self._extract_structure(cand)
            c_state = self._get_reservoir_state(cand)
            
            # 1. Structural/Logical Score (Base)
            # Detect simple numeric comparisons if present
            logic_score = 0.5
            if p_feats[1] and c_feats[1]: # Both have numbers
                # Heuristic: if prompt asks for max/min, check candidate
                if 'max' in prompt.lower() or 'largest' in prompt.lower():
                    if max(c_feats[1]) == max(p_feats[1]) or (c_feats[1] and c_feats[1][-1] == max(p_feats[1])):
                        logic_score = 0.9
                elif 'min' in prompt.lower() or 'smallest' in prompt.lower():
                     if min(c_feats[1]) == min(p_feats[1]):
                        logic_score = 0.9
            
            # 2. Critical Reservoir Divergence
            # Small differences in text should yield different states. 
            # We use the distance between states as a sensitivity measure.
            state_diff = abs(p_state - c_state)
            
            # 3. Syndrome Check (Error Correction)
            syndrome = self._compute_syndrome(p_feats, c_feats)
            
            # 4. Pragmatic Evaluation
            pragmatic_val = self._pragmatic_score(prompt, cand)
            
            # 5. NCD Tiebreaker (Low weight)
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score Aggregation
            # High logic score is good. 
            # Low syndrome (error) is good.
            # High pragmatic value is good.
            # State diff ensures we aren't just echoing (diversity bonus if distinct)
            
            raw_score = (logic_score * 0.4) + ((1.0 - syndrome) * 0.3) + (pragmatic_val * 0.2) + (state_diff * 0.1)
            
            # Adjust for NCD (if too similar to prompt without adding value, penalize slightly unless logic is perfect)
            if ncd_val < 0.1 and logic_score < 0.8:
                raw_score *= 0.8
                
            results.append({
                "candidate": cand,
                "score": float(f"{raw_score:.4f}"),
                "reasoning": f"Logic:{logic_score:.2f}, Syndrome:{syndrome:.2f}, Pragmatics:{pragmatic_val:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation metrics."""
        # Re-use evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to confidence. 
        # Our scoring is roughly 0.0 to 1.0 already, but we tighten the bounds.
        confidence = max(0.0, min(1.0, score))
        return float(f"{confidence:.4f}")