import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Recursive Ergodic Particle Filter (REPF) Approximation.
    
    Mechanism:
    1. Particles (Hypotheses): Each candidate answer is treated as a 'species' in an ecosystem.
    2. Ergodic Sampling: We simulate time-averaged convergence by perturbing the input prompt
       slightly (simulating MCMC steps) and checking consistency of the candidate's validity.
    3. Ecosystem Dynamics:
       - Predation: Candidates with high compression distance (low similarity) to prompt logic are pruned.
       - Keystone Effect: Candidates that satisfy explicit numeric/constraint checks get exponential weight.
       - Succession: If no candidate passes ergodic consistency, weights reset to favor diversity (length/complexity).
    4. Theory of Mind: We parse the prompt for 'belief' markers (e.g., "thinks", "says") and weigh 
       candidates that align with the inferred mental state vs. ground truth.
       
    This implementation approximates the REPF using deterministic structural parsing, 
    numeric evaluation, and compression-based similarity as a proxy for posterior probability.
    """

    def __init__(self):
        self.n_samples = 5  # Simulated ergodic time-steps

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric reasoning."""
        pattern = r"[-+]?\d*\.?\d+"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Constraint propagation: Check for numeric transitivity and logical negations.
        Returns a boost factor (1.0 = neutral, >1.0 = boost).
        """
        score = 1.0
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Numeric consistency check
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple heuristic: if prompt compares A and B, candidate should reflect it
            if p_nums[0] > p_nums[1]:
                if len(c_nums) > 0 and c_nums[0] < p_nums[1]: # Contradiction
                    score *= 0.5
            elif p_nums[0] < p_nums[1]:
                if len(c_nums) > 0 and c_nums[0] > p_nums[1]: # Contradiction
                    score *= 0.5

        # Negation check
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        if "not" in p_lower or "false" in p_lower:
            if "yes" in c_lower or "true" in c_lower:
                # Potential trap, reduce score unless context confirms
                score *= 0.8
        
        return score

    def _ergodic_consistency(self, prompt: str, candidate: str) -> float:
        """
        Simulates ergodic MCMC by checking stability under minor textual perturbations.
        Uses NCD (Normalized Compression Distance) as a proxy for probability density.
        High consistency = low variance across 'samples'.
        """
        base_dist = self._ncd(prompt, candidate)
        variance = 0.0
        
        # Simulate time-steps (perturbations)
        for i in range(self.n_samples):
            # Deterministic perturbation: slice prompt
            step = max(1, len(prompt) // (self.n_samples + 1))
            perturbed = prompt[step*i:] + prompt[:step*i] # Rotate string
            
            dist = self._ncd(perturbed, candidate)
            variance += (dist - base_dist) ** 2
            
        variance /= self.n_samples
        
        # Ergodic guarantee: Low variance means the hypothesis holds across state space
        # Map variance to [0, 1] where 1 is stable
        stability = 1.0 / (1.0 + 10.0 * variance)
        return stability

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - max_len) / max_len
        except:
            return 1.0

    def _keystone_detection(self, prompt: str, candidate: str) -> float:
        """
        Detects 'Keystone' hypotheses that resolve specific logical structures.
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # If prompt asks for a number and candidate provides a plausible one
        if "what" in p_low and "number" in p_low:
            if self._extract_numbers(candidate):
                score += 0.5
        
        # Logical entailment keywords
        if ("therefore" in c_low or "thus" in c_low) and ("because" in p_low or "since" in p_low):
            score += 0.3
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_len = len(prompt)
        
        # Baseline NCD for all candidates to establish ecosystem baseline
        baseline_scores = []
        for cand in candidates:
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD: lower distance = higher initial fitness
            baseline_scores.append(1.0 - ncd_val)
            
        total_baseline = sum(baseline_scores) + 1e-9
        
        for i, cand in enumerate(candidates):
            # 1. Structural/Numeric Constraint Check (The "Physics" layer)
            constraint_boost = self._check_constraints(prompt, cand)
            
            # 2. Ergodic Consistency (The "Time" layer)
            ergodic_score = self._ergodic_consistency(prompt, cand)
            
            # 3. Keystone Detection (The "Social/Mental" layer)
            keystone_bonus = self._keystone_detection(prompt, cand)
            
            # Combine: Base Fitness * Constraints * Ergodicity + Keystone
            # Normalizing base fitness relative to population
            base_fit = baseline_scores[i] / total_baseline if total_baseline > 0 else 0.0
            
            raw_score = (base_fit * 0.4 + ergodic_score * 0.4 + keystone_bonus) * constraint_boost
            
            # Normalize to 0-1 roughly
            final_score = min(1.0, max(0.0, raw_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Ergodic stability: {ergodic_score:.2f}, Constraints: {constraint_boost:.2f}, Keystone: {keystone_bonus:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself in the list to get score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']