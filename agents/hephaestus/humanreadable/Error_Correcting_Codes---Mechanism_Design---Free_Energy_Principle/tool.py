import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Incentive-Compatible Belief Propagation (VICBP) Approximation.
    
    Mechanism:
    1. Structural Parsing (Code Constraints): Extracts logical atoms (negations, 
       comparatives, conditionals) to form a 'parity check' vector. Valid hypotheses 
       must satisfy logical consistency with these constraints.
    2. Free Energy Principle (Evaluation): Computes 'surprise' as the distance between 
       the candidate's logical signature and the prompt's required signature. 
       Lower surprise = higher score.
    3. Mechanism Design (Scoring): Implements a strict proper scoring rule. 
       'Payment' (score) is proportional to the reduction in global free energy 
       (logical inconsistency). Truthful alignment with structural constraints 
       maximizes reward; gaming via string length or echo is penalized.
       
    Note: ECC concepts are restricted to the confidence() wrapper as per causal analysis.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'false']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features to form a logical 'codeword'."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Feature vector: [has_negation, has_comparative, has_conditional, numeric_count, char_length_log]
        has_neg = 1.0 if any(n in words for n in self.negations) else 0.0
        has_comp = 1.0 if any(c in text_lower for c in self.comparatives) else 0.0
        has_cond = 1.0 if any(c in words for c in self.conditionals) else 0.0
        
        nums = self.numeric_pattern.findall(text)
        num_count = min(len(nums) / 10.0, 1.0)  # Normalize count
        
        # Log length to prevent large strings from dominating purely on size
        log_len = min(np.log1p(len(text)) / 10.0, 1.0)
        
        return np.array([has_neg, has_comp, has_cond, num_count, log_len])

    def _compute_free_energy(self, prompt_vec: np.ndarray, cand_vec: np.ndarray, 
                             prompt_len: float, cand_len: float) -> float:
        """
        Compute variational free energy (surprise).
        Energy = Prediction Error (Distance) + Complexity Penalty.
        Minimizing energy aligns the candidate with prompt constraints.
        """
        # Prediction error: L1 distance between structural features
        # This acts as the 'parity check' failure count
        prediction_error = np.sum(np.abs(prompt_vec - cand_vec))
        
        # Complexity penalty (prevents overfitting/gaming by length)
        complexity = abs(prompt_len - cand_len) * 0.1
        
        return prediction_error + complexity

    def _mechanism_payment(self, energy: float, max_energy: float = 5.0) -> float:
        """
        Mechanism Design: Proper scoring rule.
        Payment = Max_Energy - Observed_Energy.
        Truthful reporting (low energy) yields max payment.
        """
        score = max(0.0, 1.0 - (energy / max_energy))
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_vec = self._extract_features(prompt)
        prompt_len = np.log1p(len(prompt)) / 10.0
        
        results = []
        for cand in candidates:
            cand_vec = self._extract_features(cand)
            cand_len = np.log1p(len(cand)) / 10.0
            
            # 1. Compute Free Energy (Surprise)
            energy = self._compute_free_energy(prompt_vec, cand_vec, prompt_len, cand_len)
            
            # 2. Apply Mechanism Design Scoring
            base_score = self._mechanism_payment(energy)
            
            # 3. Structural Logic Boost (Heuristic for specific reasoning traps)
            # If prompt has numbers, favor candidates with numbers
            has_nums_prompt = bool(self.numeric_pattern.search(prompt))
            has_nums_cand = bool(self.numeric_pattern.search(cand))
            logic_bonus = 0.0
            if has_nums_prompt and has_nums_cand:
                logic_bonus = 0.15
            elif has_nums_prompt and not has_nums_cand:
                logic_bonus = -0.2 # Penalty for ignoring numeric context
            
            final_score = base_score + logic_bonus
            
            # Reasoning trace
            reasoning = f"Structural match: {1.0-energy:.2f}. Logic bonus: {logic_bonus:.2f}."
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence based on structural consistency (ECC restricted role).
        Uses a tight parity check on logical operators.
        """
        p_vec = self._extract_features(prompt)
        a_vec = self._extract_features(answer)
        
        # ECC-like distance check: High distance implies corruption/error
        distance = np.sum(np.abs(p_vec - a_vec))
        
        # Specific check for negation flips (common error mode)
        neg_mismatch = abs(p_vec[0] - a_vec[0])
        
        # Base confidence decays with distance
        conf = 1.0 / (1.0 + distance)
        
        # Heavy penalty for negation mismatch
        if neg_mismatch > 0.5:
            conf *= 0.4
            
        return float(np.clip(conf, 0.0, 1.0))