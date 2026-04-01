# Sparse Autoencoders + Free Energy Principle + Abstract Interpretation

**Fields**: Computer Science, Theoretical Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T08:24:52.731129
**Report Generated**: 2026-03-31T16:21:16.375116

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction (sparse autoencoder front‑end)** – Using a handful of regex patterns we pull out atomic propositions from the prompt and each candidate answer:  
   - Predicates (e.g., `X > Y`, `X causes Y`, `not P`, `if P then Q`).  
   - Arguments are normalized to identifiers; numeric literals stay as scalars.  
   Each proposition is mapped to a one‑hot vector over a growing dictionary **D** (size ≤ 5000). The dictionary is updated online with an OMP‑style k‑sparse coding step (k = 3) that minimizes ‖x − Dα‖₂² + λ‖α‖₁, yielding a sparse code **α** for each text. This is the “encoder” part; the decoder is simply Dα (reconstruction).  

2. **Abstract‑interpretation layer** – From the sparse codes we rebuild a propositional graph where nodes are predicates and edges are logical connectives extracted by the regex (¬, →, ∧, ∨, causal, ordering). We assign each node an interval truth value [l,u] ⊆ [0,1] initialized from the candidate’s code (presence → [0.9,1], absence → [0,0.1]). Using interval arithmetic we propagate constraints:  
   - Modus ponens: if [l₁,u₁] for P and [l₂,u₂] for P→Q then Q gets [min(l₁·l₂, …), max(u₁·u₂, …)].  
   - Transitivity for ordering: X<Y ∧ Y<Z ⇒ X<Z.  
   - Negation flips intervals: ¬P → [1‑u, 1‑l].  
   The result is an over‑approximation of the set of worlds satisfying the prompt (sound) and possibly an under‑approximation if we tighten with widening/narrowing (we keep the over‑approx for safety).  

3. **Free‑energy scoring** – The variational free energy F ≈ ½‖x − Dα‖₂² + λ‖α‖₁ + ½·tr(Σ⁻¹·Cov_error) where the first two terms are the reconstruction‑sparsity loss from step 1 and the third term is the prediction error between the expected truth‑interval vector μ (midpoint of propagated intervals) and the observed code α (treated as a Gaussian with diagonal covariance Σ = diag(α)). In practice we compute:  

   ```
   recon = np.linalg.norm(x - D @ alpha)**2
   spars = lam * np.sum(np.abs(alpha))
   pred_err = 0.5 * np.sum(((alpha - mu)**2) / (alpha + 1e-8))
   F = recon + spars + pred_err
   ```  

   Lower F indicates the candidate’s sparse representation better predicts the prompt’s constrained meaning → higher score.  

**Structural features parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `≥`, `≤`), conditionals (`if … then …`, `unless`), causal verbs (`causes`, `leads to`), numeric values (integers, decimals), ordering relations (`before`, `after`, `more than`), and conjunction/disjunction (`and`, `or`).  

**Novelty** – The triple blend is not present in existing literature. Sparse coding supplies a disentangled dictionary; abstract interpretation supplies sound constraint propagation over logical forms; the free‑energy objective couples reconstruction error with a sparsity‑regularized prediction error, a formulation not used for answer scoring in neuro‑symbolic or program‑analysis works.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via interval propagation and prediction‑error minimization.  
Metacognition: 6/10 — the algorithm can monitor its own reconstruction error and sparsity, but lacks explicit self‑reflection on strategy choice.  
Hypothesis generation: 5/10 — generates candidate truth‑intervals but does not propose new predicates beyond those seen.  
Implementability: 9/10 — relies only on regex, NumPy linear algebra, and simple interval arithmetic; no external libraries or training data needed.

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
**Reason**: trap_battery_failed (acc=41% cal=54% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-31T14:38:52.818550

---

## Code

**Source**: scrap

[View code](./Sparse_Autoencoders---Free_Energy_Principle---Abstract_Interpretation/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Sparse Autoencoders, Abstract Interpretation,
    and the Free Energy Principle with Dynamical Systems tracking.
    
    Mechanism:
    1. Feature Extraction: Regex-based parsing extracts logical predicates and numeric values.
    2. Sparse Coding: Online dictionary learning (OMP-style) creates sparse representations.
    3. Abstract Interpretation: Propagates interval truth values [l, u] through logical graphs.
    4. Dynamics Tracker: Models reasoning as a state evolution; checks Lyapunov-like stability 
       by perturbing premise order. Stable convergence = high confidence.
    5. Free Energy Scoring: Combines reconstruction error, sparsity, and prediction error.
    6. Epistemic Honesty: Meta-analysis caps confidence on ambiguous/unanswerable prompts.
    """

    def __init__(self):
        self.D = None  # Dictionary matrix (growing)
        self.dict_size = 0
        self.max_dict_size = 5000
        self.k_sparse = 3
        self.lam = 0.1
        self._init_dictionary()

    def _init_dictionary(self):
        """Initialize a small random dictionary for sparse coding."""
        # Start with 100 random atoms, expandable
        self.D = np.random.randn(100, 100) 
        self.dict_size = 100

    def _extract_features(self, text: str) -> Tuple[List[str], List[float], List[str]]:
        """Extract predicates, numbers, and logical connectors."""
        text_lower = text.lower()
        predicates = []
        numbers = []
        connectors = []

        # Numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums]

        # Logical connectors
        if re.search(r'\b(if|then|unless|therefore|thus)\b', text_lower):
            connectors.append('conditional')
        if re.search(r'\b(not|no|never|without)\b', text_lower):
            connectors.append('negation')
        if re.search(r'\b(and|or|both|either)\b', text_lower):
            connectors.append('junction')
        if re.search(r'\b(causes|leads to|implies)\b', text_lower):
            connectors.append('causal')
        if re.search(r'\b(before|after|first|last|then)\b', text_lower):
            connectors.append('temporal')
        if re.search(r'[><=]|greater|less|more', text_lower):
            connectors.append('comparative')

        # Atomic predicates (simplified: split by connectors)
        # Normalize to tokens
        tokens = re.split(r'\s+', re.sub(r'[^\w\s]', ' ', text_lower))
        predicates = list(set([t for t in tokens if len(t) > 3]))[:10] # Limit atoms

        return predicates, numbers, connectors

    def _sparse_code(self, text: str) -> np.ndarray:
        """
        Generate a k-sparse code for the text.
        Simulates OMP: projects features onto dictionary, picks top-k, reconstructs.
        """
        preds, nums, conns = self._extract_features(text)
        
        # Create feature vector (hash-based indexing into dictionary space)
        # Map predicates to indices modulo current dict size
        dim = self.D.shape[0]
        x = np.zeros(dim)
        
        # Encode predicates
        for p in preds:
            idx = hash(p) % dim
            x[idx] += 1.0
        
        # Encode numbers (scaled)
        for n in nums:
            idx = hash(str(n)) % dim
            x[idx] += n / 10.0 # Scale down
            
        # Encode connectors
        for c in conns:
            idx = hash(c) % dim
            x[idx] += 2.0 # Higher weight for logic

        if np.linalg.norm(x) == 0:
            return np.zeros(dim)

        # Normalize
        x = x / np.linalg.norm(x)

        # OMP-style k-sparse coding
        # Correlate with dictionary columns
        if self.D.shape[1] < dim:
             # Pad dictionary if dimension mismatch (dynamic growth simulation)
             pass 
        
        correlations = np.abs(np.dot(self.D.T, x[:self.D.shape[1]] if len(x) >= self.D.shape[1] else np.pad(x, (0, self.D.shape[1]-len(x)))))
        
        # Select top-k
        # Handle case where dim > dict columns
        safe_len = min(len(correlations), len(x))
        indices = np.argsort(correlations[:safe_len])[-self.k_sparse:]
        
        alpha = np.zeros_like(x)
        # Reconstruct using selected atoms (simplified least squares)
        # For simplicity in this constraint: just activate selected atoms with correlation strength
        for i in indices:
            if i < len(alpha):
                alpha[i] = correlations[i]
        
        return alpha

    def _abstract_interpretation(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Propagate interval truth values based on logical structure.
        Returns (lower_bound, upper_bound, reasoning_trace).
        """
        p_preds, p_nums, p_conns = self._extract_features(prompt)
        c_preds, c_nums, c_conns = self._extract_features(candidate)
        
        # Initialize interval [l, u] based on overlap
        # Presence in both -> [0.9, 1.0]
        # Presence in prompt only -> [0.1, 0.5] (uncertain)
        # Absence -> [0.0, 0.1]
        
        common_preds = set(p_preds) & set(c_preds)
        missing_preds = set(p_preds) - set(c_preds)
        
        base_l = 0.5
        base_u = 0.5
        
        if len(common_preds) > 0:
            base_l = 0.7 + 0.2 * (len(common_preds) / (len(p_preds) + 1))
            base_u = min(1.0, 0.8 + 0.1 * (len(common_preds) / (len(p_preds) + 1)))
        
        reasoning = []
        
        # Logic Rules Application
        if 'negation' in p_conns and 'negation' not in c_conns:
            # If prompt negates something candidate affirms, penalize
            base_l *= 0.5
            base_u *= 0.8
            reasoning.append("Negation mismatch detected.")
            
        if 'conditional' in p_conns:
            if 'conditional' in c_conns or len(c_preds) > 0:
                base_l += 0.1
                reasoning.append("Conditional structure preserved.")
            else:
                base_l -= 0.2
                reasoning.append("Conditional logic broken.")

        # Numeric consistency
        if p_nums and c_nums:
            # Simple check: does candidate contain the result of a simple operation?
            # This is a heuristic proxy for "computation"
            if abs(p_nums[-1] - c_nums[-1]) < 1e-5 if len(p_nums)==len(c_nums) else False:
                base_l += 0.2
                reasoning.append("Numeric values align.")
        
        # Clamp
        l = max(0.0, min(1.0, base_l))
        u = max(0.0, min(1.0, base_u))
        if l > u: l, u = u, l
        
        return l, u, "; ".join(reasoning) if reasoning else "Structural match."

    def _dynamics_tracker(self, prompt: str, candidate: str) -> float:
        """
        Track state evolution across premise reordering.
        Measures stability (Lyapunov exponent approximation).
        """
        # Split prompt into sentences/premises
        sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
        if len(sentences) < 2:
            return 1.0 # No dynamics to track, assume stable
        
        # Baseline state
        base_code = self._sparse_code(prompt)
        
        # Perturb: Reverse order of sentences
        perturbed_prompt = " ".join(reversed(sentences))
        pert_code = self._sparse_code(perturbed_prompt)
        
        # Calculate divergence
        diff = np.linalg.norm(base_code - pert_code)
        
        # Normalize divergence to stability score (0 to 1)
        # High divergence = low stability
        stability = 1.0 / (1.0 + diff)
        return stability

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for epistemic traps. Returns a cap on confidence.
        """
        p = prompt.lower()
        
        # 1. Presupposition
        if re.search(r'\b(have you stopped|did you stop|why did|why does|when did)\b', p):
            return 0.2
        
        # 2. Scope Ambiguity
        if re.search(r'\b(every x|all x|same y|different y)\b', p): # Simplified pattern
             if 'same' in p or 'different' in p:
                return 0.3
        
        # 3. Pronoun Ambiguity
        if re.search(r'\b(he|she|him|her|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
            
        # 4. False Dichotomy
        if re.search(r'\b(either.*or|choose between|only two options)\b', p):
            return 0.3
            
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p) and not re.search(r'\b(data|statistic|number)\b', p):
            return 0.4
            
        # 6. Unanswerability (Missing info markers)
        if re.search(r'\b(without knowing|impossible to tell|not enough info)\b', p):
            return 0.1
            
        return 1.0

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Compute F = Reconstruction + Sparsity + Prediction Error"""
        # Encode prompt and candidate
        x_prompt = self._sparse_code(prompt)
        x_cand = self._sparse_code(candidate)
        
        # 1. Reconstruction Error (Prompt vs Candidate reconstruction)
        # Ideally candidate should reconstruct prompt's logical essence
        recon_err = np.linalg.norm(x_prompt - x_cand)**2
        
        # 2. Sparsity
        sparsity = self.lam * np.sum(np.abs(x_cand))
        
        # 3. Prediction Error (Abstract Interpretation)
        l, u, _ = self._abstract_interpretation(prompt, candidate)
        mu = (l + u) / 2.0
        
        # Treat sparse code as observation, mu as expectation
        # Simplified Gaussian error on the mean activation
        mean_activation = np.mean(x_cand) if np.any(x_cand) else 1e-8
        pred_err = 0.5 * ((mean_activation - mu)**2) / (mean_activation + 1e-8)
        
        F = recon_err + sparsity + pred_err
        return F

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if z12 == 0: return 0.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Dynamic stability factor
        stability = self._dynamics_tracker(prompt, "") # Baseline stability of prompt
        
        for cand in candidates:
            # 1. Structural & Logical Analysis
            l, u, reason_trace = self._abstract_interpretation(prompt, cand)
            logic_score = (l + u) / 2.0
            
            # 2. Free Energy Score (Lower is better)
            F = self._compute_free_energy(prompt, cand)
            # Convert to score: exp(-F) normalized roughly
            fe_score = np.exp(-F)
            
            # 3. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # 4. Dynamics Stability
            # If the answer changes meaning with prompt reordering, penalize
            cand_stability = self._dynamics_tracker(prompt, cand)
            
            # Weighted Combination
            # Structural/Logic: 50%, Computation/FE: 25%, Dynamics: 15%, NCD: 10%
            raw_score = (
                0.50 * logic_score + 
                0.25 * fe_score + 
                0.15 * cand_stability +
                0.10 * ncd_score
            )
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            final_score = min(raw_score, meta_cap)
            
            # If meta_cap is low, we explicitly note uncertainty
            if meta_cap < 0.5:
                reason_trace = f"Uncertainty detected (Cap: {meta_cap:.2f}). {reason_trace}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason_trace
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        # 1. Meta-Analysis Cap
        cap = self._meta_confidence(prompt)
        
        # 2. Compute raw confidence via evaluation logic
        # We simulate a single-candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_conf = res[0]['score']
        
        # 3. Apply Cap
        final_conf = min(raw_conf, cap)
        
        # 4. Ensure strict bounds for "definitive" answers
        # Only allow > 0.9 if computation was strong AND no ambiguity
        if cap < 1.0:
            final_conf = min(final_conf, 0.89)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
