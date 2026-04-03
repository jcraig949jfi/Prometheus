import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Constraint-Driven Lyapunov-Pragmatic Scorer (CLPS)
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, numeric constraints, and logical relations
       (negation, implication, ordering) using regex.
    2. Dynamical System: Models truth values as a state vector s. Iteratively applies 
       constraint propagation (modus ponens, transitivity) via matrix operations until 
       convergence (Lyapunov stability).
    3. Scoring: Candidates are scored by (a) Logical Consistency (stability of the system),
       (b) Numeric Validity (direct evaluation of extracted inequalities), and (c) Pragmatic
       Utility (heuristic bonus for structural completeness). 
    4. NCD Tiebreaker: Used only if structural signals are identical.
    """
    
    def __init__(self):
        self.tau = 0.5  # Threshold for activation
        self.w_imp = 0.9 # Weight for implication
        self.w_ord = 0.95 # Weight for ordering
        self.max_iter = 10
        
        # Pragmatic cache: simple heuristic scores for logical forms
        self.pragmatic_cache = {
            "implication": 0.1,
            "negation": 0.05,
            "numeric": 0.2,
            "default": 0.0
        }

    def _parse_structure(self, text: str) -> Tuple[List[str], List[Tuple], List[Tuple], List[Tuple]]:
        """Extract nodes, implications, orderings, and negations."""
        text_lower = text.lower()
        nodes = []
        implications = [] # (src_idx, tgt_idx)
        orderings = []    # (left_val, right_val) or (left_idx, right_idx)
        negations = []    # (target_idx)
        
        # Tokenize simple propositions (words/numbers)
        tokens = re.findall(r'\b\w+\b', text_lower)
        node_map = {}
        idx = 0
        for t in tokens:
            if t not in node_map:
                node_map[t] = idx
                nodes.append(t)
                idx += 1
        
        # 1. Negations: "not X", "no X"
        for match in re.finditer(r'(?:not|no)\s+(\w+)', text_lower):
            target = match.group(1)
            if target in node_map:
                negations.append(node_map[target])
                
        # 2. Implications: "if A then B", "A causes B", "A leads to B"
        patterns_imp = [
            r'if\s+(\w+)\s+(?:then\s+)?(\w+)',
            r'(\w+)\s+(?:causes|leads to|implies)\s+(\w+)'
        ]
        for pat in patterns_imp:
            for match in re.finditer(pat, text_lower):
                src, tgt = match.group(1), match.group(2)
                if src in node_map and tgt in node_map:
                    implications.append((node_map[src], node_map[tgt]))
                    
        # 3. Orderings/Comparatives: "A > B", "A greater than B", "5 < 10"
        # Numeric direct
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s*(?:<|less than|>|greater than|=)\s*(\d+(?:\.\d+)?)', text_lower):
            try:
                v1, v2 = float(match.group(1)), float(match.group(2))
                op = match.group(0)
                if ('<' in op or 'less' in op) and v1 < v2: orderings.append((True, v1, v2))
                elif ('>' in op or 'greater' in op) and v1 > v2: orderings.append((True, v1, v2))
                elif '=' in op and abs(v1-v2)<1e-9: orderings.append((True, v1, v2))
                else: orderings.append((False, v1, v2)) # Contradiction
            except: pass
            
        # Symbolic ordering A < B
        for match in re.finditer(r'(\w+)\s+(?:is\s+)?(?:less than|before|precedes)\s+(\w+)', text_lower):
            a, b = match.group(1), match.group(2)
            if a in node_map and b in node_map:
                orderings.append((True, node_map[a], node_map[b])) # Symbolic true if structure exists
                
        return nodes, implications, orderings, negations

    def _propagate_constraints(self, n: int, implications: List, negations: List) -> Tuple[np.ndarray, float]:
        """Run dynamical system to fixed point. Return final state and Lyapunov delta."""
        s = np.full(n, 0.5) # Initial uncertainty
        
        # Build adjacency matrix W
        W = np.zeros((n, n))
        for src, tgt in implications:
            W[tgt, src] = self.w_imp
            
        # Iterative update s_{t+1} = sigma(W @ s + b)
        for k in range(self.max_iter):
            s_old = s.copy()
            
            # Matrix op for implications
            s_new = W @ s
            
            # Handle negations (simple inversion if source is high confidence)
            # Simplified: if node is in negation list, push towards 1-s elsewhere? 
            # Instead, we treat negation as a constraint on the node itself if context implies it.
            # For this implementation, we focus on propagation stability.
            
            # Activation (clipped linear)
            s_new = np.clip(s_new, 0, 1)
            
            # Add base confidence from self (damping) to prevent collapse to 0
            s = 0.5 * s + 0.5 * s_new 
            
            # Check convergence (Lyapunov-like measure)
            if k == self.max_iter - 1:
                L = float(np.linalg.norm(s - s_old))
            else:
                if np.allclose(s, s_old, atol=1e-6):
                    L = 0.0
                    break
                    
        return s, L

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_nodes, p_imp, p_ord, p_neg = self._parse_structure(prompt)
        n_nodes = len(prompt_nodes)
        
        # Calculate baseline metrics for the prompt
        base_score = 0.0
        if n_nodes > 0:
            _, L = self._propagate_constraints(n_nodes, p_imp, p_neg)
            # Stability bonus: lower L is better
            base_score += (1.0 - min(L, 1.0)) * 0.3
            
        # Numeric validation from prompt
        numeric_valid = True
        for is_true, v1, v2 in p_ord:
            if not is_true: numeric_valid = False; break
            
        for cand in candidates:
            score = base_score
            reasoning = []
            
            # 1. Structural Overlap & Pragmatic Utility
            c_nodes, c_imp, c_ord, c_neg = self._parse_structure(cand)
            
            # Check if candidate contradicts prompt numerics
            cand_numeric_ok = True
            for is_true, v1, v2 in c_ord:
                if not is_true: cand_numeric_ok = False; break
            
            if not numeric_valid or not cand_numeric_ok:
                score -= 0.5
                reasoning.append("Numeric contradiction")
            
            # Pragmatic bonus for containing logical keywords found in prompt
            common_nodes = set(prompt_nodes) & set(c_nodes)
            if common_nodes:
                score += 0.1 * (len(common_nodes) / max(1, len(prompt_nodes)))
                reasoning.append("Structural alignment")
                
            # 2. Dynamical Consistency (Candidate specific)
            if len(c_nodes) > 0:
                _, c_L = self._propagate_constraints(len(c_nodes), c_imp, c_neg)
                score += (1.0 - min(c_L, 1.0)) * 0.2
                if c_L < 0.1: reasoning.append("High stability")
            
            # 3. NCD Tiebreaker (only if scores are very close or no structure)
            if len(reasoning) == 0 or abs(score - 0.5) < 0.01:
                ncd = self._compute_ncd(prompt, cand)
                # Lower NCD is better (more similar/compressible together)
                score += (1.0 - ncd) * 0.1
                reasoning.append(f"NCD:{ncd:.2f}")
            else:
                # Small NCD penalty for verbosity without substance
                if len(cand) > len(prompt) * 2:
                    score -= 0.05

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning) if reasoning else "Baseline"
            })
            
        # Rank descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        # Parse both
        p_nodes, p_imp, p_ord, _ = self._parse_structure(prompt)
        a_nodes, a_imp, a_ord, _ = self._parse_structure(answer)
        
        # 1. Numeric Check (Hard constraint)
        all_nums = p_ord + a_ord
        for is_true, _, _ in all_nums:
            if not is_true: return 0.0
            
        # 2. Logical Flow Check (Simplified)
        # If answer introduces new implications not in prompt, slight penalty unless justified
        # Here we just check stability of combined system
        combined_nodes = list(set(p_nodes + a_nodes))
        if not combined_nodes:
            return 0.5 # Uncertain
            
        # Map combined indices (simplified re-indexing for demo)
        # In a full engine, we'd merge graphs properly. 
        # Here we approximate: if answer nodes are subset of prompt nodes, higher confidence.
        overlap = len(set(a_nodes) & set(p_nodes))
        if len(a_nodes) > 0:
            overlap_ratio = overlap / len(a_nodes)
        else:
            overlap_ratio = 0.5
            
        # Base confidence on overlap and lack of numeric contradiction
        conf = 0.5 + (overlap_ratio * 0.4)
        
        # Bonus if answer is short and decisive (Pragmatic heuristic)
        if len(answer.split()) < 10 and any(k in answer.lower() for k in ['yes', 'no', 'true', 'false', '=']):
            conf += 0.05
            
        return min(1.0, max(0.0, conf))