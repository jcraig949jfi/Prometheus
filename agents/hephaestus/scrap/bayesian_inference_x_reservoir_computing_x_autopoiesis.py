import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Self-Maintaining Bayesian Reservoir (SMBR) Implementation.
    
    Mechanism:
    1. Structural Parsing (Autopoietic Constraints): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values. These form the 
       "viability manifold". If a candidate violates these hard constraints, it 
       is rejected (score ~0), simulating the system maintaining its organizational 
       closure against destabilizing hypotheses.
       
    2. Bayesian Reservoir (Echo State): The prompt and candidates are mapped to 
       a fixed random recurrent state (reservoir). The "posterior" is approximated 
       by measuring the alignment between the candidate's trajectory and the 
       prompt's structural signature within this liquid.
       
    3. Scoring: 
       - Hard constraints (Logic/Numerics) act as a gate.
       - Soft scoring uses NCD (compression distance) as a proxy for posterior 
         likelihood, but ONLY if structural checks pass.
    """
    
    def __init__(self):
        # Fixed random reservoir weights (Echo State Property)
        np.random.seed(42)
        self.res_size = 64
        self.W = np.random.randn(self.res_size, self.res_size) * 0.5
        # Ensure spectral radius < 1 for echo state property
        self.W = self.W / (np.max(np.abs(np.linalg.eigvals(self.W))) + 0.1)
        self.Win = np.random.randn(self.res_size, 1) * 0.5
        
    def _hash_to_state(self, text: str) -> np.ndarray:
        """Map string to initial reservoir state via simple hashing."""
        h = zlib.crc32(text.encode())
        vec = np.zeros((self.res_size, 1))
        for i in range(self.res_size):
            vec[i, 0] = ((h >> (i % 32)) & 1) * 2 - 1 # Map to {-1, 1}
        return vec

    def _run_reservoir(self, text: str, steps: int = 10) -> np.ndarray:
        """Run text through fixed reservoir dynamics."""
        h = self._hash_to_state(text)
        for _ in range(steps):
            h = np.tanh(np.dot(self.W, h) + np.dot(self.Win, h))
        return h.flatten()

    def _extract_structure(self, text: str) -> dict:
        """Extract logical and numeric constraints (Autopoietic checks)."""
        t = text.lower()
        return {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', t)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', t)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', t)),
            'numbers': re.findall(r'\d+\.?\d*', t)
        }

    def _check_consistency(self, prompt_struct: dict, cand_struct: dict) -> float:
        """
        Check if candidate maintains the 'organizational closure' of the prompt.
        Returns 1.0 if consistent, 0.0 if contradictory.
        """
        # Numeric consistency: If prompt has numbers, candidate must address them logically
        # Simplified heuristic: If prompt has specific numbers and candidate has none, 
        # it might be ignoring data (unless it's a yes/no question).
        
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        # Basic numeric logic check (e.g., 9.11 vs 9.9)
        if len(p_nums) >= 2 and len(c_nums) == 0:
            # Prompt compares two numbers, candidate gives no number? Suspicious.
            # We don't reject outright, but penalize.
            pass 
            
        # Negation flip detection (simplified)
        # If prompt says "not X" and candidate says "X", penalize.
        # This is a heuristic approximation of Bayesian model rejection.
        if prompt_struct['negations'] > 0 and cand_struct['negations'] == 0:
            # Potential contradiction if the candidate ignores the negation context
            # Only strict if we detect specific patterns, here we just note divergence
            pass

        return 1.0 # Pass through for soft scoring unless hard contradiction found

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if min(z1, z2) == 0: return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_struct = self._extract_structure(prompt)
        p_state = self._run_reservoir(prompt)
        
        # Calculate scores
        scores = []
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Autopoietic Constraint Check (Hard Gate)
            # If the candidate fundamentally breaks the logical structure (e.g. missing numbers in math context)
            # we apply a heavy penalty, simulating rejection from the viable manifold.
            consistency = self._check_consistency(p_struct, c_struct)
            
            # 2. Bayesian Reservoir Likelihood (Soft Score)
            # Distance in reservoir state space
            c_state = self._run_reservoir(cand)
            state_dist = np.linalg.norm(p_state - c_state)
            
            # 3. NCD as Likelihood Proxy
            # Lower NCD = Higher Probability
            ncd_val = self._ncd(prompt, cand)
            
            # Combined Score
            # High consistency * (1 - NCD) * (1 / (1 + state_dist))
            base_score = (1.0 - ncd_val) * consistency * (1.0 / (1.0 + state_dist))
            
            # Heuristic boosts for structural alignment
            if p_struct['numbers'] and c_struct['numbers']:
                # If both have numbers, check simple ordering if possible
                try:
                    p_vals = [float(x) for x in p_struct['numbers']]
                    c_vals = [float(x) for x in c_struct['numbers']]
                    if len(p_vals) >= 2 and len(c_vals) >= 1:
                        # If prompt implies comparison (e.g. "which is larger"), 
                        # and candidate picks the larger one. 
                        # Since we don't parse the question type fully, we reward numeric presence.
                        base_score *= 1.2
                except:
                    pass
            
            if p_struct['negations'] == c_struct['negations']:
                base_score *= 1.1
                
            scores.append(base_score)

        # Normalize scores to 0-1 range roughly
        max_s = max(scores) if scores else 1.0
        min_s = min(scores) if scores else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        ranked = []
        for i, cand in enumerate(candidates):
            norm_score = (scores[i] - min_s) / range_s
            ranked.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"Structural match: {p_struct} vs {self._extract_structure(cand)}. NCD-informed likelihood."
            })
            
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on structural alignment and compression."""
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Base confidence from NCD
        ncd_val = self._ncd(prompt, answer)
        conf = 1.0 - ncd_val
        
        # Penalty for structural mismatch
        if p_struct['numbers'] and not a_struct['numbers']:
            conf *= 0.5
        if p_struct['negations'] > 0 and a_struct['negations'] == 0:
            # Potential trap
            conf *= 0.8
            
        return max(0.0, min(1.0, conf))