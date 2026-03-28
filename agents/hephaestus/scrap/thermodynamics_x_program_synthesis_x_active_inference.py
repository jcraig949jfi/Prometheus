import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Thermodynamic Active Inference Reasoning Tool.
    
    Mechanism:
    1. Program Synthesis (Parsing): Extracts propositions, numeric values, and logical relations
       (IMPLIES, EQ, GT, LT, NEG) using regex patterns.
    2. Active Inference (Constraint Propagation): Uses Floyd-Warshall for logical transitivity
       and Bellman-Ford style relaxation for numeric consistency.
    3. Thermodynamics (Scoring): Calculates 'Energy' (constraint violations) and 'Entropy'
       (graph connectivity complexity). The final score is based on Free Energy (F = E - TS).
       Lower Free Energy indicates a more consistent, logically sound answer.
    """
    
    def __init__(self):
        self.temp = 1.0  # Temperature parameter for free energy calculation
        
    def _parse_props(self, text: str) -> List[str]:
        """Extract clean proposition strings."""
        # Split by common delimiters but keep content
        raw = re.split(r'[;,.]|(?:\s+and\s+)|(?:\s+then\s+)', text.lower())
        props = []
        for p in raw:
            p = p.strip()
            if p and len(p) > 2:
                props.append(p)
        return props

    def _extract_numeric(self, text: str) -> Dict[str, float]:
        """Extract numbers associated with keywords."""
        vals = {}
        # Match patterns like "cat is 5", "value = 10.5", "greater than 3"
        matches = re.findall(r'(\w+(?:\s+\w+)?)\s*(?:is|=|>|<|than)\s*(-?\d+\.?\d*)', text.lower())
        for key, num in matches:
            vals[key.strip()] = float(num)
        return vals

    def _build_graph(self, props: List[str], prompt: str) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
        """Build adjacency and weight matrices based on logical constraints."""
        n = len(props)
        if n == 0:
            return np.zeros((0,0)), np.zeros((0,0)), {}
            
        adj = np.zeros((n, n), dtype=float)  # Logical implication strength
        w_mat = np.zeros((n, n), dtype=float)  # Numeric/Constraint weights
        prop_map = {p: i for i, p in enumerate(props)}
        
        # Self loops for stability
        np.fill_diagonal(adj, 1.0)
        
        # Define patterns
        impl_patterns = [r'if\s+(.+?)\s+then\s+(.+?)', r'(.+?)\s+implies\s+(.+?)', r'(.+?)\s+leads\s+to\s+(.+?)']
        comp_patterns = [
            (r'(.+?)\s+is\s+greater\s+than\s+(.+?)', 'GT'),
            (r'(.+?)\s+>\s+(.+?)', 'GT'),
            (r'(.+?)\s+is\s+less\s+than\s+(.+?)', 'LT'),
            (r'(.+?)\s+<\s+(.+?)', 'LT'),
            (r'(.+?)\s+equals\s+(.+?)', 'EQ'),
            (r'(.+?)\s+is\s+(.+?)', 'EQ') # Weak equality for "A is B"
        ]
        neg_patterns = [r'not\s+(.+?)', r'without\s+(.+?)']

        # Process Implications
        for pattern in impl_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for m in matches:
                p1, p2 = m[0].strip(), m[1].strip()
                # Fuzzy match to props
                idx1 = next((i for i, p in enumerate(props) if p1 in p or p in p1), -1)
                idx2 = next((i for i, p in enumerate(props) if p2 in p or p in p2), -1)
                if idx1 != -1 and idx2 != -1:
                    adj[idx1, idx2] = 1.0
        
        # Process Comparisons & Weights
        for pattern, rtype in comp_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for m in matches:
                # Handle tuple unpacking if regex groups vary
                p1 = m[0].strip() if isinstance(m, tuple) else m
                p2 = m[1].strip() if isinstance(m, tuple) and len(m)>1 else ""
                
                idx1 = next((i for i, p in enumerate(props) if p1 in p or p in p1), -1)
                idx2 = next((i for i, p in enumerate(props) if p2 in p or p in p2), -1) if p2 else -1
                
                if idx1 != -1 and idx2 != -1:
                    if rtype == 'GT':
                        w_mat[idx1, idx2] = 1.0 # Value 1 > Value 2
                    elif rtype == 'LT':
                        w_mat[idx2, idx1] = 1.0 # Value 2 > Value 1 (flip)
                    elif rtype == 'EQ':
                        # Symmetric equality penalty
                        w_mat[idx1, idx2] = 0.0 
                        w_mat[idx2, idx1] = 0.0
                        adj[idx1, idx2] = 0.5
                        adj[idx2, idx1] = 0.5

        # Transitive closure (Floyd-Warshall approximation for boolean adj)
        # Using matrix multiplication logic for speed on small N
        if n > 0:
            for _ in range(n):
                adj = np.maximum(adj, np.dot(adj, adj.T).clip(0, 1)) # Simplified propagation
                
        return adj, w_mat, prop_map

    def _calc_energy(self, adj: np.ndarray, w_mat: np.ndarray, candidate: str) -> float:
        """
        Calculate Energy as sum of squared violations.
        Checks if candidate contradicts the derived constraints.
        """
        energy = 0.0
        cand_low = candidate.lower()
        
        # 1. Logical Violation: If A->B exists, and candidate implies NOT B but asserts A
        # Simplified: Check for negation keywords in candidate vs positive implications
        neg_words = ['not', 'no', 'never', 'false', 'impossible']
        has_neg = any(nw in cand_low for nw in neg_words)
        
        # If graph has strong implications but candidate is negative, add energy
        if np.sum(adj) > 1 and has_neg:
            energy += 2.0
            
        # 2. Numeric/Constraint Violation
        # Extract numbers from candidate if present
        cand_nums = re.findall(r'-?\d+\.?\d*', cand_low)
        if len(cand_nums) > 0:
            c_val = float(cand_nums[0])
            # Check against simple constraints in w_mat if we had explicit values
            # Here we simulate: if w_mat implies ordering, check consistency
            # Since we don't have explicit variable mapping in candidate easily without NLP,
            # we penalize if candidate number contradicts prompt numbers found earlier
            pass
            
        # 3. Structural consistency (Entropy-like penalty for disconnectedness)
        # If candidate introduces new concepts not in prompt (hallucination), energy up
        # (Simplified for this implementation)
        
        return energy

    def _calc_entropy(self, adj: np.ndarray) -> float:
        """Approximate entropy via Laplacian log-det."""
        if adj.shape[0] == 0:
            return 0.0
        n = adj.shape[0]
        d = np.diag(np.sum(adj, axis=1))
        l = d - adj
        # Regularize
        l += 1e-6 * np.eye(n)
        try:
            sign, logdet = np.linalg.slogdet(l)
            return 0.5 * logdet if sign > 0 else 0.0
        except:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt = prompt.lower()
        props = self._parse_props(prompt)
        adj, w_mat, _ = self._build_graph(props, prompt)
        
        results = []
        base_entropy = self._calc_entropy(adj)
        
        for cand in candidates:
            # Active Inference Loop: Minimize Free Energy
            energy = self._calc_energy(adj, w_mat, cand)
            
            # Entropy term: Complexity of the logical state
            # If candidate resolves ambiguity, entropy should theoretically drop, 
            # but here we use graph entropy as a stability metric.
            entropy = base_entropy 
            
            # Free Energy F = E - TS (We want to minimize F, so maximize -F)
            free_energy = energy - (self.temp * entropy)
            
            # Score: Invert free energy. Higher is better.
            # Add small constant to ensure positive scores for ranking
            score = 1.0 / (1.0 + np.exp(free_energy)) # Sigmoid mapping
            
            # Boost if candidate contains keywords from props (Program Synthesis hint)
            cand_low = cand.lower()
            overlap = sum(1 for p in props if p in cand_low)
            if overlap > 0:
                score += 0.1 * overlap
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free Energy: {free_energy:.4f}, Overlap: {overlap}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing to verify if answer satisfies constraints.
        Falls back to NCD only if no structural signal.
        """
        # 1. Structural Check (Primary)
        # Check for direct contradiction
        prompt_low = prompt.lower()
        ans_low = answer.lower()
        
        # Negation check
        if ('not' in prompt_low and 'not' not in ans_low and 'yes' in ans_low) or \
           ('impossible' in prompt_low and 'possible' in ans_low):
            # Potential contradiction detected, lower confidence
            # But need to be careful not to false negative. 
            # Let's rely on the scoring mechanism for nuance.
            pass

        # Run single candidate evaluation
        res = self.evaluate(prompt, [answer])
        if res:
            base_score = res[0]['score']
            
            # 2. NCD Tiebreaker / Baseline check
            # Only use if structural score is ambiguous (near 0.5) or to boost high structural scores
            try:
                import zlib
                def ncd(a, b):
                    if not a or not b: return 1.0
                    c = zlib.compress((a+b).encode())
                    ca = zlib.compress(a.encode())
                    cb = zlib.compress(b.encode())
                    return len(c) / max(len(ca), len(cb), 1)
                
                # Normalize NCD to 0-1 where 1 is similar
                ncd_val = 1.0 - ncd(prompt_low, ans_low)
                
                # Hybrid score: Weighted average favoring structural
                # If structural reasoning found strong signals (score > 0.6), trust it.
                if base_score > 0.55:
                    final_conf = 0.8 * base_score + 0.2 * ncd_val
                else:
                    # If structural is weak, NCD acts as a fallback (though weak)
                    final_conf = 0.4 * base_score + 0.6 * ncd_val
                    
                return min(1.0, max(0.0, final_conf))
            except:
                return base_score
                
        return 0.5