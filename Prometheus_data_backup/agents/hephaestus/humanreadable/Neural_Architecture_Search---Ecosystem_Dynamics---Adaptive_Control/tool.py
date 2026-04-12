class ReasoningTool:
    """
    NAS x Ecosystem Dynamics x Adaptive Control reasoning evaluator.
    
    Parses logical relations into weighted graphs, evolves variants via NAS-style
    mutation, enforces flux conservation across proposition nodes, and adaptively
    tunes weights. Computes numeric/probabilistic answers constructively.
    """
    
    def __init__(self):
        self.alpha, self.beta, self.gamma = 0.4, 0.4, 0.2
        self.pop_size, self.generations = 8, 3
        self.eta = 0.1
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": f"Fitness={score:.3f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        comp_conf = self._computational_confidence(prompt, answer)
        return min(0.85, max(meta_conf, comp_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|why did .+ (fail|stop))', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba \w+', p):
            return 0.25
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and not re.search(r'\b(only|just)\b', p):
            return 0.28
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|measure)\b', p):
            return 0.25
        return 0.5
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        num_match = self._numeric_computation(prompt, answer)
        if num_match is not None:
            return 0.8 if num_match else 0.1
        prob_match = self._probabilistic_computation(prompt, answer)
        if prob_match is not None:
            return 0.75 if prob_match else 0.15
        return 0.4
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        comp_score = self._compute_score(prompt, candidate)
        graph_score = self._graph_fitness(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        return 0.45 * comp_score + 0.45 * graph_score + 0.1 * ncd_score
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        num = self._numeric_computation(prompt, candidate)
        if num is not None:
            return 1.0 if num else 0.0
        prob = self._probabilistic_computation(prompt, candidate)
        if prob is not None:
            return 1.0 if prob else 0.2
        temp = self._temporal_computation(prompt, candidate)
        if temp is not None:
            return 1.0 if temp else 0.1
        return 0.5
    
    def _numeric_computation(self, prompt: str, candidate: str):
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*', candidate)]
        if not c_nums:
            return None
        # Comparison
        if re.search(r'\b(greater|larger|more|higher)\b', prompt.lower()):
            if len(p_nums) >= 2 and c_nums:
                return c_nums[0] == max(p_nums)
        if re.search(r'\b(smaller|less|lower|fewer)\b', prompt.lower()):
            if len(p_nums) >= 2 and c_nums:
                return c_nums[0] == min(p_nums)
        # Arithmetic
        if '+' in prompt or 'sum' in prompt.lower() or 'add' in prompt.lower():
            if len(p_nums) >= 2:
                return abs(c_nums[0] - sum(p_nums)) < 0.01
        if re.search(r'\bproduct\b|multiply', prompt.lower()):
            if len(p_nums) >= 2:
                prod = np.prod(p_nums)
                return abs(c_nums[0] - prod) < 0.01
        # Rate problems
        if re.search(r'\brate\b|\bper\b|\bhour\b|\bday\b', prompt.lower()):
            if len(p_nums) >= 2:
                rate_calc = p_nums[0] / p_nums[1] if p_nums[1] != 0 else 0
                return any(abs(c - rate_calc) < 0.01 for c in c_nums)
        return None
    
    def _probabilistic_computation(self, prompt: str, candidate: str):
        if not re.search(r'\b(probability|likely|chance|percent)\b', prompt.lower()):
            return None
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*', candidate)]
        if not c_nums:
            return None
        # Base rate computation
        if re.search(r'\bbase rate\b|\bprior\b', prompt.lower()) and len(p_nums) >= 2:
            prior = p_nums[0] / 100 if p_nums[0] <= 1 else p_nums[0]
            return any(abs(c - prior) < 0.05 for c in c_nums)
        # Expected value
        if re.search(r'\bexpected\b', prompt.lower()) and len(p_nums) >= 2:
            ev = sum(p_nums) / len(p_nums)
            return any(abs(c - ev) < 0.1 for c in c_nums)
        return None
    
    def _temporal_computation(self, prompt: str, candidate: str):
        if not re.search(r'\b(before|after|first|last|then|next)\b', prompt.lower()):
            return None
        # Extract ordering keywords
        before = re.findall(r'(\w+)\s+before\s+(\w+)', prompt.lower())
        after = re.findall(r'(\w+)\s+after\s+(\w+)', prompt.lower())
        if before and candidate.lower():
            for a, b in before:
                if a in candidate.lower() and b not in candidate.lower():
                    return True
        return None
    
    def _graph_fitness(self, prompt: str, candidate: str) -> float:
        props = self._parse_propositions(prompt + " " + candidate)
        edges = self._parse_relations(prompt + " " + candidate, props)
        if len(props) == 0:
            return 0.5
        V = {p: 1.0 if p.lower() in candidate.lower() else 0.3 for p in props}
        best_fit = 0.0
        for gen in range(self.generations):
            population = [edges.copy() for _ in range(self.pop_size)]
            for i in range(1, len(population)):
                population[i] = self._mutate_edges(population[i])
            fitness = [self._evaluate_graph(V, e) for e in population]
            best_fit = max(fitness)
            best_idx = np.argmax(fitness)
            edges = population[best_idx]
            self.eta *= 1.05 if gen > 0 and best_fit > fitness[0] else 0.95
        return min(1.0, best_fit)
    
    def _parse_propositions(self, text: str) -> list:
        sents = re.split(r'[.!?;]', text)
        props = []
        for s in sents:
            s = s.strip()
            if len(s) > 5 and len(s.split()) <= 8:
                props.append(s)
        return props[:10]
    
    def _parse_relations(self, text: str, props: list) -> np.ndarray:
        edges = []
        t = text.lower()
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j:
                    continue
                w = 0.0
                if re.search(rf'{re.escape(p1.lower())}.*\b(causes|leads to|results in)\b.*{re.escape(p2.lower())}', t):
                    w = 1.0
                elif re.search(rf'{re.escape(p1.lower())}.*\b(before|precedes)\b.*{re.escape(p2.lower())}', t):
                    w = 0.8
                elif re.search(rf'{re.escape(p1.lower())}.*\b(if|implies)\b.*{re.escape(p2.lower())}', t):
                    w = 0.9
                if w > 0:
                    edges.append([i, j, w])
        return np.array(edges) if edges else np.zeros((0, 3))
    
    def _mutate_edges(self, edges: np.ndarray) -> np.ndarray:
        if len(edges) == 0:
            return edges
        e = edges.copy()
        if np.random.rand() < 0.3 and len(e) > 0:
            idx = np.random.randint(len(e))
            e[idx, 2] += np.random.randn() * 0.1
            e[idx, 2] = np.clip(e[idx, 2], 0.1, 1.5)
        return e
    
    def _evaluate_graph(self, V: dict, edges: np.ndarray) -> float:
        if len(edges) == 0:
            return 0.5
        nodes = list(V.keys())
        consistency = self._check_consistency(edges, nodes)
        flux = self._flux_conservation(V, edges)
        return self.alpha * consistency + self.gamma * flux + 0.3
    
    def _check_consistency(self, edges: np.ndarray, nodes: list) -> float:
        violations = 0
        for i in range(len(edges)):
            for j in range(i+1, len(edges)):
                if edges[i,0] == edges[j,0] and edges[i,1] == edges[j,1]:
                    violations += (edges[i,2] - edges[j,2])**2
        return np.exp(-violations)
    
    def _flux_conservation(self, V: dict, edges: np.ndarray) -> float:
        nodes = list(V.keys())
        imbalance = 0.0
        for i, node in enumerate(nodes):
            in_flux = sum(e[2] * V[nodes[int(e[0])]] for e in edges if int(e[1]) == i)
            out_flux = sum(e[2] * V[nodes[int(e[1])]] for e in edges if int(e[0]) == i)
            imbalance += abs(in_flux - out_flux)
        return np.exp(-imbalance / max(1, len(nodes)))
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        def ncd(a, b):
            ca, cb = zlib.compress(a.encode()), zlib.compress(b.encode())
            cab = zlib.compress((a+b).encode())
            return (len(cab) - min(len(ca), len(cb))) / max(len(ca), len(cb))
        return 1.0 - ncd(prompt, candidate)