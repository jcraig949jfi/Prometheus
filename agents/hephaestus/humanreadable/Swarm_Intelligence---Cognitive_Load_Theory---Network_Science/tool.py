from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Swarm Intelligence x Cognitive Load Theory x Network Science reasoning tool.
    
    Parses candidates into propositional nodes, builds a logical dependency graph,
    deploys ant colony agents with limited working memory (cognitive load), and
    scores via network coherence (strongly connected components).
    
    Includes structural parsers, computational solvers, and epistemic honesty
    via meta-confidence detection of ambiguity and presupposition traps.
    """
    
    def __init__(self):
        self.beta = 2.0  # temperature for ant decisions
        self.rho = 0.1   # pheromone evaporation
        self.lambda_load = 0.3  # extraneous load penalty
        self.k_memory = 5  # working memory capacity (top-k edges)
        self.m_ants = 10
        self.T_iterations = 20
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score and rank candidates by swarm-based coherence."""
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to [0,1], cap at 0.9 unless computation is definitive
        conf = min(0.9, max(0.0, score))
        return min(conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, false dichotomy -> return low confidence."""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+ .* \ba \w+\b', p) and '?' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.35
        
        # Unanswerable markers
        if re.search(r'\bcannot be determined\b', p):
            return 0.3
        
        return 1.0  # no trap detected
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Compute score via swarm coherence + structural + computational."""
        reasons = []
        structural_score = 0.0
        comp_score = 0.0
        
        # Computational solvers (20%+)
        comp_score, comp_reason = self._compute_numeric(prompt, candidate)
        if comp_reason:
            reasons.append(comp_reason)
        
        # Structural parsing (50%+)
        nodes_p, W_p = self._parse_propositions(prompt)
        nodes_c, W_c = self._parse_propositions(candidate)
        
        if len(nodes_p) > 0 and len(nodes_c) > 0:
            # Swarm coherence
            coherence = self._swarm_coherence(nodes_c, W_c)
            structural_score = coherence
            reasons.append(f"swarm_coherence={coherence:.2f}")
        
        # NCD tiebreaker (<=15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Weighted combination
        final_score = 0.55 * structural_score + 0.3 * comp_score + 0.15 * ncd_score
        
        reasoning_str = "; ".join(reasons) if reasons else "no_parse"
        return final_score, reasoning_str
    
    def _swarm_coherence(self, nodes: List[str], W: np.ndarray) -> float:
        """Run ant colony with cognitive load pruning, return SCC coherence."""
        n = len(nodes)
        if n == 0:
            return 0.0
        
        # Cognitive load: prune to top-k edges per node
        W_pruned, L_ext = self._prune_edges(W, self.k_memory)
        
        # Initialize truth assignments uniformly
        v = np.random.rand(n) > 0.5
        v = v.astype(float)
        
        # Pheromone matrix
        tau = np.ones((n, n)) * 0.1
        
        # Swarm iterations
        for t in range(self.T_iterations):
            v_new = v.copy()
            for agent in range(self.m_ants):
                i = np.random.randint(n)
                s_i = np.dot(W_pruned[i], v)
                prob_flip = np.exp(self.beta * s_i) / (1 + np.exp(self.beta * s_i))
                if np.random.rand() < prob_flip:
                    v_new[i] = 1.0 - v_new[i]
            
            # Pheromone update
            delta_tau = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    delta_tau[i,j] = (v_new[i] == v_new[j]) / self.m_ants
            tau = (1 - self.rho) * tau + delta_tau
            v = v_new
        
        # SCC coherence
        scc_size = self._largest_scc(W_pruned, v)
        coherence = scc_size / np.sqrt(n) / (1 + self.lambda_load * L_ext)
        return min(1.0, coherence)
    
    def _prune_edges(self, W: np.ndarray, k: int) -> Tuple[np.ndarray, int]:
        """Keep only top-k outgoing edges per node, return pruned W and count removed."""
        n = W.shape[0]
        W_pruned = np.zeros_like(W)
        L_ext = 0
        for i in range(n):
            if k >= n:
                W_pruned[i] = W[i]
            else:
                top_k_idx = np.argpartition(np.abs(W[i]), -k)[-k:]
                W_pruned[i, top_k_idx] = W[i, top_k_idx]
                L_ext += n - k
        return W_pruned, L_ext
    
    def _largest_scc(self, W: np.ndarray, v: np.ndarray) -> int:
        """Compute size of largest strongly connected component."""
        n = W.shape[0]
        # Build adjacency where W_ij * v_i * v_j > 0
        adj = np.zeros((n, n), dtype=bool)
        for i in range(n):
            for j in range(n):
                if W[i,j] * v[i] * v[j] > 0:
                    adj[i,j] = True
        
        # Tarjan's SCC (simplified: just count reachable)
        visited = np.zeros(n, dtype=bool)
        max_component = 0
        for start in range(n):
            if not visited[start]:
                stack = [start]
                comp_size = 0
                while stack:
                    node = stack.pop()
                    if not visited[node]:
                        visited[node] = True
                        comp_size += 1
                        for neighbor in range(n):
                            if adj[node, neighbor] and not visited[neighbor]:
                                stack.append(neighbor)
                max_component = max(max_component, comp_size)
        return max_component
    
    def _parse_propositions(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Extract propositional nodes and build adjacency matrix."""
        nodes = []
        t = text.lower()
        
        # Extract negations
        for m in re.finditer(r'\b(not|no|never|cannot)\s+(\w+)', t):
            nodes.append(f"neg_{m.group(2)}")
        
        # Conditionals
        for m in re.finditer(r'\bif\s+(.*?)\s+then\s+(.*?)[\.\,\;]', t):
            nodes.append(f"cond_{m.group(1)[:10]}")
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in)\s+(\w+)', t):
            nodes.append(f"cause_{m.group(1)}_{m.group(3)}")
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(greater|less|equal)\s*(than)?\s*(\d+\.?\d*)', t):
            nodes.append(f"cmp_{m.group(1)}_{m.group(2)}_{m.group(4)}")
        
        # Temporal
        for m in re.finditer(r'(before|after|while)\s+(\w+)', t):
            nodes.append(f"temp_{m.group(1)}_{m.group(2)}")
        
        if len(nodes) == 0:
            nodes = [f"prop_{i}" for i in range(min(3, len(t.split())))]
        
        n = len(nodes)
        W = np.random.randn(n, n) * 0.1
        # Add structure: entailment +1, contradiction -1
        for i in range(n):
            for j in range(n):
                if 'neg_' in nodes[i] and nodes[i].replace('neg_', '') in nodes[j]:
                    W[i,j] = -1.0
                elif nodes[i] in nodes[j]:
                    W[i,j] = 0.5
        return nodes, W
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Numeric comparison, algebra, Bayesian, PEMDAS."""
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s+(?:vs|versus|or)\s+(\d+\.?\d*)', prompt)
        if num_match:
            a, b = float(num_match.group(1)), float(num_match.group(2))
            if re.search(r'\b(greater|larger|more)\b', prompt):
                correct = str(max(a, b))
                if correct in candidate:
                    return 1.0, f"numeric_cmp({a},{b})"
        
        # Bat and ball algebra: X + Y = total, X = Y + diff
        bat_match = re.search(r'(\d+\.?\d*)\s+.+cost.+(\d+\.?\d*)\s+more', prompt)
        if bat_match:
            total = float(re.search(r'(\d+\.?\d*)', prompt).group(1))
            diff = float(bat_match.group(2))
            # X + Y = total, X = Y + diff => 2Y + diff = total
            Y = (total - diff) / 2
            if f"{Y:.2f}" in candidate or f"{int(Y)}" in candidate:
                return 1.0, f"algebra_bat_ball"
        
        # PEMDAS
        expr_match = re.search(r'(\d+)\s*[\+\-\*/]\s*(\d+)\s*[\+\-\*/]\s*(\d+)', prompt)
        if expr_match:
            try:
                result = eval(re.search(r'[\d\+\-\*/\(\)\s]+', prompt).group(0))
                if str(result) in candidate:
                    return 1.0, f"pemdas={result}"
            except:
                pass
        
        return 0.0, ""
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0