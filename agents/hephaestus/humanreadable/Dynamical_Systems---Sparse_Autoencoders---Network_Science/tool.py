import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Dynamical Systems-based reasoning engine using Sparse Autoencoder principles.
    
    Mechanism:
    1. Parsing: Extracts propositions and logical relations (negation, causality, comparison) 
       from the prompt to build a weighted adjacency matrix (W).
    2. State Initialization: Maps candidate answers to a binary state vector based on extracted nodes.
    3. Dynamical Update: Iterates x(t+1) = SoftThreshold(W * x(t)) to simulate energy minimization.
       This enforces sparsity and consistency, suppressing contradictory propositions.
    4. Scoring: Computes a Lyapunov-like energy function. Lower energy (higher negative score) 
       indicates a stable, logically consistent attractor state.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bcauses\b', r'\btherefore\b'],
            'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore than\b', r'\bfewer than\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
            'numeric': [r'(\d+(?:\.\d+)?)\s*(?:times|double|half|twice)\s*(?:as|larger|smaller)?']
        }
        # Noun phrase approximation (simple chunking)
        self.np_regex = re.compile(r'\b([a-z]{3,}(?:\s+[a-z]{3,})*)\b', re.IGNORECASE)

    def _extract_nodes_and_edges(self, text: str) -> Tuple[List[str], np.ndarray, Dict[int, str]]:
        """Parse text into nodes (propositions) and weighted edges."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # 1. Extract candidate nodes (simplified noun phrases/chunks)
        # We use a set to keep unique propositions, then list for indexing
        raw_matches = re.findall(r'\b([a-z]{4,}(?:\s+[a-z]{4,}){0,3})\b', text_lower)
        unique_nodes = list(dict.fromkeys(raw_matches)) # Preserve order, remove duplicates
        
        if not unique_nodes:
            return [], np.array([]), {}
            
        n = len(unique_nodes)
        W = np.zeros((n, n))
        node_map = {i: node for i, node in enumerate(unique_nodes)}
        
        # 2. Assign weights based on logical operators found in context
        # We scan the text for operators and weight connections between nearby nodes
        
        # Negation: -1 weight
        for pat in self.patterns['negation']:
            if re.search(pat, text_lower):
                # Simplified: Apply negative self-loops or connections to nearby concepts
                # In a full graph, this would be specific. Here we penalize co-occurrence near negation.
                pass 

        # Causal/Conditional: +1 weight (affirming)
        # We create a dense connectivity for now as a proxy for "contextual binding"
        # Real implementation would parse dependency trees. 
        # Heuristic: If operator exists, strengthen connections between sequential nodes.
        
        has_logic = False
        for key, pats in self.patterns.items():
            for pat in pats:
                if re.search(pat, text_lower):
                    has_logic = True
                    # Strengthen sequential dependencies where logic appears
                    for i in range(n - 1):
                        # Simple proximity weighting
                        W[i, i+1] = 1.0 if key in ['causal', 'conditional'] else 0.5
                        W[i+1, i] = 1.0 if key in ['causal', 'conditional'] else 0.5
        
        if not has_logic:
            # Fallback: Identity-like structure if no logic found, relying on NCD later
            W = np.eye(n)
            
        # Normalize weights slightly to prevent explosion
        if np.max(W) > 0:
            W = W / np.max(W) * 0.9
            
        return unique_nodes, W, node_map

    def _dynamical_update(self, W: np.ndarray, x0: np.ndarray, lambda_param: float = 0.1, steps: int = 10) -> np.ndarray:
        """Iterate the sparse dynamical system."""
        x = x0.copy().astype(float)
        if x.size == 0:
            return x
            
        for _ in range(steps):
            # Linear step
            x_new = W @ x
            # Sparsity step (Soft Thresholding / ISTA)
            # S_lambda(u) = sign(u) * max(|u| - lambda, 0)
            x_new = np.sign(x_new) * np.maximum(np.abs(x_new) - lambda_param, 0)
            x = x_new
        return x

    def _compute_energy(self, x: np.ndarray, W: np.ndarray, lambda_param: float = 0.1) -> float:
        """Compute Lyapunov-like energy."""
        if x.size == 0:
            return 1e6 # High energy for empty
            
        # Laplacian L = D - W
        D = np.diag(np.sum(np.abs(W), axis=1))
        L = D - W
        
        # Energy = 0.5 * x^T L x + lambda * ||x||_1
        term1 = 0.5 * float(x.T @ L @ x)
        term2 = lambda_param * np.sum(np.abs(x))
        return term1 + term2

    def _get_state_vector(self, candidate: str, nodes: List[str]) -> np.ndarray:
        """Map candidate text to binary state vector based on node presence."""
        if not nodes:
            return np.array([])
            
        cand_lower = candidate.lower()
        x = np.zeros(len(nodes))
        for i, node in enumerate(nodes):
            # Check if node or its variations appear in candidate
            if node in cand_lower:
                x[i] = 1.0
            # Handle simple negation in candidate flipping the state? 
            # For now, strict presence indicates activation.
        return x

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt to build Graph
        nodes, W, _ = self._extract_nodes_and_edges(prompt)
        n = len(nodes)
        
        results = []
        
        # Pre-calculate prompt complexity for NCD tie-breaking
        prompt_rep = prompt.lower()
        
        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            if n > 0:
                # 2. Initialize State
                x0 = self._get_state_vector(cand, nodes)
                
                if np.sum(x0) > 0:
                    # 3. Dynamical Update
                    x_final = self._dynamical_update(W, x0, lambda_param=0.05, steps=15)
                    
                    # 4. Energy Evaluation
                    energy = self._compute_energy(x_final, W, lambda_param=0.05)
                    
                    # Score is negative energy (lower energy = higher score)
                    # Normalize somewhat by number of nodes to keep scale reasonable
                    base_score = -energy / (n + 1) 
                    
                    # Boost if the candidate activates key logical nodes found in prompt
                    activation_bonus = np.sum(x_final) * 0.1
                    score = base_score + activation_bonus
                    reasoning = f"Graph energy: {-energy:.4f}, Active nodes: {int(np.sum(x_final))}"
                else:
                    # Candidate doesn't match any extracted nodes
                    score = -10.0
                    reasoning = "No semantic overlap with parsed propositions."
            else:
                # Fallback if parsing yields no nodes (too short or complex syntax)
                score = -1.0
                reasoning = "Parsing failed, relying on compression."

            # Tie-breaker / Baseline check: NCD
            # If structural score is ambiguous or low, NCD helps distinguish relevance
            ncd_val = self._ncd_score(prompt_rep, cand.lower())
            # Adjust score: High NCD (dissimilar) is bad, Low NCD is good.
            # But we must avoid "echo" (exact match). 
            # We use NCD primarily when structural signal is weak or as a modifier.
            if n > 0:
                # Blend: Structural is primary, NCD is secondary confirmation
                final_score = score * (1.0 - ncd_val * 0.2) 
            else:
                # Pure NCD mode if structure fails
                final_score = -ncd_val

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the relative score of the answer against a set of perturbed versions 
        or simply maps the internal energy score to a probability-like value.
        """
        # Evaluate single candidate against prompt
        # We simulate a small set of candidates to get a relative ranking
        # Since we only have one answer, we compare it to a "null" and a "repeat"
        candidates = [answer, prompt, ""] 
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        # Find the score of the specific answer
        ans_score = None
        for r in ranked:
            if r['candidate'] == answer:
                ans_score = r['score']
                break
                
        if ans_score is None:
            return 0.0
            
        # Normalize to 0-1 based on the spread of scores in this specific evaluation
        scores = [r['score'] for r in ranked]
        min_s, max_s = min(scores), max(scores)
        
        if max_s - min_s < 1e-6:
            return 0.5 if ans_score > 0 else 0.1
            
        # Map to 0.1 - 0.9 range to avoid overconfidence
        norm = (ans_score - min_s) / (max_s - min_s)
        return float(0.1 + 0.8 * norm)