import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Neuromodulated Adversarial Hypothesis-Testing Loop.
    
    Mechanism:
    1. Falsificationism (Core): The 'Critic' attempts to falsify each candidate by 
       detecting logical contradictions, negation mismatches, and constraint violations 
       between the prompt and the candidate. The 'Prediction Error' is the degree of 
       mismatch.
    2. Nash Equilibrium: We simulate an equilibrium where the score represents a state 
       where no unilateral change in the candidate's alignment with prompt constraints 
       would improve its survival (score). High alignment = Low falsification error.
    3. Neuromodulation: 
       - Dopamine (Phasic): Encodes the magnitude of the falsification error. Large 
         contradictions yield high negative rewards (low score). 
       - Serotonin (Tonic): Modulates the exploration/exploitation gain. If structural 
         signals are weak (ambiguous), the system increases entropy tolerance (smoothing 
         scores), whereas strong structural signals tighten the scoring distribution.
    
    The evaluate() method acts as the conjecture-refutation cycle, ranking candidates 
    by their ability to survive the critic's falsification attempts.
    """

    def __init__(self):
        # Structural keywords for falsification testing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'only if', 'provided'}
        self.bool_yes = {'yes', 'true', 'correct', 'affirmative'}
        self.bool_no = {'no', 'false', 'incorrect', 'negative'}

    def _extract_structure(self, text: str) -> Dict:
        """Parses text for logical structures: negations, numbers, booleans."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Detect negation density
        neg_count = len(words.intersection(self.negations))
        
        # Detect numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        # Detect boolean assertions
        has_yes = bool(words.intersection(self.bool_yes))
        has_no = bool(words.intersection(self.bool_no))
        
        # Detect conditionals
        has_conditional = any(k in lower_text for k in self.conditionals)

        return {
            'negations': neg_count,
            'numbers': nums,
            'has_yes': has_yes,
            'has_no': has_no,
            'has_conditional': has_conditional,
            'length': len(text),
            'words': words
        }

    def _compute_falsification_error(self, prompt_struct: Dict, cand_struct: Dict, 
                                     prompt_raw: str, cand_raw: str) -> float:
        """
        Computes the 'Prediction Error' (delta) based on logical consistency.
        High error = Candidate is falsified by Prompt constraints.
        Returns a normalized error score (0.0 = perfect match, 1.0 = total contradiction).
        """
        error = 0.0
        constraints_checked = 0

        # 1. Boolean Contradiction Check (Modus Tollens approximation)
        # If prompt implies negative and candidate is positive (or vice versa)
        if prompt_struct['has_yes'] and cand_struct['has_no']:
            error += 1.0
            constraints_checked += 1
        elif prompt_struct['has_no'] and cand_struct['has_yes']:
            error += 1.0
            constraints_checked += 1
            
        # 2. Negation Density Mismatch (Heuristic for logical tone)
        # If prompt is highly negative but candidate is not, or vice versa
        p_neg = prompt_struct['negations'] > 0
        c_neg = cand_struct['negations'] > 0
        if p_neg != c_neg:
            # Soft penalty unless numbers suggest a specific numeric contradiction
            error += 0.4
            constraints_checked += 1

        # 3. Numeric Consistency (If both have numbers)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            # Simple check: do the numbers match or follow simple logic?
            # If prompt has "2" and candidate has "3" without operator context, penalize
            if len(p_nums) == len(c_nums):
                for pn, cn in zip(p_nums, c_nums):
                    if abs(pn - cn) > 1e-6: # Allow float tolerance
                        error += 0.5
                        constraints_checked += 1
            elif set(p_nums) != set(c_nums):
                 # Different sets of numbers often imply contradiction in strict QA
                error += 0.3
                constraints_checked += 1

        # 4. Structural Overlap (Jaccard) as a baseline for context retention
        # Low overlap suggests the candidate ignores the prompt's domain
        all_words = prompt_struct['words'].union(cand_struct['words'])
        if all_words:
            intersection = prompt_struct['words'].intersection(cand_struct['words'])
            overlap = len(intersection) / len(all_words)
            # If overlap is extremely low (<0.1) and prompt is long, it's likely a hallucination
            if prompt_struct['length'] > 20 and overlap < 0.1:
                error += 0.5
                constraints_checked += 1

        # Normalize error by constraints checked to avoid penalizing short answers unfairly
        # if no specific constraints were triggered, use NCD as a fallback signal
        if constraints_checked > 0:
            return min(1.0, error / constraints_checked)
        
        # Fallback to NCD if no structural logic found (Tiebreaker role)
        return self._ncd_distance(prompt_raw, cand_raw)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 0.5

    def _serotonergic_gain(self, prompt_struct: Dict, errors: List[float]) -> float:
        """
        Modulates the scoring gain based on ambiguity.
        High ambiguity (low structural signal) -> High entropy (flatter scores).
        Low ambiguity (high structural signal) -> Low entropy (sharp scores).
        """
        structural_strength = 0
        if prompt_struct['numbers']: structural_strength += 0.4
        if prompt_struct['has_conditional']: structural_strength += 0.3
        if prompt_struct['negations'] > 0: structural_strength += 0.3
        
        # If structural strength is low, increase temperature (flatten scores)
        # If high, decrease temperature (sharpen scores)
        base_gain = 1.0
        modulation = 1.0 / (structural_strength + 0.1) 
        return base_gain * modulation

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_struct = self._extract_structure(prompt)
        raw_scores = []
        
        # Phase 1: Compute Falsification Errors (Dopaminergic signal)
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            error = self._compute_falsification_error(prompt_struct, cand_struct, prompt, cand)
            raw_scores.append(error)
        
        # Phase 2: Neuromodulated Gain Control (Serotonergic signal)
        # Convert errors to survival probabilities (1 - error)
        survival = [max(0.0, 1.0 - e) for e in raw_scores]
        
        # Apply gain modulation
        gain = self._serotonergic_gain(prompt_struct, raw_scores)
        
        # Softmax with gain to find Nash-like equilibrium distribution
        # Higher gain = more exploitation of the best candidate
        # Lower gain = more exploration (flatter distribution)
        import math
        exp_scores = [math.exp(gain * s) for s in survival]
        sum_exp = sum(exp_scores) if sum([math.exp(gain * s) for s in survival]) > 0 else 1.0
        
        ranked = []
        for i, cand in enumerate(candidates):
            score = exp_scores[i] / sum_exp if sum_exp > 0 else 0.0
            # Refine score with NCD as a tiebreaker if structural score is ambiguous
            if gain < 2.0: # If low structural confidence, weigh NCD slightly more
                ncd = self._ncd_distance(prompt, cand)
                # Blend: Structural score is primary, NCD breaks ties in low-structure regimes
                score = 0.7 * score + 0.3 * (1.0 - ncd)
            
            ranked.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Falsification error: {raw_scores[i]:.2f}, Gain: {gain:.2f}"
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on falsification survival."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']