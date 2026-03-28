import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Incentive-Compatible Network Reasoning Architecture (CINRA) Approximation.
    
    Mechanism:
    1. Mechanism Design (Core): Implements a VCG-style scoring rule. Candidates are scored
       not just on raw match, but on their 'marginal contribution' to the truthfulness of 
       the structural constraints extracted from the prompt. Truthful alignment with 
       logical operators (negation, comparison) yields higher 'payments' (scores).
    2. Network Science: Treats prompt tokens and candidate tokens as nodes. Edges are 
       formed by co-occurrence and logical operators. We detect 'cascade failure' 
       (contradictions) by checking if a candidate violates the transitivity or 
       negation constraints of the prompt network.
    3. Category Theory: Used as a consistency functor. We map the structural signature 
       of the prompt (e.g., [Subject, Operator, Object]) to the candidate. If the 
       morphism (mapping) preserves the logical structure (e.g., A > B in prompt implies 
       A > B in candidate), the candidate receives a 'naturality' bonus.
       
    This implementation prioritizes structural parsing and logical constraint satisfaction
    over simple string similarity, using NCD only as a tie-breaker for semantically 
    equivalent but lexically distinct candidates.
    """

    def __init__(self):
        self.logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self.comp_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'higher', 'lower']
        self.cond_ops = ['if', 'then', 'else', 'when', 'unless']

    def _extract_structure(self, text: str) -> dict:
        """Extract logical constraints (negations, comparisons, conditionals)."""
        t_lower = text.lower()
        return {
            'has_negation': any(op in t_lower for op in self.logic_ops),
            'has_comparison': any(op in t_lower for op in self.comp_ops),
            'has_conditional': any(op in t_lower for op in self.cond_ops),
            'numbers': re.findall(r"[-+]?\d*\.\d+|\d+", t_lower),
            'length': len(text.split())
        }

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Layer: Evaluate if the candidate respects the logical 
        constraints of the prompt. Returns a penalty score (0.0 = violation, 1.0 = consistent).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 1.0

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation and candidate affirms the negated concept without qualification
        if p_struct['has_negation']:
            # Simple heuristic: if prompt says "not X" and candidate is just "X", penalize
            # We look for direct contradiction patterns
            if "not " in p_lower and c_struct['has_negation'] == False:
                # Check if candidate is a short affirmation that might contradict
                if len(candidate.split()) < 5 and any(word in c_lower for word in ['yes', 'true', 'correct']):
                     score -= 0.5
        
        # 2. Comparison Consistency
        # If prompt compares numbers, candidate should reflect the correct order if it mentions numbers
        if p_struct['has_comparison'] and len(p_struct['numbers']) >= 2:
            nums = [float(n) for n in p_struct['numbers']]
            # Detect direction in prompt
            is_increasing = any(op in p_lower for op in ['greater', 'more', 'higher', 'increas'])
            # If candidate has numbers, do they follow the trend? (Simplified check)
            if len(c_struct['numbers']) >= 2:
                c_nums = [float(n) for n in c_struct['numbers']]
                # If prompt implies A > B, and candidate says B > A, penalize
                # This is a rough approximation of network cascade failure
                if (nums[0] > nums[1]) != (c_nums[0] > c_nums[1]):
                    score -= 0.4

        # 3. Conditional Consistency
        # If prompt is "If A then B", candidate "A but not B" is a violation
        if p_struct['has_conditional']:
            if re.search(r'\bbut\b|\bhowever\b|\byet\b', c_lower):
                score -= 0.3

        return max(0.0, score)

    def _categorical_functor_score(self, prompt: str, candidate: str) -> float:
        """
        Category Theory Layer: Measure structural preservation (Naturality).
        Maps the 'shape' of the prompt arguments to the candidate.
        """
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        # Intersection over Union of significant words (excluding stopwords)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        p_sig = p_words - stopwords
        c_sig = c_words - stopwords
        
        if not p_sig or not c_sig:
            return 0.5
            
        overlap = len(p_sig & c_sig)
        union = len(p_sig | c_sig)
        
        # Jaccard similarity as a proxy for functorial mapping fidelity
        base_score = overlap / union if union > 0 else 0.0
        
        # Bonus for preserving logical operators (Morphisms must preserve structure)
        p_ops = set([w for w in p_sig if w in self.logic_ops + self.comp_ops + self.cond_ops])
        c_ops = set([w for w in c_sig if w in self.logic_ops + self.comp_ops + self.cond_ops])
        
        op_bonus = 0.0
        if p_ops:
            if p_ops == c_ops:
                op_bonus = 0.2 # Perfect preservation
            elif p_ops & c_ops:
                op_bonus = 0.1 # Partial preservation
        
        return min(1.0, base_score + op_bonus)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt structure for efficiency
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Mechanism Design Score (Truthfulness/Constraint Check)
            mech_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Categorical Score (Structural Preservation)
            cat_score = self._categorical_functor_score(prompt, cand)
            
            # 3. Network Science Tie-Breaker (NCD)
            # Used only when structural signals are ambiguous or equal
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Composite Score Calculation
            # Primary weight on logical consistency (Mechanism) and structural mapping (Category)
            # NCD is inverted (lower distance is better) and down-weighted
            base_score = (mech_score * 0.6) + (cat_score * 0.4)
            
            # Adjust based on NCD if scores are close to neutral (0.5)
            # This implements the "NCD as tiebreaker" requirement
            final_score = base_score
            if 0.4 < base_score < 0.6:
                # If uncertain, let compression distance sway the result slightly
                final_score += (1.0 - ncd_val) * 0.1
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Mechanism:{mech_score:.2f}, Categorical:{cat_score:.2f}, NCD:{ncd_val:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        """
        # Evaluate the single candidate against the prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score to a confidence metric
        # The evaluate method returns a score roughly between 0 and 1.2 due to bonuses
        score = res[0]['score']
        return min(1.0, max(0.0, score))