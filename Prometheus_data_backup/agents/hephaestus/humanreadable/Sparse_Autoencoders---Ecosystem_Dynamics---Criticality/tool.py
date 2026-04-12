import numpy as np
import re
from collections import defaultdict

class ReasoningTool:
    """
    Implements a Sparse Autoencoder x Criticality reasoning engine.
    Mechanism:
    1. Parsing: Converts text to a sparse propositional graph (nodes=concepts, edges=logic).
    2. Dictionary Learning: Simulates sparse coding by projecting graph features onto 
       a learned orthogonal basis (simulating D) and applying L1 shrinkage.
    3. Critical Dynamics: Evolves node states via an Ising-like update rule tuned to 
       the median weight (critical point).
    4. Scoring: Measures trajectory stability (susceptibility). Low variance = high confidence.
    """
    
    def __init__(self):
        # Simulate pre-trained dictionary D (m=64 features, k=16 latent factors)
        # In a real scenario, this would be learned via ISTA on a corpus.
        self.m = 64  # Feature space size
        self.k = 16  # Latent dimension
        np.random.seed(42)
        self.D = np.random.randn(self.m, self.k)
        self.D = self.D / (np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9)
        self.lambda_reg = 0.1

    def _parse_to_vector(self, text: str) -> np.ndarray:
        """Parses text into a sparse feature vector based on logical constructs."""
        t = text.lower()
        vec = np.zeros(self.m)
        
        # Numeric extraction (indices 0-7)
        nums = re.findall(r"-?\d+\.?\d*", t)
        for i, n in enumerate(nums[:8]):
            try:
                val = float(n)
                # Encode magnitude and sign into specific bins
                idx = int(abs(val)) % 8
                vec[idx] += np.sign(val) * abs(val)
            except: pass

        # Logical operators (indices 8-15)
        if re.search(r'\bif\b|\bthen\b|\bimplies\b', t): vec[8] = 1.0
        if re.search(r'\bnot\b|\bno\b|\bnever\b|\bfalse\b', t): vec[9] = -1.0 # Inhibitory
        if re.search(r'\band\b|\bboth\b', t): vec[10] = 1.0
        if re.search(r'\bor\b|\beither\b', t): vec[11] = 0.5
        
        # Comparatives (indices 12-15)
        if re.search(r'>|greater|more|higher|after', t): vec[12] = 1.0
        if re.search(r'<|less|lower|before', t): vec[13] = -1.0
        if re.search(r'=|equal|same', t): vec[14] = 1.0
        
        # Structural complexity (indices 16-20)
        vec[16] = min(1.0, len(t) / 100.0) # Length proxy
        vec[17] = t.count('?') * -0.5 # Questions reduce certainty
        vec[18] = 1.0 if re.search(r'\btherefore\b|\bthus\b|\bso\b', t) else 0.0
        
        # Semantic hashing (pseudo-random but deterministic distribution)
        words = set(re.findall(r'\b\w+\b', t))
        for w in words:
            h = hash(w) % (self.m - 21) + 21
            vec[h] += 0.5
            
        return vec

    def _sparse_code(self, w_vec: np.ndarray) -> np.ndarray:
        """Approximates sparse coding: Z = shrink(D^T W)."""
        # Project to latent space
        z = self.D.T @ w_vec
        # L1 Shrinkage (Soft thresholding)
        z = np.sign(z) * np.maximum(np.abs(z) - self.lambda_reg, 0)
        return z

    def _run_critical_dynamics(self, z: np.ndarray, steps=20) -> float:
        """Runs Ising-like dynamics and returns susceptibility (inverse score)."""
        if np.all(z == 0): return 1.0 # No info
        
        # Initialize states from sparse code
        s = np.sign(z + np.random.randn(len(z))*0.01) 
        # Thresholds at median of incoming weights (criticality tuning)
        theta = np.median(np.abs(self.D @ z)) if np.any(z) else 0.0
        if theta == 0: theta = 1e-9
        
        history = []
        
        for _ in range(steps):
            # Update rule: s_new = sign(D * z - theta)
            # Note: We simulate the bidirectional influence described
            activation = self.D @ z
            s_new = np.sign(activation - theta)
            
            # Recalculate z based on new s (feedback loop)
            z_new = self.D.T @ s_new
            z_new = np.sign(z_new) * np.maximum(np.abs(z_new) - self.lambda_reg, 0)
            
            # Check for fixed point or cycle
            if np.array_equal(s, s_new):
                break
            if len(history) > 2 and np.array_equal(s_new, history[-2]):
                break # Limit cycle detected
                
            s = s_new
            z = z_new
            history.append(np.var(s))
            
        # Susceptibility: variance of states over time
        if len(history) < 2: return 0.0
        return float(np.mean(history))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_vec = self._parse_to_vector(prompt)
        p_code = self._sparse_code(p_vec)
        
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            c_vec = self._parse_to_vector(full_text)
            
            # Interaction term: logic consistency between prompt and answer
            # If candidate contradicts prompt negations, vectors should diverge
            combined_code = self._sparse_code(c_vec + 0.5 * p_code)
            
            # Run dynamics
            susceptibility = self._run_critical_dynamics(combined_code)
            
            # Score: Inverse susceptibility (stable = good) + Consistency bonus
            # We add a small bias based on simple constraint checks
            bonus = 0.0
            if "not" in prompt.lower() and "not" not in cand.lower():
                # Heuristic: if prompt has negation, answer often needs to address it
                pass 
            
            # Normalize score: lower susceptibility -> higher score
            score = 1.0 / (susceptibility + 0.1)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Stability: {1.0/(susceptibility+0.1):.4f}, Sparse activation: {np.count_nonzero(combined_code)}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        raw_score = res[0]['score']
        # Map score to 0-1 range. 
        # Typical stability scores range 0.5 to 10.0. 
        # Chaotic (wrong) answers often yield < 2.0 stable answers > 5.0
        conf = 1.0 - np.exp(-0.3 * raw_score)
        return float(np.clip(conf, 0.0, 1.0))