import re
import numpy as np

class ReasoningTool:
    """
    Implements a Falsificationist reasoning engine aided by Compressed Sensing principles.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causals).
    2. Constraint Matrix (A): Encodes logical relations (e.g., If P then Q -> P <= Q).
    3. Sparse Recovery (ISTA): Solves min ||x||_1 s.t. ||Ax - b|| <= epsilon to find the 
       minimal set of assertions needed to satisfy the prompt's constraints.
    4. Energy Scoring: Computes Free Energy E = 0.5*||residual||^2 + lambda*||x||_1.
       Lower Energy (higher score) indicates fewer falsified constraints and higher consistency.
    5. Falsification: The residual directly penalizes claims that contradict prompt constraints.
    """
    
    def __init__(self):
        self.lambda_reg = 0.1
        self.max_iter = 100
        self.step_size = 0.01
        
    def _extract_props(self, text):
        """Extract atomic propositions and structural cues."""
        text_lower = text.lower()
        props = []
        
        # Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            props.append(('negation', 1))
            
        # Comparatives
        if re.search(r'\b(greater|less|more|fewer|larger|smaller)\b', text_lower):
            props.append(('comparative', 1))
        if re.search(r'[=<>]', text) or re.search(r'\b(equals|equal to)\b', text_lower):
            props.append(('equality', 1))
            
        # Conditionals
        if re.search(r'\b(if|then|provided|unless)\b', text_lower):
            props.append(('conditional', 1))
            
        # Causal
        if re.search(r'\b(because|therefore|thus|leads to|results in)\b', text_lower):
            props.append(('causal', 1))
            
        # Numeric extraction for magnitude check
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            props.append(('numeric', float(max(nums, key=float))))
            
        return props

    def _build_system(self, prompt_props, cand_props):
        """
        Build constraint matrix A and observation vector b.
        Rows represent constraints derived from the prompt.
        Columns represent propositions in the candidate.
        """
        # Map prompt constraints to expected candidate behavior
        # Simplified logic: Prompt features impose constraints on Candidate features
        
        n_vars = max(1, len(cand_props))
        m_constraints = max(1, len(prompt_props))
        
        A = np.zeros((m_constraints, n_vars))
        b = np.zeros(m_constraints)
        
        # Create a mapping based on feature types
        p_types = [p[0] for p in prompt_props]
        c_types = [c[0] for c in cand_props]
        
        for i, p_type in enumerate(p_types):
            for j, c_type in enumerate(c_types):
                if p_type == c_type:
                    # Identity constraint: Prompt presence implies Candidate presence
                    # Encoded as: 1 * x_j = 1 (if prompt has it, candidate should too)
                    # Or for negation logic: if prompt says "not", candidate must reflect it
                    A[i % m_constraints, j % n_vars] = 1.0
                    b[i % m_constraints] = 1.0
                elif (p_type == 'conditional' and c_type == 'causal') or \
                     (p_type == 'causal' and c_type == 'conditional'):
                    # Soft coupling between logic types
                    A[i % m_constraints, j % n_vars] = 0.5
                    b[i % m_constraints] = 0.5
        
        # Ensure non-empty system
        if np.all(A == 0):
            A[0, 0] = 1.0
            b[0] = 1.0 if 'numeric' in c_types else 0.0
            
        return A, b

    def _ista_solve(self, A, b, lam):
        """Iterative Shrinkage-Thresholding Algorithm for L1 minimization."""
        m, n = A.shape
        x = np.zeros(n)
        # Estimate Lipschitz constant L = max eigenvalue of A'A
        try:
            L = np.linalg.norm(A, ord=2)**2 + 1e-6
        except:
            L = 1.0
        step = 1.0 / L
        
        for _ in range(self.max_iter):
            grad = A.T @ (A @ x - b)
            x_new = x - step * grad
            # Soft thresholding
            x = np.sign(x_new) * np.maximum(np.abs(x_new) - lam * step, 0)
        return x

    def _compute_energy(self, prompt, candidate):
        """Compute Free Energy score based on falsification residuals."""
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        
        if not p_props or not c_props:
            # Fallback for empty parses
            return -1.0 if not c_props else -0.5

        A, b = self._build_system(p_props, c_props)
        
        # Sparse recovery to find minimal consistent explanation
        x_star = self._ista_solve(A, b, self.lambda_reg)
        
        # Residual (Falsification measure)
        residual = b - A @ x_star
        data_fidelity = 0.5 * np.linalg.norm(residual, 2)**2
        sparsity = np.linalg.norm(x_star, 1)
        
        # Free Energy
        E = data_fidelity + self.lambda_reg * sparsity
        
        # Numeric consistency bonus/penalty
        p_nums = [p[1] for p in p_props if p[0] == 'numeric']
        c_nums = [c[1] for c in c_props if c[0] == 'numeric']
        
        if p_nums and c_nums:
            # Check if numeric logic holds (simplified)
            if abs(p_nums[0] - c_nums[0]) > 1e-6:
                E += 2.0 # Penalty for numeric mismatch
        
        return -E # Higher is better

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as tiebreaker."""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Approx compression
            z2 = len(repr(s2.encode('utf-8')))
            s12 = len(repr((s1+s2).encode('utf-8')))
            if s12 == 0: return 0.0
            return (s12 - min(z1, z2)) / max(z1, z2, 1)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        scores = []
        
        # Primary scoring via Falsificationist Energy
        for cand in candidates:
            score = self._compute_energy(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": ""})
            scores.append(score)
        
        # Tie-breaking with NCD if scores are too close
        final_results = []
        for i, res in enumerate(results):
            # Check for ties within epsilon
            is_tie = any(abs(scores[i] - s) < 1e-4 for j, s in enumerate(scores) if i != j)
            if is_tie:
                # Adjust score slightly by NCD (lower NCD is better, so subtract)
                ncd_val = self._ncd_score(prompt, res['candidate'])
                res['score'] -= ncd_val * 1e-6
                res['reasoning'] = f"Energy score adjusted by NCD tiebreaker. Base Energy: {scores[i]:.4f}"
            else:
                res['reasoning'] = f"Derived from Free Energy of falsified constraints: {scores[i]:.4f}"
            final_results.append(res)
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on energy score normalization."""
        score = self._compute_energy(prompt, answer)
        # Map score to 0-1. Assuming typical energy range [-5, 0] for valid, < -5 for invalid
        # Shift so 0 is perfect, negative is worse.
        # Sigmoid-like mapping
        conf = 1.0 / (1.0 + np.exp(score + 2.0)) 
        return max(0.0, min(1.0, conf))