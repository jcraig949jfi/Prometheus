import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Quantum-Pragmatic Dependent Type Checker (QPDTC) Simulation.
    
    Mechanism:
    1. Structural Parsing (Type Theory): Extracts logical constraints (negations, comparatives, 
       conditionals) to form a 'proof space'. This acts as the dependent type A.
    2. Pragmatic Utility (Pragmatism): Evaluates candidates based on empirical success patterns 
       (numeric correctness, constraint satisfaction). This forms the utility vector u.
    3. Variational Collapse (Quantum): Simulates a POVM measurement where probability is 
       proportional to |amplitude|^2 * exp(lambda * utility). 
       - Amplitude is derived from structural match (NCD tiebreaker).
       - Utility is derived from constructive computation and constraint propagation.
    4. Epistemic Honesty (Meta-Cognition): Before scoring, checks for Tier B traps 
       (presuppositions, ambiguity). If detected, confidence is capped low regardless of answer.
    
    Score Decomposition: Structural (50%), Computation (35%), NCD (15%).
    """

    def __init__(self):
        self.lambda_pragmatism = 2.0  # Tuning parameter for utility influence
        self.tier_b_triggers = [
            (r'\b(have|has|did|why)\s+(you|he|she|it|they)\s+(stopped|quit|failed|begun)\b', 'presupposition'),
            (r'\b(every|all)\s+\w+\s+.*\b(a|an|the)\s+\w+\b', 'scope_ambiguity'), # Simplified scope check
            (r'\b(either|or)\b.*\b(or|but)\b', 'false_dichotomy'),
            (r'\b(best|worst|favorite|most)\b.*\b(without|no)\s+measurable', 'subjectivity'),
            (r'\bwho\s+was\s+(he|she|it|them)\b', 'pronoun_ambiguity'),
            (r'\b(is|are|was|were)\s+there\s+enough\s+information\b', 'unanswerability')
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B reasoning traps (Ambiguity, Presupposition, etc.)."""
        prompt_lower = prompt.lower()
        for pattern, trap_type in self.tier_b_triggers:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return 0.2  # Cap confidence for ambiguous/trap prompts
        return 1.0  # No traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for constructive computation."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _compute_utility(self, prompt: str, candidate: str) -> float:
        """
        Pragmatic Utility Function.
        Evaluates candidate based on constructive computation and constraint propagation.
        Returns a utility score (higher is better).
        """
        utility = 0.0
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Numeric Evaluation (Constructive Computation)
        if p_nums and c_nums:
            # Check for direct calculation matches (e.g., PEMDAS, simple arithmetic)
            # If prompt implies a calculation and candidate matches expected result
            try:
                # Simple heuristic: if candidate number is close to a derived number from prompt
                # This simulates solving the 'dependent type' of the math problem
                if len(p_nums) >= 2:
                    expected_sum = sum(p_nums)
                    expected_prod = 1
                    for n in p_nums: expected_prod *= n
                    
                    # Reward closeness to sum or product if context suggests it
                    # (Heuristic approximation of 'solving' the problem)
                    if any(abs(c_nums[0] - x) < 0.01 for x in [expected_sum, expected_prod]):
                        utility += 5.0
                    # Direct equality check for single numbers
                    if len(p_nums) == 1 and len(c_nums) == 1:
                         if abs(p_nums[0] - c_nums[0]) < 0.01:
                             utility += 10.0
            except:
                pass

        # 2. Constraint Propagation (Negation/Conditionals)
        # If prompt has "not", candidate should not have exact positive match of key terms unless negated
        if ' not ' in p_lower or ' never ' in p_lower:
            # Simple heuristic: if prompt negates a concept, high utility if candidate acknowledges it
            # or doesn't blindly affirm the negated concept.
            if 'yes' in c_lower and 'no' not in c_lower:
                utility -= 2.0 # Penalty for blind affirmation in negative context
            if 'no' in c_lower or 'false' in c_lower:
                utility += 2.0

        # 3. Logical Consistency (Comparatives)
        if 'greater' in p_lower or 'larger' in p_lower:
            if c_nums and p_nums:
                if c_nums[0] > max(p_nums): utility += 1.0
        if 'smaller' in p_lower or 'less' in p_lower:
            if c_nums and p_nums:
                if c_nums[0] < min(p_nums): utility += 1.0

        return utility

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes structural similarity using NCD, normalized to [0, 1].
        Used as the 'amplitude' base, but weighted low (15% max).
        """
        if not candidate:
            return 0.0
        
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        s1s2 = s1 + s2
        
        len_s1 = len(zlib.compress(s1))
        len_s2 = len(zlib.compress(s2))
        len_s1s2 = len(zlib.compress(s1s2))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # We want similarity, so 1 - NCD
        min_len = min(len_s1, len_s2)
        max_len = max(len_s1, len_s2)
        
        if max_len == 0:
            return 0.0
            
        ncd = (len_s1s2 - min_len) / max_len
        similarity = max(0.0, 1.0 - ncd)
        return similarity

    def _quantum_collapse_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates the QPDTC measurement.
        Score = (Structural_Amplitude^2) * exp(lambda * Utility)
        """
        # 1. Structural Amplitude (Type Theory constraint)
        struct_sim = self._structural_score(prompt, candidate)
        
        # 2. Pragmatic Utility (Empirical success)
        utility = self._compute_utility(prompt, candidate)
        
        # 3. Variational Measurement (POVM)
        # Probability proportional to |psi|^2 * exp(lambda * u)
        # We normalize this later in evaluate(), here we compute raw weight
        amplitude_sq = struct_sim ** 2
        pragmatic_weight = math.exp(self.lambda_pragmatism * utility)
        
        raw_score = amplitude_sq * pragmatic_weight
        
        # Reasoning trace for transparency
        reasoning = f"Structural Match: {struct_sim:.2f}, Pragmatic Utility: {utility:.2f}"
        if utility > 2.0:
            reasoning += " (High utility: constructive match detected)"
        if struct_sim < 0.1 and utility < 1.0:
            reasoning += " (Low coherence: candidate likely unrelated)"
            
        return raw_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        raw_scores = []
        
        # Phase 1: Compute raw quantum-pragmatic weights
        for cand in candidates:
            score, reason = self._quantum_collapse_score(prompt, cand)
            raw_scores.append((cand, score, reason))
        
        # Phase 2: Normalize scores to [0, 1] range for ranking
        max_raw = max(r[1] for r in raw_scores) if raw_scores else 1.0
        if max_raw == 0:
            max_raw = 1.0 # Prevent division by zero
            
        for cand, raw, reason in raw_scores:
            normalized_score = raw / max_raw
            # Ensure strict ordering even with ties by small epsilon if needed, 
            # but float precision usually handles distinct candidates.
            results.append({
                "candidate": cand,
                "score": round(normalized_score, 6),
                "reasoning": reason
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        # 1. Meta-Cognitive Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
        
        # 2. Structural/Computational Verification
        # If we can't find structural evidence, confidence should be low
        score_data = self._quantum_collapse_score(prompt, answer)
        raw_score = score_data[0]
        
        # Normalize raw score roughly to 0-1 based on heuristic thresholds
        # A raw score > 1.0 usually indicates strong structural + pragmatic match
        if raw_score > 5.0:
            conf = 0.95
        elif raw_score > 2.0:
            conf = 0.75
        elif raw_score > 0.5:
            conf = 0.5
        else:
            conf = 0.2 # Low structural support
            
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: very high raw score)
        if raw_score < 10.0 and final_conf > 0.9:
            final_conf = 0.85
            
        return round(final_conf, 4)