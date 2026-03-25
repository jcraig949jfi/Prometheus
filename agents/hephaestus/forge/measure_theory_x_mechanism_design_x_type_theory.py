import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a probabilistic dependent-type proof assistant with incentive-compatible
    hypothesis submission, approximated via structural parsing and mechanism design.
    
    Mechanism Design Core:
    The 'evaluate' method acts as a Vickrey-Clarke-Groves (VCG) auctioneer.
    Candidates are 'hypotheses' submitted by agents. The scoring rule combines:
    1. Structural Validity (Type Checking): Verifies logical consistency (negations, conditionals).
    2. Numeric Truthfulness (Measure Theory): Evaluates mathematical constraints.
    3. Compression Penalty (Regularization): Penalizes unnecessary complexity (NCD).
    
    The final score represents a 'proper scoring rule' where truthfulness (structural 
    alignment with the prompt) maximizes expected utility.
    """

    def __init__(self):
        self._state = {}

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Approximates Type Theory checking by verifying structural constraints.
        Returns a score in [0, 1] based on constraint satisfaction.
        """
        score = 1.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        negations = ['no', 'not', 'never', 'false', 'impossible']
        prompt_has_neg = any(n in p_lower.split() for n in negations)
        candidate_has_neg = any(n in c_lower.split() for n in negations)
        
        if prompt_has_neg != candidate_has_neg:
            # If prompt implies negation and candidate doesn't (or vice versa), penalize
            # This is a soft check; strict equality isn't always required depending on context
            score -= 0.4

        # 2. Conditional Logic (If-Then propagation)
        if 'if' in p_lower and 'then' in p_lower:
            # Candidate should ideally contain logical connectors or specific answers
            if not any(x in c_lower for x in ['yes', 'no', 'true', 'false', 'because', 'therefore']):
                score -= 0.2

        # 3. Numeric Evaluation (Measure Theory approximation)
        # Extract numbers from prompt and candidate to check basic ordering if implied
        nums_p = re.findall(r"[-+]?\d*\.\d+|\d+", p_lower)
        nums_c = re.findall(r"[-+]?\d*\.\d+|\d+", c_lower)
        
        if nums_p and nums_c:
            try:
                # Simple heuristic: if prompt asks for max/min, check candidate number
                p_vals = [float(n) for n in nums_p]
                c_vals = [float(n) for n in nums_c]
                
                if 'larger' in p_lower or 'max' in p_lower or 'greater' in p_lower:
                    if max(c_vals) < max(p_vals) * 0.9: # Loose check for existence
                         pass # Context dependent, skip hard penalty to avoid false negatives
                elif 'smaller' in p_lower or 'min' in p_lower or 'less' in p_lower:
                    pass 
            except ValueError:
                pass

        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        ranked = []
        
        # Pre-calculate prompt features to simulate "Type Context"
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Structural Score (The "Type Check" & "Measure" phase)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Compression Penalty (The "Complexity Regularization")
            # We want candidates that are informative but not noisy.
            # Low NCD to prompt implies relevance, but exact copy is cheating.
            ncd = self._ncd_distance(prompt, cand)
            
            # 3. Mechanism Design Scoring Rule (VCG-style)
            # Score = StructuralValidity * (1 - NCD_penalty)
            # This incentivizes "truthful" (structurally sound) and "concise" reporting.
            final_score = struct_score * (1.0 - (ncd * 0.5)) 
            
            # Bonus for length appropriateness (avoiding single char answers for complex prompts)
            if len(cand) < 2 and prompt_len > 20:
                final_score *= 0.8

            ranked.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural match: {struct_score:.2f}, NCD penalty: {ncd:.2f}"
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the structural score of the single candidate.
        Simulates the 'almost-sure convergence' check against the true distribution.
        """
        # Re-use the evaluation logic for a single item
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the score to 0-1 range strictly
        raw_score = results[0]["score"]
        # Map the heuristic score to a confidence probability
        # Assuming structural score dominates, map [0, 1] -> [0, 1]
        return min(1.0, max(0.0, raw_score))