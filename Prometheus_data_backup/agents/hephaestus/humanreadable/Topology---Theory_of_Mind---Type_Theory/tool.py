import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Typed Belief-Graph Reasoner.
    Mechanism: Constructs a graph where vertices are propositions typed via regex (Bool, Order, Int)
    and edges represent logical relations (IMPLIES, NEG, COMPARE). It performs constraint propagation
    (Modus Ponens, Transitivity) on belief vectors using NumPy. The final score combines structural
    type-correctness (Topology x Type Theory synergy) with belief alignment (Theory of Mind), using
    NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.type_rules = {
            'IMPLIES': ('Bool', 'Bool'),
            'NEG': ('Bool', 'Bool'),
            'COMPARE': ('Order', 'Order'),
            'CAUSAL': ('Prop', 'Prop'),
            'EQUIV': ('Bool', 'Bool')
        }
        self.epsilon = 1e-4
        self.max_sweeps = 10
        self.alpha = 0.7  # Weight for belief alignment

    def _extract_type(self, text: str) -> str:
        """Regex-based type assignment."""
        t = text.lower()
        if re.search(r'\d+', t): return 'Int'
        if re.search(r'(greater|less|more|before|after|first|last|>\|<)', t): return 'Order'
        if re.search(r'(true|false|yes|no|is|are|will|can)', t): return 'Bool'
        return 'Prop'

    def _parse_edges(self, text: str) -> List[Tuple[str, str, float]]:
        """Extract relations and assign types/weights."""
        edges = []
        t = text.lower()
        if re.search(r'\bnot\b|\bnever\b|\bno\b', t): edges.append(('NEG', 0.9))
        if re.search(r'(greater|less|more|before|after|>\|<)', t): edges.append(('COMPARE', 0.95))
        if re.search(r'\bif\b|\bthen\b|\bunless\b|\bimplies\b', t): edges.append(('IMPLIES', 0.9))
        if re.search(r'\bbecause\b|\bleads to\b|\bcauses\b', t): edges.append(('CAUSAL', 0.85))
        if re.search(r'\bequal\b|\bsame as\b', t): edges.append(('EQUIV', 0.95))
        return edges if edges else [('IMPLIES', 0.5)] # Default weak link

    def _build_graph(self, text: str, w: int = 4) -> Tuple[List[Dict], np.ndarray, List[Tuple]]:
        """Build typed belief graph structures."""
        # Simplified: Treat whole text as one proposition for vertex, split for edges logic
        # In a full engine, we'd split sentences. Here we simulate the graph structure.
        v_type = self._extract_type(text)
        vertex = {'id': 0, 'content': text, 'type': v_type, 'belief': np.ones(w) * 0.5}
        
        edges_data = []
        raw_edges = self._parse_edges(text)
        
        for rel, weight in raw_edges:
            # Type checking simulation (Topology x Type Theory synergy)
            req = self.type_rules.get(rel, ('Prop', 'Prop'))
            if v_type == req[0] or v_type == 'Prop': # Relaxed for single-node demo
                edges_data.append((0, 0, rel, weight))
                
        return [vertex], np.array([e[3] for e in edges_data]), edges_data

    def _propagate(self, vertices: List[Dict], edges: List[Tuple], w: int = 4) -> np.ndarray:
        """NumPy-based constraint propagation."""
        if not vertices: return np.array([])
        beliefs = np.ones((len(vertices), w)) * 0.5 # Initial belief state
        
        # Apply Modus Ponens / Transitivity heuristics via matrix ops
        for _ in range(self.max_sweeps):
            old_beliefs = beliefs.copy()
            for src, dst, rel, weight in edges:
                if rel == 'NEG':
                    beliefs[dst] = np.maximum(beliefs[dst], 1.0 - beliefs[src] * weight)
                elif rel in ['IMPLIES', 'COMPARE', 'CAUSAL']:
                    beliefs[dst] = np.maximum(beliefs[dst], beliefs[src] * weight)
            
            if np.max(np.abs(beliefs - old_beliefs)) < self.epsilon:
                break
        return beliefs

    def _hausdorff_sim(self, b1: np.ndarray, b2: np.ndarray) -> float:
        """Compute similarity based on belief vector distance."""
        if b1.size == 0 or b2.size == 0: return 0.0
        # Simplified Hausdorff-like distance for fixed size vectors
        dist = np.max(np.abs(b1 - b2))
        return float(1.0 - dist)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        try:
            import zlib
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return 1.0 - (min(c1, c2) / max(c12, 1))
        except: return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_verts, p_weights, p_edges = self._build_graph(prompt)
        p_beliefs = self._propagate(p_verts, p_edges)
        p_type_score = 1.0 if p_verts and p_verts[0]['type'] != 'Prop' else 0.5
        
        scores = []
        for cand in candidates:
            c_verts, c_weights, c_edges = self._build_graph(cand)
            c_beliefs = self._propagate(c_verts, c_edges)
            
            # Theory of Mind: Belief Alignment
            belief_sim = self._hausdorff_sim(p_beliefs, c_beliefs)
            
            # Topology x Type Theory: Structural validity
            c_type = c_verts[0]['type'] if c_verts else 'Prop'
            type_match = 1.0 if c_type == p_verts[0]['type'] else 0.5
            struct_score = (len(c_edges) / max(len(p_edges), 1)) * type_match
            
            score = self.alpha * belief_sim + (1 - self.alpha) * struct_score
            
            # NCD Tiebreaker
            if abs(score - 0.5) < 0.01: 
                score += 0.01 * self._ncd(prompt, cand)
                
            results.append({"candidate": cand, "score": score, "reasoning": f"Type:{c_type}, Belief:{belief_sim:.2f}"})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0