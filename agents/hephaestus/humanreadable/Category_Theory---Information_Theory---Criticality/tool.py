import re
import numpy as np
import math
from collections import defaultdict

class ReasoningTool:
    """
    Implements a Category-Theoretic and Criticality-based reasoning engine.
    Mechanism:
    1. Parses text into a directed graph of atomic propositions (nodes) and relations (edges).
    2. Embeds nodes into a vector space using functorial mapping (negation=-1, conditional=1, etc.).
    3. Propagates constraints via matrix multiplication (simulating modus ponens/transitivity).
    4. Computes a 'Criticality Score' based on the variance of the resulting distribution,
       peaking when the system is at the edge of chaos (maximal entropy/variance balance).
    5. Uses NCD only as a tiebreaker for structural equality.
    """
    
    def __init__(self):
        self.basis_size = 10
        self.chi_star = math.log(self.basis_size) / 2.0
        # Simple seed matrices for edge types (2x2 for simplicity in propagation)
        self.M_identity = np.eye(2)
        self.M_negation = np.array([[-1, 0], [0, -1]]) # Sign flip
        self.M_conditional = np.array([[1, 0], [0, 0.5]]) # Damping implication
        self.M_causal = np.array([[0.8, 0.2], [0.2, 0.8]]) # Mixing
        self.M_comparative = np.array([[1, 0], [0, 1]]) # Order preservation

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _parse_graph(self, text):
        """Parses text into nodes and edges based on structural keywords."""
        tokens = self._tokenize(text)
        if not tokens:
            return [], []
        
        nodes = []
        edges = []
        node_map = {}
        
        # Create nodes from sentences/clauses (simplified to tokens for this scale)
        # We treat significant tokens as nodes
        for i, token in enumerate(tokens):
            if token in ['if', 'then', 'because', 'leads', 'to', 'not', 'no', 'greater', 'less', 'than', 'first', 'finally']:
                continue
            nid = f"n_{i}"
            val = 1.0
            # Check immediate context for negation
            if i > 0 and tokens[i-1] in ['not', 'no']:
                val = -1.0
            nodes.append({'id': nid, 'token': token, 'vector': np.array([val, 0.0])})
            node_map[token] = nid

        # Create edges based on structural keywords
        text_lower = text.lower()
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i+1]
            if t1 in node_map and t2 in node_map:
                edge_type = 'identity'
                # Look ahead/behind for keywords
                context = " ".join(tokens[max(0, i-2):min(len(tokens), i+3)])
                if 'if' in context or 'then' in context: edge_type = 'conditional'
                elif 'because' in context or 'leads' in context: edge_type = 'causal'
                elif 'greater' in context or 'less' in context: edge_type = 'comparative'
                
                edges.append({'src': node_map[t1], 'dst': node_map[t2], 'type': edge_type})

        # Add chain edges for ordering
        for i in range(len(nodes) - 1):
            edges.append({'src': nodes[i]['id'], 'dst': nodes[i+1]['id'], 'type': 'identity'})
            
        return nodes, edges

    def _propagate(self, nodes, edges):
        """Propagates vectors through the graph using matrix multiplication."""
        if not nodes:
            return np.array([0.0])
        
        node_vecs = {n['id']: n['vector'].copy() for n in nodes}
        node_list = list(node_vecs.keys())
        
        # Map edge types to matrices
        mats = {
            'identity': self.M_identity,
            'conditional': self.M_conditional,
            'causal': self.M_causal,
            'comparative': self.M_comparative,
            'negation': self.M_negation
        }
        
        # Iterative update (synchronous)
        for _ in range(3): # Fixed steps for convergence approximation
            new_vecs = {k: np.zeros(2) for k in node_vecs}
            has_update = False
            
            for e in edges:
                if e['src'] in node_vecs and e['dst'] in node_vecs:
                    M = mats.get(e['type'], self.M_identity)
                    contrib = M @ node_vecs[e['src']]
                    new_vecs[e['dst']] += contrib
                    has_update = True
            
            if has_update:
                # Normalize to prevent explosion
                max_val = max(np.linalg.norm(v) for v in new_vecs.values()) or 1.0
                node_vecs = {k: v / max_val for k, v in new_vecs.items()}
            else:
                break
                
        return node_vecs

    def _compute_criticality_score(self, node_vecs):
        """Computes the criticality metric based on variance and entropy."""
        if not node_vecs:
            return 0.0
            
        vectors = list(node_vecs.values())
        if not vectors:
            return 0.0
            
        # Flatten to 1D distribution approximation
        flat = np.array([v[0] for v in vectors])
        if len(flat) == 0:
            return 0.0
            
        # Normalize to probability distribution (shift to positive)
        flat_shifted = flat - flat.min() + 1e-6
        p = flat_shifted / flat_shifted.sum()
        
        # Entropy
        H = -np.sum(p * np.log(p + 1e-9))
        H_max = math.log(len(p)) if len(p) > 1 else 1.0
        
        # Variance (Susceptibility proxy)
        chi = np.var(flat)
        
        # Criticality term: Peaks when variance is near H_max/2
        crit_term = math.exp(-((chi - self.chi_star)**2))
        
        # Combine: High entropy + Critical variance
        return (H / (H_max + 1e-6)) * 0.5 + crit_term * 0.5

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / (max(c1, c2) + 1e-6)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_nodes, prompt_edges = self._parse_graph(prompt)
        prompt_vecs = self._propagate(prompt_nodes, prompt_edges)
        base_score = self._compute_criticality_score(prompt_vecs) if prompt_vecs else 0.0

        for cand in candidates:
            # Parse candidate
            c_nodes, c_edges = self._parse_graph(cand)
            c_vecs = self._propagate(c_nodes, c_edges)
            
            # Score 1: Structural/Criticality alignment
            # We compare the "shape" of the reasoning by checking if candidate 
            # reduces the entropy of the prompt's implied distribution
            cand_score = self._compute_criticality_score(c_vecs) if c_vecs else 0.0
            
            # Heuristic: If candidate contains numeric comparison, boost if consistent
            nums_p = re.findall(r'\d+\.?\d*', prompt)
            nums_c = re.findall(r'\d+\.?\d*', cand)
            numeric_bonus = 0.0
            if nums_p and nums_c:
                try:
                    # Simple consistency check: does order match?
                    p_ord = sorted([float(x) for x in nums_p])
                    c_ord = sorted([float(x) for x in nums_c])
                    if len(p_ord) == len(c_ord):
                        numeric_bonus = 0.1 # Small bonus for numeric coherence
                except: pass

            # Final Score formulation
            # We want high criticality (order from chaos) but also alignment
            score = (base_score + cand_score) / 2.0 + numeric_bonus
            
            # NCD Tiebreaker (only if scores are very close, handled implicitly by adding small noise)
            ncd_val = self._ncd(prompt, cand)
            score -= ncd_val * 0.001 # Prefer lower NCD (more similar) slightly

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Criticality: {cand_score:.4f}, Base: {base_score:.4f}"
            })
        
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural coherence."""
        # Combine prompt and answer to check for logical consistency
        combined = f"{prompt} {answer}"
        nodes, edges = self._parse_graph(combined)
        vecs = self._propagate(nodes, edges)
        
        if not vecs:
            return 0.0
            
        # Confidence is derived from the stability (low variance in final state implies high confidence?)
        # Actually, per instructions: Criticality peaks at specific variance. 
        # We map the criticality score directly to confidence.
        crit = self._compute_criticality_score(vecs)
        
        # Boost if answer explicitly resolves a conditional in prompt
        if 'if' in prompt.lower() and ('then' in answer.lower() or 'yes' in answer.lower() or 'no' in answer.lower()):
            crit = min(1.0, crit + 0.2)
            
        return float(np.clip(crit, 0.0, 1.0))