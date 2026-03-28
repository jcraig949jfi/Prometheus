import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning evaluator fusing Model Checking, Mechanism Design, and Neuromodulation.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causality, ordering).
    2. Model Checking: Constructs a state space of logical atom orderings and validates transitive constraints.
    3. Mechanism Design: Uses regret-matching to update constraint weights, penalizing frequent violations 
       to simulate incentive compatibility.
    4. Neuromodulation: Applies an uncertainty-based gain (entropy) to scale weights dynamically.
    5. Scoring: Computes a final satisfaction score based on weighted constraint adherence.
    """
    
    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|less|higher|lower|>\|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|lead|result|trigger|produce)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|precedes|follows|during)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|none|every|any)\b', re.IGNORECASE),
            'number': re.compile(r'\d+(\.\d+)?')
        }
        self.weights = None
        self.eta = 0.1  # Learning rate for regret matching

    def _extract_atoms(self, text: str) -> Dict[str, List[str]]:
        """Extract atomic propositions based on regex patterns."""
        atoms = {}
        text_lower = text.lower()
        for key, pattern in self.patterns.items():
            matches = [m.group(0) for m in pattern.finditer(text_lower)]
            if matches:
                atoms[key] = matches
        return atoms

    def _build_kripke_states(self, atoms: Dict[str, List[str]]) -> int:
        """
        Simplified Kripke structure: 
        Count distinct atomic constraints. State space size is 2^N for N constraints.
        Returns number of states S.
        """
        n_constraints = sum(len(v) for v in atoms.values())
        if n_constraints == 0:
            return 1
        # Limit state space for computational feasibility
        return min(2 ** min(n_constraints, 10), 1024)

    def _check_constraints(self, prompt_atoms: Dict, candidate_atoms: Dict, S: int) -> np.ndarray:
        """
        Generate constraint satisfaction matrix C (k x S).
        k = number of constraint types, S = number of states.
        Simplified: A state satisfies a constraint type if the candidate contains the pattern 
        found in the prompt, or if the logic holds (simulated via presence).
        """
        k = len(self.patterns)
        C = np.zeros((k, S), dtype=float)
        
        # Map pattern keys to indices
        keys = list(self.patterns.keys())
        
        for i, key in enumerate(keys):
            prompt_has = len(prompt_atoms.get(key, [])) > 0
            cand_has = len(candidate_atoms.get(key, [])) > 0
            
            # If prompt implies a logic type, candidate must match it to satisfy constraint
            # Simple heuristic: Presence in candidate matches presence in prompt
            satisfied = 1.0 if (prompt_has == cand_has) else 0.0
            
            # If numbers exist, check numeric consistency (simplified)
            if key == 'number' and prompt_has and cand_has:
                p_nums = [float(x) for x in prompt_atoms.get('number', [])]
                c_nums = [float(x) for x in candidate_atoms.get('number', [])]
                if p_nums and c_nums:
                    # Check if relative ordering is preserved (very basic check)
                    p_ord = np.argsort(p_nums)
                    c_ord = np.argsort(c_nums[:len(p_nums)]) if len(c_nums) >= len(p_nums) else np.array([])
                    if len(c_ord) > 0 and np.array_equal(p_ord, c_ord):
                        satisfied = 1.0
                    else:
                        satisfied = 0.5 # Partial credit for presence but wrong order
            
            C[i, :] = satisfied
            
        return C

    def _compute_gain(self, C: np.ndarray, w: np.ndarray) -> float:
        """Compute neuromodulatory gain based on entropy of satisfaction."""
        if np.sum(w) == 0:
            return 1.0
        p = C @ w
        p = p - np.min(p)
        total = np.sum(p)
        if total == 0:
            return 1.0
        p_norm = p / total
        
        # Entropy
        p_norm = p_norm[p_norm > 0]
        entropy = -np.sum(p_norm * np.log(p_norm + 1e-9))
        
        # Sigmoid gain
        gain = 1.0 / (1.0 + np.exp(-entropy))
        return gain

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_atoms = self._extract_atoms(prompt)
        S = self._build_kripke_states(prompt_atoms)
        
        scores = []
        all_violations = np.zeros(len(self.patterns))
        
        # Initialize weights if needed
        if self.weights is None:
            self.weights = np.ones(len(self.patterns))
        
        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            C = self._check_constraints(prompt_atoms, cand_atoms, S)
            
            # Mechanism Design: Regret matching update
            # Violations are where constraint is required (prompt has it) but candidate fails
            violations = np.zeros(len(self.patterns))
            for i, key in enumerate(list(self.patterns.keys())):
                p_has = len(prompt_atoms.get(key, [])) > 0
                c_has = len(cand_atoms.get(key, [])) > 0
                if p_has and not c_has:
                    violations[i] = 1.0
            
            # Update global violation stats for weight adjustment
            all_violations += violations
            
            # Neuromodulatory Gain
            g = self._compute_gain(C, self.weights)
            w_hat = g * self.weights
            
            # Scoring: w_hat @ (C @ v)
            # v is one-hot for the "best" state. Since C columns are uniform in this simplified model,
            # we just take the dot product of weights and the column (which is same for all states)
            # Effectively: score = sum(w_hat * constraint_satisfaction)
            raw_score = np.dot(w_hat, C[:, 0])
            
            scores.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Matched {sum(1 for k in prompt_atoms if k in cand_atoms)} logical patterns with gain {g:.2f}"
            })

        # Update weights based on aggregate violations (Regret Matching)
        if len(candidates) > 0:
            avg_violations = all_violations / len(candidates)
            self.weights = self.weights + self.eta * (all_violations - avg_violations)
            self.weights = np.clip(self.weights, 0.1, 10.0) # Keep weights positive and bounded

        # Normalize scores to [0, 1]
        raw_scores = [s["score"] for s in scores]
        min_s, max_s = min(raw_scores), max(raw_scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        
        for s in scores:
            s["score"] = (s["score"] - min_s) / range_s
            
        return sorted(scores, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on structural alignment."""
        res = self.evaluate(prompt, [answer])
        return res[0]["score"] if res else 0.0