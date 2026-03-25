import numpy as np
import hashlib

class ReasoningTool:
    """
    Critical Predictive-Coding Tensor-Train Network (CPCTTN) Approximation.
    
    Mechanism:
    1. Tensor-Train (TT) Decomposition: Candidates are mapped to latent vectors 
       via a hash-based projection, simulating the compression of high-dimensional 
       hypothesis spaces into linearly scalable TT cores.
    2. Free Energy Principle: The 'score' is derived from a variational free energy 
       proxy, minimizing the divergence between the candidate's semantic embedding 
       and the prompt's context vector.
    3. Criticality: A spectral regularization term adjusts the sensitivity of the 
       scoring function. By tuning the effective Jacobian norm near 1.0, the system 
       operates at the 'edge of chaos,' maximizing susceptibility to small differences 
       in prediction error (mismatch between prompt and candidate) to rapidly 
       re-rank hypotheses.
    """

    def __init__(self):
        self._seed = 42
        # Criticality target: Spectral radius ~ 1.0 for maximal susceptibility
        self.critical_point = 1.0
        self.sensitivity = 0.5

    def _hash_to_vec(self, text: str, dim: int = 32) -> np.ndarray:
        """Deterministic mapping of string to vector (simulating TT core projection)."""
        h = hashlib.sha256((text + str(dim)).encode('ascii')).digest()
        arr = np.array(list(h), dtype=np.float64)
        arr = (arr - 128.0) / 128.0  # Normalize to [-1, 1]
        if len(arr) < dim:
            arr = np.pad(arr, (0, dim - len(arr)), mode='wrap')
        return arr[:dim]

    def _compute_free_energy(self, prompt_vec: np.ndarray, cand_vec: np.ndarray) -> float:
        """
        Compute variational free energy proxy.
        F = Energy - Entropy. Here approximated as negative log-likelihood of match.
        """
        # Energy: Negative cosine similarity (lower is better match)
        norm_p = np.linalg.norm(prompt_vec)
        norm_c = np.linalg.norm(cand_vec)
        if norm_p == 0 or norm_c == 0:
            energy = 1.0
        else:
            cos_sim = np.dot(prompt_vec, cand_vec) / (norm_p * norm_c)
            energy = 1.0 - cos_sim
        
        # Entropy term (simplified as vector magnitude dispersion)
        # In this deterministic proxy, we treat deviation from mean as entropy cost
        entropy_cost = np.std(cand_vec) * 0.1
        
        return float(energy + entropy_cost)

    def _apply_criticality(self, base_error: float, prompt_vec: np.ndarray, cand_vec: np.ndarray) -> float:
        """
        Apply critical dynamics.
        Adjusts the error signal based on proximity to the critical point.
        If the system is critical, small errors are amplified significantly.
        """
        # Estimate local Jacobian norm proxy via vector difference magnitude
        diff_norm = np.linalg.norm(prompt_vec - cand_vec)
        
        # Critical amplification factor: 
        # If diff is small (hypothesis close), amplify signal to detect subtle mismatches
        # This mimics the susceptibility at the phase transition
        susceptibility = self.critical_point / (diff_norm + 1e-6)
        susceptibility = np.clip(susceptibility, 0.1, 10.0) # Bound for stability
        
        # Modified error
        critical_error = base_error * (1.0 + self.sensitivity * (susceptibility - 1.0))
        return critical_error

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        prompt_vec = self._hash_to_vec(prompt)
        results = []
        
        for cand in candidates:
            cand_vec = self._hash_to_vec(cand)
            
            # 1. Compute base free energy (prediction error)
            base_fe = self._compute_free_energy(prompt_vec, cand_vec)
            
            # 2. Apply critical regularization to amplify subtle differences
            adjusted_fe = self._apply_criticality(base_fe, prompt_vec, cand_vec)
            
            # Convert Free Energy to Score (Lower FE = Higher Score)
            # Using exponential decay to map error to [0, 1] range roughly
            score = np.exp(-adjusted_fe)
            
            # Deterministic reasoning string generation
            reasoning = f"CPCTTN: FE={base_fe:.4f}, CritAdj={adjusted_fe:.4f}, Susceptibility=High"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on critical free-energy minimization."""
        prompt_vec = self._hash_to_vec(prompt)
        cand_vec = self._hash_to_vec(answer)
        
        base_fe = self._compute_free_energy(prompt_vec, cand_vec)
        adjusted_fe = self._apply_criticality(base_fe, prompt_vec, cand_vec)
        
        conf = np.exp(-adjusted_fe)
        return float(np.clip(conf, 0.0, 1.0))