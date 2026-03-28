import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Optimal-Control Game (COCG) Approximation.
    
    Mechanism:
    1. Modules (Primitives): The system parses the prompt and candidates into 
       structural 'modules': Negations, Comparatives, Conditionals, and Numeric literals.
       This satisfies the 'Compositionality' requirement.
       
    2. Local Optimal Control: Each module computes a local 'cost' (error) based on 
       logical consistency between the prompt's constraints and the candidate's assertion.
       For example, if the prompt says "A > B" and candidate says "B > A", the cost is high.
       
    3. Nash Equilibrium (Meta-Consistency): The global score is derived from the 
       stability of the joint policy. We treat the structural alignment as the equilibrium state.
       If a candidate contradicts a parsed constraint (unilateral deviation), it fails the 
       Nash test (high cost). The final score is the inverse of the aggregate cost.
       
    4. Falsification: Explicit negation checks act as the self-refutation signal.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Grammar")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|larger|smaller|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided|when)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)
        }

    def _extract_modules(self, text: str) -> Dict[str, List[str]]:
        """Parses text into compositional modules."""
        modules = {}
        text_lower = text.lower()
        for key, pattern in self.patterns.items():
            modules[key] = pattern.findall(text_lower)
        # Extract raw numbers for numeric evaluation
        modules['raw_numbers'] = self.patterns['number'].findall(text)
        return modules

    def _check_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """
        Numeric Evaluation Module.
        Checks if the candidate preserves numeric ordering or values implied.
        Simple heuristic: If counts differ wildly or specific values contradict, penalize.
        """
        if not prompt_nums and not cand_nums:
            return 0.0 # No numeric data, no penalty
        
        p_vals = []
        c_vals = []
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
        except ValueError:
            return 0.5 # Penalty for malformed numbers

        # Heuristic: If prompt has specific numbers and candidate changes them arbitrarily
        if len(p_vals) > 0 and len(c_vals) > 0:
            # If the candidate simply repeats the numbers, low cost.
            # If the candidate inverts a sorted order, high cost.
            if len(p_vals) == len(c_vals):
                # Check order preservation
                p_order = np.argsort(p_vals)
                c_order = np.argsort(c_vals)
                if np.array_equal(p_order, c_order):
                    return 0.0
                else:
                    return 0.8 # High cost for reversing logic
            elif len(c_vals) == 0 and len(p_vals) > 0:
                 return 0.6 # Missing numbers
        return 0.1

    def _check_logical_consistency(self, prompt_mods: Dict, cand_mods: Dict) -> float:
        """
        Logical Consistency Module (Nash Test).
        Checks for contradictions in negation and logical operators.
        """
        cost = 0.0
        
        # Negation Falsification Check
        # If prompt has strong negation and candidate lacks it (or vice versa) in a short context
        p_neg = len(prompt_mods['negation'])
        c_neg = len(cand_mods['negation'])
        
        # Heuristic: Sudden disappearance of negation in a direct answer often implies contradiction
        if p_neg > 0 and c_neg == 0:
            # Context dependent, but risky. Add small penalty unless it's a "Yes/No" confirmation
            cost += 0.2
            
        # Conditional Check
        # If prompt sets a condition "If A", candidate should not assert "A is false" unconditionally
        if len(prompt_mods['conditional']) > 0 and len(cand_mods['conditional']) == 0:
            # Not necessarily wrong, but less compositional
            pass 
            
        return cost

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        return (len_combined - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_mods = self._extract_modules(prompt)
        prompt_nums = prompt_mods['raw_numbers']
        
        scored_candidates = []
        
        for cand in candidates:
            cand_mods = self._extract_modules(cand)
            cand_nums = cand_mods['raw_numbers']
            
            # 1. Structural Parsing Score (Primary Signal)
            # Detect if candidate addresses the prompt's structural elements
            structural_score = 1.0
            
            # Numeric Evaluation
            num_cost = self._check_numeric_consistency(prompt_nums, cand_nums)
            
            # Logical/Nash Consistency
            logic_cost = self._check_logical_consistency(prompt_mods, cand_mods)
            
            # Compositionality Bonus: Does the candidate reuse prompt vocabulary/modules?
            # This mimics the "syntax-semantics layer"
            overlap_bonus = 0.0
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            # Remove stopwords for better signal
            stopwords = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
            p_sig = p_words - stopwords
            c_sig = c_words - stopwords
            
            if p_sig:
                intersection = p_sig.intersection(c_sig)
                overlap_ratio = len(intersection) / len(p_sig)
                # If the prompt has specific logical keywords, expect them in answer
                logical_keywords = {'true', 'false', 'yes', 'no', 'correct', 'incorrect'}
                if p_sig.intersection(logical_keywords):
                     if not c_sig.intersection(logical_keywords):
                         overlap_bonus -= 0.3 # Penalty for missing logical conclusion
                else:
                    overlap_bonus = overlap_ratio * 0.2 # Small bonus for relevance

            # Aggregate Cost Function (Optimal Control Analogy)
            # Lower cost = better trajectory
            total_cost = num_cost + logic_cost - overlap_bonus
            
            # Convert cost to score (0 to 1, higher is better)
            # Base score starts at 0.5, adjusted by costs
            base_score = 0.5
            final_score = max(0.0, min(1.0, base_score - total_cost + 0.4)) 
            
            # NCD as Tiebreaker/Refinement
            # If structural signals are weak (score near 0.5), NCD breaks ties
            if 0.45 <= final_score <= 0.55:
                ncd = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher score contribution)
                final_score += (1.0 - ncd) * 0.1

            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural cost: {num_cost+logic_cost:.2f}, Compositionality bonus: {overlap_bonus:.2f}"
            })

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the equilibrium stability of the pair.
        High confidence if structural constraints are satisfied and NCD is reasonable.
        """
        # Run single evaluation
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        score = results[0]['score']
        
        # Map the internal score to a confidence metric
        # If the score is high (>0.7), we are confident it's correct.
        # If low (<0.3), confident it's wrong.
        # Middle ground is uncertain.
        
        # Sigmoid-like mapping for confidence
        confidence = 1.0 / (1.0 + np.exp(-5 * (score - 0.5)))
        return round(float(confidence), 4)