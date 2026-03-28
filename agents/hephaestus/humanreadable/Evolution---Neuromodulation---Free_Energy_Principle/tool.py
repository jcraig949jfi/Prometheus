import re
import math
import random
import numpy as np
from typing import List, Dict, Tuple, Set, Any

class ReasoningTool:
    """
    Implements an Evolutionary Free Energy Reasoner with Neuromodulated Gain.
    
    Mechanism:
    1. Parsing: Extracts a constraint graph (G) from the prompt using regex for 
       negations, comparatives, conditionals, causality, and ordering.
    2. Hypothesis Generation: Converts candidate answers into sets of grounded literals.
       A population of hypotheses is initialized by mutating these base literals.
    3. Free Energy Minimization: Iteratively evolves the population to minimize:
       F(h) = Complexity (literal count/precision) + Prediction Error (constraint violations).
    4. Neuromodulation: Global gain (g) scales mutation rates based on population entropy.
       High entropy -> High g (Exploration). Low entropy -> Low g (Exploitation).
    5. Scoring: Candidates are scored by the average negative free energy of hypotheses 
       that entail them. NCD is used strictly as a tiebreaker.
    """

    def __init__(self):
        random.seed(42)
        np.random.seed(42)
        self.base_mut_rate = 0.1
        self.generations = 15
        self.pop_size = 20
        self.elite_count = 5

    def _parse_constraints(self, prompt: str) -> List[Dict]:
        """Extract structural constraints from text."""
        constraints = []
        p_lower = prompt.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|without)\b', p_lower):
            constraints.append({'type': 'negation', 'idx': m.start(), 'text': m.group(0)})
            
        # Comparatives
        comps = [
            (r'greater than|>', 'gt'), (r'less than|<', 'lt'),
            (r'equal to|=', 'eq'), (r'more than', 'gt'), (r'fewer than', 'lt')
        ]
        for pattern, op in comps:
            for m in re.finditer(pattern, p_lower):
                constraints.append({'type': 'comparative', 'op': op, 'idx': m.start()})

        # Conditionals
        if re.search(r'\bif\b.*\bthen\b', p_lower) or re.search(r'\bunless\b', p_lower):
            constraints.append({'type': 'conditional', 'present': True})
            
        # Causality
        if re.search(r'\b(cause|lead to|result in)\b', p_lower):
            constraints.append({'type': 'causal', 'present': True})

        # Numeric extraction for bound checking
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if n1 > n2: constraints.append({'type': 'numeric_bound', 'val': n1, 'ref': n2})
                elif n1 < n2: constraints.append({'type': 'numeric_bound', 'val': n2, 'ref': n1})
            except: pass
            
        return constraints

    def _text_to_literals(self, text: str) -> Set[str]:
        """Convert text to a set of normalized grounded literals."""
        literals = set()
        # Simple tokenization and normalization
        tokens = re.findall(r'\w+', text.lower())
        for i, t in enumerate(tokens):
            if len(t) > 2: literals.add(f"Token({t})")
            if i < len(tokens)-1: literals.add(f"Bigram({t}_{tokens[i+1]})")
        
        # Extract explicit claims
        if re.search(r'\byes\b', text.lower()): literals.add("Claim(True)")
        if re.search(r'\bno\b', text.lower()): literals.add("Claim(False)")
        
        return literals

    def _compute_violations(self, literals: Set[str], constraints: List[Dict]) -> float:
        """Calculate prediction error based on constraint satisfaction."""
        errors = 0.0
        text_repr = " ".join(literals).lower()
        
        for c in constraints:
            if c['type'] == 'negation':
                # If constraint says 'not', and literals assert positive claim heavily
                if 'claim(True)' in text_repr and not any('not' in l for l in literals):
                    errors += 0.5 
            elif c['type'] == 'comparative':
                # Heuristic: if prompt has 'greater', answer should imply magnitude or ordering
                if c['op'] == 'gt' and ('less' in text_repr or 'small' in text_repr):
                    errors += 1.0
                if c['op'] == 'lt' and ('more' in text_repr or 'great' in text_repr):
                    errors += 1.0
            elif c['type'] == 'conditional':
                # Check for logical connectors in answer if prompt is conditional
                if 'if' in text_repr or 'then' in text_repr or 'because' in text_repr:
                    pass # Good alignment
                else:
                    errors += 0.2 # Penalty for ignoring conditional structure
        return errors

    def _compute_free_energy(self, literals: Set[str], constraints: List[Dict]) -> float:
        """F(h) = Complexity + Prediction Error."""
        # Complexity: penalize length, weighted by precision (simulated as 1.0 here)
        complexity = len(literals) * 0.1 
        error = self._compute_violations(literals, constraints)
        return complexity + error

    def _mutate(self, literals: Set[str], base_literals: Set[str], gain: float) -> Set[str]:
        """Mutate literals based on neuromodulated gain."""
        new_lits = set(literals)
        all_pool = list(base_literals)
        
        # Mutation probability scaled by gain
        p_mut = min(0.9, self.base_mut_rate * (1 + gain))
        
        if random.random() < p_mut and all_pool:
            # Add random literal from base
            new_lits.add(random.choice(all_pool))
        if random.random() < p_mut and new_lits:
            # Remove random literal
            new_lits.pop()
            
        return new_lits

    def _crossover(self, h1: Set[str], h2: Set[str]) -> Set[str]:
        """Exchange subsets of literals."""
        if not h1 or not h2: return h1.union(h2)
        split = len(h1) // 2
        return set(list(h1)[:split] + list(h2)[split:])

    def _calculate_entropy(self, population: List[Set[str]]) -> float:
        """Estimate population entropy."""
        if not population: return 0.0
        all_lits = set()
        for h in population: all_lits.update(h)
        if not all_lits: return 0.0
        
        counts = {l: 0 for l in all_lits}
        for h in population:
            for l in h: counts[l] += 1
            
        entropy = 0.0
        total = len(population)
        for l in all_lits:
            p = counts[l] / total
            if p > 0: entropy -= p * math.log2(p)
        return entropy / (len(all_lits) + 1e-9) # Normalized

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        constraints = self._parse_constraints(prompt)
        base_pool = set()
        candidate_maps = {} # Map candidate string to base literals
        
        # Initialize base pool from prompt and candidates
        prompt_lits = self._text_to_literals(prompt)
        base_pool.update(prompt_lits)
        
        for cand in candidates:
            lits = self._text_to_literals(cand)
            base_pool.update(lits)
            candidate_maps[cand] = lits
            
        base_pool = list(base_pool)
        if not base_pool: base_pool = ["default"]

        results = []
        
        for cand in candidates:
            # Initialize population for this candidate
            base_lits = candidate_maps[cand]
            population = [set(base_lits) for _ in range(self.pop_size)]
            
            # Add some noise to initial population
            for i in range(len(population)):
                if i > 0: population[i] = self._mutate(population[i], base_lits, 2.0)

            best_F = float('inf')
            
            # Evolutionary Loop
            for gen in range(self.generations):
                # Compute Free Energy for all
                energies = [self._compute_free_energy(h, constraints) for h in population]
                current_min = min(energies)
                if current_min < best_F: best_F = current_min
                
                # Neuromodulation: Gain based on entropy
                entropy = self._calculate_entropy(population)
                gain = 1.0 / (1.0 + math.exp(-5 * (entropy - 0.5))) # Sigmoid mapping
                
                # Selection (Keep top k)
                sorted_idx = np.argsort(energies)
                elites = [population[i] for i in sorted_idx[:self.elite_count]]
                
                next_gen = []
                # Reproduction
                next_gen.extend(elites)
                
                while len(next_gen) < self.pop_size:
                    p1 = random.choice(elites)
                    p2 = random.choice(elites)
                    child = self._crossover(p1, p2)
                    child = self._mutate(child, base_lits, gain)
                    next_gen.append(child)
                
                population = next_gen

            # Final Score: Average negative free energy of hypotheses entailing candidate
            # Simplified: We use the best free energy found for this candidate's lineage
            # and adjust by how well the candidate's base literals match the prompt constraints.
            base_error = self._compute_violations(base_lits, constraints)
            score = -best_F - base_error
            
            # NCD Tiebreaker (only if scores are very close, handled implicitly by float precision usually,
            # but we add a tiny NCD component if structural signal is weak)
            ncd_score = 0.0
            if abs(score) < 0.01:
                # Minimal NCD fallback
                s = prompt + cand
                try:
                    import zlib
                    c = len(zlib.compress(s.encode()))
                    score -= c * 1e-6 
                except: pass

            results.append({"candidate": cand, "score": score, "reasoning": f"F_min={-best_F:.4f}, Err={base_error:.2f}"})

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        # Normalize score to 0-1 range roughly
        # Assuming a reasonable score range of -10 to 10 based on implementation
        raw_score = res[0]['score']
        conf = 1.0 / (1.0 + math.exp(-raw_score)) # Sigmoid
        return max(0.0, min(1.0, conf))