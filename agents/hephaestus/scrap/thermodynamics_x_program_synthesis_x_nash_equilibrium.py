import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Nash Program Synthesizer (TNPS) Approximation.
    
    Mechanism:
    1. Energy (E): Combines structural fidelity (logic parsing) and description length.
       - Structural fidelity checks negations, comparatives, and numeric consistency.
       - Description length penalizes verbosity (Kolmogorov proxy).
    2. Entropy (S): Estimates diversity of the candidate set relative to the prompt.
    3. Free Energy (F): F = E - T*S. We minimize F. 
       - High temperature (T) in early conceptual phases encourages diversity; 
         here we use a fixed moderate T to balance accuracy and simplicity.
    4. Nash Equilibrium: We treat the population of candidates as players. 
       A candidate's utility is boosted if it is a 'best response' (i.e., structurally 
       consistent) relative to the group's average structural score. This stabilizes 
       the selection against outliers that might luck into low energy via noise.
    
    This implementation approximates the theoretical loop by scoring candidates 
    on structural logic (primary), adjusting for complexity (MDL), and applying 
    a Nash-like stability bonus based on cohort performance.
    """

    def __init__(self):
        self.temperature = 0.5  # Balances exploration (entropy) vs exploitation (energy)
        self.nash_weight = 0.3  # Weight for the Nash stability term

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a structural fidelity score based on logic patterns.
        Returns a score where higher is better (lower energy).
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has "not", "no", "never", candidate should reflect understanding
        negations = ["not", "no", "never", "none", "cannot", "impossible"]
        prompt_has_neg = any(n in p_lower for n in negations)
        candidate_has_neg = any(n in c_lower for n in negations)
        
        if prompt_has_neg:
            # Reward if candidate acknowledges negation (simple heuristic)
            if candidate_has_neg:
                score += 2.0
            else:
                score -= 2.0 # Penalty for ignoring negation
        else:
            # Slight penalty if candidate introduces unnecessary negation
            if candidate_has_neg:
                score -= 0.5

        # 2. Comparative/Numeric Evaluation
        # Extract numbers from prompt and candidate
        nums_p = re.findall(r"-?\d+\.?\d*", p_lower)
        nums_c = re.findall(r"-?\d+\.?\d*", c_lower)
        
        if nums_p:
            try:
                # Check if candidate contains relevant numbers or logical conclusions
                p_vals = [float(n) for n in nums_p]
                c_vals = [float(n) for n in nums_c]
                
                # Simple transitivity/comparison check
                # If prompt implies A > B, does candidate reflect it? 
                # (Heuristic: if prompt has 2+ numbers, candidate should likely have >=1)
                if len(p_vals) >= 2:
                    if len(c_vals) > 0:
                        score += 1.5
                    # Check specific comparative keywords
                    comparatives = ["greater", "less", "more", "fewer", "larger", "smaller", "equal"]
                    if any(c in p_lower for c in comparatives):
                        if any(c in c_lower for c in comparatives):
                            score += 2.0
                        else:
                            # If prompt compares but candidate doesn't mention numbers/logic, slight penalty
                            if len(c_vals) == 0:
                                score -= 1.0
            except ValueError:
                pass

        # 3. Conditional/Constraint Propagation
        conditionals = ["if", "when", "unless", "provided"]
        if any(c in p_lower for c in conditionals):
            # Candidate should ideally contain logical connectors or definitive answers
            logic_words = ["then", "therefore", "because", "yes", "no", "true", "false"]
            if any(l in c_lower for l in logic_words):
                score += 1.0
        
        return score

    def _complexity_penalty(self, candidate: str) -> float:
        """
        Calculates MDL-like penalty based on length (proxy for Kolmogorov complexity).
        Shorter valid programs are preferred.
        """
        return len(candidate) * 0.01

    def _nash_stability_bonus(self, candidate_struct_score: float, all_struct_scores: List[float]) -> float:
        """
        Computes a Nash-like bonus. 
        If a candidate's structural score is close to the max of the population, 
        it receives a stability bonus (it's a 'best response').
        """
        if not all_struct_scores:
            return 0.0
        
        max_score = max(all_struct_scores)
        avg_score = sum(all_struct_scores) / len(all_struct_scores)
        
        # If candidate is near the best response (within 10% of the gap between avg and max)
        # or if it IS the max, it gets a bonus.
        if max_score == avg_score:
            return 0.5 # All are equal, stable
        
        # Normalized distance to best response
        performance_ratio = (candidate_struct_score - avg_score) / (max_score - avg_score + 1e-9)
        
        # Bonus scales with how close to the 'equilibrium' (best response) it is
        if performance_ratio > 0.8:
            return 1.0 * self.nash_weight
        elif performance_ratio > 0.5:
            return 0.5 * self.nash_weight
        return 0.0

    def _calculate_free_energy(self, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        """
        Calculates F = E - T*S
        E = Complexity Penalty - Structural Score (Lower E is better)
        S = Entropy contribution (approximated by diversity bonus in this context)
        """
        # Energy components
        struct_score = self._structural_score(prompt, candidate)
        complexity = self._complexity_penalty(candidate)
        
        # Base Energy (Lower is better)
        # We invert struct_score because we want to minimize energy
        energy = complexity - struct_score
        
        # Entropy term (diversity bonus is handled via Nash stability in the utility function)
        # Here we just apply the temperature factor to the 'disorder' of the text length variance?
        # Simplified: The 'Entropy' in TNPS encourages keeping diverse hypotheses.
        # In a ranking context, we simulate this by not penalizing unique but valid structures too harshly.
        # We will treat the Nash bonus as the primary driver for the 'equilibrium' state.
        
        return energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Pre-calculate structural scores for Nash computation
        struct_scores = [self._structural_score(prompt, c) for c in candidates]
        
        results = []
        for i, candidate in enumerate(candidates):
            # 1. Calculate Energy (MDL + Structural Fidelity)
            energy = self._calculate_free_energy(prompt, candidate, candidates)
            
            # 2. Calculate Nash Stability Bonus
            nash_bonus = self._nash_stability_bonus(struct_scores[i], struct_scores)
            
            # 3. Final Score (Utility = -Energy + NashBonus)
            # Higher score is better
            final_score = -energy + nash_bonus
            
            # Add small NCD tiebreaker as per requirements (only if scores are very close, 
            # but here we integrate it as a minor component of the score)
            # NCD between prompt and candidate (lower is better -> higher score)
            try:
                ncd = self._ncd(prompt, candidate)
                final_score -= (ncd * 0.05) # Small penalty for high NCD
            except:
                pass

            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural:{struct_scores[i]:.2f}, Complexity:{self._complexity_penalty(candidate):.2f}, Nash:{nash_bonus:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and free energy minimization.
        """
        # Evaluate single candidate against a dummy set to get its raw score
        # We simulate a population with itself and a few perturbations to estimate stability
        population = [answer, "No", "Yes", "Unknown"] 
        eval_results = self.evaluate(prompt, population)
        
        # Find the score of the specific answer
        target_score = None
        for res in eval_results:
            if res["candidate"] == answer:
                target_score = res["score"]
                break
        
        if target_score is None:
            return 0.0
            
        # Normalize score to 0-1 range roughly
        # Assuming typical scores range between -5 and 10
        normalized = (target_score + 5.0) / 15.0
        return max(0.0, min(1.0, normalized))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp_len = len(zlib.compress(b1 + b2))
            max_len = max(len1, len2)
            if max_len == 0:
                return 0.0
            ncd = (comp_len - max_len) / max_len # Simplified NCD
            # Standard NCD: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Using zlib lengths directly as proxy for C(x)
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            cxy = len(zlib.compress(b1 + b2))
            
            ncd_val = (cxy - min(c1, c2)) / max(c1, c2)
            return max(0.0, ncd_val)
        except:
            return 1.0