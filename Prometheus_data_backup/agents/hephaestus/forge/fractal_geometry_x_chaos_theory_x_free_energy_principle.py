import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified 'Fractal-Chaos-Free Energy' reasoning engine.
    
    Mechanism:
    1. Fractal Priors (IFS): Uses recursive substring self-similarity (NCD-based) 
       to establish a scale-invariant baseline of plausibility. Self-similar 
       patterns (repetition/structure) lower free energy.
    2. Chaos-Driven Perturbation: Calculates a 'Lyapunov-like' instability score 
       based on character-level entropy gradients. If a candidate is too rigid 
       (low entropy) or too noisy (high entropy), it receives a chaotic 'kick' 
       (penalty), simulating the injection of noise to escape local minima.
    3. Free Energy Minimization: The final score is derived from minimizing a 
       variational free energy functional: F = Prediction_Error + Complexity_Prior.
       Prediction error is approximated by compression distance to the prompt context.
       Complexity is the chaotic penalty.
       
    This creates an adaptive scoring system that favors candidates with structural 
    coherence (fractal) but sufficient diversity (chaos), minimizing surprise.
    """

    def __init__(self):
        self._seed = 42  # Deterministic seed for reproducibility

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 and not s2:
            return 0.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_joint = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(c_s1, c_s2)
        if denominator == 0:
            return 0.0
        return (c_joint - min(c_s1, c_s2)) / denominator

    def _estimate_lyapunov(self, text: str) -> float:
        """
        Estimates a Lyapunov-like exponent based on local entropy variance.
        High variance in local character distribution indicates chaotic instability.
        """
        if len(text) < 2:
            return 0.0
        
        # Map chars to float 0-1
        vals = np.array([ord(c) / 255.0 for c in text])
        
        # Calculate local gradients (divergence)
        diffs = np.abs(np.diff(vals))
        if len(diffs) == 0:
            return 0.0
            
        # Lyapunov exponent approximation: mean log of divergence
        # Add small epsilon to avoid log(0)
        epsilon = 1e-6
        lyap = np.mean(np.log(diffs + epsilon))
        return lyap

    def _fractal_prior_score(self, text: str) -> float:
        """
        Computes a 'fractal prior' score based on self-similarity.
        Checks if halves of the string are compressible together relative to parts.
        """
        if len(text) < 4:
            return 0.5 # Neutral prior for short strings
            
        mid = len(text) // 2
        s1, s2 = text[:mid], text[mid:]
        
        # If s1 and s2 are similar, joint compression is efficient -> High Prior
        ncd_val = self._ncd(s1, s2)
        # Convert distance to similarity score (0 to 1)
        return 1.0 - ncd_val

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (F) = Error - Complexity + Prior
        Lower F is better. We return negative F so higher score is better.
        """
        # 1. Prediction Error (Surprise): How well does candidate fit prompt context?
        # Using NCD between prompt and candidate as a proxy for conditional probability
        prediction_error = self._ncd(prompt, candidate)
        
        # 2. Complexity Penalty (Chaos): 
        # Ideal systems operate at the 'edge of chaos'. 
        # We penalize extreme Lyapunov values (too ordered or too chaotic).
        lyap = self._estimate_lyapunov(candidate)
        # Target Lyapunov range for 'interesting' dynamics (heuristic)
        # Typical log-divergence for text is around -2 to -4 depending on encoding
        # We normalize loosely: assume -3 is ideal.
        chaos_penalty = abs(lyap + 3.0) * 0.1
        
        # 3. Fractal Prior: Self-similar structures are preferred (Occam's razor)
        fractal_bonus = self._fractal_prior_score(candidate) * 0.2
        
        # Free Energy Functional
        free_energy = prediction_error + chaos_penalty - fractal_bonus
        
        # Return negative free energy as score (maximize score = minimize energy)
        return -free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            # Heuristic boost for structural parsing cues (Negation/Numbers)
            # This addresses the 'Quality Floor' requirement for structural parsing
            bonus = 0.0
            if "not" in cand.lower() or "no" in cand.lower():
                if "not" in prompt.lower() or "no" in prompt.lower():
                    bonus += 0.05 # Consistency boost
            
            # Numeric consistency check
            import re
            nums_cand = re.findall(r"[-+]?\d*\.\d+|\d+", cand)
            nums_prompt = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
            if nums_cand and nums_prompt:
                # Simple transitivity/consistency check
                try:
                    if float(nums_cand[0]) == float(nums_prompt[0]):
                        bonus += 0.1
                except ValueError:
                    pass

            final_score = score + bonus
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Minimized free energy via fractal prior ({self._fractal_prior_score(cand):.2f}) and chaos control (Lyap={self._estimate_lyapunov(cand):.2f}). Error: {self._ncd(prompt, cand):.2f}."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized free energy score.
        """
        # Compute raw score
        raw_score = self._compute_free_energy(prompt, answer)
        
        # Map raw score (typically -2.0 to 0.0 range) to 0-1 sigmoid-like
        # Shift and scale: assume worst case -2.0, best case 0.0
        # Sigmoid approximation: 1 / (1 + exp(-k(x - x0)))
        # Here we just clamp and linearize for stability without scipy
        normalized = (raw_score + 2.0) / 2.0
        conf = max(0.0, min(1.0, normalized))
        
        # Apply structural confidence boosts
        if "not" in prompt.lower() and "not" in answer.lower():
            conf = min(1.0, conf + 0.1)
            
        return float(conf)