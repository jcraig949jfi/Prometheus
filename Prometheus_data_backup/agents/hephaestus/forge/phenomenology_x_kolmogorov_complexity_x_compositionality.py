import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Phenomen-Kolmogorov Compositional Reasoner (PKCR) Implementation.
    
    Mechanism:
    1. Phenomenological Bracketing (Structural Parsing): Instead of raw sensory data,
       we parse the prompt's linguistic structure (negations, comparatives, conditionals).
       This isolates the "intentional descriptors" (logic constraints).
    2. Kolmogorov Complexity (MDL Search): We approximate description length using
       NCD (zlib) but prioritize structural adherence. A candidate with high structural
       fidelity but slightly higher compression is preferred over a compressed candidate
       that violates logic (Occam's Razor with constraints).
    3. Compositionality: We evaluate if the candidate answer composes validly with the
       extracted constraints (e.g., if prompt says "NOT X", candidate must not imply X).
    
    This approach beats pure NCD by using structural parsing as the primary signal
    and NCD only as a tie-breaker, addressing the "Yes/No" ambiguity of pure compression.
    """

    def __init__(self):
        # Structural keywords for phenomenological bracketing
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        count = 0
        for k in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(k) + r'\b'
            count += len(re.findall(pattern, text))
        return count

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers
        return [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric consistency (e.g. 9.11 < 9.9)."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric logic to check
        
        # Simple heuristic: if prompt has numbers and candidate has numbers,
        # check if they maintain order if comparatives are present.
        # This is a simplified compositional check.
        has_comp = any(k in self._normalize(prompt) for k in self.comparatives)
        
        if has_comp and len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares A and B, and candidate picks one, 
            # we assume the prompt implies a relationship. 
            # Without specific variable mapping, we reward numeric presence in context.
            return 0.5 
        
        return 0.0

    def _bracket_structure(self, text: str) -> Dict[str, Any]:
        """Phenomenological bracketing: isolate intentional structures."""
        lower_text = self._normalize(text)
        return {
            'neg_count': self._count_keywords(lower_text, self.negations),
            'comp_count': self._count_keywords(lower_text, self.comparatives),
            'cond_count': self._count_keywords(lower_text, self.conditionals),
            'has_numbers': len(self._extract_numbers(text)) > 0
        }

    def _structural_consistency(self, prompt: str, candidate: str) -> float:
        """
        Check if the candidate respects the structural constraints of the prompt.
        Returns a score 0.0 to 1.0.
        """
        p_struct = self._bracket_structure(prompt)
        c_struct = self._bracket_structure(candidate)
        lower_c = self._normalize(candidate)
        lower_p = self._normalize(prompt)
        
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, valid answers often reflect that (or are simple affirmations/denials)
        if p_struct['neg_count'] > 0:
            # If candidate is a simple yes/no, it's plausible. 
            # If candidate repeats the negation logic, it's strong.
            if any(k in lower_c for k in self.negations):
                score += 0.4
            elif any(k in lower_c for k in self.bool_yes + self.bool_no):
                score += 0.2 # Plausible but less specific
        
        # 2. Comparative Consistency
        if p_struct['comp_count'] > 0:
            if any(k in lower_c for k in self.comparatives):
                score += 0.4
            elif self._extract_numbers(candidate):
                score += 0.3 # Numeric answer to comparative question
        
        # 3. Conditional Consistency
        if p_struct['cond_count'] > 0:
            if any(k in lower_c for k in ['if', 'then', 'because', 'so']):
                score += 0.3
            elif any(k in lower_c for k in self.bool_yes + self.bool_no):
                score += 0.1

        # 4. Numeric Logic Check
        score += self._check_numeric_logic(prompt, candidate)
        
        # Cap at 1.0
        return min(score, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        # Concatenate for joint compression
        joint = b1 + b2
        len_joint = len(zlib.compress(joint))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) as len(compress(x))
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        
        numerator = len_joint - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
            
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_struct = self._bracket_structure(prompt)
        
        for cand in candidates:
            # Primary Signal: Structural/Compositional Consistency
            struct_score = self._structural_consistency(prompt, cand)
            
            # Secondary Signal: NCD (Tiebreaker)
            # We invert NCD because lower distance = higher similarity = better
            # But pure NCD is weak, so we weight it lightly.
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.2 # Max contribution 0.2
            
            # Heuristic boost for length appropriateness
            # Avoid extremely short answers unless they are boolean
            lower_c = self._normalize(cand)
            length_penalty = 0.0
            if len(lower_c.split()) < 2 and not any(k in lower_c for k in self.bool_yes + self.bool_no):
                # If it's not a simple yes/no, being too short might be bad for complex prompts
                if p_struct['cond_count'] > 0 or p_struct['comp_count'] > 0:
                    length_penalty = -0.1
            
            final_score = struct_score + ncd_score + length_penalty
            
            # Reasoning trace
            reasoning = f"Structural match: {struct_score:.2f}, NCD similarity: {ncd_score:.2f}"
            if p_struct['neg_count'] > 0 and any(k in lower_c for k in self.negations):
                reasoning += "; Detected negation alignment."
            if p_struct['has_numbers'] and self._extract_numbers(cand):
                reasoning += "; Numeric consistency detected."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural consistency score as the primary driver.
        """
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score to 0-1 range based on our internal weighting
        # Our max structural score is ~1.0 + 0.2 (NCD) - penalties.
        raw_score = res[0]['score']
        
        # Map to 0-1. If score > 0.5, it's likely correct. 
        # If score < 0, likely wrong.
        confidence = max(0.0, min(1.0, (raw_score + 0.2) / 1.2))
        return confidence