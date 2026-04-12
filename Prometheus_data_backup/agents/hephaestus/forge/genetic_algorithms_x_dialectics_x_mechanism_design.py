import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Evolutionary Mechanism-Design (DEMD) Tool.
    
    Mechanism:
    1. Thesis (Candidate Evaluation): Parses structural logic (negations, comparatives, 
       conditionals, numeric constraints) from the prompt to establish a 'Truth Protocol'.
    2. Antithesis (Adversarial Critique): A mechanism-design layer where candidates are 
       penalized for violating the Truth Protocol. It acts as a 'red-team' checking for 
       logical inconsistencies (e.g., answering 'Yes' to a negative constraint).
    3. Synthesis (Scoring): Combines structural adherence (primary) with NCD similarity 
       (tiebreaker) to produce a robust score.
    
    This implements the 'Mechanism Design' as the core driver, using 'Dialectics' for 
    validation and 'Genetic Algorithms' conceptually for selecting the fittest candidate.
    """

    def __init__(self):
        # Structural keywords for dialectical analysis
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'unless', 'only if', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', '1']
        self.bool_no = ['no', 'false', 'incorrect', '0']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_structural_logic(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Thesis-Antithesis Check:
        - Thesis: The candidate must align with the prompt's structural constraints.
        - Antithesis: The critic looks for contradictions (e.g., prompt says 'not', candidate says 'yes').
        Returns a score (0.0 to 1.0) and a reasoning string.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 1.0
        reasons = []

        # 1. Negation Handling (Modus Tollens check)
        # If prompt has strong negation and candidate is affirmative without qualification
        has_negation = any(n in p_low.split() for n in self.negations)
        is_affirmative = any(y in c_low.split() for y in self.bool_yes)
        is_negative = any(n in c_low.split() for n in self.bool_no)

        if has_negation and is_affirmative and not is_negative:
            # Potential trap: Prompt says "It is not X", Candidate says "Yes"
            # Heuristic penalty unless candidate explicitly references the negation
            if not any(n in c_low for n in self.negations):
                score -= 0.4
                reasons.append("Failed negation check (affirmative response to negative constraint).")

        # 2. Comparative Logic
        # Detect patterns like "Is A greater than B?" and check if candidate implies direction
        has_comparative = any(c in p_low for c in self.comparatives)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)

        if has_comparative and len(p_nums) >= 2:
            # Simple heuristic: If prompt asks "greater", and numbers are present, 
            # check if the candidate preserves the order or answers correctly based on context.
            # Since we don't have full semantic parse, we check for consistency in number presence.
            if len(c_nums) == 0:
                # If candidate doesn't mention numbers in a numeric comparison question, slight penalty
                score -= 0.1
                reasons.append("Numeric comparison detected but no numbers in candidate.")
        
        # 3. Conditional Consistency
        has_conditional = any(c in p_low for c in self.conditionals)
        if has_conditional:
            # If prompt is conditional, simple "Yes/No" might be insufficient (Hedge penalty)
            if len(c_low.split()) <= 2 and (is_affirmative or is_negative):
                score -= 0.15
                reasons.append("Conditional prompt requires nuanced answer; simple binary may be insufficient.")

        if not reasons:
            reasons.append("Structural constraints satisfied.")
        
        return max(0.0, score), "; ".join(reasons)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0:
                return 1.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        p_norm = self._normalize(prompt)
        
        # Baseline NCD for tie-breaking context relevance
        # We compare candidate to prompt to see if it's relevant (low NCD usually good, 
        # but too low might be echo. We use it as a secondary signal).
        
        for cand in candidates:
            c_norm = self._normalize(cand)
            
            # Primary Signal: Structural Logic (Mechanism Design Core)
            logic_score, logic_reason = self._check_structural_logic(prompt, cand)
            
            # Secondary Signal: NCD (Tiebreaker/Relevance)
            # Invert NCD so higher is better (similarity), but penalize exact echoes if too short
            ncd_val = self._ncd_distance(p_norm, c_norm)
            ncd_score = 1.0 - ncd_val
            
            # Synthesis: Weighted combination
            # Logic is the driver (weight 0.8), NCD is the tiebreaker (weight 0.2)
            final_score = (logic_score * 0.8) + (ncd_score * 0.2)
            
            # Bonus for length consistency (avoiding single char answers for complex prompts)
            if len(c_norm.split()) < 2 and len(p_norm.split()) > 10:
                final_score *= 0.9 

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Logic: {logic_reason} | NCD-Sim: {ncd_score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single candidate.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly, assuming max possible is ~1.0
        return min(1.0, max(0.0, res[0]["score"]))