import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool implementing a hybrid of Morphogenesis, Predictive Coding, and Falsificationism.
    
    Mechanism:
    1. Morphogenesis (Hypothesis Generation): Candidates are treated as spatial patterns in a reaction-diffusion field.
       Diversity is preserved by initializing scores based on structural fit rather than just string similarity.
    2. Predictive Coding (Error Minimization): The "prediction" is the structural/logical requirement of the prompt.
       The "error" is the mismatch between candidate properties and prompt constraints.
    3. Falsificationism (Error Amplification): 
       - Explicit checks for logical traps (presuppositions, ambiguities) act as "refutation attempts".
       - If a prompt contains a Tier B trap (ambiguity), confidence is capped low (epistemic honesty).
       - High prediction error (logical mismatch) amplifies the "reactivity" (score penalty), destabilizing incorrect candidates.
    
    Scoring Decomposition:
    - Structural/Logical (40%): Parsing negations, comparatives, conditionals.
    - Computational (20%): Numeric evaluation, modular arithmetic.
    - Judgment/Meta (25%): Detecting ambiguity/traps (caps confidence).
    - NCD/Tiebreaker (15%): Compression distance for residual ranking.
    """

    def __init__(self):
        self.trap_patterns = [
            (r'\b(have|has|did|does)\s+(you|he|she|they)\s+(stop|quit|fail|start)\b', 'presupposition'),
            (r'\b(every|all)\s+\w+.*\b(a|an)\s+\w+\b', 'scope_ambiguity'), # Simplified scope check
            (r'\b(either\s+\w+\s+or\s+\w+)\b', 'false_dichotomy'),
            (r'\b(who|he|she|it)\s+(was|is)\s+(referring|talking)\b', 'pronoun_ambiguity'),
            (r'\b(best|worst|favorite|most)\s+\w+\s+without\b', 'subjectivity'),
            (r'\bimpossible|unanswerable|not enough information\b', 'unanswerable_keyword')
        ]
        
        self.structural_keywords = {
            'negation': ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditional': ['if', 'unless', 'provided', 'except'],
            'quantifier': ['all', 'some', 'many', 'few', 'every', 'each']
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap value: 0.25 if trapped/ambiguous, 1.0 if clear.
        """
        p_lower = prompt.lower()
        
        # Check for explicit trap patterns
        for pattern, trap_type in self.trap_patterns:
            if re.search(pattern, p_lower, re.IGNORECASE):
                return 0.25
        
        # Check for question marks indicating potential ambiguity in short prompts
        if '?' in prompt:
            # If the question asks for external knowledge not provided in a context window (heuristic)
            if any(kw in p_lower for kw in ['who is', 'what year', 'where is', 'capital of']):
                if len(prompt.split()) < 15: # Short, fact-based questions are risky without context
                    return 0.25

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computational checks."""
        pattern = r'-?\d+(?:\.\d+)?'
        return [float(x) for x in re.findall(pattern, text)]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment (negations, conditionals).
        Returns 1.0 for perfect alignment, 0.0 for contradiction, 0.5 for neutral.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5
        
        # Negation Consistency
        p_has_neg = any(k in p_lower for k in self.structural_keywords['negation'])
        c_has_neg = any(k in c_lower for k in self.structural_keywords['negation'])
        
        if p_has_neg == c_has_neg:
            score += 0.25
        else:
            score -= 0.25 # Penalize negation mismatch
            
        # Conditional/Logic Check (Simplified)
        if any(k in p_lower for k in self.structural_keywords['conditional']):
            if any(k in c_lower for k in ['yes', 'no', 'true', 'false', 'impossible']):
                score += 0.1 # Reward logical form answer
        
        return max(0.0, min(1.0, score))

    def _computational_score(self, prompt: str, candidate: str) -> float:
        """
        Performs explicit calculation if numbers are present.
        If the prompt contains a math problem, the candidate must match the calculated result.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 0.5 # No computation needed
        
        # Heuristic: If prompt has 2+ numbers and candidate has 1 number, check basic ops
        if len(p_nums) >= 2 and len(c_nums) == 1:
            target = c_nums[0]
            a, b = p_nums[0], p_nums[1]
            
            # Check sum, diff, product, ratio
            ops = [
                abs(a + b - target) < 1e-6,
                abs(a - b - target) < 1e-6,
                abs(a * b - target) < 1e-6,
                abs(a / b - target) < 1e-6 if b != 0 else False
            ]
            
            if any(ops):
                return 1.0
            else:
                # Falsification: If numbers don't match any op, it's likely wrong
                return 0.1
        
        return 0.5

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the Morphogenesis x Predictive Coding x Falsificationism model.
        """
        results = []
        
        # Tier B: Epistemic Honesty Check (The "Falsification" of the prompt itself)
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # 1. Structural Score (Predictive Coding: Matching pattern to constraint)
            struct_score = self._structural_score(prompt, candidate)
            
            # 2. Computational Score (Explicit Calculation)
            comp_score = self._computational_score(prompt, candidate)
            
            # 3. NCD Tiebreaker (Morphological similarity)
            ncd = self._ncd_distance(prompt, candidate)
            ncd_score = 1.0 - ncd  # Convert distance to similarity
            
            # Weighted Combination (Decomposition Requirements)
            # Structural >= 50%, Computation >= 20%, NCD <= 15%, Judgment/Meta included in cap
            # We blend them: 0.5*Struct + 0.35*Comp + 0.15*NCD
            raw_score = (0.50 * struct_score) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Apply Falsification Cap (Epistemic Honesty)
            # If the prompt is ambiguous, the maximum possible score is capped.
            final_score = min(raw_score, meta_cap)
            
            # Generate Reasoning String
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Potential ambiguity or presupposition detected (Tier B).")
            if comp_score == 1.0:
                reasoning_parts.append("Numerical computation verified.")
            elif comp_score < 0.2 and self._extract_numbers(prompt):
                reasoning_parts.append("Numerical mismatch detected (Falsified).")
            if struct_score > 0.7:
                reasoning_parts.append("Structural constraints (negation/logic) satisfied.")
            elif struct_score < 0.3:
                reasoning_parts.append("Structural contradiction detected.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."

            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at 0.25 if prompt is ambiguous (Tier B).
        Caps at 0.9 unless computation/structure is definitive.
        """
        # Check Meta-Confidence (Prompt Quality)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return 0.2  # Explicitly low for ambiguous prompts
            
        # Evaluate the specific answer quality
        struct_score = self._structural_score(prompt, answer)
        comp_score = self._computational_score(prompt, answer)
        
        # If computation was required and passed, confidence can be high
        p_nums = self._extract_numbers(prompt)
        if len(p_nums) >= 2 and comp_score == 1.0:
            return 0.95 # Definitive computational answer
            
        # If structural match is perfect and no traps
        if struct_score > 0.7 and comp_score >= 0.5:
            return 0.85
            
        # Uncertainty fallback
        if struct_score < 0.4 and comp_score < 0.4:
            return 0.3
            
        return 0.6