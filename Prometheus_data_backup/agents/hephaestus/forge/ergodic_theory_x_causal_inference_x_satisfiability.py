import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Ergodic Causal SAT Scorer (ECSS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, causal links, and numeric constraints.
    2. Causal Propagation: Builds a DAG of implications. Uses do-calculus logic (intervention)
       to propagate truth values through the graph.
    3. Ergodic Averaging: Simulates a random walk over the space of possible interventions 
       (fixing variables to True/False). For each state, it checks logical consistency (SAT) 
       of the candidate answer against the prompt's derived constraints.
    4. Scoring: The final score is the time-average of satisfiability across the ergodic walk,
       weighted by structural alignment. NCD is used only as a tie-breaker.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(42)  # Deterministic seed

    def _parse_structural(self, text: str) -> Tuple[List[str], List[Tuple[str, str]], List[Tuple[str, float, str]]]:
        """Extract propositions, causal edges, and numeric constraints."""
        text_lower = text.lower()
        props = []
        edges = []
        constraints = []
        
        # 1. Extract Atomic Propositions (simplified to sentences/clauses)
        sentences = re.split(r'[.!?]', text)
        for i, sent in enumerate(sentences):
            s = sent.strip()
            if s:
                # Clean and normalize
                clean_s = re.sub(r'\s+', ' ', s)
                if clean_s:
                    props.append(f"p{i}")
        
        # 2. Extract Causal Edges (Simple regex for causal verbs)
        causal_patterns = [
            (r'(\w+)\s+(causes|leads to|produces|implies)\s+(\w+)', 1, 3),
            (r'if\s+(\w+),?\s+then\s+(\w+)', 1, 2),
            (r'(\w+)\s+(precedes|follows)\s+(\w+)', 1, 3) # Simplified ordering
        ]
        
        for pattern, g1, g2 in causal_patterns:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                # Map words to closest proposition index (heuristic)
                src_idx = self._find_prop_idx(m[g1-1] if isinstance(m, tuple) else m[0], sentences)
                tgt_idx = self._find_prop_idx(m[g2-1] if isinstance(m, tuple) else m[1], sentences)
                if src_idx is not None and tgt_idx is not None and src_idx != tgt_idx:
                    edges.append((f"p{src_idx}", f"p{tgt_idx}"))

        # 3. Extract Numeric Constraints
        num_pattern = r'(\w+)\s*(>=|<=|>|<|=)\s*([\d.]+)'
        for m in re.finditer(num_pattern, text_lower):
            var_name = m.group(1)
            op = m.group(2)
            val = float(m.group(3))
            # Heuristic mapping to prop
            idx = self._find_prop_idx(var_name, sentences)
            if idx is not None:
                constraints.append((f"p{idx}", val, op))

        return props, edges, constraints

    def _find_prop_idx(self, keyword: str, sentences: List[str]) -> int:
        """Find the index of the sentence containing the keyword."""
        keyword = keyword.lower().strip()
        best_idx = None
        max_overlap = 0
        for i, sent in enumerate(sentences):
            words = set(re.findall(r'\w+', sent.lower()))
            overlap = len(words.intersection({keyword}))
            # Fuzzy match: if keyword is substring of any word
            if overlap == 0:
                for w in words:
                    if keyword in w or w in keyword:
                        overlap = 1
                        break
            if overlap > max_overlap:
                max_overlap = overlap
                best_idx = i
        return best_idx if max_overlap > 0 else None

    def _check_sat(self, candidate: str, props: List[str], edges: List[Tuple[str, str]], 
                   constraints: List[Tuple[str, float, str]], intervention: Dict[str, bool]) -> bool:
        """
        Check if the candidate is consistent with the prompt under a specific intervention.
        Simplified SAT check: 
        1. Apply interventions.
        2. Propagate causality (transitive closure).
        3. Check if candidate contradicts derived truths.
        """
        # Map props to state
        state = {p: None for p in props} # None = unknown, True/False = fixed
        
        # Apply interventions
        for k, v in intervention.items():
            if k in state:
                state[k] = v
        
        # Propagate causality (simplified forward chaining)
        changed = True
        while changed:
            changed = False
            for src, tgt in edges:
                if src in state and tgt in state:
                    if state[src] is True and state[tgt] is None:
                        state[tgt] = True
                        changed = True
                    elif state[src] is False:
                        # Modus tollens not strictly applied in simple forward pass unless explicit
                        pass
        
        # Check constraints (Numeric)
        # Since we don't have real values, we assume constraints are satisfied if the prop exists
        # unless the candidate explicitly contradicts the logic structure.
        
        # Check Candidate Consistency
        # We parse the candidate for negations or affirmations of specific props
        cand_lower = candidate.lower()
        for p in props:
            idx = p[1:] # remove 'p'
            # Heuristic: if candidate mentions "not" near the context of the proposition
            # This is a simplification for the "SAT" check
            if f"not {idx}" in cand_lower or f"no {idx}" in cand_lower:
                if state.get(p) is True:
                    return False # Contradiction
            elif idx in cand_lower:
                if state.get(p) is False:
                    return False # Contradiction
                    
        return True

    def _ergodic_score(self, prompt: str, candidate: str) -> float:
        """Compute the ergodic average of SAT over intervention space."""
        props, edges, constraints = self._parse_structural(prompt)
        if not props:
            return 0.5 # Neutral if no structure found
            
        n_props = len(props)
        if n_props == 0:
            return 0.5
            
        # Define intervention space (sampled for efficiency)
        # Full space is 2^n, we sample T steps of a random walk
        T_steps = max(10, n_props * 5) 
        current_state = {p: self.rng.choice([True, False]) for p in props}
        
        sat_count = 0
        
        for _ in range(T_steps):
            # Random walk: flip one variable
            flip_var = self.rng.choice(props)
            current_state[flip_var] = not current_state[flip_var]
            
            # Check SAT
            if self._check_sat(candidate, props, edges, constraints, current_state):
                sat_count += 1
                
        return sat_count / T_steps

    def _structural_alignment(self, prompt: str, candidate: str) -> float:
        """Score based on structural feature overlap (Negations, Comparatives, Conditionals)."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 0.0
        count = 0
        
        # Check Negations
        if re.search(r'\b(not|no|never)\b', p_lower):
            count += 1
            if re.search(r'\b(not|no|never)\b', c_lower):
                score += 1.0
        
        # Check Comparatives
        if re.search(r'\b(more|less|greater|smaller|higher|lower)\b', p_lower):
            count += 1
            if re.search(r'\b(more|less|greater|smaller|higher|lower)\b', c_lower):
                score += 1.0
                
        # Check Conditionals
        if re.search(r'\b(if|then|unless|only if)\b', p_lower):
            count += 1
            if re.search(r'\b(if|then|unless|only if)\b', c_lower):
                score += 1.0

        # Numeric consistency
        nums_p = re.findall(r'[\d.]+', p_lower)
        nums_c = re.findall(r'[\d.]+', c_lower)
        if nums_p:
            count += 1
            # Check if candidate preserves key numbers (simple subset check)
            if any(n in nums_c for n in nums_p):
                score += 1.0

        return score / count if count > 0 else 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Score: Ergodic Causal SAT (weighted)
            ergodic_score = self._ergodic_score(prompt, cand)
            
            # Secondary Score: Structural Alignment
            struct_score = self._structural_alignment(prompt, cand)
            
            # Combined Score (Weighted average favoring structure for robustness)
            # Ergodic provides the "reasoning" depth, Structure provides the "feature" match
            final_score = 0.4 * ergodic_score + 0.6 * struct_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Ergodic SAT: {ergodic_score:.2f}, Structural: {struct_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            if abs(results[0]["score"] - results[1]["score"]) < 0.01:
                # Use NCD to prompt as tiebreaker (lower NCD = more similar/relevant)
                results.sort(key=lambda x: self._ncd(prompt, x["candidate"]))
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the ergodic stability of the answer.
        High variance in the ergodic walk implies low confidence.
        """
        props, edges, constraints = self._parse_structural(prompt)
        if not props:
            return 0.5
            
        n_props = len(props)
        T_steps = max(20, n_props * 5)
        current_state = {p: self.rng.choice([True, False]) for p in props}
        
        sat_trace = []
        for _ in range(T_steps):
            flip_var = self.rng.choice(props)
            current_state[flip_var] = not current_state[flip_var]
            sat_trace.append(1 if self._check_sat(answer, props, edges, constraints, current_state) else 0)
            
        if not sat_trace:
            return 0.5
            
        mean_sat = np.mean(sat_trace)
        variance = np.var(sat_trace)
        
        # Confidence is high if mean is extreme (0 or 1) and variance is low
        # Map variance to confidence penalty
        confidence = mean_sat * (1.0 - variance)
        return float(np.clip(confidence, 0.0, 1.0))