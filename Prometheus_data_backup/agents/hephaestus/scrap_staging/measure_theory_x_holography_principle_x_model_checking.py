import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Measure-Theoretic Holographic Model Checker (MHMC) Approximation.
    
    Mechanism:
    1. Measure Theory (S, Σ, μ): The state space is the text. We define a measure
       based on structural tokens (negations, comparatives, numbers). This creates
       a weighted vector representation where 'important' logical operators have
       higher measure than common words.
    2. Holography Principle: Instead of processing the full high-dimensional text,
       we project the text onto a lower-dimensional 'boundary' manifold consisting
       of logical signatures (e.g., presence of 'not', relative magnitude of numbers).
       This compression preserves the integral (logical truth value) while discarding
       noise.
    3. Model Checking: We verify candidates by checking if their holographic projection
       satisfies the constraints implied by the prompt's structural parse.
       
    Scoring:
    - Primary: Structural alignment (negation matching, numeric consistency).
    - Secondary: NCD (Compression) used only as a tie-breaker for semantic similarity.
    """

    def __init__(self):
        # Logical markers for structural parsing (The "Sigma" algebra)
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for quantitative reasoning."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text.lower())]

    def _structural_parse(self, text: str) -> Dict:
        """
        Project text onto the logical boundary manifold.
        Returns a dictionary representing the compressed logical signature.
        """
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Measure of logical operators
        neg_count = len(words.intersection(self.negations))
        comp_count = len(words.intersection(self.comparatives))
        cond_count = len(words.intersection(self.conditionals))
        
        # Numeric measure
        numbers = self._extract_numbers(text)
        num_sum = sum(numbers) if numbers else 0.0
        num_count = len(numbers)
        
        # Boolean tendency
        has_true = 'true' in words or 'yes' in words
        has_false = 'false' in words or 'no' in words
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'nums': numbers,
            'num_sum': num_sum,
            'bool_tendency': 1 if has_true else (-1 if has_false else 0),
            'length': len(text)
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """
        Verify if candidate numbers logically follow prompt numbers.
        Simple heuristic: If prompt implies ordering, candidate should respect it.
        """
        if not prompt_nums:
            return 1.0 # No numeric constraints
        
        if not cand_nums:
            return 0.5 # Missing data is uncertain
            
        # Check for direct equality or simple transformation presence
        # In a full system, this would be symbolic integration. 
        # Here we check for subset presence or magnitude consistency.
        
        p_set = set(round(x, 2) for x in prompt_nums)
        c_set = set(round(x, 2) for x in cand_nums)
        
        # Reward if candidate contains numbers derived from prompt
        overlap = len(p_set.intersection(c_set))
        if overlap > 0:
            return 0.8 + (0.2 * overlap / max(len(p_set), 1))
            
        # Penalty if magnitudes are wildly different without explanation
        return 0.4

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated here using lengths for speed, strictly C(x) is compress(x)
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def _structural_score(self, prompt_sig: Dict, cand_sig: Dict, prompt_text: str) -> float:
        """
        Compute score based on structural alignment (Measure Theoretic overlap).
        """
        score = 0.5 # Base probability
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has high negation, candidate should reflect that logic
        if prompt_sig['neg'] > 0:
            if cand_sig['neg'] > 0:
                score += 0.2 # Aligned negation
            else:
                score -= 0.3 # Missed negation (common failure mode)
        else:
            if cand_sig['neg'] > 0:
                score -= 0.1 # Unnecessary negation
        
        # 2. Numeric Consistency
        if prompt_sig['nums']:
            num_score = self._check_numeric_consistency(prompt_sig['nums'], cand_sig['nums'])
            score = (score * 0.6) + (num_score * 0.4) # Weight numeric heavily if present
            
        # 3. Conditional/Logical Depth
        if prompt_sig['cond'] > 0:
            if cand_sig['cond'] > 0 or cand_sig['bool_tendency'] != 0:
                score += 0.1
                
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_sig = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._ncd_distance(prompt, cand))
            
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0.5

        for i, cand in enumerate(candidates):
            cand_sig = self._structural_parse(cand)
            
            # Primary Score: Structural/Logical alignment
            raw_score = self._structural_score(prompt_sig, cand_sig, prompt)
            
            # Tie-breaking / Refinement with NCD (Holographic compression check)
            # If structural score is ambiguous, NCD helps distinguish semantic closeness
            ncd_val = ncd_scores[i]
            # Invert NCD (lower is better) and normalize slightly to not overpower structural
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            final_score = raw_score + ncd_bonus
            
            # Heuristic boost for exact boolean matches in simple prompts
            if "true" in cand.lower() and prompt_sig['bool_tendency'] == 1:
                final_score = min(1.0, final_score + 0.1)
            if "false" in cand.lower() and prompt_sig['bool_tendency'] == -1:
                final_score = min(1.0, final_score + 0.1)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural alignment (neg:{cand_sig['neg']}, num:{len(cand_sig['nums'])}) with NCD refinement."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the structural evaluation of the single candidate against the prompt.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']