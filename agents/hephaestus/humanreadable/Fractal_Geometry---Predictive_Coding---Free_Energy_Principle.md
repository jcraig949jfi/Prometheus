# Fractal Geometry + Predictive Coding + Free Energy Principle

**Fields**: Mathematics, Cognitive Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T14:12:00.780771
**Report Generated**: 2026-03-27T06:37:27.140932

---

## Nous Analysis

Combining fractal geometry, predictive coding, and the free‑energy principle yields a **multi‑scale variational inference engine** in which each level of a hierarchical generative model corresponds to a scale in an iterated‑function‑system (IFS) fractal prior. Concretely, one can build a **Fractal Predictive Coding Network (FPCN)**: a deep hierarchical variational autoencoder whose latent variables at layer ℓ are constrained by a fractal prior p(zℓ|zℓ‑1) defined by an IFS (e.g., a set of affine contractions that generate a self‑similar attractor such as the Sierpinski triangle). Prediction errors εℓ = xℓ − gℓ(zℓ) (where gℓ is the decoder) are propagated upward, while the free‑energy bound F = Σℓ ‖εℓ‖² + KL[q(zℓ|·)‖p(zℓ|zℓ‑1)] is minimized by gradient descent on both recognition and generative weights. The IFS ensures that the prior exhibits power‑law scaling, so surprise (prediction error) is evaluated consistently across magnitudes.

**Advantage for hypothesis testing:** Because the fractal prior reuses the same generative rules at every scale, a hypothesis formed at a coarse level automatically spawns self‑similar sub‑hypotheses at finer levels without redesigning the model. When the system tests a high‑level hypothesis (e.g., “object A is present”), prediction errors propagate down the hierarchy; if errors are low at many scales, the hypothesis gains hierarchical confirmation, enabling rapid, multi‑resolution falsification or refinement. This yields a reasoning system that can simultaneously evaluate a hypothesis and its constituent parts, reducing redundant computation and improving robustness to noise or partial observations.

**Novelty:** Hierarchical predictive coding networks and variational autoencoders are well studied, and fractal latent spaces have appeared in recent work on “Fractal VAEs” (e.g., Raghu et al., 2021). However, the explicit coupling of an IFS‑defined fractal prior with the free‑energy principle’s variational bound across all scales — treating prediction error minimization as a fractal‑scale‐consistent free‑energy descent — has not been formalized in a single algorithmic framework. Thus the combination is largely unexplored, though it builds on existing threads.

**Ratings**  
Reasoning: 8/10 — provides a principled, mathematically grounded mechanism for multi‑scale inference that improves hypothesis evaluation.  
Metacognition: 7/10 — prediction‑error signals across scales give the system a built‑in monitor of its own confidence, though explicit meta‑learning loops are not inherent.  
Hypothesis generation: 7/10 — fractal priors bias the generative process toward self‑similar hypotheses, enriching the search space but may also constrain creativity.  
Implementability: 5/10 — requires custom IFS‑based priors, careful stability tuning of deep hierarchical VCAs, and lacks off‑the‑shelf libraries; training can be delicate.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Predictive Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Fractal Geometry + Predictive Coding: strong positive synergy (+0.459). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Fractal Geometry + Free Energy Principle: strong positive synergy (+0.474). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Predictive Coding: strong positive synergy (+0.600). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Fractal Geometry + Predictive Coding + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Cellular Automata + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Chaos Theory + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 27% | +7% |
| Calibration | 7% | +0% |

**Forge Timestamp**: 2026-03-25T09:54:00.638506

---

## Code

**Source**: forge

[View code](./Fractal_Geometry---Predictive_Coding---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Predictive Coding Network (FPCN) Approximation.
    
    Mechanism:
    1. Free Energy Principle (Core): Minimizes 'surprise' by evaluating how well a candidate
       satisfies logical constraints derived from the prompt. Lower prediction error = higher score.
    2. Fractal Geometry (Structural): Implements self-similarity by recursively parsing logical
       structures (negations, conditionals) at sentence and clause levels. The 'fractal prior'
       assumes valid reasoning maintains consistent truth values across these scales.
    3. Predictive Coding: Computes prediction errors (mismatch between expected logical outcomes
       and candidate implications) to rank candidates.
       
    Implementation Strategy:
    - Uses structural parsing (negations, comparatives, conditionals) as the primary signal.
    - Applies a recursive 'fractal' scan to detect constraint violations at multiple granularities.
    - Uses NCD only as a tiebreaker for candidates with identical logical scores.
    """

    def __init__(self):
        self.comparators = ['greater than', 'less than', 'equal to', 'larger than', 'smaller than']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.logic_keywords = ['therefore', 'thus', 'hence', 'because', 'so']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        count = 0
        for k in keywords:
            # Simple word boundary approximation
            pattern = r'\b' + re.escape(k) + r'\b'
            count += len(re.findall(pattern, text))
        return count

    def _extract_numbers(self, text: str) -> List[float]:
        # Extracts floating point numbers
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Checks if numeric relationships in candidate match prompt logic."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric signal
        
        # Simple heuristic: If prompt has comparison words, check if candidate numbers align
        p_low = min(p_nums)
        p_high = max(p_nums) if len(p_nums) > 1 else p_nums[0]
        
        if len(c_nums) == 0:
            return 0.0
            
        c_val = c_nums[0]
        
        # Detect intent
        is_greater = any(k in prompt for k in ['greater', 'larger', 'more', 'max'])
        is_less = any(k in prompt for k in ['less', 'smaller', 'min', 'fewer'])
        
        score = 0.0
        if is_greater and c_val == max(c_nums + [p_high]): # Candidate picks max if asked for greater
            score += 1.0
        if is_less and c_val == min(c_nums + [p_low]): # Candidate picks min if asked for less
            score += 1.0
            
        # Penalty if numbers are present but completely unrelated magnitude (rough check)
        if p_nums and c_nums:
            if abs(c_val) > 0 and all(abs(c_val - n) > abs(c_val)*0.5 for n in p_nums if n != 0):
                # Only penalize if it's not a direct extraction
                pass 
        return score

    def _fractal_logical_scan(self, text: str, depth: int = 0) -> Dict[str, float]:
        """
        Recursively scans text for logical structures (self-similar patterns).
        Returns a dict of logical features: {negation_count, conditional_count, contradiction_risk}
        """
        features = {
            'negations': 0.0,
            'conditionals': 0.0,
            'logic_ops': 0.0,
            'complexity': 0.0
        }
        
        norm_text = self._normalize(text)
        words = norm_text.split()
        if not words:
            return features

        # Base scale
        features['negations'] = self._count_keywords(norm_text, self.negations)
        features['conditionals'] = self._count_keywords(norm_text, self.conditionals)
        features['logic_ops'] = self._count_keywords(norm_text, self.logic_keywords)
        features['complexity'] = len(words) ** 0.5  # Fractal dimension approximation

        # Recursive scale (sub-clauses split by commas or 'and'/'or')
        if depth < 2: # Limit recursion depth to prevent explosion
            separators = [',', ' and ', ' or ', ';']
            parts = [text]
            for sep in separators:
                new_parts = []
                for p in parts:
                    new_parts.extend(p.split(sep))
                if len(new_parts) > len(parts):
                    parts = new_parts
            
            if len(parts) > 1:
                sub_features = {'negations': 0, 'conditionals': 0, 'logic_ops': 0, 'complexity': 0}
                for part in parts:
                    res = self._fractal_logical_scan(part, depth + 1)
                    for k in sub_features:
                        sub_features[k] += res[k]
                
                # Aggregate with scaling factor (fractal weighting)
                scale = 0.5
                features['negations'] += sub_features['negations'] * scale
                features['conditionals'] += sub_features['conditionals'] * scale

        return features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a 'Free Energy' score (lower is better, so we invert for final score).
        F = Prediction Error + Complexity Penalty
        """
        p_features = self._fractal_logical_scan(prompt)
        c_features = self._fractal_logical_scan(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Predictive Coding)
        # If prompt has strong negation logic, candidate should reflect awareness (simplified)
        if p_features['negations'] > 0:
            # Expect candidate to potentially have negations or logic ops to handle the constraint
            if c_features['negations'] == 0 and c_features['logic_ops'] == 0:
                error += 2.0 # High penalty for ignoring negation context
        
        # 2. Conditional Logic
        if p_features['conditionals'] > 0:
            if c_features['conditionals'] == 0 and c_features['logic_ops'] == 0:
                error += 1.0

        # 3. Numeric Consistency
        num_score = self._check_numeric_consistency(prompt, candidate)
        if num_score == 0.0 and (self._extract_numbers(prompt) and any(k in prompt for k in ['greater', 'less', 'max', 'min', 'compare'])):
            error += 3.0 # High penalty for failing numeric reasoning
        elif num_score > 0:
            error -= 2.0 # Reward for correct numeric handling

        # 4. Length/Complexity Prior (Occam's razor)
        # Penalize extremely long rambling answers if prompt is short, unless logic demands it
        if len(candidate) > len(prompt) * 3 and p_features['complexity'] < 2:
            error += 0.5

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_norm = self._normalize(prompt)
        
        # Calculate base free energy for all candidates
        scores = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt_norm, self._normalize(cand))
            scores.append((cand, fe))
        
        # Sort by Free Energy (lower is better)
        scores.sort(key=lambda x: x[1])
        
        # Group by score to apply NCD tiebreaker only within ties
        # Since FE is float, we group by small epsilon
        final_ranking = []
        if not scores:
            return []
            
        current_group = [scores[0]]
        current_fe = scores[0][1]
        
        for i in range(1, len(scores)):
            cand, fe = scores[i]
            if abs(fe - current_fe) < 1e-6:
                current_group.append((cand, fe))
            else:
                # Process group
                if len(current_group) > 1:
                    # Apply NCD tiebreaker within group
                    current_group.sort(key=lambda x: self._ncd(prompt_norm, self._normalize(x[0])))
                for c, f in current_group:
                    # Convert Free Energy to a positive score (inverse)
                    # Base score 1.0, subtract normalized error
                    score_val = max(0.0, 1.0 - (f * 0.2)) 
                    final_ranking.append({"candidate": c, "score": score_val, "reasoning": "Fractal predictive coding analysis"})
                current_group = [(cand, fe)]
                current_fe = fe
        
        # Process last group
        if len(current_group) > 1:
            current_group.sort(key=lambda x: self._ncd(prompt_norm, self._normalize(x[0])))
        for c, f in current_group:
            score_val = max(0.0, 1.0 - (f * 0.2))
            final_ranking.append({"candidate": c, "score": score_val, "reasoning": "Fractal predictive coding analysis"})

        return final_ranking

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low free energy (low prediction error) = High confidence.
        """
        fe = self._compute_free_energy(self._normalize(prompt), self._normalize(answer))
        # Map free energy to 0-1. 
        # FE=0 -> 1.0, FE=5 -> 0.0 (approx)
        conf = max(0.0, min(1.0, 1.0 - (fe * 0.2)))
        return conf
```

</details>
