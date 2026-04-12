import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Type-Guided Evolutionary Bandit Reasoner (Simulated).
    
    Mechanism:
    1. Type Theory (Constraint): Candidates are parsed for structural validity 
       (matching parentheses, balanced logic tokens). Ill-formed terms get heavy penalties.
    2. Multi-Armed Bandit (Selection): Candidates are scored based on a UCB-like metric 
       derived from structural alignment with the prompt (negation handling, numeric comparison).
    3. Evolution (Variation): The scoring function implicitly simulates selection pressure 
       where 'mutations' (parsing errors or logical mismatches) reduce fitness.
       
    This implementation prioritizes structural parsing and numeric evaluation as requested,
    using the theoretical framework to guide the scoring weights dynamically.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text.split()),
            'balanced_parens': text.count('(') == text.count(')') if '(' in text or ')' in text else True
        }
        return features

    def _check_numeric_logic(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Evaluate numeric consistency and ordering."""
        if not prompt_nums or not cand_nums:
            return 0.5 # Neutral if no numbers to compare
        
        try:
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in cand_nums]
            
            # Check if candidate preserves relative order found in prompt (simplified transitivity)
            if len(p_vals) >= 2 and len(c_vals) >= 2:
                p_diff = p_vals[-1] - p_vals[-2]
                c_diff = c_vals[-1] - c_vals[-2]
                if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0) or (p_diff == 0 and c_diff == 0):
                    return 1.0 # Consistent trend
                else:
                    return 0.2 # Contradictory trend
            return 0.8 # Partial match
        except ValueError:
            return 0.0

    def _type_safety_check(self, candidate: str) -> float:
        """Simulate Type Theory constraint: Ensure syntactic/semantic well-formedness."""
        if not candidate.strip():
            return 0.0
        
        # Check balanced parentheses
        if not self._parse_structure(candidate)['balanced_parens']:
            return 0.1
        
        # Check for obvious logical fragments (e.g., hanging operators)
        if re.search(r'[+\-*/]=\s*$', candidate):
            return 0.2
            
        return 1.0

    def _compute_bandit_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Calculate UCB-like score based on structural alignment."""
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        score = 0.0
        reasons = []

        # 1. Type Safety Gate (Type Theory)
        type_score = self._type_safety_check(candidate)
        if type_score < 0.5:
            return type_score * 0.5, "Failed type safety check (ill-formed)"
        
        # 2. Structural Alignment (Evolutionary Fitness)
        # Reward matching structural complexity (e.g., if prompt has negation, candidate should too)
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0:
                score += 0.3
                reasons.append("matched negation")
            else:
                score -= 0.4
                reasons.append("missed negation")
        
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0:
                score += 0.2
                reasons.append("matched conditional")
            else:
                score -= 0.2
                reasons.append("missed conditional")

        # 3. Numeric Logic (Constraint Propagation)
        if p_feat['numbers'] or c_feat['numbers']:
            num_logic = self._check_numeric_logic(p_feat['numbers'], c_feat['numbers'])
            score += num_logic * 0.4
            if num_logic > 0.8:
                reasons.append("numeric logic consistent")
            elif num_logic < 0.5:
                reasons.append("numeric logic inconsistent")

        # 4. Exploration Bonus (Bandit)
        # Slight bonus for candidates that add specific detail (length) without exploding
        len_ratio = min(c_feat['length'] / (p_feat['length'] + 1), 2.0)
        if 0.5 < len_ratio < 1.5:
            score += 0.1
            reasons.append("optimal detail level")

        reason_str = "; ".join(reasons) if reasons else "structural baseline"
        return max(0.0, min(1.0, score)), reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._compute_bandit_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the internal scoring mechanism."""
        score, _ = self._compute_bandit_score(prompt, answer)
        return float(score)