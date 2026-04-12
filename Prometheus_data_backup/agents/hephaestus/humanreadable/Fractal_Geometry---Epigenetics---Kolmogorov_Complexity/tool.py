from typing import Dict, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-Epigenetic-Kolmogorov reasoning tool combining:
    1. Graph-based logical structure with constraint propagation
    2. Kolmogorov complexity proxy via compression
    3. Fractal dimension of argument structure
    4. Computational solvers for numeric/logical problems
    """
    
    def __init__(self):
        self.weights = [0.4, 0.3, 0.3]  # C, E, F scores
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({"candidate": cand, "score": score * conf, "reasoning": f"score={score:.3f}, conf={conf:.3f}"})
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        comp_conf = self._computational_confidence(prompt, answer)
        return min(0.85, max(meta_conf, comp_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        if re.search(r'\b(have you stopped|did you stop|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        if re.search(r'\bevery .+ a \b', p) and 'same' not in p and 'different' not in p:
            return 0.25
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        if re.search(r'\beither .+ or .+\b', p) and 'only' not in p:
            return 0.28
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and 'measure' not in p:
            return 0.3
        if re.search(r'\b(not enough|insufficient|cannot determine|missing)\b', p):
            return 0.35
        return 0.6
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        if self._solve_numeric(prompt, answer):
            return 0.75
        if self._solve_logic(prompt, answer):
            return 0.7
        if self._solve_algebra(prompt, answer):
            return 0.75
        return 0.4
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        text = prompt + " " + candidate
        props = self._extract_propositions(text)
        if len(props) < 2:
            return self._fallback_score(prompt, candidate)
        
        adj_matrix = self._build_graph(props, text)
        c_vec = self._kolmogorov_proxy(props)
        m_vec = self._epigenetic_propagation(adj_matrix, props)
        fractal_dim = self._fractal_dimension(adj_matrix)
        
        c_score = 1 - (c_vec.mean() - c_vec.min()) / (c_vec.max() - c_vec.min() + 1e-9)
        e_score = 1 - m_vec.std()
        f_score = min(1.0, fractal_dim / 3.0)
        
        base = self.weights[0]*c_score + self.weights[1]*e_score + self.weights[2]*f_score
        comp_bonus = self._computational_bonus(prompt, candidate)
        return 0.5*base + 0.5*comp_bonus
    
    def _extract_propositions(self, text: str) -> List[str]:
        sents = re.split(r'[.!?;]', text)
        props = [s.strip() for s in sents if len(s.strip()) > 5]
        return props[:20]
    
    def _build_graph(self, props: List[str], text: str) -> np.ndarray:
        n = len(props)
        A = np.zeros((n, n))
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i != j:
                    if re.search(r'\b(if|when|because)\b.*' + re.escape(p2[:10]), p1, re.I):
                        A[i, j] = 1
                    if re.search(r'\bnot\b', p1) and any(w in p2.lower() for w in p1.lower().split()):
                        A[i, j] = -1
        return A
    
    def _kolmogorov_proxy(self, props: List[str]) -> np.ndarray:
        return np.array([len(zlib.compress(p.encode())) for p in props], dtype=np.float64)
    
    def _epigenetic_propagation(self, A: np.ndarray, props: List[str]) -> np.ndarray:
        n = A.shape[0]
        m = np.random.rand(n) * 0.1 + 0.5
        neg_nodes = [i for i, p in enumerate(props) if re.search(r'\bnot\b', p)]
        for _ in range(10):
            m_new = 1 / (1 + np.exp(-(A @ m)))
            for i in neg_nodes:
                m_new[i] = 1 - m_new[i]
            if np.linalg.norm(m_new - m) < 1e-4:
                break
            m = m_new
        return m
    
    def _fractal_dimension(self, A: np.ndarray) -> float:
        n = A.shape[0]
        if n < 3:
            return 1.0
        D = np.diag(np.abs(A).sum(axis=1))
        L = D - A
        eigs = np.linalg.eigvalsh(L)
        scales, counts = [], []
        for k in [2, 3, min(4, n)]:
            if k >= n:
                continue
            evecs = np.linalg.eigh(L)[1][:, :k]
            clusters = self._kmeans(evecs, k)
            dense = sum(1 for c in set(clusters) if self._cluster_density(A, clusters, c) > 0.3)
            scales.append(1.0 / k)
            counts.append(max(1, dense))
        if len(scales) < 2:
            return 1.5
        log_s = np.log(scales)
        log_n = np.log(counts)
        return abs(np.polyfit(log_s, log_n, 1)[0])
    
    def _kmeans(self, X: np.ndarray, k: int) -> List[int]:
        n = X.shape[0]
        centers = X[np.random.choice(n, k, replace=False)]
        labels = [0] * n
        for _ in range(5):
            for i in range(n):
                labels[i] = np.argmin([np.linalg.norm(X[i] - c) for c in centers])
            for j in range(k):
                members = [X[i] for i in range(n) if labels[i] == j]
                if members:
                    centers[j] = np.mean(members, axis=0)
        return labels
    
    def _cluster_density(self, A: np.ndarray, labels: List[int], cluster: int) -> float:
        nodes = [i for i, l in enumerate(labels) if l == cluster]
        if len(nodes) < 2:
            return 0
        edges = sum(1 for i in nodes for j in nodes if A[i, j] != 0)
        return edges / (len(nodes) * (len(nodes) - 1) + 1e-9)
    
    def _fallback_score(self, prompt: str, candidate: str) -> float:
        comp = self._computational_bonus(prompt, candidate)
        ncd = self._ncd(prompt, candidate)
        return 0.85*comp + 0.15*(1-ncd)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _computational_bonus(self, prompt: str, candidate: str) -> float:
        scores = [
            self._solve_numeric(prompt, candidate),
            self._solve_logic(prompt, candidate),
            self._solve_algebra(prompt, candidate),
            self._solve_transitivity(prompt, candidate),
            self._solve_negation(prompt, candidate)
        ]
        return max(scores)
    
    def _solve_numeric(self, prompt: str, candidate: str) -> float:
        nums = re.findall(r'\b\d+\.?\d*\b', prompt)
        if len(nums) < 2:
            return 0
        try:
            vals = [float(n) for n in nums]
            if '>' in prompt or 'greater' in prompt or 'more than' in prompt:
                expected = max(vals)
            elif '<' in prompt or 'less' in prompt or 'fewer' in prompt:
                expected = min(vals)
            elif '+' in prompt or 'sum' in prompt or 'total' in prompt:
                expected = sum(vals)
            elif '*' in prompt or 'product' in prompt:
                expected = np.prod(vals)
            else:
                return 0
            cand_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
            if cand_nums and abs(float(cand_nums[0]) - expected) < 0.01:
                return 0.9
        except:
            pass
        return 0
    
    def _solve_logic(self, prompt: str, candidate: str) -> float:
        p = prompt.lower()
        c = candidate.lower()
        if re.search(r'\ball .+ are .+\b', p) and re.search(r'\b.+ is a .+\b', p):
            if 'is a' in c or 'are' in c:
                return 0.75
        if re.search(r'\bif .+ then .+\b', p) and re.search(r'\b(therefore|thus|so)\b', c):
            return 0.7
        return 0
    
    def _solve_algebra(self, prompt: str, candidate: str) -> float:
        match = re.search(r'(\w+) and (\w+) cost \$?(\d+\.?\d*).+\1 costs \$?(\d+\.?\d*)', prompt, re.I)
        if match:
            total, item1_price = float(match.group(3)), float(match.group(4))
            item2_price = total - item1_price
            cand_nums = re.findall(r'\d+\.?\d*', candidate)
            if cand_nums and abs(float(cand_nums[0]) - item2_price) < 0.01:
                return 0.9
        return 0
    
    def _solve_transitivity(self, prompt: str, candidate: str) -> float:
        matches = re.findall(r'(\w+) is (taller|faster|older|bigger) than (\w+)', prompt, re.I)
        if len(matches) >= 2:
            rel = {}
            for m in matches:
                rel[m[0]] = rel.get(m[0], 0) + 1
                rel[m[2]] = rel.get(m[2], 0) - 1
            sorted_items = sorted(rel.items(), key=lambda x: x[1], reverse=True)
            if sorted_items and sorted_items[0][0].lower() in candidate.lower():
                return 0.8
        return 0
    
    def _solve_negation(self, prompt: str, candidate: str) -> float:
        if re.search(r'\bnot\b', prompt):
            if re.search(r'\b(no|not|false|incorrect)\b', candidate, re.I):
                return 0.65
        return 0