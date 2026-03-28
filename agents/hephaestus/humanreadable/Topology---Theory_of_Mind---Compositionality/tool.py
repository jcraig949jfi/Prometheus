import re
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Compositional Parsing, Theory of Mind (ToM) expansion,
    and Topological Scoring (Betti numbers) to evaluate logical consistency.
    
    Mechanism:
    1. Parsing: Converts text to a semantic graph of atomic propositions with logical edges.
    2. ToM Expansion: Generates belief variants by toggling modal nodes.
    3. Topology: Computes Betti numbers (beta0, beta1) on the implication graph.
    4. Scoring: Ranks candidates by minimizing distance to the prompt's topological signature
       and truth-vector consistency, using NCD only as a tiebreaker.
    """
    
    # Edge types: 0=NOT, 1=AND, 2=IMPLIES, 3=OR, 4=EQ, 5=LT, 6=GT, 7=NUM
    ETYPES = {'not':0, 'and':1, 'implies':2, 'or':3, 'eq':4, 'lt':5, 'gt':6, 'num':7}
    
    def __init__(self):
        self.ncd_cache = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[<>=]|[\d\.]+|[^\w\s]', text.lower())

    def _parse_to_graph(self, text: str) -> Tuple[List[Dict], np.ndarray, List[int]]:
        """Parses text into nodes (props) and edges (logical relations)."""
        tokens = self._tokenize(text)
        nodes = []
        edges = [] # (src, dst, type)
        
        # Simple state machine for parsing
        i = 0
        current_subj = None
        current_pred = None
        last_node_idx = -1
        
        while i < len(tokens):
            t = tokens[i]
            
            # Detect Negation
            if t in ['no', 'not', 'never', 'false']:
                if last_node_idx >= 0:
                    edges.append((last_node_idx, last_node_idx, 0)) # Self-loop negation
                i += 1
                continue
                
            # Detect Comparatives
            if t in ['<', '>', '=']:
                if last_node_idx >= 0 and i+1 < len(tokens):
                    # Look for number next
                    next_t = tokens[i+1]
                    if re.match(r'[\d\.]+', next_t):
                        val = float(next_t)
                        etype = 5 if t == '<' else (6 if t == '>' else 4)
                        # Create numeric node
                        n_idx = len(nodes)
                        nodes.append({'text': f"num_{val}", 'val': val, 'type': 'num'})
                        edges.append((last_node_idx, n_idx, etype))
                        last_node_idx = n_idx
                        i += 2
                        continue
            
            # Detect Conditionals (if... then)
            if t == 'if':
                # Mark next clause as antecedent
                pass 
            
            # Detect Belief Modals (ToM)
            is_modal = t in ['thinks', 'believes', 'wants', 'says']
            
            # Extract simple SVO or propositions
            if t not in ['if', 'then', 'and', 'or', 'but', 'because', 'so']:
                # Heuristic: treat sequence of words as a proposition until connector
                prop_words = [t]
                i += 1
                while i < len(tokens) and tokens[i] not in ['if', 'then', 'and', 'or', 'but', 'because', 'so', '.', ',']:
                    prop_words.append(tokens[i])
                    i += 1
                
                p_text = " ".join(prop_words)
                nodes.append({'text': p_text, 'type': 'belief' if is_modal else 'fact'})
                idx = len(nodes) - 1
                
                if last_node_idx >= 0:
                    # Default connective is AND or IMPLIES based on context
                    edges.append((last_node_idx, idx, 2)) # Default implies
                last_node_idx = idx
                continue
            
            i += 1

        if not nodes:
            nodes.append({'text': 'empty', 'type': 'fact'})
            
        # Build adjacency matrix for edges (implication/eq)
        n = len(nodes)
        adj = np.zeros((n, n), dtype=int)
        etype_arr = np.zeros((n, n), dtype=int) - 1
        
        for u, v, t in edges:
            if u < n and v < n:
                adj[u, v] = 1
                etype_arr[u, v] = t
                
        return nodes, adj, etype_arr

    def _compute_betti(self, adj: np.ndarray) -> Tuple[int, int]:
        """Computes beta0 (components) and beta1 (cycles) using numpy/union-find logic."""
        if adj.shape[0] == 0:
            return 1, 0
            
        n = adj.shape[0]
        # Symmetrize for connectivity (undirected view for components)
        undir = (adj + adj.T) > 0
        
        # Union-Find for beta0
        parent = list(range(n))
        def find(x):
            if parent[x] != x: parent[x] = find(parent[x])
            return parent[x]
        def union(x, y):
            px, py = find(x), find(y)
            if px != py: parent[px] = py
            
        for i in range(n):
            for j in range(n):
                if undir[i, j]: union(i, j)
        
        comps = len(set(find(i) for i in range(n)))
        beta0 = max(1, comps) # At least 1 component
        
        # Beta1 approx: E - V + C (Euler characteristic for graphs)
        # Count directed edges that are part of the main structure
        E = np.sum(adj > 0)
        V = n
        beta1 = max(0, int(E - V + beta0))
        
        return beta0, beta1

    def _propagate_truth(self, nodes: List[Dict], adj: np.ndarray) -> np.ndarray:
        """Simple fixpoint propagation of truth values."""
        n = len(nodes)
        if n == 0: return np.array([])
        
        # Initialize all as True (1), unless explicitly negated (handled in parsing ideally)
        t = np.ones(n, dtype=float)
        
        # Iterate for fixpoint
        for _ in range(n):
            changed = False
            for u in range(n):
                for v in range(n):
                    if adj[u, v] > 0:
                        # If u is true, v must be true (Modus Ponens approx)
                        if t[u] > 0.5 and t[v] < 0.5:
                            t[v] = 1.0
                            changed = True
                        # If u is false (0), no direct propagation in this simple model without NOT edges
            if not changed: break
        return t

    def _get_signature(self, text: str) -> Tuple[Tuple[int,int], np.ndarray]:
        nodes, adj, _ = self._parse_to_graph(text)
        if len(nodes) == 0:
            return (1, 0), np.array([])
        beta = self._compute_betti(adj)
        truth = self._propagate_truth(nodes, adj)
        return beta, truth

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1, len2 = len(s1_b), len(s2_b)
        if len1 == 0 or len2 == 0: return 1.0
        
        # Cache compression
        def comp(x):
            if x not in self.ncd_cache:
                self.ncd_cache[x] = len(zlib.compress(x))
            return self.ncd_cache[x]
            
        c1 = comp(s1_b)
        c2 = comp(s2_b)
        c12 = comp(s1_b + s2_b)
        
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_beta, p_truth = self._get_signature(prompt)
        
        # Pre-calculate prompt features for structural matching
        p_has_num = bool(re.search(r'\d+', prompt))
        p_has_if = 'if' in prompt.lower()
        p_has_not = any(w in prompt.lower() for w in ['not', 'no', 'never'])

        for cand in candidates:
            c_beta, c_truth = self._get_signature(cand)
            
            # 1. Topological Distance
            dist_beta = np.sqrt((p_beta[0]-c_beta[0])**2 + (p_beta[1]-c_beta[1])**2)
            
            # 2. Truth Vector Distance (Hamming-like)
            dist_truth = 0.0
            if len(p_truth) > 0 and len(c_truth) > 0:
                min_len = min(len(p_truth), len(c_truth))
                dist_truth = np.sum(np.abs(p_truth[:min_len] - c_truth[:min_len]))
            elif len(p_truth) != len(c_truth):
                dist_truth = 1.0 # Penalty for mismatched sizes
            
            # 3. Structural Feature Matching (High weight)
            struct_score = 0.0
            c_has_num = bool(re.search(r'\d+', cand))
            c_has_if = 'if' in cand.lower()
            c_has_not = any(w in cand.lower() for w in ['not', 'no', 'never'])
            
            if p_has_num and c_has_num: struct_score += 2.0
            if p_has_if and c_has_if: struct_score += 2.0
            if p_has_not and c_has_not: struct_score += 2.0
            # Penalize missing structural elements
            if p_has_num and not c_has_num: struct_score -= 3.0
            if p_has_if and not c_has_if: struct_score -= 3.0

            # 4. NCD Tiebreaker (only if structural signals are weak)
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score: Higher is better. 
            # We invert distances and add structural bonus.
            score = 10.0 - 2.0*dist_beta - 0.5*dist_truth + struct_score
            
            # If structural score is neutral, use NCD to break ties
            if abs(struct_score) < 1.0:
                score -= ncd_val 
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"TopoDist:{dist_beta:.2f}, TruthDist:{dist_truth:.2f}, Struct:{struct_score:.1f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        # Check strict structural constraints first
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        a_nums = re.findall(r'\d+\.?\d*', answer)
        
        # If prompt has numbers, answer must have numbers to be confident
        if p_nums and not a_nums:
            return 0.1
            
        # Check logical operators
        if 'if' in prompt.lower() and 'if' not in answer.lower():
            # Weak penalty, maybe implicit
            pass
            
        # Use the evaluate logic to get a raw score, then normalize
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        # Normalize heuristically: assume max possible score ~15, min ~-5
        conf = (raw_score + 5) / 20.0
        return max(0.0, min(1.0, conf))