# Neural Plasticity + Free Energy Principle + Proof Theory

**Fields**: Biology, Theoretical Neuroscience, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:35:59.111593
**Report Generated**: 2026-04-02T08:39:54.354545

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions \(p_i\) from the prompt and each candidate answer. Detect logical connectives: negation (“not”), conjunction (“and”), disjunction (“or”), conditional (“if … then”), causal (“because”, “leads to”), comparatives (“>”, “<”, “more than”), and numeric literals. Store each proposition as an index \(i\) in a list \(props\).  
2. **Graph construction** – Build a weighted adjacency matrix \(W\in\mathbb{R}^{N\times N}\) (numpy array) where \(W_{j,i}\) encodes the strength of an inference rule *if \(p_i\) then \(p_j\)*. For each extracted conditional or causal clause, set \(W_{j,i}=w_0\) (e.g., 0.5). Symmetric weights for conjunction/disjunction are added as needed.  
3. **Belief vector** – Initialize a belief vector \(b\in[0,1]^N\) (numpy) with observed truth values from the prompt: 1 for propositions directly asserted, 0 for negated assertions, 0.5 for unknowns.  
4. **Free‑energy minimization (predictive coding loop)** – Repeat for \(T\) iterations:  
   - **Prediction**: \(\hat b = \sigma(W^\top b)\) where \(\sigma\) is the logistic sigmoid (numpy).  
   - **Prediction error**: \(\epsilon = b - \hat b\).  
   - **Variational free energy** (approximated): \(F = \frac12\|\epsilon\|^2\).  
   - **Belief update (Hebbian plasticity)**: \(b \leftarrow b + \eta_b\,\epsilon\odot(1-b)\odot b\) (gradient descent on \(F\)).  
   - **Weight update (Hebbian + pruning)**: \(W \leftarrow W + \eta_W\,(b b^\top) - \lambda W\) followed by thresholding: set \(|W_{ij}|<\tau\) to 0 (cut‑elimination/synaptic pruning).  
   - Renormalize rows of \(W\) to keep inference strengths bounded.  
5. **Scoring** – After convergence, compute the free energy of a candidate answer \(c\) as the sum of squared errors for its propositions:  
   \[
   \text{score}(c) = -\sum_{i\in c} \epsilon_i^2
   \]  
   Higher (less negative) scores indicate lower free energy, i.e., better fit to the prompt’s implicit model.

**Structural features parsed** – atomic propositions, negations, conjunction/disjunction, conditionals, causal claims, comparatives, ordering cues (“before”, “after”), numeric values and units, and quantifiers (“all”, “some”).

**Novelty** – The scheme merges three strands: (i) proof‑theoretic forward chaining via weighted inference rules (cut elimination), (ii) free‑energy minimization as a principled belief‑updating objective (predictive coding), and (iii) Hebbian synaptic plasticity with pruning to shape those rules. While neural‑symbolic systems (e.g., Neural Theorem Provers) combine learning and reasoning, they typically use gradient‑based loss on neural nets rather than explicit variational free energy and biologically‑inspired weight updates. Hence the combination is novel in its algorithmic formulation, though it resides in the broader neuro‑symbolic literature.

**Ratings**  
Reasoning: 7/10 — captures logical structure and propagates constraints, but limited to propositional Horn‑like rules.  
Metacognition: 5/10 — monitors prediction error yet lacks higher‑order self‑assessment of its own uncertainty.  
Hypothesis generation: 6/10 — belief updates can spawn new provisional propositions via weight growth, though not guided by exploratory search.  
Implementability: 8/10 — relies solely on numpy arrays and regex; all operations are straightforward and deterministic.

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
**Reason**: validation:runtime_error: AttributeError: 'NoneType' object has no attribute 'strip'

**Forge Timestamp**: 2026-04-02T08:01:38.921199

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Free_Energy_Principle---Proof_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib


class ReasoningTool:
    """
    Combines Neural Plasticity, Free Energy Principle, and Proof Theory.
    
    Mechanism:
    1. Extract atomic propositions from text using regex
    2. Build weighted inference graph from logical connectives
    3. Minimize variational free energy via predictive coding
    4. Apply Hebbian plasticity with synaptic pruning (cut-elimination)
    5. Score candidates by prediction error (lower free energy = better fit)
    6. Meta-confidence layer detects ambiguous/unanswerable questions
    """
    
    def __init__(self):
        self.eta_b = 0.1  # belief learning rate
        self.eta_W = 0.05  # weight learning rate
        self.lambda_prune = 0.01  # pruning rate
        self.tau = 0.05  # pruning threshold
        self.T = 15  # iterations
        self.w0 = 0.5  # initial inference weight
        
    def _extract_propositions(self, text):
        """Extract atomic propositions and assign indices."""
        text = text.lower()
        # Split on logical connectives but keep the structure
        chunks = re.split(r'\b(and|or|but|because|if|then|not|never|always|therefore|thus|hence)\b|[.!?;]', text)
        props = []
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) > 3 and chunk not in {'and', 'or', 'but', 'because', 'if', 'then', 'not', 'never', 'always', 'therefore', 'thus', 'hence'}:
                props.append(chunk)
        return list(set(props)) if props else [text.strip()]
    
    def _build_inference_graph(self, text, props):
        """Build weighted adjacency matrix from logical structure."""
        N = len(props)
        W = np.zeros((N, N))
        text = text.lower()
        
        # Extract conditionals: "if X then Y"
        conditionals = re.findall(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text)
        for antecedent, consequent in conditionals:
            i = self._find_prop_index(antecedent, props)
            j = self._find_prop_index(consequent, props)
            if i >= 0 and j >= 0:
                W[j, i] = self.w0
        
        # Extract causal: "X because Y" or "X leads to Y"
        causals = re.findall(r'(.+?)\s+(?:because|leads to|causes|results in)\s+(.+?)(?:\.|$)', text)
        for effect, cause in causals:
            i = self._find_prop_index(cause, props)
            j = self._find_prop_index(effect, props)
            if i >= 0 and j >= 0:
                W[j, i] = self.w0
        
        # Conjunctions create bidirectional weak links
        conjunctions = re.findall(r'(.+?)\s+and\s+(.+?)(?:\.|$)', text)
        for p1, p2 in conjunctions:
            i = self._find_prop_index(p1, props)
            j = self._find_prop_index(p2, props)
            if i >= 0 and j >= 0:
                W[i, j] = W[j, i] = self.w0 * 0.3
        
        return W
    
    def _find_prop_index(self, text, props):
        """Find best matching proposition index."""
        text = text.strip().lower()
        for i, prop in enumerate(props):
            if text in prop or prop in text:
                return i
        return -1
    
    def _init_beliefs(self, text, props):
        """Initialize belief vector from observed assertions."""
        b = np.ones(len(props)) * 0.5
        text = text.lower()
        
        for i, prop in enumerate(props):
            # Check for negation
            if re.search(r'\b(?:not|never|no)\b.*' + re.escape(prop[:20]), text):
                b[i] = 0.0
            elif prop in text:
                b[i] = 1.0
        
        return b
    
    def _free_energy_minimize(self, W, b):
        """Run predictive coding loop with Hebbian plasticity."""
        for _ in range(self.T):
            # Prediction
            b_hat = 1.0 / (1.0 + np.exp(-W.T @ b))
            
            # Prediction error
            eps = b - b_hat
            
            # Belief update (gradient descent on free energy)
            b += self.eta_b * eps * (1 - b) * b
            b = np.clip(b, 0, 1)
            
            # Weight update (Hebbian + regularization)
            W += self.eta_W * np.outer(b, b) - self.lambda_prune * W
            
            # Synaptic pruning (cut-elimination)
            W[np.abs(W) < self.tau] = 0
            
            # Renormalize
            row_sums = np.sum(np.abs(W), axis=1, keepdims=True)
            W = np.where(row_sums > 0, W / (row_sums + 1e-8), W)
        
        return W, b, eps
    
    def _meta_confidence(self, prompt):
        """Detect ambiguous/unanswerable questions (Tier B judgment)."""
        prompt_lower = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)\b', prompt_lower):
            return 0.2
        
        # 2. Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.+\ba\b', prompt_lower):
            return 0.25
        
        # 3. Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # 4. False dichotomy: "either A or B"
        if re.search(r'\beither\b.+\bor\b', prompt_lower) and '?' in prompt:
            return 0.25
        
        # 5. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|most important)\b', prompt_lower):
            if not re.search(r'\b(because|criteria|measure|metric)\b', prompt_lower):
                return 0.25
        
        # 6. Unanswerable: "not enough information"
        if re.search(r'\b(cannot be determined|not enough|insufficient|unknown)\b', prompt_lower):
            return 0.2
        
        return 1.0  # No issues detected
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by free energy fit."""
        meta_conf = self._meta_confidence(prompt)
        
        # Extract propositions from prompt
        props = self._extract_propositions(prompt)
        if len(props) == 0:
            props = [prompt]
        
        # Build inference graph
        W = self._build_inference_graph(prompt, props)
        b = self._init_beliefs(prompt, props)
        
        # Minimize free energy
        W_final, b_final, eps_final = self._free_energy_minimize(W.copy(), b.copy())
        
        results = []
        for cand in candidates:
            # Extract propositions from candidate
            cand_props = self._extract_propositions(cand)
            
            # Score by prediction error on candidate propositions
            score = 0.0
            matched = 0
            for cp in cand_props:
                idx = self._find_prop_index(cp, props)
                if idx >= 0:
                    score -= eps_final[idx]**2
                    matched += 1
            
            # Structural bonus: check numeric comparisons
            struct_score = self._structural_eval(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            final_score = 0.5 * score + 0.35 * struct_score + 0.15 * ncd_score
            
            reasoning = f"Free-energy: {score:.3f}, Structural: {struct_score:.3f}, NCD: {ncd_score:.3f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _structural_eval(self, prompt, answer):
        """Deterministic structural parsing for Tier A accuracy."""
        score = 0.0
        p_lower, a_lower = prompt.lower(), answer.lower()
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        if nums_p and nums_a:
            if '>' in prompt or 'greater' in p_lower or 'more than' in p_lower:
                if len(nums_a) > 0 and len(nums_p) >= 2:
                    if float(nums_a[0]) > float(nums_p[0]):
                        score += 1.0
            elif '<' in prompt or 'less' in p_lower or 'fewer' in p_lower:
                if len(nums_a) > 0 and len(nums_p) >= 2:
                    if float(nums_a[0]) < float(nums_p[0]):
                        score += 1.0
        
        # Negation handling
        if re.search(r'\b(not|never|no)\b', p_lower):
            if re.search(r'\b(not|never|no|false)\b', a_lower):
                score += 0.5
        
        # Direct answer match
        if 'yes' in p_lower and 'yes' in a_lower:
            score += 0.3
        elif 'no' in p_lower and 'no' in a_lower:
            score += 0.3
        
        return score
    
    def confidence(self, prompt, answer):
        """Return calibrated confidence 0-1."""
        # First check meta-confidence on the question itself
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.3:
            return meta_conf  # Cap at low confidence for ambiguous questions
        
        # Extract and process
        props = self._extract_propositions(prompt)
        if len(props) == 0:
            return 0.25  # Unknown structure
        
        W = self._build_inference_graph(prompt, props)
        b = self._init_beliefs(prompt, props)
        W_final, b_final, eps_final = self._free_energy_minimize(W.copy(), b.copy())
        
        # Score the answer
        ans_props = self._extract_propositions(answer)
        errors = []
        for ap in ans_props:
            idx = self._find_prop_index(ap, props)
            if idx >= 0:
                errors.append(eps_final[idx]**2)
        
        if not errors:
            # No match found - check structural
            struct_score = self._structural_eval(prompt, answer)
            if struct_score > 0.5:
                return min(0.85 * meta_conf, 0.85)  # Never return > 0.9 unless definitive
            return 0.3 * meta_conf
        
        # Convert error to confidence
        avg_error = np.mean(errors)
        conf = 1.0 / (1.0 + 5 * avg_error)  # Sigmoid-like
        
        # Apply meta-confidence cap and never exceed 0.9
        return min(conf * meta_conf, 0.9)
```

</details>
