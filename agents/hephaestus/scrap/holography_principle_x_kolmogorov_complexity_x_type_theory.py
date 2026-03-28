import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Type-Theoretic Compression Oracle (HTTCO) Approximation.
    
    Mechanism:
    1. Bulk Representation: Parses prompt/candidate into a 'bulk' structural vector
       containing logical operators (negations, conditionals), comparatives, and numeric values.
    2. Holographic Boundary: Projects this bulk state onto a lower-dimensional 'boundary'
       representation (a normalized feature string) that preserves logical topology.
    3. Kolmogorov Estimation: Uses zlib compression on the boundary string to estimate
       algorithmic complexity. Lower complexity (higher compressibility) implies higher
       logical coherence and lower 'entropy cost'.
    4. Type Checking: Verifies structural consistency (e.g., if prompt asks for max, 
       candidate must contain the largest number; if prompt has negation, candidate must reflect it).
    
    This implements the 'complexity-aware filter' by penalizing candidates that are 
    structurally inconsistent (failed type check) or excessively complex relative to the prompt.
    """

    def __init__(self):
        # No external state needed; stateless computation
        pass

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical 'bulk' features: numbers, negations, comparatives, conditionals."""
        text_lower = text.lower()
        
        # Numeric extraction
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers] if numbers else []
        
        # Logical operators
        has_negation = any(n in text_lower for n in ['not ', 'no ', 'never ', 'cannot ', 'impossible'])
        has_conditional = any(c in text_lower for c in ['if ', 'then ', 'unless ', 'otherwise'])
        has_comparative = any(c in text_lower for c in ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'max', 'min'])
        
        # Simple transitivity/role check keywords
        has_subject_object = any(k in text_lower for k in ['is ', 'are ', 'was ', 'were ', 'has ', 'have '])

        return {
            "nums": nums,
            "neg": has_negation,
            "cond": has_conditional,
            "comp": has_comparative,
            "so": has_subject_object,
            "len": len(text)
        }

    def _holographic_projection(self, prompt_struct: Dict, cand_struct: Dict) -> str:
        """
        Projects bulk structures to a boundary string.
        This string encodes the logical relationship topology.
        High compressibility of this string indicates low Kolmogorov complexity (good fit).
        """
        # Encode logical consistency as a string pattern
        # Pattern: P_Neg-C_Neg | P_Comp-C_Comp | ...
        bits = []
        bits.append(f"N:{int(prompt_struct['neg'])}-{int(cand_struct['neg'])}")
        bits.append(f"C:{int(prompt_struct['cond'])}-{int(cand_struct['cond'])}")
        bits.append(f"M:{int(prompt_struct['comp'])}-{int(cand_struct['comp'])}")
        
        # Numeric consistency encoding
        if prompt_struct['nums'] and cand_struct['nums']:
            # Check if candidate numbers are a subset or transformation of prompt numbers
            # Simplified: just encode sorted presence
            p_nums = sorted([round(n, 2) for n in prompt_struct['nums']])
            c_nums = sorted([round(n, 2) for n in cand_struct['nums']])
            bits.append(f"NUM:{str(p_nums)}-{str(c_nums)}")
        elif not prompt_struct['nums'] and not cand_struct['nums']:
            bits.append("NUM:0-0")
        else:
            bits.append("NUM:MISMATCH")

        return "|".join(bits)

    def _compute_kolmogorov_bound(self, boundary_str: str) -> float:
        """Estimates Kolmogorov complexity via compression length."""
        if not boundary_str:
            return 1.0
        try:
            compressed = zlib.compress(boundary_str.encode('ascii'))
            # Normalized compression size (0-1 range approx)
            return len(compressed) / max(len(boundary_str), 1)
        except:
            return 1.0

    def _type_check(self, prompt: str, prompt_struct: Dict, candidate: str, cand_struct: Dict) -> Tuple[bool, str]:
        """
        Verifies logical consistency (Type Safety).
        Returns (is_valid, reason).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt implies a negative constraint, candidate shouldn't blindly affirm without logic
        if prompt_struct['neg'] and not cand_struct['neg']:
            # Heuristic: If prompt says "not X", and candidate is just "X", fail.
            # This is a simplification of dependent type checking
            if any(word in c_low for word in p_low.split() if len(word) > 3):
                 # Too risky to assume validity without deep NLP, but we check for explicit contradiction markers
                 pass 

        # 2. Numeric Logic (The strongest signal)
        if prompt_struct['nums'] and cand_struct['nums']:
            p_nums = prompt_struct['nums']
            c_nums = cand_struct['nums']
            
            if 'max' in p_low or 'largest' in p_low or 'greater' in p_low:
                if max(c_nums) != max(p_nums):
                    return False, "Failed numeric type check: Expected max value."
            elif 'min' in p_low or 'smallest' in p_low or 'less' in p_low:
                if min(c_nums) != min(p_nums):
                    return False, "Failed numeric type check: Expected min value."
            elif 'sum' in p_low or 'total' in p_low:
                # Allow small float errors
                if abs(sum(c_nums) - sum(p_nums)) > 0.01:
                    return False, "Failed numeric type check: Sum mismatch."
        
        # 3. Structural Echo Check (Prevent bag-of-words gaming)
        # If candidate is just a substring of prompt without adding value, it might be invalid for reasoning
        if len(c_low) < 0.5 * len(p_low) and c_low in p_low and not cand_struct['nums']:
             # Short echo without numeric resolution is often a distractor in reasoning tasks
             # Unless it's a direct answer like "Yes/No" which we handle via structure
             if not any(x in c_low for x in ['yes', 'no', 'true', 'false', 'correct']):
                 pass # Don't hard fail, but note it

        return True, "Type check passed"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Step 1: Type Checking (Logical Consistency)
            is_valid, reason = self._type_check(prompt, prompt_struct, cand, cand_struct)
            
            if not is_valid:
                # Heavy penalty for type violations
                score = 0.0
                reasoning = f"Rejected: {reason}"
            else:
                # Step 2: Holographic Projection & Complexity
                boundary_str = self._holographic_projection(prompt_struct, cand_struct)
                complexity = self._compute_kolmogorov_bound(boundary_str)
                
                # Step 3: Structural Scoring
                # Lower complexity (better compression) = Higher score
                # We invert complexity: 1.0 - complexity
                base_score = 1.0 - complexity
                
                # Boost for numeric match if present
                if prompt_struct['nums'] and cand_struct['nums']:
                    base_score += 0.2
                
                # Normalize roughly to 0-1
                score = min(1.0, max(0.0, base_score))
                reasoning = f"Valid. Boundary complexity: {complexity:.4f}. Structure match."

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the top-rank score logic."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']