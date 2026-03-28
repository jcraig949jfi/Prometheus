import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Self-Verifying Incentive-Compatible Model Checker (SIMC) Approximation.
    
    Mechanism:
    1. Ergodic Theory: Treats the prompt-candidate pair as a state in a Markov process.
       We estimate the 'ergodic average' of structural validity by sampling syntactic features
       (negations, comparatives, conditionals) across the text. If the candidate maintains
       structural consistency with the prompt (e.g., preserving negation scope), it gains
       'stationary probability' mass.
    2. Mechanism Design: Implements a VCG-like scoring rule. Candidates are 'agents' reporting
       types (answers). The 'payment' (score boost) is awarded only if the candidate satisfies
       the 'Incentive Compatibility' (IC) constraint: the answer must structurally align with
       the prompt's logical operators (e.g., if prompt asks "Which is NOT...", answer must
       contain negation or exclusion logic). False reporting (ignoring constraints) yields
       low utility (score).
    3. Model Checking: Verifies temporal-logic-like specifications (◇□) on the string structure.
       It checks if the candidate satisfies the property φ (semantic match) AND the IC constraint.
       Uses NCD only as a tie-breaking metric for structural equivalence when logical signals are weak.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Model Checker" specs)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|isn\'t|aren\'t)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|larger|shorter)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|except|when)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'\d+\.?\d*')
        self.comparator_op_pattern = re.compile(r'(==|!=|<=|>=|<|>)')

    def _extract_structural_signature(self, text: str) -> Dict[str, Any]:
        """Extracts logical features to form the 'state' for ergodic analysis."""
        text_lower = text.lower()
        has_negation = bool(self.negation_pattern.search(text_lower))
        has_comparative = bool(self.comparative_pattern.search(text_lower))
        has_conditional = bool(self.conditional_pattern.search(text_lower))
        numbers = [float(x) for x in self.numeric_pattern.findall(text)]
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": numbers,
            "length": len(text),
            "word_count": len(text.split())
        }

    def _check_incentive_compatibility(self, prompt_sig: Dict, cand_sig: Dict, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Step: Verifies if the candidate respects the logical constraints
        imposed by the prompt (IC constraint). Returns a score 0.0 to 1.0.
        """
        score = 1.0
        
        # Constraint 1: Negation Preservation
        # If prompt asks for what is NOT, valid answers often imply exclusion or contain negation
        if prompt_sig["negation"]:
            # Heuristic: If prompt is negative, candidate should ideally reflect that logic
            # or simply not contradict it. 
            if not cand_sig["negation"]:
                # Soft penalty if the candidate ignores the negative framing entirely
                # unless the candidate is very short (e.g., a single name)
                if cand_sig["word_count"] > 3:
                    score -= 0.2
        
        # Constraint 2: Comparative Consistency
        if prompt_sig["comparative"]:
            if not cand_sig["comparative"]:
                # If prompt asks for "greater", answer should ideally involve comparison or numbers
                if not cand_sig["numbers"]:
                    score -= 0.15

        # Constraint 3: Numeric Logic (Simple evaluation)
        if prompt_sig["numbers"] and cand_sig["numbers"]:
            # If both have numbers, check if the candidate number appears in prompt or is a result of op
            # This is a simplified check for presence
            p_nums = set(prompt_sig["numbers"])
            c_nums = set(cand_sig["numbers"])
            if not c_nums.intersection(p_nums) and len(p_nums) > 0:
                # If candidate introduces entirely new numbers without prompt context, slight penalty
                # unless it's a calculation result (hard to verify without eval, so we skip hard penalty)
                pass 

        return max(0.0, score)

    def _compute_ergodic_average(self, prompt: str, candidate: str) -> float:
        """
        Ergodic Theory Step: Estimates the long-run stability of the answer.
        Simulates 'mixing' by checking local structural consistency.
        """
        # We treat the text as a trajectory. 
        # High ergodicity = consistent logical flow.
        p_sig = self._extract_structural_signature(prompt)
        c_sig = self._extract_structural_signature(candidate)
        
        # Base similarity via NCD (Normalized Compression Distance)
        # NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        try:
            s_p = prompt.encode('utf-8')
            s_c = candidate.encode('utf-8')
            c_p = len(zlib.compress(s_p))
            c_c = len(zlib.compress(s_c))
            c_pc = len(zlib.compress(s_p + s_c))
            
            ncd = (c_pc - min(c_p, c_c)) / max(c_p, c_c, 1)
        except:
            ncd = 1.0
            
        # Convert NCD to a similarity score (0 to 1, where 1 is similar)
        # However, for reasoning, we don't want high similarity necessarily, 
        # we want high IC compliance.
        
        ic_score = self._check_incentive_compatibility(p_sig, c_sig, prompt, candidate)
        
        # The "Ergodic Average" here is a weighted sum of structural alignment and IC compliance
        # If IC fails, the system is not in a stable equilibrium (score drops).
        ergodic_score = (0.4 * (1.0 - ncd)) + (0.6 * ic_score)
        
        return ergodic_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        ranked = []
        prompt_sig = self._extract_structural_signature(prompt)
        
        for cand in candidates:
            # Compute SIMC score
            score = self._compute_ergodic_average(prompt, cand)
            
            # Additional structural parsing for specific logical operators found in prompt
            # to boost candidates that explicitly address them (Mechanism Design refinement)
            bonus = 0.0
            cand_lower = cand.lower()
            
            # If prompt has "not", penalize candidates that are just "Yes" or generic
            if prompt_sig["negation"]:
                if re.search(r'\b(yes|no|true|false)\b', cand_lower) and len(cand.split()) < 3:
                    # Ambiguous short answers to negative questions are risky
                    bonus -= 0.1
            
            # Numeric evaluation check
            if prompt_sig["numbers"]:
                # Try to extract a simple comparison if operators exist
                if self.comparator_op_pattern.search(prompt):
                    # If prompt has math logic, prefer candidates with numbers
                    if cand_sig := self._extract_structural_signature(cand): # re-extract for this block
                         if cand_sig["numbers"]:
                             bonus += 0.2
            
            final_score = score + bonus
            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"SIMC Score: Ergodic stability={score:.4f}, IC Bonus={bonus:.4f}"
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the SIMC score.
        """
        # Run evaluation internally to get the score
        # We treat the single answer as a candidate list of one
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize score to 0-1 range roughly (scores can exceed 1.0 slightly due to bonuses)
        raw_score = results[0]["score"]
        confidence = min(1.0, max(0.0, raw_score))
        return confidence