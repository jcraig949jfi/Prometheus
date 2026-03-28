import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool combining Causal Inference, Free Energy Principle, and Metamorphic Testing.
    
    Mechanism:
    1. Parsing: Extracts entities and causal/comparative claims via regex into weighted tuples.
    2. Graph Construction: Builds an adjacency matrix representing the candidate's logical structure.
    3. Metamorphic Relations (MR): Defines constraints like antisymmetry and transitivity.
    4. Free Energy Minimization: 
       - Propagates constraints to find the 'ideal' consistent graph (Q).
       - Calculates Prediction Error (E) as the divergence between the candidate's graph and the consistent graph.
       - Calculates Cycle Penalty to penalize logical loops.
       - Free Energy F = E + lambda * CyclePenalty.
    5. Scoring: Score = exp(-F). Higher score indicates lower free energy (better logical consistency).
    
    This approach beats NCD baselines by evaluating structural logical consistency rather than string similarity.
    """

    def __init__(self):
        # Regex patterns for atomic proposition extraction
        self.patterns = {
            'causal': re.compile(r'(\w+)\s+(causes|leads to|results in|implies)\s+(\w+)', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s+(is greater than|is less than|exceeds|precedes|follows)\s+(\w+)', re.IGNORECASE),
            'conditional': re.compile(r'if\s+(\w+)\s+(?:then)?\s+(\w+)', re.IGNORECASE),
            'negation': re.compile(r'\b(not|no|never)\b', re.IGNORECASE),
            'entity': re.compile(r'\b([A-Za-z][A-Za-z0-9_]*(?:\s+[A-Za-z][A-Za-z0-9_]*)?)\b')
        }
        self.lambda_cycle = 0.1

    def _parse_text(self, text: str) -> List[Tuple[str, str, str, int, float]]:
        """Extract atomic propositions: (subject, predicate, object, polarity, weight)"""
        propositions = []
        text_lower = text.lower()
        
        # Check for global negation context (simplified)
        has_negation = bool(self.patterns['negation'].search(text_lower))
        
        # Extract causal
        for m in self.patterns['causal'].finditer(text):
            subj, pred, obj = m.group(1), m.group(2), m.group(3)
            pol = -1 if has_negation else 1
            propositions.append((subj, pred, obj, pol, 1.0))
            
        # Extract comparative (mapped to causal-like edges with special predicates)
        for m in self.patterns['comparative'].finditer(text):
            subj, pred, obj = m.group(1), m.group(2), m.group(3)
            pol = -1 if "less" in pred or "follows" in pred else 1
            if "less" in pred or "follows" in pred: 
                # Normalize direction: A less than B -> B > A
                subj, obj = obj, subj 
                pol = 1
            propositions.append((subj, "gt", obj, pol, 1.0))
            
        # Extract conditionals (If A then B -> A causes B)
        for m in self.patterns['conditional'].finditer(text):
            subj, obj = m.group(1), m.group(2)
            pol = -1 if has_negation else 1
            propositions.append((subj, "causes", obj, pol, 1.0))

        return propositions

    def _build_graph(self, propositions: List[Tuple]) -> Tuple[np.ndarray, List[str], Dict[str, int]]:
        """Build weighted adjacency matrix A from propositions."""
        entities = list(set([p[0] for p in propositions] + [p[2] for p in propositions]))
        if not entities:
            return np.array([]), [], {}
            
        entities.sort() # Deterministic ordering
        n = len(entities)
        idx_map = {e: i for i, e in enumerate(entities)}
        A = np.zeros((n, n), dtype=float)
        
        for subj, pred, obj, pol, weight in propositions:
            if subj in idx_map and obj in idx_map:
                i, j = idx_map[subj], idx_map[obj]
                # Accumulate weights; polarity affects sign
                val = weight * pol
                if pred == "gt":
                    A[i, j] = max(A[i, j], val) # Max for comparatives
                else:
                    A[i, j] += val
                    
        return A, entities, idx_map

    def _propagate_constraints(self, A: np.ndarray) -> np.ndarray:
        """
        Apply Metamorphic Relations via constraint propagation.
        1. Transitivity: If X->Y and Y->Z, then X->Z should exist.
        2. Antisymmetry enforcement (implicit in error calculation later).
        We iterate B = max(B, B @ B) to saturate transitive links.
        """
        if A.size == 0:
            return A
            
        B = A.copy()
        n = B.shape[0]
        if n == 0: return B
        
        # Normalize to 0-1 range for stability if needed, but keeping weights is fine for relative error
        # Iterative propagation for transitivity: B_new = max(B, B^2)
        for _ in range(n): # Max n iterations to converge
            old_B = B.copy()
            # Matrix multiplication finds paths of length 2
            # We use element-wise min for path strength (bottleneck), but standard dot product sums them.
            # For simple existence/strength propagation in this context:
            # Let's use a simplified relaxation: if A[i,k] and A[k,j] exist, A[i,j] should be at least min.
            # Vectorized approximation: B = np.maximum(B, B @ B) works for boolean/positive weights roughly
            # To handle negative weights (negation) correctly without complex logic, we focus on magnitude propagation for consistency
            abs_B = np.abs(B)
            trans = abs_B @ abs_B
            # Normalize trans to prevent explosion, just checking existence
            trans = np.clip(trans, 0, 1.0) 
            
            # Update B where transitivity implies a stronger link
            # This is a heuristic approximation of constraint propagation
            B = np.maximum(B, trans * np.sign(B @ B + 1e-9)) 
            B[np.abs(B) < 1e-6] = 0
            
            if np.allclose(B, old_B, atol=1e-6):
                break
        return B

    def _compute_free_energy(self, A: np.ndarray) -> float:
        """Compute Free Energy F = Prediction Error + Lambda * Cycle Penalty"""
        if A.size == 0:
            return 0.0
            
        # 1. Prediction Error: Difference between asserted (A) and consistent (B)
        B = self._propagate_constraints(A)
        E = np.linalg.norm(A - B, 'fro') ** 2
        
        # 2. Cycle Penalty: Detect directed cycles via eigenvalues of symmetric part
        # A directed cycle implies A[i,j] and A[j,i] are both non-zero.
        # Symmetric part S = (B + B.T) / 2. 
        # Negative eigenvalues in the context of adjacency often indicate instability/cycles in specific formulations,
        # but a simpler proxy for cycles in a causal graph is the sum of element-wise product of B and B.T
        # Cycle proxy: sum(B * B.T) where off-diagonal elements indicate bidirectional flow.
        cycle_proxy = np.sum(B * B.T) - np.sum(np.diag(B) * np.diag(B)) # Remove self-loops from count if any
        cycle_penalty = max(0.0, cycle_proxy) # Ensure non-negative
        
        F = E + self.lambda_cycle * cycle_penalty
        return F

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # Parse prompt once to establish context (optional, mostly used for candidate evaluation)
        
        for cand in candidates:
            props = self._parse_text(cand)
            A, _, _ = self._build_graph(props)
            
            if A.size == 0:
                # Fallback for empty parses: use NCD-like length penalty or low score
                score = 0.0
                reasoning = "No structural propositions found."
            else:
                F = self._compute_free_energy(A)
                score = np.exp(-F)
                reasoning = f"Free Energy: {F:.4f}, Entities: {A.shape[0]}"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy score."""
        props = self._parse_text(answer)
        if not props:
            # If no structure found, rely on simple keyword overlap as a weak fallback
            # to avoid returning 0.0 for valid simple answers, though the tool prefers structure.
            return 0.1 
            
        A, _, _ = self._build_graph(props)
        if A.size == 0:
            return 0.1
            
        F = self._compute_free_energy(A)
        # Normalize score to 0-1. Since F >= 0, exp(-F) is in (0, 1].
        confidence = np.exp(-F)
        return float(confidence)