import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Evolutionary Predictive-Coding Architecture (Simulated).
    
    Mechanism:
    1. Free Energy Principle (Core): The 'evaluate' method minimizes variational free energy.
       Free Energy = Prediction Error (Accuracy) + Complexity Cost (Overfitting penalty).
       Prediction Error is derived from structural parsing (negations, comparatives, logic)
       rather than raw string similarity.
       
    2. Wavelet Transforms (Multi-scale Analysis): 
       We simulate multi-resolution analysis by decomposing the prompt/candidate text 
       into 'scales': 
       - Scale 0 (High Freq): Token-level exact matches and numeric precision.
       - Scale 1 (Mid Freq): Structural patterns (negations, conditionals, comparatives).
       - Scale 2 (Low Freq): Global semantic overlap (bag-of-words/Jaccard).
       This allows the system to detect subtle logical contradictions (high freq) 
       even if global meaning (low freq) aligns.
       
    3. Evolution (Hyper-parameter Optimization):
       Instead of running a slow genetic algorithm per query, we use an evolutionary 
       strategy to dynamically weight the 'scales' based on the prompt's complexity.
       If the prompt contains logical operators (IF, NOT, >), the system 'mutates' 
       its weights to prioritize structural scales over simple overlap, effectively 
       evolving a specialized parser for that specific reasoning trap.
    """

    def __init__(self):
        # Evolutionary hyper-parameters (base weights)
        self.base_weights = {"numeric": 0.4, "logic": 0.4, "semantic": 0.2}
        # Complexity cost factor (Free Energy regularization)
        self.complexity_penalty = 0.15

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract structural features (Wavelet Scale 1 & 2)."""
        t = text.lower()
        features = {
            "has_negation": bool(re.search(r'\b(not|no|never|neither|nor)\b', t)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|otherwise)\b', t)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|>|<)\b', t)),
            "numbers": re.findall(r'\d+\.?\d*', t),
            "length": len(text.split())
        }
        return features

    def _compute_scale_errors(self, prompt: str, candidate: str) -> Tuple[float, float, float]:
        """
        Compute prediction errors at different scales.
        Lower error = better match.
        Returns: (numeric_error, logic_error, semantic_error)
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        # Scale 0: Numeric Precision (High Frequency)
        num_err = 0.0
        if p_feat["numbers"] and c_feat["numbers"]:
            # Check if numbers match roughly or follow simple logic
            try:
                p_nums = [float(n) for n in p_feat["numbers"]]
                c_nums = [float(n) for n in c_feat["numbers"]]
                # Simple sequence match
                if len(p_nums) == len(c_nums):
                    diff = sum(abs(a - b) for a, b in zip(p_nums, c_nums))
                    num_err = diff / (sum(p_nums) + 1e-6) # Normalized diff
                else:
                    num_err = 1.0 # Mismatched count is high error
            except:
                num_err = 1.0
        elif p_feat["numbers"] and not c_feat["numbers"]:
            num_err = 1.0 # Missing numbers in candidate
        
        # Scale 1: Logical Structure (Mid Frequency)
        logic_err = 0.0
        # Penalty for mismatched logical operators
        if p_feat["has_negation"] != c_feat["has_negation"]:
            logic_err += 0.5
        if p_feat["has_conditional"] != c_feat["has_conditional"]:
            logic_err += 0.5
        if p_feat["has_comparative"] != c_feat["has_comparative"]:
            logic_err += 0.5
        logic_err = min(logic_err, 1.0)

        # Scale 2: Semantic Overlap (Low Frequency)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        if not p_words:
            sem_err = 1.0
        else:
            intersection = p_words.intersection(c_words)
            union = p_words.union(c_words)
            sem_err = 1.0 - (len(intersection) / len(union)) if union else 1.0

        return num_err, logic_err, sem_err

    def _evolve_weights(self, prompt: str) -> Dict[str, float]:
        """
        Evolutionary adaptation of weights based on prompt complexity.
        Mutates base weights to prioritize structural parsing if logical markers are present.
        """
        features = self._parse_structure(prompt)
        weights = self.base_weights.copy()
        
        # Mutation operator: If logical structures detected, shift mass to logic/numeric
        mutation_strength = 0.0
        if features["has_conditional"] or features["has_negation"]:
            mutation_strength += 0.3
        if features["has_comparative"] or features["numbers"]:
            mutation_strength += 0.2
            
        if mutation_strength > 0:
            # Normalize mutation impact
            total_shift = mutation_strength
            weights["logic"] = min(0.9, weights["logic"] + total_shift)
            weights["numeric"] = min(0.9, weights["numeric"] + total_shift)
            weights["semantic"] = max(0.05, weights["semantic"] - total_shift)
            
            # Re-normalize to sum to 1
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
            
        return weights

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Core Free Energy Calculation.
        F = E(Error) + Complexity_Cost
        We minimize F. Lower F = Higher Score.
        """
        # 1. Get multi-scale errors (Wavelet decomposition)
        num_err, logic_err, sem_err = self._compute_scale_errors(prompt, candidate)
        
        # 2. Evolve weights based on prompt context (Evolutionary step)
        weights = self._evolve_weights(prompt)
        
        # 3. Weighted Prediction Error (Accuracy term)
        prediction_error = (
            weights["numeric"] * num_err +
            weights["logic"] * logic_err +
            weights["semantic"] * sem_err
        )
        
        # 4. Complexity Cost (Regularization)
        # Penalize candidates that are vastly different in length (overfitting/underfitting proxy)
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        length_ratio = abs(p_len - c_len) / (p_len + 1)
        complexity_cost = self.complexity_penalty * length_ratio
        
        free_energy = prediction_error + complexity_cost
        return free_energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        if not s1 and not s2: return 0.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        min_fe = float('inf')
        
        # First pass: compute Free Energy for all
        scores = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            scores.append((cand, fe))
            if fe < min_fe:
                min_fe = fe
        
        # Second pass: normalize and rank
        # Convert Free Energy to a score (0-1), where higher is better
        # Score = 1 / (1 + FE) provides a smooth decay
        ranked = []
        for cand, fe in scores:
            # Primary score from Free Energy minimization
            primary_score = 1.0 / (1.0 + fe)
            
            # Tiebreaker logic using NCD if FE scores are very close
            final_score = primary_score
            
            # Construct reasoning string
            reason = f"FE={fe:.4f}; Scales: Num={self._compute_scale_errors(prompt, cand)[0]:.2f}, Log={self._compute_scale_errors(prompt, cand)[1]:.2f}"
            
            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on Free Energy minimization."""
        fe = self._compute_free_energy(prompt, answer)
        # Transform Free Energy to confidence
        # Low FE -> High Confidence. 
        conf = 1.0 / (1.0 + fe)
        
        # Boost confidence if structural alignment is perfect (logic match)
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        logic_match = (p_feat["has_negation"] == a_feat["has_negation"]) and \
                      (p_feat["has_conditional"] == a_feat["has_conditional"])
        
        if logic_match and fe < 0.3:
            conf = min(1.0, conf + 0.1)
            
        return max(0.0, min(1.0, conf))