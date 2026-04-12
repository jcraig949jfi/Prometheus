from dataclasses import field

"""
Phase-Transition Constraint Satisfaction Reasoner

Builds a weighted constraint graph from logical structures, runs mean-field dynamics
to find the critical phase transition point (beta*), and scores candidates by their
energy at that critical regime. Uses primitives for logic, probability, and graphs.
"""

import re
import numpy as np
from zlib import compress
from forge_primitives import (
    solve_sat, check_transitivity, bayesian_update, entropy,
    dag_traverse, solve_constraints, confidence_from_agreement,
    information_sufficiency, modus_ponens
)
import networkx as nx


class ReasoningTool:
    def __init__(self):
        self.beta_range = np.linspace(0.1, 5.0, 50)
    
    def _parse_atoms(self, text):
        """Extract propositional atoms: comparisons, negations, conditionals."""
        atoms = []
        # Numeric comparisons
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==|equals?)\s*(\w+)', text, re.I):
            atoms.append(('compare', m.group(1), m.group(2), m.group(3)))
        # Negations
        for m in re.finditer(r'(not|never|no)\s+(\w+)', text, re.I):
            atoms.append(('neg', m.group(2)))
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', text, re.I):
            atoms.append(('implies', m.group(1).strip(), m.group(2).strip()))
        # Biconditionals
        for m in re.finditer(r'(.+?)\s+iff\s+(.+?)(?:\.|,|$)', text, re.I):
            atoms.append(('equiv', m.group(1).strip(), m.group(2).strip()))
        return atoms
    
    def _build_constraint_graph(self, prompt, candidate):
        """Build weighted constraint graph from prompt + candidate."""
        combined = prompt + " " + candidate
        atoms = self._parse_atoms(combined)
        
        G = nx.DiGraph()
        variables = set()
        clauses = []
        
        for atom in atoms:
            if atom[0] == 'compare':
                var1, op, var2 = atom[1], atom[2], atom[3]
                variables.add(var1)
                variables.add(var2)
                G.add_edge(var1, var2, weight=1.0, type='compare', op=op)
            elif atom[0] == 'neg':
                var = atom[1]
                variables.add(var)
                neg_var = f"NOT_{var}"
                variables.add(neg_var)
                G.add_edge(var, neg_var, weight=2.0, type='neg')
                clauses.append([(-1, var)])  # Negation clause
            elif atom[0] == 'implies':
                ante, cons = atom[1], atom[2]
                variables.add(ante)
                variables.add(cons)
                G.add_edge(ante, cons, weight=1.5, type='implies')
                clauses.append([(ante, cons)])  # A -> B
            elif atom[0] == 'equiv':
                a, b = atom[1], atom[2]
                variables.add(a)
                variables.add(b)
                G.add_edge(a, b, weight=1.5, type='equiv')
                G.add_edge(b, a, weight=1.5, type='equiv')
        
        return G, list(variables), clauses
    
    def _evaluate_numeric_constraints(self, prompt, candidate):
        """Extract and evaluate numeric comparisons."""
        score = 0.0
        combined = prompt + " " + candidate
        
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', combined):
            try:
                left = float(m.group(1))
                right = float(m.group(3))
                op = m.group(2)
                
                if op == '>' and left > right: score += 1.0
                elif op == '<' and left < right: score += 1.0
                elif op == '>=' and left >= right: score += 1.0
                elif op == '<=' and left <= right: score += 1.0
                elif op == '==' and abs(left - right) < 1e-9: score += 1.0
            except:
                pass
        
        return score
    
    def _mean_field_energy(self, G, variables, beta):
        """Run mean-field dynamics and compute energy at convergence."""
        n = len(variables)
        if n == 0:
            return 0.0
        
        var_idx = {v: i for i, v in enumerate(variables)}
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        for u, v, data in G.edges(data=True):
            if u in var_idx and v in var_idx:
                i, j = var_idx[u], var_idx[v]
                W[i, j] += data.get('weight', 1.0)
        
        # Symmetrize for energy calculation
        W = (W + W.T) / 2
        
        # Mean-field iteration
        s = np.random.rand(n) * 0.1 + 0.5  # Initialize near 0.5
        for _ in range(20):
            s = 1 / (1 + np.exp(-beta * (W @ s + b)))
        
        # Hopfield energy
        energy = -0.5 * s @ W @ s - b @ s
        return energy
    
    def _find_critical_beta(self, G, variables):
        """Find phase transition point via order parameter derivative."""
        magnetizations = []
        
        for beta in self.beta_range:
            n = len(variables)
            if n == 0:
                magnetizations.append(0.0)
                continue
            
            var_idx = {v: i for i, v in enumerate(variables)}
            W = np.zeros((n, n))
            for u, v, data in G.edges(data=True):
                if u in var_idx and v in var_idx:
                    i, j = var_idx[u], var_idx[v]
                    W[i, j] += data.get('weight', 1.0)
            W = (W + W.T) / 2
            
            s = np.random.rand(n) * 0.1 + 0.5
            for _ in range(20):
                s = 1 / (1 + np.exp(-beta * (W @ s)))
            
            magnetizations.append(np.mean(s))
        
        # Find peak of derivative
        dm_dbeta = np.abs(np.gradient(magnetizations))
        beta_star_idx = np.argmax(dm_dbeta)
        return self.beta_range[beta_star_idx]
    
    def _meta_confidence(self, prompt):
        """Check for epistemic traps that should lower confidence."""
        lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', lower):
            return 0.2
        if re.search(r'why (did|does|do).+(fail|stop|end)', lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were)', lower) and 'who' in lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+(?!\s+or)', lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|ideal)\b', lower) and not re.search(r'\d', prompt):
            return 0.3
        
        # Insufficient information
        unknowns = len(re.findall(r'\?|\bunknown\b|\bnot (given|stated|specified)\b', lower))
        if unknowns > 2:
            return 0.2
        
        return 1.0  # No trap detected
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates using phase-transition constraint satisfaction."""
        meta_conf = self._meta_confidence(prompt)
        results = []
        
        for candidate in candidates:
            # Build constraint graph
            G, variables, clauses = self._build_constraint_graph(prompt, candidate)
            
            # Structural score: graph connectivity
            structural = 0.0
            if len(variables) > 0:
                try:
                    structural = nx.density(G) * 10.0
                except:
                    structural = len(G.edges()) / max(1, len(variables))
            
            # Phase transition score
            phase_score = 0.0
            if len(variables) > 1:
                beta_star = self._find_critical_beta(G, variables)
                energy = self._mean_field_energy(G, variables, beta_star)
                phase_score = -energy  # Lower energy = better
            
            # Numeric computation score
            numeric_score = self._evaluate_numeric_constraints(prompt, candidate)
            
            # NCD tiebreaker (max 10%)
            ncd = len(compress((prompt + candidate).encode())) / max(len(compress(prompt.encode())), 1)
            ncd_score = 1.0 / (1.0 + ncd)
            
            # Weighted combination
            total_score = (
                0.50 * structural +
                0.25 * phase_score +
                0.15 * numeric_score +
                0.10 * ncd_score
            )
            
            reasoning = f"Structure={structural:.2f}, Phase={phase_score:.2f}, Numeric={numeric_score:.2f}"
            results.append({"candidate": candidate, "score": total_score, "reasoning": reasoning})
        
        # Normalize scores
        if results:
            scores = [r["score"] for r in results]
            min_s, max_s = min(scores), max(scores)
            if max_s > min_s:
                for r in results:
                    r["score"] = (r["score"] - min_s) / (max_s - min_s)
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence based on question properties."""
        meta_conf = self._meta_confidence(prompt)
        
        # Build graph to check structural clarity
        G, variables, clauses = self._build_constraint_graph(prompt, answer)
        
        # Low confidence if no structure detected
        if len(variables) == 0:
            return min(0.25, meta_conf)
        
        # Check numeric definiteness
        numeric_score = self._evaluate_numeric_constraints(prompt, answer)
        if numeric_score > 2:
            return min(0.85, meta_conf)  # Definitive computation
        
        # Phase transition stability
        conf = 0.5
        if len(variables) > 1:
            try:
                beta_star = self._find_critical_beta(G, variables)
                energy = self._mean_field_energy(G, variables, beta_star)
                # Lower energy variance = higher confidence
                conf = 0.5 + 0.3 * (1.0 / (1.0 + abs(energy)))
            except:
                conf = 0.4
        
        # Cap by meta-confidence
        return min(conf, meta_conf)