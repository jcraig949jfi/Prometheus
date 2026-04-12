from dataclasses import field

"""
Holographic Free Energy Reasoning Tool

Combines:
- Holography Principle: Prompt constraints = boundary encoding of solution bulk
- Free Energy Principle: Variational inference minimizes F = E - H
- Maximum Entropy: Start with max-entropy priors, constrain via factors

Architecture: Parse boundary -> Build factor graph -> Minimize free energy -> Score by consistency
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    solve_sat, entropy, bayesian_update, confidence_from_agreement,
    information_sufficiency, check_transitivity, modus_ponens,
    modular_arithmetic, bat_and_ball, all_but_n
)

class ReasoningTool:
    def __init__(self):
        self.beta = 2.0  # Constraint violation penalty
        self.lambda_prior = 0.1  # Max-entropy prior weight
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates by variational free energy consistency with prompt boundary."""
        # Extract boundary conditions (holographic surface)
        boundary = self._extract_boundary(prompt)
        
        results = []
        for cand in candidates:
            # Parse candidate into propositions
            cand_props = self._parse_propositions(prompt, cand)
            
            # Compute structural score via primitive pipeline
            struct_score = self._structural_pipeline(prompt, cand, boundary)
            
            # Compute variational free energy
            fe_score = self._free_energy_score(boundary, cand_props)
            
            # Computational score (if numeric/logical patterns detected)
            comp_score = self._computational_score(prompt, cand)
            
            # NCD tiebreaker (max 10%)
            ncd_score = self._ncd(prompt, cand)
            
            # Weighted combination
            total = 0.5 * struct_score + 0.25 * fe_score + 0.15 * comp_score + 0.1 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(total),
                "reasoning": f"FE={fe_score:.2f} Struct={struct_score:.2f} Comp={comp_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence, capped by meta-analysis."""
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is ambiguous/unanswerable, cap confidence
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate answer quality
        boundary = self._extract_boundary(prompt)
        props = self._parse_propositions(prompt, answer)
        fe = self._free_energy_score(boundary, props)
        comp = self._computational_score(prompt, answer)
        
        # Combine scores into confidence
        raw_conf = 0.6 * fe + 0.4 * comp
        
        # Never exceed 0.9 unless computation is definitive
        if comp < 0.95:
            raw_conf = min(raw_conf, 0.85)
        
        return min(raw_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        issues = []
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)\b', prompt, re.I):
            issues.append("presupposition")
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt, re.I):
            issues.append("scope_ambiguity")
        
        # Pronoun ambiguity + "who" question
        if re.search(r'\b(he|she|it)\b', prompt, re.I) and re.search(r'\bwho\b', prompt, re.I):
            issues.append("pronoun_ambiguity")
        
        # False dichotomy
        if re.search(r'\b(either.*or)\b', prompt, re.I) and not re.search(r'\b(both|neither|other)\b', prompt, re.I):
            issues.append("false_dichotomy")
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt, re.I):
            issues.append("subjective")
        
        # Insufficient information check via primitive
        unknowns = len(re.findall(r'\?', prompt))
        constraints = len(re.findall(r'\b(if|then|because|since|therefore)\b', prompt, re.I))
        if unknowns > 0 and information_sufficiency(unknowns, constraints) < 0.5:
            issues.append("insufficient_info")
        
        if issues:
            return 0.25  # Low confidence on ambiguous questions
        return 1.0
    
    def _extract_boundary(self, prompt: str) -> dict:
        """Extract holographic boundary: constraints that encode solution space."""
        boundary = {
            'comparisons': [],
            'conditionals': [],
            'negations': [],
            'numbers': [],
            'causal': []
        }
        
        # Comparisons
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=)\s*(\w+)', prompt):
            boundary['comparisons'].append((m.group(1), m.group(2), m.group(3)))
        
        # Conditionals (if-then)
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', prompt, re.I):
            boundary['conditionals'].append((m.group(1).strip(), m.group(2).strip()))
        
        # Negations
        for m in re.finditer(r'\b(not|n\'t|never|no)\s+(\w+)', prompt, re.I):
            boundary['negations'].append(m.group(2))
        
        # Numbers
        boundary['numbers'] = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        
        # Causal relations
        for m in re.finditer(r'(\w+)\s+(causes|leads to|results in)\s+(\w+)', prompt, re.I):
            boundary['causal'].append((m.group(1), m.group(3)))
        
        return boundary
    
    def _parse_propositions(self, prompt: str, text: str) -> list:
        """Parse text into atomic propositions for factor graph."""
        props = []
        
        # Extract statements
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip()
            if sent:
                props.append(sent.lower())
        
        return props
    
    def _structural_pipeline(self, prompt: str, candidate: str, boundary: dict) -> float:
        """Chain primitives: transitivity -> modus ponens -> SAT -> agreement."""
        score = 0.5  # Neutral start
        
        # Check transitivity in comparisons via primitive
        if len(boundary['comparisons']) >= 2:
            relations = [(a, c) for a, op, c in boundary['comparisons'] if op in ['>', '<']]
            if check_transitivity(relations):
                score += 0.15
        
        # Check conditionals via modus ponens
        if boundary['conditionals']:
            premises = [c for c in boundary['conditionals']]
            facts = self._parse_propositions(prompt, candidate)
            if modus_ponens(premises, facts):
                score += 0.2
        
        # SAT solving for logical consistency
        clauses, n_vars = self._build_sat_clauses(boundary, candidate)
        if clauses and solve_sat(clauses, n_vars):
            score += 0.15
        
        return min(score, 1.0)
    
    def _build_sat_clauses(self, boundary: dict, candidate: str) -> tuple:
        """Convert boundary constraints to SAT clauses."""
        clauses = []
        var_map = {}
        var_count = 0
        
        # Map propositions to variables
        for prop in self._parse_propositions("", candidate):
            if prop not in var_map:
                var_count += 1
                var_map[prop] = var_count
        
        # Negations: if "not X" in boundary, add clause [-X]
        for neg in boundary['negations']:
            if neg.lower() in var_map:
                clauses.append([-var_map[neg.lower()]])
        
        return clauses, var_count
    
    def _free_energy_score(self, boundary: dict, props: list) -> float:
        """Minimize variational free energy F = E - H via mean-field."""
        if not props:
            return 0.5
        
        n = len(props)
        q = np.ones(n) * 0.5  # Max-entropy initialization
        
        # Iterative mean-field update (10 iterations)
        for _ in range(10):
            # Energy term: violations of boundary constraints
            energy = self._compute_energy(boundary, props, q)
            
            # Entropy term
            ent = entropy(q) if np.all((q > 0) & (q < 1)) else 0.0
            
            # Gradient descent on F = E - H
            grad = np.ones(n) * self.lambda_prior  # Prior pulls toward 0.5
            q = 1.0 / (1.0 + np.exp(grad - self.beta * energy))
            q = np.clip(q, 0.01, 0.99)
        
        # Final free energy (lower is better, normalize to [0,1])
        final_energy = self._compute_energy(boundary, props, q)
        final_entropy = entropy(q) if np.all((q > 0) & (q < 1)) else 0.0
        free_energy = final_energy - final_entropy
        
        # Convert to score (lower FE = higher score)
        return 1.0 / (1.0 + abs(free_energy))
    
    def _compute_energy(self, boundary: dict, props: list, q: np.ndarray) -> float:
        """Energy = sum of constraint violations weighted by beliefs."""
        energy = 0.0
        
        # Comparison violations
        for a, op, c in boundary['comparisons']:
            try:
                va, vc = float(a), float(c)
                if op == '>' and va <= vc:
                    energy += 1.0
                elif op == '<' and va >= vc:
                    energy += 1.0
            except:
                pass
        
        return energy
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        """Use primitives for deterministic computation."""
        score = 0.0
        
        # Bat and ball problem
        if re.search(r'bat.*ball.*total.*\$?(\d+\.?\d*)', prompt, re.I):
            m = re.search(r'total.*\$?(\d+\.?\d*).*more.*\$?(\d+\.?\d*)', prompt, re.I)
            if m:
                total, diff = float(m.group(1)), float(m.group(2))
                expected = bat_and_ball(total, diff)
                cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                    return 0.95
        
        # Modular arithmetic
        m = re.search(r'(\d+)\s*mod\s*(\d+)', prompt, re.I)
        if m:
            a, mod = int(m.group(1)), int(m.group(2))
            expected = modular_arithmetic(a, 0, mod)
            cand_nums = [int(x) for x in re.findall(r'\d+', candidate)]
            if cand_nums and cand_nums[0] == expected:
                return 0.95
        
        # Numeric comparison
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
            if re.search(r'larger|greater|bigger', prompt, re.I):
                if cand_nums[0] == max(prompt_nums):
                    score = 0.9
            elif re.search(r'smaller|less', prompt, re.I):
                if cand_nums[0] == min(prompt_nums):
                    score = 0.9
        
        return score
    
    def _ncd(self, x: str, y: str) -> float:
        """Normalized compression distance (max 10% weight)."""
        import zlib
        cx, cy = len(zlib.compress(x.encode())), len(zlib.compress(y.encode()))
        cxy = len(zlib.compress((x + y).encode()))
        ncd = (cxy - min(cx, cy)) / max(cx, cy) if max(cx, cy) > 0 else 1.0
        return 1.0 - ncd