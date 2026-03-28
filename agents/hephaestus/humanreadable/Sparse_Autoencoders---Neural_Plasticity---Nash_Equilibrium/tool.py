import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine combining Sparse Autoencoders, Neural Plasticity,
    and Nash Equilibrium scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic logical propositions (negations, comparatives, conditionals).
    2. Sparse Coding: Maps propositions to a sparse latent space via iterative shrinkage (ISTA).
    3. Plasticity: Updates the dictionary weights based on co-occurrence (Hebbian rule).
    4. Nash Scoring: Computes a payoff matrix based on semantic similarity and constraint 
       consistency, then solves for the mixed-strategy equilibrium to rank candidates.
    """
    
    def __init__(self):
        self.vocab_size = 500
        self.num_features = 64
        self.lambda_reg = 0.1
        self.eta = 0.01
        self.beta = 5.0
        self.max_iter = 50
        
        # Initialize dictionary D with random normal values, then normalize columns
        np.random.seed(42)
        self.D = np.random.randn(self.vocab_size, self.num_features)
        self.D = self.D / (np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-8)

    def _parse_propositions(self, text: str) -> List[int]:
        """Extract structural features and hash them to indices."""
        text_lower = text.lower()
        hashes = []
        
        # Patterns for structural logic
        patterns = [
            r'\b(not|no|never)\b', r'\b(if|then|else|unless)\b',
            r'\b(because|therefore|thus)\b', r'\b(and|or|but)\b',
            r'\b(more|less|greater|smaller|higher|lower)\b',
            r'\b(first|second|third|last)\b', r'\b(equal|same|different)\b'
        ]
        
        for pat in patterns:
            matches = re.findall(pat, text_lower)
            for m in matches:
                h = hash(m) % self.vocab_size
                hashes.append(h)
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', text)
        for n in nums:
            h = hash(f"NUM:{n}") % self.vocab_size
            hashes.append(h)
            
        return list(set(hashes))

    def _sparse_code(self, prop_indices: List[int]) -> np.ndarray:
        """Compute sparse code 'a' using ISTA."""
        if not prop_indices:
            return np.zeros(self.num_features)
            
        x = np.zeros(self.vocab_size)
        for idx in prop_indices:
            x[idx] = 1.0
            
        a = np.zeros(self.num_features)
        
        # ISTA steps
        for _ in range(self.max_iter):
            residual = x - self.D @ a
            gradient = self.D.T @ residual
            a = a + 0.1 * gradient
            # Soft thresholding
            a = np.sign(a) * np.maximum(np.abs(a) - self.lambda_reg, 0)
            
        return a

    def _hebbian_update(self, codes: List[np.ndarray]):
        """Update dictionary D based on co-occurrence of active features."""
        if len(codes) < 2:
            return
            
        # Aggregate outer products approx
        delta_D = np.zeros_like(self.D)
        for a in codes:
            # Hebbian rule: strengthen connections where pre and post are active
            # Simplified: Delta D ~ eta * (a a^T) D
            update = np.outer(a, a) @ self.D.T
            delta_D += update
            
        self.D += self.eta * delta_D
        # Renormalize columns
        norms = np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-8
        self.D /= norms

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """Penalty for violating logical constraints detected in prompt."""
        penalty = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Check negation consistency
        if re.search(r'\bnot\s+all\b', p_low) and re.search(r'\ball\b', c_low) and not re.search(r'\bnot\b', c_low):
            penalty += 0.5
            
        # Check numeric consistency (simplified)
        p_nums = re.findall(r'\d+\.?\d*', p_low)
        c_nums = re.findall(r'\d+\.?\d*', c_low)
        
        if p_nums and c_nums:
            try:
                # If prompt says A > B and candidate implies A < B
                # This is a heuristic check for direct contradiction
                if len(p_nums) >= 2 and len(c_nums) >= 2:
                    p_val = float(p_nums[-1])
                    c_val = float(c_nums[-1])
                    # Rough heuristic: if candidate number is wildly different from prompt context
                    if abs(p_val - c_val) > 10 * (p_val + 1e-6): 
                        penalty += 0.2
            except ValueError:
                pass
                
        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse and Encode
        codes = []
        constraints = []
        for c in candidates:
            props = self._parse_propositions(prompt + " " + c)
            code = self._sparse_code(props)
            codes.append(code)
            constraints.append(self._check_constraints(prompt, c))
            
        codes = np.array(codes)
        
        # 2. Hebbian Plasticity Update
        self._hebbian_update(codes)
        
        # 3. Nash Equilibrium Scoring
        n = len(candidates)
        P = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                # Similarity payoff
                sim = np.dot(codes[i], codes[j])
                # Penalty for constraint violations (self-consistency check primarily)
                # In a game, P_ij is payoff to i when playing against j.
                # We penalize if candidate i violates constraints relative to prompt logic
                penalty_i = constraints[i] 
                P[i, j] = sim - penalty_i * 10.0 # Scale penalty
                
        # Best-response dynamics to find equilibrium
        p = np.ones(n) / n # Initial mixed strategy
        
        for _ in range(20): # Iterations to converge
            exp_payoffs = np.exp(self.beta * (P @ p))
            p = exp_payoffs / (np.sum(exp_payoffs) + 1e-9)
            
        scores = p.tolist()
        
        # Sort by score descending
        results = []
        for i, score in enumerate(scores):
            results.append({
                "candidate": candidates[i],
                "score": float(score),
                "reasoning": f"Sparse-Nash score based on logical consistency and feature alignment."
            })
            
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly based on equilibrium probability
        # Since sum(p) = 1, and we only have one candidate here, p=1.0 technically.
        # We need to evaluate against a dummy 'wrong' answer to get relative confidence.
        # However, per interface, we return the score from the single evaluation if possible,
        # but the Nash score depends on the set. 
        # Fallback: Use the internal score logic directly.
        
        # Re-run evaluation with a dummy competitor to force a distribution
        dummy = "This is incorrect."
        full_res = self.evaluate(prompt, [answer, dummy])
        
        # Find the score for the specific answer
        for item in full_res:
            if item['candidate'] == answer:
                return min(1.0, max(0.0, item['score']))
        return 0.0