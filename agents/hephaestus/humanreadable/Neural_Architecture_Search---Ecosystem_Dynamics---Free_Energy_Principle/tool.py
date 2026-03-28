import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a variational free-energy reasoner with NAS-optimized weights.
    Mechanism:
    1. Parses prompt/candidates into logical propositions (nodes) and relations (edges).
    2. Constructs sparse adjacency matrices for Implication, Negation, and Ordering.
    3. Uses an evolutionary NAS loop to find optimal weights (w_imp, w_neg, w_ord) that minimize
       the Free Energy (prediction error + entropy) of the belief propagation system.
    4. Scores candidates based on the minimized Free Energy; lower FE = higher score.
    """

    def __init__(self):
        self.max_iters = 10
        self.tol = 1e-3
        self.pop_size = 8
        self.generations = 5
        self.sigma = 0.1

    def _tokenize_and_parse(self, text: str) -> Tuple[List[str], List[Tuple], Dict[str, int]]:
        """Extract propositions and build relation lists."""
        text_lower = text.lower()
        # Simple sentence splitter
        sentences = re.split(r'[.!?]', text_lower)
        propositions = []
        prop_map = {} # text -> index
        relations = [] # (type, src_idx, tgt_idx)
        
        def get_idx(prop: str) -> int:
            prop = prop.strip()
            if not prop: return -1
            if prop not in prop_map:
                prop_map[prop] = len(propositions)
                propositions.append(prop)
            return prop_map[prop]

        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect Negation
            is_neg = bool(re.search(r'\b(not|no|never|cannot)\b', sent))
            
            # Detect Comparatives (A > B, A less than B)
            comp_match = re.search(r'(\w+)\s*(?:is\s+)?(greater|less|more|fewer)\s+(?:than\s+)?(\w+)', sent)
            if comp_match:
                p1, typ, p2 = comp_match.groups()
                idx1, idx2 = get_idx(p1), get_idx(p2)
                if idx1 != -1 and idx2 != -1:
                    # Ord: 1 if p1 > p2, -1 if p1 < p2
                    val = 1 if 'greater' in typ or 'more' in typ else -1
                    relations.append(('ord', idx1, idx2, val))
                continue

            # Detect Conditionals/Causal (if A then B, A causes B)
            # Pattern: A causes B / A leads to B / if A then B
            causal_match = re.search(r'(?:if\s+)?(\w+)\s+(?:causes|leads\s+to|implies|then)\s+(\w+)', sent)
            if causal_match:
                p1, p2 = causal_match.groups()
                idx1, idx2 = get_idx(p1), get_idx(p2)
                if idx1 != -1 and idx2 != -1:
                    relations.append(('imp', idx1, idx2, 1))
                continue
            
            # Generic extraction if no specific relation found, treat as atomic belief
            words = re.findall(r'\b[a-z]+\b', sent)
            if words:
                # Filter stopwords for proposition key
                key_words = [w for w in words if w not in ['the', 'a', 'an', 'is', 'are', 'was', 'were']]
                if key_words:
                    prop_key = " ".join(key_words[:3]) # Simplified proposition
                    idx = get_idx(prop_key)
                    if is_neg and idx != -1:
                         # Mark as negated self-relation or handle via prior? 
                         # For this model, we store negation as a self-loop inhibition or separate flag
                         relations.append(('neg', idx, idx, 1))

        return propositions, relations, prop_map

    def _build_matrices(self, n: int, relations: List) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build sparse COO-like matrices using numpy arrays."""
        if n == 0:
            return np.array([]), np.array([]), np.array([])

        imp_rows, imp_cols, imp_vals = [], [], []
        neg_rows, neg_cols, neg_vals = [], [], []
        ord_rows, ord_cols, ord_vals = [], [], []

        for rel in relations:
            r_type, i, j, val = rel
            if i >= n or j >= n: continue
            if r_type == 'imp':
                imp_rows.append(i); imp_cols.append(j); imp_vals.append(val)
            elif r_type == 'neg':
                neg_rows.append(i); neg_cols.append(j); neg_vals.append(val)
            elif r_type == 'ord':
                ord_rows.append(i); ord_cols.append(j); ord_vals.append(val)

        def make_sparse(rows, cols, vals, size):
            if not rows:
                return np.zeros((size, size))
            mat = np.zeros((size, size))
            for r, c, v in zip(rows, cols, vals):
                mat[r, c] = v
            return mat

        return (make_sparse(imp_rows, imp_cols, imp_vals, n),
                make_sparse(neg_rows, neg_cols, neg_vals, n),
                make_sparse(ord_rows, ord_cols, ord_vals, n))

    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))

    def _propagate(self, Imp, Neg, Ord, w: np.ndarray, b: float) -> float:
        """Run belief propagation and return Free Energy."""
        n = Imp.shape[0]
        if n == 0: return 0.0
        
        belief = np.full(n, 0.5)
        prior = np.full(n, 0.5) # Uniform prior
        
        # Unpack weights
        w_imp, w_neg, w_ord = w
        
        for _ in range(self.max_iters):
            belief_old = belief.copy()
            
            # Message passing
            # Implication: support from predecessors
            msg_imp = Imp.T @ belief 
            # Negation: inhibition (1 - belief of negator)
            msg_neg = 1.0 - (Neg.T @ belief)
            # Ordering: drive based on difference
            msg_ord = self._sigmoid(Ord.T @ (belief - 0.5))
            
            # Update
            activation = w_imp * msg_imp + w_neg * msg_neg + w_ord * msg_ord + b
            belief = self._sigmoid(activation)
            
            if np.linalg.norm(belief - belief_old, 1) < self.tol:
                break
        
        # Free Energy Calculation
        # FE = Prediction Error + Entropy (Negative Entropy to minimize)
        err_term = 0.5 * np.sum((belief - prior) ** 2)
        
        # Entropy term: - sum(p log p + (1-p) log (1-p))
        # We add a small epsilon to avoid log(0)
        eps = 1e-10
        ent_term = -np.sum(belief * np.log(belief + eps) + (1 - belief) * np.log(1 - belief + eps))
        
        return err_term + ent_term

    def _nas_search(self, Imp, Neg, Ord) -> Tuple[np.ndarray, float]:
        """Evolutionary search for optimal weights."""
        n = Imp.shape[0]
        if n == 0:
            return np.array([0.33, 0.33, 0.33]), 0.0

        # Population: [w_imp, w_neg, w_ord, bias]
        pop = np.random.rand(self.pop_size, 4) 
        # Scale bias to [-1, 1], weights [0, 1]
        pop[:, 3] = pop[:, 3] * 2 - 1 
        
        best_fe = float('inf')
        best_w = np.array([0.33, 0.33, 0.33])
        best_b = 0.0

        for gen in range(self.generations):
            fes = []
            for i in range(self.pop_size):
                w = pop[i, :3]
                b = pop[i, 3]
                fe = self._propagate(Imp, Neg, Ord, w, b)
                fes.append(fe)
                
                if fe < best_fe:
                    best_fe = fe
                    best_w = w.copy()
                    best_b = b
            
            # Selection: Keep top 2
            indices = np.argsort(fes)[:2]
            parents = pop[indices]
            
            # Mutation and replacement
            new_pop = []
            for p in parents:
                new_pop.append(p) # Elitism
                for _ in range((self.pop_size - 2) // 2):
                    child = p + np.random.normal(0, self.sigma, 4)
                    child[:3] = np.clip(child[:3], 0, 1) # Clamp weights
                    child[3] = np.clip(child[3], -2, 2)   # Clamp bias
                    new_pop.append(child)
            
            pop = np.array(new_pop[:self.pop_size])

        return best_w, best_b

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Evaluate a single candidate against the prompt."""
        # Combine prompt and candidate for context
        full_text = f"{prompt} {candidate}"
        props, rels, _ = self._tokenize_and_parse(full_text)
        n = len(props)
        
        if n == 0:
            return 0.5, "No logical structure detected."

        Imp, Neg, Ord = self._build_matrices(n, rels)
        w_opt, b_opt = self._nas_search(Imp, Neg, Ord)
        fe = self._propagate(Imp, Neg, Ord, w_opt, b_opt)
        
        # Convert FE to score (lower FE is better)
        # Heuristic scaling: FE usually small positive number
        score = 1.0 / (1.0 + fe)
        
        reason = f"Optimized weights: {w_opt}, Bias: {b_opt:.2f}, FE: {fe:.4f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: calculate scores
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scores.append(score)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        sorted_indices = np.argsort(scores)[::-1]
        return [results[i] for i in sorted_indices]

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._score_candidate(prompt, answer)
        return float(score)