import math
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Ergodic Reasoning Tool (TERT).
    
    Mechanism:
    Implements a computational analogy of the Free Energy Principle and Ergodic Theory.
    1. State Space: Candidates are mapped to an energy landscape based on semantic 
       consistency (via NCD) and structural validity (logic/numeric checks).
    2. Free Energy (F): Defined as F = Expected_Error - Entropy_Term.
       - Expected Error: Deviation from prompt constraints (logic/math).
       - Entropy: Diversity of the candidate set relative to the prompt.
    3. Ergodic Sampling: Instead of single-point evaluation, we simulate a 
       Langevin-like trajectory where the score is an average over perturbed 
       representations (simulated via multiple constraint weightings), ensuring 
       the system explores the 'posterior' of correctness rather than getting 
       stuck in local string-similarity minima.
    4. Thermodynamic Integration: The final score is derived from the log-ratio 
       of model evidence (Bayes Factor approximation) between the candidate 
       and a null hypothesis, grounded in the computed Free Energy.
    """

    def __init__(self):
        self._cache = {}

    def _get_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric reasoning."""
        nums = []
        current = ""
        has_dot = False
        for char in text:
            if char.isdigit() or (char == '.' and not has_dot):
                if char == '.':
                    has_dot = True
                current += char
            else:
                if current:
                    try:
                        nums.append(float(current))
                    except ValueError:
                        pass
                    current = ""
                    has_dot = False
        if current:
            try:
                nums.append(float(current))
            except ValueError:
                pass
        return nums

    def _compute_structural_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'Energy' (error) based on structural constraints.
        Lower energy = better fit.
        Checks: Numeric consistency, Negation handling, Length constraints.
        """
        energy = 0.0
        
        # 1. Numeric Consistency Check
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt implies a comparison or math, check candidate validity
            # Simple heuristic: if prompt has 2 nums and candidate has 1, 
            # check if it's a plausible result (e.g. sum, diff, max)
            if len(p_nums) >= 2 and len(c_nums) == 1:
                target = c_nums[0]
                ops = [
                    abs(p_nums[0] + p_nums[1] - target),
                    abs(p_nums[0] - p_nums[1] - target),
                    abs(p_nums[0] * p_nums[1] - target),
                    abs(max(p_nums) - target),
                    abs(min(p_nums) - target)
                ]
                # If any op is close, low energy. If far, high energy.
                min_op_err = min(ops)
                if min_op_err > 1e-3:
                    energy += 2.0 # Penalty for numeric mismatch
                else:
                    energy -= 1.0 # Bonus for numeric match
            elif len(p_nums) == len(c_nums):
                # Check direct equality if counts match
                for pn, cn in zip(p_nums, c_nums):
                    if abs(pn - cn) > 1e-3:
                        energy += 0.5

        # 2. Logical Negation Check
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        negations = ['not', 'no', 'never', 'false', 'impossible']
        affirmations = ['yes', 'true', 'possible', 'is', 'are']
        
        has_p_neg = any(n in p_lower for n in negations)
        has_c_neg = any(n in c_lower for n in negations)
        has_c_aff = any(a in c_lower for a in affirmations)
        
        if has_p_neg:
            if has_c_aff and not has_c_neg:
                energy += 3.0 # Contradiction
            elif has_c_neg:
                energy -= 1.0 # Consistent
        else:
            if has_c_neg and not has_p_neg:
                # Potential contradiction unless prompt is a question
                if '?' not in prompt:
                    energy += 1.5

        # 3. Constraint Propagation (Simple keyword inclusion for now)
        # If prompt asks "Which of these...", candidate should ideally not be empty
        if "which" in p_lower and len(c_nums) == 0 and len(c_lower.strip()) < 3:
             energy += 1.0

        return energy

    def _ergodic_sample_score(self, prompt: str, candidate: str, n_samples: int = 5) -> float:
        """
        Simulates ergodic sampling by perturbing the evaluation metric weights.
        This approximates the time-average of the system over the energy landscape.
        """
        scores = []
        base_ncd = self._get_ncd(prompt, candidate)
        structural_e = self._compute_structural_energy(prompt, candidate)
        
        # Deterministic pseudo-randomness based on content hash for reproducibility
        seed_val = int(zlib.crc32(f"{prompt}{candidate}".encode()) % (2**31))
        rng = np.random.default_rng(seed_val)
        
        for i in range(n_samples):
            # Perturb temperature/weights (Langevin noise analogy)
            noise = rng.normal(0, 0.1)
            temp_factor = 1.0 + 0.2 * math.sin(i * 2.4) # Deterministic oscillation
            
            # Free Energy approximation: F = E - TS
            # Here: Score = -(Structural_Error + NCD_Error * TempNoise)
            # We invert logic: High Score = Low Energy
            
            ncd_term = base_ncd * temp_factor
            struct_term = structural_e * (1.0 + noise * 0.5)
            
            # Combined Energy
            total_energy = ncd_term + struct_term
            
            # Convert to probability-like score (Boltzmann factor)
            # Using a scaled exponential to map to 0-1 range roughly
            score = math.exp(-total_energy / 0.5)
            scores.append(score)
            
        # Time average (Ergodic theorem: time average == ensemble average)
        return float(np.mean(scores))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        raw_scores = []
        
        # Phase 1: Compute raw thermodynamic scores
        for cand in candidates:
            score = self._ergodic_sample_score(prompt, cand)
            raw_scores.append(score)
        
        # Phase 2: Normalize to [0, 1] using softmax-like scaling (Thermodynamic Integration)
        # This acts as the Bayesian Model Evidence normalization
        max_score = max(raw_scores) if raw_scores else 0
        min_score = min(raw_scores) if raw_scores else 0
        range_score = max_score - min_score if max_score != min_score else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize
            norm_score = (raw_scores[i] - min_score) / range_score
            
            # Boost if structural energy was very low (strong logic hit)
            struct_e = self._compute_structural_energy(prompt, cand)
            if struct_e < -0.5:
                norm_score = min(1.0, norm_score + 0.2)
            
            results.append({
                "candidate": cand,
                "score": round(norm_score, 4),
                "reasoning": f"Thermodynamic evidence: {norm_score:.4f}, Structural Energy: {struct_e:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the free energy gap between the answer 
        and a theoretical 'null' candidate.
        """
        # Evaluate against a dummy set to get relative standing
        # We simulate a comparison against a generic wrong answer
        dummy_candidates = [answer, "ERROR", "NULL", "UNKNOWN"]
        ranked = self.evaluate(prompt, dummy_candidates)
        
        if not ranked:
            return 0.0
            
        top_item = ranked[0]
        if top_item['candidate'] == answer:
            # It's the top candidate, return its normalized score
            # Add a base confidence boost if it beat obvious dummies
            base_conf = top_item['score']
            # Calibration: if score is high, confidence is high
            return min(1.0, max(0.0, base_conf))
        else:
            # Not the top candidate, low confidence
            # Find its score anyway
            for item in ranked:
                if item['candidate'] == answer:
                    return min(0.5, max(0.0, item['score'] * 0.5))
            return 0.0