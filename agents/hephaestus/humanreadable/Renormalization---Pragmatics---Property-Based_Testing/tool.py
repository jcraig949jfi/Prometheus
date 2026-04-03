import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Renormalized Pragmatic Property-Based Scorer with Dynamics Tracking.
    
    Combines:
    - Property-based world generation (logical model checking)
    - Pragmatic weighting (context-sensitive scoring)
    - Renormalization (iterative clustering to fixed point)
    - Dynamics tracking (state evolution across premises)
    """
    
    def __init__(self):
        np.random.seed(42)
        self.theta = np.array([1.2, 0.8, 1.5, 0.6, 1.0])  # pragmatic weights
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        clauses = self._parse_clauses(prompt)
        
        # Try constructive computation first
        computed = self._compute_answer(prompt, candidates)
        if computed is not None:
            return computed
        
        # Dynamics tracking: state evolution
        dynamics_scores = self._dynamics_score(prompt, candidates)
        
        # Generate worlds satisfying clauses
        worlds, weights = self._generate_worlds(clauses, num_worlds=100)
        
        if len(worlds) == 0:
            # Fallback: use dynamics only
            results = []
            for i, cand in enumerate(candidates):
                results.append({
                    "candidate": cand,
                    "score": dynamics_scores[i],
                    "reasoning": f"Dynamics score (no valid worlds): {dynamics_scores[i]:.3f}"
                })
            results.sort(key=lambda x: x["score"], reverse=True)
            return results
        
        # Renormalization: iterative coarse-graining
        final_weights, final_worlds = self._renormalize(worlds, weights)
        
        # Score candidates
        scores = []
        for cand in candidates:
            struct_score = self._structural_score(prompt, cand, clauses)
            world_score = self._world_score(cand, final_worlds, final_weights)
            ncd = self._ncd(prompt, cand)
            
            # Weighted combination
            total = 0.4 * dynamics_scores[candidates.index(cand)] + 0.35 * struct_score + 0.15 * world_score + 0.1 * (1 - ncd)
            scores.append(total)
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": f"D={dynamics_scores[i]:.2f} S={self._structural_score(prompt, cand, clauses):.2f} W={self._world_score(cand, final_worlds, final_weights):.2f}"
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        
        computed = self._compute_answer(prompt, [answer])
        if computed and computed[0]["score"] > 0.95:
            return min(0.95, meta_conf)
        
        clauses = self._parse_clauses(prompt)
        struct_score = self._structural_score(prompt, answer, clauses)
        
        # Dynamics stability
        dyn_score = self._dynamics_score(prompt, [answer])[0]
        
        base_conf = 0.3 + 0.4 * struct_score + 0.3 * dyn_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why did .* stop)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.28
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.26
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.29
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|more|less)\b', p):
            return 0.27
        
        return 1.0
    
    def _parse_clauses(self, text: str) -> List[Dict]:
        clauses = []
        
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text):
            clauses.append({"type": "compare", "lhs": float(m.group(1)), "op": m.group(2), "rhs": float(m.group(3))})
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text, re.I):
            clauses.append({"type": "conditional", "cond": m.group(1), "cons": m.group(2)})
        
        # Negations
        for m in re.finditer(r'\b(not|n\'t)\s+(\w+)', text, re.I):
            clauses.append({"type": "negation", "pred": m.group(2)})
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text, re.I):
            clauses.append({"type": "order", "first": m.group(1), "rel": m.group(2), "second": m.group(3)})
        
        return clauses
    
    def _generate_worlds(self, clauses: List[Dict], num_worlds: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        if len(clauses) == 0:
            return np.array([]), np.array([])
        
        M = min(10, max(5, len(clauses) * 2))
        worlds = []
        
        for _ in range(num_worlds * 3):
            w = np.random.randint(0, 2, size=M)
            if self._check_world(w, clauses):
                worlds.append(w)
            if len(worlds) >= num_worlds:
                break
        
        if len(worlds) == 0:
            return np.array([]), np.array([])
        
        worlds = np.array(worlds)
        weights = np.ones(len(worlds)) / len(worlds)
        return worlds, weights
    
    def _check_world(self, world: np.ndarray, clauses: List[Dict]) -> bool:
        for cl in clauses:
            if cl["type"] == "compare":
                if cl["op"] == ">":
                    if not (cl["lhs"] > cl["rhs"]):
                        return False
                elif cl["op"] == "<":
                    if not (cl["lhs"] < cl["rhs"]):
                        return False
        return True
    
    def _renormalize(self, worlds: np.ndarray, weights: np.ndarray, max_iter: int = 5, eps: float = 1e-4) -> Tuple[np.ndarray, np.ndarray]:
        if len(worlds) == 0:
            return weights, worlds
        
        prev_weights = weights.copy()
        
        for _ in range(max_iter):
            # Cluster by Hamming distance
            clusters = self._cluster_worlds(worlds, threshold=0.4)
            
            new_worlds = []
            new_weights = []
            
            for cluster in clusters:
                centroid = np.mean(worlds[cluster], axis=0)
                centroid = (centroid > 0.5).astype(int)
                new_worlds.append(centroid)
                new_weights.append(np.sum(weights[cluster]))
            
            worlds = np.array(new_worlds)
            weights = np.array(new_weights)
            weights /= np.sum(weights)
            
            if np.linalg.norm(weights - prev_weights[:len(weights)]) < eps:
                break
            prev_weights = weights.copy()
        
        return weights, worlds
    
    def _cluster_worlds(self, worlds: np.ndarray, threshold: float = 0.4) -> List[List[int]]:
        n = len(worlds)
        clusters = [[i] for i in range(n)]
        
        while True:
            best_pair = None
            best_dist = threshold
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    d = np.mean([np.mean(worlds[ci] != worlds[cj]) for ci in clusters[i] for cj in clusters[j]])
                    if d < best_dist:
                        best_dist = d
                        best_pair = (i, j)
            
            if best_pair is None:
                break
            
            i, j = best_pair
            clusters[i].extend(clusters[j])
            clusters.pop(j)
        
        return clusters
    
    def _structural_score(self, prompt: str, candidate: str, clauses: List[Dict]) -> float:
        score = 0.5
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation alignment
        if re.search(r'\b(not|n\'t|no)\b', p_lower):
            if re.search(r'\b(not|n\'t|no)\b', c_lower):
                score += 0.2
        else:
            if not re.search(r'\b(not|n\'t|no)\b', c_lower):
                score += 0.1
        
        # Comparative alignment
        if re.search(r'\b(more|greater|larger|higher)\b', p_lower):
            if re.search(r'\b(more|greater|larger|higher|yes)\b', c_lower):
                score += 0.15
        
        return min(1.0, score)
    
    def _world_score(self, candidate: str, worlds: np.ndarray, weights: np.ndarray) -> float:
        if len(worlds) == 0:
            return 0.5
        
        c_lower = candidate.lower()
        total = 0.0
        
        for i, w in enumerate(worlds):
            if 'yes' in c_lower and np.mean(w) > 0.5:
                total += weights[i]
            elif 'no' in c_lower and np.mean(w) < 0.5:
                total += weights[i]
        
        return total
    
    def _dynamics_score(self, prompt: str, candidates: List[str]) -> np.ndarray:
        # Parse premises
        sentences = re.split(r'[.!?]', prompt)
        premises = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if len(premises) == 0:
            return np.ones(len(candidates)) * 0.5
        
        # State evolution: each candidate has a state vector
        states = {c: np.random.randn(5) * 0.1 for c in candidates}
        
        for premise in premises:
            for cand in candidates:
                # Update state based on alignment
                alignment = self._text_overlap(premise, cand)
                states[cand] = 0.7 * states[cand] + 0.3 * np.random.randn(5) * alignment
        
        # Stability: measure convergence
        scores = []
        for cand in candidates:
            stability = 1.0 / (1.0 + np.linalg.norm(states[cand]))
            scores.append(stability)
        
        scores = np.array(scores)
        if np.max(scores) > 0:
            scores /= np.max(scores)
        
        return scores
    
    def _text_overlap(self, text1: str, text2: str) -> float:
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)
    
    def _compute_answer(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Numeric comparison
        m = re.search(r'is\s+(\d+\.?\d*)\s+(>|<|greater|less)\s+(\d+\.?\d*)', prompt, re.I)
        if m:
            lhs = float(m.group(1))
            rhs = float(m.group(3))
            op = m.group(2)
            
            if '>' in op or 'greater' in op:
                correct = lhs > rhs
            else:
                correct = lhs < rhs
            
            results = []
            for cand in candidates:
                if ('yes' in cand.lower()) == correct:
                    results.append({"candidate": cand, "score": 0.98, "reasoning": "Computed numeric comparison"})
                else:
                    results.append({"candidate": cand, "score": 0.02, "reasoning": "Failed numeric comparison"})
            results.sort(key=lambda x: x["score"], reverse=True)
            return results
        
        return None
    
    def _ncd(self, text1: str, text2: str) -> float:
        c1 = len(zlib.compress(text1.encode()))
        c2 = len(zlib.compress(text2.encode()))
        c12 = len(zlib.compress((text1 + text2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)