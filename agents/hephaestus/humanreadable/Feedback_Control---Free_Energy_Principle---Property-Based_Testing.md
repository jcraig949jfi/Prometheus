# Feedback Control + Free Energy Principle + Property-Based Testing

**Fields**: Control Theory, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:37:02.977597
**Report Generated**: 2026-03-27T06:37:39.730707

---

## Nous Analysis

**Algorithm**  
1. **Parse** the candidate answer and a reference specification into a directed‑acyclic graph \(G=(V,E)\). Each node \(v_i\) holds a typed literal (boolean, numeric, or relational predicate). Edges encode logical dependencies (e.g., \(A\rightarrow B\) for “if A then B”).  
2. **Feature vector** \(\mathbf{x}\in\mathbb{R}^m\) is built by extracting structural predicates from \(G\):  
   - \(x_1\): count of negations,  
   - \(x_2\): count of comparatives (>,<,≥,≤),  
   - \(x_3\): count of conditionals (→),  
   - \(x_4\): sum of absolute numeric values,  
   - \(x_5\): number of causal claim patterns (“because”, “leads to”),  
   - \(x_6\): length of the longest chain of ordering relations.  
   NumPy is used to store \(\mathbf{x}\) as a float64 array.  
3. **Prediction model** \(\hat{y}= \mathbf{w}^\top \mathbf{x}\) where \(\mathbf{w}\in\mathbb{R}^m\) are adjustable weights. The target \(y^\*\) is 1 for a fully correct answer and 0 for a completely wrong one (derived from the reference specification).  
4. **Free‑energy loss** \(F = \frac{1}{2}(\hat{y}-y^\*)^2 + \lambda\|\mathbf{w}\|^2\) (quadratic variational free energy).  
5. **Feedback‑control update** (PID‑style) applied each iteration \(t\):  
   \[
   \mathbf{e}_t = \hat{y}_t - y^\*,\quad
   \mathbf{w}_{t+1}= \mathbf{w}_t - K_p\mathbf{e}_t\mathbf{x}
                     - K_i\bigl(\sum_{k=0}^{t}\mathbf{e}_k\bigr)\mathbf{x}
                     - K_d(\mathbf{e}_t-\mathbf{e}_{t-1})\mathbf{x},
   \]
   with fixed gains \(K_p,K_i,K_d\) (e.g., 0.1,0.01,0.05). This is the gradient descent on \(F\) with momentum‑like terms.  
6. **Property‑based testing loop**: after each weight update, generate \(N\) random perturbations of the candidate answer (swap a negation, flip a comparator, change a numeric constant) using a simple shrinking strategy: keep the perturbation that most reduces \(F\); repeat until no improvement or a max depth \(d_{max}=5\). The final \(F\) after shrinking is the **score** (lower = better).  

All operations use only NumPy (vector dot products, sums) and the Python standard library (random.choice, loops).  

**Structural features parsed** – negations, comparatives (> < ≥ ≤), conditionals (if‑then), numeric constants, causal claim cue‑words (“because”, “leads to”), and ordering relations (transitive chains like A < B < C).  

**Novelty** – The triple blend is not found in existing surveys. PID‑style weight updates appear in adaptive control; variational free energy appears in predictive coding; property‑based shrinking appears in testing libraries. Their conjunction for answer scoring is novel, though each component has precedents in neuro‑symbolic or reinforcement‑learning‑testing hybrids.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and numeric error, but relies on hand‑crafted features.  
Metacognition: 6/10 — PID provides self‑correction, yet no explicit monitoring of uncertainty beyond the loss.  
Hypothesis generation: 8/10 — property‑based shrinking actively proposes minimal counter‑examples.  
Implementability: 9/10 — only NumPy and stdlib needed; algorithm is straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Feedback Control + Free Energy Principle: strong positive synergy (+0.278). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Property-Based Testing: strong positive synergy (+0.176). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Feedback Control + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Free Energy Principle + Property-Based Testing + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Gauge Theory + Feedback Control + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T06:17:13.457840

---

## Code

**Source**: scrap

[View code](./Feedback_Control---Free_Energy_Principle---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Free Energy Principle (FEP) for loss minimization,
    Feedback Control (PID) for weight adaptation, and Property-Based Testing (PBT) 
    for structural robustness.
    
    Mechanism:
    1. Parses text into a structural feature vector (negations, comparatives, numerics).
    2. Uses FEP to define a loss landscape where correct answers minimize free energy.
    3. Employs PID-style updates to adjust feature weights dynamically based on error.
    4. Uses PBT shrinking to perturb candidates and test stability (confidence).
    5. Falls back to NCD only when structural signals are ambiguous.
    """
    
    def __init__(self):
        # Feature weights initialized to zero. 
        # Order: [negations, comparatives, conditionals, numeric_sum, causal_claims, chain_len]
        self.w = np.zeros(6, dtype=np.float64)
        self.Kp, self.Ki, self.Kd = 0.1, 0.01, 0.05
        self.integral = np.zeros(6, dtype=np.float64)
        self.prev_error = 0.0
        self.ref_features = None
        self.target_y = 1.0
        
        # Regex patterns for structural parsing
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comp': re.compile(r'[<>]=?|<=|>=|\b(more|less|greater|smaller)\b', re.I),
            'cond': re.compile(r'\b(if|then|else|unless|provided)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.I),
            'num': re.compile(r'-?\d+(?:\.\d+)?'),
            'chain': re.compile(r'\b([a-zA-Z])\s*<\s*([a-zA-Z])\s*<\s*([a-zA-Z])') # Simple A < B < C
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts the 6-dimensional structural feature vector."""
        if not text:
            return np.zeros(6, dtype=np.float64)
            
        x1 = len(self.patterns['neg'].findall(text))
        x2 = len(self.patterns['comp'].findall(text))
        x3 = len(self.patterns['cond'].findall(text))
        
        nums = [float(n) for n in self.patterns['num'].findall(text)]
        x4 = sum(abs(n) for n in nums) if nums else 0.0
        
        x5 = len(self.patterns['causal'].findall(text))
        
        chains = self.patterns['chain'].findall(text)
        x6 = max([len(c) for c in chains]) if chains else 0
        
        # Normalize numeric sum slightly to prevent dominance
        x4 = np.log1p(x4) 
        
        return np.array([x1, x2, x3, x4, x5, x6], dtype=np.float64)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def _pid_update(self, error: float, x: np.ndarray):
        """Updates weights using PID control law on the error signal."""
        self.integral += error
        derivative = error - self.prev_error
        
        # Vectorized PID update: w_new = w_old - (Kp*e + Ki*sum(e) + Kd*diff(e)) * x
        correction = (self.Kp * error + self.Ki * self.integral + self.Kd * derivative) * x
        self.w -= correction
        self.prev_error = error

    def _shrink_perturb(self, text: str, base_score: float) -> float:
        """
        Property-based testing: Perturb text to find minimal counter-examples.
        If small changes drastically reduce score, confidence drops.
        """
        if len(text) < 5: return base_score
        
        best_score = base_score
        current_text = text
        
        # Simple shrinking strategy: try removing words or flipping signs
        words = current_text.split()
        if len(words) <= 1: return best_score
        
        for i in range(min(5, len(words))):
            # Perturbation: Remove a word
            temp_words = words[:i] + words[i+1:]
            if not temp_words: continue
            perturbed = " ".join(temp_words)
            
            # Re-evaluate perturbed version
            x_p = self._extract_features(perturbed)
            y_hat = np.dot(self.w, x_p)
            
            # If perturbation improves (lowers) free energy significantly, original was fragile
            # Here we treat lower F as better, but for scoring we want stability.
            # We penalize the score if a trivial perturbation yields a "better" (lower energy) state
            # that contradicts the original structure.
            if y_hat < best_score * 0.9: # Significant drop implies instability
                best_score *= 0.85 
                
        return best_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Parse Reference (Prompt) as the structural target
        self.ref_features = self._extract_features(prompt)
        
        results = []
        
        for cand in candidates:
            # 2. Extract Features
            x = self._extract_features(cand)
            
            # 3. Prediction Model
            y_hat = float(np.dot(self.w, x))
            
            # 4. Free Energy Loss (Target is structural alignment with prompt logic)
            # We assume the prompt contains the necessary logical structure.
            # We want the candidate to match the *type* of logic, not necessarily identical counts.
            # Simplified target: High structural complexity in prompt implies high in answer.
            target_val = 1.0 if np.sum(self.ref_features) > 0 else 0.5
            
            # Error signal
            error = y_hat - target_val
            
            # 5. Feedback Control Update
            self._pid_update(error, x)
            
            # Recalculate after update for scoring
            y_hat_updated = float(np.dot(self.w, x))
            
            # Free Energy Calculation (F = 0.5 * e^2 + regularization)
            free_energy = 0.5 * (error ** 2) + 0.01 * np.sum(self.w ** 2)
            
            # Score inversion: Lower Free Energy = Higher Score
            # Base score starts at 1.0, penalized by free energy
            base_score = max(0.0, 1.0 - free_energy)
            
            # 6. Property-Based Testing Loop (Stability Check)
            final_score = self._shrink_perturb(cand, base_score)
            
            # NCD Tiebreaker: If structural signal is weak (features near zero)
            if np.sum(x) < 1e-6:
                ncd_val = self._compute_ncd(prompt, cand)
                final_score = (1.0 - ncd_val) * 0.5 # NCD contributes less
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {base_score:.4f}, Stability adjusted: {final_score:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural stability and free energy."""
        x_ans = self._extract_features(answer)
        x_prompt = self._extract_features(prompt)
        
        # Predict using current weights
        y_hat = float(np.dot(self.w, x_ans))
        
        # Calculate free energy relative to a hypothetical perfect match
        # Ideal: Answer features scale with prompt features
        scale = 1.0 if np.sum(x_prompt) == 0 else np.sum(x_ans) / (np.sum(x_prompt) + 1e-6)
        target = 1.0 # Normalized target
        
        error = y_hat - target
        F = 0.5 * (error ** 2)
        
        # Base confidence from free energy
        conf = max(0.0, 1.0 - F)
        
        # Apply PBT shrinking to test robustness
        conf = self._shrink_perturb(answer, conf)
        
        # Clamp
        return min(1.0, max(0.0, conf))
```

</details>
