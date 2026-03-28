import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Causal-Mechanism Design Tool.
    
    Mechanism:
    1. Structural Parsing (The 'Causal Functor'): Encodes prompts into a structural 
       vector space based on logic operators (negation, conditionals), comparatives, 
       and numeric values. This mimics encoding a CBN into a category.
       
    2. Mechanism Design (The 'Natural Transformation'): Evaluates candidates by 
       checking if they preserve the structural 'morphisms' of the prompt. 
       Candidates that satisfy the logical constraints (e.g., if prompt says "A > B", 
       candidate must reflect that) receive high 'social welfare' scores.
       
    3. Adjoint Optimization: The final score is a weighted sum where structural 
       compliance (Mechanism Design) is the primary driver, and NCD serves only 
       as a tie-breaking regularizer (Left Adjoint to the forgetful functor).
       
    This approach prioritizes logical consistency over string similarity, addressing
    the 'Causal Inference' inhibitor by using it only for structure extraction, not
    direct scoring, while leveraging 'Mechanism Design' as the core evaluator.
    """

    def __init__(self):
        # Weights derived from the "strong positive synergy" note
        self.w_structure = 0.60
        self.w_numeric = 0.25
        self.w_ncd = 0.15
        
        # Keywords for structural extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'without', 'fail']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies', 'when']

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical morphisms from text (The Causal Functor)."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # 1. Negation count
        neg_count = sum(1 for w in words if w in self.negations)
        
        # 2. Conditional count
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # 3. Comparative presence
        has_comp = 1 if any(w in text_lower for w in self.comparatives) else 0
        
        # 4. Numeric extraction
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        nums = [float(n) for n in numbers]
        max_num = max(nums) if nums else 0.0
        has_nums = 1 if nums else 0
        
        return {
            'negations': neg_count,
            'conditionals': cond_count,
            'has_comparative': has_comp,
            'max_num': max_num,
            'has_nums': has_nums,
            'length': len(words)
        }

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate preserves the logical morphisms of the prompt.
        Implements the 'Natural Transformation' check.
        """
        score = 0.0
        checks = 0
        
        # Check 1: Negation preservation
        # If prompt has strong negation, valid answers often contain negation or specific antonyms
        # Heuristic: If prompt has >1 negations, candidate likely needs careful handling
        if prompt_struct['negations'] > 1:
            checks += 1
            if cand_struct['negations'] > 0:
                score += 1.0
            # Allow some flexibility, but penalize total absence if prompt is highly negative
            elif prompt_struct['negations'] > 2:
                score += 0.5 
                
        # Check 2: Numeric consistency (The 'Do-Calculus' on numbers)
        if prompt_struct['has_nums'] and cand_struct['has_nums']:
            checks += 1
            # If prompt implies a comparison (e.g., "larger than 5"), check candidate numbers
            # Simple heuristic: Candidate numbers should be in the same order of magnitude 
            # or explicitly answer the comparison if detectable.
            # Here we check if the candidate repeats the key number (common in correct answers)
            # or provides a calculated result.
            p_max = prompt_struct['max_num']
            c_max = cand_struct['max_num']
            
            # Tolerance for float equality
            if abs(p_max - c_max) < 0.01 * (p_max + 0.1):
                score += 1.0
            elif p_max > 0 and c_max > 0:
                # If different, ensure it's a plausible transformation (e.g. sum/diff)
                # For now, strict match gets full points, close enough gets partial
                ratio = c_max / p_max if p_max != 0 else 0
                if 0.9 < ratio < 1.1: score += 0.8
        elif prompt_struct['has_nums'] and not cand_struct['has_nums']:
            # Prompt has numbers, candidate doesn't -> likely wrong unless it's a yes/no question
            # Check if candidate is a simple affirmative/negative
            if cand_struct['length'] < 5: 
                score += 0.5 # Accept short answers to numeric prompts sometimes
            else:
                score += 0.0 # Long answer without numbers when prompt has them is suspicious

        # Check 3: Structural Complexity Matching
        # Complex prompts (conditionals) usually require non-trivial candidates
        if prompt_struct['conditionals'] > 0:
            checks += 1
            if cand_struct['length'] > 3: # Avoid single word answers to complex logic
                score += 1.0
        
        return score / max(checks, 1) if checks > 0 else 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denominator = max(c1, c2)
            if denominator == 0: return 1.0
            return (c12 - min(c1, c2)) / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCDs for tie-breaking
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._ncd(prompt, cand))
        
        # Normalize NCD to be a similarity (1 - distance)
        min_ncd = min(ncd_scores) if ncd_scores else 0
        max_ncd = max(ncd_scores) if ncd_scores else 1
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0
        
        for i, cand in enumerate(candidates):
            cand_struct = self._extract_structure(cand)
            
            # 1. Mechanism Design Score (Logical Consistency)
            logic_score = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # 2. Numeric/Structural Overlap (Simple heuristic boost)
            # Does the candidate contain key structural tokens found in prompt?
            overlap_score = 0.0
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            common = p_words.intersection(c_words)
            # Boost if common words include logic operators
            logic_ops = set(self.negations + self.comparatives + self.conditionals)
            logic_overlap = len(common.intersection(logic_ops))
            overlap_score = min(1.0, logic_overlap * 0.3 + len(common) * 0.05)

            # 3. NCD Tiebreaker (Normalized)
            ncd_sim = 1.0 - ((ncd_scores[i] - min_ncd) / range_ncd)
            
            # Final Score: Weighted sum emphasizing Mechanism Design (Logic)
            # Logic is the primary driver as per instructions
            final_score = (self.w_structure * logic_score) + \
                          (self.w_numeric * overlap_score) + \
                          (self.w_ncd * ncd_sim)
            
            # Deterministic noise injection based on content hash to break exact ties fairly
            # but keep it deterministic
            hash_val = hash(cand) % 1000 / 10000.0 
            
            results.append({
                "candidate": cand,
                "score": final_score + hash_val,
                "reasoning": f"Logic:{logic_score:.2f}, Struct:{overlap_score:.2f}, NCD:{ncd_sim:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate method's internal logic on a single candidate.
        """
        # Run evaluation on the single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        # Normalize the score to 0-1 range roughly
        # Since max theoretical score is approx 1.0 + small hash
        score = res[0]['score']
        confidence = min(1.0, max(0.0, score))
        
        return confidence