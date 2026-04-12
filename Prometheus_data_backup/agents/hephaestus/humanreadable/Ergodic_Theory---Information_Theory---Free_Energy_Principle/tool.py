import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning evaluator combining Ergodic Theory, Information Theory, 
    and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, 
       causals, ordering) using regex, mapping them to unique IDs.
    2. Graph Construction: Builds an adjacency matrix representing logical constraints 
       (antecedent->consequent, comparative links).
    3. Ergodic Propagation: Iteratively updates probability distributions over propositions 
       assuming independence, simulating a Markov process converging to a stationary distribution.
    4. Free Energy Scoring: Computes Variational Free Energy (F = KL - H) between the 
       candidate's posterior and a reference state. Lower F implies better alignment 
       with logical constraints and lower surprise.
    """
    
    # Regex patterns for atomic proposition extraction
    PATTERNS = [
        ('neg', re.compile(r'not\s+(\w+)', re.IGNORECASE)),
        ('comp', re.compile(r'(\w+)\s*(>|<|>=|<=)\s*(\w+)', re.IGNORECASE)),
        ('cond', re.compile(r'if\s+(.+?)\s+then\s+(.+)', re.IGNORECASE)),
        ('cause', re.compile(r'(.+?)\s+because\s+(.+)', re.IGNORECASE)),
        ('order', re.compile(r'(\w+)\s+before\s+(\w+)', re.IGNORECASE)),
        ('order_aft', re.compile(r'(\w+)\s+after\s+(\w+)', re.IGNORECASE))
    ]

    def __init__(self):
        self.eps = 1e-12

    def _extract_props(self, text: str) -> Tuple[List[str], List[Tuple[str, Any]]]:
        """Extract atomic propositions and label them."""
        props = []
        labeled = []
        text_lower = text.lower()
        
        # Helper to add prop
        def add_prop(label, match_obj, full_match):
            key = f"{label}:{full_match.strip()}"
            if key not in props:
                props.append(key)
            labeled.append((label, full_match.strip()))
            return len(props) - 1

        for label, pattern in self.PATTERNS:
            for match in pattern.finditer(text_lower):
                full = match.group(0)
                add_prop(label, match, full)
                
        # Fallback: if no structured props, treat whole text as one block to ensure scoring works
        if not props:
            props = [text_lower]
            labeled = [('raw', text_lower)]
            
        return props, labeled

    def _build_graph(self, props: List[str], labeled: List[Tuple[str, Any]]) -> np.ndarray:
        """Build binary adjacency matrix A where A[i,j]=1 if i influences j."""
        n = len(props)
        if n == 0:
            return np.zeros((0,0), dtype=np.int8)
            
        A = np.zeros((n, n), dtype=np.int8)
        
        # Map text to index for quick lookup
        text_to_idx = {p: i for i, p in enumerate(props)}
        
        for label, content in labeled:
            # Re-run specific regex to get groups
            if label == 'cond':
                m = re.search(r'if\s+(.+?)\s+then\s+(.+)', content, re.IGNORECASE)
                if m:
                    ant, cons = m.group(1).strip(), m.group(2).strip()
                    # Simple substring match for antecedent/consequent in prop list
                    # In a real system, this would be more robust, but we match keys
                    for k, idx in text_to_idx.items():
                        if ant in k:
                            # If prop k is in antecedent, it influences props in consequent
                            # We approximate by linking to any prop containing the consequent string
                            found_cons = False
                            for k2, idx2 in text_to_idx.items():
                                if cons in k2:
                                    A[idx, idx2] = 1
                                    found_cons = True
            elif label == 'comp':
                m = re.search(r'(\w+)\s*(>|<|>=|<=)\s*(\w+)', content)
                if m:
                    # Link left and right tokens if they exist as substrings in props
                    left, right = m.group(1), m.group(2)
                    idx_l, idx_r = -1, -1
                    for k, idx in text_to_idx.items():
                        if left in k: idx_l = idx
                        if right in k: idx_r = idx
                    if idx_l != -1 and idx_r != -1:
                        A[idx_l, idx_r] = 1
                        A[idx_r, idx_l] = 1 # Bidirectional constraint for comparison
            elif label == 'order':
                m = re.search(r'(\w+)\s+before\s+(\w+)', content)
                if m:
                    first, second = m.group(1), m.group(2)
                    idx_f, idx_s = -1, -1
                    for k, idx in text_to_idx.items():
                        if first in k: idx_f = idx
                        if second in k: idx_s = idx
                    if idx_f != -1 and idx_s != -1:
                        A[idx_f, idx_s] = 1

        return A

    def _propagate(self, A: np.ndarray, steps: int = 5) -> np.ndarray:
        """Ergodic constraint propagation."""
        n = A.shape[0]
        if n == 0:
            return np.array([])
            
        # Initialize uniform prior
        p = np.ones(n, dtype=np.float64) * 0.5
        
        for _ in range(steps):
            # Update based on adjacency (simplified independence assumption)
            # p_j = p_j * p_i for incoming edges
            new_p = p.copy()
            for j in range(n):
                incoming = np.where(A[:, j] == 1)[0]
                if len(incoming) > 0:
                    product = np.prod(p[incoming])
                    new_p[j] = p[j] * product
            
            # Normalize to sum to 1 (Probability distribution)
            total = np.sum(new_p) + self.eps
            p = new_p / total
            
            # Handle negations implicitly by symmetry in a full system, 
            # here we rely on the structure of the graph and initial extraction.
            # For simple regex extraction, we assume the graph captures the dependency.
            
        return p

    def _compute_free_energy(self, q_ref: np.ndarray, q_cand: np.ndarray) -> float:
        """Compute F = KL(q_ref || q_cand) - H(q_ref). Score = -F."""
        if len(q_ref) == 0 or len(q_cand) == 0:
            return 0.0
            
        # Ensure same length by padding with eps if necessary (structural mismatch)
        n = max(len(q_ref), len(q_cand))
        p_ref = np.ones(n, dtype=np.float64) * self.eps
        p_cand = np.ones(n, dtype=np.float64) * self.eps
        
        l_ref, l_cand = len(q_ref), len(q_cand)
        p_ref[:l_ref] = q_ref
        p_cand[:l_cand] = q_cand
        
        # Renormalize slices used
        p_ref = p_ref / (np.sum(p_ref) + self.eps)
        p_cand = p_cand / (np.sum(p_cand) + self.eps)
        
        # KL Divergence
        kl = np.sum(p_ref * np.log((p_ref + self.eps) / (p_cand + self.eps)))
        
        # Entropy of reference
        h_ref = -np.sum(p_ref * np.log(p_ref + self.eps))
        
        F = kl - h_ref
        return -F # Higher score is better

    def _get_ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Parse prompt to get reference structure
        ref_props, ref_labeled = self._extract_props(prompt)
        A_ref = self._build_graph(ref_props, ref_labeled)
        q_ref = self._propagate(A_ref)
        
        scored_candidates = []
        
        for cand in candidates:
            # Parse candidate
            cand_props, cand_labeled = self._extract_props(cand)
            A_cand = self._build_graph(cand_props, cand_labeled)
            q_cand = self._propagate(A_cand)
            
            # Primary Score: Free Energy
            score = self._compute_free_energy(q_ref, q_cand)
            
            # Secondary Signal: Numeric consistency check (heuristic)
            # If prompt has numbers and candidate has numbers, check consistency
            # (Simplified for brevity: relying on structural overlap via FEP)
            
            # Tiebreaker: NCD if structural signal is weak or identical
            if score == 0.0 or (len(ref_props) == 1 and len(cand_props) == 1):
                ncd_sim = self._get_ncd_score(prompt, cand)
                score += (ncd_sim * 0.01) # Small boost for lexical similarity if structure fails
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"FEP Score: {score:.4f}, Props: {len(cand_props)}, Edges: {np.sum(A_cand)}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Free energy can be negative large, so we use a sigmoid-like mapping
        score = res[0]['score']
        
        # Heuristic mapping: 
        # If structural match is high, score > 0. 
        # If mismatch, score < 0.
        # Map to 0-1
        conf = 1.0 / (1.0 + np.exp(-score)) 
        return float(np.clip(conf, 0.0, 1.0))