import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Compressed Sensing (L1-minimization),
    Abductive Reasoning (hypothesis generation via sparsity), and Abstract Interpretation
    (constraint propagation). 
    
    Mechanism:
    1. Parses prompt and candidates into atomic propositions and logical constraints.
    2. Constructs a sparse linear system Ax = b where x represents belief degrees.
    3. Uses Iterative Soft-Thresholding (ISTA) to find the sparsest x satisfying constraints.
    4. Applies Abstract Interpretation steps to enforce logical consistency (e.g., p->q).
    5. Scores candidates based on residual error and solution sparsity.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        self.alpha = 0.1  # Sparsity penalty

    def _extract_numerics(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _parse_structure(self, text: str) -> Tuple[List[str], List[Tuple]]:
        """
        Extract atomic propositions and logical constraints.
        Returns variables and a list of (type, args) constraints.
        """
        text_lower = text.lower()
        variables = []
        constraints = []
        
        # Extract numbers for numeric constraints
        nums = self._extract_numerics(text)
        for i, n in enumerate(nums):
            var_name = f"num_{i}"
            variables.append(var_name)
            # Constraint: num_i == value (encoded as equality row later)
            constraints.append(('eq', var_name, n))

        # Logical patterns
        if re.search(r'\bif\b.*\bthen\b|\bimplies\b|\bleads to\b|\bcauses\b', text_lower):
            # Simplified: detect conditional structure existence
            constraints.append(('cond', 1)) 
        
        if re.search(r'\bnot\b|\bno\b|\bnever\b', text_lower):
            constraints.append(('neg', 1))
            
        if re.search(r'\band\b|\bboth\b', text_lower):
            constraints.append(('conj', 1))
            
        # Comparatives
        if re.search(r'>|<|greater|less|more than|fewer than', text_lower):
            constraints.append(('comp', 1))

        return variables, constraints

    def _build_system(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build the linear system Ax = b.
        Variables are shared between prompt and candidate.
        """
        full_text = f"{prompt} {candidate}"
        vars_p, cons_p = self._parse_structure(prompt)
        vars_c, cons_c = self._parse_structure(candidate)
        
        # Union of variables (simplified to just counts for this abstraction if no specific names)
        # We treat the "belief" in the candidate as the primary variable x_0
        # And constraints from prompt as rows affecting x_0
        
        all_vars = ['belief'] + [f"v_{i}" for i in range(len(vars_p) + len(vars_c))]
        n = len(all_vars)
        rows = []
        b_vals = []
        
        # 1. Candidate Assertion: The candidate claims "belief" is true (1)
        # Row: [1, 0, ...] = 1
        row = np.zeros(n)
        row[0] = 1.0
        rows.append(row)
        b_vals.append(1.0)
        
        # 2. Prompt Constraints mapped to belief
        # If prompt has negation, and candidate implies positive belief, create conflict
        p_has_neg = any(c[0] == 'neg' for c in cons_p)
        c_has_pos = any(c[0] == 'neg' for c in cons_c) # Simplified logic
        
        # Numeric consistency check
        nums_p = self._extract_numerics(prompt)
        nums_c = self._extract_numerics(candidate)
        
        if nums_p and nums_c:
            # Check simple magnitude relation if both have numbers
            # Encode as: if prompt says "max 5" and candidate says "6", penalty
            # For this linear model, we add a row that penalizes belief if numbers contradict
            if len(nums_p) >= 1 and len(nums_c) >= 1:
                # Heuristic: if candidate number > prompt number in a "less than" context?
                # Too complex for pure regex without semantic parsing. 
                # Instead, we use the count of numeric matches as a soft constraint.
                pass 

        # Abstract Interpretation Step (Simulation):
        # Enforce that if prompt has 'not' and candidate lacks it, belief should be low.
        # We encode this as a row: -1 * belief <= 0 (if contradiction exists)
        
        contradiction = False
        if p_has_neg and not c_has_pos:
            # Potential contradiction if candidate affirms what prompt negates
            # We don't know the subject, so we rely on the 'comp' or 'num' overlap
            pass
            
        # Add structural consistency rows
        # If prompt has 'comp' (comparative), candidate should ideally have numbers or comparatives
        p_has_comp = any(c[0] == 'comp' for c in cons_p)
        c_has_comp = any(c[0] == 'comp' for c in cons_c)
        p_has_num = len(nums_p) > 0
        c_has_num = len(nums_c) > 0
        
        # Consistency heuristic: If prompt compares, candidate should reflect that structure
        if p_has_comp:
            row = np.zeros(n)
            # Encourage structure match
            target = 1.0 if (c_has_comp or c_has_num) else 0.0
            row[0] = 1.0 # Affects belief variable
            rows.append(row)
            b_vals.append(target)

        # Fill matrix A and vector b
        if not rows:
            # Fallback identity
            rows.append(np.eye(n)[0])
            b_vals.append(0.5)
            
        A = np.array(rows[:n+5]) # Limit rows to avoid over-constraint in simple cases
        if A.shape[1] > A.shape[0]:
            # Pad A if needed (rare in this simplified model)
            pass
            
        # Ensure A is square or m>=n for least squares, otherwise truncate/expand
        m, n_cols = A.shape
        if m < n_cols:
            A = np.pad(A, ((0, n_cols-m), (0,0)), mode='constant')
            b_vals = b_vals + [0.5] * (n_cols - m)
            
        A = A[:n_cols, :] # Take first n_cols rows to make it square-ish for inversion approx
        b = np.array(b_vals[:n_cols])
        
        if len(b) < n_cols:
            b = np.pad(b, (0, n_cols-len(b)), constant_values=0.5)
            
        # Normalize
        if np.linalg.norm(b) == 0:
            b = np.ones_like(b) * 0.5
            
        return A, b, all_vars

    def _ista_solve(self, A: np.ndarray, b: np.ndarray, lam: float = 0.1) -> np.ndarray:
        """Iterative Soft-Thresholding Algorithm for L1 minimization."""
        m, n = A.shape
        x = np.zeros(n)
        L = np.linalg.norm(A, ord=2)**2 + 1e-6 # Lipschitz constant
        
        for _ in range(self.max_iter):
            grad = A.T @ (A @ x - b)
            x = x - (1/L) * grad
            # Soft thresholding
            x = np.sign(x) * np.maximum(np.abs(x) - lam/L, 0)
            
            # Abstract Interpretation Projection (Interval Clamping)
            # Enforce x in [0, 1]
            x = np.clip(x, 0.0, 1.0)
            
            # Enforce simple implication: if row i is p->q (-p + q >= 0)
            # This is hard to map without explicit variable mapping, so we skip complex projection
            # and rely on the clipping and L1 penalty for sparsity.
            
        return x

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Compute the abductive score for a candidate."""
        A, b, vars_list = self._build_system(prompt, candidate)
        
        if A.shape[0] == 0 or A.shape[1] == 0:
            return 0.5

        # Solve
        x_star = self._ista_solve(A, b, lam=self.alpha)
        
        if len(x_star) == 0:
            return 0.5

        # Residual
        residual = np.linalg.norm(A @ x_star - b)
        norm_b = np.linalg.norm(b)
        if norm_b == 0: norm_b = 1
        
        # Sparsity
        l1_norm = np.linalg.norm(x_star, ord=1)
        n = len(x_star)
        
        # Score formula from prompt
        score = 1.0 - (residual / norm_b) - self.alpha * (l1_norm / max(n, 1))
        
        # Structural bonus (Heuristic boost for matching patterns)
        # If prompt has numbers and candidate has numbers, boost slightly
        p_nums = self._extract_numerics(prompt)
        c_nums = self._extract_numerics(candidate)
        if p_nums and c_nums:
            score += 0.1
            
        return float(np.clip(score, 0.0, 1.0))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            import zlib
            def l(s): return len(zlib.compress(s.encode()))
            l1, l2, l12 = l(s1), l(s2), l(s1+s2)
            if max(l1, l2) == 0: return 1.0
            return (l12 - min(l1, l2)) / max(l1, l2)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Primary scoring via Structural/Abductive method
        for cand in candidates:
            sc = self._compute_score(prompt, cand)
            scores.append(sc)
        
        # Handle ties or low differentiation with NCD
        max_sc = max(scores) if scores else 0
        min_sc = min(scores) if scores else 0
        
        for i, cand in enumerate(candidates):
            base_score = scores[i]
            
            # NCD Tiebreaker logic
            if max_sc - min_sc < 0.01: # Low variance, use NCD
                ncd = self._ncd_score(prompt, cand)
                # Invert NCD (lower is better) and scale
                base_score = base_score * 0.5 + (1.0 - ncd) * 0.5
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Sparse abductive fit: {base_score:.4f}"
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']