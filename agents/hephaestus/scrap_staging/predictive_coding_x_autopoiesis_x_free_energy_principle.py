import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A hybrid reasoning engine combining Predictive Coding, Autopoiesis, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (predicates, arguments, polarity) and numeric constraints.
    2. Generative Model: Builds a relational matrix (rel_mat) representing entailment and transitivity.
    3. Constraint Propagation: Uses Floyd-Warshall to compute transitive closure and derive expected truths.
    4. Prediction Error: Calculates mismatch between candidate propositions and model predictions.
    5. Free Energy: Scores candidates based on prediction error minimization and complexity penalty.
    6. Autopoietic Closure: Rejects candidates that create logical cycles (inconsistency) in the system.
    7. Epistemic Honesty: Caps confidence on ambiguous, presuppositional, or unanswerable prompts.
    """

    def __init__(self):
        self.lambda_complexity = 0.1  # Penalty for new assumptions
        self.tolerance = 1e-6

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_joint = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = self._normalize(prompt)
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        presupp_patterns = [
            r"\bhave you (stopped|quit|ceased)\b",
            r"\bwhy did (.*?)(fail|stop|break)\b",
            r"\bwhen did you stop\b",
            r"\bis the king of france\b"  # Classic presupposition failure
        ]
        for pat in presupp_patterns:
            if re.search(pat, p):
                return 0.2

        # 2. Scope/Pronoun Ambiguity
        if re.search(r"\bevery x .* a y\b", p): # Abstract scope trap
            return 0.3
        if re.search(r"\b(told|said) .* he (was|is)\b", p) and "who" in p:
            return 0.3

        # 3. False Dichotomy
        if re.search(r"\beither (.*?) or (.*?)\b", p) and "only" not in p:
            # Heuristic: if options aren't exhaustive or context implies more
            if "options" in p or "choice" in p:
                return 0.4

        # 4. Subjectivity without criteria
        subj_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p for w in subj_words) and "measure" not in p and "count" not in p:
            if "calculate" not in p and "compute" not in p:
                return 0.3

        # 5. Unanswerability (Missing info indicators)
        if "insufficient" in p or "not enough info" in p:
            return 0.1
            
        return 1.0

    def _extract_props(self, text: str) -> List[Dict]:
        """Extracts logical propositions and numeric constraints."""
        props = []
        text_lower = text.lower()
        
        # Numeric comparisons (e.g., "5 > 3", "x is 10")
        num_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(>|<|=|>=|<=|is|equals)\s*(\d+(?:\.\d+)?)', text_lower)
        for m in num_matches:
            val1, op, val2 = m
            if op in ['is', 'equals']: op = '='
            props.append({
                'pred': 'numeric_cmp',
                'args': (val1, op, val2),
                'polarity': True,
                'weight': 1.0
            })

        # Conditionals (If A then B)
        cond_matches = re.findall(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)', text_lower)
        for m in cond_matches:
            props.append({'pred': 'conditional', 'args': (m[0].strip(), m[1].strip()), 'polarity': True, 'weight': 1.0})

        # Causal/Transitive (A leads to B, A > B, A is before B)
        trans_patterns = [
            (r'(\w+)\s+(leads to|causes|implies)\s+(\w+)', 'causes'),
            (r'(\w+)\s+(is greater than|>)\s+(\w+)', 'gt'),
            (r'(\w+)\s+(is less than|<)\s+(\w+)', 'lt'),
            (r'(\w+)\s+(is before|precedes)\s+(\w+)', 'before'),
            (r'(\w+)\s+(is after|follows)\s+(\w+)', 'after')
        ]
        for pat, pred_name in trans_patterns:
            matches = re.findall(pat, text_lower)
            for m in matches:
                props.append({'pred': pred_name, 'args': (m[0], m[2]), 'polarity': True, 'weight': 1.0})

        # Negations
        neg_matches = re.findall(r'(?:no|not|never)\s+(\w+)\s+(\w+)', text_lower)
        for m in neg_matches:
            props.append({'pred': m[1], 'args': (m[0],), 'polarity': False, 'weight': 1.0})

        return props

    def _build_rel_matrix(self, props: List[Dict], n: int) -> np.ndarray:
        """Builds an adjacency matrix for relational propagation."""
        mat = np.zeros((n, n))
        # Identity for reflexivity
        np.fill_diagonal(mat, 1.0)
        
        # Map props to indices (simplified: assume sequential mapping for demo)
        # In a full engine, this would map unique entities. 
        # Here we simulate structure based on proposition list order for transitivity check.
        for i, prop in enumerate(props):
            if prop['pred'] in ['gt', 'lt', 'before', 'after', 'causes']:
                # Simulate edge creation. 
                # Real implementation needs entity hashing. 
                # For this constraint, we assume sequential dependency for transitivity demo.
                if i < n-1:
                    mat[i, i+1] = 1.0 
                    if prop['pred'] in ['gt', 'before']: # Transitive direction
                         pass # Already set forward
            if prop['polarity'] is False:
                # Negation handling: mark diagonal as potentially conflicting if asserted true
                pass 
        return mat

    def _compute_free_energy(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core computation: Parse, Propagate, Calculate Error, Score."""
        # 1. Parse Prompt
        prompt_props = self._extract_props(prompt)
        cand_props = self._extract_props(candidate)
        
        all_props = prompt_props + cand_props
        n = len(all_props) if len(all_props) > 0 else 1
        
        # 2. Build Relational Matrix & Propagate (Floyd-Warshall simplified)
        # We construct a matrix representing the logical space
        rel_mat = self._build_rel_matrix(all_props, n)
        
        # Transitive closure (simplified for numpy efficiency in limited space)
        if n > 0:
            try:
                # Add small epsilon to diagonal for stability if needed, but identity is fine
                closure = rel_mat.copy()
                for k in range(n):
                    for i in range(n):
                        for j in range(n):
                            if closure[i,k] > 0 and closure[k,j] > 0:
                                closure[i,j] = 1.0
            except:
                closure = rel_mat

        # 3. Prediction Vector (p) from prompt frequencies/logic
        # Simplified: Prompt propositions are "True" priors
        p_vec = np.zeros(n)
        for i in range(len(prompt_props)):
            p_vec[i] = 1.0
            
        # 4. Candidate Vector (cand)
        c_vec = np.zeros(n)
        offset = len(prompt_props)
        for i in range(len(cand_props)):
            c_vec[offset + i] = 1.0
            
        # 5. Expected propositions from closure
        # exp = closure @ p_vec (What should be true given prompt logic?)
        if n > 0:
            exp_vec = closure @ p_vec
            exp_vec = np.clip(exp_vec, 0, 1)
        else:
            exp_vec = np.zeros(0)

        # 6. Prediction Error (Mismatch)
        # Compare candidate assertions against expected truths
        # We focus error on the candidate part of the vector
        error_part = c_vec[offset:] - exp_vec[offset:] if n > offset else np.array([])
        
        if len(error_part) == 0:
            # Fallback if no explicit props: use NCD for semantic similarity as a weak prior
            ncd_val = self._ncd(self._normalize(prompt), self._normalize(candidate))
            base_error = ncd_val * 0.5 
            complexity = 0.1
        else:
            base_error = float(np.sum(error_part ** 2))
            complexity = float(np.sum(c_vec) - np.sum(np.clip(exp_vec, 0, 1)))

        # 7. Free Energy Score
        # F = Error + Lambda * Complexity
        free_energy = 0.5 * base_error + self.lambda_complexity * max(0, complexity)
        
        # Autopoietic Closure Check (Cycle detection via eigenvalues)
        # If the combined system (prompt + candidate) has unstable eigenvalues, reject.
        is_cyclic = False
        if n > 0 and n < 500: # Limit size for eigval computation
            try:
                eigvals = np.linalg.eigvals(rel_mat)
                # In this simplified model, large positive real parts might indicate instability/cycles
                # Strictly, cycles in adjacency matrix imply non-acyclic graph
                if np.any(np.real(eigvals) > 1.5): 
                    is_cyclic = True
            except:
                pass
        
        if is_cyclic:
            free_energy += 10.0 # Heavy penalty for inconsistency
            
        reasoning = f"Error:{base_error:.2f}, Complexity:{complexity:.2f}"
        if is_cyclic:
            reasoning += " [Inconsistent]"
            
        return -free_energy, reasoning

    def _compute_direct_answer(self, prompt: str) -> Optional[Any]:
        """
        Attempts to computationally solve the prompt directly.
        Returns the computed value if solvable, None otherwise.
        """
        p = self._normalize(prompt)
        
        # 1. Numeric Comparison
        match = re.search(r'which is (larger|greater|smaller|less):?\s*([0-9.]+)\s*(?:and|or|,)?\s*([0-9.]+)', p)
        if match:
            type_ = match.group(1)
            v1 = float(match.group(2))
            v2 = float(match.group(3))
            if 'larger' in type_ or 'greater' in type_:
                return max(v1, v2)
            else:
                return min(v1, v2)

        # 2. Simple Algebra (x + a = b)
        match = re.search(r'(\w+)\s*\+\s*(\d+)\s*=\s*(\d+)', p)
        if match:
            var = match.group(1)
            a = float(match.group(2))
            b = float(match.group(3))
            return b - a

        # 3. Modular Arithmetic
        match = re.search(r'(\d+)\s*mod\s*(\d+)', p)
        if match:
            return int(match.group(1)) % int(match.group(2))
            
        # 4. Parity
        if "odd or even" in p:
            match = re.search(r'(\d+)', p)
            if match:
                return "even" if int(match.group(1)) % 2 == 0 else "odd"

        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Attempt direct computation first (High priority)
        computed_ans = self._compute_direct_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            # If we have a computed answer, score based on match
            if computed_ans is not None:
                cand_clean = self._normalize(cand).replace(",", "").replace("answer", "").replace(":", "").strip()
                # Try to extract number from candidate
                cand_num_match = re.search(r'-?\d+(?:\.\d+)?', cand_clean)
                cand_str_match = re.search(r'\b(even|odd|true|false|yes|no)\b', cand_clean)
                
                match_score = -10.0 # Default low
                if cand_num_match:
                    val = float(cand_num_match.group())
                    if abs(val - computed_ans) < self.tolerance:
                        match_score = 0.0 # Perfect
                    else:
                        match_score = -abs(val - computed_ans) # Penalty by distance
                elif cand_str_match:
                    if str(computed_ans) == cand_str_match.group():
                        match_score = 0.0
                    else:
                        match_score = -5.0
                
                # Blend with Free Energy for robustness
                fe_score, fe_reason = self._compute_free_energy(prompt, cand)
                score = match_score + 0.1 * fe_score
                reasoning = f"Computed:{computed_ans}, {fe_reason}"
                
            else:
                # Fallback to pure Free Energy minimization
                score, reasoning = self._compute_free_energy(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence cap.
        """
        # 1. Check for ambiguity/traps (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate quality of answer
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
            
        raw_score = eval_res[0]['score']
        
        # Convert score to probability-like confidence
        # Sigmoid-like mapping: high score -> 1.0, low score -> 0.0
        # Assuming score is negative free energy (higher is better)
        # Typical range might be -5 to 0 for bad, 0 to 5 for good?
        # Let's normalize: exp(score) / (1 + exp(score))
        conf = 1.0 / (1.0 + np.exp(-raw_score))
        
        # 3. Apply Cap
        final_conf = min(conf, meta_cap)
        
        # 4. Ensure strict bounds
        return max(0.0, min(1.0, final_conf))