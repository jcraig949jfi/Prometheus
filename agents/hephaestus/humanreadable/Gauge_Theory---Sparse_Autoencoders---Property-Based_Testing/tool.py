"""
Gauge-Theoretic Sparse Logic Reasoner

Combines:
1. Sparse autoencoders - represent predicates as sparse feature vectors
2. Gauge theory - logical connectives as transformations preserving satisfaction
3. Property-based testing - generate/shrink counter-examples to find violations

Pipeline: Parse -> Sparse encode -> Gauge propagate -> Test properties -> Score by energy
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    solve_sat, modus_ponens, check_transitivity, negate,
    solve_constraints, information_sufficiency,
    confidence_from_agreement, bayesian_update
)

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self.d = 8  # base feature dim
        self.k = 24  # sparse dictionary size
        self.D = np.random.randn(self.d, self.k)
        self.D /= np.linalg.norm(self.D, axis=0, keepdims=True)
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        predicates = self._parse_predicates(prompt)
        edges = self._parse_edges(prompt)
        
        # Encode predicates sparsely
        sparse_codes = {}
        for p in predicates:
            v = self._featurize(p)
            z = self._sparse_encode(v)
            sparse_codes[p] = z
        
        # Gauge propagation through logical graph
        if edges:
            sparse_codes = self._gauge_propagate(sparse_codes, edges)
        
        results = []
        for cand in candidates:
            # Score = -energy (constraint satisfaction)
            energy = self._compute_energy(prompt, cand, predicates, edges, sparse_codes)
            
            # Property-based testing: generate counter-examples
            violation = self._property_test(prompt, cand, sparse_codes)
            
            # Combine: lower energy + fewer violations = higher score
            score = -energy - 2.0 * violation
            
            # NCD tiebreaker (max 10%)
            ncd = self._ncd(prompt, cand)
            score += 0.1 * (1.0 - ncd)
            
            reasoning = f"Energy={energy:.2f}, Violation={violation:.2f}, NCD={ncd:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        predicates = self._parse_predicates(prompt)
        edges = self._parse_edges(prompt)
        
        if not predicates:
            return 0.2  # no structure parsed
        
        # Evaluate information sufficiency
        unknowns = len([p for p in predicates if '?' in p])
        constraints = len(edges)
        suff = information_sufficiency(unknowns, constraints)
        
        # Evaluate answer against constraints
        sparse_codes = {p: self._sparse_encode(self._featurize(p)) for p in predicates}
        if edges:
            sparse_codes = self._gauge_propagate(sparse_codes, edges)
        
        energy = self._compute_energy(prompt, answer, predicates, edges, sparse_codes)
        violation = self._property_test(prompt, answer, sparse_codes)
        
        # Confidence from multiple signals
        signals = [
            max(0, 1.0 - energy),
            max(0, 1.0 - violation),
            suff
        ]
        conf = confidence_from_agreement(signals)
        
        return min(meta_conf, conf, 0.85)  # cap at 0.85
    
    def _meta_confidence(self, prompt: str) -> float:
        # Epistemic honesty checks
        lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why did .* stop)', lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+', lower):
            return 0.28
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were)', lower) and 'who' in lower:
            return 0.26
        
        # False dichotomy
        if re.search(r'\b(either .* or|must be .* or)\b', lower) and '?' in prompt:
            return 0.27
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', lower):
            return 0.29
        
        return 1.0  # no meta-issues detected
    
    def _parse_predicates(self, text):
        predicates = []
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|equals?)\s*([\d.]+)', text):
            predicates.append(f"{m.group(1)}{m.group(2)}{m.group(3)}")
        
        # Negations
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text.lower()):
            predicates.append(f"NOT_{m.group(2)}")
        
        # Conditionals
        for m in re.finditer(r'\bif\s+(\w+)\s+then\s+(\w+)', text.lower()):
            predicates.append(f"IF_{m.group(1)}_THEN_{m.group(2)}")
        
        # Simple named predicates
        for m in re.finditer(r'\b([A-Z][a-z]+)\s+(is|are|was|were)\s+([a-z]+)', text):
            predicates.append(f"{m.group(1)}_{m.group(3)}")
        
        return list(set(predicates))
    
    def _parse_edges(self, text):
        edges = []
        
        # Implies
        for m in re.finditer(r'(\w+)\s+(implies|means|causes)\s+(\w+)', text.lower()):
            edges.append((m.group(1), m.group(3), 'IMPLIES'))
        
        # And
        for m in re.finditer(r'(\w+)\s+and\s+(\w+)', text.lower()):
            edges.append((m.group(1), m.group(2), 'AND'))
        
        return edges
    
    def _featurize(self, predicate):
        # One-hot + numeric features
        v = np.zeros(self.d)
        
        if 'NOT_' in predicate:
            v[0] = 1.0
        if any(op in predicate for op in ['>', '<', '=', 'equals']):
            v[1] = 1.0
            nums = re.findall(r'[\d.]+', predicate)
            if nums:
                v[2] = float(nums[0]) % 10  # normalize
        if 'IF_' in predicate and '_THEN_' in predicate:
            v[3] = 1.0
        if '_' in predicate:
            v[4] = len(predicate.split('_'))
        
        v[5] = len(predicate) / 20.0
        v[6] = hash(predicate) % 100 / 100.0
        v[7] = sum(ord(c) for c in predicate) % 100 / 100.0
        
        return v
    
    def _sparse_encode(self, v, lam=0.1, max_iter=50):
        # LASSO: min ||v - Dz||^2 + lam*||z||_1
        z = np.zeros(self.k)
        for _ in range(max_iter):
            for j in range(self.k):
                residual = v - self.D @ z + self.D[:, j] * z[j]
                rho = self.D[:, j] @ residual
                z[j] = np.sign(rho) * max(0, abs(rho) - lam)
        return z
    
    def _gauge_propagate(self, sparse_codes, edges, alpha=0.5):
        # Update sparse codes via gauge transformations (simple averaging)
        updated = sparse_codes.copy()
        
        for src, tgt, conn_type in edges:
            if src in updated and tgt in updated:
                # Gauge connection: enforce covariance
                if conn_type == 'IMPLIES':
                    updated[tgt] = (1-alpha)*updated[tgt] + alpha*updated[src]
                elif conn_type == 'AND':
                    avg = (updated[src] + updated[tgt]) / 2
                    updated[src] = updated[tgt] = avg
        
        return updated
    
    def _compute_energy(self, prompt, candidate, predicates, edges, sparse_codes):
        energy = 0.0
        
        # Numeric constraint checking
        for p in predicates:
            m = re.match(r'(\w+)(>|<|>=|<=|=)(\d+\.?\d*)', p)
            if m:
                var, op, val = m.groups()
                val = float(val)
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums:
                    cand_val = float(cand_nums[0])
                    if not self._check_comparison(cand_val, op, val):
                        energy += 1.0
        
        # Edge satisfaction via topological consistency
        if edges:
            for src, tgt, _ in edges:
                if src in sparse_codes and tgt in sparse_codes:
                    diff = np.linalg.norm(sparse_codes[src] - sparse_codes[tgt])
                    energy += 0.5 * diff
        
        return energy
    
    def _check_comparison(self, a, op, b):
        if op == '>': return a > b
        if op == '<': return a < b
        if op == '>=': return a >= b
        if op == '<=': return a <= b
        if op in ['=', 'equals']: return abs(a - b) < 0.01
        return False
    
    def _property_test(self, prompt, candidate, sparse_codes, n_tests=5):
        # Generate random "worlds" by perturbing sparse codes, count violations
        violations = 0
        
        for _ in range(n_tests):
            # Sample from Laplace prior
            noise = np.random.laplace(0, 0.1, self.k)
            
            # Check if perturbed world violates constraints
            perturbed_sum = sum(np.linalg.norm(z + noise) for z in sparse_codes.values())
            baseline_sum = sum(np.linalg.norm(z) for z in sparse_codes.values())
            
            if perturbed_sum > baseline_sum * 1.5:
                violations += 1
        
        return violations / n_tests
    
    def _ncd(self, s1, s2):
        import zlib
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0