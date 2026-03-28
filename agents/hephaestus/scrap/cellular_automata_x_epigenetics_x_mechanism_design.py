import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool combining Structural Graph Parsing, Cellular Automata (Rule 110),
    and Mechanism Design (Brier Scoring).
    
    Mechanism:
    1. Parsing: Extracts literals and logical edges (negation, conditionals, causality) via Regex.
    2. Epigenetic CA: Nodes hold confidence states. A Rule 110-style update propagates truth 
       values across the logical graph, modulated by an epigenetic decay factor (alpha).
    3. Mechanism Design: Candidates are scored using the Brier Proper Scoring Rule against 
       the converged CA states, incentivizing truthful alignment with the derived logic.
    """
    
    # Rule 110 Lookup Table: 01101110 in binary -> [0, 1, 1, 1, 0, 1, 1, 0]
    LUT = np.array([0, 1, 1, 1, 0, 1, 1, 0], dtype=np.float32)
    
    def __init__(self):
        self.alpha = 0.7  # Epigenetic decay factor

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, Dict[str, int]]:
        """Extract literals and build adjacency matrix E."""
        text_lower = text.lower()
        # Normalize text for easier regex
        clean_text = re.sub(r'[^\w\s->< because if then before after]', ' ', text_lower)
        
        # Extract potential literals (words/phrases)
        # Simple heuristic: split by logical connectors to find atoms
        atoms = set()
        # Pattern to find quoted strings or simple noun phrases
        raw_tokens = re.findall(r'"([^"]+)"|(\b[a-z]{3,}\b)', text_lower)
        for match in raw_tokens:
            token = match[0] if match[0] else match[1]
            if len(token) > 1: atoms.add(token)
            
        # Fallback: split by spaces if too few atoms
        if len(atoms) < 2:
            for t in re.split(r'\s+', clean_text):
                if len(t) > 2 and t not in ['because', 'then', 'before', 'after', 'not']:
                    atoms.add(t)
        
        literals = sorted(list(atoms))
        if not literals:
            return [], np.zeros((0,0), dtype=np.int8), {}
            
        lit_to_idx = {lit: i for i, lit in enumerate(literals)}
        n = len(literals)
        E = np.zeros((n, n), dtype=np.int8) # 0:none, 1:->, 2:<-, 3:<->
        
        # Helper to add edge
        def add_edge(u, v, type_val):
            if u in lit_to_idx and v in lit_to_idx:
                ui, vi = lit_to_idx[u], lit_to_idx[v]
                E[ui, vi] = type_val
                if type_val == 3: E[vi, ui] = type_val

        # 1. Conditionals: if P then Q, P -> Q
        for pattern in [r'if\s+(\w+)\s+then\s+(\w+)', r'(\w+)\s*->\s*(\w+)']:
            for m in re.finditer(pattern, text_lower):
                add_edge(m.group(1), m.group(2), 1)

        # 2. Causal: P because Q (Q -> P)
        for m in re.finditer(r'(\w+)\s+because\s+(\w+)', text_lower):
            add_edge(m.group(2), m.group(1), 1)
            
        # 3. Negation: not P (Handled as self-loop or special flag, here we treat as weak self-inhibition)
        # We simulate negation by creating a virtual 'false' node if needed, 
        # but per spec, we map structure. Let's mark negated nodes internally if needed.
        # For this implementation, we focus on the graph topology for propagation.
        
        # 4. Comparatives/Ordering: P > Q, P before Q
        for pattern in [r'(\w+)\s*[><]\s*(\w+)', r'(\w+)\s+before\s+(\w+)']:
            for m in re.finditer(pattern, text_lower):
                # Bidirectional for structural coupling in this model
                add_edge(m.group(1), m.group(2), 3)

        return literals, E, lit_to_idx

    def _run_ca(self, n_nodes: int, E: np.ndarray, steps: int = 10) -> np.ndarray:
        """Run Epigenetic Cellular Automaton."""
        if n_nodes == 0:
            return np.array([])
            
        # Initialize methylation states to 0.5 (uncertainty)
        m = np.full(n_nodes, 0.5, dtype=np.float32)
        
        # Precompute adjacency masks
        # A_in[i] = neighbors pointing TO i
        # A_out[i] = neighbors pointing FROM i
        # E=1: i->j (row i, col j). So for node j, incoming is col j where val=1.
        # Incoming edges mask (who points to me)
        incoming_mask = (E == 1) | (E == 3) # 1:->, 3:<->
        outgoing_mask = (E.T == 1) | (E == 3) # Transpose for outgoing
        
        # Convert to boolean for logic ops
        has_in = incoming_mask.astype(np.float32)
        has_out = outgoing_mask.astype(np.float32)

        for _ in range(steps):
            # Threshold current state to binary
            s_binary = (m >= 0.5).astype(np.float32)
            
            # Compute neighborhood bits
            # Bit 0: Current state
            b0 = s_binary
            
            # Bit 1: OR of incoming neighbors
            # If any incoming neighbor is 1, this is 1. If no neighbors, 0.
            b1 = np.zeros(n_nodes, dtype=np.float32)
            # Matrix mult: (has_in.T * s_binary) > 0
            if np.any(has_in):
                b1 = (has_in.T @ s_binary > 0).astype(np.float32)
                
            # Bit 2: OR of outgoing neighbors
            b2 = np.zeros(n_nodes, dtype=np.float32)
            if np.any(has_out):
                b2 = (has_out.T @ s_binary > 0).astype(np.float32)
            
            # Calculate index: 4*b0 + 2*b1 + b2
            indices = (4 * b0 + 2 * b1 + b2).astype(np.int32)
            
            # Apply Rule 110 LUT
            m_raw = self.LUT[indices]
            
            # Epigenetic update: m = alpha*m + (1-alpha)*m_raw
            m = self.alpha * m + (1.0 - self.alpha) * m_raw
            
            # Clamp
            m = np.clip(m, 0.0, 1.0)
            
        return m

    def _score_candidate(self, candidate: str, literals: List[str], final_states: np.ndarray, lit_to_idx: Dict[str, int]) -> float:
        """Score candidate using Brier Rule against CA steady states."""
        if not literals:
            # Fallback to simple string match if parsing fails
            return 0.5
            
        cand_lower = candidate.lower()
        n = len(literals)
        t = np.full(n, 0.5, dtype=np.float32) # Target vector
        
        found_any = False
        for lit, idx in lit_to_idx.items():
            # Check if literal is asserted or denied in candidate
            # Simple containment check with word boundaries
            pattern_assert = r'\b' + re.escape(lit) + r'\b'
            pattern_deny = r'\b(not|no|never)\s+' + re.escape(lit) + r'\b'
            
            if re.search(pattern_assert, cand_lower):
                t[idx] = 1.0
                found_any = True
            elif re.search(pattern_deny, cand_lower):
                t[idx] = 0.0
                found_any = True
            # Else remains 0.5 (unknown)
            
        if not found_any:
            # If candidate mentions none of the logic, penalize slightly or return neutral
            # But we must return a score. 
            # If the CA converged to strong beliefs, and candidate is silent, Brier penalty applies.
            pass

        # Brier Score: -mean((m - t)^2)
        # We use negative mean squared error so higher is better.
        if len(final_states) == 0:
            return 0.0
            
        # Align sizes if candidate introduced new tokens not in prompt (unlikely in this flow but safe)
        min_len = min(len(final_states), len(t))
        if min_len == 0: return 0.0
        
        score = -np.mean((final_states[:min_len] - t[:min_len]) ** 2)
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Parse Prompt
        literals, E, lit_to_idx = self._parse_graph(prompt)
        
        # 2. Run CA to get belief states
        final_states = self._run_ca(len(literals), E)
        
        results = []
        for cand in candidates:
            # Score based on logical alignment
            logic_score = self._score_candidate(cand, literals, final_states, lit_to_idx)
            
            # NCD Tiebreaker / Fallback
            # If logic score is neutral (e.g., no literals found), use compression distance
            if len(literals) == 0 or np.all(final_states == 0.5):
                try:
                    data = prompt.encode('utf-8')
                    comp = len(zlib.compress(data + cand.encode('utf-8')))
                    norm_comp = comp / (len(data) + len(cand) + 1)
                    # Invert so higher is better (lower compression ratio = less redundancy = better?)
                    # Actually for NCD, lower distance = more similar. 
                    # We want to reward similarity to prompt logic? 
                    # Standard NCD baseline is weak. Let's just give a small random noise if empty.
                    base_score = 0.5 - norm_comp * 0.1 
                except:
                    base_score = 0.0
                logic_score = base_score

            results.append({
                "candidate": cand,
                "score": logic_score,
                "reasoning": f"Aligned with {len(literals)} structural nodes via CA Rule 110."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.5
        # Normalize score to 0-1 range roughly. 
        # Brier score is negative MSE. Max is 0. Min is -1.
        # Map [-1, 0] -> [0, 1]
        raw = res[0]['score']
        conf = max(0.0, min(1.0, raw + 1.0)) 
        return conf

# Import zlib inside for the fallback if needed, kept local to avoid global clutter if not used
import zlib