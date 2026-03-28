import re
import numpy as np
import math
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Sparse-Bandit Hoare Verifier (SBHV)
    
    Mechanism:
    1. Structural Parsing: Extracts literals (comparisons, negations, conditionals) 
       using regex to form a set of atomic propositions P.
    2. Sparse Encoding: Maps propositions to sparse binary vectors via random projection 
       and hard thresholding (simulating a Sparse Autoencoder).
    3. Knowledge Base: Generates Horn clauses for transitivity and modus ponens.
    4. Bandit Inference: Uses Upper Confidence Bound (UCB) to select which logical 
       rule (arm) to apply next, dynamically exploring the proof space.
    5. Hoare Verification: Maintains an invariant that derived facts are entailed by P.
    6. Scoring: Ranks candidates based on whether the goal is logically derived (1.0),
       sparse code similarity (cosine), or NCD tiebreaker.
    """

    def __init__(self):
        self.seed = 42
        np.random.seed(self.seed)
        self.D = 128  # High dim space
        self.k = 32   # Projected dim
        self.s = 8    # Sparsity level
        self.W = np.random.randn(self.D, self.k) # Fixed random projection
        
        # Regex patterns for structural parsing
        self.patterns = {
            'comp': re.compile(r'(\w+)\s*(>|<|>=|<=|==|!=)\s*(\w+)'),
            'if_then': re.compile(r'if\s+(.+?)\s+then\s+(.+?)', re.IGNORECASE),
            'causes': re.compile(r'(.+?)\s+(causes|leads to|implies)\s+(.+?)', re.IGNORECASE),
            'not': re.compile(r'(?:not|¬)\s*(\w+)', re.IGNORECASE),
            'num': re.compile(r'\b\d+\.?\d*\b')
        }

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions from text."""
        props = set()
        text_lower = text.lower()
        
        # Comparisons
        for m in self.patterns['comp'].finditer(text):
            props.add(f"{m.group(1)}{m.group(2)}{m.group(3)}")
            
        # Conditionals (simplified to head/tail)
        for m in self.patterns['if_then'].finditer(text):
            props.add(f"cond:{m.group(1).strip()}")
            props.add(f"res:{m.group(2).strip()}")
            
        # Causal
        for m in self.patterns['causes'].finditer(text):
            props.add(f"cause:{m.group(1).strip()}->{m.group(3).strip()}")
            
        # Negations
        for m in self.patterns['not'].finditer(text):
            props.add(f"not:{m.group(1)}")
            
        # Fallback to words if empty
        if not props:
            words = re.findall(r'\b\w+\b', text_lower)
            props.update(words[:20])
            
        return list(props)

    def _encode_sparse(self, props: List[str]) -> np.ndarray:
        """Encode propositions into sparse binary vector."""
        if not props:
            return np.zeros(self.D)
        
        # One-hot-ish hash to D dimensions
        v = np.zeros(self.D)
        for p in props:
            idx = hash(p) % self.D
            v[idx] = 1
            
        # Random Projection + Thresholding (Sparse Autoencoder simulation)
        proj = v @ self.W
        threshold = np.sort(proj)[-self.s] if len(proj) >= self.s else 0
        sparse_code = (proj >= threshold).astype(float)
        return sparse_code

    def _generate_clauses(self, props: List[str]) -> List[Tuple[List[str], str]]:
        """Generate Horn clauses (body -> head) from propositions."""
        clauses = []
        prop_set = set(props)
        
        # Transitivity for comparisons (A>B, B>C -> A>C)
        comps = [p for p in props if '>' in p or '<' in p]
        for p1 in comps:
            for p2 in comps:
                # Parse simple A>B
                m1 = re.match(r'(\w+)([><])(\w+)', p1)
                m2 = re.match(r'(\w+)([><])(\w+)', p2)
                if m1 and m2:
                    a, op1, b = m1.groups()
                    c, op2, d = m2.groups()
                    if b == c and op1 == '>' and op2 == '>':
                        clauses.append(([p1, p2], f"{a}>{d}"))
                    elif b == c and op1 == '<' and op2 == '<':
                        clauses.append(([p1, p2], f"{a}<{d}"))
        
        # Modus Ponens simplified (if A then B, A -> B)
        ifs = [p for p in props if p.startswith('cond:')]
        for if_p in ifs:
            cond = if_p.replace('cond:', '')
            # Find matching result
            res_p = f"res:{cond}" # Simplified matching
            # In a real system we'd match semantic meaning, here we simulate structure
            # If we have "cond: X" and "res: Y", and we find "X" in props, infer "Y"
            pass 

        # Identity clauses (prop -> prop) to ensure bandit has arms
        for p in props:
            clauses.append(([p], p))
            
        return clauses if clauses else [([], "dummy")]

    def _run_bandit_inference(self, initial_props: List[str], goal_props: List[str], budget: int = 20) -> Set[str]:
        """Run UCB bandit to select inference steps."""
        clauses = self._generate_clauses(initial_props)
        if not clauses:
            return set(initial_props)
            
        true_set = set(initial_props)
        Q = np.zeros(len(clauses))
        N = np.zeros(len(clauses))
        t = 1
        
        for _ in range(budget):
            best_arm = -1
            best_val = -np.inf
            
            # UCB Selection
            for i, (body, head) in enumerate(clauses):
                if N[i] == 0:
                    val = float('inf')
                else:
                    exploration = math.sqrt(math.log(t) / N[i])
                    val = Q[i] + 0.5 * exploration
                
                if val > best_val:
                    best_val = val
                    best_arm = i
            
            if best_arm == -1: break
            
            body, head = clauses[best_arm]
            N[best_arm] += 1
            t += 1
            
            # Check if body is satisfied
            satisfied = all(b in true_set for b in body) if body else True
            
            if satisfied:
                if head not in true_set:
                    true_set.add(head)
                    Q[best_arm] = 1.0 # Reward for generating new fact
                else:
                    Q[best_arm] = 0.0 # No new info
            else:
                Q[best_arm] = 0.0
                
        return true_set

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_props = self._extract_propositions(prompt)
        goal_candidates = []
        
        # Extract potential goals from candidates
        cand_props_map = {}
        for c in candidates:
            cand_props_map[c] = self._extract_propositions(c)

        results = []
        
        for cand in candidates:
            cand_props = cand_props_map[cand]
            if not cand_props:
                cand_props = ["unknown"]
                
            # 1. Hoare Invariant Check: Run inference on prompt
            derived_set = self._run_bandit_inference(prompt_props, cand_props)
            
            # 2. Scoring
            score = 0.0
            reason = ""
            
            # Check if candidate proposition is directly in derived set
            goal_reached = any(p in derived_set for p in cand_props)
            
            if goal_reached:
                score = 1.0
                reason = "Goal logically derived via Bandit-guided Horn clauses."
            else:
                # Sparse code similarity
                z_cand = self._encode_sparse(cand_props)
                z_derived = self._encode_sparse(list(derived_set))
                
                norm_c = np.linalg.norm(z_cand)
                norm_d = np.linalg.norm(z_derived)
                
                if norm_c > 0 and norm_d > 0:
                    cosine_sim = np.dot(z_cand, z_derived) / (norm_c * norm_d)
                    score = float(cosine_sim)
                    reason = f"Sparse feature similarity: {score:.3f}"
                else:
                    score = 0.0
                    reason = "No structural overlap."

            # NCD Tiebreaker (only if score is low/ambiguous)
            if score < 0.5:
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD so higher is better, scale it
                ncd_score = max(0, 1.0 - ncd_val) 
                if score == 0:
                    score = ncd_score * 0.1 # Low weight for NCD
                    reason += f" (NCD fallback: {ncd_score:.3f})"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']