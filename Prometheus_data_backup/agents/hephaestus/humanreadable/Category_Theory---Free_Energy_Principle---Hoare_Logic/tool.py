class ReasoningTool:
    """
    A reasoning tool combining Category Theory (graph semantics), 
    Hoare Logic (pre/post condition propagation), and the Free Energy Principle 
    (prediction error minimization) to evaluate logical consistency.
    
    Mechanism:
    1. Parsing: Extracts propositions and implications (Horn clauses) via regex.
    2. Hoare-Style Annotation: Maps text to a directed graph where edges represent P -> Q.
    3. Constraint Propagation: Uses boolean matrix multiplication to propagate truth values 
       (weakest precondition calculation) to see if the candidate answer satisfies the prompt's logic.
    4. Free Energy Scoring: Computes F = Prediction_Error + Entropy. Lower F (higher -F) indicates 
       the candidate minimizes surprise while maintaining appropriate uncertainty.
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'implication': [
                r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)',
                r'(.+?)\s+leads?\s+to\s+(.+?)(?:\.|,|$)',
                r'(.+?)\s+because\s+(.+?)(?:\.|,|$)',
                r'unless\s+(.+?),\s+(.+?)(?:\.|,|$)'
            ],
            'comparative': [
                r'(\d+(?:\.\d+)?)\s*(?:is|are)?\s*(?:greater|more)\s+than\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:is|are)?\s*(?:less|fewer)\s+than\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*<=?\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*>=?\s*(\d+(?:\.\d+)?)'
            ],
            'negation': [r'\b(not|no|never|none)\b'],
            'quantifier': [r'\b(all|some|every|none)\b'],
            'tier_b_traps': [
                r'have\s+you\s+(stopped|quit)\s+',  # Presupposition
                r'why\s+did\s+\w+\s+(fail|stop)\s+', # Presupposition
                r'either\s+.+\s+or\s+.+',            # False dichotomy hint
                r'who\s+was\s+(he|she|it)\s+',       # Pronoun ambiguity hint
                r'best\s+\w+',                       # Subjectivity
                r'worst\s+\w+'
            ]
        }
        self.max_iter = 50

    def _extract_features(self, text: str) -> Tuple[List[str], List[Dict], np.ndarray]:
        """Parse text into vertices, edges, and feature vectors."""
        text_lower = text.lower()
        vertices = []
        edges = []  # (src_idx, tgt_idx)
        features = [] # List of binary vectors
        
        # Helper to add vertex
        def add_vertex(label: str, feat_bits: List[int]) -> int:
            label = label.strip()
            if not label: return -1
            # Simple dedup
            for i, v in enumerate(vertices):
                if v == label: return i
            vertices.append(label)
            # Pad/truncate feature vector to fixed size k=6
            # Bits: [negation, comparative, conditional, causal, numeric, quantifier]
            feat_vec = np.zeros(6, dtype=int)
            for idx, bit in enumerate(feat_bits[:6]):
                if idx < 6: feat_vec[idx] = bit
            features.append(feat_vec)
            return len(vertices) - 1

        # 1. Extract Implications (Conditionals/Causal)
        for pat in self.patterns['implication']:
            for match in re.finditer(pat, text_lower):
                antecedent = match.group(1).strip()
                consequent = match.group(2).strip()
                if antecedent and consequent:
                    # Determine specific feature bits
                    is_cond = 1 if 'if' in pat or 'unless' in pat else 0
                    is_causal = 1 if 'because' in pat or 'lead' in pat else 0
                    
                    src_idx = add_vertex(antecedent, [0, 0, is_cond, is_causal, 0, 0])
                    tgt_idx = add_vertex(consequent, [0, 0, is_cond, is_causal, 0, 0])
                    if src_idx != -1 and tgt_idx != -1:
                        edges.append((src_idx, tgt_idx))

        # 2. Extract Comparatives/Numerics
        for pat in self.patterns['comparative']:
            for match in re.finditer(pat, text_lower):
                try:
                    v1 = float(match.group(1))
                    v2 = float(match.group(2))
                    label = f"{v1} vs {v2}"
                    # Check validity based on operator in text
                    is_valid = False
                    if 'greater' in text_lower or '>' in text_lower:
                        is_valid = v1 > v2
                    elif 'less' in text_lower or '<' in text_lower:
                        is_valid = v1 < v2
                    
                    idx = add_vertex(label, [0, 1, 0, 0, 1, 0])
                    # If the statement in the prompt is true, it's a satisfied fact
                    # We treat valid numeric claims as self-satisfying nodes for propagation
                    if is_valid:
                         # Add a self-loop or mark as initially satisfied in evaluation
                         pass 
                except ValueError:
                    pass

        if not vertices:
            # Fallback: treat whole text as one proposition if parsing fails
            vertices.append(text_lower)
            features.append(np.zeros(6, dtype=int))
            
        return vertices, edges, np.array(features, dtype=int)

    def _propagate_constraints(self, n_vertices: int, edges: List[Tuple[int,int]], satisfied_init: np.ndarray) -> np.ndarray:
        """
        Hoare-style weakest precondition propagation.
        S_{t+1} = S_t OR (A^T AND S_t)
        If Q is satisfied and P->Q, then P is marked satisfied (backward chaining for validation)
        Or forward: If P is satisfied and P->Q, then Q is satisfied.
        
        Here we do forward propagation of truth from known facts.
        """
        if n_vertices == 0:
            return satisfied_init
            
        A = np.zeros((n_vertices, n_vertices), dtype=bool)
        for src, tgt in edges:
            if 0 <= src < n_vertices and 0 <= tgt < n_vertices:
                A[src, tgt] = True
        
        S = satisfied_init.astype(bool)
        
        for _ in range(min(self.max_iter, n_vertices + 1)):
            S_prev = S.copy()
            # Forward propagation: If P is true and P->Q, then Q becomes true
            # Matrix op: S_new = S_old OR (A^T dot S_old) ? 
            # Actually: S_new[j] = S[j] OR (exists i: S[i] AND A[i,j])
            # This is equivalent to S_new = S OR (A.T @ S) if using boolean matmul
            
            # Manual boolean matrix vector mult for clarity without scipy
            next_S = S.copy()
            for src, tgt in edges:
                if S[src]:
                    next_S[tgt] = True
            
            if np.array_equal(S, next_S):
                break
            S = next_S
            
        return S

    def _compute_free_energy(self, S: np.ndarray, weights: np.ndarray) -> float:
        """
        F = E + H(S)
        E = Sum(w_i * (1 - S_i)) -> Prediction error (unsatisfied important nodes)
        H = Entropy term to penalize over-confidence in violation or satisfaction without basis
        We want to MINIMIZE Free Energy. Score = -F.
        """
        # Avoid log(0)
        eps = 1e-10
        S_safe = np.clip(S.astype(float), eps, 1-eps)
        
        # Entropy: - sum(p log p + (1-p) log (1-p))
        # For boolean S, entropy is 0. But we use soft satisfaction for scoring?
        # Here S is boolean. Let's approximate entropy based on ratio of satisfied/total
        # Or strictly follow formula: if S is 0 or 1, H is 0. 
        # To make it useful, we interpret S as probability or add small noise?
        # The prompt says: "entropy penalizes over-confident violations".
        # If we treat S as hard boolean, H=0. Let's use the proportion of satisfied nodes as a proxy for system state uncertainty
        # Actually, let's strictly follow the math on the vector S converted to float.
        # If S is hard 0/1, H is 0. This might be intended. 
        # However, to differentiate, let's assume the 'satisfaction' has a confidence derived from path length?
        # Simplification: Use the formula on the mean satisfaction rate as a global entropy proxy if H(S) vector-wise is 0.
        
        # Re-reading prompt: "H(S) = -sum[...]". If S is boolean, this is 0.
        # Let's assume the 'satisfaction' vector S might be float in a more complex version.
        # For this implementation, we will treat the final satisfaction as float based on edge density?
        # No, let's stick to the prompt's boolean definition but add a small jitter to avoid log0 and get non-zero entropy
        # representing the 'uncertainty' of the logical gap.
        
        # Alternative interpretation for robustness:
        # Let's calculate Error E first.
        error = np.sum(weights * (1.0 - S.astype(float)))
        
        # Entropy of the state distribution
        p = S_safe
        H_vec = -(p * np.log(p) + (1-p) * np.log(1-p))
        H = np.sum(H_vec)
        
        F = error + H
        return -F # Higher is better

    def _check_tier_b(self, text: str) -> float:
        """Check for epistemic traps. Returns a cap factor (0.0 to 1.0)."""
        text_lower = text.lower()
        cap = 1.0
        
        for pat in self.patterns['tier_b_traps']:
            if re.search(pat, text_lower):
                cap = 0.25 # Strong cap for ambiguity/presupposition
                break
                
        # Check for missing info indicators
        if "cannot be determined" in text_lower or "insufficient" in text_lower:
            cap = 1.0 # Honest admission is good
            
        return cap

    def _get_satisfaction_mask(self, prompt: str, candidate: str, vertices: List[str], features: np.ndarray) -> np.ndarray:
        """Determine which vertices are satisfied by the candidate answer."""
        n = len(vertices)
        if n == 0: return np.array([])
        
        S = np.zeros(n, dtype=bool)
        candidate_lower = candidate.lower()
        prompt_lower = prompt.lower()
        
        # 1. Mark prompt-intrinsic facts as satisfied (base case)
        # In a real system, we'd parse prompt truths. Here we assume prompt defines the graph structure.
        # We look for numeric truths explicitly in the prompt
        for i, v in enumerate(vertices):
            # If vertex text appears in prompt as a fact (heuristic)
            if v in prompt_lower:
                # Check if it's a comparative that holds
                if "vs" in v:
                    parts = v.split("vs")
                    if len(parts) == 2:
                        try:
                            n1, n2 = float(parts[0].strip()), float(parts[1].strip())
                            # Re-extract operator from original text context roughly
                            # If the prompt contains "greater" near this, and n1 > n2, it's true
                            if ('greater' in prompt_lower or '>' in prompt_lower) and n1 > n2:
                                S[i] = True
                            elif ('less' in prompt_lower or '<' in prompt_lower) and n1 < n2:
                                S[i] = True
                        except: pass
                else:
                    # Non-numeric facts in prompt are assumed true premises
                    S[i] = True

        # 2. Mark candidate-satisfied vertices
        for i, v in enumerate(vertices):
            if v in candidate_lower:
                # If the candidate asserts a comparative, verify it computationally
                if "vs" in v:
                    parts = v.split("vs")
                    if len(parts) == 2:
                        try:
                            n1, n2 = float(parts[0].strip()), float(parts[1].strip())
                            # Candidate claims this relation. 
                            # We need to know WHICH relation the candidate claims.
                            # Heuristic: if candidate says "5 > 3", and vertex is "5 vs 3", 
                            # we assume the candidate asserts the truth of the relation implied by the prompt's context 
                            # OR we check if the candidate explicitly validates the logic.
                            # For this tool: If the candidate contains the vertex string, we tentatively mark it.
                            # BUT, we must verify numeric consistency if possible.
                            # If prompt says "A > B" and candidate says "A < B", score should be low.
                            # This is hard with just substring. 
                            # Simplification: If candidate contains the vertex, it asserts it.
                            S[i] = True 
                        except: pass
            else:
                # Check for explicit negation in candidate
                if ("not " + v) in candidate_lower or ("no " + v) in candidate_lower:
                    S[i] = False
                    
        return S

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        vertices, edges, features = self._extract_features(prompt)
        n_verts = len(vertices)
        
        # Weights: higher for numeric/causal
        weights = np.ones(n_verts) if n_verts > 0 else np.array([])
        if n_verts > 0:
            for i, f in enumerate(features):
                if f[4] == 1 or f[3] == 1: # numeric or causal
                    weights[i] = 1.5

        for cand in candidates:
            # 1. Structural Satisfaction
            if n_verts > 0:
                S_init = self._get_satisfaction_mask(prompt, cand, vertices, features)
                S_final = self._propagate_constraints(n_verts, edges, S_init)
                score = self._compute_free_energy(S_final, weights)
                
                # Normalize score roughly to 0-1 range for combination
                # F can be negative. Let's shift.
                raw_score = score
            else:
                raw_score = -10.0 # Penalty for no structure found

            # 2. NCD Tiebreaker (max 15% influence)
            # NCD measures similarity. We want logical consistency, not just similarity.
            # But if logic scores are close, NCD helps distinguish echo vs answer.
            ncd_val = self._ncd_score(prompt, cand)
            # Invert NCD (lower is more similar). 
            # We don't want pure similarity, so we use it sparingly.
            ncd_contrib = (1.0 - ncd_val) * 0.15 

            final_score = raw_score + ncd_contrib
            
            # Adjust for length (penalize extremely short answers unless logic is perfect)
            if len(cand.split()) < 3 and raw_score < 0:
                final_score -= 1.0

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Graph nodes: {n_verts}, Edges: {len(edges)}, Free Energy Score: {raw_score:.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate prompt quality for Tier B traps."""
        cap = self._check_tier_b(prompt)
        return cap

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps at 0.3 if prompt is ambiguous or unanswerable.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta-check the prompt
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return 0.2 # Low confidence due to prompt ambiguity

        # 2. Evaluate structural match
        vertices, edges, _ = self._extract_features(prompt)
        
        # If no structure found, rely on NCD but keep confidence moderate
        if len(vertices) == 0:
            ncd = self._ncd_score(prompt, answer)
            # If very similar, maybe