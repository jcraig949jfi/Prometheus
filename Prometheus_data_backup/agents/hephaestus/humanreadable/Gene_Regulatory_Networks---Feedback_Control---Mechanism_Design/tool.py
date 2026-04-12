import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a Gene Regulatory Network (GRN) inspired reasoning engine with 
    Feedback Control and Mechanism Design scoring.
    
    Mechanism:
    1. Parsing: Converts text propositions into nodes and logical operators into 
       signed edges (+1 activation, -1 inhibition) to form an adjacency matrix W.
    2. Reference Model: Constructs a target W* from the most structurally complete candidate.
    3. Dynamics: Propagates truth values x = sigma(W * x0) where x0 are observed facts.
    4. Control: Uses a PID-like loop to adjust W towards W* minimizing error e = x* - x.
    5. Scoring: Assigns scores based on error reduction (mechanism design), penalizing 
       candidates requiring significant structural correction.
       
    Epistemic Honesty:
    Integrates a meta-cognitive layer to detect ambiguity, presuppositions, and 
    unanswerable queries, capping confidence to ensure calibration.
    """

    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.1
        self.max_steps = 10
        self.tol = 1e-3
        
        # Linguistic patterns
        self.negations = ['not', 'no', 'never', 'neither', 'without', 'fails']
        self.conditionals = ['if', 'then', 'implies', 'leads to', 'causes']
        self.biconditionals = ['iff', 'if and only if', 'equivalent']
        self.comparators = ['>', '<', '=', '!=', 'greater', 'less', 'equal']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'stopped', 'why did', 'how did']
        self.ambiguity_triggers = ['every', 'all', 'he', 'she', 'it', 'they', 'either', 'or']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[<>=!]+', text.lower())

    def _extract_propositions(self, text: str) -> List[str]:
        # Simple sentence splitting and cleaning
        sentences = re.split(r'[.;]', text)
        props = []
        for s in sentences:
            s = s.strip()
            if s:
                props.append(s)
        return props

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Parses text into nodes and adjacency matrix W."""
        props = self._extract_propositions(text)
        if not props:
            return [], np.array([]), np.array([])
            
        n = len(props)
        W = np.zeros((n, n))
        nodes = props
        
        tokens = self._tokenize(text)
        
        # Build edges based on linguistic cues
        for i, p_i in enumerate(props):
            for j, p_j in enumerate(props):
                if i == j: continue
                
                # Self-loop for stability
                W[i, i] = 1.0 

                p_i_low = p_i.lower()
                p_j_low = p_j.lower()
                
                # Check for negation in source affecting target
                is_negated = any(neg in p_i_low for neg in self.negations)
                
                # Check for conditionals connecting i -> j
                has_conditional = any(cond in p_i_low or cond in p_j_low for cond in self.conditionals)
                has_bicond = any(bi in p_i_low or bi in p_j_low for bi in self.biconditionals)
                
                # Heuristic: If sentence i contains "if" and sentence j is the consequence logic
                # Since we split by '.', we look for keyword overlap or explicit connectors
                common_words = set(p_i_low.split()) & set(p_j_low.split())
                
                edge_weight = 0.0
                
                if has_bicond:
                    edge_weight = 1.0 if not is_negated else -1.0
                    W[i, j] = edge_weight
                    W[j, i] = edge_weight # Bidirectional
                elif has_conditional or len(common_words) > 0:
                    # Activation vs Inhibition
                    sign = -1.0 if is_negated else 1.0
                    W[i, j] = sign * 1.0
                    
                # Comparators
                if any(c in p_i_low for c in self.comparators):
                     W[i, j] = 1.0 if '=' in p_i_low or 'equal' in p_i_low else 1.0

        return nodes, W

    def _get_initial_state(self, text: str, nodes: List[str]) -> np.ndarray:
        """Extracts observed facts (x0) from text."""
        if not nodes:
            return np.array([])
            
        x0 = np.zeros(len(nodes))
        text_low = text.lower()
        
        # Heuristic: Nodes that appear as standalone facts or premises
        for i, node in enumerate(nodes):
            node_low = node.lower()
            # If the node text appears explicitly and doesn't start with 'if'
            if node_low in text_low and not node_low.strip().startswith('if'):
                # Check if it's a positive assertion
                is_neg = any(n in node_low for n in self.negations)
                if not is_neg:
                    x0[i] = 1.0
                else:
                    x0[i] = 0.0 # Explicitly false
            elif node_low.startswith('if'):
                x0[i] = 0.0 # Condition not yet met
            else:
                x0[i] = 0.5 # Unknown
                
        return x0

    def _propagate(self, W: np.ndarray, x0: np.ndarray) -> np.ndarray:
        """Propagates truth values through the network."""
        if W.size == 0:
            return x0
            
        x = x0.copy()
        for _ in range(5): # Fixed point iteration
            x_new = np.dot(W, x)
            # Hard threshold activation function sigma
            x_new = np.where(x_new > 0.5, 1.0, 0.0)
            if np.array_equal(x, x_new):
                break
            x = x_new
        return x

    def _run_control_loop(self, W: np.ndarray, W_star: np.ndarray, x0: np.ndarray) -> float:
        """Runs the PID control loop to measure correction cost."""
        if W.size == 0 or W_star.size == 0:
            return 0.0
            
        e_prev = np.zeros_like(W)
        integral = np.zeros_like(W)
        
        for t in range(self.max_steps):
            # Compute error in state space
            x = self._propagate(W, x0)
            x_star = self._propagate(W_star, x0)
            
            # State error vector
            e_vec = x_star - x
            
            # If converged
            if np.linalg.norm(e_vec) < self.tol:
                break
                
            # Map state error to weight adjustments (Simplified Jacobian approximation)
            # In GRN, weight change is proportional to pre-synaptic activity * error
            # Here we use a direct proportional control on the matrix difference for stability
            derivative = e_vec.reshape(-1, 1) # Simplified
            
            # PID Term (Applied to weights directly as a proxy for structural correction)
            # We simulate the 'cost' by how much W needs to change to match W_star's output
            # Actual implementation: Measure distance between W and W_star required to minimize e
            
            # Simplified for implementation: 
            # The "Control Effort" is the magnitude of difference between current W and target W
            # required to reduce state error.
            
            # Let's approximate the control signal as the difference needed to align outputs
            # Delta W ~ (x* - x) * x^T (Hebbian-like update rule for error correction)
            delta_W = self.Kp * np.outer(e_vec, x) 
            
            W = W + delta_W
            W = np.clip(W, -1, 1)
            
            e_prev = e_vec.reshape(W.shape) # Reset for next iter shape
            
        # Final Score: Negative of the total modification required (Mechanism Design)
        # Less modification = Higher score (More truthful/accurate initially)
        cost = np.linalg.norm(W - W_star)
        return float(1.0 / (1.0 + cost))

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for epistemic traps and ambiguity."""
        p_low = prompt.lower()
        score = 1.0
        
        # 1. Presupposition check
        if any(trig in p_low for trig in self.presupposition_triggers):
            if 'have you' in p_low or 'why did' in p_low or 'how did' in p_low:
                score -= 0.8
        
        # 2. Scope/Pronoun Ambiguity
        if any(trig in p_low for trig in self.ambiguity_triggers):
            if 'who' in p_low or 'which one' in p_low or 'same' in p_low:
                score -= 0.7
                
        # 3. Subjectivity
        if any(word in p_low for word in ['best', 'worst', 'favorite', 'opinion']):
            if 'measure' not in p_low and 'data' not in p_low:
                score -= 0.6
                
        # 4. False Dichotomy
        if 'either' in p_low and 'or' in p_low:
            if 'only' not in p_low: # Unless specified exhaustive
                score -= 0.5
                
        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Construct Reference Model (W*) from the longest/most detailed candidate
        # Assumption: The most detailed answer contains the most complete logical structure
        ref_candidate = max(candidates, key=len)
        nodes_star, W_star = self._parse_graph(ref_candidate)
        
        if W_star.size == 0:
            # Fallback if parsing fails completely
            scores = [(c, 0.5, "Parsing failed, using default.") for c in candidates]
            return sorted([{"candidate": c, "score": s, "reasoning": r} for c, s, r in scores], key=lambda x: -x['score'])

        x0 = self._get_initial_state(prompt + " " + ref_candidate, nodes_star)
        
        results = []
        for cand in candidates:
            nodes, W = self._parse_graph(cand)
            
            if W.size == 0:
                score = 0.1
                reason = "No logical structure detected."
            else:
                # Align dimensions if possible (simplified: assume same nodes for now or pad)
                # For this implementation, we compare the propagation result of the candidate
                # against the reference model's propagation using the control loop cost.
                
                # Resize W to match W_star if needed (padding with zeros)
                if W.shape != W_star.shape:
                    min_dim = min(W.shape[0], W_star.shape[0])
                    # Truncate or Pad logic simplified to truncation for matching
                    if W.shape[0] > W_star.shape[0]:
                        W = W[:W_star.shape[0], :W_star.shape[1]]
                    else:
                        temp_W = np.zeros_like(W_star)
                        temp_W[:W.shape[0], :W.shape[1]] = W
                        W = temp_W
                    
                    if len(x0) != W_star.shape[0]:
                        x0 = np.resize(x0, W_star.shape[0])

                # Run Control Loop to find correction cost
                correction_score = self._run_control_loop(W.copy(), W_star, x0)
                
                # Add structural similarity bonus (NCD as tiebreaker < 15%)
                import zlib
                def ncd(a, b):
                    if not a or not b: return 1.0
                    l_a, l_b = len(a), len(b)
                    if l_a == 0 or l_b == 0: return 1.0
                    try:
                        c_ab = len(zlib.compress((a+b).encode()))
                        c_a = len(zlib.compress(a.encode()))
                        c_b = len(zlib.compress(b.encode()))
                        return (c_ab - min(c_a, c_b)) / max(c_a, c_b)
                    except: return 1.0
                
                ncd_score = 1.0 - ncd(cand, ref_candidate)
                
                # Weighted Score: 85% Control Logic, 15% NCD
                final_score = 0.85 * correction_score + 0.15 * ncd_score
                score = float(np.clip(final_score, 0, 1))
                reason = f"Control convergence score: {correction_score:.2f}, Structural similarity: {ncd_score:.2f}"

            results.append({"candidate": cand, "score": score, "reasoning": reason})
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-cognitive check for ambiguity/traps
        meta_score = self._meta_confidence(prompt)
        
        # If meta_score is low, cap confidence immediately (Epistemic Honesty)
        if meta_score < 0.4:
            return min(0.3, meta_score + 0.1) # Return low confidence
        
        # 2. Structural validation
        nodes, W = self._parse_graph(answer)
        if W.size == 0 or len(nodes) == 0:
            return 0.2 # Low confidence if no structure
            
        # 3. Consistency check (Self-consistency)
        # Does the answer contradict itself?
        # Simple check: If W has strong positive and negative cycles that don't resolve
        x0 = self._get_initial_state(answer, nodes)
        x_final = self._propagate(W, x0)
        
        # If the network is unstable or empty, lower confidence
        if np.all(x_final == 0) and np.any(x0 > 0):
            # Everything died out despite inputs -> weak reasoning chain
            base_conf = 0.4
        else:
            base_conf = 0.85
            
        # Cap based on meta-analysis
        final_conf = min(base_conf, meta_score)
        
        # Never return > 0.9 unless it's a pure calculation (hard to verify without specific math parser)
        # But for general reasoning, cap at 0.9 to maintain uncertainty
        return float(np.clip(final_conf, 0.0, 0.9))