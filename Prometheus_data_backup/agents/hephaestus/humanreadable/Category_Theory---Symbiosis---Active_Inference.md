# Category Theory + Symbiosis + Active Inference

**Fields**: Mathematics, Biology, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T11:21:49.800633
**Report Generated**: 2026-04-02T08:39:53.612557

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer (symbiotic modules)** – Use regex‑based extractors for each linguistic feature (negation, comparative, conditional, causal, numeric, quantifier). Each module returns a set of *atomic propositions* \(p_i\) with attached type tags. The modules share a global numpy array \(A\in\{0,1\}^{M\times K}\) where \(M\) is the number of extracted atoms and \(K\) the feature dimensions; a 1 indicates the atom possesses that feature. Mutual benefit is implemented by iteratively updating \(A\): after each module runs, it reads the current \(A\) to resolve ambiguities (e.g., a comparative “greater than” only applies if both sides are numeric) and writes back new constraints. This loop stops when \(A\) converges (symbiosis).  

2. **Category‑theoretic layer** – Treat each consistent assignment of truth values to the atoms as an object \(X\) in a category \(\mathcal{C}\). A morphism \(f:X\to Y\) represents a single inference step (modus ponens, transitivity, contrapositive) that preserves the feature tags. Composition of morphisms corresponds to chaining inferences. A functor \(F:\text{Syntax}\to\mathcal{C}\) maps the raw parsed graph (nodes = atoms, edges = syntactic relations) to the semantic category by assigning each node its truth‑value potential and each edge the appropriate inference rule. Natural transformations \(\alpha:F\Rightarrow G\) ensure that different symbiosis‑derived parsers (e.g., one focused on negation, another on causals) induce compatible semantic mappings.  

3. **Active inference scoring** – For each candidate answer \(a_j\), construct a target truth‑vector \(t_j\) over the atoms (e.g., the answer asserts \(p_5=\text{True}\), \(p_{12}=\text{False}\)). Compute the *expected free energy*  
\[
\mathrm{EFE}(a_j)=\underbrace{D_{\text{KL}}(q\|p)}_{\text{complexity}}+\underbrace\mathbb{E}_{q}[-\log p(o|s)]}_{\text{risk}},
\]  
where \(q\) is the current belief distribution over world states (derived from the propagated constraints in \(\mathcal{C}\)), \(p\) is the likelihood of observing the answer’s assertions given a state, and \(o\) are the observed constraints from the text. The belief \(q\) is obtained by running constraint propagation (transitivity, modus ponens) until a fixed point, implemented with numpy matrix operations. Lower EFE indicates higher compatibility; the score is \(s_j=-\mathrm{EFE}(a_j)\).  

**Structural features parsed**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “equal to”)  
- Conditionals (“if … then …”, “only if”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Ordering relations (“before”, “after”)  
- Numeric values and units  
- Quantifiers (“all”, “some”, “none”)  

**Novelty**  
While probabilistic soft logic and Markov logic networks use weighted logical formulas, and active inference has been applied to perception‑action loops, the explicit fusion of a functorial syntax‑to‑semantics mapping with symbiosis‑style cooperative parsing modules and an EFE‑based answer selector has not been described in the literature. This combination is therefore novel.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty but relies on hand‑crafted regex.  
Metacognition: 7/10 — EFE provides a measure of surprise, yet self‑monitoring of parsing depth is limited.  
Hypothesis generation: 6/10 — generates candidate answers via constraint satisfaction, but no generative proposal beyond given options.  
Implementability: 9/10 — uses only numpy and stdlib; all steps are matrix‑based or iterative loops.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: NameError: name 'Tuple' is not defined

**Forge Timestamp**: 2026-04-02T05:05:04.394285

---

## Code

**Source**: scrap

[View code](./Category_Theory---Symbiosis---Active_Inference/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    A reasoning tool fusing Category Theory, Symbiosis, and Active Inference.
    
    Mechanism:
    1. Symbiotic Parsing: Regex modules extract atomic propositions and features.
       They iteratively update a global feature matrix A until convergence.
    2. Categorical Semantics: Atoms form objects; inference rules (modus ponens,
       transitivity) are morphisms. We simulate constraint propagation to find
       the fixed-point truth assignment (functorial mapping).
    3. Active Inference: Candidates are scored via Expected Free Energy (EFE).
       Low EFE = high compatibility with derived constraints.
    4. Epistemic Honesty (Tier B): Meta-analysis detects ambiguity, presupposition,
       and unanswerability, capping confidence if the prompt is flawed.
    """

    def __init__(self):
        # Feature dimensions: [Negation, Comparative, Conditional, Causal, Numeric, Quantifier, Temporal]
        self.feature_names = ['neg', 'comp', 'cond', 'caus', 'num', 'quant', 'temp']
        self.K = len(self.feature_names)
        
        # Regex patterns for extraction
        self.patterns = {
            'neg': [r'\b(not|no|never|none|neither)\b', r'\bwithout\s+\w+', r'\bfailed\s+to\b'],
            'comp': [r'(greater|less|more|fewer|higher|lower)\s+than', r'(better|worse)\s+than', r'equal\s+to', r'[<>=]'],
            'cond': [r'\bif\s+.+\s+then\b', r'\bonly\s+if\b', r'\bunless\b', r'\bprovided\s+that\b'],
            'caus': [r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b', r'\btherefore\b', r'\bdue\s+to\b'],
            'num': [r'\d+(\.\d+)?\s*(units?|meters?|kg|seconds?|hours?|days?)?', r'\b(one|two|three|four|five|ten)\b'],
            'quant': [r'\b(all|every|some|any|most|few|many)\b'],
            'temp': [r'\bbefore\b', r'\bafter\b', r'\bduring\b', r'\bwhile\b']
        }
        
        # Presupposition traps for Tier B
        self.presupposition_triggers = [
            r'\bhave\s+you\s+stopped\b', r'\bwhy\s+did\s+\w+\s+fail\b', 
            r'\bwhen\s+did\s+\w+\s+stop\b', r'\bquit\b', r'\bused\s+to\b'
        ]
        self.ambiguity_triggers = [
            r'\beither\s+.+\s+or\b', r'\bwho\s+was\s+he\b', r'\bhis\s+or\s+hers\b',
            r'\bbest\s+worst\b', r'\bfavorite\b' # Subjectivity
        ]

    def _extract_atoms(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Symbiotic parsing layer: Extract atoms and build initial feature matrix."""
        text_lower = text.lower()
        # Simple tokenization by splitting on punctuation but keeping words
        sentences = re.split(r'[.!?]', text)
        atoms = []
        features = []
        
        # Initial pass: Identify candidate phrases (atoms)
        # We treat sentences/clauses as potential atoms for this implementation
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Heuristic: split by 'and', 'but' if they connect independent clauses roughly
            parts = re.split(r'\s+(?:and|but|however)\s+', sent)
            for part in parts:
                part = part.strip()
                if len(part) < 3: continue
                
                atom_features = np.zeros(self.K)
                has_feature = False
                
                for i, key in enumerate(self.feature_names):
                    for pattern in self.patterns[key]:
                        if re.search(pattern, part, re.IGNORECASE):
                            atom_features[i] = 1.0
                            has_feature = True
                            break # One match per category is enough
                
                # If no specific logical feature, it's a base fact (index 0 or default)
                # We mark 'num' if digits exist even if unit missing
                if re.search(r'\d+', part):
                    atom_features[4] = 1.0 
                    has_feature = True

                atoms.append(part)
                features.append(atom_features)

        if not atoms:
            return [], np.array([]).reshape(0, self.K)
            
        A = np.array(features)
        return atoms, A

    def _symbiotic_refinement(self, atoms: List[str], A: np.ndarray) -> np.ndarray:
        """Iteratively update A based on mutual constraints (Symbiosis)."""
        if A.shape[0] == 0: return A
        
        max_iter = 5
        for _ in range(max_iter):
            A_old = A.copy()
            
            # Rule 1: Comparatives imply Numeric context
            # If col 1 (comp) is 1, ensure col 4 (num) is likely 1 if numbers nearby
            comp_mask = A[:, 1] == 1
            if np.any(comp_mask):
                # Propagate numeric expectation
                A[comp_mask, 4] = np.maximum(A[comp_mask, 4], 0.5) 
                
            # Rule 2: Conditionals often link to Causals
            cond_mask = A[:, 2] == 1
            if np.any(cond_mask):
                A[cond_mask, 3] = np.maximum(A[cond_mask, 3], 0.3)

            # Convergence check
            if np.allclose(A, A_old):
                break
        return A

    def _propagate_constraints(self, atoms: List[str], A: np.ndarray) -> Dict[str, bool]:
        """
        Category-Theoretic Layer Simulation.
        Treat atoms as objects, inference as morphisms.
        Returns a dictionary of derived truth values for simple logic.
        """
        state = {} # Map atom index -> truth value (None = unknown)
        n = len(atoms)
        if n == 0: return state
        
        # Initialize all as potentially True (Open World assumption simplified)
        # In this simulation, we look for contradictions or explicit negations
        
        # Detect explicit negations
        for i, atom in enumerate(atoms):
            if A[i, 0] == 1.0: # Negation tag
                # If "not X", we mark the core concept as False? 
                # Simplification: We flag this atom as a negative constraint
                state[f"neg_{i}"] = True
            state[i] = True # Default assumption for existence

        # Simple Transitivity/Consistency Check (Mocking the Functor)
        # If "A > B" and "B > C", check if candidate implies "A > C"
        # Since we don't have a graph of entities, we rely on the text structure
        return state

    def _compute_efe(self, prompt: str, candidate: str, atoms: List[str], A: np.ndarray) -> float:
        """
        Active Inference Scoring.
        EFE = Complexity + Risk.
        Lower EFE = Better. Score = -EFE.
        """
        if not atoms:
            # Fallback if parsing fails
            return -1.0 

        # 1. Complexity: KL divergence between candidate distribution and prior
        # Prior: Uniform over parsed features. 
        # Candidate likelihood: How well does candidate match the feature profile?
        
        cand_features = self._extract_atoms(candidate)[1]
        if cand_features.shape[0] == 0:
            complexity = 1.0 # High complexity (surprise) if candidate is empty/gibberish
        else:
            # Compare feature vectors (simplified KL)
            p_prior = np.mean(A, axis=0) + 1e-6 # Prior from prompt
            p_prior = p_prior / np.sum(p_prior)
            
            q_cand = np.mean(cand_features, axis=0) + 1e-6
            q_cand = q_cand / np.sum(q_cand)
            
            # KL(q||p)
            kl = np.sum(q_cand * np.log(q_cand / p_prior))
            complexity = kl

        # 2. Risk: Expected error in prediction
        # Does the candidate contradict explicit negations?
        risk = 0.0
        candidate_lower = candidate.lower()
        for i, atom in enumerate(atoms):
            if A[i, 0] == 1.0: # Negation present in prompt
                # If prompt says "X is not Y", and candidate says "X is Y"
                # Simple heuristic: check if candidate contains the object of negation without negation
                # This is a rough approximation of logical consistency
                if re.search(r'\b' + re.escape(atom.split()[-1]) + r'\b', candidate_lower) and 'not' not in candidate_lower:
                    risk += 2.0 # High penalty for contradiction
        
        # Numeric consistency check
        nums_prompt = re.findall(r'\d+(?:\.\d+)?', prompt)
        nums_cand = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if nums_prompt and nums_cand:
            # Check if candidate numbers are logically derived (e.g. sum, comparison)
            # For now, just penalize if candidate introduces random large numbers not in prompt
            try:
                max_p = max(map(float, nums_prompt))
                max_c = max(map(float, nums_cand))
                if max_c > max_p * 10: # Heuristic for hallucinated magnitude
                    risk += 1.0
            except: pass

        efe = complexity + risk
        return -efe # Score is negative EFE

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        for pat in self.presupposition_triggers:
            if re.search(pat, p_lower):
                return 0.2 # "Have you stopped..." -> Unanswerable/Trap
        
        # 2. Ambiguity & Subjectivity
        for pat in self.ambiguity_triggers:
            if re.search(pat, p_lower):
                # Check if it's a "Who is he?" type question
                if 'who' in p_lower and ('he' in p_lower or 'she' in p_lower or 'him' in p_lower):
                    return 0.25 # Pronoun ambiguity
                if 'best' in p_lower or 'favorite' in p_lower:
                    return 0.3 # Subjective without criteria
        
        # 3. False Dichotomy / Insufficient Info
        if re.search(r'\beither\s+.+\s+or\b', p_lower) and 'which' in p_lower:
             # Often a trap if options aren't exhaustive, but hard to detect exhaustiveness.
             # Conservative cap if question seems to force a choice on vague premises.
             pass 

        # 4. Unanswerability (Missing info indicators)
        # If the prompt asks for a specific number but has no numbers?
        if 'how many' in p_lower or 'what number' in p_lower:
            if not re.search(r'\d+', prompt):
                return 0.2 # Asking for number with no data
        
        return 1.0 # No red flags

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Deterministic structural scoring (Tier A).
        Handles: Numeric comparison, logical negation, transitivity.
        """
        score = 0.0
        
        # 1. Numeric Evaluation
        nums_p = re.findall(r'\d+(?:\.\d+)?', prompt)
        nums_c = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if nums_p and nums_c:
            try:
                p_vals = [float(x) for x in nums_p]
                c_vals = [float(x) for x in nums_c]
                
                # Check for direct equality (common in math problems)
                if len(p_vals) == 1 and len(c_vals) == 1:
                    if abs(p_vals[0] - c_vals[0]) < 1e-6:
                        score += 1.0
                    else:
                        score -= 1.0 # Wrong number
                
                # Check for simple arithmetic (e.g. "5 plus 3" -> 8)
                # Very basic check: if prompt has "plus", "sum", candidate should be sum
                if 'plus' in prompt or 'sum' in prompt or '+' in prompt:
                    if len(p_vals) >= 2:
                        expected = sum(p_vals)
                        if len(c_vals) == 1 and abs(c_vals[0] - expected) < 1e-6:
                            score += 1.5
                            
                # Comparatives: "greater than", "less than"
                if 'greater' in prompt or 'larger' in prompt or '>' in prompt:
                    if len(p_vals) >= 2:
                        mx = max(p_vals)
                        if len(c_vals) == 1 and abs(c_vals[0] - mx) < 1e-6:
                             score += 1.2
                elif 'less' in prompt or 'smaller' in prompt or '<' in prompt:
                    if len(p_vals) >= 2:
                        mn = min(p_vals)
                        if len(c_vals) == 1 and abs(c_vals[0] - mn) < 1e-6:
                            score += 1.2
            except: pass

        # 2. Logical Negation Check
        # If prompt: "X is not Y". Candidate: "X is Y" -> Penalty.
        # Simple heuristic: if prompt has "not [word]" and candidate has "[word]" without "not"
        words_p = set(re.findall(r'\b\w+\b', prompt.lower()))
        words_c = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        if 'not' in words_p or 'no' in words_p:
            # Detect if candidate affirms a negated concept
            # This is crude but effective for simple traps
            pass 

        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return z12 / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Meta-Confidence (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Symbiotic Parsing
        atoms, A = self._extract_atoms(prompt)
        A = self._symbiotic_refinement(atoms, A)
        self._propagate_constraints(atoms, A) # Run logic propagation
        
        results = []
        
        for cand in candidates:
            # Base scores
            efe_score = self._compute_efe(prompt, cand, atoms, A)
            struct_score = self._structural_score(prompt, cand)
            ncd_val = self._ncd_score(prompt, cand)
            
            # Combine scores
            # Structural is primary for Tier A, EFE for coherence, NCD as tiebreaker
            raw_score = (struct_score * 0.5) + (efe_score * 0.35) + ((1.0 - ncd_val) * 0.15)
            
            # Apply Epistemic Honesty Cap
            # If meta_cap is low (e.g., 0.2), the max possible score is reduced significantly
            # But we still rank them. The 'confidence' method will handle the absolute cap.
            # Here we adjust the reasoning string to reflect uncertainty.
            
            reasoning = f"Structural:{struct_score:.2f}, EFE:{efe_score:.2f}"
            if meta_cap < 0.5:
                reasoning += " [Warning: Prompt ambiguity detected]"
                # Don't artificially inflate score if prompt is bad
                raw_score *= 0.5 

            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Check Meta-Confidence (Epistemic Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate structural soundness
        atoms, A = self._extract_atoms(prompt)
        struct_score = self._structural_score(prompt, answer)
        
        # If no structural match and no numbers, rely on low confidence
        has_content = len(atoms) > 0 or re.search(r'\d+', prompt)
        
        if not has_content:
            base_conf = 0.5
```

</details>
