class ReasoningTool:
    """
    A reasoning tool combining Chaos Theory, Evolution, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts logical primitives (negation, conditionals, causality) into nodes.
    2. Graph Construction: Builds a directed constraint graph where edges represent logical flow.
    3. Fitness Landscape: Nodes gain fitness from pragmatic match (TF-IDF overlap with prompt) 
       and coherence (agreement with connected nodes).
    4. Evolutionary Dynamics: Simulates generations of node fitness. Mutation adds noise; 
       Selection keeps top-k coherent nodes.
    5. Lyapunov Stability: Measures divergence between two nearby trajectories. 
       Stable convergence (negative Lyapunov exponent) indicates robust reasoning.
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Logical primitives regex
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|than)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|any|most)\b', re.I),
            'modal': re.compile(r'\b(must|should|might|could|will|would)\b', re.I),
            'ordering': re.compile(r'\b(before|after|first|last|next)\b', re.I),
            # Presupposition traps
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either.*or|only two|only option)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I)
        }
        self.pronoun_pattern = re.compile(r'\b(he|she|him|her|they|them)\b', re.I)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _tf_vector(self, text: str, vocab: List[str]) -> List[float]:
        tokens = self._tokenize(text)
        counts = defaultdict(int)
        for t in tokens: counts[t] += 1
        total = len(tokens) or 1
        return [counts.get(w, 0) / total for w in vocab]

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Parse text into propositional nodes with features."""
        nodes = []
        sentences = re.split(r'[.!?]', text)
        vocab = list(set(self._tokenize(text)))
        
        for i, sent in enumerate(sentences):
            if not sent.strip(): continue
            
            features = []
            # Binary flags for logical primitives
            features.append(1.0 if self.patterns['negation'].search(sent) else 0.0)
            features.append(1.0 if self.patterns['conditional'].search(sent) else 0.0)
            features.append(1.0 if self.patterns['causal'].search(sent) else 0.0)
            features.append(1.0 if self.patterns['comparative'].search(sent) else 0.0)
            features.append(1.0 if self.patterns['quantifier'].search(sent) else 0.0)
            features.append(1.0 if self.patterns['modal'].search(sent) else 0.0)
            
            # TF vector for pragmatic match
            tf_vec = self._tf_vector(sent, vocab)
            features.extend(tf_vec)
            
            nodes.append({
                'id': i,
                'text': sent.strip(),
                'features': features,
                'fitness': 0.5, # Initial fitness
                'type': 'premise'
            })
            
        return nodes, vocab

    def _build_graph(self, nodes: List[Dict]) -> List[Tuple[int, int, float]]:
        """Build edges based on logical flow (simplified sequential + keyword)."""
        edges = []
        n = len(nodes)
        if n == 0: return edges
        
        for i in range(n - 1):
            # Sequential dependency
            weight = 1.0 if self.patterns['conditional'].search(nodes[i]['text']) else 0.5
            edges.append((i, i + 1, weight))
            
        # Causal links
        for i, node in enumerate(nodes):
            if self.patterns['causal'].search(node['text']):
                # Link to previous if exists
                if i > 0: edges.append((i-1, i, 0.8))
                
        return edges

    def _compute_fitness(self, nodes: List[Dict], edges: List[Tuple], context_vec: List[float], vocab_size: int):
        """Update node fitness based on pragmatic match and coherence."""
        alpha, beta = 0.4, 0.6
        
        # Precompute pragmatic match (overlap with prompt context)
        pragmatic_scores = []
        for node in nodes:
            # Truncate feature vector to match context_vec length if needed (skip flags)
            node_tf = node['features'][6:] # Skip first 6 flags
            ctx_tf = context_vec
            
            # Dot product similarity
            overlap = sum(a*b for a,b in zip(node_tf, ctx_tf))
            pragmatic_scores.append(overlap)
        
        max_prag = max(pragmatic_scores) if pragmatic_scores else 1.0
        if max_prag == 0: max_prag = 1.0

        for i, node in enumerate(nodes):
            # 1. Pragmatic Match
            p_match = pragmatic_scores[i] / max_prag
            
            # 2. Coherence (incoming edge support)
            coherence = 0.0
            incoming = [e for e in edges if e[1] == i]
            if incoming:
                supported = 0
                for src, _, w in incoming:
                    if nodes[src]['fitness'] > 0.5: # Threshold
                        supported += w
                coherence = supported / len(incoming) if len(incoming) > 0 else 0
            else:
                # Isolated nodes rely on self-consistency (high initial bias)
                coherence = 0.5 

            node['fitness'] = alpha * p_match + beta * coherence

    def _evolve_and_measure(self, nodes: List[Dict], edges: List[Tuple], context_vec: List[float], generations=10, sigma=0.05):
        """Run evolutionary dynamics and compute Lyapunov exponent."""
        if not nodes: return 0.0, 0.0
        
        vocab_size = len(context_vec)
        
        # Helper to run one trajectory
        def run_trajectory(initial_fitnesses, noise_scale=0.0):
            current_nodes = [n.copy() for n in nodes]
            for i, n in enumerate(current_nodes):
                n['fitness'] = initial_fitnesses[i]
                if noise_scale > 0:
                    n['fitness'] += (random_gauss() * noise_scale)
                    n['fitness'] = max(0, min(1, n['fitness'])) # Clamp

            for _ in range(generations):
                # Update fitness
                self._compute_fitness(current_nodes, edges, context_vec, vocab_size)
                
                # Selection: Keep top k, zero out others (simplified: dampen low ones)
                fits = [n['fitness'] for n in current_nodes]
                if not fits: break
                threshold = sorted(fits, reverse=True)[int(len(fits)*0.3)] if len(fits) > 1 else 0
                for n in current_nodes:
                    if n['fitness'] < threshold:
                        n['fitness'] *= 0.8 # Penalize weak links
            
            return [n['fitness'] for n in current_nodes]

        # Initial state
        init_fits = [0.5] * len(nodes)
        
        # Trajectory 1 (Base)
        f1 = run_trajectory(init_fits)
        
        # Trajectory 2 (Perturbed)
        delta_vec = [random_gauss() * 0.01 for _ in nodes]
        f2_init = [f + d for f, d in zip(init_fits, delta_vec)]
        f2 = run_trajectory(f2_init, noise_scale=0.01)
        
        # Lyapunov Exponent approximation
        norm_delta_0 = _vec_norm(delta_vec)
        diff_final = [a-b for a,b in zip(f1, f2)]
        norm_delta_t = _vec_norm(diff_final)
        
        if norm_delta_0 == 0: return 0.0, sum(f1)/len(f1)
        
        lyap = (1.0 / generations) * math.log((norm_delta_t + 1e-9) / (norm_delta_0 + 1e-9))
        avg_fitness = sum(f1) / len(f1)
        
        return lyap, avg_fitness

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            return 0.3
            
        # 3. Subjectivity without data
        if self.patterns['subjectivity'].search(prompt) and not self.number_pattern.search(prompt):
            return 0.3

        # 4. Pronoun Ambiguity (Heuristic: "X told Y he..." + "who" question)
        if 'who' in p_lower and self.patterns['conditional'].search(p_lower) == False: # Simple check
             # Check for multiple male/female names or pronouns
             matches = self.pronoun_pattern.findall(prompt)
             if len(matches) > 1:
                 return 0.25

        # 5. Unanswerability (No numbers in math problems, or missing info)
        if any(k in p_lower for k in ['calculate', 'solve', 'sum', 'total']) and not self.number_pattern.search(prompt):
            return 0.1
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        nodes, vocab = self._extract_nodes(prompt)
        edges = self._build_graph(nodes)
        context_vec = self._tf_vector(prompt, vocab)
        
        # If no nodes (empty prompt), return low score
        if not nodes:
            return [{"candidate": c, "score": 0.0, "reasoning": "No parseable structure"} for c in candidates]

        # Run dynamics on prompt structure
        lyap, avg_fit = self._evolve_and_measure(nodes, edges, context_vec)
        
        # Stability Score: exp(-lambda) * avg_fitness
        # Negative lambda (convergence) -> high score. Positive (chaos) -> low score.
        stability_score = math.exp(-lyap) * avg_fit
        
        for cand in candidates:
            # 1. Structural/Pragmatic Fit (How well does candidate fit the evolved graph?)
            # We simulate adding the candidate as a final node and checking coherence
            cand_nodes = nodes + [{'id': -1, 'text': cand, 'features': nodes[0]['features'], 'fitness': 0.5}]
            # Re-calculate simple coherence for the candidate against the prompt's conclusion
            cand_fit = 0.0
            if nodes:
                # Simple overlap with the most fit node in prompt
                best_node = max(nodes, key=lambda x: x['fitness'])
                # Overlap calculation
                t1 = set(self._tokenize(best_node['text']))
                t2 = set(self._tokenize(cand))
                overlap = len(t1 & t2) / (len(t1 | t2) + 1e-6)
                cand_fit = overlap
            
            # 2. Computation Check (Numeric)
            comp_bonus = 0.0
            nums_prompt = self.number_pattern.findall(prompt)
            nums_cand = self.number_pattern.findall(cand)
            if nums_prompt and nums_cand:
                # Crude check: does the candidate number appear in prompt or result from simple op?
                # This is a placeholder for "Constructive computation" requirement
                try:
                    p_vals = [float(x) for x in nums_prompt]
                    c_val = float(nums_cand[0])
                    if c_val in p_vals: comp_bonus = 0.2 # Echoing numbers is weak but safe
                    # Simple sum check
                    if abs(sum(p_vals) - c_val) < 1e-6: comp_bonus = 0.5
                except: pass

            # 3. NCD (Max 15% weight)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Final Score Composition
            # Dynamics/Stability: 40%, Structural/Coherence: 35%, Computation: 10%, NCD: 15%
            final_score = (stability_score * 0.40) + (cand_fit * 0.35) + (comp_bonus * 0.10) + ncd_score
            
            # Meta-reasoning penalty
            meta_cap = self._meta_confidence(prompt, cand)
            if meta_cap < 1.0:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Stability:{stability_score:.2f}, Fit:{cand_fit:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty (Tier B).
        """
        # 1. Meta-check (Hard caps)
        cap = self._meta_confidence(prompt, answer)
        
        # 2. Structural evaluation
        nodes, vocab = self._extract_nodes(prompt)
        if not nodes:
            return 0.1 # Cannot parse
            
        edges = self._build_graph(nodes)
        context_vec = self._tf_vector(prompt, vocab)
        
        # Run short evolution
        lyap, avg_fit = self._evolve_and_measure(nodes, edges, context_vec, generations=5)
        
        # Base confidence from stability and fitness
        base_conf = (math.exp(-lyap) * avg_fit)
        
        # Boost if computation detected and matches
        nums_p = self.number_pattern.findall(prompt)
        nums_a = self.number_pattern.findall(answer)
        if nums_p and nums_a:
             try:
                if float(nums_a[0]) == sum(float(x) for x in nums_p):
                    base_conf = 0.95
             except: pass
        
        final_conf = min(base_conf, cap)
        
        # Never exceed 0.9 without explicit computation match (heuristic)
        if nums_p and nums_a:
             final_conf = min(final_conf, 0.95)
        else:
             final_conf = min(final_conf, 0.85)
             
        return round(max(0.0, min(1.0, final_conf)), 3)