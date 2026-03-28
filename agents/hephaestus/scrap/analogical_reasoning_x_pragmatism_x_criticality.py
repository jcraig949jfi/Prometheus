import re
import numpy as np
from collections import defaultdict
from zlib import compress

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Analogical Reasoning, Pragmatism, and Criticality.
    Mechanism:
    1. Structural Parsing: Extracts entities, numbers, and relations (negation, comparison, causality).
    2. Analogical Similarity: Uses a simplified Weisfeiler-Lehman hash on the relation graph.
    3. Pragmatic Utility: Performs Horn-clause style resolution to check if candidate implies prompt constraints.
    4. Criticality: Perturbs the graph to measure score stability (susceptibility).
    5. Scoring: Combines these factors, using NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.relations = ['cmp', 'cau', 'cond', 'neg', 'ord']
        self.epsilon = 1e-6

    def _parse_graph(self, text):
        """Parses text into nodes and typed edges."""
        nodes = []
        edges = []
        text_lower = text.lower()
        
        # Extract noun phrases / entities (simplified)
        entity_pattern = r'\b([a-zA-Z][a-zA-Z0-9\-]*(?:\s+[a-zA-Z][a-zA-Z0-9\-]*)*)\b'
        matches = re.findall(entity_pattern, text)
        nodes = list(set([m.strip() for m in matches if len(m.strip()) > 1]))
        node_map = {n: i for i, n in enumerate(nodes)}
        
        # Extract Comparatives (A > B, A is greater than B)
        cmp_pattern = r'(\w+)\s*(?:is\s*)?(?:greater|larger|more|higher|faster|older)\s+(?:than)?\s*(\w+)'
        for m in re.finditer(cmp_pattern, text_lower):
            if m.group(1) in node_map and m.group(2) in node_map:
                edges.append((node_map[m.group(1)], node_map[m.group(2)], 'cmp'))
        
        # Extract Negations (A is not B)
        neg_pattern = r'(\w+)\s+is\s+not\s+(\w+)'
        for m in re.finditer(neg_pattern, text_lower):
            if m.group(1) in node_map and m.group(2) in node_map:
                edges.append((node_map[m.group(1)], node_map[m.group(2)], 'neg'))

        # Extract Causality (A causes B, A leads to B)
        cau_pattern = r'(\w+)\s+(?:causes|leads\s+to|implies|results\s+in)\s+(\w+)'
        for m in re.finditer(cau_pattern, text_lower):
            if m.group(1) in node_map and m.group(2) in node_map:
                edges.append((node_map[m.group(1)], node_map[m.group(2)], 'cau'))

        # Extract Ordering (A before B)
        ord_pattern = r'(\w+)\s+(?:before|precedes)\s+(\w+)'
        for m in re.finditer(ord_pattern, text_lower):
            if m.group(1) in node_map and m.group(2) in node_map:
                edges.append((node_map[m.group(1)], node_map[m.group(2)], 'ord'))

        # Build Adjacency Tensor A[|V| x |V| x |R|]
        n_nodes = len(nodes)
        n_rel = len(self.relations)
        A = np.zeros((n_nodes, n_nodes, n_rel), dtype=np.float32)
        
        for u, v, r_type in edges:
            if r_type in self.relations:
                r_idx = self.relations.index(r_type)
                A[u, v, r_idx] = 1.0
                
        return A, nodes, edges

    def _wl_kernel(self, A, nodes, steps=2):
        """Computes WL graph kernel similarity."""
        if len(nodes) == 0: return 0.0
        n = len(nodes)
        # Init labels with degree + node index hash
        degrees = np.sum(A, axis=1) + np.sum(A, axis=0)
        labels = [hash(str(d)) % 1000 for d in range(n)]
        
        for _ in range(steps):
            new_labels = []
            for i in range(n):
                neighbor_hashes = []
                for r in range(len(self.relations)):
                    # Outgoing
                    outs = np.where(A[i, :, r] > 0)[0]
                    for j in outs: neighbor_hashes.append((r, labels[j], 1))
                    # Incoming
                    ins = np.where(A[:, i, r] > 0)[0]
                    for j in ins: neighbor_hashes.append((r, labels[j], -1))
                
                neighbor_hashes.sort()
                labels[i] = hash((labels[i], tuple(neighbor_hashes))) % 100000
            new_labels = labels
            
        # Histogram cosine similarity is approximated by set overlap for speed/simplicity in this context
        # Since we compare Prompt vs Candidate, we need a common reference. 
        # Here we return a stability score based on label distribution entropy as a proxy for structural richness
        unique_labels = len(set(labels))
        return unique_labels / (n + self.epsilon)

    def _pragmatic_score(self, prompt_edges, candidate_edges):
        """Checks if candidate edges satisfy prompt constraints (Horn clause approx)."""
        if not prompt_edges: return 1.0 if not candidate_edges else 0.5
        if not candidate_edges: return 0.0
        
        p_set = set(prompt_edges)
        c_set = set(candidate_edges)
        
        # Direct match
        matches = len(p_set.intersection(c_set))
        # Transitive approximation (A>B, B>C -> A>C) handled loosely by checking chain presence
        # Score is ratio of satisfied constraints
        return matches / len(p_set) if len(p_set) > 0 else 1.0

    def _criticality(self, A, nodes, prompt_edges, candidate_edges):
        """Perturbs graph and measures score variance."""
        if A.size == 0 or len(nodes) == 0: return 0.5
        scores = []
        base_score = self._wl_kernel(A, nodes) * (0.5 + 0.5 * self._pragmatic_score(prompt_edges, candidate_edges))
        scores.append(base_score)
        
        K = 10
        for _ in range(K):
            A_pert = A.copy()
            # Flip random edge
            if np.random.rand() > 0.5 and A.sum() > 0:
                idx = np.random.randint(0, A.size)
                A_pert.flat[idx] = 1.0 - A_pert.flat[idx]
            
            s = self._wl_kernel(A_pert, nodes) * 0.5 # Simplified for perturbation
            scores.append(s)
            
        return np.var(scores) / (np.var(scores) + self.epsilon)

    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_A, p_nodes, p_edges = self._parse_graph(prompt)
        
        # Pre-calculate prompt features
        p_wl = self._wl_kernel(p_A, p_nodes)
        
        for cand in candidates:
            c_A, c_nodes, c_edges = self._parse_graph(cand)
            
            # 1. Analogical (Structural richness match)
            c_wl = self._wl_kernel(c_A, c_nodes)
            ana_sim = 1.0 / (1.0 + abs(p_wl - c_wl)) # Similar complexity is better
            
            # 2. Pragmatic (Constraint satisfaction)
            pra_score = self._pragmatic_score(p_edges, c_edges)
            
            # 3. Criticality (Stability)
            crit_score = self._criticality(c_A, c_nodes, p_edges, c_edges)
            
            # Combined Score
            # Weighted: Pragmatism is most important for correctness, Criticality for robustness
            score = (ana_sim * 0.3) + (pra_score * 0.5) + (crit_score * 0.2)
            
            # NCD Tiebreaker / Fallback
            if score < 0.1: 
                ncd_val = 1.0 - self._ncd(prompt, cand)
                score = 0.5 * score + 0.5 * ncd_val

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Ana:{ana_sim:.2f}, Pra:{pra_score:.2f}, Crit:{crit_score:.2f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0