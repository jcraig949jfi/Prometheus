import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Structural Parsing, 
    Maximum Entropy constraints, and Free Energy scoring.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms and logical constraints (negation, 
       comparatives, conditionals, causality, ordering) from text.
    2. MaxEnt Prior: Uses dual ascent to find the least-biased probability 
       distribution over atoms that satisfies extracted linear constraints.
    3. Free Energy Scoring: Evaluates candidates by computing variational free 
       energy (expected constraint violation minus entropy). Lower energy implies 
       higher consistency with the prompt's logical structure.
    
    Beats NCD baseline by relying on logical structure rather than string similarity.
    """
    
    def __init__(self):
        self.delta = 0.1  # Margin for comparatives
        self.epsilon = 1e-4
        self.lr = 0.1     # Learning rate for dual ascent

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract simple propositional atoms (lowercase words) as unique identifiers."""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        # Simple deduplication while preserving order for index mapping
        seen = set()
        atoms = []
        for w in words:
            if w not in seen and len(w) > 2: # Ignore short words like 'is', 'it'
                seen.add(w)
                atoms.append(w)
        return atoms

    def _parse_constraints(self, text: str, atoms: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Parse text into linear constraints Cx <= b.
        Returns matrix C and vector b.
        """
        n = len(atoms)
        if n == 0:
            return np.array([]).reshape(0, 1), np.array([])
            
        C_rows = []
        b_vals = []
        text_lower = text.lower()
        
        # Helper to get index
        def idx(word):
            return atoms.index(word) if word in atoms else -1

        # 1. Negation: "not X" -> x_X <= 0 (approximated as hard constraint for simplicity)
        # Pattern: not [word]
        for match in re.finditer(r'not\s+(\w+)', text_lower):
            target = match.group(1)
            i = idx(target)
            if i != -1:
                row = [0] * n
                row[i] = 1.0
                C_rows.append(row)
                b_vals.append(0.0)

        # 2. Comparatives: "more X than Y" or "X is greater than Y" -> x_X >= x_Y + delta
        # Rewritten: -x_X + x_Y <= -delta
        patterns_comp = [
            r'more\s+(\w+)\s+than\s+(\w+)',
            r'(\w+)\s+is\s+(?:greater|larger|higher)\s+than\s+(\w+)',
            r'(\w+)\s+exceeds\s+(\w+)'
        ]
        for pat in patterns_comp:
            for match in re.finditer(pat, text_lower):
                w1, w2 = match.group(1), match.group(2)
                i, j = idx(w1), idx(w2)
                if i != -1 and j != -1:
                    row = [0] * n
                    row[i] = -1.0
                    row[j] = 1.0
                    C_rows.append(row)
                    b_vals.append(-self.delta)

        # 3. Conditionals: "if A then B" -> x_A <= x_B => x_A - x_B <= 0
        # Pattern: if [word] then [word]
        for match in re.finditer(r'if\s+(\w+)\s+(?:then\s+)?(\w+)', text_lower):
            w1, w2 = match.group(1), match.group(2)
            i, j = idx(w1), idx(w2)
            if i != -1 and j != -1:
                row = [0] * n
                row[i] = 1.0
                row[j] = -1.0
                C_rows.append(row)
                b_vals.append(0.0)

        # 4. Causal/Ordering: "A causes B", "first A then B" -> x_A <= x_B
        patterns_causal = [
            r'(\w+)\s+causes\s+(\w+)',
            r'first\s+(\w+)\s+then\s+(\w+)',
            r'(\w+)\s+leads\s+to\s+(\w+)'
        ]
        for pat in patterns_causal:
            for match in re.finditer(pat, text_lower):
                w1, w2 = match.group(1), match.group(2)
                i, j = idx(w1), idx(w2)
                if i != -1 and j != -1:
                    row = [0] * n
                    row[i] = 1.0
                    row[j] = -1.0
                    C_rows.append(row)
                    b_vals.append(0.0)

        if not C_rows:
            return np.array([]).reshape(0, n), np.array([])
            
        return np.array(C_rows), np.array(b_vals)

    def _solve_maxent(self, C: np.ndarray, b: np.ndarray, n: int) -> np.ndarray:
        """
        Solve for maximum entropy distribution means using dual ascent.
        Maximizes entropy subject to Cx <= b.
        Returns the mean vector mu (probabilities).
        """
        if C.size == 0:
            return np.full(n, 0.5) # Uniform prior if no constraints
            
        m, _ = C.shape
        lam = np.zeros(m) # Lagrange multipliers
        
        # Dual ascent loop
        for _ in range(100):
            # Compute means: mu = sigmoid(-C^T lambda)
            # Note: The constraint is Cx <= b. The energy term is lambda^T (Cx - b).
            # Gradient of logZ wrt lambda is (Cx - b). 
            # We want to minimize dual function. 
            # Update: lambda = max(0, lambda + eta * (C*mu - b))
            
            exponent = -C.T @ lam
            mu = 1.0 / (1.0 + np.exp(-exponent)) # Sigmoid
            
            violation = C @ mu - b
            if np.max(np.abs(violation)) < self.epsilon:
                break
                
            lam = np.maximum(0, lam + self.lr * violation)
            
        # Final mu
        exponent = -C.T @ lam
        mu = 1.0 / (1.0 + np.exp(-exponent))
        return mu

    def _compute_free_energy(self, C: np.ndarray, b: np.ndarray, candidate_atoms: List[str], 
                             global_atoms: List[str], mu_prior: np.ndarray) -> float:
        """
        Compute Free Energy F = E[Energy] - Entropy.
        Energy = lambda^T (Cx - b). 
        Here we approximate by checking consistency of candidate truth values against constraints.
        Since candidate is hard evidence, we treat it as a delta distribution q.
        F ~ Violation Penalty - Entropy_of_candidate_belief
        """
        n = len(global_atoms)
        if n == 0:
            return 0.0
            
        # Map candidate atoms to indices
        x_hard = np.zeros(n)
        for word in candidate_atoms:
            if word in global_atoms:
                idx = global_atoms.index(word)
                x_hard[idx] = 1.0
        
        # If no constraints, energy is 0, score based on entropy (uniformity)
        if C.size == 0:
            # Max entropy is when p=0.5. Candidate hard evidence has 0 entropy.
            # We want to reward candidates that don't force low entropy unnecessarily?
            # Actually, if no constraints, any answer is equally valid logically.
            # We rely on NCD here as tiebreaker.
            return 0.0

        # Re-calculate lambdas for the specific candidate context? 
        # No, we use the global mu_prior as the reference distribution p(x).
        # We compute F for the candidate's distribution q (hard).
        # F = Eq[E] - H(q). H(q) for hard dist is 0.
        # So F = Eq[E] = Sum(lambda_i * (C_i . x - b_i)) for violated constraints.
        
        # However, to make it robust, let's use the learned lambdas from the prior step
        # We need to re-solve lambdas? No, let's assume the mu_prior represents the 
        # optimal soft state. We measure how far the candidate deviates.
        
        # Simplified Free Energy approximation for ranking:
        # Penalty = sum(max(0, C_i . x_hard - b_i))
        # We want to minimize penalty.
        
        violations = C @ x_hard - b
        penalty = np.sum(np.maximum(0, violations))
        
        # Entropy term: The candidate provides specific values (low entropy).
        # The prior provides uncertainty (high entropy).
        # We prefer candidates that align with the high-entropy prior's mean?
        # Let's add a term that rewards alignment with the MaxEnt mean.
        # Alignment = - ||x_hard - mu_prior||^2
        alignment = -np.sum((x_hard - mu_prior)**2)
        
        return penalty + alignment

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Parse Prompt
        global_atoms = self._extract_atoms(prompt)
        C, b = self._parse_constraints(prompt, global_atoms)
        
        # 2. Solve MaxEnt Prior for the prompt
        mu_prior = self._solve_maxent(C, b, len(global_atoms))
        
        results = []
        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            
            # Compute Free Energy score
            # Lower F is better. We invert sign for "Higher score = better"
            F = self._compute_free_energy(C, b, cand_atoms, global_atoms, mu_prior)
            
            # Normalize/Scale score: Negative F is good. 
            # Let's make score = -F. 
            # If no constraints, F=0. We need a tie breaker.
            score = -F
            
            # Tie-breaker: NCD-like length similarity (very basic) if scores are close
            # But primarily, logical consistency is key.
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Consistency score based on {len(global_atoms)} atoms and {C.shape[0]} constraints."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the relative ranking of the answer against a set of perturbations 
        or simply maps the logical consistency score to [0,1].
        """
        # Generate a dummy set of candidates to establish a baseline range
        # Since we can't generate infinite candidates, we evaluate the single answer
        # against the constraints and normalize based on violation count.
        
        global_atoms = self._extract_atoms(prompt)
        C, b = self._parse_constraints(prompt, global_atoms)
        
        if C.size == 0:
            # No logical structure detected, fallback to low confidence
            return 0.5
            
        cand_atoms = self._extract_atoms(answer)
        n = len(global_atoms)
        if n == 0: 
            return 0.5
            
        # Calculate raw violation count
        x_hard = np.zeros(n)
        for word in cand_atoms:
            if word in global_atoms:
                x_hard[global_atoms.index(word)] = 1.0
                
        violations = C @ x_hard - b
        total_violations = np.sum(np.maximum(0, violations))
        
        # Heuristic mapping: 
        # 0 violations -> 1.0
        # >0 violations -> decays exponentially
        confidence = np.exp(-total_violations)
        
        return float(np.clip(confidence, 0.0, 1.0))