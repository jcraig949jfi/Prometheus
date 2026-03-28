import re
import math
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer fusing Structural Parsing, Hoare Logic constraints,
    and Chaos/Sensitivity analysis.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (P_i), negations, comparatives, and conditionals 
       using regex to build a directed constraint graph.
    2. Hoare Layer: Checks sequential consistency. If statement A implies B, but the text 
       asserts A then not-B, a penalty is applied.
    3. Chaos/Sensitivity: Treats the logic graph as a Boolean dynamical system. Input bits 
       are flipped to measure output sensitivity (Lyapunov-like exponent). Robust answers 
       have low sensitivity (negative lambda).
    4. Scoring: Weighted sum of logical validity, robustness, and stability.
    """

    def __init__(self):
        self.weights = (0.4, 0.3, 0.3)  # w1: Hoare, w2: Sensitivity, w3: Chaos
        self.epsilon = 1e-6

    def _parse_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]]]:
        """Extract propositions and edges (u, v, type)."""
        text = text.lower()
        props = []
        edges = []
        prop_map = {}
        
        # Helper to index propositions
        def get_pid(p: str) -> int:
            p = p.strip()
            if not p: return -1
            if p not in prop_map:
                prop_map[p] = len(props)
                props.append(p)
            return prop_map[p]

        # 1. Extract Comparatives (x < y, x > y, x = y)
        comp_re = r'(\w+)\s*(<|>|=|<=|>=)\s*(\w+)'
        for m in re.finditer(comp_re, text):
            lhs, op, rhs = m.groups()
            pid_lhs = get_pid(f"{lhs}{op}{rhs}")
            # Create implicit proposition
            if pid_lhs not in [get_pid(p) for p in [lhs, rhs]]: 
                # Simplified: treat comparison as a node dependent on operands if they exist
                pass 
            # For this implementation, we treat the comparison string as the proposition
            pid = get_pid(f"{lhs} {op} {rhs}")
            # Add self-loop or dependency if operands are defined elsewhere? 
            # Simplified: Just register the proposition existence for now.

        # 2. Extract Conditionals (if A then B, A implies B)
        cond_re = r'(?:if|when|then|implies|causes)\s+(\w+)(?:\s+(?:then|implies|causes))?\s+(\w+)'
        for m in re.finditer(cond_re, text):
            antecedent, consequent = m.groups()
            u = get_pid(antecedent)
            v = get_pid(consequent)
            edges.append((u, v, 'cond'))

        # 3. Extract Negations (not A, A is false)
        neg_re = r'(?:not|no|never|false)\s+(\w+)'
        for m in re.finditer(neg_re, text):
            target = m.group(1)
            u = get_pid(target)
            # Mark as negated edge from a virtual 'TRUE' node? 
            # Simplified: We track negation in the evaluation phase by string matching
            edges.append((-1, u, 'neg')) # -1 indicates negation marker

        # 4. Sequential cues for Hoare (A then B)
        seq_re = r'(\w+)\s+(?:then|after|next|followed by)\s+(\w+)'
        for m in re.finditer(seq_re, text):
            pre, post = m.groups()
            u = get_pid(pre)
            v = get_pid(post)
            edges.append((u, v, 'seq'))

        return props, edges

    def _evaluate_bool_system(self, props: List[str], edges: List[Tuple], inputs: Dict[int, bool]) -> Dict[int, bool]:
        """Propagate boolean values through the graph."""
        state = inputs.copy()
        # Initialize unmentioned nodes to False by default for this simulation
        for i in range(len(props)):
            if i not in state: state[i] = False
            
        # Simple fixed-point iteration (max 10 steps)
        for _ in range(10):
            changed = False
            for u, v, typ in edges:
                if typ == 'cond': # u -> v
                    if u in state and state[u]:
                        if v not in state or not state[v]:
                            state[v] = True
                            changed = True
                elif typ == 'seq': # u then v
                    if u in state and state[u]:
                        if v not in state or not state[v]:
                            state[v] = True
                            changed = True
                elif typ == 'neg': # not v (u is -1)
                    # Negation is tricky in propagation without explicit structure.
                    # We skip dynamic negation propagation for simplicity in this rough approx.
                    pass
            if not changed: break
        return state

    def _check_hoare_violations(self, props: List[str], edges: List[Tuple], text: str) -> float:
        """Check for logical contradictions in sequential statements."""
        violations = 0
        total_checks = 1
        
        # Check explicit contradictions: "A then not A" or "If A then B" + "A and not B"
        text_lower = text.lower()
        
        # Pattern: A then not A
        contr_re = r'(\w+)\s+then\s+(?:not|no)\s+\1'
        if re.search(contr_re, text_lower):
            violations += 1
        total_checks += 1

        # Pattern: If A then B ... A ... not B (simplified check)
        # We look for "if X then Y" and later "not Y" while assuming X is true contextually
        # This is a heuristic approximation of Hoare Triple failure {Pre} Stmt {Post}
        if_edges = [(m.group(1), m.group(2)) for m in re.finditer(r'if\s+(\w+)\s+then\s+(\w+)', text_lower)]
        for ant, cons in if_edges:
            # Check if text contains ant and (not cons) elsewhere
            if re.search(rf'\b{ant}\b', text_lower) and re.search(rf'not\s+{cons}', text_lower):
                violations += 1
            total_checks += 1
            
        return violations / max(total_checks, 1)

    def _compute_sensitivity(self, props: List[str], edges: List[Tuple]) -> Tuple[float, float]:
        """Compute average sensitivity and Lyapunov-like exponent."""
        if not props:
            return 0.0, 0.0
            
        n_inputs = len(props)
        if n_inputs == 0: return 0.0, 0.0
        
        sensitivities = []
        lyap_sum = 0.0
        
        # Treat all props as potential inputs for this simulation
        base_inputs = {i: (i % 2 == 0) for i in range(n_inputs)} # Alternating T/F base
        
        # Base output (simplified: count True nodes)
        base_state = self._evaluate_bool_system(props, edges, base_inputs)
        base_out = sum(base_state.values())
        
        for i in range(n_inputs):
            # Perturb input i
            perturbed_inputs = base_inputs.copy()
            perturbed_inputs[i] = not perturbed_inputs[i]
            
            pert_state = self._evaluate_bool_system(props, edges, perturbed_inputs)
            pert_out = sum(pert_state.values())
            
            delta_out = abs(pert_out - base_out)
            s_i = float(delta_out) # |Delta Output| / |Delta Input| (input delta is 1)
            sensitivities.append(s_i)
            
            # Lyapunov approx: log2(s_i + epsilon)
            lyap_sum += math.log2(s_i + self.epsilon)
            
        avg_sens = np.mean(sensitivities) if sensitivities else 0.0
        lambda_exp = lyap_sum / max(n_inputs, 1)
        
        return avg_sens, lambda_exp

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Parse
            props, edges = self._parse_graph(cand)
            
            # 2. Hoare Violation Check
            violation_ratio = self._check_hoare_violations(props, edges, cand)
            hoare_score = 1.0 - violation_ratio
            
            # 3. Sensitivity & Chaos
            avg_sens, lambda_exp = self._compute_sensitivity(props, edges)
            # Normalize sensitivity: lower is better. Max sens is roughly N, but we cap at 1 for scoring
            sens_score = 1.0 - min(avg_sens / (len(props) + 1), 1.0) if props else 1.0
            
            # Chaos score: exp(-lambda). Negative lambda (stable) -> high score.
            chaos_score = math.exp(-lambda_exp)
            # Clamp chaos score to [0, 1] roughly
            chaos_score = max(0.0, min(1.0, chaos_score / 2.0 + 0.5)) # Adjust scaling

            # 4. Final Score
            w1, w2, w3 = self.weights
            score = w1 * hoare_score + w2 * sens_score + w3 * chaos_score
            
            # Fallback/NCD Tiebreaker if structural signal is weak (no props found)
            if not props:
                import zlib
                # Simple NCD approximation against prompt
                try:
                    z_prompt = len(zlib.compress(prompt.encode()))
                    z_cand = len(zlib.compress(cand.encode()))
                    z_both = len(zlib.compress((prompt + cand).encode()))
                    ncd = (z_both - min(z_prompt, z_cand)) / max(z_prompt, z_cand, 1)
                    score = (score + (1-ncd)) / 2.0 # Blend with structural score
                except:
                    pass

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Hoare:{hoare_score:.2f}, Sens:{sens_score:.2f}, Chaos:{chaos_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the top candidate score logic."""
        # Evaluate as a single candidate list
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Map score 0-1 to confidence. 
        # High structural consistency = high confidence.
        return res[0]['score']