import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Syndrome Decoder (PSD) Implementation.
    
    Mechanism:
    1. Structural Parsing (Measure-Theoretic Base): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values to form a 
       rigid structural signature. This acts as the 'measurable space' backbone.
    
    2. LDPC-inspired Syndrome Check (Error Correction): Treats the candidate's 
       structural features as a 'codeword'. Compares it against the prompt's 
       required features. Mismatches (e.g., prompt requires 'greater than', 
       candidate implies 'less than') generate a 'syndrome' (penalty).
    
    3. Pragmatic Bias (Gricean Constraints): Applies soft constraints.
       - Quantity: Penalizes excessive length deviation.
       - Relation: Boosts candidates that retain key prompt tokens.
       
    The final score is a weighted sum where structural consistency (Syndrome=0)
    is the primary driver, pragmatic fit is the secondary modifier, and NCD
    serves only as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        # Keywords for structural extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric signatures (The 'Measure' space)."""
        lower_text = text.lower()
        words = lower_text.split()
        
        # Binary flags for logical operators
        has_neg = any(n in words for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in words for c in self.conditionals)
        
        # Numeric extraction
        nums = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': tuple(sorted(nums)), # Sorted tuple for hashability/comparison
            'len': len(words)
        }

    def _compute_syndrome(self, p_struct: dict, c_struct: dict) -> float:
        """
        Computes the 'Syndrome' (Error vector magnitude).
        High penalty if logical constraints mismatch (e.g., negation flip).
        """
        penalty = 0.0
        
        # Hard constraint: Negation must align (Quality Maxim)
        if p_struct['neg'] != c_struct['neg']:
            penalty += 0.5
            
        # Hard constraint: Conditional presence (Relation Maxim)
        if p_struct['cond'] and not c_struct['cond']:
            penalty += 0.3
            
        # Soft constraint: Comparative alignment
        if p_struct['comp'] != c_struct['comp']:
            penalty += 0.2
            
        # Numeric consistency check (if both have numbers)
        if p_struct['nums'] and c_struct['nums']:
            # Simple check: do they share magnitude order? 
            # (Simplified for brevity: check if relative ordering is preserved)
            if len(p_struct['nums']) == len(c_struct['nums']):
                p_signs = [1 if n > 0 else -1 if n < 0 else 0 for n in p_struct['nums']]
                c_signs = [1 if n > 0 else -1 if n < 0 else 0 for n in c_struct['nums']]
                if p_signs != c_signs:
                    penalty += 0.4
        
        return penalty

    def _compute_pragmatics(self, prompt: str, candidate: str, p_struct: dict, c_struct: dict) -> float:
        """
        Computes pragmatic score based on Grice's Maxims.
        Returns a bonus between 0.0 and 0.4.
        """
        score = 0.0
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        
        # Relation: Overlap of significant words (excluding stop words roughly)
        common = p_words.intersection(c_words)
        overlap_ratio = len(common) / (len(p_words) + 1)
        score += min(0.2, overlap_ratio * 0.5)
        
        # Quantity: Length penalty (avoid too short or excessively long)
        len_diff = abs(p_struct['len'] - c_struct['len'])
        if len_diff == 0:
            score += 0.1
        elif len_diff < 5:
            score += 0.05
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Syndrome (Error Check) - Primary Sort Key
            syndrome = self._compute_syndrome(p_struct, c_struct)
            
            # 2. Pragmatics - Secondary Score Modifier
            pragmatic_bonus = self._compute_pragmatics(prompt, cand, p_struct, c_struct)
            
            # Base score starts high, reduced by syndrome
            base_score = 1.0 - syndrome
            
            # Final score: Structural integrity + Pragmatic nuance
            # Note: Syndrome dominates. If syndrome > 0.5, score drops below pragmatic max.
            final_score = base_score + pragmatic_bonus
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Syndrome:{syndrome:.2f}, Prag:{pragmatic_bonus:.2f}"
            })
        
        # Sort: Higher score first. 
        # Tie-breaker: NCD (lower distance to prompt is better)
        # We invert NCD so higher is better for sorting consistency
        results.sort(key=lambda x: (x['score'], -self._ncd(prompt, x['candidate'])), reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        syndrome = self._compute_syndrome(p_struct, c_struct)
        
        # If syndrome is 0, high confidence. 
        # If syndrome is high, low confidence.
        confidence = 1.0 - syndrome
        
        # Small pragmatic boost if answer isn't empty and shares tokens
        if answer.strip():
            p_words = set(prompt.lower().split())
            c_words = set(answer.lower().split())
            if p_words.intersection(c_words):
                confidence = min(1.0, confidence + 0.05)
                
        return max(0.0, min(1.0, confidence))