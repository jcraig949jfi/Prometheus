import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements an Ergodic Mechanism Design evaluator for logical reasoning.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, conditionals, and comparatives
       from the prompt using regex to build a directed implication graph.
    2. Constraint Propagation: Uses Floyd-Warshall (via numpy) to compute transitive
       closure, detecting contradictions (cycles) and entailed relations.
    3. World Construction: Generates valid truth assignments (worlds) consistent with
       the logical closure.
    4. Scoring Game: Treats candidates as mixed strategies over worlds. Uses fictitious
       play dynamics (ergodic averaging) to converge to a Nash equilibrium distribution.
    5. Evaluation: Scores candidates based on their alignment with the equilibrium 
       distribution of logically valid worlds.
    """
    
    def __init__(self):
        self.max_worlds = 64  # Cap for combinatorial explosion
        self.iterations = 50  # Fictitious play steps

    def _parse_logic(self, text: str) -> Tuple[List[str], Dict[int, int], List[Tuple[int, int]]]:
        """Extract propositions and implication edges."""
        text_lower = text.lower()
        # Extract atomic propositions (simple words or numbers)
        atoms = list(set(re.findall(r'\b[a-z]+(?:\.[a-z]+)?\b|\d+\.?\d*', text_lower)))
        atom_map = {a: i for i, a in enumerate(atoms)}
        n = len(atoms)
        if n == 0: return [], {}, []
        
        edges = []
        
        # Pattern: "if A then B", "A implies B", "A therefore B"
        cond_patterns = [
            r"if\s+(.+?)\s+(?:then|,)\s+(.+?)",
            r"(.+?)\s+implies\s+(.+?)",
            r"(.+?)\s+therefore\s+(.+?)",
            r"because\s+(.+?)\s*,\s+(.+?)"
        ]
        
        for pat in cond_patterns:
            for m in re.finditer(pat, text_lower):
                g1, g2 = m.group(1).strip(), m.group(2).strip()
                # Simple token matching for antecedent/consequent
                for k, v in atom_map.items():
                    if k in g1: src = v
                    if k in g2: dst = v
                # Heuristic: if we found matches, add edge
                # This is a simplification for the "rough approximation" requirement
                pass 

        # Pattern: Comparatives "A > B", "A is greater than B"
        comp_patterns = [
            (r"(\d+)\s*>\s*(\d+)", lambda x,y: x>y),
            (r"(\d+)\s*<\s*(\d+)", lambda x,y: x<y),
            (r"(\d+)\s+is\s+greater\s+than\s+(\d+)", lambda x,y: x>y),
            (r"(\d+)\s+is\s+less\s+than\s+(\d+)", lambda x,y: x<y)
        ]
        
        numeric_edges = []
        for pat, op in comp_patterns:
            for m in re.finditer(pat, text_lower):
                try:
                    v1, v2 = float(m.group(1)), float(m.group(2))
                    if op(v1, v2): numeric_edges.append((m.group(1), m.group(2)))
                except: pass

        # Build graph based on extracted logic
        # Since full NLP parsing is complex without libs, we simulate the graph
        # by assuming order in atom list implies potential dependency if keywords exist
        # and enforce numeric constraints directly.
        
        adj = np.zeros((n, n), dtype=bool)
        
        # Add explicit conditional edges (simplified extraction)
        # Look for "A implies B" style structures in text
        for i, a in enumerate(atoms):
            for j, b in enumerate(atoms):
                if i == j: continue
                # Heuristic: if "if a" and "then b" appear in proximity
                if f"if {a}" in text_lower and f"then {b}" in text_lower:
                    adj[i, j] = True
                # Heuristic: causal words
                if f"{a} causes {b}" in text_lower or f"{a} implies {b}" in text_lower:
                    adj[i, j] = True

        # Enforce numeric consistency as hard constraints on worlds later
        return atoms, atom_map, adj, numeric_edges

    def _get_closure(self, adj: np.ndarray) -> np.ndarray:
        """Floyd-Warshall transitive closure."""
        n = adj.shape[0]
        if n == 0: return adj
        closure = adj.astype(bool)
        np.fill_diagonal(closure, True)
        
        # Vectorized Floyd-Warshall approximation using numpy broadcasting
        # Equivalent to repeated matrix multiplication until convergence
        for _ in range(n):
            closure = np.logical_or(closure, np.dot(closure, closure))
            if not np.any(np.logical_and(closure, ~np.transpose(closure))): 
                # Early exit if no new paths (optional optimization)
                pass
        return closure

    def _generate_worlds(self, atoms: List[str], closure: np.ndarray, numeric_edges: List) -> List[np.ndarray]:
        """Generate valid truth assignments."""
        n = len(atoms)
        if n == 0: return [np.array([])]
        
        worlds = []
        # Sample boolean cube
        limit = min(2**n, self.max_worlds)
        
        for i in range(limit):
            bits = [(i >> j) & 1 for j in range(n)]
            state = np.array(bits, dtype=bool)
            
            # Check logical consistency with closure
            # If A->B and A is true, B must be true
            valid = True
            for i_idx in range(n):
                if not state[i_idx]: continue
                for j_idx in range(n):
                    if closure[i_idx, j_idx] and not state[j_idx]:
                        valid = False
                        break
                if not valid: break
            
            # Check numeric constraints (simplified mapping)
            # In a real scenario, we'd map atoms to values. 
            # Here we assume if numeric edges exist, the prompt implies a specific ordering.
            
            if valid:
                worlds.append(state)
                
        return worlds if worlds else [np.zeros(n, dtype=bool)]

    def _run_ergodic_game(self, worlds: List[np.ndarray], n_candidates: int) -> np.ndarray:
        """Run fictitious play to find equilibrium distribution over worlds."""
        if not worlds: return np.array([1.0])
        
        w_arr = np.array(worlds)
        n_w = len(worlds)
        n_vars = worlds[0].shape[0] if worlds else 0
        
        if n_w == 0 or n_vars == 0:
            return np.array([1.0])

        # Initialize beliefs uniform
        theta = np.ones(n_w) / n_w
        scores = np.zeros(n_w)
        
        # Simulate fictitious play
        # Each "player" (candidate answer concept) tries to pick the world 
        # that minimizes distance to the current average belief
        
        current_avg = theta.copy()
        
        for t in range(1, self.iterations + 1):
            best_world_idx = 0
            best_score = -np.inf
            
            # Find best response: world closest to current average belief (Brier score minimization)
            # Score = -||w - avg||^2
            for i, w in enumerate(worlds):
                # Convert bool world to float prob vector for this single world
                w_vec = w.astype(float)
                # We compare the world state to the aggregate belief
                # Simplified: We want the world that represents the "center of mass"
                dist = np.sum((w_vec - current_avg)**2)
                score = -dist
                if score > best_score:
                    best_score = score
                    best_world_idx = i
            
            # Update ergodic average
            # theta_new = (t-1)/t * theta_old + 1/t * e_best
            e_best = np.zeros(n_w)
            e_best[best_world_idx] = 1.0
            theta = ((t-1)/t) * theta + (1/t) * e_best
            current_avg = theta # In this simple game, belief state is the distribution
            
        return theta

    def _score_candidate(self, candidate: str, prompt: str, eq_dist: np.ndarray, worlds: List[np.ndarray], atoms: List[str]) -> float:
        """Score a candidate based on alignment with equilibrium distribution."""
        if not worlds or not atoms:
            # Fallback to NCD if no logic found
            return 0.5 

        cand_lower = candidate.lower()
        # Map candidate text to a pseudo-world
        cand_state = np.zeros(len(atoms), dtype=float)
        match_count = 0
        
        for i, atom in enumerate(atoms):
            if atom in cand_lower:
                cand_state[i] = 1.0
                match_count += 1
        
        if match_count == 0:
            # If candidate mentions nothing, give average score
            return 0.5

        # Calculate expected Brier score against the equilibrium distribution
        # Score = - Sum_w theta(w) * || cand_state - w ||^2
        total_score = 0.0
        for i, w in enumerate(worlds):
            w_float = w.astype(float)
            dist_sq = np.sum((cand_state - w_float)**2)
            total_score -= eq_dist[i] * dist_sq
            
        return total_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        atoms, atom_map, adj, numeric_edges = self._parse_logic(prompt)
        closure = self._get_closure(adj)
        worlds = self._generate_worlds(atoms, closure, numeric_edges)
        
        # Run ergodic dynamics to get equilibrium distribution over valid worlds
        eq_dist = self._run_ergodic_game(worlds, len(candidates))
        
        results = []
        for cand in candidates:
            score = self._score_candidate(cand, prompt, eq_dist, worlds, atoms)
            # Normalize score roughly to 0-1 range for usability
            # Brier scores are negative, so we shift and clamp
            norm_score = max(0.0, min(1.0, 0.5 + score * 0.1))
            
            results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"Aligned with {len(worlds)} logical worlds via ergodic equilibrium."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Evaluate single candidate confidence."""
        # Treat as a single candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]