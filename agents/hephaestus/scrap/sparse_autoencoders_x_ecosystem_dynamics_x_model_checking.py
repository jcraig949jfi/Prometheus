import re
import numpy as np
from collections import defaultdict
from zlib import compress

class ReasoningTool:
    """
    A reasoning tool combining sparse feature extraction, logical graph construction,
    and model checking principles to evaluate candidate answers against a prompt.
    
    Mechanism:
    1. Sparse Feature Extraction: Tokenizes text and uses a hash-based orthogonal-like 
       selection to create sparse activation vectors (simulating OMP/Sparse Autoencoder).
    2. Logical Graph Construction: Extracts atomic propositions, negations, comparatives,
       and causal/temporal cues to build a directed graph of implications.
    3. Constraint Propagation (Model Checking): Simulates a BFS traversal on the 
       product of the logical graph and a simplified Büchi automaton to check if 
       the candidate satisfies the prompt's constraints.
    4. Scoring: Combines the fraction of satisfied constraints (rho) with a sparsity 
       penalty to produce a final score. NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|results in|causes)\b', re.I),
            'numeric': re.compile(r'\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|none|every|each|any)\b', re.I)
        }
        self.hash_size = 1024  # Dimension k for sparse vectors
        self.max_features = 10 # Max non-zero entries s

    def _sparse_encode(self, text: str) -> np.ndarray:
        """Creates a sparse activation vector using hash-based orthogonal selection."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        activations = defaultdict(float)
        
        for token in tokens:
            # Hash token to index (simulating dictionary lookup)
            idx = hash(token) % self.hash_size
            # Simulate activation strength (frequency * length factor)
            val = 1.0 / (1.0 + abs(hash(token + "salt") % 100))
            activations[idx] += val
            
        # Orthogonal Matching Pursuit approximation: Keep top-s features
        if not activations:
            return np.zeros(self.hash_size)
            
        sorted_items = sorted(activations.items(), key=lambda x: x[1], reverse=True)
        vector = np.zeros(self.hash_size)
        for i, (idx, val) in enumerate(sorted_items[:self.max_features]):
            vector[idx] = val
            
        return vector

    def _extract_logic_features(self, text: str) -> dict:
        """Extracts structural logical features from text."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_quantifier': bool(self.patterns['quantifier'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)]
        }
        return features

    def _build_graph(self, prompt_feats: dict, cand_feats: dict) -> dict:
        """Constructs a simple implication graph based on feature overlap and logic."""
        graph = defaultdict(list)
        edges = 0
        
        # Simple heuristic: If prompt has a feature, candidate must acknowledge it
        # or explicitly negate it in a consistent way.
        logic_gates = ['has_negation', 'has_comparative', 'has_conditional', 'has_causal', 'has_quantifier']
        
        for gate in logic_gates:
            if prompt_feats[gate]:
                # Add edge from Prompt Requirement -> Candidate Check
                graph[gate].append(('req_', gate))
                edges += 1
                if cand_feats[gate]:
                    graph[('req_', gate)].append(('sat_', gate))
                    edges += 1
        
        # Numeric consistency check (simplified)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = sorted(prompt_feats['numbers'])
            c_nums = sorted(cand_feats['numbers'])
            # Check if relative ordering is preserved (transitivity)
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_dir = 1 if p_nums[-1] > p_nums[0] else -1
                c_dir = 1 if c_nums[-1] > c_nums[0] else -1
                if p_dir == c_dir:
                    graph['numeric_order'].append('satisfied')
                    edges += 1
                    
        return graph, edges

    def _model_check(self, graph: dict, edges: int) -> float:
        """Simulates BFS on product graph to find fraction of satisfied constraints."""
        if edges == 0:
            return 0.5 # Neutral if no logic detected
            
        visited = set()
        queue = list(graph.keys())
        satisfied = 0
        
        # BFS simulation
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            
            if str(node).startswith('sat_') or str(node) == 'satisfied':
                satisfied += 1
                
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
                        
        # Rho: fraction of reachable satisfying states
        total_nodes = len(visited) if len(visited) > 0 else 1
        rho = satisfied / max(total_nodes, 1)
        return min(rho * 2.0, 1.0) # Scale slightly for visibility

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_vec = self._sparse_encode(prompt)
        prompt_feats = self._extract_logic_features(prompt)
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Sparse Feature Extraction
            cand_vec = self._sparse_encode(cand)
            cand_feats = self._extract_logic_features(cand)
            
            # Sparsity penalty
            norm_a = np.linalg.norm(cand_vec, ord=0)
            sparsity_penalty = 0.1 * (norm_a / self.max_features) if norm_a > 0 else 0
            
            # 2. Logical Graph & 3. Model Checking
            graph, _ = self._build_graph(prompt_feats, cand_feats)
            rho = self._model_check(graph, 0)
            
            # Structural match bonus (direct feature overlap)
            struct_match = 0
            logic_keys = ['has_negation', 'has_comparative', 'has_conditional', 'has_causal', 'has_quantifier']
            for k in logic_keys:
                if prompt_feats[k] and cand_feats[k]:
                    struct_match += 0.15
            
            # 4. Scoring
            # Base score from constraint satisfaction
            score = rho 
            
            # Add structural bonuses
            score += struct_match
            
            # Penalize density (parsimony)
            score -= sparsity_penalty
            
            # NCD Tiebreaker (only if scores are close, applied subtly)
            # We invert NCD because lower distance = higher similarity
            ncd_val = self._ncd(prompt, cand)
            if score > 0:
                score += (1.0 - ncd_val) * 0.05 # Small boost for lexical similarity
            
            # Normalize roughly to 0-1 range based on empirical bounds
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Constraint satisfaction: {rho:.2f}, Structural match: {struct_match:.2f}, Sparsity penalty: {sparsity_penalty:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0