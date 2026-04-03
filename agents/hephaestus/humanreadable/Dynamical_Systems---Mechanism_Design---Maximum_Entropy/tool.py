"""
Entropic Dynamical Incentive Scorer (EDIS)

Combines Dynamical Systems, Mechanism Design, and Maximum Entropy:
- Parses prompts into atomic propositions with belief weights
- Propagates constraints via iterative dynamical updates
- Applies incentive-aware adjustments using Bayesian priors
- Regularizes with maximum entropy to avoid overconfidence
- Converges to equilibrium state scoring candidates by alignment
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    bayesian_update, entropy, solve_constraints, 
    check_transitivity, modus_ponens, confidence_from_agreement,
    information_sufficiency
)


class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-3
        self.max_iters = 20
        self.alpha = 0.3  # constraint propagation step
        self.beta = 0.2   # incentive step
        self.gamma = 0.1  # entropy regularization step
    
    def _parse_propositions(self, text):
        """Extract atomic propositions with initial weights."""
        props = {}
        
        # Numeric comparisons
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==|equals?)\s*(\w+)', text, re.I):
            props[m.group(0).lower()] = 1.0
        
        # Negations
        for m in re.finditer(r'(not|never|no)\s+(\w+)', text, re.I):
            props[f"neg_{m.group(2).lower()}"] = 1.0
        
        # Causal claims
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', text, re.I):
            props[f"{m.group(1)}_causes_{m.group(3)}".lower()] = 1.0
        
        # Boolean assertions
        for m in re.finditer(r'\b(true|false|yes|no)\b', text, re.I):
            props[m.group(1).lower()] = 1.0
        
        # Extract numbers for numeric reasoning
        for m in re.finditer(r'\b(\d+\.?\d*)\b', text):
            props[f"num_{m.group(1)}"] = float(m.group(1)) / 100.0  # normalize
        
        return props if props else {"default": 0.5}
    
    def _extract_constraints(self, text):
        """Extract logical constraints as relations."""
        constraints = []
        
        # Transitivity: A > B, B > C implies A > C
        relations = []
        for m in re.finditer(r'(\w+)\s*>\s*(\w+)', text):
            relations.append((m.group(1).lower(), m.group(2).lower()))
        
        if len(relations) >= 2:
            if not check_transitivity(relations):
                constraints.append(("transitivity_violation", -1.0))
        
        # Conditionals: if A then B
        for m in re.finditer(r'if\s+(\w+)\s+then\s+(\w+)', text, re.I):
            constraints.append((f"{m.group(1)}_implies_{m.group(2)}".lower(), 1.0))
        
        return constraints
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity, presupposition, and unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ \w+ a \w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with follow-up
        if re.search(r'(he|she|it|they) (was|is|were)', prompt_lower) and 'who' in prompt_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower):
            if not re.search(r'(most|least|highest|lowest|according to)', prompt_lower):
                return 0.25
        
        # Insufficient information
        if re.search(r'(what|which|who) (is|are|was|were)', prompt_lower):
            # Check if enough info present
            word_count = len(prompt.split())
            if word_count < 10:
                return 0.3
        
        return 1.0  # No meta-issues detected
    
    def _dynamical_update(self, state, constraints, incentives):
        """Iterative dynamical system with constraint propagation, incentive, entropy."""
        n = len(state)
        if n == 0:
            return state
        
        keys = list(state.keys())
        s = np.array([state[k] for k in keys])
        
        for _ in range(self.max_iters):
            s_old = s.copy()
            
            # Step 1: Constraint propagation (dynamical system attractor)
            if constraints:
                residual = sum(c[1] for c in constraints if c[1] < 0)
                if residual < 0:
                    s = s - self.alpha * residual / n
            
            # Step 2: Incentive update (mechanism design)
            # Use Bayesian update as incentive mechanism
            for i in range(n):
                if incentives[i] > 0:
                    s[i] = bayesian_update(s[i], incentives[i], 0.1)
            
            # Step 3: Entropy regularization (maximum entropy principle)
            s_probs = np.clip(s, 1e-9, 1 - 1e-9)
            H = entropy(s_probs)
            # Push toward max entropy (0.5) when uncertain
            entropy_gradient = 2 * (s - 0.5) * H
            s = s - self.gamma * entropy_gradient
            
            # Project to [0, 1]
            s = np.clip(s, 0, 1)
            
            # Check convergence
            if np.linalg.norm(s - s_old) < self.epsilon:
                break
        
        return {keys[i]: s[i] for i in range(n)}
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by EDIS score."""
        # Parse prompt structure
        prompt_props = self._parse_propositions(prompt)
        constraints = self._extract_constraints(prompt)
        
        # Initialize state vector
        n = len(prompt_props)
        incentives = np.ones(n) * 0.5  # neutral incentive initially
        
        # Run dynamical system to equilibrium
        equilibrium = self._dynamical_update(prompt_props, constraints, incentives)
        
        results = []
        for cand in candidates:
            # Parse candidate propositions
            cand_props = self._parse_propositions(cand)
            
            # Compute alignment score (structural)
            overlap_keys = set(equilibrium.keys()) & set(cand_props.keys())
            if overlap_keys:
                alignment = sum(equilibrium[k] * cand_props[k] for k in overlap_keys)
                alignment /= len(overlap_keys)
            else:
                alignment = 0.5
            
            # Numeric computation (if numeric comparison in prompt)
            numeric_score = 0.0
            prompt_nums = re.findall(r'\b(\d+\.?\d*)\b', prompt)
            cand_nums = re.findall(r'\b(\d+\.?\d*)\b', cand)
            if prompt_nums and cand_nums:
                # Check if candidate maintains numeric relationships
                try:
                    p_vals = [float(x) for x in prompt_nums[:2]]
                    c_vals = [float(x) for x in cand_nums[:2]]
                    if len(p_vals) == 2 and len(c_vals) == 2:
                        # Check if ordering preserved
                        if (p_vals[0] < p_vals[1]) == (c_vals[0] < c_vals[1]):
                            numeric_score = 0.8
                except:
                    pass
            
            # Constraint satisfaction score
            constraint_score = 1.0
            if constraints:
                violations = sum(1 for c in constraints if c[1] < 0 and c[0] in cand.lower())
                constraint_score = max(0, 1 - violations / len(constraints))
            
            # NCD tiebreaker (max 10%)
            try:
                import zlib
                prompt_z = len(zlib.compress(prompt.encode()))
                cand_z = len(zlib.compress(cand.encode()))
                concat_z = len(zlib.compress((prompt + cand).encode()))
                ncd = (concat_z - min(prompt_z, cand_z)) / max(prompt_z, cand_z)
                ncd_score = max(0, 1 - ncd)
            except:
                ncd_score = 0.5
            
            # Weighted combination (structural 50%, numeric 25%, constraint 15%, NCD 10%)
            final_score = (0.5 * alignment + 0.25 * numeric_score + 
                          0.15 * constraint_score + 0.1 * ncd_score)
            
            reasoning = f"Align={alignment:.2f} Num={numeric_score:.2f} Constraint={constraint_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence in answer, capped by meta-confidence check."""
        # First check for meta-level issues
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer against itself and null
        results = self.evaluate(prompt, [answer, "uncertain", "unknown"])
        
        if not results:
            return 0.3
        
        # Get score of actual answer
        answer_result = next((r for r in results if r["candidate"] == answer), None)
        if not answer_result:
            return 0.3
        
        base_score = answer_result["score"]
        
        # Cap confidence based on information sufficiency
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        
        # If very few propositions, we're uncertain
        if len(prompt_props) <= 2:
            base_score *= 0.7
        
        # Never exceed 0.9 unless perfect match
        confidence_val = min(0.9, base_score) * meta_conf
        
        # Lower bound for reasonable answers
        return max(0.1, confidence_val)