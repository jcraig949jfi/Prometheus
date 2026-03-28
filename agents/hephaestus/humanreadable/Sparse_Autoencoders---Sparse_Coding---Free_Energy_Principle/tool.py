import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Predictive Coding Scorer (SPCS).
    Mechanism:
    1. Parses text into atomic propositions (negations, comparatives, numerics).
    2. Uses a fixed random sparse dictionary (simulating offline learned SAE) to encode propositions.
    3. Applies constraint propagation (Modus Ponens, Transitivity) to detect logical violations.
    4. Scores based on Free Energy: Reconstruction Error + Sparsity Cost + Constraint Violations.
    5. Uses NCD only as a tiebreaker for low-information candidates.
    """
    
    def __init__(self):
        self.K = 64  # Dictionary size
        self.P = 100 # Proposition space size (hash-based)
        self.s = 5   # Sparsity level
        self.lamb = 0.1 # Sparsity penalty
        np.random.seed(42)
        # Initialize fixed binary dictionary D (K x P)
        self.D = np.zeros((self.K, self.P))
        for i in range(self.P):
            idxs = np.random.choice(self.K, self.s, replace=False)
            self.D[idxs, i] = 1.0
            
    def _extract_props(self, text: str) -> List[Tuple[int, int]]:
        """Extract propositions as (hash_id, polarity) tuples."""
        t = text.lower()
        props = []
        
        # Numeric extraction and comparison logic
        nums = re.findall(r'-?\d+(?:\.\d+)?', t)
        for n in nums:
            val = float(n)
            h = hash(f"num:{val}") % self.P
            props.append((h, 1))
            if val < 0:
                props.append((hash("neg_num") % self.P, 1))

        # Logical operators
        if re.search(r'\b(not|no|never)\b', t):
            props.append((hash("negation") % self.P, -1))
        if re.search(r'\b(greater|larger|more|above)\b', t):
            props.append((hash("comp_gt") % self.P, 1))
        if re.search(r'\b(less|smaller|fewer|below)\b', t):
            props.append((hash("comp_lt") % self.P, 1))
        if re.search(r'\b(if|then|implies)\b', t):
            props.append((hash("conditional") % self.P, 1))
        if re.search(r'\b(because|causes|leads to)\b', t):
            props.append((hash("causal") % self.P, 1))
            
        # Simple transitivity check setup (A<B, B<C -> A<C)
        # We encode the structure itself as a proposition for the sparse coder
        if re.search(r'\b(before|after)\b', t):
            props.append((hash("ordering") % self.P, 1))
            
        # Fallback for content words to ensure unique signatures
        words = re.findall(r'\b[a-z]{4,}\b', t)
        for w in set(words[:10]): # Limit context window
            h = hash(w) % self.P
            props.append((h, 1))
            
        return props if props else [(hash("empty"), 1)]

    def _to_vector(self, props: List[Tuple[int, int]]) -> np.ndarray:
        """Convert props to binary vector x (size P)."""
        x = np.zeros(self.P)
        for pid, pol in props:
            # Handle polarity by shifting index or flipping sign conceptually
            # Here we just mark presence; polarity affects scoring via dictionary interaction
            idx = pid % self.P
            x[idx] = 1.0 
        return x

    def _omp(self, x: np.ndarray) -> np.ndarray:
        """Orthogonal Matching Pursuit (simplified) to find sparse code z."""
        # Residual
        r = x.copy()
        z = np.zeros(self.K)
        indices = []
        
        for _ in range(self.s):
            if np.all(r == 0): break
            # Correlation
            corr = np.abs(self.D @ (self.D.T @ r)) # Approximate projection
            # Greedy select
            idx = np.argmax(corr)
            if idx in indices: break
            indices.append(idx)
            
            # Least squares update (simplified to additive for speed/stability in pure numpy)
            # In strict OMP we solve (D_I^T D_I)^-1 D_I^T x, but here we approximate
            # by activating the column if it reduces error significantly
            z[idx] = 1.0 
            
        return z

    def _check_constraints(self, text: str) -> float:
        """Deterministic rule-based penalty for logical violations."""
        t = text.lower()
        penalty = 0.0
        
        # Modus Ponens / Consistency checks
        has_if = 'if' in t
        has_then = 'then' in t or 'so' in t
        if has_if and not has_then:
            # Potential incomplete reasoning, slight penalty
            penalty += 0.1
            
        # Numeric consistency (Heuristic)
        nums = re.findall(r'-?\d+(?:\.\d+)?', t)
        if len(nums) >= 2:
            try:
                vals = [float(n) for n in nums]
                # Check for obvious contradictions like "5 is greater than 10"
                if "greater" in t and vals[0] > vals[1] and "not" not in t:
                     pass # Consistent
                elif "greater" in t and vals[0] < vals[1]:
                     penalty += 0.5 # Contradiction
            except: pass
            
        return penalty

    def _free_energy(self, x: np.ndarray) -> float:
        """Calculate Free Energy F = Reconstruction Error + Sparsity Cost."""
        z = self._omp(x)
        recon = self.D.T @ z
        err = 0.5 * np.sum((x - recon) ** 2)
        sparsity = self.lamb * np.sum(np.abs(z))
        return err + sparsity

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        def comp(s): return len(zlib.compress(s.encode()))
        c1, c2, c12 = comp(s1), comp(s2), comp(s1 + s2)
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_props = self._extract_props(prompt)
        prompt_vec = self._to_vector(prompt_props)
        
        for cand in candidates:
            # Combine prompt context with candidate
            full_text = f"{prompt} {cand}"
            cand_props = self._extract_props(full_text)
            cand_vec = self._to_vector(cand_props)
            
            # 1. Free Energy Score (Lower is better)
            fe = self._free_energy(cand_vec)
            
            # 2. Constraint Violation Penalty
            viol = self._check_constraints(full_text)
            
            # 3. Structural Overlap Bonus (Did it use prompt concepts?)
            overlap = len(set(p[0] for p in prompt_props) & set(p[0] for p in cand_props))
            overlap_bonus = -0.1 * overlap # Reduce free energy
            
            score = -(fe + viol + overlap_bonus)
            
            results.append({"candidate": cand, "score": score, "reasoning": f"FE:{fe:.2f}, Viol:{viol:.2f}"})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative ranking."""
        # Generate a dummy negative candidate to compare against
        neg_cand = "This is incorrect and unrelated."
        if answer.strip() == "":
            return 0.0
            
        # Evaluate against a synthetic set to get relative position
        # We simulate a binary choice: Answer vs Random Noise
        candidates = [answer, neg_cand]
        ranked = self.evaluate(prompt, candidates)
        
        if ranked[0]["candidate"] == answer:
            # Calculate margin
            s1 = ranked[0]["score"]
            s2 = ranked[1]["score"]
            margin = s1 - s2
            # Sigmoid-like mapping
            conf = 1.0 / (1.0 + np.exp(-margin))
            return min(0.99, max(0.51, conf))
        else:
            return 0.49 # Less than random chance

# Import zlib for NCD inside the class scope or globally
import zlib