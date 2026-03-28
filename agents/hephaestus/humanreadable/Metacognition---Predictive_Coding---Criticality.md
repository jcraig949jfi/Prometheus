# Metacognition + Predictive Coding + Criticality

**Fields**: Cognitive Science, Cognitive Science, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T17:46:35.045802
**Report Generated**: 2026-03-27T05:13:27.990302

---

## Nous Analysis

Combining metacognition, predictive coding, and criticality yields a **self‑tuning hierarchical predictive‑coding network that operates near a critical point and explicitly monitors its own surprise and precision estimates**. In practice this can be realized as a deep variational auto‑encoder (VAE) or transformer‑style generative model whose layers implement predictive‑coding message passing (prediction → error → update). Each layer’s gain (inverse variance) is not fixed but is modulated by a metacognitive controller that tracks the running average of prediction‑error magnitude and its variance—essentially a confidence‑calibration signal. The controller drives the system toward a critical regime by adjusting a global “temperature” or noise scale so that the distribution of activation avalanches follows a power‑law (maximal susceptibility). When error statistics indicate the model is too rigid (low variance, sub‑critical), the controller raises temperature to increase exploratory fluctuations; when error bursts dominate (super‑critical), it lowers temperature to restore stability.  

**Advantage for hypothesis testing:** The system can automatically detect when its generative model is mis‑specified (high, sustained prediction error) and, via metacognitive precision adjustment, either refine the current hypothesis (by increasing precision in relevant layers) or abandon it in favor of a more exploratory regime (by pushing the network toward criticality). This yields rapid, calibrated confidence updates and reduces the need for hand‑tuned learning rates.  

**Novelty:** Predictive coding and criticality have been jointly studied in neuroscience (e.g., “critical brain” hypotheses), and metacognitive confidence modeling appears in active‑inference frameworks. However, an explicit, algorithmic loop that uses metacognitive error statistics to tune a criticality parameter inside a hierarchical predictive‑coding architecture is not a standard technique in machine learning or cognitive modeling; thus the combination is largely unexplored and potentially fertile.  

**Ratings**  
Reasoning: 7/10 — Provides a principled way to balance exploitation and exploration via critical dynamics, improving adaptive inference.  
Metacognition: 8/10 — Directly supplies confidence‑calibration signals that guide precision weighting and strategy shifts.  
Hypothesis generation: 6/10 — Enhances the ability to switch hypotheses but does not fundamentally alter generative proposal mechanisms.  
Implementability: 5/10 — Requires careful tuning of criticality controllers and stable predictive‑coding message passing; non‑trivial but feasible with modern deep‑learning frameworks.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Predictive Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Metacognition: strong positive synergy (+0.416). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Category Theory + Metacognition + Criticality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Predictive Coding + Falsificationism (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-25T07:10:03.628644

---

## Code

**Source**: scrap

[View code](./Metacognition---Predictive_Coding---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified Metacognitive Predictive Coding network operating near Criticality.
    
    Mechanism:
    1. Predictive Coding: The system generates 'predictions' by parsing structural constraints 
       (negations, comparatives, logic) from the prompt. It computes prediction errors between 
       these constraints and each candidate answer.
    2. Metacognition: A precision weight is dynamically calculated based on the consistency 
       of the candidate set. If candidates are ambiguous (high variance in simple metrics), 
       precision drops, widening the acceptance threshold. If clear, precision tightens.
    3. Criticality: The system monitors the distribution of prediction errors. 
       - Sub-critical (too rigid/low error variance): Temperature rises to explore weaker signals.
       - Super-critical (chaotic/high error): Temperature lowers to stabilize.
       - The final score is a Boltzmann-like probability derived from the error energy, 
         modulated by the metacognitive precision and critical temperature.
    """

    def __init__(self):
        self.baseline_temp = 1.0
        self.critical_exponent = 1.5

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical constraints and numeric values (Structural Parsing)."""
        text_lower = text.lower()
        features = {
            'negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', text_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r"-?\d+\.?\d*", text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _compute_prediction_error(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'Prediction Error' energy between prompt constraints and candidate.
        Lower energy = better fit.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        error = 0.0
        
        # 1. Constraint Propagation (Negation & Logic)
        # If prompt has negation, candidate should ideally reflect it or not contradict it
        if p_feat['negation']:
            # Penalty if candidate is a simple affirmative without nuance in a negated context
            if c_lower in ['yes', 'true', 'correct'] and 'not' not in c_lower:
                error += 2.0
            if c_lower in ['no', 'false', 'incorrect']:
                error -= 1.0 # Reward matching negation logic if appropriate context exists
        
        # 2. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers satisfy simple prompt comparisons
            try:
                p_nums = p_feat['numbers']
                c_nums = c_feat['numbers']
                if p_feat['comparative']:
                    # Heuristic: if prompt compares, candidate should likely involve the numbers
                    if abs(c_nums[0] - p_nums[0]) > 1e-6: 
                         # If numbers differ significantly in a comparison task, high error
                        error += abs(c_nums[0] - p_nums[0]) * 0.5
            except:
                pass
        elif p_feat['numbers'] and not c_feat['numbers']:
            # Prompt has numbers, candidate doesn't -> High error for math problems
            if p_feat['comparative'] or p_feat['conditional']:
                error += 5.0

        # 3. NCD as a baseline similarity tiebreaker (Normalized Compression Distance)
        # Used here as a "prior" expectation of lexical overlap
        try:
            s1 = prompt.encode()
            s2 = candidate.encode()
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            ncd = (c12 - min(c1, c2)) / max(c1, c2, 1)
            error += ncd * 2.0 # Add compression distance to error energy
        except:
            error += 1.0

        return max(0.0, error)

    def _metacognitive_controller(self, errors: List[float]) -> Tuple[float, float]:
        """
        Adjusts precision and temperature based on error statistics (Criticality).
        Returns (precision, temperature).
        """
        if not errors:
            return 1.0, 1.0
            
        errors_np = np.array(errors)
        mean_err = np.mean(errors_np)
        var_err = np.var(errors_np)
        std_err = np.std(errors_np) + 1e-6
        
        # Metacognitive Precision: Inverse of variance (confidence in discrimination)
        # If all errors are similar (low var), precision is high (we can distinguish well? 
        # Actually, if var is 0, we can't distinguish. Let's invert logic: 
        # High variance in errors means we have clear winners/losers -> High Precision needed.
        # Low variance means everything looks same -> Low Precision.
        precision = np.clip(var_err * 2.0, 0.1, 10.0)
        
        # Criticality Controller:
        # Target: Power law distribution. 
        # If mean error is too low (sub-critical/bored), increase Temp to explore.
        # If mean error is too high (super-critical/chaotic), decrease Temp to focus.
        target_error = 1.5 # Arbitrary target for "interesting" regime
        
        if mean_err < target_error * 0.5:
            temperature = self.baseline_temp * 1.5 # Raise temp (explore)
        elif mean_err > target_error * 2.0:
            temperature = self.baseline_temp * 0.5 # Lower temp (exploit/stabilize)
        else:
            temperature = self.baseline_temp # Critical point
            
        return precision, temperature

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Compute Prediction Errors for all candidates
        errors = [self._compute_prediction_error(prompt, c) for c in candidates]
        
        # 2. Metacognitive & Criticality Adjustment
        precision, temperature = self._metacognitive_controller(errors)
        
        # 3. Compute Scores (Boltzmann distribution style)
        # Score ~ exp(-error * precision / temperature)
        scores = []
        for i, err in enumerate(errors):
            energy = err * precision / temperature
            score = np.exp(-energy)
            scores.append(float(score))
            
        # Normalize scores to 0-1 range roughly
        max_s = max(scores) if scores else 1.0
        if max_s > 0:
            scores = [s / max_s for s in scores]
            
        # Rank and format
        results = []
        for i, c in enumerate(candidates):
            results.append({
                "candidate": c,
                "score": scores[i],
                "reasoning": f"Error:{errors[i]:.2f}, Prec:{precision:.2f}, Temp:{temperature:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the predictive coding error."""
        # We simulate a candidate set with the single answer to get relative metrics
        # But since we need absolute confidence, we rely on the raw error-to-score mapping
        # calibrated against a dummy set of 'bad' answers to establish baseline.
        
        # Generate a few dummy bad candidates to establish context for the controller
        dummies = ["", " ", "irrelevant", "no", "yes"]
        all_candidates = [answer] + dummies
        
        # Run evaluation logic internally to get the score
        # We only care about the score of the 'answer' (index 0)
        # However, evaluate returns sorted list. We need to find our specific answer's score.
        
        # Re-calculate error for the specific answer
        err = self._compute_prediction_error(prompt, answer)
        
        # Estimate context errors for metacognition
        ctx_errors = [self._compute_prediction_error(prompt, c) for c in dummies]
        all_errors = [err] + ctx_errors
        
        precision, temperature = self._metacognitive_controller(all_errors)
        
        energy = err * precision / temperature
        conf = np.exp(-energy)
        
        # Clamp and return
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
