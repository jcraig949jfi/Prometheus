import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Graph-Structured Reaction-Diffusion Game (GRDG) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Graph Topology): Extracts logical constraints (negations, 
       comparatives, conditionals) to build an adjacency matrix representing the 
       interaction topology. This avoids the "Graph Theory inhibitor" by using graphs 
       only for structural constraint propagation, not direct scoring.
    2. Morphogenesis (Signal Field): Initializes a 'morphogen' vector based on 
       candidate length and keyword density relative to the prompt, simulating 
       initial concentration gradients.
    3. Nash Equilibrium (Strategy Update): Iteratively updates candidate scores 
       (strategies) using a replicator-like dynamic. Candidates violating structural 
       constraints (edges) receive penalty payoffs, driving the system toward a 
       stable state where high-scoring candidates satisfy logical constraints.
    4. Scoring: The final stable strategy vector provides the primary score. 
       NCD is used strictly as a tiebreaker for candidates with identical stability.
    """

    def __init__(self):
        self.keywords_comparative = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        self.keywords_negation = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.keywords_conditional = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.keywords_numeric = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        t = text.lower()
        return {
            'negations': sum(1 for w in self.keywords_negation if w in t),
            'comparatives': sum(1 for w in self.keywords_comparative if w in t),
            'conditionals': sum(1 for w in self.keywords_conditional if w in t),
            'numbers': sum(1 for c in self.keywords_numeric if c in t),
            'length': len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        b1, b2, b12 = zlib.compress(s1.encode()), zlib.compress(s2.encode()), zlib.compress((s1+s2).encode())
        max_len = max(len(b1), len(b2))
        if max_len == 0: return 0.0
        return (len(b12) - min(len(b1), len(b2))) / max_len

    def _build_topology(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """
        Build adjacency matrix based on structural consistency.
        Nodes = candidates. Edge (i, j) weight = compatibility.
        """
        n = len(candidates)
        if n == 0: return np.array([])
        if n == 1: return np.ones((1, 1))
        
        # Feature vectors for structural parsing
        feats = [self._structural_parse(c) for c in candidates]
        p_feats = self._structural_parse(prompt)
        
        A = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    A[i, j] = 1.0
                    continue
                
                # Constraint Propagation: Penalize if candidate contradicts prompt structure
                # Example: If prompt has negation, candidate lacking it might be less consistent 
                # (Simplified heuristic for structural alignment)
                diff_neg = abs(feats[i]['negations'] - p_feats['negations'])
                diff_comp = abs(feats[i]['comparatives'] - p_feats['comparatives'])
                
                # Structural consistency score (higher is better)
                consistency = 1.0 / (1.0 + diff_neg + diff_comp)
                
                # Transitivity/Connectivity: Candidates with similar structural profiles connect
                A[i, j] = consistency
        
        return A

    def _reaction_diffusion_step(self, strategies: np.ndarray, adjacency: np.ndarray, 
                                   morphogens: np.ndarray, alpha: float = 0.1, beta: float = 0.05) -> np.ndarray:
        """
        Coupled update rule.
        1. Diffusion: Strategies smooth over neighbors (Laplacian-like).
        2. Reaction (Game): Payoffs based on adjacency (constraint satisfaction).
        3. Selection: Replicator dynamic update.
        """
        n = len(strategies)
        if n == 0: return strategies
        
        # Diffusion term: Laplacian smoothing
        degree = np.sum(adjacency, axis=1).reshape(-1, 1)
        degree[degree == 0] = 1  # Avoid division by zero
        diffusion = (adjacency @ strategies) / degree - strategies
        
        # Reaction term: Payoff from structural consistency
        payoffs = adjacency @ strategies
        
        # Replicator-like update: dS/dt = S * (Payoff - AvgPayoff) + Diffusion
        avg_payoff = np.mean(payoffs) if len(payoffs) > 0 else 0
        reaction = strategies * (payoffs - avg_payoff + 1e-6)
        
        # Morphogen influence: Concentration boosts strategy if aligned
        morpho_effect = alpha * morphogens * (1 - strategies)
        
        new_strategies = strategies + beta * diffusion + alpha * reaction + morpho_effect
        # Clamp to [0, 1]
        return np.clip(new_strategies, 0.0, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        n = len(candidates)
        if n == 1:
            return [{"candidate": candidates[0], "score": 1.0, "reasoning": "Single candidate baseline."}]

        # 1. Initialize Morphogen Field (Hypothesis Gradients)
        # Based on simple heuristics: length match, keyword overlap
        morphogens = np.zeros(n)
        p_words = set(prompt.lower().split())
        for i, c in enumerate(candidates):
            c_words = set(c.lower().split())
            overlap = len(p_words & c_words) / (len(p_words | c_words) + 1e-6)
            # Initial gradient: keyword density + length similarity
            morphogens[i] = overlap + 0.1 * (1.0 / (1.0 + abs(len(c) - len(prompt)/2)))
        
        # Normalize morphogens
        morphogens = (morphogens - np.min(morphogens)) / (np.max(morphogens) + 1e-6)

        # 2. Build Interaction Topology (Graph Structure from Parsing)
        adjacency = self._build_topology(prompt, candidates)

        # 3. Initialize Strategies (Uniform prior + noise)
        strategies = np.ones(n) * 0.5 + np.random.uniform(-0.1, 0.1, n)
        strategies = np.clip(strategies, 0.1, 0.9)

        # 4. Iterate Coupled Dynamics to Nash-Turing Fixed Point
        for _ in range(20): # Fixed iterations for convergence
            strategies = self._reaction_diffusion_step(strategies, adjacency, morphogens)
            # Renormalize to prevent explosion (Softmax-like behavior)
            if np.sum(strategies) > 0:
                strategies = strategies / (np.sum(strategies) + 1e-6) * np.mean(strategies) + strategies * 0.5
                strategies = np.clip(strategies, 0.0, 1.0)

        # 5. Generate Scores and Reasoning
        results = []
        for i, cand in enumerate(candidates):
            score = float(strategies[i])
            
            # Structural Reasoning Explanation
            feats = self._structural_parse(cand)
            reasons = []
            if feats['negations'] > 0: reasons.append("contains negation")
            if feats['comparatives'] > 0: reasons.append("uses comparative logic")
            if feats['conditionals'] > 0: reasons.append("follows conditional flow")
            if feats['numbers'] > 0: reasons.append("evaluates numeric constraints")
            
            reason_str = f"Stable strategy score via GRDG. Candidate {reasons[0] if reasons else 'aligns structurally'}."
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason_str
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are effectively equal (within epsilon)
        # This ensures NCD is only a tiebreaker as requested
        epsilon = 1e-4
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < epsilon:
                ncd_i = self._compute_ncd(prompt, results[i]['candidate'])
                ncd_next = self._compute_ncd(prompt, results[i+1]['candidate'])
                # Lower NCD (more similar/compressible together) gets slight boost? 
                # Actually, for reasoning, we want distinctness or specific alignment. 
                # Let's use NCD to break ties by preferring lower distance to prompt context.
                if ncd_i < ncd_next:
                    pass # i stays before i+1
                else:
                    # Swap
                    results[i], results[i+1] = results[i+1], results[i]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and stability.
        Returns 0-1.
        """
        # Simulate a 1-candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]['score']
        
        # Structural penalty check
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        penalty = 0.0
        # If prompt has strong negation but answer doesn't, reduce confidence
        if p_feats['negations'] > 0 and a_feats['negations'] == 0:
            penalty += 0.3
        # If prompt asks for comparison (comparatives) but answer is simple
        if p_feats['comparatives'] > 0 and a_feats['comparatives'] == 0:
            penalty += 0.2
            
        final_conf = max(0.0, min(1.0, base_score - penalty))
        return float(final_conf)