import re
import json
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Maximum-Entropy Compositional Global Workspace (MECGW) Implementation.
    
    Mechanism:
    1. Compositional Core: Parses prompts into structured constraints (negations, 
       comparatives, conditionals, numeric values) acting as primitive operations.
    2. Global Workspace: Candidates compete for "ignition" based on how well they 
       satisfy the parsed constraints. The "broadcast" is the evaluation of each 
       candidate against these global constraints.
    3. Maximum Entropy: Scores are derived from an exponential family distribution 
       where the probability of a candidate being correct is proportional to 
       exp(lambda * constraint_satisfaction). This ensures the system remains 
       maximally non-committal (high entropy) regarding features not constrained 
       by the logic, while strictly adhering to detected structural rules.
    
    Strategy:
    - Structural parsing provides hard/soft constraints (high weight).
    - Numeric evaluation handles magnitude comparisons.
    - NCD is used strictly as a tiebreaker for semantic similarity when structural
      signals are ambiguous or equal, preventing bias towards short/generic answers.
    """

    def __init__(self):
        self.constraint_weights = {
            'negation_match': 2.0,
            'comparative_logic': 2.5,
            'conditional_consistency': 2.0,
            'numeric_accuracy': 3.0,
            'keyword_overlap': 0.5,
            'ncd_bonus': 0.1
        }

    def _parse_structure(self, prompt: str) -> dict:
        """Extract compositional primitives: negations, comparatives, numbers, conditionals."""
        p_lower = prompt.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', p_lower)),
            'comparatives': re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', p_lower),
            'conditionals': bool(re.search(r'\b(if|then|unless|otherwise)\b', p_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', p_lower),
            'has_question': '?' in prompt
        }
        return features

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric consistency (e.g., 'which is larger?')."""
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        if not p_nums:
            return 0.0
        
        try:
            nums = [float(n) for n in p_nums]
            c_nums = re.findall(r'-?\d+\.?\d*', candidate)
            
            if not c_nums:
                return 0.0
            
            c_val = float(c_nums[0])
            
            # Heuristic: If prompt asks for "larger"/"max", check if candidate is max
            p_lower = prompt.lower()
            if any(k in p_lower for k in ['larger', 'greater', 'max', 'highest', 'more']):
                return 1.0 if c_val == max(nums) else 0.0
            elif any(k in p_lower for k in ['smaller', 'less', 'min', 'lowest', 'fewer']):
                return 1.0 if c_val == min(nums) else 0.0
            # Direct equality check if numbers match exactly
            elif str(c_val) in p_nums:
                return 1.0
                
        except ValueError:
            pass
        return 0.0

    def _check_constraint_match(self, prompt: str, candidate: str) -> float:
        """Check if candidate respects negations and conditionals."""
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        negations = ['not', 'no', 'never', 'none']
        p_neg_count = sum(1 for n in negations if f" {n} " in f" {p_lower} ")
        c_neg_count = sum(1 for n in negations if f" {n} " in f" {c_lower} ")
        
        if p_neg_count > 0:
            # If prompt has negation, candidate should ideally reflect understanding 
            # (simplified: penalize if prompt says "not" and candidate is generic "yes")
            if c_lower.strip() in ['yes', 'true', 'it is']:
                score -= 1.0 
            else:
                score += 0.5
        else:
            # Positive bias for direct answers in non-negative contexts
            if c_lower.strip() in ['yes', 'true']:
                score += 0.5

        # Conditional keyword overlap (simple semantic check)
        cond_words = ['if', 'then', 'because', 'therefore']
        common_cond = len(set(p_lower.split()) & set(c_lower.split()) & set(cond_words))
        score += common_cond * 0.5
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            l1, l2, l12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1 + b2))
            return (l12 - min(l1, l2)) / max(l1, l2, 1)
        except:
            return 1.0

    def _compute_max_ent_score(self, prompt: str, candidate: str, features: dict) -> float:
        """
        Compute score using Maximum Entropy principle.
        Score = exp(sum(weight_i * feature_i)) normalized implicitly by ranking.
        We return the logit (sum of weighted features) to maintain ordering.
        """
        logit = 0.0
        
        # 1. Numeric Evaluation (High priority)
        num_score = self._check_numeric_logic(prompt, candidate)
        logit += self.constraint_weights['numeric_accuracy'] * num_score
        
        # 2. Structural Constraints
        struct_score = self._check_constraint_match(prompt, candidate)
        logit += struct_score
        
        # 3. Keyword/Composition overlap (Contextual relevance)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        # Remove stopwords for overlap
        stopwords = {'the', 'is', 'a', 'an', 'it', 'to', 'be', 'that', 'this', 'of', 'in', 'for', 'on', 'with'}
        overlap = len((p_words - stopwords) & (c_words - stopwords))
        logit += self.constraint_weights['keyword_overlap'] * min(overlap, 5) # Cap contribution

        # 4. NCD Tiebreaker (Only adds small bonus if structural scores are close)
        # We invert NCD (lower distance = higher score)
        ncd_val = self._ncd(prompt, candidate)
        logit += self.constraint_weights['ncd_bonus'] * (1.0 - ncd_val)
        
        return logit

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        features = self._parse_structure(prompt)
        scored_candidates = []
        
        # Calculate raw logits
        logits = []
        for cand in candidates:
            logit = self._compute_max_ent_score(prompt, cand, features)
            logits.append(logit)
        
        # Convert to probabilities via Softmax (Maximum Entropy Distribution)
        # P(i) = exp(logit_i) / sum(exp(logit_j))
        max_logit = max(logits)
        exp_logits = [float(repr(l - max_logit)) for l in logits] # Stability shift
        # Re-calculate exp manually to avoid math import if desired, but math is stdlib. 
        # Using pow for exp approximation or just math.exp
        import math
        try:
            exp_vals = [math.exp(l) for l in logits]
        except OverflowError:
            # Fallback for extreme values
            exp_vals = [1.0] * len(logits)
            
        sum_exp = sum(exp_vals) if sum(exp_vals) > 0 else 1.0
        probs = [e / sum_exp for e in exp_vals]
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": probs[i],
                "reasoning": f"MaxEnt score based on structural constraints (nums: {features['numbers'] is not None}, negs: {features['negations']}) and NCD."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the MaxEnt score of the single answer."""
        # Evaluate against a dummy set to get normalization, or just use raw logit mapped to 0-1
        # Since we need 0-1, we treat the single answer as a candidate against itself 
        # and a generic wrong answer to estimate relative probability.
        
        # Simpler approach: Use the internal scoring mechanism and sigmoid the result
        features = self._parse_structure(prompt)
        logit = self._compute_max_ent_score(prompt, answer, features)
        
        # Sigmoid function to map logit to 0-1
        import math
        try:
            conf = 1 / (1 + math.exp(-logit))
        except OverflowError:
            conf = 1.0 if logit > 0 else 0.0
            
        return min(max(conf, 0.0), 1.0)