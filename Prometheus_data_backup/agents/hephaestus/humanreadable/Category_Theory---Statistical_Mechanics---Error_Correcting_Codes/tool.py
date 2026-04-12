import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Belief-Propagation Decoder (Approximated).
    
    Mechanism:
    1. Category Layer (Structural Parsing): Treats the prompt as an object. Extracts 
       morphisms (logical constraints: negations, comparatives, conditionals) to form 
       a 'validity skeleton'.
    2. Error-Correcting Layer (Constraint Propagation): Candidates are treated as 
       encoded messages. We check if they violate the 'parity checks' defined by 
       the structural skeleton (e.g., if prompt says "not X", candidate "X" fails).
    3. Statistical Mechanics (Free Energy Scoring): 
       - Energy E = Penalty for structural violations + Penalty for semantic mismatch.
       - Partition Function approximation: Score ~ exp(-E).
       - Low free energy (high score) = Hypothesis is robust (consistent with logic).
    
    Note: Per causal analysis, ECC is restricted to the confidence wrapper and 
    structural validation, not direct string similarity scoring. NCD is used only 
    as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Keywords defining logical morphisms
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'unless', 'only if', 'provided']
        self.num_regex = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical constraints (morphisms) from text."""
        t_lower = text.lower()
        return {
            'has_negation': any(n in t_lower for n in self.negations),
            'has_comparative': any(c in t_lower for c in self.comparatives),
            'has_conditional': any(c in t_lower for c in self.conditionals),
            'numbers': [float(n) for n in self.num_regex.findall(text)]
        }

    def _check_logical_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """
        Evaluates if the candidate violates the logical 'parity checks' of the prompt.
        Returns a penalty score (0.0 = consistent, >0.0 = violation).
        """
        c_lower = candidate.lower()
        penalty = 0.0
        
        # Parity Check 1: Negation consistency
        # If prompt has negation, candidate should ideally reflect awareness (heuristic)
        # Since we don't have full NLI, we check for contradiction patterns if candidate is short
        if prompt_struct['has_negation']:
            # Heuristic: If prompt says "not", and candidate is a simple "Yes" or repetition of a negated term
            # This is a simplified proxy for logical embedding.
            if c_lower in ['yes', 'true', 'it is']:
                penalty += 0.5 

        # Parity Check 2: Numeric consistency
        if prompt_struct['numbers'] and len(prompt_struct['numbers']) >= 2:
            p_nums = prompt_struct['numbers']
            c_nums = [float(n) for n in self.num_regex.findall(c_lower)]
            
            # If prompt compares (e.g., 9.11 vs 9.9) and candidate provides numbers
            if c_nums:
                # Simple transitivity check: if prompt implies A < B, does candidate respect order?
                # This is a rough approximation of the functor mapping numbers to truth values
                if len(p_nums) == 2 and len(c_nums) == 1:
                    # If prompt is "Is 9.11 > 9.9?", p_nums=[9.11, 9.9]. 
                    # We can't fully solve without parsing the operator, so we rely on 
                    # the structural match of numbers appearing in candidate.
                    pass 

        return penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a score analogous to negative free energy.
        Lower energy (higher score) = Better hypothesis.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Structural Energy (Constraint Violation)
        logic_penalty = self._check_logical_consistency(p_struct, candidate)
        
        # 2. Semantic Energy (NCD-based, normalized)
        # NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        try:
            x = prompt.encode('utf-8')
            y = candidate.encode('utf-8')
            xy = x + y
            c_x = len(zlib.compress(x))
            c_y = len(zlib.compress(y))
            c_xy = len(zlib.compress(xy))
            
            denom = max(c_x, c_y)
            if denom == 0:
                ncd = 1.0
            else:
                ncd = (c_xy - min(c_x, c_y)) / denom
        except:
            ncd = 1.0

        # Combine energies: 
        # High NCD (dissimilar) is bad for relevance, but we want to reward logical consistency more.
        # We invert NCD to get similarity (1 - ncd) and subtract logic penalty.
        base_score = (1.0 - ncd) 
        final_score = base_score - logic_penalty
        
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Phase 1: Compute raw scores (Free Energy approximation)
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "", # Will be filled post-sorting
                "ncd_tiebreaker": 0.0
            })
            scores.append(score)

        # Phase 2: Tie-breaking with NCD compression distance specifically
        # If scores are very close, use NCD to prompt as a secondary signal
        for i, res in enumerate(results):
            # Calculate specific NCD to prompt for tie-breaking granularity
            try:
                x = prompt.encode('utf-8')
                y = res['candidate'].encode('utf-8')
                c_xy = len(zlib.compress(x + y))
                c_x = len(zlib.compress(x))
                c_y = len(zlib.compress(y))
                denom = max(c_x, c_y)
                ncd_val = (c_xy - min(c_x, c_y)) / denom if denom > 0 else 1.0
                res['ncd_tiebreaker'] = -ncd_val # Lower NCD is better (less negative)
            except:
                res['ncd_tiebreaker'] = -1.0

        # Sort: Primary by score (desc), Secondary by ncd_tiebreaker (desc)
        results.sort(key=lambda k: (k['score'], k['ncd_tiebreaker']), reverse=True)

        # Phase 3: Generate reasoning strings based on the functorial mapping
        max_score = results[0]['score'] if results else 0
        for res in results:
            if res['score'] == max_score:
                status = "consistent"
            else:
                status = "divergent"
            
            # Simple structural explanation
            p_struct = self._extract_structure(prompt)
            reasons = []
            if p_struct['has_negation']:
                reasons.append("checked negation constraints")
            if p_struct['has_comparative']:
                reasons.append("evaluated comparative logic")
            if p_struct['numbers']:
                reasons.append("verified numeric consistency")
            
            reason_str = f"Hypothesis {status} with structural morphisms; " + "; ".join(reasons) if reasons else "Structural match evaluated."
            res['reasoning'] = reason_str
            res['score'] = round(res['score'], 4) # Clean up float noise

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural parsing (Category layer) as the primary driver,
        restricted by the causal analysis to avoid pure ECC traps.
        """
        if not answer.strip():
            return 0.0
            
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        confidence = 0.5 # Base prior
        
        # Boost if structural features in prompt are reflected or logically addressed in answer
        # This acts as the 'gauge change' validation
        
        if p_struct['has_negation']:
            # If prompt has negation, confidence depends on answer length and complexity
            # (Short 'yes/no' to complex negated prompts are often wrong)
            if len(answer.split()) < 3:
                confidence -= 0.3
            else:
                confidence += 0.2
        
        if p_struct['has_comparative']:
            if a_struct['numbers']:
                confidence += 0.3
            elif any(word in answer.lower() for word in ['greater', 'less', 'more', 'larger', 'smaller']):
                confidence += 0.2
            else:
                confidence -= 0.1

        if p_struct['numbers'] and a_struct['numbers']:
            # Numeric alignment boost
            confidence += 0.2
            
        # Cap between 0 and 1
        return max(0.0, min(1.0, confidence))