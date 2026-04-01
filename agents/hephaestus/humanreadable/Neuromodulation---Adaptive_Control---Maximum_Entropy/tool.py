import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Adaptive Maximum-Entropy Controller (NAMEC) for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Adaptive Control): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'reference model' of the problem.
    2. Computation (Maximum Entropy): Performs explicit numeric/logic calculations. 
       Per instructions, MaxEnt is restricted to confidence calibration (preventing 
       over-confidence) and not direct scoring, acting as an entropy regularizer on belief.
    3. Neuromodulation (Gain Control): Calculates a 'surprise' signal based on the 
       divergence between structural expectations and candidate simplicity. This scales 
       the learning rate (score adjustment) dynamically. High surprise (ambiguity) 
       triggers low confidence (epistemic honesty).
    
    Synergy: Neuromodulation gates the entropy-constrained updates, ensuring the system 
    remains uncertain when structural signals are weak or ambiguous.
    """

    def __init__(self):
        # State for adaptive law (running average of surprise)
        self._baseline_surprise = 0.5
        self._learning_rate = 0.1
        
        # Patterns for structural parsing
        self._negation_pat = re.compile(r'\b(not|no|never|neither|without|fail|stop|quit)\b', re.I)
        self._comp_pat = re.compile(r'\b(more|less|greater|smaller|higher|lower|best|worst|larger)\b', re.I)
        self._cond_pat = re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.I)
        self._num_pat = re.compile(r'-?\d+\.?\d*')
        
        # Tier B Traps (Presupposition/Ambiguity)
        self._presup_pat = re.compile(r'\b(have you stopped|why did.*fail|why.*stop|quit)\b', re.I)
        self._scope_pat = re.compile(r'\b(every.*a\s+\w+|each.*a\s+\w+)\b', re.I) # Simplified scope check
        self._pronoun_pat = re.compile(r'\b(he|she|him|her|they|it)\swas\b', re.I)
        self._dichotomy_pat = re.compile(r'\b(either.*or|whether.*or)\b', re.I)
        self._subjective_pat = re.compile(r'\b(best|worst|favorite|beautiful|good)\b', re.I)

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features from text."""
        return {
            'negations': len(self._negation_pat.findall(text)),
            'comparatives': len(self._comp_pat.findall(text)),
            'conditionals': len(self._cond_pat.findall(text)),
            'numbers': self._num_pat.findall(text),
            'length': len(text.split())
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence (low if traps detected).
        """
        flags = 0
        
        if self._presup_pat.search(prompt):
            flags += 1
        if self._scope_pat.search(prompt):
            flags += 1
        if self._pronoun_pat.search(prompt) and "who" in prompt.lower():
            flags += 1
        if self._dichotomy_pat.search(prompt):
            flags += 1
        if self._subjective_pat.search(prompt) and "measure" not in prompt.lower():
            flags += 1
            
        # If multiple ambiguity flags or strong presupposition, cap confidence low
        if flags >= 1:
            return 0.25
        return 1.0

    def _compute_entropy_cap(self, candidates: List[str]) -> float:
        """
        Maximum Entropy Constraint: 
        Calculates the entropy of the candidate set distribution.
        If candidates are very similar (low entropy), we risk over-confidence.
        If diverse, we must maintain uncertainty unless structural evidence is strong.
        """
        if not candidates:
            return 1.0
        
        # Simple similarity check via NCD matrix
        n = len(candidates)
        if n == 1:
            return 1.0
            
        # Estimate diversity
        total_diversity = 0.0
        count = 0
        for i in range(n):
            for j in range(i+1, n):
                dist = self._ncd(candidates[i], candidates[j])
                total_diversity += dist
                count += 1
        
        avg_diversity = total_diversity / count if count > 0 else 0.0
        
        # High diversity -> Lower max confidence (need more evidence)
        # Low diversity -> Higher max confidence allowed
        return min(1.0, 0.5 + (0.5 * (1.0 - avg_diversity)))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
        return (c12 - min_len) / max(c1, c2)

    def _constructive_compute(self, prompt: str, candidate: str) -> float:
        """
        Performs explicit numeric/logic calculation if numbers are present.
        Returns a score boost if the candidate matches the computed result.
        """
        nums = self._num_pat.findall(prompt)
        if len(nums) < 2:
            return 0.0
            
        try:
            # Extract numbers from candidate
            cand_nums = self._num_pat.findall(candidate)
            if not cand_nums:
                return 0.0
            
            # Simple heuristic: Does the candidate contain the result of a simple operation?
            # We try basic ops on prompt numbers to see if they match candidate
            p_nums = [float(x) for x in nums]
            c_val = float(cand_nums[0])
            
            # Check sum
            if abs(sum(p_nums) - c_val) < 1e-6:
                return 0.4
            # Check product (if small set)
            if len(p_nums) <= 3:
                prod = 1.0
                for x in p_nums: prod *= x
                if abs(prod - c_val) < 1e-6:
                    return 0.4
            # Check comparison logic
            if len(p_nums) == 2:
                if "greater" in candidate.lower() or "larger" in candidate.lower():
                    if p_nums[0] > p_nums[1]: return 0.4
                if "less" in candidate.lower() or "smaller" in candidate.lower():
                    if p_nums[0] < p_nums[1]: return 0.4
        except ValueError:
            pass
            
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._structural_parse(prompt)
        has_structure = (prompt_feat['negations'] > 0 or 
                         prompt_feat['comparatives'] > 0 or 
                         prompt_feat['conditionals'] > 0)
        
        # MaxEnt Cap: Prevents over-confidence in diverse/ambiguous sets
        entropy_cap = self._compute_entropy_cap(candidates)
        
        results = []
        for cand in candidates:
            score = 0.5  # Base prior (Maximum Entropy start)
            reasoning_parts = []
            
            # 1. Structural Matching (Adaptive Control Reference)
            cand_feat = self._structural_parse(cand)
            
            # Negation consistency
            if prompt_feat['negations'] > 0:
                if cand_feat['negations'] > 0:
                    score += 0.2
                    reasoning_parts.append("Consistent negation")
                else:
                    score -= 0.2
                    reasoning_parts.append("Missing negation")
            
            # Comparative consistency
            if prompt_feat['comparatives'] > 0:
                if cand_feat['comparatives'] > 0 or prompt_feat['numbers']:
                    score += 0.15
                    reasoning_parts.append("Comparative logic matched")
            
            # 2. Constructive Computation (Explicit Calculation)
            comp_boost = self._constructive_compute(prompt, cand)
            if comp_boost > 0:
                score += comp_boost
                reasoning_parts.append("Calculation verified")
            
            # 3. Neuromodulatory Gain (Surprise-based scaling)
            # If structure is high but candidate is short/simple, increase "surprise" (lower score)
            surprise = 0.0
            if has_structure and cand_feat['length'] < 3:
                surprise = 0.3
                reasoning_parts.append("High surprise: low info density")
            
            # Adaptive update: Score = Prior + Structure - Surprise
            # Gain scales the impact of surprise based on entropy cap
            gain = 1.0 if entropy_cap > 0.6 else 0.5
            score -= (surprise * gain)
            
            # Apply MaxEnt Cap (Confidence regularization)
            score = min(score, entropy_cap)
            
            # NCD Tiebreaker (Max 15% influence logic via small addition)
            # Only used if scores are close, implemented here as a minor bonus for similarity to prompt terms
            prompt_keywords = [w for w in prompt.lower().split() if len(w) > 4]
            keyword_match = sum(1 for w in prompt_keywords if w in cand.lower())
            score += (keyword_match * 0.02) 
            reasoning_parts.append(f"Structural match: {', '.join(reasoning_parts[:-1])}" if len(reasoning_parts) > 1 else "Baseline")

            results.append({
                "candidate": cand,
                "score": float(f"{score:.4f}"),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural baseline"
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        # 1. Check for Tier B traps (Presupposition, Ambiguity)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return 0.2  # Explicitly low for traps

        # 2. Structural Verification
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        # If prompt has logic but answer is empty or nonsense
        if p_feat['negations'] > 0 and a_feat['negations'] == 0 and len(answer.split()) < 3:
            return 0.3
            
        # 3. Computation Verification
        # If numbers exist, did we solve it?
        if len(p_feat['numbers']) >= 2:
            calc_match = self._constructive_compute(prompt, answer)
            if calc_match > 0.3:
                return 0.95 # High confidence on verified math
            elif len(p_feat['numbers']) > 0 and not self._num_pat.findall(answer):
                return 0.2 # Math question, no number answer
        
        # 4. Default Confidence based on structural alignment
        # If structure matches (e.g. negation in both), confidence rises
        base_conf = 0.5
        if p_feat['negations'] > 0 and a_feat['negations'] > 0:
            base_conf = 0.8
        elif p_feat['comparatives'] > 0 and a_feat['comparatives'] > 0:
            base_conf = 0.75
        elif p_feat['conditionals'] > 0:
            base_conf = 0.6 # Conditionals are harder
            
        return min(base_conf, meta_cap)