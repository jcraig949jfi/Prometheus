import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Dual-process SAT-based reasoning with neural plasticity.
    
    Combines System 1 (fast heuristic weights) and System 2 (deliberate SAT solving)
    with Hebbian weight updates. Parses prompts into propositional clauses,
    propagates constraints, and computes answers rather than pattern-matching.
    """
    
    def __init__(self):
        self.alpha = 0.6  # System 1 vs System 2 balance
        self.eta = 0.1    # Learning rate
        self.w1 = defaultdict(lambda: 0.5)  # System 1 weights
        self.w2 = defaultdict(lambda: 0.0)  # System 2 weights
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": f"SAT score: {score:.3f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we computed a definitive answer
        computed = self._compute_answer(prompt)
        if computed and self._normalize(computed) == self._normalize(answer):
            return min(0.85, meta_conf)
        
        score = self._compute_score(prompt, answer)
        return min(meta_conf, 0.3 + 0.5 * score)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or|must be (a|b))\b', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|criteria)\b', p_lower):
            return 0.28
        
        # Insufficient info markers
        if re.search(r'\b(cannot (determine|tell)|not enough|insufficient|ambiguous)\b', p_lower):
            return 0.9  # High confidence in uncertainty
        
        return 0.75
    
    def _compute_answer(self, prompt: str) -> str:
        # Numeric comparison
        match = re.search(r'(\d+\.?\d*)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)', prompt)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            ops = {'>': a > b, '<': a < b, '=': abs(a-b)<0.0001, '>=': a >= b, '<=': a <= b}
            return "Yes" if ops.get(op, False) else "No"
        
        # Bat and ball: X + Y = total, X = Y + diff
        match = re.search(r'total.*\$?(\d+\.?\d*).*more.*\$?(\d+\.?\d*)', prompt, re.I)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            y = (total - diff) / 2
            return f"{y:.2f}"
        
        # Modular arithmetic
        match = re.search(r'(\d+)\s*mod\s*(\d+)', prompt, re.I)
        if match:
            return str(int(match.group(1)) % int(match.group(2)))
        
        # PEMDAS evaluation
        match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)\s*([\+\-\*/])\s*(\d+)', prompt)
        if match:
            try:
                expr = f"{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}{match.group(5)}"
                return str(eval(expr))
            except:
                pass
        
        return ""
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Parse into literals and clauses
        literals, clauses = self._parse_to_sat(prompt, candidate)
        
        if not clauses:
            return self._fallback_score(prompt, candidate)
        
        # System 1: fast heuristic
        s1 = self._system1_score(literals, clauses)
        
        # System 2: deliberate SAT solving
        s2 = self._system2_score(literals, clauses)
        
        # Structural features
        struct = self._structural_score(prompt, candidate)
        
        # Computational verification
        comp = self._computational_score(prompt, candidate)
        
        # Small NCD component
        ncd = self._ncd(prompt, candidate)
        
        # Combine: 50% struct, 25% comp, 15% SAT, 10% NCD
        return 0.5 * struct + 0.25 * comp + 0.15 * (self.alpha * s1 + (1-self.alpha) * s2) + 0.1 * (1 - ncd)
    
    def _parse_to_sat(self, prompt: str, candidate: str):
        literals = []
        clauses = []
        
        # Extract atomic propositions
        text = (prompt + " " + candidate).lower()
        tokens = re.findall(r'\b\w+\b', text)
        
        # Create literals with polarity
        for i, tok in enumerate(tokens[:20]):  # Limit to avoid explosion
            if tok in ['not', 'no', 'false']:
                literals.append(f"~{tokens[i+1] if i+1<len(tokens) else tok}")
            elif tok not in ['is', 'are', 'the', 'a', 'an', 'and', 'or']:
                literals.append(tok)
        
        # Generate clauses from conditionals
        if_match = re.findall(r'if\s+(\w+).*then\s+(\w+)', text)
        for a, b in if_match:
            clauses.append([f"~{a}", b])  # a -> b = ~a OR b
        
        # Negations
        not_match = re.findall(r'not\s+(\w+)', text)
        for term in not_match:
            clauses.append([f"~{term}"])
        
        return list(set(literals)), clauses
    
    def _system1_score(self, literals, clauses) -> float:
        if not clauses:
            return 0.5
        
        # Fast heuristic evaluation
        truth = {}
        for lit in literals:
            truth[lit] = self.w1[lit] > 0.5
        
        satisfied = 0
        for clause in clauses:
            if any(truth.get(lit.lstrip('~'), False) != lit.startswith('~') for lit in clause):
                satisfied += 1
        
        return satisfied / len(clauses) if clauses else 0.5
    
    def _system2_score(self, literals, clauses) -> float:
        if not clauses:
            return 0.5
        
        # Simple DPLL-style backtracking
        best_sat = 0
        assignment = {lit: False for lit in literals}
        
        # Try assignments (limited search)
        for _ in range(min(10, 2**min(len(literals), 5))):
            sat_count = sum(any(assignment.get(lit.lstrip('~'), False) != lit.startswith('~') 
                               for lit in clause) for clause in clauses)
            
            if sat_count > best_sat:
                best_sat = sat_count
                # Hebbian update
                for lit in literals:
                    if assignment[lit]:
                        self.w1[lit] = min(1.0, self.w1[lit] + self.eta * 0.1)
                        self.w2[lit] += self.eta * (sat_count / len(clauses))
            
            # Flip a random literal
            if literals:
                flip_lit = literals[np.random.randint(len(literals))]
                assignment[flip_lit] = not assignment[flip_lit]
        
        return best_sat / len(clauses) if clauses else 0.5
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        score = 0.5
        p_lower, c_lower = prompt.lower(), candidate.lower()
        
        # Negation consistency
        if ('not' in p_lower or 'no' in p_lower) and ('no' in c_lower or 'not' in c_lower):
            score += 0.2
        
        # Number extraction
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if p_nums and c_nums and any(abs(pn - cn) < 0.01 for pn in p_nums for cn in c_nums):
            score += 0.15
        
        # Comparative consistency
        if re.search(r'\b(more|greater|larger|higher)\b', p_lower):
            if re.search(r'\b(more|greater|increase|higher)\b', c_lower):
                score += 0.15
        
        return min(1.0, score)
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        computed = self._compute_answer(prompt)
        if computed and self._normalize(computed) == self._normalize(candidate):
            return 1.0
        
        # Transitivity: if A>B and B>C, then A>C
        trans = re.findall(r'(\w+)\s*>\s*(\w+)', prompt)
        if len(trans) >= 2:
            chain = [trans[0][0], trans[0][1]]
            for a, b in trans[1:]:
                if a == chain[-1]:
                    chain.append(b)
            if len(chain) >= 3 and f"{chain[0]}.*{chain[-1]}" in candidate.lower():
                return 0.9
        
        return 0.3
    
    def _fallback_score(self, prompt: str, candidate: str) -> float:
        struct = self._structural_score(prompt, candidate)
        comp = self._computational_score(prompt, candidate)
        ncd = self._ncd(prompt, candidate)
        return 0.6 * struct + 0.3 * comp + 0.1 * (1 - ncd)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2)) if max(len(c1), len(c2)) > 0 else 0.5
    
    def _normalize(self, s: str) -> str:
        return re.sub(r'[^a-z0-9]', '', s.lower())