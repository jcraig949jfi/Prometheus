import re
import numpy as np
import zlib
from collections import defaultdict

class ReasoningTool:
    """
    Renormalization x Metacognition x Network Science reasoning tool.
    
    Builds a propositional-constraint graph from prompts and candidates,
    applies belief propagation for metacognitive confidence calibration,
    performs renormalization via community detection, and scores candidates
    based on constraint satisfaction. Implements epistemic honesty for
    ambiguous questions.
    """
    
    def __init__(self):
        self.eta = 0.1  # learning rate for belief propagation
        self.lambda_penalty = 2.0  # violation penalty
        self.base_weight = 0.7
        self.neg_weight = 0.3
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Constraint score: {score:.3f}, Confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        score = self._score_candidate(prompt, answer)
        struct_conf = (score + 1) / 2  # map [-1,1] to [0,1]
        
        # Check if we computed something
        computed = self._has_computation(prompt, answer)
        if computed:
            return min(0.85, struct_conf * 1.2)
        
        # No computation, cap confidence
        return min(0.6, meta_conf * struct_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', p_lower):
            return 0.2
        if re.search(r'why did .* (fail|stop|end)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every .* a ', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) .* who', p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r'either .* or ', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.35
        
        # Unanswerable
        if re.search(r'(impossible|cannot|unknowable)', p_lower):
            return 0.15
        
        return 0.6  # base confidence
    
    def _has_computation(self, prompt: str, answer: str) -> bool:
        # Check if we performed numeric computation
        nums_p = self._extract_numbers(prompt)
        nums_a = self._extract_numbers(answer)
        if nums_p and nums_a:
            return True
        return False
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Build constraint graph
        props, edges, confidences = self._build_graph(prompt, candidate)
        if len(props) == 0:
            return self._ncd_score(prompt, candidate) * 0.15 - 0.85
        
        # Metacognitive belief propagation
        confidences = self._belief_propagation(props, edges, confidences)
        
        # Renormalization
        props, edges, confidences = self._renormalize(props, edges, confidences)
        
        # Score based on constraint satisfaction
        score = self._compute_satisfaction(edges, confidences)
        
        # Add computational component
        comp_score = self._computational_score(prompt, candidate)
        
        # Add small NCD component
        ncd = self._ncd_score(prompt, candidate)
        
        # Weighted combination
        final = 0.5 * score + 0.4 * comp_score + 0.1 * ncd
        return np.clip(final, -1, 1)
    
    def _build_graph(self, prompt: str, candidate: str):
        text = prompt + " " + candidate
        props = []
        edges = []
        prop_map = {}
        
        # Extract propositions (sentences)
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 5:
                if sent not in prop_map:
                    prop_map[sent] = len(props)
                    props.append(sent)
        
        # Extract constraints
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i != j:
                    w = self._extract_constraint(p1, p2)
                    if w > 0:
                        edges.append([i, j, w])
        
        confidences = np.ones(len(props)) * 0.5
        edges = np.array(edges) if edges else np.zeros((0, 3))
        
        return props, edges, confidences
    
    def _extract_constraint(self, p1: str, p2: str) -> float:
        p1_l, p2_l = p1.lower(), p2.lower()
        
        # Negation constraint
        if 'not' in p1_l and any(w in p2_l for w in p1_l.split()):
            return self.neg_weight
        
        # Causal constraint
        if any(c in p1_l for c in ['causes', 'leads to', 'results in']):
            if any(w in p2_l for w in p1_l.split()):
                return self.base_weight
        
        # Conditional constraint
        if 'if' in p1_l and 'then' in p1_l:
            return self.base_weight * 0.8
        
        # Comparative constraint
        if any(c in p1_l for c in ['more than', 'less than', 'greater', 'smaller']):
            return self.base_weight * 0.9
        
        # Temporal constraint
        if any(t in p1_l for t in ['before', 'after', 'during']):
            if any(w in p2_l for w in p1_l.split()):
                return self.base_weight * 0.85
        
        return 0.0
    
    def _belief_propagation(self, props, edges, confidences, rounds=3):
        if len(edges) == 0:
            return confidences
        
        for _ in range(rounds):
            new_conf = confidences.copy()
            for edge in edges:
                src, tgt, w = int(edge[0]), int(edge[1]), edge[2]
                prediction = confidences[src] * w
                new_conf[tgt] += self.eta * (prediction - confidences[tgt])
            confidences = np.clip(new_conf, 0, 1)
        
        return confidences
    
    def _renormalize(self, props, edges, confidences):
        if len(props) < 3 or len(edges) == 0:
            return props, edges, confidences
        
        # Simple community detection via modularity
        communities = self._louvain_simple(len(props), edges)
        
        # Coarse-grain
        new_props = []
        new_conf = []
        comm_map = {}
        
        for comm_id in set(communities):
            indices = [i for i, c in enumerate(communities) if c == comm_id]
            comm_map[comm_id] = len(new_props)
            new_props.append(" | ".join([props[i] for i in indices[:2]]))
            new_conf.append(np.mean([confidences[i] for i in indices]))
        
        # Remap edges
        new_edges = []
        for edge in edges:
            src_comm = communities[int(edge[0])]
            tgt_comm = communities[int(edge[1])]
            if src_comm != tgt_comm:
                new_edges.append([comm_map[src_comm], comm_map[tgt_comm], edge[2]])
        
        new_edges = np.array(new_edges) if new_edges else np.zeros((0, 3))
        new_conf = np.array(new_conf) if new_conf else np.array([0.5])
        
        return new_props, new_edges, new_conf
    
    def _louvain_simple(self, n_nodes, edges):
        # Simple community detection
        communities = list(range(n_nodes))
        
        if len(edges) == 0:
            return communities
        
        # Build adjacency
        adj = defaultdict(list)
        for edge in edges:
            adj[int(edge[0])].append(int(edge[1]))
        
        # Greedy agglomeration
        for node in range(n_nodes):
            if node in adj:
                neighbors = adj[node]
                if neighbors:
                    # Assign to most common neighbor community
                    comm_counts = defaultdict(int)
                    for nb in neighbors:
                        comm_counts[communities[nb]] += 1
                    if comm_counts:
                        communities[node] = max(comm_counts, key=comm_counts.get)
        
        return communities
    
    def _compute_satisfaction(self, edges, confidences):
        if len(edges) == 0:
            return 0.0
        
        sat_sum, vio_sum, total_sum = 0.0, 0.0, 0.0
        
        for edge in edges:
            src, tgt, w = int(edge[0]), int(edge[1]), edge[2]
            if src < len(confidences) and tgt < len(confidences):
                expected = confidences[src] * w
                actual = confidences[tgt]
                total_sum += w
                
                if abs(expected - actual) < 0.3:
                    sat_sum += w
                else:
                    vio_sum += w
        
        if total_sum > 0:
            return (sat_sum - self.lambda_penalty * vio_sum) / total_sum
        return 0.0
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric computation
        nums_p = self._extract_numbers(prompt)
        nums_c = self._extract_numbers(candidate)
        
        if nums_p and nums_c:
            # Try arithmetic operations
            if any(op in prompt.lower() for op in ['+', 'plus', 'add', 'sum']):
                expected = sum(nums_p)
                if any(abs(n - expected) < 0.01 for n in nums_c):
                    score += 0.5
            
            if any(op in prompt.lower() for op in ['-', 'minus', 'subtract', 'difference']):
                if len(nums_p) >= 2:
                    expected = nums_p[0] - nums_p[1]
                    if any(abs(n - expected) < 0.01 for n in nums_c):
                        score += 0.5
            
            if any(op in prompt.lower() for op in ['*', 'times', 'multiply', 'product']):
                expected = np.prod(nums_p)
                if any(abs(n - expected) < 0.01 for n in nums_c):
                    score += 0.5
            
            # Comparison
            if any(op in prompt.lower() for op in ['greater', 'larger', 'more than', '>']):
                if len(nums_p) >= 2 and nums_p[0] > nums_p[1]:
                    if 'yes' in candidate.lower() or str(nums_p[0]) in candidate:
                        score += 0.3
        
        return np.clip(score, 0, 1)
    
    def _extract_numbers(self, text: str) -> list:
        nums = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in nums if n]
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        c_p = len(zlib.compress(prompt.encode()))
        c_c = len(zlib.compress(candidate.encode()))
        c_pc = len(zlib.compress((prompt + candidate).encode()))
        
        ncd = (c_pc - min(c_p, c_c)) / max(c_p, c_c)
        return 1 - ncd