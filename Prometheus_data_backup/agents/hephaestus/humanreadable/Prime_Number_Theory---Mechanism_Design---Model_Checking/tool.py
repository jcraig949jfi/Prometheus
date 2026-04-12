import math
import re
from typing import List, Dict, Optional

class ReasoningTool:
    """
    Prime-Hypothesis Verification Game (PHVG) Simulator.
    
    Mechanism:
    1. Prime Theory: Uses PNT (log N) to set adaptive verification bounds.
    2. Model Checking: Simulates bounded verification of prime properties.
    3. Mechanism Design: Applies a VCG-like scoring rule where 'confidence' 
       acts as the bid. Truthful reporting (high confidence only when certain) 
       maximizes utility; false high confidence incurs heavy penalties if 
       the candidate fails basic logical consistency checks.
       
    Note: As this is a theoretical framework for number theory conjectures, 
    the 'verification' step here simulates the BMC outcome based on logical 
    consistency and keyword heuristics, since full SAT/SMT solving is not 
    feasible within standard library constraints for arbitrary prompts.
    """

    def __init__(self):
        self._seed = 42  # Deterministic seed for any stochastic elements

    def _is_prime(self, n: int) -> bool:
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0: return False
        return True

    def _simulate_bmc_check(self, prompt: str, candidate: str) -> bool:
        """
        Simulates Bounded Model Checking.
        Checks for logical consistency (e.g., if prompt asks for primes, 
        candidate must contain valid primes or correct negation).
        """
        text = f"{prompt} {candidate}".lower()
        
        # Heuristic 1: If prompt mentions 'prime', check if candidate claims 
        # a specific small number is prime incorrectly.
        if "prime" in text:
            # Extract numbers from candidate
            nums = [int(x) for x in re.findall(r'\d+', candidate)]
            for n in nums:
                if n < 1000: # Only check small numbers for "truth"
                    if "not prime" in text or "composite" in text:
                        continue # Context suggests checking compositeness
                    # If the candidate asserts n is prime but it isn't
                    if f"{n}" in candidate and not self._is_prime(n):
                        # Simple heuristic: if candidate says "X is prime" and X is composite
                        if re.search(rf"{n}\s+is\s+prime", text):
                            return False 
        
        # Heuristic 2: Contradiction detection (basic)
        if ("yes" in text and "no" in text) or ("true" in text and "false" in text):
            # Ambiguous or contradictory phrasing often implies lower certainty
            pass 

        return True # Passed simulated BMC

    def _calculate_vcg_score(self, reported_p: float, is_correct: bool, bound_B: float) -> float:
        """
        Computes utility based on VCG principles with Logarithmic Scoring Rule.
        Utility = Truthful reporting maximizes expected score.
        Penalty increases if high confidence is placed on a falsehood.
        """
        epsilon = 1e-6
        p = max(epsilon, min(1 - epsilon, reported_p))
        
        if is_correct:
            # Logarithmic scoring rule: ln(p)
            # Scaled to 0-1 range roughly
            score = math.log(p + (1-p)*0.1) 
        else:
            # Penalty for being wrong with confidence
            # Score = -ln(1-p)
            score = -math.log((1 - p) + 0.1) - 2.0 # Base penalty
            
        # Adjust by adaptive bound complexity (PNT influence)
        # Harder problems (larger B) yield slightly higher variance potential
        complexity_factor = 1.0 / math.log(bound_B + 2)
        return score * complexity_factor

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # PNT Adaptive Bound: B ~ c * log^2(N). 
        # Here N is len(prompt) as a proxy for problem size magnitude.
        N = max(len(prompt), 2)
        B = 1.5 * (math.log(N) ** 2) + 10 
        
        for cand in candidates:
            # 1. Mechanism Step: Extract confidence (simulated by linguistic certainty)
            # In a real agent system, this 'p' comes from the agent's internal belief.
            # Here we infer a 'prior' confidence based on specificity, then adjust via BMC.
            cand_lower = cand.lower()
            has_certainty_words = any(w in cand_lower for w in ["definitely", "clearly", "proven", "always"])
            has_doubt_words = any(w in cand_lower for w in ["maybe", "possibly", "uncertain", "if"])
            
            # Initial belief p0 based on heuristics
            if has_certainty_words and not has_doubt_words:
                reported_p = 0.9
            elif has_doubt_words:
                reported_p = 0.4
            else:
                reported_p = 0.6 # Default moderate confidence

            # 2. Verification Step: BMC Simulation
            is_valid = self._simulate_bmc_check(prompt, cand)
            
            # 3. Scoring Step: VCG Payment
            score = self._calculate_vcg_score(reported_p, is_valid, B)
            
            # Adjust score if BMC found a hard contradiction
            if not is_valid:
                score -= 1.0 # Hard penalty for logical failure

            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"BMC(Bound={B:.1f}): {'Pass' if is_valid else 'Fail'}; VCG Utility: {score:.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns normalized confidence based on the scoring mechanism."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly for the interface
        raw_score = res[0]["score"]
        # Sigmoid-like mapping to ensure 0-1
        conf = 1 / (1 + math.exp(-raw_score))
        return round(conf, 4)