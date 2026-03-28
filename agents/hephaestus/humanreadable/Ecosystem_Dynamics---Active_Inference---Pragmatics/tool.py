import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer combining Structural Parsing, 
    Active Inference (Free Energy minimization), and Pragmatic weighting.
    
    Mechanism:
    1. Parses propositional nodes from text using regex (concepts, numbers, modality).
    2. Constructs a relational graph where edge weights are modulated by Gricean 
       pragmatic implicatures (clarity, relevance).
    3. Computes 'Expected Free Energy' (G) as the sum of:
       - Ambiguity (KL divergence between context posterior and keystone prior).
       - Risk (prediction error across causal links).
    4. Scores candidates by -G. Lower energy = higher score.
    5. Uses NCD only as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|none|neither)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|twice|double)\b|[<>]', re.I),
            'conditional': re.compile(r'\b(if|unless|provided|then|else)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'modal': re.compile(r'\b(must|should|might|could|will|would)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|most|every|any)\b', re.I)
        }
        self.roles = ['agent', 'patient', 'condition', 'consequence']

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Extract propositional nodes with features."""
        nodes = []
        text_lower = text.lower()
        
        # Feature extraction
        has_neg = 1.0 if self.patterns['negation'].search(text_lower) else -1.0
        has_comp = 1.0 if self.patterns['comparative'].search(text_lower) else 0.0
        has_cond = 1.0 if self.patterns['conditional'].search(text_lower) else 0.0
        has_causal = 1.0 if self.patterns['causal'].search(text_lower) else 0.0
        has_modal = 1.0 if self.patterns['modal'].search(text_lower) else 0.0
        
        # Extract numeric value (priority to first found)
        nums = self.patterns['numeric'].findall(text)
        num_val = float(nums[0]) if nums else 0.0
        
        # Simple role assignment based on keywords
        role_idx = 0 # Default agent
        if has_cond > 0: role_idx = 2 # condition
        elif has_causal > 0: role_idx = 3 # consequence
        
        # Create a node representing the core proposition of the sentence
        # Feature vector: [polarity, modality(certainty), numeric, role_encoded]
        # Modality: modal verbs increase certainty weight in this simplified model
        certainty = 0.8 if has_modal == 0 else 0.5 # Hedges lower certainty slightly in this model
        if has_neg == -1.0: certainty *= 0.9 
        
        f_vec = [has_neg, certainty, num_val, role_idx]
        
        # We treat the whole text segment as a primary node for this scope
        nodes.append({
            'text': text[:50], # Truncate for display
            'f': np.array(f_vec),
            'role': role_idx,
            'polarity': has_neg
        })
        return nodes

    def _build_graph(self, prompt_nodes: List[Dict], answer_nodes: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix W and feature matrix F."""
        all_nodes = prompt_nodes + answer_nodes
        n = len(all_nodes)
        if n == 0:
            return np.array([]), np.array([])
            
        F = np.stack([node['f'] for node in all_nodes])
        W = np.zeros((n, n))
        
        # Pragmatic Implicature Scoring (Gricean Maxims)
        # Relation: Prompt nodes connect to Answer nodes
        # Manner/Quality: Penalize if answer contradicts prompt polarity without causal bridge
        
        for i, p_node in enumerate(prompt_nodes):
            for j, a_node in enumerate(answer_nodes):
                idx_j = len(prompt_nodes) + j
                
                # Base relation: Causal/Logical flow
                base_weight = 0.5
                
                # Gricean Quantity/Relevance: Numeric alignment
                if p_node['f'][2] != 0 and a_node['f'][2] != 0:
                    if abs(p_node['f'][2] - a_node['f'][2]) < 1e-6:
                        base_weight += 0.4 # Exact match bonus
                    else:
                        base_weight -= 0.2 # Mismatch penalty
                
                # Gricean Quality: Polarity consistency
                if p_node['polarity'] != a_node['polarity']:
                    # If polarities differ, we need a causal bridge or conditional to be valid
                    if p_node['role'] == 2 or a_node['role'] == 3: # If conditional/consequence involved
                        base_weight *= 0.8 # Acceptable nuance
                    else:
                        base_weight *= 0.2 # Likely contradiction
                
                W[i, idx_j] = max(0, base_weight)
                
        # Symmetrize for undirected aspects of semantic similarity, keep directed for logic
        W = (W + W.T) / 2
        np.fill_diagonal(W, 0) # No self-loops
        
        return W, F

    def _compute_free_energy(self, W: np.ndarray, F: np.ndarray) -> float:
        """Calculate G = Ambiguity + Risk."""
        if W.size == 0 or F.size == 0:
            return 10.0 # High energy for empty
            
        n = F.shape[0]
        
        # 1. Priors (Ecosystem Dynamics: Keystone nodes)
        # Nodes with high connectivity or high magnitude features are keystones
        k = np.array([0.5, 0.5, 0.5, 0.5]) # Learned-like weights
        scores = np.dot(F, k) 
        # Boost nodes with high out-degree in W (simulated)
        connectivity = np.sum(W, axis=1)
        scores += connectivity
        p = scores - np.max(scores) # Stability for softmax
        p = np.exp(p) / np.sum(np.exp(p)) + 1e-9 # Prior distribution
        
        # 2. Posterior (Active Inference: Contextual expectation)
        # q_i proportional to weighted sum of neighbors
        if np.sum(W) == 0:
            q = np.ones(n) / n
        else:
            q_raw = np.dot(W, F)
            # Normalize rows then sum to get node importance in context
            q_norm = np.linalg.norm(q_raw, axis=1)
            q = q_norm / (np.sum(q_norm) + 1e-9) + 1e-9
            
        # Ensure normalization
        p = p / np.sum(p)
        q = q / np.sum(q)

        # 3. Ambiguity (Entropy / KL Divergence)
        # D_KL(q || p)
        kl_div = np.sum(q * np.log(q / p))
        
        # 4. Risk (Prediction Error)
        # Sum of squared differences across edges weighted by W
        risk = 0.0
        for i in range(n):
            for j in range(n):
                if W[i,j] > 0:
                    diff = np.linalg.norm(F[i] - F[j])
                    risk += W[i,j] * (diff ** 2)
                    
        return kl_div + risk

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_nodes = self._extract_nodes(prompt)
        results = []
        
        for cand in candidates:
            a_nodes = self._extract_nodes(cand)
            W, F = self._build_graph(p_nodes, a_nodes)
            
            # Primary Score: Negative Free Energy
            G = self._compute_free_energy(W, F)
            score = -G
            
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"Free Energy: {G:.4f}",
                'nodes_count': len(p_nodes) + len(a_nodes)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                ncd_i = self._ncd(prompt, results[i]['candidate'])
                ncd_next = self._ncd(prompt, results[i+1]['candidate'])
                # Lower NCD (more similar/compressible together) breaks tie
                if ncd_i < ncd_next:
                    results[i], results[i+1] = results[i+1], results[i]
                    
        # Format output
        return [{
            'candidate': r['candidate'],
            'score': float(r['score']),
            'reasoning': r['reasoning']
        } for r in results]

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy minimization."""
        p_nodes = self._extract_nodes(prompt)
        a_nodes = self._extract_nodes(answer)
        W, F = self._build_graph(p_nodes, a_nodes)
        
        if W.size == 0:
            return 0.5
            
        G = self._compute_free_energy(W, F)
        
        # Map Free Energy to Confidence
        # Low G -> High Confidence. 
        # Heuristic mapping: G < 1.0 -> 0.9+, G > 5.0 -> 0.1
        # Using sigmoid-like decay
        confidence = 1.0 / (1.0 + np.exp(G - 2.0))
        return float(np.clip(confidence, 0.0, 1.0))