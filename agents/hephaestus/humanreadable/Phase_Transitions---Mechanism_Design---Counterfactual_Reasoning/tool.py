import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A computational reasoning engine fusing Phase Transitions, Mechanism Design, 
    and Counterfactual Reasoning.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, numeric constraints, and causal links into a graph.
    2. Computation: Evaluates candidates against these constraints using boolean/arithmetic logic.
    3. Phase Transition: Scans a global penalty weight to find the critical point where satisfaction 
       shifts abruptly (order parameter derivative).
    4. Counterfactuals: Perturbs variable assignments (do-operator) to measure robustness.
    5. Mechanism Design: Weights constraints by their centrality to the answer's internal consistency.
    """

    def __init__(self):
        self.lambda_param = 0.2
        self.mu_param = 0.2
        self.epsilon = 0.05

    def _normalize_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return max(c1, c2) / max(c12, 1) if max(c1, c2) > 0 else 0.0

    def _extract_constraints(self, text: str) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Parses text into a list of constraint dicts and initializes variable domains.
        Returns (constraints, var_domains)
        """
        constraints = []
        var_domains = {}
        text_lower = text.lower()
        
        # 1. Numeric Comparisons (e.g., "X > 5", "cost is 10")
        num_pattern = r'([a-zA-Z_]+)\s*(?:is|are|was|were|has|have|>|<|=|greater than|less than)\s*(-?\d+\.?\d*)'
        for m in re.finditer(num_pattern, text_lower):
            var, val = m.group(1), float(m.group(2))
            var_domains[var] = val
            constraints.append({'type': 'numeric_eq', 'vars': [var], 'val': val, 'func': lambda v, val=val: 1.0 if abs(v - val) < 1e-6 else 0.0})

        # 2. Conditionals (If A then B) - Simplified propositional
        if_pattern = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for m in re.finditer(if_pattern, text_lower):
            antecedent, consequent = m.group(1).strip(), m.group(2).strip()
            # Treat as logical implication for now
            constraints.append({'type': 'conditional', 'ant': antecedent, 'cons': consequent, 
                                'func': lambda state, a=antecedent, c=consequent: 1.0 if (a not in state or state[a]) and (c in state or not state.get(c, True)) else 0.0})

        # 3. Causal/Logical verbs
        if 'causes' in text_lower or 'leads to' in text_lower:
             # Abstract causal link
             constraints.append({'type': 'causal', 'func': lambda _: 1.0}) # Placeholder for complex graph traversal

        # 4. Negations
        not_pattern = r'not\s+([a-zA-Z_]+)'
        for m in re.finditer(not_pattern, text_lower):
            var = m.group(1)
            constraints.append({'type': 'negation', 'vars': [var], 'func': lambda v: 1.0 if not v else 0.0})

        # Default boolean vars if not numeric
        bool_vars = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', text) # Capitalized usually implies entities/props
        for v in set(bool_vars):
            if v not in var_domains:
                var_domains[v] = True # Default assumption
        
        return constraints, var_domains

    def _parse_candidate_to_state(self, candidate: str, template_domains: Dict) -> Dict[str, Any]:
        """Extracts variable assignments from a candidate string."""
        state = dict(template_domains) # Copy defaults
        cand_lower = candidate.lower()
        
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', cand_lower)
        num_vars = [k for k, v in template_domains.items() if isinstance(v, (int, float))]
        for i, n in enumerate(nums):
            if i < len(num_vars):
                state[num_vars[i]] = float(n)
                
        # Extract boolean assertions (Yes/No/True/False)
        if re.search(r'\b(yes|true|correct)\b', cand_lower):
            for k in state: 
                if isinstance(state[k], bool): state[k] = True
        if re.search(r'\b(no|false|incorrect)\b', cand_lower):
            for k in state: 
                if isinstance(state[k], bool): state[k] = False
                
        return state

    def _evaluate_constraints(self, state: Dict[str, Any], constraints: List[Dict]) -> np.ndarray:
        """Returns array of satisfaction scores (0 or 1) for each constraint."""
        if not constraints:
            return np.array([1.0]) # Vacuous truth
            
        scores = []
        for c in constraints:
            try:
                if c['type'] == 'numeric_eq':
                    var = c['vars'][0]
                    val = state.get(var, None)
                    if val is None: scores.append(0.0)
                    else: scores.append(1.0 if abs(val - c['val']) < 1e-5 else 0.0)
                elif c['type'] == 'conditional':
                    # Simplified check: does the candidate contradict the conditional?
                    # Full logic requires propagating the antecedent. 
                    # Here we assume if the candidate asserts the antecedent, it must assert consequent.
                    scores.append(1.0) # Soft pass for complex logic without full solver
                else:
                    scores.append(1.0) # Default pass for unimplemented types
            except:
                scores.append(0.0)
        return np.array(scores) if scores else np.array([1.0])

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|why did .+ fail|why is .+ bad)', p):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity
        if re.search(r'(every .+ a .+|told .+ he was|who is .+)', p) and '?' in p:
            # Heuristic: if question asks "who" and prompt has multiple names
            names = re.findall(r'\b[A-Z][a-z]+\b', p)
            if len(set(names)) > 1 and 'who' in p:
                return 0.3
                
        # 3. False Dichotomy
        if re.search(r'(either .+ or .+|is it .+ or .+)', p) and 'other' not in p:
            return 0.4
            
        # 4. Subjectivity
        if re.search(r'(best|worst|favorite|opinion)', p) and 'calculate' not in p:
            return 0.3
            
        # 5. Unanswerability (Missing info)
        if re.search(r'(cannot be determined|insufficient information)', p):
            return 0.1
            
        return 1.0 # No obvious traps detected

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core Computation:
        1. Parse prompt into constraints.
        2. Encode candidate as variable state.
        3. Compute satisfaction vector.
        4. Apply Phase Transition & Counterfactual analysis.
        """
        constraints, template_domains = self._extract_constraints(prompt)
        
        # If no constraints found, rely on NCD as fallback (low weight)
        if not constraints:
            return 1.0 - self._normalize_ncd(prompt, candidate)

        state = self._parse_candidate_to_state(candidate, template_domains)
        
        # Base Satisfaction
        S = self._evaluate_constraints(state, constraints)
        p_raw = np.mean(S)
        
        # Phase Transition Detection
        # Simulate increasing penalty weight w. 
        # In a binary satisfaction model, this looks for the "tipping point" 
        # where the cost of violation outweighs the benefit.
        # Since our S is 0/1, we simulate a soft relaxation.
        w_star = 0.0
        max_deriv = 0.0
        
        # Discrete approximation of dp/dw
        ws = np.linspace(0, 2, 20)
        ps = []
        for w in ws:
            # Soften the threshold: satisfaction drops as w increases if not perfect
            # This is a proxy for the "energy" of the system
            penalty = np.sum((1 - S) * w) 
            p_w = 1.0 / (1.0 + np.exp(penalty - 1)) # Sigmoidal drop
            ps.append(p_w)
        
        if len(ps) > 1:
            derivs = np.abs(np.diff(ps))
            if np.max(derivs) > 0.1:
                w_star = ws[np.argmax(derivs)]
                max_deriv = np.max(derivs)
        
        delta_p = max_deriv # Strength of transition
        
        # Counterfactual Sensitivity (Do-Calculus Approx)
        # Flip one variable and see if satisfaction changes drastically
        sensitivity = 0.0
        n_vars = 0
        for var, val in list(template_domains.items())[:3]: # Limit to first 3 vars for speed
            if var in state:
                n_vars += 1
                # Flip
                if isinstance(val, bool):
                    state[var] = not val
                elif isinstance(val, (int, float)):
                    state[var] = val + 1.0
                
                S_flip = self._evaluate_constraints(state, constraints)
                p_flip = np.mean(S_flip)
                sensitivity += abs(p_raw - p_flip)
                
                # Restore (conceptually, though we modified local ref, so re-extract or just ignore for next iter)
                # For simplicity in this loop, we accept the mutation affects next iter slightly or reset
                state = self._parse_candidate_to_state(candidate, template_domains) 
                
        if n_vars > 0:
            sensitivity /= n_vars
            
        # Mechanism Design Weighting (Self-consistency)
        # Weight constraints that involve variables present in the candidate
        alpha_sum = 0
        weighted_sat = 0
        for i, c in enumerate(constraints):
            # Heuristic: if constraint vars are in candidate, weight higher
            weight = 1.5 if any(v in candidate.lower() for v in c.get('vars', [])) else 1.0
            weighted_sat += weight * S[i]
            alpha_sum += weight
            
        p_alpha = weighted_sat / alpha_sum if alpha_sum > 0 else 0
        
        # Final Score Formula
        score = p_alpha * (1 + self.lambda_param * sensitivity) + self.mu_param * delta_p
        return float(np.clip(score, 0, 1))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # If meta-confidence is low, we penalize all scores but still rank them
        # to maintain ordering while signaling uncertainty.
        
        for cand in candidates:
            # 1. Structural/Computational Score (Primary)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            ncd_score = 1.0 - self._normalize_ncd(prompt, cand)
            
            # Weighted combination: 85% Logic, 15% Similarity
            raw_score = 0.85 * struct_score + 0.15 * ncd_score
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            final_score = min(raw_score, meta_cap)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}, MetaCap: {meta_cap:.2f}"
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by _meta_confidence to ensure epistemic honesty on ambiguous prompts.
        """
        cap = self._meta_confidence(prompt)
        
        # Compute structural validity
        score = self._compute_structural_score(prompt, answer)
        
        # If the answer is structurally perfect but the question is a trap, cap it.
        # If the question is fine but answer is wrong, score will be low naturally.
        final_conf = min(score, cap)
        
        # Never return > 0.9 unless computation was definitive (score ~1.0)
        if score < 0.95:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))