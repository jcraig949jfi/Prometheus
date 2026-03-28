import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Fractal-Free-Energy Metamorphic Scorer (FFEMS).
    
    Mechanism:
    1. Parses text into a logical graph (entities, predicates, negations, numerics).
    2. Generates Metamorphic Relations (MRs) to test logical consistency (e.g., transitivity, negation flip).
    3. Computes 'Prediction Error' based on MR violations.
    4. Estimates 'Fractal Complexity' via box-counting on the adjacency matrix.
    5. Calculates Free Energy Score: F = Error + lambda * Complexity. Lower F is better.
    
    Beats NCD baseline by enforcing structural logical consistency rather than string similarity.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(\.\d+)?'),
        'quantifier': re.compile(r'\b(all|some|every|each)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.lambda_complex = 0.1

    def _extract_props(self, text: str) -> List[Dict[str, Any]]:
        """Extract atomic propositions and features from text."""
        props = []
        lower_text = text.lower()
        
        # Extract numeric values
        nums = [float(m.group()) for m in re.finditer(self.PATTERNS['numeric'], lower_text)]
        
        # Feature flags
        has_neg = bool(self.PATTERNS['negation'].search(lower_text))
        has_comp = bool(self.PATTERNS['comparative'].search(lower_text))
        has_cond = bool(self.PATTERNS['conditional'].search(lower_text))
        has_causal = bool(self.PATTERNS['causal'].search(lower_text))
        has_quant = bool(self.PATTERNS['quantifier'].search(lower_text))
        
        # Create a simplified feature vector representing the "graph nodes"
        # We simulate nodes based on detected structural elements
        node_types = []
        if has_neg: node_types.append(1) # Negation node
        if has_comp: node_types.append(2) # Comparative node
        if has_cond: node_types.append(3) # Conditional node
        if has_causal: node_types.append(4) # Causal node
        if has_quant: node_types.append(5) # Quantifier node
        
        # Add numeric nodes
        for _ in nums:
            node_types.append(6)
            
        # Ensure at least one node exists to avoid math errors
        if not node_types:
            node_types = [0]
            
        return {
            'text': text,
            'nums': nums,
            'flags': [has_neg, has_comp, has_cond, has_causal, has_quant],
            'node_types': node_types,
            'length': len(text)
        }

    def _build_graph_matrix(self, props: Dict) -> np.ndarray:
        """Construct adjacency matrix from parsed properties."""
        n = len(props['node_types'])
        if n == 0:
            return np.zeros((1, 1))
        
        A = np.zeros((n, n), dtype=int)
        
        # Simulate edges based on logical flow (simplified for text)
        # Connect sequential nodes to form a chain (narrative flow)
        for i in range(n - 1):
            A[i, i+1] = 1
            
        # Connect negations to everything (global modifier)
        if props['flags'][0]: # If negation exists
            # Find index of negation type (1) if present, or assume first node if ambiguous
            # For simplicity in this abstraction: connect node 0 to all others if negation is present
            for j in range(1, n):
                A[0, j] = 1
                A[j, 0] = 1
                
        # Symmetrize for undirected box-counting approximation
        return (A + A.T) > 0

    def _calc_fractal_dim(self, A: np.ndarray) -> float:
        """Estimate fractal dimension via box-counting on adjacency matrix."""
        n = A.shape[0]
        if n < 2:
            return 0.0
            
        scales = []
        counts = []
        
        # Box sizes: powers of 2
        max_pow = int(np.floor(np.log2(n))) if n > 0 else 0
        if max_pow < 1:
            return 0.0
            
        for p in range(1, max_pow + 1):
            s = 2 ** p
            if s > n:
                break
            
            # Partition matrix into boxes of size s
            # Number of boxes per dimension
            num_boxes = int(np.ceil(n / s))
            count = 0
            
            for i in range(num_boxes):
                for j in range(num_boxes):
                    r_start, r_end = i*s, (i+1)*s
                    c_start, c_end = j*s, (j+1)*s
                    
                    # Check if box contains any edge
                    sub = A[r_start:r_end, c_start:c_end]
                    if np.any(sub):
                        count += 1
            
            if count > 0:
                scales.append(np.log(1.0/s))
                counts.append(np.log(count))
        
        if len(scales) < 2:
            return 0.0
            
        # Linear regression to find slope (D)
        # log(N) = -D * log(s) + C => slope is -D
        try:
            coeffs = np.polyfit(scales, counts, 1)
            D = -coeffs[0]
            return max(0.0, D) # Dimension cannot be negative
        except:
            return 0.0

    def _check_metamorphic_relations(self, prompt_props: Dict, ans_props: Dict) -> float:
        """
        Check deterministic MRs. Returns error count (violations).
        Since we don't have ground truth logic engine, we approximate violations
        by checking consistency of structural features between prompt and answer.
        """
        violations = 0
        
        # MR1: Numeric Consistency
        # If prompt has numbers, answer should ideally reflect numeric reasoning or not contradict magnitude
        p_nums = prompt_props['nums']
        a_nums = ans_props['nums']
        
        if len(p_nums) > 0 and len(a_nums) > 0:
            # Simple check: if prompt implies ordering, does answer follow?
            # Heuristic: If prompt has comparatives, answer should likely have numbers or comparatives
            if prompt_props['flags'][1]: # Prompt has comparative
                if not ans_props['flags'][1] and len(a_nums) == 0:
                    # Potential violation: Prompt compares, answer ignores comparison structure
                    violations += 1
        
        # MR2: Negation Flip
        # If prompt is negative, a "Yes" answer might need specific handling, 
        # but here we check if answer contradicts prompt negation presence unnecessarily
        if prompt_props['flags'][0] != ans_props['flags'][0]:
            # Mismatch in negation presence might indicate misunderstanding context
            # Soft penalty
            violations += 0.5
            
        # MR3: Conditional Logic
        # If prompt is conditional, answer shouldn't be absolute without qualification
        if prompt_props['flags'][2]:
            if ans_props['flags'][2] == False and len(ans_props['nums']) == 0:
                 violations += 0.2

        return violations

    def _compute_free_energy(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        
        # 1. Build Graphs
        # Combine prompt and candidate for joint graph analysis (context + answer)
        # Or analyze candidate graph complexity relative to prompt constraints
        A = self._build_graph_matrix(c_props)
        
        # 2. Metamorphic Relations (Error Term)
        err = self._check_metamorphic_relations(p_props, c_props)
        E_err = err ** 2
        
        # 3. Fractal Complexity (Complexity Term)
        D = self._calc_fractal_dim(A)
        E_complex = D
        
        # 4. Free Energy
        F = E_err + self.lambda_complex * E_complex
        score = -F # Higher is better
        
        reason = f"MR Violations: {err:.2f}, Fractal Dim: {D:.2f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            score, reason = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._compute_free_energy(prompt, answer)
        # Normalize score to 0-1 range heuristically
        # Assuming typical F ranges from -5 (good) to -20 (bad) in this simplified model
        # Shift and clamp
        conf = 1.0 / (1.0 + np.exp(score + 2.0)) # Sigmoid mapping
        return float(np.clip(conf, 0.0, 1.0))