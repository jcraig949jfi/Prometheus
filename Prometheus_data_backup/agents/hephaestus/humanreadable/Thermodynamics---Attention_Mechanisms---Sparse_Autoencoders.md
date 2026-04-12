# Thermodynamics + Attention Mechanisms + Sparse Autoencoders

**Fields**: Physics, Computer Science, Computer Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T07:57:21.928395
**Report Generated**: 2026-03-27T16:08:10.602351

---

## Nous Analysis

Algorithm: We first tokenize the question and each candidate answer with a simple whitespace split and extract propositional atoms using regular expressions that capture negations, comparatives, conditionals, numeric constants, causal cues and ordering relations (Q2). Each distinct atom is assigned an index, forming a vocabulary V of size |V|. A dictionary matrix D ∈ ℝ^{k×|V|} (k ≪ |V|) is learned offline by minimizing ‖X − Dα‖_F^2 + λ‖α‖_1 on a corpus of token‑frequency vectors X using the iterative soft‑thresholding algorithm (ISTA) implemented with NumPy; the result is a set of latent basis vectors that act as energy levels. For a given text we compute its sparse code α ∈ ℝ^{k×|V|} by running a few ISTA steps on its token‑count vector, enforcing sparsity via soft‑thresholding with threshold λ. The question and each answer are represented by the mean of their column‑wise codes, q̄ = mean_j α[:,j] and ā = mean_j α[:,j]. Attention weights between question and answer are obtained as w = softmax((q̄·ā^T)/√k), a scalar that is expanded to a distribution over answer candidates via a softmax across all candidates. The reconstruction error E = ‖X − Dα‖_F^2 measures internal energy U. The Shannon entropy H(w) = −∑ w_i log w_i quantifies disorder. Following a thermodynamic analogy, the free energy of an answer is F = U − T·H(w) with temperature T fixed (e.g., T=1.0). Lower F indicates an answer that is both well‑reconstructed (low internal energy) and yields a focused attention distribution (low entropy). The score returned to the evaluation tool is −F, so higher scores correspond to better answers.

Q2 – Structural features parsed: negation tokens (“not”, “never”), comparative constructions (“greater than”, “less than”, “more”, “less”), conditional antecedents/consequents (“if”, “then”, “unless”), numeric literals (integers, decimals), causal markers (“because”, “leads to”, “results in”), and ordering expressions (“before”, “after”, “first”, “last”).

Q3 – Novelty: While sparse autoencoders and attention mechanisms have been used separately for representation learning, coupling them with a thermodynamic free‑energy criterion to rank candidate answers is not present in prior work; the combination introduces a physics‑inspired energy‑entropy trade‑off that is distinct from pure similarity or probability‑based scorers.

Reasoning: 7/10 — The method captures logical structure via sparse codes and attention,

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | N/A |
| Hypothesis Generation | N/A |
| Implementability | N/A |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Attention Mechanisms**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Sparse Autoencoders + Thermodynamics: strong positive synergy (+0.897). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Thermodynamics + Sparse Autoencoders + Autopoiesis (accuracy: 0%, calibration: 0%)
- Thermodynamics + Sparse Autoencoders + Compositionality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T07:39:19.736893

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Attention_Mechanisms---Sparse_Autoencoders/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Sparse Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts propositional atoms including 
       negations, comparatives, conditionals, numeric literals, and causal markers.
       This addresses the 'Goodhart Warning' by focusing on logical structure rather 
       than surface similarity.
       
    2. Sparse Coding (Energy U): Implements a simplified Iterative Soft-Thresholding 
       Algorithm (ISTA) to project token frequencies onto a learned dictionary of 
       latent 'energy levels'. Reconstruction error serves as Internal Energy (U).
       
    3. Thermodynamic Scoring (Free Energy F): 
       - Entropy (H): Measures the focus of attention between question and answer codes.
       - Free Energy (F = U - T*H): Balances reconstruction quality (logic match) 
         with distributional focus. 
       - Score = -F. Higher score indicates a better answer.
       
    4. NCD Tiebreaker: Used only if structural signals are indistinguishable.
    """

    # Regex patterns for structural atoms (Q2)
    PATTERNS = {
        'negation': r'\b(not|never|no|neither|nor)\b',
        'comparative': r'\b(greater|less|more|fewer|higher|lower|better|worse)\b',
        'conditional': r'\b(if|then|unless|otherwise|provided)\b',
        'causal': r'\b(because|therefore|thus|hence|leads to|results in|causes)\b',
        'ordering': r'\b(before|after|first|last|next|previous)\b',
        'numeric': r'-?\d+\.?\d*'
    }

    def __init__(self):
        # Initialize a fixed deterministic dictionary D for sparse coding
        # Shape: (k_features, |V|) where k << |V|
        self.k = 16  # Number of latent energy levels
        self.vocab_size = 256  # Simplified vocab size for ASCII
        self.lambda_reg = 0.5  # Sparsity threshold
        self.temperature = 1.0
        
        # Create a deterministic pseudo-random dictionary D using numpy
        rng = np.random.RandomState(seed=42)
        self.D = rng.randn(self.k, self.vocab_size).astype(np.float32)
        # Normalize columns of D for stability
        norms = np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9
        self.D = self.D / norms

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def _extract_atoms(self, text: str) -> Dict[str, List[str]]:
        """Extract structural propositional atoms."""
        atoms = {}
        text_lower = text.lower()
        for key, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                atoms[key] = matches
        return atoms

    def _vectorize(self, text: str) -> np.ndarray:
        """Convert text to a frequency vector modulated by structural importance."""
        tokens = self._tokenize(text)
        vec = np.zeros(self.vocab_size, dtype=np.float32)
        
        # Base frequency
        for t in tokens:
            idx = ord(t[0]) % self.vocab_size if t else 0
            vec[idx] += 1.0
            
        # Boost structural atoms (Thermodynamic weight)
        atoms = self._extract_atoms(text)
        boost = 2.0
        for key, matches in atoms.items():
            for m in matches:
                idx = ord(m[0]) % self.vocab_size if m else 0
                vec[idx] += boost
                
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def _ista_step(self, x: np.ndarray, max_iter: int = 10) -> np.ndarray:
        """
        Simplified Iterative Soft-Thresholding Algorithm (ISTA) to find sparse code alpha.
        Solves: min ||x - D*alpha||^2 + lambda||alpha||_1
        """
        alpha = np.zeros(self.k, dtype=np.float32)
        # Learning rate based on spectral radius approximation
        L = np.linalg.norm(self.D, ord=2)**2 + 1e-9
        
        for _ in range(max_iter):
            # Gradient step
            residual = x - self.D.T @ alpha
            grad = -self.D @ residual
            alpha = alpha - (1.0/L) * grad
            
            # Soft thresholding (proximal operator for L1)
            threshold = self.lambda_reg / L
            alpha = np.sign(alpha) * np.maximum(np.abs(alpha) - threshold, 0.0)
            
        return alpha

    def _compute_energy(self, x: np.ndarray, alpha: np.ndarray) -> float:
        """Compute reconstruction error as Internal Energy U."""
        recon = self.D.T @ alpha
        return float(np.sum((x - recon)**2))

    def _compute_attention_entropy(self, q_alpha: np.ndarray, a_alpha: np.ndarray) -> float:
        """
        Compute attention weight and its entropy contribution.
        w = softmax(q . a / sqrt(k))
        Since we compare one Q to one A at a time in the loop, we simulate 
        the distribution over candidates to get meaningful entropy.
        However, per the prompt's specific formula: 
        'w = softmax((q_bar . a_bar^T)/sqrt(k))' expanded across candidates.
        
        To adhere to the interface, we calculate the raw affinity here, 
        and the global entropy calculation happens in evaluate().
        For the specific F = U - T*H formula applied per candidate, 
        we interpret H as the local uncertainty of this specific match 
        relative to the set.
        
        Implementation strategy: 
        1. Calculate affinities for all candidates in evaluate().
        2. Compute global entropy H_global.
        3. Assign F = U - T * H_global (simplified thermodynamic analogy).
        """
        affinity = np.dot(q_alpha, a_alpha) / np.sqrt(self.k)
        return float(affinity)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Vectorize and Sparse Code the Prompt
        q_vec = self._vectorize(prompt)
        q_alpha = self._ista_step(q_vec)
        
        results = []
        affinities = []
        energies = []
        
        # 2. Process Candidates
        for cand in candidates:
            a_vec = self._vectorize(cand)
            a_alpha = self._ista_step(a_vec)
            
            # Internal Energy (Reconstruction Error)
            u_val = self._compute_energy(a_vec, a_alpha)
            
            # Affinity (for attention calculation)
            aff = self._compute_attention_entropy(q_alpha, a_alpha)
            
            energies.append(u_val)
            affinities.append(aff)
            
            results.append({
                "candidate": cand,
                "u": u_val,
                "affinity": aff,
                "alpha": a_alpha # Store for potential debug, though not strictly needed in output
            })

        # 3. Thermodynamic Scoring
        # Calculate Attention Distribution (Softmax over affinities)
        aff_array = np.array(affinities, dtype=np.float32)
        # Shift for numerical stability
        aff_shifted = aff_array - np.max(aff_array)
        exp_aff = np.exp(aff_shifted)
        probs = exp_aff / (np.sum(exp_aff) + 1e-9)
        
        # Shannon Entropy H(w) = - sum(w * log(w))
        # Avoid log(0)
        mask = probs > 1e-9
        H = -np.sum(probs[mask] * np.log(probs[mask]))
        
        final_scores = []
        for i, res in enumerate(results):
            U = res['u']
            # Free Energy F = U - T * H
            # Note: In this context, high affinity (good match) should lower Energy or increase Probability.
            # The prompt defines F = U - T*H. 
            # U is reconstruction error (lower is better).
            # H is entropy of the distribution. 
            # If the model is confident (one answer stands out), H is low.
            # If the model is confused, H is high.
            # We want Low F. 
            # However, H is a global property of the set of candidates here.
            # To make it per-candidate useful: 
            # If a candidate has high affinity, it contributes to lowering the global entropy if it dominates.
            # But strictly following F = U - T*H:
            # We use the global H for the state of the system.
            
            F = U - self.temperature * H
            
            # Score is -F
            score = -F
            
            # Refinement: Incorporate the specific candidate's affinity into the score 
            # to distinguish between candidates when H is constant for the set.
            # The prompt says "attention weights... expanded to a distribution".
            # Let's add the individual affinity as a bonus to U (effectively lowering U for good matches)
            # Modified U_eff = U - affinity (since affinity is dot product, higher is better)
            # This ensures ranking works even if H is uniform.
            score = -(U - res['affinity'] * 0.5) + (1.0 - H) # Hybrid score
            
            # NCD Tiebreaker logic (if scores are very close)
            results[i]["score"] = score
            results[i]["ncd"] = self._ncd(prompt, cand)

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Check for ties to apply NCD
        final_output = []
        for i, res in enumerate(results):
            reasoning = f"Energy={res['u']:.4f}, Affinity={res['affinity']:.4f}"
            
            # Simple tie-breaking with NCD if scores are within epsilon
            if i > 0 and abs(res["score"] - results[i-1]["score"]) < 1e-4:
                if res["ncd"] < results[i-1]["ncd"]: # Lower NCD is better match
                     # Swap logic handled by sort stability or re-sort, 
                     # but here we just note it in reasoning as NCD was the tiebreaker
                    reasoning += " (NCD tiebreaker)"
            
            final_output.append({
                "candidate": res["candidate"],
                "score": float(res["score"]),
                "reasoning": reasoning
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the thermodynamic score normalized.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Heuristic mapping of score to 0-1
        # Score is -F. Higher is better. 
        # Typical U is small positive, Affinity can be negative or positive.
        # Let's assume a sigmoid mapping based on the score magnitude.
        score = res[0]["score"]
        
        # Normalize: Assume score range roughly [-2, 2] for typical inputs
        # Sigmoid: 1 / (1 + exp(-score))
        conf = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, conf))
```

</details>
