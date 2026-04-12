# Phase Transitions + Sparse Coding + Free Energy Principle

**Fields**: Physics, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T17:39:08.007936
**Report Generated**: 2026-03-27T16:08:11.901857

---

## Nous Analysis

**Algorithm**  
We treat each premise‑answer pair as a factor graph where binary nodes correspond to extracted linguistic features (e.g., “X > Y”, “¬P”, “if A then B”). Features are stored in a sparse binary matrix **F** ∈ {0,1}^{M×K} (M sentences, K possible feature types). Each row **fᵢ** is a candidate answer’s feature vector; the premise yields a fixed vector **p**.  

1. **Sparse coding step** – Learn a dictionary **D** ∈ ℝ^{K×L} (L ≪ K) by solving  
   \[
   \min_{D,Z}\|F - DZ\|_2^2 + \lambda\|Z\|_1
   \]  
   using coordinate descent (numpy only). **Z** gives the sparse activation codes for each answer; the L₁ term enforces few active atoms, yielding an energy‑efficient representation.  

2. **Free‑energy computation** – Define precision matrix **Π** = αI (α > 0). Prediction error for answer *i* is εᵢ = **fᵢ** – **p**. Variational free energy (approximate negative log‑likelihood) is  
   \[
   \mathcal{F}_i = \frac{1}{2}\,ε_i^{\!T}Π ε_i + \lambda\|z_i\|_1,
   \]  
   where the first term is precision‑weighted squared error and the second is the sparsity penalty (entropy term under a Laplace prior).  

3. **Phase‑transition decision** – As α increases, the system undergoes a transition from a high‑entropy regime (many active features, large 𝔽) to a low‑entropy regime (few active features, small 𝔽). The critical precision α_c is estimated analytically for a Laplace prior:  
   \[
   α_c = \frac{2\lambda}{\mathbb{E}[|ε|]} .
   \]  
   For α > α_c we accept answers whose 𝔽 falls below a threshold τ = 𝔽_min + δ (δ small). The final score is  
   \[
   s_i = -\mathcal{F}_i,
   \]  
   so higher scores correspond to lower free energy. All operations use numpy dot products, norms, and soft‑thresholding for the L₁ step.  

**Structural features parsed**  
- Negations (“not”, “no”) → polarity flag.  
- Comparatives (“greater than”, “less than”) → numeric ordering predicates.  
- Conditionals (“if … then …”) → implication edges.  
- Causal verbs (“cause”, “lead to”) → directed causal links.  
- Numeric values and units → grounded magnitude features.  
- Temporal ordering (“before”, “after”) → time‑point relations.  
- Quantifiers (“all”, “some”) → scope markers.  

**Novelty**  
Sparse coding and the free‑energy principle have been applied separately to neural modeling and perception; phase transitions are used in statistical physics of learning. Combining them to define a precision‑driven sparsity‑controlled free‑energy score for logical answer selection has not, to our knowledge, been instantiated in a pure‑numpy reasoning evaluator, making the approach novel in this context.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via sparse features and precision‑weighted error, but relies on linear approximations.  
Metacognition: 6/10 — can monitor free‑energy minima to gauge confidence, yet lacks explicit self‑reflective loops.  
Hypothesis generation: 7/10 — sparse dictionary enables rapid recombination of features into new candidate explanations.  
Implementability: 9/10 — all steps use only numpy and standard library; no external APIs or neural nets required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Phase Transitions**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 33% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sparse Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Phase Transitions + Sparse Coding: strong positive synergy (+0.277). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Phase Transitions: strong positive synergy (+0.397). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Sparse Coding: negative interaction (-0.064). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Phase Transitions + Genetic Algorithms + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Phase Transitions + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Phase Transitions + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=18% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T08:38:26.681430

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Sparse_Coding---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Sparse Coding, Free Energy Principle, and Phase Transitions.
    
    Mechanism:
    1. Structural Parsing: Extracts binary linguistic features (negations, comparatives, conditionals,
       causality, quantifiers, temporality) from prompts and candidates into feature vectors.
    2. Sparse Coding: Approximates a dictionary learning step where the 'ideal' answer matches the 
       prompt's structural signature. We enforce sparsity (L1) on the difference between candidate 
       and prompt features.
    3. Free Energy: Computes F = 0.5 * error^T * Precision * error + Lambda * sparsity.
       This balances fidelity to the prompt (prediction error) with model complexity (sparsity).
    4. Phase Transition: Uses a critical precision threshold (alpha_c) to switch between high-entropy
       (lenient) and low-entropy (strict) scoring regimes, filtering out noisy candidates.
    5. Scoring: Returns negative Free Energy as the score. NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        self.lambda_sparsity = 0.5
        self.alpha_base = 1.0
        self.delta_threshold = 0.1
        
        # Feature patterns for structural parsing
        self.patterns = [
            (r'\b(not|no|never|neither)\b', 'negation'),
            (r'\b(greater|less|more|fewer|higher|lower|before|after)\b', 'comparative'),
            (r'\b(if|then|unless|provided|when)\b', 'conditional'),
            (r'\b(cause|lead|result|effect|because|therefore)\b', 'causal'),
            (r'\b(all|some|every|none|any|most)\b', 'quantifier'),
            (r'\d+(\.\d+)?', 'numeric'), # Detects presence of numbers
            (r'\b(must|should|could|may)\b', 'modality')
        ]
        self.feature_names = [p[1] for p in self.patterns]
        self.K = len(self.feature_names)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        if not text:
            return np.zeros(self.K)
        
        text_lower = text.lower()
        features = []
        for pattern, _ in self.patterns:
            if re.search(pattern, text_lower):
                features.append(1.0)
            else:
                features.append(0.0)
        return np.array(features)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            import zlib
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 0.5

    def _compute_free_energy(self, f_candidate: np.ndarray, f_prompt: np.ndarray, alpha: float) -> float:
        """
        Compute Variational Free Energy.
        F = 0.5 * (f_c - f_p)^T * Pi * (f_c - f_p) + lambda * ||z||_1
        Where z is the sparse code approximating the difference.
        """
        epsilon = f_candidate - f_prompt
        
        # Precision weighted error (Pi = alpha * I)
        # Since Pi is diagonal, epsilon^T Pi epsilon = alpha * sum(epsilon^2)
        prediction_error_term = 0.5 * alpha * np.dot(epsilon, epsilon)
        
        # Sparsity penalty (L1 norm of the error vector as a proxy for sparse code z)
        # In this simplified model, the 'code' required to explain the deviation is the deviation itself
        sparsity_term = self.lambda_sparsity * np.sum(np.abs(epsilon))
        
        return prediction_error_term + sparsity_term

    def _get_critical_alpha(self, candidates_features: List[np.ndarray], prompt_features: np.ndarray) -> float:
        """
        Estimate critical precision alpha_c for phase transition.
        alpha_c = 2 * lambda / E[|epsilon|]
        """
        errors = []
        for f_c in candidates_features:
            eps = f_c - prompt_features
            errors.extend(np.abs(eps))
        
        if not errors:
            return self.alpha_base
            
        avg_error = np.mean(errors)
        if avg_error < 1e-9:
            return self.alpha_base * 10 # High precision if errors are negligible
            
        return (2.0 * self.lambda_sparsity) / avg_error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        cand_features = [self._extract_features(c) for c in candidates]
        
        # Phase Transition: Determine regime via critical alpha
        alpha_c = self._get_critical_alpha(cand_features, prompt_features)
        # Use a precision slightly above critical to ensure we are in the low-entropy (selective) regime
        alpha = alpha_c * 1.2 
        
        results = []
        min_energy = float('inf')
        
        # Calculate Free Energy for each candidate
        energies = []
        for i, f_c in enumerate(cand_features):
            energy = self._compute_free_energy(f_c, prompt_features, alpha)
            energies.append(energy)
            if energy < min_energy:
                min_energy = energy
        
        # Thresholding based on phase transition logic
        threshold = min_energy + self.delta_threshold
        
        scored_candidates = []
        for i, candidate in enumerate(candidates):
            energy = energies[i]
            
            # Base score is negative free energy
            score = -energy
            
            # Phase transition filter: if energy is too high (above threshold), penalize heavily
            # unless it's the best we have (to avoid empty results)
            if energy > threshold:
                # Apply a steep penalty but keep relative ordering for tie-breaking
                score -= 10.0 
            
            # Tie-breaking with NCD if scores are very close
            # We add a tiny fraction of NCD distance to break ties deterministically
            ncd_val = self._compute_ncd(prompt, candidate)
            final_score = score - (ncd_val * 1e-6)
            
            reasoning = f"Structural match (energy={energy:.4f}, alpha={alpha:.2f}). "
            if energy > threshold:
                reasoning += "High entropy regime (low confidence)."
            else:
                reasoning += "Low entropy regime (high confidence)."
                
            scored_candidates.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on free energy relative to a baseline.
        0 = high energy (wrong), 1 = low energy (correct).
        """
        prompt_features = self._extract_features(prompt)
        answer_features = self._extract_features(answer)
        
        # Use a standard high precision for confidence check
        alpha = self.alpha_base * 2.0
        energy = self._compute_free_energy(answer_features, prompt_features, alpha)
        
        # Map energy to [0, 1]. 
        # Max theoretical energy for binary features of size K is approx 0.5*alpha*K + lambda*K
        max_energy = 0.5 * alpha * self.K + self.lambda_sparsity * self.K
        if max_energy == 0:
            return 1.0
            
        # Normalize: 0 energy -> 1.0, max energy -> 0.0
        conf = 1.0 - (energy / max_energy)
        return max(0.0, min(1.0, conf))
```

</details>
