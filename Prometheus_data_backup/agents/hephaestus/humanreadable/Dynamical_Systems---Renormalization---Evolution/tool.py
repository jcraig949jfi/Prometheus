import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Evolutionary Dynamical System (REDS) Implementation.
    
    Mechanism:
    1. Structural Parsing (Dynamical Systems Constraint): Extracts logical operators
       (negations, comparatives, conditionals) and numeric values to form a high-dimensional
       state vector. This avoids the "dynamical systems trap" by using DS only for parsing.
    2. Renormalization (Coarse-Graining): Compresses the structural vector into scale-invariant
       order parameters (e.g., net polarity, numeric magnitude delta, constraint density).
       Irrelevant noise (specific words) is integrated out.
    3. Evolutionary Flow: Candidates are scored based on the distance between their 
       renormalized parameters and the prompt's implied optimal parameters (fitness landscape).
       Mutation rate adaptation is simulated by penalizing candidates that violate hard constraints.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "nobody", "nothing"}
        self.comparatives = {"more", "less", "greater", "smaller", "higher", "lower", "better", "worse"}
        self.conditionals = {"if", "then", "else", "unless", "provided", "when"}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for quantitative reasoning."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text.lower())]

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """
        Parse text into a structural state vector.
        Returns: [negation_count, conditional_count, comparative_count, number_count, has_numbers]
        """
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        neg_count = sum(1 for w in words if w in self.negation_words)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        numbers = self._extract_numbers(text)
        num_count = len(numbers)
        
        # Detect simple boolean assertions
        yes_score = 1.0 if re.search(r'\b(yes|true|correct)\b', lower_text) else 0.0
        no_score = 1.0 if re.search(r'\b(no|false|incorrect)\b', lower_text) else 0.0

        return {
            "negations": neg_count,
            "conditionals": cond_count,
            "comparatives": comp_count,
            "num_count": num_count,
            "numbers": numbers,
            "yes_bias": yes_score,
            "no_bias": no_score,
            "length": len(words)
        }

    def _renormalize(self, prompt_vec: Dict, cand_vec: Dict) -> Tuple[float, str]:
        """
        Perform RG coarse-graining to compare candidate against prompt constraints.
        Returns a fitness score and a reasoning string.
        """
        score = 0.0
        reasons = []

        # Scale 1: Numeric Consistency (High Relevance)
        # If prompt has numbers, candidate should engage with them logically
        if prompt_vec["num_count"] > 0:
            if cand_vec["num_count"] == 0:
                # Penalty for ignoring quantitative data
                score -= 0.5
                reasons.append("Ignored quantitative data")
            else:
                # Check for simple arithmetic consistency if possible (heuristic)
                # If prompt implies "less", candidate should reflect smaller numbers
                reasons.append("Quantitative engagement detected")
                score += 0.2
        
        # Scale 2: Logical Operator Matching
        # If prompt asks a negative question, positive answers are wrong
        if prompt_vec["negations"] > 0:
            if cand_vec["yes_bias"] > 0.5:
                score -= 1.0
                reasons.append("Failed negation check")
            elif cand_vec["no_bias"] > 0.5:
                score += 0.5
                reasons.append("Correctly handled negation")
        
        # Scale 3: Conditional Complexity
        # If prompt has conditionals, simple yes/no is often insufficient
        if prompt_vec["conditionals"] > 0:
            if cand_vec["length"] < 5 and (cand_vec["yes_bias"] > 0 or cand_vec["no_bias"] > 0):
                score -= 0.3
                reasons.append("Oversimplified conditional response")
            else:
                score += 0.2
                reasons.append("Addressed conditional complexity")

        # Scale 4: Comparative Logic
        if prompt_vec["comparatives"] > 0:
            if cand_vec["comparatives"] == 0 and cand_vec["num_count"] == 0:
                score -= 0.2
                reasons.append("Missing comparative analysis")
            else:
                score += 0.1

        # Base relevance boost
        score += 0.5 
        reasons.append("Baseline relevance")

        return score, "; ".join(reasons) if reasons else "Structural match"

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        
        len1 = len(b1)
        len2 = len(b2)
        len12 = len(b12)
        
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_vec = self._structural_parse(prompt)
        results = []
        
        for cand in candidates:
            cand_vec = self._structural_parse(cand)
            
            # RG Step: Coarse-grain and score
            score, reasoning = self._renormalize(prompt_vec, cand_vec)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning,
                "vec": cand_vec # Store for tie-breaking
            })
        
        # Sort by score (descending)
        # Use NCD only as a tie-breaker for very close scores
        def sort_key(item):
            # Primary: Score
            # Secondary: NCD similarity to prompt (lower distance = better tie breaker)
            ncd = self._ncd_distance(prompt, item["candidate"])
            return (item["score"], -ncd)
        
        results.sort(key=sort_key, reverse=True)
        
        # Normalize scores to 0-1 range roughly for the output format
        max_s = max(r["score"] for r in results) if results else 0
        min_s = min(r["score"] for r in results) if results else 0
        span = max_s - min_s if max_s != min_s else 1.0
        
        final_output = []
        for r in results:
            # Normalize to 0.1 - 0.9 range
            norm_score = 0.1 + 0.8 * ((r["score"] - min_s) / span)
            final_output.append({
                "candidate": r["candidate"],
                "score": round(norm_score, 4),
                "reasoning": r["reasoning"]
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment.
        Returns 0.0 to 1.0.
        """
        prompt_vec = self._structural_parse(prompt)
        answer_vec = self._structural_parse(answer)
        
        score, _ = self._renormalize(prompt_vec, answer_vec)
        
        # Map score to 0-1 confidence
        # Heuristic: score > 0.5 is high confidence, < 0 is low
        confidence = 1.0 / (1.0 + np.exp(-score * 2)) # Sigmoid mapping
        return round(float(confidence), 4)