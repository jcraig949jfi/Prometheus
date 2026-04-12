import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Regulated Active Inference Controller (TR-AIC).
    
    Core Mechanism (Free Energy Principle + Thermodynamics):
    The tool treats hypothesis evaluation as minimizing Variational Free Energy (VFE).
    1. Prediction Error (KL Divergence): Measured by structural alignment between 
       prompt constraints and candidate assertions. High alignment = low VFE.
    2. Thermodynamic Cost (Entropy Production): Estimated by the computational 
       "effort" (complexity/length) required to maintain the belief state. 
       Simple, precise answers have lower entropy production than verbose, vague ones.
       
    Strategy:
    - Primary Score: Structural parsing (negations, comparatives, numerics).
    - Regularization: Penalize candidates with high "thermodynamic cost" (complexity) 
      unless they significantly reduce prediction error.
    - Optimal Control: Used ONLY in confidence() as a stability check (inhibitor role).
    """

    def __init__(self):
        # Keywords indicating logical structures
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _structural_parse(self, text: str) -> dict:
        """Extract logical features from text."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        numbers = re.findall(r'\d+\.?\d*', t)
        
        return {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'has_numbers': len(numbers) > 0,
            'numbers': numbers,
            'word_count': len(words),
            'is_yes': any(w in t for w in self.bool_yes),
            'is_no': any(w in t for w in self.bool_no)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _evaluate_numerics(self, prompt_feats: dict, cand_feats: dict) -> float:
        """Check numeric consistency (e.g., 9.11 < 9.9)."""
        if not prompt_feats['has_numbers'] or not cand_feats['has_numbers']:
            return 0.0
        
        # Simple heuristic: if prompt has numbers and candidate has numbers,
        # check if candidate numbers are a subset or logically derived.
        # For this implementation, we reward candidates that contain specific 
        # numbers found in the prompt (constraint satisfaction).
        p_nums = set(prompt_feats['numbers'])
        c_nums = set(cand_feats['numbers'])
        
        if not p_nums:
            return 0.0
            
        overlap = len(p_nums.intersection(c_nums))
        return overlap / len(p_nums)

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculate expected Free Energy (F = Prediction Error + Thermodynamic Cost).
        We minimize F, so we return negative F as the score.
        """
        p_feats = self._structural_parse(prompt)
        c_feats = self._structural_parse(candidate)
        
        # 1. Prediction Error (KL Divergence approximation)
        # Penalize mismatch in logical operators (negation, conditionals)
        logic_error = 0.0
        if p_feats['neg_count'] > 0 and c_feats['neg_count'] == 0:
            logic_error += 0.5 # Missed negation
        if p_feats['cond_count'] > 0 and c_feats['cond_count'] == 0:
            logic_error += 0.3 # Missed condition
        
        # Numeric constraint satisfaction
        num_score = self._evaluate_numerics(p_feats, c_feats)
        if p_feats['has_numbers'] and num_score < 1.0:
            logic_error += (1.0 - num_score) * 0.5
            
        # Boolean consistency
        if p_feats['is_yes'] and c_feats['is_no']:
            logic_error += 1.0
        if p_feats['is_no'] and c_feats['is_yes']:
            logic_error += 1.0
            
        # 2. Thermodynamic Cost (Entropy Production)
        # Hypothesis: Simpler explanations (lower word count relative to info) 
        # have lower entropy production. Overly verbose answers are "costly".
        # Cost = lambda * (Complexity_Candidate - Complexity_Prompt_Ideal)
        # We approximate ideal complexity as prompt length * 0.5 (summary)
        ideal_len = max(10, len(prompt) * 0.5)
        complexity_penalty = abs(len(candidate) - ideal_len) / (len(prompt) + 1)
        thermo_cost = 0.2 * complexity_penalty
        
        # Total Free Energy (to be minimized)
        free_energy = logic_error + thermo_cost
        
        # Convert to score (maximize)
        # Base score 1.0, subtract errors and costs
        score = 1.0 - free_energy
        
        # NCD Tiebreaker (small weight)
        ncd = self._compute_ncd(prompt, candidate)
        score -= (ncd * 0.05)
        
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._calculate_free_energy(prompt, cand)
            reasoning = f"FE-minimization: logic_err={'low' if score > 0.7 else 'high'}, thermo_cost={'low' if len(cand) < len(prompt)*1.5 else 'high'}"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Confidence wrapper using Optimal Control concepts strictly as a stability check.
        Checks if the answer is a stable fixed point (deterministic match) vs volatile.
        """
        # Structural stability check
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        stability = 1.0
        
        # If prompt implies negation, answer must reflect it to be stable
        if p_feats['neg_count'] > 0:
            if a_feats['neg_count'] == 0 and not any(x in answer.lower() for x in self.bool_no):
                stability -= 0.5
        
        # Numeric stability
        if p_feats['has_numbers']:
            if not a_feats['has_numbers']:
                # If prompt has numbers but answer doesn't, confidence drops unless it's a yes/no question
                if not (a_feats['is_yes'] or a_feats['is_no']):
                    stability -= 0.3
        
        # Base confidence on the free energy score calculated internally
        fe_score = self._calculate_free_energy(prompt, answer)
        
        # Combine: Confidence is a function of FE score and structural stability
        # Optimal control acts as a gain modifier here
        final_conf = fe_score * (0.5 + 0.5 * stability)
        return max(0.0, min(1.0, final_conf))