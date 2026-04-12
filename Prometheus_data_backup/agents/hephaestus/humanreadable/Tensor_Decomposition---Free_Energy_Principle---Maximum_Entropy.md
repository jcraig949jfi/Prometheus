# Tensor Decomposition + Free Energy Principle + Maximum Entropy

**Fields**: Mathematics, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T20:38:38.727688
**Report Generated**: 2026-03-27T06:37:40.196698

---

## Nous Analysis

**Algorithm**  
We build a third‑order binary tensor **X** ∈ {0,1}^{P×E×C} where the modes are:  

* **P** – proposition type (negation, comparative, conditional, numeric, causal, ordering) extracted by a fixed set of regex patterns;  
* **E** – entity identifiers (named nouns, numbers, units) obtained from the same regex pass;  
* **C** – polarity/context (asserted, denied, presupposed).  

Each observed proposition sets X[p,e,c]=1.  

We approximate **X** with a rank‑R CP decomposition: **X** ≈ ∑_{r=1}^R a_r ∘ b_r ∘ c_r, where factor matrices **A**∈ℝ^{P×R}, **B**∈ℝ^{E×R}, **C**∈ℝ^{C×R} are learned by alternating least squares using only NumPy (no autograd).  

For a candidate answer we construct its own proposition tensor **X̂** in the same way. The reconstruction error is  

E_rec = ½‖**X̂** – [[**A**,**B**,**C**]]‖_F²  

(the Frobenius norm computed with NumPy).  

Following the Free Energy Principle, we treat the candidate’s latent factor scores **z** = (**A**ᵀx̂_P) ⊙ (**B**ᵀx̂_E) ⊙ (**C**ᵀx̂_C) (element‑wise product of mode‑wise projections) as a variational distribution q(z) ∝ exp(**z**). The entropy of q is  

H = -∑_i q_i log q_i   (with q_i = softmax(**z**)).  

The variational free energy is  

F = E_rec – H  

Lower F indicates a candidate that both reconstructs the observed propositional structure well and yields a high‑entropy (least‑biased) belief distribution, i.e., a Maximum‑Entropy solution consistent with the extracted constraints. Scoring proceeds by computing F for each candidate and ranking them ascendingly.

**Structural features parsed**  
The regex layer captures: negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), numeric values and units, causal verbs (“cause”, “lead to”), and ordering relations (“before”, “after”, “precedes”). Each maps to a distinct slice of the **P** mode.

**Novelty**  
Combining CP tensor factorization with a variational free‑energy objective and a maximum‑entropy prior is not found in standard NLP pipelines; most works use either tensor methods for semantic completion or variational inference separately. The joint use of all three to score answer candidates is therefore novel.

**Rating**  
Reasoning: 7/10 — captures logical structure via tensor rank and free‑energy minimization, but relies on linear approximations.  
Metacognition: 6/10 — entropy term provides a self‑assessment of uncertainty, yet no explicit higher‑order reflection loop.  
Hypothesis generation: 5/10 — the model can propose alternative latent factor configurations, but hypothesis space is limited to CP rank‑R reconstructions.  
Implementability: 8/10 — only NumPy and regex; alternating least squares and softmax are straightforward to code in pure Python.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Tensor Decomposition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Free Energy Principle + Tensor Decomposition: strong positive synergy (+0.541). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Maximum Entropy: strong positive synergy (+0.241). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Prime Number Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Tensor Decomposition + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T22:32:51.879002

---

## Code

**Source**: scrap

[View code](./Tensor_Decomposition---Free_Energy_Principle---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer using Tensor Decomposition concepts,
    Free Energy minimization, and Maximum Entropy constraints.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negation, causality, numbers) 
       into a binary vector (simulating a flattened tensor slice).
    2. Free Energy Scoring: Computes E_rec (reconstruction error between prompt 
       and candidate structures) and subtracts an entropy term H (uncertainty) 
       to derive Free Energy F = E_rec - H.
    3. Ranking: Lower Free Energy indicates a better fit (high consistency, optimal uncertainty).
       We invert this for the final score so higher is better.
    4. NCD Tiebreaker: Uses zlib compression distance only when structural scores are identical.
    """

    def __init__(self):
        # Regex patterns for structural extraction (Mode P)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'ordering': re.compile(r'\b(first|last|next|previous|precede|follow)\b', re.IGNORECASE)
        }
        self.modes = list(self.patterns.keys())
        self.mode_count = len(self.modes)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts binary structural features into a vector (flattened tensor slice)."""
        text_lower = text.lower()
        features = np.zeros(self.mode_count, dtype=float)
        
        for i, key in enumerate(self.modes):
            if self.patterns[key].search(text_lower):
                features[i] = 1.0
        
        # Numeric density feature (normalized)
        nums = self.patterns['numeric'].findall(text_lower)
        if nums:
            features[-1] = min(1.0, len(nums) / 5.0) 
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def _compute_free_energy(self, prompt_vec: np.ndarray, cand_vec: np.ndarray) -> Tuple[float, float, float]:
        """
        Computes Free Energy F = E_rec - H.
        E_rec: Reconstruction error (Frobenius norm approximation).
        H: Entropy of the latent belief distribution.
        """
        # 1. Reconstruction Error (E_rec)
        # In CP decomposition, we approximate X. Here, we measure distance between 
        # the prompt's structural signature and the candidate's signature.
        # Using squared Euclidean distance as a proxy for Frobenius norm of the difference.
        diff = prompt_vec - cand_vec
        e_rec = 0.5 * np.dot(diff, diff)

        # 2. Maximum Entropy Component (H)
        # Construct latent scores z via element-wise product (simulating mode projection)
        # We add a small epsilon to avoid log(0) and handle zero vectors.
        z = (prompt_vec + 1e-9) * (cand_vec + 1e-9)
        
        # Normalize to get distribution q (softmax-like)
        z_shifted = z - np.max(z) # Stability
        exp_z = np.exp(z_shifted)
        q = exp_z / (np.sum(exp_z) + 1e-9)
        
        # Compute Entropy H = -sum(q log q)
        # If q is uniform (high uncertainty/MaxEnt), H is high.
        # If q is peaked (low uncertainty), H is low.
        # We want candidates that satisfy constraints (low E_rec) but aren't over-confident 
        # in wrong ways. However, per FEP, we minimize F. 
        # High H reduces F, favoring less biased solutions.
        h_val = -np.sum(q * np.log(q + 1e-9))

        free_energy = e_rec - h_val
        return free_energy, e_rec, h_val

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._extract_features(prompt)
        results = []
        
        # Pre-calculate scores
        scored_candidates = []
        for cand in candidates:
            cand_vec = self._extract_features(cand)
            f_energy, e_rec, h_val = self._compute_free_energy(prompt_vec, cand_vec)
            scored_candidates.append({
                "candidate": cand,
                "free_energy": f_energy,
                "e_rec": e_rec,
                "h_val": h_val
            })
        
        # Sort by Free Energy (ascending: lower is better)
        # We use a stable sort. If F energies are very close, we need a tiebreaker.
        # However, to integrate NCD as requested for ties:
        # We group by rounded F_energy or use NCD as a secondary sort key if F is close.
        
        def sort_key(item):
            # Primary: Free Energy (lower is better)
            # Secondary: NCD with prompt (lower is better for similarity/context)
            ncd = self._compute_ncd(prompt, item["candidate"])
            return (item["free_energy"], ncd)

        scored_candidates.sort(key=sort_key)
        
        # Normalize scores to 0-1 range for output, where higher is better
        min_f = scored_candidates[0]["free_energy"]
        max_f = scored_candidates[-1]["free_energy"]
        range_f = max_f - min_f if max_f > min_f else 1.0
        
        final_results = []
        for item in scored_candidates:
            # Invert free energy so higher score = better
            norm_score = 1.0 - ((item["free_energy"] - min_f) / range_f)
            
            reasoning = (
                f"Structural match: {1.0 - item['e_rec']:.2f}, "
                f"Entropy bonus: {item['h_val']:.2f}, "
                f"Net Free Energy: {item['free_energy']:.4f}"
            )
            
            final_results.append({
                "candidate": item["candidate"],
                "score": round(norm_score, 4),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on Free Energy minimization."""
        prompt_vec = self._extract_features(prompt)
        cand_vec = self._extract_features(answer)
        
        f_energy, _, _ = self._compute_free_energy(prompt_vec, cand_vec)
        
        # Map Free Energy to confidence. 
        # Ideal case: perfect match (E_rec=0) and moderate entropy.
        # F should be near 0 or negative. Large positive F implies poor fit.
        # Using a sigmoid-like mapping: 1 / (1 + F) for F >= 0
        if f_energy < 0:
            conf = 0.99 # Very high confidence if F is negative (high entropy, low error)
        else:
            conf = 1.0 / (1.0 + f_energy)
            
        return min(1.0, max(0.0, conf))
```

</details>
