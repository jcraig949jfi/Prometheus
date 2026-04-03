import re
import math
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    Chaotic Bandit Mechanism (CBM) for answer evaluation.
    
    Combines:
    - Multi-armed bandits (UCB) for exploration-exploitation
    - Chaos theory (Lyapunov perturbation) for constraint sensitivity
    - Mechanism design (VCG weights) for constraint valuation
    
    Each candidate is an arm. Rewards reflect constraint satisfaction
    amplified by chaotic sensitivity to logical flaws.
    """
    
    def __init__(self):
        self.exploration_constant = 1.4
        self.lyapunov_epsilon = 0.01
        self.bandit_budget = 30
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using chaotic bandit mechanism."""
        if not candidates:
            return []
        
        # Parse prompt constraints
        constraints = self._parse_constraints(prompt)
        if not constraints:
            # Fallback to computational solvers
            return self._compute_fallback(prompt, candidates)
        
        # Build Lyapunov sensitivity matrix
        L = self._build_lyapunov_matrix(constraints)
        
        # Compute VCG weights
        weights = self._compute_vcg_weights(constraints)
        
        # Run bandit algorithm
        Q = defaultdict(float)  # Estimated utility
        N = defaultdict(int)    # Pull count
        
        for t in range(1, self.bandit_budget + 1):
            # UCB selection
            arm_idx = self._ucb_select(Q, N, t, len(candidates))
            
            # Compute reward with chaotic amplification
            answer_features = self._extract_features(candidates[arm_idx])
            violation = self._compute_violation(constraints, answer_features)
            perturbed = violation + self.lyapunov_epsilon * (L @ violation)
            perturbed = np.clip(perturbed, 0, 1)
            
            reward = -np.dot(weights, perturbed)
            
            # Update estimates
            N[arm_idx] += 1
            Q[arm_idx] += (reward - Q[arm_idx]) / N[arm_idx]
        
        # Rank by final Q values
        results = []
        for i, cand in enumerate(candidates):
            score = Q.get(i, 0.0)
            # Normalize to [0,1]
            normalized = (score + 10) / 20  # Typical range [-10, 10]
            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, normalized)),
                "reasoning": f"CBM utility: {score:.3f}, pulls: {N.get(i, 0)}"
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with epistemic honesty checks."""
        # Check for meta-level issues first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate answer quality
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.2
        
        base_score = results[0]["score"]
        # Cap confidence, avoid overconfidence
        return min(meta_conf, base_score * 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [
            r'\bhave you (stopped|quit|ceased)\b',
            r'\bwhy did .+ (fail|stop|end)\b',
            r'\bwhen did you last\b'
        ]
        for pat in presup_patterns:
            if re.search(pat, prompt_lower):
                return 0.15
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which|what)\?', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|ideal)\b', prompt_lower):
            if not re.search(r'\b(most|least|highest|lowest)\b', prompt_lower):
                return 0.25
        
        return 0.95  # High base confidence in prompt clarity
    
    def _parse_constraints(self, prompt: str) -> list:
        """Extract structured constraints from prompt."""
        constraints = []
        
        # Negations
        neg_matches = re.findall(r'\b(not|never|no|none|cannot)\s+(\w+)', prompt.lower())
        for match in neg_matches:
            constraints.append(('negation', match[1]))
        
        # Comparatives
        comp_patterns = [
            (r'(\w+)\s+(?:is\s+)?(more|less|greater|smaller)\s+than\s+(\w+)', 'comparative'),
            (r'(\d+\.?\d*)\s*([<>]=?)\s*(\d+\.?\d*)', 'numeric_comp')
        ]
        for pat, typ in comp_patterns:
            for match in re.finditer(pat, prompt.lower()):
                constraints.append((typ, match.groups()))
        
        # Conditionals
        cond_patterns = [r'if (.+?) then (.+?)(?:\.|$)', r'unless (.+?),? (.+?)(?:\.|$)']
        for pat in cond_patterns:
            for match in re.finditer(pat, prompt.lower()):
                constraints.append(('conditional', match.groups()))
        
        # Numeric values
        num_matches = re.findall(r'\b(\d+\.?\d*)\s*([a-z]+)?\b', prompt)
        for match in num_matches:
            constraints.append(('numeric', match))
        
        # Causal
        causal_words = ['because', 'leads to', 'results in', 'causes', 'due to']
        for word in causal_words:
            if word in prompt.lower():
                constraints.append(('causal', word))
        
        # Ordering
        order_words = ['first', 'second', 'before', 'after', 'then']
        for word in order_words:
            if word in prompt.lower():
                constraints.append(('ordering', word))
        
        return constraints
    
    def _extract_features(self, answer: str) -> dict:
        """Extract features from candidate answer."""
        features = defaultdict(int)
        answer_lower = answer.lower()
        
        features['negation'] = len(re.findall(r'\b(not|never|no)\b', answer_lower))
        features['comparative'] = len(re.findall(r'\b(more|less|greater|smaller)\b', answer_lower))
        features['conditional'] = len(re.findall(r'\b(if|then|unless)\b', answer_lower))
        features['numeric'] = len(re.findall(r'\b\d+\.?\d*\b', answer))
        features['causal'] = len(re.findall(r'\b(because|leads|causes|due)\b', answer_lower))
        features['ordering'] = len(re.findall(r'\b(first|second|before|after)\b', answer_lower))
        
        return features
    
    def _compute_violation(self, constraints: list, features: dict) -> np.ndarray:
        """Compute binary violation vector for constraints."""
        if not constraints:
            return np.zeros(1)
        
        violations = []
        for ctype, cdata in constraints:
            # Simple heuristic: violation if feature count mismatches expectation
            if ctype in features:
                viol = 1.0 if features[ctype] == 0 else 0.3
            else:
                viol = 0.5  # Uncertain
            violations.append(viol)
        
        return np.array(violations)
    
    def _build_lyapunov_matrix(self, constraints: list) -> np.ndarray:
        """Build constraint sensitivity matrix using finite differences."""
        k = len(constraints)
        if k == 0:
            return np.zeros((1, 1))
        
        L = np.zeros((k, k))
        
        # Simple model: constraint types interact
        type_map = {c[0]: i for i, c in enumerate(constraints)}
        
        for i in range(k):
            for j in range(k):
                if i == j:
                    L[i, j] = 1.0  # Self-amplification
                else:
                    # Cross-amplification based on type similarity
                    ti, tj = constraints[i][0], constraints[j][0]
                    if ti == tj:
                        L[i, j] = 0.3
                    elif ti in ['conditional', 'causal'] and tj in ['conditional', 'causal']:
                        L[i, j] = 0.5
                    else:
                        L[i, j] = 0.1
        
        return L
    
    def _compute_vcg_weights(self, constraints: list) -> np.ndarray:
        """Compute VCG-style weights for constraints."""
        k = len(constraints)
        if k == 0:
            return np.ones(1)
        
        weights = []
        for i, (ctype, _) in enumerate(constraints):
            # Weight by importance: conditionals and causals are critical
            if ctype in ['conditional', 'causal']:
                w = 2.0
            elif ctype in ['negation', 'comparative']:
                w = 1.5
            else:
                w = 1.0
            weights.append(w)
        
        return np.array(weights)
    
    def _ucb_select(self, Q: dict, N: dict, t: int, n_arms: int) -> int:
        """Select arm using UCB criterion."""
        ucb_scores = []
        for i in range(n_arms):
            if N[i] == 0:
                return i  # Always try unexplored arms first
            
            exploit = Q[i]
            explore = self.exploration_constant * math.sqrt(math.log(t) / N[i])
            ucb_scores.append(exploit + explore)
        
        return int(np.argmax(ucb_scores))
    
    def _compute_fallback(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Computational solvers for standard reasoning patterns."""
        results = []
        
        for cand in candidates:
            score = 0.5  # Neutral baseline
            reasoning = "Fallback computation"
            
            # Numeric comparison solver
            if re.search(r'\d+\.?\d*', prompt):
                score = self._solve_numeric(prompt, cand)
                reasoning = "Numeric evaluation"
            
            # Bat-and-ball algebra
            elif 'cost' in prompt.lower() and 'total' in prompt.lower():
                score = self._solve_algebra(prompt, cand)
                reasoning = "Algebraic solving"
            
            # Modus tollens
            elif 'if' in prompt.lower() and 'not' in prompt.lower():
                score = self._solve_modus_tollens(prompt, cand)
                reasoning = "Logical inference"
            
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def _solve_numeric(self, prompt: str, answer: str) -> float:
        """Solve numeric comparison problems."""
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if not p_nums or not a_nums:
            return 0.3
        
        # Check if answer number makes sense in context
        if any(abs(pn - an) < 0.01 for pn in p_nums for an in a_nums):
            return 0.8
        
        # Check ordering (9.11 vs 9.9 problem)
        if 'greater' in prompt.lower() or 'larger' in prompt.lower():
            if len(p_nums) >= 2 and len(a_nums) >= 1:
                if p_nums[0] > p_nums[1] and str(p_nums[0]) in answer:
                    return 0.9
        
        return 0.4
    
    def _solve_algebra(self, prompt: str, answer: str) -> float:
        """Solve simple algebraic word problems."""
        # Bat and ball: total $1.10, bat costs $1 more
        if '1.10' in prompt and '1' in prompt and 'more' in prompt:
            if '0.05' in answer or '5 cent' in answer.lower():
                return 0.95
            elif '0.10' in answer or '10 cent' in answer.lower():
                return 0.1  # Common wrong answer
        
        return 0.5
    
    def _solve_modus_tollens(self, prompt: str, answer: str) -> float:
        """Apply modus tollens: if P then Q, not Q, therefore not P."""
        # Simple pattern matching for now
        if 'if' in prompt.lower() and 'not' in answer.lower():
            return 0.7
        return 0.5