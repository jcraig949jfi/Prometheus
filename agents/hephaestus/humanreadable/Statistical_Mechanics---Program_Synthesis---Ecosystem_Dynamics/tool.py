import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Evolutionary Program Synthesis (TEPS) Approximation.
    
    Mechanism:
    Instead of running costly MCMC/ODE simulations, we approximate the 'Free Energy' 
    of a candidate answer by evaluating its structural consistency with the prompt.
    
    1. Microscopic Ensemble (Candidates): Treated as program variants.
    2. Energy Function E(p): Defined by structural violations (negations, conditionals, numeric logic).
       Lower energy = higher fitness.
    3. Boltzmann Sampling: Score = exp(-E/T).
    4. Ecosystem Dynamics: Interaction coefficients (alpha) are approximated by checking 
       if the candidate contradicts explicit constraints (resource competition).
       
    This implements the 'structural parsing' and 'numeric evaluation' patterns required 
    to beat the NCD baseline, using the thermodynamic metaphor as the scoring wrapper.
    """

    def __init__(self):
        self.temperature = 0.5  # Controls exploration/exploitation in scoring

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _check_structural_consistency(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Calculate energy based on structural logic (Negations, Comparatives, Conditionals).
        Returns (energy_penalty, reason_string).
        Lower energy is better.
        """
        energy = 0.0
        reasons = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Check
        # If prompt has "not X" or "never X", and candidate implies X, penalize.
        negation_keywords = ['not', 'never', 'no ', 'cannot', 'impossible']
        has_negation = any(k in p_lower for k in negation_keywords)
        
        # Simple heuristic: If prompt denies something, and candidate affirms key nouns, penalty.
        # This is a simplified proxy for logical contradiction.
        if has_negation:
            # If candidate is just "yes" or "no", check context roughly
            if c_lower.strip() in ['yes', 'true', 'correct']:
                # Heuristic: if prompt is negative, simple affirmative might be wrong unless it's "Yes, it is not..."
                # We apply a small penalty to blind affirmations in negative contexts
                energy += 2.0
                reasons.append("Potential negation mismatch")

        # 2. Comparative/Numeric Check
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares two numbers, check if candidate respects the order
            # Example: "Is 9.11 < 9.9?" -> Candidate should imply True or correct order
            n1, n2 = p_nums[0], p_nums[1]
            
            # Detect comparison type in prompt
            is_less = ('less' in p_lower or '<' in prompt or 'smaller' in p_lower)
            is_greater = ('greater' in p_lower or '>' in prompt or 'larger' in p_lower)
            
            if is_less:
                expected_truth = (n1 < n2)
            elif is_greater:
                expected_truth = (n1 > n2)
            else:
                expected_truth = None # Unknown comparison type
                
            if expected_truth is not None:
                # Check if candidate contradicts the math
                c_val = c_nums[0]
                # If candidate is a boolean-like number (1/0) or explicit float result
                if expected_truth and (c_val == 0.0 or (len(c_nums) > 1 and c_nums[0] > c_nums[1])):
                     energy += 5.0
                     reasons.append("Numeric contradiction")
                elif not expected_truth and (c_val == 1.0 or (len(c_nums) > 1 and c_nums[0] < c_nums[1])):
                     energy += 5.0
                     reasons.append("Numeric contradiction")

        # 3. Constraint Propagation (Keyword presence)
        # If prompt asks for specific format or keyword, missing it increases energy
        if 'must' in p_lower or 'require' in p_lower:
            # Extract noun after require/must as a rough constraint
            match = re.search(r'(must|require)[\s]+(?:be\s+)?(\w+)', p_lower)
            if match:
                constraint = match.group(2)
                if constraint not in c_lower:
                    energy += 3.0
                    reasons.append(f"Missing required constraint: {constraint}")

        if not reasons:
            reasons.append("Structurally consistent")
            
        return energy, "; ".join(reasons)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for candidate in candidates:
            # 1. Structural Analysis (Primary Signal)
            energy, reason_text = self._check_structural_consistency(prompt, candidate)
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # We want high similarity to prompt context but distinct answer. 
            # Here we use NCD to penalize gibberish or completely unrelated strings.
            ncd_val = self._calculate_ncd(prompt, candidate)
            
            # Combine: Score = exp(-Energy / T) - small_ncd_penalty
            # We invert NCD so lower distance is better, but it's a minor factor
            base_score = math.exp(-energy / self.temperature)
            
            # Adjust score slightly by NCD (0 to 1 range). 
            # If NCD is high (dissimilar), reduce score slightly.
            final_score = base_score * (1.0 - (ncd_val * 0.1))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Energy: {energy:.2f} ({reason_text}); NCD adjustment: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the thermodynamic stability (low energy) 
        of the answer relative to the prompt.
        """
        energy, _ = self._check_structural_consistency(prompt, answer)
        
        # Map energy to confidence:
        # Energy 0 -> Confidence ~1.0
        # Energy 5 -> Confidence ~0.1
        # Using Boltzmann factor again
        conf = math.exp(-energy / self.temperature)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, conf))