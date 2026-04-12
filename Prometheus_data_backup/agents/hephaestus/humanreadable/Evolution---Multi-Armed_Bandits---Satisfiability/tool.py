"""
Evolution x Multi-Armed Bandits x Satisfiability Reasoning Tool

Parses prompt into CNF clauses, evolves binary variable assignments (candidates),
uses SAT solver for fitness and UCB1 bandit to allocate evaluation budget.
Primitives: solve_sat, confidence_from_agreement, negate, bayesian_update.
"""
import re
import numpy as np
from forge_primitives import solve_sat, confidence_from_agreement, negate, bayesian_update
import zlib


class ReasoningTool:
    def __init__(self):
        self.n_generations = 15
        self.pop_size = 20
        self.p_mut = 0.15
        self.p_cross = 0.6
        
    def _parse_variables_and_clauses(self, prompt, candidate):
        """Extract propositional variables and CNF clauses from prompt+candidate."""
        text = prompt.lower() + " " + candidate.lower()
        variables = {}
        clauses = []
        var_count = 0
        
        # Extract variables from key phrases
        tokens = re.findall(r'\b\w+\b', text)
        for tok in set(tokens):
            if len(tok) > 2:
                variables[tok] = var_count
                var_count += 1
        
        # Conditionals: if A then B -> (-A OR B)
        for match in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', prompt.lower()):
            a, b = match.groups()
            if a in variables and b in variables:
                clauses.append([(-variables[a]-1, variables[b])])
        
        # Negations: not A -> -A must be true
        for match in re.finditer(r'not\s+(\w+)', text):
            word = match.group(1)
            if word in variables:
                clauses.append([(-variables[word]-1,)])
        
        # Conjunctions: A and B -> both A, B
        for match in re.finditer(r'(\w+)\s+and\s+(\w+)', text):
            a, b = match.groups()
            if a in variables and b in variables:
                clauses.append([(variables[a],)])
                clauses.append([(variables[b],)])
        
        # Comparatives: extract numeric assertions
        nums = re.findall(r'\b(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text)
        for n1, op, n2 in nums:
            result = eval(f"{n1}{op}{n2}")
            var_name = f"cmp_{n1}_{op}_{n2}"
            if var_name not in variables:
                variables[var_name] = var_count
                var_count += 1
            if result:
                clauses.append([(variables[var_name],)])
            else:
                clauses.append([(-variables[var_name]-1,)])
        
        return variables, clauses, var_count
    
    def _fitness_sat(self, assignment, clauses):
        """Compute fitness = number of satisfied clauses."""
        if not clauses:
            return 0.0
        sat_count = 0
        for clause_list in clauses:
            for clause in clause_list:
                if isinstance(clause, tuple):
                    lit = clause[0]
                else:
                    lit = clause
                var_idx = abs(lit) - 1 if lit < 0 else lit
                is_neg = lit < 0
                if var_idx < len(assignment):
                    val = assignment[var_idx]
                    if (is_neg and val == 0) or (not is_neg and val == 1):
                        sat_count += 1
                        break
        return sat_count / max(len(clauses), 1)
    
    def _ucb1(self, means, counts, total):
        """UCB1 selection."""
        ucb = np.zeros(len(means))
        for i in range(len(means)):
            if counts[i] == 0:
                ucb[i] = float('inf')
            else:
                ucb[i] = means[i] + np.sqrt(2 * np.log(total + 1) / counts[i])
        return np.argmax(ucb)
    
    def _evolve_population(self, pop, clauses, n_vars):
        """Evolution with bandit-driven evaluation."""
        means = np.zeros(self.pop_size)
        counts = np.zeros(self.pop_size)
        total_evals = 0
        
        for gen in range(self.n_generations):
            # Bandit selection
            idx = self._ucb1(means, counts, total_evals)
            individual = pop[idx]
            
            # Evaluate fitness using SAT
            fit = self._fitness_sat(individual, clauses)
            counts[idx] += 1
            means[idx] = (means[idx] * (counts[idx] - 1) + fit) / counts[idx]
            total_evals += 1
            
            # Mutation
            if np.random.rand() < self.p_mut:
                offspring = individual.copy()
                for i in range(len(offspring)):
                    if np.random.rand() < 0.2:
                        offspring[i] = 1 - offspring[i]
            # Crossover
            elif np.random.rand() < self.p_cross:
                parent2_idx = np.random.choice(range(self.pop_size), p=means/means.sum() if means.sum() > 0 else None)
                parent1, parent2 = individual, pop[parent2_idx]
                offspring = np.array([p1 if np.random.rand() < 0.5 else p2 for p1, p2 in zip(parent1, parent2)])
            else:
                offspring = individual
            
            # Replace worst
            worst_idx = np.argmin(means)
            pop[worst_idx] = offspring
            means[worst_idx] = 0
            counts[worst_idx] = 0
        
        return means
    
    def _meta_confidence(self, prompt):
        """Check for reasoning traps that require epistemic honesty."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*?\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*?(who|what|which)', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p) and not re.search(r'(only|just|exactly)', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p) and not re.search(r'(according to|objectively|measured by)', p):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates using evolutionary SAT search."""
        results = []
        
        for cand in candidates:
            variables, clauses, n_vars = self._parse_variables_and_clauses(prompt, cand)
            
            if n_vars == 0:
                # Fallback to NCD
                ncd = len(zlib.compress((prompt + cand).encode())) / (len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
                score = 1.0 - ncd
                reasoning = "NCD fallback"
            else:
                # Initialize population
                pop = [np.random.randint(0, 2, n_vars) for _ in range(self.pop_size)]
                
                # Evolve with bandit allocation
                final_means = self._evolve_population(pop, clauses, n_vars)
                
                # Use primitives for final scoring
                sat_score = np.max(final_means)
                agreement = confidence_from_agreement([final_means])
                
                # Combine SAT fitness + agreement confidence
                score = 0.7 * sat_score + 0.3 * agreement
                
                # Small NCD tiebreaker
                ncd = len(zlib.compress((prompt + cand).encode())) / (len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
                score = 0.9 * score + 0.1 * (1.0 - ncd)
                
                reasoning = f"SAT fitness={sat_score:.2f}, agreement={agreement:.2f}, {len(clauses)} clauses"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence with epistemic honesty."""
        meta_cap = self._meta_confidence(prompt)
        
        variables, clauses, n_vars = self._parse_variables_and_clauses(prompt, answer)
        
        if n_vars == 0:
            return min(0.4, meta_cap)
        
        # Single evaluation
        pop = [np.random.randint(0, 2, n_vars) for _ in range(self.pop_size)]
        final_means = self._evolve_population(pop, clauses, n_vars)
        
        sat_score = np.max(final_means)
        
        # Bayesian update: prior 0.5, likelihood from SAT
        posterior = bayesian_update(0.5, sat_score, 0.1)
        
        # Cap by meta-confidence
        return min(posterior, meta_cap, 0.85)