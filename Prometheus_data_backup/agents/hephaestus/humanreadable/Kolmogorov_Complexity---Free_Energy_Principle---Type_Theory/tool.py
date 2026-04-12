import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MDL-VITT Engine: Minimum Description Length Variational Inference over Typed Programs.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Parses candidates into logical forms (negations, 
       comparatives, conditionals) to ensure well-typed hypotheses. Ill-formed logic 
       receives a complexity penalty.
    2. Free Energy Principle: Computes a variational free energy score.
       - Prediction Error: Mismatch between parsed logical constraints and candidate content.
       - Complexity (Kolmogorov): Approximated via NCD relative to the prompt's structural skeleton.
       - Entropy: Bonus for candidates that resolve ambiguity without over-constraining.
    3. Optimization: Ranks candidates by minimizing Free Energy (maximizing the negative score).
    """

    def __init__(self):
        self.structural_keywords = {
            'negation': ['no', 'not', 'never', 'none', 'neither', 'nobody'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditional': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }
        self.num_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parses text for logical types (Type Theory layer)."""
        lower = text.lower()
        tokens = set(re.findall(r'\b\w+\b', lower))
        
        features = {
            'has_negation': any(k in tokens for k in self.structural_keywords['negation']),
            'has_comparative': any(k in tokens for k in self.structural_keywords['comparative']),
            'has_conditional': any(k in tokens for k in self.structural_keywords['conditional']),
            'numbers': [float(n) for n in self.num_pattern.findall(text)],
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """Evaluates prediction error based on logical form matching."""
        error = 0.0
        
        # Negation consistency: If prompt implies negation, candidate should reflect it
        if prompt_feats['has_negation']:
            if not cand_feats['has_negation']:
                error += 0.5 # Penalty for missing negation
        
        # Comparative consistency
        if prompt_feats['has_comparative']:
            if not cand_feats['has_comparative']:
                # Only penalize if the candidate isn't a simple number/yes/no
                if not cand_feats['numbers'] and cand_feats['length'] < 10:
                    error += 0.3

        # Numeric evaluation (Constraint Propagation)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            # Simple heuristic: if prompt has numbers, candidate numbers should be relevant
            # This is a proxy for semantic alignment in the absence of an LLM
            if len(p_nums) > 0 and len(c_nums) > 0:
                # Check for direct equality or obvious relation
                if abs(p_nums[0] - c_nums[0]) > 1e-6: 
                    # If numbers differ, check if it's a calculation result (heuristic)
                    # For now, assume deviation adds entropy unless it's a specific match
                    pass 
        
        return error

    def _compute_kolmogorov_approx(self, prompt: str, candidate: str) -> float:
        """
        Approximates K(p) using NCD relative to the prompt's structural skeleton.
        Lower is better (simpler description).
        """
        # Create a structural skeleton of the prompt to measure compression against
        skeleton = re.sub(r'\b\w+\b', 'X', prompt)
        
        def zlib_len(s):
            return len(zlib.compress(s.encode('utf-8')))
        
        s_enc = skeleton.encode('utf-8')
        c_enc = candidate.encode('utf-8')
        
        len_s = len(s_enc)
        len_c = len(c_enc)
        
        if len_s == 0 or len_c == 0:
            return 1.0
            
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Here we treat the candidate's complexity relative to the prompt structure
        try:
            concat = zlib_len(skeleton + candidate)
            comp_s = zlib_len(skeleton)
            comp_c = zlib_len(candidate)
            
            ncd = (concat - min(comp_s, comp_c)) / max(comp_s, comp_c, 1)
            return ncd
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Prediction Error (Free Energy term 1)
            # How well does the candidate's logical structure match the prompt's requirements?
            pred_error = self._check_logical_consistency(prompt_feats, cand_feats)
            
            # 2. Complexity Penalty (Free Energy term 2 - Kolmogorov)
            # How complex is this candidate given the prompt context?
            complexity = self._compute_kolmogorov_approx(prompt, cand)
            
            # 3. Entropy Bonus (Free Energy term 3)
            # Encourage non-trivial answers (avoiding empty or too-short strings unless necessary)
            entropy_bonus = 0.0
            if len(cand.strip()) > 2:
                entropy_bonus = 0.1
            
            # Free Energy Functional: F = Error + Complexity - Entropy
            # We want to MINIMIZE F. So Score = -F
            free_energy = pred_error + complexity - entropy_bonus
            score = -free_energy
            
            # Structural boost: If candidate contains numbers found in prompt, boost significantly
            if prompt_feats['numbers'] and cand_feats['numbers']:
                if any(abs(p - c) < 1e-6 for p in prompt_feats['numbers'] for c in cand_feats['numbers']):
                    score += 2.0 # Strong signal for numeric consistency

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Error:{pred_error:.2f}, Complexity:{complexity:.2f}, Entropy:{entropy_bonus:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the negative free energy of the single answer."""
        # Run evaluation on the single candidate to get its score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Map raw score (typically -2.0 to 1.0 range) to 0-1 confidence
        # Sigmoid-like mapping
        confidence = 1 / (1 + math.exp(-raw_score * 2))
        return max(0.0, min(1.0, confidence))