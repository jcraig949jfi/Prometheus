from typing import Dict, List, Tuple

class ReasoningTool:
    def __init__(self):
        self.predicates = ['is', 'not', 'greater', 'less', 'if_then', 'cause', 'before', 'after']
        
    def _parse_graph(self, text: str) -> Tuple[List[str], Dict[str, np.ndarray], Dict]:
        """Parse text into typed directed graph."""
        text = text.lower()
        nodes = []
        node_idx = {}
        triples = []
        numbers = {}
        
        # Extract entities (simple noun phrases)
        entities = re.findall(r'\b([a-z]+(?:\s+[a-z]+)?)\b', text)
        for ent in entities[:20]:  # Limit nodes
            if ent not in node_idx and len(ent) > 2:
                node_idx[ent] = len(nodes)
                nodes.append(ent)
        
        if not nodes:
            nodes = ['empty']
            node_idx['empty'] = 0
        
        n = len(nodes)
        adj = {p: np.zeros((n, n)) for p in self.predicates}
        
        # Extract numbers
        for match in re.finditer(r'(\b[a-z]+\b)\s+(?:is\s+)?(\d+\.?\d*)', text):
            entity, num = match.groups()
            if entity in node_idx:
                numbers[entity] = float(num)
        
        # Pattern: negation
        for match in re.finditer(r'(?:not|no|never)\s+(\w+)', text):
            subj = match.group(1)
            if subj in node_idx:
                adj['not'][node_idx[subj], node_idx[subj]] = 1
        
        # Pattern: comparatives
        for match in re.finditer(r'(\w+)\s+(?:is\s+)?(?:greater|more|larger|higher)\s+than\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx:
                adj['greater'][node_idx[s1], node_idx[s2]] = 1
        
        for match in re.finditer(r'(\w+)\s+(?:is\s+)?(?:less|fewer|smaller|lower)\s+than\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx:
                adj['less'][node_idx[s1], node_idx[s2]] = 1
        
        # Pattern: conditionals
        for match in re.finditer(r'if\s+(\w+).*then\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx:
                adj['if_then'][node_idx[s1], node_idx[s2]] = 1
        
        # Pattern: causal
        for match in re.finditer(r'(\w+)\s+(?:cause|lead|result|produce)\w*\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx:
                adj['cause'][node_idx[s1], node_idx[s2]] = 1
        
        # Pattern: temporal
        for match in re.finditer(r'(\w+)\s+before\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx:
                adj['before'][node_idx[s1], node_idx[s2]] = 1
        
        # Pattern: copula
        for match in re.finditer(r'(\w+)\s+is\s+(\w+)', text):
            s1, s2 = match.groups()
            if s1 in node_idx and s2 in node_idx and s1 != s2:
                adj['is'][node_idx[s1], node_idx[s2]] = 1
        
        return nodes, adj, numbers
    
    def _renormalize(self, adj: Dict[str, np.ndarray], iterations: int = 2) -> np.ndarray:
        """Weisfeiler-Lehman iterative feature propagation (RG coarse-graining)."""
        n = list(adj.values())[0].shape[0]
        F = np.eye(n) + 0.1 * np.random.rand(n, n)  # Init with identity + noise
        
        for _ in range(iterations):
            F_new = np.zeros_like(F)
            for p, A in adj.items():
                F_new += A @ F
            F_new += F  # Self-connection
            # Normalize
            norms = np.linalg.norm(F_new, axis=1, keepdims=True)
            F = F_new / (norms + 1e-8)
        
        return F
    
    def _functorial_similarity(self, F_ref: np.ndarray, F_cand: np.ndarray) -> float:
        """Compute analogical score via Hungarian algorithm."""
        S = F_ref @ F_cand.T
        row_ind, col_ind = linear_sum_assignment(-S)
        score = S[row_ind, col_ind].sum() / max(len(F_ref), len(F_cand))
        return max(0.0, min(1.0, score))
    
    def _dynamics_score(self, prompt: str, candidate: str) -> float:
        """Track state evolution: stability of reasoning trajectory."""
        # Split into sentences (premises)
        sentences = re.split(r'[.!?]+', prompt + ' ' + candidate)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if len(sentences) < 2:
            return 0.5
        
        # Build state vector as we process each premise
        states = []
        for i in range(1, len(sentences) + 1):
            partial = ' '.join(sentences[:i])
            nodes, adj, _ = self._parse_graph(partial)
            F = self._renormalize(adj)
            # State = flattened feature vector
            state = F.flatten()[:50]  # Limit dimensionality
            if len(state) < 50:
                state = np.pad(state, (0, 50 - len(state)))
            states.append(state)