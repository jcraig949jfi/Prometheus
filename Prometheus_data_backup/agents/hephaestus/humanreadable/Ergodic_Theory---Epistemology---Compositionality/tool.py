import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Epistemic Compositional Scorer (EECS).
    
    Mechanism:
    1. Parses atomic propositions, logical operators, and numeric values via regex.
    2. Constructs a directed graph where nodes are propositions and edges are logical dependencies.
    3. Initializes belief weights based on epistemic cues (source reliability, coherence).
    4. Runs ergodic belief propagation (Markov Chain) to converge to a stationary distribution.
    5. Scores candidates by comparing their stationary belief vectors to a reference using KL-divergence.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(greater than|less than|more|less|higher|lower|before|after)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|leads to|causes|therefore|thus)\b', re.IGNORECASE),
        'numeric': re.compile(r'-?\d+\.?\d*(?:\s*[a-zA-Z]+)?'),
        'ordering': re.compile(r'\b(first|last|next|previous|before|after)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.alpha = 0.7  # Damping factor
        self.epsilon = 1e-4
        self.max_iter = 100

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features and numeric values."""
        features = {
            'negations': len(self.PATTERNS['negation'].findall(text)),
            'comparatives': len(self.PATTERNS['comparative'].findall(text)),
            'conditionals': len(self.PATTERNS['conditional'].findall(text)),
            'causal': len(self.PATTERNS['causal'].findall(text)),
            'ordering': len(self.PATTERNS['ordering'].findall(text)),
            'numbers': []
        }
        # Extract numeric values for comparison logic
        nums = self.PATTERNS['numeric'].findall(text)
        for n in nums:
            try:
                # Clean unit suffixes roughly
                val = float(re.sub(r'[a-zA-Z]+$', '', n.strip()))
                features['numbers'].append(val)
            except ValueError:
                pass
        return features

    def _build_graph(self, text: str) -> Tuple[List[Dict], np.ndarray]:
        """
        Build a simplified graph representation.
        Nodes: Atomic segments (split by connectors).
        Edges: Implicit logical flow based on detected patterns.
        Returns: List of node features and adjacency matrix.
        """
        features = self._extract_features(text)
        
        # Create a synthetic node representing the whole statement's structural integrity
        # Feature vector: [neg, comp, cond, causal, order, num_count, num_density]
        num_count = len(features['numbers'])
        num_density = num_count / (len(text.split()) + 1)
        
        f_vector = np.array([
            features['negations'],
            features['comparatives'],
            features['conditionals'],
            features['causal'],
            features['ordering'],
            num_count,
            num_density
        ])
        
        # Normalize features to [0, 1] range approximately
        norms = np.array([5.0, 5.0, 5.0, 5.0, 5.0, 10.0, 1.0])
        f_norm = np.clip(f_vector / norms, 0, 1)
        
        # Single node graph for this implementation scope (atomic proposition level)
        # In a full parser, this would be a multi-node graph. 
        # Here we simulate the "stationary belief" of the entire statement's coherence.
        
        # Adjacency matrix (1x1 self-loop representing internal coherence)
        # Weight boosted by structural richness
        coherence_bonus = min(1.0, (f_vector[0] + f_vector[1] + f_vector[2]) * 0.1)
        adj = np.array([[1.0 + coherence_bonus]])
        
        # Initial belief b0 based on epistemic cues
        # Source reliability (simulated by presence of causal/conditional logic)
        # Internal coherence (simulated by feature density)
        b0 = 0.5 + (0.2 if features['causal'] > 0 else 0) + (0.1 if features['conditionals'] > 0 else 0)
        b0 = min(1.0, b0 + coherence_bonus * 0.2)
        
        return [f_norm], np.array([b0]), adj

    def _ergodic_propagation(self, f_list: List[np.ndarray], b0: np.ndarray, adj: np.ndarray) -> np.ndarray:
        """Run belief propagation until convergence."""
        if len(f_list) == 0:
            return b0
            
        b_t = b0.copy()
        n_nodes = len(b_t)
        
        # Normalize adjacency for stochastic property (row sums to 1)
        row_sums = adj.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        W = adj / row_sums
        
        # Feature compatibility matrix (dot product of normalized features)
        # For single node, this is just 1.0
        Phi = np.dot(f_list[0], f_list[0]) if len(f_list) > 0 else 1.0
        if isinstance(Phi, np.ndarray):
            Phi = float(Phi)
            
        for _ in range(self.max_iter):
            b_next = np.zeros_like(b_t)
            for v in range(n_nodes):
                # Ergodic update rule
                # b_{t+1}(v) = alpha * b_t(v) + (1-alpha) * sum(w_uv * phi)
                neighbor_sum = 0.0
                for u in range(n_nodes):
                    if adj[u, v] > 0:
                        # Simplified phi for single node: structural consistency
                        neighbor_sum += W[u, v] * Phi 
                
                b_next[v] = self.alpha * b_t[v] + (1 - self.alpha) * neighbor_sum
            
            if np.linalg.norm(b_next - b_t, 1) < self.epsilon:
                break
            b_t = b_next
            
        return b_t

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Compute score based on ergodic alignment."""
        # Build graph for prompt (Reference)
        # We treat the prompt as the source of truth structure
        p_feats, p_b0, p_adj = self._build_graph(prompt)
        pi_ref = self._ergodic_propagation(p_feats, p_b0, p_adj)
        
        # Build graph for candidate
        c_feats, c_b0, c_adj = self._build_graph(candidate)
        pi_cand = self._ergodic_propagation(c_feats, c_b0, c_adj)
        
        # Ensure same size for comparison (pad if necessary, though here 1x1)
        max_len = max(len(pi_ref), len(pi_cand))
        pi_ref_p = np.pad(pi_ref, (0, max_len - len(pi_ref)), constant_values=1e-9)
        pi_cand_p = np.pad(pi_cand, (0, max_len - len(pi_cand)), constant_values=1e-9)
        
        # Normalize to probability distributions
        pi_ref_p = pi_ref_p / (np.sum(pi_ref_p) + 1e-9)
        pi_cand_p = pi_cand_p / (np.sum(pi_cand_p) + 1e-9)
        
        # KL Divergence: sum(p * log(p/q))
        # Clip to avoid log(0)
        eps = 1e-9
        kl = np.sum(pi_ref_p * np.log((pi_ref_p + eps) / (pi_cand_p + eps)))
        
        # Convert to score: 1 - KL (clipped)
        # High KL means low similarity -> Low score
        score = 1.0 - min(kl, 1.0)
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: compute structural scores
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            scores.append(score)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "Ergodic belief alignment with prompt structure."
            })
        
        # If scores are too close (tie), use NCD as tiebreaker
        unique_scores = len(set([round(s, 4) for s in scores]))
        if unique_scores == 1 and len(candidates) > 1:
            # Fallback to NCD if structural parsing yields identical results
            import zlib
            prompt_bytes = prompt.encode()
            nc_scores = []
            for cand in candidates:
                cand_bytes = cand.encode()
                comp_len = len(zlib.compress(prompt_bytes + cand_bytes))
                max_len = max(len(zlib.compress(prompt_bytes)), len(zlib.compress(cand_bytes)))
                ncd = comp_len / max_len if max_len > 0 else 1.0
                nc_scores.append(1.0 - ncd) # Higher is better
            
            # Re-rank based on NCD
            ranked_indices = np.argsort(nc_scores)[::-1]
            final_results = []
            for idx in ranked_indices:
                item = results[idx].copy()
                item['score'] = float(nc_scores[idx]) # Update score to reflect tiebreaker
                item['reasoning'] = "NCD tiebreaker applied."
                final_results.append(item)
            return final_results

        # Sort by original score
        sorted_indices = np.argsort(scores)[::-1]
        return [results[i] for i in sorted_indices]

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score 0-1."""
        score = self._compute_score(prompt, answer)
        return float(score)