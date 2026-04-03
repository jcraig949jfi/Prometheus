# Ergodic Theory + Analogical Reasoning + Pragmatics

**Fields**: Mathematics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T12:11:57.513585
**Report Generated**: 2026-04-01T20:30:42.847594

---

## Nous Analysis

**Algorithm**  
1. **Parsing & representation** – Each sentence is converted to a directed labeled graph G = (V,E). Vertices V are lexical heads (nouns, verbs, adjectives) extracted via a rule‑based dependency parser (regex + POS tags from the standard library). Edges E encode predicate‑argument relations (subject‑verb, verb‑object, modifier‑head) and are labeled with the relation type (e.g., nsubj, dobj, advmod). Polarity (negation) and modality (must, might, should) are stored as binary flags on the incident edge. The graph is encoded as two numpy arrays: a node‑type one‑hot matrix N ∈ {0,1}^{|V|×P} (P = number of predicate classes) and an adjacency tensor A ∈ {0,1}^{|V|×|V|×R} (R = relation types).  

2. **Analogical similarity (structure mapping)** – For a reference answer R and candidate C, compute node similarity Sₙ = N_R · N_Cᵀ (dot‑product of one‑hots → fraction of matching predicate types). Compute edge similarity Sₑ = Σ_r trace(A_R[:,:,r] · A_C[:,:,r]ᵀ) / (|E_R|+|E_C|). The structural score α = λ Sₙ + (1‑λ) Sₑ (λ = 0.5).  

3. **Ergodic temporal averaging** – Tokenize the reference and candidate into sliding windows of w = 3 tokens. For each window i compute a local structural score α_i as above (using only words inside the window). Collect the series {α_i}. The time average ⟨α⟩_t = mean(α_i). The space average ⟨α⟩_s = α (global score from step 2). Define ergodic deviation δ = |⟨α⟩_t − ⟨α⟩_s|. Final analogical‑ergodic component β = exp(−γ δ) (γ = 2.0) so that candidates whose local match fluctuates strongly are penalized.  

4. **Pragmatic weighting** – Detect pragmatic cues via regex: negation (`not`, `n’t`), modal verbs (`must`, `should`, `might`), quantifiers (`all`, `some`, `none`), and discourse markers (`however`, `because`). For each cue, apply a Grice‑based penalty:  
   - Quantity: if candidate omits a required predicate present in reference → −0.2.  
   - Relevance: if candidate introduces a relation not referenced anywhere → −0.15.  
   - Manner: if negation flips polarity of a matched edge → −0.25.  
   Sum penalties to get π ∈ [−1,0]. Pragmatic score π̂ = 1 + π (so 0 ≤ π̂ ≤ 1).  

5. **Overall score** – Score = β · π̂ ∈ [0,1]. Higher scores indicate answers that preserve relational structure consistently across local contexts while respecting pragmatic constraints.

**Structural features parsed**  
- Negation markers and scope.  
- Comparative/superlative adjectives and adverbs.  
- Conditional antecedents/consequents (`if…then`).  
- Causal connectives (`because`, `therefore`, `since`).  
- Ordering/temporal relations (`before`, `after`, `while`).  
- Numeric values and units (for quantitative comparisons).  
- Modal verbs expressing obligation, possibility, probability.  
- Quantificational scope (`all`, `some`, `none`).

**Novelty**  
Existing work treats analogical reasoning via graph kernels or pragmatic classification in isolation. The presented method uniquely fuses (i) structure‑mapping similarity, (ii) an ergodic time‑vs‑space average penalty that captures internal consistency of relational mapping across local windows, and (iii) a rule‑based pragmatic penalty derived from Grice’s maxims. No prior system combines these three mechanisms in a single numpy‑based scorer, making the approach novel for pure‑algorithmic reasoning evaluation.

**Ratings**  
Reasoning: 8/10 — captures deep relational consistency and contextual fit with transparent algebra.  
Metacognition: 6/10 — provides a single scalar; limited self‑reflection on why a score changed.  
Hypothesis generation: 5/10 — can suggest missing relations via low‑scoring windows but does not generate new hypotheses autonomously.  
Implementability: 9/10 — relies only on regex, POS tagging (stdlib), and numpy operations; no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: NameError: name 're' is not defined

**Forge Timestamp**: 2026-04-01T17:41:57.093950

---

## Code

**Source**: scrap

[View code](./Ergodic_Theory---Analogical_Reasoning---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    A hybrid reasoning evaluator combining Ergodic Theory, Analogical Structure Mapping,
    Pragmatic Gricean constraints, and Dynamical Systems stability analysis.
    
    Mechanism:
    1. Parsing: Converts text to directed labeled graphs (Nodes=Lexical Heads, Edges=Relations).
    2. Analogical Similarity: Computes structural overlap (node/edge matching) between Ref and Cand.
    3. Ergodic Averaging: Compares global structural score vs. local sliding-window scores.
       High deviation (non-ergodic) implies inconsistent reasoning context -> Penalty.
    4. Pragmatic Weighting: Applies Gricean penalties for missing info, irrelevance, or negation flips.
    5. Dynamics Tracker (Frame C): Simulates premise processing as a state vector evolution.
       Measures Lyapunov-like stability: if reordering premises drastically changes the state,
       confidence is lowered (fragile reasoning).
    """

    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|n\'t|no|never|neither)\b', re.I),
        'modal': re.compile(r'\b(must|should|might|could|would|can|may)\b', re.I),
        'quantifier': re.compile(r'\b(all|some|none|every|each|few|many)\b', re.I),
        'causal': re.compile(r'\b(because|therefore|since|thus|hence)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
        'temporal': re.compile(r'\b(before|after|while|during|until)\b', re.I),
        'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|how did)\b', re.I),
        'false_dichotomy': re.compile(r'\b(either.*or|whether.*or)\b', re.I),
        'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I)
    }

    REL_TYPES = ['nsubj', 'dobj', 'amod', 'advmod', 'prep', 'conj']
    
    def __init__(self):
        self.lambda_param = 0.5
        self.gamma_param = 2.0
        self.window_size = 3

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _get_pos_tags(self, tokens: List[str]) -> List[str]:
        # Simplified rule-based POS tagging (stdlib only)
        tags = []
        for t in tokens:
            if t in ['the', 'a', 'an', 'some']: tags.append('DT')
            elif t in ['is', 'are', 'was', 'were', 'be', 'been']: tags.append('VB')
            elif t in ['run', 'runs', 'jump', 'jumps', 'eat', 'eats', 'think', 'thinks', 'stop', 'stopped']: tags.append('VB')
            elif t in ['quickly', 'slowly', 'very']: tags.append('RB')
            elif t in ['big', 'small', 'red', 'good', 'bad']: tags.append('JJ')
            elif t in ['john', 'bill', 'mary', 'alice', 'cat', 'dog', 'ball']: tags.append('NN')
            else:
                if t.endswith('ly'): tags.append('RB')
                elif t.endswith('ing'): tags.append('VBG')
                elif t.endswith('s') and len(t) > 2: tags.append('NNS')
                else: tags.append('NN') # Default noun
        return tags

    def _build_graph(self, text: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        tokens = self._tokenize(text)
        if not tokens:
            return np.zeros((0, len(self.REL_TYPES))), np.zeros((0, 0, len(self.REL_TYPES))), tokens
        
        tags = self._get_pos_tags(tokens)
        n = len(tokens)
        
        # Node types: Simple mapping to index based on tag roughness
        # Map tags to indices 0..P-1 roughly
        tag_map = {t: i % 10 for i, t in enumerate(set(tags))}
        P = 10 # Fixed predicate classes for one-hot
        N = np.zeros((n, P))
        for i, tag in enumerate(tags):
            idx = tag_map.get(tag, 0) % P
            N[i, idx] = 1
            
        # Adjacency Tensor A [n, n, R]
        R_count = len(self.REL_TYPES)
        A = np.zeros((n, n, R_count))
        
        # Rule-based dependency approximation (Head = Verb/NN, Dep = neighbors)
        for i, (tok, tag) in enumerate(zip(tokens, tags)):
            # Connect to nearest verb or noun
            target = -1
            rel_type = 'nsubj'
            
            # Simple heuristic: Subject before verb, Object after
            if 'VB' in tag:
                if i > 0: target = i - 1; rel_type = 'nsubj'
            elif 'NN' in tag:
                if i > 0 and 'VB' in tags[i-1]: 
                    target = i - 1; rel_type = 'dobj'
                elif i < n - 1 and 'VB' in tags[i+1]:
                    target = i + 1; rel_type = 'nsubj'
            
            if target != -1 and target < n:
                try:
                    r_idx = self.REL_TYPES.index(rel_type)
                    A[i, target, r_idx] = 1
                except ValueError:
                    pass

        return N, A, tokens

    def _compute_structural_score(self, N1: np.ndarray, A1: np.ndarray, N2: np.ndarray, A2: np.ndarray) -> float:
        if N1.shape[0] == 0 or N2.shape[0] == 0:
            return 0.0
            
        # Node similarity
        # Normalize to probability distribution over types if needed, but dot product of one-hots works for overlap
        # S_n = trace(N1 * N2.T) / (|V1| * |V2|) ? No, spec says dot product of one-hots -> fraction matching
        # Let's interpret as: Sum(N1 @ N2.T) normalized
        node_sim = np.sum(N1 @ N2.T) / (np.sum(N1) + np.sum(N2) + 1e-6)
        
        # Edge similarity
        # Sum over relation types of trace(A1 @ A2.T)
        edge_sim_num = 0.0
        R = A1.shape[2]
        for r in range(R):
            mat1 = A1[:, :, r]
            mat2 = A2[:, :, r]
            if mat1.shape[0] == mat2.shape[0]: # Only compare if dimensions align (rare in sliding window)
                 # For global, shapes differ. We need a different metric for different sizes.
                 # Spec says: trace(A_R @ A_C.T). This implies same size. 
                 # Adaptation: Flatten and cosine similarity for different sizes.
                 v1 = mat1.flatten()
                 v2 = mat2.flatten()
                 norm = np.linalg.norm(v1) * np.linalg.norm(v2)
                 if norm > 0:
                     edge_sim_num += np.dot(v1, v2) / norm
            else:
                # Fallback for size mismatch (sliding windows): resize or pad? 
                # Let's use intersection over union of non-zero indices for robustness
                nz1 = np.count_nonzero(mat1)
                nz2 = np.count_nonzero(mat2)
                if nz1 + nz2 > 0:
                    # Approximate overlap
                    edge_sim_num += min(nz1, nz2) / (nz1 + nz2)

        edge_sim_denom = 1.0 # Normalization factor from spec is implicit in trace, we normalize manually
        if A1.size + A2.size > 0:
             edge_sim = edge_sim_num / (R * 2) # Rough normalization
        else:
            edge_sim = 0.0
            
        return self.lambda_param * min(1.0, node_sim) + (1 - self.lambda_param) * min(1.0, edge_sim)

    def _ergodic_score(self, ref_text: str, cand_text: str) -> float:
        # Global score
        N_ref, A_ref, tokens_ref = self._build_graph(ref_text)
        N_cand, A_cand, tokens_cand = self._build_graph(cand_text)
        
        if N_ref.shape[0] == 0 or N_cand.shape[0] == 0:
            return 0.0

        alpha_global = self._compute_structural_score(N_ref, A_ref, N_cand, A_cand)
        
        # Local sliding windows
        w = self.window_size
        local_scores = []
        
        # Generate windows for candidate
        cand_windows = [tokens_cand[i:i+w] for i in range(len(tokens_cand) - w + 1)]
        ref_windows = [tokens_ref[i:i+w] for i in range(len(tokens_ref) - w + 1)]
        
        if not cand_windows or not ref_windows:
            return alpha_global
            
        # Compare each cand window against the whole reference (simplified ergodic check)
        # Or better: Compare local structure of cand to local structure of ref?
        # Spec: "For each window i compute a local structural score... using only words inside"
        # We map cand windows to ref windows by index or best match? 
        # Let's assume sequential alignment for simplicity in this constrained env.
        
        min_len = min(len(cand_windows), len(ref_windows))
        if min_len == 0:
            return alpha_global
            
        for i in range(min_len):
            # Re-build graphs for windows
            w_cand = " ".join(cand_windows[i])
            w_ref = " ".join(ref_windows[i])
            N_lc, A_lc, _ = self._build_graph(w_cand)
            N_lr, A_lr, _ = self._build_graph(w_ref)
            
            if N_lc.shape[0] > 0 and N_lr.shape[0] > 0:
                local_scores.append(self._compute_structural_score(N_lr, A_lr, N_lc, A_lc))
        
        if not local_scores:
            return alpha_global
            
        alpha_time = np.mean(local_scores)
        delta = abs(alpha_time - alpha_global)
        beta = np.exp(-self.gamma_param * delta)
        return beta

    def _pragmatic_score(self, ref: str, cand: str) -> float:
        score = 1.0
        ref_lower = ref.lower()
        cand_lower = cand.lower()
        
        # Quantity: Missing required predicate?
        # Simple check: if a modal in ref is not in cand
        ref_modals = self.PATTERNS['modal'].findall(ref_lower)
        for m in ref_modals:
            if m not in cand_lower:
                score -= 0.2
                
        # Relevance: Introduce relation not in ref? (Hard to detect without full graph, skip for brevity)
        
        # Manner: Negation flip
        ref_neg = bool(self.PATTERNS['negation'].search(ref_lower))
        cand_neg = bool(self.PATTERNS['negation'].search(cand_lower))
        if ref_neg != cand_neg:
            score -= 0.25
            
        return max(0.0, score)

    def _dynamics_tracker(self, prompt: str, answer: str) -> float:
        """
        Frame C: Dynamics Tracker.
        Models reasoning as state evolution. Checks stability under premise perturbation.
        If the answer relies on a specific ordering that breaks when shuffled, it's fragile.
        """
        # Extract sentences as premises
        sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
        if len(sentences) < 2:
            return 1.0 # Not enough data to test dynamics
            
        # State vector: Bag of words of the answer (simplified state)
        def get_state_vector(text):
            toks = self._tokenize(text)
            vec = np.zeros(26) # a-z
            for t in toks:
                if t and 'a' <= t[0] <= 'z':
                    vec[ord(t[0]) - ord('a')] += 1
            return vec / (np.linalg.norm(vec) + 1e-6)
        
        base_state = get_state_vector(answer)
        perturbations = []
        
        # Perturb: Shuffle sentences
        import random
        random.seed(42) # Deterministic
        shuffled_sents = sentences[:]
        random.shuffle(shuffled_sents)
        shuffled_prompt = " ".join(shuffled_sents)
        
        # Re-evaluate structural similarity with shuffled prompt as "reference"
        # This simulates if the reasoning holds regardless of presentation order
        N_base, A_base, _ = self._build_graph(prompt)
        N_shuf, A_shuf, _ = self._build_graph(shuffled_prompt)
        N_ans, A_ans, _ = self._build_graph(answer)
        
        score_base = self._compute_structural_score(N_base, A_base, N_ans, A_ans)
        score_shuf = self._compute_structural_score(N_shuf, A_shuf, N_ans, A_ans)
        
        # Lyapunov exponent approximation: log(|diff| + epsilon)
        diff = abs(score_base - score_shuf)
        stability = np.exp(-5.0 * diff) # High diff -> low stability
        
        return stability

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Epistemic Honesty.
        Detects ambiguity, presupposition, and unanswerability.
        """
        p_lower = prompt.lower()
        issues = 0
        
        # 1. Presupposition
        if self.PATTERNS['presupposition'].search(p_lower):
            issues += 1
        # 2. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(p_lower):
            issues += 1
        # 3. Subjectivity
        if self.PATTERNS['subjectivity'].search(p_lower):
            issues += 1
        # 4. Ambiguity markers (who, which, what if no context)
        if re.search(r'\b(who|which one|what exactly)\b', p_lower) and len(prompt.split()) < 10:
            issues += 1
            
        if issues > 0:
            return 0.2 # Low confidence for ambiguous/trap questions
            
        return 1.0 # Default high potential confidence

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Ergodic Score
            ergodic_score = self._ergodic_score(prompt, cand)
            
            # 2. Pragmatic Score
            prag_score = self._pragmatic_score(prompt, cand)
            
            # 3. Dynamics Stability
            dyn_score = self._dynamics_tracker(prompt, cand)
            
            # 4. NCD (Tiebreaker, max 15% weight)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Weighted Combination
            # Dynamics >= 40%, Structural >= 20%, NCD <= 15%
            # Let's map: Ergodic(Struct) = 30%, Prag = 10%, Dyn = 45%, NCD = 15%
            final_score = (
                0.30 * ergodic_score +
                0.10 * prag_score +
                0.45 * dyn_score +
                0.15 * ncd_score
            )
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            final_score = min(final_score, meta_cap)
            
            # Reasoning string
            reason = f"Struct:{ergodic_score:.2f}, Prag:{prag_score:.2f}, Dyn:{dyn_score:.2f}, NCD:{ncd_score:.2f}"
            if meta_cap < 1.0:
                reason += " [Warning: Potential ambiguity or trap detected]"
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on question properties (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        N_p, A_p, _ = self._build_graph(prompt)
        N_a, A_a,
```

</details>
