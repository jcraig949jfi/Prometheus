# Evolution + Wavelet Transforms + Free Energy Principle

**Fields**: Biology, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T17:08:56.249685
**Report Generated**: 2026-03-27T06:37:28.612929

---

## Nous Analysis

Combining evolution, wavelet transforms, and the free‑energy principle yields a **multi‑scale evolutionary predictive‑coding architecture**: a hierarchical neural network whose layers are organized as a wavelet‑based multiresolution analysis (e.g., a stationary wavelet transform or undecimated discrete wavelet transform). Each scale encodes prediction errors at a specific temporal‑frequency band, and the network updates its internal generative model by minimizing variational free energy (prediction error plus complexity cost) using gradient‑based or message‑passing inference. Evolutionary algorithms (e.g., CMA‑ES or NEAT‑style mutation‑selection) operate on the hyper‑parameters of the wavelet bases (number of vanishing moments, filter lengths, depth of the hierarchy) and on the sparsity‑inducing priors that shape the free‑energy objective. Over generations, the system discovers wavelet configurations that best compress sensory streams while keeping prediction error low.

**Advantage for hypothesis testing:** The system can rapidly probe hypotheses at multiple resolutions. When a high‑frequency prediction error spikes, the evolutionary layer can mutate wavelet filters to capture transient features; low‑frequency errors trigger structural changes in deeper layers. Because free‑energy minimization continuously evaluates the plausibility of each hypothesis across scales, the system self‑calibrates its model complexity, avoiding over‑fitting to noise while still detecting subtle patterns that a fixed‑resolution predictor would miss.

**Novelty:** Wavelet‑based predictive coding has appeared in neuroscience models (e.g., wavelet‑domain sparse coding for visual cortex) and in signal‑processing denoising. Evolutionary optimization of neural architectures is well studied (NEAT, HyperNEAT, CMA‑ES for hyper‑parameters). However, a tightly coupled loop where evolution directly shapes the wavelet basis *and* the free‑energy objective is not a mainstream framework; existing work treats these components separately. Thus the combination is largely unexplored, though it draws on known sub‑techniques.

**Ratings**

Reasoning: 7/10 — The multi‑scale free‑energy formulation gives a principled, uncertainty‑aware inference mechanism, but the added evolutionary loop introduces noise that can slow convergence.  
Metacognition: 6/10 — The system can monitor prediction‑error spectra across scales, offering a rudimentary form of self‑monitoring, yet explicit meta‑reasoning about its own evolutionary operators remains limited.  
Hypothesis generation: 8/10 — Evolving wavelet filters lets the system spontaneously generate novel basis functions tuned to residual errors, greatly enriching the hypothesis space.  
Implementability: 5/10 — Building a differentiable wavelet stack coupled with an evolutionary optimizer is feasible (e.g., PyTorch Wavelet layers + CMA‑ES), but the combined training‑evolution loop is computationally demanding and requires careful scheduling to avoid instability.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Evolution**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Wavelet Transforms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Evolution + Wavelet Transforms: strong positive synergy (+0.449). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Evolution + Free Energy Principle: strong positive synergy (+0.510). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Wavelet Transforms: strong positive synergy (+0.116). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Wavelet Transforms + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=40% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T02:19:27.235367

---

## Code

**Source**: scrap

[View code](./Evolution---Wavelet_Transforms---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Evolutionary Predictive-Coding Architecture (Simulated).
    
    Mechanism:
    1. Free Energy Principle (Core): The 'evaluate' method minimizes variational free energy.
       Free Energy = Prediction Error (Accuracy) + Complexity Cost (Overfitting penalty).
       Prediction Error is derived from structural parsing (negations, comparatives, logic)
       rather than raw string similarity.
       
    2. Wavelet Transforms (Multi-scale Analysis): 
       We simulate multi-resolution analysis by decomposing the prompt/candidate text 
       into 'scales': 
       - Scale 0 (High Freq): Token-level exact matches and numeric precision.
       - Scale 1 (Mid Freq): Structural patterns (negations, conditionals, comparatives).
       - Scale 2 (Low Freq): Global semantic overlap (bag-of-words/Jaccard).
       This allows the system to detect subtle logical contradictions (high freq) 
       even if global meaning (low freq) aligns.
       
    3. Evolution (Hyper-parameter Optimization):
       Instead of running a slow genetic algorithm per query, we use an evolutionary 
       strategy to dynamically weight the 'scales' based on the prompt's complexity.
       If the prompt contains logical operators (IF, NOT, >), the system 'mutates' 
       its weights to prioritize structural scales over simple overlap, effectively 
       evolving a specialized parser for that specific reasoning trap.
    """

    def __init__(self):
        # Evolutionary hyper-parameters (base weights)
        self.base_weights = {"numeric": 0.4, "logic": 0.4, "semantic": 0.2}
        # Complexity cost factor (Free Energy regularization)
        self.complexity_penalty = 0.15

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract structural features (Wavelet Scale 1 & 2)."""
        t = text.lower()
        features = {
            "has_negation": bool(re.search(r'\b(not|no|never|neither|nor)\b', t)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|otherwise)\b', t)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|>|<)\b', t)),
            "numbers": re.findall(r'\d+\.?\d*', t),
            "length": len(text.split())
        }
        return features

    def _compute_scale_errors(self, prompt: str, candidate: str) -> Tuple[float, float, float]:
        """
        Compute prediction errors at different scales.
        Lower error = better match.
        Returns: (numeric_error, logic_error, semantic_error)
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        # Scale 0: Numeric Precision (High Frequency)
        num_err = 0.0
        if p_feat["numbers"] and c_feat["numbers"]:
            # Check if numbers match roughly or follow simple logic
            try:
                p_nums = [float(n) for n in p_feat["numbers"]]
                c_nums = [float(n) for n in c_feat["numbers"]]
                # Simple sequence match
                if len(p_nums) == len(c_nums):
                    diff = sum(abs(a - b) for a, b in zip(p_nums, c_nums))
                    num_err = diff / (sum(p_nums) + 1e-6) # Normalized diff
                else:
                    num_err = 1.0 # Mismatched count is high error
            except:
                num_err = 1.0
        elif p_feat["numbers"] and not c_feat["numbers"]:
            num_err = 1.0 # Missing numbers in candidate
        
        # Scale 1: Logical Structure (Mid Frequency)
        logic_err = 0.0
        # Penalty for mismatched logical operators
        if p_feat["has_negation"] != c_feat["has_negation"]:
            logic_err += 0.5
        if p_feat["has_conditional"] != c_feat["has_conditional"]:
            logic_err += 0.5
        if p_feat["has_comparative"] != c_feat["has_comparative"]:
            logic_err += 0.5
        logic_err = min(logic_err, 1.0)

        # Scale 2: Semantic Overlap (Low Frequency)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        if not p_words:
            sem_err = 1.0
        else:
            intersection = p_words.intersection(c_words)
            union = p_words.union(c_words)
            sem_err = 1.0 - (len(intersection) / len(union)) if union else 1.0

        return num_err, logic_err, sem_err

    def _evolve_weights(self, prompt: str) -> Dict[str, float]:
        """
        Evolutionary adaptation of weights based on prompt complexity.
        Mutates base weights to prioritize structural parsing if logical markers are present.
        """
        features = self._parse_structure(prompt)
        weights = self.base_weights.copy()
        
        # Mutation operator: If logical structures detected, shift mass to logic/numeric
        mutation_strength = 0.0
        if features["has_conditional"] or features["has_negation"]:
            mutation_strength += 0.3
        if features["has_comparative"] or features["numbers"]:
            mutation_strength += 0.2
            
        if mutation_strength > 0:
            # Normalize mutation impact
            total_shift = mutation_strength
            weights["logic"] = min(0.9, weights["logic"] + total_shift)
            weights["numeric"] = min(0.9, weights["numeric"] + total_shift)
            weights["semantic"] = max(0.05, weights["semantic"] - total_shift)
            
            # Re-normalize to sum to 1
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
            
        return weights

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Core Free Energy Calculation.
        F = E(Error) + Complexity_Cost
        We minimize F. Lower F = Higher Score.
        """
        # 1. Get multi-scale errors (Wavelet decomposition)
        num_err, logic_err, sem_err = self._compute_scale_errors(prompt, candidate)
        
        # 2. Evolve weights based on prompt context (Evolutionary step)
        weights = self._evolve_weights(prompt)
        
        # 3. Weighted Prediction Error (Accuracy term)
        prediction_error = (
            weights["numeric"] * num_err +
            weights["logic"] * logic_err +
            weights["semantic"] * sem_err
        )
        
        # 4. Complexity Cost (Regularization)
        # Penalize candidates that are vastly different in length (overfitting/underfitting proxy)
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        length_ratio = abs(p_len - c_len) / (p_len + 1)
        complexity_cost = self.complexity_penalty * length_ratio
        
        free_energy = prediction_error + complexity_cost
        return free_energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        if not s1 and not s2: return 0.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        min_fe = float('inf')
        
        # First pass: compute Free Energy for all
        scores = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            scores.append((cand, fe))
            if fe < min_fe:
                min_fe = fe
        
        # Second pass: normalize and rank
        # Convert Free Energy to a score (0-1), where higher is better
        # Score = 1 / (1 + FE) provides a smooth decay
        ranked = []
        for cand, fe in scores:
            # Primary score from Free Energy minimization
            primary_score = 1.0 / (1.0 + fe)
            
            # Tiebreaker logic using NCD if FE scores are very close
            final_score = primary_score
            
            # Construct reasoning string
            reason = f"FE={fe:.4f}; Scales: Num={self._compute_scale_errors(prompt, cand)[0]:.2f}, Log={self._compute_scale_errors(prompt, cand)[1]:.2f}"
            
            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on Free Energy minimization."""
        fe = self._compute_free_energy(prompt, answer)
        # Transform Free Energy to confidence
        # Low FE -> High Confidence. 
        conf = 1.0 / (1.0 + fe)
        
        # Boost confidence if structural alignment is perfect (logic match)
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        logic_match = (p_feat["has_negation"] == a_feat["has_negation"]) and \
                      (p_feat["has_conditional"] == a_feat["has_conditional"])
        
        if logic_match and fe < 0.3:
            conf = min(1.0, conf + 0.1)
            
        return max(0.0, min(1.0, conf))
```

</details>
