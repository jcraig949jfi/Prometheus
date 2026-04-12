from typing import Any, Dict, Set, Tuple

import re
import zlib
from typing import List, Dict, Any, Set, Tuple

class ReasoningTool:
    """
    NAS x Kolmogorov Complexity x Pragmatics reasoning tool.
    
    Enumerates programs in a logical-numeric DSL, scores via MDL + pragmatic penalties,
    and uses meta-confidence to detect ambiguity/presupposition traps.
    """
    
    def __init__(self):
        self.max_depth = 4
        self.memo = {}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        atoms = self._extract_atoms(prompt)
        results = []
        
        for cand in candidates:
            programs = self._enumerate_programs(atoms, cand, self.max_depth)
            if programs:
                best_prog, best_score = min(programs, key=lambda p: self._mdl_score(p, atoms, cand))
                score = -best_score  # Higher is better
                reasoning = f"Program: {best_prog[:50]}, atoms: {len(atoms)}"
            else:
                score = self._ncd_fallback(prompt, cand)
                reasoning = "NCD fallback"
            
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        atoms = self._extract_atoms(prompt)
        programs = self._enumerate_programs(atoms, answer, self.max_depth)
        
        if not programs:
            return 0.2
        
        best_prog, best_score = min(programs, key=lambda p: self._mdl_score(p, atoms, answer))
        
        # Normalize MDL score to confidence
        base_conf = max(0.3, min(0.85, 1.0 / (1.0 + best_score / 10.0)))
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+ .* a \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy: "Either A or B" questions
        if re.search(r'\beither .* or \b', p_lower) and '?' in prompt:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\b(by|according to|measured by)\b', p_lower):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\b(insufficient|not enough|cannot determine|unknowable)\b', p_lower):
            return 0.25
        
        return 1.0
    
    def _extract_atoms(self, text: str) -> Set[Tuple]:
        atoms = set()
        t_lower = text.lower()
        
        # Negations
        for match in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', t_lower):
            atoms.add(('Neg', match.group(2)))
        
        # Numeric comparisons
        for match in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|=|equals?)\s*([\d.]+)', text):
            n1, op, n2 = float(match.group(1)), match.group(2), float(match.group(3))
            atoms.add(('Cmp', op, n1, n2))
        
        # Comparatives in text
        for match in re.finditer(r'(\w+)\s+(?:is\s+)?(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', t_lower):
            atoms.add(('Gt', match.group(1), match.group(3)))
        
        # Conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', t_lower):
            atoms.add(('Imp', match.group(1).strip(), match.group(2).strip()))
        
        # Causal markers
        for match in re.finditer(r'(\w+)\s+(because|leads to|causes|enables)\s+(\w+)', t_lower):
            atoms.add(('Cause', match.group(1), match.group(3)))
        
        # Extract all numbers for computation
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            atoms.add(('Num', float(match.group())))
        
        return atoms
    
    def _enumerate_programs(self, atoms: Set[Tuple], target: str, max_depth: int) -> List[Tuple[str, Any]]:
        programs = []
        
        # Direct numeric comparison
        prog = self._try_numeric_eval(atoms, target)
        if prog:
            programs.append(prog)
        
        # Logical inference
        prog = self._try_logical_eval(atoms, target)
        if prog:
            programs.append(prog)
        
        # Arithmetic computation
        prog = self._try_arithmetic(atoms, target)
        if prog:
            programs.append(prog)
        
        return programs
    
    def _try_numeric_eval(self, atoms: Set[Tuple], target: str) -> Tuple[str, bool]:
        t_lower = target.lower()
        
        for atom in atoms:
            if atom[0] == 'Cmp':
                _, op, n1, n2 = atom
                result = None
                if op in ('>', 'greater'):
                    result = n1 > n2
                elif op in ('<', 'less'):
                    result = n1 < n2
                elif op in ('>='):
                    result = n1 >= n2
                elif op in ('<='):
                    result = n1 <= n2
                elif op in ('=', 'equals', 'equal'):
                    result = abs(n1 - n2) < 1e-9
                
                if result is not None:
                    match = ('yes' in t_lower or 'true' in t_lower or 'correct' in t_lower) == result
                    if match or ('no' in t_lower or 'false' in t_lower or 'incorrect' in t_lower) == (not result):
                        return (f"Cmp({op},{n1},{n2})", result)
        
        return None
    
    def _try_logical_eval(self, atoms: Set[Tuple], target: str) -> Tuple[str, bool]:
        t_lower = target.lower()
        
        # Modus tollens / ponens
        for atom in atoms:
            if atom[0] == 'Imp':
                antecedent, consequent = atom[1], atom[2]
                if antecedent in t_lower or consequent in t_lower:
                    return (f"Imp({antecedent},{consequent})", True)
        
        # Negation handling
        for atom in atoms:
            if atom[0] == 'Neg':
                term = atom[1]
                if term in t_lower:
                    has_not = bool(re.search(r'\bnot\b', t_lower))
                    return (f"Neg({term})", has_not)
        
        return None
    
    def _try_arithmetic(self, atoms: Set[Tuple], target: str) -> Tuple[str, float]:
        nums = [a[1] for a in atoms if a[0] == 'Num']
        
        if len(nums) >= 2:
            # Try basic operations
            for i, n1 in enumerate(nums):
                for n2 in nums[i+1:]:
                    results = [
                        ('Add', n1 + n2),
                        ('Sub', n1 - n2),
                        ('Mul', n1 * n2),
                        ('Div', n1 / n2 if n2 != 0 else None)
                    ]
                    
                    for op, val in results:
                        if val is not None and str(val) in target:
                            return (f"{op}({n1},{n2})", val)
        
        return None
    
    def _mdl_score(self, program: Tuple, atoms: Set[Tuple], target: str) -> float:
        prog_str, result = program
        
        # Kolmogorov approximation: bit length of program
        k_complex = len(prog_str.encode()) * 8
        
        # Likelihood: does program output match target?
        likelihood = 1.0 if str(result).lower() in target.lower() else 0.01
        mdl = k_complex - 10 * (likelihood if likelihood > 0.5 else 0)
        
        # Pragmatic penalties (Grice maxims)
        penalty = 0
        
        # Quantity: irrelevant complexity
        if len(prog_str) > 30:
            penalty += 5
        
        # Relation: using atoms not in input
        penalty += max(0, len(prog_str) - len(atoms) * 10) * 0.1
        
        # Manner: excessive depth (approximated by nested parens)
        depth = prog_str.count('(')
        if depth > 2:
            penalty += (depth - 2) * 3
        
        return mdl + penalty
    
    def _ncd_fallback(self, prompt: str, candidate: str) -> float:
        def ncd(s1: str, s2: str) -> float:
            c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
            c12 = zlib.compress((s1 + s2).encode())
            return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        
        # NCD contributes at most 15% of score
        return 0.15 * (1.0 - ncd(prompt, candidate))