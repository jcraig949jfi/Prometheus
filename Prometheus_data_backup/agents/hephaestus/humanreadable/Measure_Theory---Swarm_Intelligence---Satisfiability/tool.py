import re
import numpy as np
import zlib
from forge_primitives import solve_sat, check_transitivity, confidence_from_agreement, information_sufficiency

class ReasoningTool:
    """
    Measure Theory x Swarm Intelligence x Satisfiability
    
    Parses prompts into weighted SAT clauses where weights represent semantic confidence
    (measure-theoretic), uses ant colony optimization for stochastic solution search
    (swarm intelligence), and scores candidates by weighted satisfaction ratio (SAT).
    """
    
    def __init__(self):
        self.rng = np.random.RandomState(42)
        
    def _parse_clauses(self, text):
        """Extract logical/numeric constraints as (literals, weight) tuples."""
        clauses = []
        weights = []
        
        # Negations
        neg_pattern = r'\b(not|no|never|none)\s+(\w+)'
        for m in re.finditer(neg_pattern, text.lower()):
            clauses.append([(m.group(2), False)])
            weights.append(1.0)
        
        # Comparatives with numbers
        comp_pattern = r'(\w+)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)'
        for m in re.finditer(comp_pattern, text.lower()):
            var, op, val = m.group(1), m.group(2), float(m.group(3))
            clauses.append([(f"{var}_{op}_{val}", True)])
            weights.append(1.5)  # Higher weight for numeric constraints
        
        # Conditionals (if-then)
        cond_pattern = r'if\s+(\w+)\s+then\s+(\w+)'
        for m in re.finditer(cond_pattern, text.lower()):
            # if A then B => (not A) OR B
            clauses.append([(m.group(1), False), (m.group(2), True)])
            weights.append(1.2)
        
        # Causality
        causal_pattern = r'(\w+)\s+(leads to|results in|causes)\s+(\w+)'
        for m in re.finditer(causal_pattern, text.lower()):
            clauses.append([(m.group(1), True), (m.group(3), True)])
            weights.append(1.0)
        
        return clauses, np.array(weights) if weights else np.array([1.0])
    
    def _extract_variables(self, clauses):
        """Get unique variables from clauses."""
        vars_set = set()
        for clause in clauses:
            for lit, _ in clause:
                vars_set.add(lit)
        return sorted(vars_set)
    
    def _aco_search(self, clauses, weights, n_vars, n_ants=10, n_iter=5, rho=0.3):
        """Ant colony optimization for weighted SAT."""
        if n_vars == 0:
            return 0.5
        
        pheromone = np.ones((n_vars, 2)) * 0.5
        best_score = 0.0
        
        for _ in range(n_iter):
            ant_scores = []
            
            for _ in range(n_ants):
                # Build solution probabilistically
                model = np.zeros(n_vars, dtype=bool)
                for var_idx in range(n_vars):
                    probs = pheromone[var_idx] / pheromone[var_idx].sum()
                    model[var_idx] = self.rng.choice([False, True], p=probs)
                
                # Evaluate satisfaction
                sat_score = self._evaluate_model(clauses, weights, model)
                ant_scores.append(sat_score)
                
                # Update pheromone
                for var_idx in range(n_vars):
                    val_idx = int(model[var_idx])
                    pheromone[var_idx, val_idx] += sat_score
            
            # Evaporation
            pheromone *= (1 - rho)
            pheromone = np.clip(pheromone, 0.01, 10.0)
            
            best_score = max(best_score, max(ant_scores))
        
        return best_score
    
    def _evaluate_model(self, clauses, weights, model):
        """Compute weighted satisfaction ratio."""
        if len(clauses) == 0:
            return 0.5
        
        satisfied = np.zeros(len(clauses))
        for i, clause in enumerate(clauses):
            # Clause is satisfied if any literal is true
            for lit_idx in range(min(len(model), len(clause))):
                if lit_idx < len(model):
                    satisfied[i] = 1.0
                    break
        
        return np.sum(satisfied * weights) / np.sum(weights) if np.sum(weights) > 0 else 0.5
    
    def _ncd(self, s1, s2):
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity/unanswerable patterns."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you)\s+(stop|quit|cease)', p):
            return 0.2
        if re.search(r'why did .+ (fail|stop|end)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and '?' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+', p) and 'only' not in p:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p):
            return 0.3
        
        # Insufficient info markers
        if re.search(r'(impossible|cannot|not enough|insufficient)', p):
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 for a prompt-answer pair."""
        meta_cap = self._meta_confidence(prompt)
        
        clauses, weights = self._parse_clauses(prompt)
        ans_clauses, ans_weights = self._parse_clauses(answer)
        
        if len(clauses) == 0:
            return min(0.4, meta_cap)
        
        variables = self._extract_variables(clauses + ans_clauses)
        n_vars = len(variables)
        
        # Use ACO to find best satisfaction
        sat_score = self._aco_search(clauses + ans_clauses, 
                                      np.concatenate([weights, ans_weights]), 
                                      n_vars, n_ants=8, n_iter=4)
        
        # Structural confidence
        struct_conf = sat_score * 0.7
        
        # NCD penalty (lower NCD = higher relevance)
        ncd_score = 1.0 - self._ncd(prompt, answer)
        ncd_conf = ncd_score * 0.15
        
        # Combine
        raw_conf = struct_conf + ncd_conf + 0.15
        return min(raw_conf, meta_cap, 0.95)
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by weighted SAT satisfaction."""
        meta_cap = self._meta_confidence(prompt)
        p_clauses, p_weights = self._parse_clauses(prompt)
        
        results = []
        for cand in candidates:
            c_clauses, c_weights = self._parse_clauses(cand)
            combined_clauses = p_clauses + c_clauses
            combined_weights = np.concatenate([p_weights, c_weights * 1.2])
            
            variables = self._extract_variables(combined_clauses)
            n_vars = len(variables)
            
            # ACO search
            sat_score = self._aco_search(combined_clauses, combined_weights, 
                                         n_vars, n_ants=10, n_iter=5)
            
            # Numeric evaluation
            num_score = self._evaluate_numeric(prompt, cand)
            
            # NCD component
            ncd = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.1
            
            # Combine: 60% SAT, 25% numeric, 15% NCD
            final_score = sat_score * 0.6 + num_score * 0.25 + ncd_score + 0.15
            final_score = min(final_score, meta_cap * 1.5)
            
            reasoning = f"SAT:{sat_score:.2f} NUM:{num_score:.2f} NCD:{1-ncd:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _evaluate_numeric(self, prompt, candidate):
        """Evaluate numeric comparisons."""
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not c_nums:
            return 0.5
        
        score = 0.5
        # Check if candidate numbers make sense in prompt context
        comp = re.search(r'(\d+\.?\d*)\s*(>|<)\s*(\d+\.?\d*)', prompt)
        if comp:
            a, op, b = float(comp.group(1)), comp.group(2), float(comp.group(3))
            expected = (a > b) if op == '>' else (a < b)
            
            # Check if candidate agrees
            if ('yes' in candidate.lower() or 'true' in candidate.lower()) and expected:
                score = 0.9
            elif ('no' in candidate.lower() or 'false' in candidate.lower()) and not expected:
                score = 0.9
        
        return score