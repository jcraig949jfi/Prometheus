from typing import Dict, Tuple

"""
Genetic Algorithm + Gene Regulatory Network + Compositionality Reasoner

Evolves populations of Candidate Answer Graphs (CAGs) where nodes are atomic
propositions and edges are compositional operators. Uses GRN dynamics to prune
unstable structures and constraint satisfaction for fitness evaluation.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple
from forge_primitives import (
    solve_sat, modus_ponens, check_transitivity, negate,
    dag_traverse, topological_sort, confidence_from_agreement,
    information_sufficiency, solve_constraints
)


class ReasoningTool:
    def __init__(self):
        self.pop_size = 40
        self.generations = 30
        self.mutation_rate = 0.1
        self.grn_iterations = 3
        np.random.seed(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        props_prompt = self._parse_propositions(prompt)
        constraints = self._extract_constraints(prompt, props_prompt)
        
        results = []
        for cand in candidates:
            props_cand = self._parse_propositions(cand)
            all_props = list(set(props_prompt + props_cand))
            
            best_fitness = self._evolve_cag(all_props, constraints, prompt, cand)
            comp_score = self._compositional_match(prompt, cand, props_prompt, props_cand)
            ncd = self._ncd(prompt, cand)
            
            score = 0.5 * best_fitness + 0.4 * comp_score + 0.1 * (1 - ncd)
            reasoning = f"GA fitness={best_fitness:.2f}, comp={comp_score:.2f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        props_p = self._parse_propositions(prompt)
        props_a = self._parse_propositions(answer)
        all_props = list(set(props_p + props_a))
        constraints = self._extract_constraints(prompt, props_p)
        
        population_scores = []
        for _ in range(5):
            fit = self._evolve_cag(all_props, constraints, prompt, answer)
            population_scores.append(fit)
        
        agreement_conf = confidence_from_agreement(population_scores)
        comp_match = self._compositional_match(prompt, answer, props_p, props_a)
        
        base_conf = 0.4 * agreement_conf + 0.6 * comp_match
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p_lower):
            return 0.2
        if re.search(r'\bevery .+ (a|an) \b', p_lower) and '?' in prompt:
            return 0.25
        if re.search(r'\b(he|she|they|it)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        if re.search(r'\beither .+ or \b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.25
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.3
        if re.search(r'\b(cannot determine|not enough|insufficient)\b', p_lower):
            return 0.2
        
        return 0.85
    
    def _parse_propositions(self, text: str) -> List[str]:
        props = []
        
        for match in re.finditer(r'(\w+)\s*(>|<|=|>=|<=)\s*(\w+)', text):
            props.append(f"{match.group(1)}{match.group(2)}{match.group(3)}")
        
        for match in re.finditer(r'\b(not|no|never)\s+(\w+)', text.lower()):
            props.append(f"NOT_{match.group(2)}")
        
        for match in re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)[\.\,\;]', text.lower()):
            props.append(f"IF_{match.group(1)[:10]}_THEN_{match.group(2)[:10]}")
        
        for match in re.finditer(r'(\w+)\s+(cause[sd]?|lead[s]? to|result[s]? in)\s+(\w+)', text.lower()):
            props.append(f"CAUSE_{match.group(1)}_{match.group(3)}")
        
        words = re.findall(r'\b[A-Z][a-z]+\b|\b\d+(?:\.\d+)?\b', text)
        props.extend(words[:10])
        
        return props[:15]
    
    def _extract_constraints(self, prompt: str, props: List[str]) -> List[Tuple]:
        constraints = []
        
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i < j and ('>' in p1 or '<' in p1) and ('>' in p2 or '<' in p2):
                    constraints.append(('transitive', i, j))
        
        for i, p in enumerate(props):
            if 'IF_' in p and 'THEN_' in p:
                constraints.append(('implies', i, (i + 1) % len(props)))
        
        return constraints
    
    def _evolve_cag(self, props: List[str], constraints: List[Tuple], prompt: str, cand: str) -> float:
        if len(props) < 2:
            return 0.5
        
        n_nodes = min(len(props), 10)
        population = [self._random_cag(n_nodes) for _ in range(self.pop_size)]
        
        for gen in range(self.generations):
            fitnesses = [self._fitness_cag(cag, constraints, props, prompt, cand) for cag in population]
            elite_idx = np.argsort(fitnesses)[-2:]
            
            new_pop = [population[i] for i in elite_idx]
            
            while len(new_pop) < self.pop_size:
                p1, p2 = self._tournament_select(population, fitnesses, 2)
                c1, c2 = self._crossover(p1, p2)
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                c1 = self._grn_prune(c1)
                c2 = self._grn_prune(c2)
                new_pop.extend([c1, c2])
            
            population = new_pop[:self.pop_size]
        
        final_fits = [self._fitness_cag(cag, constraints, props, prompt, cand) for cag in population]
        return max(final_fits)
    
    def _random_cag(self, n: int) -> np.ndarray:
        adj = np.random.rand(n, n) < 0.3
        adj = np.triu(adj, 1)
        return adj.astype(float)
    
    def _fitness_cag(self, cag: np.ndarray, constraints: List[Tuple], props: List[str], prompt: str, cand: str) -> float:
        n = cag.shape[0]
        
        sat_score = 0
        for ctype, i, j in constraints:
            if i < n and j < n:
                if ctype == 'transitive' and cag[i, j] > 0:
                    sat_score += 1
                elif ctype == 'implies' and cag[i, j] > 0:
                    sat_score += 1
        
        constraint_fit = sat_score / max(len(constraints), 1)
        
        density = np.sum(cag) / (n * n)
        structure_penalty = abs(density - 0.3)
        
        return constraint_fit * 0.7 + (1 - structure_penalty) * 0.3
    
    def _tournament_select(self, pop: List, fits: List[float], k: int) -> Tuple:
        indices = np.random.choice(len(pop), size=k, replace=False)
        winners = sorted(indices, key=lambda i: fits[i], reverse=True)[:2]
        return pop[winners[0]], pop[winners[1]]
    
    def _crossover(self, p1: np.ndarray, p2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        n = min(p1.shape[0], p2.shape[0])
        cut = np.random.randint(1, n)
        
        c1 = p1.copy()
        c2 = p2.copy()
        c1[cut:, :] = p2[cut:, :]
        c2[cut:, :] = p1[cut:, :]
        
        return c1, c2
    
    def _mutate(self, cag: np.ndarray) -> np.ndarray:
        result = cag.copy()
        n = cag.shape[0]
        
        for i in range(n):
            for j in range(i+1, n):
                if np.random.rand() < self.mutation_rate:
                    result[i, j] = 1 - result[i, j]
        
        return result
    
    def _grn_prune(self, cag: np.ndarray) -> np.ndarray:
        n = cag.shape[0]
        activation = np.ones(n) * 0.5
        
        for _ in range(self.grn_iterations):
            new_act = np.zeros(n)
            for i in range(n):
                incoming = np.sum(cag[:, i]) - np.sum(cag[i, :])
                new_act[i] = 1 / (1 + np.exp(-incoming))
            activation = new_act
        
        result = cag.copy()
        for i in range(n):
            if activation[i] < 0.5:
                result[i, :] = 0
                result[:, i] = 0
        
        return result
    
    def _compositional_match(self, prompt: str, cand: str, props_p: List[str], props_a: List[str]) -> float:
        if not props_p or not props_a:
            return 0.3
        
        p_set = set(props_p)
        a_set = set(props_a)
        
        overlap = len(p_set & a_set)
        union = len(p_set | a_set)
        
        jaccard = overlap / max(union, 1)
        
        numeric_match = self._numeric_eval(prompt, cand)
        
        return 0.6 * jaccard + 0.4 * numeric_match
    
    def _numeric_eval(self, prompt: str, cand: str) -> float:
        p_nums = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', cand)]
        
        if p_nums and c_nums:
            if any(cn in p_nums for cn in c_nums):
                return 0.8
            return 0.4
        
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)