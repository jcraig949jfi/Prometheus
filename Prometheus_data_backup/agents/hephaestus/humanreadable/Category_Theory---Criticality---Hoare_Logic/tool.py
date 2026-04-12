import re
import numpy as np

class ReasoningTool:
    """
    Implements a reasoning engine based on Category Theory, Criticality, and Hoare Logic.
    
    Mechanism:
    1. Structural Parsing (Category Theory): Extracts propositions (vertices) and logical 
       connectives (morphisms) using regex patterns for negation, comparatives, conditionals, 
       and causality.
    2. Critical Propagation (Criticality): Constructs an adjacency matrix where edge weights 
       are susceptibility scores derived from numeric variance in comparisons. The system 
       iteratively propagates truth values via a weighted fix-point update until convergence 
       or max steps.
    3. Verification (Hoare Logic): Evaluates the triple {Premises} Answer {Conclusion}. 
       The score combines the stability of the propagation (distance to fixed point) and 
       the binary satisfaction of the conclusion given the premises.
    """
    
    def __init__(self):
        self.max_iter = 20
        self.tolerance = 1e-4
        self.lambda_hoare = 0.5
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(greater than|less than|more than|fewer than|>|<)\s*(\w+)', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_tokens(self, text):
        """Extract structural features and build graph components."""
        text_lower = text.lower()
        vertices = []
        edges = []  # (u_idx, v_idx, weight, type)
        
        # Simple sentence splitting for vertices
        sentences = [s.strip() for s in re.split(r'[.\?!]', text) if s.strip()]
        if not sentences:
            sentences = [text]
            
        # Map sentences to vertices
        vertex_map = {s: i for i, s in enumerate(sentences)}
        vertices = sentences
        
        # Extract numeric values for susceptibility
        nums = [float(n) for n in self.patterns['numbers'].findall(text)]
        base_susceptibility = 1.0
        if len(nums) >= 2:
            base_susceptibility = 1.0 / (1.0 + np.std(nums)) if np.std(nums) > 0 else 1.0

        # 1. Negations (Unary morphisms)
        for i, s in enumerate(sentences):
            if self.patterns['negation'].search(s):
                # Self-loop with negative weight or unary operator
                edges.append((i, i, -0.5, 'negation'))

        # 2. Comparatives (Ordering edges)
        for match in self.patterns['comparative'].finditer(text):
            left, op, right = match.group(1), match.group(2), match.group(3)
            # Find closest sentences containing these terms
            u_idx, v_idx = -1, -1
            for i, s in enumerate(sentences):
                if left in s: u_idx = i
                if right in s: v_idx = i
            
            if u_idx != -1 and v_idx != -1:
                # Direction depends on operator
                weight = base_susceptibility if 'less' in op or '<' in op else base_susceptibility
                edges.append((u_idx, v_idx, weight, 'comparative'))

        # 3. Conditionals & Causal (Implication edges)
        for i, s in enumerate(sentences):
            if self.patterns['conditional'].search(s) or self.patterns['causal'].search(s):
                # Connect to next sentence if exists, else self
                target = i + 1 if i + 1 < len(sentences) else i
                edges.append((i, target, base_susceptibility, 'implication'))
        
        # Default connectivity: sequential flow if no other edges found
        if len(edges) == 0 and len(vertices) > 1:
            for i in range(len(vertices) - 1):
                edges.append((i, i+1, 1.0, 'sequence'))

        return vertices, edges, len(vertices)

    def _build_matrix(self, n, edges):
        """Construct adjacency matrix W with susceptibility weights."""
        W = np.zeros((n, n))
        for u, v, w, _ in edges:
            if 0 <= u < n and 0 <= v < n:
                W[v, u] += w  # Column u to Row v (t_new = W * t_old)
        return W

    def _propagate(self, W, initial_truth):
        """Iterative fix-point update: t_new = sigma(W * t + b)."""
        n = W.shape[0]
        t = initial_truth.copy()
        b = np.zeros(n) # Bias vector, typically 0 unless specific premises
        
        # Normalize W to prevent explosion (Criticality control)
        col_sum = W.sum(axis=0)
        col_sum[col_sum == 0] = 1
        W_norm = W / col_sum
        
        for _ in range(self.max_iter):
            t_next = np.dot(W_norm, t) + b
            # Step function approximation (sigmoid-like thresholding)
            t_next = 1.0 / (1.0 + np.exp(-10 * (t_next - 0.5)))
            
            if np.linalg.norm(t_next - t, 1) < self.tolerance:
                break
            t = t_next
            
        return t, np.linalg.norm(t_next - t, 1)

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance as tiebreaker."""
        import zlib
        def comp(s): return len(zlib.compress(s.encode()))
        c1, c2, c12 = comp(s1), comp(s2), comp(s1 + s2)
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_verts, prompt_edges, n = self._extract_tokens(prompt)
        
        if n == 0:
            # Fallback if parsing fails
            return [{"candidate": c, "score": 0.5, "reasoning": "No structure found"} for c in candidates]

        W = self._build_matrix(n, prompt_edges)
        
        # Initial truth: Assume all prompt sentences are true premises
        t_init = np.ones(n) * 0.9 
        if len(prompt_verts) > 0:
            t_init[0] = 1.0 # Anchor first sentence
            
        final_t, distance = self._propagate(W, t_init)
        
        # Hoare Logic Check: Does the candidate satisfy the conclusion?
        # We approximate Q (conclusion) as the last vertex or the candidate match
        base_score = 1.0 - (distance / max(n, 1))
        
        for cand in candidates:
            cand_score = base_score
            reasoning = f"Propagation distance: {distance:.4f}. "
            
            # Check if candidate matches any vertex (simplified Q check)
            cand_lower = cand.lower().strip()
            match_found = False
            
            # Check against extracted vertices
            for i, v in enumerate(prompt_verts):
                if cand_lower in v.lower() or v.lower() in cand_lower:
                    # If candidate aligns with a high-truth vertex
                    if final_t[i] > 0.5:
                        cand_score += self.lambda_hoare * final_t[i]
                        reasoning += f"Matched premise {i} (truth={final_t[i]:.2f}). "
                    match_found = True
                    break
            
            # Hoare Triple Satisfaction: If candidate is explicit conclusion
            # Simulate adding candidate as a new node connected to premises
            if not match_found:
                # Use NCD as tiebreaker for non-structural matches
                ncd_val = self._compute_ncd(prompt, cand)
                cand_score -= (ncd_val * 0.1) # Penalty for high compression distance (dissimilarity)
                reasoning += f"No structural match; NCD penalty applied."

            cand_score = max(0.0, min(1.0, cand_score))
            results.append({
                "candidate": cand,
                "score": round(cand_score, 4),
                "reasoning": reasoning
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation logic."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']