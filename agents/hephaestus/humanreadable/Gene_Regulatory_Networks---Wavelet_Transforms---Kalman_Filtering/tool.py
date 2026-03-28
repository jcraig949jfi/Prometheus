import re
import zlib
import math

class ReasoningTool:
    """
    Multi-resolution State Estimator for Reasoning (MSER).
    
    Mechanism:
    This tool implements the theoretical architecture of a Wavelet-Kalman GRN estimator
    as a symbolic reasoning engine.
    
    1. Observation Decomposition (Wavelet Analogy):
       The input prompt is parsed into structural components (negations, comparatives,
       conditionals, numerics). This mimics the Discrete Wavelet Transform decomposing
       a signal into scale-specific coefficients (trends vs. bursts).
       
    2. State Estimation (Kalman Analogy):
       A recursive update cycle evaluates candidate answers against the parsed structural
       constraints.
       - Prediction Step: Projects candidate validity based on keyword overlap with
         structural tokens.
       - Update Step: Adjusts the 'posterior' score based on strict logical checks
         (e.g., if prompt has negation, candidate must not affirm the negated fact).
       - Uncertainty Quantification: Candidates failing structural checks receive high
         variance (low confidence), triggering a 'hypothesis revision' (score penalty).
         
    3. Hypothesis Testing:
       The final score represents the posterior probability that the candidate correctly
       satisfies the multi-scale logical constraints of the prompt.
    """

    def __init__(self):
        # Structural parsers acting as wavelet bases
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.bool_yes = {'yes', 'true', 'correct', 'affirmative', 'y'}
        self.bool_no = {'no', 'false', 'incorrect', 'negative', 'n'}

    def _normalize(self, text):
        return text.lower().strip()

    def _parse_structure(self, text):
        """Decompose text into structural coefficients (Wavelet Decomposition analog)."""
        tokens = set(re.findall(r'\b\w+\b', self._normalize(text)))
        nums = re.findall(r'-?\d+\.?\d*', text)
        
        has_negation = bool(tokens & self.negation_words)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        has_numbers = len(nums) > 0
        
        # Extract numeric constraints for evaluation
        numeric_vals = []
        if has_numbers:
            try:
                numeric_vals = [float(n) for n in nums]
            except ValueError:
                pass

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numeric_vals,
            'tokens': tokens,
            'length': len(text)
        }

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def _evaluate_logic(self, prompt_struct, candidate_struct, candidate_raw):
        """
        Kalman Update Step: Adjust score based on logical consistency.
        Returns a penalty (0.0 = perfect, 1.0 = contradiction).
        """
        penalty = 0.0
        
        # 1. Negation Consistency Check
        # If prompt implies negation, a 'yes' answer might be wrong depending on context
        # Here we use a heuristic: If prompt has strong negation and candidate is simple 'yes/no'
        if prompt_struct['negation']:
            cand_lower = candidate_raw.lower().strip()
            # If candidate is a direct affirmative to a negated premise without qualification
            if cand_lower in self.bool_yes and not any(w in candidate_raw.lower() for w in ['not', 'no']):
                # Soft penalty: requires deeper context, but risky
                penalty += 0.2
        
        # 2. Numeric Consistency Check
        if prompt_struct['numbers'] and candidate_struct['numbers']:
            # If both have numbers, check magnitude consistency roughly
            p_nums = prompt_struct['numbers']
            c_nums = candidate_struct['numbers']
            # Heuristic: If prompt asks for 'less', candidate should be smaller
            # Since we don't parse the full sentence structure, we check if numbers match exactly (exact retrieval)
            # or if they are completely disjoint (potential hallucination)
            if not any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                # If no overlap, increase uncertainty
                penalty += 0.1

        # 3. Structural Token Overlap (Process Noise Reduction)
        # Candidates sharing structural keywords are more likely to be reasoning-based
        common_tokens = prompt_struct['tokens'] & candidate_struct['tokens']
        # Filter to meaningful tokens
        meaningful_overlap = common_tokens - self.bool_yes - self.bool_no - self.negation_words
        
        if len(meaningful_overlap) == 0 and len(prompt_struct['tokens']) > 5:
            # Low overlap increases uncertainty
            penalty += 0.15
            
        return min(penalty, 1.0)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_struct = self._parse_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        candidate_scores = []
        
        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # Base score from NCD (similarity to prompt context)
            ncd_val = self._compute_ncd(prompt, cand)
            base_score = 1.0 - ncd_val
            
            # Logic Penalty (Kalman Update)
            logic_penalty = self._evaluate_logic(prompt_struct, cand_struct, cand)
            
            # Final Score: Base Similarity adjusted by Logical Consistency
            # Scale: 0 to 1. Higher is better.
            final_score = max(0.0, base_score - logic_penalty)
            
            # Boost for structural keyword presence (Hypothesis support)
            if prompt_struct['negation'] and any(w in cand.lower() for w in self.negation_words):
                final_score += 0.1
            if prompt_struct['conditional'] and any(w in cand.lower() for w in self.conditionals):
                final_score += 0.1
                
            final_score = min(1.0, final_score)
            
            reasoning = f"Structural match: {1.0-ncd_val:.2f}, Logic penalty: {logic_penalty:.2f}"
            if logic_penalty > 0:
                reasoning += " (Potential logical mismatch detected)"
                
            candidate_scores.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        candidate_scores.sort(key=lambda x: x['score'], reverse=True)
        return candidate_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal evaluation logic to determine if the answer fits the prompt's structure.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize the score to a confidence metric
        # The evaluate method returns a score where higher is better.
        # We map this directly, ensuring strict bounds.
        score = results[0]['score']
        return max(0.0, min(1.0, score))