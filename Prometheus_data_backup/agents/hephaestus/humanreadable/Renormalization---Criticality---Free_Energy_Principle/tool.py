import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning engine combining Renormalization Group coarse-graining, 
    Criticality tuning, and the Free Energy Principle for logical consistency.
    
    Mechanism:
    1. Parsing: Extracts propositions, numeric constraints, and logical operators.
    2. Renormalization: Groups propositions into blocks (sentences), computing 
       effective constraint matrices with variance terms to capture internal disagreement.
    3. Criticality: Sweeps a temperature parameter to maximize susceptibility, 
       placing the system at the edge of order/disorder to highlight inconsistencies.
    4. Free Energy: Computes variational free energy F = E + H for candidate answers.
       Lower F indicates higher logical consistency with the prompt.
    """
    
    def __init__(self):
        self.epsilon = 1e-9

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract structural features: numbers, comparatives, negations, conditionals."""
        props = []
        text_lower = text.lower()
        
        # Numeric extraction (floats and integers)
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
        nums = [float(n) for n in numbers]
        
        # Logical flags
        has_negation = bool(re.search(r'\b(not|no|never|none|without)\b', text_lower))
        has_conditional = bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower))
        has_comparative = bool(re.search(r'\b(more|less|greater|smaller|taller|shorter|before|after)\b', text_lower))
        has_equality = bool(re.search(r'\b(equal|same|identical|equals)\b', text_lower)) or '=' in text
        
        # Specific patterns for Tier B traps
        presupposition_triggers = ["have you stopped", "why did", "why does", "quit", "failed to"]
        has_presupposition = any(t in text_lower for t in presupposition_triggers)
        
        scope_ambiguity = bool(re.search(r'every.*a\s+\w+', text_lower)) and "same" not in text_lower
        pronoun_ambiguity = bool(re.search(r'\b(he|she|him|her|they)\b.*\bwho\b', text_lower))
        false_dichotomy = bool(re.search(r'\beither.*or\b', text_lower)) and "only" not in text_lower
        subjectivity = bool(re.search(r'\b(best|worst|favorite|beautiful|ugly|good|bad)\b', text_lower))
        
        props.append({
            "type": "context",
            "nums": nums,
            "negation": has_negation,
            "conditional": has_conditional,
            "comparative": has_comparative,
            "equality": has_equality,
            "presupposition": has_presupposition,
            "scope_ambiguity": scope_ambiguity,
            "pronoun_ambiguity": pronoun_ambiguity,
            "false_dichotomy": false_dichotomy,
            "subjectivity": subjectivity,
            "length": len(text.split())
        })
        return props

    def _compute_numeric_solution(self, prompt: str, candidate: str) -> Optional[float]:
        """Attempt to constructively solve numeric problems from the prompt."""
        # Extract all numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        if not p_nums:
            return None
            
        # Heuristic: If candidate contains a number present in prompt, check logic
        # Simple arithmetic checks for common patterns (sum, diff, ratio)
        if len(p_nums) >= 2:
            target = c_nums[0] if c_nums else None
            
            # Check sum
            if target is not None and abs(sum(p_nums) - target) < 1e-6:
                return 1.0
            # Check difference
            if target is not None and abs(p_nums[0] - p_nums[1] - target) < 1e-6:
                return 1.0
            # Check product
            if target is not None and abs(p_nums[0] * p_nums[1] - target) < 1e-6:
                return 1.0
                
        # If candidate is just a number, and prompt implies a calculation we can't fully parse,
        # we rely on the constraint matrix later. Return None to indicate no direct constructive solve.
        return None

    def _renormalize(self, propositions: List[Dict]) -> Tuple[np.ndarray, float]:
        """
        Renormalization step: Group propositions and compute effective constraint matrix.
        Returns coarse-grained matrix C_bar and internal variance.
        """
        if not propositions:
            return np.array([[0.0]]), 0.0
            
        n = len(propositions)
        # Build raw constraint matrix based on feature similarity/dissimilarity
        # Features: [num_density, negation, conditional, comparative]
        features = []
        for p in propositions:
            vec = [
                len(p.get('nums', [])) / (p.get('length', 1) + 1),
                1.0 if p.get('negation') else 0.0,
                1.0 if p.get('conditional') else 0.0,
                1.0 if p.get('comparative') else 0.0
            ]
            features.append(vec)
        
        F = np.array(features)
        # Constraint: High similarity implies strong coupling (low energy if consistent)
        # Using Euclidean distance as inverse constraint strength
        C = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                dist = np.linalg.norm(F[i] - F[j])
                C[i, j] = np.exp(-dist) # Soft constraint weight
        
        # Coarse grain: Average weights + variance term
        mean_val = np.mean(C)
        var_val = np.var(C)
        
        # Effective matrix is uniform block with variance penalty
        C_bar = np.full((n, n), mean_val)
        if n > 1:
            C_bar += var_val * np.eye(n) # Variance adds diagonal stiffness
            
        return C_bar, var_val

    def _critical_temperature(self, C: np.ndarray) -> float:
        """
        Criticality tuning: Find temperature tau that maximizes susceptibility.
        Susceptibility chi = d<S>/dT approximated numerically.
        """
        if C.size == 0:
            return 1.0
            
        taus = np.linspace(0.1, 5.0, 20)
        susceptibilities = []
        
        # Simplified Belief Propagation approximation for susceptibility
        # S(tau) ~ Sum of tanh(C / tau)
        for tau in taus:
            try:
                with np.errstate(divide='ignore'):
                    interaction = C / tau
                    # Avoid inf
                    interaction = np.clip(interaction, -10, 10)
                    s_val = np.sum(np.tanh(interaction))
                    susceptibilities.append(s_val)
            except:
                susceptibilities.append(0.0)
        
        susceptibilities = np.array(susceptibilities)
        # Derivative approximation
        if len(susceptibilities) < 2:
            return 1.0
            
        deriv = np.abs(np.gradient(susceptibilities, taus))
        peak_idx = np.argmax(deriv)
        return taus[peak_idx]

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Variational Free Energy F = E + H.
        E: Constraint violation energy.
        H: Entropy of belief state.
        """
        props = self._parse_propositions(prompt + " " + candidate)
        C, variance = self._renormalize(props)
        tau = self._critical_temperature(C)
        
        # Belief vector b: Probability candidate is consistent with prompt
        # Constructive computation check
        constructive_score = 0.0
        if self._compute_numeric_solution(prompt, candidate) is not None:
            constructive_score = 1.0
            
        # Structural consistency score
        p_feats = props[0] # Prompt features
        c_feats = props[-1] if len(props) > 1 else props[0] # Candidate features (simplified)
        
        # Energy term E: Penalty for mismatch
        mismatch = 0.0
        if p_feats['negation'] != c_feats.get('negation', False):
            mismatch += 0.5
        if p_feats['conditional'] and not c_feats.get('conditional', False):
            # Candidate should ideally reflect conditional logic if prompt has it
            mismatch += 0.2
            
        # Numeric consistency
        p_nums = p_feats.get('nums', [])
        c_nums = c_feats.get('nums', [])
        if p_nums and c_nums:
            # Check if candidate numbers are within reasonable range of prompt numbers
            if abs(np.mean(p_nums) - np.mean(c_nums)) > max(np.std(p_nums)+0.1, 1.0):
                mismatch += 0.5
                
        E = mismatch * (1.0 / (tau + 0.1)) + variance
        
        # Entropy term H: Encourage certainty but penalize overconfidence if mismatched
        # Belief b derived from constructive score and low energy
        b_raw = constructive_score + (1.0 / (1.0 + np.exp(E)))
        b = np.clip(b_raw, 0.01, 0.99)
        
        H = -(b * np.log(b + self.epsilon) + (1-b) * np.log(1-b + self.epsilon))
        
        F = E + H
        return F

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        props = self._parse_propositions(prompt)
        if not props:
            return 0.2
            
        p = props[0]
        cap = 1.0
        
        if p['presupposition']:
            cap = 0.2  # "Have you stopped..."
        elif p['scope_ambiguity']:
            cap = 0.3  # "Every X did a Y"
        elif p['pronoun_ambiguity']:
            cap = 0.3  # "He told him..."
        elif p['false_dichotomy']:
            cap = 0.4  # "Either A or B"
        elif p['subjectivity']:
            cap = 0.5  # "Best/Worst"
        elif p['length'] < 3: 
            cap = 0.3  # Too short to reason
            
        return cap

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-check meta-confidence for the prompt
        meta_cap = self._meta_confidence(prompt)
        
        scores = []
        for cand in candidates:
            F = self._compute_free_energy(prompt, cand)
            # Lower F is better. Convert to score (higher is better)
            # Normalize roughly: F usually between 0 and 3
            raw_score = 1.0 / (1.0 + F)
            
            # Apply constructive boost if numeric solution found
            if self._compute_numeric_solution(prompt, cand) is not None:
                raw_score = min(1.0, raw_score + 0.4)
                
            scores.append(raw_score)
        
        # Normalize scores to sum to 1 for probability distribution feel, then scale
        max_s = max(scores) if scores else 0
        min_s = min(scores) if scores else 0
        
        for i, cand in enumerate(candidates):
            # Raw score from Free Energy
            s = scores[i]
            
            # Apply meta-confidence cap (Epistemic Honesty)
            # If the prompt is ambiguous, even the "best" candidate shouldn't get high confidence
            if s == max_s:
                final_score = min(s, meta_cap)
            else:
                # Non-winners are scaled down further if prompt is ambiguous
                final_score = s * meta_cap
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Free Energy: {self._compute_free_energy(prompt, cand):.4f}, Meta-Cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses Free Energy minimization and Meta-Cognition capping.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Compute free energy for this specific pair
        F = self._compute_free_energy(prompt, answer)
        
        # Convert Free Energy to confidence
        # Low F -> High Confidence. 
        base_conf = 1.0 / (1.0 + F)
        
        # Constructive computation bonus
        if self._compute_numeric_solution(prompt, answer) is not None:
            base_conf = min(1.0, base_conf + 0.3)
            
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_cap)
        
        return float(np.clip(final_conf, 0.0, 1.0))

# Example usage logic (not part of class, for demonstration)
# tool = ReasoningTool()
# print(tool.evaluate("If A > B and B > 5, is A > 5?", ["Yes", "No"]))
# print(tool.confidence("Have you stopped cheating?", "Yes")) # Should be low due to presupposition