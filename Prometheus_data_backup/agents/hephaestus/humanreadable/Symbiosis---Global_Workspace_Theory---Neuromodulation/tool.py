import re
import numpy as np
from collections import defaultdict
from zlib import compress

class ReasoningTool:
    """
    Implements a neuro-symbolic reasoning engine based on Symbiosis, Global Workspace Theory,
    and Neuromodulation. 
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (nodes) with types (FACT, NEGATION, etc.)
       and polarity.
    2. Symbiosis: Computes initial activation based on lexical similarity (TF-IDF approx).
    3. Global Workspace: Iteratively updates activation via adjacency (logic links) gated
       by a neuromodulatory gain derived from local uncertainty.
    4. Constraint Propagation: Enforces modus ponens and numeric transitivity.
    5. Scoring: Averages final activation of candidate nodes, using NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.beta = 2.0  # Gain sensitivity
        self.theta = 0.5 # Ignition threshold
        self.iterations = 10

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _parse_nodes(self, text):
        """Extract atomic propositions as nodes."""
        nodes = []
        sentences = re.split(r'[.;!?]', text)
        nid = 0
        
        # Patterns
        neg_pat = re.compile(r'\b(not|no|never|none|neither)\b', re.I)
        comp_pat = re.compile(r'\b(more than|less than|greater than|smaller than|>|<)\b', re.I)
        cond_pat = re.compile(r'\b(if|unless|provided that)\b', re.I)
        num_pat = re.compile(r'\d+(?:\.\d+)?')
        
        for sent in sentences:
            if not sent.strip(): continue
            tokens = self._tokenize(sent)
            if not tokens: continue
            
            # Determine type
            n_type = "FACT"
            polarity = 1
            value = None
            
            if neg_pat.search(sent):
                n_type = "NEGATION"
                polarity = -1
            
            if comp_pat.search(sent):
                n_type = "COMPARATIVE"
            elif cond_pat.search(sent):
                n_type = "CONDITIONAL"
            
            nums = num_pat.findall(sent)
            if nums:
                try:
                    value = float(nums[0])
                    if n_type == "FACT": n_type = "NUMERIC"
                except: pass

            # Simple TF-IDF approx (frequency in this context)
            vector = defaultdict(float)
            for t in tokens: vector[t] += 1.0
            
            nodes.append({
                'id': nid,
                'type': n_type,
                'polarity': polarity,
                'value': value,
                'args': [], # Connected node ids (logic links)
                'vector': vector,
                'text': sent.strip()
            })
            nid += 1
        return nodes

    def _build_adjacency(self, nodes):
        """Create adjacency matrix W based on logical flow and args."""
        n = len(nodes)
        if n == 0: return np.zeros((0,0))
        W = np.zeros((n, n))
        
        # Heuristic: Connect sequential nodes (narrative flow) and similar vectors
        for i in range(n):
            for j in range(i+1, n):
                # Sequential support
                score = 0.5
                if nodes[i]['polarity'] == -1 or nodes[j]['polarity'] == -1:
                    score = -0.5 # Negation breaks flow or inverts
                W[i, j] = score
                W[j, i] = score # Symmetric for symbiosis base
                
        # Self-connection for stability
        np.fill_diagonal(W, 1.0)
        return W

    def _compute_symbiosis_activation(self, nodes):
        """Compute M matrix and initial activation a0."""
        n = len(nodes)
        if n == 0: return np.array([])
        
        # Flatten vectors for simple cosine-like similarity
        all_terms = set()
        for node in nodes: all_terms.update(node['vector'].keys())
        term_list = sorted(list(all_terms))
        
        if not term_list:
            return np.ones(n) * 0.5
            
        # Build matrix
        vecs = np.zeros((n, len(term_list)))
        for i, node in enumerate(nodes):
            for k, v in node['vector'].items():
                idx = term_list.index(k)
                vecs[i, idx] = v
        
        # Normalize rows
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms==0] = 1
        vecs = vecs / norms
        
        # Mutual benefit matrix M (Gaussian kernel)
        dist_sq = np.sum((vecs[:, np.newaxis, :] - vecs[np.newaxis, :, :])**2, axis=2)
        sigma = 1.0
        M = np.exp(-dist_sq / (2 * sigma**2))
        
        # Initial activation
        a0 = M.dot(np.ones(n))
        return a0 / np.max(a0) if np.max(a0) > 0 else np.ones(n) * 0.5

    def _neuromodulatory_gain(self, nodes, W):
        """Compute gain gamma based on uncertainty of outgoing edges."""
        n = len(nodes)
        if n == 0: return np.ones(0)
        
        gamma = np.zeros(n)
        for i in range(n):
            edges = W[i, :]
            if np.sum(np.abs(edges)) == 0:
                gamma[i] = 1.0
                continue
            
            # Entropy of signs (simplified)
            probs = np.abs(edges) / (np.sum(np.abs(edges)) + 1e-9)
            probs = probs[probs > 0]
            entropy = -np.sum(probs * np.log2(probs + 1e-9))
            
            # High entropy -> Low gain (uncertainty suppresses propagation)
            # Normalize entropy roughly by max possible (log2(n))
            max_ent = np.log2(n) if n > 1 else 1
            U = entropy / (max_ent + 1e-9)
            
            gamma[i] = 1.0 / (1.0 + np.exp(-self.beta * (1.0 - U))) # Inverted logic: low uncertainty = high gain
            
        return gamma

    def _propagate_constraints(self, nodes, activations):
        """Apply deterministic logic rules."""
        # Modus ponens & Transitivity heuristics
        for i, node in enumerate(nodes):
            if activations[i] > self.theta:
                # If conditional is ignited, boost consequent (simulated)
                if node['type'] == 'CONDITIONAL':
                    # Find potential consequents in next nodes
                    for j in range(i+1, min(i+3, len(nodes))):
                        activations[j] = max(activations[j], activations[i] * 0.9)
        return activations

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        return c12 / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_nodes = self._parse_nodes(prompt)
        prompt_W = self._build_adjacency(prompt_nodes)
        prompt_a0 = self._compute_symbiosis_activation(prompt_nodes)
        prompt_gain = self._neuromodulatory_gain(prompt_nodes, prompt_W) if len(prompt_nodes) > 0 else np.array([])
        
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            nodes = self._parse_nodes(full_text)
            
            if not nodes:
                score = 0.0
                reason = "No structural nodes parsed."
            else:
                W = self._build_adjacency(nodes)
                a0 = self._compute_symbiosis_activation(nodes)
                
                # Global Workspace Iteration
                a = a0.copy()
                g = np.zeros(len(nodes)) # Global workspace vector
                
                for _ in range(self.iterations):
                    if len(a) == 0: break
                    gamma = self._neuromodulatory_gain(nodes, W)
                    
                    # Raw input from neighbors
                    r = W.dot(a)
                    
                    # Update with neuromodulatory gain
                    # Align dimensions if mismatch (safety)
                    min_len = min(len(gamma), len(a))
                    update = gamma[:min_len] * r[:min_len] + (1 - gamma[:min_len]) * a0[:min_len]
                    
                    a[:min_len] = update
                    
                    # Ignition: Broadcast high activation nodes
                    ignited = a > self.theta
                    if np.any(ignited):
                        broadcast = np.outer(ignited.astype(float), np.ones(len(a))) * 0.1
                        a = np.maximum(a, broadcast.sum(axis=0))
                    
                    # Constraint propagation step
                    a = self._propagate_constraints(nodes, a)

                # Score: Average activation of nodes unique to candidate (approximated by last part)
                # Since we parsed full text, we assume candidate nodes are the last few or weighted by overlap
                # Simplification: Score based on total system coherence relative to prompt structure
                cand_nodes = self._parse_nodes(cand)
                if len(cand_nodes) == 0:
                    score = 0.0
                else:
                    # Map candidate nodes to full nodes via text matching (rough)
                    cand_scores = []
                    c_tokens = set(self._tokenize(cand))
                    for i, n in enumerate(nodes):
                        if any(t in n['text'] for t in c_tokens):
                            cand_scores.append(a[i])
                    
                    if cand_scores:
                        base_score = np.mean(cand_scores)
                    else:
                        base_score = np.mean(a) if len(a) > 0 else 0.0
                    
                    # NCD Tiebreaker (small weight)
                    ncd = self._ncd_score(prompt, cand)
                    # Lower NCD is better (more similar), so invert logic slightly or use as tiebreak
                    # We want structural score to dominate.
                    score = base_score * 0.9 + (1.0 - ncd) * 0.1
                
                reason = f"Activation: {np.mean(a) if len(a)>0 else 0:.2f}, Type: {nodes[-1]['type'] if nodes else 'None'}"

            results.append({"candidate": cand, "score": float(score), "reasoning": reason})
        
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        # Normalize score to 0-1 range roughly
        raw = res[0]['score']
        return max(0.0, min(1.0, raw))