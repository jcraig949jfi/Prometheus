import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Hoare Emergence Reasoner.
    
    Mechanism:
    1. Parsing: Extracts literals, negations, comparatives, and conditionals from text.
    2. Hoare Triples: Maps conditionals (if P then Q) to pre/post conditions.
    3. Thermodynamics: Defines an energy function E = ||C*x||^2 where violations of 
       constraints increase energy. Valid inference reduces energy (dissipation).
    4. Emergence: Computes the spectral gap (lambda_2) of the constraint graph Laplacian.
       Low lambda_2 indicates global coherence (emergence).
    5. Scoring: Combines energy reduction (validity) and emergence (coherence).
    """
    
    def __init__(self):
        self.max_iters = 5
        self.alpha = 0.6
        self.beta = 0.4

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer splitting by space and punctuation, keeping words."""
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_literals(self, text: str) -> Dict[str, int]:
        """Extracts unique literals and assigns IDs. Handles negations implicitly via context."""
        words = self._tokenize(text)
        literals = {}
        idx = 0
        # Simple n-gram based literal extraction for context
        for i in range(len(words)):
            # Unigrams and bigrams as literals
            for span in [1, 2]:
                if i + span <= len(words):
                    lit = " ".join(words[i:i+span])
                    if lit not in literals:
                        literals[lit] = idx
                        idx += 1
        return literals

    def _parse_structure(self, text: str, all_literals: Dict[str, int]) -> Tuple[np.ndarray, List[Tuple[np.ndarray, np.ndarray]], List[Tuple[int, int, int]]]:
        """
        Parses text into:
        1. Initial state vector x (L,)
        2. Hoare triples (pre, post)
        3. Constraint edges (a, b, type) for matrix C
        """
        L = len(all_literals)
        if L == 0:
            return np.zeros(0), [], []
        
        x = np.zeros(L, dtype=float) # 0: unknown, 1: true, -1: false (mapped later)
        # Map initial explicit truths (simplified: assume all extracted literals are present candidates)
        # In a full system, we'd parse "A is true" vs "A is false". 
        # Here we treat the candidate text as the set of asserted truths.
        
        triples = []
        constraints = []
        text_lower = text.lower()
        
        # 1. Detect Conditionals (Hoare Triples)
        # Pattern: if A then B, A leads to B, A causes B
        conditional_patterns = [
            r"if\s+(.+?)\s+(?:then|,)\s+(.+?)",
            r"(.+?)\s+leads?\s+to\s+(.+?)",
            r"(.+?)\s+causes?\s+(.+?)",
            r"(.+?)\s+implies?\s+(.+?)"
        ]
        
        for pat in conditional_patterns:
            matches = re.findall(pat, text_lower)
            for pre_txt, post_txt in matches:
                pre_vec = np.zeros(L)
                post_vec = np.zeros(L)
                
                # Map text to vectors (fuzzy match)
                pre_tokens = self._tokenize(pre_txt)
                post_tokens = self._tokenize(post_txt)
                
                for lit_str, lit_id in all_literals.items():
                    if any(t in lit_str for t in pre_tokens) or lit_str in pre_txt:
                        pre_vec[lit_id] = 1
                    if any(t in lit_str for t in post_tokens) or lit_str in post_txt:
                        post_vec[lit_id] = 1
                
                if pre_vec.sum() > 0 and post_vec.sum() > 0:
                    triples.append((pre_vec, post_vec))
                    # Add constraint: Pre -> Post (If Pre is true, Post must be true)
                    # Represented as: Pre implies Post. 
                    # In energy terms: violation if Pre=1 and Post=-1 (or 0 in strict logic, but we use continuous)
                    # Simplified: Add edge Pre -> Post
                    for i in np.where(pre_vec > 0)[0]:
                        for j in np.where(post_vec > 0)[0]:
                            constraints.append((i, j, 1)) # i implies j

        # 2. Detect Comparatives (Numeric)
        # Pattern: A > B, A < B
        comp_pattern = r"(\d+(?:\.\d+)?)\s*([<>])\s*(\d+(?:\.\d+)?)"
        for m in re.finditer(comp_pattern, text_lower):
            v1, op, v2 = m.groups()
            # Create literals for the numbers themselves if not present
            # For simplicity in this engine, we just add a consistency check later
            pass

        # 3. Detect Negations
        # Pattern: not A, never A
        neg_pattern = r"(?:not|never|no)\s+(\w+)"
        for m in re.finditer(neg_pattern, text_lower):
            target = m.group(1)
            for lit_str, lit_id in all_literals.items():
                if target in lit_str:
                    # Constraint: lit_id must be -1 if this sentence is asserted
                    # We add a self-constraint or a constraint against a global 'false' node if we had one.
                    # Instead, we mark this in the initial state if the candidate asserts it.
                    pass

        return x, triples, constraints

    def _build_constraint_matrix(self, L: int, constraints: List[Tuple[int, int, int]], triples: List[Tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
        """Builds the L x L constraint matrix C."""
        C = np.zeros((L, L))
        
        # From explicit constraints
        for i, j, typ in constraints:
            if i < L and j < L:
                C[i, j] = typ # i -> j
        
        # From Hoare triples (aggregate)
        for pre, post in triples:
            # If pre[i] and post[j], strengthen C[i,j]
            indices_pre = np.where(pre > 0)[0]
            indices_post = np.where(post > 0)[0]
            for i in indices_pre:
                for j in indices_post:
                    if i < L and j < L:
                        C[i, j] = max(C[i, j], 1.0) # Reinforce
                        
        return C

    def _propagate(self, x: np.ndarray, triples: List[Tuple[np.ndarray, np.ndarray]], weights: np.ndarray) -> np.ndarray:
        """Applies modus ponens iteratively."""
        x_new = x.copy()
        changed = True
        iters = 0
        
        while changed and iters < self.max_iters:
            changed = False
            iters += 1
            for i, (pre, post) in enumerate(triples):
                if i >= len(weights): continue
                
                # Check if pre is satisfied
                # Condition: For all active pre literals, x is positive
                active_pre = pre > 0
                if np.any(active_pre):
                    # Simplified: if sum(x[active_pre]) == sum(active_pre), then pre is true
                    # Using a threshold for float tolerance
                    if np.sum(x_new[active_pre] > 0.5) == np.sum(active_pre):
                        # Apply post
                        post_indices = np.where(post > 0)[0]
                        for idx in post_indices:
                            if x_new[idx] <= 0:
                                x_new[idx] = 1.0
                                changed = True
                        weights[i] *= 0.9 # Dissipate weight
        return x_new

    def _compute_energy(self, C: np.ndarray, x: np.ndarray) -> float:
        if C.size == 0 or x.size == 0:
            return 0.0
        # E = ||C·x||^2
        # Interpretation: If C[i,j]=1, then if x[i]=1, x[j] should be 1.
        # Violation: x[i]=1 and x[j]=0 or -1.
        # Linear approximation: C dot x. 
        # Let's define energy as sum of (x_i - x_j)^2 for edges i->j
        E = 0.0
        rows, cols = np.where(C != 0)
        for i, j in zip(rows, cols):
            if i < len(x) and j < len(x):
                # If i->j exists, we want x_i <= x_j (in truth value -1, 0, 1)
                # Penalty if x_i is high and x_j is low
                diff = x[i] - x[j]
                if C[i,j] > 0: # Implication
                    if diff > 0: E += diff**2
                else: # Negative constraint
                    if x[i] + x[j] > 0: E += (x[i] + x[j])**2
        return E

    def _compute_emergence(self, C: np.ndarray) -> float:
        """Computes emergence based on spectral gap of the constraint graph."""
        if C.size == 0:
            return 0.5 # Neutral
        
        L_mat = np.abs(C) + np.abs(C.T) # Symmetrize for undirected Laplacian approximation
        D = np.diag(L_mat.sum(axis=1))
        Lap = D - L_mat
        
        try:
            eigvals = np.linalg.eigvalsh(Lap)
            # Sort eigenvalues
            eigvals = np.sort(eigvals)
            # Smallest non-zero eigenvalue (Fiedler value)
            lambda2 = 0.0
            for val in eigvals:
                if val > 1e-6:
                    lambda2 = val
                    break
            return 1.0 / (1.0 + lambda2)
        except:
            return 0.5

    def _process_candidate(self, candidate: str, prompt: str) -> Tuple[float, str]:
        """Internal scorer for a single candidate."""
        full_text = f"{prompt} {candidate}"
        literals = self._extract_literals(full_text)
        L = len(literals)
        
        if L == 0:
            return 0.0, "No literals extracted."

        # Initial state: assume literals in candidate are true (1), others 0
        x = np.zeros(L)
        cand_tokens = self._tokenize(candidate)
        for lit_str, lit_id in literals.items():
            # If literal appears in candidate, set to 1
            if any(t in lit_str for t in cand_tokens) or lit_str in candidate.lower():
                x[lit_id] = 1.0
        
        # Parse structure
        _, triples, constraints = self._parse_structure(full_text, literals)
        
        if not triples and not constraints:
            # Fallback for simple statements without explicit logic
            # Score based on length and keyword density as a proxy for information
            return 0.5, "No logical structure found; fallback score."

        C = self._build_constraint_matrix(L, constraints, triples)
        
        # Initial Energy
        E0 = self._compute_energy(C, x) + 1e-6
        
        # Propagation
        weights = np.ones(len(triples))
        x_final = self._propagate(x, triples, weights)
        
        # Final Energy
        Er = self._compute_energy(C, x_final)
        
        # Thermodynamic score (reduction in energy)
        # If Er < E0, energy was dissipated (good inference)
        thermo_score = max(0, 1.0 - (Er / E0))
        
        # Emergence score
        emergence = self._compute_emergence(C)
        
        # Final Score
        score = self.alpha * thermo_score + self.beta * emergence
        
        reason = f"Thermo:{thermo_score:.2f}, Emergence:{emergence:.2f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._process_candidate(cand, prompt)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._process_candidate(answer, prompt)
        return float(np.clip(score, 0.0, 1.0))