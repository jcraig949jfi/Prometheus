from typing import Any, Dict, Optional, Tuple

"""
Program Synthesis x Free Energy Principle x Hoare Logic Reasoning Tool

Core mechanism:
1. Parse prompt into constraint graph (propositions, intervals, orderings)
2. Synthesize verification programs (Hoare triples) for each constraint
3. Execute programs on candidates to compute violations (free energy)
4. Score = 1/(1+E) where E is total constraint violation cost
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    def __init__(self):
        self.constraint_graph = []
        self.interval_constraints = {}
        self.ordering_constraints = []
        self.hoare_triples = []
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by constraint satisfaction (lower free energy = higher score)"""
        # Build constraint graph from prompt
        self._parse_prompt(prompt)
        
        results = []
        for cand in candidates:
            violations = self._compute_violations(prompt, cand)
            energy = self._free_energy(violations)
            score = 1.0 / (1.0 + energy)
            
            # Add small NCD component (max 15% influence)
            ncd = self._ncd(prompt, cand)
            final_score = 0.85 * score + 0.15 * (1 - ncd)
            
            reasoning = f"Violations: {len(violations)}, Energy: {energy:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks"""
        meta_conf = self._meta_confidence(prompt)
        
        self._parse_prompt(prompt)
        violations = self._compute_violations(prompt, answer)
        energy = self._free_energy(violations)
        base_conf = 1.0 / (1.0 + energy)
        
        # Cap by metacognitive assessment
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability"""
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|did you stop|quit|why did.*fail|why.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy: "Either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(measure|metric|criteria|because)\b', p_lower):
                return 0.3
        
        # Insufficient information
        if re.search(r'\b(not enough|cannot determine|insufficient)\b', p_lower):
            return 0.25
        
        return 0.95  # High confidence in well-formed questions
    
    def _parse_prompt(self, prompt: str):
        """Extract constraints into intermediate representation"""
        self.constraint_graph = []
        self.interval_constraints = {}
        self.ordering_constraints = []
        self.hoare_triples = []
        
        # Numeric constraints
        self._parse_numeric(prompt)
        
        # Logical propositions with polarity
        self._parse_logical(prompt)
        
        # Temporal/ordering constraints
        self._parse_ordering(prompt)
        
        # Conditional/causal Hoare triples
        self._parse_conditionals(prompt)
    
    def _parse_numeric(self, text: str):
        """Extract numeric comparisons and intervals"""
        # Pattern: "X > Y", "X < Y", "X = Y"
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', text):
            left, op, right = float(m.group(1)), m.group(2), float(m.group(3))
            self.constraint_graph.append(('numeric', left, op, right))
        
        # Pattern: "costs $X", "has N items"
        for m in re.finditer(r'\$?(\d+\.?\d*)', text):
            val = float(m.group(1))
            self.interval_constraints[m.group(0)] = (val, val)
    
    def _parse_logical(self, text: str):
        """Extract propositions with negation polarity"""
        # Negation detection
        for m in re.finditer(r'\b(not|no|never|cannot)\s+(\w+)', text.lower()):
            self.constraint_graph.append(('proposition', m.group(2), -1))
        
        # Positive assertions (subject-verb-object)
        for m in re.finditer(r'(\w+)\s+(is|are|was|were|has|have)\s+(\w+)', text.lower()):
            subj, verb, obj = m.groups()
            self.constraint_graph.append(('proposition', f"{subj}_{verb}_{obj}", 1))
    
    def _parse_ordering(self, text: str):
        """Extract temporal/ordering constraints"""
        # "before", "after", "first", "last"
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text.lower()):
            a, rel, b = m.groups()
            self.ordering_constraints.append((a, rel, b))
    
    def _parse_conditionals(self, text: str):
        """Extract if-then, causal relationships as Hoare triples"""
        # "if P then Q"
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.,;]', text.lower()):
            precond, postcond = m.groups()
            self.hoare_triples.append(('if_then', precond.strip(), postcond.strip()))
        
        # "X causes/leads to Y"
        for m in re.finditer(r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)', text.lower()):
            cause, _, effect = m.groups()
            self.hoare_triples.append(('causal', cause, effect))
    
    def _compute_violations(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """Execute verification programs, return violations with costs"""
        violations = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric violations
        violations.extend(self._check_numeric(prompt, candidate))
        
        # Logical violations
        violations.extend(self._check_logical(prompt, candidate))
        
        # Ordering violations
        violations.extend(self._check_ordering(candidate))
        
        # Hoare triple violations
        violations.extend(self._check_hoare(prompt, candidate))
        
        # Standard computational patterns
        violations.extend(self._check_arithmetic(prompt, candidate))
        violations.extend(self._check_modus_tollens(prompt, candidate))
        violations.extend(self._check_transitivity(prompt, candidate))
        
        return violations
    
    def _check_numeric(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """Check numeric constraints"""
        violations = []
        
        # Extract numbers from candidate
        cand_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', candidate)]
        
        for constraint in self.constraint_graph:
            if constraint[0] == 'numeric':
                _, left, op, right = constraint
                
                # Check if constraint is satisfied
                satisfied = False
                if op in ['>', 'greater']:
                    satisfied = left > right
                elif op in ['<', 'less']:
                    satisfied = left < right
                elif op in ['>=']:
                    satisfied = left >= right
                elif op in ['<=']:
                    satisfied = left <= right
                elif op in ['=', 'equals', 'equal']:
                    satisfied = abs(left - right) < 0.01
                
                # If constraint violated in prompt, check candidate reflects it
                if not satisfied:
                    violations.append(('numeric_constraint', 1.0))
        
        # Bat-and-ball algebra: "X + Y = Z, X costs $Y more"
        bat_ball = re.search(r'(\d+\.?\d*)\s*more.*total.*\$?(\d+\.?\d*)', prompt.lower())
        if bat_ball:
            diff = float(bat_ball.group(1))
            total = float(bat_ball.group(2))
            # Solve: x + (x + diff) = total => x = (total - diff) / 2
            solution = (total - diff) / 2
            if cand_nums and abs(cand_nums[0] - solution) > 0.01:
                violations.append(('bat_ball', abs(cand_nums[0] - solution)))
        
        return violations
    
    def _check_logical(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """Check logical proposition violations"""
        violations = []
        c_lower = candidate.lower()
        
        for constraint in self.constraint_graph:
            if constraint[0] == 'proposition':
                _, prop, polarity = constraint
                
                # Check if proposition appears in candidate with wrong polarity
                if polarity == -1:  # Should NOT appear
                    if prop in c_lower and 'not' not in c_lower:
                        violations.append(('negation_violation', 1.0))
                elif polarity == 1:  # Should appear
                    if prop not in c_lower:
                        violations.append(('missing_proposition', 1.0))
        
        return violations
    
    def _check_ordering(self, candidate: str) -> List[Tuple[str, float]]:
        """Check temporal ordering via transitivity"""
        violations = []
        c_lower = candidate.lower()
        
        # Build ordering graph and check transitivity
        for i, (a1, rel1, b1) in enumerate(self.ordering_constraints):
            for j, (a2, rel2, b2) in enumerate(self.ordering_constraints[i+1:]):
                # Transitivity: if A before B and B before C, then A before C
                if b1 == a2 and rel1 == 'before' and rel2 == 'before':
                    # Check if candidate violates transitivity
                    if f"{b2} before {a1}" in c_lower:
                        violations.append(('transitivity', 2.0))
        
        return violations
    
    def _check_hoare(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """Check Hoare triples: {P} C {Q}"""
        violations = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        for triple in self.hoare_triples:
            kind, precond, postcond = triple
            
            # If precondition holds in prompt, postcondition must hold in candidate
            if precond in p_lower:
                if postcond not in c_lower:
                    violations.append(('hoare_triple', 2.0))
        
        return violations
    
    def _check_arithmetic(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """Compute arithmetic expressions (PEMDAS)"""
        violations = []
        
        # Pattern: "What is X + Y * Z?"
        expr = re.search(r'what is\s+([\d\s\+\-\*/\(\)\.]+)', prompt.lower())
        if expr:
            try:
                computed = eval(expr.group(1))
                cand_nums = [float(m.group()) for m in re.finditer(r'-?\d+\.?\d*', candidate)]
                if cand_nums and abs(cand_nums[0] - computed) > 0.01:
                    violations.append(('arithmetic', abs(cand_nums[0] - computed)))
            except:
                pass
        
        return violations
    
    def _check_modus_tollens(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """If P->Q and not Q, then not P"""
        violations = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Pattern: "If P then Q. Not Q. Therefore?"
        if 'if' in p_lower and 'then' in p_lower and 'not' in p_lower:
            # Extract implication
            impl = re.search(r'if\s+(\w+).*then\s+(\w+)', p_lower)
            if impl:
                p, q = impl.groups()
                # If "not Q" in prompt, candidate should have "not P"
                if f"not {q}" in p_lower or f"no {q}" in p_lower:
                    if f"not {p}" not in c_lower and f"no {p}" not in c_lower:
                        violations.append(('modus_tollens', 1.0))
        
        return violations
    
    def _check_transitivity(self, prompt: str, candidate: str) -> List[Tuple[str, float]]:
        """A > B, B > C => A > C"""
        violations = []
        
        # Extract all comparisons
        comparisons = list(re.finditer(r'(\w+)\s+(>|<|taller|shorter|faster|slower)\s+(\w+)', prompt.lower()))
        
        # Check transitivity
        for i, m1 in enumerate(comparisons):
            a, rel1, b = m1.groups()
            for m2 in comparisons[i+1:]:
                c, rel2, d = m2.groups()
                if b == c and rel1 == rel2:
                    # A > B and B > D => A > D should be in candidate
                    if f"{a} {rel1} {d}" not in candidate.lower():
                        violations.append(('transitivity', 0.5))
        
        return violations
    
    def _free_energy(self, violations: List[Tuple[str, float]]) -> float:
        """Compute total free energy (prediction error)"""
        if not violations:
            return 0.0
        
        total = sum(cost for _, cost in violations)
        return total
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0