import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Ergodic Theory (stationary distribution of concept graphs),
    Global Workspace Theory (iterative activation broadcasting), and Sensitivity Analysis
    (robustness scoring via perturbation).
    
    Mechanism:
    1. Parse text into a propositional graph (nodes=entities, edges=logic relations).
    2. Compute Ergodic Average: Stationary distribution of the graph's Markov chain.
    3. Compute Global Workspace: Iterative activation propagation to integrate context.
    4. Score: Cosine similarity of workspace vectors, penalized by sensitivity to noise.
    """

    def __init__(self):
        self.alpha = 0.1  # Workspace step size
        self.lambda_pen = 0.2  # Sensitivity penalty weight
        self.perturb_count = 5  # Number of perturbations for sensitivity

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[0-9]+\.?[0-9]*|[^\w\s]', text.lower())

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, List[str]]:
        """Parses text into nodes, adjacency tensor, and edge types."""
        tokens = self._tokenize(text)
        if not tokens:
            return [], np.array([]), []
        
        # Unique entities (nouns/numbers)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'}
        
        # Extract potential nodes (simple heuristic: alphanumeric tokens not in stoplist or numbers)
        raw_nodes = []
        for t in tokens:
            if t.isdigit() or (t.replace('.','',1).isdigit() if '.' in t else False) or (t not in stop_words and len(t) > 1):
                raw_nodes.append(t)
        
        # Deduplicate preserving order
        seen = set()
        nodes = []
        for n in raw_nodes:
            if n not in seen:
                seen.add(n)
                nodes.append(n)
        
        n = len(nodes)
        if n == 0:
            return [], np.array([]), []

        node_map = {node: i for i, node in enumerate(nodes)}
        # Features: [caus, cmp, ord, cond, neg, val]
        f_dim = 6 
        G = np.zeros((n, n, f_dim))

        text_lower = text.lower()
        
        # Helper to find node indices near a match
        def get_nearby_nodes(match_obj, window=3):
            start, end = match_obj.span()
            # Find tokens in vicinity
            nearby = []
            # Simple approximation: check all nodes if they appear near the match in original text
            # For efficiency in this constrained env, we just map based on presence in sentence chunks
            return nodes 

        # 1. Negations
        neg_pattern = re.compile(r'\b(not|no|never|neither)\b')
        for m in neg_pattern.finditer(text_lower):
            # Flag nearest nodes (simplified: assume global effect or nearest 2)
            # In this graph model, we attach negation to edges formed nearby or global flag
            # Simplification: Apply negation to any causal/comparative edge found later? 
            # Better: Mark nodes involved in negated statements. 
            # For this implementation: We will flag edges created by other patterns if they overlap negation.
            pass # Handled inline below for simplicity in single pass logic is hard, so we use a proxy:
                 # If a sentence has 'not', relations within it get negated.

        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent_lower = sent.lower()
            if not sent_lower.strip(): continue
            
            has_neg = bool(re.search(r'\b(not|no|never)\b', sent_lower))
            sent_tokens = self._tokenize(sent)
            sent_nodes = [t for t in sent_tokens if t in node_map]
            
            if len(sent_nodes) < 2: continue

            # Detect relations
            # Causal
            if re.search(r'\b(cause|lead to|result in|imply)\b', sent_lower):
                for i, n1 in enumerate(sent_nodes[:-1]):
                    for n2 in sent_nodes[i+1:]:
                        idx1, idx2 = node_map[n1], node_map[n2]
                        G[idx1, idx2, 0] = 1.0 # caus
                        if has_neg: G[idx1, idx2, 4] = 1.0 # neg
            
            # Comparatives
            cmp_matches = list(re.finditer(r'\b(greater|less|more|fewer|larger|smaller)\b', sent_lower))
            if cmp_matches:
                 # Simplified: connect first and last number-like or entity
                 nums = [t for t in sent_tokens if t.replace('.','',1).isdigit()]
                 if len(nums) >= 2:
                     # Find indices
                     try:
                        idx1 = node_map.get(str(float(nums[0]))) or node_map.get(nums[0])
                        idx2 = node_map.get(str(float(nums[1]))) or node_map.get(nums[1])
                        if idx1 is not None and idx2 is not None:
                            val = float(nums[1]) - float(nums[0])
                            G[idx1, idx2, 1] = 1.0 # cmp
                            G[idx1, idx2, 5] = val
                            if has_neg: G[idx1, idx2, 4] = 1.0
                     except: pass

            # Ordering
            if re.search(r'\b(first|second|before|after|precede|follow)\b', sent_lower):
                for i in range(len(sent_nodes)-1):
                    idx1, idx2 = node_map[sent_nodes[i]], node_map[sent_nodes[i+1]]
                    G[idx1, idx2, 2] = 1.0 # ord
                    if has_neg: G[idx1, idx2, 4] = 1.0

            # Conditionals
            if re.search(r'\b(if|then|unless|provided)\b', sent_lower):
                for i in range(len(sent_nodes)-1):
                    idx1, idx2 = node_map[sent_nodes[i]], node_map[sent_nodes[i+1]]
                    G[idx1, idx2, 3] = 1.0 # cond
                    if has_neg: G[idx1, idx2, 4] = 1.0
            
            # Fallback: Sequential flow for unconnected concepts in same sentence
            if np.sum(G[:, :, :4]) == 0:
                for i in range(len(sent_nodes)-1):
                    idx1, idx2 = node_map[sent_nodes[i]], node_map[sent_nodes[i+1]]
                    G[idx1, idx2, 0] = 0.5 # weak causal
                    if has_neg: G[idx1, idx2, 4] = 1.0

        return nodes, G, tokens

    def _compute_ergodic(self, G: np.ndarray) -> np.ndarray:
        """Computes stationary distribution via power iteration."""
        if G.size == 0: return np.array([])
        
        n, _, f = G.shape
        if n == 0: return np.array([])

        # Aggregate weights: caus(0), cmp(1), ord(2), cond(3) positive; neg(4) reduces weight
        # Weight = sum(types) * (1 - neg_flag)
        weights = np.sum(G[:, :, :4], axis=2) * (1 - G[:, :, 4]) 
        # Ensure self-loops for stability if no outgoing edges
        row_sums = np.sum(weights, axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid div by zero
        P = weights / row_sums
        
        # Power iteration
        pi = np.ones((n, 1)) / n
        for _ in range(100):
            pi_new = P.T @ pi
            if np.linalg.norm(pi_new - pi) < 1e-6:
                break
            pi = pi_new
        return pi.flatten()

    def _global_workspace(self, G: np.ndarray, pi: np.ndarray) -> np.ndarray:
        """Simulates global broadcast."""
        if G.size == 0 or pi.size == 0: return np.array([])
        n = G.shape[0]
        a = np.ones(n) / n
        # Aggregate graph for activation propagation
        G_agg = np.sum(G[:, :, :4], axis=2) * (1 - G[:, :, 4])
        
        for _ in range(20): # Iterations
            delta = G_agg @ a
            a = a + self.alpha * (delta - a) # Normalize implicitly via decay/balance
            a = a / (np.sum(a) + 1e-9) # Normalize
        return a

    def _score_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
        norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0: return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def _perturb(self, text: str) -> str:
        """Generates a perturbed version of the text."""
        import random
        # 1. Flip negation
        if random.random() < 0.5:
            if 'not' in text: text = text.replace('not', '', 1)
            elif 'no ' in text: text = text.replace('no ', 'some ', 1)
        # 2. Numeric jitter
        def jitter(match):
            val = float(match.group(0))
            return str(val * (1 + random.uniform(-0.1, 0.1)))
        text = re.sub(r'\d+\.?\d*', jitter, text, count=1)
        # 3. Swap comparator ( crude )
        if 'greater' in text: text = text.replace('greater', 'less')
        elif 'less' in text: text = text.replace('less', 'greater')
        
        return text

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        # Parse prompt once
        p_nodes, p_G, _ = self._parse_graph(prompt)
        if p_G.size == 0: 
            # Fallback if parsing fails completely
            p_vec = np.array([1.0])
        else:
            p_pi = self._compute_ergodic(p_G)
            p_vec = self._global_workspace(p_G, p_pi)

        for cand in candidates:
            full_text = f"{prompt} {cand}"
            c_nodes, c_G, _ = self._parse_graph(full_text)
            
            if c_G.size == 0:
                c_vec = np.array([1.0])
            else:
                c_pi = self._compute_ergodic(c_G)
                c_vec = self._global_workspace(c_G, c_pi)

            # Align dimensions if possible (simple padding/truncation for demo)
            min_len = min(p_vec.size, c_vec.size)
            if min_len == 0: 
                base_sim = 0.0
                c_vec_trim = c_vec
                p_vec_trim = p_vec
            else:
                p_vec_trim = p_vec[:min_len] if p_vec.size > min_len else np.pad(p_vec, (0, min_len-p_vec.size))
                c_vec_trim = c_vec[:min_len] if c_vec.size > min_len else np.pad(c_vec, (0, min_len-c_vec.size))
                base_sim = self._score_similarity(p_vec_trim, c_vec_trim)

            # Sensitivity Analysis
            sensitivities = []
            for _ in range(self.perturb_count):
                pert_text = self._perturb(full_text)
                _, pc_G, _ = self._parse_graph(pert_text)
                if pc_G.size == 0:
                    sens = 0.0
                else:
                    pc_pi = self._compute_ergodic(pc_G)
                    pc_vec = self._global_workspace(pc_G, pc_pi)
                    min_l = min(p_vec_trim.size, pc_vec.size)
                    if min_l == 0: sens = 0.0
                    else:
                        pc_trim = pc_vec[:min_l] if pc_vec.size > min_l else np.pad(pc_vec, (0, min_l-pc_vec.size))
                        pv_trim = p_vec_trim[:min_l] if p_vec_trim.size > min_l else np.pad(p_vec_trim, (0, min_l-pc_vec.size)) # Re-align
                        # Actually compare perturbed candidate to original prompt vector logic
                        # But here we compare Perturbed Candidate vs Prompt
                        # Wait, definition: S_i = |S0 - cosine(pi_A_i, pi_R)|
                        # R is Reference (Prompt+Candidate ideal?) or just Prompt? 
                        # Algorithm says: Candidate A, Reference R. 
                        # Let's assume Reference R is the Prompt's logical structure, A is Candidate.
                        # Actually, usually R is Ground Truth. Here we don't have GT.
                        # Interpretation: R = Prompt's implication. A = Candidate.
                        # Let's stick to the code logic: Compare Candidate Vector to Prompt Vector.
                        # Sensitivity: How much does changing the candidate change the score?
                        
                        # Recalculate base for this specific pair alignment
                        curr_sim = self._score_similarity(p_vec_trim, pc_trim)
                        sens = abs(base_sim - curr_sim)
                sensitivities.append(sens)
            
            avg_sens = np.mean(sensitivities) if sensitivities else 0.0
            score = base_sim - self.lambda_pen * avg_sens
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural match: {base_sim:.3f}, Robustness penalty: {avg_sens:.3f}"
            })

        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        # Normalize score 0-1 roughly
        sc = res[0]['score']
        return float(np.clip((sc + 1.0) / 2.0, 0.0, 1.0))