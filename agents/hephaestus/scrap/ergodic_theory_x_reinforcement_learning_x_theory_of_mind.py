import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-RL-ToM Scorer:
    1. Parses prompts/answers into proposition graphs (nodes=props, edges=logic).
    2. Runs ergodic belief propagation to estimate implicit prompt beliefs.
    3. Scores candidates by negative reward (distance to prompt belief).
    4. Adjusts via Theory-of-Mind (mirror belief) for robustness.
    """
    
    # Logical markers
    NEG_MARKERS = ['not', 'no', 'never', 'none']
    IMP_MARKERS = ['if', 'then', 'implies']
    CAU_MARKERS = ['because', 'causes', 'leads to', 'due to']
    ORD_MARKERS = ['before', 'after', 'above', 'below']
    CMP_MARKERS = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller']
    
    def __init__(self):
        pass

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_props(self, text: str) -> List[str]:
        # Simple sentence splitting and cleaning
        sentences = re.split(r'[.\?!]', text)
        props = []
        for s in sentences:
            clean = s.strip()
            if clean:
                props.append(clean)
        return props if props else ["empty"]

    def _build_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]]]:
        """Returns nodes (propositions) and edges (u, v, label)."""
        nodes = self._extract_props(text)
        edges = []
        lower_text = text.lower()
        
        # Detect global relations affecting the whole statement or specific parts
        # Simplified: We treat the whole text as a sequence of propositions p1, p2...
        # and infer relations based on keywords present in the text.
        
        has_neg = any(m in lower_text for m in self.NEG_MARKERS)
        has_imp = any(m in lower_text for m in self.IMP_MARKERS)
        has_cau = any(m in lower_text for m in self.CAU_MARKERS)
        has_ord = any(m in lower_text for m in self.ORD_MARKERS)
        has_cmp = any(m in lower_text for m in self.CMP_MARKERS)

        # Connect nodes sequentially with detected relation types
        for i in range(len(nodes)):
            # Self-loop or connection to next for propagation
            target = (i + 1) % len(nodes) if len(nodes) > 1 else i
            
            if has_imp:
                edges.append((i, target, 'IMP'))
            elif has_cau:
                edges.append((i, target, 'CAU'))
            elif has_ord:
                edges.append((i, target, 'ORD'))
            elif has_cmp:
                edges.append((i, target, 'CMP'))
            else:
                # Default implication
                edges.append((i, target, 'IMP'))
                
            if has_neg:
                # Attach negation to the first node as a special edge or property
                # Here we add a self-loop with NEG if negation is present
                edges.append((i, i, 'NEG'))

        return nodes, edges

    def _compute_belief_vector(self, text: str, T: int = 10) -> np.ndarray:
        """Ergodic belief propagation."""
        nodes, edges = self._build_graph(text)
        n = len(nodes)
        if n == 0: return np.array([0.5])
        
        # Initialize belief: 1.0 if asserted (present), 0.0 otherwise
        # Since we extracted from text, all are asserted initially.
        b = np.ones(n)
        b_avg = np.zeros(n)
        
        # Weights
        W = np.ones(len(edges))
        
        for t in range(T):
            b_new = b.copy()
            for idx, (u, v, lab) in enumerate(edges):
                if u >= n or v >= n: continue
                w = W[idx]
                
                if lab == 'IMP':
                    b_new[v] = max(b_new[v], b[u] * w)
                elif lab == 'NEG':
                    # Negation flips belief
                    b_new[v] = min(b_new[v], 1.0 - (b[u] * w))
                elif lab == 'CAU':
                    b_new[v] = max(b_new[v], b[u] * w * 0.9) # Damped
                elif lab == 'ORD':
                    b_new[v] = max(b_new[v], b[u] * w)
                elif lab == 'CMP':
                    b_new[v] = max(b_new[v], b[u] * w)
            
            b = np.clip(b_new, 0, 1)
            b_avg += b
            
        return b_avg / T

    def _extract_numbers(self, text: str) -> List[float]:
        # Find floats/ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _score_candidate(self, prompt: str, candidate: str, prompt_belief: np.ndarray) -> float:
        """Calculate score based on belief distance and numeric consistency."""
        # 1. Structural Belief Score
        cand_belief = self._compute_belief_vector(candidate, T=10)
        
        # Align dimensions by repeating or truncating (simple broadcasting)
        len_p, len_c = len(prompt_belief), len(cand_belief)
        if len_p == 0 or len_c == 0:
            struct_score = 0.5
        else:
            # Resize to match
            if len_c < len_p:
                c_exp = np.tile(cand_belief, int(np.ceil(len_p/len_c)))[:len_p]
            else:
                c_exp = cand_belief[:len_p]
            
            # Weighted error (higher weight for causal/comparative detected in prompt)
            # Simplified: uniform weight for now, error = L1 distance
            error = np.mean(np.abs(prompt_belief - c_exp))
            struct_score = 1.0 - error # Convert to similarity

        # 2. Numeric Consistency Score
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        num_score = 1.0
        if p_nums and c_nums:
            # Check if relative order is preserved
            # Simple check: do the numbers match or follow the same trend?
            # If prompt has 9.11 and 9.9, and answer implies correct comparison
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_trend = p_nums[0] < p_nums[1]
                c_trend = c_nums[0] < c_nums[1]
                if p_trend != c_trend:
                    num_score = 0.0 # Contradiction
            elif len(p_nums) == len(c_nums):
                # Exact match preference
                if p_nums == c_nums:
                    num_score = 1.0
                else:
                    # Penalty for mismatch
                    num_score = 0.5 
        elif not p_nums and not c_nums:
            num_score = 1.0 # No numbers to contradict
            
        return 0.7 * struct_score + 0.3 * num_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_belief = self._compute_belief_vector(prompt)
        results = []
        
        for cand in candidates:
            # Direct Score
            r_direct = self._score_candidate(prompt, cand, prompt_belief)
            
            # ToM Mirror Score (Simulate false belief / negation flip)
            # Construct a "mirror" candidate by logically flipping key terms
            mirror_cand = cand
            for neg in self.NEG_MARKERS:
                if neg in mirror_cand:
                    mirror_cand = mirror_cand.replace(neg, "")
                else:
                    # Crude mirror: append 'not' to simulate alternative hypothesis
                    mirror_cand = "not " + mirror_cand
                    break
            
            r_mirror = self._score_candidate(prompt, mirror_cand, prompt_belief)
            
            # Final Score: Blend of direct alignment and robustness to misinterpretation
            final_score = 0.5 * r_direct + 0.5 * r_mirror
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural alignment: {r_direct:.2f}, ToM robustness: {r_mirror:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        conf = max(0.0, min(1.0, res[0]['score']))
        return conf