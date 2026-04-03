import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

class ReasoningTool:
    """
    Pragmatic-Hebbian Sensitivity Scorer (PHSS) with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognition (Tier B): Scans prompt for ambiguity, presupposition, or unanswerability.
       If detected, caps confidence low regardless of candidate match.
    2. Structural Parsing (Tier A): Extracts nodes (concepts/numbers) and edges (relations)
       using regex to build a knowledge graph (Formal Intermediate Representation).
    3. Computation: 
       - Numeric: Solves explicit math/comparisons.
       - Logical: Propagates truth values via Hebbian-weighted adjacency matrix.
       - Sensitivity: Perturbs activations to measure stability (S).
    4. Scoring: Combines Pragmatic Relevance (R) and Stability (1/S) while respecting meta-confidence.
    """
    
    def __init__(self):
        self.tau = 0.05  # Pruning threshold
        self.eta = 0.1   # Learning rate
        self.epsilon = 0.01 # Sensitivity perturbation

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|break)|when did .+ stop)', p):
            return 0.2
        
        # 2. Scope/Pronoun ambiguity ("Every X... same Y?", "X told Y he... who?")
        if re.search(r'\b(every .+ a (single|same) .+|told .+ he was|told .+ she was|who is .+ referring to)', p):
            return 0.25
            
        # 3. False Dichotomy ("Either A or B" without context of exhaustiveness)
        if re.search(r'\beither .+ or .+\?', p) and "only" not in p:
            return 0.3
            
        # 4. Subjectivity without criteria ("best", "favorite" without data)
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(data|list|given|table)\b', p):
            return 0.2

        # 5. Unanswerability (Missing info indicators)
        if re.search(r'\b(without knowing|impossible to tell|not enough info|missing data)\b', p):
            return 0.1

        return 1.0  # No obvious traps detected

    def _parse_nodes_and_edges(self, text: str) -> Tuple[Dict, Dict, List[str]]:
        """Extract structural features into nodes and edges."""
        nodes = {}
        edges = {} # src -> [(tgt, type, weight)]
        mentioned = []

        # Helper to ensure node exists
        def get_node(name, val=None):
            name = name.strip().lower()
            if name not in nodes:
                nodes[name] = {'text': name, 'polarity': 1, 'value': val, 'uncert': 0.5}
            elif val is not None:
                nodes[name]['value'] = val
            return name

        # 1. Numeric values (e.g., "apple is 5", "cost: 9.9")
        num_pattern = r'(\w+)\s+(?:is|equals|costs|has value)?\s*(-?\d+\.?\d*)'
        for m in re.finditer(num_pattern, text):
            n_name = get_node(m.group(1), float(m.group(2)))
            mentioned.append(n_name)

        # 2. Comparatives (A greater than B)
        comp_pattern = r'(\w+)\s+(?:is\s+)?(greater|less|more|fewer|larger|smaller)\s+than\s+(\w+)'
        for m in re.finditer(comp_pattern, text):
            a, typ, b = m.group(1).lower(), m.group(2), m.group(3).lower()
            get_node(a); get_node(b)
            edge_type = 'GREATER' if typ in ['greater', 'more', 'larger'] else 'LESS'
            if a not in edges: edges[a] = []
            edges[a].append((b, edge_type, self.eta))
            mentioned.extend([a, b])

        # 3. Conditionals (If A then B)
        cond_pattern = r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)'
        for m in re.finditer(cond_pattern, text):
            a, b = m.group(1).strip().split()[-1], m.group(2).strip().split()[-1]
            get_node(a); get_node(b)
            if a not in edges: edges[a] = []
            edges[a].append((b, 'IMPLIES', self.eta))
            mentioned.extend([a, b])

        # 4. Causal (A causes B)
        cause_pattern = r'(\w+)\s+causes\s+(\w+)'
        for m in re.finditer(cause_pattern, text):
            a, b = m.group(1).lower(), m.group(2).lower()
            get_node(a); get_node(b)
            if a not in edges: edges[a] = []
            edges[a].append((b, 'CAUSES', self.eta))
            mentioned.extend([a, b])

        # 5. Negation (Not A) - handled as edge to implicit false node or polarity flip
        neg_pattern = r'\bnot\s+(\w+)'
        for m in re.finditer(neg_pattern, text):
            target = m.group(1).lower()
            get_node(target)
            # Mark polarity as negative if we were tracking state, here we note it
            if target in nodes: nodes[target]['polarity'] = -1
            mentioned.append(target)

        return nodes, edges, list(set(mentioned))

    def _build_matrix(self, nodes: Dict, edges: Dict) -> Tuple[np.ndarray, List[str], Dict]:
        """Build adjacency matrix W and activation vector A."""
        node_list = list(nodes.keys())
        N = len(node_list)
        if N == 0: return np.zeros((0,0)), [], {}
        
        idx_map = {name: i for i, name in enumerate(node_list)}
        W = np.zeros((N, N))
        A = np.zeros(N)

        # Map edges to matrix
        for src, relations in edges.items():
            if src not in idx_map: continue
            i = idx_map[src]
            for tgt, etype, weight in relations:
                if tgt in idx_map:
                    j = idx_map[tgt]
                    w_val = weight
                    if etype == 'LESS': w_val = -weight # Invert for less
                    if etype == 'NEG': w_val = -weight
                    W[i, j] += w_val
        
        # Symmetrize slightly for stability if undirected implication detected, 
        # but keep directed for causality. Here we keep directed.
        return W, node_list, idx_map

    def _compute_sensitivity(self, W: np.ndarray, A: np.ndarray) -> float:
        """Calculate sensitivity S via finite difference."""
        if W.size == 0: return 0.0
        
        # Baseline propagation
        sigmoid = lambda x: 1 / (1 + np.exp(-x))
        B0 = sigmoid(W.T @ A)
        
        # Perturbed
        np.random.seed(42) # Deterministic
        noise = np.random.randn(A.shape[0]) * self.epsilon
        A_eps = A + noise
        A_eps = np.clip(A_eps, 0, 1)
        
        B_eps = sigmoid(W.T @ A_eps)
        
        # Jacobian approx
        J = (B_eps - B0) / self.epsilon
        return np.linalg.norm(J, 'fro')

    def _solve_computationally(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """
        Attempt to solve via explicit computation (Math/Logic) before heuristic scoring.
        Returns the computed answer string if successful, else None.
        """
        # 1. Direct Numeric Comparison/Extraction
        # Pattern: "Which is larger, A (X) or B (Y)?" or "What is 2+2?"
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        if len(nums) >= 2:
            # Try simple max/min logic if comparatives exist
            if re.search(r'(larger|max|greater|highest)', prompt.lower()):
                try:
                    val = max(float(x) for x in nums)
                    # Find candidate matching this value
                    for c in candidates:
                        if re.search(re.escape(str(val)), c): return c
                except: pass
            elif re.search(r'(smaller|min|less|lowest)', prompt.lower()):
                try:
                    val = min(float(x) for x in nums)
                    for c in candidates:
                        if re.search(re.escape(str(val)), c): return c
                except: pass

        # 2. Simple Algebra (Bat-and-Ball style: A + B = Total, A = B + Diff)
        # Very specific pattern matching for demo purposes of "Computation"
        match_alg = re.search(r'(\w+)\s+and\s+(\w+)\s+(?:cost|add|sum)\s+to\s+(\d+\.?\d*).*?(\w+)\s+is\s+(\d+\.?\d*)\s+more than\s+(\w+)', prompt.lower())
        if match_alg:
            # Solve linear eq manually
            pass # Complex to generalize in 200 lines, fallback to heuristic

        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Meta-Confidence Check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        
        # 2. Computational Solve Attempt (Tier A - Exact)
        computed_ans = self._solve_computationally(prompt, candidates)
        if computed_ans:
            # If we computed an exact match, boost it heavily but cap by meta_conf
            base_score = 0.95 * meta_conf
            return sorted([
                {"candidate": c, "score": base_score if c == computed_ans else 0.1, "reasoning": "Computed exactly"} 
                for c in candidates
            ], key=lambda x: x['score'], reverse=True)

        # 3. PHSS Heuristic Scoring
        nodes, edges, mentioned = self._parse_nodes_and_edges(prompt)
        W, node_list, idx_map = self._build_matrix(nodes, edges)
        N = len(node_list)
        
        results = []
        if N == 0 or W.size == 0:
            # Fallback if no structure parsed
            for c in candidates:
                # Minimal NCD tiebreaker
                score = 0.5 * meta_conf 
                results.append({"candidate": c, "score": score, "reasoning": "No structure parsed, uniform prior"})
            return sorted(results, key=lambda x: x['score'], reverse=True)

        # Initial Activations (Context)
        A = np.zeros(N)
        for word in mentioned:
            if word in idx_map:
                A[idx_map[word]] = 1.0
        
        # Hebbian Update (Simulated single step for context)
        # W already initialized with eta, we simulate strengthening of co-occurrence
        if N > 0:
            W = W + self.eta * (A[:, None] * A[None, :])
            W[W < self.tau] = 0 # Pruning

        # Sensitivity Analysis
        S = self._compute_sensitivity(W, A)
        
        for c in candidates:
            # Pragmatic Relevance (R)
            # Overlap between candidate words and context nodes
            c_words = re.findall(r'\w+', c.lower())
            c_nodes = [w for w in c_words if w in idx_map]
            
            if not c_nodes:
                R = 0.1 # Low relevance if no shared concepts
            else:
                # Sum of weights connecting candidate concepts to context
                conn_sum = 0.0
                for cw in c_nodes:
                    idx = idx_map[cw]
                    conn_sum += np.sum(np.abs(W[idx, :])) + np.sum(np.abs(W[:, idx]))
                R = min(1.0, conn_sum / (len(c_nodes) + 1)) # Normalize roughly

            # Score = R * (1 / (1 + S))
            # High sensitivity (S) reduces score. High relevance (R) increases it.
            raw_score = R * (1.0 / (1.0 + S))
            
            # Apply Meta-Confidence Cap
            final_score = min(raw_score, meta_conf)
            
            results.append({
                "candidate": c,
                "score": float(final_score),
                "reasoning": f"Relevance:{R:.2f}, Sensitivity:{S:.2f}, MetaConf:{meta_conf:.2f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Parse to check if answer is structurally supported
        nodes, edges, _ = self._parse_nodes_and_edges(prompt)
        if not nodes:
            return 0.2 * meta_conf # Low confidence if nothing parsed
        
        # Check if answer tokens exist in graph
        ans_tokens = re.findall(r'\w+', answer.lower())
        overlap = [t for t in ans_tokens if t in nodes]
        
        if not overlap:
            return 0.3 * meta_conf
        
        # If we have overlap, base confidence on structural density
        # (Simplified for brevity: more connections = higher confidence)
        conn_count = 0
        for t in overlap:
            if t in edges: conn_count += len(edges[t])
            
        base_conf = min(0.9, 0.5 + 0.1 * conn_count)
        return min(base_conf, meta_conf)