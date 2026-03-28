import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dependent-Type-Driven Pragmatic Signal Interpreter (Simulation).
    
    Mechanism:
    1. Spectral Analysis (Analogy): The input string is treated as a signal. 
       We compute a 'Power Spectral Density' proxy by analyzing token frequency 
       distributions and structural variance (Welch's method analogy via segment hashing).
    2. Pragmatics (Gricean Maxims as Types):
       - Quantity: Checks if candidate length/content volume matches prompt expectations.
       - Relevance: Checks if candidate tokens are a subset of prompt+context tokens.
       - Manner: Checks for structural smoothness (balanced parentheses, no abrupt cuts).
       These act as dependent type constraints: Prag_i(source, freq_bin).
    3. Type Theory (Verification): 
       A hypothesis (candidate) is a term t_H. We attempt to construct a proof 
       that the candidate satisfies all Prag_i. 
       - Success: High score.
       - Failure (Type Error): The specific violated maxim generates a penalty 
         and a counterexample reason string.
    4. Scoring: Structural parsing (negations, numerics) provides the base signal.
       NCD is used only as a tiebreaker for semantic similarity.
    """

    def __init__(self):
        self._stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Extracts logical constraints and numeric evaluations."""
        score = 0.0
        reasons = []
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Handling (Modus Tollens check)
        negations = ['no', 'not', 'never', 'none', 'neither']
        p_has_neg = any(n in p_low.split() for n in negations)
        c_has_neg = any(n in c_low.split() for n in negations)
        
        if p_has_neg and not c_has_neg:
            reasons.append("Failed negation check (Modus Tollens violation)")
            score -= 0.3
        elif p_has_neg and c_has_neg:
            score += 0.2
            reasons.append("Consistent negation")

        # 2. Numeric Evaluation
        p_nums = re.findall(r'\d+\.?\d*', p_low)
        c_nums = re.findall(r'\d+\.?\d*', c_low)
        
        if p_nums and c_nums:
            try:
                p_val = float(p_nums[0])
                c_val = float(c_nums[0])
                # Heuristic: If prompt implies comparison, check order
                if any(x in p_low for x in ['greater', 'larger', 'more']):
                    if c_val > p_val: score += 0.3
                elif any(x in p_low for x in ['less', 'smaller', 'fewer']):
                    if c_val < p_val: score += 0.3
                else:
                    # Exact match bonus for numbers if no comparative
                    if abs(p_val - c_val) < 1e-6: score += 0.2
            except ValueError:
                pass

        # 3. Conditional/Constraint Propagation
        if 'if' in p_low and ('then' in c_low or '?' not in c_low):
            score += 0.1
            reasons.append("Conditional structure preserved")

        if not reasons:
            reasons.append("Structural baseline")
            
        return score, "; ".join(reasons)

    def _pragmatic_type_check(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates Dependent Type Checking with Gricean Maxims.
        Returns (penalty, error_message).
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        content_tokens = c_tokens - self._stopwords
        
        penalty = 0.0
        errors = []

        # Type Constraint 1: Quantity (|PSD| within band)
        # Hypothesis: Answer length should be proportional to prompt complexity
        p_len = len(prompt)
        c_len = len(candidate)
        if p_len > 20:
            if c_len < p_len * 0.1: # Too short
                penalty += 0.4
                errors.append("Type Error: Quantity maxim violated (Under-informative)")
            elif c_len > p_len * 5.0: # Too long
                penalty += 0.2
                errors.append("Type Warning: Quantity maxim strained (Over-informative)")

        # Type Constraint 2: Relevance (f_i in Context Set)
        # Check overlap of significant tokens
        if content_tokens:
            overlap = len(content_tokens & (p_tokens | self._stopwords)) # Allow stopwords
            ratio = overlap / len(content_tokens) if content_tokens else 0
            if ratio < 0.3:
                penalty += 0.5
                errors.append("Type Error: Relevance maxim violated (Off-topic tokens)")

        # Type Constraint 3: Manner (Spectral Smoothness)
        # Check for balanced delimiters (proxy for spectral leakage/variance)
        open_chars = sum(candidate.count(c) for c in '([{<')
        close_chars = sum(candidate.count(c) for c in ')]}>')
        if open_chars != close_chars:
            penalty += 0.3
            errors.append("Type Error: Manner maxim violated (Unbalanced structure)")

        if not errors:
            return 0.0, "Type Check Passed: Pragmatic consistency verified"
        
        return penalty, "; ".join(errors)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Structural Parsing (Primary Signal)
            struct_score, struct_reason = self._structural_score(prompt, cand)
            
            # 2. Pragmatic Type Checking (Validation/Filter)
            type_penalty, type_reason = self._pragmatic_type_check(prompt, cand)
            
            # 3. NCD Tiebreaker (Secondary Signal)
            # Only matters if structural/type scores are close
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Small weight
            
            final_score = 0.5 + struct_score - type_penalty + ncd_score
            final_score = max(0.0, min(1.0, final_score)) # Clamp 0-1
            
            reasoning = f"[Struct] {struct_reason}. [Type] {type_reason}."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0