import numpy as np
from typing import Any, Dict, List, Tuple

class ReasoningTool:
    """
    Renormalized Mechanism-Driven Property-Based Scoring with Dynamics Tracking.
    
    Extracts logical propositions, builds hierarchical clause trees via renormalization,
    generates property-based test worlds, scores candidates via VCG mechanism,
    and tracks state trajectory stability for confidence estimation.
    """
    
    def __init__(self):
        self.N_WORLDS = 50  # Number of test worlds
        self.LAMBDA_PENALTY = 2.0  # Contradiction penalty
        self.rng = np.random.RandomState(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by RMPBS score."""
        Q_tree = self._parse_and_renormalize(prompt)
        worlds = self._generate_worlds(Q_tree)
        
        results = []
        for cand in candidates:
            A_tree = self._parse_and_renormalize(cand)
            score, reasoning = self._mechanism_score(A_tree, worlds, Q_tree)
            
            # Dynamics: trajectory stability under premise reordering
            stability = self._trajectory_stability(A_tree, worlds)
            final_score = 0.6 * score + 0.4 * stability
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        Q_tree = self._parse_and_renormalize(prompt)
        A_tree = self._parse_and_renormalize(answer)
        worlds = self._generate_worlds(Q_tree)
        
        score, _ = self._mechanism_score(A_tree, worlds, Q_tree)
        stability = self._trajectory_stability(A_tree, worlds)
        
        # Confidence based on score, stability, and question clarity
        conf = min(0.9, (0.4 * score + 0.4 * stability + 0.2 * meta_conf))
        return max(0.0, min(1.0, conf))
    
    def _parse_and_renormalize(self, text: str) -> List[Tuple[str, Any]]:
        """Extract atomic propositions and build hierarchical clause tree."""
        text = text.lower()
        clauses = []
        
        # Numeric comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|!=)\s*(\d+\.?\d*)', text):
            clauses.append(('numeric_comp', (float(m.group(1)), m.group(2), float(m.group(3)))))
        
        # Negations
        if re.search(r'\b(not|no|never|neither)\b', text):
            clauses.append(('negation', None))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            clauses.append(('conditional', (m.group(1).strip(), m.group(2).strip())))
        
        # Causals
        for m in re.finditer(r'(.+?)\s+(because|since|leads to)\s+(.+?)(?:\.|$)', text):
            clauses.append(('causal', (m.group(1).strip(), m.group(3).strip())))
        
        # Ordering
        for keyword in ['before', 'after', 'first', 'last']:
            if keyword in text:
                clauses.append(('ordering', keyword))
        
        # Comparatives
        for keyword in ['more', 'less', 'most', 'least', 'better', 'worse']:
            if keyword in text:
                clauses.append(('comparative', keyword))
        
        # Renormalization: merge adjacent clauses (simple version)
        return self._coarse_grain(clauses)
    
    def _coarse_grain(self, clauses: List) -> List:
        """Merge adjacent clauses sharing structure."""
        if len(clauses) <= 1:
            return clauses
        
        merged = []
        i = 0
        while i < len(clauses):
            if i < len(clauses) - 1 and clauses[i][0] == clauses[i+1][0]:
                merged.append(('merged', [clauses[i], clauses[i+1]]))
                i += 2
            else:
                merged.append(clauses[i])
                i += 1
        return merged
    
    def _generate_worlds(self, tree: List) -> np.ndarray:
        """Generate N random worlds satisfying question constraints."""
        worlds = []
        for _ in range(self.N_WORLDS):
            world = self.rng.rand(10)  # 10-dim world state
            if self._evaluate_tree(tree, world):
                worlds.append(world)
        
        if not worlds:
            worlds = [self.rng.rand(10) for _ in range(self.N_WORLDS)]
        
        return np.array(worlds[:self.N_WORLDS])
    
    def _evaluate_tree(self, tree: List, world: np.ndarray) -> bool:
        """Check if tree is satisfied in world."""
        if not tree:
            return True
        
        for clause_type, args in tree:
            if clause_type == 'numeric_comp':
                v1, op, v2 = args
                idx1, idx2 = int(v1 * 10) % 10, int(v2 * 10) % 10
                if op == '>': return world[idx1] > world[idx2]
                elif op == '<': return world[idx1] < world[idx2]
                elif op == '>=': return world[idx1] >= world[idx2]
                elif op == '<=': return world[idx1] <= world[idx2]
                elif op == '=': return abs(world[idx1] - world[idx2]) < 0.1
        return True
    
    def _mechanism_score(self, A_tree: List, worlds: np.ndarray, Q_tree: List) -> Tuple[float, str]:
        """VCG-style scoring with payoffs and externality correction."""
        N = len(worlds)
        payoffs = np.zeros(N)
        
        for i, world in enumerate(worlds):
            if self._evaluate_tree(A_tree, world):
                payoffs[i] = 1.0
            elif self._contradicts(A_tree, Q_tree, world):
                payoffs[i] = -self.LAMBDA_PENALTY
        
        # VCG correction: subtract externality (variance)
        externality = np.var(payoffs) if len(payoffs) > 1 else 0
        score = np.mean(payoffs) - 0.1 * externality
        
        # NCD component (max 15%)
        ncd_score = self._ncd_score(A_tree, Q_tree)
        final = 0.85 * score + 0.15 * ncd_score
        
        reasoning = f"Payoff={np.mean(payoffs):.2f}, Externality={externality:.2f}, NCD={ncd_score:.2f}"
        return max(0, min(1, (final + 1) / 2)), reasoning
    
    def _contradicts(self, A_tree: List, Q_tree: List, world: np.ndarray) -> bool:
        """Check if answer contradicts question in world."""
        a_sat = self._evaluate_tree(A_tree, world)
        q_sat = self._evaluate_tree(Q_tree, world)
        
        # Simple contradiction: A has negation but Q doesn't
        a_neg = any(t == 'negation' for t, _ in A_tree)
        q_neg = any(t == 'negation' for t, _ in Q_tree)
        return a_neg != q_neg
    
    def _trajectory_stability(self, A_tree: List, worlds: np.ndarray) -> float:
        """Measure state trajectory stability under reordering."""
        if len(A_tree) < 2:
            return 0.5
        
        # Simulate state evolution with different clause orderings
        trajectories = []
        perms = list(permutations(range(min(len(A_tree), 4))))[:10]
        
        for perm in perms:
            state = np.zeros(len(worlds))
            reordered = [A_tree[i] for i in perm if i < len(A_tree)]
            
            for clause in reordered:
                for j, world in enumerate(worlds):
                    if self._evaluate_tree([clause], world):
                        state[j] += 1
            
            trajectories.append(state)
        
        if not trajectories:
            return 0.5
        
        # Stability = 1 - variance across trajectories (Lyapunov-style)
        traj_array = np.array(trajectories)
        stability = 1.0 / (1.0 + np.mean(np.var(traj_array, axis=0)))
        return stability
    
    def _ncd_score(self, A_tree: List, Q_tree: List) -> float:
        """Normalized Compression Distance (max 15% of score)."""
        a_str = str(A_tree)
        q_str = str(Q_tree)
        
        ca = len(zlib.compress(a_str.encode()))
        cq = len(zlib.compress(q_str.encode()))
        caq = len(zlib.compress((a_str + q_str).encode()))
        
        ncd = (caq - min(ca, cq)) / max(ca, cq) if max(ca, cq) > 0 else 1.0
        return max(0, 1 - ncd)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity/unanswerability in prompt."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+who\?', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite)\b', prompt_lower) and not re.search(r'\b(metric|measure|criterion)\b', prompt_lower):
            return 0.3
        
        # Insufficient information
        if re.search(r'\bhow (many|much)\b', prompt_lower) and len(re.findall(r'\d+', prompt)) < 2:
            return 0.25
        
        return 0.8