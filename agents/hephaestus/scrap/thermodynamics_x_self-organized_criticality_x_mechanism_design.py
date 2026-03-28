import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Constraint-Energy Avalanche Scorer (CEAS).
    Uses thermodynamic energy assignment on logical constraints and Self-Organized Criticality
    avalanches to dissipate inconsistency. Mechanism design principles score the final stable state.
    Primary signal: Structural parsing of logic/numbers. Tiebreaker: NCD.
    """
    
    def __init__(self):
        self.theta = 1.0  # Critical threshold
        self.c_contr = 2.0 # Penalty for contradiction
        self.c_num = 2.0   # Penalty for numeric violation
        self.lambda_truth = 0.5

    def _extract_literals_and_edges(self, text: str) -> Tuple[List[str], List[Tuple[int, int]], Set[str]]:
        """Parse text into literals, edges, and numeric facts."""
        text_lower = text.lower()
        literals = []
        edges = []
        facts = set()
        lit_map = {} # Map normalized literal to index
        
        def get_lit_idx(lit_str: str) -> int:
            norm = lit_str.strip().lower()
            if not norm: return -1
            if norm not in lit_map:
                lit_map[norm] = len(literals)
                literals.append(norm)
            return lit_map[norm]

        # 1. Numeric Comparisons (e.g., "9.11 < 9.9", "5 > 3")
        num_pattern = re.compile(r'(\d+\.?\d*)\s*(<|>|=|<=|>=|==)\s*(\d+\.?\d*)')
        for m in re.finditer(num_pattern, text):
            v1, op, v2 = m.groups()
            f1, f2 = float(v1), float(v2)
            lit_str = f"{v1} {op} {v2}"
            idx = get_lit_idx(lit_str)
            
            # Evaluate truth
            valid = False
            if op == '<': valid = f1 < f2
            elif op == '>': valid = f1 > f2
            elif op in ('=', '=='): valid = abs(f1 - f2) < 1e-9
            elif op == '<=': valid = f1 <= f2
            elif op == '>=': valid = f1 >= f2
            
            if valid:
                facts.add(lit_str)
            else:
                # If false, it's a contradiction if asserted as true, 
                # but here we treat the statement itself as a node. 
                # If the text asserts "5 > 3", and 5>3 is true, energy low. 
                # If text asserts "3 > 5", energy high.
                # For simplicity in this parser: if the relation holds in reality, 
                # we mark it as a 'fact'. If the candidate contains a relation that is false,
                # it will get high energy later.
                pass 
            # We add an edge representing the claim exists. 
            # To simulate constraint: If "A > B" is present and false, add self-loop penalty later.
            if not valid:
                # Self loop to trigger energy
                edges.append((idx, idx)) 

        # 2. Conditionals and Logic
        # "if X then Y", "X implies Y"
        cond_pattern = re.compile(r'if\s+(.+?)\s+(?:then|implies|leads to|causes)\s+(.+?)(?:\.|,|$)')
        for m in re.finditer(cond_pattern, text_lower):
            pre, post = m.group(1).strip(), m.group(2).strip()
            # Simple literal extraction (first noun phrase approximation)
            u = get_lit_idx(pre)
            v = get_lit_idx(post)
            if u != -1 and v != -1:
                edges.append((u, v))

        # 3. Negations ("not X")
        neg_pattern = re.compile(r'not\s+(\w+)')
        for m in re.finditer(neg_pattern, text_lower):
            target = m.group(1)
            # Check if positive version exists
            pos_idx = get_lit_idx(target)
            neg_lit = f"not_{target}"
            neg_idx = get_lit_idx(neg_lit)
            # Edge from negation to positive implies conflict if both active
            edges.append((neg_idx, pos_idx)) 
            edges.append((pos_idx, neg_idx)) # Bidirectional conflict

        # 4. Biconditionals ("X iff Y")
        bi_pattern = re.compile(r'(.+?)\s+iff\s+(.+?)')
        for m in re.finditer(bi_pattern, text_lower):
            u = get_lit_idx(m.group(1).strip())
            v = get_lit_idx(m.group(2).strip())
            if u != -1 and v != -1:
                edges.append((u, v))
                edges.append((v, u))

        return literals, edges, facts

    def _compute_energy(self, text: str) -> float:
        """Compute final energy after avalanche."""
        lits, edges, true_facts = self._extract_literals_and_edges(text)
        n = len(lits)
        if n == 0:
            return 0.0
            
        # Adjacency
        A = np.zeros((n, n), dtype=np.float64)
        for u, v in edges:
            if 0 <= u < n and 0 <= v < n:
                A[u, v] = 1.0
        
        # Initial Energy
        e = np.zeros(n, dtype=np.float64)
        
        # Check for internal contradictions (e.g. "A and not A" roughly via substring overlap)
        # Or numeric falsehoods detected during parsing (self-loops)
        for i in range(n):
            # Self loop indicates a false numeric claim or direct contradiction
            if A[i, i] > 0:
                e[i] += self.c_num
            # Check for explicit "not" conflicts in the string
            lit_str = lits[i]
            if lit_str.startswith("not_"):
                base = lit_str[4:]
                if base in text.lower():
                    e[i] += self.c_contr # Penalty for asserting both not_X and X contextually
        
        # Avalanche Dynamics
        out_deg = A.sum(axis=1)
        # Avoid division by zero
        out_deg_safe = np.where(out_deg == 0, 1, out_deg)
        
        max_iter = 1000
        for _ in range(max_iter):
            unstable = np.where(e > self.theta)[0]
            if len(unstable) == 0:
                break
            
            for i in unstable:
                delta = e[i] - self.theta
                e[i] = self.theta
                if out_deg[i] > 0:
                    # Distribute excess to neighbors
                    neighbors = A[i, :] > 0
                    if np.any(neighbors):
                        share = delta / np.sum(neighbors)
                        e[neighbors] += share
                    else:
                        # Dissipate if no neighbors
                        pass 
                else:
                    # Dissipate to nowhere (loss)
                    pass
        
        # Mechanism Design Score: Potential = -Energy + Truth Bonus
        # Truth bonus: count how many extracted true facts appear in text
        truth_count = 0
        for f in true_facts:
            if f in text.lower():
                truth_count += 1
                
        potential = -np.sum(e) + (self.lambda_truth * truth_count)
        return potential

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        l1, l2 = len(b1), len(b2)
        if l1 == 0 or l2 == 0: return 1.0
        comp = len(zlib.compress(b1 + b2))
        max_len = max(l1, l2)
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) approx
        # Simplified: (C(xy) - min) / max. 
        # Here we use a variant: lower is better similarity. 
        # We want distance. 
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        numerator = comp - min(c1, c2)
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return max(0.0, numerator / denominator)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_energy = self._compute_energy(prompt) # Baseline complexity
        
        scores = []
        for cand in candidates:
            # Primary Signal: Structural Energy
            cand_energy = self._compute_energy(cand)
            
            # Contextual check: Does candidate reduce energy relative to prompt constraints?
            # We score based on the candidate's own internal consistency (lower energy is better, so higher potential)
            # But we also check consistency with prompt.
            combined_text = f"{prompt} {cand}"
            combined_energy = self._compute_energy(combined_text)
            
            # Score = Potential (negative energy) + Consistency bonus
            # If adding the candidate makes the system explode (high energy), it's bad.
            # We want the state with the lowest final energy (highest potential).
            score = -combined_energy 
            
            scores.append((cand, score))
        
        # Normalize scores to roughly 0-1 range for readability, though ranking is key
        if scores:
            min_s = min(s[1] for s in scores)
            max_s = max(s[1] for s in scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            normalized_scores = [(c, (s - min_s) / range_s) for c, s in scores]
        else:
            normalized_scores = []

        # Sort descending by score
        normalized_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        final_results = []
        for i, (cand, score) in enumerate(normalized_scores):
            reasoning = f"Energy Score: {score:.4f}. "
            # If top two are close, use NCD to prompt as tiebreaker
            if i > 0 and abs(score - normalized_scores[i-1][1]) < 0.01:
                ncd_val = self._ncd(prompt, cand)
                reasoning += f"Tiebreak NCD: {ncd_val:.4f} "
            
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Map score to 0-1. Assuming score can be negative, use sigmoid-like mapping or min-max
        # Heuristic: If score > 0, high confidence. 
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))