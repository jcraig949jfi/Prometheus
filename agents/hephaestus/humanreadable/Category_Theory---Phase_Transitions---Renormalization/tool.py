import re
import numpy as np
import zlib


class ReasoningTool:
    """
    Category Theory x Phase Transitions x Renormalization reasoning tool.
    
    Represents candidate answers as directed hypergraphs where vertices are atomic
    propositions (comparisons, conditionals, negations). Applies renormalization-group
    fixed-point iteration to propagate truth values. Measures spectral radius to detect
    phase transitions - answers near critical point (rho~1) exhibit consistent logical
    structure. Includes meta-confidence for epistemic honesty on ambiguous prompts.
    """
    
    def __init__(self):
        self.max_iter = 50
        self.convergence_tol = 1e-4
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"RG-flow score={score:.3f}, conf={conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Base confidence on structural match + numeric solve
        structural_score = self._structural_match_score(prompt, answer)
        numeric_score = self._numeric_solve_score(prompt, answer)
        
        # Never exceed 0.9 unless we computed a definitive answer
        if numeric_score > 0.8:
            return min(0.85, 0.4 + 0.5 * numeric_score)
        return min(0.7, 0.3 + 0.4 * structural_score)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            if not re.search(r'\b(most|least|greater|measure|metric)\b', p_lower):
                return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(cannot know|impossible to|not enough info)', p_lower):
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Extract propositions from prompt and candidate
        prompt_props = self._extract_propositions(prompt)
        cand_props = self._extract_propositions(candidate)
        
        if not cand_props:
            return 0.3  # Baseline for empty parse
        
        # Build graph adjacency matrix
        all_props = list(set(prompt_props + cand_props))
        n = len(all_props)
        
        if n == 0:
            return 0.3
        
        W = self._build_adjacency_matrix(all_props, prompt, candidate)
        
        # RG fixed-point iteration
        x = np.ones(n) * 0.5  # Initial truth vector
        rho = self._spectral_radius(W)
        
        for _ in range(self.max_iter):
            x_new = self._propagate(W, x)
            if np.linalg.norm(x_new - x) < self.convergence_tol:
                break
            x = x_new
        
        # Phase transition score: closeness to critical point (rho=1)
        if rho > 1e-6:
            phase_score = 1.0 - abs(rho - 1.0) / max(rho, 1.0)
        else:
            phase_score = 0.5
        
        # Structural consistency: fixed-point variance (low=consistent)
        consistency = 1.0 - min(np.var(x), 0.5) * 2.0
        
        # Numeric computation
        numeric_score = self._numeric_solve_score(prompt, candidate)
        
        # NCD (max 15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        # Weighted combination
        final_score = (0.35 * phase_score + 
                      0.25 * consistency + 
                      0.25 * numeric_score + 
                      0.15 * ncd_score)
        
        return max(0.0, min(1.0, final_score))
    
    def _extract_propositions(self, text: str) -> list:
        """Extract atomic propositions: comparisons, conditionals, negations."""
        props = []
        
        # Numeric comparisons: "X > Y", "9.11 < 9.9"
        for match in re.finditer(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text):
            props.append(('numeric', match.group(0)))
        
        # Negations: "not X", "no Y"
        for match in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', text.lower()):
            props.append(('neg', match.group(2)))
        
        # Conditionals: "if X then Y"
        for match in re.finditer(r'\bif\b.*\bthen\b', text.lower()):
            props.append(('cond', match.group(0)))
        
        # Comparatives: "more than", "less than", "greater"
        for match in re.finditer(r'\b(more|less|greater|fewer|higher|lower)\s+than\b', text.lower()):
            props.append(('comp', match.group(0)))
        
        return props
    
    def _build_adjacency_matrix(self, props: list, prompt: str, candidate: str) -> np.ndarray:
        """Build weighted adjacency matrix encoding logical relations."""
        n = len(props)
        W = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 0.5  # Self-consistency
                else:
                    # Connect negations with negative weight
                    if props[i][0] == 'neg' or props[j][0] == 'neg':
                        W[i, j] = -0.3
                    # Connect same-type propositions
                    elif props[i][0] == props[j][0]:
                        W[i, j] = 0.2
                    else:
                        W[i, j] = 0.1
        
        return W
    
    def _propagate(self, W: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Constraint propagation: x_new = sigma(W @ x)."""
        result = W @ x
        return np.clip(result, 0.0, 1.0)  # Clamp to [0,1]
    
    def _spectral_radius(self, W: np.ndarray) -> float:
        """Compute spectral radius (largest eigenvalue magnitude)."""
        try:
            eigvals = np.linalg.eigvals(W)
            return np.max(np.abs(eigvals))
        except:
            return 1.0
    
    def _numeric_solve_score(self, prompt: str, candidate: str) -> float:
        """Solve numeric comparisons and arithmetic."""
        score = 0.0
        count = 0
        
        # Numeric comparison validation
        for match in re.finditer(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', prompt):
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            expected = self._eval_comparison(a, op, b)
            
            # Check if candidate reflects this
            if ('yes' in candidate.lower() or 'true' in candidate.lower()) == expected:
                score += 1.0
            count += 1
        
        # Simple arithmetic: look for "= X" patterns
        for match in re.finditer(r'=\s*(\d+\.?\d*)', candidate):
            count += 1
            score += 0.5  # Partial credit for having a numeric answer
        
        return score / count if count > 0 else 0.5
    
    def _eval_comparison(self, a: float, op: str, b: float) -> bool:
        """Evaluate numeric comparison."""
        if '<' in op:
            return a < b
        elif '>' in op:
            return a > b
        elif '=' in op:
            return abs(a - b) < 1e-6
        return False
    
    def _structural_match_score(self, prompt: str, answer: str) -> float:
        """Score based on structural feature alignment."""
        p_props = self._extract_propositions(prompt)
        a_props = self._extract_propositions(answer)
        
        if not p_props:
            return 0.5
        
        # Count matching proposition types
        p_types = set([p[0] for p in p_props])
        a_types = set([p[0] for p in a_props])
        
        overlap = len(p_types & a_types)
        return overlap / max(len(p_types), 1)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        if max(c1, c2) == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)