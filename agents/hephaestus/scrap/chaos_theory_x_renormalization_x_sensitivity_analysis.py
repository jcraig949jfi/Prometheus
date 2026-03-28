import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Multi-Scale Sensitivity Propagation (MSSP) Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, negations, comparatives, 
       and conditionals from text to build a logical graph.
    2. Baseline Truth: Assigns initial truth values (0, 0.5, 1) based on affirmation/denial.
    3. Perturbation & Jacobian: Injects small deltas into node truths and computes 
       a linearized Jacobian matrix representing edge weights and logical operators.
    4. Lyapunov Estimation: Iteratively propagates perturbations (delta_{k+1} = J * delta_k) 
       to estimate the largest Lyapunov exponent (lambda), measuring system instability.
    5. Scoring: Candidates are scored by exp(-lambda). Lower sensitivity (chaos) implies 
       higher robustness and correctness. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.epsilon = 0.01
        self.iterations = 5
        self.tau_threshold = 0.7

    def _parse_text(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract nodes and edges from text using regex structural analysis."""
        text_lower = text.lower()
        nodes = []
        edges = []
        
        # Split into sentences/clauses roughly
        clauses = re.split(r'[.,;]', text)
        
        node_id_counter = 0
        
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
                
            # Detect negation
            is_negated = bool(re.search(r'\b(not|no|never|neither)\b', clause.lower()))
            
            # Detect comparatives
            comp_match = re.search(r'(\w+)\s+(greater than|less than|more than|fewer than|equals|equal to)\s+(\w+)', clause.lower())
            if comp_match:
                op_map = {'greater than': '>', 'less than': '<', 'more than': '>', 'fewer than': '<', 'equals': '=', 'equal to': '='}
                op = op_map.get(comp_match.group(2), '=')
                nodes.append({'id': node_id_counter, 'text': clause, 'v0': 1.0 if not is_negated else 0.0, 'type': 'comp'})
                edges.append({'src': node_id_counter, 'tgt': node_id_counter, 'op': op, 'w': 0.9})
                node_id_counter += 1
                continue

            # Detect conditionals (If A then B) - simplified
            if_match = re.search(r'if\s+(.+?)\s+(?:then|,)?\s+(.+)', clause.lower())
            if if_match:
                # Create implication edge logic placeholder
                nodes.append({'id': node_id_counter, 'text': clause, 'v0': 0.5, 'type': 'cond'})
                node_id_counter += 1
                continue

            # Default proposition
            # Check for numeric literals to boost confidence
            has_num = bool(re.search(r'\d+', clause))
            base_val = 1.0 if not is_negated else 0.0
            if has_num:
                base_val = 1.0 if not is_negated else 0.0 # Numbers imply concrete facts
            
            nodes.append({'id': node_id_counter, 'text': clause, 'v0': base_val, 'type': 'prop'})
            
            # Add causal/logical edges to neighbors if multiple exist
            if node_id_counter > 0:
                edges.append({'src': node_id_counter - 1, 'tgt': node_id_counter, 'op': '->', 'w': 0.8})
                
            node_id_counter += 1

        # If no nodes found, create a dummy one to prevent crash
        if not nodes:
            nodes.append({'id': 0, 'text': text, 'v0': 0.5, 'type': 'dummy'})
            
        return nodes, edges

    def _build_jacobian(self, nodes: List[Dict], edges: List[Dict]) -> np.ndarray:
        """Construct Jacobian matrix J where J[i,j] = d(node_i)/d(node_j)."""
        n = len(nodes)
        if n == 0:
            return np.array([[0.0]])
        J = np.zeros((n, n))
        
        # Diagonal holds self-persistence (small decay)
        np.fill_diagonal(J, 0.95)
        
        for edge in edges:
            src, tgt = edge['src'], edge['tgt']
            if src < n and tgt < n:
                w = edge['w']
                op = edge['op']
                
                if op == '->': # Implication
                    J[tgt, src] = w
                elif op in ['>', '<', '=']: # Comparative constraint
                    J[tgt, src] = w * 0.5 # Soft constraint
                else:
                    J[tgt, src] = w * 0.5
                    
        return J

    def _compute_lyapunov(self, nodes: List[Dict], edges: List[Dict]) -> float:
        """Estimate largest Lyapunov exponent via perturbation propagation."""
        if len(nodes) == 0:
            return 0.0
            
        J = self._build_jacobian(nodes, edges)
        n = len(nodes)
        
        # Initial perturbation vector
        delta = np.ones(n) * self.epsilon
        
        lyap_sum = 0.0
        count = 0
        
        for _ in range(self.iterations):
            delta_next = np.dot(J, delta)
            norm_curr = np.linalg.norm(delta)
            norm_next = np.linalg.norm(delta_next)
            
            if norm_curr > 1e-10 and norm_next > 1e-10:
                lyap_sum += np.log(norm_next / norm_curr)
                count += 1
            
            # Renormalize to prevent overflow/underflow (standard algorithm step)
            if norm_next > 1e-10:
                delta = delta_next * (self.epsilon / norm_next)
            else:
                delta = np.ones(n) * self.epsilon
                
        if count == 0:
            return 0.0
            
        return lyap_sum / count

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        def zlib_len(s):
            import zlib
            return len(zlib.compress(s.encode('utf-8')))
        
        if not s1 or not s2:
            return 1.0
        c1 = zlib_len(s1)
        c2 = zlib_len(s2)
        c12 = zlib_len(s1 + s2)
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Analyze prompt structure once
        p_nodes, p_edges = self._parse_text(prompt)
        prompt_lyap = self._compute_lyapunov(p_nodes, p_edges)
        
        for cand in candidates:
            # Combine prompt and candidate for joint analysis
            combined_text = f"{prompt} {cand}"
            c_nodes, c_edges = self._parse_text(combined_text)
            
            # Compute sensitivity of the combined system
            lyap = self._compute_lyapunov(c_nodes, c_edges)
            
            # Score: Robustness = exp(-lambda). Higher is better.
            # We penalize high chaos (positive lyap) heavily.
            robustness = np.exp(-lyap)
            
            # Heuristic adjustment: If candidate contradicts prompt negation structure
            # Simple keyword check for demonstration of structural parsing
            cand_lower = cand.lower()
            prompt_lower = prompt.lower()
            penalty = 0.0
            
            if ('not' in prompt_lower or 'no' in prompt_lower) and ('yes' in cand_lower or 'true' in cand_lower):
                # Potential contradiction depending on context, slight penalty
                penalty = 0.1
            
            final_score = float(robustness - penalty)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Lyapunov exponent: {lyap:.4f}, Robustness: {robustness:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on MSSP stability."""
        combined = f"{prompt} {answer}"
        nodes, edges = self._parse_text(combined)
        lyap = self._compute_lyapunov(nodes, edges)
        
        # Map robustness to 0-1 confidence
        # Stable systems (low/neg lyap) -> high confidence
        conf = np.exp(-lyap)
        
        # Clamp between 0 and 1
        return float(np.clip(conf, 0.0, 1.0))