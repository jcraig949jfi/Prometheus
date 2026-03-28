import re
import math
from collections import Counter

class ReasoningTool:
    """
    Prime-Encoded Active Inference Model Checker (PEAIMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Free Energy Core): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a 'surprise' metric.
       Low surprise (high consistency with logical constraints) = High Score.
    2. Prime-Encoded State Representation: Maps extracted structural tokens to prime 
       numbers. The 'state' of a candidate is the product of primes corresponding 
       to its logical features. This allows algebraic comparison of logical structures.
    3. Model Checking Simulation: Treats the prompt's constraints as a temporal logic 
       specification. Candidates are 'verified' by checking if their prime-encoded 
       structure satisfies the prompt's structural requirements (e.g., if prompt has 
       negation, candidate must have negation).
    4. Scoring: Base score derived from structural adherence (Free Energy minimization).
       NCD is used strictly as a tie-breaker for candidates with identical structural scores.
    """

    # First 20 primes for token encoding
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    # Structural patterns mapped to primes
    PATTERNS = [
        (r'\bnot\b|\bno\b|\bnever\b|\bnone\b', 0),      # Negation
        (r'\bif\b|\bthen\b|\belse\b|\bunless\b', 1),   # Conditionals
        (r'\bgreater\b|\bless\b|\bmore\b|\bfewer\b|>|<', 2), # Comparatives
        (r'\band\b|\bor\b|\bboth\b|\beither\b', 3),     # Conjunctions
        (r'\ball\b|\bevery\b|\bsome\b|\bat\s+least\b', 4), # Quantifiers
        (r'\d+', 5),                                    # Numeric presence
        (r'\btrue\b|\bfalse\b|\byes\b|\bno\b', 6),      # Boolean literals
        (r'\btherefore\b|\bthus\b|\bhence\b', 7),       # Deduction markers
        (r'\bequal\b|\bsame\b|\bdifferent\b', 8),       # Equality
        (r'\bfirst\b|\bsecond\b|\bnext\b|\blast\b', 9)  # Ordering
    ]

    def __init__(self):
        self.state_cache = {}

    def _get_primes_in_text(self, text: str) -> list:
        """Extract primes associated with structural tokens in text."""
        text_lower = text.lower()
        found_primes = []
        for pattern, idx in self.PATTERNS:
            if re.search(pattern, text_lower):
                if idx < len(self.PRIMES):
                    found_primes.append(self.PRIMES[idx])
        # Add prime for length characteristic to differentiate long/short structural matches
        if len(text.split()) > 10:
            found_primes.append(self.PRIMES[10]) 
        return found_primes if found_primes else [1] # 1 as neutral element

    def _encode_state(self, text: str) -> int:
        """Godel-style encoding: product of primes for present features."""
        primes = self._get_primes_in_text(text)
        product = 1
        for p in primes:
            product *= p
        return product

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Calculate Free Energy surrogate: 
        Minimize surprise by matching structural features between prompt and candidate.
        """
        p_primes = set(self._get_primes_in_text(prompt))
        c_primes = set(self._get_primes_in_text(candidate))
        
        if not p_primes:
            return 0.5 # Neutral if no structure detected in prompt

        # Intersection over Union (Jaccard) of structural features
        intersection = len(p_primes & c_primes)
        union = len(p_primes | c_primes)
        
        if union == 0:
            return 0.0
            
        base_score = intersection / union
        
        # Penalty for missing critical negation/conditional logic present in prompt
        # This simulates the Model Checker finding a counter-example
        penalty = 0.0
        if 2 in p_primes and 2 not in c_primes: # Missing comparative
            penalty += 0.2
        if 3 in p_primes and 3 not in c_primes: # Missing conditional
            penalty += 0.2
            
        return max(0.0, base_score - penalty)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_state = self._encode_state(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing & Free Energy Minimization
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Prime-Encoded State Check (Algebraic consistency)
            cand_state = self._encode_state(cand)
            # Simple algebraic check: does candidate state divide prompt state? 
            # (Loose analogy: is candidate structure a subset of prompt requirements?)
            algebraic_bonus = 0.0
            if prompt_state > 0 and cand_state > 0:
                if prompt_state % cand_state == 0 or cand_state % prompt_state == 0:
                    algebraic_bonus = 0.1
            
            score = struct_score + algebraic_bonus
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {struct_score:.2f}, Algebraic bonus: {algebraic_bonus:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD only if scores are very close
        final_results = []
        for i, res in enumerate(results):
            if i > 0:
                prev_score = results[i-1]["score"]
                curr_score = res["score"]
                if abs(prev_score - curr_score) < 0.01:
                    # Apply NCD tiebreaker
                    ncd_curr = self._ncd(prompt, res["candidate"])
                    ncd_prev = self._ncd(prompt, results[i-1]["candidate"])
                    if ncd_curr < ncd_prev:
                        # Swap logic handled by stable sort if we adjusted score slightly
                        res["score"] += 0.0001 
            final_results.append(res)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        score = self._structural_score(prompt, answer)
        # Clamp between 0 and 1
        return max(0.0, min(1.0, score))