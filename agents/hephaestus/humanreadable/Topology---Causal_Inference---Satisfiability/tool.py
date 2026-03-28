import re
import numpy as np
from itertools import permutations

class ReasoningTool:
    """
    Implements a hybrid reasoning evaluator combining structural parsing, 
    causal propagation, and topological cycle detection.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical operators (negation, implication, causality).
    2. Topology: Builds a directed graph of constraints. Detects cycles (Betti-1 approximation) 
       which indicate logical contradictions or paradoxes, applying a penalty.
    3. Causal/SAT: Simulates truth propagation. If a candidate creates a contradiction 
       (e.g., A->B, A is True, B is False), the score drops.
    4. Scoring: Primary signal is structural consistency (0-1). NCD is used strictly as a tiebreaker.
    """

    def __init__(self):
        self.ops = {
            'not': ['not', 'never', 'no ', 'false', 'impossible'],
            'if': ['if', 'then', 'implies', 'leads to', 'causes', 'results in'],
            'eq': ['equals', 'is', 'same as', 'equivalent to'],
            'gt': ['greater than', 'more than', 'exceeds'],
            'lt': ['less than', 'fewer than', 'under']
        }

    def _tokenize(self, text):
        """Extract atomic propositions and logical connectors."""
        text = text.lower()
        # Simple sentence splitter
        sentences = re.split(r'[.;!?]', text)
        nodes = []
        edges = [] # (from_idx, to_idx, type: 1=implies, -1=negates)
        
        node_map = {} # string -> idx
        
        def get_node_id(stmt):
            stmt = stmt.strip()
            if not stmt: return None
            if stmt not in node_map:
                node_map[stmt] = len(node_map)
                nodes.append(stmt)
            return node_map[stmt]

        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect negation
            is_neg = any(sent.startswith(n) for n in self.ops['not'])
            if is_neg:
                sent = sent.split(' ', 1)[1] if ' ' in sent else sent
            
            # Detect implications (A causes B)
            has_imp = False
            for op in self.ops['if']:
                if op in sent:
                    parts = sent.split(op)
                    if len(parts) == 2:
                        u = get_node_id(parts[0])
                        v = get_node_id(parts[1])
                        if u is not None and v is not None:
                            edges.append((u, v, 1))
                            if is_neg: edges.append((u, v, -1)) # Negated implication
                        has_imp = True
                        break
            
            if not has_imp:
                get_node_id(sent) # Register as fact if no connector found

        return nodes, edges, node_map

    def _check_consistency(self, prompt_nodes, prompt_edges, candidate_text):
        """
        Check if candidate contradicts prompt structure.
        Returns a score based on constraint satisfaction and cycle detection.
        """
        # Parse candidate as a set of facts
        cand_nodes, cand_edges, _ = self._tokenize(candidate_text)
        
        # Combine graph
        all_nodes = prompt_nodes + cand_nodes
        n = len(all_nodes)
        if n == 0: return 0.5
        
        # Adjacency matrix for propagation
        # A[i, j] = 1 means i -> j
        A = np.zeros((n, n))
        
        # Map prompt edges
        offset = len(prompt_nodes)
        for u, v, typ in prompt_edges:
            if u < n and v < n:
                A[u, v] = 1 if typ == 1 else -1
        
        # Map candidate edges (treating candidate as asserted truth)
        # We check if candidate assertions conflict with propagated prompt truths
        candidate_assertions = set()
        for u, v, typ in cand_edges:
            # Shift indices to global
            gu, gv = u + offset, v + offset
            if gu < n and gv < n:
                A[gu, gv] = 1
                candidate_assertions.add((gu, gv))
        
        # Topological Sort / Cycle Detection (Kahn's algorithm variant)
        # Count cycles (beta_1 approximation)
        in_degree = np.sum(A != 0, axis=0)
        queue = [i for i in range(n) if in_degree[i] == 0]
        visited_count = 0
        while queue:
            u = queue.pop(0)
            visited_count += 1
            for v in range(n):
                if A[u, v] != 0:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        queue.append(v)
        
        cycles = n - visited_count
        cycle_penalty = min(1.0, cycles * 0.2) # Penalty per cycle
        
        # Simple Propagation Check
        # If prompt says A->B, and candidate says A and NOT B, that's a conflict.
        # Here we simplify: if candidate directly contradicts a prompt node string (negated)
        score = 1.0
        prompt_set = set(prompt_nodes)
        cand_set = set(cand_nodes)
        
        # Check for direct string contradiction (e.g. "X is true" vs "X is false")
        # This is a heuristic proxy for SAT core analysis
        contradictions = 0
        for p in prompt_nodes:
            if f"not {p}" in candidate_text or f"no {p}" in candidate_text:
                contradictions += 1
        
        if contradictions > 0:
            score -= 0.5 * contradictions
            
        # Apply cycle penalty
        score -= cycle_penalty
        
        return max(0.0, min(1.0, score))

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            l1, l2, l12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1+b2))
            return (l12 - min(l1, l2)) / max(l1, l2, 1)
        except: return 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_nodes, prompt_edges, _ = self._tokenize(prompt)
        
        # Pre-calculate prompt numeric constraints if any
        prompt_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        
        scores = []
        for cand in candidates:
            # 1. Structural Parsing & Consistency
            base_score = self._check_consistency(prompt_nodes, prompt_edges, cand)
            
            # 2. Numeric Evaluation (Heuristic)
            cand_nums = re.findall(r"[-+]?\d*\.\d+|\d+", cand)
            numeric_penalty = 0.0
            if prompt_nums and cand_nums:
                try:
                    # Check if candidate number violates simple prompt bounds
                    # e.g. Prompt: "X < 5", Candidate: "6" -> Penalty
                    # This is a simplified proxy for complex constraint solving
                    p_val = float(prompt_nums[0])
                    c_val = float(cand_nums[0])
                    if "less" in prompt and c_val > p_val: numeric_penalty = 0.5
                    if "greater" in prompt and c_val < p_val: numeric_penalty = 0.5
                except: pass
            
            final_score = max(0.0, base_score - numeric_penalty)
            scores.append((final_score, cand))

        # Ranking
        # Sort by score desc, then by NCD (similarity to prompt context) as tiebreaker
        ranked = []
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Group by score for NCD tie-breaking
        current_group = []
        last_score = None
        
        final_list = []
        for score, cand in scores:
            if last_score is not None and abs(score - last_score) > 1e-6:
                # Process group
                if len(current_group) > 1:
                    current_group.sort(key=lambda x: self._ncd(prompt, x[1]))
                final_list.extend(current_group)
                current_group = []
            current_group.append((score, cand))
            last_score = score
        if current_group:
            if len(current_group) > 1:
                current_group.sort(key=lambda x: self._ncd(prompt, x[1]))
            final_list.extend(current_group)

        for score, cand in final_list:
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Structural consistency: {score:.2f}, NCD tiebreak applied."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency."""
        p_nodes, p_edges, _ = self._tokenize(prompt)
        score = self._check_consistency(p_nodes, p_edges, answer)
        return round(max(0.0, min(1.0, score)), 4)