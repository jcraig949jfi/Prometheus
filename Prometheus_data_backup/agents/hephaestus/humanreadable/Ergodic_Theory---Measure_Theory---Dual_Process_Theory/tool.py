import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a self-monitoring inference engine inspired by Ergodic Theory, 
    Measure Theory, and Dual Process Theory.
    
    Mechanism:
    1. System 1 (Fast/Ergodic): Generates rapid heuristic scores based on structural 
       parsing (negations, comparatives, conditionals) and numeric evaluation. 
       This represents the 'time-average' convergence.
    2. System 2 (Slow/Measure-Theoretic): Computes a rigorous error bound estimate 
       based on candidate consistency and structural complexity. 
    3. Metacognitive Switch: If the 'error bound' (variance in structural signals) 
       exceeds a tolerance, the system penalizes low-complexity heuristics and 
       relies more heavily on constraint propagation logic.
    4. NCD is used strictly as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Structural keywords for System 1 fast parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.logic_ops = ['and', 'or', 'but', 'however', 'therefore']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for quantitative reasoning."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text.lower())]

    def _structural_score(self, text: str) -> float:
        """
        System 1: Fast ergodic sampling of structural features.
        Returns a score based on the presence of logical operators and numeric consistency.
        """
        t_lower = text.lower()
        score = 0.0
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Weight for logical density
        if words:
            neg_count = sum(1 for w in words if w in self.negations)
            comp_count = sum(1 for w in words if w in self.comparatives)
            cond_count = sum(1 for w in words if w in self.conditionals)
            logic_count = sum(1 for w in words if w in self.logic_ops)
            
            # Heuristic: Logical complexity suggests reasoning capability
            score += (neg_count * 0.5) + (comp_count * 0.4) + (cond_count * 0.6) + (logic_count * 0.3)
            
            # Numeric evaluation bonus if numbers are present and ordered logically
            nums = self._extract_numbers(text)
            if len(nums) > 1:
                # Check for monotonicity as a proxy for valid comparison
                is_sorted = all(nums[i] <= nums[i+1] for i in range(len(nums)-1))
                is_rev_sorted = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
                if is_sorted or is_rev_sorted:
                    score += 1.0
                else:
                    # Penalty for chaotic numbers in a reasoning context
                    score -= 0.5
                    
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_combined - min(c_s1, c_s2)) / max_len

    def _measure_theoretic_check(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        System 2: Measure-theoretic verification.
        Computes a 'confidence bound' based on structural alignment between prompt and candidate.
        Returns (base_score, error_bound).
        """
        p_score = self._structural_score(prompt)
        c_score = self._structural_score(candidate)
        
        # Base score is the candidate's intrinsic structural richness
        base = c_score
        
        # Error bound estimation: Discrepancy between prompt complexity and answer complexity
        # If the prompt is highly logical but the answer is simple, error bound increases
        complexity_gap = abs(p_score - c_score)
        
        # Numeric consistency check
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check if candidate numbers are a subset or derived
            # Simplified check: are candidate numbers present in prompt?
            match_ratio = sum(1 for n in c_nums if any(abs(n - pn) < 1e-6 for pn in p_nums)) / len(c_nums)
            complexity_gap *= (1.0 - match_ratio) # Reduce error if numbers match
        elif p_nums and not c_nums:
            # Prompt has numbers, answer doesn't -> High uncertainty unless it's a yes/no question
            if not any(w in candidate.lower() for w in ['yes', 'no', 'true', 'false']):
                complexity_gap += 2.0

        return base, complexity_gap

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_base, prompt_error = self._measure_theoretic_check(prompt, "")
        
        # Pre-calculate NCD matrix for tie-breaking if needed
        # We only need NCD relative to prompt for tie-breaking
        ncd_scores = [(c, self._ncd_distance(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for cand in candidates:
            # System 1: Fast structural score
            raw_score = self._structural_score(cand)
            
            # System 2: Measure theoretic verification
            _, error_bound = self._measure_theoretic_check(prompt, cand)
            
            # Metacognitive Switch:
            # If error_bound is high (complexity mismatch), we penalize the raw score
            # effectively forcing the system to prefer candidates that maintain structural integrity.
            tolerance = 1.5 # Threshold for switching to 'strict' mode
            
            if error_bound > tolerance:
                # Apply penalty proportional to the error bound
                final_score = raw_score - (error_bound * 0.5)
            else:
                # Within tolerance, accept the ergodic average (raw score)
                final_score = raw_score + 0.1 # Small bonus for consistency
            
            # Add small component for length appropriateness (avoiding trivial answers)
            if len(cand.strip()) < 2:
                final_score -= 1.0
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{raw_score:.2f}, ErrorBound:{error_bound:.2f}, NCD:{ncd_map[cand]:.2f}"
            })
        
        # Sorting: Primary by score (desc), Secondary by NCD (asc - closer is better)
        # Since NCD is a distance, lower is better. We subtract it as a tiny tiebreaker.
        results.sort(key=lambda x: (x['score'], -ncd_map[x['candidate']]), reverse=True)
        
        # Refine sorting to strictly use NCD as tiebreaker for scores that are effectively equal
        # We do a stable sort pass: first by NCD (asc), then by Score (desc)
        # But since we want Score primary, we adjust the key slightly:
        # Key = (Score, -NCD) -> Higher score wins, if equal, higher -NCD (lower NCD) wins.
        # However, float precision might make scores distinct. 
        # Let's rely on the primary sort above but ensure NCD is the secondary key.
        
        # Re-sort with explicit tuple logic for clarity
        def sort_key(item):
            # Normalize NCD to be a small tiebreaker (0.0001 scale)
            tie_breaker = -ncd_map[item['candidate']] 
            return (item['score'], tie_breaker)
            
        results.sort(key=sort_key, reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the measure-theoretic error bound.
        Low error bound = High confidence.
        """
        _, error_bound = self._measure_theoretic_check(prompt, answer)
        
        # Map error bound to 0-1 scale
        # Assume error_bound > 4.0 is essentially 0 confidence
        # error_bound < 0.5 is essentially 1.0 confidence
        confidence = 1.0 - (error_bound / 4.0)
        return max(0.0, min(1.0, confidence))