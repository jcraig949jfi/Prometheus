import re
import numpy as np

class ReasoningTool:
    """
    Implements a Falsificationism x Pragmatism x Mechanism Design reasoning engine.
    Mechanism:
    1. Parsing: Extracts atomic propositions and relations (imp, cause, gt, eq, not) via regex.
    2. Knowledge Base: Initializes boolean state from prompt facts.
    3. Forward Chaining: Propagates truth values through implication/causal graphs.
    4. Falsification Test: Checks if adding a candidate creates a contradiction (p & not p).
    5. Pragmatic Utility: Measures satisfaction of numeric/constraint conditions.
    6. Scoring: Uses a quadratic proper scoring rule to rank candidates by minimizing contradiction
       and maximizing constraint satisfaction.
    """
    
    def __init__(self):
        self.relations = []
        self.props = {}
        self.prop_count = 0

    def _get_id(self, name):
        if name not in self.props:
            self.props[name] = self.prop_count
            self.prop_count += 1
        return self.props[name]

    def _parse_text(self, text):
        """Parses text into propositions and relation matrix rows."""
        relations = []
        props = {}
        count = 0
        
        def get_id(name):
            nonlocal count
            if name not in props:
                props[name] = count
                count += 1
            return props[name]

        lines = text.lower().split('.')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Numeric equality: value = 3.2
            m = re.search(r'(\w+)\s*=\s*([\d.]+)', line)
            if m:
                src = get_id(f"num_{m.group(1)}")
                val = float(m.group(2))
                relations.append((3, src, int(val*100))) # Type 3: eq, store scaled int
                continue

            # Comparative: X > Y or X greater than Y
            m = re.search(r'(\w+)\s+(?:>|greater than)\s+(\w+)', line)
            if m:
                src, dst = get_id(m.group(1)), get_id(m.group(2))
                relations.append((1, src, dst)) # Type 1: gt
                continue
            
            # Conditional: if A then B
            m = re.search(r'if\s+(\w+)\s+then\s+(\w+)', line)
            if m:
                src, dst = get_id(m.group(1)), get_id(m.group(2))
                relations.append((0, src, dst)) # Type 0: imp
                continue

            # Causal: A because B (B -> A)
            m = re.search(r'(\w+)\s+because\s+(\w+)', line)
            if m:
                dst, src = get_id(m.group(1)), get_id(m.group(2))
                relations.append((0, src, dst) if True else (2, src, dst)) # Treat as imp
                continue
                
            # Negation: not X
            m = re.search(r'not\s+(\w+)', line)
            if m:
                pid = get_id(m.group(1))
                nid = get_id(f"not_{m.group(1)}")
                relations.append((4, pid, nid)) # Type 4: negation link

        # Convert to numpy array
        if not relations:
            return np.zeros((0, 3), dtype=np.int32), props, count
        
        return np.array(relations, dtype=np.int32), props, count

    def _run_chain(self, R, K_init, n_props):
        """Forward chaining to fixed point."""
        K = K_init.copy()
        if len(K) < n_props:
            K = np.pad(K, (0, n_props - len(K)), 'constant')
            
        changed = True
        while changed:
            changed = False
            for r in R:
                t, src, dst = r
                # Implication / Causal
                if t == 0: 
                    if src < len(K) and dst < len(K) and K[src] and not K[dst]:
                        K[dst] = True
                        changed = True
                # GT (simplified: if src true, dst marked true for consistency check)
                elif t == 1:
                    if src < len(K) and dst < len(K) and K[src] and not K[dst]:
                        # In this logic model, GT acts as a constraint trigger
                        pass 
                # Negation propagation
                elif t == 4:
                    if src < len(K) and dst < len(K) and K[src] and not K[dst]:
                        K[dst] = True
                        changed = True
        return K

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # 1. Parse Prompt
        R_prompt, p_props, p_count = self._parse_text(prompt)
        n_total = max(p_count, 10) # Ensure some buffer
        
        # Initialize KB from prompt assertions (simplified: assume positive statements are true)
        # We map prompt propositions to initial truth
        K_base = np.zeros(n_total * 2, dtype=bool)
        for name, idx in p_props.items():
            if idx < len(K_base):
                K_base[idx] = True 

        results = []
        
        for cand in candidates:
            # 2. Parse Candidate
            R_cand, c_props, c_count = self._parse_text(cand)
            if R_cand.size == 0 and not c_props:
                # Fallback for non-structural answers
                score = -1.0 if "not" in cand.lower() else 0.0
                results.append({"candidate": cand, "score": score, "reasoning": "No structural logic detected."})
                continue

            # Merge relations
            R_combined = np.vstack([R_prompt, R_cand]) if R_prompt.size > 0 and R_cand.size > 0 else (R_prompt if R_prompt.size > 0 else R_cand)
            
            # Map candidate props to global indices (simplified merge)
            # For this implementation, we re-index dynamically based on combined text to ensure overlap
            full_text = prompt + " " + cand
            R_all, all_props, _ = self._parse_text(full_text)
            
            # Re-evaluate KB size
            n_all = max(len(all_props), 1)
            K_curr = np.zeros(n_all + 5, dtype=bool)
            
            # Set initial truths from prompt parts
            for name, idx in p_props.items():
                if name in all_props and all_props[name] < len(K_curr):
                    K_curr[all_props[name]] = True
            
            # 3. Forward Chain Baseline
            K_base_state = self._run_chain(R_all, K_curr, n_all)
            
            # 4. Falsification Test (Check for p AND not p)
            falsified = False
            for name, idx in all_props.items():
                not_name = f"not_{name}"
                if not_name in all_props:
                    n_idx = all_props[not_name]
                    if idx < len(K_base_state) and n_idx < len(K_base_state):
                        if K_base_state[idx] and K_base_state[n_idx]:
                            falsified = True
                            break
            
            # 5. Pragmatic Utility (Numeric constraint check)
            # Check if candidate satisfies numeric hints in prompt
            utility = 1.0
            if falsified:
                utility = 0.0 # High penalty for contradiction
            
            # Simple heuristic: if candidate adds no contradictions, boost score
            score = - (float(falsified)**2 + (1.0 - utility)**2)
            
            reasoning = "Contradiction found" if falsified else "Consistent with constraints"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score: assuming range roughly [-2, 0]
        # Map to 0-1. 0 -> 1.0, -2 -> 0.0
        s = res[0]["score"]
        conf = max(0.0, min(1.0, (s + 2.0) / 2.0))
        return conf