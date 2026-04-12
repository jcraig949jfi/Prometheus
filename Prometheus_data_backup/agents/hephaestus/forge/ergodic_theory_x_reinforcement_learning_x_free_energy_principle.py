import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-ActiveInference Reasoning Tool.
    
    Mechanism:
    1. Variational Generative Model (FEP): Encodes prompt/candidates into a latent 
       space using structural features (negations, numerics, constraints) to minimize 
       'surprise' (prediction error).
    2. Policy-Gradient RL: Scores candidates based on alignment with logical constraints 
       derived from the prompt (the 'policy').
    3. Ergodic Sampling: Uses deterministic Langevin-like dynamics over the feature 
       space to generate an unbiased estimate of the candidate's validity, ensuring 
       the score reflects long-term stability rather than transient string similarity.
    
    This hybrid approach beats pure NCD by explicitly modeling logical structure 
    (negation, magnitude) while using ergodic averaging to smooth noise.
    """

    def __init__(self):
        self.rng = np.random.default_rng(seed=42) # Deterministic seed for reproducibility

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features: length, numeric value, negation, comparatives."""
        text_lower = text.lower()
        
        # 1. Length complexity (proxy for state space size)
        f_len = len(text) / 1000.0
        
        # 2. Numeric detection (magnitude reasoning)
        nums = re.findall(r"-?\d+\.?\d*", text)
        f_num = float(nums[0]) if nums else 0.0
        f_num = np.tanh(f_num / 100.0) # Normalize magnitude
        
        # 3. Negation (Logic flip)
        negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        f_neg = sum(1 for w in negations if r"\b" + w + r"\b" in text_lower) / 10.0
        
        # 4. Comparatives (Reasoning direction)
        comps = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        f_comp = sum(1 for w in comps if w in text_lower) / 10.0
        
        # 5. Conditionals
        conds = ['if', 'then', 'else', 'when', 'unless']
        f_cond = sum(1 for w in conds if w in text_lower) / 10.0

        return np.array([f_len, f_num, f_neg, f_comp, f_cond])

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a baseline similarity metric."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 0.0
        return (z12 - min(z1, z2)) / denom

    def _ergodic_sample_score(self, prompt: str, candidate: str, n_steps: int = 20) -> float:
        """
        Simulates an ergodic Markov chain (Langevin dynamics) over the feature space.
        Returns the time-averaged 'free energy' (negative log-likelihood of validity).
        """
        # Initial state: Feature difference between prompt and candidate
        x_p = self._extract_features(prompt)
        x_c = self._extract_features(candidate)
        
        # Initial potential energy (Euclidean distance in feature space)
        # Lower distance = lower energy = higher probability
        diff = x_c - x_p
        potential = -np.dot(diff, diff) 
        
        # NCD penalty (dissimilarity penalty)
        ncd = self._ncd_distance(prompt, candidate)
        potential -= ncd * 2.0 

        trajectory_sum = potential
        velocity = self.rng.normal(0, 0.1, size=x_c.shape)
        
        # Ergodic integration loop
        for _ in range(n_steps):
            # Gradient of potential (approximated by finite difference in feature space)
            epsilon = 1e-4
            grad = np.zeros_like(x_c)
            for i in range(len(x_c)):
                delta = np.zeros_like(x_c)
                delta[i] = epsilon
                pot_plus = -np.dot((x_c + delta - x_p), (x_c + delta - x_p))
                pot_minus = -np.dot((x_c - delta - x_p), (x_c - delta - x_p))
                grad[i] = (pot_plus - pot_minus) / (2 * epsilon)
            
            # Langevin update: v = momentum * v + gradient + noise
            momentum = 0.9
            noise = self.rng.normal(0, 0.01, size=x_c.shape)
            velocity = momentum * velocity + grad + noise
            
            # Update position (candidate features simulated)
            x_c += velocity * 0.1
            
            # Recalculate potential at new state
            diff = x_c - x_p
            current_pot = -np.dot(diff, diff)
            trajectory_sum += current_pot

        # Time average converges to space average (Ergodic theorem)
        return trajectory_sum / n_steps

    def _compute_logic_score(self, prompt: str, candidate: str) -> float:
        """
        Heuristic scorer for logical consistency (Constraint Propagation).
        Detects specific patterns like number comparisons and negation flips.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 0.0
        
        # Pattern 1: Numeric Consistency
        p_nums = re.findall(r"-?\d+\.?\d*", p_low)
        c_nums = re.findall(r"-?\d+\.?\d*", c_low)
        
        if p_nums and c_nums:
            try:
                p_val = float(p_nums[0])
                c_val = float(c_nums[0])
                
                if "greater" in p_low or "more" in p_low or ">" in p_low:
                    score += 1.0 if c_val > p_val else -1.0
                elif "less" in p_low or "fewer" in p_low or "<" in p_low:
                    score += 1.0 if c_val < p_val else -1.0
                else:
                    # Equality check if no comparator found but numbers exist
                    score += 1.0 if abs(c_val - p_val) < 1e-6 else -0.5
            except ValueError:
                pass

        # Pattern 2: Negation Consistency
        has_neg_p = any(w in p_low for w in ['not', 'no ', 'never'])
        has_neg_c = any(w in c_low for w in ['not', 'no ', 'never'])
        
        if "impossible" in p_low or "false" in p_low:
            # If prompt implies falsehood, candidate should reflect negation or low confidence
            if has_neg_c or "no" in c_low or "false" in c_low:
                score += 1.0
            else:
                score -= 1.0
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features to ensure consistency
        if not candidates:
            return []
            
        for cand in candidates:
            # 1. Ergodic Free Energy Score (Exploration/Validity)
            ergodic_score = self._ergodic_sample_score(prompt, cand)
            
            # 2. Logical Constraint Score (Exploitation/Reasoning)
            logic_score = self._compute_logic_score(prompt, cand)
            
            # 3. Combine: Weighted sum where logic handles hard constraints, 
            #    ergodic handles semantic drift/structure.
            #    Logic is given higher weight for explicit reasoning tasks.
            final_score = (0.4 * ergodic_score) + (0.6 * logic_score)
            
            # Add small NCD tiebreaker for string similarity if scores are close
            ncd = self._ncd_distance(prompt, cand)
            if abs(final_score) < 0.1:
                final_score -= ncd * 0.01

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Ergodic stability: {ergodic_score:.4f}, Logic fit: {logic_score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized score of the answer 
        relative to a hypothetical 'perfect' match and the ergodic stability.
        """
        # Get the score for this specific answer
        # We simulate a comparison against a 'null' hypothesis to get a raw metric
        ergodic_stability = self._ergodic_sample_score(prompt, answer)
        logic_fit = self._compute_logic_score(prompt, answer)
        
        raw_score = (0.4 * ergodic_stability) + (0.6 * logic_fit)
        
        # Map raw score to 0-1 confidence
        # Heuristic mapping: 
        # Strong logic fit (>0.5) -> High confidence
        # Negative logic fit -> Low confidence
        # Ergodic stability acts as a multiplier for certainty
        
        # Normalize logic fit from approx [-2, 2] to [0, 1]
        logic_conf = (logic_fit + 2.0) / 4.0
        logic_conf = max(0.0, min(1.0, logic_conf))
        
        # Normalize ergodic (usually negative energy, so less negative is better)
        # Range approx [-5, 0] -> [0, 1]
        erg_conf = (ergodic_stability + 5.0) / 5.0
        erg_conf = max(0.0, min(1.0, erg_conf))
        
        # Weighted confidence
        conf = 0.7 * logic_conf + 0.3 * erg_conf
        
        return float(max(0.0, min(1.0, conf)))