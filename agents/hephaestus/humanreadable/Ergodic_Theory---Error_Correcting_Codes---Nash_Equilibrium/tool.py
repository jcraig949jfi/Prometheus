import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Noisy-Channel Co-evolutionary Game' for hypothesis testing.
    
    Mechanism:
    1. Structural Parsing (The Code): Extracts logical constraints (negations, comparatives,
       conditionals) acting as the 'syndrome' of the hypothesis. This provides robustness
       against noise (irrelevant text).
    2. Nash Equilibrium (The Game): Scores candidates based on a payoff function balancing
       'Decodability' (structural match to prompt constraints) and 'Complexity Cost' (length/entropy).
       This prevents drifting to trivially short but incorrect answers.
    3. Ergodic Validation: Uses NCD (Compression) as a tie-breaking convergence metric, 
       assuming that over the space of valid answers, the compressed distance converges 
       to the true semantic distance.
       
    This architecture forces the generator to find hypotheses that are both logically 
    consistent (high structural score) and informationally efficient (low NCD), mimicking 
    the equilibrium of the described theoretical system.
    """

    def __init__(self):
        # Thresholds for the "Game" payoffs
        self.negation_weight = 2.0
        self.comparative_weight = 1.5
        self.conditional_weight = 1.8
        self.length_penalty = 0.05

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical signatures (syndromes) from text."""
        lower_text = text.lower()
        
        # Detect Negations
        negations = len(re.findall(r'\b(not|no|never|neither|none|without|fail)\b', lower_text))
        
        # Detect Comparatives/Superlatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|larger|better|worse|than|most|least)\b', lower_text))
        
        # Detect Conditionals
        conditionals = len(re.findall(r'\b(if|then|unless|provided|otherwise|else)\b', lower_text))
        
        # Detect Numeric literals for evaluation
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        numeric_vals = []
        for n in numbers:
            try:
                numeric_vals.append(float(n))
            except ValueError:
                pass
                
        return {
            "negations": negations,
            "comparatives": comparatives,
            "conditionals": conditionals,
            "numbers": numeric_vals,
            "length": len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as the ergodic tiebreaker."""
        if not s1 or not s2:
            return 1.0
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except Exception:
            return 1.0

    def _calculate_payoff(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        Calculates the Nash payoff.
        High score = High structural alignment (Decodability) - Complexity Cost.
        """
        score = 0.0
        
        # 1. Decodability Score (Matching logical signatures)
        # If prompt has negations, valid answer should likely reflect understanding (simplified heuristic)
        # We reward candidates that have distinct structural features if the prompt implies complexity
        if prompt_struct["negations"] > 0:
            # Reward candidates that aren't empty and have specific structure
            score += (cand_struct["negations"] * self.negation_weight)
        
        if prompt_struct["comparatives"] > 0:
            score += (cand_struct["comparatives"] * self.comparative_weight)
            
        if prompt_struct["conditionals"] > 0:
            score += (cand_struct["conditionals"] * self.conditional_weight)

        # 2. Numeric Consistency Check (Constraint Propagation)
        # If both have numbers, check basic ordering consistency if possible
        if prompt_struct["numbers"] and cand_struct["numbers"]:
            # Heuristic: If prompt asks for "larger", candidate should ideally be larger.
            # Since we don't parse the specific question type perfectly, we reward 
            # candidates that contain numeric data when prompt does (signal of relevance).
            score += 1.0 

        # 3. Complexity Cost (Preventing trivial solutions)
        # Penalize extremely short answers unless they are perfect matches (handled by NCD later)
        cost = cand_struct["length"] * self.length_penalty
        if cand_struct["length"] < 3:
            cost += 0.5 # Heavy penalty for trivial answers like "Yes"
            
        return score - cost

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD for all candidates against prompt for tie-breaking
        # In a full ergodic system, this represents the time-averaged convergence
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._compute_ncd(prompt, cand))
            
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        min_ncd = min(ncd_scores) if ncd_scores else 0.0
        ncd_range = (max_ncd - min_ncd) if (max_ncd - min_ncd) > 1e-9 else 1.0

        for i, cand in enumerate(candidates):
            cand_struct = self._extract_structure(cand)
            
            # Primary Signal: Structural Payoff (The Game Equilibrium)
            payoff = self._calculate_payoff(prompt_struct, cand_struct, cand)
            
            # Secondary Signal: Ergodic Convergence (NCD Tiebreaker)
            # Normalize NCD to be a small modifier so it doesn't override logic
            # Lower NCD is better (more similar/compressible together)
            normalized_ncd = (ncd_scores[i] - min_ncd) / ncd_range 
            # Invert so lower NCD = higher score contribution
            ergodic_bonus = (1.0 - normalized_ncd) * 0.1 
            
            final_score = payoff + ergodic_bonus
            
            # Reasoning string generation
            reasoning = f"Structural Payoff: {payoff:.2f}. "
            if prompt_struct["negations"] > 0 and cand_struct["negations"] > 0:
                reasoning += "Matched negation logic. "
            if prompt_struct["numbers"] and cand_struct["numbers"]:
                reasoning += "Numeric consistency detected. "
            if final_score > 0:
                reasoning += "High decodability."
            else:
                reasoning += "Low structural alignment."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and compression stability.
        0.0 = Definitely wrong, 1.0 = Definitely correct.
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        # Calculate base payoff
        payoff = self._calculate_payoff(prompt_struct, ans_struct, answer)
        
        # Normalize payoff to 0-1 range roughly
        # Assume max possible payoff per component is around 5.0 for scaling
        base_conf = max(0.0, min(1.0, (payoff + 2.0) / 5.0))
        
        # Ergodic check: NCD distance
        ncd = self._compute_ncd(prompt, answer)
        # If NCD is very high (very different), reduce confidence unless payoff is huge
        if ncd > 0.8 and payoff < 1.0:
            base_conf *= 0.5
            
        return float(base_conf)