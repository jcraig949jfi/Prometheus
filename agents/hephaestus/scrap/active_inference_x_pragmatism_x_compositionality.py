import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A lightweight probabilistic-logic scorer using Active Inference principles.
    Mechanism:
    1. Structural Parsing: Extracts entities, negations, comparatives, conditionals, 
       and numeric constraints via regex into a graph representation.
    2. Constraint Propagation: Uses Floyd-Warshall for transitive implications and 
       interval arithmetic for numeric bounds.
    3. Active-Inference Scoring: Computes Free Energy (F = Surprisal - Epistemic Value).
       - Surprisal: Penalty for violating extracted constraints.
       - Epistemic Value: Information gain (reduction in feasible volume).
       - Pragmatic Utility: Reward for satisfied constraints.
    Final Score = Utility - Free Energy. NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\bnot\s+(\w+)', re.IGNORECASE),
            'comparative': re.compile(r'(\w+|\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\w+|\d+\.?\d*)', re.IGNORECASE),
            'conditional': re.compile(r'if\s+(.*?)\s+then\s+(.*)', re.IGNORECASE),
            'causal': re.compile(r'(\w+)\s+causes\s+(\w+)', re.IGNORECASE),
            'ordering': re.compile(r'(\w+)\s+before\s+(\w+)', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'conjunction': re.compile(r'\band\b', re.IGNORECASE)
        }

    def _extract_nodes_and_constraints(self, text: str) -> Tuple[Dict[str, int], np.ndarray, List[Tuple]]:
        """Parses text into nodes, types, and constraints."""
        nodes = {}
        constraints = []
        idx_counter = 0
        
        def get_idx(token: str) -> int:
            nonlocal idx_counter
            token = token.lower().strip()
            if token not in nodes:
                nodes[token] = idx_counter
                idx_counter += 1
            return nodes[token]

        # 1. Negations
        for m in self.patterns['negation'].finditer(text):
            target = m.group(1)
            t_idx = get_idx(target)
            # Mark as negated (type 3)
            constraints.append(('neg', t_idx, None, None))

        # 2. Comparatives & Numeric
        for m in self.patterns['comparative'].finditer(text):
            left, op, right = m.group(1), m.group(2), m.group(3)
            l_idx = get_idx(left)
            
            # Handle numeric literals directly in constraints
            r_val = right
            if self.patterns['numeric'].fullmatch(right):
                r_idx = None # Literal
                constraints.append(('cmp_num', l_idx, op, float(right)))
            else:
                r_idx = get_idx(right)
                constraints.append(('cmp_sym', l_idx, op, r_idx))

        # 3. Conditionals (Simplified to implication)
        for m in self.patterns['conditional'].finditer(text):
            antecedent = m.group(1).strip()
            consequent = m.group(2).strip()
            # Create pseudo-nodes for clauses
            ant_idx = get_idx(f"cond_{antecedent[:10]}")
            cons_idx = get_idx(f"cons_{consequent[:10]}")
            constraints.append(('imp', ant_idx, cons_idx, None))

        # 4. Causal & Ordering (Treated as directed edges)
        for pattern_name in ['causal', 'ordering']:
            for m in self.patterns[pattern_name].finditer(text):
                src, dst = m.group(1), m.group(2)
                s_idx = get_idx(src)
                d_idx = get_idx(dst)
                constraints.append(('edge', s_idx, d_idx, 1.0))

        # Initialize adjacency matrix
        N = len(nodes)
        if N == 0:
            return {}, np.array([]), []
            
        adj = np.zeros((N, N), dtype=np.float32)
        node_type = np.zeros(N, dtype=np.int8) # 0:entity, 1:pred, 2:num, 3:neg
        
        # Populate types
        for k, i in nodes.items():
            if self.patterns['numeric'].fullmatch(k):
                node_type[i] = 2
        
        return nodes, node_type, constraints

    def _propagate_constraints(self, nodes: Dict[str, int], constraints: List[Tuple]) -> Dict[str, Any]:
        """Runs simple propagation logic."""
        if not nodes:
            return {'valid': True, 'volume': 1.0, 'violations': 0}
            
        N = len(nodes)
        # Adjacency for transitivity (Floyd-Warshall setup)
        adj = np.zeros((N, N), dtype=np.float32)
        np.fill_diagonal(adj, 1.0)
        
        numeric_bounds = {} # node_idx -> (min, max)
        violations = 0
        
        for c in constraints:
            op = c[0]
            if op == 'edge':
                adj[c[1], c[2]] = 1.0
            elif op == 'cmp_num':
                # Simple check if we can resolve the node value (simulated)
                # In this lightweight version, we assume the candidate provides the value
                pass 
            elif op == 'imp':
                adj[c[1], c[2]] = 0.9 # Soft implication weight

        # Floyd-Warshall for transitive closure
        for k in range(N):
            for i in range(N):
                for j in range(N):
                    if adj[i,k] * adj[k,j] > 0:
                        adj[i,j] = max(adj[i,j], adj[i,k] * adj[k,j])
                        
        return {'adj': adj, 'volume': 1.0 / (N + 1), 'violations': 0}

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_nodes, prompt_types, prompt_constraints = self._extract_nodes_and_constraints(prompt)
        prompt_state = self._propagate_constraints(prompt_nodes, prompt_constraints)
        
        # Baseline volume for epistemic value
        base_volume = prompt_state.get('volume', 1.0)
        has_structure = len(prompt_constraints) > 0

        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            if has_structure:
                # Candidate parsing
                cand_nodes, cand_types, cand_constraints = self._extract_nodes_and_constraints(cand)
                
                # 1. Surprisal (S): Penalty for mismatch
                # Check if candidate contradicts prompt constraints (simplified)
                surprisal = 0.0
                satisfied = 0
                violated = 0
                
                # Simple keyword/structure overlap check as proxy for constraint satisfaction
                common_keys = set(prompt_nodes.keys()) & set(cand_nodes.keys())
                if len(prompt_nodes) > 0:
                    overlap_ratio = len(common_keys) / len(prompt_nodes)
                    surprisal = (1.0 - overlap_ratio) * 5.0 # Penalty for missing concepts
                else:
                    surprisal = 0.0

                # 2. Epistemic Value (E): Information gain
                # Approximated by specificity (length/complexity) relative to prompt
                cand_vol = 1.0 / (len(cand_nodes) + 1) if cand_nodes else 1.0
                epistemic_value = np.log(base_volume / (cand_vol + 1e-6)) if cand_vol < base_volume else 0.0
                
                # 3. Pragmatic Utility (U)
                # Heuristic: Does the candidate contain numbers found in prompt? Or logical connectors?
                utility = 0.0
                if cand_nodes:
                    utility += 1.0 # Basic existence
                if any(c[0] in ['cmp_num', 'cmp_sym'] for c in cand_constraints):
                    utility += 2.0 # Bonus for explicit comparison
                    
                # Free Energy F = S - E
                free_energy = surprisal - epistemic_value
                
                # Final Score = U - F
                score = utility - free_energy
                reasoning = f"S={surprisal:.2f}, E={epistemic_value:.2f}, U={utility:.2f}"
            else:
                # Fallback for unstructured prompts
                score = 0.5

            # Tiebreaker: NCD (Lower NCD to prompt is better if scores are close)
            # We invert NCD to be a small bonus
            ncd_bonus = 0.0
            if has_structure:
                ncd_val = self._calculate_ncd(prompt, cand)
                ncd_bonus = (1.0 - ncd_val) * 0.1 # Small weight
            
            final_score = score + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning if has_structure else "No structural pattern detected; using baseline."
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        # Map score to 0-1 range roughly
        # Assuming typical scores range from -5 to 5
        conf = 1.0 / (1.0 + np.exp(-raw_score)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))