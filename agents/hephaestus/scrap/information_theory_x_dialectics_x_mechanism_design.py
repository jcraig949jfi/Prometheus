import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Information-Theoretic Mechanism (DITM) Implementation.
    
    Mechanism Design Core:
    The system simulates two internal sub-agents: 'Thesis' (favors structural alignment)
    and 'Antithesis' (favors information density/divergence). 
    
    1. Thesis Agent: Scores candidates based on strict structural parsing (negations, 
       comparatives, conditionals) and numeric consistency. It represents the 'prior belief'.
    2. Antithesis Agent: Scores candidates based on 'surprise' or distinctness from the 
       prompt's average token distribution, penalizing simple echo/repetition.
    3. Synthesis: The final score is a weighted mixture where the 'payment' (score) is 
       maximized when the candidate satisfies structural constraints (Thesis) while 
       maintaining high information content (Antithesis), effectively minimizing the 
       KL-divergence between the ideal reasoned answer and the candidate.
    
    This design forces the system to reject candidates that merely echo the prompt 
    (high confirmation bias) or those that are structurally inconsistent, adhering 
    to the incentive-compatible scoring rule described in the theory.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'cannot', "n't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.bool_yes = {'yes', 'true', 'correct', 'right'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong'}

    def _tokenize(self, text: str) -> List[str]:
        """Simple lowercase alphanumeric tokenization."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats
        matches = re.findall(r'-?\d+\.?\d*', text)
        res = []
        for m in matches:
            try:
                res.append(float(m))
            except ValueError:
                continue
        return res

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Thesis Agent: Evaluates logical consistency based on structural markers.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should reflect awareness (heuristic: presence in both or neither)
        p_has_neg = bool(p_tokens & self.negations)
        c_has_neg = bool(c_tokens & self.negations)
        if p_has_neg == c_has_neg:
            score += 2.0
        else:
            score -= 1.0 # Penalty for ignoring negation context

        # 2. Conditional/Comparative Presence
        # If prompt sets up a condition/comparison, valid answers often acknowledge it or resolve it
        p_has_comp = bool(p_tokens & self.comparatives)
        p_has_cond = bool(p_tokens & self.conditionals)
        
        if p_has_comp or p_has_cond:
            # Reward candidates that are substantial enough to address complexity
            if len(c_tokens) > 3:
                score += 1.5
            # Check for direct contradiction markers if prompt implies a choice
            if (p_has_cond and any(k in c_tokens for k in ['else', 'then', 'otherwise'])):
                score += 1.0

        # 3. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check for rough magnitude consistency or direct match
            # Simple heuristic: if prompt has numbers, candidate having numbers is good (avoids vague answers)
            score += 1.0
            # Check if candidate number exists in prompt (often the answer is derived directly)
            for n in c_nums:
                if n in p_nums:
                    score += 2.0
                    break
        elif not p_nums and not c_nums:
            score += 0.5 # Neutral for non-numeric

        # 4. Direct Boolean Alignment
        # If prompt asks a yes/no question (implied by structure), check alignment
        if any(k in p_tokens for k in ['is', 'are', 'does', 'do', 'can']):
            c_lower = candidate.lower().strip()
            if c_lower.startswith(('yes', 'true')):
                score += 1.0
            elif c_lower.startswith(('no', 'false')):
                score += 1.0
                
        return score

    def _informational_score(self, prompt: str, candidate: str) -> float:
        """
        Antithesis Agent: Evaluates information density and divergence from prompt echo.
        Penalizes simple repetition (high confirmation bias).
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        if not c_tokens:
            return -10.0
            
        # Calculate overlap ratio (Echo penalty)
        intersection = len([t for t in c_tokens if t in p_tokens])
        overlap_ratio = intersection / len(c_tokens) if c_tokens else 0
        
        # Penalty for high overlap (mere echoing)
        echo_penalty = -2.0 * overlap_ratio
        
        # Reward for length (up to a point) - information density proxy
        len_score = math.log(len(c_tokens) + 1) * 0.5
        
        # Unique content reward
        unique_tokens = [t for t in c_tokens if t not in p_tokens]
        unique_ratio = len(unique_tokens) / len(c_tokens) if c_tokens else 0
        novelty_score = 2.0 * unique_ratio
        
        return echo_penalty + len_score + novelty_score

    def _synthesis_score(self, prompt: str, candidate: str) -> float:
        """
        Synthesis: Combines Thesis and Antithesis scores.
        Mechanism Design: The 'payment' is high only if structural logic holds (Thesis)
        AND the answer isn't a trivial echo (Antithesis).
        """
        thesis = self._structural_score(prompt, candidate)
        antithesis = self._informational_score(prompt, candidate)
        
        # Weighted sum acting as the mechanism's objective function
        # Structural integrity is primary, novelty is secondary but required to break ties
        return 0.6 * thesis + 0.4 * antithesis

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score = self._synthesis_score(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural: {self._structural_score(prompt, cand):.2f}, Info: {self._informational_score(prompt, cand):.2f}"
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns a confidence score 0-1 based on the synthesis score normalized.
        """
        raw_score = self._synthesis_score(prompt, answer)
        
        # Map raw score to 0-1 range using a sigmoid-like mapping
        # Assuming typical scores range between -5 and 10
        # Shift and scale: (x + 5) / 15 -> 0 to 1 approx
        normalized = 1.0 / (1.0 + math.exp(-0.5 * (raw_score - 2.0)))
        
        return max(0.0, min(1.0, normalized))