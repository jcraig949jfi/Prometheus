from typing import Dict, Tuple

"""
Criticality x Compositionality x Nash Equilibrium Reasoning Tool

Parses logical propositions into a constraint graph, converges to Nash equilibrium
via best-response dynamics, measures criticality through perturbation susceptibility,
and computes compositional scores weighted by syntactic depth.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-3
        self.max_iters = 50
        self.n_perturbations = 10
        self.delta = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for candidate in candidates:
            combined = f"{prompt} {candidate}"
            score = self._compute_score(prompt, candidate, combined)
            conf = self.confidence(prompt, candidate)
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": f"Nash score: {score:.3f}, Confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        combined = f"{prompt} {answer}"
        nodes, edges, depths = self._parse_to_graph(combined)
        if len(nodes) == 0:
            return 0.2
        values = self._nash_equilibrium(nodes, edges)
        chi = self._criticality(nodes, edges, values)
        base_conf = min(0.85, 0.5 + 0.3 * (1.0 - min(chi, 1.0)))
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|quit|why did .* fail|why .* stop)', p_lower):
            return 0.25
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an)\b', p_lower):
            return 0.28
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.27
        # False dichotomy
        if re.search(r'\beither .+ or\b', p_lower) and 'only' not in p_lower:
            return 0.29
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(highest|lowest|most|least|largest|smallest)\b', p_lower):
                return 0.26
        # Unanswerability markers
        if re.search(r'\b(cannot determine|insufficient|not enough info|depends on)\b', p_lower):
            return 0.24
        return 1.0
    
    def _compute_score(self, prompt: str, candidate: str, combined: str) -> float:
        # Constructive computation (40%)
        comp_score = self._constructive_compute(prompt, candidate)
        # Structural Nash score (45%)
        nodes, edges, depths = self._parse_to_graph(combined)
        if len(nodes) > 0:
            values = self._nash_equilibrium(nodes, edges)
            nash_score = self._compositional_score(values, depths)
        else:
            nash_score = 0.5
        # NCD tiebreaker (15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        return 0.4 * comp_score + 0.45 * nash_score + 0.15 * ncd_score
    
    def _constructive_compute(self, prompt: str, candidate: str) -> float:
        score = 0.5
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|==|greater|less)\s*(\d+\.?\d*)', prompt)
        if num_match:
            try:
                a, op, b = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
                correct = (op in ['>', 'greater'] and a > b) or (op in ['<', 'less'] and a < b)
                ans_lower = candidate.lower()
                if correct and any(w in ans_lower for w in ['yes', 'true', 'correct', 'greater']):
                    score = 0.9
                elif not correct and any(w in ans_lower for w in ['no', 'false', 'incorrect', 'less']):
                    score = 0.9
            except:
                pass
        # Arithmetic evaluation
        arith_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if arith_match:
            try:
                a, op, b = int(arith_match.group(1)), arith_match.group(2), int(arith_match.group(3))
                ops = {'+': a+b, '-': a-b, '*': a*b, '/': a//b if b!=0 else 0}
                result = ops.get(op, 0)
                if str(result) in candidate:
                    score = 0.95
            except:
                pass
        # Bayesian reasoning
        if 'base rate' in prompt.lower() or 'probability' in prompt.lower():
            nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            if len(nums) >= 2:
                posterior = nums[0] * nums[1] / (nums[0] * nums[1] + (1 - nums[0]) * 0.1) if len(nums) >= 2 else 0.5
                cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if cand_nums and abs(cand_nums[0] - posterior) < 0.1:
                    score = 0.92
        # Temporal ordering
        if re.search(r'\b(before|after|then|first|second)\b', prompt.lower()):
            events = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(events) >= 2 and events[0] in candidate and events[-1] not in candidate[:len(candidate)//2]:
                score = 0.85
        return score
    
    def _parse_to_graph(self, text: str) -> Tuple[List[float], List[Tuple[int, int, str]], List[int]]:
        nodes = []
        edges = []
        depths = []
        tokens = re.split(r'[,;.]', text)
        node_idx = 0
        for depth, token in enumerate(tokens):
            t = token.strip().lower()
            if len(t) < 3:
                continue
            # Negation
            if re.search(r'\b(not|no|never)\b', t):
                nodes.append(0.0)
                depths.append(depth + 1)
                node_idx += 1
            # Numeric comparison
            elif re.search(r'\d+\.?\d*\s*(>|<)', t):
                m = re.search(r'(\d+\.?\d*)\s*([><])\s*(\d+\.?\d*)', t)
                if m:
                    a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
                    val = 1.0 / (1.0 + np.exp(-(a - b))) if op == '>' else 1.0 / (1.0 + np.exp(-(b - a)))
                    nodes.append(val)
                    depths.append(depth + 1)
                    node_idx += 1
            # Conditional
            elif 'if' in t and 'then' in t:
                nodes.append(0.7)
                depths.append(depth + 1)
                if node_idx > 0:
                    edges.append((node_idx - 1, node_idx, 'IMPLIES'))
                node_idx += 1
            # Causal
            elif re.search(r'\b(because|causes|leads to)\b', t):
                nodes.append(0.6)
                depths.append(depth + 1)
                if node_idx > 0:
                    edges.append((node_idx - 1, node_idx, 'CAUSE'))
                node_idx += 1
            # Default positive
            elif len(t.split()) > 2:
                nodes.append(1.0)
                depths.append(depth + 1)
                if node_idx > 0 and 'and' in t:
                    edges.append((node_idx - 1, node_idx, 'AND'))
                elif node_idx > 0 and 'or' in t:
                    edges.append((node_idx - 1, node_idx, 'OR'))
                node_idx += 1
        return nodes, edges, depths
    
    def _nash_equilibrium(self, nodes: List[float], edges: List[Tuple[int, int, str]]) -> np.ndarray:
        n = len(nodes)
        if n == 0:
            return np.array([])
        v = np.array(nodes, dtype=float)
        W_and = np.zeros((n, n))
        W_or = np.zeros((n, n))
        W_imp = np.zeros((n, n))
        for i, j, op in edges:
            if i < n and j < n:
                if op == 'AND':
                    W_and[i, j] = 1
                elif op == 'OR':
                    W_or[i, j] = 1
                elif op in ['IMPLIES', 'CAUSE']:
                    W_imp[i, j] = 1
        for _ in range(self.max_iters):
            v_prev = v.copy()
            for i in range(n):
                E0 = np.sum(W_and[i, :] * v) + np.sum(W_or[i, :] * (1 - v)) + np.sum(W_imp[i, :] * v)
                E1 = np.sum(W_and[i, :] * (1 - v)) + np.sum(W_or[i, :] * v) + np.sum(W_imp[i, :] * (1 - v))
                v[i] = 0.0 if E0 < E1 else 1.0
            if np.linalg.norm(v - v_prev, 1) < self.epsilon:
                break
        return v
    
    def _criticality(self, nodes: List[float], edges: List[Tuple[int, int, str]], v: np.ndarray) -> float:
        if len(v) == 0:
            return 0.0
        variations = []
        for _ in range(self.n_perturbations):
            v_pert = v + np.random.uniform(-self.delta, self.delta, len(v))
            v_pert = np.clip(v_pert, 0, 1)
            v_new = self._nash_equilibrium(v_pert.tolist(), edges)
            variations.append(v_new)
        chi = np.var(variations) / (self.delta ** 2) if self.delta > 0 else 0.0
        return float(chi)
    
    def _compositional_score(self, values: np.ndarray, depths: List[int]) -> float:
        if len(values) == 0:
            return 0.5
        weights = np.array([1.0 / max(d, 1) for d in depths])
        return float(np.sum(weights * values) / np.sum(weights))
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))