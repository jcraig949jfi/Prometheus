from typing import Dict, List

class ReasoningTool:
    """
    Genetic Algorithm with Attention Mechanisms over Pragmatic Proposition Graphs.
    
    Maintains a population of candidate interpretations, each represented as a directed
    graph of propositions extracted via regex. Attention weights are evolved via GA to
    focus on high-value nodes. Fitness combines pragmatic constraints (Gricean maxims)
    with structural and computational verification.
    """
    
    def __init__(self):
        self.pop_size = 12
        self.generations = 8
        self.mutation_rate = 0.3
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._ga_score(prompt, cand)
            reasoning = self._explain(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score = self._ga_score(prompt, answer)
        return min(meta_conf, score)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'(have you|did you) (stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ .{5,50} a \w+', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|were)', p_lower) and re.search(r'who|which person', p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r'either .{3,30} or .{3,30}[.?]', p_lower):
            if 'only' not in p_lower:
                return 0.25
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|better|worse)', p_lower):
            if not re.search(r'(measure|metric|criteri|most|least|more|less|faster|slower|cheaper)', p_lower):
                return 0.25
        
        return 0.75
    
    def _ga_score(self, prompt: str, answer: str) -> float:
        # Extract proposition graphs
        p_graph = self._extract_graph(prompt)
        a_graph = self._extract_graph(answer)
        
        # Try specialized parsers first (constructive computation)
        comp_score = self._computational_score(prompt, answer)
        if comp_score >= 0:
            struct_score = self._structural_match(p_graph, a_graph)
            ncd = self._ncd(prompt, answer)
            return 0.6 * comp_score + 0.3 * struct_score + 0.1 * (1 - ncd)
        
        # GA evolution
        population = [self._random_individual(a_graph) for _ in range(self.pop_size)]
        
        for gen in range(self.generations):
            fitness = [self._fitness(ind, p_graph, a_graph, prompt, answer) for ind in population]
            new_pop = []
            for _ in range(self.pop_size):
                p1 = self._tournament(population, fitness)
                p2 = self._tournament(population, fitness)
                child = self._crossover(p1, p2)
                child = self._mutate(child)
                new_pop.append(child)
            population = new_pop
        
        final_fitness = [self._fitness(ind, p_graph, a_graph, prompt, answer) for ind in population]
        return max(final_fitness)
    
    def _extract_graph(self, text: str) -> Dict:
        nodes = []
        edges = []
        
        # Negations
        for m in re.finditer(r'(not|no|never|none)\s+(\w+)', text.lower()):
            nodes.append(('neg', m.group(2)))
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer|larger|smaller|higher|lower)\s+than\s+(\w+)', text.lower()):
            nodes.append(('comp', m.group(1), m.group(2), m.group(3)))
        
        # Numeric values
        for m in re.finditer(r'(\d+\.?\d*)', text):
            nodes.append(('num', float(m.group(1))))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.{3,40}?)\s+then\s+(.{3,40}?)[\.,]', text.lower()):
            premise = m.group(1).strip()
            conclusion = m.group(2).strip()
            nodes.append(('cond', premise, conclusion))
            edges.append((premise, conclusion, 'implies'))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(causes?|leads? to|results? in|produces?)\s+(\w+)', text.lower()):
            nodes.append(('causal', m.group(1), m.group(3)))
            edges.append((m.group(1), m.group(3), 'causes'))
        
        # Temporal
        for m in re.finditer(r'(\w+)\s+(before|after|first|last|earlier|later)\s+(\w+)', text.lower()):
            nodes.append(('temporal', m.group(1), m.group(2), m.group(3)))
        
        return {'nodes': nodes, 'edges': edges, 'text': text}
    
    def _random_individual(self, graph: Dict) -> Dict:
        n_nodes = len(graph['nodes']) if graph['nodes'] else 1
        weights = [random.random() for _ in range(n_nodes)]
        total = sum(weights)
        weights = [w/total for w in weights] if total > 0 else [1.0/n_nodes] * n_nodes
        return {'weights': weights, 'graph': graph}
    
    def _fitness(self, ind: Dict, p_graph: Dict, a_graph: Dict, prompt: str, answer: str) -> float:
        nodes = ind['graph']['nodes']
        weights = ind['weights']
        
        if not nodes:
            return 0.5
        
        total_score = 0
        for i, node in enumerate(nodes):
            w = weights[i] if i < len(weights) else 0
            s = self._pragmatic_score(node, p_graph, a_graph, prompt, answer)
            total_score += w * s
        
        return min(1.0, total_score)
    
    def _pragmatic_score(self, node, p_graph: Dict, a_graph: Dict, prompt: str, answer: str) -> float:
        score = 0
        
        # Literal match (Quantity)
        node_str = str(node).lower()
        prompt_lower = prompt.lower()
        answer_lower = answer.lower()
        
        tokens = re.findall(r'\w+', node_str)
        matches = sum(1 for t in tokens if t in prompt_lower)
        if tokens:
            score += 0.3 * (matches / len(tokens))
        
        # Quality: check contradictions
        if node[0] == 'neg':
            pos_form = node[1]
            if any(pos_form in str(n).lower() for n in a_graph['nodes'] if n[0] != 'neg'):
                score -= 0.2
        
        # Relation: edge matching
        for edge in a_graph['edges']:
            for p_edge in p_graph['edges']:
                if edge[2] == p_edge[2]:
                    score += 0.2
        
        # Manner: brevity bonus
        if len(answer) < 100:
            score += 0.1
        
        return max(0, min(1, score))
    
    def _tournament(self, population: List, fitness: List) -> Dict:
        i1, i2 = random.sample(range(len(population)), 2)
        return population[i1] if fitness[i1] > fitness[i2] else population[i2]
    
    def _crossover(self, p1: Dict, p2: Dict) -> Dict:
        w1, w2 = p1['weights'], p2['weights']
        child_w = [(w1[i] + w2[i])/2 if i < len(w1) and i < len(w2) else 0.5 for i in range(max(len(w1), len(w2)))]
        return {'weights': child_w, 'graph': p1['graph']}
    
    def _mutate(self, ind: Dict) -> Dict:
        if random.random() < self.mutation_rate:
            weights = ind['weights'][:]
            if weights:
                idx = random.randint(0, len(weights)-1)
                weights[idx] += random.gauss(0, 0.1)
                total = sum(weights)
                weights = [w/total for w in weights] if total > 0 else weights
            ind['weights'] = weights
        return ind
    
    def _structural_match(self, p_graph: Dict, a_graph: Dict) -> float:
        if not p_graph['nodes']:
            return 0.5
        
        match_count = 0
        for a_node in a_graph['nodes']:
            for p_node in p_graph['nodes']:
                if a_node[0] == p_node[0]:
                    match_count += 1
                    break
        
        return match_count / max(len(p_graph['nodes']), 1)
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        # Numeric comparison
        nums_p = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', prompt)]
        nums_a = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', answer)]
        
        if len(nums_p) == 2 and re.search(r'which.*?(greater|larger|bigger|more)', prompt.lower()):
            correct = max(nums_p)
            if nums_a and abs(nums_a[0] - correct) < 0.01:
                return 0.95
            if str(correct) in answer:
                return 0.9
        
        # Bat and ball problem
        if re.search(r'cost.*?together.*?([\d.]+)', prompt.lower()):
            total_m = re.search(r'([\d.]+)', prompt)
            diff_m = re.search(r'more than.*?([\d.]+)', prompt)
            if total_m and diff_m:
                total, diff = float(total_m.group(1)), float(diff_m.group(1))
                ball = (total - diff) / 2
                if nums_a and abs(nums_a[0] - ball) < 0.01:
                    return 0.95
        
        # Negation/modus tollens
        if re.search(r'not.*?all', prompt.lower()) and re.search(r'some.*?not', answer.lower()):
            return 0.8
        
        return -1
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)
    
    def _explain(self, prompt: str, answer: str) -> str:
        comp = self._computational_score(prompt, answer)
        if comp >= 0:
            return f"Computational match (score: {comp:.2f})"
        
        p_graph = self._extract_graph(prompt)
        a_graph = self._extract_graph(answer)
        
        if p_graph['nodes'] and a_graph['nodes']:
            return f"Structural match: {len(a_graph['nodes'])} propositions extracted"
        return "Pragmatic GA evaluation"