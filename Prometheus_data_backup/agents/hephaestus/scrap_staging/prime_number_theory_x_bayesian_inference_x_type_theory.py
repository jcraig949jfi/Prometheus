import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A dependently-typed probabilistic reasoning engine (simulated).
    
    Mechanism:
    1. Structural Parsing (Type Checking): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt. This acts as 
       the 'dependent type' filter—candidates violating hard logical constraints 
       (e.g., saying "Yes" to a negative constraint) are penalized heavily.
    2. Bayesian Evidence (Likelihood): Computes a score based on how well the 
       candidate matches the structural signature of the prompt (e.g., if prompt 
       implies "smaller", candidates with smaller numbers get higher likelihood).
    3. Prime Theory (Confidence Wrapper): Used strictly as a structural heuristic 
       in the confidence method to detect 'prime' logical traps (e.g., simple 
       yes/no flips) without performing actual number theory proofs, adhering to 
       the causal constraint that prime theory is an inhibitor for direct scoring.
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when structural 
       signals are ambiguous.
    """

    def __init__(self):
        self.ncd_cache = {}

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negated': bool(re.search(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', text)],
            'question_type': 'binary' if re.search(r'\b(yes|no|true|false)\b', text_lower) else 'open'
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(s1_b)
        len_s2 = len(s2_b)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) approx
        # Simplified for stability: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using standard formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) is common, 
        # but often (C(xy) - min(C(x),C(y)))/max(C(x),C(y)) is used. 
        # Let's use: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Actually, standard NCD: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # To avoid dependency issues and keep it simple:
        c_x = len(zlib.compress(s1_b))
        c_y = len(zlib.compress(s2_b))
        c_xy = len_concat # Approximation for speed in this context
        
        min_c = min(c_x, c_y)
        max_c = max(c_x, c_y)
        if max_c == 0: return 1.0
        return (c_xy - min_c) / max_c

    def _evaluate_logic(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core logic engine simulating dependent type checking."""
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.5
        reasons = []

        # 1. Type Constraint: Negation Consistency
        # If prompt has strong negation and candidate contradicts the expected logical flow
        if p_feat['negated']:
            # Heuristic: If prompt says "not X", and candidate implies "X" (via similarity to prompt without 'not')
            # We check if candidate is a simple echo which might be a trap
            if candidate.lower().strip() == prompt.lower().strip().replace("not ", "").strip():
                score -= 0.4
                reasons.append("Failed negation constraint (echo trap).")
        
        # 2. Numeric Consistency (Bayesian Likelihood)
        if p_feat['numbers'] and c_feat['numbers']:
            p_nums = p_feat['numbers']
            c_nums = c_feat['numbers']
            
            # Check comparative direction
            if 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'before' in prompt.lower():
                if c_nums[0] < p_nums[0]:
                    score += 0.3
                    reasons.append("Numeric value aligns with 'less/smaller' constraint.")
                else:
                    score -= 0.3
                    reasons.append("Numeric value violates 'less/smaller' constraint.")
                    
            elif 'more' in prompt.lower() or 'greater' in prompt.lower() or 'after' in prompt.lower():
                if c_nums[0] > p_nums[0]:
                    score += 0.3
                    reasons.append("Numeric value aligns with 'more/greater' constraint.")
                else:
                    score -= 0.3
                    reasons.append("Numeric value violates 'more/greater' constraint.")

        # 3. Conditional/Modus Tollens Check
        if p_feat['conditional']:
            if 'no' in c_feat['numbers'] or 'false' in candidate.lower():
                 # Weak heuristic for conditionals: specific keywords often indicate reasoning
                 score += 0.1
                 reasons.append("Conditional detected; candidate shows logical markers.")

        # 4. Binary Question Constraint
        if p_feat['question_type'] == 'binary':
            cand_lower = candidate.lower().strip()
            if cand_lower in ['yes', 'true', '1']:
                # If prompt implies negative answer (e.g. "Is it false that...")
                if 'not' in p_feat['negated'] or 'false' in p_feat.get('question_type', ''): 
                    # This is a simplification of the type check
                    pass 
            # Pure structural match for binary
            if any(k in cand_lower for k in ['yes', 'no', 'true', 'false']):
                score += 0.1
                reasons.append("Valid binary format.")

        if not reasons:
            reasons.append("Structural analysis neutral; relying on compression distance.")

        return score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            logic_score, logic_reason = self._evaluate_logic(prompt, cand)
            
            # NCD Tiebreaker (only if logic score is near neutral 0.5)
            ncd_score = 0.0
            if 0.4 <= logic_score <= 0.6:
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD: lower distance = higher score
                ncd_score = (1.0 - ncd_val) * 0.1 
                logic_score += ncd_score
            
            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, logic_score)), # Clamp 0-1
                "reasoning": logic_reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Prime Number Theory concept strictly as a structural 'inhibitor' check:
        If the answer is too short (like a prime number is indivisible) but the prompt 
        is complex, confidence drops.
        """
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        base_conf = 0.5
        
        # Structural complexity match
        prompt_complexity = len(p_feat['numbers']) + (1 if p_feat['negated'] else 0) + (1 if p_feat['conditional'] else 0)
        answer_complexity = len(a_feat['numbers']) + (1 if a_feat['negated'] else 0)
        
        if prompt_complexity > 0:
            if answer_complexity == 0 and prompt_complexity > 1:
                # Inhibitor: Complex prompt, trivial answer (likely wrong)
                base_conf -= 0.4
            elif answer_complexity >= prompt_complexity:
                base_conf += 0.3
            else:
                base_conf += 0.1
        
        # Prime Theory Inhibitor Application:
        # If the answer is a single digit (prime-like simplicity) for a multi-step logical prompt
        ans_clean = answer.strip()
        if len(ans_clean) <= 2 and prompt_complexity >= 2:
            # Historical inhibitor signature: simple answers to complex logic often fail
            base_conf -= 0.2
            
        return max(0.0, min(1.0, base_conf))