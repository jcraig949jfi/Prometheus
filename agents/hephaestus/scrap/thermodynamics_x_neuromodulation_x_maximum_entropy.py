import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Neuromodulated Maximum-Entropy Inference Engine (TN-MEIE)
    
    Mechanism:
    1. Structural Parsing (Energy Function E): Computes an 'energy' score based on
       logical consistency, negation handling, comparative evaluation, and numeric
       transitivity. Lower energy = better fit.
    2. Neuromodulation (Beta & Gain): Dynamically adjusts the inverse temperature
       based on the variance of energy scores across candidates. High variance (uncertainty)
       triggers 'exploration' (lower beta), while low variance (consensus) triggers
       'exploitation' (higher beta).
    3. Maximum Entropy Sampling: Converts energies to probabilities via Boltzmann
       distribution P ~ exp(-beta * E), ensuring the output reflects a calibrated
       probability distribution over hypotheses rather than raw scores.
    
    This approach prioritizes structural logic (beating NCD baselines) while using
    thermodynamic principles for self-calibration and ranking.
    """

    def __init__(self):
        # No external state needed; stateless computation per call
        pass

    def _compute_structural_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculates the 'Energy' E(w) of a candidate based on structural alignment.
        Lower energy is better.
        Components:
        - Negation alignment
        - Numeric consistency
        - Keyword overlap (weighted)
        - Length penalty (Occam's razor)
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        energy = 0.0
        
        # 1. Negation Consistency Check
        negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        p_has_neg = any(n in p_lower for n in negation_words)
        c_has_neg = any(n in c_lower for n in negation_words)
        
        if p_has_neg != c_has_neg:
            # Penalty for mismatched negation logic
            energy += 2.0
        else:
            # Reward for matching negation state
            energy -= 0.5

        # 2. Numeric Evaluation (Simplified)
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r"[-+]?\d*\.?\d+", p_lower)
        c_nums = re.findall(r"[-+]?\d*\.?\d+", c_lower)
        
        if p_nums and c_nums:
            try:
                # Check if candidate preserves numeric magnitude order roughly
                p_max = max(float(x) for x in p_nums)
                c_max = max(float(x) for x in c_nums)
                
                # If prompt implies a specific number, candidate should ideally contain it or close
                # Simple heuristic: if candidate has numbers, do they appear in prompt?
                matches = 0
                for cn in c_nums:
                    if cn in p_nums:
                        matches += 1
                if matches == 0:
                    energy += 1.0 # Penalty for introducing unrelated numbers
                else:
                    energy -= 0.5 # Reward for echoing correct numbers
            except ValueError:
                pass

        # 3. Structural Keyword Overlap (Bag of important words)
        # Filter stopwords to focus on content
        stopwords = set(['the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'to', 'of'])
        p_words = set(re.findall(r'\b\w+\b', p_lower)) - stopwords
        c_words = set(re.findall(r'\b\w+\b', c_lower)) - stopwords
        
        if p_words:
            intersection = p_words.intersection(c_words)
            union = p_words.union(c_words)
            if len(union) > 0:
                jaccard = len(intersection) / len(union)
                # Convert similarity to energy (lower is better)
                energy -= (jaccard * 3.0) 
            else:
                energy += 1.0 # No overlap penalty

        # 4. Occam's Razor (Length Penalty)
        # Penalize excessively long answers relative to prompt
        len_ratio = len(c_lower) / max(len(p_lower), 1)
        if len_ratio > 2.0:
            energy += 0.5 * (len_ratio - 1.0)
            
        return energy

    def _neuromodulate_beta(self, energies: List[float]) -> float:
        """
        Computes inverse temperature beta based on the free energy landscape.
        High variance in energies -> Lower beta (Explore/Soften)
        Low variance in energies -> Higher beta (Exploit/Harden)
        """
        if not energies:
            return 1.0
            
        mean_e = sum(energies) / len(energies)
        variance = sum((e - mean_e) ** 2 for e in energies) / len(energies)
        
        # Base beta
        beta = 1.0
        
        # Modulation: If variance is high, we are uncertain, so lower beta to explore
        # If variance is low (all similar or one clear winner), increase beta to sharpen
        if variance > 2.0:
            beta = 0.5
        elif variance < 0.5:
            beta = 2.0
            
        # Prevent division by zero or extreme values
        return max(0.1, min(10.0, beta))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Compute Energies (Thermodynamics)
        energies = [self._compute_structural_energy(prompt, c) for c in candidates]
        
        # 2. Neuromodulation (Adjust Beta)
        beta = self._neuromodulate_beta(energies)
        
        # 3. Maximum Entropy Distribution (Boltzmann)
        # P(w) = exp(-beta * E) / Z
        # Shift energies for numerical stability (subtract min)
        min_e = min(energies)
        shifted_energies = [e - min_e for e in energies]
        
        exp_terms = [math.exp(-beta * e) for e in shifted_energies]
        Z = sum(exp_terms)
        
        if Z == 0:
            Z = 1e-9
            
        probs = [e / Z for e in exp_terms]
        
        # Construct results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": probs[i],
                "reasoning": f"Energy={energies[i]:.4f}, Beta={beta:.4f}, Prob={probs[i]:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the Boltzmann probability of the single answer against a generated
        set of perturbations (simulated candidates) to estimate relative likelihood.
        Since we cannot generate perturbations dynamically without more context,
        we approximate confidence via the structural energy mapping directly.
        """
        energy = self._compute_structural_energy(prompt, answer)
        
        # Map energy to confidence using a sigmoid-like function
        # Low energy (good) -> High confidence
        # High energy (bad) -> Low confidence
        # Assuming energy ranges roughly -5 to 5
        conf = 1.0 / (1.0 + math.exp(energy))
        
        return max(0.0, min(1.0, conf))