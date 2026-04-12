from typing import Dict, Tuple

"""
Morphogenesis x Analogical Reasoning x Nash Equilibrium Reasoning Tool

Combines reaction-diffusion activation spreading to Nash equilibrium with
structural graph similarity and constructive computation.
"""

import re
import zlib
from typing import List, Dict, Tuple
import math

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.6  # Weight for equilibrium vs structural similarity
        self.convergence_threshold = 1e-4
        self.max_iterations = 100
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined morphogenesis + analogy + computation."""
        results = []
        
        # Extract reference structure from prompt
        prompt_graph = self._build_graph(prompt)
        
        for candidate in candidates:
            # Structural + computation score
            score = self._score_candidate(prompt, candidate, prompt_graph)
            reasoning = self._explain_score(prompt, candidate)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-cognitive checks."""
        # Check for epistemic issues first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural + computational confidence
        prompt_graph = self._build_graph(prompt)
        base_score = self._score_candidate(prompt, answer, prompt_graph)
        
        # Cap at 0.9 unless we have definitive computation
        if self._has_definitive_computation(prompt, answer):
            return min(0.95, base_score)
        
        return min(0.75, base_score * meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower) and not re.search(r'\b(most|least|faster|slower)\b', p_lower):
            return 0.3
        
        return 1.0  # No epistemic issues detected
    
    def _build_graph(self, text: str) -> Dict:
        """Extract nodes (propositions) and typed edges (relations)."""
        nodes = []
        edges = []
        
        # Extract propositions (simplified: sentences/clauses)
        sentences = re.split(r'[.;]', text)
        for i, sent in enumerate(sentences):
            if len(sent.strip()) < 3:
                continue
            
            feature = [
                1.0 if re.search(r'\b(not|no|never)\b', sent.lower()) else 0.0,
                1.0 if re.search(r'\d+', sent) else 0.0,
                float(hash(sent) % 10)  # Semantic type approximation
            ]
            nodes.append({"id": i, "text": sent.strip(), "feature": feature})
        
        # Extract typed edges
        full_text = text.lower()
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i == j:
                    continue
                
                # Check if node_i and node_j are related
                text_i = node_i["text"].lower()
                text_j = node_j["text"].lower()
                
                # Causal
                if re.search(r'(because|leads to|results in|causes)', full_text):
                    if text_i in full_text and text_j in full_text:
                        edges.append({"from": i, "to": j, "type": "causal", "weight": 1.0})
                
                # Conditional
                if re.search(r'\bif\b.*\bthen\b', full_text):
                    edges.append({"from": i, "to": j, "type": "conditional", "weight": 0.8})
                
                # Comparative
                if re.search(r'(more|less|greater|smaller)', text_i):
                    weight = 0.5 if 'more' in text_i or 'greater' in text_i else -0.5
                    edges.append({"from": i, "to": j, "type": "comparative", "weight": weight})
        
        return {"nodes": nodes, "edges": edges}
    
    def _morphogenesis(self, graph: Dict, external: List[float]) -> List[float]:
        """Run reaction-diffusion to Nash equilibrium."""
        n = len(graph["nodes"])
        if n == 0:
            return []
        
        # Build adjacency matrix
        W = [[0.0] * n for _ in range(n)]
        for edge in graph["edges"]:
            i, j = edge["from"], edge["to"]
            if i < n and j < n:
                w = edge["weight"]
                # Apply negation multiplier
                if graph["nodes"][i]["feature"][0] > 0.5:
                    w *= -1.0
                W[i][j] = w
        
        # Initialize activation
        a = external[:]
        bias = 0.1
        
        # Iterate to convergence
        for _ in range(self.max_iterations):
            a_new = []
            for i in range(n):
                val = sum(W[i][j] * a[j] for j in range(n)) + bias
                a_new.append(1.0 / (1.0 + math.exp(-val)))  # Sigmoid
            
            # Check convergence
            delta = sum(abs(a_new[i] - a[i]) for i in range(n))
            a = a_new
            if delta < self.convergence_threshold:
                break
        
        return a
    
    def _compute_answer(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Constructive computation for numeric, probabilistic, logical questions."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        if len(nums_p) >= 2 and len(nums_c) >= 1:
            # Check if question asks for comparison
            if re.search(r'(greater|larger|more|higher|bigger)', p_lower):
                try:
                    vals = [float(x) for x in nums_p]
                    ans = float(nums_c[0])
                    if ans == max(vals):
                        return True, 0.9
                except:
                    pass
            
            if re.search(r'(less|smaller|lower|fewer)', p_lower):
                try:
                    vals = [float(x) for x in nums_p]
                    ans = float(nums_c[0])
                    if ans == min(vals):
                        return True, 0.9
                except:
                    pass
        
        # Boolean negation
        if re.search(r'\bnot\b', p_lower):
            if re.search(r'\b(no|false|incorrect)\b', c_lower):
                return True, 0.7
        
        # Conditional logic (modus ponens)
        if re.search(r'\bif\b.*\bthen\b', p_lower):
            if re.search(r'\btherefore\b', c_lower):
                return True, 0.6
        
        return False, 0.0
    
    def _score_candidate(self, prompt: str, candidate: str, prompt_graph: Dict) -> float:
        """Combined score: morphogenesis + analogy + computation."""
        # Constructive computation (40%)
        has_computation, comp_score = self._compute_answer(prompt, candidate)
        
        # Morphogenesis equilibrium (30%)
        candidate_graph = self._build_graph(candidate)
        n_prompt = len(prompt_graph["nodes"])
        n_cand = len(candidate_graph["nodes"])
        
        if n_prompt > 0:
            external = [1.0] * n_prompt  # All prompt nodes activated
            a_star = self._morphogenesis(prompt_graph, external)
            morph_score = math.sqrt(sum(x*x for x in a_star)) / max(1, len(a_star))
        else:
            morph_score = 0.5
        
        # Structural similarity (20%)
        struct_score = self._structural_similarity(prompt_graph, candidate_graph)
        
        # NCD tiebreaker (10%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - min(1.0, ncd)
        
        # Combine
        score = 0.4 * comp_score + 0.3 * morph_score + 0.2 * struct_score + 0.1 * ncd_score
        
        return min(1.0, max(0.0, score))
    
    def _structural_similarity(self, g1: Dict, g2: Dict) -> float:
        """Approximate graph edit distance via node/edge matching."""
        n1, n2 = len(g1["nodes"]), len(g2["nodes"])
        if n1 == 0 and n2 == 0:
            return 1.0
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Simplified Hungarian: greedy matching on feature distance
        max_size = max(n1, n2)
        matched = 0
        
        for node1 in g1["nodes"]:
            best_dist = float('inf')
            for node2 in g2["nodes"]:
                dist = sum((node1["feature"][k] - node2["feature"][k])**2 for k in range(3))
                best_dist = min(best_dist, dist)
            if best_dist < 1.0:  # Threshold
                matched += 1
        
        return matched / max_size
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _has_definitive_computation(self, prompt: str, answer: str) -> bool:
        """Check if we computed a definitive answer."""
        has_comp, score = self._compute_answer(prompt, answer)
        return has_comp and score > 0.85
    
    def _explain_score(self, prompt: str, candidate: str) -> str:
        """Brief explanation of scoring."""
        has_comp, comp_score = self._compute_answer(prompt, candidate)
        
        if has_comp:
            return f"Computation match (score: {comp_score:.2f})"
        
        if self._meta_confidence(prompt) < 0.3:
            return "Low confidence: ambiguous or unanswerable prompt"
        
        return "Structural and morphogenesis-based scoring"