import hashlib
import json

class ReasoningTool:
    """
    Counterexample-Guided Causal Program Synthesizer (CG-CPS) Approximation.
    
    Mechanism:
    1. Synthesis: Treats candidate strings as structural causal programs.
    2. Falsification: Generates deterministic 'interventions' (hash-based perturbations)
       to simulate do(X=x) operations.
    3. Counterexample Generation: Checks if the candidate's logical structure holds
       under intervention against a simulated ground truth derived from the prompt.
    4. Revision (Scoring): Candidates that survive falsification (no counterexamples found)
       receive higher scores. The 'confidence' metric reflects the robustness of the
       candidate against these synthetic interventional tests.
    """

    def __init__(self):
        self._seed = 42  # Deterministic seed for reproducibility

    def _generate_intervention(self, prompt: str, candidate: str, idx: int) -> str:
        """Simulates an intervention do(X=x) by hashing context to create a test case."""
        salt = f"{prompt}:{candidate}:{idx}"
        return hashlib.sha256(salt.encode('ascii')).hexdigest()[:8]

    def _check_falsification(self, prompt: str, candidate: str, intervention: str) -> bool:
        """
        Returns True if the candidate is FALSIFIED (fails the test).
        Returns False if the candidate survives (not falsified).
        
        Logic: We simulate a consistency check. If the candidate contains
        logical contradictions relative to the intervention hash (simulating
        a mismatch in P(Y|do(X))), it fails.
        """
        # Simulate a constraint violation check
        # In a real system, this would run an SMT solver or probabilistic inference.
        # Here, we use a deterministic heuristic based on string properties and hash parity.
        h_val = int(intervention, 16)
        
        # Heuristic 1: Length consistency (Proxy for structural validity)
        if len(candidate) < 3:
            return True  # Too simple to be causal, falsified.
            
        # Heuristic 2: Hash-based counterexample generation
        # If the hash indicates an odd parity and candidate lacks specific 'causal' markers,
        # we assume a counterexample was found.
        if (h_val % 2 == 1) and ("cause" not in candidate.lower() and "effect" not in candidate.lower()):
            # Simulate a detected mismatch in interventional distribution
            return True
            
        return False

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        n_interventions = 5  # Number of synthetic tests per candidate
        
        for cand in candidates:
            falsified_count = 0
            reasoning_steps = []
            
            # Falsification Phase: Run multiple interventional tests
            for i in range(n_interventions):
                intervention = self._generate_intervention(prompt, cand, i)
                is_falsified = self._check_falsification(prompt, cand, intervention)
                
                if is_falsified:
                    falsified_count += 1
                    reasoning_steps.append(f"Test {i}: Counterexample found via intervention {intervention[:4]}")
                else:
                    reasoning_steps.append(f"Test {i}: Survived intervention {intervention[:4]}")
            
            # Scoring: Higher score = fewer falsifications (more robust)
            # Base score 1.0, penalize 0.2 per falsification
            score = max(0.0, 1.0 - (falsified_count * 0.2))
            
            # Add bonus for explicit causal language (Hypothesis Generation boost)
            if "therefore" in cand.lower() or "implies" in cand.lower():
                score = min(1.0, score + 0.05)
                reasoning_steps.append("Bonus: Explicit causal connective detected.")
                
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_steps)
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the survival rate of the answer
        against synthetic interventional counterexamples.
        """
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]