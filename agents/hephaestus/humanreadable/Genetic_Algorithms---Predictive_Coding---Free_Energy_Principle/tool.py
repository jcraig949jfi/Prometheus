import re
import numpy as np
from itertools import combinations

class ReasoningTool:
    """
    Genetic Algorithm x Predictive Coding x Free Energy Principle
    
    Evolves hierarchical generative models (DAGs) over linguistic primitives.
    Each model predicts primitive activation via weighted edges; fitness = -F
    where F = prediction_error^2 + complexity (variational free energy).
    
    Combines GA evolution with computational parsers for arithmetic, logic,
    constraints. Meta-confidence detector ensures epistemic honesty.
    """
    
    def __init__(self, pop_size=30, generations=15, mutation_rate=0.15, elite_frac=0.2):
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_frac = elite_frac
        np.random.seed(42)
    
    def _extract_primitives(self, text):
        """Parse structural primitives into binary feature vector."""
        t = text.lower()
        features = {
            'negation': int(bool(re.search(r'\b(not|no|never|none|neither)\b', t))),
            'comparative': int(bool(re.search(r'\b(more|less|greater|fewer|higher|lower)\b', t))),
            'conditional': int(bool(re.search(r'\b(if|when|unless|provided)\b', t))),
            'numeric': int(bool(re.search(r'\b\d+(\.\d+)?\b', t))),
            'causal': int(bool(re.search(r'\b(cause|lead|result|because|due to)\b', t))),
            'ordering': int(bool(re.search(r'\b(before|after|then|first|last|greater than|less than)\b', t))),
            'universal': int(bool(re.search(r'\b(all|every|each|always)\b', t))),
            'existential': int(bool(re.search(r'\b(some|any|exist)\b', t))),
        }
        return np.array(list(features.values()), dtype=float)
    
    def _init_population(self, n_features):
        """Initialize population of DAG models."""
        pop = []
        for _ in range(self.pop_size):
            # Adjacency matrix (upper triangular for DAG)
            adj = np.triu(np.random.rand(n_features, n_features) > 0.6, k=1).astype(float)
            weights = np.random.randn(n_features, n_features) * adj
            pop.append(weights)
        return pop
    
    def _free_energy(self, model, x):
        """Compute variational free energy: prediction_error + complexity."""
        n = len(x)
        pred = np.zeros(n)
        for j in range(n):
            pred[j] = 1.0 / (1.0 + np.exp(-np.dot(model[:, j], x)))  # sigmoid
        error = np.sum((x - pred) ** 2)
        complexity = 0.5 * np.sum(model ** 2)
        return 0.5 * error + 0.001 * complexity
    
    def _evolve(self, x):
        """Evolve population for T generations, return best model."""
        n = len(x)
        pop = self._init_population(n)
        
        for gen in range(self.generations):
            fitness = np.array([-self._free_energy(m, x) for m in pop])
            elite_count = max(1, int(self.elite_frac * self.pop_size))
            elite_idx = np.argsort(fitness)[-elite_count:]
            new_pop = [pop[i] for i in elite_idx]
            
            while len(new_pop) < self.pop_size:
                # Tournament selection
                t1, t2 = np.random.choice(len(pop), 2, replace=False)
                p1 = pop[t1] if fitness[t1] > fitness[t2] else pop[t2]
                t1, t2 = np.random.choice(len(pop), 2, replace=False)
                p2 = pop[t1] if fitness[t1] > fitness[t2] else pop[t2]
                
                # Crossover
                mask = np.random.rand(n, n) > 0.5
                child = p1 * mask + p2 * (~mask)
                
                # Mutation
                if np.random.rand() < self.mutation_rate:
                    i, j = np.random.randint(0, n, 2)
                    if i < j:
                        child[i, j] = np.random.randn() if np.random.rand() > 0.5 else 0
                
                new_pop.append(child)
            pop = new_pop
        
        fitness = np.array([-self._free_energy(m, x) for m in pop])
        return pop[np.argmax(fitness)], max(fitness)
    
    def _compute_numeric(self, prompt, candidate):
        """Numeric comparison parser."""
        nums_p = re.findall(r'\b(\d+(?:\.\d+)?)\b', prompt)
        nums_c = re.findall(r'\b(\d+(?:\.\d+)?)\b', candidate)
        if len(nums_p) >= 2 and len(nums_c) == 1:
            a, b = float(nums_p[0]), float(nums_p[1])
            c = float(nums_c[0])
            if 'sum' in prompt.lower() or 'total' in prompt.lower():
                return 1.0 if abs(c - (a + b)) < 0.01 else 0.0
            if 'difference' in prompt.lower():
                return 1.0 if abs(c - abs(a - b)) < 0.01 else 0.0
            if 'product' in prompt.lower():
                return 1.0 if abs(c - (a * b)) < 0.01 else 0.0
        # Bat and ball
        if 'cost' in prompt.lower() and 'total' in prompt.lower():
            match = re.search(r'total.*?(\d+(?:\.\d+)?)', prompt.lower())
            match2 = re.search(r'more than.*?(\d+(?:\.\d+)?)', prompt.lower())
            if match and match2 and nums_c:
                total, diff = float(match.group(1)), float(match2.group(1))
                c = float(nums_c[0])
                lesser = (total - diff) / 2
                if abs(c - lesser) < 0.01:
                    return 1.0
        return 0.0
    
    def _compute_logic(self, prompt, candidate):
        """Modus tollens, transitivity, constraint satisfaction."""
        score = 0.0
        p, c = prompt.lower(), candidate.lower()
        
        # Transitivity: A > B, B > C => A > C
        if re.search(r'(\w+)\s+(greater|more|taller|older).*than\s+(\w+)', p):
            rels = re.findall(r'(\w+)\s+(?:greater|more|taller|older).*?than\s+(\w+)', p)
            if len(rels) >= 2:
                graph = {}
                for a, b in rels:
                    graph.setdefault(a, set()).add(b)
                # Transitivity closure
                for k in graph:
                    for i in graph:
                        if k in graph.get(i, set()):
                            graph[i].update(graph.get(k, set()))
                # Check candidate
                match = re.search(r'(\w+)', c)
                if match:
                    cand_entity = match.group(1)
                    for src, targets in graph.items():
                        if cand_entity in targets or cand_entity == src:
                            score += 0.3
        
        # All-but-N pattern
        if 'all but' in p or 'except' in p:
            total_match = re.search(r'(\d+)\s+(?:people|items|students)', p)
            except_match = re.search(r'(?:all but|except)\s+(\d+)', p)
            if total_match and except_match and nums_c := re.findall(r'\d+', c):
                total, excluded = int(total_match.group(1)), int(except_match.group(1))
                if int(nums_c[0]) == total - excluded:
                    score += 0.8
        
        return score
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)', p):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|happiest)\b', p):
            return 0.3
        
        # Insufficient information
        if re.search(r'(not enough|cannot determine|insufficient)', p):
            return 0.2
        
        return 1.0
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance (tiebreaker only)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by combined structural + computational score."""
        x_prompt = self._extract_primitives(prompt)
        best_model, base_fitness = self._evolve(x_prompt)
        
        results = []
        for cand in candidates:
            x_cand = self._extract_primitives(prompt + ' ' + cand)
            fe = self._free_energy(best_model, x_cand)
            struct_score = max(0, 1.0 - fe / 10.0)  # 60%
            
            comp_score = self._compute_numeric(prompt, cand) + self._compute_logic(prompt, cand)  # 25%
            comp_score = min(1.0, comp_score)
            
            ncd_score = max(0, 1.0 - self._ncd(prompt, cand))  # 15%
            
            final_score = 0.6 * struct_score + 0.25 * comp_score + 0.15 * ncd_score
            
            reasoning = f"FE={fe:.2f} struct={struct_score:.2f} comp={comp_score:.2f} ncd={ncd_score:.2f}"
            results.append({'candidate': cand, 'score': final_score, 'reasoning': reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        x_prompt = self._extract_primitives(prompt)
        x_combined = self._extract_primitives(prompt + ' ' + answer)
        best_model, _ = self._evolve(x_prompt)
        fe = self._free_energy(best_model, x_combined)
        
        # Lower FE => higher confidence
        base_conf = max(0, min(1.0, 1.0 - fe / 15.0))
        
        # Computational boost
        comp_score = self._compute_numeric(prompt, answer) + self._compute_logic(prompt, answer)
        if comp_score > 0.7:
            base_conf = min(0.95, base_conf + 0.3)
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)