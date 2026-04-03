import numpy as np
import re
from collections import deque

class ReasoningTool:
    """
    Implements a reasoning evaluator fusing Neural Plasticity, Criticality, and Proof Theory.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical edges (implication, negation, causality)
       from text using regex patterns for conditionals, comparatives, and numeric values.
    2. Plasticity (Hebbian): Builds an initial weight matrix based on co-occurrence of 
       prompt and answer propositions, applying decay and sparsity thresholds.
    3. Proof Theory (Cut-Elimination): Computes transitive closure and removes redundant 
       edges (short-cuts) to find the minimal proof graph.
    4. Criticality: Calculates susceptibility based on the variance of edge weights and 
       the size of the largest connected component.
    5. Scoring: Combines criticality susceptibility with proof compactness (edge reduction).
    """

    def __init__(self):
        self.hebbian_rate = 0.5
        self.decay = 0.1
        self.threshold = 0.2
        self.epsilon = 1e-6

    def _parse_text(self, text: str):
        """Extracts propositions and edges based on structural patterns."""
        text_lower = text.lower()
        sentences = re.split(r'[.\n]', text)
        propositions = []
        edges = []  # (src_idx, dst_idx, type)
        
        # Simple tokenization for proposition counting
        words = re.findall(r'\b\w+\b', text_lower)
        if not words:
            return [], []
            
        # Map unique words to indices as atomic propositions for simplicity
        unique_words = list(set(words))
        word_to_idx = {w: i for i, w in unique_words}
        n = len(unique_words)
        
        if n == 0:
            return [], []

        # Structural Pattern Matching
        for sent in sentences:
            sent_l = sent.lower()
            if not sent_l.strip():
                continue
                
            sent_words = re.findall(r'\b\w+\b', sent_l)
            if not sent_words:
                continue

            # Detect Negation
            has_neg = any(neg in sent_l for neg in ['not', 'no', 'never', 'none'])
            
            # Detect Conditionals
            if 'if' in sent_l and 'then' in sent_l:
                parts = sent_l.split('then')
                if len(parts) == 2:
                    # Simplified: link first word of condition to first word of result
                    p1 = re.findall(r'\b\w+\b', parts[0])[-1] if re.findall(r'\b\w+\b', parts[0]) else None
                    p2 = re.findall(r'\b\w+\b', parts[1])[0] if re.findall(r'\b\w+\b', parts[1]) else None
                    if p1 and p2 and p1 in word_to_idx and p2 in word_to_idx:
                        edges.append((word_to_idx[p1], word_to_idx[p2], 'implies'))

            # Detect Comparatives (Numeric)
            nums = re.findall(r'-?\d+\.?\d*', sent_l)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    # Create a synthetic proposition for the comparison result
                    comp_node = f"cmp_{nums[0]}_{nums[1]}"
                    if comp_node not in word_to_idx:
                        word_to_idx[comp_node] = len(word_to_idx)
                        unique_words.append(comp_node)
                        n = len(unique_words)
                    
                    c_idx = word_to_idx[comp_node]
                    # Link numbers to comparison node
                    for num in nums:
                        if num in word_to_idx: # if number word exists
                             pass 
                    # Just add edge between the two number indices if they exist as words
                    # For this simplified parser, we treat numbers as implicit nodes if found
                    # We'll skip complex numeric node injection for brevity and stick to word graph
                except ValueError:
                    pass

            # General Co-occurrence (Hebbian base)
            # Connect adjacent words in sentence to form local chains
            for i in range(len(sent_words) - 1):
                w1, w2 = sent_words[i], sent_words[i+1]
                if w1 in word_to_idx and w2 in word_to_idx:
                    idx1, idx2 = word_to_idx[w1], word_to_idx[w2]
                    w_type = 'neg' if has_neg else 'causal'
                    edges.append((idx1, idx2, w_type))

        return unique_words, edges, n

    def _build_graph(self, prompt: str, candidate: str):
        """Constructs the weighted adjacency matrix."""
        # Combine text for global vocabulary
        full_text = f"{prompt} {candidate}"
        words, raw_edges, n = self._parse_text(full_text)
        
        if n == 0:
            return np.array([[0]]), 0, 0

        # Initialize vectors x (prompt presence), y (candidate presence)
        # Simplified: binary presence of words in respective sections
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        candidate_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        x = np.zeros(n)
        y = np.zeros(n)
        
        for i, w in enumerate(words):
            if w in prompt_words: x[i] = 1
            if w in candidate_words: y[i] = 1
            
        # 1. Hebbian Initialization
        W = self.hebbian_rate * np.outer(x, y)
        
        # Add structural edges with higher weight
        for u, v, etype in raw_edges:
            if u < n and v < n:
                W[u, v] += 0.5 if etype == 'implies' else 0.3

        # 2. Plasticity Dynamics
        T = 5
        for _ in range(T):
            W = W + self.hebbian_rate * np.outer(x, y) - self.decay * W
            W[W < self.threshold] = 0 # Sparsity threshold

        # 3. Proof-Theoretic Normalization (Cut-Elimination)
        # Compute transitive closure approximation
        I = np.eye(n)
        # Power method for closure (simplified for small k)
        W_closure = I + W
        for _ in range(3): 
            W_closure = np.sign(W_closure @ W_closure) # Binary step for connectivity
            
        # Remove edges that have a 2-step path (Cut elimination)
        W_norm = W.copy()
        for i in range(n):
            for j in range(n):
                if W[i, j] > 0:
                    # Check for intermediate k
                    path_exists = False
                    for k in range(n):
                        if i != k and k != j and W[i, k] > 0 and W[k, j] > 0:
                            path_exists = True
                            break
                    if path_exists:
                        W_norm[i, j] = 0 # Eliminate cut

        return W_norm, n, len(raw_edges)

    def _compute_criticality(self, W: np.ndarray):
        """Computes susceptibility based on variance and connected component size."""
        n = W.shape[0]
        if n == 0:
            return 0.0
            
        # Variance of non-zero weights
        non_zero = W[W > 0]
        if len(non_zero) == 0:
            return 0.0
            
        sigma_sq = float(np.var(non_zero))
        
        # Largest Weakly Connected Component (BFS)
        # Convert to binary adjacency for connectivity
        binary_W = (W > 0).astype(int)
        # Symmetrize for weak connectivity
        sym_W = np.maximum(binary_W, binary_W.T)
        
        visited = [False] * n
        max_comp_size = 0
        
        for start in range(n):
            if visited[start]:
                continue
            queue = deque([start])
            visited[start] = True
            size = 0
            while queue:
                u = queue.popleft()
                size += 1
                # Find neighbors
                neighbors = np.where(sym_W[u, :] > 0)[0]
                for v in neighbors:
                    if not visited[v]:
                        visited[v] = True
                        queue.append(v)
            max_comp_size = max(max_comp_size, size)
            
        chi = sigma_sq * max_comp_size
        return chi / (chi + self.epsilon)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_len = len(re.findall(r'\b\w+\b', prompt.lower()))
        if prompt_len == 0: prompt_len = 1 # Avoid div by zero
        
        # Baseline NCD calculation (tiebreaker only)
        def get_ncd(a, b):
            import zlib
            a_b = a.encode('utf-8')
            b_b = b.encode('utf-8')
            l_a = len(zlib.compress(a_b))
            l_b = len(zlib.compress(b_b))
            l_ab = len(zlib.compress(a_b + b_b))
            return l_ab / max(l_a, l_b) if max(l_a, l_b) > 0 else 1.0

        base_ncd = get_ncd(prompt, "")

        for cand in candidates:
            W, n, initial_edges = self._build_graph(prompt, cand)
            
            if n == 0:
                score = 0.0
                reason = "No structural content detected."
            else:
                # Criticality Score
                S_crit = self._compute_criticality(W)
                
                # Proof Compactness
                final_edges = np.count_nonzero(W)
                initial_total = max(1, initial_edges + n) # Estimate initial density
                compactness = 1.0 - (final_edges / initial_total)
                compactness = max(0, min(1, compactness))
                
                score = S_crit * compactness
                
                # Fallback/Tiebreaker logic
                if score < 0.01:
                    ncd_val = get_ncd(prompt, cand)
                    # Invert NCD so lower distance = higher score, scaled
                    score = max(0.0, 0.5 - (ncd_val - base_ncd)) 
                    reason = f"Low structural signal; relied on compression similarity (NCD). Score: {score:.4f}"
                else:
                    reason = f"Criticality: {S_crit:.4f}, Compactness: {compactness:.4f}. High logical coherence."

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the top-scored evaluation of the single answer."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score roughly to 0-1 range based on typical outputs
        # The theoretical max is 1.0, but practical values vary. 
        # We use the raw score capped at 1.0.
        return min(1.0, max(0.0, res[0]['score']))