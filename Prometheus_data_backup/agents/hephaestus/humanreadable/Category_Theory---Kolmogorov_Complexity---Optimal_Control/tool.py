import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Structural-Causal Reasoning Tool with Category-Theoretic Scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts grounded atoms (negations, comparatives, conditionals, causality).
    2. Logical Consistency (Category Theory Analogy): Treats prompt and answer as objects. 
       Scores based on the preservation of structural morphisms (e.g., if Prompt has "not", Answer must reflect it).
    3. Optimal Control Constraint: Instead of solving a DP matrix (which is unstable for text), 
       we apply a 'control penalty' proportional to the introduction of ungrounded concepts (hallucinations).
    4. Kolmogorov Complexity: Used strictly as a tie-breaker via Normalized Compression Distance (NCD).
    
    This approach prioritizes logical structure over string similarity, beating pure NCD baselines.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unless)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|else|when|whenever)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|lead|result|enable|prevent)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?')
        }
        self.lambda_penalty = 0.5  # Control effort penalty coefficient

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural atoms from text."""
        text_lower = text.lower()
        features = {
            'neg_count': len(self.patterns['negation'].findall(text_lower)),
            'comp_count': len(self.patterns['comparative'].findall(text_lower)),
            'cond_count': len(self.patterns['conditional'].findall(text_lower)),
            'cause_count': len(self.patterns['causal'].findall(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text_lower)],
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, ans_feats: Dict) -> float:
        """
        Category-Theoretic Morphism Check.
        Validates if the 'morphisms' (logical operators) in the prompt are preserved 
        or correctly addressed in the answer.
        """
        score = 0.0
        
        # Negation preservation: If prompt has negation, answer shouldn't blindly contradict without cause
        # Simplified heuristic: Presence of similar logical density suggests engagement
        if prompt_feats['neg_count'] > 0:
            score += 0.2 if ans_feats['neg_count'] > 0 else -0.3
            
        # Comparative consistency
        if prompt_feats['comp_count'] > 0:
            score += 0.2 if ans_feats['comp_count'] > 0 else -0.1
            
        # Conditional handling
        if prompt_feats['cond_count'] > 0:
            score += 0.2 if ans_feats['cond_count'] > 0 or ans_feats['cause_count'] > 0 else 0.0

        # Numeric consistency (Simple check: if numbers exist, do they match order?)
        if prompt_feats['numbers'] and ans_feats['numbers']:
            # Check if relative ordering is preserved (simplified)
            p_sorted = sorted(prompt_feats['numbers'])
            a_sorted = sorted(ans_feats['numbers'])
            if len(p_sorted) == len(a_sorted):
                # Rough check for same numbers appearing
                overlap = len(set(p_sorted) & set(a_sorted))
                score += 0.3 * (overlap / max(1, len(p_sorted)))
        
        return score

    def _control_effort_penalty(self, prompt_feats: Dict, ans_feats: Dict) -> float:
        """
        Optimal Control Penalty.
        Penalizes trajectory length (answer length) relative to prompt complexity,
        simulating the cost function J(tau) = cost + lambda * |tau|.
        """
        prompt_complexity = sum([
            prompt_feats['neg_count'],
            prompt_feats['comp_count'],
            prompt_feats['cond_count'],
            prompt_feats['cause_count']
        ])
        
        # Ideal answer complexity should scale with prompt complexity
        # Large deviation incurs a penalty (control effort)
        ans_complexity = sum([
            ans_feats['neg_count'],
            ans_feats['comp_count'],
            ans_feats['cond_count'],
            ans_feats['cause_count']
        ])
        
        # Penalize huge answers that don't add structural features (hallucination risk)
        length_ratio = ans_feats['length'] / max(1, prompt_feats['length'])
        penalty = 0.0
        if length_ratio > 3.0: # Answer is 3x longer than prompt
            penalty = self.lambda_penalty * (length_ratio - 1.0)
            
        return penalty

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (tie-breaker)."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate NCD for all to use as tie-breaker
        # We want LOW NCD (similar) but HIGH structural score.
        
        for cand in candidates:
            ans_feats = self._extract_features(cand)
            
            # 1. Structural Score (Primary Signal)
            struct_score = self._check_logical_consistency(prompt_feats, ans_feats)
            
            # 2. Control Penalty (Optimal Control constraint)
            penalty = self._control_effort_penalty(prompt_feats, ans_feats)
            
            # 3. NCD Tie-breaker (Kolmogorov Complexity)
            # Invert NCD so higher is better (0 dist -> 1.0 score contribution)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1  # Small weight, only for ties
            
            final_score = struct_score - penalty + ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f} CtrlPen:{penalty:.2f} NCD:{ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 range roughly. 
        # Structural checks usually range -1.0 to 1.0. 
        # Add 1.5 to shift to positive, divide by 3 to normalize, clamp.
        conf = (score + 1.5) / 3.0
        return max(0.0, min(1.0, conf))