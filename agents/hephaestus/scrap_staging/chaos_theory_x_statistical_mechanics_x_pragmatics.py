import numpy as np
import re
from math import log, exp

class ReasoningTool:
    """
    A reasoning tool combining Chaos Theory (Lyapunov exponents), 
    Statistical Mechanics (Free Energy), and Pragmatics (Gricean maxims)
    to evaluate logical coherence of candidate answers.
    
    Mechanism:
    1. Parses propositions (negations, comparatives, conditionals) from text.
    2. Constructs a logical weight matrix W and bias vector b.
    3. Simulates deterministic dynamics (Hopfield-like) to find stable states.
    4. Computes Lyapunov exponent (sensitivity) and Energy (constraint violations).
    5. Scores based on Free Energy relative to a reference.
    """
    
    def __init__(self):
        self.T_steps = 20
        self.Temp = 0.5
        self.w_imp = 2.0
        self.w_and = 1.5
        self.w_neg = 2.0
        self.w_grice = 1.0

    def _parse_props(self, text: str):
        """Extract structural features and return props list, W, b, c."""
        text_lower = text.lower()
        props = []
        M = 0
        
        # Simple regex extractors
        negs = re.findall(r'\b(not|no|never)\b', text_lower)
        comps = re.findall(r'\b(greater|less|more|fewer)\b', text_lower)
        conds = re.findall(r'\b(if|unless|then)\b', text_lower)
        nums = re.findall(r'\d+\.?\d*', text_lower)
        
        # Assign IDs to detected features
        def add_prop(t, typ):
            nonlocal M
            props.append({'id': M, 'text': t, 'type': typ})
            M += 1
            return M - 1
            
        for _ in negs: add_prop("neg", "neg")
        for _ in comps: add_prop("comp", "comp")
        for _ in conds: add_prop("cond", "cond")
        for _ in nums: add_prop("num", "num")
        
        # Ensure at least one proposition to avoid empty matrix
        if M == 0:
            add_prop("default", "num")
            M = 1
            
        W = np.zeros((M, M))
        b = np.zeros(M)
        c = np.zeros(M)
        
        # Populate W and b based on logical heuristics
        # Negation penalty
        for i, p in enumerate(props):
            if p['type'] == 'neg':
                b[i] = -self.w_neg
            elif p['type'] == 'num':
                c[i] = 0.5 # Context strength for numbers
        
        # Logical coupling heuristics
        if len(props) > 1:
            # If conditionals exist, couple them to implications
            cond_ids = [i for i, p in enumerate(props) if p['type'] == 'cond']
            other_ids = [i for i, p in enumerate(props) if p['type'] != 'cond']
            
            for ci in cond_ids:
                for oi in other_ids:
                    W[ci, oi] = self.w_imp * 0.5 # Weak implication
            
            # Transitivity-like coupling for comparatives
            comp_ids = [i for i, p in enumerate(props) if p['type'] == 'comp']
            for i in range(len(comp_ids)-1):
                idx1, idx2 = comp_ids[i], comp_ids[i+1]
                W[idx1, idx2] = self.w_and
                W[idx2, idx1] = self.w_and
                
        return props, W, b, c

    def _dynamics(self, W, b, c, x0):
        """Run deterministic discrete-time dynamics."""
        x = x0.astype(float)
        history = [x.copy()]
        
        for _ in range(self.T_steps):
            z = W @ x + b + c
            x_new = 1.0 / (1.0 + np.exp(-z)) # Sigmoid
            x = (x_new > 0.5).astype(float)
            history.append(x.copy())
            
        return history

    def _compute_lyapunov(self, W, b, c, x0):
        """Approximate largest Lyapunov exponent."""
        eps = 1e-3
        x_prime = x0.copy().astype(float)
        # Perturb first element if possible, else random
        if len(x_prime) > 0:
            x_prime[0] = (x_prime[0] + eps) % 2.0 
        else:
            return 0.0
            
        hist_orig = self._dynamics(W, b, c, x0)
        hist_pert = self._dynamics(W, b, c, x_prime)
        
        dists = []
        T_eff = min(len(hist_orig), len(hist_pert))
        
        for t in range(T_eff):
            d = np.linalg.norm(hist_orig[t] - hist_pert[t], ord=1)
            if d > 1e-10:
                dists.append(d)
        
        if len(dists) < 2:
            return 0.0
            
        # Approximate lambda
        lyap_sum = 0.0
        count = 0
        for i in range(len(dists)-1):
            if dists[i] > 1e-10:
                ratio = dists[i+1] / dists[i]
                if ratio > 0:
                    lyap_sum += log(ratio)
                    count += 1
                    
        return lyap_sum / count if count > 0 else 0.0

    def _compute_energy(self, x, props, W, b):
        """Compute energy based on violated constraints."""
        E = 0.0
        M = len(x)
        if M == 0: return 0.0
        
        # Penalty for active negations
        for i, p in enumerate(props):
            if p['type'] == 'neg' and x[i] == 1:
                E += self.w_neg
                
        # Penalty for inconsistent weights (simple Ising-like)
        # If W[i,j] > 0, we prefer x[i]==x[j]. Violation adds energy.
        for i in range(M):
            for j in range(M):
                if W[i,j] > 0 and x[i] != x[j]:
                    E += W[i,j] * 0.5
                    
        return E

    def _sample_ensemble(self, x_final, W, b, c, n_samples=50):
        """Monte Carlo sampling around final state."""
        M = len(x_final)
        if M == 0: return 0.0
        
        energies = []
        for _ in range(n_samples):
            # Flip random bits with probability 0.2
            noise = np.random.rand(M) < 0.2
            x_sample = (x_final.copy() ^ noise).astype(float)
            # We need props for energy calc, but we don't have full list here.
            # Simplified energy: just constraint violation count on sample
            E = 0.0
            for i in range(M):
                for j in range(M):
                    if W[i,j] > 0 and x_sample[i] != x_sample[j]:
                        E += W[i,j]
            energies.append(E)
            
        # Free energy approximation F = -T log(Z)
        # Z approx sum(exp(-E/T))
        Z = sum(exp(-E / self.Temp) for E in energies)
        F = -self.Temp * log(Z + 1e-10)
        return F

    def _score_candidate(self, prompt: str, candidate: str):
        full_text = f"{prompt} {candidate}"
        props, W, b, c = self._parse_props(full_text)
        M = len(props)
        if M == 0: return 0.0, "No propositions"
        
        # Initial state: all true (optimistic)
        x0 = np.ones(M)
        
        # Run dynamics
        history = self._dynamics(W, b, c, x0)
        x_final = history[-1]
        
        # Chaos metric
        lyap = self._compute_lyapunov(W, b, c, x0)
        
        # Stats Mech metric
        F = self._sample_ensemble(x_final, W, b, c)
        
        # Pragmatics: Penalty if length is too short (Grice: Quantity)
        if len(candidate.split()) < 2:
            F += self.w_grice
            
        # Score: Lower Free Energy and Lower Lyapunov (stability) is better
        # We invert so higher is better. 
        # Base score 1.0, subtract penalties.
        raw_score = 1.0 / (1.0 + F + max(0, lyap))
        
        reason = f"Lyap={lyap:.3f}, FreeE={F:.3f}, Stable={x_final.sum()}/{M}"
        return raw_score, reason

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        scores = []
        
        # Compute scores
        for cand in candidates:
            sc, reason = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": sc, "reasoning": reason})
            scores.append(sc)
        
        # Normalize scores to 0-1 range for better interpretability if needed,
        # but the prompt asks for ranking. We keep raw scores but ensure ranking.
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        sc, _ = self._score_candidate(prompt, answer)
        # Map score to 0-1. Since raw score is ~1/(1+E), it's already bounded (0,1] roughly.
        # Clamp to [0, 1]
        return float(np.clip(sc, 0.0, 1.0))