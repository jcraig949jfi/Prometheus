import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Structural Parsing, 
    Optimal Control analogies, and Pragmatic constraints.
    
    Mechanism:
    1. Parsing: Extracts logical primitives (negations, comparatives, conditionals) 
       into a propositional state vector.
    2. Ecosystem/Control Analogy: Treats logical consistency as a 'flow conservation' 
       problem. Infeasible logical jumps incur high 'control costs' (u_k).
    3. Scoring: Computes a cost function J penalizing deviation from the prompt's 
       logical structure (Q matrix) and excessive logical manipulation (R matrix).
    4. Pragmatics: Adjusts weights based on relevance (Gricean maxims) to penalize 
       irrelevant or redundant information.
    5. Fallback: Uses NCD only if structural signals are weak.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features from text."""
        features = {
            'neg_count': len(self.patterns['negation'].findall(text)),
            'comp_count': len(self.patterns['comparative'].findall(text)),
            'cond_count': len(self.patterns['conditional'].findall(text)),
            'causal_count': len(self.patterns['causal'].findall(text)),
            'quant_count': len(self.patterns['quantifier'].findall(text)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text.split()),
            'text_lower': text.lower()
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Check if numeric relationships are preserved (simplified)."""
        if not prompt_nums or not cand_nums:
            return 0.0
        
        # Simple heuristic: If prompt has ordered numbers, check if candidate respects order
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            p_diff = prompt_nums[-1] - prompt_nums[0]
            c_diff = cand_nums[-1] - cand_nums[0]
            if p_diff == 0: return 1.0 if c_diff == 0 else 0.5
            if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0):
                return 1.0
            return 0.2 # Penalty for reversing order
        return 0.5

    def _compute_logical_cost(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute the 'Control Cost' (u_k^T R u_k) based on logical deviations.
        High cost if candidate misses key logical operators present in prompt.
        """
        cost = 0.0
        
        # Penalty for missing negations (critical for logic)
        if prompt_feats['neg_count'] > 0:
            if cand_feats['neg_count'] == 0:
                cost += 2.0 # High penalty
            elif abs(cand_feats['neg_count'] - prompt_feats['neg_count']) > 1:
                cost += 0.5 # Moderate penalty for over-negation
        
        # Penalty for missing conditionals/causality
        if prompt_feats['cond_count'] > 0 and cand_feats['cond_count'] == 0:
            cost += 1.5
        if prompt_feats['causal_count'] > 0 and cand_feats['causal_count'] == 0:
            cost += 1.5
            
        # Pragmatic penalty: Relevance (Length mismatch penalty)
        len_ratio = cand_feats['length'] / max(prompt_feats['length'], 1)
        if len_ratio < 0.5 or len_ratio > 3.0:
            cost += 1.0 # Too short or too verbose
            
        return cost

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Baseline structural signal strength
        prompt_signal_strength = (prompt_feats['neg_count'] + prompt_feats['cond_count'] + 
                                  prompt_feats['causal_count'] + len(prompt_feats['numbers']))
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural/Logical Scoring (Primary)
            logical_cost = self._compute_logical_cost(prompt_feats, cand_feats)
            numeric_score = self._check_numeric_consistency(prompt_feats['numbers'], cand_feats['numbers'])
            
            # Normalize logical cost to a 0-1 penalty (higher cost = lower score)
            # Assuming max reasonable cost ~5.0 for scaling
            logic_score = max(0.0, 1.0 - (logical_cost / 5.0))
            
            # Combine: Weighted sum favoring logic
            # If prompt has strong structure, logic dominates. If weak, rely more on NCD.
            structure_weight = min(1.0, prompt_signal_strength * 0.3) 
            ncd_weight = 1.0 - structure_weight
            
            # 2. NCD Scoring (Secondary/Tiebreaker)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Final Score Calculation
            final_score = (logic_score * (0.7 + 0.3*structure_weight)) + \
                          (ncd_score * ncd_weight * 0.4) + \
                          (numeric_score * 0.2)
            
            # Adjust for specific numeric contradictions (hard constraint)
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # If numbers exist but logic failed completely, penalize heavily
                if logical_cost > 3.0:
                    final_score *= 0.5

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Logic:{logic_score:.2f}, NCD:{ncd_score:.2f}, Num:{numeric_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        Uses the internal evaluation logic but returns a single scalar.
        """
        # Evaluate as a single candidate
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        score = res_list[0]['score']
        
        # Calibration: Map score to confidence
        # Scores > 0.7 are high confidence, < 0.3 are low
        confidence = max(0.0, min(1.0, (score - 0.3) / 0.7))
        return float(confidence)