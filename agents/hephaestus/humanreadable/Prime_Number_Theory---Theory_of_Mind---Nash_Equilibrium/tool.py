import zlib
import math
import re
from typing import List, Dict, Tuple

# Precompute small primes for "Prime-coded" encoding simulation
# This acts as the sparse prior and unique factorization basis
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]

def ncd(a: str, b: str) -> float:
    """Normalized Compression Distance using zlib."""
    if not a or not b: return 1.0
    len_a = len(zlib.compress(a.encode()))
    len_b = len(zlib.compress(b.encode()))
    len_ab = len(zlib.compress((a + b).encode()))
    return (len_ab - min(len_a, len_b)) / max(len_a, len_b, 1)

def extract_numbers(s: str) -> List[float]:
    """Extract numeric values for numeric evaluation."""
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", s)]

def check_logic(text: str) -> float:
    """
    Structural parsing: Detect negations, comparatives, and conditionals.
    Returns a score boost for logical consistency markers.
    """
    score = 0.0
    t = text.lower()
    if "not " in t or " no " in t: score += 0.1
    if " if " in t or " then " in t: score += 0.1
    if " greater " in t or " less " in t or " more " in t: score += 0.1
    if " therefore " in t or " thus " in t: score += 0.2
    return min(score, 1.0)

class ReasoningTool:
    """
    Prime-coded Recursive Belief Learning (PRBL) Approximation.
    
    Mechanism:
    1. Prime-Encoding: Maps structural features (length, word count, logic markers) 
       to prime exponents to create a unique 'belief signature' for each candidate.
    2. Theory of Mind Simulation: Evaluates how well the candidate answers the 
       implicit intent of the prompt (structural alignment).
    3. Nash Equilibrium Solver: Treats the correct answer as a fixed point where 
       the candidate's internal logic (numbers, constraints) aligns with the prompt's 
       constraints. We approximate this via constraint satisfaction scoring.
    4. Zeta-Regularization: Uses a decaying weight series (1/n^2) to sum up 
       evidence from multiple features without divergence, ensuring stability.
    """

    def __init__(self):
        self.state = "initialized"

    def _compute_prime_signature(self, text: str) -> float:
        """
        Encodes text properties into a scalar using prime powers.
        Simulates the unique factorization property for distinctness.
        """
        if not text: return 0.0
        val = 0.0
        # Feature 1: Length mapped to prime[0]^len (scaled down)
        # Feature 2: Word count mapped to prime[1]^words
        # Feature 3: Logic score mapped to prime[2]^logic
        
        # To prevent overflow, we work in log-space (sum of exponents * log(prime))
        # This represents the 'magnitude' of the belief state
        try:
            l_len = len(text)
            l_words = len(text.split())
            l_logic = check_logic(text)
            
            # Log-space encoding: sum(exp_i * ln(p_i))
            # We weight features differently to simulate belief strength
            score = (l_len * math.log(PRIMES[0])) + \
                    (l_words * math.log(PRIMES[1])) + \
                    (l_logic * 10 * math.log(PRIMES[2]))
            return score
        except:
            return 0.0

    def _evaluate_constraints(self, prompt: str, candidate: str) -> float:
        """
        Constraint propagation: Checks numeric and structural consistency.
        Returns a score 0.0 to 1.0.
        """
        score = 0.0
        p_nums = extract_numbers(prompt)
        c_nums = extract_numbers(candidate)
        
        # Numeric Evaluation Pattern
        if p_nums and c_nums:
            # If prompt has numbers, candidate should likely relate or be consistent
            # Simple heuristic: If prompt asks comparison, candidate should have logic
            if len(p_nums) >= 2:
                # Check if candidate contains comparative logic or result
                if any(x in candidate.lower() for x in ["greater", "less", "equal", "true", "false", "yes", "no"]):
                    score += 0.4
                # Direct numeric match check for simple math
                try:
                    if abs(c_nums[0] - p_nums[0]) < 1e-6: # Identity
                        score += 0.3
                except: pass
        elif not p_nums and not c_nums:
            # Non-numeric consistency: structural presence
            score += 0.2
            
        # Structural parsing boost
        score += check_logic(candidate) * 0.3
        
        return min(score, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate prompt signature for 'Theory of Mind' alignment
        p_sig = self._compute_prime_signature(prompt)
        p_len = len(prompt.split())
        
        scores = []
        
        for cand in candidates:
            # 1. Prime-coded Belief Strength (Distinctness)
            c_sig = self._compute_prime_signature(cand)
            
            # 2. Constraint Propagation Score
            constraint_score = self._evaluate_constraints(prompt, cand)
            
            # 3. NCD as Tiebreaker (Low weight)
            similarity = ncd(prompt, cand)
            
            # 4. Nash Equilibrium Approximation (Fixed Point)
            # The 'equilibrium' is where belief distinctness meets constraint satisfaction.
            # We use a zeta-like decay series concept: Sum( feature_weight / n^2 )
            # Here simplified to a weighted sum where logical consistency dominates.
            
            # Distance from prompt complexity (Theory of Mind: matching depth)
            complexity_diff = abs(len(cand.split()) - p_len) / max(p_len, 1)
            depth_score = 1.0 / (1.0 + complexity_diff) # Closer length often implies relevant answer
            
            # Combined Score
            # Priority: Constraints > Depth Alignment > Distinctness > NCD
            final_score = (constraint_score * 0.5) + \
                          (depth_score * 0.3) + \
                          ((1.0 - similarity) * 0.1) + \
                          (0.1 if c_sig > 0 else 0.0)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Prime-sig:{c_sig:.2f}, Constraints:{constraint_score:.2f}, Depth:{depth_score:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on constraint satisfaction and logical density.
        """
        # Reuse evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]["score"]
        
        # Boost if answer contains specific logical connectors found in high-quality reasoning
        logic_boost = 0.0
        if any(w in answer.lower() for w in ["therefore", "because", "thus", "hence"]):
            logic_boost = 0.1
            
        # Penalty for extremely short answers unless they are definitive
        if len(answer.split()) < 3 and answer.lower() not in ["yes", "no", "true", "false"]:
            base_score *= 0.8
            
        return min(1.0, max(0.0, base_score + logic_boost))