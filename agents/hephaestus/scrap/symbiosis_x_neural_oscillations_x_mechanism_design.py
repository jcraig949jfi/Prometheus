import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Oscillator Network with Mechanism Design Scoring.
    
    Mechanism:
    1. Parsing: Extracts entities, relations (negation, causal, conditional), and numeric values.
       Maps these to a bipartite graph structure (Entities vs Predicates).
    2. Dynamics: Uses Kuramoto-style oscillator dynamics where phase represents truth value.
       Positive coupling aligns phases (agreement); negative coupling opposes them (contradiction).
    3. Convergence: Iterates until phase stability or max steps.
    4. Scoring: Computes constraint energy (E). Applies a Clarke-Groves style penalty 
       based on the deviation from a 'ground' consistency model to incentivize truthfulness.
    """

    def __init__(self):
        self.max_iter = 500
        self.tol = 1e-4
        self.dt = 0.1
        self.k_base = 1.0

    def _parse_text(self, text: str) -> Tuple[List[str], List[Tuple[int, int, float]], List[float]]:
        """
        Extracts nodes and edges. 
        Returns: (nodes, edges, numeric_anchors)
        nodes: list of unique tokens
        edges: list of (idx_i, idx_j, weight)
        numeric_anchors: list of (node_idx, fixed_phase)
        """
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        if not tokens:
            return [], [], []
        
        # Map token to index (simplified to first occurrence for stability)
        token_to_idx = {}
        nodes = []
        for t in tokens:
            if t not in token_to_idx:
                token_to_idx[t] = len(nodes)
                nodes.append(t)
        
        edges = []
        numeric_anchors = []
        
        # Helper to add edge
        def add_edge(t1, t2, w):
            if t1 in token_to_idx and t2 in token_to_idx:
                edges.append((token_to_idx[t1], token_to_idx[t2], w))

        # 1. Negations (not, no) -> Opposition (-1.0)
        neg_words = {'not', 'no', 'never', 'none'}
        for i, t in enumerate(tokens):
            if t in neg_words:
                # Connect to next word with negative weight
                if i + 1 < len(tokens):
                    next_t = tokens[i+1]
                    if next_t in token_to_idx and t in token_to_idx:
                         # Self-loop or neighbor opposition logic simplified to neighbor
                         edges.append((token_to_idx[t], token_to_idx[next_t], -1.5))

        # 2. Comparatives (greater, less) -> Strong coupling
        comp_words = {'greater', 'less', 'more', 'fewer', 'higher', 'lower'}
        for t in comp_words:
            if t in token_to_idx:
                # Connect to surrounding context strongly
                idx = token_to_idx[t]
                # Connect to neighbors
                if idx > 0: edges.append((idx, token_to_idx[nodes[idx-1]], 1.0))
                if idx < len(nodes)-1: edges.append((idx, token_to_idx[nodes[idx+1]], 1.0))

        # 3. Conditionals/Causal (if, then, because, leads) -> Directed implication
        logic_words = {'if', 'then', 'because', 'leads', 'causes', 'therefore'}
        for t in logic_words:
            if t in token_to_idx:
                idx = token_to_idx[t]
                if idx < len(nodes)-1:
                    edges.append((idx, token_to_idx[nodes[idx+1]], 1.2))

        # 4. Numeric Anchors
        # Detect numbers and fix their phase based on magnitude (normalized 0-1)
        nums = re.findall(r'\d+\.?\d*', text)
        if nums:
            vals = [float(n) for n in nums]
            min_v, max_v = min(vals), max(vals)
            span = max_v - min_v if max_v != min_v else 1.0
            
            for n_str in nums:
                val = float(n_str)
                norm_val = (val - min_v) / span # 0 to 1
                phase = norm_val * 2 * np.pi 
                if n_str in token_to_idx:
                    numeric_anchors.append((token_to_idx[n_str], phase))
                else:
                    # If number wasn't tokenized as word, create dummy node (skip for simplicity)
                    pass

        # Default connectivity: sequential adjacency to ensure graph connectivity
        for i in range(len(nodes) - 1):
            edges.append((i, i+1, 0.5))

        return nodes, edges, numeric_anchors

    def _run_oscillators(self, n_nodes: int, edges: List[Tuple[int, int, float]], 
                         anchors: List[Tuple[int, float]]) -> np.ndarray:
        if n_nodes == 0:
            return np.array([])
        
        # Initialize phases randomly but deterministically based on index
        np.random.seed(42)
        theta = np.random.uniform(0, 2*np.pi, n_nodes)
        omega = np.zeros(n_nodes) # Natural frequency 0 for logic nodes
        
        # Apply anchors as fixed frequency drivers or strong pulls
        # For this implementation, we treat anchors as nodes with strong external forcing
        anchor_map = {idx: phase for idx, phase in anchors}
        
        # Build adjacency matrix W
        W = np.zeros((n_nodes, n_nodes))
        for i, j, w in edges:
            if i < n_nodes and j < n_nodes:
                W[i, j] = w
                W[j, i] = w # Symmetric for undirected graph logic
        
        # Iterative Kuramoto Update
        for _ in range(self.max_iter):
            theta_old = theta.copy()
            dtheta = omega.copy()
            
            for i in range(n_nodes):
                sum_sin = 0.0
                for j in range(n_nodes):
                    if W[i, j] != 0:
                        sum_sin += W[i, j] * np.sin(theta[j] - theta[i])
                dtheta[i] += sum_sin
            
            theta += self.dt * dtheta
            
            # Anchor enforcement:强力 pull anchors to their target phase
            for idx, target_phase in anchor_map.items():
                if idx < n_nodes:
                    # Strong coupling to target
                    theta[idx] = (1 - 0.5) * theta[idx] + 0.5 * target_phase

            theta = theta % (2 * np.pi)
            
            if np.max(np.abs(np.sin(theta - theta_old))) < self.tol:
                break
                
        return theta

    def _compute_energy(self, theta: np.ndarray, edges: List[Tuple[int, int, float]]) -> float:
        if len(theta) == 0:
            return 0.0
        energy = 0.0
        count = 0
        for i, j, w in edges:
            if i < len(theta) and j < len(theta):
                diff = theta[j] - theta[i]
                energy += w * (1 - np.cos(diff))
                count += 1
        return energy / (count + 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Parse prompt structure
        p_nodes, p_edges, p_anchors = self._parse_text(prompt)
        p_theta = self._run_oscillators(len(p_nodes), p_edges, p_anchors)
        p_energy = self._compute_energy(p_theta, p_edges)
        
        # Ground truth approximation: The prompt's own consistency is the "Gold"
        # In a real scenario, V_ground comes from external validation. 
        # Here we assume the prompt defines the valid constraint space.
        v_ground = -p_energy 

        for cand in candidates:
            full_text = f"{prompt} {cand}"
            c_nodes, c_edges, c_anchors = self._parse_text(full_text)
            
            # Run dynamics on candidate+prompt
            c_theta = self._run_oscillators(len(c_nodes), c_edges, c_anchors)
            c_energy = self._compute_energy(c_theta, c_edges)
            
            # Mechanism Design Score
            # S = -E + (V_ground - V_report)
            # V_report is approximated by how much the candidate disrupts the prompt's energy
            # We want low energy (high consistency). 
            # Score = Consistency Bonus - Disruption Penalty
            
            base_score = -c_energy
            
            # Penalty for deviating from prompt structure (simplified Clarke-Groves)
            # If candidate adds contradictions, energy increases, score drops.
            disruption = max(0, c_energy - p_energy) 
            score = base_score - disruption * 2.0
            
            # Fallback to NCD if structural signal is weak (no edges)
            if len(c_edges) == 0:
                import zlib
                data_prompt = prompt.encode()
                data_cand = cand.encode()
                comp = zlib.compress(data_prompt + data_cand)
                ncd = len(comp) / (len(zlib.compress(data_prompt)) + len(zlib.compress(data_cand)))
                score = -ncd # Lower NCD is better

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Oscillator convergence energy: {c_energy:.4f}. Mechanism penalty applied."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized score of the answer.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Normalize score to 0-1 range heuristically
        # Assuming reasonable scores fall between -5 and 5
        normalized = 1.0 / (1.0 + np.exp(-score)) 
        return float(np.clip(normalized, 0.0, 1.0))