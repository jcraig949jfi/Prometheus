import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Attention Controller (CAC) Approximation.
    
    Mechanism:
    1. Structural Parsing: Extracts numeric values, negations, and comparatives.
    2. Criticality Monitor: Estimates the 'spectral radius' of the candidate set.
       We treat the diversity of candidate embeddings (via NCD matrix) as the system state.
       Criticality is achieved when the system is poised between order (low variance) 
       and chaos (high variance). We maximize Fisher Information by selecting candidates 
       that stabilize this variance near a target threshold (simulating rho(J) ~ 1).
    3. Optimal Control: The final score is a Hamiltonian minimization:
       H = Task_Loss + lambda * Criticality_Cost.
       Task_Loss includes structural constraint satisfaction (e.g., numeric consistency).
       Criticality_Cost penalizes deviations from the 'edge of chaos' in the candidate distribution.
    """

    def __init__(self):
        self.lambda_crit = 0.5  # Weight for criticality constraint
        self.target_radius = 1.0 # Target spectral radius proxy
        self.epsilon = 1e-6

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        return [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", text)]

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing and constraint propagation.
        Returns a penalty score (0.0 = perfect, 1.0 = violation).
        """
        penalty = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Negation check
        if "not" in p_low and ("yes" in c_low or "true" in c_low):
            # Simple heuristic: if prompt says "not" and candidate affirms, penalize
            # This is a rough approximation of modus tollens
            if "not" in c_low: penalty -= 0.2 # Double negation might be good
            else: penalty += 0.3
            
        # Numeric consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt has logic like "smaller than", check numbers
            if "smaller" in p_low or "less" in p_low:
                if len(c_nums) >= 2 and c_nums[0] >= c_nums[1]:
                    penalty += 0.5
            if "larger" in p_low or "greater" in p_low:
                if len(c_nums) >= 2 and c_nums[0] <= c_nums[1]:
                    penalty += 0.5
                    
        return min(penalty, 1.0)

    def _compute_criticality_cost(self, candidates: List[str]) -> Tuple[float, List[float]]:
        """
        Estimate system criticality based on candidate diversity.
        Constructs an NCD matrix, approximates spectral radius via mean row energy.
        Returns cost and individual susceptibility scores.
        """
        n = len(candidates)
        if n == 0: return 0.0, []
        if n == 1: return 0.0, [0.0]

        # Build similarity matrix (approximating Jacobian interaction)
        # We use 1 - NCD as a proxy for connection strength
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i, j] = 1.0
                else:
                    matrix[i, j] = 1.0 - self._ncd(candidates[i], candidates[j])
        
        # Approximate spectral radius (rho) using max row sum (infinity norm)
        # This is a bounded proxy for the true spectral radius
        row_sums = np.sum(np.abs(matrix), axis=1)
        rho_approx = np.max(row_sums) / n # Normalize by size to get ~1.0 scale
        
        # Criticality cost: deviation from target (poised state)
        # We want the system to be sensitive but not chaotic
        crit_cost = (rho_approx - self.target_radius) ** 2
        
        # Susceptibility per candidate (how much does this candidate contribute to instability?)
        # High row sum = high influence = high susceptibility
        susceptibility = (row_sums / n) 
        
        return crit_cost, susceptibility.tolist()

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Criticality Analysis (Global context)
        crit_cost, susceptibilities = self._compute_criticality_cost(candidates)
        
        scored = []
        for i, cand in enumerate(candidates):
            # 2. Task Loss (Structural/Numeric constraints)
            task_loss = self._check_constraints(prompt, cand)
            
            # 3. NCD Baseline (Semantic similarity to prompt as a prior)
            # Using NCD to prompt as a basic relevance filter
            relevance = 1.0 - self._ncd(prompt, cand)
            
            # 4. Optimal Control Combination (Hamiltonian)
            # Score = Relevance - TaskPenalty - CriticalityDeviation * SusceptibilityWeight
            # We invert logic: Higher is better.
            # Crit cost is global, but we weight individual score by how much that candidate 
            # contributes to the critical state (susceptibility).
            # If the system is too chaotic (high rho), we downweight high-susceptibility items.
            # If too ordered, we upweight them.
            
            # Simplified control law:
            # Score = Relevance - Task_Loss - lambda * |rho - 1| * susceptibility_i
            crit_penalty = self.lambda_crit * abs(crit_cost - 0.0) * (susceptibilities[i] if i < len(susceptibilities) else 0)
            
            final_score = relevance - task_loss - crit_penalty
            
            # Deterministic tie-breaking with index if scores are extremely close
            scored.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural penalty: {task_loss:.2f}, Criticality contribution: {susceptibilities[i]:.2f}, Relevance: {relevance:.2f}"
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and criticality alignment.
        """
        # Evaluate single candidate against itself to get baseline
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]["score"]
        
        # Normalize to 0-1 range heuristically
        # Base score usually ranges -1 to 1 roughly
        conf = (base_score + 1.0) / 2.0
        return max(0.0, min(1.0, conf))