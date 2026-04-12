import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A Type-Theoretic Active Inference Reasoning Tool with Prime-Derived Priors.
    
    Mechanism:
    1. Structural Parsing (Type Theory): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'dependent type' skeleton of the prompt.
       Candidates are scored on how well their structure matches this skeleton.
    2. Active Inference (Free Energy Minimization): 
       - Risk: Penalty for violating explicit logical constraints (e.g., saying "Yes" when prompt has "not").
       - Epistemic Gain: Bonus for candidates that resolve numeric or comparative ambiguities.
       - The final score balances these via a Free Energy heuristic.
    3. Prime-Derived Prior (Confidence Wrapper): 
       - Uses a lightweight check based on prime-number properties (length primality, 
         character code sums modulo primes) as a "structural prior" to adjust confidence.
       - Per instructions, this is restricted to the confidence wrapper and does not 
         drive the primary ranking logic to avoid reasoning traps.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self.primes = self._generate_primes(1000)
        
    def _generate_primes(self, limit: int) -> List[int]:
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        return [i for i, is_prime in enumerate(sieve) if is_prime]

    def _is_prime(self, n: int) -> bool:
        if n < 2: return False
        for p in self.primes:
            if p * p > n: break
            if n % p == 0: return False
        return True

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical types: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|>=|<=|>|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return structure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_candidate_logic(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        Compute Free Energy score: Risk (constraint violation) + Prior (structural match).
        Lower energy = better candidate. We invert this for a higher-is-better score.
        """
        score = 0.0
        
        # 1. Negation Consistency (Type Constraint)
        # If prompt has negations, candidate should ideally reflect awareness (simplified heuristic)
        if prompt_struct['negations'] > 0:
            # Penalize if candidate is extremely short (likely ignoring nuance) or lacks negation words if prompt is heavy on them
            if cand_struct['negations'] == 0 and len(candidate.split()) < 5:
                score -= 2.0 # High risk
            else:
                score += 0.5 # Reward checking
        
        # 2. Comparative/Number Matching (Active Inference - Epistemic Gain)
        if prompt_struct['comparatives'] > 0 or prompt_struct['numbers']:
            # Did the candidate pick up numbers?
            if cand_struct['numbers']:
                score += 1.5 # High information gain
            elif prompt_struct['numbers']:
                # If prompt has numbers but candidate doesn't, slight penalty unless it's a yes/no question
                if len(prompt_struct['numbers']) > 0 and len(cand_struct['numbers']) == 0:
                     if len(candidate.split()) > 2: # Not a simple yes/no
                         score -= 1.0
        
        # 3. Conditional Logic
        if prompt_struct['conditionals'] > 0:
            if cand_struct['conditionals'] > 0 or 'if' in candidate.lower() or 'then' in candidate.lower():
                score += 1.0
        
        # 4. Length Prior (Heuristic for completeness)
        if cand_struct['length'] < prompt_struct['length'] * 0.1 and prompt_struct['length'] > 20:
            score -= 0.5 # Too short to be reasoned
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Structural/Logical consistency (Type Theory + Active Inference)
            logic_score = self._evaluate_candidate_logic(prompt_struct, cand_struct, cand)
            
            results.append({
                "candidate": cand,
                "score": logic_score,
                "reasoning": f"Structural match: {logic_score:.2f}",
                "_struct": cand_struct # Internal use for tie-breaking
            })
        
        # Sort by logic score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD only if scores are very close (within 0.01)
        final_results = []
        if len(results) > 1:
            for i in range(len(results)):
                if i == 0:
                    final_results.append(results[i])
                    continue
                
                prev = final_results[-1]
                curr = results[i]
                
                if abs(prev["score"] - curr["score"]) < 0.01:
                    # Use NCD as tiebreaker
                    ncd_prev = self._compute_ncd(prompt, prev["candidate"])
                    ncd_curr = self._compute_ncd(prompt, curr["candidate"])
                    # Lower NCD is better (more similar/compressible together)
                    if ncd_curr < ncd_prev:
                        final_results.append(curr)
                        # Swap in list to maintain sort order visually if needed, 
                        # but here we just append. Actually, we need to re-sort or insert.
                        # Simpler: Just adjust score slightly for tiebreak
                        curr["score"] -= 0.001 # Penalty for higher NCD (wait, lower NCD is better)
                        # Let's just rely on the fact that we process in order and only swap if strictly better
                        if ncd_curr < ncd_prev:
                             final_results[-1] = curr
                             final_results.append(prev) # This logic is getting messy for a simple sort.
                             # Correct approach: Modify score slightly based on NCD for ties
                        final_results.pop() # Remove previous to re-evaluate
                        # Re-sorting the whole list is safer for ties
                        for item in final_results:
                            item["score"] -= self._compute_ncd(prompt, item["candidate"]) * 0.0001
                        final_results.append(curr)
                        final_results.sort(key=lambda x: x["score"], reverse=True)
                    else:
                        final_results.append(curr)
                else:
                    final_results.append(curr)
        else:
            final_results = results

        # Clean up internal keys and format output
        output = []
        for item in final_results:
            output.append({
                "candidate": item["candidate"],
                "score": round(item["score"], 4),
                "reasoning": item["reasoning"]
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Prime-Derived Priors as a structural wrapper (per constraints).
        Checks: 
        1. Basic logical consistency (via structural overlap).
        2. Prime-based heuristic: Is the answer length or char-sum 'prime-aligned'?
           (Used as a weak prior signal, not a hard filter).
        """
        # 1. Structural Consistency Check (Base Confidence)
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        base_score = 0.5
        
        # Negation alignment
        if p_struct['negations'] > 0:
            if a_struct['negations'] > 0 or len(answer) < 10: # Short answers might be 'No'
                base_score += 0.2
            else:
                base_score -= 0.3
        
        # Number presence alignment
        if p_struct['numbers']:
            if a_struct['numbers']:
                base_score += 0.2
            else:
                base_score -= 0.1
                
        # 2. Prime-Derived Prior (Wrapper only)
        # Heuristic: Does the answer exhibit 'prime-like' randomness or structure?
        # We check if the length is prime or if the sum of ASCII codes mod a small prime is non-zero
        ans_len = len(answer)
        is_len_prime = self._is_prime(ans_len)
        
        ascii_sum = sum(ord(c) for c in answer)
        # Check against first few primes
        prime_aligned = any(ascii_sum % p != 0 for p in [2, 3, 5, 7])
        
        prior_bonus = 0.0
        if is_len_prime:
            prior_bonus += 0.05
        if prime_aligned:
            prior_bonus += 0.05
            
        # Cap and floor
        final_conf = base_score + prior_bonus
        return max(0.0, min(1.0, final_conf))

# Example usage logic would go here if run as script, but class is the requirement.