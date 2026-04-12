import re
import numpy as np

class ReasoningTool:
    """
    A reasoning tool combining Category Theory (functorial mapping), Compositionality,
    and the Free Energy Principle (FEP) for answer scoring.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic propositions and logical relations
       (negation, comparison, conditionals) using regex patterns.
    2. Functorial Mapping: Maps syntactic tokens to a semantic graph (vertices=propositions,
       edges=logical morphisms).
    3. Free Energy Minimization: Treats truth values as variational parameters.
       Minimizes a Free Energy function balancing prediction error (match with prompt)
       and logical consistency (implication constraints).
    4. Scoring: Final score is negative Free Energy (lower energy = higher score).
       NCD is used only as a tiebreaker.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+than\b', r'\bfewer\s+than\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
            'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bcauses\b', r'\btherefore\b'],
            'ordering': [r'\bfirst\b', r'\blast\b', r'\bafter\b', r'\bbefore\b'],
            'connective': [r'\band\b', r'\bor\b', r'\but\b']
        }
        self.eta = 0.01  # Learning rate
        self.steps = 10  # Optimization steps

    def _extract_predicates(self, text):
        """Extract atomic predicates and relations using regex (Compositionality)."""
        text_lower = text.lower()
        predicates = []
        relations = []
        
        # Simple noun-verb-noun extraction approximation
        # Look for patterns like "A is B", "A > B", "if A then B"
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
                
            # Check for specific relation types
            found_rel = False
            
            # Comparatives
            for pat in self.patterns['comparative']:
                if re.search(pat, sent, re.IGNORECASE):
                    # Extract rough subject/object around the pattern
                    parts = re.split(pat, sent, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        subj = parts[0].strip().split()[-1] if parts[0].strip() else "unknown"
                        obj = parts[1].strip().split()[0] if parts[1].strip() else "unknown"
                        predicates.append(f"{subj}_GT_{obj}") # Greater Than relation
                        relations.append(('comp', subj, obj))
                        found_rel = True
                    break
            
            if not found_rel:
                # Negations
                for pat in self.patterns['negation']:
                    if re.search(pat, sent, re.IGNORECASE):
                        # Mark surrounding context as negated
                        predicates.append(f"NEG:{sent[:50]}")
                        found_rel = True
                        break
            
            if not found_rel:
                # Conditionals
                if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['conditional']):
                    predicates.append(f"COND:{sent[:50]}")
                    found_rel = True

            # Fallback: generic proposition
            if not found_rel and len(sent) > 5:
                words = sent.split()
                if len(words) >= 3:
                    predicates.append(f"{words[0]}_{words[-1]}")

        return list(set(predicates)), relations

    def _build_graph(self, prompt, candidate):
        """
        Build the semantic graph G=(V, E).
        Vertices: Propositions from prompt and candidate.
        Edges: Logical morphisms.
        """
        # Combine text for context, but distinguish sources
        full_text = f"{prompt} {candidate}"
        preds, rels = self._extract_predicates(full_text)
        
        # Create unique vertex list
        vertices = list(set(preds))
        n = len(vertices)
        if n == 0:
            return [], [], np.array([]), np.array([])
            
        v_map = {v: i for i, v in enumerate(vertices)}
        
        # Initialize p (observed truth) and q (variational truth)
        # p_i = 1 if in prompt, 0.5 if unknown, 0 if explicitly negated in prompt
        p = np.full(n, 0.5)
        prompt_lower = prompt.lower()
        
        for i, v in enumerate(vertices):
            # Simple heuristic: if vertex substring exists in prompt, assume true (1)
            # If it contains NEG, assume false (0)
            if "NEG:" in v:
                # Check if the core content is in prompt
                core = v.replace("NEG:", "")
                if core.lower() in prompt_lower:
                    p[i] = 0.0 # Explicitly negated in prompt context
            else:
                # Check presence in prompt
                # Very loose matching for demonstration
                if any(part.lower() in prompt_lower for part in v.split('_')):
                    p[i] = 1.0
                else:
                    p[i] = 0.5 # Unknown (candidate only)

        # Build adjacency matrix for implications (A -> B)
        # For this implementation, we assume transitivity among extracted relations
        # and direct implication from prompt assertions to candidate assertions.
        W = np.zeros((n, n))
        
        # Add edges based on extracted relations
        for r_type, subj, obj in rels:
            if r_type == 'comp':
                # Find vertices containing these terms
                idx_subj = [i for i, v in enumerate(vertices) if subj in v]
                idx_obj = [i for i, v in enumerate(vertices) if obj in v]
                for i in idx_subj:
                    for j in idx_obj:
                        if i != j:
                            W[i, j] = 0.8 # Strong implication weight

        # Diagonal self-consistency
        np.fill_diagonal(W, 1.0)
        
        return vertices, p, W

    def _compute_free_energy(self, p, W):
        """
        Compute Free Energy F and minimize it via gradient descent.
        F = Sum((q - p)^2) + Sum(w_ij * max(0, q_i - q_j)^2)
        """
        n = len(p)
        if n == 0:
            return 0.0
            
        q = p.copy() # Initialize q = p
        pi = 1.0 # Uniform precision
        
        for _ in range(self.steps):
            # Prediction Error Term Gradient: 2 * (q - p) * pi
            grad_pred = 2 * (q - p) * pi
            
            # Consistency Term Gradient
            # Term: w_ij * max(0, q_i - q_j)^2
            # Derivative w.r.t q_i: if q_i > q_j: 2 * w_ij * (q_i - q_j)
            # Derivative w.r.t q_j: if q_i > q_j: -2 * w_ij * (q_i - q_j)
            
            grad_cons = np.zeros(n)
            for i in range(n):
                for j in range(n):
                    if W[i, j] > 0:
                        diff = q[i] - q[j]
                        if diff > 0:
                            d_val = 2 * W[i, j] * diff
                            grad_cons[i] += d_val
                            grad_cons[j] -= d_val
            
            total_grad = grad_pred + grad_cons
            q -= self.eta * total_grad
            
            # Clamp q to [0, 1]
            q = np.clip(q, 0, 1)
            
        # Calculate final Free Energy
        pred_err = np.sum((q - p)**2 * pi)
        cons_err = 0.0
        for i in range(n):
            for j in range(n):
                if W[i, j] > 0:
                    diff = q[i] - q[j]
                    if diff > 0:
                        cons_err += W[i, j] * (diff ** 2)
        
        F = pred_err + cons_err
        return -F # Return negative F so higher is better

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_base = prompt.lower()
        
        # Pre-calculate prompt graph components if needed, but here we do per-candidate
        # to handle candidate-specific propositions.
        
        scores = []
        for cand in candidates:
            vertices, p, W = self._build_graph(prompt, cand)
            
            if len(vertices) == 0:
                # Fallback for empty parse
                fe_score = -1.0
            else:
                fe_score = self._compute_free_energy(p, W)
            
            scores.append((cand, fe_score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Handle ties with NCD
        final_results = []
        for i, (cand, score) in enumerate(scores):
            # Check for ties within a small epsilon
            is_tie = False
            if i > 0:
                if abs(score - scores[i-1][1]) < 1e-6:
                    is_tie = True
            
            if is_tie:
                # Use NCD to break tie (lower NCD to prompt is better)
                # Note: In a real tie-breaker scenario we might compare to a hypothetical ideal
                # Here we just use NCD to prompt as a secondary heuristic
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly by NCD (inverted, so lower NCD adds to score)
                score += (1.0 - ncd_val) * 1e-9

            reasoning = f"Free Energy minimized over {len(self._build_graph(prompt, cand)[0])} propositions."
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the free energy score."""
        # Evaluate single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1 range
        # Score is negative free energy. 
        # Theoretically unbounded below, but in practice bounded by our setup.
        # A perfect match (p=q, no conflicts) yields F=0 -> score=0.
        # Errors yield negative scores.
        # We need to normalize. Let's assume worst case F is roughly N (number of props).
        # Normalize: 1 / (1 + |score|) gives a rough probability-like value.
        
        if score >= 0:
            return 1.0
        else:
            # Transform negative score to 0-1
            # e.g., score -10 -> 0.09, score -0.1 -> 0.9
            conf = 1.0 / (1.0 + abs(score))
            return min(1.0, max(0.0, conf))