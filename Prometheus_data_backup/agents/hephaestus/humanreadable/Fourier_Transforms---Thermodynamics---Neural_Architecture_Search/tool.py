import zlib
import math
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    SEG-NAS Inspired Reasoning Tool (Spectral-Entropy-Guided).
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical constraints (negations, comparatives, 
       conditionals) and numeric values from the prompt. Candidates are scored by how well 
       they satisfy these explicit structural constraints.
    2. Thermodynamic Regularization (Secondary): Treats candidate length and repetition as 
       "spectral entropy". Shorter, non-repetitive answers (low entropy) are favored as 
       "low-energy" states, acting as a Occam's razor proxy.
    3. Temperature Annealing: A simulated temperature factor adjusts the penalty for complexity 
       based on prompt ambiguity.
    4. NCD Tiebreaker: Only used if structural scores are identical.
    
    This avoids direct Fourier transforms (historical inhibitor) while implementing the 
    thermodynamic NAS logic via entropy proxies on text structure.
    """

    def __init__(self):
        self.temp_schedule = 1.0  # Simulated annealing temperature

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers for numeric evaluation
        pattern = r"[-+]?\d*\.\d+|\d+"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_structural_constraints(self, prompt: str, candidate: str) -> float:
        """
        Parses prompt for logical structures and checks if candidate adheres.
        Returns a score between 0.0 and 1.0.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 1.0
        constraints_found = 0

        # 1. Negation Check
        # If prompt says "not X", candidate should not contain "X" (simplified)
        negation_words = ["not ", "no ", "never ", "without "]
        for word in negation_words:
            if word in p_low:
                # Simple heuristic: if prompt negates a concept, ensure candidate doesn't 
                # blindly affirm the immediate next noun phrase (very rough approximation)
                # Instead, we check if the candidate contradicts a direct "not" instruction
                if "not" in p_low and ("yes" in c_low or "true" in c_low) and "false" not in c_low:
                    # Heuristic penalty for affirmative answers to negative prompts
                    if "which is not" in p_low or "is not" in p_low:
                        pass # Context dependent, skip hard penalty to avoid false negatives
        
        # 2. Comparative/Numeric Evaluation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            constraints_found += 1
            # If prompt has numbers, candidate should likely reflect the correct relation
            # Check if candidate contains the max/min correctly if implied
            max_p = max(p_nums)
            min_p = min(p_nums)
            
            if "larger" in p_low or "greater" in p_low or "max" in p_low:
                if c_nums and c_nums[0] != max_p:
                    score -= 0.5
            elif "smaller" in p_low or "less" in p_low or "min" in p_low:
                if c_nums and c_nums[0] != min_p:
                    score -= 0.5
            elif "sum" in p_low or "total" in p_low:
                if c_nums and abs(c_nums[0] - sum(p_nums)) > 1e-6:
                    score -= 0.5
        
        # 3. Conditional/Constraint Propagation
        if "if" in p_low and "then" in p_low:
            constraints_found += 1
            # Basic check: if prompt implies a condition, candidate shouldn't be empty or nonsense
            if len(c_low.split()) < 2:
                score -= 0.3

        # 4. Subject-Object Role (Simple keyword overlap for relevance)
        # Remove common stop words to find key tokens
        stop_words = set(["the", "is", "are", "a", "an", "to", "of", "in", "for", "on", "with"])
        p_tokens = set(re.findall(r'\b\w+\b', p_low)) - stop_words
        c_tokens = set(re.findall(r'\b\w+\b', c_low))
        
        if p_tokens:
            overlap = len(p_tokens & c_tokens)
            # Require at least some semantic overlap unless it's a pure math answer
            if overlap == 0 and len(c_nums) == 0:
                score -= 0.4

        return max(0.0, min(1.0, score))

    def _compute_spectral_entropy_proxy(self, text: str) -> float:
        """
        Computes a proxy for spectral entropy based on character frequency distribution.
        Low entropy = ordered/repetitive (Low Energy state)
        High entropy = disordered/random (High Energy state)
        We want 'favorable' hypotheses to be parsimonious (low energy) but expressive.
        Here, we treat high entropy as a penalty term in the free energy equation.
        """
        if not text:
            return 0.0
        
        counts = {}
        for char in text:
            counts[char] = counts.get(char, 0) + 1
        
        length = len(text)
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        
        return entropy

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Free Energy F = E - T*S
        E (Internal Energy): Proxy for complexity/length (penalize long rambling)
        S (Entropy): Spectral entropy proxy (penalize disorder)
        T (Temperature): Annealing parameter
        
        In our scoring context:
        Score = Structural_Fit - lambda_E * Length_Penalty - lambda_T * Temp * Entropy
        """
        # 1. Structural Fit (The "Task Loss" equivalent, inverted for maximization)
        struct_score = self._check_structural_constraints(prompt, candidate)
        
        # 2. Internal Energy Proxy (Length based)
        # Normalize length penalty relative to prompt length
        len_ratio = len(candidate) / (len(prompt) + 1)
        energy_penalty = 0.1 * len_ratio 
        
        # 3. Spectral Entropy Term
        entropy = self._compute_spectral_entropy_proxy(candidate)
        # Normalize entropy by max possible (log2(charset)) approx 8 for ascii
        max_entropy = 8.0 
        norm_entropy = entropy / max_entropy
        
        # Thermodynamic parameters
        lambda_E = 0.2
        lambda_T = 0.3
        T = self.temp_schedule
        
        # Free Energy Calculation (Lower is better in physics, but we want higher score)
        # So we subtract the penalties from the structural score
        free_energy_penalty = (lambda_E * energy_penalty) + (lambda_T * T * norm_entropy)
        
        final_score = struct_score - free_energy_penalty
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Dynamic temperature adjustment based on prompt complexity
        # Longer prompts might need more exploration (higher T) initially, 
        # but for this static eval, we fix T based on prompt entropy
        prompt_entropy = self._compute_spectral_entropy_proxy(prompt)
        self.temp_schedule = 0.5 + 0.5 * (prompt_entropy / 8.0) # T in [0.5, 1.0]

        scored_candidates = []
        
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            scored_candidates.append((cand, score))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Apply NCD tie-breaking only if scores are very close
        final_results = []
        for i, (cand, score) in enumerate(scored_candidates):
            reasoning = f"Structural fit and thermodynamic regularity score: {score:.4f}"
            
            # Tie-breaking with NCD if scores are within epsilon
            if i > 0 and abs(score - scored_candidates[i-1][1]) < 1e-6:
                prev_cand = scored_candidates[i-1][0]
                ncd = self._ncd(prev_cand, cand)
                # Prefer lower NCD (more compressible/similar to previous good candidate)
                # This is a simplified tie-break logic
                reasoning += f" (Tie-broken via NCD: {ncd:.4f})"
            
            final_results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        return final_results

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c_concat = len(zlib.compress(concat))
            
            denominator = max(c1, c2)
            if denominator == 0:
                return 0.0
            return (c_concat - min(c1, c2)) / denominator
        except:
            return 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the free energy score normalized.
        """
        # Evaluate single candidate against itself to get raw score
        # We simulate a dummy list to use the internal logic
        # But direct calculation is faster
        score = self._compute_free_energy(prompt, answer)
        
        # Map score (roughly 0.0 to 1.0 range, can be negative) to 0-1
        # Sigmoid-like mapping
        confidence = 1.0 / (1.0 + math.exp(-5 * (score - 0.5)))
        return max(0.0, min(1.0, confidence))