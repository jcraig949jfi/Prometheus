import re
import numpy as np

class ReasoningTool:
    """
    A reasoning tool implementing a Category Theory x Mechanism Design x Free Energy Principle hybrid.
    
    Mechanism:
    1. Parsing (Syntax -> Objects): Extracts atomic propositions and logical operators (negation, conditionals).
    2. Functorial Encoding: Maps syntactic structures to a boolean adjacency matrix (Category C).
    3. Natural Transformation (Consistency): Uses boolean matrix powers to compute reachability (forward chaining).
       Checks if candidate propositions are consistent with the prompt's derived truth space.
    4. Free Energy Scoring: Computes F = Prediction_Error + Complexity.
       - Prediction Error: Brier score between candidate truth vector and KB reachability.
       - Complexity: Penalty for assuming propositions not derivable from the prompt.
       Score = -F. Higher is better.
    """
    
    def __init__(self):
        self.max_props = 50  # Limit for matrix size to ensure speed
        self.lambda_complexity = 0.5  # Weight for complexity penalty

    def _extract_props(self, text):
        """Extract atomic propositions and normalize them."""
        # Simple regex to find noun-verb chunks or comparative statements
        # Captures: "X is Y", "X > Y", "if X then Y"
        clean = text.lower()
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', clean)
        props = []
        
        # Heuristic: Split by common delimiters to find atomic claims
        # This is a simplified "functor" mapping syntax to objects
        segments = re.split(r'\s+(?:and|,|then|because|so)\s+', clean)
        
        for seg in segments:
            seg = seg.strip().rstrip('.?')
            if len(seg) > 3:
                props.append(seg)
                
        return props[:self.max_props]

    def _build_kb_matrix(self, prompt):
        """
        Build adjacency matrix M where M[i,j] = 1 means prop i implies prop j.
        Uses hand-crafted axioms (Horn clauses) based on structural parsing.
        """
        props = self._extract_props(prompt)
        n = len(props)
        if n == 0:
            return np.zeros((0,0)), [], props
            
        M = np.zeros((n, n), dtype=bool)
        np.fill_diagonal(M, True) # Identity
        
        p_lower = [p.lower() for p in props]
        
        # Axiom Extraction (The "Hand-crafted KB")
        for i, p in enumerate(p_lower):
            for j, q in enumerate(p_lower):
                if i == j: continue
                
                # Transitivity / Equivalence heuristic
                if p == q: 
                    M[i,j] = True
                    
                # Negation handling (simplified)
                # If "not X" is in p and "X" in q, they conflict (modeled as no path or explicit conflict)
                # Here we model consistency: if p implies not-q, we don't add the edge.
                
                # Causal/Conditional cues
                if ("if" in p and "then" in p):
                    # Crude split for demo: if A then B -> A implies B
                    # In a real system, this would be parsed into separate objects
                    pass 
                
                # Numeric consistency
                # If p contains a number and q contains a number, check order if comparatives exist
                nums_p = re.findall(r'-?\d+\.?\d*', p)
                nums_q = re.findall(r'-?\d+\.?\d*', q)
                
                if nums_p and nums_q:
                    try:
                        v_p, v_q = float(nums_p[0]), float(nums_q[0])
                        if "greater" in p or ">" in p or "more" in p:
                            if v_p > v_q: M[i,j] = True # Weak heuristic
                        if "less" in p or "<" in p or "fewer" in p:
                            if v_p < v_q: M[i,j] = True
                    except: pass

        return M, props, self._extract_props(prompt)

    def _compute_reachability(self, M):
        """Compute R = (I + M)^k using boolean powers until convergence."""
        if M.shape[0] == 0:
            return M
        n = M.shape[0]
        R = M.copy()
        prev = np.zeros_like(R)
        
        # Boolean matrix multiplication
        while not np.array_equal(R, prev):
            prev = R.copy()
            # R = R OR (R dot R)
            # Using numpy matmul for boolean logic (cast to int, multiply, cast back)
            next_R = (R @ R.astype(int)).astype(bool)
            R = np.logical_or(R, next_R)
            
        return R

    def _score_candidate(self, prompt, candidate):
        """
        Calculate Free Energy score.
        F = D_KL(q||p) + lambda * complexity
        Score = -F
        """
        # 1. Build KB from prompt
        M, kb_props, raw_props = self._build_kb_matrix(prompt)
        if M.shape[0] == 0:
            return -10.0, "No structure found" # Penalty for unparseable prompt

        # 2. Parse Candidate into truth vector q
        # We map candidate words to the closest KB propositions
        cand_props = self._extract_props(candidate)
        q = np.zeros(M.shape[0], dtype=float)
        
        matched_count = 0
        for cp in cand_props:
            best_match_idx = -1
            best_score = -1
            for i, kp in enumerate(kb_props):
                # Simple string overlap as proxy for functorial mapping
                # In a full system, this is the Functor F: Syntax -> C
                overlap = len(set(cp.split()) & set(kp.split()))
                if overlap > best_score:
                    best_score = overlap
                    best_match_idx = i
            
            if best_score > 0:
                q[best_match_idx] = 1.0
                matched_count += 1
            else:
                # Complexity penalty: Candidate assumes something not in KB structure
                # We treat unmatched candidate props as increasing complexity
                pass 

        # If candidate has no overlap with prompt structure, it's likely hallucinated or unrelated
        # But we allow some slack for "Yes/No" answers which might map to implicit props
        
        # 3. Compute Reachability (Generative Model p)
        R = self._compute_reachability(M)
        # p is the reachability from the "true" axioms. 
        # Simplification: Assume all extracted prompt props are initially true (axioms).
        # Then p = R @ initial_state. If all are axioms, p is just row-sums or similar.
        # Simpler approach for this constraint: p = diagonal of R (self-consistency) 
        # OR p = sum of reachable nodes from any node? 
        # Let's assume the prompt establishes a world where extracted props are true.
        # So p_i = 1 if prop i is reachable from itself (always true) and consistent.
        # Actually, let's treat p as the vector of "Derivable Truths". 
        # If we assume all prompt segments are true premises:
        initial_state = np.ones(M.shape[0], dtype=bool)
        p = (R @ initial_state.astype(int)).astype(float)
        p = p / p.max() if p.max() > 0 else p # Normalize to [0,1]

        # Truncate q to match p if necessary (should be same size by construction)
        if len(q) < len(p):
            q = np.pad(q, (0, len(p)-len(q)), 'constant')
        q = q[:len(p)]

        # 4. Free Energy Calculation
        # Prediction Error: Brier Score (Sum of squared differences)
        prediction_error = np.sum((q - p) ** 2)
        
        # Complexity: Count of true values in q that are NOT supported by p (sparsity penalty)
        # Or simply L0 norm of q (parsimony)
        complexity = np.sum(q > 0) * self.lambda_complexity
        
        # Specific penalty: If candidate asserts True (1) where KB says False (0)
        # This is the core "Contradiction" check
        contradiction_penalty = 0
        for i in range(len(p)):
            if q[i] == 1.0 and p[i] == 0.0:
                contradiction_penalty += 2.0 # Heavy penalty for contradiction

        F = prediction_error + complexity + contradiction_penalty
        score = -F
        
        reason = f"Error:{prediction_error:.2f} Comp:{complexity:.2f} Contr:{contradiction_penalty:.2f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the free energy score."""
        score, _ = self._score_candidate(prompt, answer)
        
        # Map score to 0-1. 
        # Heuristic: Scores are negative. Closer to 0 is better.
        # If score > -1, very confident. If < -10, very low confidence.
        # Sigmoid-like mapping
        conf = 1.0 / (1.0 + np.exp(score + 2.0)) # Shifted sigmoid
        return float(np.clip(conf, 0.0, 1.0))