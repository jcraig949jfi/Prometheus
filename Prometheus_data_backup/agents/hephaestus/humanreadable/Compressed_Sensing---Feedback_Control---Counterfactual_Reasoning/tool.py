import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Combines Compressed Sensing, Feedback Control, and Counterfactual Reasoning.
    
    Mechanism:
    1. Parse prompt into atomic propositions and logical constraints
    2. Build sparse constraint matrix A and target vector b
    3. Use iterative feedback control (PID-inspired) to find consistent truth assignment
    4. Score candidates by counterfactual residual: how well does the world where
       the answer is true satisfy the original constraints?
    5. Meta-confidence detects ambiguity, presupposition, and unanswerability
    """
    
    def __init__(self):
        self.kp = 0.3  # PID proportional gain
        self.ki = 0.05  # PID integral gain
        self.kd = 0.1  # PID derivative gain
        
    def _parse_propositions(self, text: str) -> Tuple[List[str], List[Tuple], Dict]:
        """Extract atomic propositions and constraints from text."""
        propositions = []
        constraints = []
        prop_map = {}
        
        # Normalize text
        text = text.lower()
        
        # Extract atomic propositions from simple patterns
        # Negations
        for match in re.finditer(r'(not|no|never)\s+([a-z]+(?:\s+[a-z]+){0,3})', text):
            prop = match.group(2).strip()
            if prop not in prop_map:
                prop_map[prop] = len(propositions)
                propositions.append(prop)
            constraints.append(('neg', prop_map[prop]))
        
        # Conditionals: "if X then Y" or "X implies Y"
        for match in re.finditer(r'if\s+([^,]+?)\s+then\s+([^,.]+)', text):
            antecedent = match.group(1).strip()
            consequent = match.group(2).strip()
            if antecedent not in prop_map:
                prop_map[antecedent] = len(propositions)
                propositions.append(antecedent)
            if consequent not in prop_map:
                prop_map[consequent] = len(propositions)
                propositions.append(consequent)
            constraints.append(('implies', prop_map[antecedent], prop_map[consequent]))
        
        # Comparatives: extract numeric comparisons
        numeric_map = {}
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text):
            left, op, right = float(match.group(1)), match.group(2), float(match.group(3))
            prop = f"{left}{op}{right}"
            result = self._eval_comparison(left, op, right)
            if prop not in prop_map:
                prop_map[prop] = len(propositions)
                propositions.append(prop)
                numeric_map[prop_map[prop]] = result
        
        # Simple assertions (words that appear frequently)
        words = re.findall(r'\b[a-z]+\b', text)
        for word in set(words):
            if len(word) > 3 and word not in ['then', 'that', 'this', 'with', 'have', 'from']:
                if word not in prop_map:
                    prop_map[word] = len(propositions)
                    propositions.append(word)
        
        return propositions, constraints, numeric_map
    
    def _eval_comparison(self, left: float, op: str, right: float) -> bool:
        """Evaluate numeric comparison."""
        if op == '>': return left > right
        if op == '<': return left < right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '=': return abs(left - right) < 1e-9
        return False
    
    def _build_constraint_matrix(self, n_props: int, constraints: List, numeric_map: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Build sparse constraint matrix A and target b."""
        n_constraints = len(constraints) + len(numeric_map)
        A = np.zeros((n_constraints, n_props))
        b = np.zeros(n_constraints)
        
        for i, constraint in enumerate(constraints):
            if constraint[0] == 'neg':
                # Negation: x_i should be 0
                A[i, constraint[1]] = 1.0
                b[i] = 0.0
            elif constraint[0] == 'implies':
                # Implication: -x_i + x_j = 0 (enforces x_i <= x_j)
                A[i, constraint[1]] = -1.0
                A[i, constraint[2]] = 1.0
                b[i] = 0.0
        
        # Numeric constraints
        for idx, (prop_idx, value) in enumerate(numeric_map.items()):
            row = len(constraints) + idx
            A[row, prop_idx] = 1.0
            b[row] = 1.0 if value else 0.0
        
        return A, b
    
    def _sparse_recovery_with_feedback(self, A: np.ndarray, b: np.ndarray, iterations: int = 8) -> np.ndarray:
        """Compressed sensing with PID feedback control."""
        n = A.shape[1]
        if n == 0:
            return np.array([])
        
        x = np.full(n, 0.5)  # Initialize to neutral
        
        # Regularization for underdetermined systems
        lambda_reg = 0.01
        A_reg = np.vstack([A, lambda_reg * np.eye(n)])
        
        integral = np.zeros(n)
        prev_residual = np.zeros(A.shape[0])
        
        for _ in range(iterations):
            b_reg = np.concatenate([b, np.zeros(n)])
            
            try:
                x_new = solve_linear_system(A_reg, b_reg)
                if x_new is None or len(x_new) != n:
                    x_new = np.linalg.lstsq(A_reg, b_reg, rcond=None)[0]
            except:
                break
            
            # PID feedback control
            residual = b - A @ x_new
            integral += residual * 0.1
            derivative = residual - prev_residual
            
            correction = self.kp * A.T @ residual + self.ki * integral + self.kd * A.T @ derivative
            x = np.clip(x_new + correction, 0, 1)
            
            prev_residual = residual
            
            if np.linalg.norm(residual) < 1e-6:
                break
        
        return x
    
    def _counterfactual_score(self, A: np.ndarray, b: np.ndarray, x_base: np.ndarray, 
                             candidate: str, prop_map: Dict) -> float:
        """Score candidate by counterfactual residual."""
        if len(x_base) == 0:
            return 0.0
        
        x_cf = x_base.copy()
        
        # Flip propositions mentioned in candidate
        candidate_lower = candidate.lower()
        for prop, idx in prop_map.items():
            if prop in candidate_lower:
                # If "not" precedes the prop in candidate, set to 0, else 1
                pattern = r'\b(?:not|no)\s+' + re.escape(prop)
                if re.search(pattern, candidate_lower):
                    x_cf[idx] = 0.0
                else:
                    x_cf[idx] = 1.0
        
        # Refine counterfactual assignment
        x_cf_refined = self._sparse_recovery_with_feedback(A, b, iterations=3)
        if len(x_cf_refined) == len(x_cf):
            x_cf = x_cf_refined
        
        # Score by residual (lower is better)
        residual = np.linalg.norm(b - A @ x_cf)
        return -residual
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower):
            if not re.search(r'\b(measure|metric|criterion|according to)\b', prompt_lower):
                return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot be|not enough|insufficient)\b', prompt_lower):
            return 0.25
        
        return 1.0  # No red flags
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        # Parse prompt structure
        propositions, constraints, numeric_map = self._parse_propositions(prompt)
        
        if len(propositions) == 0:
            # Fallback to pure NCD if no structure found
            results = []
            for cand in candidates:
                ncd_score = 1.0 - self._ncd(prompt, cand)
                results.append({
                    'candidate': cand,
                    'score': ncd_score * 0.5,
                    'reasoning': 'No logical structure detected; using similarity only'
                })
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Build constraint system
        A, b = self._build_constraint_matrix(len(propositions), constraints, numeric_map)
        
        # Sparse recovery with feedback control
        x_base = self._sparse_recovery_with_feedback(A, b)
        
        # Score each candidate
        results = []
        for cand in candidates:
            # Counterfactual score (primary)
            cf_score = self._counterfactual_score(A, b, x_base, cand, 
                                                 {p: i for i, p in enumerate(propositions)})
            
            # NCD score (secondary, max 10%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combined score: 85% counterfactual, 15% NCD
            final_score = 0.85 * (cf_score + 10) / 20 + 0.15 * ncd_score
            
            results.append({
                'candidate': cand,
                'score': max(0.0, min(1.0, final_score)),
                'reasoning': f'CF residual: {cf_score:.3f}, constraints: {len(constraints)}, props: {len(propositions)}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a proposed answer."""
        # Meta-confidence check (caps the result)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer against prompt
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        score = results[0]['score']
        
        # Parse to check if we found structure
        propositions, constraints, _ = self._parse_propositions(prompt)
        
        # If no structure found, return low confidence
        if len(propositions) == 0:
            return min(0.4, score * meta_conf)
        
        # Scale based on constraint density
        density_factor = min(1.0, len(constraints) / max(1, len(propositions)))
        
        # Never exceed 0.9 unless very high score and dense constraints
        conf = score * meta_conf * (0.6 + 0.4 * density_factor)
        
        return min(0.85, max(0.05, conf))