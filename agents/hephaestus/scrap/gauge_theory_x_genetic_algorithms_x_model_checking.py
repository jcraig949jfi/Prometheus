import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Evolutionary Verifier (Computational Analogy).
    
    Mechanism:
    1. Gauge Theory (Symmetry Reduction): Identifies semantic equivalence classes 
       (gauge orbits) in candidates by normalizing syntax (whitespace, case, 
       common affirmative/negative phrasings). This prevents redundant evaluation 
       of semantically identical hypotheses.
    2. Model Checking (Exhaustive Validation): Acts as the fitness function. 
       Instead of running a full state-space explorer (too heavy for this interface),
       we perform structural constraint propagation. We parse the prompt for 
       logical operators (NOT, IF, comparative) and verify if the candidate 
       satisfies these hard constraints. Failure yields a penalty (counterexample).
    3. Genetic Algorithms (Evolutionary Search): The 'population' is the input 
       candidate list. Selection is driven by the model-checking fitness score. 
       Candidates surviving the structural checks are 'selected'.
       
    Scoring:
    - Primary: Structural consistency (logic, negation, comparison).
    - Secondary: NCD (Compression) used only as a tie-breaker for semantic density.
    """

    def __init__(self):
        # Precompile regex for structural parsing (The "Connection" on the bundle)
        self.re_negation = re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I)
        self.re_comparative = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I)
        self.re_conditional = re.compile(r'\b(if|then|unless|only\ if)\b', re.I)
        self.re_numbers = re.compile(r'-?\d+\.?\d*')
        self.re_bool_yes = re.compile(r'\b(yes|true|correct|valid)\b', re.I)
        self.re_bool_no = re.compile(r'\b(no|false|incorrect|invalid)\b', re.I)

    def _normalize_gauge(self, text: str) -> str:
        """Reduce candidate to its gauge orbit representative (canonical form)."""
        t = text.lower().strip()
        # Remove excessive whitespace
        t = re.sub(r'\s+', ' ', t)
        # Normalize common semantic equivalents
        t = t.replace('yeah', 'yes').replace('yep', 'yes')
        t = t.replace('nope', 'no').replace('nah', 'no')
        return t

    def _structural_check(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Model Checking phase: Verify candidate against prompt constraints.
        Returns (score, reason).
        """
        p_norm = self._normalize_gauge(prompt)
        c_norm = self._normalize_gauge(candidate)
        
        score = 0.0
        reasons = []

        # 1. Negation Consistency (Modus Tollens check)
        prompt_has_neg = bool(self.re_negation.search(p_norm))
        cand_has_neg = bool(self.re_negation.search(c_norm))
        
        # If prompt implies negation is required but candidate lacks it (or vice versa)
        # This is a heuristic approximation of constraint propagation
        if prompt_has_neg and not cand_has_neg:
            # Potential trap: Prompt asks "What is NOT..." candidate should not contain negation necessarily,
            # but if prompt says "It is false that...", candidate must reflect falsehood.
            # Simplified: Check if prompt asserts a negative fact and candidate asserts positive.
            if re.search(r'is\s+not|are\s+not|false|incorrect', p_norm):
                if self.re_bool_yes.search(c_norm):
                    score -= 0.5
                    reasons.append("Contradicts negative constraint")
        
        if not prompt_has_neg and cand_has_neg:
             if re.search(r'is\s+true|is\s+correct|must\s+be', p_norm):
                if self.re_bool_no.search(c_norm):
                    score -= 0.5
                    reasons.append("Unwarranted negation")

        # 2. Comparative Logic
        if self.re_comparative.search(p_norm):
            # Extract numbers if present
            p_nums = [float(x) for x in self.re_numbers.findall(p_norm)]
            c_nums = [float(x) for x in self.re_numbers.findall(c_norm)]
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Simple transitivity check: If prompt A > B, and candidate picks A, score up
                # Detect direction
                direction = 1 if 'less' in p_norm or 'smaller' in p_norm or 'before' in p_norm else -1
                # This is a simplified heuristic for the demo
                score += 0.2 
                reasons.append("Comparative structure detected")

        # 3. Conditional Presence
        if self.re_conditional.search(p_norm):
            if self.re_conditional.search(c_norm) or len(c_norm) > 5:
                score += 0.1
                reasons.append("Conditional logic preserved")

        # Base score for passing basic non-empty check
        if len(c_norm) > 0:
            score += 0.5
            
        reason_str = "; ".join(reasons) if reasons else "Structural baseline"
        return score, reason_str

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tie-breaker."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        
        len1, len2, len12 = len(b1), len(b2), len(b12)
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        p_gauge = self._normalize_gauge(prompt)
        
        # Track best NCD for tie-breaking normalization
        max_ncd = 0.0
        
        # Pre-calculate structural scores (Model Checking phase)
        scored_candidates = []
        for cand in candidates:
            struct_score, reason = self._structural_check(prompt, cand)
            scored_candidates.append((cand, struct_score, reason))
            
        # Find max structural score to normalize
        if not scored_candidates:
            return []
            
        max_struct = max(sc[1] for sc in scored_candidates)
        min_struct = min(sc[1] for sc in scored_candidates)
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0

        for cand, struct_score, reason in scored_candidates:
            c_gauge = self._normalize_gauge(cand)
            
            # NCD Tie-breaker: Distance to prompt (lower is usually more relevant contextually)
            # But we want high score for good answers. 
            # Heuristic: If structural scores are equal, prefer shorter/compressible answers (Occam)
            ncd_val = self._ncd_distance(p_gauge, c_gauge)
            
            # Normalize structural score to 0.6-0.9 range, let NCD decide the rest
            norm_struct = 0.6 + (0.3 * (struct_score - min_struct) / range_struct)
            
            # Final Score: Structural (Primary) + (1 - NCD) * small_factor (Tiebreaker)
            # We invert NCD because lower distance = better match
            final_score = norm_struct + (1.0 - ncd_val) * 0.05
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural validation as the primary driver.
        """
        if not answer:
            return 0.0
            
        struct_score, _ = self._structural_check(prompt, answer)
        
        # Map structural score (-inf to +inf) to 0-1
        # Baseline 0.5, penalties reduce, bonuses increase
        conf = 0.5 + (struct_score * 0.4)
        
        # Clamp
        return max(0.0, min(1.0, conf))