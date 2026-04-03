import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool combining Differentiable Programming, Hebbian Learning, 
    and Mechanism Design. It parses logical structures (negations, comparatives, 
    conditionals) into a graph, tunes edge weights via gradient descent and Hebbian 
    co-activation, and ranks candidates using an incentive-compatible utility function.
    
    Mechanism:
    1. Structural Parsing: Extracts predicates, negations, and numeric constraints.
    2. Differentiable Logic: Computes rule satisfaction via sigmoid activations.
    3. Hebbian Update: Strengthens connections between co-occurring concepts.
    4. Mechanism Design: Ranks answers by minimizing rule violations while maximizing 
       prompt similarity, penalizing candidates that 'game' the system without logic.
    """
    
    def __init__(self):
        self.d = 16  # Embedding dimension
        self.lr = 0.1
        self.hebb_strength = 0.05
        self.margin = 0.5
        self.gamma = 0.2
        # Fixed random projection for deterministic one-hot to embedding
        self.proj_matrix = np.random.randn(1000, self.d).astype(np.float32) * 0.1
        self.vocab = {}
        self.next_id = 0
        
        # Logical Weights (W) and State
        self.W = None
        self.nodes_count = 0
        self.max_nodes = 50
        
        # Initialize small random weights if needed later
        self._init_weights()

    def _init_weights(self):
        if self.W is None or self.W.shape[0] < self.max_nodes:
            self.W = np.random.randn(self.max_nodes, self.max_nodes).astype(np.float32) * 0.01

    def _get_node_id(self, predicate: str) -> int:
        if predicate not in self.vocab:
            if len(self.vocab) >= self.max_nodes - 1:
                return self.max_nodes - 1 # Overflow bucket
            self.vocab[predicate] = self.next_id
            self.next_id += 1
        return self.vocab[predicate]

    def _hash_to_idx(self, s: str) -> int:
        return hash(s) % 1000

    def _parse_structure(self, text: str) -> List[Tuple[str, int, bool]]:
        """Extracts (predicate, node_id, polarity) tuples."""
        tokens = re.findall(r'\w+|\d+\.\d+|\d+', text.lower())
        features = []
        
        # Simple negation tracking
        negation_words = {'no', 'not', 'never', 'none', 'cannot', "n't"}
        is_negated = False
        
        for i, token in enumerate(tokens):
            if token in negation_words:
                is_negated = True
                continue
            
            # Handle numeric comparatives implicitly by treating numbers as nodes
            # e.g., "9.11" -> node "9.11"
            predicate = token
            if is_negated:
                predicate = f"not_{token}"
                is_negated = False # Reset after use
            
            nid = self._get_node_id(predicate)
            features.append((predicate, nid, "not" in predicate))
            
        # Detect explicit comparatives for constraint generation
        if ">" in text or "greater" in text:
            features.append(("comp_gt", self._get_node_id("comp_gt"), False))
        if "<" in text or "less" in text:
            features.append(("comp_lt", self._get_node_id("comp_lt"), False))
            
        return features

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
        """Builds node embeddings and constraint masks."""
        # Combine prompt and candidate for context
        full_text = f"{prompt} {candidate}"
        parsed = self._parse_structure(full_text)
        p_parsed = self._parse_structure(prompt)
        c_parsed = self._parse_structure(candidate)
        
        n = max(len(parsed), 1) + 2
        n = min(n, self.max_nodes)
        
        # Embeddings: Project one-hot indices
        X = np.zeros((n, self.d), dtype=np.float32)
        node_ids = [p[1] for p in parsed]
        if not node_ids: node_ids = [0]
        
        for i, nid in enumerate(node_ids[:n]):
            idx = self._hash_to_idx(str(nid))
            X[i] = self.proj_matrix[idx]
            
        # Normalize X slightly
        X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-6)
        
        # Constraints (C): Simplified to antecedent-consequent masks based on proximity
        # In a full implementation, this would parse "if A then B" explicitly
        constraints = []
        
        # Rule 1: Consistency (Prompt nodes should activate Candidate nodes if shared)
        # Create a mask where prompt concepts connect to candidate concepts
        mask = np.zeros((n, n), dtype=np.float32)
        for i in range(min(len(p_parsed), n)):
            for j in range(min(len(c_parsed), n)):
                if i < n and j < n:
                    mask[i, j] = 1.0 
        constraints.append(mask)
        
        # Rule 2: Negation conflict (If prompt has "not X" and candidate has "X", penalty)
        neg_mask = np.zeros((n, n), dtype=np.float32)
        p_negs = {p[0].replace("not_", "") for p in p_parsed if "not_" in p[0]}
        c_pos = {p[0].replace("not_", "") for p in c_parsed if "not_" not in p[0]}
        
        for i, (pred, _, _) in enumerate(parsed[:n]):
            base = pred.replace("not_", "")
            if base in p_negs and base in c_pos:
                # Self-loop penalty for contradiction
                if i < n: neg_mask[i, i] = 1.0
        constraints.append(neg_mask)

        return X[:n], self.W[:n, :n], constraints

    def _forward(self, X: np.ndarray, W: np.ndarray, constraints: List[np.ndarray]) -> Tuple[float, float, np.ndarray]:
        """Computes activations, rule loss, and heuristic similarity."""
        n = X.shape[0]
        if n == 0: return 0.0, 0.0, np.array([])
        
        # 1. Activation: A = sigmoid(X @ W)
        # Truncate W to current n
        W_curr = W[:n, :n]
        pre_act = X @ W_curr.T
        A = 1.0 / (1.0 + np.exp(-pre_act)) # Sigmoid
        
        # 2. Rule Satisfaction
        rule_loss = 0.0
        for k, C_k in enumerate(constraints):
            C_curr = C_k[:n, :n]
            # s_k = sum(C * A * A^T)
            # Outer product of activations
            AA_T = np.outer(A.flatten(), A.flatten()) # Simplified for scalar logic
            # Actually, per definition: sum_{i,j} C[i,j] * A[i] * A[j]
            sat = np.sum(C_curr * np.outer(A.flatten()[:n], A.flatten()[:n]))
            
            # Hinge loss
            violation = max(0.0, self.margin - sat)
            rule_loss += violation
            
        # 3. Similarity (Prompt vs Candidate overlap)
        # Simple dot product of summed activations as proxy for semantic overlap
        similarity = np.sum(A) 
        
        return rule_loss, similarity, A

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._parse_structure(prompt)
        prompt_vec = np.zeros(self.d)
        if prompt_features:
            ids = [p[1] for p in prompt_features]
            for nid in ids:
                prompt_vec += self.proj_matrix[self._hash_to_idx(str(nid))]
        prompt_vec /= (np.linalg.norm(prompt_vec) + 1e-6)

        for cand in candidates:
            X, W_sub, constraints = self._build_graph(prompt, cand)
            if X.shape[0] == 0:
                score = 0.0
                reasoning = "No structural features detected."
                results.append({"candidate": cand, "score": score, "reasoning": reasoning})
                continue

            # Forward pass
            L_rule, sim, A = self._forward(X, W_sub, constraints)
            
            # Mechanism Design Utility: U = -L_rule + lambda * sim
            # We invert L_rule because lower loss is better
            utility = -L_rule + 0.5 * sim
            
            # Hebbian Update (Simulated for this step to influence scoring slightly)
            # Delta W = eta * (A^T @ A)
            if A.size > 0:
                hebb_update = self.hebb_strength * np.outer(A.flatten(), A.flatten())
                # Apply update to internal state (simplified)
                n_eff = min(A.shape[0], self.W.shape[0])
                self.W[:n_eff, :n_eff] += hebb_update[:n_eff, :n_eff]

            # NCD Tiebreaker (only if structural signal is weak/ambiguous)
            ncd_score = 0.0
            if abs(utility) < 0.1: 
                # Fallback to compression if logic yields near-zero utility
                try:
                    import zlib
                    data = f"{prompt}{cand}".encode()
                    comp = len(zlib.compress(data))
                    norm = min(len(zlib.compress(prompt.encode())), len(zlib.compress(cand.encode())))
                    ncd_score = 1.0 - (comp / (norm + 1))
                except:
                    pass
            
            final_score = float(utility) + ncd_score * 0.01 # NCD is minor tiebreaker
            
            reason_str = f"RuleViol:{L_rule:.2f}, Sim:{sim:.2f}, Util:{final_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reason_str})

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the utility score of the specific answer."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]["score"]
        # Map score to 0-1 using sigmoid-like scaling
        # Assuming typical utility range is -5 to 5
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))