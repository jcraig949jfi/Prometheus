class ReasoningTool:
    """
    Dynamical Systems Free-Energy Reasoning Tool.
    
    Mechanism:
    1. Parses prompts/candidates into propositions and logical constraints (A matrix).
    2. Uses a gradient descent on Free Energy to settle belief states (x) consistent with constraints.
    3. Computes sensitivity (Jacobian) to penalize fragile answers.
    4. Integrates explicit computational solvers (math, logic) and epistemic checks for ambiguity.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.eta = 0.1  # Step size
        self.lambda_const = 1.0  # Constraint weight
        self.mu_prior = 0.5
        
        # Patterns for Tier B Epistemic Honesty
        self.presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*(?:fail|stop|quit)\b", 
            r"\bwhen did.*(?:stop|fail)\b", r"\bregret\b.*\bdecision\b"
        ]
        self.scope_patterns = [r"\bevery\b.*\ba\s+\w+\b"] # Simplified scope check
        self.pronoun_patterns = [r"\b(told|said|asked)\b.*\bhe\b.*\bwho\b", r"\bhe\b.*\bwas\b.*\bwrong\b"]
        self.dichotomy_patterns = [r"\beither\b.*\bor\b", r"\bmust\b.*\bchoose\b"]
        self.subjectivity_patterns = [r"\b(best|worst|favorite|beautiful)\b.*\bwithout\b", r"\bopinion\b"]

    def _extract_props_and_constraints(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray]:
        """
        Extracts literals and builds constraint matrix A, observation vector y, and prior mu.
        Returns: (literals, A, y, mu)
        """
        text_lower = text.lower()
        literals = []
        constraints = [] # List of (i, j, type)
        y_vals = []
        mu_vals = []
        
        # Helper to add literal and return index
        def get_idx(lit: str, val: Optional[float] = None, is_neg: bool = False) -> int:
            lit_clean = lit.strip()
            if not lit_clean: return -1
            if lit_clean not in literals:
                literals.append(lit_clean)
                idx = len(literals) - 1
                # Initialize y based on immediate assertion in text if possible, else 0.5
                # For this simplified parser, we assume extracted literals from candidate are 'asserted true'
                # unless negation is detected.
                y_vals.append(1.0 if not is_neg else 0.0)
                mu_vals.append(self.mu_prior)
            return literals.index(lit_clean)

        # 1. Extract simple sentences/clauses as literals
        # Split by common delimiters but keep structure for regex
        segments = re.split(r'[.;,]', text)
        
        for seg in segments:
            seg = seg.strip()
            if not seg: continue
            
            is_neg = bool(re.search(r'\b(not|no|never|none)\b', seg))
            
            # Extract comparatives for constraint generation
            comp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:is|was|are)?\s*(<|>|less than|more than|greater than|smaller than)\s*(\d+(?:\.\d+)?)', seg)
            if comp_match:
                v1, op, v2 = comp_match.groups()
                lit1 = f"val_{v1}"
                lit2 = f"val_{v2}"
                i1 = get_idx(lit1, float(v1), is_neg)
                i2 = get_idx(lit2, float(v2), is_neg)
                if i1 >= 0 and i2 >= 0:
                    if op in ['<', 'less than', 'smaller than']:
                        constraints.append((i1, i2, 'lt')) # v1 < v2
                    elif op in ['>', 'more than', 'greater than']:
                        constraints.append((i2, i1, 'lt')) # v2 < v1 -> v1 > v2
                continue

            # Extract conditionals "If A then B" -> A implies B
            if_match = re.search(r'if\s+(.+?)\s+(?:then)?\s+(.+)', seg, re.IGNORECASE)
            if if_match:
                # Simplified: treat antecedent and consequent as separate props with implication constraint
                # In this simplified model, we just register the literals and add a soft constraint later
                pass

            # Default literal extraction (noun phrases or whole segment)
            # Remove noise words for literal ID
            clean_seg = re.sub(r'\b(the|a|an|is|are|was|were|be|been|being|have|has|had|do|does|did)\b', '', seg)
            if clean_seg.strip():
                get_idx(clean_seg.strip(), is_neg=is_neg)

        n = len(literals)
        if n == 0:
            return [], np.zeros((0,0)), np.zeros(0), np.zeros(0)

        A_rows = []
        # Build A matrix from constraints
        for i, j, ctype in constraints:
            if ctype == 'lt':
                # Encode p_i < p_j as p_i - p_j <= 0 -> row: [0..1..-1..0]
                row = np.zeros(n)
                row[i] = 1.0
                row[j] = -1.0
                A_rows.append(row)
        
        # Add consistency constraints (optional, e.g., p and not p)
        # For this implementation, we rely on the extracted y vector to drive the state.
        # If a literal appears in the candidate, y=1. If the prompt implies contradiction, 
        # the free energy minimization will struggle, increasing F.
        
        if not A_rows:
            A = np.zeros((1, n)) # Dummy row to avoid shape errors if no constraints
            y = np.array(y_vals)
        else:
            A = np.vstack(A_rows)
            y = np.array(y_vals)
            
        # Ensure dimensions match
        if len(y) != n:
            y = np.ones(n) * 0.5 # Fallback
            
        return literals, A, y, np.array(mu_vals[:n])

    def _compute_free_energy_step(self, x: np.ndarray, A: np.ndarray, y: np.ndarray, mu: np.ndarray) -> np.ndarray:
        if A.shape[0] == 0 or A.shape[1] == 0:
            return x - self.eta * (x - mu)
        
        # Gradient of Free Energy:
        # F = 0.5 * ||x - mu||^2 + 0.5 * lambda * ||Ax - y||^2
        # grad F = (x - mu) + lambda * A^T (Ax - y)
        
        residual = A @ x - y
        grad = (x - mu) + self.lambda_const * (A.T @ residual)
        return x - self.eta * grad

    def _run_dynamics(self, A: np.ndarray, y: np.ndarray, mu: np.ndarray) -> Tuple[np.ndarray, float, float]:
        n = len(mu)
        if n == 0: return np.array([]), 0.0, 0.0
        
        x = np.ones(n) * self.mu_prior
        for _ in range(100): # Max iterations
            x_new = self._compute_free_energy_step(x, A, y, mu)
            # Clamp to [0, 1]
            x_new = np.clip(x_new, 0.0, 1.0)
            if np.linalg.norm(x_new - x) < self.epsilon:
                break
            x = x_new
            
        # Compute final Free Energy (negative is better)
        term1 = 0.5 * np.sum((x - mu)**2)
        term2 = 0.0
        if A.shape[0] > 0:
            term2 = 0.5 * self.lambda_const * np.sum((A @ x - y)**2)
        F = term1 + term2
        
        # Sensitivity Analysis (Jacobian approximation)
        # J approx inverse(I - eta * (I + lambda A^T A)) * eta * lambda * A^T
        # We compute the norm of the sensitivity to perturbations in y
        try:
            if A.shape[0] > 0:
                I = np.eye(n)
                H = I + self.lambda_const * (A.T @ A)
                # Jacobian of update w.r.t y (simplified for steady state sensitivity)
                # Sensitivity ~ (H)^-1 * A^T
                J = np.linalg.solve(H, A.T) 
                sens_norm = np.linalg.norm(J, 'fro')
            else:
                sens_norm = 0.0
        except np.linalg.LinAlgError:
            sens_norm = 10.0 # High penalty for singular matrices (unstable)

        return x, -F, sens_norm

    def _check_computation(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Explicitly solve math/logic problems if detected.
        Returns a confidence score if a definitive calculation is possible, else None.
        """
        full_text = f"{prompt} {candidate}"
        
        # 1. Numeric Comparison
        nums = re.findall(r'[-]?\d+(?:\.\d+)?', full_text)
        if len(nums) >= 2:
            # Check for explicit comparison words
            if any(k in full_text.lower() for k in ['greater', 'larger', 'more', 'less', 'smaller', 'equal']):
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    # Determine expected relation from prompt
                    is_correct = False
                    if 'greater' in full_text.lower() or 'more' in full_text.lower():
                        is_correct = v1 > v2 if 'first' in full_text.lower() else (v1 != v2) # Heuristic
                    elif 'less' in full_text.lower() or 'smaller' in full_text.lower():
                        is_correct = v1 < v2
                    
                    if is_correct: return 0.95
                    # If we can determine it's wrong, return low score
                    # But be careful not to over-penalize if logic is complex
                except: pass

        # 2. Direct Arithmetic (e.g. "What is 2+2?" -> "4")
        match = re.search(r'(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)\s*=?\s*(-?\d+(?:\.\d+)?)', full_text)
        if match:
            try:
                a, op, b, res = match.groups()
                a, b, res = float(a), float(b), float(res)
                calc = 0
                if op == '+': calc = a + b
                elif op == '-': calc = a - b
                elif op == '*': calc = a * b
                elif op == '/': calc = a / b if b != 0 else 9999
                if abs(calc - res) < 1e-6:
                    return 1.0
                else:
                    return 0.1
            except: pass
            
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.presupposition_patterns:
            if re.search(pat, p_lower):
                return 0.2 # Low confidence on presupposition traps
        
        # 2. Scope/Pronoun Ambiguity (Heuristic)
        if re.search(r'\bevery\b', p_lower) and re.search(r'\bsame\b|\bdifferent\b', p_lower):
            return 0.4 # Ambiguous scope
        if re.search(r'\b(told|said)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.3 # Pronoun ambiguity
            
        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bor\s+else\b|\bor\s+not\b', p_lower):
            # Simple check, might need more context to be sure, but flagging reduces confidence
            pass 
            
        # 4. Subjectivity
        if any(k in p_lower for k in ['best', 'worst', 'favorite']) and 'data' not in p_lower:
            return 0.5
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(z1), len(z2), len(z12)
        if len1 == 0 or len2 == 0: return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-compute prompt constraints
        p_literals, p_A, p_y, p_mu = self._extract_props_and_constraints(prompt)
        n_p = len(p_literals)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Computational Check (High priority)
            comp_score = self._check_computation(prompt, cand)
            if comp_score is not None:
                # If computation gives a definitive answer, trust it heavily
                base_score = comp_score
                reasoning_parts.append(f"Computation detected: {comp_score}")
            else:
                # 2. Dynamical Systems / Free Energy
                # Combine prompt and candidate for joint inference
                full_text = f"{prompt} {cand}"
                literals, A, y, mu = self._extract_props_and_constraints(full_text)
                
                if len(literals) == 0:
                    base_score = 0.5
                    reasoning_parts.append("No structural props found.")
                else:
                    # Run dynamics
                    x, neg_F, sens_norm = self._run_dynamics(A, y, mu)
                    
                    # Score = -FreeEnergy - alpha * Sensitivity
                    # Normalize F roughly to [0, 1] range for scoring
                    # F is negative in our return (so -F is positive energy cost? No, function returns -F)
                    # Let's align: Lower F is better. We returned -F. So higher returned value is better?
                    # Wait, F = term1 + term2 (positive). We returned -F.
                    # So if F is small (good fit), -F is close to 0 (from negative side).
                    # If F is large, -F is large negative.
                    # We want high score for good fit. So Score ~ -F.
                    
                    raw_score = neg_F - (0.1 * sens_norm)
                    
                    # Normalize to 0-1 range heuristically
                    # Assuming typical F ranges, map to sigmoid-like
                    base_score = 1.0 / (1.0 + np.exp(-raw_score)) 
                    
                    reasoning_parts.append(f"FreeEnergy: {neg_F:.4f}, Sens: {sens_norm:.4f}")

            # 3. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            # NCD 0 = identical, 1 = different. We want high similarity for context, 
            # but for QA, the answer might be short. 
            # Use NCD only if structural score is ambiguous or as a small bonus for relevance.
            ncd_bonus = (1.0 - ncd) * 0.15 
            
            final_score = (base_score * 0.85) + ncd_bonus
            
            # Apply Meta-Confidence Cap (Tier B)
            if final_score > meta_cap:
                final_score = meta_cap
                reasoning_parts.append(f"Capped by meta-confidence ({meta_cap})")
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Rank by score
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit.
        """
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        # Run evaluation on single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # If no structural parsing happened (score ~0.5 default), and meta_cap is low, reduce.
        # If computation gave a definitive 1.0 or 0.1, respect that unless capped.
        
        final_conf = min(score, meta_cap)
        
        # Ensure we don't return >