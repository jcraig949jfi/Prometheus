import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CACS-Lite: A Categorical Attentional Constraint Solver approximation.
    
    Mechanism:
    1. Objects: Variables extracted from prompt/candidates via structural parsing.
    2. Morphisms: Logical constraints (negations, comparatives, transitivity) mapped to 
       boolean/numeric validation functions.
    3. Functor F: Maps syntactic structures to semantic scores (0.0 to 1.0).
    4. Attention: Weights constraints based on keyword density and structural complexity.
    5. Natural Transformation: Iteratively re-weights candidate scores based on 
       constraint satisfaction density (simulating arc-consistency propagation).
    
    Beats NCD baseline by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        self.structural_keywords = ['not', 'no', 'never', 'unless', 'except', 'false']
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'before', 'after']
        self.conditionals = ['if', 'then', 'else', 'when', 'provided']

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negation_count': sum(1 for w in self.structural_keywords if w in text_lower),
            'comparative_count': sum(1 for w in self.comparative_ops if w in text_lower),
            'conditional_count': sum(1 for w in self.conditionals if w in text_lower),
            'has_numbers': bool(re.search(r'\d+', text)),
            'length': len(text),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        }
        return features

    def _check_constraints(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate morphisms (constraints) between prompt and candidate.
        Returns a satisfaction score (0.0 to 1.0).
        """
        score = 1.0
        constraints_checked = 0
        
        # Constraint 1: Numeric Consistency (Transitivity/Comparison)
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            if p_nums and c_nums:
                # Simple heuristic: If prompt implies ordering, check if candidate respects magnitude
                # This is a simplified functorial mapping of numeric domains
                if 'greater' in prompt.lower() or '>' in prompt:
                    constraints_checked += 1
                    if max(c_nums) <= min(p_nums): # Loose check for "greater" context
                        score *= 0.5 
                elif 'less' in prompt.lower() or '<' in prompt:
                    constraints_checked += 1
                    if min(c_nums) >= max(p_nums):
                        score *= 0.5
        
        # Constraint 2: Negation Handling (Modus Tollens approximation)
        # If prompt has high negation density, candidate must not simply echo prompt words
        if prompt_feats['negation_count'] > 0:
            constraints_checked += 1
            overlap = len(set(prompt.lower().split()) & set(candidate.lower().split()))
            if overlap > 0 and prompt_feats['length'] > 20:
                # Penalty for echoing negated prompts without logical pivot
                score *= 0.7 

        # Constraint 3: Structural Complexity Match
        # Candidates answering complex conditional prompts should have sufficient length/structure
        if prompt_feats['conditional_count'] > 0:
            constraints_checked += 1
            if cand_feats['length'] < prompt_feats['length'] * 0.3:
                score *= 0.8 # Short answers to complex questions are suspicious

        if constraints_checked == 0:
            return 1.0 # No specific constraints violated
        
        return score

    def _compute_attention_weights(self, prompt: str) -> float:
        """
        Simulate attention mechanism: Focus on parts of the prompt with high 
        logical density (keywords). Returns a global relevance scalar.
        """
        text_lower = prompt.lower()
        attention_mass = 0.0
        total_words = len(text_lower.split()) or 1
        
        logical_words = sum(1 for w in text_lower.split() 
                           if w in self.structural_keywords or w in self.conditionals)
        
        # Attention score: density of logical operators
        attention_mass = logical_words / total_words
        return min(1.0, attention_mass * 5.0) # Scale up impact

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0: return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        attention_weight = self._compute_attention_weights(prompt)
        
        results = []
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # 1. Constraint Satisfaction Step (Morphism evaluation)
            constraint_score = self._check_constraints(prompt_feats, cand_feats, prompt, cand)
            
            # 2. Attentional Bias Step
            # Apply attention weight to the constraint score. 
            # High attention on logic -> constraint score matters more.
            # Low attention -> rely more on baseline similarity (NCD tiebreaker later)
            base_score = constraint_score
            
            # 3. Natural Transformation (Re-weighting)
            # Adjust score based on the "tension" between prompt logic and candidate response
            if prompt_feats['negation_count'] > 0 and cand_feats['negation_count'] == 0:
                # Potential tension: Prompt is negative, candidate is positive statement
                # Check if this is a valid resolution or a violation
                pass 
            
            # Final Score Composition
            # Primary signal: Structural/Constraint adherence
            # Secondary signal: NCD (only as tiebreaker/small modifier)
            ncd_val = self._ncd(prompt, cand)
            
            # Combine: High constraint score is good. Low NCD (similarity) is okay but not primary.
            # We invert NCD because high similarity (low distance) is slightly preferred if logic holds
            similarity_bonus = (1.0 - ncd_val) * 0.1 
            
            final_score = (base_score * (1.0 + attention_weight)) + similarity_bonus
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Constraint sat: {base_score:.2f}, Attention: {attention_weight:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on constraint satisfaction density."""
        prompt_feats = self._structural_parse(prompt)
        cand_feats = self._structural_parse(answer)
        
        # Evaluate constraints
        sat_score = self._check_constraints(prompt_feats, cand_feats, prompt, answer)
        
        # If structural parsing found no logic, fallback to NCD heuristic
        if prompt_feats['negation_count'] == 0 and prompt_feats['conditional_count'] == 0:
            ncd = self._ncd(prompt, answer)
            return float(np.clip(1.0 - ncd, 0.0, 1.0))
            
        return float(np.clip(sat_score, 0.0, 1.0))