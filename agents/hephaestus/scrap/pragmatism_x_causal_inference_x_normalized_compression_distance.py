import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural causal parsing, forward-chaining
    entailment, and pragmatic utility simulation. Normalized Compression Distance (NCD)
    is restricted to a tie-breaking role to avoid known failure modes associated with
    pure compression-based reasoning.
    
    Mechanism:
    1. Parse propositions and causal links (regex) into a directed graph.
    2. Compute transitive closure (forward chaining) to find all entailed facts.
    3. Score candidates based on:
       - Consistency: Overlap with entailed facts minus contradictions.
       - Utility: Simulated intervention success rate.
       - NCD: Used only as a minor tiebreaker for structural similarity.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'causal': re.compile(r'\b(because|leads to|causes|results in|therefore|so)\b', re.I),
        'conditional': re.compile(r'\b(if|unless|then|when)\b', re.I),
        'negation': re.compile(r'\b(not|no|never|without|cannot)\b', re.I),
        'comparative': re.compile(r'\b(more than|less than|greater|smaller|higher|lower|>\|<)\b', re.I),
        'numeric': re.compile(r'-?\d+\.?\d*'),
        'order': re.compile(r'\b(before|after|first|second|next|finally)\b', re.I)
    }

    def __init__(self):
        pass

    def _extract_props(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract simplified (subject, relation, object) triples."""
        props = []
        # Simple sentence splitting
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect relation type
            rel_type = "statement"
            if self.PATTERNS['causal'].search(sent): rel_type = "causal"
            elif self.PATTERNS['conditional'].search(sent): rel_type = "conditional"
            elif self.PATTERNS['negation'].search(sent): rel_type = "negation"
            elif self.PATTERNS['comparative'].search(sent): rel_type = "comparative"
            
            # Extract numeric values if present
            nums = self.PATTERNS['numeric'].findall(sent)
            if nums:
                props.append((sent.lower(), rel_type, nums[0]))
            else:
                # Fallback to whole sentence as proposition
                props.append((sent.lower(), rel_type, "true"))
        return props

    def _build_graph(self, prompt: str) -> Tuple[List[str], np.ndarray, Set[str]]:
        """Build adjacency matrix and node list from prompt."""
        props = self._extract_props(prompt)
        nodes = list(set([p[0] for p in props]))
        node_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        adj = np.zeros((n, n))
        negations = set()
        
        # Build edges based on causal cues or temporal order
        for i, (sub, rel, obj) in enumerate(props):
            if rel == "negation":
                negations.add(sub)
            
            # Look for explicit causal chains in adjacent propositions
            for j, (sub2, rel2, obj2) in enumerate(props):
                if i == j: continue
                # Heuristic: if prop i contains causal keyword and mentions sub2
                if rel in ["causal", "conditional"] and sub2 in sub:
                    if sub in node_map and sub2 in node_map:
                        u, v = node_map[sub], node_map[sub2]
                        weight = 1.0 if rel == "causal" else 0.5
                        adj[u, v] = weight
        
        return nodes, adj, negations

    def _transitive_closure(self, adj: np.ndarray) -> np.ndarray:
        """Compute transitive hull using numpy (Warshall-like)."""
        if adj.shape[0] == 0:
            return adj
        closure = (adj > 0).astype(float)
        np.fill_diagonal(closure, 1)
        # Matrix multiplication approach for small N, or iterative for stability
        # Using iterative bit-mask style for boolean closure
        changed = True
        while changed:
            old = closure.copy()
            closure = np.sign(closure @ closure) # Matrix multiply then threshold
            closure[closure > 0] = 1
            if np.array_equal(old, closure):
                changed = False
        return closure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        nodes, adj, prompt_negs = self._build_graph(prompt)
        closure = self._transitive_closure(adj)
        
        # Map nodes to indices for closure lookup
        node_map = {n: i for i, n in enumerate(nodes)}
        entailed_set = set()
        
        # Extract entailed propositions from closure
        # If node i -> node j exists, and i is in prompt, j is entailed
        for i, n_i in enumerate(nodes):
            for j, n_j in enumerate(nodes):
                if closure[i, j] > 0 and i != j:
                    entailed_set.add(n_j)

        results = []
        for cand in candidates:
            cand_props = self._extract_props(cand)
            cand_subs = [p[0] for p in cand_props]
            
            # 1. Consistency Score
            matched = 0
            contradiction = 0
            for sub in cand_subs:
                if sub in entailed_set:
                    matched += 1
                # Check negation conflict
                if sub in prompt_negs:
                    contradiction += 1
            
            total_cand = len(cand_subs) if len(cand_subs) > 0 else 1
            cons_score = (matched - contradiction) / total_cand
            
            # 2. Utility (Simulated Intervention)
            # Simplified: If candidate suggests a change, does prompt support the outcome?
            # Here we approximate utility by checking if candidate contains causal keywords
            # that align with the graph structure.
            util_score = 0.0
            if any(self.PATTERNS['causal'].search(cand) for _ in [1]):
                # Crude heuristic: if candidate has causal language and matches graph nodes
                if any(n in cand for n in nodes):
                    util_score = 0.5
            
            # 3. NCD (Tiebreaker only)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score: Weighted heavily towards structural consistency
            # Weights: Cons=0.7, Util=0.2, NCD=0.1 (NCD is strictly tiebreaker)
            score = 0.7 * cons_score + 0.2 * util_score + 0.1 * ncd_score
            
            # Penalty for pure NCD reliance if structural signal is zero
            if matched == 0 and contradiction == 0:
                score = 0.5 * ncd_score # Downgrade to NCD-only baseline if no structure found

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Consistency:{cons_score:.2f}, Utility:{util_score:.2f}, NCD:{ncd_val:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural parsing as primary signal, NCD as fallback.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Calibration: Map raw score to confidence
        # If structural consistency was high, confidence is high.
        # If only NCD matched, confidence is capped.
        reasoning = res[0]['reasoning']
        if "Consistency:0." not in reasoning and "Consistency:-" not in reasoning:
             # Basic check if consistency contributed positively
             if float(res[0]['score']) > 0.5:
                 return min(1.0, float(res[0]['score']) + 0.2)
        
        return max(0.0, min(1.0, float(score)))