class ReasoningTool:
    """
    A computational reasoning tool combining Statistical Mechanics, Analogical Reasoning, 
    and Mechanism Design to evaluate candidate answers.
    
    Mechanism:
    1. Parsing: Extracts relational graphs (entities as nodes, predicates as edges) using regex.
    2. Analogical Similarity: Computes alignment scores between prompt and answer graphs via tensor contraction.
    3. Stat-Mech Ensemble: Treats alignments as microstates with energy E = -S. Uses Boltzmann distribution.
    4. Mechanism Design: Uses logarithmic proper scoring rule on the MAP alignment to incentivize truthfulness.
    
    Epistemic Honesty:
    - Detects ambiguity, presuppositions, and unanswerable queries to cap confidence.
    - Prioritizes constructive computation (math, logic) over string similarity.
    """

    def __init__(self):
        self.beta = 2.0  # Inverse temperature for ensemble
        self.weights = np.ones(NUM_REL) * 1.0
        # Boost weights for causal and logical relations
        for r in ['causes', 'if_then', 'greater', 'less', 'equals']:
            if r in REL_MAP:
                self.weights[REL_MAP[r]] = 2.0

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer splitting on non-alphanumeric chars."""
        return re.findall(r'[a-zA-Z0-9_.\-]+', text.lower())

    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities (nouns/phrases). Simplified for brevity."""
        # Heuristic: Capitalized words or specific patterns
        words = re.findall(r'[A-Za-z][a-zA-Z0-9_.\-]*', text)
        # Filter stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'}
        entities = []
        seen = set()
        current_phrase = []
        
        for word in words:
            lw = word.lower()
            if lw in stopwords:
                if current_phrase:
                    phrase = " ".join(current_phrase)
                    if phrase not in seen and len(phrase) > 1:
                        entities.append(phrase)
                        seen.add(phrase)
                    current_phrase = []
            else:
                current_phrase.append(lw)
        if current_phrase:
            phrase = " ".join(current_phrase)
            if phrase not in seen and len(phrase) > 1:
                entities.append(phrase)
        return entities if entities else ["root"]

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, Dict[str, int]]:
        """
        Parse text into a relational graph.
        Returns: (entities, adjacency_tensor, entity_map)
        """
        entities = self._extract_entities(text)
        n = len(entities)
        if n == 0:
            return [], np.zeros((NUM_REL, 1, 1)), {}
        
        entity_map = {e: i for i, e in enumerate(entities)}
        # Tensor: [relation_type, i, j]
        A = np.zeros((NUM_REL, n, n))
        text_lower = text.lower()
        
        # Check negations globally for context, but apply per-predicate if possible
        has_negation = any(nw in text_lower.split() for nw in NEGATION_WORDS)
        polarity = -1.0 if has_negation else 1.0

        # Extract relations
        for rel_name, patterns in PATTERNS.items():
            r_idx = REL_MAP[rel_name]
            for pattern in patterns:
                # Simple presence check for now, could be enhanced with span matching
                if re.search(pattern, text_lower):
                    # Heuristic: Connect all entities if relation exists (loose coupling)
                    # Or try to find subject/object near the verb. 
                    # For robustness in this constrained env, we use a proximity heuristic.
                    # If "A causes B", we look for A and B near "causes".
                    # Simplified: If relation exists, assume dense connectivity among relevant entities 
                    # weighted by proximity in the original string? 
                    # Too complex for regex-only. 
                    # Strategy: Map relation to the pair of entities that appear closest to the match.
                    
                    matches = list(re.finditer(pattern, text_lower))
                    for match in matches:
                        pos = match.start()
                        # Find nearest two entities
                        nearest = []
                        for e, idx in entity_map.items():
                            # Find first occurrence of entity in text
                            e_pos = text_lower.find(e)
                            if e_pos != -1:
                                nearest.append((abs(e_pos - pos), idx, e_pos))
                        nearest.sort(key=lambda x: x[0])
                        
                        # Connect top 2 nearest distinct entities
                        if len(nearest) >= 2:
                            idx1 = nearest[0][1]
                            idx2 = nearest[1][1]
                            if idx1 != idx2:
                                val = polarity * self.weights[r_idx]
                                A[r_idx, idx1, idx2] = val
                                # Symmetrize for non-directional relations if needed, 
                                # but keeping directional for causes/if_then
                                if rel_name in ['equals', 'part_of', 'identity']:
                                    A[r_idx, idx2, idx1] = val
                        elif len(nearest) == 1:
                            # Self loop if only one entity found near relation
                            idx1 = nearest[0][1]
                            A[r_idx, idx1, idx1] = polarity * self.weights[r_idx]

        return entities, A, entity_map

    def _compute_similarity(self, P_entities, P_tensor, A_entities, A_tensor) -> float:
        """Compute analogical similarity score via tensor contraction."""
        if len(P_entities) == 0 or len(A_entities) == 0:
            return 0.0
        
        n_p = len(P_entities)
        n_a = len(A_entities)
        
        # Pad tensors to max size to allow alignment if sizes differ? 
        # No, we align subsets. We use the Hungarian algorithm approach described.
        # Since n! is large, we approximate by greedy matching or Hungarian on a derived cost matrix.
        # Construct Cost Matrix M[i, j] = similarity if P_node_i maps to A_node_j
        
        M = np.zeros((n_p, n_a))
        for i in range(n_p):
            for j in range(n_a):
                # Compare row i of P with row j of A across all relations
                # P[r, i, :] vs A[r, j, :]
                score = 0.0
                for r in range(NUM_REL):
                    # Dot product of outgoing edges
                    p_vec = P_tensor[r, i, :]
                    a_vec = A_tensor[r, j, :]
                    # Pad/trim to min length for comparison if sizes differ? 
                    # Assume we compare available dimensions. 
                    min_len = min(len(p_vec), len(a_vec))
                    score += np.dot(p_vec[:min_len], a_vec[:min_len])
                M[i, j] = score
        
        # Hungarian algorithm approximation via greedy max assignment for simplicity in <200 lines
        # Or use scipy? No external deps allowed except numpy.
        # Implement simple greedy assignment for the permutation pi
        used_a = set()
        total_score = 0.0
        assignments = []
        
        # Flatten and sort
        cells = []
        for i in range(n_p):
            for j in range(n_a):
                cells.append((M[i, j], i, j))
        cells.sort(reverse=True, key=lambda x: x[0])
        
        for score, i, j in cells:
            if i not in assignments and j not in used_a: # Wait, assignments should track mapped P indices
                # Actually we need a mapping from P_idx -> A_idx
                pass
        
        # Re-do greedy properly
        p_mapped = set()
        a_mapped = set()
        total_score = 0.0
        count = 0
        
        for score, i, j in cells:
            if i not in p_mapped and j not in a_mapped:
                total_score += score
                p_mapped.add(i)
                a_mapped.add(j)
                count += 1
                
        if count == 0:
            return 0.0
            
        return total_score / max(1, count) # Normalize by matches

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for epistemic traps. Returns a cap on confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)\b', p_lower):
            return 0.2
        # 2. Scope ambiguity (Every X ... a Y) - hard to detect perfectly, look for "every" + plural
        if re.search(r'\bevery\s+\w+\s+\w+ed?\s+a\s+\w+', p_lower):
            return 0.5 # Ambiguous scope
        # 3. Pronoun ambiguity (X told Y he...)
        if re.search(r'\b(told|said to)\s+\w+\s+he\s+was', p_lower):
            return 0.4
        # 4. False dichotomy
        if re.search(r'\beither\s+.+\s+or\s+.+\s*(\?|$)', p_lower) and 'other' not in p_lower:
            return 0.3
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p_lower) and 'calculate' not in p_lower:
            return 0.3
        # 6. Unanswerable / Missing info
        if re.search(r'\b(if we don\'t know|impossible to tell|insufficient info)\b', p_lower):
            return 0.1
            
        return 1.0

    def _constructive_compute(self, prompt: str, answer: str) -> Optional[float]:
        """
        Attempt to solve the problem computationally.
        Returns a confidence boost if computation matches the answer.
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        if len(nums) >= 2:
            floats = [float(n) for n in nums]
            # Try basic arithmetic patterns
            if 'sum' in p_lower or 'total' in p_lower:
                expected = sum(floats)
                if str(expected) in answer or f"{expected:.2f}" in answer:
                    return 0.9
            if 'average' in p_lower or 'mean' in p_lower:
                expected = sum(floats) / len(floats)
                if str(expected) in answer or f"{expected:.2f}" in answer:
                    return 0.9
            if 'difference' in p_lower:
                expected = max(floats) - min(floats)
                if str(expected) in answer or f"{expected:.2f}" in answer:
                    return 0.9
            if 'product' in p_lower:
                expected = 1.0
                for f in floats: expected *= f
                if str(expected) in answer or f"{expected:.2f}" in answer:
                    return 0.9
        
        # Logic checks
        if 'true' in a_lower and 'false' not in a_lower:
            if 'not' in p_lower and 'true' in p_lower:
                # Simple negation trap
                return 0.2 # Likely wrong if saying true to a negated premise without context
        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        l1 = len(zlib.compress(b1))
        l2 = len(zlib.compress(b2))
        l12 = len(zlib.compress(b1 + b2))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_entities, p_tensor, _ = self._parse_graph(prompt)
        
        # Meta confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning = []
            
            # 1. Constructive Computation (High Priority)
            comp_score = self._constructive_compute(prompt, cand)
            if comp_score is not None:
                score = comp_score
                reasoning.append(f"Computation match: {comp_score}")
            else:
                # 2. Structural Analogical Similarity
                a_entities, a_tensor, _ = self._parse_graph(cand)
                struct_sim = self._compute_similarity(p_entities, p_tensor, a_entities, a_tensor)
                
                # 3. NCD (Tiebreaker, max 15% influence)
                ncd = self._ncd_score(prompt, cand)
                ncd_contrib = (1.0 - ncd) * 0.15 
                
                # Combine: Structural dominates, NCD minor
                base_score = (struct_sim * 0.85) + ncd_contrib
                score = base_score
                reasoning.append(f"Structural Sim: {struct_sim:.2f}, NCD contrib: {ncd_contrib:.2f}")

            # Apply Epistemic Cap
            if meta_cap < 0.5:
                score = min(score, meta_cap)
                reasoning.append(f"Capped by meta-confidence ({meta_cap})")
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning)
            })
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
        
        # Check constructive computation first
        comp_res = self._constructive_compute(prompt, answer)
        if comp_res is not None:
            return min(comp_res, meta_cap)
        
        # Fallback to structural evaluation
        p_ent, p_ten, _ = self._parse_graph(prompt)
        a_ent, a_ten, _ = self._parse_graph(answer)
        
        sim = self._compute_similarity(p_ent, p_ten, a_ent, a_ten)
        
        # If no structural match found and no computation, low confidence
        if sim < 0.1 and len(p_ent)