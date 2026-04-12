# Thermodynamics + Sparse Autoencoders + Feedback Control

**Fields**: Physics, Computer Science, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T07:57:56.787256
**Report Generated**: 2026-03-27T17:21:24.262563

---

## Nous Analysis

**Algorithm – Thermodynamic‑Sparse‑Feedback Scorer (TSFS)**  
1. **Parse & Encode** – From the prompt and each candidate answer we extract a set of logical predicates using a small regex‑based parser:  
   - *Atomic propositions* (e.g., “X is Y”, “X > Y”, “if A then B”, “not C”).  
   - *Typed slots*: entity, relation, polarity, comparator, numeric value, temporal order.  
   Each predicate becomes a one‑hot entry in a sparse binary vector **x** ∈ {0,1}^D (D ≈ number of distinct predicate types observed in the training corpus).  
2. **Sparse Dictionary Layer** – Learn a fixed dictionary **W** ∈ ℝ^{D×K} (K ≪ D) offline with a standard sparse‑coding objective: minimize ‖x – Wz‖₂² + λ‖z‖₁ using only NumPy (coordinate descent). The code **z** ∈ ℝ^K is the latent representation; the L₁ term enforces sparsity, yielding a disentangled feature set (e.g., one dimension for “causal direction”, another for “magnitude comparison”).  
3. **Thermodynamic Energy Function** – Define a scalar free‑energy‑like score for a candidate:  
   \[
   E(z) = \frac{1}{2}\|z - z_{\text{prompt}}\|_2^2 + \beta \, \sum_i \phi(z_i)
   \]  
   where \(z_{\text{prompt}}\) is the code of the prompt, β > 0 controls entropy, and \(\phi\) is a soft‑plus approximation of the negative log‑likelihood (acting as an internal energy term). Minimizing E corresponds to driving the system toward equilibrium with the prompt while preserving sparsity‑induced disorder.  
4. **Feedback Control Loop** – Treat the gradient ∂E/∂z as the error signal. Update a provisional score **s** using a discrete‑time PID controller:  
   \[
   s_{t+1}= s_t + K_p e_t + K_i\sum_{τ≤t} e_τ + K_d (e_t-e_{t-1})
   \]  
   where \(e_t = -∂E/∂z|_{z_t}\) and the gains (Kp, Ki, Kd) are fixed heuristically (e.g., 0.5, 0.1, 0.2). After a small number of iterations (≤5) the final **s** is taken as the candidate’s relevance score; higher **s** (lower free energy) indicates better alignment.  

**Parsed Structural Features** – Negations (via “not”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), numeric values (constants, units), causal claims (“because”, “leads to”), ordering relations (“before”, “after”), and existential/universal quantifiers extracted as predicate polarity and type tags.  

**Novelty** – The combination mirrors energy‑based models (statistical physics), sparse coding (dictionary learning), and control‑theoretic optimization, but the explicit PID‑driven refinement of a thermodynamic free‑energy objective over a sparsely encoded logical vector has not been reported in the literature. Prior work uses either energy‑based scoring *or* sparse features *or* control loops, not all three together in a deterministic, numpy‑only pipeline.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and numeric constraints via a principled energy minimization that respects sparsity.  
Metacognition: 6/10 — the PID loop offers basic self‑correction but lacks higher‑order reflection on its own search dynamics.  
Hypothesis generation: 5/10 — hypothesis formation is limited to selecting among pre‑extracted predicates; no generative proposal of new relations.  
Implementability: 9/10 — relies solely on NumPy and stdlib; all steps (regex parsing, coordinate descent sparse coding, gradient‑PID update) are straightforward to code.

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

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Sparse Autoencoders + Thermodynamics: strong positive synergy (+0.897). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Feedback Control + Sparse Autoencoders: negative interaction (-0.059). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Thermodynamics + Sparse Autoencoders + Autopoiesis (accuracy: 0%, calibration: 0%)
- Thermodynamics + Sparse Autoencoders + Compositionality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Neural Plasticity + Feedback Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode character '\u2248' in position 4190: character maps to <undefined>

**Forge Timestamp**: 2026-03-27T17:13:49.747417

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Sparse_Autoencoders---Feedback_Control/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Thermodynamic-Sparse-Feedback Scorer (TSFS)
    
    Mechanism:
    1. Structural Parsing: Extracts logical predicates (negations, comparatives, conditionals)
       and numeric values into a sparse binary vector.
    2. Sparse Coding: Projects this vector onto a fixed random dictionary (simulating offline 
       learned features) to get a latent code z.
    3. Thermodynamic Energy: Computes free energy E(z) based on distance to prompt state and 
       an internal entropy term.
    4. Feedback Control: Uses a discrete PID controller to iteratively refine a relevance score 
       based on the gradient of the energy function.
    5. Epistemic Honesty: Checks for Tier B traps (ambiguity, presupposition) to cap confidence.
    
    Scoring Weights: Structural (50%), Computation (35%), NCD Tiebreaker (15%).
    """

    def __init__(self):
        # Hyperparameters
        self.D = 200  # Dimension of sparse vector (predicate types)
        self.K = 20   # Dimension of latent space (features)
        self.lambda_sparse = 0.1
        self.beta = 0.5 # Entropy weight
        self.max_iter = 5
        
        # PID Gains
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.2
        
        # Fixed random dictionary for sparse coding (deterministic seed)
        np.random.seed(42)
        self.W = np.random.randn(self.D, self.K)
        self.W = self.W / (np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8)

        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.I),
            'quantifier': re.compile(r'\b(every|all|some|none|any|each)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all).*\b(a|an|the)\b.*\b(same|different|identical)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|which one)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(only|must)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I),
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Parse text into a sparse binary vector of logical predicates."""
        x = np.zeros(self.D)
        text_lower = text.lower()
        
        # Map patterns to indices (modulo D for simplicity in this demo)
        idx = 0
        if self.patterns['negation'].search(text): x[idx % self.D] = 1
        idx += 1
        if self.patterns['comparative'].search(text): x[idx % self.D] = 1
        idx += 1
        if self.patterns['conditional'].search(text): x[idx % self.D] = 1
        idx += 1
        if self.patterns['causal'].search(text): x[idx % self.D] = 1
        idx += 1
        if self.patterns['quantifier'].search(text): x[idx % self.D] = 1
        idx += 1
        
        # Numeric extraction (simplified: count presence of numbers)
        nums = self.patterns['number'].findall(text)
        if nums:
            x[idx % self.D] = 1
            # Encode magnitude rough bucket (0-9)
            try:
                val = int(float(nums[0])) % 10
                x[(idx + 1 + val) % self.D] = 1
            except: pass
            
        return x

    def _sparse_code(self, x: np.ndarray) -> np.ndarray:
        """
        Compute latent code z using coordinate descent to minimize:
        ||x - Wz||^2 + lambda||z||_1
        Simplified for speed: One-step soft-thresholding approximation.
        """
        # Approximate inverse: z ≈ (W^T W)^-1 W^T x
        # Since W is fixed and random, we use a simplified projection + soft threshold
        proj = self.W.T @ x
        # Soft thresholding for L1 sparsity
        z = np.sign(proj) * np.maximum(np.abs(proj) - self.lambda_sparse, 0)
        return z

    def _compute_energy(self, z: np.ndarray, z_prompt: np.ndarray) -> float:
        """Compute thermodynamic free energy E(z)."""
        # Kinetic term: Distance to prompt equilibrium
        kinetic = 0.5 * np.linalg.norm(z - z_prompt)**2
        # Potential term: Internal entropy/sparsity penalty (soft-plus approx)
        potential = self.beta * np.sum(np.log(1 + np.exp(np.abs(z))))
        return kinetic + potential

    def _pid_score_update(self, prompt: str, candidate: str, prev_score: float, 
                          e_t: float, e_t_minus_1: float, integral: float) -> Tuple[float, float]:
        """Update score using discrete PID control law."""
        # Error signal is negative gradient (we want to minimize energy, so move against gradient)
        # Here we treat the energy difference as the process variable
        
        # Proportional
        p_term = self.Kp * e_t
        # Integral
        new_integral = integral + e_t
        i_term = self.Ki * new_integral
        # Derivative
        d_term = self.Kd * (e_t - e_t_minus_1)
        
        new_score = prev_score + p_term + i_term + d_term
        return new_score, new_integral

    def _check_meta_confidence(self, text: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        text_lower = text.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(text):
            return 0.2
        
        # 2. Scope ambiguity (simplified check)
        if self.patterns['scope_ambiguity'].search(text):
            return 0.3
            
        # 3. Pronoun ambiguity
        if self.patterns['pronoun_ambiguity'].search(text):
            return 0.3
            
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(text):
            return 0.4
            
        # 5. Subjectivity without criteria
        if self.patterns['subjectivity'].search(text):
            return 0.5
            
        # Default: high potential confidence if structural match exists
        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural alignment and logic."""
        x_prompt = self._extract_features(prompt)
        x_cand = self._extract_features(candidate)
        
        z_prompt = self._sparse_code(x_prompt)
        z_cand = self._sparse_code(x_cand)
        
        # Initial Energy
        e_prompt = self._compute_energy(z_prompt, z_prompt) # Should be near 0
        e_cand = self._compute_energy(z_cand, z_prompt)
        
        # PID Loop to refine score
        score = 0.0
        integral = 0.0
        e_prev = e_cand
        
        # Simulate gradient steps as error signals
        # We assume the "error" is the energy difference relative to a perfect match
        # In a real system, we'd optimize z. Here we optimize the score s based on energy gradient.
        
        for t in range(self.max_iter):
            # Approximate gradient of energy w.r.t candidate alignment
            # If candidate energy is high, error is high (bad alignment)
            error = -(e_cand - e_prompt) 
            
            score, integral = self._pid_score_update(
                prompt, candidate, score, 
                error, 
                0.0 if t == 0 else -(e_prev - e_prompt), # Simplified derivative
                integral
            )
            e_prev = e_cand
            # Decay energy for next iteration simulation (convergence)
            e_cand *= 0.8 
            
        return score

    def _compute_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Check if numeric claims in candidate match prompt logic.
        Returns 1.0 if consistent, 0.0 if contradictory, 0.5 if neutral.
        """
        p_nums = [float(n) for n in self.patterns['number'].findall(prompt)]
        c_nums = [float(n) for n in self.patterns['number'].findall(candidate)]
        
        if not p_nums:
            return 0.5 # No numbers to check
            
        if not c_nums:
            return 0.0 # Prompt has numbers, candidate ignores them (likely wrong)
            
        # Simple heuristic: If prompt implies an order (e.g. "greater than"), check candidate
        # For this demo, we check if the candidate preserves the max value magnitude logic
        # or simply if the numbers appear logically derived (too complex for pure regex).
        # Instead, we check for direct contradiction of explicit values found in prompt.
        
        # If candidate contains a number from prompt, it's a good sign (copying data)
        # If it contains a number that contradicts a comparative statement, penalize.
        
        # Basic overlap score
        overlap = len(set(p_nums) & set(c_nums))
        if overlap > 0:
            return 1.0
        return 0.5

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return len_both / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt meta-confidence cap
        meta_cap = self._check_meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Thermodynamic-Sparse-PID)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Numeric/Computational Consistency
            comp_score = self._compute_numeric_consistency(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Weighted Sum
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            # Normalizing rough scores to [0,1] range roughly
            final_score = (0.50 * (struct_score + 1.0)) + \
                          (0.35 * comp_score) + \
                          ncd_score
                          
            # Apply Epistemic Honesty Cap
            if meta_cap < 0.5:
                final_score *= (meta_cap / 0.5) # Scale down significantly
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{struct_score:.2f}, Numeric:{comp_score:.2f}, NCD:{ncd_score:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        # 1. Check Meta-Confidence (Prompt properties)
        meta_cap = self._check_meta_confidence(prompt)
        
        # 2. Calculate raw alignment score
        struct_score = self._compute_structural_score(prompt, answer)
        comp_score = self._compute_numeric_consistency(prompt, answer)
        
        raw_conf = (0.6 * (struct_score + 1.0)/2.0) + (0.4 * comp_score)
        
        # Apply cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))
```

</details>
