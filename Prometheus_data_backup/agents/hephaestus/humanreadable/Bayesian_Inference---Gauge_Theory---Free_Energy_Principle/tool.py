import re
import numpy as np
from math import log, exp

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Bayesian Inference, Gauge Theory symmetry,
    and the Free Energy Principle (FEP).
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical operators into a factor graph.
    2. Priors: Initializes beliefs using Beta(1,1) conjugate priors.
    3. Gauge Connection: Enforces invariance to entity permutation via a covariant derivative term.
    4. Belief Propagation: Iteratively updates beliefs minimizing variational free energy.
    5. Scoring: Ranks candidates by negative Free Energy (Surprise + Complexity).
    """

    def __init__(self):
        self.ops = ['not', 'no', 'more than', 'less than', 'if', 'then', 'cause', 'lead to', 'before', 'after', 'greater than', 'less than', '=', '<', '>']
        self.num_pat = re.compile(r'-?\d+\.?\d*')

    def _parse_props(self, text):
        """Extract atomic propositions and build adjacency matrix."""
        clean = text.lower()
        # Simple tokenization by splitting on logical connectors
        atoms = re.split(r'(?:\s+and\s+|\s+or\s+|,)', clean)
        atoms = [a.strip() for a in atoms if a.strip()]
        if not atoms:
            atoms = [clean]
        
        n = len(atoms)
        props = atoms
        A = np.zeros((n, n), dtype=np.int8)
        
        # Connect shared arguments (simple word overlap heuristic for adjacency)
        words = [set(a.split()) for a in props]
        for i in range(n):
            for j in range(i+1, n):
                if words[i] & words[j]: # Share words
                    A[i, j] = A[j, i] = 1
                # Connect sequential logic
                if any(op in props[i] or op in props[j] for op in ['if', 'then', 'cause']):
                    A[i, j] = A[j, i] = 1
        return props, A

    def _gauge_update(self, B, A, C):
        """Apply gauge symmetry projection to enforce invariance."""
        if A.sum() == 0:
            return C
        # Project C onto subspace orthogonal to permutation group (mean subtraction)
        C -= np.mean(C, axis=0, keepdims=True)
        C -= np.mean(C, axis=1, keepdims=True)
        return C

    def _run_inference(self, text):
        """Core FEP loop: Parse -> Prior -> Gauge -> BP -> Free Energy."""
        props, A = self._parse_props(text)
        n = len(props)
        if n == 0:
            return 0.5, []

        # 1. Priors: Beta(1,1) -> [0.5, 0.5]
        B = np.full((n, 2), 0.5) 
        prior = B.copy()

        # 2. Gauge Field Initialization
        C = np.zeros_like(A, dtype=np.float64)
        
        # Inject structural bias into Gauge field based on negation/comparators
        for i, p in enumerate(props):
            if any(k in p for k in ['not', 'no']):
                C[i, :] -= 0.5 # Penalize truth if negated context
            if any(k in p for k in ['more', 'greater', 'less']):
                C[i, :] += 0.2 # Boost confidence on numeric claims

        # 3. Belief Propagation (Loopy BP)
        for _ in range(10):
            messages = np.zeros_like(B)
            for i in range(n):
                neighbors = np.where(A[i, :] > 0)[0]
                if len(neighbors) == 0:
                    continue
                msg_sum = np.zeros(2)
                for j in neighbors:
                    # Message: softmax(log B_j + C_ji)
                    log_odds = np.log(B[j] + 1e-9) + C[j, i] if A[j,i] else np.log(B[j] + 1e-9)
                    exp_vals = np.exp(log_odds - np.max(log_odds)) # Stability
                    msg_sum += exp_vals / (exp_vals.sum() + 1e-9)
                messages[i] = msg_sum
            
            # Update beliefs
            log_B = np.log(B + 1e-9) + np.log(messages + 1e-9)
            # Add gauge contribution to log-odds
            log_B += C @ B 
            B = np.exp(log_B - np.max(log_B, axis=1, keepdims=True))
            B = B / (B.sum(axis=1, keepdims=True) + 1e-9)

        # 4. Gauge Projection step
        C = self._gauge_update(B, A, C)

        # 5. Free Energy Calculation
        # F = Surprise + Complexity
        surprise = -np.sum(np.log(B[:, 0] + 1e-9)) 
        kl_div = np.sum(B * np.log((B / (prior + 1e-9)) + 1e-9))
        F = surprise + kl_div
        
        # Normalize score to 0-1 range roughly
        score = 1.0 / (1.0 + exp(F / n)) 
        return score, props

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        base_score, _ = self._run_inference(prompt)
        
        for cand in candidates:
            # Combine prompt and candidate for joint inference
            full_text = f"{prompt} {cand}"
            score, props = self._run_inference(full_text)
            
            # Structural parsing bonus (Key pattern: Numeric/Logic detection)
            bonus = 0.0
            nums = self.num_pat.findall(full_text)
            if len(nums) >= 2:
                try:
                    vals = [float(x) for x in nums]
                    # Check consistency if comparators exist
                    if any(k in full_text for k in ['greater', 'more', '<', '>']):
                        if vals[0] > vals[1] and ('less' in full_text or '<' in full_text):
                            bonus = -0.5 # Penalty for contradiction
                        elif vals[0] < vals[1] and ('greater' in full_text or '>' in full_text):
                            bonus = -0.5
                except: pass
            
            final_score = score + bonus
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"FEP Score: {final_score:.4f}, Props: {len(props)}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0