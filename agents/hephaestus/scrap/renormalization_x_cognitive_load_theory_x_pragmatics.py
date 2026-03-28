import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hierarchical, load-aware hypothesis tester combining:
    1. Renormalization: Coarse-graining text to universal structural tokens.
    2. Cognitive Load: Penalizing hypotheses that exceed complexity budgets relative to the prompt.
    3. Pragmatics: Scoring based on Gricean maxims (Relevance, Clarity, Truthfulness via logic).
    
    Strategy:
    - Structural parsing (negations, comparatives, numerics) forms the primary signal.
    - NCD is used only as a tie-breaker for structural equivalence.
    - 'Renormalization' is implemented as recursive token abstraction.
    - 'Cognitive Load' limits the depth of comparison to high-salience chunks.
    - 'Pragmatics' filters candidates that fail logical consistency or relevance checks.
    """

    def __init__(self):
        # Gricean weights
        self.w_relevance = 0.4
        self.w_clarity = 0.3
        self.w_truth = 0.3
        
        # Cognitive load capacity (arbitrary units of complexity)
        self.max_load = 50.0 

    def _coarse_grain(self, text: str) -> List[str]:
        """
        Renormalization step: Map fine-grained text to coarse structural tokens.
        Preserves logic operators, numbers, and negations; discards noise.
        """
        if not text:
            return []
        
        t = text.lower()
        tokens = []
        
        # Extract numeric values for magnitude comparison
        nums = re.findall(r'-?\d+\.?\d*', t)
        for n in nums:
            tokens.append(f"<NUM:{n}>")
            
        # Extract logical operators
        if re.search(r'\b(not|no|never|neither)\b', t):
            tokens.append("<OP:NEG>")
        if re.search(r'\b(if|then|unless|provided)\b', t):
            tokens.append("<OP:COND>")
        if re.search(r'\b(and|both|plus)\b', t):
            tokens.append("<OP:AND>")
        if re.search(r'\b(or|either)\b', t):
            tokens.append("<OP:OR>")
        if re.search(r'\b(more|less|greater|smaller|larger|fewer|better|worst)\b', t):
            tokens.append("<OP:COMP>")
        if re.search(r'\b(equal|same|identical)\b', t):
            tokens.append("<OP:EQ>")
            
        # If no structural tokens, keep raw length as a coarse feature
        if not tokens:
            tokens.append(f"<LEN:{len(text.split())}>")
            
        return tokens

    def _calculate_load(self, prompt: str, candidate: str) -> float:
        """
        Cognitive Load Controller:
        Estimates intrinsic load via entropy of coarse-grained representation.
        Extraneous load estimated by noise ratio.
        """
        p_tokens = self._coarse_grain(prompt)
        c_tokens = self._coarse_grain(candidate)
        
        # Intrinsic load: complexity of the candidate's structure
        intrinsic = len(c_tokens) * 2.0 + len(candidate) * 0.05
        
        # Extraneous load: mismatch in structural density (noise)
        # If candidate has way more tokens than prompt, it's likely hallucinated noise
        extraneous = max(0, (len(c_tokens) - len(p_tokens)) * 3.0)
        
        return intrinsic + extraneous

    def _pragmatic_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Pragmatic Filter (Gricean Maxims):
        1. Relevance: Overlap of structural tokens.
        2. Clarity: Simplicity (inverse of load).
        3. Truthfulness: Logical consistency (heuristic: negation matching).
        """
        p_struct = set(self._coarse_grain(prompt))
        c_struct = set(self._coarse_grain(candidate))
        
        # Relevance: Jaccard similarity of structural tokens
        if not p_struct and not c_struct:
            relevance = 0.5 # Neutral if no structure
        else:
            intersection = p_struct.intersection(c_struct)
            union = p_struct.union(c_struct)
            relevance = len(intersection) / len(union) if union else 0.0
            
        # Clarity: Penalize excessive length relative to prompt
        load = self._calculate_load(prompt, candidate)
        clarity = 1.0 / (1.0 + math.exp((load - self.max_load) / 10.0)) # Sigmoid penalty
        
        # Truthfulness heuristic: 
        # If prompt has negation and candidate lacks it (or vice versa) in a short answer, penalize?
        # Instead, we check if candidate contradicts prompt structure explicitly
        truth_penalty = 0.0
        p_neg = "<OP:NEG>" in p_struct
        c_neg = "<OP:NEG>" in c_struct
        
        # Simple contradiction detection for short answers
        if len(candidate.split()) < 5:
            if p_neg != c_neg and ("<OP:COMP>" in p_struct or "<OP:COND>" in p_struct):
                # Potential contradiction in logic flow
                truth_penalty = 0.2

        score = (self.w_relevance * relevance) + (self.w_clarity * clarity) - truth_penalty
        reason = f"Rel:{relevance:.2f}, Clr:{clarity:.2f}, Load:{load:.1f}"
        return score, reason

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._coarse_grain(prompt)
        prompt_load = self._calculate_load(prompt, prompt) # Baseline load

        for cand in candidates:
            # 1. Pragmatic Score (Primary Signal)
            prag_score, prag_reason = self._pragmatic_score(prompt, cand)
            
            # 2. Structural Parsing Bonus (Explicit checks)
            struct_bonus = 0.0
            
            # Numeric evaluation
            p_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt.lower())]
            c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', cand.lower())]
            
            if p_nums and c_nums:
                # Check if candidate preserves numeric magnitude order if comparatives exist
                if "<OP:COMP>" in prompt_struct:
                    # Rough heuristic: if prompt compares, candidate should likely reflect numbers
                    struct_bonus += 0.1 if len(c_nums) > 0 else -0.2
            
            # Negation check
            if "<OP:NEG>" in prompt_struct:
                if "<OP:NEG>" in self._coarse_grain(cand):
                    struct_bonus += 0.15 # Reinforces matching negation
            
            # 3. Cognitive Load Check
            cand_load = self._calculate_load(prompt, cand)
            load_penalty = 0.0
            if cand_load > self.max_load * 1.5:
                load_penalty = 0.2 # Heavy penalty for overload

            # 4. NCD Tiebreaker (Only if structural signals are weak)
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_bonus = 0.0
            if abs(prag_score) < 0.1: # If pragmatic signal is noise
                ncd_bonus = (1.0 - ncd_val) * 0.1 # Low weight
            
            final_score = prag_score + struct_bonus + ncd_bonus - load_penalty
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"{prag_reason}; StructBonus:{struct_bonus:.2f}; NCD:{ncd_val:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score normalized."""
        # Evaluate single candidate against itself to get relative score
        # We simulate a dummy competitor to get a range, but simpler:
        # Use the internal scoring mechanism directly
        prag_score, _ = self._pragmatic_score(prompt, answer)
        load = self._calculate_load(prompt, answer)
        
        # Normalize pragmatic score (theoretically -0.2 to 1.0 range roughly)
        # Map to 0-1
        conf = (prag_score + 0.5) / 1.5 
        conf = max(0.0, min(1.0, conf))
        
        # Apply load penalty to confidence
        if load > self.max_load:
            conf *= 0.5
            
        return float(conf)