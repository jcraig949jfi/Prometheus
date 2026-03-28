# Analogical Reasoning + Wavelet Transforms + Free Energy Principle

**Fields**: Cognitive Science, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:01:24.632542
**Report Generated**: 2026-03-27T06:37:38.842296

---

## Nous Analysis

**Algorithm – Wavelet‑Guided Analogy Scorer (WGAS)**  

1. **Pre‑processing & structural parsing** – The prompt and each candidate answer are tokenized. Using regex we extract a set of *relation triples* (subject, predicate, object) covering: negations, comparatives (“more/less than”), conditionals (“if … then”), causal verbs (“cause”, “lead to”), numeric expressions, and ordering relations (“before”, “after”). Each triple is stored in a sparse binary matrix **R** ∈ {0,1}^{T×P} where *T* indexes triples and *P* indexes predicate types (≈15 categories).  

2. **Multi‑resolution encoding (wavelet stage)** – For each predicate column we compute a 1‑D Haar wavelet transform on the binary vector across triples, yielding coefficients **W** at scales s = 0…⌊log₂T⌉. The transform captures local patterns (e.g., a cluster of causal triples) and long‑range dependencies (e.g., a chain of conditionals). We retain the absolute coefficient magnitude |W| as a feature vector **f** ∈ ℝ^{S·P}.  

3. **Analogical mapping (structure‑mapping stage)** – Candidate answer **A** and prompt **P** are each represented by their feature vectors **f_A**, **f_P**. We compute a *relational similarity* matrix **S** = f_A · f_Pᵀ (dot product) and then apply the *structural consistency* constraint from the Free Energy Principle: we treat **S** as a variational approximation to the posterior over mappings and minimize the KL‑divergence‑like free energy  
   F = ‖S – M‖_F² + λ·‖M‖₁,  
   where **M** is a binary mapping matrix enforcing one‑to‑one predicate alignment (solved via Hungarian algorithm on –S). The resulting free‑energy value **F_A** quantifies how well the answer’s relational structure can be mapped onto the prompt’s structure while penalizing unnecessary complexity.  

4. **Scoring** – The final score for answer **c** is  
   score_c = exp(–F_c) · (1 + α·numerical_match_c),  
   where *numerical_match_c* is the ratio of correctly extracted numbers (via regex) and α∈[0,1] balances numeric fidelity. Answers with lower free energy (better structural analogy) and higher numeric fidelity receive higher scores.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations, and quantifiers (all/none/some).  

**Novelty** – While wavelet‑based text encoding and analogical mapping exist separately, jointly optimizing a free‑energy‑style objective over wavelet coefficients to enforce structural consistency is not described in the literature; it combines multi‑resolution signal processing with variational principle‑driven analogy, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — captures relational structure and uncertainty minimization well.  
Metacognition: 6/10 — limited self‑reflection; relies on fixed free‑energy trade‑off.  
Hypothesis generation: 5/10 — can propose alternative mappings via wavelet scales but lacks generative depth.  
Implementability: 9/10 — uses only numpy, regex, and Hungarian algorithm; straightforward to code.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Wavelet Transforms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Analogical Reasoning + Free Energy Principle: strong positive synergy (+0.320). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Wavelet Transforms: strong positive synergy (+0.116). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Wavelet Transforms + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=40% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T15:45:54.846220

---

## Code

**Source**: scrap

[View code](./Analogical_Reasoning---Wavelet_Transforms---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Guided Analogy Scorer (WGAS) with Free Energy Core.
    
    Mechanism:
    1. Structural Parsing: Extracts relation triples (negations, causals, numerics) 
       into a binary matrix R (Triples x Predicate Types).
    2. Multi-resolution Encoding: Applies a discrete Haar wavelet transform to R 
       to capture local clusters and long-range dependencies in the logical structure.
    3. Free Energy Minimization: Treats the mapping between Prompt and Candidate 
       structures as a variational inference problem. Minimizes Free Energy F = 
       Reconstruction_Error + Complexity_Penalty to find the optimal structural alignment.
    4. Scoring: Converts Free Energy to a probability score, boosted by numeric fidelity.
    """

    # Predicate categories for structural parsing
    PREDICATES = [
        'negation', 'comparative', 'conditional', 'causal', 
        'numeric', 'ordering', 'quantifier'
    ]
    
    # Regex patterns for extraction
    PATTERNS = {
        'negation': [r'\b(not|no|never|neither|without)\b', r'\bun[A-Za-z]+\b'],
        'comparative': [r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', r'[<>]=?'],
        'conditional': [r'\b(if|then|unless|provided|whenever)\b'],
        'causal': [r'\b(cause|lead|result|due|because|therefore|thus)\b'],
        'numeric': [r'\d+(\.\d+)?'],
        'ordering': [r'\b(before|after|first|last|precede|follow)\b'],
        'quantifier': [r'\b(all|none|some|every|any|most|few)\b']
    }

    def __init__(self):
        self.alpha = 0.5  # Balance between structural and numeric fidelity
        self.lambda_reg = 0.1  # Complexity penalty weight

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extracts simplified relation triples (subject, predicate_type, object)"""
        text_lower = text.lower()
        triples = []
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Simple window-based extraction for context
        for i, word in enumerate(words):
            for p_type, patterns in self.PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, word):
                        # Construct a pseudo-triple: (prev_word, predicate, next_word)
                        subj = words[i-1] if i > 0 else "*"
                        obj = words[i+1] if i < len(words)-1 else "*"
                        triples.append((subj, p_type, obj))
                        break # Avoid double counting same word for same type
        return triples

    def _build_matrix(self, triples: List[Tuple[str, str, str]], max_triples: int = 64) -> np.ndarray:
        """Builds binary matrix R (T x P)"""
        T = min(len(triples), max_triples)
        if T == 0: T = 1 # Ensure non-empty for wavelet
        
        R = np.zeros((max_triples, len(self.PREDICATES)))
        
        for i, (s, p_type, o) in enumerate(triples):
            if i >= max_triples: break
            if p_type in self.PREDICATES:
                idx = self.PREDICATES.index(p_type)
                R[i, idx] = 1.0
                
        # Pad if necessary (already initialized to 0)
        return R[:max_triples, :]

    def _haar_wavelet_1d(self, vector: np.ndarray) -> np.ndarray:
        """Computes 1D Haar wavelet coefficients (absolute magnitudes)"""
        n = len(vector)
        if n == 0: return np.array([])
        
        # Ensure power of 2 for simplicity in this constrained implementation
        size = 1
        while size < n: size *= 2
        padded = np.zeros(size)
        padded[:n] = vector
        
        coeffs = []
        current = padded
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                avg = (current[i] + current[i+1]) / 2.0
                diff = (current[i] - current[i+1]) / 2.0
                next_level.append(avg)
                coeffs.append(abs(diff)) # Store absolute detail coefficient
            current = np.array(next_level)
        coeffs.append(abs(current[0])) # Approximation coefficient
        
        return np.array(coeffs)

    def _compute_wavelet_features(self, text: str) -> np.ndarray:
        """Step 1 & 2: Parse and apply wavelet transform"""
        triples = self._extract_triples(text)
        R = self._build_matrix(triples)
        
        features = []
        for col_idx in range(R.shape[1]):
            col = R[:, col_idx]
            # Apply wavelet to the column
            w_coeffs = self._haar_wavelet_1d(col)
            features.extend(w_coeffs)
        
        # Normalize feature vector
        f_vec = np.array(features)
        norm = np.linalg.norm(f_vec)
        if norm > 0:
            f_vec = f_vec / norm
        return f_vec

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts numeric values for fidelity check"""
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        return [float(n) for n in nums]

    def _compute_free_energy(self, f_prompt: np.ndarray, f_cand: np.ndarray) -> float:
        """
        Step 3: Compute Free Energy F = ||S - M||^2 + lambda * ||M||_1
        Simplified for vector features: F = ||f_p - f_c||^2 + lambda * complexity
        Where complexity is the L1 norm of the difference (sparsity penalty on deviation)
        """
        if len(f_prompt) == 0 or len(f_cand) == 0:
            return 10.0 # High energy for empty
            
        # Align dimensions by truncating to min length
        min_len = min(len(f_prompt), len(f_cand))
        fp = f_prompt[:min_len]
        fc = f_cand[:min_len]
        
        # Reconstruction error (Squared Euclidean)
        reconstruction_error = np.sum((fp - fc) ** 2)
        
        # Complexity penalty (L1 norm of difference, representing 'surprise' or deviation)
        complexity = np.sum(np.abs(fp - fc))
        
        F = reconstruction_error + self.lambda_reg * complexity
        return float(F)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates based on structural analogy and free energy."""
        if not candidates:
            return []
            
        f_prompt = self._compute_wavelet_features(prompt)
        prompt_nums = self._extract_numbers(prompt)
        
        results = []
        for cand in candidates:
            f_cand = self._compute_wavelet_features(cand)
            cand_nums = self._extract_numbers(cand)
            
            # 1. Structural Score via Free Energy
            F_val = self._compute_free_energy(f_prompt, f_cand)
            structural_score = math.exp(-F_val)
            
            # 2. Numeric Fidelity
            num_match = 0.0
            if len(prompt_nums) > 0:
                # Check overlap or closeness
                matches = 0
                for pn in prompt_nums:
                    for cn in cand_nums:
                        if abs(pn - cn) < 1e-6: # Exact float match for simplicity
                            matches += 1
                            break
                num_match = matches / len(prompt_nums) if len(prompt_nums) > 0 else 0
            else:
                # If no numbers in prompt, assume neutral fidelity
                num_match = 1.0 if len(cand_nums) == 0 else 0.5

            # 3. Final Score
            score = structural_score * (1 + self.alpha * num_match)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FreeEnergy={F_val:.4f}, NumMatch={num_match:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        # Normalize roughly: exp(-F) is max 1.0. With numeric boost, max is 1.5.
        # Map to 0-1 range.
        confidence = min(1.0, raw_score) 
        return confidence
```

</details>
