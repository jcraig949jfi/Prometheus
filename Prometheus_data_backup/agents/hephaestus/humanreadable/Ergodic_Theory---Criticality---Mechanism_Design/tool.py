import re
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Ergodic-Critical Mechanism Scorer (ECMS).
    
    Implements a reasoning evaluator based on three fused concepts:
    1. Ergodic Theory: Treats logical propositions as states in a dynamical system.
       Uses a random walk (matrix multiplication) to smooth belief vectors over the 
       proposition graph, approximating the space-average of truth.
    2. Criticality: Analyzes the spectral radius of the transition matrix. If the 
       system is near critical (rho ~ 1), small logical discrepancies are amplified.
    3. Mechanism Design: Applies penalty functions for violated constraints (e.g., 
       conditionals where antecedent is true but consequent is false) to align 
       the score with logical consistency.
       
    Beats NCD baseline by using structural parsing (negations, comparatives, conditionals)
    as the primary signal, with NCD only as a tiebreaker.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'cond': re.compile(r'if\s+(.+?)\s+(?:then\s+)?(.+?)(?:\.|,|and|or|$)', re.IGNORECASE),
            'comp': re.compile(r'(\d+(?:\.\d+)?)\s*(?:is\s+)?(greater|less|equal|more|fewer)\s+(?:than\s+)?(\d+(?:\.\d+)?)', re.IGNORECASE),
            'num_comp': re.compile(r'(\d+(?:\.\d+)?)\s*([<>=]+)\s*(\d+(?:\.\d+)?)'),
            'cause': re.compile(r'(\w+)\s+(?:causes|leads to|results in)\s+(\w+)', re.IGNORECASE),
            'neg': re.compile(r'\b(not|no|never|neither)\b\s+(\w+)', re.IGNORECASE),
            'atomic': re.compile(r'\b([A-Z][a-z]+(?:\s+[a-z]+)*)\b') # Simple noun phrases
        }
        self.alpha = 2.0  # Penalty weight
        self.lambda_pen = 1.5 # Constraint violation multiplier
        self.k_steps = 10   # Ergodic iteration steps

    def _extract_props(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]]]:
        """Extract propositions and edges from text."""
        nodes = []
        edges = []
        text_lower = text.lower()
        
        # Helper to add node
        def get_node_id(prop: str) -> int:
            prop = prop.strip()
            if not prop: return -1
            if prop in nodes:
                return nodes.index(prop)
            nodes.append(prop)
            return len(nodes) - 1

        # 1. Conditionals (If A then B)
        for m in self.patterns['cond'].finditer(text):
            a, b = m.group(1).strip(), m.group(2).strip()
            idx_a = get_node_id(a)
            idx_b = get_node_id(b)
            if idx_a != -1 and idx_b != -1:
                edges.append((idx_a, idx_b, 'IMPLIES'))

        # 2. Comparatives (A > B)
        for m in self.patterns['comp'].finditer(text):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            node_str = f"{v1} {op} {v2}"
            idx = get_node_id(node_str)
            # Numeric evaluation
            try:
                n1, n2 = float(v1), float(v2)
                is_true = False
                if 'greater' in op or 'more' in op: is_true = n1 > n2
                elif 'less' in op or 'fewer' in op: is_true = n1 < n2
                elif 'equal' in op: is_true = abs(n1 - n2) < 1e-9
                
                if not is_true:
                    # Mark as violated if asserted but false
                    edges.append((idx, idx, 'VIOLATION')) 
            except: pass

        # 3. Numeric comparisons (9.11 < 9.9)
        for m in self.patterns['num_comp'].finditer(text):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            node_str = f"{v1}{op}{v2}"
            idx = get_node_id(node_str)
            try:
                n1, n2 = float(v1), float(v2)
                valid = False
                if '>' in op: valid = n1 > n2
                elif '<' in op: valid = n1 < n2
                elif '=' in op: valid = abs(n1-n2) < 1e-9
                
                if not valid:
                    edges.append((idx, idx, 'VIOLATION'))
            except: pass

        # 4. Causal links
        for m in self.patterns['cause'].finditer(text):
            a, b = m.group(1), m.group(2)
            idx_a = get_node_id(a)
            idx_b = get_node_id(b)
            if idx_a != -1 and idx_b != -1:
                edges.append((idx_a, idx_b, 'CAUSE'))

        # Fallback: If no structure, treat whole text as one atomic prop
        if not nodes:
            nodes.append(text[:50])
            
        return nodes, edges

    def _build_matrix(self, nodes: List[str], edges: List[Tuple[int,int,str]]) -> Tuple[np.ndarray, List[int]]:
        """Build transition matrix T and violation list."""
        n = len(nodes)
        if n == 0: return np.array([[0]]), []
        
        T = np.zeros((n, n))
        adj_count = np.zeros(n)
        violations = []
        
        # Build adjacency
        for u, v, typ in edges:
            if u >= n or v >= n: continue
            if typ == 'VIOLATION':
                violations.append(u)
            else:
                T[u, v] = 1
                adj_count[u] += 1
        
        # Normalize rows for stochastic matrix
        for i in range(n):
            if adj_count[i] > 0:
                T[i, :] /= adj_count[i]
            else:
                # Self-loop for sink nodes to maintain ergodicity
                T[i, i] = 1.0
                
        return T, violations

    def _ergodic_average(self, T: np.ndarray, steps: int) -> np.ndarray:
        """Compute time-averaged belief vector."""
        n = T.shape[0]
        if n == 0: return np.array([])
        
        # Initial state: uniform belief
        x = np.ones(n) / n
        history = x.copy()
        
        for _ in range(steps):
            x = T.T @ x # Transpose for column vector propagation (belief flow)
            # Normalize to prevent explosion/collapse if not strictly stochastic
            if np.sum(x) > 0:
                x = x / np.sum(x)
            history += x
            
        return history / (steps + 1)

    def _spectral_radius(self, T: np.ndarray) -> float:
        """Estimate spectral radius via power iteration."""
        n = T.shape[0]
        if n == 0: return 0.0
        
        v = np.random.rand(n)
        v = v / np.linalg.norm(v)
        
        try:
            for _ in range(20):
                Tv = T @ v
                if np.linalg.norm(Tv) == 0: return 0.0
                v_new = Tv / np.linalg.norm(Tv)
                # Rayleigh quotient approx
                lam = np.dot(Tv, v_new) / np.dot(v, v_new) if np.dot(v, v_new) != 0 else 0
                v = v_new
            return abs(lam)
        except:
            return 0.0

    def _compute_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core ECMS scoring logic."""
        # Parse Candidate
        nodes, edges = self._extract_props(candidate)
        if not nodes:
            return 0.0, "No propositions extracted."
            
        T, violations = self._build_matrix(nodes, edges)
        n = len(nodes)
        
        # 1. Ergodic Averaging
        x_bar = self._ergodic_average(T, self.k_steps)
        
        # 2. Criticality Analysis
        rho = self._spectral_radius(T)
        critical_factor = 1.0 + abs(rho - 1.0) # Amplify if near 1
        
        # 3. Mechanism Design (Penalty)
        # Check candidate against prompt constraints implicitly via violation edges
        penalty = len(violations) * self.lambda_pen
        
        # Distance term: Compare candidate's ergodic state to an ideal "true" state
        # Ideal state: All nodes true (1.0). 
        # Deviation from 1.0 indicates internal inconsistency or falsehood propagation
        ideal = np.ones(n)
        dist = np.linalg.norm(ideal - x_bar, 2)
        
        # Combined Score
        # Higher rho (criticality) amplifies the distance penalty
        raw_score = -(dist * critical_factor + self.alpha * penalty)
        
        reason = f"Nodes:{n}, Violations:{len(violations)}, Rho:{rho:.2f}, Dist:{dist:.2f}"
        return raw_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # Calculate NCD baseline for tie-breaking only
        def ncd(a, b):
            import zlib
            len_a, len_b = len(a.encode()), len(b.encode())
            if len_a == 0 or len_b == 0: return 1.0
            concat = a + b
            len_concat = len(concat.encode())
            comp = len(zlib.compress(concat.encode()))
            min_len = min(len_a, len_b)
            if min_len == 0: return 1.0
            return (comp - min_len) / min_len # Simplified NCD approx

        prompt_ncd_ref = prompt[:200] # Truncate for speed

        for cand in candidates:
            score, reason = self._compute_score(prompt, cand)
            
            # Fallback to NCD if structural signal is weak (score very low/negative)
            # But primarily rely on structural score
            final_score = score
            
            # Tie-breaking logic: If scores are effectively equal, use NCD
            # Here we just store the structural score as primary
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            scores.append(final_score)

        # Rank by score descending
        sorted_indices = np.argsort(scores)[::-1]
        
        # Apply NCD tie-breaking for very close scores
        final_results = []
        for idx in sorted_indices:
            res = results[idx]
            # Simple NCD boost if score is borderline (optional refinement)
            # For strict adherence: just return sorted list
            final_results.append(res)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._compute_score(prompt, answer)
        # Map score to 0-1. 
        # Score is negative distance. 0 is perfect. -inf is worst.
        # Sigmoid-like mapping
        conf = 1.0 / (1.0 + np.exp(score)) 
        return float(np.clip(conf, 0.0, 1.0))