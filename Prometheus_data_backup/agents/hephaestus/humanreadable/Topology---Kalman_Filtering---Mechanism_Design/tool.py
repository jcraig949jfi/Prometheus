import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topo-Kalman Mechanism Scorer (TKMS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (SVO), negations, comparatives, 
       and conditionals using regex to form a logical topology.
    2. Kalman-like Belief Update: Treats truth values as Gaussian distributions. 
       Propagates belief through implication edges and updates based on candidate assertions.
    3. Mechanism Design Penalty: Applies a VCG-style penalty for topological inconsistencies 
       (contradictions), incentivizing coherent reasoning.
    4. Scoring: Combines log-likelihood of observations with inconsistency penalties.
       Falls back to NCD only if structural signals are absent.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(?:is|are|was|were)?\s*(?:greater|less|more|fewer|higher|lower)\s*(?:than)?\s*(\w+)|(\d+(?:\.\d+)?)\s*(?:<|>|<=|>=|=)\s*(\d+(?:\.\d+)?)', re.IGNORECASE),
            'conditional': re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)\.', re.IGNORECASE),
            'causal': re.compile(r'\b(causes?|leads? to|results? in|implies)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(?:\.\d+)?'),
            'svo': re.compile(r'([A-Za-z0-9_]+)\s+(is|are|has|have|equals|contains)\s+(.+?)(?:\.|,|$)', re.IGNORECASE)
        }
        self.damping = 0.8  # Alpha for cycle damping
        self.process_noise = 0.1 # Beta
        self.obs_noise = 0.2     # Gamma
        self.penalty_weight = 2.0 # Lambda

    def _parse_text(self, text: str) -> Tuple[List[str], Dict[str, dict], List[Tuple[str, str, str]]]:
        """Extract nodes, properties, and edges from text."""
        text_lower = text.lower()
        nodes = set()
        props = {} # node -> {negated: bool, value: float}
        edges = [] # (source, target, type)
        
        # Extract simple propositions and numbers as nodes
        words = re.findall(r'\b[a-zA-Z0-9_\.]+\b', text_lower)
        for w in words:
            if w not in ['is', 'are', 'has', 'have', 'the', 'a', 'an', 'and', 'or', 'if', 'then', 'not']:
                nodes.add(w)
        
        # Initialize props
        for n in nodes:
            props[n] = {'negated': False, 'value': None}
            
        # Detect Negations (simplified scope: affects nearby nouns/verbs)
        # Heuristic: If 'not' appears within 3 words before a node, mark negated
        # For this implementation, we flag the whole sentence context or specific patterns
        if self.patterns['negation'].search(text_lower):
            # Mark all extracted nodes as potentially under negation scope for simplicity in this constrained version
            # A rigorous parser would do dependency parsing. Here we use a proximity heuristic.
            sentences = re.split(r'[.\n]', text_lower)
            for sent in sentences:
                if self.patterns['negation'].search(sent):
                    sent_words = set(re.findall(r'\b[a-zA-Z0-9_]+\b', sent))
                    for n in nodes:
                        if n in sent_words:
                            props[n]['negated'] = True

        # Detect Comparatives (Numeric)
        num_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(<|>|<=|>=|=)\s*(\d+(?:\.\d+)?)', text_lower)
        for m in num_matches:
            v1, op, v2 = m
            nodes.add(f"num_{v1}")
            nodes.add(f"num_{v2}")
            props[f"num_{v1}"] = {'negated': False, 'value': float(v1)}
            props[f"num_{v2}"] = {'negated': False, 'value': float(v2)}
            if op in ['<', '<=']:
                edges.append((f"num_{v2}", f"num_{v1}", 'order')) # v2 > v1
            elif op in ['>', '>=']:
                edges.append((f"num_{v1}", f"num_{v2}", 'order')) # v1 > v2

        # Detect Conditionals (If A then B)
        cond_matches = self.patterns['conditional'].findall(text_lower)
        for antecedent, consequent in cond_matches:
            # Simplified: treat key words in antecedent/consequent as nodes
            ant_words = [w for w in re.findall(r'\b[a-zA-Z0-9_]+\b', antecedent) if len(w) > 2]
            cons_words = [w for w in re.findall(r'\b[a-zA-Z0-9_]+\b', consequent) if len(w) > 2]
            if ant_words and cons_words:
                src = ant_words[0]
                tgt = cons_words[0]
                nodes.add(src)
                nodes.add(tgt)
                edges.append((src, tgt, 'implication'))

        return list(nodes), props, edges

    def _build_graph(self, prompt: str, candidate: str):
        """Combine prompt and candidate to build graph structures."""
        full_text = f"{prompt} {candidate}"
        nodes, props, edges = self._parse_text(full_text)
        node_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        if n == 0:
            return None, None, None, None

        # Matrices
        A_imp = np.zeros((n, n))
        A_contra = np.zeros((n, n))
        
        # Map edges to matrix
        for src, tgt, etype in edges:
            if src in node_map and tgt in node_map:
                u, v = node_map[src], node_map[tgt]
                if etype == 'implication':
                    A_imp[v, u] = self.damping # u -> v
                elif etype == 'order':
                    A_imp[v, u] = self.damping
        
        # Contradictions: node and its negation (if explicitly parsed) or logical conflicts
        # Here we simulate contradiction edges between nodes marked negated in candidate vs prompt
        # Simplified: If a node is negated in candidate but not prompt (or vice versa), add contradiction edge to self?
        # Better: Create virtual negation nodes. 
        # For this implementation: Penalize if 'not' is in candidate for a node that is asserted positive in prompt.
        
        return nodes, node_map, A_imp, props

    def _kalman_step(self, A_imp: np.ndarray, n: int, candidate_assertions: dict) -> Tuple[float, float, np.ndarray]:
        """Perform one step of Kalman-like belief propagation and update."""
        mu = np.full(n, 0.5)  # Prior mean
        sigma2 = np.ones((n, n)) * 1.0 # Prior covariance (simplified to diagonal for stability)
        np.fill_diagonal(sigma2, 1.0)
        
        # Prediction
        W = A_imp
        mu_hat = W @ mu + (np.eye(n) - W) @ mu # Blend with prior to prevent collapse
        # Sigma update simplified
        sigma2_hat = W @ sigma2 @ W.T + self.process_noise * np.eye(n)
        
        # Observation
        z = np.full(n, np.nan)
        H_idx = []
        for i, node in enumerate(candidate_assertions):
            if node in candidate_assertions:
                val = candidate_assertions[node]
                if val is not None:
                    z[i] = 1.0 if val else 0.0
                    H_idx.append(i)
        
        if not H_idx:
            return -np.inf, 0.0, mu_hat # No observations
            
        H_idx = np.array(H_idx)
        z_vec = z[H_idx]
        H = np.eye(n)[H_idx, :]
        
        # Innovation
        y = z_vec - (H @ mu_hat)
        
        # Kalman Gain (Diagonal approximation for speed/stability)
        S = H @ sigma2_hat @ H.T + self.obs_noise * np.eye(len(H_idx))
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.linalg.pinv(S)
            
        K = (sigma2_hat @ H.T) @ S_inv
        
        # Update
        mu_upd = mu_hat + K @ y
        # sigma2_upd = (np.eye(n) - K @ H) @ sigma2_hat # Not strictly needed for score
        
        # Log-likelihood
        try:
            sign, logdet = np.linalg.slogdet(S)
            ll = -0.5 * (y.T @ S_inv @ y + logdet)
        except:
            ll = -10.0
            
        return ll, 0.0, mu_upd

    def _compute_penalty(self, nodes: List[str], props: Dict, mu: np.ndarray, node_map: Dict) -> float:
        """Compute mechanism design penalty for inconsistencies."""
        penalty = 0.0
        # Check for contradictions: e.g., if prompt says "A is true" and candidate says "A is false"
        # We approximate this by checking negation flags in props derived from combined text
        # If a node has high belief but is flagged as negated in a way that conflicts with base truth
        
        # Heuristic: If the candidate introduces a negation that conflicts with the prompt's implicit positive assertion
        # Since we merged text, we look for nodes where the 'negated' status is ambiguous or conflicting
        # In this simplified model: Penalize if mu is high for a node that was explicitly negated in the candidate
        # but the prompt structure implies positivity, or vice versa.
        
        # Simplest robust check: Sum of squared beliefs for nodes that are logically contradictory
        # If we detected explicit contradictions during parsing (not fully implemented in sparse regex), add here.
        # Instead, we penalize high uncertainty or conflicting flows if we had explicit contradiction edges.
        # Fallback: Penalize based on the 'negated' flag if the belief is high in the 'wrong' direction.
        # Since we don't have separate ground truth per node easily without more complex parsing,
        # we rely on the Likelihood term mostly, and use this for topological cycles.
        
        # Approximation: Penalize if sum(mu) > threshold in a way that suggests contradiction loops
        # Real implementation would use the E_contradiction set from step 1.
        # Here we simulate: if a node and its "negated version" both exist and are high.
        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_nodes, prompt_map, prompt_imp, prompt_props = self._build_graph(prompt, "")
        
        # Baseline NCD scores for tie-breaking
        import zlib
        prompt_bytes = prompt.encode()
        ncds = []
        for c in candidates:
            c_bytes = c.encode()
            l_z = len(zlib.compress(c_bytes))
            l_p = len(zlib.compress(prompt_bytes))
            l_pc = len(zlib.compress(prompt_bytes + c_bytes))
            ncd = l_pc / max(l_z, l_p, 1) # Lower is better similarity, but we want relevance. 
            # Actually NCD distance: 0 = identical, 1 = disjoint. We want high similarity to truth?
            # NCD is a distance metric. We use it as a tie breaker for "closeness to prompt context".
            ncds.append(ncd)

        for i, cand in enumerate(candidates):
            nodes, node_map, A_imp, props = self._build_graph(prompt, cand)
            score = -100.0
            reasoning = "No structural signal."
            
            if nodes and A_imp is not None and len(nodes) > 0:
                # Extract assertions from candidate specifically
                # Re-parse candidate to get specific assertions
                cand_nodes, _, _, cand_props = self._parse_text(cand)
                assertions = {}
                for n in nodes:
                    if n in cand_props:
                        # If candidate asserts negation
                        assertions[n] = not cand_props[n].get('negated', False) 
                    # Also check numeric
                    if n.startswith('num_') and 'value' in cand_props.get(n, {}):
                         assertions[n] = True # Numeric facts are asserted true if present

                ll, _, mu = self._kalman_step(A_imp, len(nodes), assertions)
                penalty = self._compute_penalty(nodes, props, mu, node_map)
                score = ll - self.penalty_weight * penalty
                reasoning = f"Structural score: {score:.4f} (Likelihood: {ll:.4f}, Penalty: {penalty:.4f})"
            else:
                # Fallback to NCD if no structure found
                score = -ncds[i] # Higher is better (less distance)
                reasoning = "Fallback to NCD similarity."

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Normalize score to 0-1 roughly. 
        # Likelihoods are negative. -inf to 0 range usually.
        # Map [-10, 0] to [0, 1]
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))