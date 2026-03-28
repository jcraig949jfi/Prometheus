import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Information-Directed Sampling (PIDS) Tool.
    
    Mechanism:
    1. Structural Parsing (Pragmatics Core): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt to form a 'Context Model'.
    2. Hypothesis Testing (Bandit Analogy): Treats candidates as arms. 
       - 'Information Gain': Estimated by how well the candidate satisfies structural constraints.
       - 'Pragmatic Score': Penalizes candidates that violate Gricean maxims (e.g., ignoring negations).
    3. Scoring: Candidates are ranked by a weighted sum of structural adherence (primary) 
       and NCD similarity (tiebreaker only).
    4. Confidence: Derived from the margin between the top candidate's score and the baseline.
    """

    def __init__(self):
        # Regex patterns for structural parsing (Pragmatic constraints)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'\d+\.?\d*')

    def _extract_structural_constraints(self, text: str) -> Dict[str, any]:
        """Extracts logical features to serve as the Pragmatic Context Model."""
        return {
            'has_negation': bool(self.negation_pattern.search(text)),
            'has_comparative': bool(self.comparative_pattern.search(text)),
            'has_conditional': bool(self.conditional_pattern.search(text)),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)]
        }

    def _check_candidate_alignment(self, candidate: str, constraints: Dict) -> float:
        """
        Checks if the candidate violates pragmatic constraints derived from the prompt.
        Returns a score: 1.0 (perfect alignment), 0.0 (violation), negative (strong violation).
        """
        score = 1.0
        cand_lower = candidate.lower()
        
        # Negation Check: If prompt has negation, candidate should ideally reflect it or not contradict it
        # Heuristic: If prompt says "not X" and candidate is "X", penalize.
        if constraints['has_negation']:
            # Simple heuristic: if candidate lacks negation words but prompt strongly implies exclusion
            # This is a proxy for "Relation" maxim.
            if not self.negation_pattern.search(candidate):
                # If the candidate is a simple "Yes" or repetition of a noun, it might be a trap
                if cand_lower in ['yes', 'true', 'correct']:
                    score -= 0.5 
        
        # Comparative Check: Ensure relative ordering makes sense if numbers are present
        if constraints['has_comparative'] and len(constraints['numbers']) >= 2:
            nums = constraints['numbers']
            # If prompt asks for "larger", and candidate contains the smaller number, penalize
            # This is a simplified logic check.
            if 'larger' in cand_lower or 'greater' in cand_lower or 'more' in cand_lower:
                # Expecting candidate to point to max number if it's a direct answer
                if any(str(int(n)) in candidate for n in nums if n != max(nums)):
                     score -= 0.3
            elif 'smaller' in cand_lower or 'less' in cand_lower:
                 if any(str(int(n)) in candidate for n in nums if n != min(nums)):
                    score -= 0.3

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Pragmatic Context Model (Structural Parsing)
        constraints = self._extract_structural_constraints(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            # 2. Compute Pragmatic Score (Primary Signal)
            # Does the candidate respect the logical structure (negations, etc)?
            pragmatic_score = self._check_candidate_alignment(cand, constraints)
            
            # 3. Compute Information Gain Proxy (Structural Match)
            # High overlap of key logical terms increases confidence
            struct_bonus = 0.0
            if constraints['has_negation'] and self.negation_pattern.search(cand):
                struct_bonus += 0.2
            if constraints['has_comparative'] and self.comparative_pattern.search(cand):
                struct_bonus += 0.1
            
            # 4. NCD as Tiebreaker (Only if structural signals are weak/equal)
            # We invert NCD (1 - ncd) to get similarity. 
            # Weight is low to ensure it only breaks ties or adds noise correction.
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            ncd_weight = 0.05 
            
            # Final Score Calculation
            # Primary: Pragmatic alignment (0 to 1) + Structural bonuses
            # Secondary: NCD similarity (tiny weight)
            final_score = (pragmatic_score + struct_bonus) + (ncd_sim * ncd_weight)
            
            # Reasoning trace
            reason = f"Pragmatic alignment: {pragmatic_score:.2f}. "
            if struct_bonus > 0:
                reason += "Structural match detected. "
            if ncd_weight > 0:
                reason += f"NCD tiebreaker applied."

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on the gap between the answer's score and a random baseline,
        normalized against the best possible candidate in a hypothetical set.
        """
        # Generate a synthetic set of alternatives to estimate the landscape
        # This simulates the "bandit" exploring other arms to see if 'answer' is truly optimal
        synthetic_candidates = [
            answer,
            "No", "Yes", "Unknown", "Maybe",
            # Invert negation if present
            re.sub(r'\b(not|no|never)\b', '', answer, flags=re.IGNORECASE),
            # Random noise
            "irrelevant response"
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for c in synthetic_candidates:
            if c not in seen and c.strip():
                seen.add(c)
                unique_candidates.append(c)
                
        ranked = self.evaluate(prompt, unique_candidates)
        
        if not ranked:
            return 0.0
            
        best_score = ranked[0]["score"]
        answer_score = next((item["score"] for item in ranked if item["candidate"] == answer), 0.0)
        
        # If the answer is the top ranked, confidence is high relative to the gap with #2
        if ranked[0]["candidate"] == answer:
            if len(ranked) > 1:
                gap = best_score - ranked[1]["score"]
                # Map gap to 0.5 - 1.0 range
                return min(1.0, 0.5 + gap)
            return 0.9 # Only one candidate, high confidence by default if it passed eval
            
        # If not top ranked, confidence drops based on how far behind it is
        max_possible = best_score + 0.1 # Hypothetical max
        normalized = max(0.0, answer_score / max_possible) if max_possible > 0 else 0.0
        return normalized * 0.4 # Cap non-top answers at 0.4