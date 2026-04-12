import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified Ergodic-Pragmatic Free Energy Reasoner.
    
    Mechanism:
    1. Structural Parsing (Pragmatics): Extracts logical operators (negation, comparatives)
       and numeric values to define the 'semantic content'.
    2. Ergodic Sampling (MCMC approximation): Instead of heavy MCMC, we perform 
       deterministic 'trajectory sampling' by generating perturbed versions of the 
       candidate interpretation (via token masking/swapping) to estimate the stability 
       of the answer under noise. This mimics the ergodic theorem's time-average convergence.
    3. Free Energy Minimization: Calculates a 'prediction error' based on how well the 
       candidate satisfies the extracted constraints (logic/numbers). 
       Score = - (Prediction Error) + (Stability Bonus).
    4. NCD Tiebreaker: Uses zlib compression distance only when scores are nearly identical.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.logic_ops = {'if', 'then', 'else', 'and', 'or', 'but', 'however'}
        
    def _tokenize(self, text: str) -> List[str]:
        return text.lower().replace('.', '').replace(',', '').split()

    def _extract_numbers(self, text: str) -> List[float]:
        nums = []
        for word in self._tokenize(text):
            try:
                # Handle basic floats
                if '.' in word or word.isdigit():
                    nums.append(float(word))
            except ValueError:
                continue
        return nums

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Evaluates logical and numeric consistency (Pragmatic Likelihood).
        Returns a penalty score (lower is better).
        """
        penalty = 0.0
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        full_text = f"{prompt} {candidate}"
        f_tokens = self._tokenize(full_text)
        
        # 1. Negation Consistency
        p_has_neg = any(w in self.negation_words for w in p_tokens)
        c_has_neg = any(w in self.negation_words for w in c_tokens)
        
        # Simple heuristic: If prompt implies negation logic, candidate must align
        # This is a rough proxy for Gricean maxims
        if 'not' in prompt and 'yes' in c_tokens:
            penalty += 2.0
        if 'not' in prompt and 'no' not in c_tokens and 'false' not in c_tokens:
             # If prompt has 'not' but candidate doesn't explicitly negate or deny, slight penalty
             # unless it's a complex sentence. Simplified for brevity.
             pass

        # 2. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) == 1:
            # Check comparative logic if present
            has_greater = any(w in self.comparatives and w in ['greater', 'larger', 'more', '>'] for w in p_tokens)
            has_less = any(w in self.comparatives and w in ['less', 'smaller', 'fewer', '<'] for w in p_tokens)
            
            if has_greater:
                if c_nums[0] != max(p_nums):
                    penalty += 5.0 # High penalty for wrong max
                else:
                    penalty -= 1.0 # Reward
            elif has_less:
                if c_nums[0] != min(p_nums):
                    penalty += 5.0
                else:
                    penalty -= 1.0
                    
        # 3. Keyword Overlap (Semantic Content)
        # Penalize if candidate introduces random words not in prompt context (unless it's a standard yes/no)
        common_vocab = set(p_tokens) | {'yes', 'no', 'true', 'false', 'the', 'is', 'are', 'a', 'an'}
        for w in c_tokens:
            if w not in common_vocab and len(w) > 3:
                penalty += 0.5
                
        return penalty

    def _ergodic_stability_score(self, prompt: str, candidate: str, iterations: int = 5) -> float:
        """
        Simulates ergodic sampling by perturbing the input and checking 
        if the 'meaning' (represented by hash of key tokens) remains stable.
        In this deterministic implementation, we measure sensitivity to token removal.
        """
        stability = 0.0
        base_tokens = self._tokenize(candidate)
        if not base_tokens:
            return 0.0
            
        base_sig = len(base_tokens) # Simple signature
        
        for i in range(min(iterations, len(base_tokens))):
            # Create a perturbed version (masking one token)
            perturbed = base_tokens[:i] + base_tokens[i+1:]
            # Check if the core meaning (approximated by remaining length/structure) holds
            # In a real system, this would re-run the inference engine.
            # Here, we assume shorter deviations from the original structure indicate 
            # a more robust (ergodic) hypothesis if the constraint check still passes.
            
            temp_cand = " ".join(perturbed)
            if not temp_cand:
                stability += 1.0
                continue
                
            # If the perturbed version still satisfies constraints (low penalty), it's stable
            if self._check_constraints(prompt, temp_cand) < 2.0:
                stability += 1.0
                
        return stability / max(1, iterations)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len12 = len(zlib.compress(b1 + b2))
        denominator = max(len1, len2)
        if denominator == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_lower = prompt.lower()
        
        for cand in candidates:
            cand_lower = cand.lower()
            
            # 1. Pragmatic Likelihood (Constraint Check)
            constraint_penalty = self._check_constraints(prompt_lower, cand_lower)
            
            # 2. Ergodic Stability (Sampling)
            stability = self._ergodic_stability_score(prompt_lower, cand_lower)
            
            # 3. Free Energy Score
            # F = Energy (Penalty) - Entropy (Stability)
            # We want to minimize F, so Score = -F = Stability - Penalty
            raw_score = stability - constraint_penalty
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Stability:{stability:.2f}, Penalty:{constraint_penalty:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD tie-breaking for top candidates if scores are close
        if len(results) > 1:
            top_score = results[0]["score"]
            # Check if top 2 are within 0.1 threshold
            if abs(results[0]["score"] - results[1]["score"]) < 0.1:
                ncd_0 = self._ncd(prompt, results[0]["candidate"])
                ncd_1 = self._ncd(prompt, results[1]["candidate"])
                # Lower NCD is better (more similar to prompt context usually implies relevance)
                if ncd_0 > ncd_1:
                    results[0]["reasoning"] += " (NCD tiebreak)"
                    # Swap
                    results[0], results[1] = results[1], results[0]

        # Normalize scores to 0-1 range roughly for consistency, though raw is fine for ranking
        max_s = results[0]["score"] if results else 0
        min_s = results[-1]["score"] if results else 0
        span = max_s - min_s if max_s != min_s else 1.0
        
        final_results = []
        for r in results:
            # Shift to positive
            norm_score = (r["score"] - min_s) / span
            final_results.append({
                "candidate": r["candidate"],
                "score": float(norm_score),
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the gap between the best candidate and this answer.
        Since we don't have the full candidate list here, we estimate based on 
        internal consistency of the single answer against the prompt.
        """
        res = self.evaluate(prompt, [answer, "INVALID_PLACEHOLDER"])
        # If 'answer' is the top result and has a high normalized score, confidence is high.
        if res and res[0]["candidate"] == answer:
            return res[0]["score"]
        return 0.0