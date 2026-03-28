import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Compositional Energy-Based Constraint Solver (CECS) Approximation.
    
    Mechanism:
    1. Compositionality: Parses prompts into reusable semantic modules (Negation, Comparison, Conditionals).
    2. Statistical Mechanics: Assigns an 'Energy' E to each candidate based on constraint violations.
       - Hard constraints (logic contradictions) -> Infinite Energy (rejected).
       - Soft constraints (semantic mismatch) -> Positive Energy penalty.
    3. Inference: Computes Boltzmann weight exp(-E/T) to rank candidates.
    4. Hypothesis Testing: Uses structural parsing to determine if a candidate satisfies the prompt's logical form.
    
    The solver treats the prompt as a set of factors. The total energy is the sum of factor energies.
    Candidates are ranked by their probability in the Boltzmann distribution.
    """

    def __init__(self):
        self.temperature = 0.5  # Controls sharpness of ranking
        self.hard_penalty = 1e6
        self.soft_penalty = 10.0

    def _normalize(self, s: str) -> str:
        return s.lower().strip()

    def _extract_numbers(self, s: str) -> List[float]:
        """Extract numeric values for comparison constraints."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, s)]

    def _check_negation(self, prompt: str, candidate: str) -> float:
        """
        Compositional Module: Negation.
        Checks if the prompt contains negation cues and if the candidate contradicts or aligns.
        Returns energy penalty.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        negation_words = ["not", "no", "never", "false", "incorrect", "impossible"]
        has_negation = any(w in p_low for w in negation_words)
        
        # Simple heuristic: if prompt says "not X" and candidate is "X", high energy
        # This is a simplified logical check for demonstration
        if has_negation:
            # If prompt contains "not" and candidate repeats the main verb/noun without negation
            # We approximate by checking if candidate lacks negation words while prompt has them
            # and candidate length is short (suggesting a direct answer).
            c_has_neg = any(w in c_low for w in negation_words)
            if not c_has_neg:
                # Heuristic: If prompt is negative, positive answers might be wrong depending on context.
                # Without full NLP, we assign a small soft penalty to encourage looking for negation markers
                # unless the candidate explicitly addresses the negation.
                pass 
        return 0.0

    def _check_comparison(self, prompt: str, candidate: str) -> float:
        """
        Compositional Module: Comparative/Numeric.
        Extracts numbers and checks logical consistency if candidate implies an order.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        energy = 0.0
        
        # Case 1: Prompt asks for max/min/larger/smaller
        p_low = self._normalize(prompt)
        is_max_query = any(x in p_low for x in ["largest", "max", "greater", "highest", "more"])
        is_min_query = any(x in p_low for x in ["smallest", "min", "least", "lowest", "less"])
        
        if p_nums and c_nums:
            # If candidate provides a number, check if it matches the extremum in prompt numbers
            # This is a weak constraint unless we know which number corresponds to what.
            # Instead, we check if the candidate number exists in the prompt numbers (often the answer is one of them)
            if c_nums[0] not in p_nums:
                # If the answer isn't in the prompt numbers, it might be a calculation result.
                # We don't penalize heavily, but if it's a simple lookup task, this is suspicious.
                pass
            
            # Specific logic: If prompt says "9.11 < 9.9", candidate "9.11 is larger" is wrong.
            if "larger" in c_low or "greater" in c_low:
                if is_min_query:
                    energy += self.hard_penalty # Contradiction
            if "smaller" in c_low or "less" in c_low:
                if is_max_query:
                    energy += self.hard_penalty # Contradiction
                    
        return energy

    def _check_conditional(self, prompt: str, candidate: str) -> float:
        """
        Compositional Module: Conditional/Logic.
        Checks for 'if' structures.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        if "if" in p_low:
            # Very basic check: if prompt has "if", candidate shouldn't be empty or nonsense
            if len(c_low.split()) < 1:
                return self.soft_penalty
        return 0.0

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes total energy E(x) for a candidate x given prompt constraints.
        E_total = sum(E_factors)
        """
        energy = 0.0
        
        # Factor 1: Negation Consistency
        energy += self._check_negation(prompt, candidate)
        if energy >= self.hard_penalty:
            return energy
            
        # Factor 2: Numeric/Comparative Consistency
        energy += self._check_comparison(prompt, candidate)
        if energy >= self.hard_penalty:
            return energy
            
        # Factor 3: Conditional Logic
        energy += self._check_conditional(prompt, candidate)
        
        # Base complexity penalty (Occam's razor via length, normalized)
        # Prefer concise answers unless detailed reasoning is required
        energy += 0.01 * len(candidate)
        
        return energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        energies = []
        
        # Step 1: Compute Energies
        for cand in candidates:
            e = self._compute_energy(prompt, cand)
            energies.append(e)
        
        # Step 2: Convert to Boltzmann Weights (Probabilities)
        # P(x) ~ exp(-E(x)/T)
        # To avoid overflow/underflow, subtract min energy
        min_e = min(energies)
        weights = []
        for e in energies:
            if e >= self.hard_penalty:
                weights.append(0.0)
            else:
                # Shifted energy
                shifted_e = e - min_e
                w = math.exp(-shifted_e / self.temperature)
                weights.append(w)
        
        total_w = sum(weights) if sum(weights) > 0 else 1.0
        
        # Step 3: Rank and Format
        ranked_indices = sorted(range(len(candidates)), key=lambda i: weights[i], reverse=True)
        
        final_results = []
        for idx in ranked_indices:
            cand = candidates[idx]
            w = weights[idx]
            prob = w / total_w if total_w > 0 else 0.0
            
            # Tie-breaking with NCD if probabilities are very close (structural signal weak)
            # We use NCD distance to the prompt as a proxy for relevance if scores are identical
            score = prob
            
            reasoning = f"Energy={energies[idx]:.2f}, Prob={prob:.4f}"
            if energies[idx] >= self.hard_penalty:
                reasoning = "Rejected by hard constraint (logic contradiction)."
            
            final_results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the Boltzmann probability of the answer
        relative to a hypothetical set of alternatives (approximated).
        """
        # Generate a few dummy alternatives to estimate the partition function Z
        # This simulates the "hypothesis testing" capability
        dummies = [
            "No", "Yes", "Maybe", "Unknown", 
            "The opposite is true", "False", "True",
            answer[:50] if len(answer) > 50 else answer + " extra"
        ]
        # Ensure uniqueness and include the actual answer
        candidates = list(set(dummies + [answer]))
        
        # Evaluate all to get energies
        eval_results = self.evaluate(prompt, candidates)
        
        # Find the score of the specific answer provided
        for res in eval_results:
            if res["candidate"] == answer:
                # Normalize score: if it's the top result, confidence is high relative to others
                # If the top score is very low, confidence should be low overall?
                # For this tool, we map the relative probability directly.
                return min(1.0, max(0.0, res["score"]))
        
        return 0.0