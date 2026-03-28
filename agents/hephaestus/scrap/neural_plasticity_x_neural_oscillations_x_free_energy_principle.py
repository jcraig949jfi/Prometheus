import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine based on Neural Plasticity, Oscillations, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositional triples (subject, relation, object) using regex.
    2. Graph Rep: Builds an adjacency tensor R where edges represent relation types.
    3. Plasticity: Uses Hebbian updates (co-occurrence within gamma windows) to strengthen weights.
    4. Oscillations: Applies theta-cycle decay to simulate context refreshing and cross-frequency coupling.
    5. Free Energy: Scores candidates by computing variational free energy (prediction error + complexity)
       between the prompt's learned weight matrix and the candidate's structural tensor.
    """
    
    RELATIONS = ['not', 'gt', 'lt', 'if', 'causes', 'before', 'after', 'eq', 'neq']
    GAMMA = 4  # Gamma cycle window size
    THETA = 10 # Theta cycle length
    ETA = 0.05 # Learning rate
    LAMBDA = 0.1 # Decay rate
    DELTA = 0.001 # Regularization
    
    def __init__(self):
        self.relation_patterns = [
            (r'\bnot\b|\bno\b|\bnever\b', 'not'),
            (r'\bmore than\b|\bgreater than\b|>', 'gt'),
            (r'\bless than\b|<', 'lt'),
            (r'\bif\b|\bthen\b|\bunless\b', 'if'),
            (r'\bbecause\b|\bleads to\b|\bresults in\b|\bcauses\b', 'causes'),
            (r'\bbefore\b|\bfirst\b', 'before'),
            (r'\bafter\b|\bsecond\b|\bnext\b', 'after'),
            (r'\bequal\b|=', 'eq'),
            (r'\bunequal\b|\b!=\b', 'neq')
        ]

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (subject, relation, object) triples."""
        triples = []
        tokens = self._tokenize(text)
        text_lower = text.lower()
        
        # Simple heuristic: look for relation keywords and grab surrounding words
        for pattern, rel_type in self.relation_patterns:
            matches = list(re.finditer(pattern, text_lower))
            for m in matches:
                start, end = m.start(), m.end()
                # Find nearest nouns/words before and after
                pre_text = text_lower[:start].strip()
                post_text = text_lower[end:].strip()
                
                subj = pre_text.split()[-1] if pre_text.split() else "null"
                obj = post_text.split()[0] if post_text.split() else "null"
                
                # Clean punctuation
                subj = re.sub(r'[^\w]', '', subj)
                obj = re.sub(r'[^\w]', '', obj)
                
                if subj and obj:
                    triples.append((subj, rel_type, obj))
        
        # Add numeric comparisons if detected
        nums = re.findall(r'\d+\.?\d*', text)
        if len(nums) >= 2:
            # Assume order implies relation if no explicit comparator found near them
            triples.append((nums[0], 'gt', nums[1])) # Heuristic assumption
            
        return triples

    def _build_tensor(self, triples: List[Tuple[str, str, str]], all_nodes: List[str]) -> np.ndarray:
        """Build adjacency tensor R [n_nodes, n_nodes, n_relations]."""
        n = len(all_nodes)
        r_len = len(self.RELATIONS)
        tensor = np.zeros((n, n, r_len))
        
        node_map = {node: i for i, node in enumerate(all_nodes)}
        
        for subj, rel, obj in triples:
            if subj in node_map and obj in node_map:
                i, j = node_map[subj], node_map[obj]
                if rel in self.RELATIONS:
                    k = self.RELATIONS.index(rel)
                    tensor[i, j, k] = 1.0
        return tensor

    def _simulate_dynamics(self, text: str, all_nodes: List[str]) -> np.ndarray:
        """Simulate plasticity and oscillations to learn weights W."""
        if not all_nodes:
            return np.zeros((1, 1, len(self.RELATIONS)))
            
        n = len(all_nodes)
        r_len = len(self.RELATIONS)
        W = np.full((n, n, r_len), 0.01) # Initialize with epsilon
        
        tokens = self._tokenize(text)
        if not tokens:
            return W
            
        node_map = {node: i for i, node in enumerate(all_nodes)}
        
        # Gamma windows for Hebbian update
        for t in range(len(tokens)):
            # Gamma window
            window_start = max(0, t - self.GAMMA)
            window_tokens = tokens[window_start:t+1]
            
            # Activation vector
            a = np.zeros(n)
            for tok in window_tokens:
                if tok in node_map:
                    a[node_map[tok]] = 1.0
            
            # Hebbian update: Delta W = eta * (a outer a)
            # We apply this to all relation layers where co-occurrence happens
            if np.sum(a) > 0:
                outer_prod = np.outer(a, a)
                for k in range(r_len):
                    # Strengthen connections between active nodes
                    W[:, :, k] += self.ETA * (outer_prod * (1.0 if np.any(a) else 0.0))
            
            # Theta reset (decay)
            if t % self.THETA == 0 and t > 0:
                W *= np.exp(-self.LAMBDA)
                
        return W

    def _compute_free_energy(self, W: np.ndarray, A: np.ndarray) -> float:
        """Compute Free Energy F = 0.5 * sum(Pi * (A-W)^2) + 0.5 * log|Sigma|."""
        if W.size == 0 or A.size == 0:
            return 1e6
            
        # Precision matrix approximation (diagonal dominance for stability)
        Pi = W + self.DELTA
        
        # Prediction error term
        diff = A - W
        error_term = 0.5 * np.sum(Pi * (diff ** 2))
        
        # Complexity term (Log determinant)
        # Flatten for slogdet or use diagonal approximation if too large
        try:
            # Use a simplified trace/log-det approximation for stability in small dims
            # Or just log det of the flattened view if square, but tensor is 3D.
            # We treat the tensor as a collection of independent graphs or flatten.
            # Let's use the sum of log diagonals as a proxy for log-det to ensure stability
            log_det_term = 0.5 * np.sum(np.log(np.abs(Pi) + 1e-10))
        except:
            log_det_term = 0.0
            
        return float(error_term + log_det_term)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_triples = self._extract_triples(prompt)
        prompt_nodes = list(set([s for s, _, o in prompt_triples] + [o for _, _, o in prompt_triples]))
        
        # If no structure found, use all words as nodes to allow NCD fallback logic via tensor density
        if not prompt_nodes:
            prompt_nodes = list(set(self._tokenize(prompt)))[:10] # Limit size

        # Learn W from prompt
        W = self._simulate_dynamics(prompt, prompt_nodes)
        
        results = []
        for cand in candidates:
            cand_triples = self._extract_triples(cand)
            # Map candidate nodes to prompt nodes where possible, else ignore
            cand_nodes = [n for n in prompt_nodes if n in [s for s,_,o in cand_triples] or n in [o for _,_,o in cand_triples]]
            
            if not cand_nodes:
                # Fallback: if no structural overlap, score based on string similarity (NCD proxy)
                # But per instructions, NCD is tiebreaker. We assign a neutral high energy.
                score = 100.0 
            else:
                # Build candidate tensor A aligned with prompt nodes
                A = self._build_tensor(cand_triples, prompt_nodes)
                F = self._compute_free_energy(W, A)
                score = -F # Lower F is better, so higher score is better
            
            results.append({"candidate": cand, "score": score, "reasoning": "Free Energy Minimization"})

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score roughly to 0-1 based on typical free energy ranges
        # Since F can be large negative, we use a sigmoid-like mapping
        score = res[0]["score"]
        # Heuristic normalization: assume scores > -10 are good, < -100 are bad
        conf = 1.0 / (1.0 + np.exp(0.1 * (score + 50))) 
        return float(np.clip(conf, 0.0, 1.0))