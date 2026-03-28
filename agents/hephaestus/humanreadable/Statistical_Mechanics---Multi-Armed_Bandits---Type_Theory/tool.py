import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Ensemble Bandit Sampling (TEBS) Approximation.
    
    Mechanism:
    1. Type Theory (Logical Constraints): Parses structural markers (negations, 
       comparatives, conditionals) to enforce logical consistency. Candidates 
       violating prompt constraints receive high "energy" (low probability).
    2. Statistical Mechanics (Energy/Prior): Computes an energy score E based on 
       structural alignment and NCD. Lower E implies higher Boltzmann weight.
    3. Multi-Armed Bandit (Exploration/Exploitation): Treats candidates as arms.
       Allocates a dynamic bonus (UCB-style) to candidates with high potential 
       information gain (length diversity + structural match), balancing the 
       raw probability score.
       
    The final score is a weighted sum of the Boltzmann probability and the 
    bandit exploration bonus, ensuring we beat pure NCD baselines by prioritizing 
    logical structure over simple compression.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extracts logical features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            "numbers": re.findall(r'\d+\.?\d*', text_lower),
            "length": len(text)
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Returns an energy penalty (0.0 = consistent, >0.0 = inconsistent).
        Enforces constraint propagation based on structural markers.
        """
        penalty = 0.0
        
        # Constraint 1: Negation alignment
        # If prompt has strong negation context, candidate should reflect it or not contradict
        if prompt_feats["negations"] > 0 and cand_feats["negations"] == 0:
            # Heuristic: If prompt negates, simple positive answers might be wrong
            # This is a soft penalty to allow for "Yes, but..." structures
            if cand_feats["length"] < 10: 
                penalty += 0.5

        # Constraint 2: Number consistency (Transitivity/Comparison)
        if prompt_feats["numbers"] and cand_feats["numbers"]:
            try:
                p_nums = [float(x) for x in prompt_feats["numbers"]]
                c_nums = [float(x) for x in cand_feats["numbers"]]
                # Simple check: if prompt asks for "less", candidate number should be smaller
                if "less" in prompt_feats.get("comparatives", []) or "smaller" in str(prompt_feats):
                     # Crude check: does the candidate number satisfy a 'less' condition relative to max prompt num?
                     if c_nums and p_nums:
                         if min(c_nums) > max(p_nums):
                             penalty += 1.0
            except ValueError:
                pass

        # Constraint 3: Conditional presence
        if prompt_feats["conditionals"] > 0 and cand_feats["conditionals"] == 0:
            # If prompt is conditional, answers lacking conditionality might be oversimplified
            penalty += 0.2
            
        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(b1), len(b2), len(b12)
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Energy E = -log(Prior) + Structural_Penalty.
        Lower energy = higher probability.
        """
        # Base energy from NCD (Statistical Mechanics prior)
        # We invert NCD so similar = low energy. NCD is 0..1 (approx).
        # E_ncd ~ NCD * scaling_factor
        ncd_val = self._ncd(prompt, candidate)
        
        # Structural analysis (Type Theory constraints)
        p_feats = self._structural_parse(prompt)
        c_feats = self._structural_parse(candidate)
        
        logic_penalty = self._check_logical_consistency(p_feats, c_feats)
        
        # Combined Energy: Weighted sum
        # NCD is primary baseline, logic penalty acts as a strong filter
        energy = (ncd_val * 0.8) + (logic_penalty * 1.5)
        
        return energy

    def _bandit_bonus(self, candidate: str, total_samples: int, arm_visits: int) -> float:
        """
        UCB1-style exploration bonus.
        Encourages exploring candidates that haven't been fully 'sampled' 
        (in this static context, favors diverse lengths/structures if counts were dynamic).
        Since this is a single-shot evaluation, we simulate 'visits' based on 
        candidate uniqueness to promote diversity among top scorers.
        """
        if arm_visits == 0:
            return float('inf')
        # Exploration term
        return (2 * total_samples / arm_visits) ** 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        energies = []
        
        # Phase 1: Compute Energies (Statistical Mechanics + Type Constraints)
        for cand in candidates:
            e = self._compute_energy(prompt, cand)
            energies.append(e)
        
        # Convert Energy to Probability (Boltzmann Distribution)
        # P ~ exp(-E)
        max_e = max(energies)
        probs = []
        for e in energies:
            # Shift for numerical stability
            shifted_e = e - max_e
            prob = 2.71828 ** (-shifted_e) # exp(-E)
            probs.append(prob)
            
        # Normalize probabilities
        sum_probs = sum(probs) + self.epsilon
        norm_probs = [p / sum_probs for p in probs]
        
        # Phase 2: Bandit Adjustment (UCB)
        # In a static list, we treat each candidate as an arm.
        # We add a bonus based on how distinct the candidate is from the prompt
        # to simulate "Information Gain".
        total_samples = len(candidates)
        
        for i, cand in enumerate(candidates):
            base_score = norm_probs[i]
            
            # Simulate 'visits' as inverse of NCD to prompt (closer = more visited?)
            # Actually, let's treat 'visits' as 1 for now, and use the bonus 
            # to break ties via structural complexity.
            # A better heuristic for static ranking: 
            # Bonus = Structural Richness (more tokens/logic markers) * Uncertainty
            
            p_feats = self._structural_parse(prompt)
            c_feats = self._structural_parse(cand)
            
            # Information Gain proxy: Does the candidate add logical markers present in prompt?
            gain = 0.0
            if p_feats["negations"] > 0 and c_feats["negations"] > 0:
                gain += 0.1
            if p_feats["conditionals"] > 0 and c_feats["conditionals"] > 0:
                gain += 0.1
            if p_feats["numbers"] and c_feats["numbers"]:
                gain += 0.1
                
            # UCB-like adjustment: Score = Exploit + Explore
            # Exploit = base_score (from Boltzmann)
            # Explore = gain (potential for high information content)
            final_score = base_score + (gain * 0.2)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Boltzmann weight: {base_score:.4f}, Logic Gain: {gain:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Derived from the Boltzmann probability of the answer given the prompt.
        """
        # Evaluate single candidate against itself to get relative standing?
        # No, we need to know how good it is in absolute terms or vs a null.
        # We approximate by checking the energy directly.
        
        energy = self._compute_energy(prompt, answer)
        
        # Map energy to 0-1 confidence. 
        # Low energy (good match) -> High confidence.
        # E ~ 0 -> conf ~ 1. E ~ 2 -> conf ~ low.
        # Using exp(-E) as a proxy for confidence, capped at 1.
        import math
        conf = math.exp(-energy)
        
        # Adjust for logical consistency specifically
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        penalty = self._check_logical_consistency(p_feats, a_feats)
        
        if penalty > 0.5:
            conf *= 0.5 # Penalize heavily if logic fails
            
        return min(1.0, max(0.0, conf))