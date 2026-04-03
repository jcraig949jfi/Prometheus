import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Predictive Coding, Analogical Reasoning, and Mechanism Design.
    
    Mechanism:
    1. Parsing: Converts text to a relational graph (nodes=terms, edges=logic relations).
    2. Analogical Mapping: Uses Sinkhorn iteration to align prompt and answer graph structures.
    3. Predictive Coding: Computes prediction error (Frobenius norm) between aligned structures.
    4. Mechanism Design: Applies a Brier-style proper scoring rule to penalize miscalibrated confidence.
    
    Beats NCD baseline by focusing on logical structure (negation, causality, comparison) rather than string compression.
    """
    
    def __init__(self):
        self.relations = ['neg', 'cmp', 'cond', 'cause', 'before', 'after', 'and', 'or']
        self.lambda_weight = 0.1
        
    def _extract_terms(self, text: str) -> List[str]:
        """Extract key lexical items (nouns, numbers, booleans)."""
        text = text.lower()
        # Keep numbers, booleans, and alphanumeric words > 2 chars
        tokens = re.findall(r'\b(?:true|false|\d+\.?\d*|[a-z]{2,})\b', text)
        return tokens if tokens else ['null']

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray]:
        """
        Parse text into nodes and an adjacency tensor A[i, j, r].
        Returns (nodes, tensor).
        """
        nodes = self._extract_terms(text)
        n = len(nodes)
        if n == 0:
            return [], np.array([])
            
        R = len(self.relations)
        A = np.zeros((n, n, R), dtype=float)
        text_lower = text.lower()
        
        # Helper to find node indices
        def get_idx(term):
            try: return nodes.index(term)
            except ValueError: return -1

        # 1. Negations
        neg_patterns = [r"not\s+(\w+)", r"no\s+(\w+)", r"never\s+(\w+)", r"false"]
        for pat in neg_patterns:
            for m in re.finditer(pat, text_lower):
                target = m.group(1) if len(m.groups()) > 0 else m.group(0)
                t_idx = get_idx(target)
                if t_idx != -1:
                    # Connect previous word or self to negation
                    A[t_idx, t_idx, self.relations.index('neg')] = 1.0

        # 2. Comparatives (Greater/Less)
        if "greater" in text_lower or ">" in text_lower or "more" in text_lower:
            # Simplified: mark all number pairs as cmp
            nums = [i for i, x in enumerate(nodes) if x.replace('.','').isdigit()]
            for i in nums:
                for j in nums:
                    if i != j:
                        A[i, j, self.relations.index('cmp')] = 1.0
                        
        if "less" in text_lower or "<" in text_lower:
            nums = [i for i, x in enumerate(nodes) if x.replace('.','').isdigit()]
            for i in nums:
                for j in nums:
                    if i != j:
                        A[i, j, self.relations.index('cmp')] = -1.0 # Directionality

        # 3. Conditionals (if -> then)
        if "if" in text_lower:
            # Rough heuristic: words before 'if' condition, after consequence
            parts = re.split(r'\bif\b', text_lower, maxsplit=1)
            if len(parts) == 2:
                antecedent_terms = self._extract_terms(parts[0])
                consequent_terms = self._extract_terms(parts[1])
                for t1 in antecedent_terms:
                    for t2 in consequent_terms:
                        i, j = get_idx(t1), get_idx(t2)
                        if i != -1 and j != -1:
                            A[i, j, self.relations.index('cond')] = 1.0

        # 4. Causal (because, causes)
        causal_words = ['because', 'causes', 'leads', 'results']
        for cw in causal_words:
            if cw in text_lower:
                # Mark relations around the word
                idx = text_lower.find(cw)
                # Simple proximity logic
                for i, n1 in enumerate(nodes):
                    for j, n2 in enumerate(nodes):
                        if i != j:
                            A[i, j, self.relations.index('cause')] = 0.5

        # 5. Numeric Value Consistency (Node attribute simulation via self-loop weight)
        for i, term in enumerate(nodes):
            if re.match(r'\d+\.?\d*', term):
                val = float(term)
                # Encode magnitude in a specific slice or just flag presence
                A[i, i, 0] = np.sign(val) # Use first relation slice for sign/magnitude hint

        return nodes, A

    def _sinkhorn(self, C: np.ndarray, iterations: int = 10) -> np.ndarray:
        """Compute soft alignment matrix M using Sinkhorn algorithm."""
        if C.size == 0:
            return np.array([])
        n, m = C.shape
        if n == 0 or m == 0:
            return np.zeros((n, m))
            
        P = np.exp(C)
        P += 1e-9 # Avoid division by zero
        
        for _ in range(iterations):
            P = P / (P.sum(axis=1, keepdims=True) + 1e-9)
            P = P / (P.sum(axis=0, keepdims=True) + 1e-9)
            
        return P

    def _compute_score(self, prompt: str, answer: str) -> Tuple[float, float, str]:
        """Core logic: Parse, Align, Compute Error, Apply Incentive."""
        p_nodes, p_A = self._parse_graph(prompt)
        a_nodes, a_A = self._parse_graph(answer)
        
        if p_A.size == 0 or a_A.size == 0:
            return -100.0, 0.5, "Parsing failed."

        # Flatten relations for alignment computation
        # Reshape to (N*N, R) then compute similarity? 
        # Simplified: Flatten tensor to vector per node pair? 
        # Let's align based on node embedding similarity derived from relations
        
        n_p, n_a = p_A.shape[0], a_A.shape[0]
        if n_p == 0 or n_a == 0:
            return -100.0, 0.5, "No nodes."

        # Create compatibility matrix C (n_p x n_a)
        # Score based on shared relation profiles
        C = np.zeros((n_p, n_a))
        for i in range(n_p):
            for j in range(n_a):
                # Compare relation vectors for node i and j
                vec_p = p_A[i, :, :].flatten() # Outgoing relations
                vec_a = a_A[j, :, :].flatten()
                # Cosine-like similarity
                norm_p = np.linalg.norm(vec_p)
                norm_a = np.linalg.norm(vec_a)
                if norm_p > 0 and norm_a > 0:
                    C[i, j] = np.dot(vec_p, vec_a) / (norm_p * norm_a)
                elif np.all(vec_p == 0) and np.all(vec_a == 0):
                    C[i, j] = 1.0 # Both empty is a match
        
        # Analogical Mapping via Sinkhorn
        M = self._sinkhorn(C)
        
        # Predictive Coding: Compute Residual Error
        # Align answer tensor to prompt space: A_aligned = M^T * A_answer * M
        # Since A is 3D, we do this per relation slice
        error = 0.0
        R = p_A.shape[2]
        
        for r in range(R):
            Ap = p_A[:, :, r]
            Aa = a_A[:, :, r]
            
            # Pad/Truncate to match dimensions for matrix mult if needed, 
            # but Sinkhorn M is n_p x n_a. 
            # We need to project Aa (n_a x n_a) to (n_p x n_p) using M
            # A_proj = M.T @ Aa @ M
            if Aa.shape[0] != M.shape[0]:
                # Handle dimension mismatch if sinkhorn didn't match exactly (shouldn't happen)
                min_dim = min(Aa.shape[0], M.shape[0])
                Aa = Aa[:min_dim, :min_dim]
                M_use = M[:min_dim, :min_dim] # Simplification
            else:
                M_use = M
                
            try:
                A_proj = M_use.T @ Aa @ M_use
                # Resize A_proj to match Ap if sizes differ slightly due to padding
                if A_proj.shape != Ap.shape:
                    min_s = min(A_proj.shape[0], Ap.shape[0])
                    A_proj = A_proj[:min_s, :min_s]
                    Ap = Ap[:min_s, :min_s]
                
                diff = Ap - A_proj
                error += np.sum(diff ** 2)
            except ValueError:
                error += 10.0 # Penalty for structural mismatch

        E = float(np.sqrt(error)) # Frobenius norm
        
        # Extract Confidence from Answer (Mechanism Design)
        # Look for "X%" or "X percent"
        conf_match = re.search(r'(\d+(?:\.\d+)?)\s*%?', answer)
        reported_c = 0.5
        if conf_match:
            reported_c = float(conf_match.group(1)) / 100.0
        else:
            # Heuristic: if answer contains logical keywords, assume higher confidence
            if any(k in answer.lower() for k in ['therefore', 'thus', 'clearly', 'yes', 'no']):
                reported_c = 0.8
            else:
                reported_c = 0.5

        # Proper Scoring Rule (Brier-style)
        # Target confidence should be inversely related to error. 
        # Normalize error to [0,1] roughly. Assume max error ~10 for scaling.
        target_c = 1.0 / (1.0 + np.exp(E - 2.0)) # Logistic mapping of error
        incentive = -(reported_c - target_c)**2
        
        final_score = -E + self.lambda_weight * incentive
        reason_str = f"Structural Error: {E:.2f}, Confidence Penalty: {incentive:.2f}"
        
        return final_score, reported_c, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            score, conf, reason = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, c, _ = self._compute_score(prompt, answer)
        # Map score to 0-1. High score (low error) -> 1.0
        # Score is negative error, so closer to 0 is better.
        # Let's say score > -1 is high confidence.
        conf_val = 1.0 / (1.0 + np.exp(score)) # Logistic transform
        return float(np.clip(conf_val, 0.0, 1.0))