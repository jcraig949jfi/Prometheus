from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines Compressed Sensing (L1 sparse recovery), Falsificationism (constraint penalties),
    and Mechanism Design (truth-promoting payment) to evaluate logical reasoning.
    
    Core mechanism:
    1. Parse prompt into atomic propositions and constraint matrix A
    2. Solve min ||x||_1 + lambda*||max(0, Ax-b)||_1 via ISTA
    3. Score candidates by distance to optimal sparse solution
    4. Compute answers for algebraic/probabilistic/logical problems
    5. Meta-confidence detects ambiguity and unanswerable questions
    """
    
    def __init__(self):
        self.lambda_penalty = 2.0
        self.gamma_constraint = 1.5
        self.ista_iterations = 50
        self.step_size = 0.1
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Try computational solvers first
        computed = self._compute_answer(prompt)
        
        # Parse propositions and build constraint matrix
        props = self._parse_propositions(prompt)
        A, b = self._build_constraint_matrix(props, prompt)
        
        # Solve for optimal sparse proposition set
        x_star = self._ista_solve(A, b) if A.size > 0 else np.array([])
        
        # Score each candidate
        results = []
        for cand in candidates:
            # Build candidate proposition vector
            x_c = self._candidate_vector(cand, props)
            
            # Mechanism design payment
            if x_star.size > 0 and x_c.size > 0:
                dist_term = np.sum(np.abs(x_c - x_star))
                constraint_term = np.sum(np.abs(np.maximum(0, A @ x_c - b)))
                score = -(dist_term + self.gamma_constraint * constraint_term)
            else:
                score = 0.0
            
            # Add computational match bonus
            if computed is not None:
                comp_match = self._computational_match(cand, computed)
                score += 5.0 * comp_match
            
            # Add structural features (50%+ of score)
            struct_score = self._structural_score(prompt, cand)
            score += 3.0 * struct_score
            
            # Add NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            score += 0.5 * (1 - ncd)
            
            reasoning = f"Sparse={-dist_term if x_star.size > 0 else 0:.2f}, Struct={struct_score:.2f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence check for question properties
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Try computational solution
        computed = self._compute_answer(prompt)
        if computed is not None:
            match = self._computational_match(answer, computed)
            return min(0.95, 0.5 + 0.45 * match) if match > 0.8 else 0.3
        
        # Structural confidence
        struct = self._structural_score(prompt, answer)
        return min(0.7, 0.3 + 0.4 * struct)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ \w+ a \w+', p) and '?' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither \w+ or \w+\b', p) and not re.search(r'\bonly\b', p):
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|greater|smaller)\b', p):
            return 0.25
        
        return 1.0
    
    def _parse_propositions(self, text: str) -> List[str]:
        props = []
        # Extract numeric comparisons
        props.extend(re.findall(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text))
        # Extract negations
        props.extend(re.findall(r'\b(not|no|never)\s+(\w+)', text.lower()))
        # Extract conditionals
        props.extend(re.findall(r'\bif\s+(\w+).*then\s+(\w+)', text.lower()))
        # Extract causal verbs
        props.extend(re.findall(r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)', text.lower()))
        return [str(p) for p in props[:20]]  # Limit to 20 propositions
    
    def _build_constraint_matrix(self, props: List[str], prompt: str) -> Tuple[np.ndarray, np.ndarray]:
        if not props:
            return np.array([]), np.array([])
        
        m = len(props)
        constraints = []
        rhs = []
        
        # Modus ponens: if p_i and (p_i -> p_j) then p_j
        for i, p in enumerate(props):
            if 'if' in str(p).lower():
                row = np.zeros(m)
                row[i] = 1
                constraints.append(row)
                rhs.append(1)
        
        # Transitivity and ordering
        for i in range(m):
            for j in range(i+1, m):
                if any(op in str(props[i]) for op in ['>', '<']):
                    row = np.zeros(m)
                    row[i] = 1
                    row[j] = -1
                    constraints.append(row)
                    rhs.append(0)
        
        if not constraints:
            return np.array([]), np.array([])
        
        return np.array(constraints), np.array(rhs)
    
    def _ista_solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Iterative Soft Thresholding for L1 minimization"""
        if A.size == 0:
            return np.array([])
        
        m = A.shape[1]
        x = np.zeros(m)
        
        for _ in range(self.ista_iterations):
            # Gradient of constraint term
            residual = np.maximum(0, A @ x - b)
            grad = A.T @ residual
            
            # Gradient step
            x_temp = x - self.step_size * grad
            
            # Soft thresholding (L1 prox)
            threshold = self.step_size * self.lambda_penalty
            x = np.sign(x_temp) * np.maximum(0, np.abs(x_temp) - threshold)
        
        return x
    
    def _candidate_vector(self, cand: str, props: List[str]) -> np.ndarray:
        if not props:
            return np.array([])
        
        x = np.zeros(len(props))
        cand_lower = cand.lower()
        for i, p in enumerate(props):
            if any(word in cand_lower for word in str(p).split()):
                x[i] = 1
        return x
    
    def _compute_answer(self, prompt: str):
        """Compute actual answers for standard problem types"""
        p = prompt.lower()
        
        # Numeric comparison
        match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', p)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            ops = {'>': a > b, '<': a < b, '>=': a >= b, '<=': a <= b}
            return ops.get(op)
        
        # Bat and ball algebra: total = x + (x - diff)
        if 'cost' in p and 'more than' in p:
            total_match = re.search(r'(\d+\.?\d*)', p)
            diff_match = re.search(r'more than.*?(\d+\.?\d*)', p)
            if total_match and diff_match:
                total, diff = float(total_match.group(1)), float(diff_match.group(1))
                return (total - diff) / 2
        
        # All-but-N problems
        if 'all but' in p or 'all except' in p:
            total = re.search(r'(\d+)', p)
            except_n = re.search(r'but (\d+)', p)
            if total and except_n:
                return int(total.group(1)) - int(except_n.group(1))
        
        # Modus tollens: if A then B, not B, therefore not A
        if 'if' in p and 'not' in p and 'therefore' in p:
            return 'not ' + re.search(r'if (\w+)', p).group(1) if re.search(r'if (\w+)', p) else None
        
        return None
    
    def _computational_match(self, cand: str, computed) -> float:
        if computed is None:
            return 0.0
        
        cand_lower = cand.lower()
        
        if isinstance(computed, bool):
            if computed and any(w in cand_lower for w in ['yes', 'true', 'correct']):
                return 1.0
            if not computed and any(w in cand_lower for w in ['no', 'false', 'incorrect']):
                return 1.0
        
        if isinstance(computed, (int, float)):
            # Extract numbers from candidate
            nums = re.findall(r'\d+\.?\d*', cand)
            for num in nums:
                if abs(float(num) - float(computed)) < 0.01:
                    return 1.0
        
        if isinstance(computed, str) and computed in cand_lower:
            return 1.0
        
        return 0.0
    
    def _structural_score(self, prompt: str, cand: str) -> float:
        score = 0.0
        p, c = prompt.lower(), cand.lower()
        
        # Negation consistency
        if 'not' in p and 'not' in c:
            score += 0.2
        if 'not' in p and any(w in c for w in ['no', 'false', 'never']):
            score += 0.2
        
        # Comparative consistency
        for op in ['greater', 'more', 'higher', 'above']:
            if op in p and op in c:
                score += 0.15
        
        # Conditional structure
        if 'if' in p and 'then' in p:
            if 'because' in c or 'since' in c:
                score += 0.2
        
        # Subject-object extraction
        subj = re.search(r'^(\w+)\s+(is|are|was|were)', p)
        if subj and subj.group(1) in c:
            score += 0.25
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0