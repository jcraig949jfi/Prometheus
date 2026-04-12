import numpy as np
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a Thermodynamic-Gene-Regulatory-ActiveInference reasoning engine.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (nodes) and logical relations 
       (edges: +1 implication, -1 negation) from text using regex patterns for 
       negations, comparatives, conditionals, and causality.
    2. Gene-Regulatory Dynamics: Models truth probabilities as node states in a network.
       Uses iterative constraint propagation (sigmoid(A^T p + b)) to reach a steady 
       state (attractor), simulating logical consistency.
    3. Active Inference/Thermodynamics: Computes Free Energy (F) as a scoring metric.
       F = Expected Surprise (weighted by priors) - Entropy + Epistemic term.
       Lower F indicates higher logical consistency and lower uncertainty.
    4. Scoring: Candidates are ranked by -F. NCD is used strictly as a tiebreaker.
    """
    
    def __init__(self):
        self.priors = 0.6  # Baseline probability for unverified claims
        self.gamma = 0.1   # Epistemic exploration weight
        self.temp = 0.5    # Sigmoid temperature
        
    def _extract_features(self, text: str) -> tuple:
        """Extract nodes and adjacency matrix from text."""
        # Simple tokenization into sentences/clauses as nodes
        raw_nodes = re.split(r'[.,;]', text.lower())
        nodes = [n.strip() for n in raw_nodes if len(n.strip()) > 3]
        if not nodes:
            nodes = [text.lower()]
            
        n = len(nodes)
        A = np.zeros((n, n))
        biases = np.full(n, self.priors)
        
        # Patterns
        neg_pat = re.compile(r'\b(not|no|never|without|false)\b')
        cond_pat = re.compile(r'\b(if|then|implies|causes|leads to)\b')
        comp_pat = re.compile(r'\b(greater|less|more|fewer|before|after)\b')
        num_pat = re.compile(r'(\d+\.?\d*)')
        
        for i, node in enumerate(nodes):
            # Node attributes via bias modification
            if neg_pat.search(node):
                biases[i] -= 0.4 # Negation reduces baseline truth
            if comp_pat.search(node):
                biases[i] += 0.1 # Comparatives add structural weight
            
            # Numeric evaluation within node
            nums = num_pat.findall(node)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if ("less" in node or "before" in node) and v1 >= v2:
                        biases[i] -= 0.5 # Contradiction
                    elif ("greater" in node or "after" in node) and v1 <= v2:
                        biases[i] -= 0.5
                except: pass

            # Edges (Logical relations)
            for j, other in enumerate(nodes):
                if i == j: continue
                # Implication: if i contains 'if' and j is subset or related
                if cond_pat.search(node) and (other in node or node in other):
                    A[j, i] = 0.5 # Weak implication
                # Inhibition: if i has 'not' and matches j
                if neg_pat.search(node) and (other in node or node in other):
                    A[j, i] = -0.8 # Strong inhibition
        
        return nodes, A, biases

    def _propagate(self, A: np.ndarray, b: np.ndarray, steps: int = 10) -> np.ndarray:
        """Iterative constraint propagation to steady state."""
        p = np.full(A.shape[0], self.priors)
        for _ in range(steps):
            p_new = 1.0 / (1.0 + np.exp(-(A.T @ p + b) / self.temp))
            if np.max(np.abs(p_new - p)) < 1e-3:
                break
            p = p_new
        return p

    def _compute_free_energy(self, p: np.ndarray, A: np.ndarray, b: np.ndarray) -> float:
        """Calculate Free Energy: Surprise - Entropy + Epistemic."""
        # Avoid log(0)
        p_safe = np.clip(p, 1e-9, 1-1e-9)
        
        # Expected Surprise (simplified as mismatch between prior and state)
        surprise = np.sum(self.priors * np.abs(p_safe - self.priors))
        
        # Entropy H(p)
        entropy = -np.sum(p_safe * np.log(p_safe))
        
        # Epistemic term (approximated by variance reduction potential)
        epistemic = self.gamma * np.mean(np.var(A, axis=0))
        
        F = surprise - entropy + epistemic
        return float(F)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        def zlib_len(s): return len(__import__('zlib').compress(s.encode()))
        l1, l2, l12 = zlib_len(s1), zlib_len(s2), zlib_len(s1+s2)
        return (l12 - min(l1, l2)) / max(l1, l2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        full_texts = [f"{prompt} {c}" for c in candidates]
        
        # Parse all candidates
        parsed = [self._extract_features(t) for t in full_texts]
        
        scores = []
        for i, (nodes, A, b) in enumerate(parsed):
            if len(nodes) == 0:
                scores.append(-1e9)
                continue
            p_state = self._propagate(A, b)
            F = self._compute_free_energy(p_state, A, b)
            scores.append(-F) # Lower F -> Higher Score
        
        # NCD Tie-breaking
        final_scores = []
        for i, s in enumerate(scores):
            # Normalize NCD to be small perturbation
            ncd_val = self._ncd_score(prompt, candidates[i])
            final_scores.append(s + 0.01 * (1 - ncd_val))
            
        # Rank
        ranked_idx = np.argsort(final_scores)[::-1]
        
        output = []
        for idx in ranked_idx:
            output.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": f"Free-energy minimized state: {final_scores[idx]:.4f}"
            })
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on free energy gap."""
        # Evaluate against a dummy wrong answer to get scale
        dummy = "This is incorrect."
        res = self.evaluate(prompt, [answer, dummy])
        
        # If answer is ranked first and score is positive
        if res[0]['candidate'] == answer:
            # Map score to 0-1 roughly
            conf = 1.0 / (1.0 + np.exp(-res[0]['score'])) 
            return max(0.0, min(1.0, conf))
        return 0.2 # Low confidence if not top ranked