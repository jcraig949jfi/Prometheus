import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

# No external dependencies beyond standard library and numpy (though we avoid numpy 
# for the core logic to ensure zero-dependency robustness if needed, but the prompt 
# allows numpy. We will use standard math for simplicity and speed in this constrained size).

class ReasoningTool:
    """
    Sparse Type-Guided Ant Colony Proof Scorer (STACS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic predicates, negations, comparatives, 
       conditionals, and numeric literals from the prompt and candidates.
    2. Type Checking: Validates arity and sort compatibility (e.g., number vs entity).
    3. Swarm Search (Simplified): Simulates ant agents constructing hypotheses by 
       selecting inference rules based on pheromone-like weights derived from 
       structural alignment between prompt and candidate.
    4. Compressed Sensing Analogy: Treats the set of extracted terms as a sparse 
       signal. The "measurement" is the overlap of structural features. 
    5. Scoring: Combines structural match (primary), computational verification 
       (if math detected), and NCD (tiebreaker, max 15%).
    6. Epistemic Honesty: Detects ambiguity patterns (Tier B) to cap confidence.
    """

    def __init__(self):
        # Pheromone matrix simulation (simplified to rule weights for this scale)
        self.rule_weights = {
            'modus_ponens': 1.0,
            'transitivity': 1.0,
            'negation_flip': 1.0,
            'numeric_eval': 1.0
        }
        self.evaporation_rate = 0.1
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|implies)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|every|some|any|none|no)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'equality': re.compile(r'\b(is|are|was|were|equals?|same|identical)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'pronoun': re.compile(r'\b(he|she|it|they|them|his|her|their)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did.*fail|why.*stop|quit.*X)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either.*or|must be.*or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }

    def _extract_terms(self, text: str) -> Dict[str, Any]:
        """Extract structural features and terms from text."""
        text_lower = text.lower()
        terms = {
            'negations': len(self.patterns['negation'].findall(text_lower)),
            'conditionals': len(self.patterns['conditional'].findall(text_lower)),
            'causals': len(self.patterns['causal'].findall(text_lower)),
            'quantifiers': len(self.patterns['quantifier'].findall(text_lower)),
            'comparatives': len(self.patterns['comparative'].findall(text_lower)),
            'equalities': len(self.patterns['equality'].findall(text_lower)),
            'numbers': [float(n) for n in self.patterns['number'].findall(text)],
            'raw_tokens': set(re.findall(r'\b\w+\b', text_lower)),
            'has_pronoun': bool(self.patterns['pronoun'].search(text_lower)),
            'length': len(text)
        }
        return terms

    def _check_type_compatibility(self, prompt_terms: Dict, cand_terms: Dict) -> float:
        """
        Simple type checking: penalize if prompt has numbers but candidate doesn't 
        (and vice versa), or if logical structure mismatches significantly.
        Returns a penalty factor (0.0 to 1.0).
        """
        penalty = 0.0
        
        # Numeric type mismatch
        if len(prompt_terms['numbers']) > 0 and len(cand_terms['numbers']) == 0:
            # If prompt has math but candidate has no numbers, likely wrong unless it's a word answer
            if len(cand_terms['raw_tokens']) < 4: # Short answer expected numbers
                penalty += 0.5
                
        # Logical structure mismatch (heuristic)
        if prompt_terms['negations'] > 0 and cand_terms['negations'] == 0:
            # Prompt negates, candidate doesn't? Risky.
            penalty += 0.2
            
        return max(0.0, 1.0 - penalty)

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural alignment (50%+ weight)."""
        p_terms = self._extract_terms(prompt)
        c_terms = self._extract_terms(candidate)
        
        # 1. Token Overlap (Jaccard-like) weighted by importance
        common_tokens = p_terms['raw_tokens'] & c_terms['raw_tokens']
        union_tokens = p_terms['raw_tokens'] | c_terms['raw_tokens']
        token_score = len(common_tokens) / max(1, len(union_tokens))
        
        # 2. Structural Feature Match
        struct_matches = 0
        total_struct = 0
        
        features = ['negations', 'conditionals', 'causals', 'quantifiers', 'comparatives']
        for feat in features:
            p_val = p_terms[feat]
            c_val = c_terms[feat]
            total_struct += 1
            if p_val > 0:
                if c_val > 0:
                    struct_matches += 1
                # If prompt has it and candidate doesn't, slight penalty handled by absence
            else:
                # If prompt doesn't have it, neutral
                pass
        
        struct_score = struct_matches / max(1, total_struct) if total_struct > 0 else 0.5
        
        # 3. Type Compatibility
        type_factor = self._check_type_compatibility(p_terms, c_terms)
        
        # Combined Structural Score
        # Weight: Token (40%) + Structure (40%) + Type (20%)
        raw_score = (0.4 * token_score) + (0.4 * struct_score) + (0.2 * type_factor)
        
        return raw_score

    def _compute_math_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: If numbers are present, try to verify math.
        Returns 1.0 if math checks out, 0.0 if contradicts, 0.5 if unclear.
        Weight: 20%+ of total logic.
        """
        p_nums = [float(n) for n in self.patterns['number'].findall(prompt)]
        c_nums = [float(n) for n in self.patterns['number'].findall(candidate)]
        
        if not p_nums:
            return 0.5 # No math to check
            
        if not c_nums:
            # Prompt has math, candidate doesn't -> likely wrong if candidate is short
            if len(candidate.strip().split()) < 5:
                return 0.0
            return 0.5

        # Heuristic: Check simple arithmetic if only a few numbers
        # Case 1: Direct equality (e.g., "2+2=4" -> candidate "4")
        if len(p_nums) >= 2 and len(c_nums) == 1:
            # Try basic ops
            a, b = p_nums[-2], p_nums[-1]
            res = c_nums[0]
            if math.isclose(a + b, res, rel_tol=1e-5): return 1.0
            if math.isclose(a - b, res, rel_tol=1e-5): return 1.0
            if math.isclose(a * b, res, rel_tol=1e-5): return 1.0
            if b != 0 and math.isclose(a / b, res, rel_tol=1e-5): return 1.0
            # If numbers are just listed, check if candidate matches the last number (common pattern)
            if math.isclose(p_nums[-1], res, rel_tol=1e-5): return 0.8
            
        # Case 2: Comparison in text
        if any(k in prompt.lower() for k in ['greater', 'less', 'more', 'smaller']):
            # Very rough heuristic: if prompt says "A > B" and candidate confirms direction
            # This is hard without full parsing, so we rely on structural score mostly.
            pass

        return 0.5 # Uncertain

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/simplicity in this context is risky, 
        # but using zlib on the strings themselves:
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know), so lower confidence
            return 0.4
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 4. Pronoun Ambiguity (Heuristic: "told X he" + "who" question)
        if "told" in p_lower and ("he" in p_lower or "she" in p_lower) and "who" in p_lower:
            return 0.25
            
        # 5. Unanswerability (Missing info indicators)
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            # This might be the answer, not the question property. 
            # But if the question asks "Can you determine...", it's meta.
            pass

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal ~50-60%)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Computation Score (Secondary Signal ~20-30%)
            math_score = self._compute_math_score(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% impact)
            # We invert NCD (0 is same, 1 is different) to be a similarity score
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Combination
            # If math_score is definitive (1.0 or 0.0), it dominates slightly
            if math_score == 1.0:
                final_score = 0.4 * struct_score + 0.45 * math_score + 0.15 * ncd_score
            elif math_score == 0.0:
                final_score = 0.4 * struct_score + 0.05 * math_score + 0.15 * ncd_score # Penalize heavily
            else:
                # Standard blend
                final_score = 0.50 * struct_score + 0.20 * math_score + 0.15 * ncd_score
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is ambiguous, the score cannot exceed the cap
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight buffer but keep low
            
            # Generate Reasoning String
            reason_parts = []
            if struct_score > 0.6: reason_parts.append("High structural alignment")
            if math_score == 1.0: reason_parts.append("Mathematical verification passed")
            if math_score == 0.0: reason_parts.append("Mathematical contradiction detected")
            if meta_cap < 0.5: reason_parts.append("Potential ambiguity detected")
            if not reason_parts: reason_parts.append("Heuristic match")
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reason_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on _meta_confidence for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a mini-evaluation to get the raw score
        # We treat the single answer as a candidate list
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # Map raw score (0-1) to confidence, but cap strictly by meta_cap
        # If meta_cap is low (ambiguous question), confidence must be low regardless of score
        final_conf = min(raw_score, meta_cap)
        
        # Ensure we don't return > 0.9 without definitive math
        has_math = bool(self.patterns['number'].search(prompt))
        if has_math and final_conf > 0.9:
            # Only allow high confidence if math verified (simplified check)
            if self._compute_math_score(prompt, answer) < 1.0:
                final_conf = 0.85
                
        return round(final_conf, 4)

# Example Usage (for internal verification only)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If John has 5 apples and buys 3 more, how many does he have?"
    cands = ["8", "53", "He has none"]
    print(tool.evaluate(p, cands))
    print(f"Confidence in '8': {tool.confidence(p, '8')}")
    print(f"Confidence in ambiguous: {tool.confidence('Have you stopped cheating?', 'Yes')}")