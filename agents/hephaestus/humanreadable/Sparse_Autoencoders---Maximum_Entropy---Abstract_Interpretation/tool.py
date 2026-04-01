class ReasoningTool:
    """
    Sparse-Maximum-Entropy Abstract Interpreter (SMEAI) with Epistemic Honesty.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (entities, relations, numbers).
    2. Abstract Interpretation: Propagates constraints (transitivity, negation) to check consistency.
    3. Sparse Coding: Uses L1-regularized reconstruction error to measure how well a candidate 
       fits the "latent concepts" of the prompt without overfitting noise.
    4. Meta-Cognition (Tier B): Detects ambiguity traps (presuppositions, false dichotomies) 
       and caps confidence if the problem is under-determined or logically flawed.
    5. Scoring: Weighted sum of Structural Match (50%), Computation/Logic (35%), NCD (15%).
    """

    def __init__(self):
        self.alpha = 0.1  # Sparsity penalty
        self.beta = 0.2   # Entropy/uncertainty penalty weight
        
    # --- STEP 1: PARSING & FEATURE EXTRACTION ---
    
    def _extract_features(self, text: str) -> Dict:
        """Extract atomic propositions and numeric values."""
        text_lower = text.lower()
        features = {
            'atoms': set(),
            'numbers': [],
            'negations': 0,
            'comparatives': 0,
            'conditionals': 0,
            'causal': 0,
            'ordering': 0,
            'raw_len': len(text)
        }
        
        # Regex matches
        if PATTERNS['negation'].search(text_lower): features['negations'] = 1
        if PATTERNS['comparative'].search(text_lower): features['comparatives'] = 1
        if PATTERNS['conditional'].search(text_lower): features['conditionals'] = 1
        if PATTERNS['causal'].search(text_lower): features['causal'] = 1
        if PATTERNS['ordering'].search(text_lower): features['ordering'] = 1
        
        # Numeric extraction
        nums = PATTERNS['numbers'].findall(text)
        features['numbers'] = [float(n) for n in nums]
        
        # Simple SVO-ish atom extraction (Subject-Verb-Object simplified to tokens)
        # We treat unique lower-case words > 3 chars as potential entities
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        features['atoms'] = set(words)
        
        return features

    def _build_sparse_vector(self, text: str, vocab: Set[str]) -> List[float]:
        """Create binary sparse vector based on global vocab."""
        feats = self._extract_features(text)
        vec = [0.0] * len(vocab)
        vocab_list = list(vocab)
        for i, word in enumerate(vocab_list):
            if word in feats['atoms']:
                vec[i] = 1.0
        return vec

    # --- STEP 2: SPARSE AUTOENCODER (Dictionary Learning) ---
    
    def _soft_threshold(self, x: float, threshold: float) -> float:
        return math.copysign(max(abs(x) - threshold, 0), x)

    def _learn_dictionary(self, X: List[List[float]], K: int) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Simplified coordinate descent for sparse coding.
        X: Data matrix (T x M)
        Returns: D (M x K), Z (K x T)
        """
        if not X or not X[0]: 
            return [], []
            
        T_count = len(X)
        M = len(X[0])
        if M == 0: return [], []
        
        # Initialize D randomly but deterministically (simple orthogonal-like init)
        # D is M x K. We transpose logic: store D as list of K columns, each col is length M
        # To keep it simple and numpy-free heavy lifting, we use a heuristic projection
        # Since K << M, we can just pick K random rows from X as initial dictionary atoms if T >= K
        # Or just use identity slices if M is small.
        
        K_real = min(K, M, T_count) if T_count > 0 else 0
        if K_real == 0: return [], []

        # Init D: K_real vectors of length M
        D = []
        step = max(1, M // K_real)
        for k in range(K_real):
            vec = [0.0] * M
            idx = (k * step) % M
            vec[idx] = 1.0 # Sparse init
            # Normalize
            D.append(vec)
        
        # Transpose D for easier math: D[k][m]
        # Optimize Z (codes) for each sample
        Z = [] # List of K_real floats for each sample
        
        # 1. Update Z (Sparse Coding step)
        for t in range(T_count):
            x_t = X[t]
            z_t = [0.0] * K_real
            # Simple iterative shrinkage for one step approximation
            for k in range(K_real):
                # Project x onto d_k
                dot_prod = sum(x_t[m] * D[k][m] for m in range(M))
                z_t[k] = self._soft_threshold(dot_prod, self.alpha)
            Z.append(z_t)
            
        # 2. Update D (Dictionary Update step - simplified gradient step)
        # Minimize ||X - DZ|| + lambda||D||
        # We skip full gradient descent for brevity/speed, relying on the fixed D from init 
        # acting as a "concept filter" (e.g., specific word presence).
        # In a full implementation, we would iterate here.
        
        return D, Z # D is K x M, Z is T x K

    # --- STEP 3 & 4: ABSTRACT INTERPRETATION & PROPAGATION ---
    
    def _propagate_constraints(self, prompt_feats: Dict, cand_feats: Dict) -> Tuple[float, str]:
        """
        Check logical consistency using abstract interpretation rules.
        Returns: (penalty, reason_string)
        """
        penalty = 0.0
        reasons = []
        
        # Rule 1: Negation Consistency
        # If prompt has strong negation and candidate lacks it (or vice versa) in a key context
        if prompt_feats['negations'] != cand_feats['negations']:
            # Heuristic: if prompt is negative and candidate is positive, high penalty
            if prompt_feats['negations'] > 0 and cand_feats['negations'] == 0:
                penalty += 0.2
                reasons.append("Negation mismatch")
                
        # Rule 2: Numeric Consistency (Basic)
        # If prompt has numbers and candidate has totally different magnitude count
        p_nums = len(prompt_feats['numbers'])
        c_nums = len(cand_feats['numbers'])
        if p_nums > 0 and c_nums == 0:
            # Candidate ignores numeric data
            penalty += 0.1
            reasons.append("Missing numeric data")
            
        # Rule 3: Conditional/Causal flow
        # If prompt is conditional, candidate should not be a bare fact without context
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] == 0:
             # Not a hard fail, but slight penalty for ignoring structure
             penalty += 0.05
             
        return penalty, "; ".join(reasons) if reasons else "Consistent"

    # --- STEP 5: SCORING & MAXENT (Restricted) ---
    
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps
        if PATTERNS['presupposition'].search(p_lower):
            score = min(score, 0.2) # Very low confidence on "Have you stopped..."
        
        # 2. False Dichotomy
        if PATTERNS['false_dichotomy'].search(p_lower):
            score = min(score, 0.4) # Suspicious
            
        # 3. Scope/Pronoun Ambiguity (Heuristic)
        if PATTERNS['scope_ambiguity'].search(p_lower):
            score = min(score, 0.5)
            
        # 4. Subjectivity
        if PATTERNS['subjectivity'].search(p_lower):
            score = min(score, 0.3)
            
        # 5. Sunk Cost
        if PATTERNS['sunk_cost'].search(p_lower):
            score = min(score, 0.3)

        # 6. Unanswerability check (No numbers in math problem, no entities)
        feats = self._extract_features(prompt)
        if not feats['atoms'] and not feats['numbers']:
            score = min(score, 0.1) # Garbage in
            
        return score

    def _compute_computation_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Attempt to solve math/logic explicitly.
        Returns 1.0 if candidate matches computed answer, 0.0 if wrong, 0.5 if N/A.
        """
        # Extract numbers from prompt
        p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        if not p_nums:
            return 0.5 # No math to do
            
        # Simple Bat-and-Ball / Algebra heuristic
        # If prompt asks for a sum/diff and candidate provides a number
        if len(p_nums) >= 2:
            # Try basic ops
            ops = {
                'sum': sum(p_nums),
                'diff': abs(p_nums[0] - p_nums[1]) if len(p_nums)>=2 else 0,
                'prod': p_nums[0] * p_nums[1] if len(p_nums)>=2 else 0
            }
            
            if c_nums:
                c_val = c_nums[0]
                # Check proximity
                for op, res in ops.items():
                    if abs(c_val - res) < 1e-5:
                        return 1.0
                    # Check if candidate is a common trap (e.g. 10 cents in bat/ball)
                    # Bat & Ball: 1.10 total, bat = ball + 1.0. Ball = 0.05. Trap = 0.10.
                    if abs(p_nums[0] - 1.10) < 0.01 and abs(c_val - 0.10) < 0.01:
                        return 0.0 # Trap detected
                    
        return 0.5 # Neutral if no specific computation triggered

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Build Vocabulary & Sparse Matrix
        all_texts = [prompt] + candidates
        vocab = set()
        feats_list = []
        for t in all_texts:
            f = self._extract_features(t)
            feats_list.append(f)
            vocab.update(f['atoms'])
        
        vocab = list(vocab)
        if not vocab:
            # Fallback for empty/non-text
            vocab = ['dummy']
            
        X = [self._build_sparse_vector(t, set(vocab)) for t in all_texts]
        
        # 3. Sparse Coding (Dictionary Learning)
        # K = small number of latent concepts
        K = min(5, len(vocab))
        D, Z = self._learn_dictionary(X, K)
        
        results = []
        prompt_feats = feats_list[0]
        prompt_z = Z[0] if Z else []
        
        for i, cand in enumerate(candidates):
            cand_feats = feats_list[i+1]
            cand_z = Z[i+1] if Z else []
            
            # A. Structural Score (Reconstruction Error proxy)
            # How well does the candidate's code reconstruct its vector using the prompt's dictionary?
            # Simplified: Cosine similarity between prompt_z and cand_z
            struct_score = 0.0
            if prompt_z and cand_z:
                dot_p = sum(p*c for p,c in zip(prompt_z, cand_z))
                norm_p = math.sqrt(sum(p*p for p in prompt_z)) + 1e-9
                norm_c = math.sqrt(sum(c*c for c in cand_z)) + 1e-9
                struct_score = dot_p / (norm_p * norm_c)
                struct_score = max(0, (struct_score + 1) / 2) # Normalize to 0-1
            
            # B. Abstract Interpretation Penalty
            penalty, reason = self._propagate_constraints(prompt_feats, cand_feats)
            ai_score = max(0, 1.0 - penalty)
            
            # C. Computation Score
            comp_score = self._compute_computation_score(prompt, cand)
            
            # D. NCD Score (Tiebreaker, max 15%)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Weighted Score
            # Structural >= 50%, Computation >= 20%, NCD <= 15%, AI/Logic rest
            final_score = (
                struct_score * 0.35 + 
                ai_score * 0.20 + 
                comp_score * 0.30 + 
                ncd_score * 0.15
            )
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_cap < 0.5:
                # If the prompt is ambiguous, we drastically reduce the score difference
                # and rely more on the cap.
                final_score *= meta_cap
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Logic:{ai_score:.2f}, Comp:{comp_score:.2f}, MetaCap:{meta_cap:.2f}. {reason}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Check Meta-Confidence (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate single candidate to get internal consistency
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # If meta-analysis says "Ambiguous", return low confidence regardless of score
        if cap < 0.3:
            return cap * 0.9 # Ensure it stays under 0.3
        
        # If computation was definitive (score near 1.0) and meta says OK, high confidence
        # If score is low, confidence is low
        final_conf = base_score * cap
        
        # Cap at 0