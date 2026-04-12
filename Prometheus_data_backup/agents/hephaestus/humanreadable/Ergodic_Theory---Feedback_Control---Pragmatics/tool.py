import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a reasoning engine combining Ergodic Theory, Feedback Control, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations (negation, causality, ordering)
       using regex to form a propositional graph.
    2. Constraint Representation: Hard constraints (logic) vs Soft constraints (pragmatics).
    3. Ergodic Averaging: Simulates T iterations of random constraint application orders to 
       estimate the expected inconsistency (error) of the system, approximating the space-average.
    4. Feedback Control: Uses a discrete PID controller to adaptively weight soft pragmatic 
       constraints based on the error signal from the ergodic sweep.
    5. Scoring: Final score is inverse to the converged average inconsistency.
    """
    
    def __init__(self):
        # PID Constants
        self.Kp = 0.01
        self.Ki = 0.001
        self.Kd = 0.005
        
        # Ergodic parameters
        self.T_iterations = 200
        self.seed = 42  # Deterministic
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|few|many|every|each)\b', re.IGNORECASE),
            'scalar_implicature': re.compile(r'\b(some|few|might|possibly)\b', re.IGNORECASE),
            'speech_act': re.compile(r'\b(please|suggest|request|order)\b', re.IGNORECASE)
        }

    def _parse_to_graph(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Parse text into nodes (clauses) and edges (relations)."""
        # Simple sentence splitter as node generator
        sentences = [s.strip() for s in re.split(r'[.;!?]', text) if s.strip()]
        if not sentences:
            sentences = [text]
            
        nodes = sentences
        edges = []
        
        # Extract relations between sentences or within sentences
        for i, stmt in enumerate(sentences):
            stmt_lower = stmt.lower()
            
            # Check for negation
            if self.patterns['negation'].search(stmt_lower):
                edges.append((stmt, f"NOT({stmt})", "neg"))
                
            # Check for conditionals (simplified: if A then B -> A implies B)
            if 'if' in stmt_lower and 'then' in stmt_lower:
                parts = re.split(r'\bthen\b', stmt, flags=re.IGNORECASE)
                if len(parts) == 2:
                    edges.append((parts[0].strip(), parts[1].strip(), "implies"))
            
            # Check for causal
            if self.patterns['causal'].search(stmt_lower):
                # Assume subject causes object roughly
                edges.append((stmt, "CAUSAL_LINK", "causes"))
                
            # Check for comparatives (numeric extraction attempt)
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", stmt)
            if len(nums) >= 2 and self.patterns['comparative'].search(stmt_lower):
                edges.append((nums[0], nums[1], "comp"))
                
        return nodes, edges

    def _check_hard_constraints(self, nodes: List[str], edges: List[Tuple], state: Dict[str, bool]) -> int:
        """Count violated hard logical constraints."""
        violations = 0
        for u, v, label in edges:
            if label == "neg":
                # If 'NOT(A)' is in state as True, then A must be False (simplified)
                if u in state and state[u]:
                     violations += 1
            elif label == "implies":
                # If u is True and v is False -> violation
                u_val = state.get(u, False)
                v_val = state.get(v, False)
                if u_val and not v_val:
                    violations += 1
        return violations

    def _ergodic_sweep(self, nodes: List[str], edges: List[Tuple], soft_weights: Dict[str, float]) -> float:
        """
        Perform T iterations of random constraint ordering to estimate average inconsistency.
        Returns the time-averaged error.
        """
        rng = np.random.default_rng(self.seed)
        total_error = 0.0
        
        # Initialize state (all False initially)
        base_state = {n: False for n in nodes}
        
        for t in range(self.T_iterations):
            # Random permutation of edges (Ergodic step)
            shuffled_edges = list(edges)
            rng.shuffle(shuffled_edges)
            
            # Unit propagation / Fix-point attempt
            current_state = base_state.copy()
            step_violations = 0
            
            # Apply hard constraints
            for u, v, label in shuffled_edges:
                if label == "neg":
                    # Propagate negation
                    if u in current_state:
                        current_state[u] = not current_state[u]
                elif label == "implies":
                    if u in current_state and current_state[u]:
                        if v in current_state:
                            current_state[v] = True
            
            # Calculate Hard Violations
            hard_violations = self._check_hard_constraints(nodes, edges, current_state)
            
            # Calculate Soft Violations (Pragmatics)
            # Heuristic: If scalar implicature trigger exists but context suggests 'all', penalize
            soft_penalty = 0.0
            for node in nodes:
                if self.patterns['scalar_implicature'].search(node.lower()):
                    # Soft constraint: 'some' implies 'not all' pragmatically
                    # If we treated it as 'all' in logic, add penalty weighted by w
                    w = soft_weights.get('scalar', 1.0)
                    if "all" in node.lower(): 
                        soft_penalty += w * 0.5 # Partial penalty
            
            # Total error for this sweep
            e_t = (hard_violations + soft_penalty) / (len(edges) + 1) if (len(edges) + 1) > 0 else 0
            total_error += e_t
            
        return total_error / self.T_iterations

    def _pid_update(self, weights: Dict[str, float], error: float, prev_errors: List[float]) -> Dict[str, float]:
        """Update soft constraint weights using discrete PID control."""
        # P term
        p_term = self.Kp * error
        
        # I term
        i_term = self.Ki * sum(prev_errors) if prev_errors else 0
        
        # D term
        d_term = 0
        if len(prev_errors) > 1:
            d_term = self.Kd * (error - prev_errors[-1])
            
        adjustment = p_term + i_term + d_term
        
        # Update weights (clamped to positive)
        new_weights = {}
        for k, w in weights.items():
            new_w = max(0.1, w + adjustment) # Prevent zero/negative weights
            new_weights[k] = new_w
        return new_weights

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        all_scores = []
        
        # Pre-calculate prompt structure
        p_nodes, p_edges = self._parse_to_graph(prompt)
        
        # Initial soft weights
        soft_weights = {'scalar': 1.0, 'speech': 1.0}
        error_history = []
        
        # Evaluate each candidate
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            nodes, edges = self._parse_to_graph(full_text)
            
            # Add candidate-specific edges (simple inclusion)
            # In a real graph, we'd merge prompt and candidate graphs explicitly
            combined_edges = p_edges + edges 
            
            # Ergodic Averaging Loop with Feedback
            # We simulate a few "epochs" of PID adjustment for stability per candidate
            current_weights = soft_weights.copy()
            local_errors = []
            
            # Quick convergence simulation (fewer iterations per candidate for speed)
            for _ in range(5): 
                avg_err = self._ergodic_sweep(nodes, combined_edges, current_weights)
                local_errors.append(avg_err)
                current_weights = self._pid_update(current_weights, avg_err, local_errors)
            
            final_error = np.mean(local_errors[-3:]) # Use last few for stability
            score = 1.0 - min(1.0, final_error)
            
            # Fallback to NCD if structural signal is weak (score ~1.0 or 0.0 ambiguity)
            if len(p_edges) == 0:
                # NCD Tiebreaker
                import zlib
                s1 = prompt.encode()
                s2 = cand.encode()
                l1, l2 = len(s1), len(s2)
                if l1 == 0 or l2 == 0:
                    ncd = 1.0
                else:
                    try:
                        ncd = (len(zlib.compress(s1 + s2)) - min(l1, l2)) / max(l1, l2)
                    except:
                        ncd = 0.5
                score = 1.0 - ncd # Higher NCD = less similar = lower score in this context? 
                # Actually for NCD, lower is more similar. If prompt asks question, answer should be related.
                # But NCD is poor for logic. We only use it if no logic found.
                if len(p_edges) == 0:
                     score = 0.5 * (1.0 - ncd) # Downweight NCD only scenarios

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Ergodic error: {final_error:.4f}, Weights: {current_weights}"
            })
            all_scores.append(score)
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        # Reuse evaluate logic but for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']