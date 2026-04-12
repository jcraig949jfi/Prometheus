import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A computational reasoning tool integrating Category Theory (functorial graph matching),
    Metacognition (belief propagation on confidence), and Causal Inference (intervention detection).
    
    Mechanism:
    1. Parses text into a typed directed hypergraph (Nodes=entities, Edges=relations).
    2. Computes a structural similarity score via Frobenius norm of adjacency matrices (Category Theory).
    3. Adjusts scores based on modal verbs and belief propagation (Metacognition).
    4. Penalizes causal inconsistencies in intervention scenarios (Causal Inference).
    5. Uses NCD only as a tie-breaker when structural signals are weak.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|causes|due to|do\(|set)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'modal_strong': re.compile(r'\b(must|will|definitely|certainly)\b', re.I),
            'modal_weak': re.compile(r'\b(maybe|could|might|possibly)\b', re.I)
        }
        self.stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'it', 'that', 'this'}

    def _extract_nodes(self, text: str) -> List[str]:
        """Extract propositional entities (simplified to nouns/numbers for this constraint)."""
        # Simple tokenization avoiding stopwords
        tokens = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
        nodes = [t for t in tokens if t not in self.stopwords and len(t) > 1]
        # Deduplicate while preserving order
        seen = set()
        unique_nodes = []
        for n in nodes:
            if n not in seen:
                seen.add(n)
                unique_nodes.append(n)
        return unique_nodes

    def _build_graph(self, text: str) -> Tuple[List[str], Dict[str, np.ndarray]]:
        """Build typed adjacency matrices for the text."""
        nodes = self._extract_nodes(text)
        n = len(nodes)
        if n == 0:
            return [], {}
        
        node_map = {node: i for i, node in enumerate(nodes)}
        # Edge types: causal, conditional, comparative, negation, equivalence
        edge_types = ['causal', 'conditional', 'comparative', 'negation', 'equivalence']
        matrices = {k: np.zeros((n, n), dtype=int) for k in edge_types}
        
        text_lower = text.lower()
        
        # 1. Negation edges (self-loops or immediate next word)
        for m in self.patterns['negation'].finditer(text_lower):
            # Find closest node
            pos = m.start()
            # Simple heuristic: negate the nearest node in the sentence window
            for node, idx in node_map.items():
                if node in text_lower[max(0, pos-20):pos+20]:
                    matrices['negation'][idx, idx] = 1
        
        # 2. Conditional edges (if X then Y)
        if self.patterns['conditional'].search(text_lower):
            # Crude heuristic: connect first mentioned node to last mentioned node
            if len(nodes) >= 2:
                src = node_map[nodes[0]]
                tgt = node_map[nodes[-1]]
                matrices['conditional'][src, tgt] = 1

        # 3. Comparative edges
        if self.patterns['comparative'].search(text_lower):
            nums = self.patterns['numeric'].findall(text)
            if len(nums) >= 2:
                # Connect nodes associated with numbers? 
                # Fallback: connect first and last nodes as a comparative relation
                if len(nodes) >= 2:
                    matrices['comparative'][node_map[nodes[0]], node_map[nodes[-1]]] = 1

        # 4. Causal edges
        if self.patterns['causal'].search(text_lower):
            if len(nodes) >= 2:
                matrices['causal'][node_map[nodes[0]], node_map[nodes[-1]]] = 1
                
        return nodes, matrices

    def _compute_metacognition(self, text: str, nodes: List[str]) -> float:
        """Compute confidence based on modals and belief propagation."""
        if not nodes:
            return 0.5
            
        n = len(nodes)
        c = np.full(n, 0.5)
        
        # Initial confidence from modals
        text_lower = text.lower()
        if self.patterns['modal_strong'].search(text_lower):
            c += 0.2
        if self.patterns['modal_weak'].search(text_lower):
            c -= 0.2
            
        # Numeric precision boost
        nums = self.patterns['numeric'].findall(text)
        if len(nums) > 0:
            c += 0.1
            
        # Belief propagation (simplified: 2 rounds)
        # Construct adjacency based on co-occurrence in text (window)
        adj = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    # If nodes appear close, they influence each other
                    if f"{nodes[i]}" in text and f"{nodes[j]}" in text:
                        adj[i, j] = 1.0 / n # weak uniform coupling for simplicity
        
        if np.sum(adj) > 0:
            # Normalize rows
            row_sums = adj.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            adj_norm = adj / row_sums
            
            for _ in range(2):
                c = 1.0 / (1.0 + np.exp(-np.dot(adj_norm, c))) # Logistic squash
                
        return float(np.mean(c))

    def _causal_penalty(self, prompt: str, answer: str) -> float:
        """Detect causal claims and check consistency."""
        # If no causal language, penalty is 0
        if not (self.patterns['causal'].search(prompt.lower()) or self.patterns['causal'].search(answer.lower())):
            return 0.0
            
        # Heuristic: If prompt asks for "do(X)" or intervention, and answer lacks numeric change or causal keyword
        has_intervention = 'do(' in prompt.lower() or 'set' in prompt.lower()
        answer_has_causal = any(k in answer.lower() for k in ['because', 'leads', 'causes', 'due'])
        
        if has_intervention and not answer_has_causal:
            return 0.5 # Penalty for missing causal explanation in intervention query
            
        return 0.0

    def _structural_distance(self, nodes_ref: List[str], mats_ref: Dict, nodes_ans: List[str], mats_ans: Dict) -> float:
        """Compute Frobenius norm distance between aligned graphs."""
        if not nodes_ref or not nodes_ans:
            return 1.0 if (nodes_ref or nodes_ans) else 0.0
            
        # Map answer nodes to reference nodes (Functor F)
        # Exact string match only for this implementation
        ref_indices = {n: i for i, n in enumerate(nodes_ref)}
        ans_indices = {n: i for i, n in enumerate(nodes_ans)}
        
        # Create mapping: ans_idx -> ref_idx
        mapping = {}
        for ans_node, ans_idx in ans_indices.items():
            if ans_node in ref_indices:
                mapping[ans_idx] = ref_indices[ans_node]
        
        total_dist = 0.0
        count = 0
        
        for k in mats_ref:
            A_ref = mats_ref[k]
            A_ans = mats_ans.get(k, np.zeros_like(A_ref))
            
            # Align A_ans to A_ref shape via mapping
            # Since sizes differ, we project to the intersection of nodes
            common_nodes = set(nodes_ref) & set(nodes_ans)
            if len(common_nodes) < 2:
                # If very little overlap, high distance
                total_dist += 1.0
                count += 1
                continue
                
            ref_idxs = [ref_indices[n] for n in common_nodes]
            ans_idxs = [ans_indices[n] for n in common_nodes]
            
            # Extract submatrices
            sub_ref = A_ref[np.ix_(ref_idxs, ref_idxs)]
            sub_ans = A_ans[np.ix_(ans_idxs, ans_idxs)]
            
            dist = np.linalg.norm(sub_ref - sub_ans, 'fro')
            total_dist += dist
            count += 1
            
        return total_dist / (count + 1e-6)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        ref_nodes, ref_mats = self._build_graph(prompt)
        
        # If prompt yields no structure, rely on NCD
        use_ncd_primary = len(ref_nodes) < 2
        
        for cand in candidates:
            ans_nodes, ans_mats = self._build_graph(cand)
            
            if use_ncd_primary:
                # Fallback to NCD if structural parsing fails
                score = 1.0 - self._ncd(prompt, cand)
                reason = "NCD baseline (low structural signal)"
            else:
                # Primary structural scoring
                struct_dist = self._structural_distance(ref_nodes, ref_mats, ans_nodes, ans_mats)
                meta_conf = self._compute_metacognition(cand, ans_nodes)
                causal_pen = self._causal_penalty(prompt, cand)
                
                # Formula: exp(-dist) * meta * (1 - causal_pen)
                score = np.exp(-struct_dist) * meta_conf * (1.0 - causal_pen)
                reason = f"Structural dist: {struct_dist:.2f}, Meta: {meta_conf:.2f}, Causal pen: {causal_pen:.2f}"
                
                # Tie-breaking with NCD if scores are very close to baseline
                if score < 0.1:
                    ncd_score = 1.0 - self._ncd(prompt, cand)
                    if ncd_score > score:
                        score = 0.5 * score + 0.5 * ncd_score # Blend
                        reason += " (blended with NCD)"

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0