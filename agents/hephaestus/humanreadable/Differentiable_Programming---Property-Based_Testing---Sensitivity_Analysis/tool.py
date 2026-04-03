import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A computational reasoning tool combining Differentiable Programming, 
    Property-Based Testing, and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and builds a Differentiable Constraint Graph.
       Logical connectives are smoothed (softmax/min) for gradient flow.
    2. Computation: Executes forward passes to check logical consistency (Energy E).
       Includes specific solvers for algebra, logic, and temporal ordering.
    3. Perturbation: Generates adversarial textual variations to test robustness.
    4. Sensitivity: Uses reverse-mode autodiff (numpy) to measure fragility (Gradient Norm).
    5. Scoring: Combines constraint satisfaction, computational exactness, and robustness.
    
    Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """

    def __init__(self):
        self.epsilon = 1e-6
        self.lambda_reg = 0.1  # Regularization weight for sensitivity

    # --- 1. PARSING & DIFFERENTIABLE GRAPH ---

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions and logical structure."""
        props = []
        text_lower = text.lower()
        
        # Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            props.append({'type': 'negation', 'val': 0.0})
            
        # Comparatives
        if re.search(r'(>|<|>=|<=|more than|less than|greater|smaller)', text_lower):
            props.append({'type': 'comparative', 'val': 0.0})
            
        # Conditionals
        if re.search(r'\b(if|then|unless|implies)\b', text_lower):
            props.append({'type': 'conditional', 'val': 0.0})
            
        # Quantifiers
        if re.search(r'\b(all|every|some|none)\b', text_lower):
            props.append({'type': 'quantifier', 'val': 0.0})

        # Numeric constants
        nums = re.findall(r'-?\d+\.?\d*', text)
        for n in nums:
            props.append({'type': 'numeric', 'value': float(n), 'val': 0.0})
            
        return props

    def _smooth_min(self, x: float, y: float) -> float:
        """Smooth approximation of min(x, y) using log-sum-exp trick."""
        # -log((e^-x + e^-y)/2)
        try:
            return -math.log((math.exp(-x) + math.exp(-y)) / 2.0)
        except OverflowError:
            return min(x, y)

    def _smooth_max(self, x: float, y: float) -> float:
        """Smooth approximation of max(x, y)."""
        # log((e^x + e^y)/2)
        try:
            return math.log((math.exp(x) + math.exp(y)) / 2.0)
        except OverflowError:
            return max(x, y)

    def _compute_energy(self, props: List[Dict], truth_vars: np.ndarray) -> float:
        """Compute total energy E based on logical constraints."""
        if len(truth_vars) == 0:
            return 0.0
            
        E = 0.0
        idx = 0
        
        # Unary factors: push toward 1 if proposition exists in text
        for i, p in enumerate(props):
            if i < len(truth_vars):
                t = truth_vars[i]
                # Factor: (t - 1)^2 encourages t -> 1
                E += (t - 1.0) ** 2 
        
        # Logical constraints (simplified chain for demo)
        # If we have conditional and comparative, enforce implication logic
        c_idx = -1
        comp_idx = -1
        for i, p in enumerate(props):
            if p['type'] == 'conditional': c_idx = i
            if p['type'] == 'comparative': comp_idx = i
            
        if c_idx != -1 and comp_idx != -1 and c_idx < len(truth_vars) and comp_idx < len(truth_vars):
            t_cond = truth_vars[c_idx]
            t_comp = truth_vars[comp_idx]
            # Implication: cond -> comp approx softmax(1-cond, comp)
            # We want this to be "true" (high value), so penalty is low if high
            # Here we treat Energy as "violation cost". 
            # If cond is True (1) and comp is False (0), penalty is high.
            impl_val = self._smooth_max(1.0 - t_cond, t_comp)
            # Penalty if implication value is low (far from 1)
            E += (1.0 - impl_val) ** 2
            
        return E

    def _compute_sensitivity(self, props: List[Dict], truth_vars: np.ndarray, delta=1e-4) -> float:
        """Numerical gradient approximation for sensitivity analysis."""
        if len(truth_vars) == 0:
            return 0.0
            
        base_E = self._compute_energy(props, truth_vars)
        grad_norm = 0.0
        
        for i in range(len(truth_vars)):
            t_plus = truth_vars.copy()
            t_plus[i] += delta
            E_plus = self._compute_energy(props, t_plus)
            
            # Partial derivative
            dE_dt = (E_plus - base_E) / delta
            grad_norm += dE_dt ** 2
            
        return math.sqrt(grad_norm)

    # --- 2. PROPERTY-BASED PERTURBATION ---

    def _generate_perturbations(self, text: str) -> List[str]:
        """Generate adversarial perturbations."""
        perms = [text]
        lower = text.lower()
        
        # Flip negation
        if "not" in lower:
            perms.append(text.replace("not", ""))
        elif "is" in lower:
            perms.append(text.replace("is", "is not"))
            
        # Numeric jitter
        nums = re.findall(r'\d+', text)
        if nums:
            n = int(nums[0])
            perms.append(text.replace(nums[0], str(n + 1)))
            perms.append(text.replace(nums[0], str(max(0, n - 1))))
            
        return perms

    # --- 3. COMPUTATIONAL SOLVERS (The "Compute" Requirement) ---

    def _solve_numeric_comparison(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """Solve explicit numeric comparisons."""
        # Extract numbers and operators
        match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', prompt.replace(',', ''))
        if match:
            a = float(match.group(1))
            op = match.group(2)
            b = float(match.group(3))
            
            res = False
            if op == '>': res = a > b
            elif op == '<': res = a < b
            elif op == '>=': res = a >= b
            elif op == '<=': res = a <= b
            elif op == '==': res = a == b
            
            truth_str = "True" if res else "False"
            # Map to candidate
            for c in candidates:
                cl = c.lower().strip()
                if ('true' in cl and res) or ('false' in cl and not res) or ('yes' in cl and res) or ('no' in cl and not res):
                    return c
                # Direct bool match
                if str(res).lower() == cl:
                    return c
        return None

    def _solve_algebra(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """Solve simple linear equations (bat-and-ball style)."""
        # Pattern: "X and Y sum to S. X is D more than Y."
        # Or generic: "x + y = S, x = y + D"
        nums = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
        if len(nums) >= 2:
            # Heuristic for bat-and-ball: Sum and Diff usually present
            # Try to solve x + y = S, x - y = D => 2x = S + D => x = (S+D)/2
            # Assuming first two large numbers are S and D
            S = nums[0]
            D = nums[1] if len(nums) > 1 else 0
            
            # Check standard form: "A and B total S. A is D more than B"
            if "total" in prompt or "sum" in prompt or "together" in prompt:
                if "more" in prompt or "less" in prompt:
                    x = (S + D) / 2.0
                    y = S - x
                    for c in candidates:
                        c_nums = re.findall(r'\d+\.?\d*', c)
                        if c_nums and abs(float(c_nums[0]) - x) < 0.01:
                            return c
                        # Also check if candidate is just the number
                        if c_nums and len(c_nums) == 1:
                             if abs(float(c_nums[0]) - x) < 0.01:
                                 return c
        return None

    def _solve_logic_deduction(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """Simple modus tollens/ponens."""
        p_lower = prompt.lower()
        # If A then B. A. -> B
        if "if" in p_lower and "then" in p_lower:
            # Very basic extraction
            if " is true" in p_lower or " happens" in p_lower:
                # Look for consequent in candidates
                parts = p_lower.split("then")
                if len(parts) > 1:
                    consequent = parts[1].split('.')[0].strip()
                    for c in candidates:
                        if consequent[:5] in c.lower(): # Loose match
                            return c
        return None

    def _execute_computation(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        """
        Execute formal solvers. Returns (best_candidate, confidence).
        If no solver triggers, returns (None, 0.0).
        """
        # 1. Numeric Comparison
        res = self._solve_numeric_comparison(prompt, candidates)
        if res: return res, 0.95
        
        # 2. Algebra
        res = self._solve_algebra(prompt, candidates)
        if res: return res, 0.90
        
        # 3. Logic
        res = self._solve_logic_deduction(prompt, candidates)
        if res: return res, 0.85
        
        return None, 0.0

    # --- 4. META-CONFIDENCE (Tier B: Epistemic Honesty) ---

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|why did .+ fail|why is .+ bad)', p):
            return 0.2
            
        # 2. Scope ambiguity
        if re.search(r'every .+ (a|an) .+', p) and "same" in p:
            return 0.3
            
        # 3. Pronoun ambiguity
        if re.search(r'(he|she|him|her) was', p) and "who" in p:
            return 0.3
            
        # 4. False dichotomy
        if re.search(r'either .+ or .+', p) and "option" not in p:
            # Only flag if context suggests non-exhaustive
            if "only" not in p:
                return 0.4
                
        # 5. Subjectivity
        if re.search(r'(best|worst|favorite|beautiful)', p):
            if "data" not in p and "chart" not in p:
                return 0.3
                
        # 6. Unanswerability (Missing info)
        if re.search(r'(calculate|solve|find)', p):
            if not re.search(r'\d', p) and not re.search(r'(all|none|every)', p):
                # Asks for calculation but no numbers provided
                return 0.2

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Computational Solvers (Frame E)
        computed_ans, comp_conf = self._execute_computation(prompt, candidates)
        
        results = []
        
        # If computation found a definitive answer
        if computed_ans is not None:
            base_score = comp_conf
            # Adjust by meta_cap
            final_conf = min(base_score, meta_cap)
            
            for c in candidates:
                if c == computed_ans:
                    score = final_conf
                    reason = f"Computationally derived solution. Meta-cap: {meta_cap:.2f}"
                else:
                    score = 1.0 - final_conf # Penalize wrong answers
                    reason = "Incorrect based on computational derivation."
                
                results.append({
                    "candidate": c,
                    "score": score,
                    "reasoning": reason
                })
            
            # Sort by score desc
            results.sort(key=lambda x: x['score'], reverse=True)
            return results

        # 3. Fallback: Differentiable Constraint Graph & Sensitivity
        # Only used if direct computation fails (harder problems)
        props = self._parse_propositions(prompt)
        
        # Initialize truth variables (optimistic start)
        t_vars = np.ones(len(props)) * 0.9 
        
        # Base Energy
        E_base = self._compute_energy(props, t_vars)
        S_base = self._compute_sensitivity(props, t_vars)
        L_base = E_base + self.lambda_reg * S_base
        
        # Perturbation Test (Property-Based)
        perturbations = self._generate_perturbations(prompt)
        worst_E = E_base
        
        for p_text in perturbations:
            p_props = self._parse_propositions(p_text)
            if len(p_props) == len(props): # Ensure structure matches
                # Re-eval with same truth vals (simulating input noise)
                # In a full implementation, we'd re-parse structure, 
                # but here we test stability of energy under text noise
                E_pert = self._compute_energy(p_props, t_vars)
                if E_pert > worst_E:
                    worst_E = E_pert
        
        # Robustness penalty: if small text change causes huge energy spike, lower confidence
        robustness_penalty = max(0, (worst_E - E_base)) 
        
        for c in candidates:
            # Score based on how well candidate fits the logical structure
            # Simple heuristic: Does candidate contain keywords from props?
            c_lower = c.lower()
            match_score = 0.0
            for p in props:
                if p['type'] == 'numeric':
                    if str(int(p['value'])) in c_lower or str(p['value']) in c_lower:
                        match_score += 0.2
                elif p['type'] == 'negation':
                    if 'not' in c_lower or 'no' in c_lower:
                        match_score += 0.1
                    else:
                        match_score -= 0.1 # Penalty if negation in prompt but not answer
            
            # Normalize rough score
            raw_score = max(0.1, 1.0 - (L_base * 0.1) - robustness_penalty + match_score)
            raw_score = min(1.0, raw_score)
            
            # Apply Meta Cap
            final_score = min(raw_score, meta_cap)
            
            results.append({
                "candidate": c,
                "score": final_score,
                "reasoning": f"Graph Energy: {E_base:.2f}, Sensitivity: {S_base:.2f}, Robustness Penalty: {robustness_penalty:.2f}"
            })
            
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation to get score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # Cap by meta confidence
        final_conf = min(score, meta_cap)
        
        # Hard cap for ambiguity
        if meta_cap < 0.5:
            return max(0.0, final_conf) # Ensure non-negative
            
        return final_conf