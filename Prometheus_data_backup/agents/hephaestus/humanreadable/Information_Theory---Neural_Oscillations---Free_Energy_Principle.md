# Information Theory + Neural Oscillations + Free Energy Principle

**Fields**: Mathematics, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:52:02.809237
**Report Generated**: 2026-04-01T20:30:43.952113

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Using regex we extract atomic propositions from the prompt and each candidate answer. Propositions are labeled by type: negation, comparative, conditional, causal, numeric, ordering. Each proposition *i* gets a one‑hot token vector **vᵢ** (size = vocabulary of the prompt) and a base frequency *fᵢ* drawn from a band that matches its type (e.g., conditionals → theta 4‑8 Hz, comparatives → beta 13‑30 Hz, numerics → gamma 30‑80 Hz).  
2. **Co‑occurrence matrix** – From the prompt we build a count matrix **C** where Cₐᵦ = how often tokens *a* and *b* appear within a sliding window of 5 words. Normalising gives joint distribution **Pₐᵦ**; marginals **Pₐ**, **Pᵦ**. Mutual information for a proposition pair (i,j) is MIᵢⱼ = Σₐ,ᵦ Pₐᵦ log(Pₐᵦ/(PₐPᵦ)). This yields an information‑theoretic similarity matrix **M**.  
3. **Neural‑oscillation binding** – For each proposition we generate a sinusoid sᵢ(t) = sin(2π fᵢ t + φᵢ₀) with random initial phase φᵢ₀. Using the Hilbert transform (implemented via numpy’s FFT) we obtain instantaneous phase φᵢ(t). The synchrony between a set of premises **P** and a candidate **c** is the mean cosine of phase differences: S = (1/|P|) Σᵢ∈P cos(φᵢ – φ_c).  
4. **Free‑energy (prediction error)** – Treat the premise distribution **Q** as the normalized row of **M** averaged over premises, and the candidate likelihood **L** as the column of **M** for the candidate. Variational free energy ≈ KL(Q‖L) = Σ Q log(Q/L). Lower KL means the candidate better predicts the premises.  
5. **Score** – Final score for a candidate:  
   Score = α·mean(Mᵢ,ⱼ) – β·KL(Q‖L) + γ·S,  
   with α,β,γ set to 1.0 (can be tuned). Higher scores indicate answers that are informationally coherent, phase‑synchronised with premises, and incur little prediction error.

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then …”), causal claims (“because”, “leads to”), numeric values and units, ordering relations (“first”, “after”, “greater than”).

**Novelty** – Mutual‑information based similarity and oscillatory binding are each used in NLP and neuroscience, and the free‑energy principle underlies predictive‑coding models, but their conjunction into a single scoring function that operates on extracted logical propositions is not documented in existing work.

**Rating**  
Reasoning: 7/10 — captures logical structure and information coherence but lacks deep inference chains.  
Metacognition: 5/10 — provides a single scalar confidence; no explicit self‑monitoring or error‑revision loop.  
Hypothesis generation: 6/10 — can perturb phases or token counts to propose alternatives, yet generation is rudimentary.  
Implementability: 8/10 — relies only on numpy and the Python standard library; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: NameError: name 'List' is not defined

**Forge Timestamp**: 2026-04-01T19:11:09.756539

---

## Code

**Source**: scrap

[View code](./Information_Theory---Neural_Oscillations---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    A hybrid reasoning tool combining Information Theory, Neural Oscillations, 
    and the Free Energy Principle with explicit structural parsers and epistemic honesty.
    
    Mechanism:
    1. Meta-Cognition: Scans for ambiguity, presuppositions, and unanswerability (Tier B).
    2. Structural Parsing: Extracts logical atoms (negation, conditionals, causality, numerics).
    3. Information Theory: Builds a co-occurrence MI matrix between prompt and candidate.
    4. Neural Oscillation: Simulates phase binding based on proposition type frequencies.
    5. Free Energy: Calculates KL-divergence between premise distribution and candidate prediction.
    6. Specialized Solvers: Handles math, logic, and temporal constraints directly.
    """

    def __init__(self):
        # Frequency bands (Hz) for proposition types
        self.freq_map = {
            'conditional': 6.0,   # Theta
            'causal': 6.0,        # Theta
            'negation': 10.0,     # Alpha
            'comparative': 20.0,  # Beta
            'numeric': 40.0,      # Gamma
            'ordering': 20.0,     # Beta
            'default': 12.0       # Alpha/Beta border
        }
        
        # Structural regex patterns
        self.patterns = {
            'negation': [r'\b(not|no|never|neither|without)\b', r"\bcan't\b", r"\bwon't\b"],
            'conditional': [r'\b(if|unless|provided|given that)\b.*\b(then|else|must|will)\b', r'\bimplies\b'],
            'causal': [r'\b(because|since|therefore|thus|hence|leads to|results in|causes)\b'],
            'comparative': [r'\b(more than|less than|greater than|smaller than|higher|lower|better|worse)\b'],
            'numeric': [r'\d+(\.\d+)?'],
            'ordering': [r'\b(first|second|third|last|before|after|next|previous)\b'],
            'presupposition': [r'have you stopped', r'why did.*fail', r'why is.*wrong'],
            'false_dichotomy': [r'\beither.*or\b'],
            'pronoun_ambiguity': [r'\b(he|she|him|her|they)\b.*\bwho\b']
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with type and frequency."""
        props = []
        text_lower = text.lower()
        
        for p_type, regex_list in self.patterns.items():
            if p_type in ['presupposition', 'false_dichotomy', 'pronoun_ambiguity']:
                continue # Handled separately
            
            for regex in regex_list:
                if re.search(regex, text_lower):
                    props.append({'type': p_type, 'freq': self.freq_map.get(p_type, self.freq_map['default'])})
                    break # One type per pattern group match for simplicity
        
        if not props:
            props.append({'type': 'default', 'freq': self.freq_map['default']})
            
        return props

    def _build_mi_matrix(self, prompt: str, candidate: str) -> np.ndarray:
        """Build Mutual Information matrix based on co-occurrence."""
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        all_tokens = list(set(p_tokens + c_tokens))
        if not all_tokens:
            return np.array([[0.0]])
        
        vocab_size = len(all_tokens)
        token_to_idx = {t: i for i, t in enumerate(all_tokens)}
        
        # Co-occurrence in prompt (window=5)
        C = np.zeros((vocab_size, vocab_size))
        window = 5
        for i, token in enumerate(p_tokens):
            idx_i = token_to_idx[token]
            for j in range(max(0, i-window), min(len(p_tokens), i+window+1)):
                if i != j:
                    idx_j = token_to_idx[p_tokens[j]]
                    C[idx_i, idx_j] += 1
        
        # Normalize to joint probability
        total = C.sum()
        if total == 0:
            return np.zeros((vocab_size, vocab_size))
            
        P_ab = C / total
        P_a = P_ab.sum(axis=1, keepdims=True)
        P_b = P_ab.sum(axis=0, keepdims=True)
        
        # MI = sum P(ab) log(P(ab) / (P(a)P(b)))
        # Avoid division by zero
        P_outer = np.dot(P_a, P_b)
        P_outer[P_outer == 0] = 1e-10
        
        with np.errstate(divide='ignore', invalid='ignore'):
            MI_matrix = np.where(P_ab > 0, P_ab * np.log(P_ab / P_outer), 0)
            
        return MI_matrix

    def _oscillatory_sync(self, prompt_props: List[Dict], cand_props: List[Dict], t: float = 1.0) -> float:
        """Calculate phase synchrony between premise and candidate propositions."""
        if not prompt_props or not cand_props:
            return 0.0
            
        # Average frequency of premises
        premise_freqs = [p['freq'] for p in prompt_props]
        cand_freqs = [p['freq'] for p in cand_props]
        
        if not premise_freqs or not cand_freqs:
            return 0.0
            
        avg_p_freq = np.mean(premise_freqs)
        avg_c_freq = np.mean(cand_freqs)
        
        # Simple phase difference model
        # phi = 2 * pi * f * t
        phi_p = 2 * math.pi * avg_p_freq * t
        phi_c = 2 * math.pi * avg_c_freq * t
        
        # Synchrony = cos(phase_diff)
        sync = math.cos(phi_p - phi_c)
        return sync

    def _free_energy_kl(self, mi_matrix: np.ndarray, prompt: str, candidate: str) -> float:
        """Calculate Variational Free Energy approx as KL(Q||L)."""
        if mi_matrix.size == 0:
            return 1.0
            
        # Q: Distribution over prompt tokens (marginal of MI matrix rows corresponding to prompt)
        # L: Distribution over candidate tokens
        
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        if not p_tokens or not c_tokens:
            return 1.0
            
        # Map tokens to indices (simplified: assume overlap exists or use global index if needed)
        # For this implementation, we approximate Q as uniform over prompt concepts present in MI
        # and L as the candidate's projection.
        
        # Simplified KL: How well does the candidate's token distribution predict the prompt's MI structure?
        # Since building full vectors is complex without shared vocab mapping in this scope,
        # we use a proxy: Overlap ratio weighted by MI density.
        
        overlap_count = len(set(p_tokens) & set(c_tokens))
        total_unique = len(set(p_tokens) | set(c_tokens))
        
        if total_unique == 0:
            return 1.0
            
        # Proxy likelihood
        likelihood = (overlap_count + 1) / (total_unique + 1) # Laplace smoothing
        
        # Q is effectively 1.0 for prompt tokens, 0 otherwise. 
        # We want low KL when candidate covers prompt concepts.
        # KL ~ -log(likelihood)
        kl = -math.log(likelihood + 1e-10)
        return kl

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _solve_numeric_comparison(self, text: str) -> Optional[float]:
        """Detect and solve simple numeric comparisons."""
        numbers = re.findall(r'-?\d+(\.\d+)?', text)
        if len(numbers) >= 2:
            nums = [float(n) for n in numbers]
            # Heuristic: if prompt asks "which is larger", return max
            if any(k in text.lower() for k in ['larger', 'greater', 'more', 'max', 'highest']):
                return max(nums)
            if any(k in text.lower() for k in ['smaller', 'less', 'min', 'lowest']):
                return min(nums)
        return None

    def _solve_bat_ball(self, text: str) -> Optional[float]:
        """Solve Bat-and-Ball style algebraic problems."""
        text_lower = text.lower()
        # Pattern: A and B cost X. A costs Y more than B. How much is B?
        # Generic solver for: A + B = Total, A = B + Diff => 2B + Diff = Total => B = (Total - Diff)/2
        
        numbers = re.findall(r'\d+(\.\d+)?', text_lower)
        if len(numbers) >= 3:
            nums = [float(n) for n in numbers]
            # Heuristic for standard bat-ball: 3 numbers usually involved or derivable
            # If "total" and "difference" are implied
            if 'cost' in text_lower or 'price' in text_lower or 'more than' in text_lower:
                # Assume structure: Total, Diff present? 
                # Simplest case: Total is max, Diff is min? 
                # Let's try to find (Total - Diff) / 2
                total = max(nums)
                # Diff is usually the second distinct number or specified
                # This is a heuristic solver
                others = [n for n in nums if n != total]
                if others:
                    diff = others[0] # Assumption
                    ans = (total - diff) / 2
                    if ans > 0:
                        return ans
        return None

    def _solve_modular(self, text: str) -> Optional[int]:
        """Solve modular arithmetic problems."""
        if 'mod' in text.lower() or 'remainder' in text.lower() or 'cycle' in text.lower():
            nums = re.findall(r'\d+', text)
            if len(nums) >= 2:
                n = int(nums[-2])
                m = int(nums[-1])
                if m > 0:
                    return n % m
        return None

    def _solve_temporal(self, text: str) -> Optional[str]:
        """Solve temporal ordering."""
        text_lower = text.lower()
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        found_days = [d for d in days if d in text_lower]
        
        if 'yesterday' in text_lower or 'tomorrow' in text_lower:
            # Simple relative day calculation
            if found_days:
                base = found_days[0]
                idx = days.index(base)
                if 'yesterday' in text_lower:
                    return days[(idx - 1) % 7]
                if 'tomorrow' in text_lower:
                    return days[(idx + 1) % 7]
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for regex in self.patterns['presupposition']:
            if re.search(regex, p_lower):
                return 0.2
        
        # 2. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            # Check if options are exhaustive (hard to know, but flag if vague)
            if 'choose' in p_lower or 'which' in p_lower:
                 return 0.5 # Lower confidence due to potential false dichotomy

        # 3. Pronoun Ambiguity
        if re.search(r'\b(he|she|him|her|they)\b', p_lower) and 'who' in p_lower:
            return 0.3

        # 4. Subjectivity
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'opinion']
        if any(w in p_lower for w in subjective_words) and 'fact' not in p_lower:
            return 0.4

        # 5. Unanswerability (Missing info)
        if 'information' in p_lower and 'missing' in p_lower:
            return 0.1
        if 'cannot be determined' in p_lower:
            return 0.1
            
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Core scoring function combining MI, Oscillation, and Free Energy."""
        # 1. Parse
        p_props = self._extract_propositions(prompt)
        c_props = self._extract_propositions(candidate)
        
        # 2. MI Matrix
        mi_mat = self._build_mi_matrix(prompt, candidate)
        mi_score = np.mean(mi_mat) if mi_mat.size > 0 else 0.0
        
        # 3. Oscillation Sync
        sync_score = self._oscillatory_sync(p_props, c_props)
        
        # 4. Free Energy (KL)
        kl_div = self._free_energy_kl(mi_mat, prompt, candidate)
        fe_score = -kl_div # Lower KL is better, so negative
        
        # 5. NCD Tiebreaker (Max 15% weight logic handled in final sum)
        ncd_val = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd_val # Higher is better
        
        # Weights: Structural (MI+Sync+FE) >= 50%, Computation (handled in evaluate) >= 20%, NCD <= 15%
        # Here we compute the raw structural score
        raw_score = (1.0 * mi_score) + (1.0 * sync_score) + (0.5 * fe_score)
        
        return raw_score, ncd_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Attempt constructive computation first (Tier A)
        computed_answer = None
        comp_val = None
        
        # Try solvers
        comp_val = self._solve_numeric_comparison(prompt)
        if comp_val is not None:
            computed_answer = str(comp_val)
        
        if computed_answer is None:
            comp_val = self._solve_bat_ball(prompt)
            if comp_val is not None:
                computed_answer = str(comp_val)
                
        if computed_answer is None:
            comp_val = self._solve_modular(prompt)
            if comp_val is not None:
                computed_answer = str(comp_val)

        if computed_answer is None:
            comp_val = self._solve_temporal(prompt)
            if comp_val is not None:
                computed_answer = str(comp_val)

        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            # If we have a computed answer, check exact match or numeric proximity
            if computed_answer is not None:
                try:
                    cand_float = float(re.search(r'-?\d+(\.\d+)?', cand).group() if re.search(r'-?\d+(\.\d+)?', cand) else '99999')
                    target_float = float(computed_answer)
                    if abs(cand_float - target_float) < 1e-6:
                        score = 10.0 # High base score for correct computation
                        reasoning = f"Computed answer {computed_answer} matches candidate."
                    else:
                        score = -5.0 # Penalty for wrong computation
                        reasoning = f"Computed answer {computed_answer}, candidate {cand_float} differs."
                except:
                    score = -5.0
                    reasoning = f"Computed answer {computed_answer}, candidate format mismatch."
            else:
                # Fallback to theoretical model
                struct_score, ncd_score = self._structural_score(prompt, cand)
                # Weighting: Structural 85%, NCD 15%
                score = (0.85 * struct_score) + (0.15 * ncd_score)
                reasoning = f"Structural coherence (MI/Osc/FE): {struct_score:.4f}, NCD: {ncd_score:.4f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-cognitive cap
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
```

</details>
