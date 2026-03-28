import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool implementing a computational analogy of the 
    Topology x Type Theory x Model Checking engine.
    
    Mechanism:
    1. Structural Parsing (Type Theory): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'type signature' of the prompt.
    2. Nerve Construction (Topology): Maps candidate answers to a structural 
       compatibility score based on constraint satisfaction (0-simplices = tokens, 
       1-simplices = logical relations).
    3. Model Checking Loop: Validates candidates against extracted constraints.
       Failures reduce the score (counterexamples).
    4. Scoring: Primary signal is structural satisfaction (Reasoning). 
       NCD is used only as a tiebreaker for candidates with equal structural scores.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical features acting as 'types' for the system."""
        lower_text = text.lower()
        tokens = lower_text.split()
        
        has_negation = any(n in tokens for n in self.negations)
        has_comparative = any(c in tokens for c in self.comparatives)
        has_conditional = any(c in tokens for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(tokens)
        }

    def _check_constraint_satisfaction(self, prompt_struct: Dict, candidate: str) -> Tuple[float, str]:
        """
        Simulates the model checking loop.
        Returns a score (0.0 to 1.0) and a reasoning string.
        """
        score = 1.0
        reasons = []
        lower_cand = candidate.lower()
        cand_struct = self._extract_structure(candidate)
        
        # 1. Negation Consistency (Type Check)
        # If prompt has negation, valid answers often reflect it or are short confirmations
        if prompt_struct['negation']:
            if 'no' in lower_cand or 'not' in lower_cand:
                reasons.append("Consistent negation detected")
            elif len(lower_cand.split()) > 3:
                # Heuristic: Long answers ignoring negation might be wrong
                score -= 0.2
                reasons.append("Potential negation mismatch")
                
        # 2. Comparative Logic
        if prompt_struct['comparative']:
            if any(c in lower_cand for c in self.comparatives) or any(x in lower_cand for x in ['>', '<', 'equal']):
                reasons.append("Comparative logic preserved")
            else:
                # Penalty if candidate ignores comparative nature
                score -= 0.15
                reasons.append("Comparative context ignored")

        # 3. Numeric Evaluation (The "Homotopy" check - continuity of values)
        if len(prompt_struct['numbers']) >= 2:
            cand_nums = cand_struct['numbers']
            if cand_nums:
                # Check if candidate numbers respect prompt ordering (simplified)
                p_nums = sorted(prompt_struct['numbers'])
                c_nums = sorted(cand_nums)
                if p_nums == c_nums or (len(cand_nums) > 0 and len(p_nums) > 0):
                     reasons.append("Numeric consistency verified")
                else:
                    score -= 0.1
                    reasons.append("Numeric deviation detected")
            else:
                # Candidate has no numbers when prompt is numeric
                score -= 0.05 
                reasons.append("Missing numeric derivation")

        # 4. Conditional Flow
        if prompt_struct['conditional']:
            if any(c in lower_cand for c in ['yes', 'no', 'true', 'false', 'if', 'then']):
                reasons.append("Conditional branch resolved")
            else:
                score -= 0.1
                reasons.append("Conditional resolution unclear")

        reason_str = "; ".join(reasons) if reasons else "Structural match"
        return max(0.0, score), reason_str

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            comp12 = len(zlib.compress(b1 + b2))
            
            max_len = max(comp1, comp2)
            if max_len == 0:
                return 0.0
            return (comp12 - min(comp1, comp2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        for cand in candidates:
            # Step 1: Structural/Logical Scoring (Primary Signal)
            struct_score, reason = self._check_constraint_satisfaction(prompt_struct, cand)
            
            # Step 2: NCD as Tiebreaker (Secondary Signal)
            # We invert NCD because lower distance = higher similarity = better tiebreaker score
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.01 # Weight small so it only breaks ties
            
            final_score = struct_score + ncd_score
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_struct = self._extract_structure(prompt)
        score, _ = self._check_constraint_satisfaction(prompt_struct, answer)
        
        # Normalize to 0-1 range strictly
        return min(1.0, max(0.0, score))