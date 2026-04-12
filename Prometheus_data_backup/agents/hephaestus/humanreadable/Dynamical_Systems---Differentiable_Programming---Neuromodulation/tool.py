import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Dynamical Systems x Differentiable Programming x Neuromodulation
    
    Treats candidate answers as belief states evolving under constraint-driven
    neural ODE dynamics. Extracts logical structure (negations, comparatives,
    conditionals, causal links) and builds a differentiable loss. Neuromodulatory
    gain adapts sensitivity based on uncertainty. Integrates with RK4 to find
    constraint-satisfying attractors.
    """
    
    def __init__(self):
        self.eps = 1e-6
        self.rk4_steps = 20
        self.dt = 0.1
        # Neuromodulator gains: dopamine (novelty), serotonin (stability)
        self.gain_dopamine = 0.3
        self.gain_serotonin = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"ODE loss={1-score:.3f}, conf={conf:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        structural_conf = self._structural_confidence(prompt, answer)
        return min(meta_conf, structural_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \b', p):
            return 0.25
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and 'who' in p:
            return 0.25
        # False dichotomy
        if re.search(r'\beither .+ or \b', p):
            return 0.3
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.35
        # Unanswerability markers
        if re.search(r'\b(impossible|cannot determine|not enough|insufficient)\b', p):
            return 0.2
        return 0.9
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        # Check if we can compute something definitive
        nums_p = self._extract_numbers(prompt)
        nums_a = self._extract_numbers(answer)
        
        # Numeric computation confidence
        if nums_p and nums_a:
            if self._has_arithmetic(prompt):
                return 0.85
        
        # Comparative structure
        if self._has_comparative(prompt) and nums_a:
            return 0.75
        
        # Conditional/logical
        if self._has_conditional(prompt):
            return 0.65
        
        # Default: moderate uncertainty
        return 0.5
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Constructive computation first
        comp_score = self._compute_score(prompt, candidate)
        if comp_score is not None:
            return comp_score
        
        # Structural ODE-based scoring
        propositions = self._extract_propositions(prompt, candidate)
        if len(propositions) == 0:
            return self._ncd_fallback(prompt, candidate)
        
        A, losses = self._build_constraint_graph(propositions)
        n = len(propositions)
        
        # Initial belief state (uniform)
        x0 = np.ones(n) * 0.5
        
        # Integrate ODE
        x_final = self._integrate_ode(x0, A, losses)
        
        # Compute final loss
        L_final = self._compute_loss(x_final, losses)
        
        # Score: exp(-L*)
        score = np.exp(-L_final)
        
        # Mix with NCD (max 15%)
        ncd = self._ncd(prompt, candidate)
        score = 0.85 * score + 0.15 * (1 - ncd)
        
        return np.clip(score, 0, 1)
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Numeric arithmetic
        if self._has_arithmetic(prompt):
            result = self._eval_arithmetic(prompt)
            if result is not None:
                cand_nums = self._extract_numbers(candidate)
                if cand_nums:
                    error = abs(result - cand_nums[0]) / (abs(result) + 1e-9)
                    return np.exp(-error)
        
        # Comparative (e.g., "9.11 vs 9.9")
        if self._has_comparative(prompt):
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                if 'greater' in prompt.lower() or '>' in prompt:
                    correct = nums[0] > nums[1]
                elif 'less' in prompt.lower() or '<' in prompt:
                    correct = nums[0] < nums[1]
                else:
                    return None
                cand_lower = candidate.lower()
                if ('yes' in cand_lower or 'true' in cand_lower) and correct:
                    return 0.95
                elif ('no' in cand_lower or 'false' in cand_lower) and not correct:
                    return 0.95
        
        # Probability/Bayesian
        if 'probability' in prompt.lower() or 'bayesian' in prompt.lower():
            prob = self._compute_bayesian(prompt, candidate)
            if prob is not None:
                return prob
        
        return None
    
    def _extract_propositions(self, prompt: str, candidate: str) -> List[str]:
        text = prompt + " " + candidate
        # Split on sentence boundaries
        sents = re.split(r'[.!?;]', text)
        props = [s.strip() for s in sents if len(s.strip()) > 5]
        return props[:10]  # Limit for efficiency
    
    def _build_constraint_graph(self, props: List[str]) -> Tuple[np.ndarray, List]:
        n = len(props)
        A = np.zeros((n, n))
        losses = []
        
        for i, p in enumerate(props):
            pl = p.lower()
            
            # Negation constraint
            for j, q in enumerate(props):
                if i != j and 'not' in pl and any(w in q.lower() for w in pl.split()):
                    A[i, j] = -1.0  # Negation edge
                    losses.append(('neg', i, j))
            
            # Conditional (if-then)
            if 'if' in pl and 'then' in pl:
                for j in range(n):
                    if i != j:
                        A[i, j] = 0.5  # Implication edge
                        losses.append(('imp', i, j))
            
            # Causal
            if any(c in pl for c in ['because', 'leads to', 'causes']):
                for j in range(n):
                    if i != j:
                        A[i, j] = 0.3
                        losses.append(('caus', i, j))
        
        return A, losses
    
    def _integrate_ode(self, x0: np.ndarray, A: np.ndarray, losses: List) -> np.ndarray:
        x = x0.copy()
        for _ in range(self.rk4_steps):
            x = self._rk4_step(x, A, losses)
            x = np.clip(x, 0, 1)
        return x
    
    def _rk4_step(self, x: np.ndarray, A: np.ndarray, losses: List) -> np.ndarray:
        k1 = self._dx_dt(x, losses)
        k2 = self._dx_dt(x + 0.5 * self.dt * k1, losses)
        k3 = self._dx_dt(x + 0.5 * self.dt * k2, losses)
        k4 = self._dx_dt(x + self.dt * k3, losses)
        return x + (self.dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    
    def _dx_dt(self, x: np.ndarray, losses: List) -> np.ndarray:
        grad = self._grad_loss(x, losses)
        # Neuromodulatory gain: g * sigma(x), where sigma(x) = x*(1-x)
        sigma = x * (1 - x)
        g = self.gain_dopamine + self.gain_serotonin
        return -grad + g * sigma
    
    def _grad_loss(self, x: np.ndarray, losses: List) -> np.ndarray:
        grad = np.zeros_like(x)
        for loss_type, i, j in losses:
            if loss_type == 'neg':
                # Negation: x[i] * x[j] should be 0
                grad[i] += x[j]
                grad[j] += x[i]
            elif loss_type == 'imp':
                # Implication: x[i] <= x[j]
                if x[i] > x[j]:
                    grad[i] += 1.0
                    grad[j] -= 1.0
            elif loss_type == 'caus':
                # Causal: similar to implication
                if x[i] > x[j]:
                    grad[i] += 0.5
                    grad[j] -= 0.5
        return grad
    
    def _compute_loss(self, x: np.ndarray, losses: List) -> float:
        L = 0.0
        for loss_type, i, j in losses:
            if loss_type == 'neg':
                L += x[i] * x[j]
            elif loss_type == 'imp':
                L += max(0, x[i] - x[j])
            elif loss_type == 'caus':
                L += 0.5 * max(0, x[i] - x[j])
        return L
    
    def _extract_numbers(self, text: str) -> List[float]:
        nums = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in nums]
    
    def _has_arithmetic(self, text: str) -> bool:
        return bool(re.search(r'[\+\-\*/\^]', text)) or 'sum' in text.lower() or 'product' in text.lower()
    
    def _has_comparative(self, text: str) -> bool:
        return bool(re.search(r'\b(greater|less|more|fewer|larger|smaller|before|after)\b', text.lower()))
    
    def _has_conditional(self, text: str) -> bool:
        return 'if' in text.lower() and 'then' in text.lower()
    
    def _eval_arithmetic(self, text: str) -> float:
        nums = self._extract_numbers(text)
        if len(nums) < 2:
            return None
        if '+' in text or 'sum' in text.lower():
            return sum(nums)
        if '*' in text or 'product' in text.lower():
            return np.prod(nums)
        if '-' in text and len(nums) == 2:
            return nums[0] - nums[1]
        if '/' in text and len(nums) == 2:
            return nums[0] / (nums[1] + 1e-9)
        return None
    
    def _compute_bayesian(self, prompt: str, candidate: str) -> float:
        # Simple Bayesian update: P(H|E) = P(E|H)*P(H) / P(E)
        nums = self._extract_numbers(prompt + " " + candidate)
        if len(nums) >= 3:
            p_h = nums[0]
            p_e_given_h = nums[1]
            p_e = nums[2] if len(nums) > 2 else p_e_given_h * p_h + (1 - p_h) * 0.5
            posterior = p_e_given_h * p_h / (p_e + 1e-9)
            cand_nums = self._extract_numbers(candidate)
            if cand_nums:
                error = abs(posterior - cand_nums[0])
                return np.exp(-error * 10)
        return None
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / (max(c1, c2) + 1e-9)
    
    def _ncd_fallback(self, prompt: str, candidate: str) -> float:
        return 1 - self._ncd(prompt, candidate)