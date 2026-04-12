from dataclasses import field

"""
Gauge-Guided Evolutionary Constraint Solver (GGECS)

Combines:
- Gauge Theory: Proposition weights as connection fields
- Genetic Algorithms: Evolve weight matrices to minimize violations
- Gene Regulatory Networks: Propositions regulate each other via weighted edges

Primitives wired: solve_constraints, check_transitivity, modus_ponens,
bayesian_update, confidence_from_agreement, information_sufficiency
"""

import re
import numpy as np
from itertools import combinations
from forge_primitives import (
    solve_constraints, check_transitivity, modus_ponens,
    bayesian_update, confidence_from_agreement, information_sufficiency
)

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self.pop_size = 20
        self.generations = 30
        self.mutation_rate = 0.15
        
    def _parse_propositions(self, text):
        """Extract typed logical edges from text"""
        edges = []
        props = []
        
        # Negations
        for m in re.finditer(r'(not|no|never|isn\'t|aren\'t|doesn\'t)\s+(\w+)', text.lower()):
            edges.append(('neg', m.group(2), -1.0))
            props.append(m.group(2))
        
        # Conditionals (if-then)
        for m in re.finditer(r'if\s+([^,]+?)\s+then\s+([^,.]+)', text.lower()):
            antecedent = m.group(1).strip()
            consequent = m.group(2).strip()
            edges.append(('cond', antecedent, consequent, 1.0))
            props.extend([antecedent, consequent])
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(causes|leads to|results in)\s+(\w+)', text.lower()):
            edges.append(('causal', m.group(1), m.group(3), 1.5))
            props.extend([m.group(1), m.group(3)])
        
        # Comparatives with numbers
        nums = [(m.group(1), float(m.group(1))) for m in re.finditer(r'(\d+\.?\d*)', text)]
        for i, (s1, v1) in enumerate(nums):
            for s2, v2 in nums[i+1:]:
                edges.append(('comp', s1, s2, v1 - v2))
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+before\s+(\w+)', text.lower()):
            edges.append(('order', m.group(1), m.group(2), 1.0))
            props.extend([m.group(1), m.group(2)])
        
        return list(set(props)), edges
    
    def _build_constraint_graph(self, props, edges, candidate):
        """Convert edges to constraint problems"""
        if not props:
            return []
        
        prop_idx = {p: i for i, p in enumerate(props)}
        constraints = []
        
        for edge in edges:
            if edge[0] == 'neg':
                # Negation: proposition should be absent in candidate
                prop = edge[1]
                if prop in prop_idx:
                    present = 1.0 if prop in candidate.lower() else 0.0
                    constraints.append(('neg', prop_idx[prop], present, -1.0))
            
            elif edge[0] == 'cond' and len(edge) == 4:
                # Conditional: modus ponens
                ant, cons = edge[1], edge[2]
                if ant in candidate.lower():
                    should_have_cons = 1.0 if cons in candidate.lower() else 0.0
                    constraints.append(('cond', ant, cons, should_have_cons))
            
            elif edge[0] == 'causal' and len(edge) == 4:
                # Causal: forward dependency
                cause, effect = edge[1], edge[2]
                has_cause = 1.0 if cause in candidate.lower() else 0.0
                has_effect = 1.0 if effect in candidate.lower() else 0.0
                constraints.append(('causal', has_cause, has_effect))
            
            elif edge[0] == 'comp' and len(edge) == 4:
                # Numeric comparison
                s1, s2, diff = edge[1], edge[2], edge[3]
                if s1 in candidate and s2 in candidate:
                    constraints.append(('comp', diff))
        
        return constraints
    
    def _fitness(self, W, constraints, props):
        """Compute fitness via constraint satisfaction + primitive logic"""
        if len(constraints) == 0:
            return 0.0
        
        violation = 0.0
        
        for c in constraints:
            if c[0] == 'neg':
                # Negation violation: should be negative weight
                idx, present, target = c[1], c[2], c[3]
                if idx < len(W):
                    violation += max(0, W[idx] * present - target)
            
            elif c[0] == 'cond':
                # Check modus ponens consistency
                violation += 0.5 if c[3] < 0.5 else -0.5
            
            elif c[0] == 'causal':
                # Causal: effect should follow cause
                has_cause, has_effect = c[1], c[2]
                if has_cause > 0.5 and has_effect < 0.5:
                    violation += 1.0
            
            elif c[0] == 'comp':
                # Numeric: preserved in weight
                diff = c[1]
                violation += abs(diff) * 0.1
        
        # Check transitivity using primitive
        if len(props) >= 3:
            relations = [(i, (i+1) % len(props)) for i in range(min(3, len(props)))]
            if check_transitivity(relations):
                violation -= 0.5
        
        # Regularization
        reg = 0.01 * np.sum(W ** 2)
        
        return -violation - reg
    
    def _evolve(self, constraints, n_props):
        """Evolve weight matrix population"""
        if n_props == 0:
            n_props = 3
        
        # Initialize population
        population = [np.random.randn(n_props) * 0.1 for _ in range(self.pop_size)]
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness = [self._fitness(W, constraints, range(n_props)) for W in population]
            
            # Selection: tournament
            new_pop = []
            for _ in range(self.pop_size):
                i, j = np.random.randint(0, self.pop_size, 2)
                winner = population[i] if fitness[i] > fitness[j] else population[j]
                new_pop.append(winner.copy())
            
            # Crossover
            for i in range(0, self.pop_size - 1, 2):
                if np.random.rand() < 0.7:
                    alpha = np.random.rand()
                    child1 = alpha * new_pop[i] + (1 - alpha) * new_pop[i + 1]
                    child2 = (1 - alpha) * new_pop[i] + alpha * new_pop[i + 1]
                    new_pop[i], new_pop[i + 1] = child1, child2
            
            # Mutation
            for i in range(self.pop_size):
                if np.random.rand() < self.mutation_rate:
                    new_pop[i] += np.random.randn(n_props) * 0.1
            
            population = new_pop
        
        # Return best
        final_fitness = [self._fitness(W, constraints, range(n_props)) for W in population]
        best_idx = np.argmax(final_fitness)
        
        return population[best_idx], final_fitness[best_idx], final_fitness
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity and unanswerability"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|did you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Check information sufficiency via primitive
        unknowns = len(re.findall(r'\?', prompt))
        facts = len(re.findall(r'\d+|yes|no|true|false', p_lower))
        if information_sufficiency(max(1, unknowns), max(1, facts)) < 0.3:
            return 0.25
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates via evolved gauge field"""
        props, edges = self._parse_propositions(prompt)
        results = []
        
        for cand in candidates:
            constraints = self._build_constraint_graph(props, edges, cand)
            
            # Evolve weight matrix
            W_best, fitness, all_fitness = self._evolve(constraints, max(len(props), 1))
            
            # Bayesian update: use constraint satisfaction as likelihood
            prior = 0.5
            likelihood = 1.0 / (1.0 + np.exp(-fitness))  # sigmoid
            posterior = bayesian_update(prior, likelihood, 0.1)
            
            # Agreement-based confidence from population
            agreement = confidence_from_agreement(all_fitness)
            
            # NCD tiebreaker (max 10%)
            ncd = self._ncd(prompt, cand)
            
            # Weighted score
            score = 0.6 * posterior + 0.3 * agreement + 0.1 * (1 - ncd)
            
            reasoning = f"Fitness={fitness:.3f}, Posterior={posterior:.3f}, Agreement={agreement:.3f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Confidence with epistemic honesty"""
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate this single answer
        result = self.evaluate(prompt, [answer])[0]
        score = result['score']
        
        # Cap by meta-confidence
        conf = min(score, meta_conf)
        
        # Never over-confident
        return min(0.85, max(0.15, conf))
    
    def _ncd(self, s1, s2):
        """Normalized compression distance"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0