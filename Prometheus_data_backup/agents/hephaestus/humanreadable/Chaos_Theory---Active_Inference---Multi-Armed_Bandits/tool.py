import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    BAICS Implementation: Bandit-Active-Inference-Chaos Scorer.
    
    Mechanism:
    1. Parsing: Extracts logical nodes (negations, comparatives, conditionals, causals, numbers)
       from prompt and candidates to form symbolic graphs.
    2. Belief State: Maintains a particle filter of possible logical interpretations.
    3. Scoring:
       - Risk: Weighted graph edit distance between candidate and belief particles.
       - Info Gain: Estimated reduction in entropy of the belief state.
       - Chaos: Lyapunov-like stability score via edge perturbation.
       - Bandit: UCB exploration bonus for uncertain candidates.
    4. Output: Combines Free Energy, Stability, and Exploration into a final score.
    """
    
    # Regex patterns for logical structures
    PATTERNS = {
        'NEG': [r'\bnot\b', r'\bno\b', r'\bnever\b'],
        'COMP': [r'\b(?:more|less|greater|fewer|higher|lower)\b', r'[><]=?', r'\b(?:greater\s+than|less\s+than)\b'],
        'COND': [r'\bif\b.*?\bthen\b', r'\bunless\b', r'\bprovided\s+that\b', r'\bif\b'],
        'CAUS': [r'\bbecause\b', r'\bdue\s+to\b', r'\bleads\s+to\b', r'\bresults\s+in\b'],
        'ORD': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b', r'\bprecedes\b'],
        'NUM': [r'\d+(?:\.\d+)?']
    }
    
    EDGE_TYPES = {'NEG': 0, 'COMP': 1, 'COND': 2, 'CAUS': 3, 'ORD': 4, 'NUM': 5}
    TYPE_COSTS = {0: 2.0, 1: 1.0, 2: 1.5, 3: 1.5, 4: 1.0, 5: 0.5} # Cost to flip/change type

    def __init__(self):
        self.particles = [] # List of (graph_edges, weight)
        self.arm_stats = {} # {candidate_hash: {'n': int, 'Q': float}}
        self.total_pulls = 0
        self._init_particles()

    def _init_particles(self):
        # Initialize K=5 random belief particles (empty or noise graphs)
        self.particles = [([], 1.0/5.0) for _ in range(5)]

    def _extract_graph(self, text: str) -> List[Tuple[int, int, int]]:
        """Parse text into a list of edges (node_id_u, node_id_v, type_id)."""
        text_lower = text.lower()
        nodes = []
        edges = []
        
        # Find all matches with positions
        matches = []
        for type_name, patterns in self.PATTERNS.items():
            for pat in patterns:
                for m in re.finditer(pat, text_lower):
                    matches.append((m.start(), m.end(), type_name, m.group()))
        
        # Sort by position to establish order
        matches.sort(key=lambda x: x[0])
        
        # Create nodes and sequential/dependency edges
        for i, (start, end, type_name, content) in enumerate(matches):
            node_id = i
            nodes.append((node_id, type_name))
            
            # Connect to previous node (Order/Sequence)
            if i > 0:
                edges.append((i-1, i, self.EDGE_TYPES['ORD']))
            
            # Specific logical connections (simplified heuristics)
            if type_name == 'NEG' and i > 0:
                # Negation likely modifies previous concept
                edges.append((i-1, i, self.EDGE_TYPES['NEG']))
            elif type_name in ['CAUS', 'COND']:
                # Causal/Conditional links forward if possible
                if i < len(matches) - 1:
                    edges.append((i, i+1, self.EDGE_TYPES[type_name]))

        return edges

    def _graph_edit_distance(self, g1: List, g2: List) -> float:
        """Compute weighted edit distance between two edge lists."""
        if not g1 and not g2: return 0.0
        if not g1: return len(g2) * 1.0
        if not g2: return len(g1) * 1.0
        
        # Simplified distance: Set difference with type costs
        # Represent edges as sets of tuples for O(1) lookup
        s1 = set(g1)
        s2 = set(g2)
        
        cost = 0.0
        # Penalties for missing/extra edges
        cost += len(s1 - s2) * 0.5
        cost += len(s2 - s1) * 0.5
        
        # Penalty for type mismatches (if nodes exist in both but types differ)
        # This is a rough approximation for speed
        nodes1 = {e[0] for e in g1} | {e[1] for e in g1}
        nodes2 = {e[0] for e in g2} | {e[1] for e in g2}
        
        if nodes1 and nodes2:
            # Check type consistency for shared node pairs
            common_nodes = nodes1 & nodes2
            if len(common_nodes) > 1:
                # Heuristic: if structure size differs significantly, penalize
                cost += abs(len(g1) - len(g2)) * 0.2
                
        return cost

    def _compute_entropy(self, weights: List[float]) -> float:
        if not weights: return 0.0
        total = sum(weights)
        if total == 0: return 0.0
        probs = [w/total for w in weights if w > 0]
        return -sum(p * math.log(p + 1e-10) for p in probs)

    def _perturb_graph(self, edges: List, p: float = 0.05) -> List:
        """Randomly toggle edges to test stability (Chaos term)."""
        if not edges: return edges
        new_edges = []
        for u, v, t in edges:
            if np.random.random() > p:
                new_edges.append((u, v, t))
            else:
                # Perturb type or remove
                if np.random.random() > 0.5:
                    new_t = (t + 1) % 6
                    new_edges.append((u, v, new_t))
        return new_edges

    def _calculate_lyapunov(self, edges: List) -> float:
        """Approximate Lyapunov exponent by averaging divergence of perturbed copies."""
        if not edges: return 0.0
        divergences = []
        base_dist = self._graph_edit_distance(edges, edges) # 0
        
        for _ in range(10): # M=10 iterations
            perturbed = self._perturb_graph(edges)
            dist = self._graph_edit_distance(edges, perturbed)
            # Logarithmic growth rate approximation
            if dist > 0:
                divergences.append(math.log(dist + 1.0))
        
        return np.mean(divergences) if divergences else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_graph = self._extract_graph(prompt)
        results = []
        
        # Update belief state based on prompt (simplified: prompt anchors the particles)
        # In a full system, this would be a Bayesian update. Here we bias particles toward prompt structure.
        prompt_edges_set = set(prompt_graph)
        new_particles = []
        for i in range(len(self.particles)):
            # Mix particle with prompt structure
            mixed_edges = list(prompt_edges_set) 
            # Add some noise to create particle diversity
            if i > 0:
                mixed_edges = self._perturb_graph(mixed_edges, p=0.2)
            new_particles.append((mixed_edges, 1.0/len(self.particles)))
        self.particles = new_particles

        scores = []
        weights = [p[1] for p in self.particles]
        initial_entropy = self._compute_entropy(weights)

        for cand in candidates:
            cand_hash = hash(cand)
            cand_graph = self._extract_graph(cand)
            
            # A. Risk (Expected Negative Log Likelihood via Edit Distance)
            risk = 0.0
            posterior_weights = []
            
            for p_graph, p_w in self.particles:
                dist = self._graph_edit_distance(p_graph, cand_graph)
                risk += p_w * dist
                # B. Expected Information Gain (Posterior calculation)
                # Likelihood ~ exp(-dist/sigma)
                likelihood = math.exp(-dist / 2.0) 
                posterior_weights.append(p_w * likelihood)
            
            # Normalize posterior
            sum_pw = sum(posterior_weights) + 1e-10
            posterior_weights = [w/sum_pw for w in posterior_weights]
            
            ig = initial_entropy - self._compute_entropy(posterior_weights)
            
            # C. Free Energy
            free_energy = risk - ig
            
            # D. Chaos (Stability)
            lambda_val = self._calculate_lyapunov(cand_graph)
            
            # E. Bandit Exploration Bonus
            if cand_hash not in self.arm_stats:
                self.arm_stats[cand_hash] = {'n': 0, 'Q': 0.0}
            
            stats = self.arm_stats[cand_hash]
            n_i = stats['n']
            Q_i = stats['Q']
            
            # UCB1 bonus
            if n_i == 0:
                ucb_bonus = float('inf')
            else:
                ucb_bonus = math.sqrt(math.log(self.total_pulls + 1) / (n_i + 1))
            
            # Final Score: -FreeEnergy + Exploration - ChaosPenalty
            # Eta (exploration) = 0.5, Zeta (chaos) = 0.2
            score = -free_energy + 0.5 * ucb_bonus - 0.2 * lambda_val
            
            # Update Bandit Stats
            stats['n'] += 1
            stats['Q'] += (score - stats['Q']) / stats['n']
            self.total_pulls += 1
            
            scores.append((cand, score, risk, ig, lambda_val))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        output = []
        for cand, score, risk, ig, chaos in scores:
            reason = f"Risk:{risk:.2f} InfoGain:{ig:.2f} Chaos:{chaos:.2f}"
            output.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the score of the single answer."""
        # Evaluate against itself to get intrinsic score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1 using a sigmoid-like function
        # Assuming scores are roughly centered around 0, with range +/- 5
        conf = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, conf))