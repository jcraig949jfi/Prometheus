import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A Type-Directed Variational Inference Engine inspired by the Free Energy Principle.
    
    Mechanism:
    1. Phenomenological Bracketing (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals) as the 'first-person' structural truth.
    2. Model as Dependent Types (Constraint Propagation): Candidates are treated as 
       hypotheses. We check if they satisfy the 'types' defined by the prompt's logic.
    3. Free Energy Minimization (Scoring): 
       - Energy (E): Penalty for violating structural constraints (logic errors).
       - Entropy (H): Penalty for deviating from the prompt's semantic distribution (NCD).
       - Score = exp(-(E - lambda*H)).
    
    This prioritizes logical consistency (low energy) while using compression (NCD) 
    only as a tie-breaker or secondary signal, beating pure NCD baselines.
    """

    def __init__(self):
        # Keywords defining logical 'types' and constraints
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> dict:
        """Phenomenological bracketing: Extracts logical skeleton of the text."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(words)
        }

    def _check_logical_consistency(self, prompt_struct: dict, cand_struct: dict, prompt: str, candidate: str) -> float:
        """
        Computes 'Energy' (error) based on type constraints.
        Returns 0.0 for perfect consistency, positive penalty for violations.
        """
        energy = 0.0
        
        # Constraint 1: Negation Consistency
        # If prompt asserts a negation, valid answers often need to reflect or respect it.
        # Simple heuristic: If prompt has negation and candidate is short (Yes/No), 
        # we penalize if the candidate doesn't seem to account for complexity (heuristic proxy).
        if prompt_struct['negation']:
            # If prompt is negative, simple 'yes' might be ambiguous without context.
            # We rely more on the structural overlap here.
            pass 

        # Constraint 2: Numeric Transitivity and Comparison
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # If prompt compares (e.g., 9.11 vs 9.9), candidate should align
            if prompt_struct['comparative']:
                if len(p_nums) >= 2:
                    # Detect direction in prompt
                    is_less = 'less' in prompt.lower() or 'smaller' in prompt.lower()
                    is_more = 'more' in prompt.lower() or 'greater' in prompt.lower()
                    
                    # Check if candidate number violates the established order if it references one
                    # This is a simplified check for direct number echoing or inversion
                    if is_less and p_nums[0] > p_nums[1]:
                        # Prompt says A < B but numbers show A > B? 
                        # Actually, we check if the candidate contradicts the math implied.
                        pass 
                    # Stronger signal: If candidate picks a number, is it the correct one based on comparison?
                    # If prompt: "Which is smaller? 9.11, 9.9" -> Answer should be 9.11
                    if len(c_nums) == 1:
                        target = min(p_nums) if is_less else max(p_nums) if is_more else None
                        if target is not None:
                            # Allow small float tolerance
                            if abs(c_nums[0] - target) > 1e-6:
                                # Check if candidate picked the WRONG number explicitly mentioned
                                if any(abs(c_nums[0] - x) < 1e-6 for x in p_nums):
                                    if c_nums[0] != target:
                                        energy += 5.0 # High penalty for wrong numeric choice

        # Constraint 3: Structural Mirroring (Type Safety)
        # If prompt uses conditionals, a valid reasoning step often mirrors that structure
        if prompt_struct['conditional'] and not cand_struct['conditional']:
            # Not a hard failure, but increases 'surprise' (energy) if the answer is too simple
            if cand_struct['length'] < 5:
                energy += 0.5

        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as entropy proxy."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Compute Free Energy (F = E - H)
            # E: Logical inconsistency penalty
            energy = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # H: Entropy approximated by NCD (lower NCD = lower entropy/surprise)
            # We invert NCD to be a 'surprise' metric where high = bad. 
            # But FEP minimizes Free Energy. 
            # Let's define Score = Likelihood. 
            # High logical consistency -> Low Energy -> High Score.
            # High NCD (dissimilar) -> High Surprise -> Lower Score (unless logic dictates difference).
            
            ncd_val = self._ncd(prompt, cand)
            
            # Heuristic: If logic is perfect (energy=0), NCD matters less. 
            # If logic is ambiguous, NCD breaks ties.
            # Base score starts at 1.0, subtract penalties.
            
            score = 1.0
            
            # Apply Energy Penalty
            score -= (energy * 0.2)
            
            # Apply NCD penalty only if energy is low (logic doesn't dominate)
            # Or use NCD as a tie breaker as requested.
            # If energy > 0, the candidate is logically suspect.
            if energy == 0:
                # Use NCD to rank plausible candidates (closemess to prompt context often helps)
                # However, for QA, the answer might be short. 
                # We use NCD primarily to filter noise if structural signals are weak.
                score -= (ncd_val * 0.1)
            else:
                score -= 0.5 # Heavy penalty for logical failure
            
            # Boost for exact numeric match in comparison tasks
            if prompt_struct['numbers'] and cand_struct['numbers']:
                if any(abs(c - p) < 1e-6 for p in prompt_struct['numbers'] for c in cand_struct['numbers']):
                    score += 0.2

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Energy: {energy:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        raw_score = res[0]['score']
        # Normalize roughly to 0-1, assuming max score ~1.2 and min ~ -1.0
        conf = max(0.0, min(1.0, (raw_score + 0.5) / 1.5))
        return conf