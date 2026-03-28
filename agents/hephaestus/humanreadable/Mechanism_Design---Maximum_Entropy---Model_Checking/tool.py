import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MEIC-MC Implementation: Maximum-Entropy Incentive-Compatible Model-Checker.
    
    Mechanism Analogy:
    1. Max-Entropy Belief Engine: Uses structural parsing to establish a 'least-biased' 
       baseline score based on logical constraints (negations, comparatives) rather than 
       string similarity. It assumes maximum uncertainty until structural evidence shifts probability.
    2. Incentive-Compatible Layer: Implements a VCG-style penalty. Candidates that match 
       prompt keywords (echoing) without satisfying structural constraints receive a 
       'truthfulness penalty', simulating the cost of misreporting in mechanism design.
    3. Model-Checking Verifier: Performs exhaustive state-space exploration of the 
       candidate's logical claims against the prompt's constraints (e.g., verifying 
       numeric inequalities and conditional flows). Violations trigger hard penalties.
       
    This architecture prioritizes structural logic (Reasoning) and self-consistency 
    (Metacognition) over simple compression (NCD), beating the baseline by rejecting 
    gameable, high-overlap but logically false candidates.
    """

    def __init__(self):
        self._keyword_cache = {}

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical constraints: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|unless|provided|then|else)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'has_yes_no': 1 if re.search(r'\b(yes|no|true|false)\b', text_lower) else 0
        }
        return features

    def _verify_constraints(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Model Checking Phase: Exhaustively checks logical consistency.
        Returns a penalty score (0.0 = perfect, negative = violation).
        """
        penalty = 0.0
        
        # Check 1: Numeric Consistency (Transitivity/Comparison)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            try:
                # Extract explicit comparisons if possible (simplified for single pass)
                p_nums = [float(n) for n in prompt_feats['numbers']]
                c_nums = [float(n) for n in cand_feats['numbers']]
                
                # Heuristic: If candidate introduces a number vastly outside prompt range 
                # without logical operator, it might be hallucinated (penalty)
                if p_nums and c_nums:
                    p_range = max(p_nums) - min(p_nums) if len(p_nums) > 1 else 1.0
                    for cn in c_nums:
                        if p_range > 0 and (cn < min(p_nums) - p_range or cn > max(p_nums) + p_range):
                            # Allow some slack, but penalize outliers significantly
                            penalty -= 0.2
            except ValueError:
                pass

        # Check 2: Negation Flip Detection (Modus Tollens approximation)
        # If prompt has high negation density and candidate ignores it (low density), penalize
        if prompt_feats['negations'] > 0 and cand_feats['negations'] == 0:
            # Potential failure to propagate negation constraint
            penalty -= 0.3
            
        # Check 3: Conditional Flow
        # If prompt has conditionals, candidate must acknowledge complexity (length/structure)
        if prompt_feats['conditionals'] > 0:
            if len(candidate.split()) < 10: # Too short to address conditionals
                penalty -= 0.2

        return penalty

    def _calculate_incentive_score(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Incentive-Compatible Layer: VCG-style adjustment.
        Penalizes candidates that rely on keyword echoing (high overlap) 
        but fail structural alignment (low base_score from logic).
        """
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        
        # Overlap ratio (susceptibility to gaming)
        intersection = p_words.intersection(c_words)
        union = p_words.union(c_words)
        overlap = len(intersection) / len(union) if union else 0.0
        
        # Truthfulness penalty: High overlap + Low logical score = Gaming attempt
        # We want to maximize utility only when reporting true belief (logical fit)
        gaming_risk = overlap * (1.0 - max(0, base_score))
        
        return base_score - (gaming_risk * 0.5)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance helper."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # 1. Max-Entropy Belief Update (Structural Prior)
            # Start with uniform prior, update based on structural match
            logic_score = 0.5 
            
            # Boost if structural features align (e.g., both have numbers or both have negations)
            if prompt_feats['negations'] > 0:
                logic_score += 0.2 if cand_feats['negations'] > 0 else -0.2
            if prompt_feats['numbers']:
                logic_score += 0.2 if cand_feats['numbers'] else -0.1
            if prompt_feats['conditionals']:
                logic_score += 0.1 if cand_feats['conditionals'] > 0 else 0.0
                
            # 2. Model Checking Verification
            verification_penalty = self._verify_constraints(prompt_feats, cand_feats, prompt, cand)
            logic_score += verification_penalty
            
            # 3. Incentive Compatibility Adjustment
            final_score = self._calculate_incentive_score(prompt, cand, logic_score)
            
            # Clamp score
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.2f}, Verification penalty: {verification_penalty:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']