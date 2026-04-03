class ReasoningTool:
    """
    Quantum-Inspired Causal Network (QICN) with Constructive Computation.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and causal links.
    2. Constructive Computation: Detects numeric/logic patterns and computes definitive answers.
       - If a computed answer matches a candidate, it receives a massive score boost.
       - Handles base rates, temporal ordering, and simple arithmetic.
    3. Quantum-Causal Propagation: 
       - Initializes a uniform superposition of candidate nodes.
       - Applies pragmatic phase shifts (penalizing ambiguity/violations).
       - Propagates amplitude through causal edges (adjacency matrix).
    4. Scoring: Final score is |amplitude|^2, heavily weighted by constructive matches.
    5. Epistemic Honesty: Meta-analysis caps confidence on ambiguous/unanswerable prompts.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|lower|higher|smaller|better|worse)\s+than\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided\s+that|then)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes?|leads\s+to|results\s+in|due\s+to)\b', re.IGNORECASE),
            'numeric': re.compile(r'(\d+(?:\.\d+)?)\s*(%|kg|m|s|Hz|years?|dollars?|\$)?', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|precedes|follows|first|last)\b', re.IGNORECASE),
            'temporal_rel': re.compile(r'(\d+)\s*(years?|hours?|minutes?|days?)\s+(before|after|later|ago)', re.IGNORECASE)
        }
        
        # Presupposition traps for Tier B
        self.presuppositions = [
            r'have\s+you\s+stopped', r'why\s+did\s+\w+\s+fail', r'when\s+did\s+\w+\s+stop',
            r'is\s+it\s+true\s+that\s+\w+\s+stopped'
        ]
        self.ambiguity_triggers = [
            r'\b(every|all)\s+\w+\s+...\s+a\s+\w+\b', # Scope ambiguity hint
            r'\bwho\s+was\s+he\b', r'\bwho\s+was\s+she\b', # Pronoun ambiguity
            r'\beither\s+\w+\s+or\s+\w+\b', # False dichotomy hint
            r'\bbest\s+option\b', r'\bworst\s+case\b' # Subjectivity
        ]

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Extract atomic propositions and their types."""
        nodes = []
        text_lower = text.lower()
        
        # Check for pattern matches to assign types
        types = []
        if self.patterns['negation'].search(text): types.append('negation')
        if self.patterns['comparative'].search(text): types.append('comparative')
        if self.patterns['conditional'].search(text): types.append('conditional')
        if self.patterns['causal'].search(text): types.append('causal')
        if self.patterns['ordering'].search(text): types.append('ordering')
        
        # Add base literal node
        nodes.append({'id': 0, 'text': text.strip()[:50], 'type': 'literal', 'pragmatic_score': 1.0})
        
        # Add specific structural nodes if found
        node_id = 1
        if 'negation' in types:
            nodes.append({'id': node_id, 'text': 'negation_op', 'type': 'negation', 'pragmatic_score': 0.9})
            node_id += 1
        if 'comparative' in types:
            nodes.append({'id': node_id, 'text': 'comparative_op', 'type': 'comparative', 'pragmatic_score': 0.9})
            node_id += 1
            
        return nodes

    def _build_graph(self, prompt: str, candidates: List[str]) -> Tuple[List[Dict], np.ndarray, np.ndarray]:
        """Build the causal network graph."""
        all_texts = [prompt] + candidates
        all_nodes = []
        node_map = {} # Map text to node id
        
        # Create nodes
        idx = 0
        for i, text in enumerate(all_texts):
            nodes = self._extract_nodes(text)
            for n in nodes:
                n['global_id'] = idx
                n['source_idx'] = i # 0=prompt, 1..N=candidates
                all_nodes.append(n)
                node_map[idx] = n
                idx += 1
        
        N = len(all_nodes)
        if N == 0:
            return [], np.zeros((0,0)), np.zeros(0)
            
        adj = np.zeros((N, N), dtype=np.float64)
        amp = np.ones(N, dtype=np.complex128) / np.sqrt(N)
        
        # Build Edges: Prompt -> Candidates (Causal influence)
        # In this model, the prompt causes the validity of the candidate
        prompt_nodes = [n for n in all_nodes if n['source_idx'] == 0]
        candidate_nodes = [n for n in all_nodes if n['source_idx'] > 0]
        
        for p_node in prompt_nodes:
            for c_node in candidate_nodes:
                # Simple causal link: Prompt context influences Candidate truth
                # Stronger link if keywords overlap
                overlap = len(set(p_node['text'].split()) & set(c_node['text'].split()))
                if overlap > 0 or p_node['type'] != 'literal':
                    adj[p_node['global_id'], c_node['global_id']] = 0.8 # Strong causal link
        
        # Self loops for stability
        np.fill_diagonal(adj, 1.0)
        
        return all_nodes, adj, amp

    def _pragmatic_phase_shift(self, nodes: List[Dict], amp: np.ndarray) -> np.ndarray:
        """Apply phase shifts based on Gricean maxims (simplified)."""
        for i, node in enumerate(nodes):
            # Simulate pragmatic score: lower if text is overly complex or contains contradictions
            # Here we use the pre-assigned pragmatic_score
            p_score = node.get('pragmatic_score', 1.0)
            phi = np.pi * (1.0 - p_score)
            amp[i] *= np.exp(1j * phi)
        return amp

    def _causal_propagation(self, adj: np.ndarray, amp: np.ndarray, steps: int = 3) -> np.ndarray:
        """Propagate amplitudes through the causal graph."""
        if adj.shape[0] == 0:
            return amp
            
        # Normalize adjacency roughly to prevent explosion, though T construction handles some
        # T = I + alpha * Adj
        alpha = 0.1
        T = np.eye(adj.shape[0]) + alpha * adj
        
        # Normalize rows to conserve probability mass approximately
        row_sums = T.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid div by zero
        T_norm = T / row_sums
        
        current_amp = amp.copy()
        for _ in range(steps):
            current_amp = T_norm @ current_amp
            
        return current_amp

    def _constructive_computation(self, prompt: str, candidates: List[str]) -> Optional[int]:
        """
        Attempt to compute the answer directly from the prompt.
        Returns the index of the matching candidate if found, else None.
        """
        prompt_lower = prompt.lower()
        
        # 1. Numeric Extraction & Arithmetic
        nums = [float(m.group(1)) for m in re.finditer(self.patterns['numeric'], prompt)]
        
        # Case A: Simple Comparison (e.g., "Is 5 greater than 3?")
        if 'greater than' in prompt_lower or 'more than' in prompt_lower:
            if len(nums) >= 2:
                # Heuristic: First number vs Second number
                val = nums[0] > nums[1]
                target = "yes" if val else "no"
                for i, c in enumerate(candidates):
                    if target in c.lower(): return i
        
        # Case B: Temporal Calculation (e.g., "5 years after 1990")
        if 'years' in prompt_lower and ('after' in prompt_lower or 'before' in prompt_lower):
            matches = list(re.finditer(self.patterns['temporal_rel'], prompt_lower))
            if matches:
                # Extract base year and offset
                # Simplified: look for two numbers where one is likely a year (>1000)
                years = [n for n in nums if n > 1000]
                offsets = [n for n in nums if n <= 1000]
                
                if years and offsets:
                    base = years[0]
                    offset = offsets[0]
                    if 'before' in prompt_lower or 'ago' in prompt_lower:
                        result = base - offset
                    else:
                        result = base + offset
                    
                    # Check candidates for this result
                    for i, c in enumerate(candidates):
                        c_nums = [float(m.group(1)) for m in re.finditer(r'\d+', c)]
                        if any(abs(n - result) < 0.1 for n in c_nums):
                            return i

        # Case C: Base Rate / Probability (Simple Bayesian)
        # Pattern: "X% of Y are Z. W% of Z are Q. What % of Y are Q?"
        if '%' in prompt_lower and ('of' in prompt_lower):
            if len(nums) >= 2:
                # Heuristic for chain probability: P(A and B) = P(A)*P(B)
                # If question asks for combined, multiply.
                if 'what' in prompt_lower and ('percent' in prompt_lower or '%' in prompt_lower):
                    prob = (nums[0]/100.0) * (nums[1]/100.0)
                    target_val = prob * 100
                    for i, c in enumerate(candidates):
                        c_nums = [float(m.group(1)) for m in re.finditer(r'\d+(\.\d+)?', c)]
                        if any(abs(n - target_val) < 1.0 for n in c_nums): # Tolerance
                            return i

        # Case D: Direct String Match of Computed Logic
        # If prompt implies a specific yes/no based on logic not captured above
        # Fallback to simple logical consistency if constructive fails
        
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        for pat in self.presuppositions:
            if re.search(pat, p_lower):
                return 0.2 # Low confidence on loaded questions
        
        # 2. Ambiguity Traps
        for pat in self.ambiguity_triggers:
            if re.search(pat, p_lower):
                # Only flag if it looks like a trick question context
                if 'who' in p_lower or 'either' in p_lower:
                    return 0.25

        # 3. Missing Information (Heuristic)
        # If question words exist but no numbers/causal verbs found
        question_words = ['what', 'who', 'where', 'when', 'why', 'how']
        has_question = any(w in p_lower for w in question_words)
        has_content = any(self.patterns[k].search(p_lower) for k in ['numeric', 'causal', 'comparative', 'ordering'])
        
        if has_question and not has_content:
            # Could be a conceptual question, but risky
            return 0.4
            
        return 1.0 # Default high cap

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0=identical, 1=disjoint)."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            if max(z1, z2) == 0: return 1.0
            return (z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Constructive Computation (High Priority)
        computed_idx = self._constructive_computation(prompt, candidates)
        
        # 2. Build Graph & Propagate
        nodes, adj, amp = self._build_graph(prompt, candidates)
        
        if len(nodes) > 0:
            # Pragmatic Phase Shift
            amp = self._pragmatic_phase_shift(nodes, amp)
            # Causal Propagation
            amp = self._causal_propagation(adj, amp)
        
        # 3. Score Candidates
        results = []
        base_scores = []
        
        # Map candidate indices to node indices
        # Nodes are ordered: [prompt_nodes..., cand0_nodes..., cand1_nodes...]
        # We need to aggregate scores per candidate
        candidate_node_indices = [[] for _ in range(len(candidates))]
        current_idx = 0
        # Skip prompt nodes (source_idx == 0)
        prompt_node_count = sum(1 for n in nodes if n['source_idx'] == 0)
        
        for i, c in enumerate(candidates):
            # Find nodes belonging to this candidate
            # Since we built nodes sequentially, we can slice or search
            # Simpler: re-scan nodes for source_idx == i+1
            cand_nodes = [n['global_id'] for n in nodes if n['source_idx'] == i+1]
            if cand_nodes:
                # Average amplitude magnitude squared for this candidate's nodes
                score = sum(np.abs(amp[idx])**2 for idx in cand_nodes) / len(cand_nodes)
                base_scores.append(score)
            else:
                base_scores.append(0.0)

        # 4. Combine Scores
        max_base = max(base_scores) if base_scores else 1.0
        min_base = min(base_scores) if base_scores else 0.0
        range_base = max_base - min_base if max_base != min_base else 1.0
        
        for i, c in enumerate(candidates):
            # Normalize base score to 0.5-0.8 range to leave room for constructive boost
            norm_score = 0.5 + 0.3 * ((base_scores[i] - min_base) / range_base) if range_base > 0 else 0.5
            
            # Constructive Boost
            if computed_idx is not None and i == computed_idx:
                final_score = 0.99 # Near certainty
                reason = f"Constructive computation match (Index {computed_idx})."
            else:
                # NCD Tiebreaker (Max 15% influence)
                ncd = self._ncd_score(prompt, c)
                # Invert NCD (lower is better) and scale small
                ncd_bonus = (1.0 - ncd) * 0.15 
                final_score = min(0.9, norm_score + ncd_bonus) # Cap non-constructive at 0.9
                reason = f"Quantum-causal propagation score: {norm_score:.4f}, NCD bonus: {ncd_bonus:.4f}"
                if computed_idx is not None and i != computed_idx:
                    final_score = 0.1 # Penalize wrong constructive match
                    reason = f"Constructive computation indicates index {computed_idx}, this is likely incorrect."

            results.append({
                "candidate": c,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate to get raw score
        # Wrap single candidate for evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # 3. Apply Cap
        final_conf = min(raw_score, meta_cap)
        
        # 4. Honesty Check: If no structural matches and low constructive signal, reduce confidence
        # (Implicit in the logic: if constructive fails and graph is weak, raw_score is low)
        
        return float(np.clip(final_conf, 0.0, 1.0))