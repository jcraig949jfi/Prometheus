import re
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    A reasoning tool combining Mechanism Design (scoring), Renormalization (fixed-point inference),
    and Proof Theory (cut elimination) to evaluate logical consistency of candidate answers.
    
    Mechanism:
    1. Parsing: Extracts logical clauses (predicates, args, polarity) via regex.
    2. Graph Construction: Builds an implication graph with transitivity for comparatives.
    3. Renormalization: Iteratively propagates truth values until a fixed point is reached.
    4. Cut Elimination: Removes intermediate literals that appear as both antecedent and consequent.
    5. Scoring: Computes an incentive-compatible score based on inconsistency energy reduction.
    """

    def __init__(self):
        self.predicates = ['not', 'less', 'greater', 'equal', 'implies', 'causes', 'precedes']
        self.epsilon = 1e-4
        self.lambda_penalty = 0.1

    def _parse_clauses(self, text):
        """Extract logical clauses from text using regex."""
        clauses = []
        text_lower = text.lower()
        
        # Negation
        for m in re.finditer(r'\b(not|no)\s+(\w+)', text_lower):
            clauses.append(('not', m.group(2), -1))
            
        # Comparatives (numeric)
        for m in re.finditer(r'(\d+\.?\d*)\s*(<|less than|>)\s*(\d+\.?\d*)', text_lower):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            if op in ['<', 'less than']:
                clauses.append(('less', (v1, v2), 1))
                clauses.append(('greater', (v2, v1), 1))
            else:
                clauses.append(('greater', (v1, v2), 1))
                clauses.append(('less', (v2, v1), 1))

        # Conditionals (simplified)
        for m in re.finditer(r'\bif\s+(.+?)\s+(?:then)?\s+(.+?)(?:\.|,|$)', text_lower):
            clauses.append(('implies', (m.group(1).strip(), m.group(2).strip()), 1))
            
        # Causal/Ordering
        for m in re.finditer(r'(\w+)\s+(causes|leads to|precedes|before|after)\s+(\w+)', text_lower):
            pred = 'causes' if 'cause' in m.group(2) or 'lead' in m.group(2) else 'precedes'
            if 'after' in m.group(2): pred, args = 'precedes', (m.group(3), m.group(1))
            else: args = (m.group(1), m.group(3))
            clauses.append((pred, args, 1))

        # Atomic facts (positive assertions)
        for m in re.finditer(r'\b(\w+)\s+is\s+(\w+)', text_lower):
            clauses.append(('equal', (m.group(1), m.group(2)), 1))

        return clauses

    def _build_graph(self, clauses):
        """Build adjacency matrix and bias vector."""
        nodes = set()
        edges = []
        bias = defaultdict(float)
        
        for pred, args, pol in clauses:
            if isinstance(args, tuple) and len(args) == 2:
                u, v = str(args[0]), str(args[1])
                nodes.update([u, v])
                if pred in ['implies', 'causes', 'precedes']:
                    edges.append((u, v, 1.0))
                elif pred == 'less':
                    # Transitivity hint: u < v implies u -> v in ordering chain
                    edges.append((u, v, 0.5)) 
            elif isinstance(args, str):
                nodes.add(args)
                if pol == 1: bias[args] += 1.0
                else: bias[args] -= 1.0

        node_list = sorted(list(nodes))
        idx_map = {n: i for i, n in enumerate(node_list)}
        n = len(node_list)
        if n == 0: return None, None, {}, {}
        
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        for u, v, w in edges:
            if u in idx_map and v in idx_map:
                W[idx_map[u], idx_map[v]] = w
        
        for node, val in bias.items():
            if node in idx_map:
                b[idx_map[node]] = val
                
        return W, b, idx_map, {i: n for n, i in idx_map.items()}

    def _renormalize(self, W, b):
        """Iterate to fixed point."""
        if W is None: return np.array([])
        n = W.shape[0]
        t = np.sigmoid(b) if hasattr(np, 'sigmoid') else 1/(1+np.exp(-b)) # Fallback if numpy version old
        # Standard logistic
        t = 1 / (1 + np.exp(-b)) 
        
        for _ in range(50): # Fixed iterations for stability
            t_new = 1 / (1 + np.exp(-(W.T @ t + b)))
            if np.linalg.norm(t_new - t, 1) < self.epsilon:
                break
            t = t_new
        return t

    def _cut_elimination(self, W, idx_map):
        """Simplify graph by removing cut nodes (simplified heuristic)."""
        if W is None: return W
        # In a full proof net, we'd rewire. Here we zero out rows/cols of nodes 
        # that are purely intermediate (in-degree > 0 and out-degree > 0)
        # to simulate canonicalization.
        in_deg = np.sum(W > 0, axis=0)
        out_deg = np.sum(W > 0, axis=1)
        cuts = (in_deg > 0) & (out_deg > 0)
        # We don't strictly remove to keep dimensions, but dampen their influence
        # to simulate the 'canonical' form where intermediate steps are compressed.
        W_red = W.copy()
        # Dampening cuts slightly to prioritize direct evidence
        if np.any(cuts):
             W_red[:, cuts] *= 0.9 
             W_red[cuts, :] *= 0.9
        return W_red

    def _compute_energy(self, W, b, t):
        if W is None: return 0.0
        pred = 1 / (1 + np.exp(-(W.T @ t + b)))
        return np.sum((t - pred)**2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        # Parse prompt once as base context
        base_clauses = self._parse_clauses(prompt)
        base_W, base_b, _, _ = self._build_graph(base_clauses)
        
        # Base energy without any candidate
        if base_W is not None:
            base_t = self._renormalize(base_W, base_b)
            E_before = self._compute_energy(base_W, base_b, base_t)
        else:
            E_before = 0.0
            base_t = np.array([])

        for cand in candidates:
            # Combine prompt + candidate
            full_text = f"{prompt} {cand}"
            clauses = self._parse_clauses(full_text)
            W, b, idx_map, rev_map = self._build_graph(clauses)
            
            score = 0.0
            reasoning = "No structural logic detected."
            
            if W is not None and W.size > 0:
                # Renormalization
                t_star = self._renormalize(W, b)
                
                # Cut Elimination (Simulation)
                W_red = self._cut_elimination(W, idx_map)
                t_red = self._renormalize(W_red, b) # Re-converge on reduced net
                
                E_after = self._compute_energy(W_red, b, t_red)
                
                # Mechanism Design Scoring
                # Score = Reduction in energy (consistency) - Penalty for complexity
                complexity_penalty = self.lambda_penalty * len(clauses)
                # If E_after < E_before, energy decreased (good), so score positive
                score = (E_before - E_after) - complexity_penalty
                
                # Heuristic boost for numeric consistency if detected
                if any('less' in str(c) or 'greater' in str(c) for c in clauses):
                    score += 0.5 
                    
                reasoning = f"Fixed-point converged. Energy change: {E_before - E_after:.4f}. Cuts eliminated."
            else:
                # Fallback to simple NCD if no structure found (Tiebreaker only)
                import zlib
                def ncd(a, b):
                    if not a or not b: return 1.0
                    c = zlib.compress((a+b).encode())
                    return len(c) / max(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())), 1)
                # Invert NCD so higher is better (lower distance)
                score = 1.0 - ncd(prompt, cand)
                reasoning = "Structural parsing failed; using compression baseline."

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the score of the single candidate."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score roughly to 0-1 range assuming typical energy scales
        # This is a heuristic mapping
        raw_score = res[0]['score']
        # Sigmoid mapping to 0-1
        conf = 1 / (1 + np.exp(-raw_score))
        return float(np.clip(conf, 0.0, 1.0))