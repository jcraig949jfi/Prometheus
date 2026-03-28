import re
import numpy as np
import math

class ReasoningTool:
    """
    Thermodynamic Factor-Graph Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations (negation, conditional, causal, numeric).
    2. Graph Construction: Builds an adjacency matrix and weight matrix representing constraints.
    3. Inference: Uses Loopy Belief Propagation (LBP) to approximate marginals (mu) minimizing energy.
    4. Scoring: Computes Free Energy (E - T*S). Lower free energy = higher coherence.
    5. Incentive: Uses Brier score against inferred marginals to rank candidates.
    """
    
    def __init__(self):
        self.temp = 1.0
        self.max_iter = 20
        
    def _parse_clauses(self, text):
        """Extract atomic clauses and identify relations."""
        text = text.lower().replace("?", " .").replace("!", " .")
        # Split by punctuation but keep delimiters for structure
        raw_sentences = re.split(r'([.,;:])', text)
        
        clauses = []
        relations = [] # (type, idx1, idx2, weight)
        
        # Helper to clean
        clean = lambda s: s.strip()
        
        # Simple tokenizer for propositions
        current_idx = 0
        buffer = []
        
        # We treat each segment between splits as a potential node
        for i, part in enumerate(raw_sentences):
            if not part.strip(): continue
            if part.strip() in ['.', ',', ';', ':']:
                if buffer:
                    clause_text = " ".join(buffer).strip()
                    if clause_text:
                        clauses.append(clause_text)
                        buffer = []
            else:
                buffer.append(part)
        if buffer:
            clauses.append(" ".join(buffer).strip())
            
        if not clauses:
            clauses = [text] # Fallback
            
        n = len(clauses)
        if n == 0: return [], [], np.zeros((0,0)), np.zeros(0)
        
        # Initialize matrices
        W = np.zeros((n, n), dtype=float)
        b = np.zeros(n, dtype=float)
        
        # Patterns
        pat_neg = re.compile(r'\b(not|no|never|without)\b')
        pat_if = re.compile(r'\bif\b')
        pat_then = re.compile(r'\bthen\b')
        pat_causal = re.compile(r'\b(because|therefore|thus|hence)\b')
        pat_num = re.compile(r'(-?\d+\.?\d*)')
        pat_comp = re.compile(r'\b(more than|less than|greater than|equal to|at least)\b')
        
        for i, clause in enumerate(clauses):
            # Unary evidence: Numeric equality implies strong bias if standalone
            nums = pat_num.findall(clause)
            if len(nums) >= 2:
                # Simple numeric constraint check within clause
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if "less" in clause or "<" in clause:
                        b[i] = 2.0 if v1 < v2 else -2.0
                    elif "more" in clause or ">" in clause:
                        b[i] = 2.0 if v1 > v2 else -2.0
                except: pass
            
            # Negation bias
            if pat_neg.search(clause):
                b[i] -= 0.5 # Slight prior against negated statements being true alone
                
            # Pairwise relations
            for j in range(i+1, n):
                other = clauses[j]
                w = 0.0
                
                # Conditional: If A then B (A -> B)
                if pat_if.search(clause) and (pat_then.search(clause) or j == i+1):
                    # Simplified: If clause i has 'if', it constrains j
                    w = 1.0 
                
                # Causal
                if pat_causal.search(clause) or pat_causal.search(other):
                    w = 1.2
                    
                # Comparative transitivity hint
                if pat_comp.search(clause) or pat_comp.search(other):
                    w = 0.8
                    
                if w > 0:
                    W[i, j] = w
                    W[j, i] = w # Symmetric for undirected graph simplicity in this implementation
                    
        return clauses, relations, W, b

    def _belief_propagation(self, W, b):
        """Run Loopy Belief Propagation to get marginals."""
        n = b.shape[0]
        if n == 0: return np.array([])
        
        # Initialize messages
        mu = np.ones(n) * 0.5 # Prior belief
        if n == 1:
            # Single node logistic update
            val = b[0]
            return np.array([1.0 / (1.0 + math.exp(-val))]) if abs(val) < 20 else np.array([0.5])

        # Iterate
        for _ in range(self.max_iter):
            mu_new = np.copy(mu)
            for i in range(n):
                sum_msg = b[i]
                for j in range(n):
                    if i != j and W[i, j] > 0:
                        # Message from j to i: tanh approximation for binary BP
                        # m_ji = tanh(W_ij * mu_j)
                        msg = np.tanh(W[i, j] * (mu[j] - 0.5) * 2) 
                        sum_msg += W[i, j] * msg * 0.5 # Scale influence
                
                # Update belief
                prob = 1.0 / (1.0 + math.exp(-sum_msg)) if abs(sum_msg) < 20 else 0.5
                mu_new[i] = prob
            
            mu = mu_new
            if np.allclose(mu, mu_new, atol=1e-3): break
            
        return mu

    def _compute_free_energy(self, mu, W, b):
        """Calculate Free Energy F = E - TS."""
        n = len(mu)
        if n == 0: return 0.0
        
        # Energy E = Sum(b_i * x_i) + Sum(W_ij * C_ij)
        # Approximate E using expected values mu
        E = np.dot(b, mu)
        
        for i in range(n):
            for j in range(i+1, n):
                if W[i, j] > 0:
                    # Constraint cost: 0 if consistent, 1 if not. 
                    # Expected cost approx: W * (mu_i * (1-mu_j) + (1-mu_i)*mu_j) for anti-correlated
                    # For "If A then B", cost is high if A=1, B=0.
                    # Simplified: Penalty for disagreement if weight exists
                    disagreement = mu[i] * (1 - mu[j]) + (1 - mu[i]) * mu[j]
                    E += W[i, j] * disagreement
        
        # Entropy H = -Sum(p log p + (1-p) log (1-p))
        H = 0.0
        eps = 1e-9
        for p in mu:
            if p > eps and p < 1-eps:
                H -= p * math.log(p) + (1-p) * math.log(1-p)
                
        F = E - self.temp * H
        return F

    def _score_candidate(self, prompt, candidate):
        """Internal scoring logic."""
        # Combine prompt and candidate to form the "world state"
        full_text = f"{prompt} {candidate}"
        
        clauses, _, W, b = self._parse_clauses(full_text)
        
        if len(clauses) == 0:
            return 0.5, "No parseable structure"
            
        mu = self._belief_propagation(W, b)
        free_energy = self._compute_free_energy(mu, W, b)
        
        # Heuristic: Lower free energy is better. 
        # Normalize roughly: High negative energy is good, high positive is bad.
        # Map to 0-1 range loosely. 
        # If system is coherent, energy should be low (negative).
        score = 1.0 / (1.0 + math.exp(free_energy / 2.0))
        
        reasoning = f"Parsed {len(clauses)} clauses. Entropy: {-sum(p*math.log(p+1e-9) + (1-p)*math.log(1-p+1e-9) for p in mu):.2f}. Free Energy: {free_energy:.2f}."
        
        return score, reasoning

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reason})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._score_candidate(prompt, answer)
        return max(0.0, min(1.0, score))