import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaos-Pragmatic Free-Energy Scorer.
    Mechanism:
    1. Parses text into a propositional graph using regex (nodes=beliefs, edges=dependencies).
    2. Computes Free Energy (prediction error) between inferred states and observed facts.
    3. Applies a Chaos Penalty based on the spectral radius (Lyapunov exponent proxy) of the Jacobian.
    4. Iteratively adjusts edge weights via Pragmatic cues (Gricean maxims).
    5. Scores candidates by minimizing (Free Energy + Chaos Penalty).
    """
    
    def __init__(self):
        self.alpha = 0.1  # Chaos penalty weight
        self.beta = 0.05  # Pragmatic adjustment rate
        self.max_iter = 10
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|else)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|results in|causes)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|most|every|none)\b', re.IGNORECASE),
            'modal': re.compile(r'\b(might|must|should|could|will)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>=|<=|>|<|==|!=|greater than|less than)\s*(\w+)', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'assertion': re.compile(r'^[A-Z][^.!?]*[.]$', re.MULTILINE)
        }

    def _extract_props(self, text: str) -> Tuple[List[str], Dict]:
        """Extract atomic propositions and metadata."""
        props = []
        meta = {}
        
        # Simple sentence splitting as proxy for atomic propositions
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        for i, sent in enumerate(sentences):
            if not sent: continue
            props.append(sent)
            meta[i] = {
                'negated': bool(self.patterns['negation'].search(sent)),
                'conditional': bool(self.patterns['conditional'].search(sent)),
                'causal': bool(self.patterns['causal'].search(sent)),
                'quantified': bool(self.patterns['quantifier'].search(sent)),
                'modal': bool(self.patterns['modal'].search(sent)),
                'has_number': bool(self.patterns['number'].search(sent)),
                'polarity': -1 if bool(self.patterns['negation'].search(sent)) else 1
            }
        return props, meta

    def _build_graph(self, text: str, candidate: str = "") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build adjacency matrix W, belief vector b, and observation vector o."""
        full_text = f"{text} {candidate}"
        props, meta = self._extract_props(full_text)
        n = max(len(props), 2) # Ensure at least 2 nodes for matrix ops
        
        if n == 0: n = 2
        
        # Initialize matrices
        W = np.zeros((n, n), dtype=np.float64)
        b = np.ones(n, dtype=np.float64) * 0.5 # Prior belief 0.5
        o = np.ones(n, dtype=np.float64) * 0.5 # Observation 0.5 (unknown)
        
        # Populate beliefs and observations based on parsing
        for i, (sent, m) in enumerate(zip(props, meta.values())):
            # Belief initialization based on modality
            if m['modal']: b[i] = 0.7 # "Must" implies higher prior than random
            if m['negated']: b[i] = 0.3 # Negation lowers initial truth probability
            
            # Observation vector: explicit numbers or assertions get higher confidence
            if m['has_number'] or m['assertion'] if 'assertion' in m else False:
                # Simple heuristic: if it looks like a fact, set observation to 1 (true) or 0 (false if negated)
                o[i] = 1.0 if not m['negated'] else 0.0
            else:
                o[i] = 0.5 # Unknown

        # Build edges based on co-occurrence and pragmatic cues
        for i in range(n):
            for j in range(n):
                if i == j: 
                    W[i, j] = 0.0
                    continue
                
                mi = props[i] if i < len(props) else ""
                mj = props[j] if j < len(props) else ""
                
                # Pragmatic weight initialization
                weight = 0.1
                if meta[i].get('conditional') and meta[j].get('assertion'):
                    weight = 0.8 # Strong link if conditional leads to assertion
                elif meta[i].get('causal'):
                    weight = 0.7
                elif meta[i].get('quantified'):
                    weight = 0.5
                
                # Modulate by Gricean maxims (simplified)
                if meta[i].get('modal') and not meta[j].get('modal'):
                    weight *= 0.8 # Hedging reduces strength
                
                W[i, j] = weight

        return W, b, o

    def _compute_free_energy(self, W: np.ndarray, b: np.ndarray, o: np.ndarray) -> float:
        """Compute Free Energy F = 0.5 * (o-p)^T * pi * (o-p)."""
        if W.size == 0: return 0.0
        try:
            p = 1.0 / (1.0 + np.exp(-np.dot(W.T, b))) # Sigmoid prediction
            pi = np.ones_like(b) # Precision = 1
            diff = o - p
            F = 0.5 * np.dot(diff.T, pi * diff)
            return float(F)
        except:
            return 1e6

    def _compute_chaos_penalty(self, W: np.ndarray, b: np.ndarray) -> float:
        """Compute chaos penalty based on spectral radius of Jacobian."""
        if W.size == 0: return 0.0
        try:
            # Jacobian approximation: J = diag(sigmoid'(W^T b)) * W^T
            z = np.dot(W.T, b)
            sigmoid_prime = np.exp(-z) / ((1.0 + np.exp(-z)) ** 2)
            J = np.diag(sigmoid_prime) @ W.T
            
            # Largest eigenvalue magnitude (Lyapunov proxy)
            eigvals = np.linalg.eigvals(J)
            lambda_max = np.max(np.abs(eigvals))
            return self.alpha * lambda_max
        except:
            return 1.0

    def _pragmatic_adjust(self, W: np.ndarray, meta: Dict) -> np.ndarray:
        """Adjust edge weights based on pragmatic cues."""
        n = W.shape[0]
        W_adj = W.copy()
        for i in range(n):
            if i in meta:
                m = meta[i]
                factor = 1.0
                if m.get('quantified'): factor += self.beta # Stronger entailment
                if m.get('modal') and not m.get('conditional'): factor -= self.beta # Hedging weakness
                W_adj[i, :] *= factor
        return W_adj

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            W, b, o = self._build_graph(prompt, cand)
            props, meta = self._extract_props(f"{prompt} {cand}")
            
            # Iterative minimization loop
            current_F = self._compute_free_energy(W, b, o)
            
            for _ in range(self.max_iter):
                # 1. Compute Prediction
                if W.size > 0:
                    p = 1.0 / (1.0 + np.exp(-np.dot(W.T, b)))
                    # Gradient descent step on beliefs (simplified)
                    b = b + 0.1 * (o - p) 
                    b = np.clip(b, 0.01, 0.99)
                
                # 2. Pragmatic Adjustment
                W = self._pragmatic_adjust(W, meta)
                
                # 3. Recalculate F
                new_F = self._compute_free_energy(W, b, o)
                if abs(current_F - new_F) < 1e-4:
                    break
                current_F = new_F

            # Final Scoring
            F_final = current_F
            C_final = self._compute_chaos_penalty(W, b)
            score = -(F_final + C_final) # Higher is better (less energy/chaos)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"F={F_final:.4f}, C={C_final:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        # Normalize score to 0-1 range heuristically
        # Since score is negative energy, higher (closer to 0) is better.
        # Assume worst case is -10, best is 0.
        s = res[0]['score']
        conf = 1.0 / (1.0 + np.exp(s + 2.0)) # Sigmoid shift
        return float(np.clip(conf, 0.0, 1.0))